# CAN Real-Time Plotter

A comprehensive CAN bus data analysis and visualization application supporting PCAN and IXXAT USB adapters.

## Features

- **Real-time Data Plotting**: Visualize CAN signals in real-time with multiple configurable plots
- **Hardware Support**: PCAN and IXXAT USB adapters
- **DBC/SYM Support**: Import and decode CAN signals using DBC or SYM files
- **Data Recording**: Record CAN messages to CSV format
- **Message Transmission**: Send CAN messages with signal encoding
- **Signal Processing**: 
  - Statistical analysis (average, min, max)
  - FFT analysis for frequency domain visualization
- **Advanced Triggers**: Complex trigger logic with AND/OR conditions
- **Multi-source**: Support for multiple CAN channels simultaneously
- **Cross-platform**: Works on Windows and Linux

## Requirements

- Python 3.8+
- PCAN or IXXAT hardware adapter
- Appropriate drivers installed (PCAN-Basic or IXXAT VCI)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd can-realtime-plotter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Project Structure

```
can-realtime-plotter/
├── main.py                 # Application entry point
├── src/
│   ├── can_interface/      # CAN hardware interface
│   ├── data_processing/    # Signal processing and statistics
│   ├── gui/                # PyQt GUI components
│   ├── parsers/            # DBC/SYM file parsers
│   ├── recorder/           # Data recording module
│   └── triggers/           # Trigger system
├── config/                 # Configuration files
├── docs/                   # Documentation
└── tests/                  # Unit tests
```

## Usage

### Starting the Application

1. Launch the application
2. Select your CAN interface (PCAN/IXXAT)
3. Load a DBC or SYM file
4. Select signals to plot
5. Start the CAN interface

### Recording Data

- Click "Start Recording" to begin logging
- Data is saved in CSV format with timestamps
- Stop recording at any time

### Sending Messages

- Use the Message Sender panel
- Encode signals using loaded DBC/SYM
- Send periodic or single-shot messages

### Triggers

- Configure complex trigger conditions
- Combine multiple signal conditions with AND/OR logic
- Trigger actions: start/stop recording, capture snapshot

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.
