# ~/InvisVM/config.py
"""
InvisVM Configuration Module
Centralized configuration for all settings
"""

import os
from pathlib import Path

# Directories
HOME_DIR = str(Path.home())
APP_DIR = os.path.join(HOME_DIR, 'InvisVM')
LOG_DIR = os.path.join(APP_DIR, 'logs')
ASSETS_DIR = os.path.join(APP_DIR, 'assets')

# Create directories if they don't exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Files
LOG_FILE = os.path.join(LOG_DIR, 'invisvm.log')
ICON_FILE = os.path.join(ASSETS_DIR, 'invisvm.png')

# Firejail settings
FIREJAIL_PROFILES = [
    'firefox',
    'chromium',
    'google-chrome',
    'vlc',
    'mpv',
    'evince',
    'gedit',
    'libreoffice',
    'thunderbird',
    'telegram',
]

# Security policies
# NOTE: D-Bus filtering is now handled intelligently per-application
# Applications that require D-Bus (like LibreOffice) will use filtered D-Bus
# Applications that don't need D-Bus will have it completely blocked
SECURITY_POLICIES = {
    'restrictive': {
        'network': False,
        'devices': False,
        'capabilities': ['drop-all'],
        'description': 'Ultra-Restrictive (No network, No devices, Smart D-Bus filtering)'
    },
    'standard': {
        'network': True,  # Unchanged - standard allows network
        'devices': False,
        'capabilities': ['drop-dangerous'],
        'description': 'Standard (Network allowed, Smart D-Bus filtering)'
    },
    'permissive': {
        'network': True,
        'devices': True,
        'capabilities': ['drop-minimal'],
        'description': 'Permissive (Most access allowed, Smart D-Bus filtering)'
    }
}

# Application settings
APP_NAME = 'InvisVM'
APP_VERSION = '1.0.2'  # Updated version with Python script fix
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = f'{APP_NAME} v{APP_VERSION} - Security Sandbox Launcher'

# Logging
LOG_FORMAT = '[%(asctime)s] %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Right-click menu
CONTEXT_MENU_NAME = 'InvisVM'
NAUTILUS_SCRIPTS_DIR = os.path.join(HOME_DIR, '.local/share/nautilus/scripts')
SCRIPT_NAME = 'Open-with-InvisVM'
