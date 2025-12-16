"""
Message Browser - Navigation dans les messages CAN par trame
Affichage hiérarchique des messages et signaux avec support des énumérations
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QLabel, QLineEdit, QPushButton,
                             QSplitter, QTextEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor


class SignalValueWidget(QWidget):
    """Widget pour afficher la valeur d'un signal avec son énumération"""
    
    def __init__(self, signal_name, parent=None):
        super().__init__(parent)
        self.signal_name = signal_name
        self.raw_value = None
        self.enum_values = {}  # value -> name mapping
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        
        self.value_label = QLabel("---")
        self.value_label.setStyleSheet("color: #58a6ff; font-weight: 600;")
        layout.addWidget(self.value_label)
        
        self.enum_label = QLabel("")
        self.enum_label.setStyleSheet("color: #8b949e; font-style: italic;")
        layout.addWidget(self.enum_label)
        
        layout.addStretch()
        
    def set_enum_values(self, enum_dict):
        """Set enumeration values for this signal"""
        self.enum_values = enum_dict
        
    def update_value(self, raw_value, physical_value, unit=""):
        """Update the displayed value"""
        self.raw_value = raw_value
        
        # Format physical value
        if isinstance(physical_value, float):
            value_str = f"{physical_value:.3f}"
        else:
            value_str = str(physical_value)
            
        if unit:
            value_str += f" {unit}"
            
        self.value_label.setText(value_str)
        
        # Check for enumeration
        if self.enum_values and raw_value in self.enum_values:
            enum_name = self.enum_values[raw_value]
            self.enum_label.setText(f"[{enum_name}]")
        else:
            self.enum_label.setText("")


class MessageBrowser(QWidget):
    """Navigateur de messages CAN"""
    
    signal_selected = pyqtSignal(str, str)  # message_name, signal_name
    message_selected = pyqtSignal(str)  # message_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = None
        self.current_values = {}  # (message_name, signal_name) -> (raw, physical, unit)
        self.signal_widgets = {}  # (message_name, signal_name) -> SignalValueWidget
        self.raw_messages = {}  # can_id -> (data, timestamp, item)
        
        self.init_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 10 Hz
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar compact pour recherche et actions
        toolbar = QFrame()
        toolbar.setFixedHeight(45)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-bottom: 1px solid #30363d;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Rechercher un message ou signal...")
        self.search_box.textChanged.connect(self.filter_messages)
        toolbar_layout.addWidget(self.search_box)
        
        layout.addWidget(toolbar)
        
        # Splitter pour messages et détails
        splitter = QSplitter(Qt.Horizontal)
        
        # Tree widget pour les messages
        self.tree = QTreeWidget()
        self.all_collapsed = False
        self.tree.setHeaderLabels(["▼ Message / Signal", "ID", "Valeur", "Unité"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 150)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.header().setSectionsClickable(True)
        self.tree.header().setSortIndicatorShown(True)
        self.tree.sortByColumn(1, Qt.AscendingOrder)  # Tri par défaut
        self.tree.itemClicked.connect(self.on_item_clicked)
        
        # Connect header click for column 0 to toggle expand/collapse
        self.tree.header().sectionClicked.connect(self.on_header_clicked)
        
        # Install event filter for right-click and middle-click
        self.tree.viewport().installEventFilter(self)
        
        splitter.addWidget(self.tree)
        
        # Details panel
        details = QWidget()
        details_layout = QVBoxLayout(details)
        details_layout.setContentsMargins(16, 16, 16, 16)
        
        details_title = QLabel("Détails du signal")
        details_title.setStyleSheet("font-size: 13px; font-weight: 600;")
        details_layout.addWidget(details_title)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        details_layout.addWidget(self.details_text)
        
        splitter.addWidget(details)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
    def load_database(self, db):
        """Load database and populate tree"""
        self.db = db
        self.tree.clear()
        self.signal_widgets.clear()
        self.raw_messages.clear()  # Clear raw messages when loading new DB
        
        if not db:
            return
            
        # Sort messages by CAN ID
        messages = sorted(db.messages, key=lambda m: m.frame_id)
        
        for message in messages:
            # Message item
            msg_item = QTreeWidgetItem(self.tree)
            msg_item.setText(0, message.name)
            msg_item.setText(1, f"0x{message.frame_id:03X}")
            msg_item.setData(0, Qt.UserRole, {"type": "message", "message": message})
            
            # Style message
            font = QFont()
            font.setBold(True)
            msg_item.setFont(0, font)
            msg_item.setForeground(0, QColor("#58a6ff"))
            
            # Add signals
            for signal in message.signals:
                sig_item = QTreeWidgetItem(msg_item)
                sig_item.setText(0, f"  └─ {signal.name}")
                sig_item.setText(3, signal.unit or "")
                sig_item.setData(0, Qt.UserRole, {
                    "type": "signal",
                    "message": message,
                    "signal": signal
                })
                
                # Create value widget
                value_widget = SignalValueWidget(signal.name)
                
                # Set enumeration if available
                if hasattr(signal, 'choices') and signal.choices:
                    value_widget.set_enum_values(signal.choices)
                    
                self.tree.setItemWidget(sig_item, 2, value_widget)
                self.signal_widgets[(message.name, signal.name)] = value_widget
                
                # Signal info
                sig_item.setForeground(0, QColor("#8b949e"))
                
        self.tree.expandAll()
        
    def add_raw_message(self, can_id, data, timestamp):
        """Add or update a raw CAN message (no DBC)"""
        import time
        
        # Check if message already exists
        if can_id in self.raw_messages:
            # Update existing
            _, _, item = self.raw_messages[can_id]
            data_str = " ".join(f"{b:02X}" for b in data)
            item.setText(2, data_str)
            item.setText(3, f"{time.time():.3f}")
            self.raw_messages[can_id] = (data, timestamp, item)
        else:
            # Create new raw message item
            msg_item = QTreeWidgetItem(self.tree)
            msg_name = f"Unknown_0x{can_id:03X}"
            msg_item.setText(0, msg_name)
            msg_item.setText(1, f"0x{can_id:03X}")
            data_str = " ".join(f"{b:02X}" for b in data)
            msg_item.setText(2, data_str)
            msg_item.setText(3, f"{time.time():.3f}")
            msg_item.setData(0, Qt.UserRole, {"type": "raw_message", "can_id": can_id})
            
            # Style raw message differently
            font = QFont()
            font.setBold(True)
            msg_item.setFont(0, font)
            msg_item.setForeground(0, QColor("#d29922"))  # Orange for undecoded
            
            self.raw_messages[can_id] = (data, timestamp, msg_item)
    
    def update_signal_value(self, message_name, signal_name, raw_value, physical_value, unit=""):
        """Update a signal's value"""
        key = (message_name, signal_name)
        self.current_values[key] = (raw_value, physical_value, unit)
        
    def update_display(self):
        """Update all displayed values"""
        for key, widget in self.signal_widgets.items():
            if key in self.current_values:
                raw, physical, unit = self.current_values[key]
                widget.update_value(raw, physical, unit)
                
    def on_item_clicked(self, item, column):
        """Handle item click"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
            
        if data["type"] == "signal":
            message = data["message"]
            signal = data["signal"]
            
            # Show signal details
            details = []
            details.append(f"Message: {message.name} (0x{message.frame_id:03X})")
            details.append(f"Signal: {signal.name}")
            details.append(f"")
            details.append(f"Start bit: {signal.start}")
            details.append(f"Length: {signal.length} bits")
            details.append(f"Byte order: {'Little Endian' if signal.byte_order == 'little_endian' else 'Big Endian'}")
            details.append(f"Type: {'Signed' if signal.is_signed else 'Unsigned'}")
            details.append(f"")
            details.append(f"Factor: {signal.scale}")
            details.append(f"Offset: {signal.offset}")
            details.append(f"Min: {signal.minimum}")
            details.append(f"Max: {signal.maximum}")
            
            if signal.unit:
                details.append(f"Unit: {signal.unit}")
                
            # Enumeration
            if hasattr(signal, 'choices') and signal.choices:
                details.append(f"")
                details.append(f"Énumérations:")
                for value, name in sorted(signal.choices.items()):
                    details.append(f"  {value}: {name}")
                    
            # Comment
            if signal.comment:
                details.append(f"")
                details.append(f"Description:")
                details.append(f"  {signal.comment}")
                
            self.details_text.setText("\n".join(details))
            
            self.signal_selected.emit(message.name, signal.name)
            
        elif data["type"] == "message":
            message = data["message"]
            
            details = []
            details.append(f"Message: {message.name}")
            details.append(f"CAN ID: 0x{message.frame_id:03X} ({message.frame_id})")
            details.append(f"DLC: {message.length} bytes")
            details.append(f"Signals: {len(message.signals)}")
            
            if message.comment:
                details.append(f"")
                details.append(f"Description:")
                details.append(f"  {message.comment}")
                
            details.append(f"")
            details.append(f"Signaux:")
            for sig in message.signals:
                details.append(f"  - {sig.name}")
                
            self.details_text.setText("\n".join(details))
            
            self.message_selected.emit(message.name)
        
        elif data["type"] == "raw_message":
            # Raw message without DBC
            can_id = data["can_id"]
            if can_id in self.raw_messages:
                msg_data, timestamp, _ = self.raw_messages[can_id]
                
                details = []
                details.append(f"Message: Unknown_0x{can_id:03X}")
                details.append(f"CAN ID: 0x{can_id:03X} ({can_id})")
                details.append(f"DLC: {len(msg_data)} bytes")
                details.append(f"")
                details.append(f"Données brutes:")
                details.append(f"  HEX: {' '.join(f'{b:02X}' for b in msg_data)}")
                details.append(f"  DEC: {' '.join(f'{b:3d}' for b in msg_data)}")
                details.append(f"  BIN: {' '.join(f'{b:08b}' for b in msg_data)}")
                details.append(f"")
                details.append(f"⚠️ Message non décodé")
                details.append(f"Aucune base de données (DBC/SYM) n'est chargée")
                details.append(f"ou ce message n'est pas défini dans la base.")
                
                self.details_text.setText("\n".join(details))
            
    def eventFilter(self, obj, event):
        """Handle right-click and middle-click on tree viewport"""
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QMouseEvent
        
        if obj == self.tree.viewport():
            if event.type() == QEvent.MouseButtonPress:
                mouse_event = event
                # Right click or middle click
                if mouse_event.button() == Qt.RightButton or mouse_event.button() == Qt.MiddleButton:
                    self.toggle_all_items()
                    return True
        
        return super().eventFilter(obj, event)
    
    def on_header_clicked(self, logical_index):
        """Handle header click"""
        if logical_index == 0:  # First column
            self.toggle_all_items()
    
    def toggle_all_items(self):
        """Toggle collapse/expand all items"""
        self.all_collapsed = not self.all_collapsed
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if self.all_collapsed:
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        
        # Update header text
        if self.all_collapsed:
            self.tree.headerItem().setText(0, "▶ Message / Signal")
        else:
            self.tree.headerItem().setText(0, "▼ Message / Signal")
    
    def filter_messages(self, text):
        """Filter messages/signals by search text"""
        text = text.lower()
        
        for i in range(self.tree.topLevelItemCount()):
            msg_item = self.tree.topLevelItem(i)
            msg_visible = False
            
            # Check message name
            if text in msg_item.text(0).lower() or text in msg_item.text(1).lower():
                msg_visible = True
                # Show all signals
                for j in range(msg_item.childCount()):
                    msg_item.child(j).setHidden(False)
            else:
                # Check signals
                for j in range(msg_item.childCount()):
                    sig_item = msg_item.child(j)
                    sig_visible = text in sig_item.text(0).lower()
                    sig_item.setHidden(not sig_visible)
                    if sig_visible:
                        msg_visible = True
                        
            msg_item.setHidden(not msg_visible)
            
    def sort_messages(self, sort_type):
        """Sort messages by different criteria"""
        # TODO: Implement sorting by activity
        pass
