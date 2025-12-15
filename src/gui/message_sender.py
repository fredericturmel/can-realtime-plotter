"""
Message Sender Widget

Widget for sending CAN messages.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QComboBox, QSpinBox, QDoubleSpinBox, QPushButton,
                             QFormLayout, QLabel, QLineEdit, QCheckBox,
                             QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import QTimer
import can
from src.can_interface.can_manager import CANInterfaceManager
from src.parsers.database_parser import DatabaseParser


class MessageSenderWidget(QWidget):
    """Widget for sending CAN messages."""
    
    def __init__(self, can_manager: CANInterfaceManager, db_parser: DatabaseParser, parent=None):
        super().__init__(parent)
        self.can_manager = can_manager
        self.db_parser = db_parser
        self.periodic_timer = QTimer()
        self.periodic_timer.timeout.connect(self.send_periodic_message)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Message selection
        msg_group = QGroupBox("📨 Message Configuration")
        msg_layout = QFormLayout()
        msg_layout.setSpacing(12)
        msg_layout.setContentsMargins(16, 20, 16, 16)
        
        self.message_combo = QComboBox()
        self.message_combo.currentTextChanged.connect(self.on_message_selected)
        msg_layout.addRow("📋 Message:", self.message_combo)
        
        self.msg_id_label = QLabel("N/A")
        self.msg_id_label.setStyleSheet("font-weight: bold; color: #4a9eff;")
        msg_layout.addRow("🆔 CAN ID:", self.msg_id_label)
        
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)
        
        # Signal values
        signal_group = QGroupBox("📊 Signal Values")
        self.signal_layout = QVBoxLayout()
        self.signal_layout.setContentsMargins(16, 20, 16, 16)
        
        self.signal_table = QTableWidget()
        self.signal_table.setColumnCount(3)
        self.signal_table.setHorizontalHeaderLabels(['Signal', 'Value', 'Unit'])
        self.signal_table.setAlternatingRowColors(True)
        self.signal_table.horizontalHeader().setStretchLastSection(True)
        self.signal_layout.addWidget(self.signal_table)
        
        signal_group.setLayout(self.signal_layout)
        layout.addWidget(signal_group)
        
        # Send controls
        control_group = QGroupBox("🚀 Send Controls")
        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(16, 20, 16, 16)
        control_layout.setSpacing(12)
        
        # Single send
        single_layout = QHBoxLayout()
        single_layout.setSpacing(8)
        
        self.send_once_btn = QPushButton("📤 Send Once")
        self.send_once_btn.setObjectName("primaryButton")
        self.send_once_btn.setMinimumHeight(36)
        self.send_once_btn.clicked.connect(self.send_once)
        single_layout.addWidget(self.send_once_btn)
        
        # Test send button (for virtual interface testing)
        self.test_send_btn = QPushButton("🧪 Send Test Frame")
        self.test_send_btn.setMinimumHeight(36)
        self.test_send_btn.clicked.connect(self.send_test_frame)
        self.test_send_btn.setToolTip("Send a test frame (ID=0x123) for verification")
        single_layout.addWidget(self.test_send_btn)
        
        single_layout.addStretch()
        control_layout.addLayout(single_layout)
        
        # Periodic send
        periodic_layout = QHBoxLayout()
        periodic_layout.setSpacing(12)
        
        self.periodic_check = QCheckBox("🔄 Send Periodically")
        self.periodic_check.toggled.connect(self.toggle_periodic)
        periodic_layout.addWidget(self.periodic_check)
        
        periodic_layout.addWidget(QLabel("⏱️ Period (ms):"))
        self.period_spin = QSpinBox()
        self.period_spin.setRange(10, 10000)
        self.period_spin.setValue(100)
        self.period_spin.setMinimumWidth(100)
        periodic_layout.addWidget(self.period_spin)
        periodic_layout.addStretch()
        
        control_layout.addLayout(periodic_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        layout.addStretch()
        
    def set_managers(self, can_manager, db_parser):
        """Set CAN manager and database parser."""
        self.can_manager = can_manager
        self.db_parser = db_parser
        if db_parser and db_parser.db:
            self.update_database()
    
    def update_database(self):
        """Update message list from database."""
        if not self.db_parser or not self.db_parser.db:
            return
        
        self.message_combo.clear()
        messages = self.db_parser.get_messages()
        
        for msg in messages:
            self.message_combo.addItem(msg['name'], userData=msg['id'])
    
    def on_message_selected(self, msg_name: str):
        """Handle message selection."""
        if not msg_name or not self.db_parser or not self.db_parser.db:
            return
        
        msg_id = self.message_combo.currentData()
        if msg_id is None:
            return
        
        self.msg_id_label.setText(f"0x{msg_id:X}")
        
        # Load signals for this message
        signals = self.db_parser.get_signals_for_message(msg_id)
        
        self.signal_table.setRowCount(len(signals))
        
        for i, signal in enumerate(signals):
            # Signal name
            name_item = QTableWidgetItem(signal['name'])
            self.signal_table.setItem(i, 0, name_item)
            
            # Value spinbox
            value_spin = QDoubleSpinBox()
            value_spin.setRange(signal['minimum'], signal['maximum'])
            value_spin.setValue(0.0)
            value_spin.setDecimals(3)
            self.signal_table.setCellWidget(i, 1, value_spin)
            
            # Unit
            unit_item = QTableWidgetItem(signal['unit'] or '')
            self.signal_table.setItem(i, 2, unit_item)
    
    def get_signal_values(self) -> dict:
        """Get current signal values from the table."""
        values = {}
        
        for i in range(self.signal_table.rowCount()):
            signal_name = self.signal_table.item(i, 0).text()
            value_widget = self.signal_table.cellWidget(i, 1)
            
            if value_widget:
                values[signal_name] = value_widget.value()
        
        return values
    
    def send_once(self, show_warning=True):
        """Send message once.
        
        Args:
            show_warning: If True, show warning dialog when not connected
        """
        if not self.can_manager or not self.can_manager.is_connected:
            if show_warning:
                QMessageBox.warning(self, "Warning", "Not connected to CAN interface")
            return False
        
        msg_id = self.message_combo.currentData()
        if msg_id is None:
            return False
        
        signal_values = self.get_signal_values()
        
        # Encode message
        data = self.db_parser.encode_message(msg_id, signal_values)
        
        if data is None:
            if show_warning:
                QMessageBox.warning(self, "Error", "Failed to encode message")
            return False
        
        # Create and send CAN message
        msg = can.Message(
            arbitration_id=msg_id,
            data=data,
            is_extended_id=False
        )
        
        success = self.can_manager.send_message(msg)
        return success
    
    def toggle_periodic(self, enabled: bool):
        """Toggle periodic message sending."""
        if enabled:
            # Check connection before starting periodic send
            if not self.can_manager or not self.can_manager.is_connected:
                QMessageBox.warning(self, "Warning", "Not connected to CAN interface")
                self.periodic_check.setChecked(False)
                return
            
            # Check if message is selected
            if self.message_combo.currentData() is None:
                QMessageBox.warning(self, "Warning", "No message selected")
                self.periodic_check.setChecked(False)
                return
            
            period_ms = self.period_spin.value()
            self.periodic_timer.start(period_ms)
            self.send_once_btn.setEnabled(False)
            self.message_combo.setEnabled(False)
        else:
            self.periodic_timer.stop()
            self.send_once_btn.setEnabled(True)
            self.message_combo.setEnabled(True)
    
    def send_periodic_message(self):
        """Send message periodically (called by timer)."""
        # Send without showing warning dialog (silent mode)
        success = self.send_once(show_warning=False)
        
        # If send failed (e.g., disconnected), stop periodic sending
        if not success:
            self.periodic_check.setChecked(False)
            self.periodic_timer.stop()
            self.send_once_btn.setEnabled(True)
            self.message_combo.setEnabled(True)
    
    def send_test_frame(self):
        """Send a test CAN frame for verification."""
        if not self.can_manager or not self.can_manager.is_connected:
            QMessageBox.warning(self, "Warning", "Not connected to CAN interface")
            return
        
        # Create a test message with known ID and data
        msg = can.Message(
            arbitration_id=0x123,
            data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
            is_extended_id=False
        )
        
        if self.can_manager.send_message(msg):
            QMessageBox.information(
                self,
                "Test Frame Sent",
                f"Successfully sent test frame:\n\n"
                f"CAN ID: 0x{msg.arbitration_id:03X}\n"
                f"Data: {' '.join(f'{b:02X}' for b in msg.data)}\n"
                f"DLC: {len(msg.data)}\n\n"
                f"Check the plot or message log to verify reception."
            )
        else:
            QMessageBox.warning(
                self,
                "Send Failed",
                "Failed to send test frame. Check the connection."
            )
