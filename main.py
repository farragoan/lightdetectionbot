#!/usr/bin/env python3

import time
import logging
import signal
import sys
from datetime import datetime
from camera_manager import CameraManager
from light_detector import LightDetector
from alert_manager import AlertManager
from config import Config

class LightDetectionSystem:
    def __init__(self):
        self.config = Config()
        self.setup_logging()
        
        self.camera = None
        self.detector = None
        self.alert_manager = None
        
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize(self):
        """Initialize all components"""
        try:
            self.logger.info("Initializing Light Detection System...")
            
            # Initialize camera
            self.camera = CameraManager()
            self.logger.info("Camera initialized")
            
            # Initialize detector
            self.detector = LightDetector()
            self.logger.info("Light detector initialized")
            
            # Initialize alert manager
            self.alert_manager = AlertManager()
            self.logger.info("Alert manager initialized")
            
            self.logger.info("System initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def run_detection_cycle(self):
        """Run one complete detection cycle"""
        try:
            # Capture image
            self.logger.debug("Capturing image...")
            image = self.camera.capture_image(save_image=True)
            
            if image is None:
                self.logger.error("Failed to capture image")
                return
            
            # Analyze image
            self.logger.debug("Analyzing image...")
            analysis = self.detector.analyze_image(image)
            
            # Log results
            self.logger.info(f"Detection result: {analysis['detected']}, "
                           f"Confidence: {analysis['confidence']:.2f}, "
                           f"Red pixels: {analysis['red_pixels']}")
            
            # Trigger alert if red light detected
            if analysis['detected']:
                self.logger.warning("RED LIGHT DETECTED!")
                self.alert_manager.trigger_alert(analysis)
            else:
                self.logger.debug("No red light detected")
            
        except Exception as e:
            self.logger.error(f"Error in detection cycle: {e}")
    
    def run(self):
        """Main run loop"""
        if not self.initialize():
            self.logger.error("Failed to initialize system")
            return
        
        self.running = True
        self.logger.info("Starting light detection system...")
        self.logger.info(f"Detection interval: {self.config.DETECTION_INTERVAL} seconds")
        
        try:
            while self.running:
                start_time = time.time()
                
                # Run detection cycle
                self.run_detection_cycle()
                
                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.DETECTION_INTERVAL - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up...")
        
        if self.camera:
            self.camera.close()
        
        if self.alert_manager:
            self.alert_manager.cleanup()
        
        self.logger.info("Cleanup complete")

def main():
    """Main entry point"""
    # Security check for secrets
    from config import Config
    missing = Config.check_secrets()
    if missing:
        print("[ERROR] Required secrets are missing. Please set them in your .env file before running.")
        exit(1)
    system = LightDetectionSystem()
    system.run()

if __name__ == "__main__":
    main() 