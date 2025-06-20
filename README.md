# Desktop Time & Date Screensaver

A professional Windows desktop application that functions as an intelligent screensaver, displaying a customizable full-screen time and date interface when the user is inactive.

## Features

- **Smart Activation System**: Automatically detects user inactivity with customizable timers
- **Visual Interface**: Full-screen time and date display with elegant typography and themes
- **Dashboard Integration**: Connects to developer website dashboard for remote configuration
- **Application Management**: Auto-update system, system tray integration, and startup options
- **Multi-monitor Support**: Works across all connected displays
- **Low Resource Usage**: Optimized for minimal system impact

## Installation

1. **Prerequisites**:
   - Python 3.8 or higher
   - Windows 10/11

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

## Configuration

The application can be configured through:
- System tray menu
- Settings dialog
- Configuration file (`config.json`)

## Usage

- **Automatic Mode**: The screensaver activates automatically after the set inactivity period
- **Manual Activation**: Press `Ctrl+Alt+S` to manually activate/deactivate
- **System Tray**: Right-click the tray icon for quick access to settings

## Development

This application is built with:
- **PyQt6**: Modern GUI framework
- **pynput**: Input monitoring for inactivity detection
- **psutil**: System resource monitoring
- **requests**: Dashboard API communication

## macOS Installation & Usage

### Prerequisites
- Python 3.8+
- pip
- (Optional) [PyInstaller](https://pyinstaller.org/) for building a .app bundle
- (Optional) [pyobjc](https://pypi.org/project/pyobjc/) if you want to extend macOS integration

### Install dependencies
```sh
pip install -r requirements.txt
```

### Run the app
```sh
python main.py
```

### Build a macOS .app bundle
```sh
pip install pyinstaller
pyinstaller --windowed --name Restmode main.py
```
The .app bundle will be in the `dist/` folder.

### Enable Startup at Login
Use the in-app settings or tray menu to enable/disable startup at login. This uses AppleScript to add/remove the app from Login Items.

### Notes
- Fullscreen video detection and system activity are implemented using AppleScript.
- Screen turn-off uses `pmset displaysleepnow` (requires appropriate permissions).
- If you encounter permission dialogs, grant the app Accessibility and Automation permissions in System Preferences > Security & Privacy.

## Linux Installation & Usage

### Prerequisites
- Python 3.8+
- pip
- (Optional) [PyInstaller](https://pyinstaller.org/) for building a .AppImage or binary
- [wmctrl](https://github.com/wmctrl/wmctrl), [xdotool](https://github.com/jordansissel/xdotool), [xset] (for X11)

### Install dependencies
```sh
sudo apt install wmctrl xdotool x11-xserver-utils  # For Ubuntu/Debian
pip install -r requirements.txt
```

### Run the app
```sh
python main.py
```

### Build a Linux binary
```sh
pip install pyinstaller
pyinstaller --windowed --name Restmode main.py
```
The binary will be in the `dist/` folder.

### Enable Startup at Login
Use the in-app settings or tray menu to enable/disable startup at login. This creates/removes a `.desktop` file in `~/.config/autostart/`.

### Notes
- Fullscreen video detection and system activity are implemented using `wmctrl` and `xdotool`.
- Screen turn-off uses `xset dpms force off` (X11) or `loginctl lock-session` (Wayland/GNOME).
- If you encounter permission dialogs, ensure the app has access to the X server (may require running with `xhost +` or similar for testing).

## License

MIT License - see LICENSE file for details.

## Download InactivityWatch Pro

- [Windows (.exe)](https://github.com/Restmode-Time/restmode-window/releases/download/v1.0.0/InactivityWatchPro-setup.exe)
- [macOS (.dmg)](https://github.com/Restmode-Time/restmode-window/releases/download/v1.0.0/InactivityWatchPro.dmg)
- [Linux (.AppImage)](https://github.com/Restmode-Time/restmode-window/releases/download/v1.0.0/InactivityWatchPro.AppImage)
- [Android (.apk)](https://github.com/Restmode-Time/restmode-window/releases/download/v1.0.0/InactivityWatchPro.apk) 