import cv2
import numpy as np
import time
import os
from datetime import datetime
from config import Config

class CameraManager:
    def __init__(self):
        self.config = Config()
        self.picam2 = None
        self.setup_camera()
        
    def setup_camera(self):
        """Initialize the Pi Camera"""
        try:
            # Try to import picamera2
            try:
                from picamera2 import Picamera2
                self.picam2 = Picamera2()
                camera_config = self.picam2.create_still_configuration(
                    main={"size": self.config.CAMERA_RESOLUTION},
                    controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
                )
                self.picam2.configure(camera_config)
                self.picam2.start()
                time.sleep(2)  # Allow camera to warm up
                print("Camera initialized successfully with picamera2")
            except ImportError:
                print("picamera2 not available - this is expected on non-Pi systems")
                self.picam2 = None
            except Exception as e:
                print(f"Failed to initialize picamera2: {e}")
                self.picam2 = None
                
        except Exception as e:
            print(f"Failed to initialize camera: {e}")
            self.picam2 = None
    
    def capture_image(self, save_image=True):
        """Capture an image and optionally save it"""
        try:
            if self.picam2 is None:
                # Create a mock image for testing
                return self._create_mock_image()
            
            # Capture image
            image = self.picam2.capture_array()
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Crop to detection region
            cropped_image = self._crop_to_detection_region(image_rgb)
            
            if save_image:
                self._save_image(cropped_image)
            
            return cropped_image
            
        except Exception as e:
            print(f"Error capturing image: {e}")
            return self._create_mock_image()
    
    def _create_mock_image(self):
        """Create a mock image for testing when camera is not available"""
        # Create a 1920x1080 image
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Add some background
        image[:] = (50, 50, 50)  # Dark gray background
        
        # Add a red LED (simulating the meter LED)
        center_x, center_y = 960, 540
        cv2.circle(image, (center_x, center_y), 20, (0, 0, 255), -1)  # Red circle
        
        # Add some text
        cv2.putText(image, "MOCK CAMERA", (center_x-100, center_y-100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        return image
    
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
        if self.picam2:
            self.picam2.close() 