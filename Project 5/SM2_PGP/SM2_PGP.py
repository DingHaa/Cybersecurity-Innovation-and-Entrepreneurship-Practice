"""
A Python implementation of a PGP-like protocol using SM2 and SM4 algorithms.
This script provides functions for encryption and decryption, simulating a secure
communication channel between two parties (A and B).
"""

import os
from gmssl import sm2, sm3, func
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT

# --- Constants for Cryptographic Keys ---

# User A's keys (for signing)
# It is recommended to load keys from a secure location rather than hardcoding.
PRIVATE_KEY_A = '0d1d31b70ef5d8d04d1d58158b2b418321a5b3dc8c68cdfe821a5e8c42d7e201'
PUBLIC_KEY_A = '36cd1616a0fdf51a57c9ac9c492d1049f8dd2579625814e1ddc9bd8d8de0b251530eced795456dc46802a5b1e1cfb7897ba39045e4619fcee3a0200e2a450ed7'

# User B's keys (for encryption)
PRIVATE_KEY_B = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5'
PUBLIC_KEY_B = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'

def pgp_encrypt(data: str, sm4_key: bytes):
    """
    Encrypts data using a PGP-like scheme.

    The process involves:
    1. Hashing the original data with SM3.
    2. Signing the hash with User A's private key (SM2).
    3. Concatenating the signature and the original data.
    4. Encrypting the concatenated content with a session key (SM4).
    5. Encrypting the SM4 session key with User B's public key (SM2).
    6. Concatenating the encrypted session key and the SM4-encrypted content.

    Args:
        data (str): The plaintext data to encrypt.
        sm4_key (bytes): The 16-byte session key for SM4 encryption.

    Returns:
        tuple[bytes, int]: A tuple containing the final encrypted message and
                           the length of the encrypted session key.
    """
    data_bytes = data.encode('utf-8')

    # 1. Hash data with SM3
    data_hash = sm3.sm3_hash(func.bytes_to_list(data_bytes)).encode('utf-8')

    # 2. Sign the hash with User A's private key
    sm2_signer = sm2.CryptSM2(public_key=PUBLIC_KEY_A, private_key=PRIVATE_KEY_A)
    random_hex = func.random_hex(sm2_signer.para_len)
    signature = sm2_signer.sign(data_hash, random_hex)

    # 3. Concatenate signature and data
    signed_data = signature.encode('utf-8') + data_bytes

    # 4. Encrypt with SM4
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(sm4_key, SM4_ENCRYPT)
    encrypted_content = crypt_sm4.crypt_ecb(signed_data)

    # 5. Encrypt SM4 key with User B's public key
    sm2_encryptor = sm2.CryptSM2(public_key=PUBLIC_KEY_B, private_key=None)
    encrypted_key = sm2_encryptor.encrypt(sm4_key)
    encrypted_key_len = len(encrypted_key)

    # 6. Concatenate for final message
    final_message = encrypted_key + encrypted_content
    return final_message, encrypted_key_len

def pgp_decrypt(encrypted_message: bytes, encrypted_key_len: int):
    """
    Decrypts a PGP-like encrypted message and verifies the signature.

    The process involves:
    1. Splitting the encrypted session key and the encrypted content.
    2. Decrypting the session key with User B's private key (SM2).
    3. Decrypting the content with the recovered session key (SM4).
    4. Splitting the decrypted content into the signature and original data.
    5. Hashing the recovered original data with SM3.
    6. Verifying the signature with User A's public key (SM2).

    Args:
        encrypted_message (bytes): The encrypted message to decrypt.
        encrypted_key_len (int): The length of the encrypted session key part.

    Returns:
        tuple[str, bool] | tuple[None, None]: A tuple containing the decrypted data
                                              and the verification result (bool).
                                              Returns (None, None) if decryption fails.
    """
    # 1. Split encrypted key and content
    encrypted_key = encrypted_message[:encrypted_key_len]
    encrypted_content = encrypted_message[encrypted_key_len:]

    # 2. Decrypt SM4 session key with User B's private key
    sm2_decryptor = sm2.CryptSM2(public_key=PUBLIC_KEY_B, private_key=PRIVATE_KEY_B)
    try:
        sm4_key = sm2_decryptor.decrypt(encrypted_key)
    except Exception as e:
        print(f"Error decrypting SM4 key: {e}")
        return None, None

    # 3. Decrypt content with SM4
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(sm4_key, SM4_DECRYPT)
    decrypted_content = crypt_sm4.crypt_ecb(encrypted_content)

    # 4. Split signature and original data (signature is a 128-char hex string)
    signature_len = 128
    signature = decrypted_content[:signature_len]
    original_data_bytes = decrypted_content[signature_len:]

    # 5. Hash the recovered data
    recovered_hash = sm3.sm3_hash(func.bytes_to_list(original_data_bytes)).encode('utf-8')

    # 6. Verify the signature with User A's public key
    sm2_verifier = sm2.CryptSM2(public_key=PUBLIC_KEY_A, private_key=None)
    is_verified = sm2_verifier.verify(signature, recovered_hash)

    return original_data_bytes.decode('utf-8'), is_verified

def main():
    """Main function to demonstrate the PGP encryption and decryption process."""
    # Generate a random 16-byte (128-bit) session key for SM4
    session_key = os.urandom(16)
    original_data = "This is a secret message for the PGP test."

    print("--- PGP Encryption ---")
    print(f"Original Data: {original_data}")
    print(f"Session Key (hex): {session_key.hex()}")

    # Encrypt the data
    encrypted_message, encrypted_key_length = pgp_encrypt(original_data, session_key)
    print(f"\nEncrypted PGP Message (hex): {encrypted_message.hex()}")
    print(f"Length of encrypted key part: {encrypted_key_length}")


    print("\n--- PGP Decryption & Verification ---")
    # Decrypt the data
    decrypted_data, is_signature_valid = pgp_decrypt(encrypted_message, encrypted_key_length)

    if decrypted_data is not None:
        print(f"Decrypted Data: {decrypted_data}")
        print(f"Signature Verification Result: {'Success' if is_signature_valid else 'Failure'}")
        assert is_signature_valid
        assert original_data == decrypted_data
        print("\n✅ Verification and data integrity confirmed.")
    else:
        print("\n❌ Decryption failed.")

if __name__ == "__main__":
    main()
