# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CAN Real-Time Plotter                        │
│                            Main Window (GUI)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │  Control Panel │       │   Tab Widget   │
        │  - Connect     │       │  - Plot View   │
        │  - Load DB     │       │  - Sender      │
        │  - Select Sig  │       │  - Triggers    │
        │  - Record      │       └───────┬────────┘
        └────────────────┘               │
                                         │
    ┌────────────────────────────────────┼────────────────────────┐
    │                                    │                        │
┌───▼────────────┐          ┌───────────▼──────────┐   ┌─────────▼─────────┐
│  Plot Widget   │          │  Message Sender      │   │  Trigger Config   │
│  - Real-time   │          │  - Signal values     │   │  - Add conditions │
│  - Multi-mode  │          │  - Periodic send     │   │  - AND/OR logic   │
│  - Autoscale   │          │  - Single shot       │   │  - Enable/disable │
└────────────────┘          └──────────────────────┘   └───────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                          Core Components                             │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│ CANInterfaceManager│◄────►│ DatabaseParser   │◄────►│ SignalProcessor │
│  - Connect/disco │       │  - Load DBC/SYM  │       │  - Statistics   │
│  - Send/receive  │       │  - Decode/encode │       │  - FFT          │
│  - PCAN/IXXAT    │       │  - Get signals   │       │  - Filtering    │
└────────┬─────────┘       └──────────────────┘       └─────────────────┘
         │
         │ CAN Messages
         │
    ┌────▼────────────┐                    ┌─────────────────┐
    │  Data Recorder  │                    │ TriggerManager  │
    │  - CSV output   │                    │  - Evaluate     │
    │  - Raw/decoded  │                    │  - Actions      │
    │  - Timestamps   │                    │  - Enable/dis   │
    └─────────────────┘                    └─────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                          Data Flow                                   │
└─────────────────────────────────────────────────────────────────────┘

    Hardware         Interface         Parser          Processor
    ┌──────┐         ┌──────┐         ┌──────┐        ┌──────┐
    │ PCAN │────────►│ CAN  │────────►│ DBC  │───────►│Signal│
    │IXXAT │  USB    │Manager│ raw msg│Parser│ decode │Proc. │
    └──────┘         └──┬───┘         └──────┘        └───┬──┘
                        │                                  │
                        │                                  │
                    ┌───▼────┐                        ┌───▼────┐
                    │Recorder│                        │ Plots  │
                    │  CSV   │                        │  GUI   │
                    └────────┘                        └────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                       Signal Flow Examples                           │
└─────────────────────────────────────────────────────────────────────┘

1. Receiving & Plotting:
   Hardware → CANManager → DatabaseParser → SignalProcessor → PlotWidget
                    ↓                               ↓
              DataRecorder                  StatisticsPanel
                    ↓
              TriggerManager

2. Sending Messages:
   MessageSender → DatabaseParser → CANManager → Hardware
                     (encode)         (send)

3. Trigger Activation:
   SignalProcessor → TriggerManager → Action (start/stop record, alert)
      (values)         (evaluate)


┌─────────────────────────────────────────────────────────────────────┐
│                      Module Dependencies                             │
└─────────────────────────────────────────────────────────────────────┘

main.py
  └─► MainWindow (gui/main_window.py)
       ├─► CANInterfaceManager (can_interface/can_manager.py)
       │    └─► python-can library
       │
       ├─► DatabaseParser (parsers/database_parser.py)
       │    └─► cantools library
       │
       ├─► SignalProcessor (data_processing/signal_processor.py)
       │    └─► numpy, scipy
       │
       ├─► DataRecorder (recorder/data_recorder.py)
       │    └─► csv, datetime
       │
       ├─► TriggerManager (triggers/trigger_system.py)
       │    └─► Trigger, TriggerCondition classes
       │
       └─► GUI Widgets
            ├─► ConnectionDialog
            ├─► SignalSelector
            ├─► PlotWidget (pyqtgraph)
            ├─► MessageSenderWidget
            ├─► StatisticsPanel
            └─► TriggerConfigWidget


┌─────────────────────────────────────────────────────────────────────┐
│                    Communication Pattern (Qt Signals)                │
└─────────────────────────────────────────────────────────────────────┘

CANInterfaceManager:
  Signals:
    - message_received(can.Message) ──► MainWindow.on_message_received()
    - connection_status_changed()   ──► MainWindow.update_status()
    - error_occurred()              ──► MainWindow.show_error()

DataRecorder:
  Signals:
    - recording_started(str)        ──► MainWindow.update_ui()
    - recording_stopped(int)        ──► MainWindow.show_stats()

TriggerManager:
  Signals:
    - trigger_fired(str, dict)      ──► MainWindow.on_trigger_fired()
                                     ──► Actions (start/stop recording)


┌─────────────────────────────────────────────────────────────────────┐
│                         File Formats                                 │
└─────────────────────────────────────────────────────────────────────┘

Input:
  - DBC files: CAN database (standard format)
  - SYM files: PEAK PCAN symbol files
  
Output:
  - CSV (Raw mode):
      Timestamp, ID, ID_Hex, DLC, Data, Extended, Error
      1.234567, 256, 0x100, 8, 0102030405060708, False, False
      
  - CSV (Decoded mode):
      Timestamp, Message_ID, Message_Name, Signal1, Signal2, ...
      1.234567, 256, EngineData, 2500, 85.5, ...


┌─────────────────────────────────────────────────────────────────────┐
│                    Performance Characteristics                       │
└─────────────────────────────────────────────────────────────────────┘

- CAN Reception:      Real-time (handled by python-can threads)
- Plot Update Rate:   20 Hz (50ms timer)
- Max Samples/Signal: 10,000 (configurable)
- Memory Usage:       ~100MB typical (depends on # of signals)
- GUI Responsiveness: Non-blocking (Qt event loop)
- Recording Speed:    Limited only by disk I/O
```
