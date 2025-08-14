#include "SM3_optimize.h"
#include "SM3_Primitive.h"
#include "SM3_Promote.h"
#include <iomanip>

SM3Optimizer::SM3Optimizer(const std::string& message) {
    message_data.assign(message.begin(), message.end());
}

void SM3Optimizer::print_hex(const std::string& label, const std::vector<uint8_t>& data) const {
    std::cout << label;
    for (uint8_t byte : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)byte;
    }
    std::cout << std::dec << std::endl;
}

void SM3Optimizer::benchmark_sm3(int iterations) {
    std::vector<uint8_t> digest(32);
    auto start_time = std::chrono::steady_clock::now();
    for (int i = 0; i < iterations; i++) {
        sm3_hash(digest.data(), message_data.data(), message_data.size());
    }
    auto end_time = std::chrono::steady_clock::now();
    auto running_time = std::chrono::duration<double, std::milli>(end_time - start_time);
    std::cout << "  Standard SM3 execution time for " << iterations << " iterations: " << running_time.count() << " ms" << std::endl;
    print_hex("  Standard SM3 Hash: ", digest);
}

void SM3Optimizer::benchmark_sm3_simd(int iterations) {
    std::vector<uint8_t> digest(32);
    auto start_time = std::chrono::steady_clock::now();
    for (int i = 0; i < iterations; i++) {
        sm3_hash_simd(digest.data(), message_data.data(), message_data.size());
    }
    auto end_time = std::chrono::steady_clock::now();
    auto running_time = std::chrono::duration<double, std::milli>(end_time - start_time);
    std::cout << "  Optimized SM3 (SIMD) execution time for " << iterations << " iterations: " << running_time.count() << " ms" << std::endl;
    print_hex("  Optimized SM3 Hash: ", digest);
}

void SM3Optimizer::run_benchmark(int iterations) {
    std::cout << "\n--- SM3 Performance Benchmark ---" << std::endl;
    benchmark_sm3(iterations);
    std::cout << "---------------------------------" << std::endl;
    benchmark_sm3_simd(iterations);
    std::cout << "---------------------------------\n" << std::endl;
}

int main() {
    std::cout << "Starting SM3 optimization benchmark..." << std::endl;
    std::string message = "optimize SM3, optimize SM3,optimize SM3, optimize SM3, optimize SM3, optimize SM3, optimize SM3, optimize SM3, optimize SM3, optimize SM3";
    SM3Optimizer optimizer(message);
    optimizer.run_benchmark(100000);
    std::cout << "Benchmark completed successfully!" << std::endl;
    return 0;
}