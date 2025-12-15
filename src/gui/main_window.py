"""
Main Window

Primary application window with all GUI components.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStatusBar, QDockWidget, QAction,
                             QMenuBar, QFileDialog, QMessageBox, QTabWidget,
                             QLabel, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import can
import time
import logging

from src.can_interface.can_manager import CANInterfaceManager
from src.parsers.database_parser import DatabaseParser
from src.data_processing.signal_processor import SignalProcessor
from src.recorder.data_recorder import DataRecorder
from src.triggers.trigger_system import TriggerManager
from src.gui.connection_dialog import ConnectionDialog
from src.gui.signal_selector import SignalSelector
from src.gui.plot_widget import PlotWidget
from src.gui.message_sender import MessageSenderWidget
from src.gui.statistics_panel import StatisticsPanel
from src.gui.trigger_config import TriggerConfigWidget
from src.gui.configuration_panel import ConfigurationPanel
from src.gui.bus_load_analyzer import BusLoadAnalyzer
from src.gui.styles import get_theme

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.can_manager = CANInterfaceManager()
        self.db_parser = DatabaseParser()
        self.signal_processor = SignalProcessor()
        self.recorder = DataRecorder()
        self.trigger_manager = TriggerManager()
        
        # State
        self.selected_signals = []
        self.signal_values = {}
        self.message_count = 0
        self.sent_message_count = 0
        self.current_theme = 'dark'
        self.plot_sent_messages = True  # Option to plot sent messages
        
        # Apply modern theme
        self.setStyleSheet(get_theme(self.current_theme))
        
        # Setup UI
        self.init_ui()
        self.create_menu_bar()
        self.create_dock_widgets()
        self.connect_signals()
        
        # Setup update timer for real-time plotting
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_plots)
        self.update_timer.start(50)  # 20 Hz update rate
        
        self.setWindowTitle("CAN Real-Time Plotter - Modern Edition")
        self.resize(1600, 1000)
        
    def init_ui(self):
        """Initialize the user interface."""
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header section with title
        header_layout = QHBoxLayout()
        title_label = QLabel("🚗 CAN Real-Time Plotter")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Theme toggle button
        self.theme_btn = QPushButton("🌓 Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setMaximumWidth(150)
        header_layout.addWidget(self.theme_btn)
        
        layout.addLayout(header_layout)
        
        # Control buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.setObjectName("successButton")
        self.connect_btn.clicked.connect(self.show_connection_dialog)
        
        self.disconnect_btn = QPushButton("⏹ Disconnect")
        self.disconnect_btn.setObjectName("dangerButton")
        self.disconnect_btn.clicked.connect(self.disconnect_can)
        self.disconnect_btn.setEnabled(False)
        
        self.load_db_btn = QPushButton("📁 Load Database")
        self.load_db_btn.clicked.connect(self.load_database)
        
        self.select_signals_btn = QPushButton("📊 Select Signals")
        self.select_signals_btn.clicked.connect(self.show_signal_selector)
        self.select_signals_btn.setEnabled(False)
        
        self.record_btn = QPushButton("⏺ Start Recording")
        self.record_btn.setObjectName("dangerButton")
        self.record_btn.clicked.connect(self.toggle_recording)
        self.record_btn.setEnabled(False)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        button_layout.addWidget(self.load_db_btn)
        button_layout.addWidget(self.select_signals_btn)
        button_layout.addWidget(self.record_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Options bar
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)
        
        from PyQt5.QtWidgets import QCheckBox
        self.plot_sent_checkbox = QCheckBox("📊 Plot Sent Messages")
        self.plot_sent_checkbox.setChecked(self.plot_sent_messages)
        self.plot_sent_checkbox.toggled.connect(self.on_plot_sent_checkbox_toggled)
        self.plot_sent_checkbox.setToolTip("Display sent CAN messages on the real-time plot")
        options_layout.addWidget(self.plot_sent_checkbox)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Tab widget for different views with icons
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Configuration tab (First tab - main workflow)
        self.config_panel = ConfigurationPanel(self.db_parser)
        self.tab_widget.addTab(self.config_panel, "⚙️ Configuration")
        
        # Plot tab
        self.plot_widget = PlotWidget()
        self.tab_widget.addTab(self.plot_widget, "📈 Real-Time Plot")
        
        # Message sender tab
        self.message_sender = MessageSenderWidget(self.can_manager, self.db_parser)
        self.tab_widget.addTab(self.message_sender, "📤 Message Sender")
        
        # Expert mode: Bus Load Analyzer
        self.bus_analyzer = BusLoadAnalyzer(self.can_manager)
        self.tab_widget.addTab(self.bus_analyzer, "🔬 Expert Mode")
        
        # Trigger configuration tab
        self.trigger_config = TriggerConfigWidget(self.trigger_manager)
        self.tab_widget.addTab(self.trigger_config, "⚡ Triggers")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar with modern look
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Message counter with icons
        self.msg_counter_label = QLabel("📥 RX: 0 | 📤 TX: 0")
        self.msg_counter_label.setStyleSheet("padding: 4px 12px; font-weight: bold;")
        self.status_bar.addWidget(self.msg_counter_label)
        
        # Connection status with icon
        self.status_label = QLabel("⚫ Not connected")
        self.status_label.setStyleSheet("padding: 4px 12px;")
        self.status_bar.addPermanentWidget(self.status_label)
        
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        load_db_action = QAction("Load DBC/SYM...", self)
        load_db_action.triggered.connect(self.load_database)
        file_menu.addAction(load_db_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Options menu
        options_menu = menubar.addMenu("Options")
        
        self.plot_sent_action = QAction("Plot Sent Messages", self)
        self.plot_sent_action.setCheckable(True)
        self.plot_sent_action.setChecked(self.plot_sent_messages)
        self.plot_sent_action.triggered.connect(self.toggle_plot_sent_messages)
        options_menu.addAction(self.plot_sent_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        clear_data_action = QAction("Clear All Data", self)
        clear_data_action.triggered.connect(self.clear_all_data)
        tools_menu.addAction(clear_data_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_dock_widgets(self):
        """Create dock widgets for statistics and info."""
        # Statistics panel
        self.statistics_panel = StatisticsPanel()
        stats_dock = QDockWidget("Statistics", self)
        stats_dock.setWidget(self.statistics_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, stats_dock)
        
    def connect_signals(self):
        """Connect signals and slots."""
        # CAN manager signals
        self.can_manager.message_received.connect(self.on_message_received)
        self.can_manager.message_sent.connect(self.on_message_sent)
        self.can_manager.connection_status_changed.connect(self.on_connection_status_changed)
        self.can_manager.error_occurred.connect(self.on_error)
        
        # Connect bus analyzer to receive messages
        self.can_manager.message_received.connect(self.bus_analyzer.record_message)
        
        # Configuration panel signals
        self.config_panel.dbc_loaded.connect(self.on_dbc_loaded)
        self.config_panel.dbc_removed.connect(self.on_dbc_removed)
        
        # Recorder signals
        self.recorder.recording_started.connect(self.on_recording_started)
        self.recorder.recording_stopped.connect(self.on_recording_stopped)
        
        # Trigger signals
        self.trigger_manager.trigger_fired.connect(self.on_trigger_fired)
        
    def show_connection_dialog(self):
        """Show the connection configuration dialog."""
        dialog = ConnectionDialog(self)
        if dialog.exec_():
            config = dialog.get_configuration()
            success = self.can_manager.connect(
                interface=config['interface'],
                channel=config['channel'],
                bitrate=config['bitrate']
            )
            if success:
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.record_btn.setEnabled(True)
    
    def disconnect_can(self):
        """Disconnect from CAN interface."""
        self.can_manager.disconnect()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        
    def load_database(self):
        """Load a DBC or SYM file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Database File",
            "",
            "Database Files (*.dbc *.sym);;All Files (*)"
        )
        
        if file_path:
            if self.db_parser.load_database(file_path):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Loaded database with {len(self.db_parser.get_messages())} messages"
                )
                self.select_signals_btn.setEnabled(True)
                self.message_sender.update_database()
            else:
                error_msg = "Failed to load database file.\n\n"
                if file_path.lower().endswith('.sym'):
                    error_msg += "SYM File Issue:\n"
                    error_msg += "Only SYM version 6.0 is supported by cantools.\n\n"
                    error_msg += "Recommended solutions:\n"
                    error_msg += "1. Convert to DBC format (recommended)\n"
                    error_msg += "2. Export as SYM version 6.0\n"
                    error_msg += "3. Use a different database file\n\n"
                    error_msg += "Check the terminal/console for more details."
                else:
                    error_msg += "Please check that the file is a valid DBC or SYM file."
                
                QMessageBox.critical(
                    self,
                    "Database Load Error",
                    error_msg
                )
    
    def on_dbc_loaded(self, file_path: str):
        """Handle DBC file loaded from configuration panel."""
        self.select_signals_btn.setEnabled(True)
        self.message_sender.update_database()
        logger.info(f"DBC loaded: {file_path}")
    
    def on_dbc_removed(self, file_path: str):
        """Handle DBC file removed from configuration panel."""
        logger.info(f"DBC removed: {file_path}")
    
    def show_signal_selector(self):
        """Show signal selection dialog."""
        if not self.db_parser.is_loaded():
            QMessageBox.warning(self, "Warning", "Please load a DBC/SYM file first")
            return
        
        dialog = SignalSelector(self.db_parser, self)
        if dialog.exec_():
            self.selected_signals = dialog.get_selected_signals()
            self.plot_widget.set_signals(self.selected_signals)
            self.statistics_panel.set_signals(self.selected_signals)
            self.trigger_config.set_available_signals(self.selected_signals)
            logger.info(f"Selected {len(self.selected_signals)} signals for plotting")
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.setStyleSheet(get_theme(self.current_theme))
    
    def toggle_plot_sent_messages(self):
        """Toggle plotting of sent messages (from menu)."""
        self.plot_sent_messages = self.plot_sent_action.isChecked()
        self.plot_sent_checkbox.setChecked(self.plot_sent_messages)
        status = "enabled" if self.plot_sent_messages else "disabled"
        self.status_bar.showMessage(f"Plot sent messages {status}", 3000)
    
    def on_plot_sent_checkbox_toggled(self, checked: bool):
        """Handle plot sent messages checkbox toggle."""
        self.plot_sent_messages = checked
        self.plot_sent_action.setChecked(checked)
        status = "enabled" if checked else "disabled"
        self.status_bar.showMessage(f"Plot sent messages {status}", 3000)
    
    def toggle_recording(self):
        """Toggle data recording on/off."""
        if not self.recorder.is_recording:
            # Start recording
            mode = 'decoded' if self.selected_signals else 'raw'
            if self.recorder.start_recording(mode=mode, selected_signals=self.selected_signals):
                self.record_btn.setText("⏹ Stop Recording")
        else:
            # Stop recording
            self.recorder.stop_recording()
            self.record_btn.setText("⏺ Start Recording")
    
    def on_message_sent(self, msg: can.Message):
        """Handle sent CAN message."""
        self.sent_message_count += 1
        self.msg_counter_label.setText(f"📥 RX: {self.message_count} | 📤 TX: {self.sent_message_count}")
        logger.info(f"Sent: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex().upper()}")
        
        # Process sent message for plotting if enabled
        if self.plot_sent_messages and self.db_parser.is_loaded():
            timestamp = time.time()
            decoded = self.db_parser.decode_message(msg.arbitration_id, msg.data)
            
            if decoded:
                # Update signal values with sent data
                for signal_name, value in decoded.items():
                    full_signal_name = f"{msg.arbitration_id:X}_{signal_name}"
                    self.signal_values[full_signal_name] = value
                    
                    # Add to signal processor for plotting
                    if full_signal_name in self.selected_signals:
                        self.signal_processor.add_sample(full_signal_name, value, timestamp)
                        logger.debug(f"Plotted sent signal: {full_signal_name} = {value}")
    
    def on_message_received(self, msg: can.Message):
        """Handle received CAN message."""
        timestamp = time.time()
        
        # Update message counter
        self.message_count += 1
        self.msg_counter_label.setText(f"📥 RX: {self.message_count} | 📤 TX: {self.sent_message_count}")
        
        # Record raw message if in raw mode
        if self.recorder.is_recording and self.recorder.recording_mode == 'raw':
            self.recorder.record_raw_message(msg, timestamp)
        
        # Decode message if database loaded
        if self.db_parser.is_loaded():
            decoded = self.db_parser.decode_message(msg.arbitration_id, msg.data)
            
            if decoded:
                # Update signal values
                for signal_name, value in decoded.items():
                    full_signal_name = f"{msg.arbitration_id:X}_{signal_name}"
                    self.signal_values[full_signal_name] = value
                    
                    # Add to signal processor for analysis
                    if full_signal_name in self.selected_signals:
                        self.signal_processor.add_sample(full_signal_name, value, timestamp)
                
                # Record decoded message if in decoded mode
                if self.recorder.is_recording and self.recorder.recording_mode == 'decoded':
                    message = self.db_parser.get_message_by_id(msg.arbitration_id)
                    msg_name = message.name if message else f"0x{msg.arbitration_id:X}"
                    self.recorder.record_decoded_message(timestamp, msg.arbitration_id, 
                                                        msg_name, decoded)
                
                # Evaluate triggers
                self.trigger_manager.evaluate_all(self.signal_values)
    
    def update_plots(self):
        """Update plots with latest data."""
        for signal_name in self.selected_signals:
            times, values = self.signal_processor.get_data(signal_name)
            if len(times) > 0:
                self.plot_widget.update_plot(signal_name, times, values)
        
        # Update statistics
        self.statistics_panel.update_statistics(self.signal_processor)
    
    def on_connection_status_changed(self, connected: bool, message: str):
        """Handle connection status changes."""
        if connected:
            self.status_label.setText(f"🟢 {message}")
            self.status_label.setStyleSheet("color: #4caf50; padding: 4px 12px; font-weight: bold;")
        else:
            self.status_label.setText(f"⚫ {message}")
            self.status_label.setStyleSheet("color: #f44336; padding: 4px 12px;")
    
    def on_recording_started(self, file_path: str):
        """Handle recording started."""
        self.status_bar.showMessage(f"Recording to: {file_path}", 5000)
    
    def on_recording_stopped(self, message_count: int):
        """Handle recording stopped."""
        self.status_bar.showMessage(f"Recording stopped. Saved {message_count} messages", 5000)
    
    def on_trigger_fired(self, trigger_name: str, signal_values: dict):
        """Handle trigger fired event."""
        logger.info(f"Trigger fired: {trigger_name}")
        self.status_bar.showMessage(f"Trigger '{trigger_name}' fired!", 3000)
    
    def on_error(self, error_msg: str):
        """Handle error messages."""
        self.status_bar.showMessage(f"Error: {error_msg}", 5000)
        logger.error(error_msg)
    
    def clear_all_data(self):
        """Clear all recorded data."""
        reply = QMessageBox.question(
            self,
            "Clear Data",
            "Clear all recorded signal data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.signal_processor.clear_all()
            self.plot_widget.clear_all()
            self.status_bar.showMessage("Data cleared", 3000)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About CAN Real-Time Plotter",
            "<h3>CAN Real-Time Plotter</h3>"
            "<p>A comprehensive tool for CAN bus data visualization and analysis.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Real-time signal plotting</li>"
            "<li>PCAN and IXXAT support</li>"
            "<li>DBC/SYM file parsing</li>"
            "<li>Data recording and playback</li>"
            "<li>Signal processing (FFT, statistics)</li>"
            "<li>Complex trigger system</li>"
            "</ul>"
            "<p>Version 1.0</p>"
        )
    
    def closeEvent(self, event):
        """Handle application close."""
        # Stop recording if active
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        
        # Disconnect from CAN
        if self.can_manager.is_connected:
            self.can_manager.disconnect()
        
        event.accept()
