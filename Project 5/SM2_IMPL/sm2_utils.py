"""
SM2 Cryptography Utility Functions and Constants.

This module provides the core components for SM2 elliptic curve cryptography,
including curve parameters and arithmetic functions. The parameters are based on
the standard SM2 curve.
"""

from typing import Tuple

# --- Standard SM2 Elliptic Curve Parameters ---
P = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
A = 0x787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498
B = 0x63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A
N = 0x8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7
GX = 0x421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D
GY = 0x0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2
G = (GX, GY)

Point = Tuple[int, int]

def point_add(p1: Point, p2: Point) -> Point:
    """Performs elliptic curve point addition."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and y1 == P - y2:
        return None  # Point at infinity

    if x1 == x2:
        # Point doubling
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, P)
    else:
        # Point addition
        lam = (y2 - y1) * pow(x2 - x1, -1, P)

    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return x3, y3

def scalar_mult(k: int, p_point: Point) -> Point:
    """
    Performs elliptic curve scalar multiplication (k * P).
    Uses the binary method (double-and-add).
    """
    if k == 0 or p_point is None:
        return None
    
    result: Point = None
    current = p_point
    
    while k > 0:
        if k & 1:
            result = point_add(result, current)
        current = point_add(current, current)
        k >>= 1
        
    return result
