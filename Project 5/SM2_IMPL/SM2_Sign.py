"""
SM2 Digital Signature Generation and Verification.

This script demonstrates the SM2 digital signature algorithm. It includes:
1.  Key generation (using a predefined private key).
2.  Calculation of Z_A, the hash of the user's identity and public key.
3.  Signature generation for a given message.
4.  Signature verification.
"""

import binascii
from random import randint
from gmpy2 import invert
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

def get_za(id_a: str, pa: Point) -> str:
    """
    Calculate the Z_A value, which is a hash of the user's identity and
    the public key, as defined in the SM2 standard.
    """
    id_a_hex = id_a.encode().hex()
    entl_a = f'{len(id_a_hex) * 4:04x}'
    
    a_hex = f'{A:064x}'
    b_hex = f'{B:064x}'
    gx_hex = f'{G[0]:064x}'
    gy_hex = f'{G[1]:064x}'
    pax_hex = f'{pa[0]:064x}'
    pay_hex = f'{pa[1]:064x}'

    m1 = (entl_a + id_a_hex + a_hex + b_hex + gx_hex + gy_hex + pax_hex + pay_hex).upper()
    za = Hash(m1)
    return za

def sign(message: str, za: str, private_key: int) -> tuple[str, str]:
    """
    Generates an SM2 signature for a message.

    Args:
        message (str): The message to be signed (in hex format).
        za (str): The pre-calculated Z_A value (in hex format).
        private_key (int): The signer's private key.

    Returns:
        A tuple (r, s) representing the signature.
    """
    m_prime = za + message
    e = Hash(m_prime)
    e_int = int(e, 16)

    while True:
        k = randint(1, N - 1)
        k_g = scalar_mult(k, G)
        
        r = (e_int + k_g[0]) % N
        if r == 0 or r + k == N:
            continue

        s = (invert(1 + private_key, N) * (k - r * private_key)) % N
        if s != 0:
            break
            
    return f'{r:x}', f'{s:x}'

def verify(message: str, za: str, public_key: Point, r_hex: str, s_hex: str) -> bool:
    """
    Verifies an SM2 signature.

    Args:
        message (str): The message that was signed (in hex format).
        za (str): The pre-calculated Z_A value (in hex format).
        public_key (Point): The signer's public key.
        r_hex (str): The 'r' component of the signature.
        s_hex (str): The 's' component of the signature.

    Returns:
        True if the signature is valid, False otherwise.
    """
    r = int(r_hex, 16)
    s = int(s_hex, 16)

    if not (1 <= r < N and 1 <= s < N):
        return False

    m_prime = za + message
    e = Hash(m_prime)
    e_int = int(e, 16)

    t = (r + s) % N
    if t == 0:
        return False

    p1 = scalar_mult(s, G)
    p2 = scalar_mult(t, public_key)
    x1, y1 = point_add(p1, p2)

    r_prime = (e_int + x1) % N
    return r == r_prime

def main():
    """Main function to demonstrate SM2 signing and verification."""
    # --- Key and Identity Setup ---
    private_key_da = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    public_key_pa = scalar_mult(private_key_da, G)
    
    user_id = "d1ngHd1ngH"
    message_text = "d1ngH"
    message_hex = message_text.encode().hex()

    print("--- SM2 Signature ---")
    print(f"User ID: {user_id}")
    print(f"Message: '{message_text}'")
    print(f"Private Key (DA): {private_key_da:x}")
    print(f"Public Key (PA): ({public_key_pa[0]:x}, {public_key_pa[1]:x})")

    # --- Signing Process ---
    za_hex = get_za(user_id, public_key_pa)
    print(f"\nZ_A: {za_hex}")

    r_val, s_val = sign(message_hex, za_hex, private_key_da)
    print(f"Signature (r, s): ({r_val}, {s_val})")

    # --- Verification Process ---
    is_valid = verify(message_hex, za_hex, public_key_pa, r_val, s_val)
    print(f"\nVerification Result: {'Success' if is_valid else 'Failure'}")
    assert is_valid
    print("✅ Signature is valid.")

if __name__ == "__main__":
    main()