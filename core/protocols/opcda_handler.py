"""
OPC DA Protocol Handler for SCADA Data Gateway (Simulation Mode)
This is a simulated version since OpenOPC/DCOM is difficult to set up on Windows
"""

import logging
from datetime import datetime
import random
from .base_handler import BaseProtocolHandler, ConnectionStatus

class OPCDAHandler(BaseProtocolHandler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('SCADA_Gateway.OPCDA')
        self.client = None
        self.connected = False
        self.server_name = None
        self.sim_data = {}
        self.status = ConnectionStatus.DISCONNECTED

    def get_config_template(self):
        """Return configuration template for OPC DA connection"""
        return {
            "server_name": "",
            "host": "localhost",
            "update_rate": 1000,
            "deadband": 0.0,
            "groups": [
                {
                    "name": "Group1",
                    "update_rate": 1000,
                    "active": True,
                    "items": []
                }
            ]
        }

    async def connect(self, config):
        """
        Simulate connection to OPC DA server
        
        Args:
            config (dict): Connection configuration
        """
        try:
            self.logger.info(f"[SIMULATION] Connecting to OPC DA server {config['server_name']} on {config['host']}")
            self.status = ConnectionStatus.CONNECTING
            self.config = config
            self.server_name = config['server_name']
            
            # Simulate connection delay
            import asyncio
            await asyncio.sleep(0.5)
            
            self.connected = True
            self.status = ConnectionStatus.CONNECTED
            self._init_sim_data()
            
            self.logger.info("[SIMULATION] Successfully connected to OPC DA server")
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.logger.error(f"[SIMULATION] Connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def disconnect(self):
        """Simulate disconnection from OPC DA server"""
        try:
            if self.connected:
                self.logger.info("[SIMULATION] Disconnecting from OPC DA server")
                self.connected = False
                self.status = ConnectionStatus.DISCONNECTED
                self.sim_data.clear()
        except Exception as e:
            self.logger.error(f"[SIMULATION] Disconnect error: {str(e)}")
            raise

    async def read_data(self, tags):
        """
        Simulate reading data from OPC DA server
        
        Args:
            tags (list): List of tag names to read
            
        Returns:
            list: List of simulated values with quality and timestamp
        """
        if not self.connected:
            raise ConnectionError("Not connected to OPC DA server")

        results = []
        try:
            for tag in tags:
                value = self._get_simulated_value(tag)
                results.append({
                    'value': value,
                    'quality': 'GOOD',
                    'timestamp': datetime.utcnow().isoformat()
                })
                self.logger.debug(f"[SIMULATION] Read tag {tag}: {value}")
        except Exception as e:
            self.logger.error(f"[SIMULATION] Read error: {str(e)}")
            raise

        return results

    async def write_data(self, tags, values):
        """
        Simulate writing data to OPC DA server
        
        Args:
            tags (list): List of tag names to write to
            values (list): List of values to write
            
        Returns:
            list: List of success indicators
        """
        if not self.connected:
            raise ConnectionError("Not connected to OPC DA server")

        results = []
        try:
            for tag, value in zip(tags, values):
                self.sim_data[tag] = value
                results.append(True)
                self.logger.debug(f"[SIMULATION] Write tag {tag}: {value}")
        except Exception as e:
            self.logger.error(f"[SIMULATION] Write error: {str(e)}")
            raise

        return results

    async def browse_tags(self, path=""):
        """
        Simulate browsing OPC DA server tags
        
        Args:
            path (str): Path to browse from
            
        Returns:
            list: List of simulated tags
        """
        sample_tags = [
            "System.Temperature",
            "System.Pressure",
            "System.Flow",
            "Process.Status",
            "Process.Mode",
            "Process.Setpoint",
            "Device1.Status",
            "Device1.Temperature",
            "Device2.Status",
            "Device2.Temperature"
        ]
        
        if path:
            return [tag for tag in sample_tags if tag.startswith(path)]
        return sample_tags

    def _init_sim_data(self):
        """Initialize simulation data with random values"""
        self.sim_data = {
            "System.Temperature": random.uniform(20, 30),
            "System.Pressure": random.uniform(1, 5),
            "System.Flow": random.uniform(10, 50),
            "Process.Status": random.choice([0, 1]),
            "Process.Mode": random.choice(["Auto", "Manual"]),
            "Process.Setpoint": random.uniform(0, 100),
            "Device1.Status": random.choice([0, 1]),
            "Device1.Temperature": random.uniform(20, 30),
            "Device2.Status": random.choice([0, 1]),
            "Device2.Temperature": random.uniform(20, 30)
        }

    def _get_simulated_value(self, tag):
        """
        Get simulated value for a tag
        
        Args:
            tag (str): Tag name
            
        Returns:
            value: Simulated value based on tag type
        """
        if tag not in self.sim_data:
            if "Status" in tag:
                self.sim_data[tag] = random.choice([0, 1])
            elif "Temperature" in tag:
                self.sim_data[tag] = random.uniform(20, 30)
            elif "Pressure" in tag:
                self.sim_data[tag] = random.uniform(1, 5)
            elif "Flow" in tag:
                self.sim_data[tag] = random.uniform(10, 50)
            else:
                self.sim_data[tag] = random.uniform(0, 100)

        # Add some random variation to analog values
        if isinstance(self.sim_data[tag], float):
            self.sim_data[tag] += random.uniform(-0.1, 0.1)

        return self.sim_data[tag]

    def get_status(self):
        """Get connection status"""
        return {
            "connected": self.connected,
            "status": self.status.value,
            "mode": "SIMULATION",
            "server": self.server_name,
            "tags_count": len(self.sim_data),
            "last_update": datetime.utcnow().isoformat()
        }

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if self.connected:
                import asyncio
                asyncio.run(self.disconnect())
        except:
            pass