#!/usr/bin/env python3

import subprocess
import time
import signal
import sys
import os

def signal_handler(sig, frame):
    print('\nStopping stream...')
    subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
    subprocess.run(['pkill', '-f', 'python3.*stream_camera'], capture_output=True)
    sys.exit(0)

def start_camera_stream():
    """Start camera streaming with rpicam-vid using web server approach"""
    
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Raspberry Pi Camera Stream...")
    print("=" * 50)
    print("Stream will be available at:")
    print("Web browser: http://192.168.29.91:8080")
    print("VLC: vlc http://192.168.29.91:8080/stream.m3u8")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Kill any existing rpicam processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        time.sleep(1)
        
        # Create a simple web server directory
        os.makedirs('/tmp/stream', exist_ok=True)
        
        # Start rpicam-vid with HLS streaming
        cmd = [
            'rpicam-vid',
            '--width', '1280',
            '--height', '720',
            '--framerate', '30',
            '--codec', 'h264',
            '--inline',
            '--output', '/tmp/stream/stream.m3u8',
            '--timeout', '0'
        ]
        
        print("Starting rpicam-vid with HLS streaming...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start a simple HTTP server to serve the stream
        http_cmd = ['python3', '-m', 'http.server', '8080', '--directory', '/tmp/stream']
        print("Starting HTTP server on port 8080...")
        http_process = subprocess.Popen(http_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Stream started successfully!")
        print("Access via web browser: http://192.168.29.91:8080")
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
        subprocess.run(['pkill', '-f', 'python3.*http.server'], capture_output=True)
        print("Stream stopped")

def start_simple_stream():
    """Start a simple MJPEG stream that works with Wayland"""
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting simple MJPEG stream...")
    print("=" * 50)
    print("Stream will be available at:")
    print("Web browser: http://192.168.29.91:8080")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        time.sleep(1)
        
        # Start rpicam-vid with MJPEG streaming
        cmd = [
            'rpicam-vid',
            '--width', '1280',
            '--height', '720',
            '--framerate', '30',
            '--codec', 'mjpeg',
            '--inline',
            '--listen',
            '--port', '8080',
            '--output', '-',
            '--timeout', '0'
        ]
        
        print("Starting rpicam-vid with MJPEG streaming...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Stream started successfully!")
        print("Access via web browser: http://192.168.29.91:8080")
        print("Waiting for connections...")
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping stream...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        print("Stream stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mjpeg":
        start_simple_stream()
    else:
        start_camera_stream() 