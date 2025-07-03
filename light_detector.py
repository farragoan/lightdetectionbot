import cv2
import numpy as np
from config import Config

class LightDetector:
    def __init__(self):
        self.config = Config()
        
    def detect_red_light(self, image):
        """
        Detect red light in the image
        Returns: (detected: bool, confidence: float, red_pixels: int)
        """
        try:
            # Convert RGB to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Define red color ranges (red wraps around 0/180 in HSV)
            lower_red1 = np.array([0, self.config.RED_SATURATION_MIN, self.config.RED_VALUE_MIN])
            upper_red1 = np.array([self.config.RED_HUE_MAX, 255, 255])
            
            lower_red2 = np.array([160, self.config.RED_SATURATION_MIN, self.config.RED_VALUE_MIN])
            upper_red2 = np.array([180, 255, 255])
            
            # Create masks for red detection
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = mask1 + mask2
            
            # Count red pixels
            red_pixels = cv2.countNonZero(red_mask)
            total_pixels = image.shape[0] * image.shape[1]
            red_ratio = red_pixels / total_pixels
            
            # Check if red light is detected
            detected = red_ratio > self.config.RED_LIGHT_THRESHOLD
            
            # Calculate confidence based on red pixel density
            confidence = min(red_ratio * 10, 1.0)  # Scale up for better confidence
            
            return detected, confidence, red_pixels
            
        except Exception as e:
            print(f"Error in light detection: {e}")
            return False, 0.0, 0
    
    def analyze_image(self, image):
        """
        Comprehensive image analysis
        Returns: dict with detection results and metadata
        """
        detected, confidence, red_pixels = self.detect_red_light(image)
        
        # Calculate additional metrics
        total_pixels = image.shape[0] * image.shape[1]
        red_ratio = red_pixels / total_pixels
        
        # Get image statistics
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        brightness = np.mean(gray)
        
        return {
            'detected': detected,
            'confidence': confidence,
            'red_pixels': red_pixels,
            'total_pixels': total_pixels,
            'red_ratio': red_ratio,
            'brightness': brightness,
            'image_shape': image.shape
        }
    
    def create_debug_image(self, image, analysis_result):
        """
        Create a debug image showing detection results
        """
        debug_image = image.copy()
        
        # Draw detection box
        height, width = image.shape[:2]
        cv2.rectangle(debug_image, (0, 0), (width, height), (0, 255, 0) if analysis_result['detected'] else (0, 0, 255), 3)
        
        # Add text overlay
        text = f"Red Light: {'DETECTED' if analysis_result['detected'] else 'NOT DETECTED'}"
        cv2.putText(debug_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        text2 = f"Confidence: {analysis_result['confidence']:.2f}"
        cv2.putText(debug_image, text2, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        text3 = f"Red Pixels: {analysis_result['red_pixels']}"
        cv2.putText(debug_image, text3, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return debug_image 