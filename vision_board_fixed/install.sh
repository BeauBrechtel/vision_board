#!/bin/bash
set -e

APP_USER="${SUDO_USER:-$USER}"
APP_HOME="$(eval echo ~$APP_USER)"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$APP_USER" = "root" ]; then
  echo "Do not run this installer with sudo. Run it like this: ./install.sh"
  exit 1
fi

echo "Installing Vision Board for user: $APP_USER"
echo "App folder: $APP_DIR"

# Only install the pieces this app actually needs.
# Do NOT install/remove LightDM, raspberrypi-ui-mods, pi-greeter, or gnome-keyring.
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git chromium

# Create folders the app needs.
mkdir -p "$APP_DIR/static/uploads"
mkdir -p "$APP_HOME/.config/autostart"

# Create Python virtual environment.
cd "$APP_DIR"
python3 -m venv venv
"$APP_DIR/venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r requirements.txt

# Create systemd service for Flask app.
sudo tee /etc/systemd/system/visionboard.service > /dev/null <<SERVICEEOF
[Unit]
Description=Vision Board
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo systemctl daemon-reload
sudo systemctl enable visionboard
sudo systemctl restart visionboard

# Create Chromium kiosk autostart. This assumes Desktop Autologin is already enabled in Raspberry Pi Imager.
cat > "$APP_HOME/.config/autostart/visionboard-kiosk.desktop" <<DESKTOPEOF
[Desktop Entry]
Type=Application
Name=Vision Board Kiosk
Exec=sh -c "sleep 30 && chromium --noerrdialogs --disable-infobars --kiosk http://localhost:5000/display"
X-GNOME-Autostart-enabled=true
DESKTOPEOF

chown -R "$APP_USER:$APP_USER" "$APP_HOME/.config/autostart"

echo ""
echo "Install complete."
echo "Check app status with: sudo systemctl status visionboard"
echo "Admin page: http://$(hostname -I | awk '{print $1}'):5000/admin"
echo "Display page: http://localhost:5000/display"
echo ""
echo "Now reboot with: sudo reboot"
