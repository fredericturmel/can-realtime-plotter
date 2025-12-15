"""
Connection Dialog

Dialog for configuring CAN interface connection.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QSpinBox, QGroupBox,
                             QFormLayout)
from PyQt5.QtCore import Qt
from src.can_interface.can_manager import CANInterfaceManager


class ConnectionDialog(QDialog):
    """Dialog for CAN interface connection configuration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔌 CAN Interface Configuration")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.init_ui()
        self.load_available_interfaces()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Interface selection group
        interface_group = QGroupBox("⚙️ Interface Configuration")
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(16, 20, 16, 16)
        
        # Interface type
        self.interface_combo = QComboBox()
        self.interface_combo.currentTextChanged.connect(self.on_interface_changed)
        form_layout.addRow("🔌 Interface Type:", self.interface_combo)
        
        # Channel
        self.channel_combo = QComboBox()
        self.channel_combo.setEditable(True)
        form_layout.addRow("📡 Channel:", self.channel_combo)
        
        # Bitrate
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.setEditable(True)
        bitrates = ['125000', '250000', '500000', '1000000']
        self.bitrate_combo.addItems(bitrates)
        self.bitrate_combo.setCurrentText('500000')
        form_layout.addRow("⚡ Bitrate (bps):", self.bitrate_combo)
        
        interface_group.setLayout(form_layout)
        layout.addWidget(interface_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.setObjectName("successButton")
        self.connect_btn.setMinimumHeight(36)
        self.connect_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.connect_btn)
        
        layout.addLayout(button_layout)
        
    def load_available_interfaces(self):
        """Load available CAN interfaces."""
        available = CANInterfaceManager.get_available_interfaces()
        
        for interface_type in available.keys():
            self.interface_combo.addItem(interface_type)
        
        # Select first interface by default
        if self.interface_combo.count() > 0:
            self.on_interface_changed(self.interface_combo.currentText())
    
    def on_interface_changed(self, interface_type: str):
        """Handle interface type change."""
        available = CANInterfaceManager.get_available_interfaces()
        
        self.channel_combo.clear()
        
        if interface_type in available:
            channels = available[interface_type]
            self.channel_combo.addItems(channels)
            
            # Set default channel based on interface
            if interface_type == 'pcan' and channels:
                self.channel_combo.setCurrentText('PCAN_USBBUS1')
            elif interface_type == 'socketcan' and channels:
                self.channel_combo.setCurrentText('can0')
    
    def get_configuration(self) -> dict:
        """
        Get the configured connection parameters.
        
        Returns:
            Dictionary with connection configuration
        """
        return {
            'interface': self.interface_combo.currentText(),
            'channel': self.channel_combo.currentText(),
            'bitrate': int(self.bitrate_combo.currentText())
        }
