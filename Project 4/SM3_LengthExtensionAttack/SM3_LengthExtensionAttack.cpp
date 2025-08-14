#include "SM3_LengthExtensionAttack.h"
#include <iostream>
#include <iomanip>

SM3LengthExtensionAttack::SM3LengthExtensionAttack(const std::string& original_message, const std::string& append_message)
    : original_message(original_message), append_message(append_message) {
    original_hash.resize(sm3_digest_BYTES);
    new_hash_from_attack.resize(sm3_digest_BYTES);
    new_hash_from_scratch.resize(sm3_digest_BYTES);
}

void SM3LengthExtensionAttack::print_hex(const std::string& label, const std::vector<uint8_t>& data) {
    std::cout << label << std::endl << "  ";
    for (uint8_t byte : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)byte;
    }
    std::cout << std::dec << std::endl;
}

void SM3LengthExtensionAttack::compute_original_hash() {
    sm3_ctx ctx;
    sm3_init(&ctx);
    std::vector<uint8_t> copy_buffer(256); 
    int times = 0;
    sm3_update(&ctx, (const uint8_t*)original_message.c_str(), original_message.length(), copy_buffer.data(), times);
    sm3_final(&ctx, original_hash.data(), copy_buffer.data(), times);
}

std::vector<uint8_t> SM3LengthExtensionAttack::generate_padding(size_t message_len_bits) const {
    size_t padding_len = sm3_block_BYTES - (message_len_bits / 8 % sm3_block_BYTES);
    if (padding_len < 9) {
        padding_len += sm3_block_BYTES;
    }
    std::vector<uint8_t> padding(padding_len, 0);
    padding[0] = 0x80;
    uint64_t bit_len_be = bswap_64(message_len_bits);
    memcpy(padding.data() + padding_len - 8, &bit_len_be, 8);
    return padding;
}

void SM3LengthExtensionAttack::perform_length_extension() {
    sm3_ctx ctx;
    memcpy(ctx.digest, original_hash.data(), sm3_digest_BYTES);
    for(size_t i = 0; i < 8; ++i) {
        ctx.digest[i] = bswap_32(ctx.digest[i]);
    }

    size_t original_len_bytes = original_message.length();
    size_t original_len_bits = original_len_bytes * 8;
    size_t padded_len = original_len_bytes + generate_padding(original_len_bits).size();
    
    ctx.nblocks = padded_len / sm3_block_BYTES;
    ctx.num = 0;

    std::vector<uint8_t> copy_buffer(256);
    int times = 0;
    sm3_update(&ctx, (const uint8_t*)append_message.c_str(), append_message.length(), copy_buffer.data(), times);
    sm3_final(&ctx, new_hash_from_attack.data(), copy_buffer.data(), times);
}

void SM3LengthExtensionAttack::verify_attack() {
    std::vector<uint8_t> padding = generate_padding(original_message.length() * 8);
    std::string extended_message = original_message;
    extended_message.append((char*)padding.data(), padding.size());
    extended_message.append(append_message);

    sm3_ctx ctx;
    sm3_init(&ctx);
    std::vector<uint8_t> copy_buffer(extended_message.size() + 128);
    int times = 0;
    sm3_update(&ctx, (const uint8_t*)extended_message.c_str(), extended_message.length(), copy_buffer.data(), times);
    sm3_final(&ctx, new_hash_from_scratch.data(), copy_buffer.data(), times);
}

bool SM3LengthExtensionAttack::execute_attack() {
    compute_original_hash();
    perform_length_extension();
    verify_attack();

    print_hex("Original Message Hash:", original_hash);
    print_hex("New Hash (from attack):", new_hash_from_attack);
    print_hex("New Hash (from scratch):", new_hash_from_scratch);

    if (new_hash_from_attack == new_hash_from_scratch) {
        std::cout << "\nSuccess: Length extension attack successful!" << std::endl;
        return true;
    } else {
        std::cout << "\nFailure: Length extension attack failed." << std::endl;
        return false;
    }
}

int main() {
    std::string original_message = "This is the original secret message";
    std::string append_message = "This is the appended data";

    std::cout << "Original Message: \"" << original_message << "\"" << std::endl;
    std::cout << "Appended Message: \"" << append_message << "\"" << std::endl;
    std::cout << "--------------------------------------------------" << std::endl;

    SM3LengthExtensionAttack attack(original_message, append_message);
    attack.execute_attack();

    return 0;
}