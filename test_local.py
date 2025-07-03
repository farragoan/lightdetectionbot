#!/usr/bin/env python3

import cv2
import numpy as np
import os
import time
from datetime import datetime

# Mock classes for local testing
class MockCamera:
    """Mock camera for local testing"""
    def __init__(self, test_image_path=None):
        self.test_image_path = test_image_path or "test_images/"
        self.test_images = self._load_test_images()
        self.current_image_index = 0
    
    def _load_test_images(self):
        """Load test images from directory"""
        images = []
        if os.path.exists(self.test_image_path):
            for file in os.listdir(self.test_image_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    images.append(os.path.join(self.test_image_path, file))
        return sorted(images)
    
    def capture_array(self):
        """Mock camera capture - returns test image"""
        if not self.test_images:
            # Create a synthetic test image
            return self._create_synthetic_image()
        
        # Cycle through test images
        image_path = self.test_images[self.current_image_index]
        self.current_image_index = (self.current_image_index + 1) % len(self.test_images)
        
        image = cv2.imread(image_path)
        if image is None:
            return self._create_synthetic_image()
        
        return image
    
    def _create_synthetic_image(self):
        """Create a synthetic image for testing"""
        # Create a 1920x1080 image
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # Add some background
        image[:] = (50, 50, 50)  # Dark gray background
        
        # Add a red LED (simulating the meter LED)
        center_x, center_y = 960, 540
        cv2.circle(image, (center_x, center_y), 20, (0, 0, 255), -1)  # Red circle
        
        # Add some text
        cv2.putText(image, "MOCK METER", (center_x-100, center_y-100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        return image
    
    def close(self):
        pass

class MockGPIO:
    """Mock GPIO for local testing"""
    def __init__(self):
        self.led_state = False
        self.buzzer_state = False
    
    def setmode(self, mode):
        pass
    
    def setup(self, pin, mode):
        pass
    
    def output(self, pin, state):
        if pin == 18:  # LED pin
            self.led_state = state
            print(f"🔴 LED: {'ON' if state else 'OFF'}")
        elif pin == 23:  # Buzzer pin
            self.buzzer_state = state
            print(f"🔊 Buzzer: {'ON' if state else 'OFF'}")
    
    def cleanup(self):
        pass

# Mock the Pi-specific imports
import sys
sys.modules['picamera2'] = type('MockPicamera2', (), {})
sys.modules['RPi.GPIO'] = MockGPIO()

def test_light_detection_local():
    """Test light detection with mock camera"""
    print("🧪 Testing Light Detection System (Local)")
    print("=" * 50)
    
    # Import our modules (they'll use mock components)
    from light_detector import LightDetector
    from config import Config
    
    # Create mock camera
    mock_camera = MockCamera()
    
    # Create detector
    detector = LightDetector()
    
    print("📷 Testing with synthetic image...")
    
    # Test with synthetic image
    image = mock_camera.capture_array()
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Analyze image
    analysis = detector.analyze_image(image_rgb)
    
    print(f"🔍 Detection Results:")
    print(f"   Detected: {analysis['detected']}")
    print(f"   Confidence: {analysis['confidence']:.2f}")
    print(f"   Red Pixels: {analysis['red_pixels']}")
    print(f"   Red Ratio: {analysis['red_ratio']:.4f}")
    print(f"   Brightness: {analysis['brightness']:.1f}")
    
    # Create debug image
    debug_image = detector.create_debug_image(image_rgb, analysis)
    cv2.imwrite("local_test_result.jpg", cv2.cvtColor(debug_image, cv2.COLOR_RGB2BGR))
    print("📸 Debug image saved as 'local_test_result.jpg'")
    
    return analysis

def test_with_real_images():
    """Test with real images if available"""
    print("\n📸 Testing with real images...")
    
    test_dir = "test_images/"
    if not os.path.exists(test_dir):
        print(f"❌ No test images found in {test_dir}")
        print("   Create this directory and add some test images")
        return
    
    from light_detector import LightDetector
    detector = LightDetector()
    
    images = [f for f in os.listdir(test_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print("❌ No images found in test_images/")
        return
    
    print(f"🔍 Testing {len(images)} images...")
    
    for i, image_file in enumerate(images[:5]):  # Test first 5 images
        image_path = os.path.join(test_dir, image_file)
        image = cv2.imread(image_path)
        
        if image is not None:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            analysis = detector.analyze_image(image_rgb)
            
            print(f"   {image_file}: {'🔴 DETECTED' if analysis['detected'] else '⚪ No red light'} "
                  f"(conf: {analysis['confidence']:.2f})")
            
            # Save debug image
            debug_image = detector.create_debug_image(image_rgb, analysis)
            debug_filename = f"debug_{image_file}"
            cv2.imwrite(debug_filename, cv2.cvtColor(debug_image, cv2.COLOR_RGB2BGR))

def test_alert_system():
    """Test alert system with mock components"""
    print("\n🚨 Testing Alert System...")
    
    # Mock the GPIO import
    import sys
    sys.modules['RPi.GPIO'] = MockGPIO()
    
    from alert_manager import AlertManager
    
    alert_manager = AlertManager()
    
    # Test alert triggering
    mock_analysis = {
        'detected': True,
        'confidence': 0.8,
        'red_pixels': 1000,
        'total_pixels': 10000,
        'red_ratio': 0.1,
        'brightness': 150
    }
    
    print("🔔 Triggering mock alert...")
    success = alert_manager.trigger_alert(mock_analysis)
    print(f"   Alert result: {'✅ Success' if success else '❌ Failed'}")
    
    alert_manager.cleanup()

def main():
    """Run all local tests"""
    print("🚀 Light Detection System - Local Testing")
    print("=" * 50)
    
    # Test 1: Light detection with synthetic image
    test_light_detection_local()
    
    # Test 2: Light detection with real images (if available)
    test_with_real_images()
    
    # Test 3: Alert system
    test_alert_system()
    
    print("\n✅ Local testing complete!")
    print("\nNext steps:")
    print("1. Review test results and debug images")
    print("2. Adjust detection parameters in config.py if needed")
    print("3. Add real test images to test_images/ directory")
    print("4. Deploy to Raspberry Pi for hardware testing")

if __name__ == "__main__":
    main() 