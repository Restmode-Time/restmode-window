import os
import json
import shutil

CONFIG_PATH = os.path.expandvars(r'%USERPROFILE%/.screensaver/config.json')
BACKUP_PATH = os.path.expandvars(r'%USERPROFILE%/.screensaver/config_backup.json')

# Backup the original config
if os.path.exists(CONFIG_PATH):
    shutil.copy(CONFIG_PATH, BACKUP_PATH)
    print(f"Backup created at {BACKUP_PATH}")
else:
    print(f"Config file not found at {CONFIG_PATH}")
    exit(1)

# Read and attempt to fix malformed JSON
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    raw = f.read()

# Try to fix common trailing comma issues
import re
raw = re.sub(r',\s*([}\]])', r'\1', raw)

try:
    config = json.loads(raw)
except Exception as e:
    print(f"Failed to parse config: {e}")
    exit(1)

# Ensure display settings
config.setdefault('display', {})
config['display']['show_weather'] = True
config['display']['show_todo'] = True

# Ensure todo section
if 'todo' not in config or not isinstance(config['todo'], dict):
    config['todo'] = {"items": ["Buy groceries", "Call Alice", "Finish report"]}
else:
    config['todo'].setdefault('items', ["Buy groceries", "Call Alice", "Finish report"])

# Write back the fixed config
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print("Config updated successfully!") 