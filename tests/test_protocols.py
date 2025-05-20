import unittest
from unittest.mock import MagicMock, patch
from core.protocols import (
    ModbusHandler, OPCUAHandler, DNP3Handler,
    IEC104Handler, IEC61850Handler, OPCDAHandler, MQTTHandler
)
from core.protocols.base_handler import ConnectionStatus

class TestModbusHandler(unittest.TestCase):
    def setUp(self):
        self.handler = ModbusHandler()
        self.test_config = {
            "host": "localhost",
            "port": 502,
            "unit": 1,
            "timeout": 3
        }

    @patch('pymodbus.client.ModbusTcpClient')
    async def test_connect(self, mock_client):
        mock_client.return_value.connect.return_value = True
        await self.handler.connect(self.test_config)
        self.assertEqual(self.handler.status, ConnectionStatus.CONNECTED)

    @patch('pymodbus.client.ModbusTcpClient')
    async def test_disconnect(self, mock_client):
        await self.handler.disconnect()
        self.assertEqual(self.handler.status, ConnectionStatus.DISCONNECTED)

class TestOPCUAHandler(unittest.TestCase):
    def setUp(self):
        self.handler = OPCUAHandler()
        self.test_config = {
            "url": "opc.tcp://localhost:4840",
            "username": "user",
            "password": "pass",
            "security_policy": "None",
            "security_mode": "None",
            "certificate_path": "",
            "private_key_path": ""
        }

    @patch('asyncua.Client')
    async def test_connect(self, mock_client):
        await self.handler.connect(self.test_config)
        self.assertEqual(self.handler.status, ConnectionStatus.CONNECTED)

class TestMQTTHandler(unittest.TestCase):
    def setUp(self):
        self.handler = MQTTHandler()
        self.test_config = {
            "broker": "localhost",
            "port": 1883,
            "username": "user",
            "password": "pass",
            "use_tls": False,
            "client_id": "test_client",
            "keep_alive": 60
        }

    @patch('paho.mqtt.client.Client')
    async def test_connect(self, mock_client):
        await self.handler.connect(self.test_config)
        self.assertEqual(self.handler.status, ConnectionStatus.CONNECTED)

    async def test_publish(self):
        self.handler.client = MagicMock()
        result = await self.handler.write_data(
            [{"topic": "test/topic"}],
            ["test_message"]
        )
        self.assertTrue(result[0])

if __name__ == '__main__':
    unittest.main()