# Testing Strategy Guide

## 🧪 **Complete Testing Strategy**

### **Phase 1: Local Development Testing**
- ✅ **Core Logic Validation** - Test detection algorithms locally
- ✅ **Mock Components** - Simulate Pi camera and GPIO
- ✅ **Image Processing** - Validate OpenCV operations
- ✅ **Alert System** - Test notification logic

### **Phase 2: Pi Hardware Testing**
- 🔧 **Camera Integration** - Real Pi Camera testing
- 🔧 **GPIO Validation** - Physical LED/buzzer testing
- 🔧 **Performance Testing** - Resource usage optimization
- 🔧 **Real-world Validation** - Actual meter testing

---

## 🖥️ **Phase 1: Local Testing**

### **Step 1: Install Local Dependencies**
```bash
# Install local requirements (no Pi-specific packages)
pip install -r requirements_local.txt
```

### **Step 2: Run Local Tests**
```bash
# Test with synthetic images
python3 test_local.py
```

**What this tests:**
- ✅ Light detection algorithm
- ✅ Image processing pipeline
- ✅ Alert system logic
- ✅ Configuration loading

### **Step 3: Add Real Test Images**
1. **Create `test_images/` directory**
2. **Add photos of your electricity meter:**
   - `red_led_on.jpg` - When red LED is lit
   - `red_led_off.jpg` - When red LED is off
   - `different_lighting.jpg` - Various conditions

### **Step 4: Validate Detection**
```bash
# Test with your real images
python3 test_local.py
```

**Review results:**
- Check `local_test_result.jpg` for synthetic test
- Check `debug_*.jpg` files for real image tests
- Adjust `RED_LIGHT_THRESHOLD` in `config.py` if needed

---

## 🍓 **Phase 2: Pi Hardware Testing**

### **Step 1: SSH Setup**
```bash
# Connect to your Pi
ssh pi@your-pi-ip

# Clone or transfer the code
cd /home/pi
git clone <your-repo> lightdetectionbot
cd lightdetectionbot
```

### **Step 2: Install Pi Dependencies**
```bash
# Run installation script
chmod +x install.sh
./install.sh
```

### **Step 3: Test Camera**
```bash
# Test camera functionality
python3 test_camera.py
```

**What to check:**
- ✅ Camera initializes without errors
- ✅ Live preview shows (if using X11 forwarding)
- ✅ Images can be captured and saved
- ✅ Crop region is correctly positioned

### **Step 4: Test Light Detection**
```bash
# Test detection on Pi
python3 test_camera.py detect
```

**What to check:**
- ✅ Detection algorithm works with real camera
- ✅ Debug images are generated
- ✅ Detection sensitivity is appropriate

### **Step 5: Test Full System**
```bash
# Run the complete system
python3 main.py
```

**Monitor for:**
- ✅ System starts without errors
- ✅ Images are captured every 15 seconds
- ✅ Detection results are logged
- ✅ Alerts trigger when red light detected

---

## 🔧 **Testing Commands Reference**

### **Local Testing**
```bash
# Basic local test
python3 test_local.py

# Test specific components
python3 -c "from light_detector import LightDetector; print('✅ Light detector works')"
python3 -c "from alert_manager import AlertManager; print('✅ Alert manager works')"
```

### **Pi Testing**
```bash
# Camera test
python3 test_camera.py

# Detection test
python3 test_camera.py detect

# Full system test
python3 main.py

# Service test
sudo systemctl start light-detector
sudo systemctl status light-detector
tail -f /home/pi/lightdetectionbot/light_detector.log
```

### **Debugging**
```bash
# View logs
tail -f /home/pi/lightdetectionbot/light_detector.log

# Check system status
sudo systemctl status light-detector

# Manual camera test
python3 -c "from camera_manager import CameraManager; c = CameraManager(); print('Camera OK')"
```

---

## 🎯 **Testing Checklist**

### **Local Testing ✅**
- [ ] `pip install -r requirements_local.txt` succeeds
- [ ] `python3 test_local.py` runs without errors
- [ ] Synthetic image detection works
- [ ] Real image detection works (if images provided)
- [ ] Alert system logic works
- [ ] Debug images are generated

### **Pi Hardware Testing 🔧**
- [ ] Camera module is connected and recognized
- [ ] `python3 test_camera.py` shows live preview
- [ ] Images can be captured and saved
- [ ] Crop region focuses on LED area
- [ ] Light detection works with real camera
- [ ] GPIO indicators work (LED/buzzer)
- [ ] Full system runs continuously
- [ ] Alerts trigger appropriately
- [ ] Service starts on boot

### **Real-world Validation 🔧**
- [ ] System detects red LED when lit
- [ ] System doesn't trigger false positives
- [ ] Alerts reach intended recipients
- [ ] System runs stable for 24+ hours
- [ ] Image storage doesn't fill up disk
- [ ] Performance is acceptable

---

## 🚨 **Troubleshooting**

### **Local Testing Issues**
```bash
# Import errors
pip install opencv-python numpy pillow

# Mock issues
python3 -c "import sys; print('Python path:', sys.path)"
```

### **Pi Testing Issues**
```bash
# Camera not working
sudo raspi-config  # Enable camera
sudo reboot

# Permission issues
sudo chown -R pi:pi /home/pi/lightdetectionbot

# Service issues
sudo systemctl daemon-reload
sudo systemctl restart light-detector
```

### **Detection Issues**
- **Too many false positives**: Increase `RED_LIGHT_THRESHOLD`
- **Missed detections**: Decrease `RED_LIGHT_THRESHOLD`
- **Poor crop region**: Adjust `CROP_*` settings in `config.py`

---

## 📊 **Performance Monitoring**

### **Resource Usage**
```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h /home/pi/lightdetectionbot

# Monitor camera temperature
vcgencmd measure_temp
```

### **Log Analysis**
```bash
# View recent detections
grep "DETECTED" /home/pi/lightdetectionbot/light_detector.log

# View errors
grep "ERROR" /home/pi/lightdetectionbot/light_detector.log

# View system stats
grep "Detection result" /home/pi/lightdetectionbot/light_detector.log
```

---

## 🎯 **Success Criteria**

The system is ready for production when:

1. ✅ **Local tests pass** - Core logic works
2. ✅ **Pi tests pass** - Hardware integration works
3. ✅ **Detection accuracy** - 95%+ true positive rate
4. ✅ **False positive rate** - <5% false alarms
5. ✅ **System stability** - Runs 24/7 without crashes
6. ✅ **Alert reliability** - Alerts reach users consistently
7. ✅ **Performance** - Uses <50% CPU, <200MB RAM
8. ✅ **Storage** - Images don't fill disk (>1GB free)

---

## 🚀 **Next Steps After Testing**

1. **Deploy to production** - Enable auto-start
2. **Monitor for 1 week** - Watch for issues
3. **Fine-tune parameters** - Adjust based on real usage
4. **Add features** - Web interface, mobile alerts, etc.
5. **Scale up** - Add more meters or locations 