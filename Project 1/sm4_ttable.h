#ifndef SM4_TTABLE_H
#define SM4_TTABLE_H

#include <cstdint>

using word8 = uint8_t;
using word32 = uint32_t;

class SM4_TTable_Context {
public:
    SM4_TTable_Context();
    void set_key(const word8 key[16]);
    void encrypt(const word8 plaintext[16], word8 ciphertext[16]);
    void decrypt(const word8 ciphertext[16], word8 plaintext[16]);
    static word32 T_tables[4][256];

private:
    word32 round_keys[32];
    static void generate_ttables();
    void process_block(const word8 input[16], word8 output[16], bool is_encrypt);
};

#endif