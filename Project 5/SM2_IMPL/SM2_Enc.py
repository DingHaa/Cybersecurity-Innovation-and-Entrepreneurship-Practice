"""
SM2 Public Key Encryption and Decryption.

This script provides functions for encrypting and decrypting messages using the
SM2 public-key encryption standard. It relies on an underlying implementation
of elliptic curve arithmetic and the SM3 hash function.
"""

import math
from random import randint
from gmssl import sm3, func
from sm2_utils import P, N, G, A, B, scalar_mult, point_add, Point

def Hash(data_hex: str) -> str:
    """SM3 hash function wrapper that takes hex string and returns hex string."""
    # Convert hex string to bytes
    data_bytes = bytes.fromhex(data_hex)
    # Convert bytes to list for gmssl sm3
    data_list = func.bytes_to_list(data_bytes)
    # Compute SM3 hash
    return sm3.sm3_hash(data_list)

def kdf(z: str, klen: int) -> str:
    """
    Key Derivation Function (KDF) based on SM3 hash.
    Derives a key of `klen` bits from the input string `z`.
    """
    ct = 1
    key = ''
    v = 256  # Hash output length for SM3

    for i in range(math.ceil(klen / v)):
        # In Python, string formatting with binary doesn't need explicit padding
        # as we can directly work with hex strings.
        h_input = z + f'{ct:08x}' # SM3 expects hex input
        key += Hash(h_input)
        ct += 1
    
    # The Hash function should return a hex string.
    # We need to ensure the final key has the correct bit length.
    key_bin = bin(int(key, 16))[2:].zfill(len(key) * 4)
    return key_bin[:klen]


def encrypt(message: str, public_key: Point) -> tuple[str, str, str]:
    """
    Encrypts a message using SM2 public-key encryption.

    Args:
        message (str): The plaintext message to encrypt.
        public_key (Point): The recipient's public key.

    Returns:
        A tuple (C1, C2, C3) where:
        - C1 is the ephemeral public key point (hex encoded).
        - C2 is the ciphertext (hex encoded).
        - C3 is the MAC tag (hex encoded).
    """
    msg_bytes = message.encode('utf-8')
    msg_hex = msg_bytes.hex()
    klen = len(msg_hex) * 4

    while True:
        k = randint(1, N - 1)
        
        # C1 = k * G
        c1_point = scalar_mult(k, G)
        c1_hex = f'{c1_point[0]:064x}{c1_point[1]:064x}'

        # S = h * PB, where h is the cofactor (assumed to be 1)
        # For SM2, if S is the point at infinity, we must restart.
        s_point = scalar_mult(k, public_key)
        if s_point is None:
            continue

        # t = KDF(x2 || y2, klen)
        x2_hex = f'{s_point[0]:064x}'
        y2_hex = f'{s_point[1]:064x}'
        t_bin = kdf(x2_hex + y2_hex, klen)
        
        # C2 = M xor t
        c2_int = int(msg_hex, 16) ^ int(t_bin, 2)
        c2_hex = f'{c2_int:0{klen//4}x}'

        # C3 = Hash(x2 || M || y2)
        c3_input = x2_hex + msg_hex + y2_hex
        c3_hex = Hash(c3_input)
        
        return c1_hex, c2_hex, c3_hex


def decrypt(c1_hex: str, c2_hex: str, c3_hex: str, private_key: int) -> str | None:
    """
    Decrypts an SM2-encrypted message.

    Args:
        c1_hex (str): The ephemeral public key point (hex encoded).
        c2_hex (str): The ciphertext (hex encoded).
        c3_hex (str): The MAC tag (hex encoded).
        private_key (int): The recipient's private key.

    Returns:
        The decrypted plaintext message, or None if decryption fails.
    """
    c1_x = int(c1_hex[:64], 16)
    c1_y = int(c1_hex[64:], 16)
    c1_point = (c1_x, c1_y)

    # Verify C1 is on the curve
    # y^2 = x^3 + ax + b
    if pow(c1_y, 2, P) != (pow(c1_x, 3, P) + A * c1_x + B) % P:
        print("Error: C1 is not on the curve.")
        return None

    # S = h * C1, where h is the cofactor (assumed to be 1)
    s_point = scalar_mult(private_key, c1_point)
    if s_point is None:
        print("Error: S is the point at infinity.")
        return None

    # t = KDF(x2 || y2, klen)
    klen = len(c2_hex) * 4
    x2_hex = f'{s_point[0]:064x}'
    y2_hex = f'{s_point[1]:064x}'
    t_bin = kdf(x2_hex + y2_hex, klen)

    # M' = C2 xor t
    m_prime_int = int(c2_hex, 16) ^ int(t_bin, 2)
    m_prime_hex = f'{m_prime_int:0{klen//4}x}'

    # C3' = Hash(x2 || M' || y2)
    c3_prime_input = x2_hex + m_prime_hex + y2_hex
    c3_prime_hex = Hash(c3_prime_input)

    if c3_prime_hex.lower() != c3_hex.lower():
        print("Error: MAC verification failed.")
        return None

    # Convert hex message back to string
    return bytes.fromhex(m_prime_hex).decode('utf-8')

def main():
    """Main function to demonstrate SM2 encryption and decryption."""
    # --- Key Setup ---
    # Use the same curve parameters as SM2_Sign
    from sm2_utils import N, G, scalar_mult
    
    private_key_db = 0x58892B807074F53FBF67288A1DFAA1AC313455FE60355AFD
    public_key_pb = scalar_mult(private_key_db, G)
    
    message = "d1ngH"

    print("--- SM2 Encryption ---")
    print(f"Original Message: {message}")
    print(f"Recipient Public Key (PB): ({public_key_pb[0]:x}, {public_key_pb[1]:x})")

    # --- Encryption ---
    c1, c2, c3 = encrypt(message, public_key_pb)
    print("\nEncrypted Components:")
    print(f"C1: {c1}")
    print(f"C2: {c2}")
    print(f"C3: {c3}")

    # --- Decryption ---
    print("\n--- SM2 Decryption ---")
    decrypted_message = decrypt(c1, c2, c3, private_key_db)

    if decrypted_message:
        print(f"Decrypted Message: {decrypted_message}")
        assert message == decrypted_message
        print("✅ Decryption successful and message matches original.")
    else:
        print("❌ Decryption failed.")

if __name__ == "__main__":
    main()
