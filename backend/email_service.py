"""
Email Service - Send paper details and encrypted packages to principals
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class EmailService:
    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587):
        """
        Email Service for sending paper notifications to principals.
        
        ╔══════════════════════════════════════════════════════════╗
        ║  HOW TO ENABLE REAL EMAIL SENDING:                      ║
        ║                                                          ║
        ║  1. Set demo_mode = False                                ║
        ║  2. Set SENDER_EMAIL to your Gmail address               ║
        ║  3. Set SENDER_PASSWORD to your Gmail App Password       ║
        ║                                                          ║
        ║  To get a Gmail App Password:                            ║
        ║  - Go to Google Account → Security → 2-Step Verification ║
        ║  - Scroll down → App Passwords → Generate one for "Mail" ║
        ║  - Copy the 16-character password below                  ║
        ╚══════════════════════════════════════════════════════════╝
        
        The email will be sent FROM your SENDER_EMAIL address
        TO the principal's email address entered during upload.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
        # ===== CONFIGURATION =====
        self.demo_mode = False              # Set to False to send real emails
        self.SENDER_EMAIL = "yourname@gmail.com"             # e.g. "yourname@gmail.com"
        self.SENDER_PASSWORD = "raarf abbz fccy eddb"          # Gmail App Password (16 chars, NOT your regular password)
        # ==========================
    
    def _build_html_template(self, paper_id, subject_code, timestamp, college_id):
        """Build a professional HTML email template"""
        upload_time = datetime.fromtimestamp(timestamp).strftime('%d %B %Y, %I:%M %p') if isinstance(timestamp, (int, float)) else str(timestamp)
        
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:0; background-color:#f4f4f7; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7; padding:40px 0;">
        <tr><td align="center">
            <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
                <tr><td style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); padding:30px 40px; text-align:center;">
                    <h1 style="color:#ffffff; margin:0; font-size:22px; font-weight:700;">🔗 Blockchain Exam Verification</h1>
                    <p style="color:rgba(255,255,255,0.8); margin:8px 0 0; font-size:14px;">Secure Exam Paper Notification</p>
                </td></tr>
                <tr><td style="padding:40px;">
                    <p style="color:#333; font-size:16px; margin:0 0 20px;">Dear Principal,</p>
                    <p style="color:#555; font-size:14px; line-height:1.7; margin:0 0 30px;">A new exam paper has been uploaded and securely stored on the Ethereum Blockchain. Below are the details:</p>
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9ff; border-radius:10px; border:1px solid #e8ebf5;">
                        <tr><td style="padding:24px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr><td style="padding:10px 0; border-bottom:1px solid #e8ebf5;">
                                    <span style="color:#888; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Paper ID</span><br>
                                    <span style="font-size:20px; font-weight:700; color:#667eea;">{paper_id}</span>
                                </td></tr>
                                <tr><td style="padding:10px 0; border-bottom:1px solid #e8ebf5;">
                                    <span style="color:#888; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Subject Code</span><br>
                                    <span style="color:#333; font-size:18px; font-weight:600;">{subject_code}</span>
                                </td></tr>
                                <tr><td style="padding:10px 0; border-bottom:1px solid #e8ebf5;">
                                    <span style="color:#888; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">Upload Timestamp</span><br>
                                    <span style="color:#333; font-size:15px; font-weight:500;">{upload_time}</span>
                                </td></tr>
                                <tr><td style="padding:10px 0;">
                                    <span style="color:#888; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:1px;">College ID</span><br>
                                    <span style="color:#333; font-size:15px; font-weight:500;">{college_id}</span>
                                </td></tr>
                            </table>
                        </td></tr>
                    </table>
                    <div style="margin-top:30px; padding:20px; background:#fffbeb; border-radius:8px; border-left:4px solid #f59e0b;">
                        <p style="color:#92400e; font-size:14px; font-weight:600; margin:0 0 8px;">📋 Next Steps:</p>
                        <ol style="color:#78350f; font-size:13px; line-height:1.8; margin:0; padding-left:18px;">
                            <li>Login to the <strong>GET Portal</strong> as Principal</li>
                            <li>Enter Paper ID: <strong>{paper_id}</strong></li>
                            <li>Upload the encrypted package file</li>
                            <li>The system will verify and decrypt the paper</li>
                        </ol>
                    </div>
                </td></tr>
                <tr><td style="background:#f8f9ff; padding:20px 40px; text-align:center; border-top:1px solid #e8ebf5;">
                    <p style="color:#aaa; font-size:11px; margin:0;">
                        This is an automated message from the Blockchain Exam Verification System.<br>
                        Secured with Ethereum · AES-256 · RSA-4096
                    </p>
                </td></tr>
            </table>
        </td></tr>
    </table>
</body>
</html>"""
    
    def send_encrypted_package(self, recipient_email, paper_id, college_id, subject_code, 
                               encrypted_pdf_path, principal_name="Principal"):
        """
        Send exam paper details to principal.
        
        In DEMO mode: Logs to terminal (no email sent)
        In PRODUCTION mode: Sends real email via Gmail SMTP
        
        FROM: self.SENDER_EMAIL (your configured Gmail)
        TO:   recipient_email (principal's email entered during upload)
        """
        try:
            current_timestamp = datetime.now().timestamp()
            
            if self.demo_mode:
                print(f"\n📧 [DEMO MODE] Email Notification")
                print(f"   From: {self.SENDER_EMAIL or '(not configured)'}")
                print(f"   To: {recipient_email}")
                print(f"   Subject: New Exam Paper Available - {subject_code}")
                print(f"   ─────────────────────────────────")
                print(f"   📄 Paper ID     : {paper_id}")
                print(f"   📚 Subject Code : {subject_code}")
                print(f"   🕐 Timestamp    : {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
                print(f"   🏫 College ID   : {college_id}")
                print(f"   ─────────────────────────────────")
                print(f"   ⚠️  Set demo_mode=False and configure Gmail to send real emails\n")
                
                return True, "Email sent successfully (demo mode)"
            
            # ===== PRODUCTION: Real email sending via Gmail =====
            if not self.SENDER_EMAIL or not self.SENDER_PASSWORD:
                print("❌ Email not configured! Set SENDER_EMAIL and SENDER_PASSWORD in email_service.py")
                return False, "Email credentials not configured"
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = f"📄 New Exam Paper Available - {subject_code} (Paper ID: {paper_id})"
            
            # Plain text fallback
            plain_body = f"""Dear {principal_name},

A new exam paper has been uploaded to the Blockchain.

Paper ID: {paper_id}
Subject Code: {subject_code}
Timestamp: {datetime.now().strftime('%d %B %Y, %I:%M %p')}
College ID: {college_id}

Please login to the GET Portal to verify and decrypt the paper.

Best regards,
University Examination Board"""
            
            html_body = self._build_html_template(paper_id, subject_code, current_timestamp, college_id)
            
            msg.attach(MIMEText(plain_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach encrypted package
            if os.path.exists(encrypted_pdf_path):
                with open(encrypted_pdf_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename=paper_{paper_id}.pdf'
                    )
                    msg.attach(part)
            
            # Connect to Gmail and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return True, "Email sent successfully"
            
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False, f"Failed to send email: {str(e)}"
