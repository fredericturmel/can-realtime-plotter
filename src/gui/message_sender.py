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
        msg_group = QGroupBox("Message Configuration")
        msg_layout = QFormLayout()
        
        self.message_combo = QComboBox()
        self.message_combo.currentTextChanged.connect(self.on_message_selected)
        msg_layout.addRow("Message:", self.message_combo)
        
        self.msg_id_label = QLabel("N/A")
        msg_layout.addRow("CAN ID:", self.msg_id_label)
        
        msg_group.setLayout(msg_layout)
        layout.addWidget(msg_group)
        
        # Signal values
        signal_group = QGroupBox("Signal Values")
        self.signal_layout = QVBoxLayout()
        
        self.signal_table = QTableWidget()
        self.signal_table.setColumnCount(3)
        self.signal_table.setHorizontalHeaderLabels(['Signal', 'Value', 'Unit'])
        self.signal_layout.addWidget(self.signal_table)
        
        signal_group.setLayout(self.signal_layout)
        layout.addWidget(signal_group)
        
        # Send controls
        control_group = QGroupBox("Send Controls")
        control_layout = QVBoxLayout()
        
        # Single send
        single_layout = QHBoxLayout()
        self.send_once_btn = QPushButton("Send Once")
        self.send_once_btn.clicked.connect(self.send_once)
        single_layout.addWidget(self.send_once_btn)
        single_layout.addStretch()
        control_layout.addLayout(single_layout)
        
        # Periodic send
        periodic_layout = QHBoxLayout()
        self.periodic_check = QCheckBox("Send Periodically")
        self.periodic_check.toggled.connect(self.toggle_periodic)
        periodic_layout.addWidget(self.periodic_check)
        
        periodic_layout.addWidget(QLabel("Period (ms):"))
        self.period_spin = QSpinBox()
        self.period_spin.setRange(10, 10000)
        self.period_spin.setValue(100)
        periodic_layout.addWidget(self.period_spin)
        periodic_layout.addStretch()
        
        control_layout.addLayout(periodic_layout)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        layout.addStretch()
        
    def update_database(self):
        """Update message list from database."""
        if not self.db_parser.is_loaded():
            return
        
        self.message_combo.clear()
        messages = self.db_parser.get_messages()
        
        for msg in messages:
            self.message_combo.addItem(msg['name'], userData=msg['id'])
    
    def on_message_selected(self, msg_name: str):
        """Handle message selection."""
        if not msg_name:
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
    
    def send_once(self):
        """Send message once."""
        if not self.can_manager.is_connected:
            QMessageBox.warning(self, "Warning", "Not connected to CAN interface")
            return
        
        msg_id = self.message_combo.currentData()
        if msg_id is None:
            return
        
        signal_values = self.get_signal_values()
        
        # Encode message
        data = self.db_parser.encode_message(msg_id, signal_values)
        
        if data is None:
            QMessageBox.warning(self, "Error", "Failed to encode message")
            return
        
        # Create and send CAN message
        msg = can.Message(
            arbitration_id=msg_id,
            data=data,
            is_extended_id=False
        )
        
        if self.can_manager.send_message(msg):
            self.statusBar().showMessage(f"Sent message 0x{msg_id:X}", 2000)
    
    def toggle_periodic(self, enabled: bool):
        """Toggle periodic message sending."""
        if enabled:
            period_ms = self.period_spin.value()
            self.periodic_timer.start(period_ms)
            self.send_once_btn.setEnabled(False)
        else:
            self.periodic_timer.stop()
            self.send_once_btn.setEnabled(True)
    
    def send_periodic_message(self):
        """Send message periodically (called by timer)."""
        self.send_once()
