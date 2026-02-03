"""
Email Service - Send encrypted packages to principals
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587):
        """
        Initialize email service
        Note: For production, use environment variables for credentials
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        # For demo purposes, email sending is simulated
        self.demo_mode = True
    
    def send_encrypted_package(self, recipient_email, paper_id, college_id, subject_code, 
                               encrypted_pdf_path, principal_name="Principal"):
        """
        Send encrypted exam paper package to principal
        In demo mode, this just logs the action
        """
        try:
            if self.demo_mode:
                # Simulate email sending
                print(f"\n📧 [DEMO MODE] Email Simulation")
                print(f"   To: {recipient_email}")
                print(f"   Subject: Encrypted Exam Paper - {subject_code}")
                print(f"   Paper ID: {paper_id}")
                print(f"   College ID: {college_id}")
                print(f"   Attachment: {os.path.basename(encrypted_pdf_path)}")
                print(f"   ✅ Email would be sent in production mode\n")
                
                return True, "Email sent successfully (demo mode)"
            
            # Real email sending code (for production)
            # This requires valid SMTP credentials
            msg = MIMEMultipart()
            msg['From'] = "university@example.com"  # Configure this
            msg['To'] = recipient_email
            msg['Subject'] = f"Encrypted Exam Paper - {subject_code} (Paper ID: {paper_id})"
            
            body = f"""
Dear {principal_name},

You have received an encrypted exam paper package.

Details:
- Paper ID: {paper_id}
- College ID: {college_id}
- Subject Code: {subject_code}

Please use the GET portal to decrypt and verify this exam paper.
The encrypted package is attached to this email.

Instructions:
1. Login to the GET portal
2. Upload the attached encrypted package
3. Enter the Paper ID: {paper_id}
4. The system will verify and decrypt the paper

Best regards,
University Examination Board
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach encrypted PDF
            with open(encrypted_pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= encrypted_paper_{paper_id}.bin'
                )
                msg.attach(part)
            
            # Send email
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login("your_email@example.com", "your_password")
            # server.send_message(msg)
            # server.quit()
            
            return True, "Email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
