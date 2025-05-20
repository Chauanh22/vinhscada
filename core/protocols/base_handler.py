from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any

class ConnectionStatus(Enum):
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    ERROR = "Error"

class BaseProtocolHandler(ABC):
    def __init__(self):
        self.status = ConnectionStatus.DISCONNECTED
        self.config = {}
        self.connection = None

    @abstractmethod
    async def connect(self, config: Dict[str, Any]):
        """Connect to the device/server"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the device/server"""
        pass

    @abstractmethod
    async def read_data(self, tags: list):
        """Read data from the device/server"""
        pass

    @abstractmethod
    async def write_data(self, tags: list, values: list):
        """Write data to the device/server"""
        pass

    def get_status(self):
        """Get current connection status"""
        return self.status

    def get_config_template(self):
        """Return configuration template for this protocol"""
        return {}