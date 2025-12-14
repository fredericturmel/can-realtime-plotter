#!/bin/bash
# Quick start script for Linux

echo "CAN Real-Time Plotter - Quick Start"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "For SocketCAN on Linux, you may need to set up your CAN interface:"
echo "  sudo ip link set can0 type can bitrate 500000"
echo "  sudo ip link set can0 up"
echo ""
