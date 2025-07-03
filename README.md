# Light Detection System for Raspberry Pi

A smart light detection system that monitors your electricity meter for red LED indicators and triggers alerts when expensive backup power is being used.

## Features

- **Automatic Detection**: Monitors electricity meter LED every 15 seconds
- **Smart Alerts**: Multiple alert methods (smart bulbs, audio, GPIO indicators)
- **Image Storage**: Saves detection images with timestamps
- **Rate Limiting**: Prevents alert spam with configurable cooldowns
- **Auto-start**: Runs automatically on system boot
- **Logging**: Comprehensive logging for monitoring and debugging

## Hardware Requirements

- Raspberry Pi Zero 2 W (or any Pi with camera support)
- Pi Camera Module (v1.3 or v2.1)
- Optional: LED and buzzer for local indicators
- Optional: Smart bulbs for remote alerts

## Installation

### 1. Flash Raspberry Pi OS Bookworm
- Download and flash Raspberry Pi OS Bookworm to your SD card
- Enable SSH during first boot setup

### 2. Connect to Pi and Clone Repository
```bash
ssh pi@your-pi-ip
cd /home/pi
git clone https://github.com/yourusername/lightdetectionbot.git
cd lightdetectionbot
```

### 3. Run Setup Script
```bash
chmod +x setup.py
python3 setup.py
```

### 4. Configure Camera Position
1. Mount your camera in front of the electricity meter
2. Run camera test to adjust crop settings:
```bash
python3 test_camera.py
```
3. Adjust crop region in `config.py` to focus on the LED area

### 5. Test Light Detection
```bash
python3 test_camera.py detect
```

### 6. Enable Auto-start
```bash
sudo cp light-detector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable light-detector
sudo systemctl start light-detector
```

## Configuration

Edit `config.py` to customize settings:

### Camera Settings
```python
CAMERA_RESOLUTION = (1920, 1080)  # Image resolution
DETECTION_INTERVAL = 15  # Seconds between checks
```

### Detection Settings
```python
RED_LIGHT_THRESHOLD = 0.3  # Sensitivity (0-1)
CROP_LEFT = 0.4   # Crop region percentages
CROP_TOP = 0.3
CROP_RIGHT = 0.6
CROP_BOTTOM = 0.7
```

### Alert Settings
```python
ALERT_COOLDOWN = 300  # 5 minutes between alerts
MAX_ALERTS_PER_HOUR = 12  # Prevent spam
```

## Smart Bulb Integration

### Home Assistant
1. Create a long-lived access token in Home Assistant
2. Add to `.env` file:
```
SMART_BULB_API_URL=http://your-ha-ip:8123
SMART_BULB_API_KEY=your_long_lived_token
```

### Alexa/Other Systems
Modify `alert_manager.py` to integrate with your smart home system.

## Usage

### Manual Start
```bash
python3 main.py
```

### Check Status
```bash
sudo systemctl status light-detector
```

### View Logs
```bash
tail -f /home/pi/lightdetectionbot/light_detector.log
```

### Stop Service
```bash
sudo systemctl stop light-detector
```

## Troubleshooting

### Camera Not Working
1. Check camera connection
2. Enable camera in raspi-config
3. Reboot Pi

### False Positives/Negatives
1. Adjust `RED_LIGHT_THRESHOLD` in config.py
2. Fine-tune crop region settings
3. Check lighting conditions

### Alerts Not Working
1. Check network connectivity
2. Verify smart bulb API credentials
3. Test GPIO connections

### Performance Issues
1. Reduce camera resolution
2. Increase detection interval
3. Check Pi temperature and cooling

## File Structure

```
lightdetectionbot/
├── main.py              # Main application
├── config.py            # Configuration settings
├── camera_manager.py    # Camera operations
├── light_detector.py    # Light detection logic
├── alert_manager.py     # Alert handling
├── test_camera.py       # Camera testing utility
├── setup.py             # Installation script
├── requirements.txt     # Python dependencies
├── light-detector.service # Systemd service
├── images/              # Captured images
└── logs/                # Log files
```

## Development

### Adding New Alert Methods
1. Extend `AlertManager` class
2. Add configuration options
3. Update documentation

### Improving Detection
1. Modify `LightDetector` class
2. Adjust HSV color ranges
3. Add machine learning models

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in `/home/pi/lightdetectionbot/light_detector.log`
3. Open an issue on GitHub 