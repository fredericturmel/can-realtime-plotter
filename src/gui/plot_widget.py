"""
Plot Widget

Real-time plotting widget using pyqtgraph.
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import Qt
from typing import Dict, List
import numpy as np


class PlotWidget(QWidget):
    """Widget for real-time signal plotting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = []
        self.plots = {}
        self.curves = {}
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (255, 128, 0), (128, 255, 0), (255, 0, 128)
        ]
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        self.plot_mode_combo = QComboBox()
        self.plot_mode_combo.addItems(['Separate Plots', 'Single Plot', 'Grid Layout'])
        self.plot_mode_combo.currentTextChanged.connect(self.change_plot_mode)
        
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems(['5s', '10s', '30s', '60s', 'All'])
        self.time_window_combo.setCurrentText('10s')
        
        self.autoscale_btn = QPushButton("Auto Scale")
        self.autoscale_btn.clicked.connect(self.autoscale_all)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        
        control_layout.addWidget(QLabel("Plot Mode:"))
        control_layout.addWidget(self.plot_mode_combo)
        control_layout.addWidget(QLabel("Time Window:"))
        control_layout.addWidget(self.time_window_combo)
        control_layout.addWidget(self.autoscale_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Graphics layout for plots
        self.graphics_layout = pg.GraphicsLayoutWidget()
        self.graphics_layout.setBackground('w')
        layout.addWidget(self.graphics_layout)
        
    def set_signals(self, signal_names: List[str]):
        """
        Set the signals to plot.
        
        Args:
            signal_names: List of signal names
        """
        self.signals = signal_names
        self.setup_plots()
        
    def setup_plots(self):
        """Setup plot areas for selected signals."""
        # Clear existing plots
        self.graphics_layout.clear()
        self.plots.clear()
        self.curves.clear()
        
        if not self.signals:
            return
        
        plot_mode = self.plot_mode_combo.currentText()
        
        if plot_mode == 'Single Plot':
            # All signals on one plot
            plot = self.graphics_layout.addPlot(row=0, col=0)
            plot.setLabel('left', 'Value')
            plot.setLabel('bottom', 'Time', units='s')
            plot.showGrid(x=True, y=True)
            plot.addLegend()
            
            for i, signal_name in enumerate(self.signals):
                color = self.colors[i % len(self.colors)]
                curve = plot.plot(pen=pg.mkPen(color=color, width=2), name=signal_name)
                self.curves[signal_name] = curve
                self.plots[signal_name] = plot
                
        elif plot_mode == 'Separate Plots':
            # Separate plot for each signal
            for i, signal_name in enumerate(self.signals):
                plot = self.graphics_layout.addPlot(row=i, col=0)
                plot.setLabel('left', signal_name)
                plot.setLabel('bottom', 'Time', units='s')
                plot.showGrid(x=True, y=True)
                
                color = self.colors[i % len(self.colors)]
                curve = plot.plot(pen=pg.mkPen(color=color, width=2))
                
                self.plots[signal_name] = plot
                self.curves[signal_name] = curve
                
        else:  # Grid Layout
            # Grid layout for signals
            cols = 2
            for i, signal_name in enumerate(self.signals):
                row = i // cols
                col = i % cols
                
                plot = self.graphics_layout.addPlot(row=row, col=col)
                plot.setLabel('left', signal_name)
                plot.setLabel('bottom', 'Time', units='s')
                plot.showGrid(x=True, y=True)
                
                color = self.colors[i % len(self.colors)]
                curve = plot.plot(pen=pg.mkPen(color=color, width=2))
                
                self.plots[signal_name] = plot
                self.curves[signal_name] = curve
    
    def update_plot(self, signal_name: str, times: np.ndarray, values: np.ndarray):
        """
        Update plot data for a signal.
        
        Args:
            signal_name: Name of the signal
            times: Time array
            values: Value array
        """
        if signal_name not in self.curves:
            return
        
        # Apply time window filter
        time_window_text = self.time_window_combo.currentText()
        if time_window_text != 'All' and len(times) > 0:
            window_seconds = float(time_window_text.rstrip('s'))
            current_time = times[-1]
            mask = times >= (current_time - window_seconds)
            times = times[mask]
            values = values[mask]
        
        # Update curve
        self.curves[signal_name].setData(times, values)
    
    def change_plot_mode(self, mode: str):
        """Change plot layout mode."""
        self.setup_plots()
    
    def autoscale_all(self):
        """Auto-scale all plots."""
        for plot in set(self.plots.values()):
            plot.enableAutoRange()
    
    def clear_all(self):
        """Clear all plot data."""
        for curve in self.curves.values():
            curve.setData([], [])
