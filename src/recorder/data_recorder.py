"""
Data Recorder

Records CAN messages and decoded signals to CSV files.
"""

import csv
import can
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from PyQt5.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)


class DataRecorder(QObject):
    """Records CAN data to CSV files."""
    
    # Signals
    recording_started = pyqtSignal(str)  # file_path
    recording_stopped = pyqtSignal(int)  # message_count
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.file_path: Optional[Path] = None
        self.csv_file = None
        self.csv_writer = None
        self.message_count = 0
        self.recording_mode = 'raw'  # 'raw' or 'decoded'
        self.selected_signals: List[str] = []
        
    def start_recording(self, output_dir: str = 'recordings', 
                       filename: Optional[str] = None,
                       mode: str = 'raw',
                       selected_signals: Optional[List[str]] = None) -> bool:
        """
        Start recording CAN data.
        
        Args:
            output_dir: Directory to save recordings
            filename: Custom filename (None for auto-generated)
            mode: 'raw' for raw CAN messages, 'decoded' for decoded signals
            selected_signals: List of signal names to record (for decoded mode)
            
        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            self.error_occurred.emit("Recording already in progress")
            return False
        
        try:
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"can_recording_{timestamp}.csv"
            
            self.file_path = output_path / filename
            self.recording_mode = mode
            self.selected_signals = selected_signals or []
            
            # Open CSV file
            self.csv_file = open(self.file_path, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            
            # Write header based on mode
            if mode == 'raw':
                self.csv_writer.writerow([
                    'Timestamp', 'ID', 'ID_Hex', 'DLC', 'Data', 'Extended', 'Error'
                ])
            else:  # decoded mode
                header = ['Timestamp', 'Message_ID', 'Message_Name']
                header.extend(self.selected_signals)
                self.csv_writer.writerow(header)
            
            self.message_count = 0
            self.is_recording = True
            
            logger.info(f"Started recording to {self.file_path}")
            self.recording_started.emit(str(self.file_path))
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to start recording: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def stop_recording(self):
        """Stop recording and close the file."""
        if not self.is_recording:
            return
        
        try:
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
                self.csv_writer = None
            
            self.is_recording = False
            
            logger.info(f"Stopped recording. Total messages: {self.message_count}")
            self.recording_stopped.emit(self.message_count)
            
        except Exception as e:
            error_msg = f"Error stopping recording: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
    
    def record_raw_message(self, msg: can.Message, timestamp: Optional[float] = None):
        """
        Record a raw CAN message.
        
        Args:
            msg: CAN message to record
            timestamp: Custom timestamp (uses msg.timestamp if None)
        """
        if not self.is_recording or self.recording_mode != 'raw':
            return
        
        try:
            ts = timestamp if timestamp is not None else msg.timestamp
            data_hex = msg.data.hex().upper()
            
            self.csv_writer.writerow([
                ts,
                msg.arbitration_id,
                f"0x{msg.arbitration_id:X}",
                msg.dlc,
                data_hex,
                msg.is_extended_id,
                msg.is_error_frame
            ])
            
            self.message_count += 1
            
        except Exception as e:
            logger.error(f"Error recording message: {str(e)}")
    
    def record_decoded_message(self, timestamp: float, msg_id: int, 
                               msg_name: str, signals: Dict[str, float]):
        """
        Record decoded signal values.
        
        Args:
            timestamp: Message timestamp
            msg_id: CAN message ID
            msg_name: Message name
            signals: Dictionary of signal names to values
        """
        if not self.is_recording or self.recording_mode != 'decoded':
            return
        
        try:
            row = [timestamp, msg_id, msg_name]
            
            # Add signal values in the order specified
            for signal_name in self.selected_signals:
                value = signals.get(signal_name, '')
                row.append(value)
            
            self.csv_writer.writerow(row)
            self.message_count += 1
            
        except Exception as e:
            logger.error(f"Error recording decoded message: {str(e)}")
    
    def get_status(self) -> Dict:
        """
        Get current recording status.
        
        Returns:
            Dictionary with recording status information
        """
        return {
            'is_recording': self.is_recording,
            'file_path': str(self.file_path) if self.file_path else None,
            'message_count': self.message_count,
            'mode': self.recording_mode
        }
