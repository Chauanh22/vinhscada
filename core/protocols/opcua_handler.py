"""
OPC UA Protocol Handler for SCADA Data Gateway
Uses asyncua for OPC UA communication
"""

import logging
from datetime import datetime
import random
import asyncio
from asyncua import Client, Server, ua
from .base_handler import BaseProtocolHandler, ConnectionStatus

class OPCUAHandler(BaseProtocolHandler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('SCADA_Gateway.OPCUA')
        self.client = None
        self.server = None
        self.connected = False
        self.mode = 'client'  # 'client' or 'server'
        self.nodes = {}
        self.sim_data = {}
        self.status = ConnectionStatus.DISCONNECTED
        self.subscription = None
        self.monitored_items = {}

    def get_config_template(self):
        """Return configuration template for OPC UA connection"""
        return {
            "mode": "client",  # or "server"
            "endpoint": "opc.tcp://localhost:4840/freeopcua/server/",
            "security_mode": "None",  # None, Sign, SignAndEncrypt
            "security_policy": "None",  # None, Basic128Rsa15, Basic256, Basic256Sha256
            "username": "",
            "password": "",
            "nodes": [
                {
                    "node_id": "ns=2;s=Channel1.Device1.Tag1",
                    "browse_name": "Tag1",
                    "data_type": "Float",
                    "access": "rw"  # r, w, rw
                }
            ]
        }

    async def connect(self, config):
        """
        Connect to OPC UA server or start OPC UA server
        
        Args:
            config (dict): Connection configuration
        """
        try:
            self.config = config
            self.mode = config.get('mode', 'client')
            self.status = ConnectionStatus.CONNECTING

            if self.mode == 'client':
                await self._connect_client()
            else:
                await self._start_server()

            self._init_sim_data()
            self.connected = True
            self.status = ConnectionStatus.CONNECTED
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.logger.error(f"Connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def _connect_client(self):
        """Connect to OPC UA server as client"""
        try:
            self.logger.info(f"Connecting to OPC UA server at {self.config['endpoint']}")
            self.client = Client(url=self.config['endpoint'])
            
            # Set security if configured
            if self.config['security_mode'] != 'None':
                self.client.set_security(
                    getattr(ua.MessageSecurityMode, self.config['security_mode']),
                    getattr(ua.SecurityPolicyType, self.config['security_policy'])
                )

            # Set user authentication if provided
            if self.config['username'] and self.config['password']:
                await self.client.set_user(self.config['username'])
                await self.client.set_password(self.config['password'])

            await self.client.connect()
            self.logger.info("Successfully connected to OPC UA server")
            
            # Setup subscription
            self.subscription = await self.client.create_subscription(500, self)
            
        except Exception as e:
            self.logger.error(f"Client connection error: {str(e)}")
            raise

    async def _start_server(self):
        """Start OPC UA server"""
        try:
            self.logger.info(f"Starting OPC UA server at {self.config['endpoint']}")
            self.server = Server()
            await self.server.init()
            
            self.server.set_endpoint(self.config['endpoint'])
            
            # Set up server security if configured
            if self.config['security_mode'] != 'None':
                self.server.set_security_policy([
                    ua.SecurityPolicyType[self.config['security_policy']]
                ])

            # Set up authentication if configured
            if self.config['username'] and self.config['password']:
                self.server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
                user_manager = self.server.get_user_manager()
                user_manager.add_user(self.config['username'], self.config['password'])

            # Create sample nodes
            objects = self.server.get_objects_node()
            
            # Add a custom namespace
            uri = "http://examples.freeopcua.github.io"
            idx = await self.server.register_namespace(uri)
            
            # Create nodes defined in config
            for node_config in self.config['nodes']:
                node_id = node_config['node_id']
                browse_name = node_config['browse_name']
                data_type = getattr(ua.VariantType, node_config['data_type'])
                
                var = await objects.add_variable(
                    ua.NodeId(browse_name, idx),
                    ua.QualifiedName(browse_name, idx),
                    ua.Variant(0, data_type)
                )
                
                if 'w' in node_config['access'].lower():
                    await var.set_writable()
                
                self.nodes[node_id] = var

            await self.server.start()
            self.logger.info("OPC UA server started successfully")
            
        except Exception as e:
            self.logger.error(f"Server start error: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from OPC UA server or stop OPC UA server"""
        try:
            if self.connected:
                if self.mode == 'client':
                    if self.subscription:
                        await self.subscription.delete()
                    if self.client:
                        await self.client.disconnect()
                else:
                    if self.server:
                        await self.server.stop()
                
                self.connected = False
                self.status = ConnectionStatus.DISCONNECTED
                self.logger.info("Disconnected from OPC UA")
                
        except Exception as e:
            self.logger.error(f"Disconnect error: {str(e)}")
            raise

    async def read_data(self, nodes):
        """
        Read data from OPC UA nodes
        
        Args:
            nodes (list): List of node IDs to read
            
        Returns:
            list: List of values with quality and timestamp
        """
        if not self.connected:
            raise ConnectionError("Not connected to OPC UA")

        results = []
        try:
            for node_id in nodes:
                if self.mode == 'client':
                    node = await self.client.get_node(node_id)
                    value = await node.read_value()
                else:
                    value = self._get_simulated_value(node_id)
                
                results.append({
                    'value': value,
                    'quality': 'GOOD',
                    'timestamp': datetime.utcnow().isoformat()
                })
                self.logger.debug(f"Read node {node_id}: {value}")
                
        except Exception as e:
            self.logger.error(f"Read error: {str(e)}")
            raise

        return results

    async def write_data(self, nodes, values):
        """
        Write data to OPC UA nodes
        
        Args:
            nodes (list): List of node IDs to write to
            values (list): List of values to write
            
        Returns:
            list: List of success indicators
        """
        if not self.connected:
            raise ConnectionError("Not connected to OPC UA")

        results = []
        try:
            for node_id, value in zip(nodes, values):
                if self.mode == 'client':
                    node = await self.client.get_node(node_id)
                    await node.write_value(value)
                else:
                    self.sim_data[node_id] = value
                    if node_id in self.nodes:
                        await self.nodes[node_id].write_value(value)
                
                results.append(True)
                self.logger.debug(f"Write node {node_id}: {value}")
                
        except Exception as e:
            self.logger.error(f"Write error: {str(e)}")
            raise

        return results

    def _init_sim_data(self):
        """Initialize simulation data with random values"""
        self.sim_data = {}
        if self.mode == 'server':
            for node_config in self.config['nodes']:
                node_id = node_config['node_id']
                data_type = node_config['data_type']
                
                if data_type == 'Boolean':
                    self.sim_data[node_id] = random.choice([True, False])
                elif data_type in ['Int32', 'Int64']:
                    self.sim_data[node_id] = random.randint(0, 100)
                else:  # Float, Double
                    self.sim_data[node_id] = random.uniform(0, 100)

    def _get_simulated_value(self, node_id):
        """
        Get simulated value for a node
        
        Args:
            node_id (str): Node ID
            
        Returns:
            value: Simulated value based on node type
        """
        if node_id not in self.sim_data:
            self.sim_data[node_id] = random.uniform(0, 100)
        elif isinstance(self.sim_data[node_id], float):
            self.sim_data[node_id] += random.uniform(-0.1, 0.1)

        return self.sim_data[node_id]

    async def browse_nodes(self, node_id=None):
        """
        Browse OPC UA nodes
        
        Args:
            node_id (str): Starting node ID, None for root
            
        Returns:
            list: List of child nodes
        """
        try:
            if self.mode == 'client':
                if node_id is None:
                    node = self.client.get_root_node()
                else:
                    node = await self.client.get_node(node_id)
                
                children = await node.get_children()
                return [
                    {
                        'node_id': str(child.nodeid),
                        'browse_name': (await child.read_browse_name()).Name,
                        'display_name': (await child.read_display_name()).Text,
                        'node_class': (await child.read_node_class()).name
                    }
                    for child in children
                ]
            else:
                return list(self.nodes.keys())
                
        except Exception as e:
            self.logger.error(f"Browse error: {str(e)}")
            raise

    def get_status(self):
        """Get connection status"""
        return {
            "connected": self.connected,
            "status": self.status.value,
            "mode": self.mode,
            "endpoint": self.config.get('endpoint') if hasattr(self, 'config') else None,
            "security": {
                "mode": self.config.get('security_mode') if hasattr(self, 'config') else None,
                "policy": self.config.get('security_policy') if hasattr(self, 'config') else None
            },
            "nodes_count": len(self.nodes),
            "last_update": datetime.utcnow().isoformat()
        }

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if self.connected:
                asyncio.run(self.disconnect())
        except:
            pass

    # Subscription callback methods
    async def datachange_notification(self, node, val, data):
        """Callback for data changes"""
        node_id = str(node.nodeid)
        self.logger.debug(f"Data change notification - Node: {node_id}, Value: {val}")
        if node_id in self.monitored_items:
            callback = self.monitored_items[node_id]
            await callback(node_id, val, data)

    async def event_notification(self, event):
        """Callback for events"""
        self.logger.debug(f"Event notification: {event}")

    async def status_change_notification(self, status):
        """Callback for connection status changes"""
        self.logger.debug(f"Status change notification: {status}")
