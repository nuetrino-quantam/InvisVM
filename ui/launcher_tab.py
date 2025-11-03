"""
Application Launcher Tab
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config import SECURITY_POLICIES
from .theme import COLORS, FONTS, get_button_style, get_card_style

class LauncherTab(QWidget):
    """Application launcher tab"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet(f'background-color: {COLORS["tab_bg"]};')
        self.setup_ui()
    
    def setup_ui(self):
        """Setup launcher tab UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        
        # Header
        layout.addLayout(self._create_header())
        
        # File selection
        layout.addWidget(self._create_file_card())
        
        # Quick Launch
        label = QLabel('QUICK LAUNCH')
        label.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 10px; font-weight: 600; letter-spacing: 0.5px;')
        layout.addWidget(label)
        layout.addLayout(self._create_quick_launch())
        
        # Policy selection
        layout.addWidget(self._create_policy_card())
        
        # Launch button
        layout.addWidget(self._create_launch_button())
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_header(self):
        """Create header with logo"""
        layout = QHBoxLayout()
        logo = QLabel('InvisVM')
        font = QFont(*FONTS['logo'])
        logo.setFont(font)
        logo.setStyleSheet(f'color: {COLORS["primary"]}; letter-spacing: 1px;')
        layout.addWidget(logo)
        layout.addStretch()
        return layout
    
    def _create_file_card(self):
        """Create file selection card"""
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)
        
        label = QLabel('FILE OR APPLICATION')
        label.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 10px; font-weight: 600;')
        card_layout.addWidget(label)
        
        file_layout = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        self.file_label.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-style: italic;')
        
        browse_btn = QPushButton('Browse')
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.setMaximumWidth(100)
        browse_btn.clicked.connect(self.main_window.browse_file)
        browse_btn.setStyleSheet(get_button_style())
        
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        file_layout.addWidget(browse_btn)
        card_layout.addLayout(file_layout)
        
        card = QWidget()
        card.setLayout(card_layout)
        card.setStyleSheet(get_card_style())
        return card
    
    def _create_quick_launch(self):
        """Create quick launch buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        apps = [
            ('🌐 Firefox', 'firefox'),
            ('🎬 VLC', 'vlc'),
            ('📄 Document', 'evince'),
            ('🖼️ Image', 'nomacs'),
            ('🗂️ Archive', 'file-roller'),
        ]
        
        for name, cmd in apps:
            btn = QPushButton(name)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, c=cmd: self.main_window.quick_launch(c))
            btn.setStyleSheet(get_button_style())
            layout.addWidget(btn)
        
        layout.addStretch()
        return layout
    
    def _create_policy_card(self):
        """Create policy selection card"""
        from PyQt5.QtWidgets import QComboBox
        
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(10)
        
        label = QLabel('SECURITY POLICY')
        label.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-size: 10px; font-weight: 600;')
        card_layout.addWidget(label)
        
        policy_layout = QHBoxLayout()
        self.policy_combo = QComboBox()
        self.policy_combo.addItems(SECURITY_POLICIES.keys())
        self.policy_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_white']};
                color: {COLORS['text_primary']};
                border: 1.5px solid {COLORS['border']};
                padding: 8px 12px;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: 500;
            }}
        """)
        
        self.policy_desc = QLabel()
        self.policy_desc.setStyleSheet(f'color: {COLORS["primary"]}; font-style: italic; font-size: 9pt;')
        self.policy_desc.setWordWrap(True)
        self.update_policy_description()
        self.policy_combo.currentTextChanged.connect(self.update_policy_description)
        
        policy_layout.addWidget(self.policy_combo, 1)
        policy_layout.addWidget(self.policy_desc, 2)
        card_layout.addLayout(policy_layout)
        
        card = QWidget()
        card.setLayout(card_layout)
        card.setStyleSheet(get_card_style())
        return card
    
    def _create_launch_button(self):
        """Create launch button"""
        btn = QPushButton('🚀  Launch in Sandbox')
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-weight: bold;
                padding: 14px 28px;
                border-radius: 7px;
                font-size: 12pt;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
        """)
        btn.setMinimumHeight(48)
        btn.clicked.connect(self.main_window.launch_sandboxed)
        return btn
    
    def update_policy_description(self):
        """Update policy description"""
        policy = self.policy_combo.currentText()
        desc = SECURITY_POLICIES[policy]['description']
        self.policy_desc.setText(desc)
    
    def set_file_path(self, file_name):
        """Set file path label"""
        self.file_label.setText(file_name)
        self.file_label.setStyleSheet(f'color: {COLORS["text_primary"]};')
    
    def get_selected_policy(self):
        """Get selected policy"""
        return self.policy_combo.currentText()
