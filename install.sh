#!/bin/bash

echo "🚀 Installing Light Detection System for Raspberry Pi..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
sudo apt install -y python3-pip python3-opencv python3-numpy python3-pil python3-requests python3-gpiozero

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt

# Enable camera
echo "📷 Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Create directories
echo "📁 Creating directories..."
mkdir -p /home/pi/lightdetectionbot/images
mkdir -p /home/pi/lightdetectionbot/logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x main.py
chmod +x test_camera.py

# Install service
echo "⚙️ Installing systemd service..."
sudo cp light-detector.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Position your camera in front of the electricity meter"
echo "2. Test camera: python3 test_camera.py"
echo "3. Adjust crop settings in config.py if needed"
echo "4. Test detection: python3 test_camera.py detect"
echo "5. Enable auto-start: sudo systemctl enable light-detector"
echo "6. Start service: sudo systemctl start light-detector"
echo ""
echo "Check status: sudo systemctl status light-detector"
echo "View logs: tail -f /home/pi/lightdetectionbot/light_detector.log" 