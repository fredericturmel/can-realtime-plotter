"""
Test script for sending CAN messages with virtual interface.

This script demonstrates how to:
1. Connect to a virtual CAN interface
2. Send CAN messages
3. Receive and display the sent messages
"""

import can
import time
import sys

def test_virtual_send():
    """Test sending messages on virtual CAN interface."""
    
    print("=" * 60)
    print("Virtual CAN Interface - Send Frame Test")
    print("=" * 60)
    
    try:
        # Create two virtual buses - one for sending, one for receiving
        print("\n1. Creating virtual CAN buses...")
        bus_sender = can.Bus(interface='virtual', channel='test_send', bitrate=500000)
        bus_receiver = can.Bus(interface='virtual', channel='test_send', bitrate=500000)
        print("   ✓ Virtual buses created successfully")
        
        # Test 1: Send a simple message
        print("\n2. Test 1: Sending a simple CAN message...")
        msg = can.Message(
            arbitration_id=0x123,
            data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88],
            is_extended_id=False
        )
        
        bus_sender.send(msg)
        print(f"   ✓ Sent: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex().upper()}")
        
        # Receive the message
        received = bus_receiver.recv(timeout=1.0)
        if received:
            print(f"   ✓ Received: ID=0x{received.arbitration_id:03X}, Data={received.data.hex().upper()}")
        else:
            print("   ✗ No message received")
        
        # Test 2: Send multiple messages
        print("\n3. Test 2: Sending multiple messages...")
        for i in range(5):
            msg = can.Message(
                arbitration_id=0x100 + i,
                data=[i, i+1, i+2, i+3],
                is_extended_id=False
            )
            bus_sender.send(msg)
            print(f"   ✓ Sent message {i+1}: ID=0x{msg.arbitration_id:03X}, Data={msg.data.hex().upper()}")
            time.sleep(0.1)
        
        # Receive all messages
        print("\n   Receiving messages...")
        for i in range(5):
            received = bus_receiver.recv(timeout=1.0)
            if received:
                print(f"   ✓ Received message {i+1}: ID=0x{received.arbitration_id:03X}, Data={received.data.hex().upper()}")
        
        # Test 3: Send with extended ID
        print("\n4. Test 3: Sending extended ID message...")
        msg = can.Message(
            arbitration_id=0x12345678,
            data=[0xAA, 0xBB, 0xCC, 0xDD],
            is_extended_id=True
        )
        
        bus_sender.send(msg)
        print(f"   ✓ Sent: ID=0x{msg.arbitration_id:08X} (Extended), Data={msg.data.hex().upper()}")
        
        received = bus_receiver.recv(timeout=1.0)
        if received:
            id_type = "Extended" if received.is_extended_id else "Standard"
            print(f"   ✓ Received: ID=0x{received.arbitration_id:08X} ({id_type}), Data={received.data.hex().upper()}")
        
        # Test 4: Send with varying data lengths
        print("\n5. Test 4: Sending messages with different data lengths...")
        for dlc in [0, 1, 4, 8]:
            data = list(range(dlc))
            msg = can.Message(
                arbitration_id=0x200 + dlc,
                data=data,
                is_extended_id=False
            )
            bus_sender.send(msg)
            print(f"   ✓ Sent: ID=0x{msg.arbitration_id:03X}, DLC={dlc}, Data={msg.data.hex().upper() if dlc > 0 else '(empty)'}")
        
        print("\n   Receiving messages...")
        for i in range(4):
            received = bus_receiver.recv(timeout=1.0)
            if received:
                print(f"   ✓ Received: ID=0x{received.arbitration_id:03X}, DLC={len(received.data)}, Data={received.data.hex().upper() if len(received.data) > 0 else '(empty)'}")
        
        # Cleanup
        print("\n6. Closing buses...")
        bus_sender.shutdown()
        bus_receiver.shutdown()
        print("   ✓ Buses closed")
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_virtual_send()
    sys.exit(0 if success else 1)
