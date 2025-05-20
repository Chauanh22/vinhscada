from pymodbus.client import ModbusTcpClient
from .base_handler import BaseProtocolHandler, ConnectionStatus

class ModbusHandler(BaseProtocolHandler):
    def __init__(self):
        super().__init__()
        self.client = None

    def get_config_template(self):
        return {
            "host": "",
            "port": 502,
            "unit": 1,
            "timeout": 3
        }

    async def connect(self, config):
        try:
            self.status = ConnectionStatus.CONNECTING
            self.config = config
            self.client = ModbusTcpClient(
                host=config["host"],
                port=config["port"],
                timeout=config["timeout"]
            )
            if await self.client.connect():
                self.status = ConnectionStatus.CONNECTED
            else:
                self.status = ConnectionStatus.ERROR
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            raise ConnectionError(f"Failed to connect: {str(e)}")

    async def disconnect(self):
        if self.client:
            await self.client.close()
        self.status = ConnectionStatus.DISCONNECTED

    async def read_data(self, tags):
        if not self.client or not self.client.is_connected():
            raise ConnectionError("Not connected")
        
        results = []
        for tag in tags:
            if tag["type"] == "holding":
                result = await self.client.read_holding_registers(
                    tag["address"],
                    tag["count"],
                    slave=self.config["unit"]
                )
                results.append(result.registers if not result.isError() else None)
        return results

    async def write_data(self, tags, values):
        if not self.client or not self.client.is_connected():
            raise ConnectionError("Not connected")
        
        results = []
        for tag, value in zip(tags, values):
            if tag["type"] == "holding":
                result = await self.client.write_register(
                    tag["address"],
                    value,
                    slave=self.config["unit"]
                )
                results.append(not result.isError())
        return results