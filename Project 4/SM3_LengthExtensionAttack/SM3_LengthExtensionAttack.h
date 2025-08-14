#ifndef SM3_LENGTH_EXTENSION_ATTACK_H
#define SM3_LENGTH_EXTENSION_ATTACK_H

#include "SM3_Primitive.h"
#include <string>
#include <vector>

class SM3LengthExtensionAttack {
public:
    SM3LengthExtensionAttack(const std::string& original_message, const std::string& append_message);

    bool execute_attack();

private:
    std::string original_message;
    std::string append_message;
    std::vector<uint8_t> original_hash;
    std::vector<uint8_t> new_hash_from_attack;
    std::vector<uint8_t> new_hash_from_scratch;

    void compute_original_hash();
    std::vector<uint8_t> generate_padding(size_t message_len_bits) const;
    void perform_length_extension();
    void verify_attack();
    
    static void print_hex(const std::string& label, const std::vector<uint8_t>& data);
};

#endif