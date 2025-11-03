"""
Active Sandboxes Tab
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .theme import COLORS, FONTS

class SandboxesTab(QWidget):
    """Active sandboxes tab"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet(f'background-color: {COLORS["tab_bg"]};')
        self.setup_ui()
    
    def setup_ui(self):
        """Setup sandboxes tab"""
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
        title = QLabel('Active Sandboxes')
        title.setFont(QFont(*FONTS['title']))
        title.setStyleSheet(f'color: {COLORS["text_primary"]};')
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Application', 'PID', 'Policy', 'Actions'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_white']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 10px;
                border: none;
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_light']};
                padding: 10px;
                border: none;
                font-weight: 600;
                font-size: 10pt;
            }}
        """)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        refresh = QPushButton('🔄  Refresh')
        refresh.clicked.connect(self.main_window.refresh_sandboxes)
        btn_layout.addWidget(refresh)
        
        self.kill_all = QPushButton('⛔  Kill All')
        self.kill_all.clicked.connect(self.main_window.kill_all_sandboxes)
        self.kill_all.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_dark']};
            }}
        """)
        btn_layout.addWidget(self.kill_all)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.status = QLabel('No sandboxes running')
        self.status.setStyleSheet(f'color: {COLORS["text_secondary"]}; font-style: italic;')
        layout.addWidget(self.status)
        
        self.setLayout(layout)
    
    def populate_sandboxes(self, sandboxes):
        """Populate sandboxes table"""
        self.table.setRowCount(0)
        self.kill_all.setEnabled(len(sandboxes) > 0)
        
        if not sandboxes:
            self.table.setRowCount(1)
            item = QTableWidgetItem('No active sandboxes')
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 4)
            self.status.setText('All sandboxes inactive')
        else:
            self.table.setRowCount(len(sandboxes))
            for row, sandbox in enumerate(sandboxes):
                name = QTableWidgetItem(sandbox['name'])
                self.table.setItem(row, 0, name)
                
                pid = QTableWidgetItem(str(sandbox['pid']))
                pid.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, pid)
                
                policy = QTableWidgetItem(sandbox['policy'].capitalize())
                policy.setTextAlignment(Qt.AlignCenter)
                color_map = {'restrictive': Qt.red, 'standard': Qt.blue, 'permissive': Qt.darkGreen}
                policy.setForeground(color_map.get(sandbox['policy'], Qt.black))
                self.table.setItem(row, 2, policy)
                
                kill = QPushButton('❌ Kill')
                kill.setMaximumWidth(80)
                kill.setMinimumHeight(36)
                kill.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['danger']};
                        color: white;
                        border: none;
                        padding: 6px 10px;
                        border-radius: 4px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['danger_dark']};
                    }}
                """)
                pid_val = sandbox['pid']
                kill.clicked.connect(lambda checked, p=pid_val: self.main_window.kill_sandbox_action(p))
                self.table.setCellWidget(row, 3, kill)
                self.table.setRowHeight(row, 48)
            
            self.status.setText(f'{len(sandboxes)} sandbox(es) running')
