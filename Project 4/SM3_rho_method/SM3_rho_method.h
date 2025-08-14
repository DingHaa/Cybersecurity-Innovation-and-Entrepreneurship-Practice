#ifndef SM3_RHO_METHOD_H
#define SM3_RHO_METHOD_H

#include <iostream>
#include <chrono>
#include <cstring>
#include <vector>
#include <openssl/evp.h>
#include <openssl/rand.h>

class SM3RhoMethod {
private:
    static const int COLLISION_LEN = 24;
    static const int COLLISION_BYTE = COLLISION_LEN >> 3;
    static const size_t HASH_SIZE = 32;
    
    std::vector<uint8_t> initial_data;
    
    void print_hex(const uint8_t data[], size_t len) const;
    std::vector<uint8_t> compute_sm3_hash(const std::vector<uint8_t>& data) const;
    uint32_t extract_key(const std::vector<uint8_t>& hash) const;
    std::vector<uint8_t> generate_initial_data();
    
public:
    SM3RhoMethod();
    ~SM3RhoMethod() = default;
    
    bool find_collision();
    void run_attack();
};

#endif