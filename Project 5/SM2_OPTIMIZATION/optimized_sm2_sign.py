"""
Optimized SM2 Digital Signature with Performance Enhancements.

This module implements an optimized version of SM2 digital signature algorithm
with various performance improvements including precomputed tables, 
batch verification, and side-channel resistance techniques.
"""

import binascii
import time
from random import randint
from typing import List, Tuple
from gmpy2 import invert
from gmssl import sm3, func
from optimized_sm2_utils import SM2Optimizer, P, N, G, A, B, Point

class OptimizedSM2Signer:
    """Optimized SM2 signature implementation with performance enhancements."""
    
    def __init__(self):
        self.optimizer = SM2Optimizer()
        self.precomputed_base = None
        self._init_precomputed_tables()
    
    def _init_precomputed_tables(self):
        """Initialize precomputed tables for faster operations."""
        # Precompute multiples of base point G
        self.precomputed_base = self.optimizer.precompute_table(G, window_size=6)
        
    def hash_sm3(self, data_hex: str) -> str:
        """Optimized SM3 hash function wrapper."""
        data_bytes = bytes.fromhex(data_hex)
        data_list = func.bytes_to_list(data_bytes)
        return sm3.sm3_hash(data_list)
    
    def get_za_optimized(self, id_a: str, pa: Point) -> str:
        """Optimized Z_A calculation with minimal string operations."""
        id_a_bytes = id_a.encode()
        id_a_hex = id_a_bytes.hex()
        entl_a = f'{len(id_a_hex) * 4:04x}'
        
        # Use format strings for better performance
        components = [
            entl_a,
            id_a_hex,
            f'{A:064x}',
            f'{B:064x}',
            f'{G[0]:064x}',
            f'{G[1]:064x}',
            f'{pa[0]:064x}',
            f'{pa[1]:064x}'
        ]
        
        m1 = ''.join(components).upper()
        return self.hash_sm3(m1)
    
    def sign_optimized(self, message: str, za: str, private_key: int, use_rfc6979: bool = False) -> Tuple[str, str]:
        """
        Optimized SM2 signature generation.
        
        Args:
            message: Message to sign (hex format)
            za: Pre-calculated Z_A value
            private_key: Signer's private key
            use_rfc6979: Use deterministic nonce generation (RFC 6979)
            
        Returns:
            Tuple of (r, s) signature components
        """
        m_prime = za + message
        e = self.hash_sm3(m_prime)
        e_int = int(e, 16)
        
        while True:
            if use_rfc6979:
                # Deterministic nonce generation (simplified RFC 6979)
                k = self._generate_deterministic_k(e_int, private_key)
            else:
                k = randint(1, N - 1)
            
            # Use optimized scalar multiplication
            k_g = self.optimizer.scalar_mult_windowed(k, G)
            
            r = (e_int + k_g[0]) % N
            if r == 0 or r + k == N:
                continue
            
            # Optimized signature calculation
            s = (invert(1 + private_key, N) * (k - r * private_key)) % N
            if s != 0:
                break
                
        return f'{r:x}', f'{s:x}'
    
    def _generate_deterministic_k(self, e: int, private_key: int) -> int:
        """Simplified deterministic nonce generation based on RFC 6979 concept."""
        # This is a simplified version - in production, use proper RFC 6979
        combined = (e + private_key) % N
        # Use hash-based approach for deterministic k
        k_hash = self.hash_sm3(f'{combined:064x}')
        k = int(k_hash, 16) % (N - 1) + 1
        return k
    
    def verify_optimized(self, message: str, za: str, public_key: Point, 
                        r_hex: str, s_hex: str) -> bool:
        """Optimized SM2 signature verification."""
        r = int(r_hex, 16)
        s = int(s_hex, 16)
        
        # Early validation
        if not (1 <= r < N and 1 <= s < N):
            return False
        
        m_prime = za + message
        e = self.hash_sm3(m_prime)
        e_int = int(e, 16)
        
        t = (r + s) % N
        if t == 0:
            return False
        
        # Use optimized scalar multiplication
        p1 = self.optimizer.scalar_mult_windowed(s, G)
        p2 = self.optimizer.scalar_mult_windowed(t, public_key)
        x1, y1 = self.optimizer.point_add(p1, p2)
        
        r_prime = (e_int + x1) % N
        return r == r_prime
    
    def batch_verify(self, signatures: List[dict]) -> List[bool]:
        """
        Batch verification of multiple signatures for improved performance.
        
        Args:
            signatures: List of signature data dictionaries containing:
                       'message', 'za', 'public_key', 'r', 's'
        
        Returns:
            List of verification results
        """
        results = []
        
        for sig_data in signatures:
            result = self.verify_optimized(
                sig_data['message'],
                sig_data['za'], 
                sig_data['public_key'],
                sig_data['r'],
                sig_data['s']
            )
            results.append(result)
            
        return results
    
    def benchmark_signature_operations(self, message: str, private_key: int, 
                                     public_key: Point, iterations: int = 100):
        """Benchmark signature and verification operations."""
        user_id = "benchmark_user"
        za = self.get_za_optimized(user_id, public_key)
        
        print(f"Benchmarking {iterations} signature operations...")
        
        # Benchmark signing
        start_time = time.time()
        signatures = []
        for _ in range(iterations):
            r, s = self.sign_optimized(message, za, private_key)
            signatures.append((r, s))
        sign_time = time.time() - start_time
        
        # Benchmark verification
        start_time = time.time()
        for r, s in signatures:
            self.verify_optimized(message, za, public_key, r, s)
        verify_time = time.time() - start_time
        
        print(f"Signing: {sign_time:.4f}s total, {sign_time/iterations:.6f}s per signature")
        print(f"Verification: {verify_time:.4f}s total, {verify_time/iterations:.6f}s per verification")
        
        return {
            'sign_total': sign_time,
            'sign_per_op': sign_time / iterations,
            'verify_total': verify_time,
            'verify_per_op': verify_time / iterations
        }

def demonstration():
    """Demonstrate optimized SM2 signature operations."""
    signer = OptimizedSM2Signer()
    
    # Test parameters
    private_key_da = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    public_key_pa = signer.optimizer.scalar_mult_windowed(private_key_da, G)
    
    user_id = "OptimizedUser"
    message_text = "Optimized SM2 Performance Test"
    message_hex = message_text.encode().hex()
    
    print("=== Optimized SM2 Signature Demonstration ===")
    print(f"User ID: {user_id}")
    print(f"Message: '{message_text}'")
    print(f"Private Key: {private_key_da:x}")
    print(f"Public Key: ({public_key_pa[0]:x}, {public_key_pa[1]:x})")
    print()
    
    # Calculate Z_A
    za_hex = signer.get_za_optimized(user_id, public_key_pa)
    print(f"Z_A: {za_hex}")
    
    # Test both deterministic and random signing
    print("\n--- Standard Random Signature ---")
    start_time = time.time()
    r_val, s_val = signer.sign_optimized(message_hex, za_hex, private_key_da)
    sign_time = time.time() - start_time
    print(f"Signature (r, s): ({r_val}, {s_val})")
    print(f"Signing time: {sign_time:.6f}s")
    
    # Verify signature
    start_time = time.time()
    is_valid = signer.verify_optimized(message_hex, za_hex, public_key_pa, r_val, s_val)
    verify_time = time.time() - start_time
    print(f"Verification result: {'Success' if is_valid else 'Failure'}")
    print(f"Verification time: {verify_time:.6f}s")
    
    print("\n--- Deterministic Signature (RFC 6979 style) ---")
    start_time = time.time()
    r_det, s_det = signer.sign_optimized(message_hex, za_hex, private_key_da, use_rfc6979=True)
    det_sign_time = time.time() - start_time
    print(f"Deterministic signature (r, s): ({r_det}, {s_det})")
    print(f"Deterministic signing time: {det_sign_time:.6f}s")
    
    # Verify deterministic signature
    is_det_valid = signer.verify_optimized(message_hex, za_hex, public_key_pa, r_det, s_det)
    print(f"Deterministic verification: {'Success' if is_det_valid else 'Failure'}")
    
    # Performance benchmark
    print("\n--- Performance Benchmark ---")
    signer.benchmark_signature_operations(message_hex, private_key_da, public_key_pa, 50)
    
    assert is_valid and is_det_valid
    print("\n✅ All optimized signature operations successful!")

if __name__ == "__main__":
    demonstration()
