"""
P2 (Server) implementation of DDH-based Private Intersection-Sum protocol.
"""
import socket
import pickle
import random
from gmpy2 import powmod
from phe import paillier
from shared_logic import FIXED_PRIME, PORT, hash_to_group, generate_private_key

# P2's private data
W = [("user1", 100), ("user3", 300), ("user4", 400)]
k2 = generate_private_key()
pk, sk = paillier.generate_paillier_keypair()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('localhost', PORT))
        server.listen(1)
        print("P2: Waiting for P1...")

        conn, addr = server.accept()
        print(f"P2: Connected with P1 from {addr}")

        # Round 1: Receive A from P1
        A = pickle.loads(conn.recv(40960))
        print(f"P2: Received {len(A)} elements")

        # Round 2: Compute Z and C, send to P1
        Z = [powmod(a, k2, FIXED_PRIME) for a in A]
        random.shuffle(Z)

        C = [(powmod(hash_to_group(w), k2, FIXED_PRIME), pk.encrypt(t)) for w, t in W]
        random.shuffle(C)

        conn.sendall(pickle.dumps((Z, C, pk)))
        print(f"P2: Sent Z({len(Z)}), C({len(C)}), pk")

        # Round 3: Receive and decrypt result
        encrypted_sum = pickle.loads(conn.recv(40960))
        result = sk.decrypt(encrypted_sum)
        print(f"P2: Intersection sum = {result}")

        conn.close()
        
    except Exception as e:
        print(f"P2 Error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    main()