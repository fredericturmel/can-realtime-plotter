"""
CAN Interface Manager

Handles communication with PCAN and IXXAT hardware adapters.
"""

import can
from typing import Optional, List, Dict, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CANInterfaceManager(QObject):
    """Manages CAN bus interface connections and message handling."""
    
    # Signals
    message_received = pyqtSignal(can.Message)
    connection_status_changed = pyqtSignal(bool, str)  # (connected, status_message)
    error_occurred = pyqtSignal(str)
    
    # Supported interfaces
    SUPPORTED_INTERFACES = {
        'pcan': 'PCAN-USB',
        'ixxat': 'IXXAT VCI',
        'socketcan': 'SocketCAN (Linux)',
        'virtual': 'Virtual (Testing)'
    }
    
    def __init__(self):
        super().__init__()
        self.bus: Optional[can.Bus] = None
        self.notifier: Optional[can.Notifier] = None
        self.interface_type: Optional[str] = None
        self.channel: Optional[str] = None
        self.bitrate: int = 500000
        self.is_connected: bool = False
        self._listener_thread: Optional[QThread] = None
        
    def connect(self, interface: str, channel: str, bitrate: int = 500000, 
                **kwargs) -> bool:
        """
        Connect to a CAN interface.
        
        Args:
            interface: Interface type ('pcan', 'ixxat', 'socketcan', 'virtual')
            channel: Channel identifier (e.g., 'PCAN_USBBUS1', 'can0')
            bitrate: Bus bitrate in bps
            **kwargs: Additional interface-specific parameters
            
        Returns:
            bool: True if connection successful
        """
        try:
            # Disconnect if already connected
            if self.is_connected:
                self.disconnect()
            
            logger.info(f"Connecting to {interface} on channel {channel} at {bitrate} bps")
            
            # Create bus instance based on interface type
            self.bus = can.Bus(
                interface=interface,
                channel=channel,
                bitrate=bitrate,
                **kwargs
            )
            
            # Set up message listener
            self.notifier = can.Notifier(self.bus, [self._message_listener])
            
            self.interface_type = interface
            self.channel = channel
            self.bitrate = bitrate
            self.is_connected = True
            
            status_msg = f"Connected to {interface} ({channel}) at {bitrate} bps"
            logger.info(status_msg)
            self.connection_status_changed.emit(True, status_msg)
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect to {interface}: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.connection_status_changed.emit(False, error_msg)
            return False
    
    def disconnect(self):
        """Disconnect from the CAN interface."""
        if not self.is_connected:
            return
        
        try:
            if self.notifier:
                self.notifier.stop()
                self.notifier = None
            
            if self.bus:
                self.bus.shutdown()
                self.bus = None
            
            self.is_connected = False
            logger.info(f"Disconnected from {self.interface_type}")
            self.connection_status_changed.emit(False, "Disconnected")
            
        except Exception as e:
            error_msg = f"Error during disconnect: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def send_message(self, msg: can.Message) -> bool:
        """
        Send a CAN message.
        
        Args:
            msg: CAN message to send
            
        Returns:
            bool: True if message sent successfully
        """
        if not self.is_connected or not self.bus:
            self.error_occurred.emit("Not connected to CAN interface")
            return False
        
        try:
            self.bus.send(msg)
            logger.debug(f"Sent message: {msg}")
            return True
        except Exception as e:
            error_msg = f"Failed to send message: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def _message_listener(self, msg: can.Message):
        """Internal callback for received messages."""
        self.message_received.emit(msg)
    
    @staticmethod
    def get_available_interfaces() -> Dict[str, List[str]]:
        """
        Get available CAN interfaces on the system.
        
        Returns:
            Dict mapping interface type to list of available channels
        """
        available = {}
        
        # Check for PCAN
        try:
            configs = can.detect_available_configs(interfaces=['pcan'])
            if configs:
                available['pcan'] = [cfg['channel'] for cfg in configs]
        except:
            pass
        
        # Check for IXXAT
        try:
            configs = can.detect_available_configs(interfaces=['ixxat'])
            if configs:
                available['ixxat'] = [cfg['channel'] for cfg in configs]
        except:
            pass
        
        # Check for SocketCAN (Linux)
        try:
            configs = can.detect_available_configs(interfaces=['socketcan'])
            if configs:
                available['socketcan'] = [cfg['channel'] for cfg in configs]
        except:
            pass
        
        # Always add virtual for testing
        available['virtual'] = ['vcan0', 'vcan1']
        
        return available
    
    def get_bus_statistics(self) -> Dict:
        """
        Get current bus statistics.
        
        Returns:
            Dictionary with bus statistics
        """
        if not self.is_connected or not self.bus:
            return {}
        
        stats = {
            'interface': self.interface_type,
            'channel': self.channel,
            'bitrate': self.bitrate,
            'connected': self.is_connected
        }
        
        return stats
