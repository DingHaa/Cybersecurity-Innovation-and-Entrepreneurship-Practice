#ifndef SM4_AESNI_H
#define SM4_AESNI_H

#include <immintrin.h>
#include <cstdint>

typedef uint8_t  word8;
typedef uint32_t word32;

void sm4_keyinit(const word8 key[16], word32 rk[32]);
void sm4_aesni_enc(const word8 in[16], word8 out[16], const word8 key[16]);
void sm4_aesni_dec(const word8 in[16], word8 out[16], const word8 key[16]);

#endif