"""
Bus Load Analyzer

Expert mode panel for analyzing CAN bus load and statistics.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
                             QPushButton, QComboBox, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import time
import logging

logger = logging.getLogger(__name__)


class BusLoadAnalyzer(QWidget):
    """Expert mode panel for bus load analysis."""
    
    def __init__(self, can_manager, parent=None):
        super().__init__(parent)
        self.can_manager = can_manager
        
        # Statistics tracking
        self.message_count = 0
        self.byte_count = 0
        self.error_count = 0
        self.last_reset_time = time.time()
        self.message_ids = {}  # id -> count
        self.recent_messages = []  # Recent message timestamps
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(1000)  # Update every second
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🔬 Expert Mode: Bus Load Analysis")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        
        # Reset button
        self.reset_btn = QPushButton("🔄 Reset Statistics")
        self.reset_btn.setMaximumWidth(180)
        self.reset_btn.clicked.connect(self.reset_statistics)
        header_layout.addWidget(self.reset_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Bus Load Group
        load_group = QGroupBox("📊 Real-Time Bus Load")
        load_layout = QVBoxLayout()
        load_layout.setContentsMargins(16, 20, 16, 16)
        load_layout.setSpacing(12)
        
        # Bus load bar
        bus_load_layout = QHBoxLayout()
        bus_load_layout.addWidget(QLabel("Bus Utilization:"))
        self.bus_load_bar = QProgressBar()
        self.bus_load_bar.setMinimum(0)
        self.bus_load_bar.setMaximum(100)
        self.bus_load_bar.setValue(0)
        self.bus_load_bar.setTextVisible(True)
        self.bus_load_bar.setFormat("%p%")
        self.bus_load_bar.setMinimumHeight(30)
        bus_load_layout.addWidget(self.bus_load_bar)
        load_layout.addLayout(bus_load_layout)
        
        # Message rate bar
        msg_rate_layout = QHBoxLayout()
        msg_rate_layout.addWidget(QLabel("Message Rate:"))
        self.msg_rate_bar = QProgressBar()
        self.msg_rate_bar.setMinimum(0)
        self.msg_rate_bar.setMaximum(1000)  # Up to 1000 msg/s
        self.msg_rate_bar.setValue(0)
        self.msg_rate_bar.setTextVisible(True)
        self.msg_rate_bar.setFormat("%v msg/s")
        self.msg_rate_bar.setMinimumHeight(30)
        msg_rate_layout.addWidget(self.msg_rate_bar)
        load_layout.addLayout(msg_rate_layout)
        
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)
        
        # Statistics Group
        stats_group = QGroupBox("📈 Traffic Statistics")
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(16, 20, 16, 16)
        stats_layout.setSpacing(12)
        
        # Stats grid
        stats_grid_1 = QHBoxLayout()
        stats_grid_1.setSpacing(30)
        
        self.total_msg_label = QLabel("📨 Total Messages: 0")
        self.total_msg_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        stats_grid_1.addWidget(self.total_msg_label)
        
        self.total_bytes_label = QLabel("💾 Total Bytes: 0")
        self.total_bytes_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        stats_grid_1.addWidget(self.total_bytes_label)
        
        self.avg_rate_label = QLabel("⚡ Avg Rate: 0 msg/s")
        self.avg_rate_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        stats_grid_1.addWidget(self.avg_rate_label)
        
        stats_grid_1.addStretch()
        stats_layout.addLayout(stats_grid_1)
        
        stats_grid_2 = QHBoxLayout()
        stats_grid_2.setSpacing(30)
        
        self.unique_ids_label = QLabel("🆔 Unique IDs: 0")
        self.unique_ids_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        stats_grid_2.addWidget(self.unique_ids_label)
        
        self.bandwidth_label = QLabel("📶 Bandwidth: 0 kbps")
        self.bandwidth_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        stats_grid_2.addWidget(self.bandwidth_label)
        
        self.uptime_label = QLabel("⏱️ Uptime: 00:00:00")
        self.uptime_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        stats_grid_2.addWidget(self.uptime_label)
        
        stats_grid_2.addStretch()
        stats_layout.addLayout(stats_grid_2)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Top Messages Group
        top_msg_group = QGroupBox("🏆 Top Message IDs by Frequency")
        top_msg_layout = QVBoxLayout()
        top_msg_layout.setContentsMargins(16, 20, 16, 16)
        
        self.top_msg_table = QTableWidget()
        self.top_msg_table.setColumnCount(4)
        self.top_msg_table.setHorizontalHeaderLabels(['CAN ID', 'Count', 'Percentage', 'Rate (msg/s)'])
        self.top_msg_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.top_msg_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.top_msg_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.top_msg_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.top_msg_table.setAlternatingRowColors(True)
        self.top_msg_table.setMaximumHeight(300)
        top_msg_layout.addWidget(self.top_msg_table)
        
        top_msg_group.setLayout(top_msg_layout)
        layout.addWidget(top_msg_group)
        
        layout.addStretch()
    
    def record_message(self, msg):
        """Record a received message for statistics."""
        self.message_count += 1
        self.byte_count += len(msg.data)
        
        # Track message ID
        msg_id = msg.arbitration_id
        self.message_ids[msg_id] = self.message_ids.get(msg_id, 0) + 1
        
        # Track recent messages for rate calculation
        current_time = time.time()
        self.recent_messages.append(current_time)
        
        # Keep only messages from last 2 seconds
        cutoff_time = current_time - 2.0
        self.recent_messages = [t for t in self.recent_messages if t > cutoff_time]
    
    def update_statistics(self):
        """Update all statistics displays."""
        current_time = time.time()
        elapsed_time = current_time - self.last_reset_time
        
        if elapsed_time == 0:
            return
        
        # Calculate rates
        avg_msg_rate = self.message_count / elapsed_time if elapsed_time > 0 else 0
        instant_msg_rate = len(self.recent_messages) / 2.0  # Messages in last 2 seconds / 2
        
        # Calculate bandwidth (assume 8 data bytes + 6 overhead bytes per message, 1 start bit + 8 data bits + 1 stop bit per byte)
        # Simplified: ~14 bytes per message * 10 bits/byte = 140 bits per message
        bits_per_msg = 140
        bandwidth_bps = instant_msg_rate * bits_per_msg
        bandwidth_kbps = bandwidth_bps / 1000.0
        
        # Calculate bus load (for 500 kbps CAN)
        bitrate = 500000  # 500 kbps
        if self.can_manager.is_connected and hasattr(self.can_manager, 'bitrate'):
            bitrate = self.can_manager.bitrate
        
        bus_load_percent = min(100, (bandwidth_bps / bitrate) * 100) if bitrate > 0 else 0
        
        # Update labels
        self.total_msg_label.setText(f"📨 Total Messages: {self.message_count:,}")
        self.total_bytes_label.setText(f"💾 Total Bytes: {self.byte_count:,}")
        self.avg_rate_label.setText(f"⚡ Avg Rate: {avg_msg_rate:.1f} msg/s")
        self.unique_ids_label.setText(f"🆔 Unique IDs: {len(self.message_ids)}")
        self.bandwidth_label.setText(f"📶 Bandwidth: {bandwidth_kbps:.2f} kbps")
        
        # Update uptime
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        self.uptime_label.setText(f"⏱️ Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update progress bars
        self.bus_load_bar.setValue(int(bus_load_percent))
        self.msg_rate_bar.setValue(int(instant_msg_rate))
        
        # Color code bus load bar
        if bus_load_percent < 50:
            self.bus_load_bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; }")
        elif bus_load_percent < 80:
            self.bus_load_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff9800; }")
        else:
            self.bus_load_bar.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")
        
        # Update top messages table
        self.update_top_messages_table()
    
    def update_top_messages_table(self):
        """Update the top messages table."""
        # Sort by count
        sorted_messages = sorted(self.message_ids.items(), key=lambda x: x[1], reverse=True)
        
        # Show top 10
        top_messages = sorted_messages[:10]
        
        self.top_msg_table.setRowCount(len(top_messages))
        
        total_count = self.message_count if self.message_count > 0 else 1
        elapsed_time = time.time() - self.last_reset_time
        
        for row, (msg_id, count) in enumerate(top_messages):
            # CAN ID
            id_item = QTableWidgetItem(f"0x{msg_id:03X}")
            id_item.setTextAlignment(Qt.AlignCenter)
            self.top_msg_table.setItem(row, 0, id_item)
            
            # Count
            count_item = QTableWidgetItem(f"{count:,}")
            count_item.setTextAlignment(Qt.AlignCenter)
            self.top_msg_table.setItem(row, 1, count_item)
            
            # Percentage
            percentage = (count / total_count) * 100
            pct_item = QTableWidgetItem(f"{percentage:.1f}%")
            pct_item.setTextAlignment(Qt.AlignCenter)
            self.top_msg_table.setItem(row, 2, pct_item)
            
            # Rate
            rate = count / elapsed_time if elapsed_time > 0 else 0
            rate_item = QTableWidgetItem(f"{rate:.1f}")
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.top_msg_table.setItem(row, 3, rate_item)
    
    def reset_statistics(self):
        """Reset all statistics."""
        self.message_count = 0
        self.byte_count = 0
        self.error_count = 0
        self.last_reset_time = time.time()
        self.message_ids.clear()
        self.recent_messages.clear()
        
        # Reset displays
        self.bus_load_bar.setValue(0)
        self.msg_rate_bar.setValue(0)
        self.top_msg_table.setRowCount(0)
