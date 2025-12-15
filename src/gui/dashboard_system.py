"""
Dashboard System - Système de création de dashboards dynamiques
Support: jauges, valeurs numériques, états binaires, énumérations, graphes
Import/Export JSON pour réutilisation
"""

import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QFrame, QMenu, QAction,
                             QFileDialog, QMessageBox, QDialog, QComboBox,
                             QLineEdit, QSpinBox, QCheckBox, QColorDialog,
                             QFormLayout, QDialogButtonBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient
import pyqtgraph as pg


class GaugeWidget(QWidget):
    """Widget jauge circulaire"""
    
    def __init__(self, title="Gauge", min_val=0, max_val=100, unit="", parent=None):
        super().__init__(parent)
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.value = 0
        self.signal_name = ""
        self.setMinimumSize(200, 200)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        """Show context menu for widget"""
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
        resize_action = menu.addAction("↔️ Redimensionner")
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(self.mapToGlobal(pos))
        if action == edit_action:
            parent = self.parent()
            if parent and hasattr(parent, 'edit_widget'):
                parent.edit_widget(self)
        elif action == resize_action:
            parent = self.parent()
            if parent and hasattr(parent, 'resize_widget'):
                parent.resize_widget(self)
        elif action == delete_action:
            parent = self.parent()
            if parent and hasattr(parent, 'remove_widget'):
                parent.remove_widget(self)
        
    def set_value(self, value):
        """Update gauge value"""
        self.value = max(self.min_val, min(self.max_val, value))
        self.update()
        
    def paintEvent(self, event):
        """Draw the gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 20
        
        center_x = width / 2
        center_y = height / 2
        
        # Background
        painter.fillRect(self.rect(), QColor("#0d1117"))
        
        # Title
        painter.setPen(QColor("#8b949e"))
        font = QFont()
        font.setPixelSize(12)
        painter.setFont(font)
        painter.drawText(10, 20, self.title)
        
        # Gauge background arc
        painter.setPen(QPen(QColor("#30363d"), 15, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(
            int(center_x - size/2), int(center_y - size/2),
            int(size), int(size),
            40 * 16, 260 * 16
        )
        
        # Value arc
        if self.max_val > self.min_val:
            percentage = (self.value - self.min_val) / (self.max_val - self.min_val)
            angle = int(percentage * 260 * 16)
            
            # Color based on percentage
            if percentage < 0.6:
                color = QColor("#3fb950")  # Green
            elif percentage < 0.85:
                color = QColor("#d29922")  # Orange
            else:
                color = QColor("#f85149")  # Red
                
            painter.setPen(QPen(color, 15, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(
                int(center_x - size/2), int(center_y - size/2),
                int(size), int(size),
                40 * 16, angle
            )
        
        # Value text
        painter.setPen(QColor("#c9d1d9"))
        font.setPixelSize(24)
        font.setBold(True)
        painter.setFont(font)
        
        value_text = f"{self.value:.1f}"
        text_rect = painter.fontMetrics().boundingRect(value_text)
        painter.drawText(
            int(center_x - text_rect.width()/2),
            int(center_y + text_rect.height()/4),
            value_text
        )
        
        # Unit
        if self.unit:
            painter.setPen(QColor("#8b949e"))
            font.setPixelSize(12)
            font.setBold(False)
            painter.setFont(font)
            unit_rect = painter.fontMetrics().boundingRect(self.unit)
            painter.drawText(
                int(center_x - unit_rect.width()/2),
                int(center_y + 30),
                self.unit
            )
            
        # Min/Max labels
        painter.setPen(QColor("#8b949e"))
        font.setPixelSize(10)
        painter.setFont(font)
        painter.drawText(int(center_x - size/2 - 10), int(center_y + 20), str(self.min_val))
        painter.drawText(int(center_x + size/2 - 10), int(center_y + 20), str(self.max_val))


class NumericDisplayWidget(QWidget):
    """Widget affichage numérique simple"""
    
    def __init__(self, title="Value", unit="", decimals=2, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.decimals = decimals
        self.value = 0
        self.signal_name = ""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet("""
            color: #58a6ff;
            font-size: 36px;
            font-weight: 700;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Unit
        if self.unit:
            unit_label = QLabel(self.unit)
            unit_label.setStyleSheet("color: #8b949e; font-size: 14px;")
            unit_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(unit_label)
            
        self.setStyleSheet("""
            NumericDisplayWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
    
    def show_context_menu(self, pos):
        """Show context menu for widget"""
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
        resize_action = menu.addAction("↔️ Redimensionner")
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(self.mapToGlobal(pos))
        if action == edit_action:
            parent = self.parent()
            if parent and hasattr(parent, 'edit_widget'):
                parent.edit_widget(self)
        elif action == resize_action:
            parent = self.parent()
            if parent and hasattr(parent, 'resize_widget'):
                parent.resize_widget(self)
        elif action == delete_action:
            parent = self.parent()
            if parent and hasattr(parent, 'remove_widget'):
                parent.remove_widget(self)
        
    def set_value(self, value):
        """Update displayed value"""
        self.value = value
        self.value_label.setText(f"{value:.{self.decimals}f}")


class BinaryStateWidget(QWidget):
    """Widget état binaire (ON/OFF)"""
    
    def __init__(self, title="State", true_label="ON", false_label="OFF", parent=None):
        super().__init__(parent)
        self.title = title
        self.true_label = true_label
        self.false_label = false_label
        self.state = False
        self.signal_name = ""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(title_label)
        
        # State indicator
        self.state_frame = QFrame()
        self.state_frame.setFixedSize(80, 80)
        self.state_frame.setStyleSheet("""
            QFrame {
                background-color: #30363d;
                border-radius: 40px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.state_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        self.state_label = QLabel(self.false_label)
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: 600;")
        frame_layout.addWidget(self.state_label)
        
        layout.addWidget(self.state_frame, 0, Qt.AlignCenter)
        
        self.setStyleSheet("""
            BinaryStateWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        
    def set_state(self, state):
        """Update state"""
        self.state = bool(state)
        
        if self.state:
            self.state_frame.setStyleSheet("""
                QFrame {
                    background-color: #238636;
                    border-radius: 40px;
                }
            """)
            self.state_label.setText(self.true_label)
            self.state_label.setStyleSheet("color: white; font-size: 14px; font-weight: 600;")
        else:
            self.state_frame.setStyleSheet("""
                QFrame {
                    background-color: #30363d;
                    border-radius: 40px;
                }
            """)
            self.state_label.setText(self.false_label)
            self.state_label.setStyleSheet("color: #8b949e; font-size: 14px; font-weight: 600;")
    
    def show_context_menu(self, pos):
        """Show context menu for widget"""
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
        resize_action = menu.addAction("↔️ Redimensionner")
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(self.mapToGlobal(pos))
        if action == edit_action:
            parent = self.parent()
            if parent and hasattr(parent, 'edit_widget'):
                parent.edit_widget(self)
        elif action == resize_action:
            parent = self.parent()
            if parent and hasattr(parent, 'resize_widget'):
                parent.resize_widget(self)
        elif action == delete_action:
            parent = self.parent()
            if parent and hasattr(parent, 'remove_widget'):
                parent.remove_widget(self)


class EnumDisplayWidget(QWidget):
    """Widget affichage énumération"""
    
    def __init__(self, title="Enum", enum_values=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.enum_values = enum_values or {}  # value -> name
        self.current_value = None
        self.signal_name = ""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(title_label)
        
        # Value name
        self.value_label = QLabel("---")
        self.value_label.setStyleSheet("""
            color: #58a6ff;
            font-size: 20px;
            font-weight: 600;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)
        
        # Raw value
        self.raw_label = QLabel("")
        self.raw_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        self.raw_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.raw_label)
        
        self.setStyleSheet("""
            EnumDisplayWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        
    def set_value(self, value):
        """Update displayed value"""
        self.current_value = value
        
        if value in self.enum_values:
            self.value_label.setText(self.enum_values[value])
            self.raw_label.setText(f"(valeur: {value})")
        else:
            self.value_label.setText(str(value))
    
    def show_context_menu(self, pos):
        """Show context menu for widget"""
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
        resize_action = menu.addAction("↔️ Redimensionner")
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(self.mapToGlobal(pos))
        if action == edit_action:
            parent = self.parent()
            if parent and hasattr(parent, 'edit_widget'):
                parent.edit_widget(self)
        elif action == resize_action:
            parent = self.parent()
            if parent and hasattr(parent, 'resize_widget'):
                parent.resize_widget(self)
        elif action == delete_action:
            parent = self.parent()
            if parent and hasattr(parent, 'remove_widget'):
                parent.remove_widget(self)


class MiniGraphWidget(QWidget):
    """Mini graphe pour dashboard"""
    
    def __init__(self, title="Graph", unit="", max_points=100, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.max_points = max_points
        self.signal_name = ""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(title_label)
        
        # Graph
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#0d1117')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget.setLabel('left', self.unit, color='#8b949e', size='10pt')
        
        # Style axes
        self.plot_widget.getAxis('bottom').setPen('#30363d')
        self.plot_widget.getAxis('left').setPen('#30363d')
        self.plot_widget.getAxis('bottom').setTextPen('#8b949e')
        self.plot_widget.getAxis('left').setTextPen('#8b949e')
        
        # Data
        self.x_data = []
        self.y_data = []
        self.curve = self.plot_widget.plot(pen=pg.mkPen('#58a6ff', width=2))
        
        layout.addWidget(self.plot_widget)
        
        self.setStyleSheet("""
            MiniGraphWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        
    def add_point(self, x, y):
        """Add a data point"""
        self.x_data.append(x)
        self.y_data.append(y)
        
        # Limit number of points
        if len(self.x_data) > self.max_points:
            self.x_data.pop(0)
            self.y_data.pop(0)
            
        self.curve.setData(self.x_data, self.y_data)
    
    def show_context_menu(self, pos):
        """Show context menu for widget"""
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
        resize_action = menu.addAction("↔️ Redimensionner")
        delete_action = menu.addAction("🗑️ Supprimer")
        
        action = menu.exec_(self.mapToGlobal(pos))
        if action == edit_action:
            parent = self.parent()
            if parent and hasattr(parent, 'edit_widget'):
                parent.edit_widget(self)
        elif action == resize_action:
            parent = self.parent()
            if parent and hasattr(parent, 'resize_widget'):
                parent.resize_widget(self)
        elif action == delete_action:
            parent = self.parent()
            if parent and hasattr(parent, 'remove_widget'):
                parent.remove_widget(self)


class DashboardWidget(QWidget):
    """Container for a dashboard with grid layout"""
    
    def __init__(self, dashboard_name="Dashboard", parent=None):
        super().__init__(parent)
        self.dashboard_name = dashboard_name
        self.widgets = {}  # (row, col) -> widget
        self.widget_configs = {}  # (row, col) -> config dict
        self.available_signals = {}  # interface_id -> [(msg_name, signal_name, unit), ...]
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(50)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        
        title = QLabel(f"📊 {self.dashboard_name}")
        title.setStyleSheet("font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Add widget button
        add_btn = QPushButton("+ Ajouter Widget")
        add_btn.clicked.connect(self.add_widget_dialog)
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
        
        # Export button
        export_btn = QPushButton("💾 Exporter")
        export_btn.clicked.connect(self.export_dashboard)
        header_layout.addWidget(export_btn)
        
        main_layout.addWidget(header)
        
        # Scroll area for widgets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def add_widget_dialog(self):
        """Show dialog to add a new widget"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un widget")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        form = QFormLayout()
        
        # Widget type
        type_combo = QComboBox()
        type_combo.addItems([
            "Jauge circulaire",
            "Affichage numérique",
            "État binaire",
            "Énumération",
            "Mini graphe"
        ])
        form.addRow("Type:", type_combo)
        
        # Title
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("Titre du widget")
        form.addRow("Titre:", title_edit)
        
        # Signal selection
        signal_combo = QComboBox()
        signal_combo.addItem("Sélectionner un signal...", None)
        # Populate from available signals
        for interface_id, signals in self.available_signals.items():
            for msg_name, signal_name, unit in signals:
                display_text = f"[{interface_id}] {msg_name} → {signal_name}"
                if unit:
                    display_text += f" ({unit})"
                signal_data = {
                    'interface_id': interface_id,
                    'message': msg_name,
                    'signal': signal_name,
                    'unit': unit
                }
                signal_combo.addItem(display_text, signal_data)
        form.addRow("Signal:", signal_combo)
        
        # Position
        row_spin = QSpinBox()
        row_spin.setMinimum(0)
        row_spin.setMaximum(10)
        form.addRow("Ligne:", row_spin)
        
        col_spin = QSpinBox()
        col_spin.setMinimum(0)
        col_spin.setMaximum(10)
        form.addRow("Colonne:", col_spin)
        
        # Size
        rowspan_spin = QSpinBox()
        rowspan_spin.setMinimum(1)
        rowspan_spin.setMaximum(5)
        rowspan_spin.setValue(1)
        form.addRow("Hauteur:", rowspan_spin)
        
        colspan_spin = QSpinBox()
        colspan_spin.setMinimum(1)
        colspan_spin.setMaximum(5)
        colspan_spin.setValue(1)
        form.addRow("Largeur:", colspan_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            widget_type = type_combo.currentText()
            title = title_edit.text() or "Widget"
            row = row_spin.value()
            col = col_spin.value()
            rowspan = rowspan_spin.value()
            colspan = colspan_spin.value()
            signal_data = signal_combo.currentData()
            
            config = {
                'signal_data': signal_data
            } if signal_data else None
            
            self.add_widget(widget_type, title, row, col, rowspan, colspan, config)
            
    def add_widget(self, widget_type, title, row, col, rowspan=1, colspan=1, config=None):
        """Add a widget to the dashboard"""
        widget = None
        
        if widget_type == "Jauge circulaire":
            widget = GaugeWidget(title, parent=self)
        elif widget_type == "Affichage numérique":
            widget = NumericDisplayWidget(title, parent=self)
        elif widget_type == "État binaire":
            widget = BinaryStateWidget(title, parent=self)
        elif widget_type == "Énumération":
            widget = EnumDisplayWidget(title, parent=self)
        elif widget_type == "Mini graphe":
            widget = MiniGraphWidget(title, parent=self)
            
        if widget:
            # Set signal info if available
            if config and 'signal_data' in config and config['signal_data']:
                signal_data = config['signal_data']
                widget.signal_name = f"{signal_data['message']}.{signal_data['signal']}"
            
            widget.setMinimumSize(180, 180)
            self.grid_layout.addWidget(widget, row, col, rowspan, colspan)
            self.widgets[(row, col)] = widget
            
            # Save configuration
            self.widget_configs[(row, col)] = {
                "type": widget_type,
                "title": title,
                "row": row,
                "col": col,
                "rowspan": rowspan,
                "colspan": colspan,
                "config": config or {}
            }
            
    def update_widget_value(self, row, col, value):
        """Update a widget's value"""
        widget = self.widgets.get((row, col))
        if widget and hasattr(widget, 'set_value'):
            widget.set_value(value)
            
    def export_dashboard(self):
        """Export dashboard configuration to JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le dashboard",
            f"{self.dashboard_name}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            config = {
                "name": self.dashboard_name,
                "widgets": list(self.widget_configs.values())
            }
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Dashboard exporté vers:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur d'export",
                    f"Impossible d'exporter le dashboard:\n{str(e)}"
                )
                
    def import_dashboard(self, file_path):
        """Import dashboard configuration from JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.dashboard_name = config.get("name", "Dashboard")
            
            # Clear existing widgets
            for widget in self.widgets.values():
                widget.deleteLater()
            self.widgets.clear()
            self.widget_configs.clear()
            
            # Add widgets from config
            for widget_config in config.get("widgets", []):
                self.add_widget(
                    widget_config["type"],
                    widget_config["title"],
                    widget_config["row"],
                    widget_config["col"],
                    widget_config.get("rowspan", 1),
                    widget_config.get("colspan", 1),
                    widget_config.get("config", {})
                )
                
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur d'import",
                f"Impossible d'importer le dashboard:\n{str(e)}"
            )
            return False
    
    def set_available_signals(self, interface_id, signals):
        """Set available signals for this dashboard
        
        Args:
            interface_id: ID of the CAN interface
            signals: List of tuples (msg_name, signal_name, unit)
        """
        self.available_signals[interface_id] = signals
    
    def edit_widget(self, widget):
        """Edit an existing widget"""
        # Find widget position
        widget_pos = None
        for pos, w in self.widgets.items():
            if w == widget:
                widget_pos = pos
                break
        
        if not widget_pos:
            return
        
        config = self.widget_configs.get(widget_pos, {})
        
        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Éditer Widget")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        # Title
        title_edit = QLineEdit()
        title_edit.setText(config.get('title', ''))
        form.addRow("Titre:", title_edit)
        
        # Signal selection
        signal_combo = QComboBox()
        signal_combo.addItem("Sélectionner un signal...", None)
        
        current_signal_data = config.get('config', {}).get('signal_data')
        current_index = 0
        
        # Populate signals
        for interface_id, signals in self.available_signals.items():
            for idx, (msg_name, signal_name, unit) in enumerate(signals):
                display_text = f"[{interface_id}] {msg_name} → {signal_name}"
                if unit:
                    display_text += f" ({unit})"
                signal_data = {
                    'interface_id': interface_id,
                    'message': msg_name,
                    'signal': signal_name,
                    'unit': unit
                }
                signal_combo.addItem(display_text, signal_data)
                
                # Check if this is the current signal
                if current_signal_data and \
                   signal_data['interface_id'] == current_signal_data.get('interface_id') and \
                   signal_data['message'] == current_signal_data.get('message') and \
                   signal_data['signal'] == current_signal_data.get('signal'):
                    current_index = signal_combo.count() - 1
        
        signal_combo.setCurrentIndex(current_index)
        form.addRow("Signal:", signal_combo)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Update widget
            new_title = title_edit.text()
            signal_data = signal_combo.currentData()
            
            widget.title = new_title
            if hasattr(widget, 'setWindowTitle'):
                widget.setWindowTitle(new_title)
            
            if signal_data:
                widget.signal_name = f"{signal_data['message']}.{signal_data['signal']}"
            
            # Update config
            config['title'] = new_title
            if 'config' not in config:
                config['config'] = {}
            config['config']['signal_data'] = signal_data
            
            widget.update()
    
    def remove_widget(self, widget):
        """Remove a widget from the dashboard"""
        # Find widget position
        widget_pos = None
        for pos, w in self.widgets.items():
            if w == widget:
                widget_pos = pos
                break
        
        if not widget_pos:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Supprimer Widget",
            "Êtes-vous sûr de vouloir supprimer ce widget ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from layout and delete
            self.grid_layout.removeWidget(widget)
            widget.deleteLater()
            
            # Remove from dictionaries
            del self.widgets[widget_pos]
            if widget_pos in self.widget_configs:
                del self.widget_configs[widget_pos]
    
    def resize_widget(self, widget):
        """Resize a widget (change rowspan/colspan)"""
        # Find widget position
        widget_pos = None
        for pos, w in self.widgets.items():
            if w == widget:
                widget_pos = pos
                break
        
        if not widget_pos:
            return
        
        config = self.widget_configs.get(widget_pos, {})
        current_rowspan = config.get('rowspan', 1)
        current_colspan = config.get('colspan', 1)
        
        # Create resize dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Redimensionner Widget")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        # Rowspan
        rowspan_spin = QSpinBox()
        rowspan_spin.setMinimum(1)
        rowspan_spin.setMaximum(5)
        rowspan_spin.setValue(current_rowspan)
        form.addRow("Hauteur (lignes):", rowspan_spin)
        
        # Colspan
        colspan_spin = QSpinBox()
        colspan_spin.setMinimum(1)
        colspan_spin.setMaximum(5)
        colspan_spin.setValue(current_colspan)
        form.addRow("Largeur (colonnes):", colspan_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            new_rowspan = rowspan_spin.value()
            new_colspan = colspan_spin.value()
            
            # Remove from layout
            self.grid_layout.removeWidget(widget)
            
            # Re-add with new size
            row, col = widget_pos
            self.grid_layout.addWidget(widget, row, col, new_rowspan, new_colspan)
            
            # Update config
            config['rowspan'] = new_rowspan
            config['colspan'] = new_colspan


class DashboardManager(QWidget):
    """Manager for multiple dashboards"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboards = {}  # name -> DashboardWidget
        self.current_dashboard = None
        self.all_available_signals = {}  # interface_id -> signals (stored centrally)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("header")
        toolbar.setFixedHeight(40)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 0, 8, 0)
        
        # Dashboard selector
        self.dashboard_combo = QComboBox()
        self.dashboard_combo.currentTextChanged.connect(self.switch_dashboard)
        toolbar_layout.addWidget(self.dashboard_combo)
        
        toolbar_layout.addStretch()
        
        # New dashboard
        new_btn = QPushButton("+ Nouveau")
        new_btn.clicked.connect(self.create_dashboard)
        toolbar_layout.addWidget(new_btn)
        
        # Import
        import_btn = QPushButton("📥 Importer")
        import_btn.clicked.connect(self.import_dashboard)
        toolbar_layout.addWidget(import_btn)
        
        # Delete dashboard
        delete_btn = QPushButton("🗑️ Supprimer")
        delete_btn.clicked.connect(self.delete_dashboard)
        toolbar_layout.addWidget(delete_btn)
        
        layout.addWidget(toolbar)
        
        # Dashboard container
        self.stack_layout = QVBoxLayout()
        layout.addLayout(self.stack_layout)
        
    def create_dashboard(self, name=None):
        """Create a new dashboard"""
        if not name:
            from PyQt5.QtWidgets import QInputDialog
            name, ok = QInputDialog.getText(
                self,
                "Nouveau Dashboard",
                "Nom du dashboard:"
            )
            if not ok or not name:
                return
                
        dashboard = DashboardWidget(name)
        # Set available signals from centralized storage
        for interface_id, signals in self.all_available_signals.items():
            dashboard.set_available_signals(interface_id, signals)
        
        self.dashboards[name] = dashboard
        
        self.dashboard_combo.addItem(name)
        self.dashboard_combo.setCurrentText(name)
        
    def switch_dashboard(self, name):
        """Switch to a different dashboard"""
        # Hide current
        if self.current_dashboard:
            self.current_dashboard.hide()
            self.stack_layout.removeWidget(self.current_dashboard)
            
        # Show new
        if name in self.dashboards:
            self.current_dashboard = self.dashboards[name]
            self.stack_layout.addWidget(self.current_dashboard)
            self.current_dashboard.show()
            
    def import_dashboard(self):
        """Import a dashboard from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un dashboard",
            "",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                name = config.get("name", "Dashboard")
                
                # Create dashboard
                dashboard = DashboardWidget(name)
                # Set available signals from centralized storage
                for interface_id, signals in self.all_available_signals.items():
                    dashboard.set_available_signals(interface_id, signals)
                
                if dashboard.import_dashboard(file_path):
                    self.dashboards[name] = dashboard
                    self.dashboard_combo.addItem(name)
                    self.dashboard_combo.setCurrentText(name)
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'importer le dashboard:\n{str(e)}"
                )
    
    def delete_dashboard(self):
        """Delete the current dashboard"""
        current_name = self.dashboard_combo.currentText()
        
        if not current_name:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Supprimer Dashboard",
            f"Êtes-vous sûr de vouloir supprimer le dashboard '{current_name}' ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from combo
            index = self.dashboard_combo.findText(current_name)
            if index >= 0:
                self.dashboard_combo.removeItem(index)
            
            # Delete dashboard widget
            if current_name in self.dashboards:
                dashboard = self.dashboards[current_name]
                if dashboard == self.current_dashboard:
                    self.stack_layout.removeWidget(dashboard)
                    self.current_dashboard = None
                dashboard.deleteLater()
                del self.dashboards[current_name]
    
    def set_available_signals(self, interface_id, signals):
        """Set available signals for all dashboards
        
        Args:
            interface_id: ID of the CAN interface
            signals: List of tuples (msg_name, signal_name, unit)
        """
        # Store centrally
        self.all_available_signals[interface_id] = signals
        
        # Update all existing dashboards
        for dashboard in self.dashboards.values():
            dashboard.set_available_signals(interface_id, signals)
