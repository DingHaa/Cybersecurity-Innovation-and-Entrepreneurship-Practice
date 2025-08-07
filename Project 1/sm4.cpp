#include "sm4.h"
#include <iostream>
#include <iomanip>
#include <vector>
#include <numeric>
#include <random>
#include <chrono>
#include <stdexcept>

#define rotl(x, n) (((x) << (n)) | ((x) >> (32 - (n))))

static const word8 Sbox[256] = {
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
    0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
    0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62,
    0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6,
    0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8,
    0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35,
    0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87,
    0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e,
    0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
    0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3,
    0x1d, 0xf6, 0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f,
    0xd5, 0xdb, 0x37, 0x45, 0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51,
    0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8,
    0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0,
    0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39, 0x48
};

static const word32 FK[4] = {0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc};
static const word32 CK[32] = {
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269, 0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249, 0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229, 0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209, 0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
};

inline word32 get_word(const word8* p) {
    return ((word32)p[0] << 24) | ((word32)p[1] << 16) | ((word32)p[2] << 8) | (word32)p[3];
}

inline void put_word(word32 w, word8* p) {
    p[0] = (word8)(w >> 24);
    p[1] = (word8)(w >> 16);
    p[2] = (word8)(w >> 8);
    p[3] = (word8)w;
}

inline word8 sbox_lookup(word8 x) {
    return Sbox[x];
}

word32 SM4_Context::T_transform(word32 x) {
    word8 b[4];
    put_word(x, b);
    b[0] = sbox_lookup(b[0]);
    b[1] = sbox_lookup(b[1]);
    b[2] = sbox_lookup(b[2]);
    b[3] = sbox_lookup(b[3]);
    word32 y = get_word(b);
    return y ^ rotl(y, 2) ^ rotl(y, 10) ^ rotl(y, 18) ^ rotl(y, 24);
}

word32 SM4_Context::T_prime_transform(word32 x) {
    word8 b[4];
    put_word(x, b);
    b[0] = sbox_lookup(b[0]);
    b[1] = sbox_lookup(b[1]);
    b[2] = sbox_lookup(b[2]);
    b[3] = sbox_lookup(b[3]);
    word32 y = get_word(b);
    return y ^ rotl(y, 13) ^ rotl(y, 23);
}

void SM4_Context::set_key(const word8 key[16]) {
    word32 MK[4];
    for (int i = 0; i < 4; ++i) {
        MK[i] = get_word(key + i * 4);
    }

    word32 K[36];
    for (int i = 0; i < 4; ++i) {
        K[i] = MK[i] ^ FK[i];
    }

    for (int i = 0; i < 32; ++i) {
        K[i + 4] = K[i] ^ T_prime_transform(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i]);
        this->round_keys[i] = K[i + 4];
    }
}

void SM4_Context::process_block(const word8 input[16], word8 output[16], bool is_encrypt) {
    word32 X[4];
    for (int i = 0; i < 4; ++i) {
        X[i] = get_word(input + i * 4);
    }

    for (int i = 0; i < 32; ++i) {
        word32 current_round_key = is_encrypt ? this->round_keys[i] : this->round_keys[31 - i];
        word32 temp = X[1] ^ X[2] ^ X[3] ^ current_round_key;
        X[0] = X[0] ^ T_transform(temp);
        word32 next_X0 = X[1];
        X[1] = X[2];
        X[2] = X[3];
        X[3] = X[0];
        X[0] = next_X0;
    }

    for (int i = 0; i < 4; ++i) {
        put_word(X[3 - i], output + i * 4);
    }
}

void SM4_Context::encrypt(const word8 plaintext[16], word8 ciphertext[16]) {
    process_block(plaintext, ciphertext, true);
}

void SM4_Context::decrypt(const word8 ciphertext[16], word8 plaintext[16]) {
    process_block(ciphertext, plaintext, false);
}

int main() {
    const int NUM_TESTS = 1000;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);

    std::vector<double> durations;
    durations.reserve(NUM_TESTS);

    word8 m[16], k[16], c[16], decrypted_m[16];

    for (int i = 0; i < NUM_TESTS; i++) {
        for (int j = 0; j < 16; j++) {
            m[j] = dis(gen);
            k[j] = dis(gen);
        }

        SM4_Context ctx;
        ctx.set_key(k);

        auto start = std::chrono::high_resolution_clock::now();
        ctx.encrypt(m, c);
        auto end = std::chrono::high_resolution_clock::now();
        
        std::chrono::duration<double, std::milli> duration_ms = end - start;
        durations.push_back(duration_ms.count());

        ctx.decrypt(c, decrypted_m);
        for(int j=0; j<16; ++j) {
            if(m[j] != decrypted_m[j]) {
                std::cerr << "Error: Decryption failed at test " << i << std::endl;
                return 1;
            }
        }
    }

    double total = std::accumulate(durations.begin(), durations.end(), 0.0);
    double average = total / NUM_TESTS;

    std::cout << "Correctness and Performance Test Completed." << std::endl;
    std::cout << "Total tests: " << NUM_TESTS << " random encryptions/decryptions." << std::endl;
    std::cout << "Average encryption time: " << std::fixed << std::setprecision(4) << average << " ms" << std::endl;
    std::cout << "Total time for all encryptions: " << std::fixed << std::setprecision(2) << total << " ms" << std::endl;

    return 0;
}