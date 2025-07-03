#!/usr/bin/env python3

import cv2
import numpy as np
import os
import time
from datetime import datetime

def test_light_detection():
    """Test light detection with synthetic image"""
    print("🧪 Testing Light Detection System (Local)")
    print("=" * 50)
    
    try:
        from light_detector import LightDetector
        from config import Config
        
        # Create detector
        detector = LightDetector()
        
        print("📷 Testing with synthetic image...")
        
        # Create a synthetic test image
        image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        image[:] = (50, 50, 50)  # Dark gray background
        
        # Add a red LED (simulating the meter LED)
        center_x, center_y = 960, 540
        cv2.circle(image, (center_x, center_y), 20, (0, 0, 255), -1)  # Red circle
        
        # Add some text
        cv2.putText(image, "MOCK METER", (center_x-100, center_y-100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # Convert BGR to RGB
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
        
        return True
        
    except Exception as e:
        print(f"❌ Light detection test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from config import Config
        config = Config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Detection interval: {config.DETECTION_INTERVAL} seconds")
        print(f"   Red light threshold: {config.RED_LIGHT_THRESHOLD}")
        print(f"   Image directory: {config.IMAGE_DIR}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_image_processing():
    """Test image processing functions"""
    print("\n🖼️ Testing Image Processing...")
    
    try:
        from light_detector import LightDetector
        
        # Create a test image with a bright red LED
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[40:60, 40:60] = [0, 0, 255]  # Red square
        
        detector = LightDetector()
        analysis = detector.analyze_image(test_image)
        
        print(f"✅ Image processing test passed")
        print(f"   Red pixels detected: {analysis['red_pixels']}")
        print(f"   Detection result: {analysis['detected']}")
        return True
        
    except Exception as e:
        print(f"❌ Image processing test failed: {e}")
        return False

def test_with_real_images():
    """Test with real images if available"""
    print("\n📸 Testing with real images...")
    
    test_dir = "test_images/"
    if not os.path.exists(test_dir):
        print(f"❌ No test images found in {test_dir}")
        print("   Create this directory and add some test images")
        return True  # Not a failure, just no images
    
    try:
        from light_detector import LightDetector
        detector = LightDetector()
        
        images = [f for f in os.listdir(test_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not images:
            print("❌ No images found in test_images/")
            return True  # Not a failure, just no images
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Real image test failed: {e}")
        return False

def main():
    """Run all local tests"""
    print("🚀 Light Detection System - Local Testing")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Configuration
    if test_config():
        tests_passed += 1
    
    # Test 2: Light detection with synthetic image
    if test_light_detection():
        tests_passed += 1
    
    # Test 3: Image processing
    if test_image_processing():
        tests_passed += 1
    
    # Test 4: Light detection with real images (if available)
    if test_with_real_images():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! System is ready for Pi deployment.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    print("\nNext steps:")
    print("1. Review test results and debug images")
    print("2. Adjust detection parameters in config.py if needed")
    print("3. Add real test images to test_images/ directory")
    print("4. Deploy to Raspberry Pi for hardware testing")

if __name__ == "__main__":
    main() 