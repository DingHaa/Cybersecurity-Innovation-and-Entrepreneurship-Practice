#include <cstdint>
#include <vector>
#include <array>
#include <random>
#include <algorithm>
#include <iostream>
#include <chrono>
#include <omp.h>

static constexpr int WORDS = 32;
static constexpr int BYTES16 = 16;

namespace SM4GCM {
    // 添加 SBOX 定义以消除未定义引用
    static constexpr uint8_t SBOX[256] = {
        0xd6,0x90,0xe9,0xfe,0xcc,0xe1,0x3d,0xb7,0x16,0xb6,0x14,0xc2,0x28,0xfb,0x2c,0x05,
        0x2b,0x67,0x9a,0x76,0x2a,0xbe,0x04,0xc3,0xaa,0x44,0x13,0x26,0x49,0x86,0x06,0x99,
        0x9c,0x42,0x50,0xf4,0x91,0xef,0x98,0x7a,0x33,0x54,0x0b,0x43,0xed,0xcf,0xac,0x62,
        0xe4,0xb3,0x1c,0xa9,0xc9,0x08,0xe8,0x95,0x80,0xdf,0x94,0xfa,0x75,0x8f,0x3f,0xa6,
        0x47,0x07,0xa7,0xfc,0xf3,0x73,0x17,0xba,0x83,0x59,0x3c,0x19,0xe6,0x85,0x4f,0xa8,
        0x68,0x6b,0x81,0xb2,0x71,0x64,0xda,0x8b,0xf8,0xeb,0x0f,0x4b,0x70,0x56,0x9d,0x35,
        0x1e,0x24,0x0e,0x5e,0x63,0x58,0xd1,0xa2,0x25,0x22,0x7c,0x3b,0x01,0x21,0x78,0x87,
        0xd4,0x00,0x46,0x57,0x9f,0xd3,0x27,0x52,0x4c,0x36,0x02,0xe7,0xa0,0xc4,0xc8,0x9e,
        0xea,0xbf,0x8a,0xd2,0x40,0xc7,0x38,0xb5,0xa3,0xf7,0xf2,0xce,0xf9,0x61,0x15,0xa1,
        0xe0,0xae,0x5d,0xa4,0x9b,0x34,0x1a,0x55,0xad,0x93,0x32,0x30,0xf5,0x8c,0xb1,0xe3,
        0x1d,0xf6,0xe2,0x2e,0x82,0x66,0xca,0x60,0xc0,0x29,0x23,0xab,0x0d,0x53,0x4e,0x6f,
        0xd5,0xdb,0x37,0x45,0xde,0xfd,0x8e,0x2f,0x03,0xff,0x6a,0x72,0x6d,0x6c,0x5b,0x51,
        0x8d,0x1b,0xaf,0x92,0xbb,0xdd,0xbc,0x7f,0x11,0xd9,0x5c,0x41,0x1f,0x10,0x5a,0xd8,
        0x0a,0xc1,0x31,0x88,0xa5,0xcd,0x7b,0xbd,0x2d,0x74,0xd0,0x12,0xb8,0xe5,0xb4,0xb0,
        0x89,0x69,0x97,0x4a,0x0c,0x96,0x77,0x7e,0x65,0xb9,0xf1,0x09,0xc5,0x6e,0xc6,0x84,
        0x18,0xf0,0x7d,0xec,0x3a,0xdc,0x4d,0x20,0x79,0xee,0x5f,0x3e,0xd7,0xcb,0x39,0x48
    };

    using Block16 = std::array<uint8_t, BYTES16>;
    using KeySched = std::array<uint32_t, WORDS>;

    uint32_t rol(uint32_t v, int s){ return (v<<s)|(v>>(32-s)); }

    void expand_key(const uint8_t* mk, KeySched& rk){
        static constexpr uint32_t FK[4] = {0xa3b1bac6u,0x56aa3350u,0x677d9197u,0xb27022dcu};
        static constexpr uint32_t CK[32] = {
            0x00070e15u,0x1c232a31u,0x383f464du,0x545b6269u,0x70777e85u,0x8c939aa1u,0xa8afb6bdu,0xc4cbd2d9u,
            0xe0e7eef5u,0xfc030a11u,0x181f262du,0x343b4249u,0x50575e65u,0x6c737a81u,0x888f969du,0xa4abb2b9u,
            0xc0c7ced5u,0xdce3eaf1u,0xf8ff060du,0x141b2229u,0x30373e45u,0x4c535a61u,0x686f767du,0x848b9299u,
            0xa0a7aeb5u,0xbcc3cad1u,0xd8dfe6edu,0xf4fb0209u,0x10171e25u,0x2c333a41u,0x484f565du,0x646b7279u
        };
        uint32_t W[36];
        for(int i=0;i<4;++i){
            W[i] = (mk[4*i]<<24)|(mk[4*i+1]<<16)|(mk[4*i+2]<<8)|mk[4*i+3];
            W[i] ^= FK[i];
        }
        auto Tp = [&](uint32_t x){
            uint32_t t = 0;
            extern const uint8_t SBOX[256];
            t  = SBOX[x&0xFF];
            t |= uint32_t(SBOX[(x>>8)&0xFF])<<8;
            t |= uint32_t(SBOX[(x>>16)&0xFF])<<16;
            t |= uint32_t(SBOX[x>>24])<<24;
            return t ^ rol(t,13) ^ rol(t,23);
        };
        for(int i=0;i<32;++i){
            uint32_t z = W[i+1]^W[i+2]^W[i+3]^CK[i];
            W[i+4] = W[i] ^ Tp(z);
            rk[i] = W[i+4];
        }
    }

    void crypt_block(const KeySched& rk, const uint8_t in[BYTES16], uint8_t out[BYTES16]){
        extern const uint8_t SBOX[256];
        auto T = [&](uint32_t x){
            uint32_t t=0;
            t  = SBOX[x&0xFF];
            t |= uint32_t(SBOX[(x>>8)&0xFF])<<8;
            t |= uint32_t(SBOX[(x>>16)&0xFF])<<16;
            t |= uint32_t(SBOX[x>>24])<<24;
            return t ^ rol(t,2)^rol(t,10)^rol(t,18)^rol(t,24);
        };
        uint32_t s[4];
        for(int i=0;i<4;++i) s[i] = (in[4*i]<<24)|(in[4*i+1]<<16)|(in[4*i+2]<<8)|in[4*i+3];
        for(int i=0;i<32;++i){
            uint32_t tmp = s[1]^s[2]^s[3]^rk[i];
            uint32_t v = s[0] ^ T(tmp);
            s[0]=s[1]; s[1]=s[2]; s[2]=s[3]; s[3]=v;
        }
        for(int i=0;i<4;++i){
            out[4*i]   = s[3-i]>>24;
            out[4*i+1] = s[3-i]>>16;
            out[4*i+2] = s[3-i]>>8;
            out[4*i+3] = s[3-i];
        }
    }

    void xor_bytes(uint8_t* dst, const uint8_t* src, size_t n){
        for(size_t i=0;i<n;++i) dst[i]^=src[i];
    }

    void inc_ctr(uint8_t ctr[BYTES16]){
        for(int i=15;i>=0;--i) if(++ctr[i]) break;
    }

    void ghash(const std::vector<uint8_t>& A, const std::vector<uint8_t>& C, const Block16& H, Block16& X){
        size_t m = (A.size()+BYTES16-1)/BYTES16;
        size_t n = (C.size()+BYTES16-1)/BYTES16;
        std::vector<uint8_t> Y((m+n+1)*BYTES16);
        auto wp = Y.data();
        std::copy(A.begin(),A.end(),wp); wp+=m*BYTES16;
        std::copy(C.begin(),C.end(),wp); wp+=n*BYTES16;
        uint64_t al=A.size()*8, cl=C.size()*8;
        for(int i=0;i<8;++i) *wp++ = al>>(56-8*i);
        for(int i=0;i<8;++i) *wp++ = cl>>(56-8*i);
        std::fill(X.begin(),X.end(),0);
        auto mul = [&](const uint8_t* a,const Block16& h, Block16& r){
            Block16 Z{};
            std::array<uint8_t,BYTES16> V;
            std::copy(a,a+BYTES16,V.begin());
            for(int i=0;i<BYTES16;++i){
                for(int b=0;b<8;++b){
                    if(V[i]&(1<<(7-b))){
                        for(int k=0;k<BYTES16;++k) Z[k]^=H[k];
                    }
                    bool carry = H[0]&1;
                    for(int k=0;k<BYTES16-1;++k) V[k]=V[k+1]<<1|(V[k+1]>>7);
                    V[15]<<=1;
                    if(carry) V[15]^=0xe1;
                }
            }
            r=Z;
        };
        for(size_t i=0; i<Y.size(); i+=BYTES16) {
            for(int k=0; k<BYTES16; ++k) 
                X[k] ^= Y[i+k];
            Block16 Z;
            mul(X.data(), H, Z);
            X = Z;
        }
    }

    void encrypt_auth(const uint8_t* key, const uint8_t* iv, size_t ivlen,
                      const std::vector<uint8_t>& A, const std::vector<uint8_t>& P,
                      std::vector<uint8_t>& C, Block16& T){
        KeySched rk; expand_key(key,rk);
        Block16 H{}, E0{};
        crypt_block(rk,H.data(),H.data());
        crypt_block(rk,iv,E0.data());
        uint8_t ctr[BYTES16]; std::copy(iv,iv+ivlen,ctr); ctr[15]=1;
        size_t N = (P.size()+BYTES16-1)/BYTES16;
        C.resize(P.size());
        #pragma omp parallel for
        for(size_t i=0;i<N;++i){
            uint8_t cb[BYTES16]; std::copy(ctr,ctr+BYTES16,cb);
            inc_ctr(cb);
            uint8_t ks[BYTES16];
            crypt_block(rk,cb,ks);
            size_t l = std::min(P.size()-i*BYTES16, size_t(BYTES16));
            for(size_t j=0;j<l;++j) C[i*BYTES16+j] = P[i*BYTES16+j] ^ ks[j];
        }
        ghash(A,C,H,T);
        for(int i=0;i<BYTES16;++i) T[i] ^= E0[i];
    }
}

int main(){
    const int R=10000;
    const size_t L=1024;
    std::mt19937_64 rd{std::random_device{}()};
    std::uniform_int_distribution<uint8_t> d{0,255};
    std::vector<uint8_t> A(16), P(L), C;
    SM4GCM::Block16 T;
    uint8_t key[16], iv[12];
    for(auto&e:key)e=d(rd);
    for(auto&e:iv)e=d(rd);
    double sum=0;
    for(int i=0;i<R;++i){
        std::generate(A.begin(),A.end(),[&](){return d(rd);});
        std::generate(P.begin(),P.end(),[&](){return d(rd);});
        auto t0=std::chrono::high_resolution_clock::now();
        SM4GCM::encrypt_auth(key,iv,12,A,P,C,T);
        auto t1=std::chrono::high_resolution_clock::now();
        sum+=std::chrono::duration<double>(t1-t0).count();
    }
    std::cout<<"avg(s):"<<sum/R<<"\n";

    double avg_time = sum / R;
    double total_time = sum;
    std::cout << "Test complete! Results:" << std::endl;
    std::cout << "Number of tests: " << R << std::endl;
    std::cout << "Plaintext length: " << L << " bytes" << std::endl;
    std::cout << "Average encryption time: " << avg_time * 1000 << " ms" << std::endl;
    std::cout << "Total time elapsed: " << total_time << " seconds" << std::endl;
}