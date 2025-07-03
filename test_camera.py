#!/usr/bin/env python3

import cv2
import numpy as np
import time
import subprocess
import threading
import os
from config import Config

def start_streaming_server():
    """Start rpicam-vid streaming server"""
    try:
        # Kill any existing rpicam processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        
        # Start rpicam-vid with H.264 streaming
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
        
        print("Starting rpicam-vid streaming server...")
        print(f"Stream available at: tcp/h264://<pi-ip>:8888")
        print(f"Your Pi IP: 192.168.29.91")
        print("Use VLC: vlc tcp/h264://192.168.29.91:8888")
        print("Or Chrome: http://192.168.29.91:8888")
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process
        
    except Exception as e:
        print(f"Failed to start streaming server: {e}")
        return None

def test_camera_with_stream():
    """Test camera with streaming capability"""
    config = Config()
    
    print("Testing camera with streaming...")
    print(f"Resolution: {config.CAMERA_RESOLUTION}")
    print(f"Crop region: {config.CROP_LEFT:.1%} to {config.CROP_RIGHT:.1%} width, {config.CROP_TOP:.1%} to {config.CROP_BOTTOM:.1%} height")
    
    # Start streaming server in background
    stream_process = start_streaming_server()
    
    if not stream_process:
        print("Failed to start streaming. Trying fallback method...")
        test_camera_fallback()
        return
    
    try:
        print("\nStreaming server started!")
        print("Press 'q' to quit, 's' to save image, 'r' to restart stream")
        
        while True:
            key = input().strip().lower()
            
            if key == 'q':
                break
            elif key == 's':
                # Save current frame using rpicam-still
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"test_capture_{timestamp}.jpg"
                subprocess.run([
                    'rpicam-still',
                    '--width', '1280',
                    '--height', '720',
                    '--output', filename
                ])
                print(f"Saved: {filename}")
            elif key == 'r':
                # Restart stream
                if stream_process:
                    stream_process.terminate()
                    stream_process.wait()
                stream_process = start_streaming_server()
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if stream_process:
            stream_process.terminate()
            stream_process.wait()
        print("Streaming stopped")

def test_camera_fallback():
    """Fallback camera test using OpenCV"""
    print("Using fallback camera test...")
    
    try:
        # Try to open camera with OpenCV
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Could not open camera with OpenCV")
            return
        
        print("Camera opened with OpenCV. Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            cv2.imshow('Camera Test (Fallback)', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Fallback camera test failed: {e}")

def test_light_detection():
    """Test light detection on a saved image"""
    from light_detector import LightDetector
    
    print("Testing light detection...")
    
    detector = LightDetector()
    
    # Test with a saved image
    test_image = "test_capture_20231201_120000.jpg"  # Adjust filename
    
    try:
        image = cv2.imread(test_image)
        if image is not None:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            analysis = detector.analyze_image(image_rgb)
            
            print(f"Detection result: {analysis}")
            
            # Create debug image
            debug_image = detector.create_debug_image(image_rgb, analysis)
            cv2.imwrite("debug_result.jpg", cv2.cvtColor(debug_image, cv2.COLOR_RGB2BGR))
            print("Debug image saved as debug_result.jpg")
        else:
            print(f"Could not load image: {test_image}")
            
    except Exception as e:
        print(f"Light detection test failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "detect":
            test_light_detection()
        elif sys.argv[1] == "stream":
            test_camera_with_stream()
        elif sys.argv[1] == "fallback":
            test_camera_fallback()
        else:
            print("Usage: python3 test_camera.py [detect|stream|fallback]")
    else:
        test_camera_with_stream() 