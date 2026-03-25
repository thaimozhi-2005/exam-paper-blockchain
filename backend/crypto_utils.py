"""
Crypto Utilities - AES-256 and RSA-4096 encryption/decryption
"""

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os

class CryptoUtils:
    
    @staticmethod
    def generate_rsa_keys(key_size=4096):
        """
        Generate RSA-4096 key pair
        Returns: (private_key_pem, public_key_pem)
        """
        key = RSA.generate(key_size)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key
    
    @staticmethod
    def save_rsa_keys(private_key, public_key, principal_id, keys_dir='keys'):
        """Save RSA keys to files"""
        os.makedirs(keys_dir, exist_ok=True)
        
        private_key_path = os.path.join(keys_dir, f'{principal_id}_private.pem')
        public_key_path = os.path.join(keys_dir, f'{principal_id}_public.pem')
        
        with open(private_key_path, 'wb') as f:
            f.write(private_key)
        
        with open(public_key_path, 'wb') as f:
            f.write(public_key)
        
        return private_key_path, public_key_path
    
    @staticmethod
    def load_rsa_public_key(public_key_path):
        """Load RSA public key from file"""
        with open(public_key_path, 'rb') as f:
            return RSA.import_key(f.read())
    
    @staticmethod
    def load_rsa_private_key(private_key_path):
        """Load RSA private key from file"""
        with open(private_key_path, 'rb') as f:
            return RSA.import_key(f.read())
    
    @staticmethod
    def encrypt_pdf_aes(pdf_data):
        """
        Encrypt PDF data using AES-256 CBC
        Returns: (encrypted_data, aes_key, iv)
        """
        # Generate random AES key (256-bit)
        aes_key = get_random_bytes(32)
        
        # Generate random IV (128-bit for AES)
        iv = get_random_bytes(16)
        
        # Create AES cipher
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        
        # Pad and encrypt data
        padded_data = pad(pdf_data, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        
        return encrypted_data, aes_key, iv
    
    @staticmethod
    def decrypt_pdf_aes(encrypted_data, aes_key, iv):
        """
        Decrypt PDF data using AES-256 CBC
        Returns: decrypted_data
        """
        # Create AES cipher
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        decrypted_padded = cipher.decrypt(encrypted_data)
        decrypted_data = unpad(decrypted_padded, AES.block_size)
        
        return decrypted_data
    
    @staticmethod
    def encrypt_aes_key_rsa(aes_key, public_key):
        """
        Encrypt AES key using RSA-4096 OAEP
        Returns: encrypted_aes_key (base64 encoded)
        """
        cipher_rsa = PKCS1_OAEP.new(public_key)
        encrypted_key = cipher_rsa.encrypt(aes_key)
        return base64.b64encode(encrypted_key).decode('utf-8')
    
    @staticmethod
    def decrypt_aes_key_rsa(encrypted_aes_key_b64, private_key):
        """
        Decrypt AES key using RSA-4096 OAEP
        Returns: aes_key
        """
        encrypted_key = base64.b64decode(encrypted_aes_key_b64)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        aes_key = cipher_rsa.decrypt(encrypted_key)
        return aes_key
    
    @staticmethod
    def create_encrypted_package(pdf_data, public_key):
        """
        Complete encryption workflow:
        1. Encrypt PDF with AES-256
        2. Encrypt AES key with RSA-4096
        Returns: (encrypted_pdf, encrypted_aes_key, iv)
        """
        # Encrypt PDF with AES
        encrypted_pdf, aes_key, iv = CryptoUtils.encrypt_pdf_aes(pdf_data)
        
        # Encrypt AES key with RSA
        encrypted_aes_key = CryptoUtils.encrypt_aes_key_rsa(aes_key, public_key)
        
        # Encode encrypted PDF and IV to base64 for storage
        encrypted_pdf_b64 = base64.b64encode(encrypted_pdf).decode('utf-8')
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        
        return encrypted_pdf_b64, encrypted_aes_key, iv_b64
    
    @staticmethod
    def decrypt_package(encrypted_pdf_b64, encrypted_aes_key_b64, iv_b64, private_key):
        """
        Complete decryption workflow for legacy JSON packages:
        1. Decrypt AES key with RSA-4096
        2. Decrypt PDF with AES-256
        Returns: decrypted_pdf_data
        """
        # Decode from base64
        encrypted_pdf = base64.b64decode(encrypted_pdf_b64)
        iv = base64.b64decode(iv_b64)
        
        # Decrypt AES key with RSA
        aes_key = CryptoUtils.decrypt_aes_key_rsa(encrypted_aes_key_b64, private_key)
        
        # Decrypt PDF with AES
        decrypted_pdf = CryptoUtils.decrypt_pdf_aes(encrypted_pdf, aes_key, iv)
        
        return decrypted_pdf

    @staticmethod
    def create_encrypted_file_package(pdf_data, public_key):
        """
        New Binary Overhaul:
        1. Encrypt PDF with AES-256
        2. Encrypt AES key with RSA-4096
        3. Pack into binary format: [IV(16 bytes)] + [RSA_KEY_LEN(2 bytes)] + [RSA_KEY] + [ENC_PDF]
        
        Returns: binary_blob, encrypted_aes_key_b64 (for blockchain)
        """
        # 1. AES Encrypt
        encrypted_pdf, aes_key, iv = CryptoUtils.encrypt_pdf_aes(pdf_data)
        
        # 2. RSA Encrypt AES Key
        cipher_rsa = PKCS1_OAEP.new(public_key)
        encrypted_rsa_key = cipher_rsa.encrypt(aes_key)
        
        # 3. Construct Binary Blob
        # RSA key length (usually 512 bytes for 4096-bit RSA)
        rsa_len = len(encrypted_rsa_key).to_bytes(2, byteorder='big')
        
        binary_blob = iv + rsa_len + encrypted_rsa_key + encrypted_pdf
        
        # Also return base64 RSA key for blockchain storage (as per existing smart contract)
        encrypted_aes_key_b64 = base64.b64encode(encrypted_rsa_key).decode('utf-8')
        
        return binary_blob, encrypted_aes_key_b64

    @staticmethod
    def parse_encrypted_file_package(binary_blob, private_key):
        """
        Extract and decrypt components from binary blob:
        Format: [IV(16)] + [RSA_LEN(2)] + [RSA_KEY] + [ENC_PDF]
        
        Returns: decrypted_pdf
        """
        # 1. Extract IV
        iv = binary_blob[:16]
        
        # 2. Extract RSA Key Length
        rsa_len = int.from_bytes(binary_blob[16:18], byteorder='big')
        
        # 3. Extract RSA Key
        encrypted_rsa_key = binary_blob[18:18+rsa_len]
        
        # 4. Extract Encrypted PDF
        encrypted_pdf = binary_blob[18+rsa_len:]
        
        # 5. Decrypt RSA Key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        aes_key = cipher_rsa.decrypt(encrypted_rsa_key)
        
        # 6. Decrypt PDF
        decrypted_pdf = CryptoUtils.decrypt_pdf_aes(encrypted_pdf, aes_key, iv)
        
        return decrypted_pdf
