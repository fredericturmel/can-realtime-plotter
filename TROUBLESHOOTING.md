# Troubleshooting Guide

## Installation Issues

### Problem: pip install fails
**Symptoms:** Error during `pip install -r requirements.txt`

**Solutions:**
1. Update pip: `python -m pip install --upgrade pip`
2. Install Visual C++ Build Tools (Windows) if needed
3. Try installing packages individually to identify the problem:
   ```bash
   pip install PyQt5
   pip install pyqtgraph
   pip install python-can
   pip install cantools
   pip install numpy scipy pandas
   ```

### Problem: PyQt5 installation fails on Linux
**Solution:**
```bash
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtsvg
```

## Connection Issues

### Problem: Cannot detect PCAN interface
**Symptoms:** No PCAN devices shown in connection dialog

**Checklist:**
- [ ] PCAN hardware connected via USB
- [ ] PCAN-Basic driver installed
- [ ] Device shows up in Device Manager (Windows)
- [ ] Try unplugging and reconnecting the device
- [ ] Restart the application

**Windows Driver:**
- Download from: https://www.peak-system.com/PCAN-Basic.239.0.html
- Install PCAN-View to test hardware independently

### Problem: Cannot detect IXXAT interface  
**Symptoms:** No IXXAT devices shown

**Checklist:**
- [ ] IXXAT hardware connected
- [ ] IXXAT VCI driver installed
- [ ] Device recognized by Windows
- [ ] Check IXXAT hardware configuration tool

**Windows Driver:**
- Download from: https://www.ixxat.com/

### Problem: SocketCAN not working (Linux)
**Symptoms:** Interface not found or permission denied

**Solution:**
```bash
# Load kernel module
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan  # for virtual CAN

# Set up interface
sudo ip link set can0 type can bitrate 500000
sudo ip link set can0 up

# Check status
ip -details link show can0

# Add user to dialout group (may require logout)
sudo usermod -a -G dialout $USER
```

### Problem: "Permission denied" on Linux
**Solution:**
```bash
# Option 1: Run with sudo (not recommended)
sudo python main.py

# Option 2: Add user to dialout group (recommended)
sudo usermod -a -G dialout $USER
# Log out and back in

# Option 3: Set up udev rules
sudo nano /etc/udev/rules.d/99-can.rules
# Add: SUBSYSTEM=="net", KERNEL=="can*", MODE="0666"
sudo udevadm control --reload-rules
```

## Database Loading Issues

### Problem: DBC file won't load
**Symptoms:** Error message when loading DBC

**Solutions:**
1. Verify file format - open in text editor, should start with `VERSION ""`
2. Check file encoding (should be UTF-8 or ASCII)
3. Try loading in another tool (e.g., CANdb++)
4. Check for syntax errors in DBC file

### Problem: No signals appear after loading
**Symptoms:** Database loads but signal selector is empty

**Possible Causes:**
- DBC file has no messages defined
- Messages have no signals
- File format issue

**Debug:**
Check console output for parsing errors

### Problem: Signal decoding fails
**Symptoms:** Raw messages received but not decoded

**Solutions:**
1. Verify message IDs in DBC match actual CAN traffic
2. Check byte order (Intel vs Motorola)
3. Verify DLC (Data Length Code) matches
4. Use raw recording mode to inspect actual message format

## Plotting Issues

### Problem: Plot is empty or not updating
**Symptoms:** No data displayed in plots

**Checklist:**
- [ ] CAN interface connected
- [ ] DBC/SYM file loaded
- [ ] Signals selected
- [ ] CAN traffic actually present on bus
- [ ] Check status bar for connection status

**Debug:**
- Switch to "Message Sender" tab and send a test message
- Check if raw messages are being received (enable logging)

### Problem: Plot performance is poor
**Symptoms:** Slow, choppy, or laggy plotting

**Solutions:**
1. Reduce number of plotted signals
2. Decrease time window (use 5s instead of "All")
3. Increase update timer interval in main_window.py:
   ```python
   self.update_timer.start(100)  # Change from 50 to 100ms
   ```
4. Reduce max_samples in config:
   ```json
   "max_samples": 5000
   ```

### Problem: Plot scales incorrectly
**Solution:**
- Click "Auto Scale" button
- Or right-click plot and select "View All"

## Recording Issues

### Problem: Recording button disabled
**Symptoms:** Cannot start recording

**Cause:** Not connected to CAN interface

**Solution:** Connect to CAN interface first

### Problem: No file created when recording
**Symptoms:** Recording appears to start but no CSV file

**Solutions:**
1. Check `recordings/` directory permissions
2. Verify disk space available
3. Check console for error messages
4. Try specifying a different output directory

### Problem: CSV file is empty or incomplete
**Symptoms:** File created but no data or truncated

**Solutions:**
1. Ensure CAN messages are being received
2. Stop recording properly (don't force-quit)
3. Check if disk is full
4. Verify write permissions

## Message Sending Issues

### Problem: Cannot send messages
**Symptoms:** Send button does nothing or shows error

**Checklist:**
- [ ] CAN interface connected
- [ ] DBC file loaded
- [ ] Message selected
- [ ] Signal values set
- [ ] Hardware is not bus-powered only (needs termination)

### Problem: Message sent but not received by other devices
**Possible Causes:**
1. **Wrong bitrate** - Verify all devices use same bitrate
2. **Bus not terminated** - Add 120Ω resistors at both ends
3. **Wrong CAN ID** - Verify ID matches expected value
4. **Extended vs Standard ID** - Check ID format
5. **Incorrect encoding** - Verify DBC signal definitions

**Debug:**
- Use CAN bus analyzer to verify transmission
- Check if your device receives its own transmitted messages (loopback)

## Trigger Issues

### Problem: Triggers not firing
**Symptoms:** Conditions met but no trigger event

**Checklist:**
- [ ] Trigger enabled
- [ ] Correct signals selected
- [ ] Threshold values appropriate
- [ ] Logic (AND/OR) correct
- [ ] For single-shot: trigger is armed (not already fired)

**Debug:**
1. Check Statistics panel to see actual signal values
2. Simplify trigger to single condition
3. Watch trigger counter in Triggers tab

### Problem: Too many trigger events
**Solution:**
- Use single-shot mode
- Add hysteresis with multiple conditions
- Increase threshold values
- Use edge detection instead of level

## GUI Issues

### Problem: Application won't start
**Symptoms:** Error on launch or immediate crash

**Solutions:**
1. Check Python version: `python --version` (needs 3.8+)
2. Verify all dependencies installed
3. Run from terminal to see error messages:
   ```bash
   python main.py
   ```
4. Check for import errors in console output

### Problem: Dialogs not appearing
**Symptoms:** Click button but dialog doesn't show

**Solution:**
- Dialog may be behind main window - check taskbar
- Try Alt+Tab to find dialog
- Minimize other windows

### Problem: Text is too small/large
**Solution:**
Modify display scaling:
- Windows: Display Settings → Scale
- Linux: Display Settings → Scale
- Or modify font size in Qt stylesheets

## Performance Issues

### Problem: High CPU usage
**Causes & Solutions:**
1. **Too many signals plotted**
   - Reduce number of active plots
   
2. **High CAN bus traffic**
   - Increase update timer interval
   - Reduce sample buffer size

3. **Complex triggers**
   - Simplify trigger conditions
   - Disable unused triggers

### Problem: High memory usage
**Solutions:**
1. Reduce `max_samples` in configuration
2. Clear data periodically (Tools → Clear All Data)
3. Restart application for long sessions

## Common Error Messages

### "Interface not available"
- Hardware not connected
- Driver not installed
- Device in use by another program

### "Failed to load database"
- Invalid DBC/SYM file format
- File permissions issue
- File path contains special characters

### "Failed to decode message"
- Message ID not in database
- Incorrect DBC file for this CAN network
- Data length mismatch

### "Cannot write to file"
- Insufficient disk space
- Directory doesn't exist
- Permission denied

## Getting More Help

1. **Check logs**: Look in console output for detailed errors

2. **Enable debug logging**: Modify main.py:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Test with virtual CAN**:
   ```python
   # Use 'virtual' interface to test without hardware
   ```

4. **Minimal test**:
   ```python
   # Test just CAN interface
   from src.can_interface.can_manager import CANInterfaceManager
   
   manager = CANInterfaceManager()
   available = manager.get_available_interfaces()
   print(available)
   ```

5. **Verify installation**:
   ```bash
   python -c "import PyQt5; import pyqtgraph; import can; import cantools; print('All imports OK')"
   ```

## Known Issues & Workarounds

### Issue: Application freezes on exit
**Workaround:** Stop recording before closing application

### Issue: Plot legend overlaps data
**Workaround:** Resize plot or use separate plot mode

### Issue: Long signal names truncated
**Workaround:** Rename signals in DBC file or use abbreviations

## Platform-Specific Notes

### Windows
- Requires Visual C++ Runtime (usually pre-installed)
- Antivirus may need exception for CAN drivers
- UAC may require admin for driver installation

### Linux
- SocketCAN is kernel-integrated (preferred)
- Virtual CAN excellent for testing
- May need to compile python-can with interface support

## Debugging Checklist

When something doesn't work:

1. [ ] Check connection status in status bar
2. [ ] Verify hardware with vendor tools (PCAN-View, etc.)
3. [ ] Look at console output for errors
4. [ ] Try with virtual CAN interface
5. [ ] Test DBC file in another tool
6. [ ] Restart application
7. [ ] Reboot computer (Windows especially)
8. [ ] Check for USB cable/connection issues
9. [ ] Verify CAN bus termination
10. [ ] Test with minimal configuration

## Still Having Issues?

1. Run tests: `pytest tests/`
2. Check dependencies: `pip list`
3. Update python-can: `pip install --upgrade python-can`
4. Try older/newer PyQt5 version
5. Search python-can documentation
6. Check if issue is hardware-related (test with manufacturer tools)
