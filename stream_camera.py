#!/usr/bin/env python3

import subprocess
import time
import signal
import sys
import os

def signal_handler(sig, frame):
    print('\nStopping stream...')
    subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
    subprocess.run(['pkill', '-f', 'python3.*stream_camera'], capture_output=True)
    sys.exit(0)

def start_camera_stream():
    """Start camera streaming with rpicam-vid using web server approach"""
    
    # Set up signal handler for clean shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting Raspberry Pi Camera Stream...")
    print("=" * 50)
    print("Stream will be available at:")
    print("Web browser: http://192.168.29.91:8080")
    print("VLC: vlc http://192.168.29.91:8080/stream.m3u8")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Kill any existing rpicam processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        time.sleep(1)
        
        # Create a simple web server directory
        os.makedirs('/tmp/stream', exist_ok=True)
        
        # Start rpicam-vid with HLS streaming
        cmd = [
            'rpicam-vid',
            '--width', '1280',
            '--height', '720',
            '--framerate', '30',
            '--codec', 'h264',
            '--inline',
            '--output', '/tmp/stream/stream.m3u8',
            '--timeout', '0'
        ]
        
        print("Starting rpicam-vid with HLS streaming...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start a simple HTTP server to serve the stream
        http_cmd = ['python3', '-m', 'http.server', '8080', '--directory', '/tmp/stream']
        print("Starting HTTP server on port 8080...")
        http_process = subprocess.Popen(http_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Stream started successfully!")
        print("Access via web browser: http://192.168.29.91:8080")
        print("Waiting for connections...")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping stream...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        subprocess.run(['pkill', '-f', 'python3.*http.server'], capture_output=True)
        print("Stream stopped")

def start_simple_stream():
    """Start a simple MJPEG stream that works with Wayland"""
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting simple MJPEG stream...")
    print("=" * 50)
    print("Stream will be available at:")
    print("Web browser: http://192.168.29.91:8080")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        time.sleep(1)
        
        # Start rpicam-vid with MJPEG streaming to stdout
        cmd = [
            'rpicam-vid',
            '--width', '1280',
            '--height', '720',
            '--framerate', '30',
            '--codec', 'mjpeg',
            '--inline',
            '--output', '-',
            '--timeout', '0'
        ]
        
        print("Starting rpicam-vid with MJPEG streaming...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start a simple HTTP server that pipes the MJPEG stream
        http_cmd = ['python3', '-m', 'http.server', '8080']
        print("Starting HTTP server on port 8080...")
        http_process = subprocess.Popen(http_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Stream started successfully!")
        print("Access via web browser: http://192.168.29.91:8080")
        print("Waiting for connections...")
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping stream...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        subprocess.run(['pkill', '-f', 'python3.*http.server'], capture_output=True)
        print("Stream stopped")

def start_web_stream():
    """Start a web-based stream using rpicam-vid and a custom web server"""
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Starting web-based camera stream...")
    print("=" * 50)
    print("Stream will be available at:")
    print("Web browser: http://192.168.29.91:8080")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        time.sleep(1)
        
        # Create a simple web server that serves the camera stream
        web_server_script = '''
import http.server
import socketserver
import subprocess
import threading
import time

class CameraHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <head><title>Raspberry Pi Camera Stream</title></head>
            <body>
            <h1>Raspberry Pi Camera Stream</h1>
            <img src="/stream" width="1280" height="720" />
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            
            # Start rpicam-vid process
            cmd = ['rpicam-vid', '--width', '1280', '--height', '720', '--framerate', '30', '--codec', 'mjpeg', '--inline', '--output', '-', '--timeout', '0']
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            try:
                while True:
                    # Read MJPEG data
                    data = process.stdout.read(1024)
                    if not data:
                        break
                    self.wfile.write(b'--frame\\r\\n')
                    self.wfile.write(b'Content-Type: image/jpeg\\r\\n\\r\\n')
                    self.wfile.write(data)
                    self.wfile.write(b'\\r\\n')
            except:
                pass
            finally:
                process.terminate()
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", 8080), CameraHandler) as httpd:
    print("Server started at http://192.168.29.91:8080")
    httpd.serve_forever()
'''
        
        # Write the web server script to a temporary file
        with open('/tmp/camera_server.py', 'w') as f:
            f.write(web_server_script)
        
        print("Starting web server with camera stream...")
        process = subprocess.Popen(['python3', '/tmp/camera_server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("Stream started successfully!")
        print("Access via web browser: http://192.168.29.91:8080")
        print("Waiting for connections...")
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping stream...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        subprocess.run(['pkill', '-f', 'rpicam-vid'], capture_output=True)
        subprocess.run(['pkill', '-f', 'python3.*camera_server'], capture_output=True)
        print("Stream stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "mjpeg":
            start_simple_stream()
        elif sys.argv[1] == "web":
            start_web_stream()
        else:
            print("Usage: python3 stream_camera.py [mjpeg|web]")
            print("  mjpeg: Simple MJPEG stream")
            print("  web: Web-based stream with custom server")
    else:
        start_web_stream() 