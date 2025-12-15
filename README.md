# CAN Real-Time Plotter

## 🚀 Version 2.0 - Professional Edition

A comprehensive CAN bus data analysis and visualization application with **multi-interface support**, **dynamic dashboards**, and **professional design**.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Version](https://img.shields.io/badge/version-2.0-brightgreen)

---

## 🎉 **NEW in v2.0!**

### ✨ Major Features

- **🔌 Multi-Interface Management** - Manage multiple CAN interfaces simultaneously
- **📋 Hierarchical Message Browser** - Navigate messages with full enumeration support  
- **📊 Dynamic Dashboards** - Create custom dashboards with 5 widget types
- **💾 Import/Export** - Share dashboard configurations as JSON
- **🎨 Professional Design** - Minimalist UI with single accent color
- **📈 Real-time Bus Load** - Per-interface monitoring with colored progress bars

### 📚 Documentation v2.0

- **[🚀 Quick Start](QUICK_START.md)** - Get started in 30 seconds
- **[✨ New Features](NEW_FEATURES.md)** - Complete v2.0 documentation
- **[🔄 Migration Guide](MIGRATION_GUIDE.md)** - Migrate from v1.x
- **[📊 V2 Summary](V2_SUMMARY.md)** - Complete changelog

---

## 🎯 Quick Links

- **[📖 User Guide](docs/USER_GUIDE.md)** - Complete usage instructions
- **[🏗️ Architecture](ARCHITECTURE.md)** - System design and diagrams
- **[🔧 Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[💻 Development](DEVELOPMENT.md)** - Developer notes and extension guide
- **[📋 Project Summary](PROJECT_SUMMARY.md)** - Complete feature overview

## ✨ Features

### 🔌 Hardware Support
- **PCAN** USB adapters (via PCAN-Basic)
- **IXXAT** USB adapters (via IXXAT VCI)
- **SocketCAN** (Linux native)
- **Virtual CAN** for testing

### 📊 Real-Time Visualization
- Multi-signal plotting with 20 Hz update rate
- Three plot modes: Separate, Single, Grid layout
- Configurable time windows (5s, 10s, 30s, 60s, all)
- Auto-scaling and manual zoom
- Color-coded signals with legends

### 📁 Data Management
- **DBC/SYM parsing** - Import CAN databases
- **CSV recording** - Raw messages or decoded signals
- **Signal encoding** - Send messages from GUI
- Timestamped data with microsecond precision

### 🔬 Signal Processing
- **Statistics**: Mean, Min, Max, Std Dev, RMS
- **FFT Analysis**: Frequency domain visualization
- **Digital Filters**: Lowpass, highpass, bandpass
- **Moving Average**: Configurable window sizes

### ⚡ Advanced Triggers
- Complex logic with **AND/OR** combinations
- Multiple condition types:
  - Comparisons: `>`, `<`, `==`, `!=`, `>=`, `<=`
  - Edge detection: Rising, Falling
  - Change detection
- Single-shot or continuous mode
- Trigger actions and counters

### 🎨 Professional GUI
- Modern Qt5 interface
- Tabbed layout for different functions
- Dockable statistics panel
- Connection status indicators
- Signal search and filtering

## 🚀 Quick Start

### Windows
```batch
cd can-realtime-plotter
setup.bat
venv\Scripts\activate
python main.py
```

### Linux
```bash
cd can-realtime-plotter
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python main.py
```

## 📋 Prerequisites

### Software
- Python 3.8 or higher
- pip package manager

### Hardware Drivers
- **PCAN**: [PCAN-Basic driver](https://www.peak-system.com/PCAN-Basic.239.0.html)
- **IXXAT**: [IXXAT VCI driver](https://www.ixxat.com/)
- **Linux**: SocketCAN (usually built-in)

### Python Dependencies
Automatically installed by setup scripts:
```
PyQt5 (GUI framework)
pyqtgraph (real-time plotting)
python-can (CAN interface)
cantools (DBC/SYM parsing)
numpy (numerical operations)
scipy (signal processing)
pandas (data handling)
```

## 📖 Usage Overview

### 1. Connect to CAN Interface
- Click **"Connect"** button
- Select interface type (PCAN/IXXAT/SocketCAN)
- Choose channel (e.g., PCAN_USBBUS1, can0)
- Set bitrate (default: 500 kbps)

### 2. Load Database
- Click **"Load DBC/SYM"**
- Select your CAN database file
- Signals become available for selection

### 3. Select Signals to Plot
- Click **"Select Signals"**
- Search or browse available signals
- Check signals to plot
- View in real-time

### 4. Record Data (Optional)
- Click **"Start Recording"**
- Data saves to `recordings/` directory in CSV format
- Click **"Stop Recording"** when done

### 5. Send Messages (Optional)
- Switch to **"Message Sender"** tab
- Select message and set signal values
- Send once or enable periodic transmission

### 6. Configure Triggers (Optional)
- Switch to **"Triggers"** tab
- Add trigger with complex conditions
- Set actions and logic (AND/OR)

## 📁 Project Structure

```
can-realtime-plotter/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── setup.bat / setup.sh         # Quick start scripts
│
├── src/                         # Source code
│   ├── can_interface/           # CAN hardware communication
│   ├── data_processing/         # Signal analysis & statistics
│   ├── gui/                     # User interface (7 modules)
│   ├── parsers/                 # DBC/SYM file parsing
│   ├── recorder/                # Data logging to CSV
│   └── triggers/                # Complex trigger system
│
├── config/                      # Configuration files
├── recordings/                  # Recorded data output
├── tests/                       # Unit tests
└── docs/                        # Documentation
```

**Total:** 37 files, ~2,400 lines of Python code

## 🎓 Documentation

| Document | Description |
|----------|-------------|
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Complete usage guide with examples |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, data flow, diagrams |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Solutions for common issues |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Developer guide, patterns, extensions |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Feature overview and statistics |

## 🧪 Testing

Run unit tests:
```bash
pytest tests/
```

With coverage:
```bash
pytest --cov=src tests/
```

## 🔧 Configuration

Default settings in `config/default_config.json`:
- Bitrate: 500 kbps
- Max samples: 10,000 per signal
- Update rate: 20 Hz
- Time window: 10 seconds

## 🌐 Cross-Platform

- ✅ **Windows 10/11** - Full PCAN and IXXAT support
- ✅ **Linux** - SocketCAN native support, virtual CAN for testing
- 🚫 **macOS** - Not supported (requires CAN hardware drivers)

## 📊 Performance

- **Plot Update**: 20 Hz (50ms intervals)
- **Sample Buffer**: 10,000 samples/signal (configurable)
- **Memory Usage**: ~100 MB typical
- **CAN Reception**: Real-time (hardware limited)

## 🔐 License

MIT License - Free for commercial and personal use

See [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! The codebase is modular and well-documented:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 💡 Use Cases

- **Automotive Development**: ECU testing and validation
- **Signal Analysis**: FFT, statistics, filtering
- **Bus Monitoring**: Real-time CAN traffic visualization
- **Data Logging**: Long-term recording and analysis
- **Protocol Testing**: Send/receive validation
- **Education**: Learn CAN bus communication

## 🎯 Key Advantages

- ✅ **No Cloud Required** - Runs completely offline
- ✅ **Open Source** - Modify and extend freely
- ✅ **Professional Grade** - Production-ready code
- ✅ **Well Documented** - Extensive guides and comments
- ✅ **Tested** - Unit tests included
- ✅ **Extensible** - Plugin-friendly architecture

## ⚡ Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
2. Review [USER_GUIDE.md](docs/USER_GUIDE.md) for usage questions
3. See [DEVELOPMENT.md](DEVELOPMENT.md) for architecture questions
4. Open an issue for bugs or feature requests

## 📊 Statistics

- **Files**: 37
- **Python Code**: ~2,400 lines
- **Modules**: 12 core + 7 GUI components
- **Git Commits**: 5 (clean history)
- **Documentation**: 5 comprehensive guides

---

**Ready to start?** Run the setup script and launch the application! 🚀
