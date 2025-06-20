import os
import sys
import shutil
import subprocess
import winreg
from pathlib import Path

APP_NAME = "Restmode"
DEFAULT_INSTALL_DIR = r"C:\\Program Files\\Restmode"
ICON_PATH = "assets/icon.ico"
MAIN_SCRIPT = "main.py"
REQUIREMENTS = "requirements.txt"

# Helper to check admin rights
import ctypes
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

# 1. Ensure admin rights
run_as_admin()

# 2. Ask for install location
print(f"Install location [{DEFAULT_INSTALL_DIR}]: ", end="")
install_dir = input().strip() or DEFAULT_INSTALL_DIR
install_dir = os.path.expandvars(install_dir)

# 3. Install dependencies
print("Installing dependencies...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS])

# 4. Copy files
print(f"Copying files to {install_dir}...")
if os.path.exists(install_dir):
    shutil.rmtree(install_dir)
os.makedirs(install_dir)
for item in os.listdir('.'):
    if item in ["installer", "__pycache__"]:
        continue
    if os.path.isdir(item):
        shutil.copytree(item, os.path.join(install_dir, item))
    else:
        shutil.copy2(item, os.path.join(install_dir, item))

# 5. Create desktop and start menu shortcuts
import winshell
from win32com.client import Dispatch

def create_shortcut(path, target, icon, desc):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.IconLocation = icon
    shortcut.Description = desc
    shortcut.save()

desktop = winshell.desktop()
start_menu = winshell.start_menu()
shortcut_path = os.path.join(desktop, f"{APP_NAME}.lnk")
shortcut_start = os.path.join(start_menu, f"{APP_NAME}.lnk")
main_exe = sys.executable
main_script = os.path.join(install_dir, MAIN_SCRIPT)
create_shortcut(shortcut_path, f'"{main_exe}" "{main_script}"', os.path.join(install_dir, ICON_PATH), APP_NAME)
create_shortcut(shortcut_start, f'"{main_exe}" "{main_script}"', os.path.join(install_dir, ICON_PATH), APP_NAME)

# 6. Set up auto-start with Windows
print("Setting up auto-start...")
key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{main_exe}" "{main_script}"')
winreg.CloseKey(key)

# 7. Register uninstaller
print("Registering uninstaller...")
uninstall_cmd = f'"{main_exe}" "{os.path.join(install_dir, "installer", "uninstall.py")}"'
key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, fr"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}")
winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)
winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, os.path.join(install_dir, ICON_PATH))
winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
winreg.CloseKey(key)

print(f"{APP_NAME} installed successfully!")
print("You can launch it from the desktop or start menu shortcut.")

# Launch the app after install
def launch_app():
    try:
        import subprocess
        main_exe = sys.executable
        main_script = os.path.join(install_dir, MAIN_SCRIPT)
        subprocess.Popen([main_exe, main_script], cwd=install_dir)
        print(f"{APP_NAME} has been launched!")
    except Exception as e:
        print(f"Failed to launch {APP_NAME}: {e}")

launch_app() 