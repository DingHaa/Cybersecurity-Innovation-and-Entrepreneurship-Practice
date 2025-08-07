#ifndef SM4_GCM_H
#define SM4_GCM_H

#include <cstdint>
#include <vector>

constexpr uint32_t SM4_BLOCK_SIZE = 16;
constexpr uint32_t SM4_KEY_SIZE  = 16;
constexpr uint32_t SM4_NUM_ROUNDS = 32;

uint32_t SM4_L(uint32_t b);
uint32_t SM4_T(uint32_t x);
void SM4_KeySchedule(const uint8_t key[SM4_KEY_SIZE], uint32_t rk[SM4_NUM_ROUNDS]);
void SM4_Round(const uint32_t rk[SM4_NUM_ROUNDS],
               const uint8_t input[SM4_BLOCK_SIZE],
               uint8_t output[SM4_BLOCK_SIZE],
               bool decrypt = false);

void parallel_ghash(const std::vector<uint8_t>& data,
                    const uint8_t* h, uint8_t* output,
                    size_t block_size = SM4_BLOCK_SIZE);

void SM4_GCM_Encrypt(const uint8_t* key, const uint8_t* iv, size_t iv_len,
                     const uint8_t* aad, size_t aad_len,
                     const uint8_t* plaintext, size_t plaintext_len,
                     uint8_t* ciphertext, uint8_t* tag, size_t tag_len);

inline void xor_block(uint8_t* dst, const uint8_t* src, size_t len) {
    for (size_t i = 0; i < len; i++) dst[i] ^= src[i];
}
inline void inc_counter(uint8_t ctr[SM4_BLOCK_SIZE]) {
    for (int i = SM4_BLOCK_SIZE - 1; i >= 0; i--) {
        if (++ctr[i]) break;
    }
}

#endif