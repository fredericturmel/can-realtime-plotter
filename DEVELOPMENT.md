# CAN Real-Time Plotter - Development Notes

## Project Structure

```
can-realtime-plotter/
├── main.py                          # Application entry point
├── src/
│   ├── can_interface/
│   │   └── can_manager.py          # CAN hardware interface manager
│   ├── data_processing/
│   │   └── signal_processor.py     # Signal analysis & statistics
│   ├── gui/
│   │   ├── main_window.py          # Main application window
│   │   ├── connection_dialog.py    # CAN connection dialog
│   │   ├── signal_selector.py      # Signal selection dialog
│   │   ├── plot_widget.py          # Real-time plotting widget
│   │   ├── statistics_panel.py     # Statistics display panel
│   │   ├── message_sender.py       # CAN message sender widget
│   │   └── trigger_config.py       # Trigger configuration UI
│   ├── parsers/
│   │   └── database_parser.py      # DBC/SYM file parser
│   ├── recorder/
│   │   └── data_recorder.py        # CSV data recorder
│   └── triggers/
│       └── trigger_system.py       # Complex trigger system
├── config/                          # Configuration files
├── recordings/                      # Recorded data output
├── tests/                          # Unit tests
└── docs/                           # Documentation
```

## Key Features Implemented

### 1. CAN Interface Support
- **Hardware**: PCAN, IXXAT, SocketCAN (Linux)
- **Auto-detection**: Scans for available interfaces
- **Connection management**: Connect/disconnect with status feedback

### 2. Database Parsing
- **Formats**: DBC and SYM files
- **Decoding**: Automatic signal extraction from raw data
- **Encoding**: Build messages from signal values

### 3. Real-Time Plotting
- **Multiple modes**: Separate plots, single plot, grid layout
- **Configurable**: Time windows, colors, auto-scaling
- **Performance**: Optimized with pyqtgraph for real-time display

### 4. Data Recording
- **Formats**: CSV output
- **Modes**: Raw CAN messages or decoded signals
- **Timestamped**: All data includes precise timestamps

### 5. Signal Processing
- **Statistics**: Mean, min, max, std dev, RMS
- **FFT**: Frequency domain analysis
- **Filtering**: Lowpass, highpass, bandpass filters
- **Moving average**: Smoothing algorithms

### 6. Message Transmission
- **GUI-based**: Easy signal value entry
- **Periodic sending**: Configurable transmission rate
- **Database integration**: Uses loaded DBC/SYM for encoding

### 7. Advanced Triggers
- **Complex logic**: AND/OR combinations
- **Condition types**: >, <, ==, !=, >=, <=, rising edge, falling edge, change
- **Multiple conditions**: Combine any number of conditions
- **Single-shot or continuous**: Configurable trigger behavior

## Dependencies

- **PyQt5**: GUI framework
- **pyqtgraph**: High-performance plotting
- **python-can**: CAN interface abstraction
- **cantools**: DBC/SYM parsing
- **numpy**: Numerical operations
- **scipy**: Signal processing
- **pandas**: Data handling

## Architecture Patterns

### Signal/Slot (Qt)
All components use Qt signals for event-driven communication:
- CAN messages trigger signal emissions
- GUI updates on signal reception
- Loose coupling between modules

### Manager Pattern
- `CANInterfaceManager`: Centralized CAN control
- `TriggerManager`: Trigger lifecycle management

### MVC-like Separation
- Models: Data parsers, signal processor
- Views: Qt widgets
- Controllers: Manager classes

## Extension Points

### Adding New CAN Interfaces
1. python-can supports many interfaces
2. Add to `SUPPORTED_INTERFACES` in `can_manager.py`
3. Update connection dialog

### Custom Signal Processing
1. Extend `SignalProcessor` class
2. Add methods for new algorithms
3. Expose in GUI if needed

### Additional Trigger Actions
1. Add to `TriggerAction` enum
2. Implement action handler in main window
3. Update trigger configuration UI

### New Export Formats
1. Extend `DataRecorder` class
2. Add format-specific writers
3. Update UI for format selection

## Testing Strategy

- **Unit tests**: Core functionality (parsers, processors)
- **Integration tests**: CAN interface with virtual bus
- **GUI tests**: pytest-qt for widget testing
- **Manual testing**: Real hardware validation

## Performance Considerations

- **Deques**: Fixed-size buffers for memory efficiency
- **Update rate**: 20 Hz plot updates (configurable)
- **Sampling**: Max 10,000 samples per signal
- **Threading**: python-can handles CAN reception in threads

## Cross-Platform Notes

### Windows
- PCAN-Basic API via python-can
- IXXAT VCI support
- Tested on Windows 10/11

### Linux
- SocketCAN native support
- Virtual CAN for testing
- Requires appropriate permissions for CAN devices

### Potential Issues
- Hardware drivers must be installed separately
- Linux: May need to run with sudo or add user to appropriate groups
- Windows: Some antivirus may flag CAN drivers

## Future Enhancements

- [ ] Playback mode for recorded data
- [ ] Advanced FFT visualization (spectrogram)
- [ ] Export plots as images
- [ ] Custom trigger actions (scripting)
- [ ] Multiple CAN channels simultaneously
- [ ] Network support (remote CAN access)
- [ ] Plugin system for custom processing
- [ ] Database editor
- [ ] Real-time performance metrics
- [ ] Dark theme support
