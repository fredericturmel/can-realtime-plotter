"""
Example test for CAN interface manager.
"""

import pytest
from src.can_interface.can_manager import CANInterfaceManager


def test_can_manager_initialization():
    """Test CAN manager can be initialized."""
    manager = CANInterfaceManager()
    assert manager is not None
    assert not manager.is_connected


def test_get_available_interfaces():
    """Test getting available interfaces."""
    interfaces = CANInterfaceManager.get_available_interfaces()
    assert isinstance(interfaces, dict)
    assert 'virtual' in interfaces  # Virtual should always be available
