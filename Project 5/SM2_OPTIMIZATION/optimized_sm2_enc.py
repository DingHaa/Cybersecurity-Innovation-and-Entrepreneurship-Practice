"""
Optimized SM2 Encryption with Advanced Performance Features.

This module implements optimized SM2 public key encryption with various
performance improvements including parallel processing, memory optimization,
and enhanced key derivation functions.
"""

import math
import time
from random import randint
from typing import Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from gmssl import sm3, func
from optimized_sm2_utils import SM2Optimizer, P, N, G, A, B, Point

class OptimizedSM2Encryptor:
    """Optimized SM2 encryption implementation with performance enhancements."""
    
    def __init__(self):
        self.optimizer = SM2Optimizer()
        self.kdf_cache = {}  # Cache for KDF results
        
    def hash_sm3(self, data_hex: str) -> str:
        """Optimized SM3 hash function wrapper."""
        data_bytes = bytes.fromhex(data_hex)
        data_list = func.bytes_to_list(data_bytes)
        return sm3.sm3_hash(data_list)
    
    def kdf_optimized(self, z: str, klen: int) -> str:
        """
        Optimized Key Derivation Function with caching and parallel processing.
        """
        cache_key = (z, klen)
        if cache_key in self.kdf_cache:
            return self.kdf_cache[cache_key]
        
        v = 256  # Hash output length for SM3
        num_rounds = math.ceil(klen / v)
        
        if num_rounds == 1:
            # Single round - no need for parallelization
            h_input = z + '00000001'
            key = self.hash_sm3(h_input)
        else:
            # Multiple rounds - use parallel processing
            def compute_round(ct):
                h_input = z + f'{ct:08x}'
                return self.hash_sm3(h_input)
            
            with ThreadPoolExecutor(max_workers=min(num_rounds, 4)) as executor:
                futures = [executor.submit(compute_round, ct) for ct in range(1, num_rounds + 1)]
                key_parts = [future.result() for future in futures]
                key = ''.join(key_parts)
        
        # Convert to binary and truncate to required length
        key_bin = bin(int(key, 16))[2:].zfill(len(key) * 4)
        result = key_bin[:klen]
        
        # Cache the result
        self.kdf_cache[cache_key] = result
        return result
    
    def encrypt_optimized(self, message: str, public_key: Point, 
                         use_deterministic_k: bool = False) -> Tuple[str, str, str]:
        """
        Optimized SM2 encryption with performance improvements.
        
        Args:
            message: Plaintext message to encrypt
            public_key: Recipient's public key
            use_deterministic_k: Use deterministic k generation
            
        Returns:
            Tuple of (C1, C2, C3) ciphertext components
        """
        msg_bytes = message.encode('utf-8')
        msg_hex = msg_bytes.hex()
        klen = len(msg_hex) * 4
        
        while True:
            if use_deterministic_k:
                # Deterministic k based on message hash
                msg_hash = self.hash_sm3(msg_hex)
                k = int(msg_hash, 16) % (N - 1) + 1
            else:
                k = randint(1, N - 1)
            
            # C1 = k * G using optimized scalar multiplication
            c1_point = self.optimizer.scalar_mult_windowed(k, G)
            c1_hex = f'{c1_point[0]:064x}{c1_point[1]:064x}'
            
            # S = k * PB using optimized scalar multiplication
            s_point = self.optimizer.scalar_mult_windowed(k, public_key)
            if s_point is None:
                continue
            
            # Optimized KDF
            x2_hex = f'{s_point[0]:064x}'
            y2_hex = f'{s_point[1]:064x}'
            t_bin = self.kdf_optimized(x2_hex + y2_hex, klen)
            
            # Check if t is all zeros
            if int(t_bin, 2) == 0:
                continue
            
            # C2 = M XOR t
            c2_int = int(msg_hex, 16) ^ int(t_bin, 2)
            c2_hex = f'{c2_int:0{klen//4}x}'
            
            # C3 = Hash(x2 || M || y2)
            c3_input = x2_hex + msg_hex + y2_hex
            c3_hex = self.hash_sm3(c3_input)
            
            return c1_hex, c2_hex, c3_hex
    
    def decrypt_optimized(self, c1_hex: str, c2_hex: str, c3_hex: str, 
                         private_key: int) -> Optional[str]:
        """
        Optimized SM2 decryption with enhanced error handling and performance.
        """
        # Parse C1
        c1_x = int(c1_hex[:64], 16)
        c1_y = int(c1_hex[64:], 16)
        c1_point = (c1_x, c1_y)
        
        # Optimized curve point validation
        if not self._is_on_curve(c1_point):
            return None
        
        # S = dB * C1 using optimized scalar multiplication
        s_point = self.optimizer.scalar_mult_windowed(private_key, c1_point)
        if s_point is None:
            return None
        
        # Optimized KDF
        klen = len(c2_hex) * 4
        x2_hex = f'{s_point[0]:064x}'
        y2_hex = f'{s_point[1]:064x}'
        t_bin = self.kdf_optimized(x2_hex + y2_hex, klen)
        
        # M' = C2 XOR t
        m_prime_int = int(c2_hex, 16) ^ int(t_bin, 2)
        m_prime_hex = f'{m_prime_int:0{klen//4}x}'
        
        # Verify MAC: C3' = Hash(x2 || M' || y2)
        c3_prime_input = x2_hex + m_prime_hex + y2_hex
        c3_prime_hex = self.hash_sm3(c3_prime_input)
        
        if c3_prime_hex.lower() != c3_hex.lower():
            return None
        
        try:
            return bytes.fromhex(m_prime_hex).decode('utf-8')
        except UnicodeDecodeError:
            return None
    
    def _is_on_curve(self, point: Point) -> bool:
        """Efficiently check if a point is on the SM2 curve."""
        x, y = point
        left = pow(y, 2, P)
        right = (pow(x, 3, P) + A * x + B) % P
        return left == right
    
    def encrypt_large_data(self, data: str, public_key: Point, chunk_size: int = 1024) -> list:
        """
        Encrypt large data by splitting into chunks for better performance.
        
        Args:
            data: Large data to encrypt
            public_key: Recipient's public key
            chunk_size: Size of each chunk in characters
            
        Returns:
            List of encrypted chunks
        """
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        encrypted_chunks = []
        
        for i, chunk in enumerate(chunks):
            print(f"Encrypting chunk {i+1}/{len(chunks)}...")
            c1, c2, c3 = self.encrypt_optimized(chunk, public_key)
            encrypted_chunks.append((c1, c2, c3))
            
        return encrypted_chunks
    
    def decrypt_large_data(self, encrypted_chunks: list, private_key: int) -> Optional[str]:
        """
        Decrypt large data from encrypted chunks.
        
        Args:
            encrypted_chunks: List of encrypted chunks
            private_key: Recipient's private key
            
        Returns:
            Decrypted data or None if decryption fails
        """
        decrypted_chunks = []
        
        for i, (c1, c2, c3) in enumerate(encrypted_chunks):
            print(f"Decrypting chunk {i+1}/{len(encrypted_chunks)}...")
            chunk = self.decrypt_optimized(c1, c2, c3, private_key)
            if chunk is None:
                return None
            decrypted_chunks.append(chunk)
            
        return ''.join(decrypted_chunks)
    
    def benchmark_encryption(self, message: str, public_key: Point, 
                           private_key: int, iterations: int = 50):
        """Benchmark encryption and decryption operations."""
        print(f"Benchmarking {iterations} encryption/decryption operations...")
        
        # Benchmark encryption
        start_time = time.time()
        encrypted_data = []
        for _ in range(iterations):
            c1, c2, c3 = self.encrypt_optimized(message, public_key)
            encrypted_data.append((c1, c2, c3))
        encrypt_time = time.time() - start_time
        
        # Benchmark decryption
        start_time = time.time()
        for c1, c2, c3 in encrypted_data:
            decrypted = self.decrypt_optimized(c1, c2, c3, private_key)
            assert decrypted == message
        decrypt_time = time.time() - start_time
        
        print(f"Encryption: {encrypt_time:.4f}s total, {encrypt_time/iterations:.6f}s per operation")
        print(f"Decryption: {decrypt_time:.4f}s total, {decrypt_time/iterations:.6f}s per operation")
        
        return {
            'encrypt_total': encrypt_time,
            'encrypt_per_op': encrypt_time / iterations,
            'decrypt_total': decrypt_time,
            'decrypt_per_op': decrypt_time / iterations
        }

def demonstration():
    """Demonstrate optimized SM2 encryption operations."""
    encryptor = OptimizedSM2Encryptor()
    
    # Test keys
    private_key_db = 0x58892B807074F53FBF67288A1DFAA1AC313455FE60355AFD
    public_key_pb = encryptor.optimizer.scalar_mult_windowed(private_key_db, G)
    
    message = "Optimized SM2 Encryption Performance Test - 这是一个性能测试消息！"
    
    print("=== Optimized SM2 Encryption Demonstration ===")
    print(f"Original Message: {message}")
    print(f"Message Length: {len(message)} characters")
    print(f"Public Key: ({public_key_pb[0]:x}, {public_key_pb[1]:x})")
    print()
    
    # Standard encryption
    print("--- Standard Encryption ---")
    start_time = time.time()
    c1, c2, c3 = encryptor.encrypt_optimized(message, public_key_pb)
    encrypt_time = time.time() - start_time
    
    print(f"Encryption time: {encrypt_time:.6f}s")
    print(f"C1: {c1}")
    print(f"C2: {c2}")
    print(f"C3: {c3}")
    
    # Decryption
    print("\n--- Decryption ---")
    start_time = time.time()
    decrypted_message = encryptor.decrypt_optimized(c1, c2, c3, private_key_db)
    decrypt_time = time.time() - start_time
    
    print(f"Decryption time: {decrypt_time:.6f}s")
    print(f"Decrypted Message: {decrypted_message}")
    print(f"Match Original: {message == decrypted_message}")
    
    # Deterministic encryption test
    print("\n--- Deterministic Encryption Test ---")
    c1_det, c2_det, c3_det = encryptor.encrypt_optimized(message, public_key_pb, use_deterministic_k=True)
    decrypted_det = encryptor.decrypt_optimized(c1_det, c2_det, c3_det, private_key_db)
    print(f"Deterministic encryption successful: {message == decrypted_det}")
    
    # Performance benchmark
    print("\n--- Performance Benchmark ---")
    encryptor.benchmark_encryption(message, public_key_pb, private_key_db, 30)
    
    # Large data test
    print("\n--- Large Data Encryption Test ---")
    large_data = message * 50  # Create large data
    print(f"Large data length: {len(large_data)} characters")
    
    start_time = time.time()
    encrypted_chunks = encryptor.encrypt_large_data(large_data, public_key_pb, chunk_size=100)
    large_encrypt_time = time.time() - start_time
    
    start_time = time.time()
    decrypted_large = encryptor.decrypt_large_data(encrypted_chunks, private_key_db)
    large_decrypt_time = time.time() - start_time
    
    print(f"Large data encryption time: {large_encrypt_time:.4f}s")
    print(f"Large data decryption time: {large_decrypt_time:.4f}s")
    print(f"Large data integrity: {large_data == decrypted_large}")
    
    assert message == decrypted_message
    assert message == decrypted_det
    assert large_data == decrypted_large
    print("\n✅ All optimized encryption operations successful!")

if __name__ == "__main__":
    demonstration()
