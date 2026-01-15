#!/usr/bin/env python3
"""
Test script for file encryption and decryption functionality.
"""

import os
import tempfile
from models.crypto_utils import encrypt_file_bytes, decrypt_file_bytes
from models.chiffrement_model import generer_matrice_inversible, matrice_en_base64

def test_file_encryption():
    # Create a test file
    test_content = b"This is a test file for encryption."
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Generate a key
        matrice = generer_matrice_inversible(5)
        encryption_key = matrice_en_base64(matrice)
        
        # Read the file content
        with open(temp_file_path, 'rb') as file:
            file_content = file.read()
        
        # Encrypt the file content
        encrypted_content = encrypt_file_bytes(file_content, encryption_key)
        print(f"Encrypted content: {encrypted_content[:50]}...")
        
        # Decrypt the file content
        decrypted_content = decrypt_file_bytes(encrypted_content, encryption_key)
        print(f"Decrypted content: {decrypted_content}")
        
        # Verify the content
        assert decrypted_content == test_content, "Decrypted content does not match original content!"
        print("Test passed: File encryption and decryption work correctly.")
        
    finally:
        # Clean up
        os.remove(temp_file_path)

if __name__ == "__main__":
    test_file_encryption()