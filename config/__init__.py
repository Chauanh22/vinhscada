"""
Configuration module for SCADA Data Gateway Tool
Contains default settings and configuration management
"""

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_config():
    """Load configuration from settings.json"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return get_default_config()

def save_config(config):
    """Save configuration to settings.json"""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def get_default_config():
    """Return default configuration"""
    return {
        "application": {
            "name": "SCADA Data Gateway",
            "version": "1.0.0",
            "log_level": "INFO",
            "max_connections": 100
        },
        "security": {
            "enable_encryption": True,
            "token_expiry_hours": 8,
            "max_login_attempts": 3
        },
        "protocols": {
            "modbus": {
                "enabled": True,
                "default_port": 502,
                "timeout": 3
            },
            "opcua": {
                "enabled": True,
                "default_port": 4840,
                "timeout": 5
            },
            "dnp3": {
                "enabled": True,
                "default_port": 20000,
                "timeout": 5
            },
            "iec104": {
                "enabled": True,
                "default_port": 2404,
                "timeout": 5
            },
            "iec61850": {
                "enabled": True,
                "default_port": 102,
                "timeout": 5
            },
            "opcda": {
                "enabled": True
            },
            "mqtt": {
                "enabled": True,
                "default_port": 1883,
                "keep_alive": 60
            }
        }
    }