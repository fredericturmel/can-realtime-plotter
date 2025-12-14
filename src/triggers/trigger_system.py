"""
Trigger System

Implements complex trigger conditions for data capture and actions.
"""

from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class TriggerConditionType(Enum):
    """Types of trigger conditions."""
    GREATER_THAN = '>'
    LESS_THAN = '<'
    EQUAL = '=='
    NOT_EQUAL = '!='
    GREATER_EQUAL = '>='
    LESS_EQUAL = '<='
    RISING_EDGE = 'rising'
    FALLING_EDGE = 'falling'
    CHANGE = 'change'


class TriggerLogic(Enum):
    """Logical operators for combining conditions."""
    AND = 'AND'
    OR = 'OR'


class TriggerAction(Enum):
    """Actions to perform when trigger fires."""
    START_RECORDING = 'start_recording'
    STOP_RECORDING = 'stop_recording'
    CAPTURE_SNAPSHOT = 'capture_snapshot'
    EMIT_SIGNAL = 'emit_signal'


class TriggerCondition:
    """Represents a single trigger condition."""
    
    def __init__(self, signal_name: str, condition_type: TriggerConditionType, 
                 threshold: Optional[float] = None):
        """
        Initialize a trigger condition.
        
        Args:
            signal_name: Name of the signal to monitor
            condition_type: Type of condition to check
            threshold: Threshold value for comparison (not needed for edge/change)
        """
        self.signal_name = signal_name
        self.condition_type = condition_type
        self.threshold = threshold
        self.last_value: Optional[float] = None
        
    def evaluate(self, value: float) -> bool:
        """
        Evaluate the condition with a signal value.
        
        Args:
            value: Current signal value
            
        Returns:
            bool: True if condition is met
        """
        result = False
        
        if self.condition_type == TriggerConditionType.GREATER_THAN:
            result = value > self.threshold
        elif self.condition_type == TriggerConditionType.LESS_THAN:
            result = value < self.threshold
        elif self.condition_type == TriggerConditionType.EQUAL:
            result = abs(value - self.threshold) < 1e-6
        elif self.condition_type == TriggerConditionType.NOT_EQUAL:
            result = abs(value - self.threshold) >= 1e-6
        elif self.condition_type == TriggerConditionType.GREATER_EQUAL:
            result = value >= self.threshold
        elif self.condition_type == TriggerConditionType.LESS_EQUAL:
            result = value <= self.threshold
        elif self.condition_type == TriggerConditionType.RISING_EDGE:
            if self.last_value is not None:
                result = self.last_value < self.threshold <= value
        elif self.condition_type == TriggerConditionType.FALLING_EDGE:
            if self.last_value is not None:
                result = self.last_value >= self.threshold > value
        elif self.condition_type == TriggerConditionType.CHANGE:
            if self.last_value is not None:
                result = abs(value - self.last_value) > 1e-6
        
        self.last_value = value
        return result
    
    def reset(self):
        """Reset the condition state."""
        self.last_value = None
    
    def __str__(self) -> str:
        """String representation of the condition."""
        if self.threshold is not None:
            return f"{self.signal_name} {self.condition_type.value} {self.threshold}"
        else:
            return f"{self.signal_name} {self.condition_type.value}"


class Trigger(QObject):
    """Represents a complete trigger with multiple conditions."""
    
    # Signals
    triggered = pyqtSignal(str, dict)  # (trigger_name, signal_values)
    
    def __init__(self, name: str, logic: TriggerLogic = TriggerLogic.AND):
        """
        Initialize a trigger.
        
        Args:
            name: Trigger name
            logic: Logic for combining conditions (AND/OR)
        """
        super().__init__()
        self.name = name
        self.logic = logic
        self.conditions: List[TriggerCondition] = []
        self.actions: List[TriggerAction] = []
        self.enabled = True
        self.trigger_count = 0
        self.armed = True  # For single-shot triggers
        self.single_shot = False
        
    def add_condition(self, condition: TriggerCondition):
        """Add a condition to the trigger."""
        self.conditions.append(condition)
    
    def add_action(self, action: TriggerAction):
        """Add an action to perform when triggered."""
        self.actions.append(action)
    
    def evaluate(self, signal_values: Dict[str, float]) -> bool:
        """
        Evaluate all conditions with current signal values.
        
        Args:
            signal_values: Dictionary of signal names to current values
            
        Returns:
            bool: True if trigger conditions are met
        """
        if not self.enabled or not self.armed:
            return False
        
        if not self.conditions:
            return False
        
        # Evaluate each condition
        results = []
        for condition in self.conditions:
            signal_value = signal_values.get(condition.signal_name)
            if signal_value is None:
                results.append(False)
            else:
                results.append(condition.evaluate(signal_value))
        
        # Combine results based on logic
        if self.logic == TriggerLogic.AND:
            triggered = all(results)
        else:  # OR
            triggered = any(results)
        
        if triggered:
            self.trigger_count += 1
            if self.single_shot:
                self.armed = False
            self.triggered.emit(self.name, signal_values)
            logger.debug(f"Trigger '{self.name}' fired (count: {self.trigger_count})")
        
        return triggered
    
    def reset(self):
        """Reset the trigger state."""
        for condition in self.conditions:
            condition.reset()
        self.armed = True
        self.trigger_count = 0
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the trigger."""
        self.enabled = enabled
    
    def __str__(self) -> str:
        """String representation of the trigger."""
        cond_str = f" {self.logic.value} ".join(str(c) for c in self.conditions)
        return f"{self.name}: {cond_str}"


class TriggerManager(QObject):
    """Manages multiple triggers."""
    
    # Signals
    trigger_fired = pyqtSignal(str, dict)  # (trigger_name, signal_values)
    
    def __init__(self):
        super().__init__()
        self.triggers: Dict[str, Trigger] = {}
        
    def add_trigger(self, trigger: Trigger):
        """Add a trigger to the manager."""
        self.triggers[trigger.name] = trigger
        trigger.triggered.connect(self._on_trigger_fired)
        logger.info(f"Added trigger: {trigger}")
    
    def remove_trigger(self, name: str):
        """Remove a trigger by name."""
        if name in self.triggers:
            del self.triggers[name]
            logger.info(f"Removed trigger: {name}")
    
    def evaluate_all(self, signal_values: Dict[str, float]):
        """
        Evaluate all triggers with current signal values.
        
        Args:
            signal_values: Dictionary of signal names to current values
        """
        for trigger in self.triggers.values():
            trigger.evaluate(signal_values)
    
    def reset_all(self):
        """Reset all triggers."""
        for trigger in self.triggers.values():
            trigger.reset()
    
    def enable_trigger(self, name: str, enabled: bool = True):
        """Enable or disable a specific trigger."""
        if name in self.triggers:
            self.triggers[name].set_enabled(enabled)
    
    def get_trigger(self, name: str) -> Optional[Trigger]:
        """Get a trigger by name."""
        return self.triggers.get(name)
    
    def get_all_triggers(self) -> List[Trigger]:
        """Get list of all triggers."""
        return list(self.triggers.values())
    
    def _on_trigger_fired(self, name: str, signal_values: dict):
        """Internal handler for trigger events."""
        self.trigger_fired.emit(name, signal_values)
