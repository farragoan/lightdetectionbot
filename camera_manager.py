import cv2
import numpy as np
import time
import os
import subprocess
from datetime import datetime
from config import Config

class CameraManager:
    def __init__(self):
        self.config = Config()
        self.stream_process = None
        self.setup_camera()
        
    def setup_camera(self):
        """Initialize the Pi Camera using rpicam"""
        try:
            # Test if rpicam is available
            result = subprocess.run(['rpicam-still', '--help'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("rpicam-still not found. Please install rpicam-apps.")
            
            print("Camera initialized successfully with rpicam")
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            raise
    
    def capture_image(self, save_image=True):
        """Capture an image using rpicam-still with ROI"""
        try:
            # Create temporary filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"/tmp/capture_{timestamp}.jpg"
            
            # ROI from config
            roi = self.config.CAMERA_ROI
            roi_str = f"{roi[0]},{roi[1]},{roi[2]},{roi[3]}"
            
            # Capture image using rpicam-still with ROI
            cmd = [
                'rpicam-still',
                '--width', str(self.config.CAMERA_RESOLUTION[0]),
                '--height', str(self.config.CAMERA_RESOLUTION[1]),
                '--roi', roi_str,
                '--output', temp_filename,
                '--timeout', '1000',  # 1 second timeout
                '--nopreview'  # No preview window
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Failed to capture image: {result.stderr}")
                return None
            
            # Read the captured image
            image = cv2.imread(temp_filename)
            if image is None:
                print("Failed to read captured image")
                return None
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # No need to crop in Python, already cropped by camera
            if save_image:
                self._save_image(image_rgb)
            
            # Clean up temporary file
            os.remove(temp_filename)
            
            return image_rgb
            
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None
    
    def start_streaming(self, port=8888):
        """Start video streaming using rpicam-vid with ROI"""
        try:
            # Kill any existing rpicam processes
            subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
            time.sleep(1)
            
            roi = self.config.CAMERA_ROI
            roi_str = f"{roi[0]},{roi[1]},{roi[2]},{roi[3]}"
            
            # Start rpicam-vid streaming with ROI
            cmd = [
                'rpicam-vid',
                '--width', '1280',
                '--height', '720',
                '--framerate', '30',
                '--codec', 'h264',
                '--inline',
                '--roi', roi_str,
                '--listen',
                '--port', str(port),
                '--output', '-',
                '--timeout', '0'
            ]
            
            self.stream_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Streaming started on port {port}")
            print(f"Access with: vlc tcp/h264://192.168.29.91:{port}")
            return True
            
        except Exception as e:
            print(f"Failed to start streaming: {e}")
            return False
    
    def stop_streaming(self):
        """Stop video streaming"""
        if self.stream_process:
            self.stream_process.terminate()
            self.stream_process.wait()
            self.stream_process = None
            print("Streaming stopped")
    
    def _crop_to_detection_region(self, image):
        """Crop image to focus on the LED area"""
        height, width = image.shape[:2]
        
        left = int(width * self.config.CROP_LEFT)
        top = int(height * self.config.CROP_TOP)
        right = int(width * self.config.CROP_RIGHT)
        bottom = int(height * self.config.CROP_BOTTOM)
        
        return image[top:bottom, left:right]
    
    def _save_image(self, image):
        """Save image with timestamp"""
        if not os.path.exists(self.config.IMAGE_DIR):
            os.makedirs(self.config.IMAGE_DIR)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.IMAGE_DIR}/capture_{timestamp}.jpg"
        
        # Convert RGB to BGR for saving
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, image_bgr)
        
        # Clean up old images
        self._cleanup_old_images()
    
    def _cleanup_old_images(self):
        """Keep only the most recent images"""
        if not os.path.exists(self.config.IMAGE_DIR):
            return
        
        files = [f for f in os.listdir(self.config.IMAGE_DIR) if f.endswith('.jpg')]
        files.sort(reverse=True)  # Newest first
        
        # Remove excess files
        for file in files[self.config.MAX_IMAGES:]:
            os.remove(os.path.join(self.config.IMAGE_DIR, file))
    
    def close(self):
        """Clean up camera resources"""
        self.stop_streaming() 