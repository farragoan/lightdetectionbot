#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, send_file
import os
import json
from datetime import datetime
import cv2
import numpy as np
from config import Config

app = Flask(__name__)
config = Config()

# Create templates directory and HTML template
os.makedirs('templates', exist_ok=True)

# Create HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Light Detection System</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .status { padding: 15px; border-radius: 5px; margin: 10px 0; }
        .status.online { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.offline { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .card { background: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; }
        .latest-image { text-align: center; }
        .latest-image img { max-width: 100%; height: auto; border-radius: 5px; }
        .log { background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0056b3; }
        .button.danger { background: #dc3545; }
        .button.danger:hover { background: #c82333; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .stat-label { color: #6c757d; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔴 Light Detection System</h1>
            <p>Monitoring electricity meter for red LED indicators</p>
        </div>
        
        <div class="status" id="systemStatus">
            <strong>System Status:</strong> <span id="statusText">Checking...</span>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="detectionCount">-</div>
                <div class="stat-label">Total Detections</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="lastDetection">-</div>
                <div class="stat-label">Last Detection</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uptime">-</div>
                <div class="stat-label">Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="imageCount">-</div>
                <div class="stat-label">Images Stored</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Latest Image</h3>
                <div class="latest-image" id="latestImage">
                    <p>No images available</p>
                </div>
            </div>
            
            <div class="card">
                <h3>System Controls</h3>
                <button class="button" onclick="captureImage()">📸 Capture Image</button>
                <button class="button" onclick="testDetection()">🔍 Test Detection</button>
                <button class="button danger" onclick="restartSystem()">🔄 Restart System</button>
                <button class="button" onclick="clearLogs()">🗑️ Clear Logs</button>
            </div>
        </div>
        
        <div class="card">
            <h3>Recent Logs</h3>
            <div class="log" id="logContent">
                Loading logs...
            </div>
        </div>
    </div>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('statusText').textContent = data.status;
                    document.getElementById('systemStatus').className = 'status ' + (data.status === 'Online' ? 'online' : 'offline');
                    document.getElementById('detectionCount').textContent = data.detection_count;
                    document.getElementById('lastDetection').textContent = data.last_detection;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('imageCount').textContent = data.image_count;
                });
        }
        
        function updateLatestImage() {
            fetch('/api/latest-image')
                .then(response => response.json())
                .then(data => {
                    if (data.image_url) {
                        document.getElementById('latestImage').innerHTML = 
                            `<img src="${data.image_url}" alt="Latest capture" />`;
                    }
                });
        }
        
        function updateLogs() {
            fetch('/api/logs')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('logContent').innerHTML = data.logs;
                });
        }
        
        function captureImage() {
            fetch('/api/capture', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateLatestImage();
                        updateStatus();
                    }
                });
        }
        
        function testDetection() {
            fetch('/api/test-detection', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert('Detection test completed: ' + (data.detected ? 'RED LIGHT DETECTED' : 'No red light'));
                });
        }
        
        function restartSystem() {
            if (confirm('Are you sure you want to restart the system?')) {
                fetch('/api/restart', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        alert('System restart initiated');
                    });
            }
        }
        
        function clearLogs() {
            if (confirm('Are you sure you want to clear logs?')) {
                fetch('/api/clear-logs', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        updateLogs();
                    });
            }
        }
        
        // Update every 5 seconds
        setInterval(() => {
            updateStatus();
            updateLogs();
        }, 5000);
        
        // Update image every 30 seconds
        setInterval(updateLatestImage, 30000);
        
        // Initial load
        updateStatus();
        updateLatestImage();
        updateLogs();
    </script>
</body>
</html>
"""

# Write template to file
with open('templates/index.html', 'w') as f:
    f.write(html_template)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Get system status"""
    try:
        # Check if system is running
        system_running = os.path.exists('/tmp/light_detector.pid')
        
        # Get detection count from logs
        detection_count = 0
        last_detection = "Never"
        if os.path.exists(config.LOG_FILE):
            with open(config.LOG_FILE, 'r') as f:
                lines = f.readlines()
                detection_count = len([l for l in lines if "DETECTED" in l])
                for line in reversed(lines):
                    if "DETECTED" in line:
                        last_detection = line.split(' - ')[0]
                        break
        
        # Get image count
        image_count = 0
        if os.path.exists(config.IMAGE_DIR):
            image_count = len([f for f in os.listdir(config.IMAGE_DIR) if f.endswith('.jpg')])
        
        # Calculate uptime (simplified)
        uptime = "Unknown"
        if os.path.exists('/proc/uptime'):
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                uptime = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
        
        return jsonify({
            'status': 'Online' if system_running else 'Offline',
            'detection_count': detection_count,
            'last_detection': last_detection,
            'uptime': uptime,
            'image_count': image_count
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/latest-image')
def api_latest_image():
    """Get latest captured image"""
    try:
        if os.path.exists(config.IMAGE_DIR):
            images = [f for f in os.listdir(config.IMAGE_DIR) if f.endswith('.jpg')]
            if images:
                latest = sorted(images)[-1]
                return jsonify({'image_url': f'/images/{latest}'})
        return jsonify({'image_url': None})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve captured images"""
    return send_file(os.path.join(config.IMAGE_DIR, filename))

@app.route('/api/logs')
def api_logs():
    """Get recent logs"""
    try:
        if os.path.exists(config.LOG_FILE):
            with open(config.LOG_FILE, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-50:]  # Last 50 lines
                return jsonify({'logs': ''.join(recent_lines)})
        return jsonify({'logs': 'No logs available'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/capture', methods=['POST'])
def api_capture():
    """Capture a new image"""
    try:
        from camera_manager import CameraManager
        camera = CameraManager()
        image = camera.capture_image(save_image=True)
        camera.close()
        
        if image is not None:
            return jsonify({'success': True, 'message': 'Image captured'})
        else:
            return jsonify({'success': False, 'message': 'Failed to capture image'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-detection', methods=['POST'])
def api_test_detection():
    """Test light detection on latest image"""
    try:
        from light_detector import LightDetector
        
        # Get latest image
        if os.path.exists(config.IMAGE_DIR):
            images = [f for f in os.listdir(config.IMAGE_DIR) if f.endswith('.jpg')]
            if images:
                latest = sorted(images)[-1]
                image_path = os.path.join(config.IMAGE_DIR, latest)
                
                # Test detection
                image = cv2.imread(image_path)
                if image is not None:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    detector = LightDetector()
                    analysis = detector.analyze_image(image_rgb)
                    
                    return jsonify({
                        'success': True,
                        'detected': analysis['detected'],
                        'confidence': analysis['confidence'],
                        'red_pixels': analysis['red_pixels']
                    })
        
        return jsonify({'success': False, 'message': 'No images available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """Restart the light detection system"""
    try:
        os.system('sudo systemctl restart light-detector')
        return jsonify({'success': True, 'message': 'System restart initiated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/clear-logs', methods=['POST'])
def api_clear_logs():
    """Clear log files"""
    try:
        if os.path.exists(config.LOG_FILE):
            with open(config.LOG_FILE, 'w') as f:
                f.write('')
        return jsonify({'success': True, 'message': 'Logs cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🌐 Starting Light Detection Web Interface...")
    print("📱 Access at: http://your-pi-ip:5000")
    print("🔧 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 