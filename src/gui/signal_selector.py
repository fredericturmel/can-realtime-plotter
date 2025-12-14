"""
Signal Selector Dialog

Dialog for selecting signals to plot.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QListWidgetItem, QLabel, QLineEdit,
                             QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
from src.parsers.database_parser import DatabaseParser


class SignalSelector(QDialog):
    """Dialog for selecting signals from loaded database."""
    
    def __init__(self, db_parser: DatabaseParser, parent=None):
        super().__init__(parent)
        self.db_parser = db_parser
        self.selected_signals = []
        
        self.setWindowTitle("Select Signals")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        self.load_signals()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter_signals)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Signal list
        list_label = QLabel("Available Signals (check to select):")
        layout.addWidget(list_label)
        
        self.signal_list = QListWidget()
        self.signal_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.signal_list)
        
        # Selection buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # OK/Cancel buttons
        ok_cancel_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        ok_cancel_layout.addStretch()
        ok_cancel_layout.addWidget(ok_btn)
        ok_cancel_layout.addWidget(cancel_btn)
        
        layout.addLayout(ok_cancel_layout)
        
    def load_signals(self):
        """Load signals from the database."""
        all_signals = self.db_parser.get_all_signals()
        
        for signal_info in all_signals:
            signal_name = f"{signal_info['message_id']:X}_{signal_info['signal_name']}"
            display_text = (f"{signal_name} "
                          f"[{signal_info['message_name']}] "
                          f"({signal_info['unit']})")
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, signal_name)
            item.setCheckState(Qt.Unchecked)
            self.signal_list.addItem(item)
    
    def filter_signals(self, text: str):
        """Filter signal list based on search text."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def select_all(self):
        """Select all visible signals."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.Checked)
    
    def deselect_all(self):
        """Deselect all signals."""
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def get_selected_signals(self) -> list:
        """
        Get list of selected signal names.
        
        Returns:
            List of signal names
        """
        selected = []
        for i in range(self.signal_list.count()):
            item = self.signal_list.item(i)
            if item.checkState() == Qt.Checked:
                signal_name = item.data(Qt.UserRole)
                selected.append(signal_name)
        
        return selected
