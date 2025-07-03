import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Camera settings
    CAMERA_RESOLUTION = (1920, 1080)  # Full HD
    CAMERA_FPS = 30
    CAMERA_ROTATION = 0  # Adjust if camera is mounted differently
    
    # Detection settings
    DETECTION_INTERVAL = 15  # seconds between checks
    RED_LIGHT_THRESHOLD = 0.3  # Minimum red intensity to trigger alert (0-1)
    RED_HUE_MIN = 0  # Red hue range for detection
    RED_HUE_MAX = 20  # or 160-180 for red
    RED_SATURATION_MIN = 100  # Minimum saturation
    RED_VALUE_MIN = 100  # Minimum brightness
    
    # Alert settings
    ALERT_COOLDOWN = 300  # 5 minutes between alerts
    MAX_ALERTS_PER_HOUR = 12  # Prevent spam
    
    # Smart bulb settings (Alexa/Home Assistant)
    SMART_BULB_API_URL = os.getenv('SMART_BULB_API_URL', '')
    SMART_BULB_API_KEY = os.getenv('SMART_BULB_API_KEY', '')
    
    # Audio alert settings
    AUDIO_ALERT_ENABLED = True
    AUDIO_ALERT_FILE = '/home/pi/lightdetectionbot/alert.wav'
    
    # GPIO settings for local indicators
    GPIO_LED_PIN = 18  # Physical pin 12
    GPIO_BUZZER_PIN = 23  # Physical pin 16
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/home/pi/lightdetectionbot/light_detector.log'
    
    # Image storage
    IMAGE_DIR = '/home/pi/lightdetectionbot/images'
    MAX_IMAGES = 100  # Keep last 100 images
    
    # Detection region (crop image to focus on LED area)
    # These are percentages of the image dimensions
    CROP_LEFT = 0.4   # 40% from left
    CROP_TOP = 0.3    # 30% from top
    CROP_RIGHT = 0.6  # 60% from left
    CROP_BOTTOM = 0.7 # 70% from top

    # ROI for rpicam-vid/rpicam-still (left, top, width, height)
    # Example: --roi 0.64,0.50,0.05,0.05
    CAMERA_ROI = (0.64, 0.50, 0.05, 0.05) 