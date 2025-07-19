from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import subprocess
import socket
import threading
import time
import os
from datetime import datetime
from functools import wraps
import logging

# Configure logging to filter SSL connection attempts
logging.getLogger('werkzeug').setLevel(logging.WARNING)

class NoSSLFilter(logging.Filter):
    def filter(self, record):
        # Filter out SSL-related error messages
        message = record.getMessage()
        return not any(ssl_term in message.lower() for ssl_term in [
            'ssl', 'tls', 'https', 'certificate', 'handshake', 'connection broken'
        ])

# Apply the filter to Flask's logger
flask_logger = logging.getLogger('werkzeug')
flask_logger.addFilter(NoSSLFilter())

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bluetooth-switch-secret-key-change-me')

# Authentication settings
USERNAME = os.environ.get('BT_USERNAME', '')
PASSWORD = os.environ.get('BT_PASSWORD', '')
AUTH_ENABLED = bool(USERNAME and PASSWORD)

# Store connected clients
clients = {}

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AUTH_ENABLED:
            return f(*args, **kwargs)
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_local_ip():
    """Get the local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a non-routable address to determine local IP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_hostname():
    """Get the hostname of this Mac"""
    return socket.gethostname()

def get_bluetooth_status():
    """Get current Bluetooth status using blueutil"""
    try:
        result = subprocess.run(['blueutil', '-p'], capture_output=True, text=True)
        return result.stdout.strip() == '1'
    except Exception as e:
        print(f"Error getting Bluetooth status: {e}")
        return False

def get_bluetooth_devices():
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

def set_bluetooth_status(enabled):
    """Set Bluetooth status using blueutil"""
    try:
        cmd = ['blueutil', '-p', '1' if enabled else '0']
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error setting Bluetooth status: {e}")
        return False

@app.route('/')
@login_required
def index():
    """Main page with Bluetooth controls"""
    host_bt_status = get_bluetooth_status()
    host_devices = get_bluetooth_devices()
    return render_template('index.html', 
                         host_ip=get_local_ip(),
                         host_name=get_hostname(),
                         host_bt_status=host_bt_status,
                         host_devices=host_devices,
                         clients=clients)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if not AUTH_ENABLED:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/bluetooth/host', methods=['POST'])
@login_required
def toggle_host_bluetooth():
    """Toggle Bluetooth on the host Mac"""
    data = request.json
    enabled = data.get('enabled', False)
    
    success = set_bluetooth_status(enabled)
    current_status = get_bluetooth_status()
    
    return jsonify({
        'success': success,
        'status': current_status,
        'devices': get_bluetooth_devices(),
        'message': f"Host Bluetooth {'enabled' if current_status else 'disabled'}"
    })

@app.route('/api/devices', methods=['GET'])
@login_required
def get_devices():
    """Get Bluetooth devices for both host and clients"""
    host_devices = get_bluetooth_devices()
    client_devices = {}
    
    # Get devices from each client
    for client_id, client_info in clients.items():
        try:
            import requests
            response = requests.get(f'http://{client_info["ip"]}:5001/devices', timeout=3)
            if response.status_code == 200:
                client_devices[client_id] = response.json().get('devices', [])
        except:
            client_devices[client_id] = []
    
    return jsonify({
        'host_devices': host_devices,
        'client_devices': client_devices
    })

@app.route('/api/bluetooth/client/<client_id>', methods=['POST'])
@login_required
def toggle_client_bluetooth(client_id):
    """Toggle Bluetooth on a client Mac"""
    if client_id not in clients:
        return jsonify({'success': False, 'message': 'Client not found'}), 404
    
    data = request.json
    enabled = data.get('enabled', False)
    client_ip = clients[client_id]['ip']
    
    try:
        # Send request to client
        import requests
        response = requests.post(f'http://{client_ip}:5001/bluetooth', 
                               json={'enabled': enabled}, 
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            clients[client_id]['bluetooth_status'] = result.get('status', False)
            clients[client_id]['last_seen'] = datetime.now().isoformat()
            
            return jsonify({
                'success': True,
                'status': result.get('status', False),
                'message': f"Client {client_id} Bluetooth {'enabled' if result.get('status') else 'disabled'}"
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to communicate with client'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/register', methods=['POST'])
def register_client():
    """Register a new client"""
    data = request.json
    client_id = data.get('client_id')
    client_ip = request.remote_addr
    
    if not client_id:
        return jsonify({'success': False, 'message': 'Client ID required'}), 400
    
    # Get client's Bluetooth status
    bluetooth_status = False
    try:
        import requests
        response = requests.get(f'http://{client_ip}:5001/status', timeout=3)
        if response.status_code == 200:
            bluetooth_status = response.json().get('bluetooth_status', False)
    except:
        pass
    
    clients[client_id] = {
        'ip': client_ip,
        'registered_at': datetime.now().isoformat(),
        'last_seen': datetime.now().isoformat(),
        'bluetooth_status': bluetooth_status
    }
    
    print(f"✅ Client registered: {client_id} at {client_ip}")
    
    return jsonify({
        'success': True, 
        'message': f'Client {client_id} registered successfully',
        'host_ip': get_local_ip()
    })

@app.route('/api/status')
def get_status():
    """Get overall system status"""
    return jsonify({
        'host': {
            'ip': get_local_ip(),
            'bluetooth_status': get_bluetooth_status()
        },
        'clients': clients
    })

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest file"""
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json')

@app.route('/icon-192.png')
def icon_192():
    """Serve 192x192 icon as SVG with PNG mime type"""
    from flask import Response
    svg_content = '''<svg width="192" height="192" viewBox="0 0 192 192" xmlns="http://www.w3.org/2000/svg">
        <rect width="192" height="192" rx="40" fill="#3b82f6"/>
        <path d="M106.13 57.13L84 35V67.18l-17.1-17.1-8.52 8.52L72.76 72l-22.38 22.38 8.52 8.52L84 87.82V120l34.26-34.26L99.28 78l-8.46-8.46 8.46-8.46 19.8 19.8zm-8.46-8.46L84 63.28V41.28l7.8 7.8zm0 56.28L84 120.52v-19.08l13.8 13.77z" fill="white"/>
    </svg>'''
    return Response(svg_content, mimetype='image/svg+xml')

@app.route('/icon-512.png') 
def icon_512():
    """Serve 512x512 icon as SVG with PNG mime type"""
    from flask import Response
    svg_content = '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
        <rect width="512" height="512" rx="100" fill="#3b82f6"/>
        <path d="M284.35 152.35L224 92V179.49l-45.6-45.6-22.72 22.72L194.03 192l-59.68 59.68 22.72 22.72L224 230.51V320l91.35-91.35L265.41 208l-22.56-22.56 22.56-22.56 52.8 52.8zm-22.56-22.56L224 168.75V108.75l20.8 20.8zm0 150.08L224 321.39V249.39l36.8 36.74z" fill="white"/>
    </svg>'''
    return Response(svg_content, mimetype='image/svg+xml')

@app.route('/sw.js')
def service_worker():
    """Serve service worker"""
    from flask import send_from_directory, make_response
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

def cleanup_clients():
    """Remove clients that haven't been seen for a while"""
    while True:
        time.sleep(30)  # Check every 30 seconds
        now = datetime.now()
        to_remove = []
        
        for client_id, client_info in clients.items():
            try:
                last_seen = datetime.fromisoformat(client_info['last_seen'])
                if (now - last_seen).total_seconds() > 120:  # 2 minutes timeout
                    to_remove.append(client_id)
            except:
                to_remove.append(client_id)
        
        for client_id in to_remove:
            print(f"🗑️  Removing inactive client: {client_id}")
            del clients[client_id]

if __name__ == '__main__':
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_clients, daemon=True)
    cleanup_thread.start()
    
    host_ip = get_local_ip()
    print(f"🎯 Starting Bluetooth Manager Host")
    print(f"📱 Access from your phone: http://{host_ip}:5002")
    print(f"🖥️  Local access: http://localhost:5002")
    print(f"🖥️  Also try: http://127.0.0.1:5002")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
    except PermissionError:
        print("❌ Permission denied. Trying localhost only...")
        app.run(host='127.0.0.1', port=5002, debug=False, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 5002 is already in use. Please kill the process first:")
            print("   lsof -ti:5002 | xargs kill -9")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
