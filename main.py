"""
InvisVM - Main Application (main.py)
Contains application logic, event handling, and integration
ROBUST DETECTION: Shared state file for cross-process sandbox tracking
"""

import sys
import os
import argparse
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileDialog, QTabWidget, QDialog, QLabel,
    QPushButton, QComboBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from pathlib import Path

# Import custom modules
from config import *
from firejail_handler import FirejailHandler
from context_menu_installer import ContextMenuInstaller
from ui import LauncherTab, AppSearchLauncher, PoliciesTab, SandboxesTab, AboutTab, COLORS


class PolicySelectionDialog(QDialog):
    """
    Dialog for selecting security policy when opening from context menu
    """
    
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.selected_policy = None
        self.setup_ui()
        
        # Make dialog stay on top
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle('InvisVM - Select Security Policy')
        self.setGeometry(300, 300, 550, 350)
        self.setModal(True)
        
        # Modern styling - FIXED dropdown hover issue
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #1a1a1a;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QComboBox {
                background-color: white;
                color: #1a1a1a;
                border: 2px solid #2196F3;
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 2px solid #1976D2;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #2196F3;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #1a1a1a;
                selection-background-color: #E3F2FD;
                selection-color: #1976D2;
                border: 2px solid #2196F3;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #1a1a1a;
                background-color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #BBDEFB;
                color: #0D47A1;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel('🔐 Select Security Policy')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976D2;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # File info
        file_name = os.path.basename(self.file_path)
        file_label = QLabel(f'📁 File: {file_name}')
        file_label.setStyleSheet('color: #666; font-size: 11pt; padding: 10px; background-color: #e3f2fd; border-radius: 5px;')
        file_label.setWordWrap(True)
        layout.addWidget(file_label)
        
        # Policy selection
        policy_label = QLabel('Choose security policy:')
        policy_label.setStyleSheet('font-weight: bold; font-size: 12pt; color: #424242;')
        layout.addWidget(policy_label)
        
        self.policy_combo = QComboBox()
        self.policy_combo.addItems(SECURITY_POLICIES.keys())
        self.policy_combo.setCurrentText('standard')
        self.policy_combo.currentTextChanged.connect(self.update_description)
        self.policy_combo.setMinimumHeight(45)
        layout.addWidget(self.policy_combo)
        
        # Policy description
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet('color: #1976D2; font-style: italic; font-size: 10pt; padding: 10px; background-color: white; border-radius: 5px;')
        self.update_description('standard')
        layout.addWidget(self.desc_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        launch_btn = QPushButton('✓ Launch in Sandbox')
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        launch_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton('✗ Cancel')
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(launch_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_description(self, policy):
        """Update policy description"""
        desc = SECURITY_POLICIES[policy]['description']
        self.desc_label.setText(f"ℹ️ {desc}")
    
    def accept(self):
        """User clicked Launch"""
        self.selected_policy = self.policy_combo.currentText()
        super().accept()
    
    def get_selected_policy(self):
        """Get the selected policy"""
        return self.selected_policy


class InvisVMMainWindow(QMainWindow):
    """
    Main application window for InvisVM
    Handles logic, events, and UI integration
    """
    
    def __init__(self, file_path=None):
        """
        Initialize main window
        
        Args:
            file_path: Optional file path to open immediately
        """
        super().__init__()
        self.file_path = file_path
        self.firejail_handler = FirejailHandler(log_callback=self.log_message)
        
        # Setup logging
        self.setup_logging()
        
        # Setup UI components
        self.setup_ui()
        self.setup_menubar()
        
        # Setup auto-refresh timer (updates every 2 seconds)
        # CRITICAL: This will now detect ALL firejail processes, even from right-click
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_sandboxes)
        self.refresh_timer.start(2000)
        
        # Initial refresh of sandboxes
        self.refresh_sandboxes()
        
        # If file path provided, open it immediately (without dialog)
        if file_path:
            self.open_file_with_default_policy(file_path)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_ui(self):
        """Setup user interface using UI components"""
        self.setWindowTitle(f'InvisVM v{APP_VERSION} - Sandbox Launcher')
        self.setMinimumSize(900, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Import all UI components
        from ui import LauncherTab, AppSearchLauncher, PoliciesTab, SandboxesTab, AboutTab
        
        # Create UI components from ui.py
        self.launcher_tab = LauncherTab(self)
        self.search_launcher_tab = AppSearchLauncher(self)  # NEW
        self.policies_tab = PoliciesTab()
        self.sandboxes_tab = SandboxesTab(self)
        self.about_tab = AboutTab(self.firejail_handler)
        
        # Add tabs
        self.tabs.addTab(self.launcher_tab, '🚀 Launcher')
        self.tabs.addTab(self.search_launcher_tab, '🔍 Search Apps')  # NEW
        self.tabs.addTab(self.policies_tab, '🔒 Security Policies')
        self.tabs.addTab(self.sandboxes_tab, '📊 Active Sandboxes')
        self.tabs.addTab(self.about_tab, 'ℹ️ About')
        
        layout.addWidget(self.tabs)
        
        # Setup refresh timer (existing code continues...)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_sandboxes)
        self.refresh_timer.start(2000)  # Refresh every 2 seconds
        
        # Initial refresh
        self.refresh_sandboxes()

    
    def setup_menubar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        open_action = file_menu.addAction('&Open File...')
        open_action.triggered.connect(self.browse_file)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('E&xit')
        exit_action.triggered.connect(self.close)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        install_action = tools_menu.addAction('Install &Context Menu')
        install_action.triggered.connect(self.install_context_menu)
        
        uninstall_action = tools_menu.addAction('&Uninstall Context Menu')
        uninstall_action.triggered.connect(self.uninstall_context_menu)
    
    # =========================================================================
    # FILE MANAGEMENT
    # =========================================================================
    
    def browse_file(self):
        """Browse for file to sandbox"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select File or Application',
            os.path.expanduser('~'),
            'All Files (*)'
        )
        
        if file_path:
            self.file_path = file_path
            self.launcher_tab.set_file_path(os.path.basename(file_path))
    
    # =========================================================================
    # SANDBOX LAUNCHING
    # =========================================================================
    
    def quick_launch(self, app_cmd):
        """Quick launch application"""
        self.file_path = app_cmd
        self.launcher_tab.set_file_path(app_cmd)
        
        policy = self.launcher_tab.get_selected_policy()
        success, pid, message = self.firejail_handler.launch_sandboxed(
            app_cmd,
            policy
        )
        
        if success:
            QMessageBox.information(self, '✓ Sandbox Started', message)
            self.refresh_sandboxes()
        else:
            QMessageBox.critical(self, '✗ Error', message)
    
    def launch_sandboxed(self):
        """Launch selected file in sandbox"""
        if not self.file_path:
            QMessageBox.warning(
                self,
                'No File Selected',
                'Please select a file or application to sandbox.'
            )
            return
        
        policy = self.launcher_tab.get_selected_policy()
        success, pid, message = self.firejail_handler.launch_sandboxed(
            self.file_path,
            policy
        )
        
        if success:
            QMessageBox.information(self, '✓ Sandbox Started', message)
            self.refresh_sandboxes()
        else:
            QMessageBox.critical(self, '✗ Error', message)
    
    def open_file_with_default_policy(self, file_path):
        """Open file with default (standard) policy"""
        self.file_path = file_path
        self.launcher_tab.set_file_path(os.path.basename(file_path))
        
        policy = 'standard'
        success, pid, message = self.firejail_handler.launch_sandboxed(
            file_path,
            policy
        )
        
        self.log_message(f'Opened: {message}')
    
    # =========================================================================
    # SANDBOX MANAGEMENT - ROBUST DETECTION
    # =========================================================================
    
    def refresh_sandboxes(self):
        """
        Refresh active sandboxes list
        CRITICAL: This now uses robust detection to find ALL firejail processes
        """
        # Force reload state from disk (catches right-click launches)
        self.firejail_handler.reload_state_from_disk()
        
        # Get sandboxes (includes detection from firejail --list)
        sandboxes = self.firejail_handler.get_active_sandboxes()
        
        # Update UI
        self.sandboxes_tab.populate_sandboxes(sandboxes)
    
    def auto_refresh_sandboxes(self):
        """Auto-refresh sandboxes (called by timer)"""
        self.refresh_sandboxes()
    
    def kill_sandbox_action(self, pid):
        """Kill a specific sandbox"""
        reply = QMessageBox.question(
            self,
            'Confirm Kill',
            f'Terminate process {pid}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = self.firejail_handler.kill_sandbox(pid)
            
            if success:
                QMessageBox.information(self, '✓ Sandbox Terminated', message)
                self.refresh_sandboxes()
            else:
                QMessageBox.critical(self, '✗ Error', message)
    
    def kill_all_sandboxes(self):
        """Kill all active sandboxes"""
        sandboxes = self.firejail_handler.get_active_sandboxes()
        
        if not sandboxes:
            QMessageBox.information(
                self,
                'No Sandboxes',
                'There are no active sandboxes to terminate.'
            )
            return
        
        reply = QMessageBox.question(
            self,
            'Confirm Kill All',
            f'Terminate all {len(sandboxes)} active sandbox(es)?\n\nThis action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            killed_count = 0
            failed_count = 0
            
            for sandbox in sandboxes:
                success, message = self.firejail_handler.kill_sandbox(sandbox['pid'])
                if success:
                    killed_count += 1
                else:
                    failed_count += 1
            
            self.refresh_sandboxes()
            
            result_msg = f'Successfully terminated {killed_count} sandbox(es).'
            if failed_count > 0:
                result_msg += f'\n{failed_count} sandbox(es) failed to terminate.'
            
            QMessageBox.information(self, '✓ Kill All Complete', result_msg)
    
    # =========================================================================
    # CONTEXT MENU INTEGRATION
    # =========================================================================
    
    def install_context_menu(self):
        """Install context menu integration"""
        installer = ContextMenuInstaller()
        success, message = installer.install()
        
        if success:
            QMessageBox.information(self, 'Success', message)
        else:
            QMessageBox.critical(self, 'Error', message)
    
    def uninstall_context_menu(self):
        """Uninstall context menu integration"""
        installer = ContextMenuInstaller()
        success, message = installer.uninstall()
        
        if success:
            QMessageBox.information(self, 'Success', message)
        else:
            QMessageBox.critical(self, 'Error', message)
    
    # =========================================================================
    # LOGGING & UTILITIES
    # =========================================================================
    
    def log_message(self, message):
        """Log message to file and console"""
        self.logger.info(message)


# ============================================================================
# CONTEXT MENU POLICY DIALOG HANDLER (STANDALONE MODE)
# ============================================================================

def launch_with_policy_dialog(file_path):
    """
    Launch file with policy selection dialog (for context menu)
    CRITICAL: Uses shared state file so main GUI can detect it
    """
    app = QApplication(sys.argv)
    
    # Show policy selection dialog
    dialog = PolicySelectionDialog(file_path)
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        policy = dialog.get_selected_policy()
        
        # Close the dialog first
        dialog.close()
        app.processEvents()
        
        # CRITICAL: Create handler that saves to shared state file
        handler = FirejailHandler()
        
        # Launch sandbox - this will save to state file
        success, pid, message = handler.launch_sandboxed(file_path, policy)
        
        # Force immediate state save
        if success:
            handler.save_state()
            
        # Show result dialog
        msg_box = QMessageBox()
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        if success:
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle('✓ Sandbox Started')
            msg_box.setText(f'{message}\n\nThe application is now running in a secure {policy} sandbox.')
            msg_box.setInformativeText(f'Process ID: {pid}\n\nOpen InvisVM GUI to monitor this sandbox in the Active Sandboxes tab.')
        else:
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle('✗ Error')
            msg_box.setText(f'Failed to start sandbox:\n\n{message}')
        
        msg_box.exec_()
    
    sys.exit(0)


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='InvisVM - Security Sandbox Launcher')
    parser.add_argument('--file', help='File to open in sandbox')
    parser.add_argument('--install-menu', action='store_true', help='Install context menu')
    parser.add_argument('--uninstall-menu', action='store_true', help='Uninstall context menu')
    parser.add_argument('--select-policy', action='store_true', help='Show policy selection dialog for context menu')
    
    args = parser.parse_args()
    
    # Handle context menu installation
    if args.install_menu:
        installer = ContextMenuInstaller()
        success, message = installer.install()
        print(message)
        return
    
    # Handle context menu uninstallation
    if args.uninstall_menu:
        installer = ContextMenuInstaller()
        success, message = installer.uninstall()
        print(message)
        return
    
    # Handle context menu with policy selection
    if args.select_policy and args.file:
        launch_with_policy_dialog(args.file)
        return
    
    # Launch GUI application
    app = QApplication(sys.argv)
    window = InvisVMMainWindow(file_path=args.file)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()