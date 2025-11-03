"""
Security Policies Tab
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont
from config import APP_VERSION
from .theme import COLORS, FONTS

class PoliciesTab(QWidget):
    """Security policies tab"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f'background-color: {COLORS["tab_bg"]};')
        self.setup_ui()
    
    def setup_ui(self):
        """Setup policies tab"""
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
        
        # Title
        title = QLabel('Security Policies')
        title.setFont(QFont(*FONTS['title']))
        title.setStyleSheet(f'color: {COLORS["text_primary"]};')
        layout.addWidget(title)
        
        # Content
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
<h3 style="color: #212121; margin-top: 8px;">🔒 Security Policies</h3>
<p><b style="color: #f44336;">■ Restrictive (Maximum Security)</b></p>
<ul><li>Network: BLOCKED</li><li>Devices: BLOCKED</li><li>Sound: BLOCKED</li></ul>
<p><b style="color: #2196F3;">■ Standard (Balanced)</b></p>
<ul><li>Network: ALLOWED</li><li>Devices: BLOCKED</li><li>Sound: BLOCKED</li></ul>
<p><b style="color: #4CAF50;">■ Permissive (Maximum Compatibility)</b></p>
<ul><li>Network: ALLOWED</li><li>Devices: ALLOWED</li><li>Sound: ALLOWED</li></ul>
<h3 style="color: #212121; margin-top: 16px;">📋 Application Types</h3>
<ul><li>📋 Desktop</li><li>📦 Snap</li><li>🏠 Flatpak</li><li>⚙️ Executable</li><li>🖼️ AppImage</li></ul>
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
