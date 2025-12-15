"""
Test script for the new v2.0 architecture
Tests all major components without requiring actual CAN hardware
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def test_imports():
    """Test that all new modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.gui.interface_manager import InterfaceManagerPanel, CanInterfaceWidget
        print("✅ interface_manager imported successfully")
    except Exception as e:
        print(f"❌ interface_manager import failed: {e}")
        return False
        
    try:
        from src.gui.message_browser import MessageBrowser, SignalValueWidget
        print("✅ message_browser imported successfully")
    except Exception as e:
        print(f"❌ message_browser import failed: {e}")
        return False
        
    try:
        from src.gui.dashboard_system import (DashboardManager, DashboardWidget,
                                              GaugeWidget, NumericDisplayWidget,
                                              BinaryStateWidget, EnumDisplayWidget,
                                              MiniGraphWidget)
        print("✅ dashboard_system imported successfully")
    except Exception as e:
        print(f"❌ dashboard_system import failed: {e}")
        return False
        
    try:
        from src.gui.modern_main_window import ModernMainWindow
        print("✅ modern_main_window imported successfully")
    except Exception as e:
        print(f"❌ modern_main_window import failed: {e}")
        return False
        
    return True


def test_widgets():
    """Test that widgets can be instantiated"""
    print("\nTesting widget instantiation...")
    
    app = QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    
    try:
        from src.gui.interface_manager import CanInterfaceWidget
        widget = CanInterfaceWidget("test_interface", "Virtual")
        print("✅ CanInterfaceWidget created")
        widget.deleteLater()
    except Exception as e:
        print(f"❌ CanInterfaceWidget failed: {e}")
        return False
        
    try:
        from src.gui.dashboard_system import GaugeWidget
        widget = GaugeWidget("Test Gauge", 0, 100, "km/h")
        print("✅ GaugeWidget created")
        widget.deleteLater()
    except Exception as e:
        print(f"❌ GaugeWidget failed: {e}")
        return False
        
    try:
        from src.gui.dashboard_system import NumericDisplayWidget
        widget = NumericDisplayWidget("Test Value", "°C", 2)
        print("✅ NumericDisplayWidget created")
        widget.deleteLater()
    except Exception as e:
        print(f"❌ NumericDisplayWidget failed: {e}")
        return False
        
    try:
        from src.gui.dashboard_system import BinaryStateWidget
        widget = BinaryStateWidget("Test State", "ON", "OFF")
        print("✅ BinaryStateWidget created")
        widget.deleteLater()
    except Exception as e:
        print(f"❌ BinaryStateWidget failed: {e}")
        return False
        
    try:
        from src.gui.dashboard_system import EnumDisplayWidget
        widget = EnumDisplayWidget("Test Enum", {0: "Value0", 1: "Value1"})
        print("✅ EnumDisplayWidget created")
        widget.deleteLater()
    except Exception as e:
        print(f"❌ EnumDisplayWidget failed: {e}")
        return False
        
    return True


def test_dashboard_json():
    """Test dashboard JSON loading"""
    print("\nTesting dashboard JSON...")
    
    import json
    import os
    
    dashboard_path = "dashboards/example_vehicle.json"
    
    if not os.path.exists(dashboard_path):
        print(f"⚠️  Dashboard file not found: {dashboard_path}")
        return True  # Not critical
        
    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        assert "name" in config, "Missing 'name' field"
        assert "widgets" in config, "Missing 'widgets' field"
        assert isinstance(config["widgets"], list), "'widgets' should be a list"
        
        print(f"✅ Dashboard JSON valid: {config['name']}")
        print(f"   - Widgets: {len(config['widgets'])}")
        
        # Check widget structure
        for i, widget in enumerate(config["widgets"]):
            required = ["type", "title", "row", "col", "rowspan", "colspan", "config"]
            for field in required:
                assert field in widget, f"Widget {i} missing field: {field}"
                
        print(f"✅ All {len(config['widgets'])} widgets have valid structure")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard JSON test failed: {e}")
        return False


def test_main_window():
    """Test main window creation"""
    print("\nTesting main window creation...")
    
    try:
        app = QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app = QApplication(sys.argv)
        
        from src.gui.modern_main_window import ModernMainWindow
        window = ModernMainWindow()
        
        # Check main components
        assert hasattr(window, 'interface_panel'), "Missing interface_panel"
        assert hasattr(window, 'message_browser'), "Missing message_browser"
        assert hasattr(window, 'dashboard_manager'), "Missing dashboard_manager"
        assert hasattr(window, 'tab_widget'), "Missing tab_widget"
        
        print("✅ ModernMainWindow created successfully")
        print(f"   - Interface panel: {'✓' if window.interface_panel else '✗'}")
        print(f"   - Message browser: {'✓' if window.message_browser else '✗'}")
        print(f"   - Dashboard manager: {'✓' if window.dashboard_manager else '✗'}")
        print(f"   - Tab widget: {'✓' if window.tab_widget else '✗'}")
        print(f"   - Tabs count: {window.tab_widget.count()}")
        
        window.deleteLater()
        return True
        
    except Exception as e:
        print(f"❌ Main window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("CAN Real-Time Plotter v2.0 - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Widgets
    if results[-1][1]:  # Only if imports passed
        results.append(("Widgets", test_widgets()))
    else:
        results.append(("Widgets", None))  # Skipped
        
    # Test 3: Dashboard JSON
    results.append(("Dashboard JSON", test_dashboard_json()))
    
    # Test 4: Main Window
    if results[0][1]:  # Only if imports passed
        results.append(("Main Window", test_main_window()))
    else:
        results.append(("Main Window", None))  # Skipped
        
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⊘  SKIPPED"
        print(f"{status:12} - {name}")
        
    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    if failed > 0:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False
    else:
        print("\n🎉 All tests passed! v2.0 is ready to use.")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
