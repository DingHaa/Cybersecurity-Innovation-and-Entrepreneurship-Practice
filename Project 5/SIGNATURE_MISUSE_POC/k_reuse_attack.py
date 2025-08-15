"""
Proof-of-Concept for SM2 Private Key Recovery via k-Reuse Attack.

This script demonstrates how reusing the random number 'k' in two different
SM2 signatures allows an attacker to recover the signer's private key.
"""

from random import randint
from gmpy2 import invert
from gmssl import sm3, func
from sm2_utils import N, G, scalar_mult

def hash_sm3(data_hex: str) -> str:
    """SM3 hash function wrapper."""
    data_bytes = bytes.fromhex(data_hex)
    data_list = func.bytes_to_list(data_bytes)
    return sm3.sm3_hash(data_list)

def faulty_sign(message_hex: str, private_key: int, k: int) -> tuple[int, int]:
    """
    A flawed SM2 signing function that uses a fixed 'k'.
    This simulates the vulnerability of k-reuse.
    """
    e = hash_sm3(message_hex)
    e_int = int(e, 16)
    
    k_g = scalar_mult(k, G)
    r = (e_int + k_g[0]) % N
    
    # This check is part of the standard, but we assume it passes for the PoC
    if r == 0 or r + k == N:
        raise ValueError("r or r+k is invalid, try another k")
        
    s = (invert(1 + private_key, N) * (k - r * private_key)) % N
    
    if s == 0:
        raise ValueError("s is zero, try another k")
        
    return r, s

def k_reuse_attack(sig1: tuple[int, int], sig2: tuple[int, int]) -> int:
    """
    Recovers the private key 'd' from two signatures that reused 'k'.
    
    Args:
        sig1: The first signature (r1, s1).
        sig2: The second signature (r2, s2).
        
    Returns:
        The recovered private key.
    """
    r1, s1 = sig1
    r2, s2 = sig2
    
    # d = (s1 - s2) * (s2 + r2 - s1 - r1)^-1 mod n
    numerator = (s1 - s2) % N
    denominator = (s2 + r2 - s1 - r1) % N
    
    # Calculate modular inverse
    inv_denominator = invert(denominator, N)
    
    # Recover the private key
    recovered_d = (numerator * inv_denominator) % N
    return recovered_d

def main():
    """Main function to demonstrate the k-reuse attack."""
    # --- Setup ---
    # A "secret" private key
    private_key_d = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    
    # The reused random number 'k'
    reused_k = randint(1, N - 1)
    
    # Two different messages
    msg1_text = "First message for k-reuse attack"
    msg2_text = "Second message for k-reuse attack"
    msg1_hex = msg1_text.encode().hex()
    msg2_hex = msg2_text.encode().hex()
    
    print("--- SM2 k-Reuse Attack PoC ---")
    print(f"Original Private Key (d): {private_key_d:x}")
    print(f"Reused Random Number (k): {reused_k:x}")
    print(f"Message 1: '{msg1_text}'")
    print(f"Message 2: '{msg2_text}'")
    print("-" * 40)
    
    # --- Simulate the Attack ---
    # 1. Generate two signatures with the same 'k'
    try:
        r1, s1 = faulty_sign(msg1_hex, private_key_d, reused_k)
        r2, s2 = faulty_sign(msg2_hex, private_key_d, reused_k)
        
        print(f"Signature 1 (r1, s1): ({r1:x}, {s1:x})")
        print(f"Signature 2 (r2, s2): ({r2:x}, {s2:x})")
        
    except ValueError as e:
        print(f"Signature generation failed: {e}")
        return
        
    # 2. Perform the attack to recover the private key
    recovered_private_key = k_reuse_attack((r1, s1), (r2, s2))
    
    print("-" * 40)
    print(f"Recovered Private Key: {recovered_private_key:x}")
    
    # --- Verification ---
    if recovered_private_key == private_key_d:
        print("\n✅ Attack Successful! The recovered private key matches the original.")
    else:
        print("\n❌ Attack Failed. The recovered key does not match.")
        
    assert recovered_private_key == private_key_d

if __name__ == "__main__":
    main()
