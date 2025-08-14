#ifndef SM3_OPTIMIZE_H
#define SM3_OPTIMIZE_H

#include <iostream>
#include <vector>
#include <string>
#include <chrono>

class SM3Optimizer {
public:
    SM3Optimizer(const std::string& message);
    void run_benchmark(int iterations);

private:
    std::vector<uint8_t> message_data;

    void print_hex(const std::string& label, const std::vector<uint8_t>& data) const;
    void benchmark_sm3(int iterations);
    void benchmark_sm3_simd(int iterations);
};

#endif