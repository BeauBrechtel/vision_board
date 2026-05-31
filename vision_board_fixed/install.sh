#!/bin/bash
set -e

APP_USER="${SUDO_USER:-$USER}"
APP_HOME="$(getent passwd "$APP_USER" | cut -d: -f6)"
APP_DIR="$APP_HOME/vision_board"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Vision Board for user: $APP_USER"

sudo apt update
sudo apt install -y python3 python3-pip python3-venv chromium-browser lightdm raspberrypi-ui-mods

mkdir -p "$APP_DIR"
if [ "$SCRIPT_DIR" != "$APP_DIR" ]; then
  cp -a "$SCRIPT_DIR"/. "$APP_DIR"/
fi
sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"

cd "$APP_DIR"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

sudo tee /etc/systemd/system/visionboard.service > /dev/null <<EOF
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
EOF

sudo systemctl daemon-reload
sudo systemctl enable visionboard
sudo systemctl restart visionboard

mkdir -p "$APP_HOME/.config/autostart"
cp "$APP_DIR/visionboard-kiosk.desktop" "$APP_HOME/.config/autostart/visionboard-kiosk.desktop"
sudo chown -R "$APP_USER:$APP_USER" "$APP_HOME/.config"

# Try to enable Desktop Autologin. If this command is unavailable, use raspi-config manually.
if command -v raspi-config >/dev/null 2>&1; then
  sudo raspi-config nonint do_boot_behaviour B4 || true
fi

echo ""
echo "DONE. Reboot now with:"
echo "sudo reboot"
echo ""
echo "Admin page after reboot:"
echo "http://$(hostname -I | awk '{print $1}'):5000/admin"
