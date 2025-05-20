"""
Core module for SCADA Data Gateway Tool
Contains protocol handlers, data mapping, and security components
"""

from .data_mapping import DataMapping, DataPoint
from .security import SecurityManager
from .protocols import initialize_protocols

__version__ = "1.0.0"
__author__ = "dat007a"
__date__ = "2025-05-20"