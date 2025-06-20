#!/usr/bin/env python3
"""
Installation Script for Desktop Screensaver
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    try:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_shortcut():
    """Create desktop shortcut"""
    try:
        import winreg
        
        # Get the path to the current script
        script_path = Path(__file__).parent / "main.py"
        python_path = sys.executable
        
        # Create shortcut on desktop
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "Desktop Screensaver.lnk"
        
        # Create .lnk file content (simplified)
        shortcut_content = f"""
[InternetShortcut]
URL=file:///{python_path}
IconFile={python_path}
IconIndex=0
        """.strip()
        
        with open(shortcut_path, 'w') as f:
            f.write(shortcut_content)
        
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"Warning: Could not create desktop shortcut: {e}")
        return False

def setup_startup():
    """Setup application to start with Windows"""
    try:
        import winreg
        
        # Get the path to the current script
        script_path = Path(__file__).parent / "main.py"
        python_path = sys.executable
        
        # Create registry key
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run"
        )
        
        # Set the value
        winreg.SetValueEx(
            key,
            "DesktopScreensaver",
            0,
            winreg.REG_SZ,
            f'"{python_path}" "{script_path}"'
        )
        
        winreg.CloseKey(key)
        print("Application will start with Windows")
        return True
        
    except Exception as e:
        print(f"Warning: Could not setup startup: {e}")
        return False

def main():
    """Main installation function"""
    print("Desktop Screensaver Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Installation failed!")
        sys.exit(1)
    
    # Create desktop shortcut
    create_shortcut()
    
    # Ask about startup
    try:
        startup = input("Start application with Windows? (y/n): ").lower().strip()
        if startup in ['y', 'yes']:
            setup_startup()
    except KeyboardInterrupt:
        print("\nInstallation cancelled")
        sys.exit(1)
    
    print("\nInstallation completed successfully!")
    print("\nTo run the application:")
    print("1. Double-click the desktop shortcut, or")
    print("2. Run: python main.py")
    print("\nThe application will appear in your system tray.")

if __name__ == "__main__":
    main() 