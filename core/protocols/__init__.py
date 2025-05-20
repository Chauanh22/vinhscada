from .modbus_handler import ModbusHandler
from .opcua_handler import OPCUAHandler
from .dnp3_handler import DNP3Handler
from .iec104_handler import IEC104Handler
from .iec61850_handler import IEC61850Handler
from .opcda_handler import OPCDAHandler
from .mqtt_handler import MQTTHandler

def initialize_protocols():
    """Initialize all protocol handlers"""
    protocols = {
        'Modbus': ModbusHandler(),
        'OPC UA': OPCUAHandler(),
        'DNP3': DNP3Handler(),
        'IEC 60870-5-104': IEC104Handler(),
        'IEC 61850': IEC61850Handler(),
        'OPC DA': OPCDAHandler(),
        'MQTT': MQTTHandler()
    }
    return protocols