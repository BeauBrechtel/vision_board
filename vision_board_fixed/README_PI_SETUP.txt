VISION BOARD - SIMPLE PI SETUP

1. Flash Raspberry Pi OS WITH DESKTOP using Raspberry Pi Imager.
   In Imager settings, set:
   - username: pi
   - a password you will remember
   - hostname: visionboardpi
   - WiFi if needed
   - SSH enabled if you want remote access

2. Copy this whole vision_board_fixed folder onto the Pi.
   The easiest place is /home/pi/vision_board_fixed.

3. Open Terminal on the Pi and run:

   cd ~/vision_board_fixed
   ./install.sh
   sudo reboot

That is it.

What install.sh does:
- installs Python/Flask/Chromium requirements
- copies the app to /home/pi/vision_board
- creates the Python virtual environment
- creates and starts the visionboard system service
- creates the Chromium kiosk autostart file
- tries to enable Desktop Autologin

After reboot:
- Display: http://localhost:5000/display
- Admin from another computer: http://visionboardpi.local:5000/admin
- Or use the Pi IP: http://PI-IP-ADDRESS:5000/admin

Important:
- Do not remove or mask gnome-keyring.
- If you see a keyring popup, leave password and confirm blank and click Continue.
- Employee and announcement uploads use unique filenames so photos do not overwrite each other.
