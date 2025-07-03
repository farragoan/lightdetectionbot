# Test Images Directory

Add your test images here to validate the light detection system locally.

## Supported Formats
- `.jpg` / `.jpeg`
- `.png`

## Recommended Test Images
1. **Meter with red LED ON** - To test positive detection
2. **Meter with red LED OFF** - To test negative detection
3. **Meter in different lighting conditions** - To test robustness
4. **Meter from different angles** - To test crop region accuracy

## Image Naming Convention
- `red_led_on.jpg` - Red LED is lit
- `red_led_off.jpg` - Red LED is off
- `test_1.jpg`, `test_2.jpg` - General test images

## How to Use
1. Add your test images to this directory
2. Run `python3 test_local.py` to test detection
3. Review debug images in the root directory
4. Adjust detection parameters in `config.py` if needed 