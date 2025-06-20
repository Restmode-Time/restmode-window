import os
import sys
import shutil
import winreg
import ctypes
import winshell
from pathlib import Path

APP_NAME = "Restmode"
DEFAULT_INSTALL_DIR = r"C:\\Program Files\\Restmode"
ICON_PATH = "assets/icon.ico"

# Helper to check admin rights
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        print("Requesting admin rights...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit(0)

run_as_admin()

# Confirm uninstall
yes = input(f"Are you sure you want to uninstall {APP_NAME}? (y/N): ").strip().lower()
if yes != 'y':
    print("Uninstall cancelled.")
    sys.exit(0)

# Remove install directory
install_dir = DEFAULT_INSTALL_DIR
if os.path.exists(install_dir):
    print(f"Removing {install_dir}...")
    shutil.rmtree(install_dir)

# Remove desktop and start menu shortcuts
desktop = winshell.desktop()
start_menu = winshell.start_menu()
shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
shortcut_start = os.path.join(start_menu, f"{APP_NAME}.lnk")
for shortcut in [shortcut_path, shortcut_start]:
    if os.path.exists(shortcut):
        os.remove(shortcut)

# Remove auto-start entry
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteValue(key, APP_NAME)
    winreg.CloseKey(key)
except FileNotFoundError:
    pass

# Remove uninstall registry entry
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, fr"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}", 0, winreg.KEY_ALL_ACCESS)
    winreg.DeleteKey(key, "")
    winreg.CloseKey(key)
except FileNotFoundError:
    pass

print(f"{APP_NAME} has been uninstalled.") 