#ifndef __SM4_H__
#define __SM4_H__

#include <cstdint>

using word8 = uint8_t;
using word32 = uint32_t;

class SM4_Context {
public:
    void set_key(const word8 key[16]);

    void encrypt(const word8 plaintext[16], word8 ciphertext[16]);

    void decrypt(const word8 ciphertext[16], word8 plaintext[16]);

private:
    word32 round_keys[32];

    static word32 T_transform(word32 x);
    static word32 T_prime_transform(word32 x);
    void process_block(const word8 input[16], word8 output[16], bool is_encrypt);
};

#endif