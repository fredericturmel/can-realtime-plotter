"""
Trigger Configuration Widget

Widget for configuring trigger conditions.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QListWidget, QListWidgetItem,
                             QDialog, QFormLayout, QComboBox, QDoubleSpinBox,
                             QLineEdit, QCheckBox, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from src.triggers.trigger_system import (TriggerManager, Trigger, TriggerCondition,
                                          TriggerConditionType, TriggerLogic, TriggerAction)


class TriggerConfigWidget(QWidget):
    """Widget for configuring triggers."""
    
    def __init__(self, trigger_manager: TriggerManager, parent=None):
        super().__init__(parent)
        self.trigger_manager = trigger_manager
        self.available_signals = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Trigger list
        list_group = QGroupBox("Configured Triggers")
        list_layout = QVBoxLayout()
        
        self.trigger_list = QListWidget()
        list_layout.addWidget(self.trigger_list)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Trigger")
        self.add_btn.clicked.connect(self.add_trigger)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_trigger)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.clicked.connect(self.remove_trigger)
        
        self.enable_btn = QPushButton("Enable/Disable")
        self.enable_btn.clicked.connect(self.toggle_trigger)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.enable_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def set_available_signals(self, signals: list):
        """Set available signals for trigger configuration."""
        self.available_signals = signals
        
    def add_trigger(self):
        """Add a new trigger."""
        if not self.available_signals:
            QMessageBox.warning(self, "Warning", "Please select signals first")
            return
        
        dialog = TriggerDialog(self.available_signals, parent=self)
        if dialog.exec_():
            trigger = dialog.get_trigger()
            self.trigger_manager.add_trigger(trigger)
            self.refresh_trigger_list()
    
    def edit_trigger(self):
        """Edit selected trigger."""
        current_item = self.trigger_list.currentItem()
        if not current_item:
            return
        
        trigger_name = current_item.data(Qt.UserRole)
        trigger = self.trigger_manager.get_trigger(trigger_name)
        
        if trigger:
            dialog = TriggerDialog(self.available_signals, trigger, parent=self)
            if dialog.exec_():
                # Remove old and add new
                self.trigger_manager.remove_trigger(trigger_name)
                new_trigger = dialog.get_trigger()
                self.trigger_manager.add_trigger(new_trigger)
                self.refresh_trigger_list()
    
    def remove_trigger(self):
        """Remove selected trigger."""
        current_item = self.trigger_list.currentItem()
        if not current_item:
            return
        
        trigger_name = current_item.data(Qt.UserRole)
        self.trigger_manager.remove_trigger(trigger_name)
        self.refresh_trigger_list()
    
    def toggle_trigger(self):
        """Toggle trigger enabled state."""
        current_item = self.trigger_list.currentItem()
        if not current_item:
            return
        
        trigger_name = current_item.data(Qt.UserRole)
        trigger = self.trigger_manager.get_trigger(trigger_name)
        
        if trigger:
            trigger.set_enabled(not trigger.enabled)
            self.refresh_trigger_list()
    
    def refresh_trigger_list(self):
        """Refresh the trigger list display."""
        self.trigger_list.clear()
        
        for trigger in self.trigger_manager.get_all_triggers():
            status = "✓" if trigger.enabled else "✗"
            text = f"{status} {trigger.name} [{trigger.trigger_count} fires]"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, trigger.name)
            self.trigger_list.addItem(item)


class TriggerDialog(QDialog):
    """Dialog for creating/editing triggers."""
    
    def __init__(self, available_signals: list, trigger: Trigger = None, parent=None):
        super().__init__(parent)
        self.available_signals = available_signals
        self.editing_trigger = trigger
        self.conditions = []
        
        self.setWindowTitle("Configure Trigger")
        self.setModal(True)
        self.resize(500, 400)
        
        self.init_ui()
        
        if trigger:
            self.load_trigger(trigger)
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Basic settings
        basic_group = QGroupBox("Trigger Settings")
        basic_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("Name:", self.name_edit)
        
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(['AND', 'OR'])
        basic_layout.addRow("Logic:", self.logic_combo)
        
        self.single_shot_check = QCheckBox("Single Shot")
        basic_layout.addRow("", self.single_shot_check)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Conditions
        cond_group = QGroupBox("Conditions")
        cond_layout = QVBoxLayout()
        
        self.condition_list = QListWidget()
        cond_layout.addWidget(self.condition_list)
        
        cond_btn_layout = QHBoxLayout()
        add_cond_btn = QPushButton("Add Condition")
        add_cond_btn.clicked.connect(self.add_condition)
        remove_cond_btn = QPushButton("Remove")
        remove_cond_btn.clicked.connect(self.remove_condition)
        
        cond_btn_layout.addWidget(add_cond_btn)
        cond_btn_layout.addWidget(remove_cond_btn)
        cond_btn_layout.addStretch()
        cond_layout.addLayout(cond_btn_layout)
        
        cond_group.setLayout(cond_layout)
        layout.addWidget(cond_group)
        
        # OK/Cancel
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_condition(self):
        """Add a condition."""
        dialog = ConditionDialog(self.available_signals, parent=self)
        if dialog.exec_():
            condition = dialog.get_condition()
            self.conditions.append(condition)
            self.refresh_condition_list()
    
    def remove_condition(self):
        """Remove selected condition."""
        current_row = self.condition_list.currentRow()
        if current_row >= 0:
            del self.conditions[current_row]
            self.refresh_condition_list()
    
    def refresh_condition_list(self):
        """Refresh condition list display."""
        self.condition_list.clear()
        for condition in self.conditions:
            self.condition_list.addItem(str(condition))
    
    def load_trigger(self, trigger: Trigger):
        """Load trigger data into dialog."""
        self.name_edit.setText(trigger.name)
        self.logic_combo.setCurrentText(trigger.logic.value)
        self.single_shot_check.setChecked(trigger.single_shot)
        self.conditions = trigger.conditions.copy()
        self.refresh_condition_list()
    
    def get_trigger(self) -> Trigger:
        """Get configured trigger."""
        logic = TriggerLogic.AND if self.logic_combo.currentText() == 'AND' else TriggerLogic.OR
        trigger = Trigger(self.name_edit.text(), logic)
        trigger.single_shot = self.single_shot_check.isChecked()
        
        for condition in self.conditions:
            trigger.add_condition(condition)
        
        return trigger


class ConditionDialog(QDialog):
    """Dialog for creating a trigger condition."""
    
    def __init__(self, available_signals: list, parent=None):
        super().__init__(parent)
        self.available_signals = available_signals
        
        self.setWindowTitle("Add Condition")
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QFormLayout(self)
        
        self.signal_combo = QComboBox()
        self.signal_combo.addItems(self.available_signals)
        layout.addRow("Signal:", self.signal_combo)
        
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(['>', '<', '==', '!=', '>=', '<=', 'rising', 'falling', 'change'])
        self.condition_combo.currentTextChanged.connect(self.on_condition_changed)
        layout.addRow("Condition:", self.condition_combo)
        
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(-1e9, 1e9)
        self.threshold_spin.setDecimals(3)
        layout.addRow("Threshold:", self.threshold_spin)
        
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow("", button_layout)
    
    def on_condition_changed(self, condition_text: str):
        """Handle condition type change."""
        # Disable threshold for change detection
        if condition_text == 'change':
            self.threshold_spin.setEnabled(False)
        else:
            self.threshold_spin.setEnabled(True)
    
    def get_condition(self) -> TriggerCondition:
        """Get configured condition."""
        signal_name = self.signal_combo.currentText()
        condition_text = self.condition_combo.currentText()
        
        # Map text to enum
        condition_map = {
            '>': TriggerConditionType.GREATER_THAN,
            '<': TriggerConditionType.LESS_THAN,
            '==': TriggerConditionType.EQUAL,
            '!=': TriggerConditionType.NOT_EQUAL,
            '>=': TriggerConditionType.GREATER_EQUAL,
            '<=': TriggerConditionType.LESS_EQUAL,
            'rising': TriggerConditionType.RISING_EDGE,
            'falling': TriggerConditionType.FALLING_EDGE,
            'change': TriggerConditionType.CHANGE
        }
        
        condition_type = condition_map[condition_text]
        threshold = self.threshold_spin.value() if condition_text != 'change' else None
        
        return TriggerCondition(signal_name, condition_type, threshold)
