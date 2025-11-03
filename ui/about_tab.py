"""
About Tab
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont
from config import APP_VERSION
from .theme import COLORS, FONTS

class AboutTab(QWidget):
    """About tab"""
    
    def __init__(self, firejail_handler):
        super().__init__()
        self.firejail_handler = firejail_handler
        self.setStyleSheet(f'background-color: {COLORS["tab_bg"]};')
        self.setup_ui()
    
    def setup_ui(self):
        """Setup about tab"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        
        # Header
        logo = QLabel('InvisVM')
        logo.setFont(QFont(*FONTS['logo']))
        logo.setStyleSheet(f'color: {COLORS["primary"]}; letter-spacing: 1px;')
        header = QHBoxLayout()
        header.addWidget(logo)
        header.addStretch()
        layout.addLayout(header)
        
        # Content
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml(f"""
<h2 style="color: #212121; margin-top: 0;">InvisVM v{APP_VERSION}</h2>
<p style="color: #757575;">Security Sandbox Launcher for Linux</p>
<h3 style="color: #212121;">Features</h3>
<ul><li>🔍 Search and launch any application</li><li>📦 Snap, Flatpak, AppImage support</li><li>🔒 Multiple security policies</li><li>📊 Real-time sandbox monitoring</li></ul>
<h3 style="color: #212121;">System Information</h3>
<p><b>Firejail:</b> {self.firejail_handler.get_firejail_version()}</p>
<h3 style="color: #212121;">Installation</h3>
<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">python3 ~/InvisVM/main.py --install-menu</pre>
<p style="color: #757575; font-size: 12px;">Open Source • GPL v3.0</p>
        """)
        text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_white']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 18px;
            }}
        """)
        layout.addWidget(text)
        layout.addStretch()
        self.setLayout(layout)
