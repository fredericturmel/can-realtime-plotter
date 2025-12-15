"""
Configuration Panel

Panel for managing DBC files and interface configuration.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLabel, QFileDialog, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigurationPanel(QWidget):
    """Panel for managing DBC files and configuration."""
    
    dbc_loaded = pyqtSignal(str)  # Signal when DBC is loaded
    dbc_removed = pyqtSignal(str)  # Signal when DBC is removed
    
    def __init__(self, db_parser, parent=None):
        super().__init__(parent)
        self.db_parser = db_parser
        self.loaded_dbc_files = {}  # path -> info dict
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("⚙️ Configuration & Database Management")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # DBC Management Group
        dbc_group = QGroupBox("📚 DBC Database Files")
        dbc_layout = QVBoxLayout()
        dbc_layout.setContentsMargins(16, 20, 16, 16)
        dbc_layout.setSpacing(12)
        
        # DBC Table
        self.dbc_table = QTableWidget()
        self.dbc_table.setColumnCount(4)
        self.dbc_table.setHorizontalHeaderLabels(['File Name', 'Path', 'Messages', 'Status'])
        self.dbc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.dbc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.dbc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.dbc_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.dbc_table.setAlternatingRowColors(True)
        self.dbc_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dbc_table.setMinimumHeight(200)
        dbc_layout.addWidget(self.dbc_table)
        
        # DBC Buttons
        dbc_btn_layout = QHBoxLayout()
        dbc_btn_layout.setSpacing(8)
        
        self.add_dbc_btn = QPushButton("➕ Add DBC/SYM")
        self.add_dbc_btn.setObjectName("primaryButton")
        self.add_dbc_btn.setMinimumHeight(36)
        self.add_dbc_btn.clicked.connect(self.add_dbc_file)
        dbc_btn_layout.addWidget(self.add_dbc_btn)
        
        self.remove_dbc_btn = QPushButton("➖ Remove Selected")
        self.remove_dbc_btn.setObjectName("dangerButton")
        self.remove_dbc_btn.setMinimumHeight(36)
        self.remove_dbc_btn.clicked.connect(self.remove_selected_dbc)
        self.remove_dbc_btn.setEnabled(False)
        dbc_btn_layout.addWidget(self.remove_dbc_btn)
        
        self.reload_dbc_btn = QPushButton("🔄 Reload Selected")
        self.reload_dbc_btn.setMinimumHeight(36)
        self.reload_dbc_btn.clicked.connect(self.reload_selected_dbc)
        self.reload_dbc_btn.setEnabled(False)
        dbc_btn_layout.addWidget(self.reload_dbc_btn)
        
        dbc_btn_layout.addStretch()
        dbc_layout.addLayout(dbc_btn_layout)
        
        # Info label
        self.info_label = QLabel("💡 Tip: Load multiple DBC files to work with different CAN networks")
        self.info_label.setObjectName("subtitleLabel")
        dbc_layout.addWidget(self.info_label)
        
        dbc_group.setLayout(dbc_layout)
        layout.addWidget(dbc_group)
        
        # Quick Stats Group
        stats_group = QGroupBox("📊 Database Statistics")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(16, 20, 16, 16)
        stats_layout.setSpacing(12)
        
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(20)
        
        self.total_messages_label = QLabel("📨 Total Messages: 0")
        self.total_messages_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        stats_grid.addWidget(self.total_messages_label)
        
        self.total_signals_label = QLabel("📊 Total Signals: 0")
        self.total_signals_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        stats_grid.addWidget(self.total_signals_label)
        
        self.loaded_files_label = QLabel("📁 Loaded Files: 0")
        self.loaded_files_label.setStyleSheet("font-size: 10pt; font-weight: bold;")
        stats_grid.addWidget(self.loaded_files_label)
        
        stats_grid.addStretch()
        stats_layout.addLayout(stats_grid)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        # Connect signals
        self.dbc_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def add_dbc_file(self):
        """Add a new DBC/SYM file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Database File",
            "",
            "Database Files (*.dbc *.sym);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Check if already loaded
        if file_path in self.loaded_dbc_files:
            QMessageBox.information(self, "Info", "This file is already loaded")
            return
        
        # Try to load the file
        if self.db_parser.load_database(file_path):
            path_obj = Path(file_path)
            messages = self.db_parser.get_messages()
            signals = self.db_parser.get_all_signals()
            
            # Store info
            self.loaded_dbc_files[file_path] = {
                'name': path_obj.name,
                'path': file_path,
                'messages': len(messages),
                'signals': len(signals),
                'status': '✅ Loaded'
            }
            
            # Add to table
            self.update_dbc_table()
            self.update_stats()
            
            # Emit signal
            self.dbc_loaded.emit(file_path)
            
            QMessageBox.information(
                self,
                "Success",
                f"Loaded {len(messages)} messages and {len(signals)} signals"
            )
        else:
            error_msg = "Failed to load database file.\n\n"
            if file_path.lower().endswith('.sym'):
                error_msg += "⚠️ SYM File Issue:\n"
                error_msg += "Only SYM version 6.0 is supported.\n\n"
                error_msg += "Please convert to DBC format or SYM v6.0"
            
            QMessageBox.critical(self, "Error", error_msg)
    
    def remove_selected_dbc(self):
        """Remove the selected DBC file."""
        selected_rows = self.dbc_table.selectedItems()
        if not selected_rows:
            return
        
        row = self.dbc_table.currentRow()
        if row < 0:
            return
        
        file_path = self.dbc_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove database file?\n\n{Path(file_path).name}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if file_path in self.loaded_dbc_files:
                del self.loaded_dbc_files[file_path]
                self.update_dbc_table()
                self.update_stats()
                self.dbc_removed.emit(file_path)
    
    def reload_selected_dbc(self):
        """Reload the selected DBC file."""
        row = self.dbc_table.currentRow()
        if row < 0:
            return
        
        file_path = self.dbc_table.item(row, 1).text()
        
        if self.db_parser.load_database(file_path):
            messages = self.db_parser.get_messages()
            signals = self.db_parser.get_all_signals()
            
            self.loaded_dbc_files[file_path]['messages'] = len(messages)
            self.loaded_dbc_files[file_path]['signals'] = len(signals)
            self.loaded_dbc_files[file_path]['status'] = '✅ Reloaded'
            
            self.update_dbc_table()
            self.update_stats()
            
            QMessageBox.information(self, "Success", "Database file reloaded successfully")
        else:
            QMessageBox.critical(self, "Error", "Failed to reload database file")
    
    def update_dbc_table(self):
        """Update the DBC table display."""
        self.dbc_table.setRowCount(0)
        
        for file_path, info in self.loaded_dbc_files.items():
            row = self.dbc_table.rowCount()
            self.dbc_table.insertRow(row)
            
            # File name
            name_item = QTableWidgetItem(info['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.dbc_table.setItem(row, 0, name_item)
            
            # Path
            path_item = QTableWidgetItem(info['path'])
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            path_item.setToolTip(info['path'])
            self.dbc_table.setItem(row, 1, path_item)
            
            # Messages count
            msg_item = QTableWidgetItem(str(info['messages']))
            msg_item.setFlags(msg_item.flags() & ~Qt.ItemIsEditable)
            msg_item.setTextAlignment(Qt.AlignCenter)
            self.dbc_table.setItem(row, 2, msg_item)
            
            # Status
            status_item = QTableWidgetItem(info['status'])
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            status_item.setTextAlignment(Qt.AlignCenter)
            self.dbc_table.setItem(row, 3, status_item)
    
    def update_stats(self):
        """Update statistics labels."""
        total_messages = sum(info['messages'] for info in self.loaded_dbc_files.values())
        total_signals = sum(info['signals'] for info in self.loaded_dbc_files.values())
        loaded_files = len(self.loaded_dbc_files)
        
        self.total_messages_label.setText(f"📨 Total Messages: {total_messages}")
        self.total_signals_label.setText(f"📊 Total Signals: {total_signals}")
        self.loaded_files_label.setText(f"📁 Loaded Files: {loaded_files}")
    
    def on_selection_changed(self):
        """Handle selection change in DBC table."""
        has_selection = len(self.dbc_table.selectedItems()) > 0
        self.remove_dbc_btn.setEnabled(has_selection)
        self.reload_dbc_btn.setEnabled(has_selection)
    
    def get_loaded_files(self):
        """Get list of loaded DBC files."""
        return list(self.loaded_dbc_files.keys())
