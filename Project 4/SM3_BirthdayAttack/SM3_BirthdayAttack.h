#ifndef SM3_BIRTHDAY_ATTACK_H
#define SM3_BIRTHDAY_ATTACK_H

#include <iostream>
#include <unordered_map>
#include <chrono>
#include <cstring>
#include <vector>
#include <openssl/evp.h>
#include <openssl/rand.h>

class SM3BirthdayAttack {
private:
    static const int COLLISION_LEN = 24;
    static const int COLLISION_BYTE = COLLISION_LEN >> 3;
    static const uint64_t MAX_ITERATIONS = 429496;
    
    std::unordered_map<uint64_t, std::vector<uint8_t>> hash_map;
    
    void print_hex(const uint8_t data[], size_t len) const;
    uint64_t extract_key(const uint8_t hash[]) const;
    std::vector<uint8_t> generate_random_data() const;
    std::vector<uint8_t> compute_sm3_hash(const std::vector<uint8_t>& data) const;
    
public:
    SM3BirthdayAttack() = default;
    ~SM3BirthdayAttack() = default;
    
    bool find_collision();
    void run_attack();
};

#endif