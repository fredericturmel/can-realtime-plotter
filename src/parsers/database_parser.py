"""
Database Parser

Handles parsing and management of DBC and SYM files.
"""

import cantools
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseParser:
    """Parses and manages CAN database files (DBC/SYM)."""
    
    def __init__(self):
        self.db: Optional[cantools.database.Database] = None
        self.file_path: Optional[Path] = None
        self.file_type: Optional[str] = None
        
    @property
    def database(self):
        """Alias for self.db for compatibility"""
        return self.db
        
    def load_database(self, file_path: str) -> bool:
        """
        Load a DBC or SYM file.
        
        Args:
            file_path: Path to the database file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            # Determine file type
            extension = file_path_obj.suffix.lower()
            
            if extension == '.dbc':
                self.db = cantools.database.load_file(file_path)
                self.file_type = 'dbc'
            elif extension == '.sym':
                try:
                    self.db = cantools.database.load_file(file_path, database_format='sym')
                    self.file_type = 'sym'
                except Exception as sym_error:
                    error_msg = str(sym_error)
                    if "Only SYM version 6.0 is supported" in error_msg:
                        logger.error(f"SYM file version not supported by cantools")
                        logger.error(f"cantools only supports SYM version 6.0")
                        logger.error(f"Please convert your SYM file to:")
                        logger.error(f"  1. DBC format (recommended) - use Vector CANdb++ or similar tools")
                        logger.error(f"  2. SYM version 6.0 - if your tool supports exporting to this version")
                        logger.error(f"  3. Use a DBC file instead")
                        return False
                    else:
                        raise sym_error
            else:
                logger.error(f"Unsupported file type: {extension}")
                return False
            
            self.file_path = file_path_obj
            logger.info(f"Loaded {self.file_type.upper()} file: {file_path}")
            logger.info(f"Found {len(self.db.messages)} messages")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load database: {str(e)}")
            return False
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages from the database.
        
        Returns:
            List of message dictionaries
        """
        if not self.db:
            return []
        
        messages = []
        for msg in self.db.messages:
            messages.append({
                'name': msg.name,
                'id': msg.frame_id,
                'dlc': msg.length,
                'signals': [sig.name for sig in msg.signals],
                'cycle_time': getattr(msg, 'cycle_time', None),
                'comment': msg.comment
            })
        
        return messages
    
    def get_message_by_id(self, msg_id: int):
        """
        Get message object by CAN ID.
        
        Args:
            msg_id: CAN message ID
            
        Returns:
            Message object or None
        """
        if not self.db:
            return None
        
        try:
            return self.db.get_message_by_frame_id(msg_id)
        except KeyError:
            return None
    
    def get_message_by_name(self, name: str):
        """
        Get message object by name.
        
        Args:
            name: Message name
            
        Returns:
            Message object or None
        """
        if not self.db:
            return None
        
        try:
            return self.db.get_message_by_name(name)
        except KeyError:
            return None
    
    def get_signals_for_message(self, msg_id: int) -> List[Dict[str, Any]]:
        """
        Get all signals for a specific message.
        
        Args:
            msg_id: CAN message ID
            
        Returns:
            List of signal dictionaries
        """
        message = self.get_message_by_id(msg_id)
        if not message:
            return []
        
        signals = []
        for sig in message.signals:
            signals.append({
                'name': sig.name,
                'start_bit': sig.start,
                'length': sig.length,
                'byte_order': sig.byte_order,
                'scale': sig.scale,
                'offset': sig.offset,
                'minimum': sig.minimum,
                'maximum': sig.maximum,
                'unit': sig.unit,
                'comment': sig.comment,
                'choices': sig.choices if hasattr(sig, 'choices') else None
            })
        
        return signals
    
    def decode_message(self, msg_id: int, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decode a CAN message using the database.
        
        Args:
            msg_id: CAN message ID
            data: Raw message data bytes
            
        Returns:
            Dictionary of signal_name -> {raw, physical, unit} or None
        """
        if not self.db:
            return None
        
        try:
            message = self.get_message_by_id(msg_id)
            if not message:
                return None
            
            # Decode to get physical values
            decoded_physical = message.decode(data)
            
            # Build result with raw, physical, and unit for each signal
            result = {}
            for signal in message.signals:
                signal_name = signal.name
                if signal_name in decoded_physical:
                    physical_value = decoded_physical[signal_name]
                    
                    # Calculate raw value (reverse scale and offset)
                    if signal.scale != 0:
                        raw_value = int((physical_value - signal.offset) / signal.scale)
                    else:
                        raw_value = physical_value
                    
                    result[signal_name] = {
                        'raw': raw_value,
                        'physical': physical_value,
                        'unit': signal.unit or ''
                    }
            
            return result if result else None
            
        except Exception as e:
            logger.debug(f"Failed to decode message {msg_id:X}: {str(e)}")
            return None
    
    def encode_message(self, msg_id: int, data: Dict[str, Any]) -> Optional[bytes]:
        """
        Encode signal values into a CAN message.
        
        Args:
            msg_id: CAN message ID
            data: Dictionary of signal names to values
            
        Returns:
            Encoded message bytes or None
        """
        if not self.db:
            return None
        
        try:
            message = self.get_message_by_id(msg_id)
            if not message:
                return None
            
            encoded = message.encode(data)
            return encoded
            
        except Exception as e:
            logger.error(f"Failed to encode message {msg_id:X}: {str(e)}")
            return None
    
    def get_all_signals(self) -> List[Dict[str, Any]]:
        """
        Get all signals from all messages.
        
        Returns:
            List of all signals with message context
        """
        if not self.db:
            return []
        
        all_signals = []
        for msg in self.db.messages:
            for sig in msg.signals:
                all_signals.append({
                    'message_name': msg.name,
                    'message_id': msg.frame_id,
                    'signal_name': sig.name,
                    'unit': sig.unit,
                    'min': sig.minimum,
                    'max': sig.maximum,
                    'scale': sig.scale,
                    'offset': sig.offset
                })
        
        return all_signals
    
    def is_loaded(self) -> bool:
        """Check if a database is currently loaded."""
        return self.db is not None
