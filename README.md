# 🔵 Bluetooth Manager for Two Macs

A simple Flask## 🚀 Quick Start

### 🔐 Authentication Setup

**Option 1: Using the run script with custom credentials**
```bash
# Default credentials (admin/bluetooth123)
./scripts/run_with_auth.sh

# Custom credentials
./scripts/run_with_auth.sh myuser mypassword
```

**Option 2: Environment variables**
```bash
export BT_USERNAME="myuser"
export BT_PASSWORD="mypassword"
cd host && python3 app.py
```

**Option 3: Docker with custom credentials**
```bash
BT_USERNAME=myuser BT_PASSWORD=mypass docker-compose -f docker/docker-compose.yml up
```

### 📱 iPhone Home Screen Setup

1. Open Safari on your iPhone
2. Navigate to `http://YOUR_MAC_IP:5002`
3. Tap the Share button (square with arrow up)
4. Tap "Add to Home Screen"
5. Name it "Bluetooth Switch"
6. Tap "Add" - you now have a home screen icon!

### Docker Setup (Recommended)sed solution to manage Bluetooth on two Macs sharing the same Magic Keyboard and Mouse. Switch between Macs easily through a clean, modern web interface accessible from your phone or any device on the local network.

## 📋 Features

- **Host-Client Architecture**: One Mac acts as the host, the other as a client
- **Modern Web Interface**: Clean, white background with blue glow effects and smooth animations  
- **Device Listing**: Shows connected Magic Mouse and Magic Keyboard with real device names
- **Dynamic Hostnames**: Shows actual Mac names instead of "Mac 1/Mac 2"
- **Authentication**: Secure login with customizable username/password (optional)
- **iPhone Home Screen**: Easy bookmark creation for quick access from iPhone home screen
- **Docker Support**: Easy deployment with Docker containers or native Python
- **Mobile-Friendly**: Responsive design optimized for phones and tablets
- **Quick Switch**: Toggle Bluetooth off on one Mac and on the other with one click
- **Real-time Status**: See current Bluetooth status with animated blue indicators
- **Local Network Only**: All communication stays within your local WiFi network

## 🛠️ Setup Options

### Option 1: Docker (Recommended)
Easiest deployment with isolated containers and automatic dependency management.

### Option 2: Native Python
Traditional Python virtual environment setup.

## 📁 Project Structure

```
bluetooth/
├── host/                   # Host server files
│   ├── app.py             # Flask server application
│   ├── templates/         # Web interface templates
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Docker configuration
├── client/                # Client files
│   ├── app.py            # Client application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Docker configuration
├── docker/               # Docker orchestration
│   ├── docker-compose.yml        # Host container config
│   └── docker-compose.client.yml # Client container config
└── scripts/              # Setup and run scripts
    ├── setup-docker.sh          # Docker setup
    ├── setup-native.sh          # Native Python setup
    ├── start-host-docker.sh     # Start host with Docker
    ├── start-client-docker.sh   # Start client with Docker
    ├── start-host.sh            # Start host native
    ├── start-client.sh          # Start client native
    ├── run_with_auth.sh         # Start host with authentication
    └── kill-ports.sh            # Kill processes on ports 5001/5002
```

## � Quick Start

### Docker Setup (Recommended)

1. **Setup Docker environment on both Macs:**
   ```bash
   ./scripts/setup-docker.sh
   ```

2. **On the Host Mac (Mac 1):**
   ```bash
   ./scripts/start-host-docker.sh
   ```

3. **On the Client Mac (Mac 2):**
   ```bash
   ./scripts/start-client-docker.sh 192.168.1.100
   ```

4. **Access the interface:**
   - From your phone: `http://192.168.1.100:5002`
   - From the same Mac: `http://localhost:5002`
   - Login with your credentials

### Native Python Setup

1. **Setup on both Macs:**
   ```bash
   ./scripts/setup-native.sh
   ```

2. **On the Host Mac (Mac 1):**
   ```bash
   ./scripts/start-host.sh
   ```

3. **On the Client Mac (Mac 2):**
   ```bash
   ./scripts/start-client.sh 192.168.1.100
   ```

## 📱 Using the Web Interface

1. **Modern Design**: Clean white background with blue glow effects and smooth animations
2. **Device Lists**: Shows connected Magic Mouse and Magic Keyboard for each Mac
3. **Apple Icons**: Large Apple logos with blue glow effects for device identification
4. **Animated Status**: Blue pulsing lights show real-time Bluetooth status
5. **Individual Controls**: Turn Bluetooth on/off for each Mac with gradient buttons
6. **Quick Switch**: One-click button to toggle between Macs
7. **Mobile Optimized**: Perfect for phone access with responsive design
8. **Auto-refresh**: Updates device lists after switching

## 🐳 Docker Benefits

- **Isolation**: Containers don't interfere with your system
- **Easy Setup**: One script installs everything needed
- **Consistency**: Same environment on both Macs
- **Easy Updates**: Pull new versions without conflicts
- **Resource Management**: Better control over resource usage

⚠️ **Note**: Docker on macOS runs in a Linux VM, so Bluetooth control uses Linux tools (bluez) inside containers but still needs native blueutil for actual macOS Bluetooth control. The setup script installs both.

## 🔧 How It Works

1. **Host Mac** runs a Flask server that provides the web interface and coordinates Bluetooth control
2. **Client Mac** runs a lightweight Flask client that receives commands from the host
3. **Both Macs** use `blueutil` to control their Bluetooth hardware
4. **Communication** happens over HTTP on your local network only

## 📝 Command Examples

```bash
# Docker Commands
./scripts/start-host-docker.sh           # Start host with Docker
./scripts/start-client-docker.sh 192.168.1.100  # Start client with Docker

# Native Python Commands
./scripts/start-host.sh                  # Start host native
./scripts/start-client.sh 192.168.1.100 # Start client native

# Manual Docker commands
docker-compose -f docker/docker-compose.yml up --build        # Host
HOST_IP=192.168.1.100 docker-compose -f docker/docker-compose.client.yml up --build  # Client

# Direct Python commands
cd host && python3 app.py               # Host server
cd client && python3 app.py --host 192.168.1.100  # Client

# Bluetooth control (macOS)
blueutil -p  # Shows 1 if Bluetooth is on, 0 if off
blueutil -p 1  # Turn Bluetooth ON
blueutil -p 0  # Turn Bluetooth OFF
```

## 🔒 Security Notes

- **Local network only**: The system only works on your local WiFi network
- **Optional Authentication**: Set BT_USERNAME and BT_PASSWORD environment variables for login protection
- **Session-based**: Login sessions are maintained until browser is closed or logout
- **Environment Variables**: Credentials are configured via environment variables (not hardcoded)
- **HTTP only**: Uses plain HTTP since it's local network only (consider HTTPS for production)

### Authentication Examples:
```bash
# No authentication (anyone on network can access)
python3 app.py

# With authentication 
export BT_USERNAME="admin"
export BT_PASSWORD="secure123"
python3 app.py

# Docker with auth
BT_USERNAME=admin BT_PASSWORD=secure123 docker-compose up
```

## 🐛 Troubleshooting

### Docker Issues:
- **Container won't start**: Check Docker is running and has proper permissions
- **Bluetooth not working**: Ensure native blueutil is installed (`brew install blueutil`)
- **Port conflicts**: Make sure ports 5002 and 5001 are available
- **Network issues**: Use `docker network ls` to check network configuration

### Connection Issues:
- **Client won't connect**: Verify both Macs are on the same network
- **Wrong IP address**: Use `ipconfig getifaddr en0` to get correct IP
- **Firewall blocking**: Check macOS firewall settings for ports 5002/5001
- **Login issues**: Verify BT_USERNAME and BT_PASSWORD environment variables are set correctly

### Bluetooth Issues:
- **Commands not working**: Test `blueutil -p` manually
- **Permission denied**: Grant terminal/Docker Bluetooth permissions in System Preferences
- **Device not switching**: Wait a few seconds between commands for devices to reconnect

## 📄 Files Overview

- `host/app.py` - Main Flask server for the host Mac
- `client/app.py` - Client script for the second Mac  
- `host/templates/index.html` - Modern web interface
- `scripts/setup-*.sh` - Automated setup scripts
- `scripts/start-*.sh` - Start scripts for different methods
- `docker/docker-compose*.yml` - Docker orchestration files
- `*/requirements.txt` - Python dependencies
- `*/Dockerfile` - Docker container configurations

## 🎯 Quick Start Summary

**Docker with Authentication (Recommended):**
1. `BT_USERNAME=myuser BT_PASSWORD=mypass ./scripts/setup-docker.sh` on both Macs
2. `BT_USERNAME=myuser BT_PASSWORD=mypass ./scripts/start-host-docker.sh` on Mac 1
3. `./scripts/start-client-docker.sh <MAC1_IP>` on Mac 2
4. Open `http://<MAC1_IP>:5002` on your phone and login

**Native Python with Authentication:**
1. `./scripts/setup-native.sh` on both Macs  
2. `./scripts/run_with_auth.sh myuser mypass` on Mac 1
3. `./scripts/start-client.sh <MAC1_IP>` on Mac 2
4. Open `http://<MAC1_IP>:5002` on your phone and login

**iPhone Home Screen Icon:**
1. Safari → `http://<MAC1_IP>:5002`
2. Share button → Add to Home Screen
3. Name it "Bluetooth Switch" → Add

Control Bluetooth with the beautiful web interface! 🎉
