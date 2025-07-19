import requests
import subprocess
import time
import argparse
import socket
import threading
import os
from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps

class BluetoothClient:
    def __init__(self, host_ip, client_name=None):
        self.host_ip = host_ip  # Can be full URL or just IP
        self.client_name = client_name or socket.gethostname()
        self.running = True
        self.api_key = os.environ.get('BT_API_KEY', 'bluetooth-switch-default-api-key-change-me')
        
        # Create Flask app for receiving commands
        self.app = Flask(__name__)
        self.setup_routes()
    
    def api_key_required(self, f):
        """Decorator to require valid API key"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != self.api_key:
                return jsonify({'success': False, 'message': 'Invalid or missing API key'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def get_bluetooth_status(self):
        """Get current Bluetooth status using blueutil"""
        try:
            result = subprocess.run(['blueutil', '-p'], capture_output=True, text=True)
            return result.stdout.strip() == '1'
        except Exception as e:
            print(f"Error getting Bluetooth status: {e}")
            return False
    
    def get_bluetooth_devices(self):
        """Get connected Bluetooth devices"""
        try:
            result = subprocess.run(['blueutil', '--connected', '--format', 'json'], capture_output=True, text=True)
            if result.returncode == 0:
                import json
                devices = json.loads(result.stdout)
                # Filter for Magic Mouse and Magic Keyboard
                magic_devices = []
                for device in devices:
                    name = device.get('name', '').lower()
                    if 'magic' in name or 'keyboard' in name or 'mouse' in name:
                        magic_devices.append({
                            'name': device.get('name', 'Unknown Device'),
                            'type': 'keyboard' if 'keyboard' in name else 'mouse' if 'mouse' in name else 'device',
                            'connected': device.get('connected', False)
                        })
                return magic_devices
            return []
        except Exception as e:
            print(f"Error getting Bluetooth devices: {e}")
            return []
    
    def set_bluetooth_status(self, enabled):
        """Set Bluetooth status using blueutil"""
        try:
            cmd = ['blueutil', '-p', '1' if enabled else '0']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error setting Bluetooth status: {e}")
            return False
    
    def setup_routes(self):
        """Setup Flask routes for receiving commands"""
        
        @self.app.route('/bluetooth', methods=['POST'])
        @self.api_key_required
        def toggle_bluetooth():
            data = request.json
            enabled = data.get('enabled', False)
            
            success = self.set_bluetooth_status(enabled)
            current_status = self.get_bluetooth_status()
            
            print(f"🔵 Bluetooth {'enabled' if current_status else 'disabled'}")
            
            return jsonify({
                'success': success,
                'status': current_status,
                'client_id': self.client_name
            })
        
        @self.app.route('/status', methods=['GET'])
        @self.api_key_required
        def get_status():
            return jsonify({
                'client_id': self.client_name,
                'bluetooth_status': self.get_bluetooth_status(),
                'devices': self.get_bluetooth_devices(),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/devices', methods=['GET'])
        @self.api_key_required
        def get_devices():
            return jsonify({
                'client_id': self.client_name,
                'devices': self.get_bluetooth_devices(),
                'timestamp': datetime.now().isoformat()
            })
    
    def register_with_host(self):
        """Register this client with the host"""
        try:
            headers = {'X-API-Key': self.api_key}
            # Handle both full URLs and IP addresses
            host_url = self.host_ip if self.host_ip.startswith('http') else f'http://{self.host_ip}:5002'
            response = requests.post(f'{host_url}/api/register',
                                   json={'client_id': self.client_name},
                                   headers=headers,
                                   timeout=5)
            
            if response.status_code == 200:
                host_url = self.host_ip if self.host_ip.startswith('http') else f'http://{self.host_ip}:5002'
                print(f"✅ Successfully registered with host at {host_url}")
                return True
            else:
                print(f"❌ Failed to register with host: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering with host: {e}")
            return False
    
    def heartbeat(self):
        """Send periodic heartbeat to host"""
        while self.running:
            try:
                # Re-register to update last_seen timestamp
                self.register_with_host()
                time.sleep(30)  # Send heartbeat every 30 seconds
            except Exception as e:
                print(f"⚠️  Heartbeat error: {e}")
                time.sleep(30)
    
    def run(self):
        """Run the client"""
        print(f"🔌 Starting Bluetooth Client: {self.client_name}")
        print(f"🎯 Connecting to host: {self.host_ip}")
        
        # Register with host
        if not self.register_with_host():
            print("❌ Failed to register with host. Exiting.")
            return
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self.heartbeat, daemon=True)
        heartbeat_thread.start()
        
        # Start Flask server to receive commands
        print(f"🚀 Client listening on port 5001")
        print(f"🔵 Current Bluetooth status: {'ON' if self.get_bluetooth_status() else 'OFF'}")
        
        try:
            self.app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            print("\n👋 Shutting down client...")
            self.running = False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bluetooth Client')
    parser.add_argument('--host', required=True, help='Host IP address')
    parser.add_argument('--name', help='Client name (default: hostname)')
    
    args = parser.parse_args()
    
    client = BluetoothClient(args.host, args.name)
    client.run()
