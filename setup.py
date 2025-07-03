#!/usr/bin/env python3

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("Setting up Light Detection System for Raspberry Pi...")
    
    # Update system
    if not run_command("sudo apt update", "Updating package list"):
        return False
    
    if not run_command("sudo apt upgrade -y", "Upgrading system packages"):
        return False
    
    # Install system dependencies
    system_packages = [
        "python3-pip",
        "python3-opencv",
        "python3-numpy",
        "python3-pil",
        "python3-requests",
        "python3-gpiozero",
        "libatlas-base-dev",  # For numpy
        "libhdf5-dev",
        "libhdf5-serial-dev",
        "libharfbuzz0b",
        "libwebp6",
        "libtiff5",
        "libjasper1",
        "libilmbase23",
        "libopenexr23",
        "libgstreamer1.0-0",
        "libavcodec58",
        "libavformat58",
        "libswscale5",
        "libv4l-0",
        "libxvidcore4",
        "libx264-163",
        "libgtk-3-0",
        "libatlas-base-dev",
        "libblas-dev",
        "liblapack-dev",
        "libhdf5-dev",
        "libhdf5-serial-dev",
        "libharfbuzz0b",
        "libwebp6",
        "libtiff5",
        "libjasper1",
        "libilmbase23",
        "libopenexr23",
        "libgstreamer1.0-0",
        "libavcodec58",
        "libavformat58",
        "libswscale5",
        "libv4l-0",
        "libxvidcore4",
        "libx264-163",
        "libgtk-3-0"
    ]
    
    for package in system_packages:
        if not run_command(f"sudo apt install -y {package}", f"Installing {package}"):
            return False
    
    # Install Python dependencies
    if not run_command("pip3 install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Enable camera interface
    if not run_command("sudo raspi-config nonint do_camera 0", "Enabling camera interface"):
        return False
    
    # Enable I2C for potential future sensors
    if not run_command("sudo raspi-config nonint do_i2c 0", "Enabling I2C"):
        return False
    
    # Create necessary directories
    directories = [
        "/home/pi/lightdetectionbot/images",
        "/home/pi/lightdetectionbot/logs"
    ]
    
    for directory in directories:
        if not run_command(f"mkdir -p {directory}", f"Creating directory {directory}"):
            return False
    
    # Set permissions
    if not run_command("chmod +x main.py", "Making main.py executable"):
        return False
    
    print("\n✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Configure your camera position and adjust crop settings in config.py")
    print("2. Test the system with: python3 main.py")
    print("3. Set up auto-start with: sudo systemctl enable light-detector")
    
    return True

if __name__ == "__main__":
    if not main():
        sys.exit(1) 