#include "SM3_BirthdayAttack.h"

void SM3BirthdayAttack::print_hex(const uint8_t data[], size_t len) const {
    for (size_t i = 0; i < len; i++) {
        printf("%02X", data[i]);
    }
    printf("\n");
}

uint64_t SM3BirthdayAttack::extract_key(const uint8_t hash[]) const {
    uint64_t key = 0;
    std::memcpy(&key, hash, COLLISION_BYTE);
    return key;
}

std::vector<uint8_t> SM3BirthdayAttack::generate_random_data() const {
    std::vector<uint8_t> data(32);
    RAND_bytes(data.data(), 32);
    return data;
}

std::vector<uint8_t> SM3BirthdayAttack::compute_sm3_hash(const std::vector<uint8_t>& data) const {
    std::vector<uint8_t> hash(32);
    uint32_t hash_len = 0;
    EVP_Digest(data.data(), data.size(), hash.data(), &hash_len, EVP_sm3(), nullptr);
    return hash;
}

bool SM3BirthdayAttack::find_collision() {
    hash_map.clear();
    
    for (uint64_t i = 0; i < MAX_ITERATIONS; i++) {
        auto data = generate_random_data();
        auto hash = compute_sm3_hash(data);
        uint64_t key = extract_key(hash.data());
        
        auto it = hash_map.find(key);
        if (it != hash_map.end()) {
            std::cout << "Found collision with hash key: 0x" << std::hex << key << std::endl;
            std::cout << "First preimage: ";
            print_hex(it->second.data(), 32);
            std::cout << "Second preimage: ";
            print_hex(data.data(), 32);
            return true;
        }
        
        hash_map[key] = std::move(data);
    }
    
    std::cout << "No collision found within " << MAX_ITERATIONS << " iterations." << std::endl;
    return false;
}

void SM3BirthdayAttack::run_attack() {
    std::cout << "Collision bit length: " << COLLISION_LEN << std::endl;
    
    auto start_time = std::chrono::steady_clock::now();
    bool collision_found = find_collision();
    auto end_time = std::chrono::steady_clock::now();
    
    auto running_time = std::chrono::duration<double, std::milli>(end_time - start_time);
    std::cout << "SM3 Birthday Attack time: " << running_time.count() << " ms" << std::endl;
    
    if (!collision_found) {
        std::cout << "Attack failed to find collision." << std::endl;
    }
}

int main() {
    SM3BirthdayAttack attack;
    attack.run_attack();
    return 0;
}