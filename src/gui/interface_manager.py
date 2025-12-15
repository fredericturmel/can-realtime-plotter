"""
Interface Manager - Gestion complète des interfaces CAN
Panneau latéral pour gérer plusieurs interfaces CAN avec leurs DBC/SYM
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem,
                             QFrame, QProgressBar, QCheckBox, QMenu, QAction, QMessageBox,
                             QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QColor

class CanInterfaceWidget(QWidget):
    """Widget pour une interface CAN individuelle"""
    
    connect_requested = pyqtSignal(str)  # interface_id
    disconnect_requested = pyqtSignal(str)
    database_changed = pyqtSignal(str, str)  # interface_id, db_path
    
    def __init__(self, interface_id, interface_type, parent=None):
        super().__init__(parent)
        self.interface_id = interface_id
        self.interface_type = interface_type
        self.is_connected = False
        self.bus_load = 0.0
        self.message_count = 0
        self.error_count = 0
        self.database_path = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # En-tête avec nom d'interface éditable
        header_layout = QHBoxLayout()
        
        self.name_edit = QLineEdit(self.interface_id)
        self.name_edit.setPlaceholderText("Nom de l'interface")
        self.name_edit.setMaximumWidth(200)
        header_layout.addWidget(self.name_edit)
        
        # Type d'interface
        type_label = QLabel(f"[{self.interface_type}]")
        type_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        header_layout.addWidget(type_label)
        
        header_layout.addStretch()
        
        # Bouton de connexion
        self.connect_btn = QPushButton("Connecter")
        self.connect_btn.setCheckable(True)
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setFixedWidth(100)
        header_layout.addWidget(self.connect_btn)
        
        layout.addLayout(header_layout)
        
        # Sélection de base de données
        db_layout = QHBoxLayout()
        db_label = QLabel("DBC/SYM:")
        db_label.setFixedWidth(70)
        db_layout.addWidget(db_label)
        
        self.db_combo = QComboBox()
        self.db_combo.addItem("Aucune base de données", None)
        self.db_combo.currentIndexChanged.connect(self.on_database_changed)
        db_layout.addWidget(self.db_combo)
        
        self.db_btn = QPushButton("📁")
        self.db_btn.setFixedWidth(40)
        self.db_btn.clicked.connect(self.browse_database)
        self.db_btn.setToolTip("Parcourir...")
        db_layout.addWidget(self.db_btn)
        
        layout.addLayout(db_layout)
        
        # Bus load
        load_layout = QHBoxLayout()
        load_label = QLabel("Bus Load:")
        load_label.setFixedWidth(70)
        load_layout.addWidget(load_label)
        
        self.load_bar = QProgressBar()
        self.load_bar.setMaximum(100)
        self.load_bar.setTextVisible(True)
        self.load_bar.setFormat("%p%")
        self.load_bar.setFixedHeight(20)
        load_layout.addWidget(self.load_bar)
        
        layout.addLayout(load_layout)
        
        # Statistiques
        stats_layout = QHBoxLayout()
        
        self.msg_label = QLabel("Messages: 0")
        self.msg_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        stats_layout.addWidget(self.msg_label)
        
        stats_layout.addStretch()
        
        self.error_label = QLabel("Erreurs: 0")
        self.error_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        stats_layout.addWidget(self.error_label)
        
        layout.addLayout(stats_layout)
        
        # Style du widget
        self.setFrameStyle()
        
    def setFrameStyle(self):
        """Style du cadre de l'interface"""
        self.setStyleSheet("""
            CanInterfaceWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        
    def toggle_connection(self):
        """Toggle connection state"""
        if self.connect_btn.isChecked():
            # Vérifier si une base de données est nécessaire
            if self.interface_type != "virtual" and self.db_combo.currentData() is None:
                QMessageBox.warning(
                    self,
                    "Base de données requise",
                    "Une base de données DBC/SYM doit être chargée avant de connecter une interface physique."
                )
                self.connect_btn.setChecked(False)
                return
            self.connect_requested.emit(self.interface_id)
        else:
            self.disconnect_requested.emit(self.interface_id)
            
    def set_connected(self, connected):
        """Update connection state"""
        self.is_connected = connected
        self.connect_btn.setChecked(connected)
        
        if connected:
            self.connect_btn.setText("Déconnecter")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #238636;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #2ea043;
                }
            """)
            self.setStyleSheet("""
                CanInterfaceWidget {
                    background-color: #161b22;
                    border: 2px solid #238636;
                    border-radius: 8px;
                }
            """)
        else:
            self.connect_btn.setText("Connecter")
            self.connect_btn.setStyleSheet("")
            self.setFrameStyle()
            self.update_bus_load(0.0)
            
    def update_bus_load(self, load_percent):
        """Update bus load display"""
        self.bus_load = load_percent
        self.load_bar.setValue(int(load_percent))
        
        # Couleur selon la charge
        if load_percent < 50:
            color = "#238636"  # Vert
        elif load_percent < 80:
            color = "#d29922"  # Orange
        else:
            color = "#da3633"  # Rouge
            
        self.load_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
    def update_statistics(self, message_count, error_count):
        """Update statistics display"""
        self.message_count = message_count
        self.error_count = error_count
        self.msg_label.setText(f"Messages: {message_count}")
        self.error_label.setText(f"Erreurs: {error_count}")
        
    def add_database(self, name, path):
        """Add a database to the combo box"""
        self.db_combo.addItem(name, path)
        
    def on_database_changed(self, index):
        """Database selection changed"""
        db_path = self.db_combo.itemData(index)
        if db_path:
            self.database_path = db_path
            self.database_changed.emit(self.interface_id, db_path)
            
    def browse_database(self):
        """Browse for database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une base de données",
            "",
            "Database Files (*.dbc *.sym);;All Files (*)"
        )
        
        if file_path:
            import os
            file_name = os.path.basename(file_path)
            # Check if already in combo
            found = False
            for i in range(self.db_combo.count()):
                if self.db_combo.itemData(i) == file_path:
                    self.db_combo.setCurrentIndex(i)
                    found = True
                    break
                    
            if not found:
                self.db_combo.addItem(file_name, file_path)
                self.db_combo.setCurrentIndex(self.db_combo.count() - 1)


class InterfaceManagerPanel(QWidget):
    """Panneau de gestion des interfaces CAN"""
    
    interface_added = pyqtSignal(str, str)  # interface_id, interface_type
    interface_removed = pyqtSignal(str)
    connection_requested = pyqtSignal(str, str, str)  # interface_id, interface_type, db_path
    disconnection_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interfaces = {}  # interface_id -> CanInterfaceWidget
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        
        title = QLabel("🔌 Interfaces CAN")
        title.setStyleSheet("font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("+")
        add_btn.clicked.connect(self.add_interface_dialog)
        add_btn.setFixedSize(32, 32)
        add_btn.setToolTip("Ajouter une interface CAN")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #c9d1d9;
                border: none;
                font-size: 22px;
                font-weight: 300;
                padding: 0px;
            }
            QPushButton:hover {
                color: #58a6ff;
                background-color: #21262d;
                border-radius: 4px;
            }
            QPushButton:pressed {
                color: #58a6ff;
                background-color: #161b22;
            }
        """)
        header_layout.addWidget(add_btn)
        
        layout.addWidget(header)
        
        # Scroll area pour les interfaces
        from PyQt5.QtWidgets import QScrollArea
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.interfaces_container = QWidget()
        self.interfaces_layout = QVBoxLayout(self.interfaces_container)
        self.interfaces_layout.setContentsMargins(12, 12, 12, 12)
        self.interfaces_layout.setSpacing(12)
        self.interfaces_layout.addStretch()
        
        scroll.setWidget(self.interfaces_container)
        layout.addWidget(scroll)
        
    def detect_hardware_devices(self):
        """Detect all connected CAN hardware devices"""
        devices = []
        
        # Detect PCAN devices
        try:
            import can
            for i in range(1, 17):  # Check PCAN_USBBUS1-16
                channel = f"PCAN_USBBUS{i}"
                try:
                    bus = can.Bus(interface='pcan', channel=channel, bitrate=500000, receive_own_messages=False)
                    bus.shutdown()
                    devices.append(("PCAN", channel))
                except:
                    pass
        except:
            pass
        
        # Detect IXXAT devices
        try:
            import can
            for i in range(4):  # Check channels 0-3
                try:
                    bus = can.Bus(interface='ixxat', channel=i, bitrate=500000, receive_own_messages=False)
                    bus.shutdown()
                    devices.append(("IXXAT", str(i)))
                except:
                    pass  # Channel not available
        except:
            pass
        
        # Detect SocketCAN interfaces (Linux only)
        try:
            import os
            import platform
            if platform.system() == "Linux" and os.path.exists("/sys/class/net"):
                channels = [f for f in os.listdir("/sys/class/net") 
                          if f.startswith("can") or f.startswith("vcan")]
                for channel in sorted(channels):
                    devices.append(("SocketCAN", channel))
        except:
            pass
        
        return devices
    
    def add_interface_dialog(self):
        """Show dialog to add new interface with hardware detection first"""
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QRadioButton, QButtonGroup, QLabel
        import can
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une interface CAN")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        # Name field
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Mon Interface CAN")
        form.addRow("Nom:", name_edit)
        
        # Device selection combo with refresh button
        device_layout = QHBoxLayout()
        device_combo = QComboBox()
        device_combo.setMinimumHeight(32)
        device_layout.addWidget(device_combo)
        
        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Rafraîchir la liste des périphériques")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        device_layout.addWidget(refresh_btn)
        
        # Manual type selection combo (hidden by default)
        manual_type_combo = QComboBox()
        manual_type_combo.addItems(["PCAN", "IXXAT"])
        manual_type_combo.setMinimumHeight(32)
        manual_type_combo.hide()
        
        # Manual channel input (hidden by default)
        manual_channel_edit = QLineEdit()
        manual_channel_edit.setPlaceholderText("Ex: PCAN_USBBUS1 ou 0")
        manual_channel_edit.hide()
        
        # Function to populate device list
        def populate_devices():
            """Populate device combo with detected devices"""
            device_combo.clear()
            detected_devices = self.detect_hardware_devices()
            
            if detected_devices:
                device_combo.addItem("🔍 Périphériques détectés:", "header")
                for dev_type, channel in detected_devices:
                    device_combo.addItem(f"  {dev_type} - {channel}", (dev_type, channel))
                device_combo.insertSeparator(device_combo.count())
            else:
                device_combo.addItem("⚠️ Aucun périphérique détecté", "no_device")
                device_combo.insertSeparator(device_combo.count())
            
            device_combo.addItem("⚙️ Configuration manuelle", "manual")
            device_combo.insertSeparator(device_combo.count())
            device_combo.addItem("🖥️ SocketCAN / Virtual", "virtual")
        
        # Initial population
        populate_devices()
        
        # Connect refresh button
        refresh_btn.clicked.connect(populate_devices)
        
        form.addRow("Périphérique:", device_layout)
        
        # Add manual type row (initially hidden)
        type_row_label = QLabel("Type:")
        form.addRow(type_row_label, manual_type_combo)
        type_row_label.hide()
        
        # Add manual channel row (initially hidden)
        channel_row_label = QLabel("Canal:")
        form.addRow(channel_row_label, manual_channel_edit)
        channel_row_label.hide()
        
        # Virtual interface options (initially hidden)
        virtual_type_combo = QComboBox()
        virtual_type_combo.addItems(["Virtual CAN", "SocketCAN (can0)", "SocketCAN (vcan0)"])
        virtual_type_combo.setMinimumHeight(32)
        virtual_type_combo.hide()
        
        virtual_row_label = QLabel("Interface:")
        form.addRow(virtual_row_label, virtual_type_combo)
        virtual_row_label.hide()
        
        # Store interface info
        selected_interface = {"type": None, "channel": None}
        
        def on_device_changed():
            """Handle device selection change"""
            current_data = device_combo.currentData()
            
            # Hide all manual/virtual options first
            manual_type_combo.hide()
            manual_channel_edit.hide()
            type_row_label.hide()
            channel_row_label.hide()
            virtual_type_combo.hide()
            virtual_row_label.hide()
            
            if current_data == "header" or current_data == "no_device":
                # Header item or no device message, select next valid item
                device_combo.setCurrentIndex(device_combo.currentIndex() + 1)
                return
            elif current_data == "manual":
                # Show manual configuration
                manual_type_combo.show()
                manual_channel_edit.show()
                type_row_label.show()
                channel_row_label.show()
                selected_interface["type"] = manual_type_combo.currentText()
                selected_interface["channel"] = None
            elif current_data == "virtual":
                # Show virtual options
                virtual_type_combo.show()
                virtual_row_label.show()
                selected_interface["type"] = "Virtual"
                selected_interface["channel"] = "virtual"
            elif isinstance(current_data, tuple):
                # Detected device selected
                dev_type, channel = current_data
                selected_interface["type"] = dev_type
                selected_interface["channel"] = channel
        
        device_combo.currentIndexChanged.connect(on_device_changed)
        
        # Manual type changed
        def on_manual_type_changed():
            selected_interface["type"] = manual_type_combo.currentText()
        
        manual_type_combo.currentTextChanged.connect(on_manual_type_changed)
        
        # Virtual type changed
        def on_virtual_type_changed():
            vtype = virtual_type_combo.currentText()
            if vtype == "Virtual CAN":
                selected_interface["type"] = "Virtual"
                selected_interface["channel"] = "virtual"
            elif "can0" in vtype:
                selected_interface["type"] = "SocketCAN"
                selected_interface["channel"] = "can0"
            elif "vcan0" in vtype:
                selected_interface["type"] = "SocketCAN"
                selected_interface["channel"] = "vcan0"
        
        virtual_type_combo.currentTextChanged.connect(on_virtual_type_changed)
        
        # Initialize with first valid selection
        on_device_changed()
        
        # Bitrate
        bitrate_combo = QComboBox()
        bitrate_combo.addItems(["125000", "250000", "500000", "1000000"])
        bitrate_combo.setCurrentText("500000")
        bitrate_combo.setMinimumHeight(32)
        form.addRow("Bitrate:", bitrate_combo)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            interface_name = name_edit.text() or f"Interface_{len(self.interfaces)+1}"
            interface_type = selected_interface["type"]
            
            # Get channel based on selection mode
            if device_combo.currentData() == "manual":
                channel = manual_channel_edit.text()
                if not channel:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(dialog, "Erreur", "Veuillez saisir un canal")
                    return
            else:
                channel = selected_interface["channel"]
            
            self.add_interface(interface_name, interface_type)
            
    def add_interface(self, interface_id, interface_type):
        """Add a new CAN interface widget"""
        widget = CanInterfaceWidget(interface_id, interface_type)
        
        # Connect signals
        widget.connect_requested.connect(self.on_connect_requested)
        widget.disconnect_requested.connect(self.on_disconnect_requested)
        
        self.interfaces[interface_id] = widget
        
        # Insert before stretch
        self.interfaces_layout.insertWidget(
            self.interfaces_layout.count() - 1,
            widget
        )
        
        self.interface_added.emit(interface_id, interface_type)
        
    def on_connect_requested(self, interface_id):
        """Handle connection request"""
        widget = self.interfaces.get(interface_id)
        if widget:
            db_path = widget.database_path
            self.connection_requested.emit(
                interface_id,
                widget.interface_type,
                db_path or ""
            )
            
    def on_disconnect_requested(self, interface_id):
        """Handle disconnection request"""
        self.disconnection_requested.emit(interface_id)
        
    def set_interface_connected(self, interface_id, connected):
        """Update interface connection state"""
        if interface_id in self.interfaces:
            self.interfaces[interface_id].set_connected(connected)
            
    def update_interface_bus_load(self, interface_id, load_percent):
        """Update interface bus load"""
        if interface_id in self.interfaces:
            self.interfaces[interface_id].update_bus_load(load_percent)
            
    def update_interface_statistics(self, interface_id, message_count, error_count):
        """Update interface statistics"""
        if interface_id in self.interfaces:
            self.interfaces[interface_id].update_statistics(message_count, error_count)
