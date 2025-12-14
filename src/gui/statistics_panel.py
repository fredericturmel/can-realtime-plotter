"""
Statistics Panel

Panel for displaying signal statistics.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QHBoxLayout, QLabel, QComboBox)
from PyQt5.QtCore import Qt
from src.data_processing.signal_processor import SignalProcessor


class StatisticsPanel(QWidget):
    """Panel for displaying signal statistics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Window:"))
        self.window_combo = QComboBox()
        self.window_combo.addItems(['100 samples', '500 samples', '1000 samples', 'All'])
        self.window_combo.setCurrentText('All')
        control_layout.addWidget(self.window_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Statistics table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Signal', 'Mean', 'Min', 'Max', 'Std Dev', 'RMS'])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
    def set_signals(self, signal_names: list):
        """Set the signals to display statistics for."""
        self.signals = signal_names
        self.table.setRowCount(len(signal_names))
        
        for i, signal_name in enumerate(signal_names):
            self.table.setItem(i, 0, QTableWidgetItem(signal_name))
    
    def update_statistics(self, signal_processor: SignalProcessor):
        """Update statistics display."""
        window_text = self.window_combo.currentText()
        window_size = None
        
        if window_text != 'All':
            window_size = int(window_text.split()[0])
        
        for i, signal_name in enumerate(self.signals):
            stats = signal_processor.get_statistics(signal_name, window_size)
            
            self.table.setItem(i, 1, QTableWidgetItem(f"{stats['mean']:.3f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{stats['min']:.3f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{stats['max']:.3f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{stats['std']:.3f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{stats['rms']:.3f}"))
