"""
Proof-of-Concept: Forging a Bitcoin Signature from a Leaked 'k'.

This script demonstrates how to forge a signature from Satoshi Nakamoto by
recovering the private key from a known public key, a historical signature,
and a hypothetically leaked random number 'k'.

Disclaimer: This is for educational purposes only to highlight the security
implications of 'k' reuse in ECDSA.
"""

import hashlib
from gmpy2 import invert

# --- Bitcoin's secp256k1 Elliptic Curve Parameters ---
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)

# --- Test data for demonstration ---
# We'll create a consistent set of test data where we know the private key
# and can verify our attack works correctly

# Let's use a known private key for testing
TEST_PRIVATE_KEY = 0x1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF

# Calculate the corresponding public key
def calculate_public_key(private_key):
    return scalar_mult(private_key, G)

# Test message and its hash
TEST_MESSAGE = "This is a test message for signature forgery"
Z = int.from_bytes(hashlib.sha256(TEST_MESSAGE.encode()).digest(), 'big')

# Known random number k for testing
LEAKED_K = 0x9E56F205A471157523109AA203764A4D5985C3B425644550612024C0C0744A45

# We'll generate a proper signature using this k and private key

def point_add(p1, p2):
    """Elliptic curve point addition."""
    if p1 is None: return p2
    if p2 is None: return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and y1 != y2: return None
    if x1 == x2:
        m = (3 * x1 * x1 + A) * invert(2 * y1, P)
    else:
        m = (y2 - y1) * invert(x2 - x1, P)
    x3 = m * m - x1 - x2
    y3 = m * (x1 - x3) - y1
    return (x3 % P, y3 % P)

def scalar_mult(k, point):
    """Elliptic curve scalar multiplication."""
    if k % N == 0 or point is None: return None
    if k < 0: return scalar_mult(-k, point_add(point, (point[0], -point[1] % P)))
    result = None
    addend = point
    while k:
        if k & 1: result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result

def recover_private_key(k, r, s, z):
    """
    Recovers the private key 'd' using the leaked 'k'.
    Formula: d = r^-1 * (s*k - z) mod n
    """
    r_inv = invert(r, N)
    d = r_inv * (s * k - z) % N
    return d

def sign_message(private_key, message):
    """Signs a new message with the recovered private key."""
    # Hash the message using SHA-256
    z = int.from_bytes(hashlib.sha256(message.encode()).digest(), 'big')
    
    # Use a new, secure random k for the new signature
    k = int.from_bytes(hashlib.sha256(b'a_secure_random_value').digest(), 'big')
    
    # Calculate r and s
    p = scalar_mult(k, G)
    r = p[0] % N
    s = invert(k, N) * (z + r * private_key) % N
    
    return r, s

def verify_signature(public_key, message, signature):
    """Verifies the forged signature."""
    r, s = signature
    z = int.from_bytes(hashlib.sha256(message.encode()).digest(), 'big')
    
    s_inv = invert(s, N)
    u1 = (z * s_inv) % N
    u2 = (r * s_inv) % N
    
    p = point_add(scalar_mult(u1, G), scalar_mult(u2, public_key))
    
    return p[0] % N == r

def generate_test_signature(private_key, k, message_hash):
    """Generate a signature using known private key and k for testing."""
    # Calculate r
    p = scalar_mult(k, G)
    r = p[0] % N
    
    # Calculate s
    k_inv = invert(k, N)
    s = (k_inv * (message_hash + r * private_key)) % N
    
    return r, s

def main():
    """Main function to demonstrate the signature forgery."""
    print("--- Forging Bitcoin-style Signature from Leaked 'k' ---")
    print("Step 1: Setting up test scenario")
    
    # Calculate public key from our test private key
    public_key = calculate_public_key(TEST_PRIVATE_KEY)
    print(f"Test Private Key: {TEST_PRIVATE_KEY:x}")
    print(f"Test Public Key: ({public_key[0]:x}, {public_key[1]:x})")
    print(f"Test Message: '{TEST_MESSAGE}'")
    print(f"Message Hash (z): {Z:x}")
    print(f"Leaked k: {LEAKED_K:x}")
    
    print("\nStep 2: Generating signature with known k")
    # Generate a signature using our known private key and k
    r, s = generate_test_signature(TEST_PRIVATE_KEY, LEAKED_K, Z)
    print(f"Generated Signature (r, s): ({r:x}, {s:x})")
    
    print("\nStep 3: Recovering private key from leaked 'k'")
    # Now attempt to recover the private key
    recovered_d = recover_private_key(LEAKED_K, r, s, Z)
    print(f"Recovered Private Key: {recovered_d:x}")
    
    # Verify that the recovered key corresponds to the public key
    p_check = scalar_mult(recovered_d, G)
    if p_check == public_key:
        print("✅ Private key successfully recovered and verified against public key.")
    else:
        print("❌ Private key recovery failed.")
        print(f"Expected public key: ({public_key[0]:x}, {public_key[1]:x})")
        print(f"Calculated public key: ({p_check[0]:x}, {p_check[1]:x})")
        return
        
    print("\nStep 4: Forging a signature for a new message")
    new_message = "Satoshi was here - this signature is forged!"
    print(f"New message to sign: '{new_message}'")
    
    # Sign the new message with the recovered private key
    forged_r, forged_s = sign_message(recovered_d, new_message)
    print(f"Forged Signature (r, s): ({forged_r:x}, {forged_s:x})")
    
    print("\nStep 5: Verifying the forged signature with the original public key")
    
    # Verify the forged signature
    is_valid = verify_signature(public_key, new_message, (forged_r, forged_s))
    
    if is_valid:
        print("\n✅ SUCCESS: The forged signature is valid!")
        print("This proves that with the recovered private key, we can sign any message.")
        print("This demonstrates the critical importance of keeping 'k' values secret and unique.")
    else:
        print("\n❌ FAILURE: The forged signature is invalid.")

if __name__ == "__main__":
    main()
