"""
Signal Processor

Performs statistical analysis and signal processing operations.
"""

import numpy as np
from scipy import signal as scipy_signal
from collections import deque
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SignalProcessor:
    """Processes CAN signal data for analysis and visualization."""
    
    def __init__(self, max_samples: int = 10000):
        """
        Initialize the signal processor.
        
        Args:
            max_samples: Maximum number of samples to keep in memory per signal
        """
        self.max_samples = max_samples
        self.signal_data: Dict[str, deque] = {}
        self.timestamps: Dict[str, deque] = {}
        
    def add_sample(self, signal_name: str, value: float, timestamp: float):
        """
        Add a new sample for a signal.
        
        Args:
            signal_name: Name of the signal
            value: Signal value
            timestamp: Timestamp in seconds
        """
        if signal_name not in self.signal_data:
            self.signal_data[signal_name] = deque(maxlen=self.max_samples)
            self.timestamps[signal_name] = deque(maxlen=self.max_samples)
        
        self.signal_data[signal_name].append(value)
        self.timestamps[signal_name].append(timestamp)
    
    def get_data(self, signal_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get signal data as numpy arrays.
        
        Args:
            signal_name: Name of the signal
            
        Returns:
            Tuple of (timestamps, values) as numpy arrays
        """
        if signal_name not in self.signal_data:
            return np.array([]), np.array([])
        
        times = np.array(self.timestamps[signal_name])
        values = np.array(self.signal_data[signal_name])
        
        return times, values
    
    def get_statistics(self, signal_name: str, window_size: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate statistical measures for a signal.
        
        Args:
            signal_name: Name of the signal
            window_size: Number of recent samples to analyze (None for all)
            
        Returns:
            Dictionary with statistics (mean, min, max, std, rms)
        """
        if signal_name not in self.signal_data or len(self.signal_data[signal_name]) == 0:
            return {
                'mean': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std': 0.0,
                'rms': 0.0,
                'samples': 0
            }
        
        data = np.array(self.signal_data[signal_name])
        
        if window_size and window_size < len(data):
            data = data[-window_size:]
        
        stats = {
            'mean': float(np.mean(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'std': float(np.std(data)),
            'rms': float(np.sqrt(np.mean(data**2))),
            'samples': len(data)
        }
        
        return stats
    
    def calculate_fft(self, signal_name: str, sampling_rate: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate FFT (Fast Fourier Transform) of a signal.
        
        Args:
            signal_name: Name of the signal
            sampling_rate: Sampling rate in Hz (estimated from timestamps if None)
            
        Returns:
            Tuple of (frequencies, magnitudes)
        """
        if signal_name not in self.signal_data or len(self.signal_data[signal_name]) < 2:
            return np.array([]), np.array([])
        
        times = np.array(self.timestamps[signal_name])
        values = np.array(self.signal_data[signal_name])
        
        # Estimate sampling rate if not provided
        if sampling_rate is None and len(times) > 1:
            time_diffs = np.diff(times)
            avg_time_diff = np.mean(time_diffs)
            sampling_rate = 1.0 / avg_time_diff if avg_time_diff > 0 else 1.0
        elif sampling_rate is None:
            sampling_rate = 1.0
        
        # Calculate FFT
        n = len(values)
        fft_values = np.fft.rfft(values)
        fft_freq = np.fft.rfftfreq(n, d=1.0/sampling_rate)
        
        # Calculate magnitude
        magnitude = np.abs(fft_values)
        
        return fft_freq, magnitude
    
    def apply_filter(self, signal_name: str, filter_type: str = 'lowpass', 
                    cutoff: float = 10.0, order: int = 4) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply a digital filter to a signal.
        
        Args:
            signal_name: Name of the signal
            filter_type: 'lowpass', 'highpass', 'bandpass', 'bandstop'
            cutoff: Cutoff frequency in Hz (or tuple for bandpass/bandstop)
            order: Filter order
            
        Returns:
            Tuple of (timestamps, filtered_values)
        """
        times, values = self.get_data(signal_name)
        
        if len(values) < order * 3:
            return times, values
        
        # Estimate sampling rate
        if len(times) > 1:
            time_diffs = np.diff(times)
            avg_time_diff = np.mean(time_diffs)
            sampling_rate = 1.0 / avg_time_diff if avg_time_diff > 0 else 1.0
        else:
            return times, values
        
        # Design filter
        nyquist = sampling_rate / 2.0
        normalized_cutoff = cutoff / nyquist
        
        try:
            b, a = scipy_signal.butter(order, normalized_cutoff, btype=filter_type)
            filtered = scipy_signal.filtfilt(b, a, values)
            return times, filtered
        except Exception as e:
            logger.error(f"Filter error: {str(e)}")
            return times, values
    
    def calculate_moving_average(self, signal_name: str, window_size: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate moving average of a signal.
        
        Args:
            signal_name: Name of the signal
            window_size: Number of samples in moving window
            
        Returns:
            Tuple of (timestamps, averaged_values)
        """
        times, values = self.get_data(signal_name)
        
        if len(values) < window_size:
            return times, values
        
        # Calculate moving average using convolution
        weights = np.ones(window_size) / window_size
        averaged = np.convolve(values, weights, mode='same')
        
        return times, averaged
    
    def clear_signal(self, signal_name: str):
        """Clear all data for a specific signal."""
        if signal_name in self.signal_data:
            self.signal_data[signal_name].clear()
            self.timestamps[signal_name].clear()
    
    def clear_all(self):
        """Clear all signal data."""
        self.signal_data.clear()
        self.timestamps.clear()
    
    def get_signal_names(self) -> List[str]:
        """Get list of all signal names."""
        return list(self.signal_data.keys())
    
    def get_sample_count(self, signal_name: str) -> int:
        """Get number of samples for a signal."""
        if signal_name not in self.signal_data:
            return 0
        return len(self.signal_data[signal_name])
