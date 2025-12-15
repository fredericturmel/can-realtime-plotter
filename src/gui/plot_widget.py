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
        # Modern, harmonious color palette
        self.colors = [
            '#58a6ff',  # Blue
            '#3fb950',  # Green
            '#f85149',  # Red
            '#d29922',  # Yellow
            '#bc8cff',  # Purple
            '#56d4dd',  # Cyan
            '#ff7b72',  # Light red
            '#79c0ff',  # Light blue
            '#a5d6ff'   # Lighter blue
        ]
        self.time_sync_enabled = True  # Enable time synchronization by default
        self.master_plot = None  # Reference to the master plot for time sync
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Interpolation mode
        control_layout.addWidget(QLabel("📊 Interpolation:"))
        self.interpolation_combo = QComboBox()
        self.interpolation_combo.addItems(['Differential (Steps)', 'Linear', 'Smooth', 'None (Points)'])
        self.interpolation_combo.setCurrentText('Differential (Steps)')
        self.interpolation_combo.currentTextChanged.connect(self.change_interpolation)
        self.interpolation_combo.setToolTip("Choose how data points are connected")
        control_layout.addWidget(self.interpolation_combo)
        
        control_layout.addWidget(QLabel("|"))
        
        # Plot mode
        control_layout.addWidget(QLabel("📈 Layout:"))
        self.plot_mode_combo = QComboBox()
        self.plot_mode_combo.addItems(['Separate Plots', 'Single Plot', 'Grid Layout'])
        self.plot_mode_combo.currentTextChanged.connect(self.change_plot_mode)
        control_layout.addWidget(self.plot_mode_combo)
        
        control_layout.addWidget(QLabel("|"))
        
        # Time window
        control_layout.addWidget(QLabel("⏱️ Window:"))
        self.time_window_combo = QComboBox()
        self.time_window_combo.addItems(['5s', '10s', '30s', '60s', 'All'])
        self.time_window_combo.setCurrentText('10s')
        control_layout.addWidget(self.time_window_combo)
        
        control_layout.addWidget(QLabel("|"))
        
        # Time sync checkbox
        from PyQt5.QtWidgets import QCheckBox
        self.time_sync_checkbox = QCheckBox("🔗 Sync Time Axis")
        self.time_sync_checkbox.setChecked(self.time_sync_enabled)
        self.time_sync_checkbox.toggled.connect(self.toggle_time_sync)
        self.time_sync_checkbox.setToolTip("Synchronize time axis across all plots")
        control_layout.addWidget(self.time_sync_checkbox)
        
        control_layout.addWidget(QLabel("|"))
        
        self.autoscale_btn = QPushButton("🔍 Auto Scale")
        self.autoscale_btn.clicked.connect(self.autoscale_all)
        
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        
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
        interpolation_mode = self.interpolation_combo.currentText()
        
        # Determine curve style based on interpolation
        use_step = interpolation_mode == 'Differential (Steps)'
        use_points_only = interpolation_mode == 'None (Points)'
        
        # Reset master plot
        self.master_plot = None
        
        if plot_mode == 'Single Plot':
            # All signals on one plot
            plot = self.graphics_layout.addPlot(row=0, col=0)
            plot.setLabel('left', 'Value')
            plot.setLabel('bottom', 'Time', units='s')
            plot.showGrid(x=True, y=True)
            plot.addLegend()
            
            # Set as master plot for time sync
            self.master_plot = plot
            
            for i, signal_name in enumerate(self.signals):
                color = self.colors[i % len(self.colors)]
                if use_points_only:
                    curve = plot.plot(pen=None, symbol='o', symbolSize=6, 
                                    symbolBrush=color, name=signal_name)
                else:
                    curve = plot.plot(pen=pg.mkPen(color=color, width=2), 
                                    name=signal_name, stepMode='right' if use_step else False)
                self.curves[signal_name] = curve
                self.plots[signal_name] = plot
                
        elif plot_mode == 'Separate Plots':
            # Separate plot for each signal
            for i, signal_name in enumerate(self.signals):
                plot = self.graphics_layout.addPlot(row=i, col=0)
                plot.setLabel('left', signal_name)
                plot.setLabel('bottom', 'Time', units='s')
                plot.showGrid(x=True, y=True)
                
                # Link X-axis to master plot for time synchronization
                if i == 0:
                    self.master_plot = plot
                elif self.time_sync_enabled and self.master_plot:
                    plot.setXLink(self.master_plot)
                
                color = self.colors[i % len(self.colors)]
                if use_points_only:
                    curve = plot.plot(pen=None, symbol='o', symbolSize=6, symbolBrush=color)
                else:
                    curve = plot.plot(pen=pg.mkPen(color=color, width=2), 
                                    stepMode='right' if use_step else False)
                
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
                
                # Link X-axis to master plot for time synchronization
                if i == 0:
                    self.master_plot = plot
                elif self.time_sync_enabled and self.master_plot:
                    plot.setXLink(self.master_plot)
                
                color = self.colors[i % len(self.colors)]
                if use_points_only:
                    curve = plot.plot(pen=None, symbol='o', symbolSize=6, symbolBrush=color)
                else:
                    curve = plot.plot(pen=pg.mkPen(color=color, width=2), 
                                    stepMode='right' if use_step else False)
                
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
    
    def toggle_time_sync(self, enabled: bool):
        """Toggle time synchronization between plots."""
        self.time_sync_enabled = enabled
        
        if enabled:
            # Re-link all plots to master
            for signal_name, plot in self.plots.items():
                if plot != self.master_plot and self.master_plot:
                    plot.setXLink(self.master_plot)
        else:
            # Unlink all plots
            for signal_name, plot in self.plots.items():
                if plot != self.master_plot:
                    plot.setXLink(None)
    
    def change_interpolation(self, mode: str):
        """Change curve interpolation mode."""
        for signal_name, curve in self.curves.items():
            if mode == 'Differential (Steps)':
                # Step mode - keeps value until next sample
                curve.setData(stepMode='right')
            elif mode == 'Linear':
                # Linear interpolation (default)
                curve.setData(stepMode=False)
                curve.opts['connect'] = 'all'
            elif mode == 'Smooth':
                # Smooth curve using spline-like effect
                curve.setData(stepMode=False)
                curve.opts['connect'] = 'all'
                # Note: For true smoothing, we'd need to interpolate data
            elif mode == 'None (Points)':
                # Only show points, no lines
                curve.opts['connect'] = 'finite'
                pen = curve.opts['pen']
                if pen:
                    curve.setPen(None)
                    curve.setSymbol('o')
                    curve.setSymbolSize(6)
                    curve.setSymbolBrush(pen.color())
                return
            
            # Restore line style for non-point modes
            if 'pen' in curve.opts and curve.opts['pen'] is None:
                color = curve.opts.get('symbolBrush', (255, 255, 255))
                curve.setPen(pg.mkPen(color=color, width=2))
                curve.setSymbol(None)
    
    def autoscale_all(self):
        """Auto-scale all plots."""
        for plot in set(self.plots.values()):
            plot.enableAutoRange()
    
    def clear_all(self):
        """Clear all plot data."""
        for curve in self.curves.values():
            curve.setData([], [])
