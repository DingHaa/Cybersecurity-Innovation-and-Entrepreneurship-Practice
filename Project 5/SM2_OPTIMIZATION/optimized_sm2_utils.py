"""
Optimized SM2 Utility Functions with Performance Improvements.

This module provides optimized implementations of SM2 elliptic curve operations,
including window-based scalar multiplication, precomputed tables, and 
Montgomery ladder algorithms for enhanced performance.
"""

from typing import Tuple, List, Optional
import time

# --- Standard SM2 Elliptic Curve Parameters ---
P = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
A = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
B = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
N = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
GX = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
GY = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
G = (GX, GY)

Point = Tuple[int, int]

class SM2Optimizer:
    """Optimized SM2 implementation with various performance enhancements."""
    
    def __init__(self):
        self.precomputed_table = {}
        self.window_size = 4  # Window size for sliding window method
        
    def point_add(self, p1: Optional[Point], p2: Optional[Point]) -> Optional[Point]:
        """Optimized elliptic curve point addition with early returns."""
        if p1 is None:
            return p2
        if p2 is None:
            return p1
            
        x1, y1 = p1
        x2, y2 = p2
        
        # Early check for point at infinity
        if x1 == x2:
            if y1 == P - y2:
                return None  # Point at infinity
            # Point doubling - optimized with fewer modular operations
            s = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
        else:
            # Point addition
            dx = (x2 - x1) % P
            dy = (y2 - y1) % P
            s = dy * pow(dx, -1, P) % P
            
        x3 = (s * s - x1 - x2) % P
        y3 = (s * (x1 - x3) - y1) % P
        return (x3, y3)
    
    def point_double(self, point: Point) -> Optional[Point]:
        """Optimized point doubling operation."""
        if point is None:
            return None
            
        x, y = point
        if y == 0:
            return None
            
        # Optimized doubling formula
        s = (3 * x * x + A) * pow(2 * y, -1, P) % P
        x3 = (s * s - 2 * x) % P
        y3 = (s * (x - x3) - y) % P
        return (x3, y3)
    
    def scalar_mult_binary(self, k: int, point: Point) -> Optional[Point]:
        """Traditional binary scalar multiplication (double-and-add)."""
        if k == 0 or point is None:
            return None
            
        result = None
        current = point
        
        while k > 0:
            if k & 1:
                result = self.point_add(result, current)
            current = self.point_double(current)
            k >>= 1
            
        return result
    
    def precompute_table(self, point: Point, window_size: int = 4) -> List[Optional[Point]]:
        """Precompute table for windowed scalar multiplication."""
        table_size = 1 << window_size  # 2^window_size
        table = [None] * table_size
        
        table[0] = None  # 0 * P
        if point is not None:
            table[1] = point  # 1 * P
            
            # Compute odd multiples
            double_p = self.point_double(point)
            for i in range(3, table_size, 2):
                table[i] = self.point_add(table[i-2], double_p)
                
            # Compute even multiples
            for i in range(2, table_size, 2):
                table[i] = self.point_double(table[i//2])
                
        return table
    
    def scalar_mult_windowed(self, k: int, point: Point, window_size: int = 4) -> Optional[Point]:
        """Windowed scalar multiplication for better performance."""
        if k == 0 or point is None:
            return None
            
        # Precompute table
        table = self.precompute_table(point, window_size)
        
        result = None
        bit_length = k.bit_length()
        
        # Process k in windows from most significant to least significant
        i = bit_length - 1
        while i >= 0:
            # Extract window
            window_start = max(0, i - window_size + 1)
            window_bits = (k >> window_start) & ((1 << (i - window_start + 1)) - 1)
            
            # Double result for each bit in the window
            for _ in range(i - window_start + 1):
                result = self.point_double(result)
                
            # Add precomputed value
            if window_bits > 0:
                result = self.point_add(result, table[window_bits])
                
            i = window_start - 1
            
        return result
    
    def scalar_mult_montgomery_ladder(self, k: int, point: Point) -> Optional[Point]:
        """Montgomery ladder scalar multiplication - resistant to side-channel attacks."""
        if k == 0 or point is None:
            return None
            
        r0 = None  # 0 * P
        r1 = point  # 1 * P
        
        for bit in format(k, 'b'):
            if bit == '0':
                r1 = self.point_add(r0, r1)
                r0 = self.point_double(r0)
            else:
                r0 = self.point_add(r0, r1)
                r1 = self.point_double(r1)
                
        return r0
    
    def benchmark_scalar_mult(self, k: int, point: Point) -> dict:
        """Benchmark different scalar multiplication methods."""
        methods = {
            'binary': self.scalar_mult_binary,
            'windowed': self.scalar_mult_windowed,
            'montgomery': self.scalar_mult_montgomery_ladder
        }
        
        results = {}
        
        for method_name, method_func in methods.items():
            start_time = time.time()
            result = method_func(k, point)
            end_time = time.time()
            
            results[method_name] = {
                'time': end_time - start_time,
                'result': result
            }
            
        return results

def performance_test():
    """Performance comparison of different optimization techniques."""
    optimizer = SM2Optimizer()
    
    # Test with a large scalar
    k = 0x128B2FA8BD433C6C068C8D803DFF79792A519A55171B1B650C23661D15897263
    point = G
    
    print("=== SM2 Optimization Performance Test ===")
    print(f"Testing scalar multiplication: k = {k:x}")
    print(f"Point: ({point[0]:x}, {point[1]:x})")
    print()
    
    # Benchmark different methods
    results = optimizer.benchmark_scalar_mult(k, point)
    
    print("Performance Results:")
    print("-" * 40)
    
    for method, data in results.items():
        print(f"{method.capitalize():12}: {data['time']:.6f} seconds")
        
    print()
    
    # Verify all methods produce the same result
    first_result = next(iter(results.values()))['result']
    all_same = all(data['result'] == first_result for data in results.values())
    
    print(f"✅ All methods produce same result: {all_same}")
    
    if first_result:
        print(f"Result: ({first_result[0]:x}, {first_result[1]:x})")
    
    # Find fastest method
    fastest = min(results.items(), key=lambda x: x[1]['time'])
    print(f"🏆 Fastest method: {fastest[0]} ({fastest[1]['time']:.6f}s)")

if __name__ == "__main__":
    performance_test()
