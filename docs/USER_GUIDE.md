# Documentation

## User Guide

### Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Hardware Drivers**
   - **PCAN**: Download and install PCAN-Basic driver from PEAK-System
   - **IXXAT**: Download and install IXXAT VCI driver from HMS Networks

3. **Run the Application**
   ```bash
   python main.py
   ```

### Connecting to CAN Interface

1. Click "Connect" button
2. Select your interface type (PCAN, IXXAT, or SocketCAN for Linux)
3. Select the channel (e.g., PCAN_USBBUS1)
4. Set bitrate (default: 500000 bps)
5. Click "Connect"

### Loading a Database File

1. Click "Load DBC/SYM" or use File menu
2. Select your .dbc or .sym file
3. The database will be parsed and loaded

### Selecting Signals to Plot

1. Click "Select Signals" (requires database loaded first)
2. Browse or search for signals
3. Check the signals you want to plot
4. Click OK

### Recording Data

1. Connect to CAN interface
2. Click "Start Recording"
3. Data will be saved to the `recordings/` directory
4. Click "Stop Recording" when done

### Sending Messages

1. Go to "Message Sender" tab
2. Select a message from the dropdown
3. Set signal values
4. Click "Send Once" or enable "Send Periodically"

### Configuring Triggers

1. Go to "Triggers" tab
2. Click "Add Trigger"
3. Set trigger name and logic (AND/OR)
4. Add conditions:
   - Select signal
   - Choose condition type (>, <, ==, rising edge, etc.)
   - Set threshold value
5. Click OK

## API Documentation

### CANInterfaceManager

Manages CAN hardware connections.

```python
from src.can_interface.can_manager import CANInterfaceManager

manager = CANInterfaceManager()
manager.connect(interface='pcan', channel='PCAN_USBBUS1', bitrate=500000)
```

### DatabaseParser

Parses DBC and SYM files.

```python
from src.parsers.database_parser import DatabaseParser

parser = DatabaseParser()
parser.load_database('path/to/file.dbc')
messages = parser.get_messages()
```

### SignalProcessor

Processes signal data for analysis.

```python
from src.data_processing.signal_processor import SignalProcessor

processor = SignalProcessor()
processor.add_sample('signal_name', value, timestamp)
stats = processor.get_statistics('signal_name')
freq, magnitude = processor.calculate_fft('signal_name')
```

### TriggerSystem

Creates complex trigger conditions.

```python
from src.triggers.trigger_system import (Trigger, TriggerCondition, 
                                          TriggerConditionType, TriggerLogic)

trigger = Trigger('my_trigger', TriggerLogic.AND)
condition = TriggerCondition('signal_name', TriggerConditionType.GREATER_THAN, 100.0)
trigger.add_condition(condition)
```

## Troubleshooting

### Cannot Connect to PCAN

- Ensure PCAN-Basic driver is installed
- Check that the device is connected via USB
- Verify the channel name (use PCAN-View to check)

### Cannot Connect to IXXAT

- Ensure IXXAT VCI driver is installed
- Check device connection
- Verify channel number

### Linux SocketCAN Setup

```bash
# Bring up CAN interface
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Use virtual CAN for testing
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Database Loading Errors

- Ensure file is valid DBC or SYM format
- Check file permissions
- Try opening in a text editor to verify format

## Advanced Features

### FFT Analysis

Access FFT analysis in the signal processor:
- Useful for frequency domain analysis
- Identifies periodic patterns
- Can detect noise and harmonics

### Signal Filtering

Apply filters to signals:
- Lowpass: Remove high-frequency noise
- Highpass: Remove DC offset and slow drift
- Bandpass: Isolate specific frequency range

### Complex Triggers

Combine multiple conditions:
- Use AND logic: All conditions must be true
- Use OR logic: Any condition triggers
- Mix comparison and edge detection
- Single-shot or continuous triggering
