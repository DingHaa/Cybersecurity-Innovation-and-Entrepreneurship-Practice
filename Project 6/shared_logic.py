"""
DDH-based Private Intersection-Sum Protocol - Shared Components
"""
import hashlib
import random
from gmpy2 import mpz, next_prime, powmod

# Protocol parameters
PRIME_BITS = 256
FIXED_PRIME = mpz(next_prime(2**PRIME_BITS))
PORT = 1234

def hash_to_group(identifier, prime=FIXED_PRIME):
    """Hash function H: U -> G mapping identifiers to group elements."""
    digest = hashlib.sha3_512(str(identifier).encode()).hexdigest()
    return mpz(int(digest, 16)) % prime

def generate_private_key(prime=FIXED_PRIME):
    """Generate a random private key for the protocol."""
    return random.randint(1, prime - 1)
