"""
Hash Utilities - SHA-256 hashing for document verification
"""

import hashlib

class HashUtils:
    
    @staticmethod
    def hash_file(file_data):
        """
        Generate SHA-256 hash of file data
        Returns: hex string of hash
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_data)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def hash_string(text):
        """
        Generate SHA-256 hash of string
        Returns: hex string of hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_hash(file_data, expected_hash):
        """
        Verify if file data matches expected hash
        Returns: True if match, False otherwise
        """
        actual_hash = HashUtils.hash_file(file_data)
        return actual_hash == expected_hash
    
    @staticmethod
    def generate_master_hash(page_hashes):
        """
        Generate master hash from list of page hashes
        This creates a hash chain for tamper detection
        Returns: master hash
        """
        combined = ''.join(page_hashes)
        return HashUtils.hash_string(combined)
