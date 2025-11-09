"""
Firejail Handler Module - CORRECTED WITH PYTHON SCRIPT FIX
Manages sandboxed application execution with comprehensive monitoring

CHANGES:
- Added Python and shell script detection methods
- Modified build_firejail_command() to launch scripts with proper interpreters
- Enhanced get_app_name() to identify script types
- Network policy unchanged: only restrictive blocks network, standard/permissive allow it
"""

import subprocess
import os
import logging
from datetime import datetime
from pathlib import Path
import re
import json
import signal
import time
import uuid
import shutil
import threading

class SandboxLogger:
    """
    Enhanced logger for detailed sandbox monitoring
    """
    def __init__(self, sandbox_id, app_name, policy):
        self.sandbox_id = sandbox_id
        self.app_name = app_name
        self.policy = policy
        self.start_time = datetime.now()
        self.events = []
        self.log_file = os.path.expanduser(f'~/InvisVM/logs/sandbox_{sandbox_id}.log')
        # Initialize log file
        self._init_log_file()
    
    def _init_log_file(self):
        """Initialize detailed log file"""
        with open(self.log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write(f"InvisVM Sandbox Log - {self.app_name}\n")
            f.write("="*80 + "\n")
            f.write(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Security Policy: {self.policy.upper()}\n")
            f.write(f"Sandbox ID: {self.sandbox_id}\n")
            f.write("="*80 + "\n\n")
    
    def log_event(self, event_type, message, details=None):
        """Log a sandbox event"""
        timestamp = datetime.now()
        event = {
            'timestamp': timestamp.isoformat(),
            'type': event_type,
            'message': message,
            'details': details
        }
        self.events.append(event)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp.strftime('%H:%M:%S')}] {event_type.upper()}: {message}\n")
            if details:
                f.write(f"  Details: {details}\n")
    
    def get_formatted_log(self):
        """Get formatted, colorized log for display"""
        lines = []
        
        # Header
        lines.append("╔" + "═"*78 + "╗")
        lines.append(f"║ {'SANDBOX LOG - ' + self.app_name:^76} ║")
        lines.append("╠" + "═"*78 + "╣")
        lines.append(f"║ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S'):62} ║")
        lines.append(f"║ Security Policy: {self.policy.upper():58} ║")
        lines.append(f"║ Sandbox ID: {self.sandbox_id:62} ║")
        lines.append("╠" + "═"*78 + "╣")
        
        # Events
        for event in self.events:
            timestamp = datetime.fromisoformat(event['timestamp'])
            time_str = timestamp.strftime('%H:%M:%S')
            event_type = event['type']
            message = event['message']
            
            # Color coding based on event type
            if event_type in ['error', 'blocked', 'denied']:
                prefix = "🔴"
            elif event_type in ['warning', 'restricted']:
                prefix = "🟡"
            elif event_type in ['success', 'allowed']:
                prefix = "🟢"
            else:
                prefix = "🔵"
            
            lines.append(f"║ [{time_str}] {prefix} {event_type.upper()}")
            lines.append(f"║   {message}")
            if event.get('details'):
                lines.append(f"║   → {event['details']}")
            lines.append("║")
        
        # Runtime
        runtime = (datetime.now() - self.start_time).total_seconds()
        lines.append("╠" + "═"*78 + "╣")
        lines.append(f"║ Total Runtime: {runtime:.1f} seconds{' '*55} ║")
        lines.append("╚" + "═"*78 + "╝")
        
        return "\n".join(lines)


class FirejailHandler:
    """
    Handles launching and monitoring firejailed applications
    """
    
    def __init__(self, log_callback=None):
        """
        Initialize Firejail handler
        
        Args:
            log_callback: Function to call for logging messages
        """
        self.log_callback = log_callback
        self.active_sandboxes = {}
        self.sandbox_loggers = {}
        self.state_file = os.path.expanduser('~/InvisVM/logs/sandboxes.json')
        self.runtime_log_file = os.path.expanduser('~/InvisVM/logs/runtime.log')
        self.setup_logging()
        self.load_state()
        self._ensure_runtime_log()
        
        # Applications that REQUIRE D-Bus to function
        self.dbus_required_apps = {
            'libreoffice', 'lowriter', 'localc', 'loimpress', 'lodraw', 'lomath', 'lobase',
            'soffice', 'writer', 'calc', 'impress', 'draw', 'math', 'base',
            'gnome-terminal', 'konsole', 'xfce4-terminal', 'tilix',
            'nautilus', 'dolphin', 'thunar', 'nemo', 'pcmanfm',
            'gedit', 'kate', 'mousepad', 'pluma',
            'evince', 'okular', 'atril',
            'thunderbird', 'evolution',
            'telegram', 'signal', 'discord', 'slack',
            'gimp', 'inkscape', 'blender',
            'vlc', 'mpv', 'rhythmbox', 'totem',
            'code', 'codium', 'atom', 'sublime',
        }
        
        # LibreOffice file extensions
        self.libreoffice_extensions = {
            '.odt', '.ods', '.odp', '.odg', '.odf', '.odb',
            '.doc', '.docx',
            '.xls', '.xlsx',
            '.ppt', '.pptx',
            '.rtf', '.txt',
        }
    
    def _ensure_runtime_log(self):
        """Ensure runtime log exists and append session separator"""
        if not os.path.exists(self.runtime_log_file):
            with open(self.runtime_log_file, 'w') as f:
                f.write("="*80 + "\n")
                f.write("InvisVM Runtime Log\n")
                f.write("="*80 + "\n\n")
        
        # Add session separator
        with open(self.runtime_log_file, 'a') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
    
    def _log_to_runtime(self, message, level='INFO'):
        """Log to runtime log file (append mode)"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.runtime_log_file, 'a') as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
    
    # ========== NEW SCRIPT DETECTION METHODS ==========
    
    def _is_python_script(self, path):
        """Check if the file is a Python script"""
        if not os.path.isfile(path):
            return False
        
        # Check extension
        ext = os.path.splitext(path)[1].lower()
        if ext == '.py':
            return True
        
        # Check shebang
        try:
            with open(path, 'rb') as f:
                first_line = f.readline()
                if first_line.startswith(b'#!/usr/bin/env python') or \
                   first_line.startswith(b'#!/usr/bin/python'):
                    return True
        except:
            pass
        
        return False
    
    def _is_shell_script(self, path):
        """Check if the file is a shell script"""
        if not os.path.isfile(path):
            return False
        
        # Check extension
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.sh', '.bash']:
            return True
        
        # Check shebang
        try:
            with open(path, 'rb') as f:
                first_line = f.readline()
                if first_line.startswith(b'#!/bin/bash') or \
                   first_line.startswith(b'#!/bin/sh') or \
                   first_line.startswith(b'#!/usr/bin/env bash'):
                    return True
        except:
            pass
        
        return False
    
    def _get_script_interpreter(self, path):
        """
        Get the appropriate interpreter for a script file
        Returns: (interpreter_command, True) if script detected, (None, False) otherwise
        """
        if self._is_python_script(path):
            self.log(f'Detected Python script: {os.path.basename(path)}', 'INFO')
            return (['python3', path], True)
        
        elif self._is_shell_script(path):
            self.log(f'Detected shell script: {os.path.basename(path)}', 'INFO')
            return (['bash', path], True)
        
        # Support for other script types
        ext = os.path.splitext(path)[1].lower()
        interpreters = {
            '.rb': 'ruby',
            '.pl': 'perl',
            '.js': 'node',
            '.lua': 'lua',
            '.tcl': 'tclsh',
        }
        
        if ext in interpreters:
            interpreter = interpreters[ext]
            self.log(f'Detected {interpreter} script: {os.path.basename(path)}', 'INFO')
            return ([interpreter, path], True)
        
        return (None, False)
    
    # ========== END OF NEW METHODS ==========
    
    def setup_logging(self):
        """Setup logging for firejail operations"""
        self.logger = logging.getLogger('FirejailHandler')
        if not self.logger.handlers:
            log_dir = os.path.expanduser('~/InvisVM/logs')
            os.makedirs(log_dir, exist_ok=True)
            
            handler = logging.FileHandler(
                os.path.join(log_dir, 'invisvm.log')
            )
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def cleanup_sandbox_instances(self):
        """
        Clean up orphaned sandbox instance directories
        Returns: (cleaned_count, total_size_mb)
        """
        sandboxes_dir = os.path.expanduser('~/InvisVM/sandboxes')
        if not os.path.exists(sandboxes_dir):
            return 0, 0
        
        running_pids = set(self._get_firejail_pids())
        cleaned_count = 0
        total_size = 0
        
        for item in os.listdir(sandboxes_dir):
            if item.startswith('instance-'):
                instance_path = os.path.join(sandboxes_dir, item)
                
                # Calculate size
                try:
                    for dirpath, dirnames, filenames in os.walk(instance_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if os.path.exists(fp):
                                total_size += os.path.getsize(fp)
                except:
                    pass
                
                # Check if instance is still active
                instance_active = False
                for pid in running_pids:
                    try:
                        with open(f'/proc/{pid}/cwd', 'r') as f:
                            if instance_path in os.readlink(f'/proc/{pid}/cwd'):
                                instance_active = True
                                break
                    except:
                        pass
                
                # Remove if not active
                if not instance_active:
                    try:
                        shutil.rmtree(instance_path)
                        cleaned_count += 1
                        self.log(f'Cleaned up orphaned instance: {item}', 'INFO')
                    except Exception as e:
                        self.log(f'Failed to clean {item}: {str(e)}', 'WARNING')
        
        total_size_mb = total_size / (1024 * 1024)
        self._log_to_runtime(f'Cleanup: Removed {cleaned_count} instances, freed {total_size_mb:.2f} MB')
        return cleaned_count, total_size_mb
    
    def load_state(self):
        """Load sandbox state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    for pid_str, info in data.items():
                        pid = int(pid_str)
                        if self._is_firejail_pid(pid):
                            info['process'] = None
                            info['timestamp'] = datetime.fromisoformat(info['timestamp'])
                            self.active_sandboxes[pid] = info
                            self._monitor_process(pid, info['name'])
        except Exception as e:
            self.log(f'Could not load state: {str(e)}', 'WARNING')
    
    def save_state(self):
        """Save sandbox state to file"""
        try:
            data = {}
            for pid, info in self.active_sandboxes.items():
                data[str(pid)] = {
                    'name': info['name'],
                    'path': info['path'],
                    'policy': info['policy'],
                    'timestamp': info['timestamp'].isoformat(),
                    'sandbox_id': info.get('sandbox_id', '')
                }
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.log(f'Could not save state: {str(e)}', 'WARNING')
    
    def _is_process_running(self, pid):
        """Check if a process is still running"""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def _is_firejail_pid(self, pid):
        """Check if PID is actually a firejail process"""
        try:
            with open(f'/proc/{pid}/cmdline', 'r') as f:
                cmdline = f.read()
                return 'firejail' in cmdline
        except:
            return False
    
    def _get_firejail_pids(self):
        """Get all firejail PIDs using firejail --list"""
        try:
            result = subprocess.run(
                ['firejail', '--list'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            
            pids = []
            for line in result.stdout.split('\n'):
                match = re.match(r'^\s*(\d+):', line)
                if match:
                    pid = int(match.group(1))
                    if 'zombie' not in line.lower():
                        pids.append(pid)
            return pids
        except Exception as e:
            self.log(f'Error getting firejail PIDs: {str(e)}', 'WARNING')
            return []
    
    def log(self, message, level='INFO'):
        """Log message both to file and callback"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f'[{timestamp}] {level} - {message}'
        
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'SUCCESS':
            self.logger.info(f'✓ {message}')
        
        if self.log_callback:
            self.log_callback(log_message)
        
        self._log_to_runtime(message, level)
    
    def get_app_name(self, path):
        """Determine application name from path - ENHANCED VERSION"""
        
        # ADDED: Check for Python scripts first
        if self._is_python_script(path):
            basename = os.path.basename(path)
            return f'Python Script ({basename})'
        
        # ADDED: Check for shell scripts
        if self._is_shell_script(path):
            basename = os.path.basename(path)
            return f'Shell Script ({basename})'
        
        if not '/' in path and not os.path.exists(path):
            return path.capitalize()
        
        if os.path.isdir(path):
            return f'File Manager ({os.path.basename(path)})'
        
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return os.path.basename(path)
        
        basename = os.path.basename(path)
        _, ext = os.path.splitext(path)
        
        ext_map = {
            '.pdf': f'PDF ({basename})',
            '.txt': f'Text ({basename})',
            '.html': f'Browser ({basename})',
            '.htm': f'Browser ({basename})',
            '.mp4': f'Video ({basename})',
            '.avi': f'Video ({basename})',
            '.mkv': f'Video ({basename})',
            '.webm': f'Video ({basename})',
            '.mp3': f'Audio ({basename})',
            '.wav': f'Audio ({basename})',
            '.flac': f'Audio ({basename})',
            '.jpg': f'Image ({basename})',
            '.jpeg': f'Image ({basename})',
            '.png': f'Image ({basename})',
            '.gif': f'Image ({basename})',
            '.bmp': f'Image ({basename})',
            '.webp': f'Image ({basename})',
            '.svg': f'Image ({basename})',
            '.doc': f'Document ({basename})',
            '.docx': f'Document ({basename})',
            '.odt': f'Document ({basename})',
            '.xls': f'Spreadsheet ({basename})',
            '.xlsx': f'Spreadsheet ({basename})',
            '.ods': f'Spreadsheet ({basename})',
            '.ppt': f'Presentation ({basename})',
            '.pptx': f'Presentation ({basename})',
            '.odp': f'Presentation ({basename})',
        }
        
        return ext_map.get(ext.lower(), f'File ({basename})')
    
    def _is_libreoffice_file(self, path):
        """Check if the file should be opened with LibreOffice"""
        if not os.path.isfile(path):
            return False
        ext = os.path.splitext(path)[1].lower()
        return ext in self.libreoffice_extensions
    
    def _get_libreoffice_command(self, file_path):
        """Get the appropriate LibreOffice command for a file"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.odt', '.doc', '.docx', '.rtf', '.txt']:
            return 'lowriter'
        elif ext in ['.ods', '.xls', '.xlsx']:
            return 'localc'
        elif ext in ['.odp', '.ppt', '.pptx']:
            return 'loimpress'
        elif ext in ['.odg']:
            return 'lodraw'
        elif ext in ['.odf']:
            return 'lomath'
        elif ext in ['.odb']:
            return 'lobase'
        else:
            return 'libreoffice'
    
    def _requires_dbus(self, path):
        """Check if the application requires D-Bus to function properly"""
        # Check if it's a LibreOffice file
        if os.path.isfile(path) and self._is_libreoffice_file(path):
            return True
        
        # Check app name against D-Bus required apps
        app_name = os.path.basename(path).lower()
        for dbus_app in self.dbus_required_apps:
            if dbus_app in app_name:
                return True
        
        return False
    
    def _create_firefox_profile(self, instance_id):
        """Create a unique Firefox profile for this instance"""
        profiles_dir = os.path.expanduser('~/.mozilla/firefox')
        os.makedirs(profiles_dir, exist_ok=True)
        
        profile_name = f'invisvm-{instance_id}'
        profile_path = os.path.join(profiles_dir, profile_name)
        
        if os.path.exists(profile_path):
            try:
                shutil.rmtree(profile_path)
            except:
                pass
        
        os.makedirs(profile_path, exist_ok=True)
        
        profiles_ini = os.path.join(profiles_dir, 'profiles.ini')
        profile_section = f'\n[Profile{instance_id}]\nName=invisvm-{instance_id}\nIsRelative=1\nPath={profile_name}\n'
        
        try:
            with open(profiles_ini, 'a') as f:
                f.write(profile_section)
            self.log(f'Created Firefox profile: {profile_name}', 'INFO')
        except Exception as e:
            self.log(f'Warning: Could not update profiles.ini: {str(e)}', 'WARNING')
        
        return profile_path, profile_name
    
    def _monitor_sandbox_activity(self, pid, sandbox_logger, policy):
        """Monitor sandbox for specific activities"""
        def monitor():
            try:
                # Monitor network attempts
                if policy == 'restrictive':
                    sandbox_logger.log_event('restricted', 'Network access blocked by policy')
                    sandbox_logger.log_event('info', 'Application is running in restricted mode')
                
                # Monitor process status
                while self._is_firejail_pid(pid):
                    time.sleep(2)
                    
                    # Check for network activity (if allowed)
                    if policy != 'restrictive':
                        try:
                            net_result = subprocess.run(
                                ['ss', '-tunp'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=2
                            )
                            if str(pid) in net_result.stdout:
                                sandbox_logger.log_event('network', 'Network connection established')
                        except:
                            pass
            
            except Exception as e:
                sandbox_logger.log_event('error', f'Monitoring error: {str(e)}')
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    def build_firejail_command(self, path, policy='standard'):
        """Build firejail command with security policy - CORRECTED VERSION"""
        cmd = ['firejail']
        
        # CRITICAL: Disable default firejail profiles that may block network
        cmd.append('--noprofile')
        
        # D-Bus configuration
        needs_dbus = self._requires_dbus(path)
        if needs_dbus:
            cmd.append('--dbus-user=filter')
            cmd.append('--dbus-system=none')
            self.log(f'Using filtered D-Bus (app requires it)', 'INFO')
        else:
            cmd.append('--dbus-user=none')
            cmd.append('--dbus-system=none')
            self.log(f'Blocking D-Bus (app does not require it)', 'INFO')
        
        # Network policy: ONLY restrictive blocks network
        if policy == 'restrictive':
            cmd.extend([
                '--net=none',
                '--nosound',
                '--novideo',
            ])
            self.log('Policy: Restrictive (network, sound, video blocked)', 'INFO')
        
        elif policy == 'standard':
            # Standard allows network - explicitly allow it
            # No --net=none, and allow protocols
            cmd.append('--protocol=unix,inet,inet6,netlink')
            if not needs_dbus:
                cmd.extend(['--nosound', '--novideo'])
            self.log('Policy: Standard (network ALLOWED, basic restrictions)', 'INFO')
        
        elif policy == 'permissive':
            # Permissive allows everything - explicitly allow network
            cmd.append('--protocol=unix,inet,inet6,netlink')
            self.log('Policy: Permissive (network ALLOWED, most access allowed)', 'INFO')
        
        # FIXED: Determine how to launch the file
        if os.path.isdir(path):
            # Directory: open with file manager
            cmd.extend(['xdg-open', path])
            self.log('Opening directory with file manager', 'INFO')
        
        elif os.path.isfile(path):
            # Check if it's a script that needs an interpreter
            interpreter_cmd, is_script = self._get_script_interpreter(path)
            
            if is_script:
                # FIXED: Launch script with explicit interpreter
                cmd.extend(interpreter_cmd)
                self.log(f'Launching script with interpreter: {interpreter_cmd[0]}', 'SUCCESS')
            
            elif self._is_libreoffice_file(path):
                # LibreOffice documents
                lo_command = self._get_libreoffice_command(path)
                cmd.extend([lo_command, path])
                self.log(f'Launching LibreOffice directly with {lo_command}', 'INFO')
            
            elif os.access(path, os.X_OK):
                # Executable file
                cmd.append(path)
                self.log('Launching executable directly', 'INFO')
            
            else:
                # Other files: use default handler
                cmd.extend(['xdg-open', path])
                self.log('Opening file with default handler', 'INFO')
        
        else:
            # Application command (not a file path)
            app_binary = os.path.basename(path).lower()
            cmd.append(path)
            
            # Special handling for Firefox
            if 'firefox' in app_binary:
                instance_id = str(uuid.uuid4())[:8]
                profile_path, profile_name = self._create_firefox_profile(instance_id)
                cmd.extend([
                    '-P', profile_name,
                    '--new-instance',
                    '--no-remote'
                ])
                self.log(f'Firefox: Using unique profile {profile_name}', 'INFO')
        
        return cmd
    
    def launch_sandboxed(self, path, policy='standard'):
        """Launch application in firejail sandbox"""
        try:
            sandbox_id = str(uuid.uuid4())[:8]
            self.log(f'Preparing to launch: {path}', 'INFO')
            self.log(f'Security policy: {policy}', 'INFO')
            
            # Handle file:// URLs and clean path
            if path.startswith('file://'):
                path = path.replace('file://', '')
                import urllib.parse
                path = urllib.parse.unquote(path)
            
            path = path.strip()
            
            if path.startswith('~'):
                path = os.path.expanduser(path)
            
            if os.path.exists(path):
                path = os.path.abspath(path)
            
            self.log(f'Resolved path: {path}', 'INFO')
            
            # Check if path exists
            if not os.path.exists(path) and not self._is_executable(path):
                error_msg = f'Path not found: {path}'
                self.log(error_msg, 'ERROR')
                return False, None, error_msg
            
            app_name = self.get_app_name(path)
            self.log(f'Application: {app_name}', 'INFO')
            
            # Create sandbox logger
            sandbox_logger = SandboxLogger(sandbox_id, app_name, policy)
            sandbox_logger.log_event('startup', f'Initializing sandbox with {policy} policy')
            
            # Build firejail command
            cmd = self.build_firejail_command(path, policy)
            self.log(f'Command: {" ".join(cmd)}', 'INFO')
            
            # Check if firejail is installed
            if not self._check_firejail_installed():
                error_msg = 'Firejail is not installed'
                self.log(error_msg, 'ERROR')
                sandbox_logger.log_event('error', error_msg)
                return False, None, error_msg
            
            try:
                # Set up environment
                env = os.environ.copy()
                
                # Determine working directory
                if os.path.isfile(path):
                    work_dir = os.path.dirname(path)
                elif os.path.isdir(path):
                    work_dir = path
                else:
                    work_dir = os.path.expanduser('~')
                
                sandbox_logger.log_event('launch', f'Starting application in {policy} sandbox')
                
                # Launch the process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,     # ← Discards all output
                    stderr=subprocess.DEVNULL,     # ← Discards all errors
                    start_new_session=True,
                    env=env,
                    cwd=work_dir
                )

                pid = process.pid


                
                # Track the sandbox
                self.active_sandboxes[pid] = {
                    'name': app_name,
                    'path': path,
                    'policy': policy,
                    'timestamp': datetime.now(),
                    'process': process,
                    'sandbox_id': sandbox_id
                }
                
                self.sandbox_loggers[pid] = sandbox_logger
                sandbox_logger.log_event('success', f'Application started successfully (PID: {pid})')
                
                self.save_state()
                
                success_msg = f'Successfully launched {app_name} (PID: {pid}) in {policy} sandbox'
                self.log(success_msg, 'SUCCESS')
                
                # Start monitoring
                self._monitor_process(pid, app_name)
                self._monitor_sandbox_activity(pid, sandbox_logger, policy)
                
                return True, pid, success_msg
            
            except Exception as e:
                error_msg = f'Failed to launch process: {str(e)}'
                self.log(error_msg, 'ERROR')
                sandbox_logger.log_event('error', error_msg)
                return False, None, error_msg
        
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            self.log(error_msg, 'ERROR')
            import traceback
            self.log(traceback.format_exc(), 'ERROR')
            return False, None, error_msg
    
    def _check_firejail_installed(self):
        """Check if firejail is installed"""
        try:
            result = subprocess.run(
                ['which', 'firejail'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _is_executable(self, path):
        """Check if path is an executable in PATH"""
        try:
            result = subprocess.run(
                ['which', path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def kill_sandbox(self, pid):
        """Kill a sandboxed process"""
        try:
            if pid not in self.active_sandboxes:
                if self._is_process_running(pid):
                    app_name = f"Process {pid}"
                else:
                    return False, f'Process {pid} not found'
            else:
                app_name = self.active_sandboxes[pid]['name']
            
            # Log termination
            if pid in self.sandbox_loggers:
                self.sandbox_loggers[pid].log_event('shutdown', 'Sandbox terminated by user')
            
            try:
                # Try graceful shutdown first
                subprocess.run(
                    ['firejail', '--shutdown', str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                self.log(f'Sent shutdown to {app_name} (PID: {pid})', 'INFO')
                
                time.sleep(0.5)
                
                # Force kill if still running
                if self._is_process_running(pid):
                    os.kill(pid, signal.SIGKILL)
                    self.log(f'Sent SIGKILL to {app_name} (PID: {pid})', 'INFO')
                
                # Clean up tracking
                if pid in self.active_sandboxes:
                    del self.active_sandboxes[pid]
                if pid in self.sandbox_loggers:
                    del self.sandbox_loggers[pid]
                
                self.save_state()
                return True, f'Terminated {app_name} (PID: {pid})'
            
            except ProcessLookupError:
                # Already dead
                if pid in self.active_sandboxes:
                    del self.active_sandboxes[pid]
                if pid in self.sandbox_loggers:
                    del self.sandbox_loggers[pid]
                self.save_state()
                return True, f'Process {pid} already terminated'
            
        except Exception as e:
            return False, f'Failed to kill: {str(e)}'
    
    def get_sandbox_log(self, pid):
        """Get formatted log for a specific sandbox"""
        if pid in self.sandbox_loggers:
            return self.sandbox_loggers[pid].get_formatted_log()
        else:
            # Try to load from file
            sandbox_id = self.active_sandboxes.get(pid, {}).get('sandbox_id', '')
            log_file = os.path.expanduser(f'~/InvisVM/logs/sandbox_{sandbox_id}.log')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    return f.read()
        
        return "No log available for this sandbox."
    
    def get_runtime_log(self):
        """Get current runtime log"""
        if os.path.exists(self.runtime_log_file):
            with open(self.runtime_log_file, 'r') as f:
                return f.read()
        return "No runtime log available."
    
    def _monitor_process(self, pid, app_name):
        """Monitor process in background thread"""
        import threading
        
        def monitor():
            try:
                if pid not in self.active_sandboxes:
                    return
                
                process = self.active_sandboxes[pid].get('process')
                
                if process:
                    process.wait()
                    try:
                        process.communicate(timeout=1)
                    except:
                        pass
                else:
                    # No process object, poll PID
                    while self._is_firejail_pid(pid):
                        time.sleep(1)
                
                # Process ended
                if pid in self.active_sandboxes:
                    timestamp = self.active_sandboxes[pid]['timestamp']
                    elapsed = (datetime.now() - timestamp).total_seconds()
                    msg = f'Application closed: {app_name} (ran for {elapsed:.1f}s)'
                    self.log(msg, 'INFO')
                    
                    if pid in self.sandbox_loggers:
                        self.sandbox_loggers[pid].log_event('shutdown', f'Application closed after {elapsed:.1f}s')
                    
                    del self.active_sandboxes[pid]
                    if pid in self.sandbox_loggers:
                        del self.sandbox_loggers[pid]
                    self.save_state()
            
            except Exception as e:
                self.log(f'Error monitoring process: {str(e)}', 'ERROR')
                if pid in self.active_sandboxes:
                    del self.active_sandboxes[pid]
                self.save_state()
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def reload_state_from_disk(self):
        """
        Force reload state from disk
        CRITICAL: This catches sandboxes launched from other processes (right-click)
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                
                # Merge new PIDs from disk with existing ones
                for pid_str, info in data.items():
                    pid = int(pid_str)
                    
                    # Only add if not already tracking and process is still running
                    if pid not in self.active_sandboxes and self._is_firejail_pid(pid):
                        info['process'] = None
                        info['timestamp'] = datetime.fromisoformat(info['timestamp'])
                        self.active_sandboxes[pid] = info
                        self._monitor_process(pid, info['name'])
                        self.log(f'Detected external sandbox: {info["name"]} (PID: {pid})', 'INFO')
        
        except Exception as e:
            self.log(f'Could not reload state: {str(e)}', 'WARNING')
    
    def get_active_sandboxes(self):
        """
        Get list of active sandboxes with ROBUST detection
        CRITICAL: Now detects ALL firejail processes, even from other InvisVM instances
        """
        # Get all running firejail PIDs from system
        running_pids = set(self._get_firejail_pids())
        
        # First, reload state from disk to catch external launches
        self.reload_state_from_disk()
        
        # Clean up finished processes
        finished_pids = []
        for pid in list(self.active_sandboxes.keys()):
            if pid not in running_pids and not self._is_firejail_pid(pid):
                finished_pids.append(pid)
        
        for pid in finished_pids:
            if pid in self.active_sandboxes:
                self.log(f'Cleaning up dead process: {pid}', 'INFO')
                del self.active_sandboxes[pid]
        
        if finished_pids:
            self.save_state()
        
        # Now detect any firejail PIDs not in our tracking
        # This catches right-click launches that haven't been loaded yet
        for pid in running_pids:
            if pid not in self.active_sandboxes:
                # This is a firejail process we're not tracking
                # Try to get info about it
                try:
                    with open(f'/proc/{pid}/cmdline', 'r') as f:
                        cmdline = f.read().replace('\x00', ' ').strip()
                    
                    # Extract app name from command line
                    app_name = self._extract_app_name_from_cmdline(cmdline)
                    
                    # Add to tracking
                    self.active_sandboxes[pid] = {
                        'name': app_name,
                        'path': 'Unknown',
                        'policy': 'unknown',
                        'timestamp': datetime.now(),
                        'process': None
                    }
                    
                    self.log(f'Detected untracked firejail: {app_name} (PID: {pid})', 'INFO')
                    self._monitor_process(pid, app_name)
                
                except Exception as e:
                    # If we can't read cmdline, just use PID
                    self.active_sandboxes[pid] = {
                        'name': f'Firejail Process (PID {pid})',
                        'path': 'Unknown',
                        'policy': 'unknown',
                        'timestamp': datetime.now(),
                        'process': None
                    }
                    self._monitor_process(pid, f'Process {pid}')
        
        return [
            {
                'pid': pid,
                'name': info['name'],
                'policy': info['policy'],
                'path': info['path'],
                'timestamp': info['timestamp']
            }
            for pid, info in self.active_sandboxes.items()
            if pid in running_pids or self._is_firejail_pid(pid)
        ]
    
    def _extract_app_name_from_cmdline(self, cmdline):
        """
        Extract application name from firejail command line
        """
        # Common patterns in firejail cmdline
        if 'python3' in cmdline.lower():
            # Extract Python script name
            parts = cmdline.split()
            for i, part in enumerate(parts):
                if part == 'python3' and i + 1 < len(parts):
                    script_path = parts[i + 1]
                    basename = os.path.basename(script_path)
                    return f'Python Script ({basename})'
            return 'Python Script'
        
        elif 'bash' in cmdline.lower():
            # Extract shell script name
            parts = cmdline.split()
            for i, part in enumerate(parts):
                if part == 'bash' and i + 1 < len(parts):
                    script_path = parts[i + 1]
                    basename = os.path.basename(script_path)
                    return f'Shell Script ({basename})'
            return 'Shell Script'
        
        elif 'firefox' in cmdline.lower():
            return 'Firefox (firefox)'
        elif 'chrome' in cmdline.lower():
            return 'Chrome (google-chrome)'
        elif 'lowriter' in cmdline.lower():
            return 'LibreOffice Writer'
        elif 'localc' in cmdline.lower():
            return 'LibreOffice Calc'
        elif 'loimpress' in cmdline.lower():
            return 'LibreOffice Impress'
        elif 'libreoffice' in cmdline.lower():
            return 'LibreOffice'
        elif 'nautilus' in cmdline.lower():
            return 'Files (nautilus)'
        elif 'gnome-terminal' in cmdline.lower():
            return 'Terminal'
        elif 'evince' in cmdline.lower():
            return 'Document Viewer'
        elif 'xdg-open' in cmdline.lower():
            # Try to extract filename
            parts = cmdline.split()
            for part in parts:
                if '/' in part and not part.startswith('-'):
                    basename = os.path.basename(part)
                    if basename:
                        return f'File ({basename})'
            return 'File Viewer'
        else:
            # Try to extract any recognizable binary name
            parts = cmdline.split()
            for part in parts:
                if '/' in part or part.startswith('-'):
                    continue
                if len(part) > 2 and part.isalnum():
                    return f'{part.capitalize()}'
        
        return 'Sandboxed Application'
    
    def get_firejail_version(self):
        """Get installed firejail version"""
        try:
            result = subprocess.run(
                ['firejail', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            output = result.stdout.strip()
            if output:
                return output.split('\n')[0]
            return 'Unknown version'
        except:
            return 'Not installed'
    
    def verify_sandbox(self, path, policy='standard'):
        """Verify that sandbox will work correctly"""
        if not self._check_firejail_installed():
            return False, 'Firejail is not installed'
        
        path = os.path.abspath(os.path.expanduser(path))
        
        if not os.path.exists(path) and not self._is_executable(path):
            return False, f'Path does not exist: {path}'
        
        if os.path.isfile(path) and not os.access(path, os.R_OK):
            return False, f'No read permission: {path}'
        
        return True, 'Sandbox configuration is valid'
