#!/usr/bin/env python3
"""
CAN Real-Time Plotter - Main Application Entry Point

A comprehensive tool for CAN bus data visualization, recording, and analysis.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.gui.modern_main_window import ModernMainWindow


def main():
    """Initialize and run the application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("CAN Real-Time Plotter")
    app.setOrganizationName("CANTools")
    
    # Create and show modern main window
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
