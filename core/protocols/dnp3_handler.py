"""
DNP3 Protocol Handler for SCADA Data Gateway (Simulation Mode)
This is a simulated version since pydnp3 is not supported on Windows
"""

import logging
from datetime import datetime
import random
from .base_handler import BaseProtocolHandler, ConnectionStatus

class DNP3Handler(BaseProtocolHandler):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('SCADA_Gateway.DNP3')
        self.client = None
        self.connected = False
        self.points = {}
        self.sim_data = {}

    def get_config_template(self):
        """Return configuration template for DNP3 connection"""
        return {
            "master": {
                "local_address": 1,
                "remote_address": 1024,
                "host": "localhost",
                "port": 20000,
                "timeout_ms": 5000
            },
            "outstation": {
                "local_address": 1024,
                "remote_address": 1,
                "host": "0.0.0.0",
                "port": 20000
            }
        }

    async def connect(self, config):
        """
        Simulate connection to DNP3 device
        
        Args:
            config (dict): Connection configuration
        """
        try:
            self.logger.info(f"[SIMULATION] Connecting to DNP3 device at {config['master']['host']}:{config['master']['port']}")
            self.status = ConnectionStatus.CONNECTING
            self.config = config
            
            # Simulate connection delay
            import asyncio
            await asyncio.sleep(0.5)
            
            self.connected = True
            self.status = ConnectionStatus.CONNECTED
            self.logger.info("[SIMULATION] Successfully connected to DNP3 device")
            
            # Initialize simulation data
            self._init_sim_data()
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.logger.error(f"[SIMULATION] Connection error: {str(e)}")
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def disconnect(self):
        """Simulate disconnection from DNP3 device"""
        try:
            if self.connected:
                self.logger.info("[SIMULATION] Disconnecting from DNP3 device")
                self.connected = False
                self.status = ConnectionStatus.DISCONNECTED
                self.sim_data.clear()
        except Exception as e:
            self.logger.error(f"[SIMULATION] Disconnect error: {str(e)}")
            raise

    async def read_data(self, points):
        """
        Simulate reading data from DNP3 device
        
        Args:
            points (list): List of point definitions to read
            
        Returns:
            list: List of simulated values
        """
        if not self.connected:
            raise ConnectionError("Not connected to DNP3 device")

        results = []
        try:
            for point in points:
                point_id = point.get('id', 0)
                value = self._get_simulated_value(point)
                results.append({
                    'value': value,
                    'quality': 'ONLINE',
                    'timestamp': datetime.utcnow().isoformat()
                })
                self.logger.debug(f"[SIMULATION] Read point {point_id}: {value}")
        except Exception as e:
            self.logger.error(f"[SIMULATION] Read error: {str(e)}")
            raise

        return results

    async def write_data(self, points, values):
        """
        Simulate writing data to DNP3 device
        
        Args:
            points (list): List of point definitions to write to
            values (list): List of values to write
            
        Returns:
            list: List of success indicators
        """
        if not self.connected:
            raise ConnectionError("Not connected to DNP3 device")

        results = []
        try:
            for point, value in zip(points, values):
                point_id = point.get('id', 0)
                self.sim_data[point_id] = value
                results.append(True)
                self.logger.debug(f"[SIMULATION] Write point {point_id}: {value}")
        except Exception as e:
            self.logger.error(f"[SIMULATION] Write error: {str(e)}")
            raise

        return results

    def _init_sim_data(self):
        """Initialize simulation data with random values"""
        self.sim_data = {
            # Binary Input points (1-100)
            **{i: random.choice([0, 1]) for i in range(1, 101)},
            # Analog Input points (101-200)
            **{i: random.uniform(0, 100) for i in range(101, 201)},
            # Counter points (201-300)
            **{i: random.randint(0, 1000) for i in range(201, 301)}
        }

    def _get_simulated_value(self, point):
        """
        Get simulated value for a point
        
        Args:
            point (dict): Point definition
            
        Returns:
            value: Simulated value based on point type
        """
        point_id = point.get('id', 0)
        point_type = point.get('type', 'analog')

        if point_id not in self.sim_data:
            if point_type == 'binary':
                self.sim_data[point_id] = random.choice([0, 1])
            elif point_type == 'counter':
                self.sim_data[point_id] = random.randint(0, 1000)
            else:  # analog
                self.sim_data[point_id] = random.uniform(0, 100)

        # Add some random variation to analog values
        if point_type == 'analog':
            self.sim_data[point_id] += random.uniform(-0.5, 0.5)

        return self.sim_data[point_id]

    def get_status(self):
        """Get connection status"""
        return {
            "connected": self.connected,
            "status": self.status.value,
            "mode": "SIMULATION",
            "points_count": len(self.sim_data),
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
