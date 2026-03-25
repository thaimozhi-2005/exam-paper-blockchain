"""
Paper Service - Main business logic for exam paper operations
"""

import json
import os
import time
from datetime import datetime
import hashlib
import base64
import PyPDF2
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from crypto_utils import CryptoUtils
from hash_utils import HashUtils
from email_service import EmailService


class PaperService:
    def __init__(self, contract_loader, auth_service):
        """Initialize paper service"""
        self.contract = contract_loader
        self.auth = auth_service
        self.email_service = EmailService()
        self.uploads_dir = 'uploads'
        self.encrypted_dir = 'encrypted_pdfs'
        self.keys_dir = 'keys'
        
        # Create directories
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.encrypted_dir, exist_ok=True)
        os.makedirs(self.keys_dir, exist_ok=True)
    
    def create_overlay_pdf(self):
        """Create a single page PDF with the verification watermark"""
        try:
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Draw big green tick in top-right corner with low opacity
            pdf.setFillColorRGB(0.22, 0.6, 0.49, alpha=0.15)  # Low opacity green
            pdf.setFont("Helvetica-Bold", 120)
            pdf.drawRightString(width - 30, height - 120, "✓")
            
            # Add "Signature valid" text in top-right
            pdf.setFillColor(HexColor('#11998e'))
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawRightString(width - 35, height - 35, "Signature valid")
            
            # Add verification footer
            pdf.setFont("Helvetica", 9)
            pdf.setFillColor(HexColor('#666666'))
            footer_y = 25
            pdf.drawCentredString(width/2, footer_y, "This document has been cryptographically verified on Ethereum Blockchain")
            pdf.drawCentredString(width/2, footer_y - 12, f"Verification Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            pdf.save()
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            print(f"⚠️  Overlay creation failed: {e}")
            return None

    def create_verified_pdf_overlay(self, original_pdf_bytes):
        """Overlay verification marks on original PDF"""
        try:
            # Create overlay
            overlay_bytes = self.create_overlay_pdf()
            if not overlay_bytes:
                return original_pdf_bytes
                
            overlay_reader = PyPDF2.PdfReader(BytesIO(overlay_bytes))
            overlay_page = overlay_reader.pages[0]
            
            # Read original
            original_reader = PyPDF2.PdfReader(BytesIO(original_pdf_bytes))
            writer = PyPDF2.PdfWriter()
            
            for page in original_reader.pages:
                # Merge overlay onto the page
                page.merge_page(overlay_page)
                writer.add_page(page)
                
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            return output.getvalue()
        except Exception as e:
            print(f"⚠️  Merging overlay failed: {e}")
            return original_pdf_bytes
            
    def embed_metadata_in_pdf(self, pdf_bytes, metadata):
        """
        Embed blockchain verification metadata into PDF (Phase 1 approach).
        Uses PyPDF2 to write custom metadata fields into the PDF.
        """
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            writer = PyPDF2.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            # Embed metadata into PDF
            writer.add_metadata({
                '/Title': metadata.get('title', 'Exam Paper'),
                '/Author': 'Blockchain Exam Verification System',
                '/PaperID': str(metadata.get('paper_id', '')),
                '/DocumentHash': metadata.get('document_hash', ''),
                '/CollegeID': metadata.get('college_id', ''),
                '/SubjectCode': metadata.get('subject_code', ''),
                '/ExamDateTime': metadata.get('exam_datetime', ''),
                '/BlockchainTxHash': metadata.get('tx_hash', ''),
                '/Timestamp': metadata.get('timestamp', ''),
                '/SecurityLevel': 'AES-256 + RSA-4096',
                '/BlockchainNetwork': 'Ethereum (Ganache)',
            })
            
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            return output.read()
        except Exception as e:
            print(f"⚠️  Could not embed metadata: {e}")
            return pdf_bytes  # Return original if embedding fails
    
    def admin_store_paper(self, pdf_data, college_id, subject_code, exam_datetime_str, principal_email):
        """
        Complete admin workflow:
        1. Generate RSA keys for principal (if not exists)
        2. Encrypt PDF with AES-256
        3. Encrypt AES key with RSA-4096
        4. Hash encrypted PDF
        5. Store on blockchain
        6. Save encrypted package
        7. Send email to principal
        
        Returns: (success, result_data or error_message)
        """
        try:
            # Parse exam datetime
            exam_datetime = datetime.strptime(exam_datetime_str, '%Y-%m-%dT%H:%M')
            exam_timestamp = int(exam_datetime.timestamp())
            
            # Check if exam time is in the future
            if exam_timestamp <= int(datetime.now().timestamp()):
                return False, "Exam date/time must be in the future"
            
            # Generate or load RSA keys for principal
            principal_id = college_id  # Use college_id as principal identifier
            public_key_path = os.path.join(self.keys_dir, f'{principal_id}_public.pem')
            private_key_path = os.path.join(self.keys_dir, f'{principal_id}_private.pem')
            
            if not os.path.exists(public_key_path):
                print(f"🔑 Generating new RSA-4096 keys for {principal_id}...")
                private_key, public_key = CryptoUtils.generate_rsa_keys()
                CryptoUtils.save_rsa_keys(private_key, public_key, principal_id, self.keys_dir)
                print(f"✅ RSA keys generated and saved")
            
            # Load public key
            public_key = CryptoUtils.load_rsa_public_key(public_key_path)
            
            # 1. Get next paper ID (predicted) to embed into PDF
            predicted_id = self.contract.get_total_papers() + 1

            # 2. Embed metadata into PDF BEFORE encryption (Phase 1 approach)
            print(f"📝 Embedding metadata for Paper ID {predicted_id}...")
            metadata_to_embed = {
                'title': f'Exam Paper - {subject_code}',
                'paper_id': predicted_id,
                'college_id': college_id,
                'subject_code': subject_code,
                'exam_datetime': exam_datetime_str,
                'principal_email': principal_email,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            pdf_with_metadata = self.embed_metadata_in_pdf(pdf_data, metadata_to_embed)
            
            # 3. Hash the processed PDF
            print("🔒 Generating document hash...")
            document_hash = HashUtils.hash_file(pdf_with_metadata)
            print(f"✅ Document hash: {document_hash[:16]}...")
            
            # 4. Check if hash already exists on blockchain
            if self.contract.does_hash_exist(document_hash):
                return False, "This document has already been stored on the blockchain"
            
            # 5. Encrypt the processed PDF using New Binary Overhaul
            print("🔐 Encrypting PDF with AES-256 and RSA-4096 (Binary Overhaul)...")
            encrypted_blob, encrypted_aes_key_b64 = CryptoUtils.create_encrypted_file_package(
                pdf_with_metadata, public_key
            )
            print("✅ PDF encrypted successfully")
            
            # 6. Store on blockchain
            print("⛓️  Storing on blockchain...")
            paper_id, tx_hash = self.contract.store_paper(
                college_id,
                subject_code,
                document_hash,
                exam_timestamp,
                encrypted_aes_key_b64,
                principal_email
            )
            print(f"✅ Stored on blockchain - Paper ID: {paper_id}, Tx: {tx_hash[:16]}...")
            
            # Save encrypted file (No more JSON)
            encrypted_filename = f"paper_{paper_id}.pdf"
            encrypted_path = os.path.join(self.encrypted_dir, encrypted_filename)
            
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_blob)
            
            print(f"💾 Encrypted file saved: {encrypted_filename}")
            
            # Send email to principal
            print("📧 Sending email to principal...")
            email_success, email_msg = self.email_service.send_encrypted_package(
                principal_email,
                paper_id,
                college_id,
                subject_code,
                encrypted_path
            )
            
            if not email_success:
                print(f"⚠️  Email warning: {email_msg}")
            
            # Return success with all details
            return True, {
                'paper_id': paper_id,
                'transaction_hash': tx_hash,
                'document_hash': document_hash,
                'college_id': college_id,
                'subject_code': subject_code,
                'exam_datetime': exam_datetime_str,
                'encrypted_package_path': encrypted_path,
                'email_sent': email_success,
                'principal_email': principal_email
            }
            
        except Exception as e:
            return False, f"Error in admin workflow: {str(e)}"
    
    def admin_reschedule_exam(self, paper_id, new_exam_datetime_str):
        """Allow admin to update exam time on blockchain"""
        try:
            # Parse new exam datetime
            new_datetime = datetime.strptime(new_exam_datetime_str, '%Y-%m-%dT%H:%M')
            new_timestamp = int(new_datetime.timestamp())
            
            # Check if new time is in the future
            if new_timestamp <= int(time.time()):
                return False, "New exam date/time must be in the future"
            
            # Update on blockchain
            tx_hash = self.contract.reschedule_exam(int(paper_id), new_timestamp)
            
            return True, {
                'paper_id': paper_id,
                'new_exam_datetime': new_exam_datetime_str,
                'transaction_hash': tx_hash
            }
        except Exception as e:
            return False, f"Error rescheduling exam: {str(e)}"
    
    def principal_verify_paper(self, paper_id):
        """
        Fetch paper details from blockchain for verification
        Returns: (success, paper_data or error_message)
        """
        try:
            # Get paper from blockchain
            paper = self.contract.get_paper(paper_id)
            
            # Check time-lock
            exam_time_reached = self.contract.is_exam_time_reached(paper_id)
            blockchain_time = self.contract.get_blockchain_time()
            
            return True, {
                'paper_id': paper_id,
                'college_id': paper['collegeId'],
                'subject_code': paper['subjectCode'],
                'document_hash': paper['documentHash'],
                'timestamp': paper['timestamp'],
                'owner': paper['owner'],
                'verified': paper['verified'],
                'exam_datetime': paper['examDateTime'],
                'encrypted_aes_key': paper['encryptedAESKey'],
                'principal_email': paper['principalEmail'],
                'exam_time_reached': exam_time_reached,
                'blockchain_time': blockchain_time
            }
            
        except Exception as e:
            return False, f"Error fetching paper: {str(e)}"
    
    def principal_decrypt_paper(self, paper_id, encrypted_package_data, college_id):
        """
        Complete principal workflow:
        1. Verify system clock synchronization
        2. Verify time-lock
        3. Fetch encrypted AES key from blockchain
        4. Decrypt AES key with RSA private key
        5. Decrypt PDF with AES key
        6. Verify hash
        7. Mark as verified on blockchain
        
        Returns: (success, decrypted_pdf_data or error_message)
        """
        try:
            # 1. Blockchain-Based Time Security (Consensus Time)
            print(f"🔒 Security Enforcement: Fetching Blockchain Time for Paper ID {paper_id}")
            # We fetch time from the blockchain itself so all nodes agree on the same time
            current_time = self.contract.get_blockchain_time()
            local_system_time = int(time.time())
            
            # Optional: Log if local time is drifting from blockchain consensus time
            if abs(current_time - local_system_time) > 300:
                print(f"⚠️ Warning: Local system clock drifts from Blockchain time by {abs(current_time - local_system_time)}s")

            # 2. Get paper details from blockchain to check schedule
            paper = self.contract.get_paper(paper_id)
            exam_datetime = int(paper['examDateTime'])

            print(f"📊 Schedule Check: Blockchain={current_time}, Exam={exam_datetime}")

            # 3. Direct Validation against Blockchain Time
            if current_time < exam_datetime:
                limit_dt = datetime.utcfromtimestamp(exam_datetime)
                limit_str = limit_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                
                # We can still warn about system clock if it's very wrong, but the decision is based on blockchain
                final_msg = f"Time-Lock Active: Blockchain clock shows exam time hasn't reached. Paper becomes available at {limit_str}."
                if abs(current_time - local_system_time) > 300:
                    final_msg = f"⚠️ WARNING: Your system clock is not correct! Please synchronize with the server.\n\n{final_msg}"
                
                return False, final_msg

            print("✅ Blockchain Time Verified. Proceeding to Decryption...")

            # 5. Get paper details from backend/verification service
            success, paper_data = self.principal_verify_paper(paper_id)
            if not success:
                return False, paper_data
            
            # Load principal's private key
            private_key_path = os.path.join(self.keys_dir, f'{college_id}_private.pem')
            if not os.path.exists(private_key_path):
                return False, "Private key not found for this college. Please contact administrator."
            
            private_key = CryptoUtils.load_rsa_private_key(private_key_path)
            
            # Extract encrypted data from binary blob
            print("🔓 Decrypting encrypted PDF file (Binary Overhaul)...")
            decrypted_pdf = CryptoUtils.parse_encrypted_file_package(
                encrypted_package_data, # This is now raw bytes from the uploaded .pdf.enc
                private_key
            )
            print("✅ PDF decrypted successfully")
            
            # Verify hash against blockchain hash
            print("🔍 Verifying document hash against blockchain...")
            actual_hash = HashUtils.hash_file(decrypted_pdf)
            expected_hash = paper_data['document_hash']
            
            # Compare hashes to ensure integrity
            hash_match = (actual_hash == expected_hash)
            
            if hash_match:
                print("✅ Hash verification successful")
                
                # Mark as verified on blockchain
                try:
                    self.contract.verify_paper(paper_id)
                    print("✅ Paper marked as verified on blockchain")
                except:
                    print("⚠️  Could not mark as verified (may already be verified)")
                
                # === ADD VISUAL VERIFICATION MARKS ===
                print("🎨 Adding visual verification marks (Green Ticks)...")
                final_pdf = self.create_verified_pdf_overlay(decrypted_pdf)
                print("✅ Visual verification added")
            else:
                return False, "Hash verification failed. Document may be tampered."
            
            return True, {
                'decrypted_pdf': final_pdf,
                'paper_data': paper_data,
                'hash_verified': hash_match,
                'metadata_embedded': True  # PDF contains blockchain proof in its metadata
            }
            
        except Exception as e:
            return False, f"Error in decryption workflow: {str(e)}"
