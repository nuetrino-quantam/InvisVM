"""
Application Search Tab
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config import SECURITY_POLICIES
from .theme import COLORS, FONTS, get_search_style
import os
import subprocess

class AppSearchLauncher(QWidget):
    """Application search launcher"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.all_apps = []
        self.setStyleSheet(f'background-color: {COLORS["tab_bg"]};')
        self.setup_ui()
        self.load_applications()
    
    def setup_ui(self):
        """Setup search tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        
        # Header
        logo = QLabel('InvisVM')
        logo.setFont(QFont(*FONTS['logo']))
        logo.setStyleSheet(f'color: {COLORS["primary"]}; letter-spacing: 1px;')
        header_layout = QHBoxLayout()
        header_layout.addWidget(logo)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Title
        title = QLabel('Search & Launch Applications')
        title.setFont(QFont(*FONTS['title']))
        title.setStyleSheet(f'color: {COLORS["text_primary"]};')
        layout.addWidget(title)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍  Search apps...')
        self.search_input.setStyleSheet(get_search_style())
        self.search_input.textChanged.connect(self.filter_applications)
        layout.addWidget(self.search_input)
        
        # Results
        self.results_label = QLabel('Loading...')
        self.results_label.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 9pt;')
        layout.addWidget(self.results_label)
        
        # App list
        self.app_list = QListWidget()
        self.app_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 7px;
                background-color: {COLORS['bg_white']};
                font-size: 11pt;
            }}
            QListWidget::item {{
                padding: 12px 14px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_light']};
            }}
        """)
        self.app_list.itemDoubleClicked.connect(self.launch_selected_app)
        layout.addWidget(self.app_list)
        
        # Controls
        controls = QHBoxLayout()
        controls.addWidget(QLabel('Policy:'))
        self.policy_combo = QComboBox()
        self.policy_combo.addItems(SECURITY_POLICIES.keys())
        self.policy_combo.setCurrentText('permissive')
        self.policy_combo.setMaximumWidth(150)
        controls.addWidget(self.policy_combo)
        controls.addStretch()
        
        refresh = QPushButton('🔄')
        refresh.setMaximumWidth(45)
        refresh.clicked.connect(self.load_applications)
        controls.addWidget(refresh)
        
        launch = QPushButton('🚀  Launch')
        launch.clicked.connect(self.launch_selected_app)
        launch.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: bold;
                padding: 8px 18px;
                border-radius: 5px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
        """)
        controls.addWidget(launch)
        
        layout.addLayout(controls)
        layout.addStretch()
        self.setLayout(layout)
    
    def load_applications(self):
        """Load all applications"""
        self.all_apps = []
        
        # Load from all sources
        self.all_apps.extend(self._get_desktop_apps())
        self.all_apps.extend(self._get_snap_apps())
        self.all_apps.extend(self._get_flatpak_apps())
        self.all_apps.extend(self._get_binary_apps())
        self.all_apps.extend(self._get_appimage_apps())
        
        # Remove duplicates
        seen = set()
        unique = []
        for app in self.all_apps:
            key = (app['command'].lower(), app['type'])
            if key not in seen:
                unique.append(app)
                seen.add(key)
        
        self.all_apps = sorted(unique, key=lambda x: x['name'].lower())
        self.filter_applications()
    
    def _get_desktop_apps(self):
        """Get desktop applications"""
        apps = []
        dirs = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            os.path.expanduser('~/.local/share/applications')
        ]
        
        for d in dirs:
            if not os.path.exists(d):
                continue
            try:
                for f in os.listdir(d):
                    if not f.endswith('.desktop'):
                        continue
                    path = os.path.join(d, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            name = None
                            cmd = None
                            for line in file:
                                if line.startswith('Name=') and not name:
                                    name = line.split('=', 1)[1].strip()
                                elif line.startswith('Exec='):
                                    cmd = line.split('=', 1)[1].strip().split()[0].split('/')[-1]
                                elif line.startswith('NoDisplay=true'):
                                    name = None
                                    break
                            if name and cmd:
                                apps.append({'name': name, 'command': cmd, 'path': cmd, 'type': 'desktop', 'icon': '📋'})
                    except:
                        pass
            except:
                pass
        return apps
    
    def _get_snap_apps(self):
        """Get snap applications"""
        apps = []
        if not os.path.exists('/snap/bin'):
            return apps
        try:
            for item in os.listdir('/snap/bin'):
                if item.startswith('.'):
                    continue
                full = os.path.join('/snap/bin', item)
                if os.path.isfile(full) and os.access(full, os.X_OK):
                    apps.append({'name': item.replace('-', ' ').title(), 'command': item, 'path': full, 'type': 'snap', 'icon': '📦'})
        except:
            pass
        return apps
    
    def _get_flatpak_apps(self):
        """Get flatpak applications"""
        apps = []
        dirs = [os.path.expanduser('~/.local/share/applications'), '/usr/share/applications']
        for d in dirs:
            if not os.path.exists(d):
                continue
            try:
                for f in os.listdir(d):
                    if not (f.endswith('.desktop') and f.startswith('org.')):
                        continue
                    path = os.path.join(d, f)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                            name = None
                            cmd = None
                            for line in file:
                                if line.startswith('Name=') and not name:
                                    name = line.split('=', 1)[1].strip()
                                elif line.startswith('Exec=') and 'flatpak' in line:
                                    parts = line.split('=', 1)[1].strip().split()
                                    if 'run' in parts:
                                        idx = parts.index('run')
                                        if idx + 1 < len(parts):
                                            cmd = parts[idx + 1]
                            if name and cmd:
                                apps.append({'name': name, 'command': f'flatpak run {cmd}', 'path': cmd, 'type': 'flatpak', 'icon': '🏠'})
                    except:
                        pass
            except:
                pass
        return apps
    
    def _get_binary_apps(self):
        """Get binary executables"""
        apps = []
        paths = ['/usr/bin', '/usr/local/bin', '/opt/bin', os.path.expanduser('~/.local/bin'), '/usr/games']
        for path in paths:
            if not os.path.exists(path):
                continue
            try:
                for item in os.listdir(path):
                    if item.startswith('.'):
                        continue
                    full = os.path.join(path, item)
                    if os.path.isfile(full) and os.access(full, os.X_OK):
                        apps.append({'name': item.capitalize(), 'command': item, 'path': full, 'type': 'executable', 'icon': '⚙️'})
            except:
                pass
        return apps
    
    def _get_appimage_apps(self):
        """Get AppImage applications"""
        apps = []
        dirs = [os.path.expanduser('~/Applications'), os.path.expanduser('~/Downloads'), '/opt', '/usr/local/bin']
        for d in dirs:
            if not os.path.exists(d):
                continue
            try:
                for item in os.listdir(d):
                    if item.endswith(('.AppImage', '.appimage')):
                        full = os.path.join(d, item)
                        if os.path.isfile(full) and os.access(full, os.X_OK):
                            name = item.replace('.AppImage', '').replace('.appimage', '')
                            apps.append({'name': name, 'command': full, 'path': full, 'type': 'appimage', 'icon': '🖼️'})
            except:
                pass
        return apps
    
    def filter_applications(self):
        """Filter applications"""
        text = self.search_input.text().lower()
        filtered = [app for app in self.all_apps if text in app['name'].lower() or text in app['command'].lower()] if text else self.all_apps[:60]
        
        self.app_list.clear()
        for app in filtered[:150]:
            item = QListWidgetItem(f"{app.get('icon', '⚙️')}  {app['name']}")
            item.setData(Qt.UserRole, app)
            self.app_list.addItem(item)
        
        self.results_label.setText(f"Found {len(filtered)} results" if text else f"{len(self.all_apps)} applications available")
    
    def launch_selected_app(self):
        """Launch selected app"""
        item = self.app_list.currentItem()
        if not item:
            QMessageBox.warning(self, 'No Selection', 'Please select an application')
            return
        
        app = item.data(Qt.UserRole)
        policy = self.policy_combo.currentText()
        success, pid, msg = self.main_window.firejail_handler.launch_sandboxed(app['command'], policy)
        
        if success:
            QMessageBox.information(self, '✓ Sandbox Started', f"{app['name']} (PID: {pid})\nType: {app['type'].upper()}")
            self.main_window.refresh_sandboxes()
        else:
            QMessageBox.critical(self, '✗ Error', f"Failed to launch {app['name']}\n\n{msg}")
