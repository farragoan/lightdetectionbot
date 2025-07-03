#!/usr/bin/env python3

import subprocess
import time
import signal
import sys

def signal_handler(sig, frame):
    print('\nStopping stream...')
    subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
    sys.exit(0)

def start_camera_stream():
    """Start camera streaming with rpicam-vid"""
    
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Raspberry Pi Camera Stream...")
    print("=" * 50)
    print("Stream will be available at:")
    print("VLC: vlc tcp/h264://192.168.29.91:8888")
    print("Chrome: http://192.168.29.91:8888")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Kill any existing rpicam processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        time.sleep(1)
        
        # Start rpicam-vid streaming
        cmd = [
            'rpicam-vid',
            '--width', '1280',
            '--height', '720',
            '--framerate', '30',
            '--codec', 'h264',
            '--inline',  # Enable inline headers
            '--listen',  # Enable TCP listening
            '--port', '8888',
            '--output', '-',  # Output to stdout
            '--timeout', '0'  # Run indefinitely
        ]
        
        print("Starting rpicam-vid...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Stream started successfully!")
        print("Waiting for connections...")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping stream...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        print("Stream stopped")

if __name__ == "__main__":
    start_camera_stream() 