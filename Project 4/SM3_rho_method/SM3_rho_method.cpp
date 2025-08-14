#include "SM3_rho_method.h"

SM3RhoMethod::SM3RhoMethod() {
    initial_data = generate_initial_data();
}

void SM3RhoMethod::print_hex(const uint8_t data[], size_t len) const {
    for (size_t i = 0; i < len; i++) {
        printf("%02X", data[i]);
    }
    printf("\n");
}

std::vector<uint8_t> SM3RhoMethod::compute_sm3_hash(const std::vector<uint8_t>& data) const {
    std::vector<uint8_t> hash(HASH_SIZE);
    uint32_t hash_len = 0;
    EVP_Digest(data.data(), data.size(), hash.data(), &hash_len, EVP_sm3(), nullptr);
    return hash;
}

uint32_t SM3RhoMethod::extract_key(const std::vector<uint8_t>& hash) const {
    uint32_t key = 0;
    std::memcpy(&key, hash.data(), COLLISION_BYTE);
    return key;
}

std::vector<uint8_t> SM3RhoMethod::generate_initial_data() {
    std::vector<uint8_t> data(HASH_SIZE);
    RAND_bytes(data.data(), HASH_SIZE);
    return data;
}

bool SM3RhoMethod::find_collision() {
    auto x = compute_sm3_hash(initial_data);
    auto y = compute_sm3_hash(x);
    
    while (true) {
        auto x_next = compute_sm3_hash(x);
        auto y_next1 = compute_sm3_hash(y);
        auto y_next2 = compute_sm3_hash(y_next1);
        
        uint32_t key_x = extract_key(x_next);
        uint32_t key_y = extract_key(y_next2);
        
        if (key_x == key_y) {
            std::cout << "Collision found!" << std::endl;
            std::cout << "First message: ";
            print_hex(x.data(), HASH_SIZE);
            std::cout << "First hash: ";
            print_hex(x_next.data(), HASH_SIZE);
            std::cout << "Second message: ";
            print_hex(y_next1.data(), HASH_SIZE);
            std::cout << "Second hash: ";
            print_hex(y_next2.data(), HASH_SIZE);
            return true;
        }
        
        x = std::move(x_next);
        y = std::move(y_next2);
    }
    
    return false;
}

void SM3RhoMethod::run_attack() {
    std::cout << "Rho method collision length: " << COLLISION_LEN << " bits" << std::endl;
    std::cout << "Initial random data: ";
    print_hex(initial_data.data(), HASH_SIZE);
    
    auto start_time = std::chrono::steady_clock::now();
    bool collision_found = find_collision();
    auto end_time = std::chrono::steady_clock::now();
    
    auto running_time = std::chrono::duration<double>(end_time - start_time);
    std::cout << "SM3 Rho Method time: " << running_time.count() << " seconds" << std::endl;
    
    if (!collision_found) {
        std::cout << "Attack failed to find collision." << std::endl;
    }
}

int main() {
    SM3RhoMethod rho_attack;
    rho_attack.run_attack();
    return 0;
}