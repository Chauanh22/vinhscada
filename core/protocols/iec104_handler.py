from .base_handler import BaseProtocolHandler, ConnectionStatus

class IEC104Handler(BaseProtocolHandler):
    def __init__(self):
        super().__init__()
        self.connection = None

    def get_config_template(self):
        return {
            "ip": "",
            "port": 2404,
            "common_address": 1,
            "asdu_address": 1,
            "originator_address": 0
        }

    async def connect(self, config):
        try:
            self.status = ConnectionStatus.CONNECTING
            self.config = config
            # Implementation would require a specific IEC 60870-5-104 library
            # This is a placeholder for the actual implementation
            self.status = ConnectionStatus.CONNECTED
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def disconnect(self):
        if self.connection:
            # Implement disconnect logic
            pass
        self.status = ConnectionStatus.DISCONNECTED

    async def read_data(self, tags):
        if not self.connection:
            raise ConnectionError("Not connected")
        
        results = []
        for tag in tags:
            # Implement IEC 104 read logic
            pass
        return results

    async def write_data(self, tags, values):
        if not self.connection:
            raise ConnectionError("Not connected")
        
        results = []
        for tag, value in zip(tags, values):
            # Implement IEC 104 write logic
            pass
        return results