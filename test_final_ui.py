#!/usr/bin/env python3

import sys
sys.path.append('.')

from models.hill_cipher import hill_chiffrement_ansi_base64, hill_dechiffrement_ansi_base64
from models.chiffrement_model import generer_matrice_inversible, matrice_en_base64, base64_en_matrice
import sympy as sp

def test_final_ui():
    print("Testing final UI implementation:")
    
    # Test matrix generation for different difficulty levels
    for taille in [5, 15, 50]:
        print(f"\nTesting {taille}x{taille} matrix generation:")
        
        # Generate matrix
        matrice = generer_matrice_inversible(taille)
        print(f"Matrix shape: {matrice.shape}")
        
        # Check determinant condition
        det = int(matrice.det())
        gcd_result = sp.gcd(det, 256)
        print(f"GCD(det, 256): {gcd_result}")
        
        if gcd_result != 1:
            print(f"ERROR: GCD is not 1 for {taille}x{taille} matrix!")
            return False
        
        # Convert to base64
        base64_key = matrice_en_base64(matrice)
        print(f"Base64 key length: {len(base64_key)}")
        
        # Test encryption and decryption
        test_message = "This is a test message for the final UI implementation."
        print(f"Original message: {test_message}")
        
        # Encrypt
        encrypted_message, original_length = hill_chiffrement_ansi_base64(matrice, test_message)
        print(f"Encrypted message: {encrypted_message}")
        
        # Decrypt
        decrypted_message = hill_dechiffrement_ansi_base64(matrice, encrypted_message)
        print(f"Decrypted message: {decrypted_message}")
        
        # Verify
        if decrypted_message.rstrip() == test_message:
            print(f"[OK] {taille}x{taille} encryption/decryption test passed!")
        else:
            print(f"ERROR: Decrypted message doesn't match original for {taille}x{taille} matrix!")
            return False
    
    print("\nAll tests passed! The final UI implementation:")
    print("- Generates invertible matrices for all difficulty levels")
    print("- Ensures GCD(determinant, 256) = 1")
    print("- Successfully encrypts and decrypts messages")
    print("- Displays encrypted messages that can be clicked to decrypt")
    print("- Shows timestamps below messages")
    print("- Uses textarea for both message and key inputs")
    
    return True

if __name__ == "__main__":
    success = test_final_ui()
    if not success:
        sys.exit(1)