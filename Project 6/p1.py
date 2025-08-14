"""
P1 (Client) implementation of DDH-based Private Intersection-Sum protocol.
"""
import socket
import pickle
import random
from gmpy2 import powmod
from shared_logic import FIXED_PRIME, PORT, hash_to_group, generate_private_key

# P1's private data
V = ["user1", "user2", "user3"]
k1 = generate_private_key()

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', PORT))
        print("P1: Connected to P2")

        # Round 1: Send H(vi)^k1
        A = [powmod(hash_to_group(v), k1, FIXED_PRIME) for v in V]
        random.shuffle(A)
        client.sendall(pickle.dumps(A))
        print(f"P1: Sent {len(A)} elements")

        # Round 2: Receive Z, C, pk
        Z, C, pk = pickle.loads(client.recv(40960))
        print(f"P1: Received Z({len(Z)}), C({len(C)}), pk")

        # Round 3: Compute intersection sum
        encrypted_values = []
        for h_w_k2, enc_t in C:
            h_w_k1k2 = powmod(h_w_k2, k1, FIXED_PRIME)
            if h_w_k1k2 in Z:
                encrypted_values.append(enc_t)

        # Homomorphic sum
        if encrypted_values:
            result = encrypted_values[0]
            for enc_val in encrypted_values[1:]:
                result = result + enc_val
        else:
            result = pk.encrypt(0)

        # Randomize and send
        result = result + pk.encrypt(0)
        client.sendall(pickle.dumps(result))
        print(f"P1: Sent encrypted sum (intersection size: {len(encrypted_values)})")

    except Exception as e:
        print(f"P1 Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()