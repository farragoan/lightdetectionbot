import requests
import time
import os
import subprocess
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
from config import Config

class AlertManager:
    def __init__(self):
        self.config = Config()
        self.last_alert_time = None
        self.alert_count = 0
        self.last_hour = datetime.now().hour
        
        # Setup GPIO
        self.setup_gpio()
        
    def setup_gpio(self):
        """Initialize GPIO pins for local indicators"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.config.GPIO_LED_PIN, GPIO.OUT)
            GPIO.setup(self.config.GPIO_BUZZER_PIN, GPIO.OUT)
            GPIO.output(self.config.GPIO_LED_PIN, GPIO.LOW)
            GPIO.output(self.config.GPIO_BUZZER_PIN, GPIO.LOW)
        except Exception as e:
            print(f"GPIO setup failed: {e}")
    
    def should_alert(self):
        """Check if we should send an alert based on cooldown and rate limiting"""
        now = datetime.now()
        
        # Reset counter if hour changed
        if now.hour != self.last_hour:
            self.alert_count = 0
            self.last_hour = now.hour
        
        # Check cooldown
        if self.last_alert_time:
            time_since_last = (now - self.last_alert_time).total_seconds()
            if time_since_last < self.config.ALERT_COOLDOWN:
                return False
        
        # Check rate limit
        if self.alert_count >= self.config.MAX_ALERTS_PER_HOUR:
            return False
        
        return True
    
    def trigger_alert(self, analysis_result):
        """Trigger all configured alerts"""
        if not self.should_alert():
            print("Alert suppressed due to cooldown or rate limiting")
            return False
        
        print("🚨 RED LIGHT DETECTED - TRIGGERING ALERTS! 🚨")
        
        success = True
        
        # Smart bulb alert
        if self.config.SMART_BULB_API_URL:
            success &= self.trigger_smart_bulb_alert()
        
        # Audio alert
        if self.config.AUDIO_ALERT_ENABLED:
            success &= self.trigger_audio_alert()
        
        # GPIO indicators
        success &= self.trigger_gpio_alert()
        
        # Update alert tracking
        self.last_alert_time = datetime.now()
        self.alert_count += 1
        
        return success
    
    def trigger_smart_bulb_alert(self):
        """Trigger smart bulb alert via API"""
        try:
            if not self.config.SMART_BULB_API_URL:
                return False
            
            # Example for Home Assistant API
            headers = {
                'Authorization': f'Bearer {self.config.SMART_BULB_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Turn on bulbs with red color
            data = {
                'entity_id': 'light.living_room',  # Adjust entity ID
                'state': 'on',
                'attributes': {
                    'rgb_color': [255, 0, 0],  # Red
                    'brightness': 255
                }
            }
            
            response = requests.post(
                f"{self.config.SMART_BULB_API_URL}/api/services/light/turn_on",
                headers=headers,
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                print("Smart bulb alert triggered successfully")
                return True
            else:
                print(f"Smart bulb alert failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Smart bulb alert error: {e}")
            return False
    
    def trigger_audio_alert(self):
        """Play audio alert"""
        try:
            if os.path.exists(self.config.AUDIO_ALERT_FILE):
                # Play audio file
                subprocess.run(['aplay', self.config.AUDIO_ALERT_FILE], 
                             capture_output=True, timeout=10)
                print("Audio alert played")
                return True
            else:
                # Generate beep sound using speaker-test
                subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'], 
                             capture_output=True, timeout=5)
                print("Beep alert played")
                return True
                
        except Exception as e:
            print(f"Audio alert error: {e}")
            return False
    
    def trigger_gpio_alert(self):
        """Trigger GPIO indicators"""
        try:
            # Flash LED and buzzer
            for _ in range(5):  # 5 flashes
                GPIO.output(self.config.GPIO_LED_PIN, GPIO.HIGH)
                GPIO.output(self.config.GPIO_BUZZER_PIN, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.config.GPIO_LED_PIN, GPIO.LOW)
                GPIO.output(self.config.GPIO_BUZZER_PIN, GPIO.LOW)
                time.sleep(0.5)
            
            print("GPIO alert triggered")
            return True
            
        except Exception as e:
            print(f"GPIO alert error: {e}")
            return False
    
    def clear_smart_bulbs(self):
        """Turn off smart bulbs after alert"""
        try:
            if not self.config.SMART_BULB_API_URL:
                return False
            
            headers = {
                'Authorization': f'Bearer {self.config.SMART_BULB_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'entity_id': 'light.living_room',  # Adjust entity ID
                'state': 'off'
            }
            
            response = requests.post(
                f"{self.config.SMART_BULB_API_URL}/api/services/light/turn_off",
                headers=headers,
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                print("Smart bulbs cleared")
                return True
            else:
                print(f"Failed to clear smart bulbs: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Clear smart bulbs error: {e}")
            return False
    
    def cleanup(self):
        """Clean up GPIO resources"""
        try:
            GPIO.cleanup()
        except:
            pass 