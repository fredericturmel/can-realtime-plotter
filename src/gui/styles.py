"""
Modern UI Styles

Modern stylesheet and styling utilities for the application.
"""

DARK_THEME = """
/* Main Window */
QMainWindow {
    background-color: #0d1117;
}

/* Central Widget */
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', -apple-system, system-ui, sans-serif;
    font-size: 9pt;
}

/* Group Box */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    margin-top: 16px;
    padding: 16px;
    padding-top: 24px;
    font-weight: 600;
    color: #c9d1d9;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #58a6ff;
    font-size: 10pt;
}

/* Push Buttons */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-height: 28px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #58a6ff;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

/* Primary Button */
QPushButton#primaryButton {
    background-color: #238636;
    border-color: #238636;
    color: #ffffff;
}

QPushButton#primaryButton:hover {
    background-color: #2ea043;
    border-color: #2ea043;
}

/* Danger Button */
QPushButton#dangerButton {
    background-color: #da3633;
    border-color: #da3633;
    color: #ffffff;
}

QPushButton#dangerButton:hover {
    background-color: #f85149;
    border-color: #f85149;
}

/* Success Button */
QPushButton#successButton {
    background-color: #238636;
    border-color: #238636;
    color: #ffffff;
}

QPushButton#successButton:hover {
    background-color: #2ea043;
    border-color: #2ea043;
}

/* Line Edit */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #c9d1d9;
    selection-background-color: #1f6feb;
}

QLineEdit:focus {
    border-color: #58a6ff;
    background-color: #161b22;
}

QLineEdit:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}

/* Combo Box */
QComboBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #c9d1d9;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #58a6ff;
    background-color: #161b22;
}

QComboBox:focus {
    border-color: #58a6ff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #c9d1d9;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
    color: #c9d1d9;
    outline: none;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    color: #c9d1d9;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #58a6ff;
    background-color: #161b22;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #21262d;
    border-top-right-radius: 4px;
    border-left: 1px solid #30363d;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #21262d;
    border-bottom-right-radius: 4px;
    border-left: 1px solid #30363d;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #30363d;
}

/* Check Box */
QCheckBox {
    spacing: 8px;
    color: #c9d1d9;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #30363d;
    background-color: #0d1117;
}

QCheckBox::indicator:hover {
    border-color: #58a6ff;
    background-color: #161b22;
}

QCheckBox::indicator:checked {
    background-color: #1f6feb;
    border-color: #1f6feb;
    image: url(none);
}

/* Radio Button */
QRadioButton {
    spacing: 8px;
    color: #e0e0e0;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #4d4d4d;
    background-color: #3d3d3d;
}

QRadioButton::indicator:checked {
    background-color: #0d47a1;
    border: 2px solid #0d47a1;
}

/* Table Widget */
QTableWidget {
    background-color: #0d1117;
    alternate-background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #c9d1d9;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #1f6feb;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #161b22;
    color: #c9d1d9;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid #30363d;
    font-weight: 600;
    text-align: left;
}

QHeaderView::section:hover {
    background-color: #21262d;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #30363d;
    border-radius: 6px;
    background-color: #0d1117;
    top: 0px;
}

QTabBar::tab {
    background-color: transparent;
    color: #8b949e;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 10px 16px;
    margin-right: 8px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: transparent;
    color: #c9d1d9;
    border-bottom: 2px solid #f78166;
}

QTabBar::tab:hover:!selected {
    color: #c9d1d9;
    border-bottom: 2px solid #30363d;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #0d1117;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #0d1117;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #484f58;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu Bar */
QMenuBar {
    background-color: #161b22;
    color: #c9d1d9;
    border-bottom: 1px solid #30363d;
    padding: 4px 8px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #21262d;
}

QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #1f6feb;
}

/* Status Bar */
QStatusBar {
    background-color: #161b22;
    color: #c9d1d9;
    border-top: 1px solid #30363d;
}

QStatusBar QLabel {
    padding: 4px 12px;
    color: #8b949e;
}

/* Dock Widget */
QDockWidget {
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
    color: #e0e0e0;
}

QDockWidget::title {
    background-color: #1e1e1e;
    padding: 8px;
    border-bottom: 2px solid #4a9eff;
    font-weight: bold;
}

/* Tool Tip */
QToolTip {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 2px solid #4a9eff;
    border-radius: 6px;
    padding: 6px;
}

/* Progress Bar */
QProgressBar {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    text-align: center;
    color: #c9d1d9;
    font-weight: 600;
    min-height: 24px;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 4px;
}

/* Label */
QLabel {
    color: #c9d1d9;
}

QLabel#titleLabel {
    color: #c9d1d9;
    font-size: 14pt;
    font-weight: 600;
}

QLabel#subtitleLabel {
    color: #8b949e;
    font-size: 9pt;
}

/* Dialog */
QDialog {
    background-color: #2d2d2d;
}

QMessageBox {
    background-color: #2d2d2d;
}
"""

LIGHT_THEME = """
/* Main Window */
QMainWindow {
    background-color: #f5f5f5;
}

/* Central Widget */
QWidget {
    background-color: #ffffff;
    color: #212121;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
}

/* Group Box */
QGroupBox {
    background-color: #fafafa;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 15px;
    font-weight: bold;
    color: #212121;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 8px;
    color: #1976d2;
}

/* Push Buttons */
QPushButton {
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 28px;
}

QPushButton:hover {
    background-color: #2196f3;
}

QPushButton:pressed {
    background-color: #0d47a1;
}

QPushButton:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
}

/* Primary Button */
QPushButton#primaryButton {
    background-color: #00897b;
}

QPushButton#primaryButton:hover {
    background-color: #26a69a;
}

/* Danger Button */
QPushButton#dangerButton {
    background-color: #d32f2f;
}

QPushButton#dangerButton:hover {
    background-color: #f44336;
}

/* Success Button */
QPushButton#successButton {
    background-color: #388e3c;
}

QPushButton#successButton:hover {
    background-color: #4caf50;
}

/* Line Edit */
QLineEdit {
    background-color: #ffffff;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    padding: 6px 10px;
    color: #212121;
    selection-background-color: #1976d2;
}

QLineEdit:focus {
    border: 2px solid #1976d2;
}

/* Combo Box */
QComboBox {
    background-color: #ffffff;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    padding: 6px 10px;
    color: #212121;
    min-height: 24px;
}

QComboBox:hover {
    border: 2px solid #bdbdbd;
}

QComboBox:focus {
    border: 2px solid #1976d2;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #212121;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 2px solid #1976d2;
    selection-background-color: #1976d2;
    color: #212121;
}

/* Table Widget */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #fafafa;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    gridline-color: #e0e0e0;
    color: #212121;
}

QTableWidget::item:selected {
    background-color: #1976d2;
    color: white;
}

QHeaderView::section {
    background-color: #f5f5f5;
    color: #1976d2;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e0e0e0;
    font-weight: bold;
}

/* Tab Widget */
QTabWidget::pane {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background-color: #ffffff;
    top: -2px;
}

QTabBar::tab {
    background-color: #f5f5f5;
    color: #757575;
    border: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 20px;
    margin-right: 4px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #1976d2;
    border-bottom: 3px solid #1976d2;
}

QTabBar::tab:hover:!selected {
    background-color: #eeeeee;
    color: #424242;
}

/* Status Bar */
QStatusBar {
    background-color: #f5f5f5;
    color: #212121;
    border-top: 1px solid #e0e0e0;
}
"""


def get_theme(theme_name: str = 'dark') -> str:
    """
    Get the stylesheet for the specified theme.
    
    Args:
        theme_name: Theme name ('dark' or 'light')
        
    Returns:
        Stylesheet string
    """
    return DARK_THEME if theme_name == 'dark' else LIGHT_THEME
