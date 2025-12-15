"""
New Modern Main Window - Architecture complètement refaite
Gestion d'interfaces CAN en panneau latéral, dashboards, navigation de messages
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QDockWidget, QAction, QMenuBar,
                             QFileDialog, QMessageBox, QTabWidget, QLabel,
                             QSplitter, QToolBar, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
import can
import time
import logging

from src.can_interface.can_manager import CANInterfaceManager
from src.parsers.database_parser import DatabaseParser
from src.data_processing.signal_processor import SignalProcessor
from src.recorder.data_recorder import DataRecorder
from src.triggers.trigger_system import TriggerManager

# New modules
from src.gui.interface_manager import InterfaceManagerPanel
from src.gui.message_browser import MessageBrowser
from src.gui.dashboard_system import DashboardManager
from src.gui.message_sender import MessageSenderWidget
from src.gui.trigger_config import TriggerConfigWidget

logger = logging.getLogger(__name__)


class ModernMainWindow(QMainWindow):
    """Fenêtre principale moderne avec nouvelle architecture"""
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.can_managers = {}  # interface_id -> CANInterfaceManager
        self.db_parsers = {}  # interface_id -> DatabaseParser
        self.signal_processor = SignalProcessor()
        self.recorder = DataRecorder()
        self.trigger_manager = TriggerManager()
        
        # UI State
        self.interface_panel_visible = True
        self.current_interface = None
        
        # Statistics
        self.interface_stats = {}  # interface_id -> {messages, errors, bus_load}
        
        # Apply dark theme
        self.apply_modern_theme()
        
        # Setup UI
        self.init_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all)
        self.update_timer.start(100)  # 10 Hz
        
        self.setWindowTitle("CAN Real-Time Plotter - Professional Edition")
        self.resize(1800, 1000)
        
    def apply_modern_theme(self):
        """Apply minimalist professional theme"""
        stylesheet = """
            QMainWindow {
                background-color: #0d1117;
            }
            
            QWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 13px;
            }
            
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #30363d;
                border-color: #8b949e;
            }
            
            QPushButton:pressed {
                background-color: #161b22;
            }
            
            QPushButton.primary {
                background-color: #238636;
                border-color: #238636;
                color: white;
            }
            
            QPushButton.primary:hover {
                background-color: #2ea043;
                border-color: #2ea043;
            }
            
            QPushButton.danger {
                background-color: #da3633;
                border-color: #da3633;
                color: white;
            }
            
            QPushButton.danger:hover {
                background-color: #e5534b;
            }
            
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 6px 12px;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #58a6ff;
                outline: none;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: #21262d;
                border-radius: 4px;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #8b949e;
                width: 0;
                height: 0;
            }
            
            QComboBox QAbstractItemView {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 4px;
                selection-background-color: #1f6feb;
                selection-color: white;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                border-radius: 4px;
                background-color: transparent;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #21262d;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #1f6feb;
                color: white;
            }
            
            QTabWidget::pane {
                border: 1px solid #30363d;
                border-radius: 6px;
                background-color: #0d1117;
            }
            
            QTabBar::tab {
                background-color: #161b22;
                color: #8b949e;
                border: 1px solid #30363d;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 4px;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background-color: #0d1117;
                color: #c9d1d9;
                border-bottom: 2px solid #58a6ff;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #21262d;
            }
            
            QDockWidget {
                titlebar-close-icon: url(none);
                titlebar-normal-icon: url(none);
                border: 1px solid #30363d;
            }
            
            QDockWidget::title {
                background-color: #161b22;
                color: #c9d1d9;
                padding: 8px;
                font-weight: 600;
            }
            
            QMenuBar {
                background-color: #161b22;
                color: #c9d1d9;
                border-bottom: 1px solid #30363d;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #21262d;
            }
            
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
            
            QToolBar {
                background-color: #161b22;
                border-bottom: 1px solid #30363d;
                spacing: 8px;
                padding: 4px;
            }
            
            QToolBar::separator {
                background-color: #30363d;
                width: 1px;
                margin: 4px;
            }
            
            QStatusBar {
                background-color: #161b22;
                color: #8b949e;
                border-top: 1px solid #30363d;
            }
            
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: 700;
                color: #c9d1d9;
            }
            
            QFrame#header {
                background-color: #161b22;
            }
            
            QFrame QLabel {
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: #0d1117;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #30363d;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #484f58;
            }
            
            QScrollBar:horizontal {
                background-color: #0d1117;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #30363d;
                border-radius: 6px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #484f58;
            }
            
            QSplitter::handle {
                background-color: #30363d;
            }
            
            QSplitter::handle:hover {
                background-color: #484f58;
            }
            
            QTableWidget, QTableView, QTreeWidget, QTreeView {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                gridline-color: #21262d;
                selection-background-color: #1f6feb;
                selection-color: white;
            }
            
            QTableWidget::item, QTableView::item, QTreeWidget::item, QTreeView::item {
                padding: 4px;
                background-color: transparent;
                border: none;
            }
            
            QTableWidget::item:selected, QTableView::item:selected,
            QTreeWidget::item:selected, QTreeView::item:selected {
                background-color: #1f6feb;
                color: white;
            }
            
            QTableWidget::item:hover, QTableView::item:hover,
            QTreeWidget::item:hover, QTreeView::item:hover {
                background-color: #161b22;
            }
            
            QTableWidget::item:alternate, QTableView::item:alternate,
            QTreeWidget::item:alternate, QTreeView::item:alternate {
                background-color: #0d1117;
            }
            
            QHeaderView::section {
                background-color: #161b22;
                color: #8b949e;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #30363d;
                border-right: 1px solid #21262d;
                font-weight: 600;
            }
            
            QHeaderView::section:hover {
                background-color: #21262d;
            }
            
            QTextEdit, QPlainTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #1f6feb;
                selection-color: white;
            }
            
            QProgressBar {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 4px;
                text-align: center;
                color: #c9d1d9;
            }
            
            QProgressBar::chunk {
                background-color: #238636;
                border-radius: 3px;
            }
            
            QCheckBox {
                color: #c9d1d9;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #30363d;
                border-radius: 4px;
                background-color: #0d1117;
            }
            
            QCheckBox::indicator:hover {
                border-color: #58a6ff;
            }
            
            QCheckBox::indicator:checked {
                background-color: #1f6feb;
                border-color: #1f6feb;
            }
            
            QRadioButton {
                color: #c9d1d9;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #30363d;
                border-radius: 9px;
                background-color: #0d1117;
            }
            
            QRadioButton::indicator:hover {
                border-color: #58a6ff;
            }
            
            QRadioButton::indicator:checked {
                background-color: #1f6feb;
                border-color: #1f6feb;
            }
            
            QRadioButton::indicator:checked:after {
                width: 10px;
                height: 10px;
                border-radius: 5px;
                background-color: white;
            }
            
            QGroupBox {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                margin-top: 12px;
                padding: 16px;
                font-weight: 600;
                color: #c9d1d9;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                background-color: #0d1117;
                color: #c9d1d9;
            }
            
            QDialog {
                background-color: #0d1117;
                color: #c9d1d9;
            }
            
            QFormLayout {
                spacing: 8px;
            }
            
            QLabel {
                color: #c9d1d9;
            }
        """
        
        self.setStyleSheet(stylesheet)
        
    def init_ui(self):
        """Initialize the modern UI with dockable panels"""
        
        # Create interface manager dock (left side)
        self.interface_dock = QDockWidget("", self)
        self.interface_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.interface_dock.setTitleBarWidget(QWidget())  # Hide title bar
        
        self.interface_panel = InterfaceManagerPanel()
        self.interface_panel.connection_requested.connect(self.on_interface_connect)
        self.interface_panel.disconnection_requested.connect(self.on_interface_disconnect)
        self.interface_dock.setWidget(self.interface_panel)
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.interface_dock)
        
        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Tab 1: Message Browser
        self.message_browser = MessageBrowser()
        self.message_browser.signal_selected.connect(self.on_signal_selected)
        self.tab_widget.addTab(self.message_browser, "📋 Messages CAN")
        
        # Tab 2: Dashboards
        self.dashboard_manager = DashboardManager()
        self.tab_widget.addTab(self.dashboard_manager, "📊 Dashboards")
        
        # Tab 3: Message Sender
        self.message_sender = MessageSenderWidget(None, None)  # Will be updated per interface
        self.tab_widget.addTab(self.message_sender, "📤 Envoyer")
        
        # Tab 4: Triggers
        self.trigger_widget = TriggerConfigWidget(self.trigger_manager)
        self.tab_widget.addTab(self.trigger_widget, "⚡ Déclencheurs")
        
        layout.addWidget(self.tab_widget)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&Fichier")
        
        import_dashboard_action = QAction("📥 Importer Dashboard...", self)
        import_dashboard_action.setShortcut(QKeySequence("Ctrl+O"))
        import_dashboard_action.triggered.connect(self.import_dashboard)
        file_menu.addAction(import_dashboard_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # View menu
        view_menu = menubar.addMenu("&Affichage")
        
        toggle_interface_action = QAction("Panneau Interfaces", self)
        toggle_interface_action.setCheckable(True)
        toggle_interface_action.setChecked(True)
        toggle_interface_action.triggered.connect(self.toggle_interface_panel)
        view_menu.addAction(toggle_interface_action)
        
        view_menu.addSeparator()
        
        # Theme toggle
        self.theme_action = QAction("🌞 Mode Clair", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        self.is_dark_mode = True
        view_menu.addAction(self.theme_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Outils")
        
        start_recording_action = QAction("⏺️ Démarrer enregistrement", self)
        start_recording_action.triggered.connect(self.start_recording)
        tools_menu.addAction(start_recording_action)
        
        stop_recording_action = QAction("⏹️ Arrêter enregistrement", self)
        stop_recording_action.triggered.connect(self.stop_recording)
        tools_menu.addAction(stop_recording_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the main toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New dashboard
        new_dashboard_btn = QPushButton("+ Dashboard")
        new_dashboard_btn.clicked.connect(self.dashboard_manager.create_dashboard)
        toolbar.addWidget(new_dashboard_btn)
        
        toolbar.addSeparator()
        
        # Recording controls
        self.record_btn = QPushButton("⏺️ Enregistrer")
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.toggle_recording)
        toolbar.addWidget(self.record_btn)
        
        toolbar.addWidget(QWidget())  # Spacer
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Interface count label
        self.interface_count_label = QLabel("Interfaces: 0")
        self.status_bar.addWidget(self.interface_count_label)
        
        self.status_bar.addWidget(QLabel("|"))
        
        # Message count
        self.message_count_label = QLabel("Messages: 0")
        self.status_bar.addWidget(self.message_count_label)
        
        self.status_bar.addWidget(QLabel("|"))
        
        # Status
        self.status_label = QLabel("Prêt")
        self.status_bar.addWidget(self.status_label)
        
        self.status_bar.addPermanentWidget(QLabel("CAN Real-Time Plotter v2.0"))
        
    def on_interface_connect(self, interface_id, interface_type, db_path):
        """Handle interface connection request"""
        try:
            # Create CAN manager for this interface
            can_manager = CANInterfaceManager()
            
            # Connect (simplified - you'd need proper channel/bitrate from interface_panel)
            # This is a placeholder
            can_manager.connect(
                interface_type.lower(),
                channel="vcan0" if interface_type == "Virtual" else "PCAN_USBBUS1",
                bitrate=500000
            )
            
            self.can_managers[interface_id] = can_manager
            
            # Load database if specified
            if db_path:
                db_parser = DatabaseParser()
                if db_parser.load_database(db_path):
                    self.db_parsers[interface_id] = db_parser
                    self.message_browser.load_database(db_parser.database)
                    # Update message sender with new db_parser and can_manager
                    self.message_sender.set_managers(can_manager, db_parser)
            else:
                # Update message sender with just can_manager
                self.message_sender.set_managers(can_manager, None)
                    
            # Setup message reception
            can_manager.message_received.connect(
                lambda msg: self.on_message_received(interface_id, msg)
            )
            
            # Update dashboard with available signals
            if db_parser and db_parser.database:
                signals = []
                for msg in db_parser.database.messages:
                    for sig in msg.signals:
                        signals.append((msg.name, sig.name, sig.unit or ""))
                self.dashboard_manager.set_available_signals(interface_id, signals)
            
            # Update UI
            self.interface_panel.set_interface_connected(interface_id, True)
            self.status_label.setText(f"Interface {interface_id} connectée")
            
            # Initialize stats
            self.interface_stats[interface_id] = {
                'messages': 0,
                'errors': 0,
                'bus_load': 0.0,
                'last_update': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error connecting interface {interface_id}: {e}")
            QMessageBox.critical(
                self,
                "Erreur de connexion",
                f"Impossible de connecter l'interface {interface_id}:\n{str(e)}"
            )
            self.interface_panel.set_interface_connected(interface_id, False)
            
    def on_interface_disconnect(self, interface_id):
        """Handle interface disconnection"""
        if interface_id in self.can_managers:
            self.can_managers[interface_id].disconnect()
            del self.can_managers[interface_id]
            
        if interface_id in self.db_parsers:
            del self.db_parsers[interface_id]
            
        if interface_id in self.interface_stats:
            del self.interface_stats[interface_id]
            
        self.interface_panel.set_interface_connected(interface_id, False)
        self.status_label.setText(f"Interface {interface_id} déconnectée")
        
    def on_message_received(self, interface_id, message):
        """Handle received CAN message"""
        # Update statistics
        if interface_id in self.interface_stats:
            stats = self.interface_stats[interface_id]
            stats['messages'] += 1
            
        # Decode message if database available
        if interface_id in self.db_parsers:
            db = self.db_parsers[interface_id]
            decoded = db.decode_message(message.arbitration_id, message.data)
            
            if decoded:
                # Update message browser
                for signal_name, signal_data in decoded.items():
                    msg_name = self.find_message_name(db, message.arbitration_id)
                    if msg_name:
                        self.message_browser.update_signal_value(
                            msg_name,
                            signal_name,
                            signal_data['raw'],
                            signal_data['physical'],
                            signal_data.get('unit', '')
                        )
                        
        # Record if active
        if self.recorder.is_recording:
            self.recorder.record_message(message)
            
    def find_message_name(self, db_parser, can_id):
        """Find message name by CAN ID"""
        if db_parser.database:
            for msg in db_parser.database.messages:
                if msg.frame_id == can_id:
                    return msg.name
        return None
        
    def on_signal_selected(self, message_name, signal_name):
        """Handle signal selection from browser"""
        # Could add to dashboard or plot
        pass
        
    def update_all(self):
        """Update all displays"""
        # Update interface statistics
        for interface_id, stats in self.interface_stats.items():
            # Calculate bus load (simplified)
            now = time.time()
            elapsed = now - stats.get('last_update', now)
            if elapsed > 0:
                # Rough estimation
                bus_load = min(100, (stats['messages'] / elapsed) / 10)
                stats['bus_load'] = bus_load
                stats['last_update'] = now
                
                # Update UI
                self.interface_panel.update_interface_bus_load(
                    interface_id,
                    bus_load
                )
                self.interface_panel.update_interface_statistics(
                    interface_id,
                    stats['messages'],
                    stats['errors']
                )
                
        # Update status bar
        total_messages = sum(s['messages'] for s in self.interface_stats.values())
        self.message_count_label.setText(f"Messages: {total_messages}")
        self.interface_count_label.setText(f"Interfaces: {len(self.can_managers)}")
        
    def toggle_interface_panel(self, checked):
        """Toggle interface panel visibility"""
        self.interface_dock.setVisible(checked)
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.apply_modern_theme()
            self.theme_action.setText("🌞 Mode Clair")
        else:
            self.apply_light_theme()
            self.theme_action.setText("🌙 Mode Sombre")
    
    def apply_light_theme(self):
        """Apply light theme"""
        stylesheet = """
            QMainWindow {
                background-color: #ffffff;
            }
            
            QWidget {
                background-color: #ffffff;
                color: #24292f;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 13px;
            }
            
            QPushButton {
                background-color: #f6f8fa;
                color: #24292f;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: #1f2328;
            }
            
            QPushButton:pressed {
                background-color: #e1e4e8;
            }
            
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 6px 12px;
                selection-background-color: #0969da;
                selection-color: white;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #0969da;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }
            
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #57606a;
            }
            
            QComboBox::down-arrow:hover {
                border-top-color: #24292f;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                selection-background-color: #0969da;
                selection-color: white;
                padding: 4px;
                outline: none;
            }
            
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #f6f8fa;
            }
            
            QTabWidget::pane {
                border: 1px solid #d0d7de;
                background-color: #ffffff;
            }
            
            QTabBar::tab {
                background-color: #f6f8fa;
                color: #57606a;
                border: 1px solid #d0d7de;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #24292f;
                font-weight: 600;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #f3f4f6;
            }
            
            QTreeWidget, QTableWidget {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d0d7de;
                alternate-background-color: #f6f8fa;
            }
            
            QTreeWidget::item:selected, QTableWidget::item:selected {
                background-color: #0969da;
                color: white;
            }
            
            QTreeWidget::item:hover, QTableWidget::item:hover {
                background-color: #f6f8fa;
            }
            
            QHeaderView::section {
                background-color: #f6f8fa;
                color: #57606a;
                border: none;
                border-bottom: 1px solid #d0d7de;
                border-right: 1px solid #d0d7de;
                padding: 8px;
                font-weight: 600;
            }
            
            QHeaderView::section:hover {
                background-color: #e1e4e8;
                color: #24292f;
            }
            
            QHeaderView::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 5px solid #0969da;
                margin-left: 4px;
            }
            
            QHeaderView::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-bottom: 5px solid #0969da;
                margin-left: 4px;
            }
            
            QDockWidget {
                titlebar-close-icon: url(none);
                titlebar-normal-icon: url(none);
                border: 1px solid #d0d7de;
            }
            
            QDockWidget::title {
                background-color: #f6f8fa;
                color: #24292f;
                padding: 8px;
                font-weight: 600;
            }
            
            QMenuBar {
                background-color: #f6f8fa;
                color: #24292f;
                border-bottom: 1px solid #d0d7de;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #e1e4e8;
            }
            
            QMenu {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #0969da;
                color: white;
            }
            
            QToolBar {
                background-color: #f6f8fa;
                border-bottom: 1px solid #d0d7de;
                spacing: 8px;
                padding: 4px;
            }
            
            QToolBar::separator {
                background-color: #d0d7de;
                width: 1px;
                margin: 4px;
            }
            
            QStatusBar {
                background-color: #f6f8fa;
                color: #57606a;
                border-top: 1px solid #d0d7de;
            }
            
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: 700;
                color: #24292f;
            }
            
            QScrollBar:vertical {
                background-color: #f6f8fa;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #d0d7de;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #afb8c1;
            }
            
            QScrollBar:horizontal {
                background-color: #f6f8fa;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #d0d7de;
                border-radius: 6px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #afb8c1;
            }
            
            QFrame {
                background-color: #ffffff;
                border: none;
            }
            
            QFrame#header {
                background-color: #f6f8fa;
                border-bottom: 1px solid #d0d7de;
            }
            
            QFrame QLabel {
                background-color: transparent;
                color: #24292f;
            }
            
            QGroupBox {
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: 600;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                background-color: #ffffff;
                border: 1px solid #d0d7de;
                border-radius: 4px;
            }
            
            QProgressBar {
                border: 1px solid #d0d7de;
                border-radius: 4px;
                background-color: #f6f8fa;
                text-align: center;
                color: #24292f;
                min-height: 20px;
                font-size: 11px;
                font-weight: 500;
            }
            
            QProgressBar::chunk {
                background-color: #0969da;
                border-radius: 3px;
            }
            
            QCheckBox {
                color: #24292f;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #d0d7de;
                border-radius: 4px;
                background-color: #ffffff;
            }
            
            QCheckBox::indicator:hover {
                border-color: #0969da;
            }
            
            QCheckBox::indicator:checked {
                background-color: #0969da;
                border-color: #0969da;
            }
            
            QRadioButton {
                color: #24292f;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #d0d7de;
                border-radius: 9px;
                background-color: #ffffff;
            }
            
            QRadioButton::indicator:hover {
                border-color: #0969da;
            }
            
            QRadioButton::indicator:checked {
                background-color: #0969da;
                border-color: #0969da;
            }
        """
        self.setStyleSheet(stylesheet)
        
    def toggle_recording(self, checked):
        """Toggle recording on/off"""
        if checked:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        """Start recording CAN messages"""
        if not self.recorder.is_recording:
            self.recorder.start_recording()
            self.record_btn.setText("⏹️ Arrêter")
            self.record_btn.setProperty("class", "danger")
            self.status_label.setText("Enregistrement en cours...")
            
    def stop_recording(self):
        """Stop recording CAN messages"""
        if self.recorder.is_recording:
            file_path = self.recorder.stop_recording()
            self.record_btn.setText("⏺️ Enregistrer")
            self.record_btn.setProperty("class", "")
            self.status_label.setText(f"Enregistrement sauvegardé: {file_path}")
            
    def import_dashboard(self):
        """Import a dashboard configuration"""
        self.dashboard_manager.import_dashboard()
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "À propos",
            "<h2>CAN Real-Time Plotter</h2>"
            "<p>Version 2.0 - Professional Edition</p>"
            "<p>Outil de visualisation en temps réel pour bus CAN</p>"
            "<p><b>Fonctionnalités:</b></p>"
            "<ul>"
            "<li>Gestion multi-interfaces CAN</li>"
            "<li>Navigation hiérarchique des messages</li>"
            "<li>Support des énumérations DBC/SYM</li>"
            "<li>Dashboards dynamiques personnalisables</li>"
            "<li>Import/Export de configurations</li>"
            "</ul>"
        )
        
    def closeEvent(self, event):
        """Handle window close"""
        # Disconnect all interfaces
        for interface_id in list(self.can_managers.keys()):
            self.on_interface_disconnect(interface_id)
            
        # Stop recording
        if self.recorder.is_recording:
            self.recorder.stop_recording()
            
        event.accept()
