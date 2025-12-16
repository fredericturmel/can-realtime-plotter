"""
Interface Manager V2 - Gestion des interfaces CAN en tableau
Vue tabulaire avec expansion pour gestion DBC
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem,
                             QFrame, QProgressBar, QCheckBox, QMenu, QAction, QMessageBox,
                             QFileDialog, QHeaderView, QDialog, QFormLayout, QDialogButtonBox,
                             QStyledItemDelegate, QStyleOptionButton, QStyle, QApplication,
                             QTreeWidget, QTreeWidgetItem, QAbstractItemView, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRect, QSize, QPoint
from PyQt5.QtGui import QIcon, QColor, QPainter, QBrush, QPen
import time


class CheckBoxDelegate(QStyledItemDelegate):
    """Delegate for checkbox in table cell"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_rows = set()
    
    def paint(self, painter, option, index):
        """Draw checkbox"""
        # Center checkbox
        checkbox_rect = QApplication.style().subElementRect(
            QStyle.SE_CheckBoxIndicator, 
            option, 
            None
        )
        checkbox_rect.moveCenter(option.rect.center())
        
        # Draw checkbox
        checkbox_option = QStyleOptionButton()
        checkbox_option.rect = checkbox_rect
        checkbox_option.state = QStyle.State_Enabled
        
        if index.row() in self.checked_rows:
            checkbox_option.state |= QStyle.State_On
        else:
            checkbox_option.state |= QStyle.State_Off
        
        QApplication.style().drawControl(
            QStyle.CE_CheckBox,
            checkbox_option,
            painter
        )
    
    def editorEvent(self, event, model, option, index):
        """Handle click on checkbox"""
        if event.type() == event.MouseButtonRelease:
            if index.row() in self.checked_rows:
                self.checked_rows.remove(index.row())
            else:
                self.checked_rows.add(index.row())
            return True
        return False


class InterfaceTableWidget(QTableWidget):
    """Custom table widget for CAN interfaces"""
    
    interface_toggled = pyqtSignal(int, bool)  # row, enabled
    interface_edited = pyqtSignal(int)  # row
    interface_deleted = pyqtSignal(int)  # row
    dbc_section_toggled = pyqtSignal(int, bool)  # row, expanded
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interface_data = []  # List of interface configs
        self.expanded_rows = set()
        
        self.setup_table()
    
    def setup_table(self):
        """Configure table appearance"""
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "✓", "Nom", "Type", "Canal", "Débit", "Bus Load", "État"
        ])
        
        # Set column widths
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Channel
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Bitrate
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Bus Load
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
        
        self.setColumnWidth(0, 40)
        
        # Style
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Enable sorting
        self.setSortingEnabled(True)
        
    def add_interface(self, interface_config):
        """Add an interface to the table
        
        Args:
            interface_config: dict with keys: name, type, channel, bitrate, enabled
        """
        row = self.rowCount()
        self.insertRow(row)
        
        # Store config
        self.interface_data.append(interface_config)
        
        # Checkbox column
        checkbox_item = QTableWidgetItem()
        checkbox_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        checkbox_item.setCheckState(Qt.Checked if interface_config.get('enabled', False) else Qt.Unchecked)
        checkbox_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 0, checkbox_item)
        
        # Name
        name_item = QTableWidgetItem(interface_config['name'])
        self.setItem(row, 1, name_item)
        
        # Type
        type_item = QTableWidgetItem(interface_config['type'])
        type_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 2, type_item)
        
        # Channel
        channel_item = QTableWidgetItem(interface_config['channel'])
        channel_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 3, channel_item)
        
        # Bitrate (format appropriately)
        bitrate = interface_config['bitrate']
        if bitrate >= 1000000:
            bitrate_text = f"{bitrate / 1000000:.1f} Mbit/s"
        elif bitrate >= 1000:
            bitrate_text = f"{bitrate / 1000:.0f} kbit/s"
        else:
            bitrate_text = f"{bitrate} bit/s"
        bitrate_item = QTableWidgetItem(bitrate_text)
        bitrate_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 4, bitrate_item)
        
        # Bus Load (progress bar)
        bus_load_item = QTableWidgetItem("")
        self.setItem(row, 5, bus_load_item)
        
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(0)
        progress.setTextVisible(True)
        progress.setFormat("%p%")
        progress.setFixedHeight(20)
        self.setCellWidget(row, 5, progress)
        
        # Status
        status_item = QTableWidgetItem("● Déconnecté")
        status_item.setForeground(QColor("#8b949e"))
        self.setItem(row, 6, status_item)
        
        return row
    
    def update_bus_load(self, row, load_percent):
        """Update bus load for a row"""
        if row < self.rowCount():
            progress = self.cellWidget(row, 5)
            if progress:
                progress.setValue(int(load_percent))
                
                # Update color
                if load_percent < 50:
                    color = "#238636"
                elif load_percent < 80:
                    color = "#d29922"
                else:
                    color = "#da3633"
                
                progress.setStyleSheet(f"""
                    QProgressBar::chunk {{
                        background-color: {color};
                        border-radius: 3px;
                    }}
                """)
    
    def update_status(self, row, connected, message=""):
        """Update connection status"""
        if row < self.rowCount():
            status_item = self.item(row, 6)
            if connected:
                status_item.setText("● Connecté")
                status_item.setForeground(QColor("#238636"))
            else:
                status_item.setText("● Déconnecté")
                status_item.setForeground(QColor("#8b949e"))
    
    def show_context_menu(self, pos):
        """Show context menu on row"""
        item = self.itemAt(pos)
        if not item:
            return
        
        row = item.row()
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
            }
        """)
        
        edit_action = menu.addAction("✏️ Éditer")
        dbc_action = menu.addAction("📁 Gérer les DBC")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == edit_action:
            self.interface_edited.emit(row)
        elif action == dbc_action:
            self.dbc_section_toggled.emit(row, True)
        elif action == delete_action:
            self.interface_deleted.emit(row)
    
    def toggle_dbc_section(self, row):
        """Toggle DBC management section for a row"""
        if row in self.expanded_rows:
            self.expanded_rows.remove(row)
            # Remove DBC widget if exists
            # TODO: Implement collapsible section
        else:
            self.expanded_rows.add(row)
            # Show DBC widget
            # TODO: Implement collapsible section
        
        self.dbc_section_toggled.emit(row, row in self.expanded_rows)


class InterfaceManagerPanel(QWidget):
    """Panneau de gestion des interfaces CAN en tableau"""
    
    interface_added = pyqtSignal(str, str)  # interface_id, interface_type
    interface_removed = pyqtSignal(str)
    connection_requested = pyqtSignal(str, str, str)  # interface_id, interface_type, db_path
    disconnection_requested = pyqtSignal(str)
    database_changed = pyqtSignal(str, str)  # interface_id, db_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interfaces = {}  # interface_id -> config with 'dbc_files': []
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
        
        # Add button
        add_btn = QPushButton("+ Ajouter")
        add_btn.clicked.connect(self.add_interface_dialog)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
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
        header_layout.addWidget(add_btn)
        
        layout.addWidget(header)
        
        # Table
        self.table = InterfaceTableWidget()
        self.table.interface_edited.connect(self.edit_interface)
        self.table.interface_deleted.connect(self.delete_interface)
        self.table.dbc_section_toggled.connect(self.on_dbc_section_toggled)
        self.table.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.table)
        
    def on_item_changed(self, item):
        """Handle item change (checkbox toggle)"""
        if item.column() == 0:  # Checkbox column
            row = item.row()
            enabled = item.checkState() == Qt.Checked
            
            # Emit connection/disconnection signal
            if row < len(self.table.interface_data):
                interface_id = self.table.interface_data[row].get('name', f"Interface_{row}")
                
                if enabled:
                    interface_type = self.table.interface_data[row]['type']
                    self.connection_requested.emit(interface_id, interface_type, "")
                else:
                    self.disconnection_requested.emit(interface_id)
    
    def detect_hardware_devices(self):
        """Detect all connected CAN hardware devices"""
        devices = []
        
        # Detect PCAN devices
        try:
            import can
            for i in range(1, 17):
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
            for i in range(4):
                try:
                    bus = can.Bus(interface='ixxat', channel=i, bitrate=500000, receive_own_messages=False)
                    bus.shutdown()
                    devices.append(("IXXAT", str(i)))
                except:
                    pass
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
        """Show dialog to add new interface"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une interface CAN")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        # Name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Mon Interface CAN")
        form.addRow("Nom:", name_edit)
        
        # Device selection with refresh
        device_layout = QHBoxLayout()
        device_combo = QComboBox()
        device_combo.setMinimumHeight(32)
        device_layout.addWidget(device_combo)
        
        refresh_btn = QPushButton("⟳")
        refresh_btn.setFixedSize(32, 32)
        refresh_btn.setToolTip("Rafraîchir la liste des périphériques")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        device_layout.addWidget(refresh_btn)
        
        # Manual configuration
        manual_type_combo = QComboBox()
        manual_type_combo.addItems(["PCAN", "IXXAT"])
        manual_type_combo.setMinimumHeight(32)
        manual_type_combo.hide()
        
        manual_channel_edit = QLineEdit()
        manual_channel_edit.setPlaceholderText("Ex: PCAN_USBBUS1 ou 0")
        manual_channel_edit.hide()
        
        # Virtual options
        virtual_type_combo = QComboBox()
        virtual_type_combo.addItems(["Virtual CAN", "SocketCAN (can0)", "SocketCAN (vcan0)"])
        virtual_type_combo.setMinimumHeight(32)
        virtual_type_combo.hide()
        
        virtual_row_label = QLabel("Interface:")
        
        def populate_devices():
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
        
        populate_devices()
        refresh_btn.clicked.connect(populate_devices)
        
        form.addRow("Périphérique:", device_layout)
        
        # Manual type/channel rows
        type_row_label = QLabel("Type:")
        form.addRow(type_row_label, manual_type_combo)
        type_row_label.hide()
        
        channel_row_label = QLabel("Canal:")
        form.addRow(channel_row_label, manual_channel_edit)
        channel_row_label.hide()
        
        # Virtual row
        form.addRow(virtual_row_label, virtual_type_combo)
        virtual_row_label.hide()
        
        selected_interface = {"type": None, "channel": None}
        
        def on_device_changed():
            current_data = device_combo.currentData()
            
            manual_type_combo.hide()
            manual_channel_edit.hide()
            type_row_label.hide()
            channel_row_label.hide()
            virtual_type_combo.hide()
            virtual_row_label.hide()
            
            if current_data == "header" or current_data == "no_device":
                device_combo.setCurrentIndex(device_combo.currentIndex() + 1)
                return
            elif current_data == "manual":
                manual_type_combo.show()
                manual_channel_edit.show()
                type_row_label.show()
                channel_row_label.show()
                selected_interface["type"] = manual_type_combo.currentText()
                selected_interface["channel"] = None
            elif current_data == "virtual":
                virtual_type_combo.show()
                virtual_row_label.show()
                selected_interface["type"] = "Virtual"
                selected_interface["channel"] = "virtual"
            elif isinstance(current_data, tuple):
                dev_type, channel = current_data
                selected_interface["type"] = dev_type
                selected_interface["channel"] = channel
        
        device_combo.currentIndexChanged.connect(on_device_changed)
        manual_type_combo.currentTextChanged.connect(lambda: selected_interface.update({"type": manual_type_combo.currentText()}))
        
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
        on_device_changed()
        
        # Bitrate
        bitrate_spin = QSpinBox()
        bitrate_spin.setMinimum(10000)
        bitrate_spin.setMaximum(5000000)
        bitrate_spin.setSingleStep(125000)
        bitrate_spin.setValue(500000)
        bitrate_spin.setSuffix(" bit/s")
        bitrate_spin.setMinimumHeight(32)
        form.addRow("Débit:", bitrate_spin)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            interface_name = name_edit.text() or f"Interface_{len(self.interfaces)+1}"
            interface_type = selected_interface["type"]
            
            if device_combo.currentData() == "manual":
                channel = manual_channel_edit.text()
                if not channel:
                    QMessageBox.warning(dialog, "Erreur", "Veuillez saisir un canal")
                    return
            else:
                channel = selected_interface["channel"]
            
            # Add to table
            config = {
                'name': interface_name,
                'type': interface_type,
                'channel': channel,
                'bitrate': bitrate_spin.value(),
                'enabled': False,
                'dbc_files': []  # List of DBC file paths
            }
            
            row = self.table.add_interface(config)
            self.interfaces[interface_name] = config
            self.interface_added.emit(interface_name, interface_type)
    
    def edit_interface(self, row):
        """Edit an interface"""
        if row >= len(self.table.interface_data):
            return
        
        config = self.table.interface_data[row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Éditer l'interface")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        name_edit = QLineEdit(config['name'])
        form.addRow("Nom:", name_edit)
        
        channel_edit = QLineEdit(config['channel'])
        form.addRow("Canal:", channel_edit)
        
        bitrate_spin = QSpinBox()
        bitrate_spin.setMinimum(10000)
        bitrate_spin.setMaximum(5000000)
        bitrate_spin.setSingleStep(125000)
        bitrate_spin.setValue(config['bitrate'])
        bitrate_spin.setSuffix(" bit/s")
        form.addRow("Débit:", bitrate_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Update config
            old_name = config['name']
            config['name'] = name_edit.text()
            config['channel'] = channel_edit.text()
            config['bitrate'] = bitrate_spin.value()
            
            # Update table
            self.table.item(row, 1).setText(config['name'])
            self.table.item(row, 3).setText(config['channel'])
            
            bitrate = config['bitrate']
            if bitrate >= 1000000:
                bitrate_text = f"{bitrate / 1000000:.1f} Mbit/s"
            elif bitrate >= 1000:
                bitrate_text = f"{bitrate / 1000:.0f} kbit/s"
            else:
                bitrate_text = f"{bitrate} bit/s"
            self.table.item(row, 4).setText(bitrate_text)
            
            # Update interfaces dict
            if old_name in self.interfaces:
                del self.interfaces[old_name]
            self.interfaces[config['name']] = config
    
    def delete_interface(self, row):
        """Delete an interface"""
        if row >= len(self.table.interface_data):
            return
        
        config = self.table.interface_data[row]
        
        reply = QMessageBox.question(
            self,
            "Supprimer l'interface",
            f"Voulez-vous vraiment supprimer l'interface '{config['name']}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Emit signal
            self.interface_removed.emit(config['name'])
            
            # Remove from table
            self.table.removeRow(row)
            self.table.interface_data.pop(row)
            
            # Remove from dict
            if config['name'] in self.interfaces:
                del self.interfaces[config['name']]
    
    def on_dbc_section_toggled(self, row, expanded):
        """Handle DBC section toggle - show DBC management dialog"""
        if row >= len(self.table.interface_data):
            return
        
        config = self.table.interface_data[row]
        interface_name = config['name']
        
        # Create DBC management dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Gérer les DBC - {interface_name}")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        info_label = QLabel(f"Bases de données pour l'interface: <b>{interface_name}</b>")
        layout.addWidget(info_label)
        
        # DBC list
        dbc_list = QTreeWidget()
        dbc_list.setHeaderLabels(["Fichier DBC/SYM", "Chemin"])
        dbc_list.setAlternatingRowColors(True)
        dbc_list.setRootIsDecorated(False)
        
        # Populate with existing DBCs
        if 'dbc_files' not in config:
            config['dbc_files'] = []
        
        for dbc_path in config['dbc_files']:
            import os
            filename = os.path.basename(dbc_path)
            item = QTreeWidgetItem([filename, dbc_path])
            dbc_list.addTopLevelItem(item)
        
        dbc_list.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        dbc_list.header().setSectionResizeMode(1, QHeaderView.Stretch)
        
        layout.addWidget(dbc_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Ajouter DBC")
        add_btn.setStyleSheet("""
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
        
        def add_dbc():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog,
                "Sélectionner une base de données",
                "",
                "Database Files (*.dbc *.sym);;All Files (*)"
            )
            
            if file_path:
                import os
                filename = os.path.basename(file_path)
                
                # Check if already added
                if file_path in config['dbc_files']:
                    QMessageBox.warning(dialog, "DBC déjà ajouté", "Cette base de données est déjà dans la liste.")
                    return
                
                # Add to config
                config['dbc_files'].append(file_path)
                
                # Add to list
                item = QTreeWidgetItem([filename, file_path])
                dbc_list.addTopLevelItem(item)
                
                # Emit signal for first DBC or if interface is connected
                if len(config['dbc_files']) == 1 or config.get('enabled', False):
                    self.database_changed.emit(interface_name, file_path)
        
        add_btn.clicked.connect(add_dbc)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("− Supprimer")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #da3633;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e5534b;
            }
        """)
        
        def remove_dbc():
            current_item = dbc_list.currentItem()
            if not current_item:
                QMessageBox.warning(dialog, "Aucune sélection", "Veuillez sélectionner un fichier à supprimer.")
                return
            
            file_path = current_item.text(1)
            
            reply = QMessageBox.question(
                dialog,
                "Supprimer DBC",
                f"Voulez-vous vraiment supprimer cette base de données ?\n\n{current_item.text(0)}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Remove from config
                if file_path in config['dbc_files']:
                    config['dbc_files'].remove(file_path)
                
                # Remove from list
                index = dbc_list.indexOfTopLevelItem(current_item)
                dbc_list.takeTopLevelItem(index)
        
        remove_btn.clicked.connect(remove_dbc)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def set_interface_connected(self, interface_id, connected):
        """Update interface connection state"""
        for row, config in enumerate(self.table.interface_data):
            if config['name'] == interface_id:
                self.table.update_status(row, connected)
                break
    
    def update_interface_bus_load(self, interface_id, load_percent):
        """Update interface bus load"""
        for row, config in enumerate(self.table.interface_data):
            if config['name'] == interface_id:
                self.table.update_bus_load(row, load_percent)
                break
    
    def update_interface_statistics(self, interface_id, message_count, error_count):
        """Update interface statistics"""
        # Could add columns for message/error count if needed
        pass
