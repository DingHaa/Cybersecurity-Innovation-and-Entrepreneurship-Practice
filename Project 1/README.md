# SM4分组密码软件实现与优化技术

本项目实现了SM4分组密码的多种软件版本，并进行了多维度性能优化。包含四种实现方式：基础实现、T-Table优化、AES-NI加速和GCM模式实现，展示了密码算法在工程实践中的性能提升技术。

## 目录
- [1. 编译与执行](#1-编译与执行)
- [2. 性能对比](#2-性能对比)
- [3. SM4算法数学基础](#3-sm4算法数学基础)
- [4. 实现细节与优化思路](#4-实现细节与优化思路)
- [5. 安全性分析与优化权衡](#5-安全性分析与优化权衡)
- [附录](#附录)

## 1. 编译与执行

### 1.1 编译说明
```shell
# 完整编译（自动检测CPU特性）
make all

# 单独编译选项
g++ -std=c++17 -O3 -march=native -o sm4 sm4.cpp                  # 基础实现
g++ -std=c++17 -O3 -march=native -o sm4_ttable sm4_ttable.cpp    # T-Table优化
g++ -std=c++17 -O3 -maes -mavx2 -o sm4_aesni sm4_aesni.cpp       # AES-NI加速
g++ -std=c++17 -O3 -fopenmp -o sm4_gcm sm4_gcm.cpp               # GCM并行模式
```

### 1.2 硬件要求
| 实现版本    | 硬件要求                       | 依赖特性       |
| ----------- | ------------------------------ | -------------- |
| 基础实现    | 支持C++17的平台                | -              |
| T-Table优化 | L1缓存≥4KB                     | 高速缓存访问   |
| AES-NI加速  | Intel Westmere+/AMD Bulldozer+ | AES-NI指令集   |
| GCM模式     | 多核CPU                        | OpenMP并行支持 |

## 2. 性能对比
### 2.1 加密吞吐量(MB/s)
| 数据大小 | 基础实现 | T-Table | AES-NI | GCM模式 |
| -------- | -------- | ------- | ------ | ------- |
| 16B      | 80       | 160     | 320    | 10      |
| 1KB      | 85       | 170     | 340    | 80      |
| 1MB      | 90       | 180     | 360    | 150     |

> **测试环境**：Intel i7-10700K @3.8GHz (8核16线程), 16GB DDR4-3200, Ubuntu 20.04 LTS  
> **编译选项**：-O3 -march=native -fopenmp

## 3. SM4算法数学基础
### 3.1 算法结构
SM4采用32轮不平衡Feistel结构：
```math
\begin{cases}
X_{i+4} = X_i \oplus T(X_{i+1} \oplus X_{i+2} \oplus X_{i+3} \oplus rk_i) \\
\text{其中 } 0 \leq i \leq 31
\end{cases}
```

**迭代过程解析**：
1. 输入明文分为4个32位字：$(X_0, X_1, X_2, X_3)$
2. 32轮迭代后得到$(X_{32}, X_{33}, X_{34}, X_{35})$
3. 最终输出为反序排列：$(Y_0, Y_1, Y_2, Y_3) = (X_{35}, X_{34}, X_{33}, X_{32})$

### 3.2 合成置换T
#### 非线性变换τ：
```math
\tau(A) = (S(a_0), S(a_1), S(a_2), S(a_3)) \quad A = (a_0 \| a_1 \| a_2 \| a_3) \in \mathbb{F}_{2^{32}}
```
S盒构造特点：
- 基于复合域$GF(2^8)/GF(2^4)/GF(2^2)$实现
- 代数表达式：$S(x) = A \cdot (x^{-1} + c) + d$，其中A为仿射矩阵
- 密码学性质：
  - 非线性度：112（最优值为120）
  - 差分均匀性：8（最优值为4）
  - 代数次数：7

#### 线性变换L：
```math
L(B) = B \oplus (B \lll 2) \oplus (B \lll 10) \oplus (B \lll 18) \oplus (B \lll 24)
```
多项式表示：
```math
L(B) \equiv B \cdot (1 + \alpha^2 + \alpha^{10} + \alpha^{18} + \alpha^{24}) \pmod{\alpha^{32} + 1}
```

**扩散性质分析**：
线性变换L的分支数为5，确保单比特变化经过一轮扩散到多个字节：
```
输入差分：0x80000000
输出差分：0xE000E0E0 → 扩散到4个字节
```

### 3.3 密钥扩展算法
```math
\begin{aligned}
& \text{初始密钥处理:} \quad K_i = MK_i \oplus FK_i \\
& \text{轮密钥生成:} \quad rk_i = K_{i+4} = K_i \oplus T'(K_{i+1} \oplus K_{i+2} \oplus K_{i+3} \oplus CK_i) \\
& \text{其中} \quad T'(B) = \tau(B) \oplus (\tau(B) \lll 13) \oplus (\tau(B) \lll 23)
\end{aligned}
```

**CK常数生成公式**：
```math
CK_{i,j} = (4i + j) \times 7 \mod 256 \quad (0 \leq i \leq 31,  0 \leq j \leq 3)
```
系统参数FK：
```
FK_0 = 0xA3B1BAC6, FK_1 = 0x56AA3350
FK_2 = 0x677D9197, FK_3 = 0xB27022DC
```

### 3.4 GCM模式数学原理
#### GHASH函数：
```math
GHASH_H(X) = \sum_{i=1}^m X_i \cdot H^{m-i+1} \pmod{p(x)}
```
其中：
- $H = E_K(0^{128})$ 是认证密钥
- $p(x) = x^{128} + x^7 + x^2 + x + 1$ 是GF(2^128)的不可约多项式

#### 认证标签生成：
```math
T = MSB_t(GHASH_H(AAD \| C) \oplus E_K(J_0))
```
其中：
- $J_0$ 是初始计数器
- $t$ 是标签长度（通常128位）

## 4. 实现细节与优化思路
### 4.1 T-Table优化实现
#### 数学基础：
```math
T(A) = \bigoplus_{k=0}^3 L(S(a_k) \ll (24-8k))
```
预计算四个256元素查找表：
```math
T_k[i] = L(S(i) \ll (24-8k)) \quad (k=0,1,2,3)
```

#### 内存优化实现：
```cpp
// 缓存行对齐结构（减少缓存冲突）
struct alignas(64) TTable {
    uint32_t T0[256] __attribute__((aligned(64)));
    uint32_t T1[256] __attribute__((aligned(64)));
    uint32_t T2[256] __attribute__((aligned(64)));
    uint32_t T3[256] __attribute__((aligned(64)));
    
    // 初始化函数
    void init() {
        for (int i = 0; i < 256; i++) {
            uint32_t s = SBOX[i];
            T0[i] = linear_transform(s << 24);
            T1[i] = linear_transform(s << 16);
            T2[i] = linear_transform(s << 8);
            T3[i] = linear_transform(s);
        }
    }
};

// 优化的T变换（减少内存访问）
inline uint32_t T_transform(uint32_t X, const TTable* tbl) {
    return tbl->T0[ (X >> 24)       ] ^ 
           tbl->T1[(X >> 16) & 0xFF] ^ 
           tbl->T2[(X >>  8) & 0xFF] ^ 
           tbl->T3[ X        & 0xFF];
}
```

#### 性能优化技术：
1. **缓存预热**：初始化时预加载所有表项到缓存
2. **数据预取**：使用`__builtin_prefetch`预取下一轮数据
3. **内存对齐**：64字节对齐减少缓存行冲突

### 4.2 AES-NI加速实现
#### S-Box仿射变换：
```math
S_{SM4}(x) = \phi^{-1} \circ S_{AES} \circ \phi(x)
```
其中$\phi$是GF(2⁸)上的可逆仿射变换：
```math
\phi(x) = A \cdot x + b, \quad A \in GL(8,\mathbb{F}_2), b \in \mathbb{F}_2^8
```

#### 完整轮函数实现：
```cpp
// 仿射变换参数
const __m128i AFFINE_MAT = _mm_setr_epi8(0x8,0x1,0x6,0x5,0xC,0x3,0xE,0xD,
                                         0x4,0x7,0x2,0xF,0x9,0xB,0x0,0xA);
const __m128i INV_AFFINE = _mm_setr_epi8(0x2,0x1,0xA,0x5,0x8,0x3,0xB,0x9,
                                         0x0,0xC,0xF,0xD,0x4,0x7,0x6,0xE);

__m128i sm4_round(__m128i state, __m128i rk) {
    // 添加轮密钥
    state = _mm_xor_si128(state, rk);
    
    // 仿射变换（映射到AES域）
    __m128i affine_out = _mm_gf2p8affine_epi64_epi8(
        state, AFFINE_MAT, 0);
    
    // AES-NI S-Box（硬件加速）
    __m128i sbox_out = _mm_aesenc_si128(
        affine_out, _mm_setzero_si128());
    
    // 逆仿射变换（映射回SM4域）
    __m128i result = _mm_gf2p8affine_epi64_epi8(
        sbox_out, INV_AFFINE, 0);
    
    // 线性变换L
    result = _mm_xor_si128(result, _mm_rol_epi32(result, 2));
    result = _mm_xor_si128(result, _mm_rol_epi32(result, 10));
    result = _mm_xor_si128(result, _mm_rol_epi32(result, 18));
    result = _mm_xor_si128(result, _mm_rol_epi32(result, 24));
    
    return result;
}
```

#### 性能优势分析：
1. **S-Box加速**：AES-NI指令单周期完成S-Box计算
2. **向量化处理**：同时加密4个数据块（AVX2）
3. **流水线优化**：消除数据依赖，提高指令级并行

### 4.3 GCM模式优化
#### 分层处理架构：
```mermaid
graph TD
    A[初始化] --> B[CTR加密]
    A --> C[GHASH认证]
    B --> D[密文输出]
    C --> E[标签生成]
    D --> F[输出]
    E --> F
```

#### 并行GHASH计算：
```math
GHASH_H(X) = \bigoplus_{i=1}^{m} (X_i \cdot H^{m-i+1})
```
使用预计算表优化：
```cpp
// 预计算H的幂次表
struct GHASHTable {
    __m128i H[16];  // H^1, H^2, H^4, ..., H^32768
    
    void init(__m128i H_base) {
        H[0] = H_base;
        for (int i = 1; i < 16; i++) {
            H[i] = gf128_mult(H[i-1], H[i-1]);
        }
    }
    
    __m128i pow(int exp) {
        __m128i result = _mm_setzero_si128();
        for (int i = 0; i < 16; i++) {
            if (exp & (1 << i)) {
                result = gf128_mult(result, H[i]);
            }
        }
        return result;
    }
};

// 并行GHASH更新
void ghash_parallel(__m128i* state, const uint8_t* data, 
                   size_t blocks, const GHASHTable* tbl) {
    #pragma omp parallel for reduction(gf128_xor)
    for (size_t i = 0; i < blocks; i += 8) {
        __m128i acc = _mm_setzero_si128();
        
        // 处理8个块
        for (int j = 0; j < 8; j++) {
            __m128i blk = _mm_loadu_si128(
                (__m128i*)(data + (i+j)*16));
            __m128i H_power = tbl->pow(blocks - (i+j) - 1);
            acc = _mm_xor_si128(acc, gf128_mult(blk, H_power));
        }
        
        #pragma omp critical
        *state = gf128_mult(*state, tbl->pow(8)) ^ acc;
    }
}
```

#### 优化技术：
1. **预计算表**：减少GF(2^128)乘法次数
2. **Karatsuba算法**：优化大数乘法
3. **OpenMP并行**：利用多核并行计算
4. **流水线处理**：加密和认证并行执行

## 5. 安全性分析与优化权衡
### 5.1 侧信道防护
#### 时间攻击防护：
```cpp
// 恒定时间表查找
inline uint32_t ct_table_lookup(const uint32_t* table, uint8_t index) {
    uint32_t result = 0;
    for (int i = 0; i < 256; i++) {
        // 恒定时间比较
        uint32_t mask = ct_equal(i, index);
        result |= mask & table[i];
    }
    return result;
}

// 恒定时间比较
inline uint32_t ct_equal(uint8_t a, uint8_t b) {
    uint32_t diff = a ^ b;
    diff |= diff >> 4;
    diff |= diff >> 2;
    diff |= diff >> 1;
    return (~diff) & 1;
}
```

#### 缓存侧信道防护：
1. **固定内存访问模式**：无论输入如何，访问所有表项
2. **缓存刷新**：敏感操作后清除缓存
3. **数据随机化**：添加随机掩码

### 5.2 优化权衡矩阵
| 优化方式 | 性能 | 安全 | 内存 | 适用场景     | 关键技术 |
| -------- | ---- | ---- | ---- | ------------ | -------- |
| 基础实现 | ★★☆  | ★★★  | 1KB  | 安全敏感场景 | 恒定时间实现 |
| T-Table  | ★★★  | ★★☆  | 5KB  | 通用服务器   | 缓存优化 |
| AES-NI   | ★★★  | ★★☆  | 1KB  | 高性能计算   | 指令级并行 |
| GCM并行  | ★★☆  | ★★★  | 8KB  | 网络通信系统 | 多核并行 |

### 5.3 使用建议
1. **嵌入式系统**：基础实现+恒定时间优化
2. **服务器应用**：T-Table+缓存侧信道防护
3. **数据中心**：AES-NI+AVX2向量化
4. **网络加密**：GCM模式+并行优化

## 附录
### A. 线性变换等价证明
```math
\begin{align*}
L(B) &= B \oplus (B \lll 2) \oplus (B \lll 10) \oplus (B \lll 18) \oplus (B \lll 24) \\
&= B \otimes (1 + x^2 + x^{10} + x^{18} + x^{24}) \pmod{x^{32} + 1}
\end{align*}
```

**证明**：
考虑循环移位运算的多项式表示：
```math
B \lll k \equiv B \cdot x^k \pmod{x^{32} + 1}
```
因此：
```math
L(B) \equiv B \cdot (1 + x^2 + x^{10} + x^{18} + x^{24}) \pmod{x^{32} + 1}
```

### B. GF(2¹²⁸)乘法优化
使用Karatsuba算法：
```math
\begin{aligned}
& \text{设} \quad A = A_1x^{64} + A_0, \quad B = B_1x^{64} + B_0 \\
& Z_0 = A_0 \otimes B_0 \\
& Z_2 = A_1 \otimes B_1 \\
& Z_1 = (A_0 \oplus A_1) \otimes (B_0 \oplus B_1) \oplus Z_0 \oplus Z_2 \\
& \text{结果} = Z_2 \cdot x^{128} \oplus Z_1 \cdot x^{64} \oplus Z_0
\end{aligned}
```

C++实现：
```cpp
void gf128_mult(const uint64_t a[2], const uint64_t b[2], uint64_t result[2]) {
    uint64_t a0 = a[0], a1 = a[1];
    uint64_t b0 = b[0], b1 = b[1];
    
    // Karatsuba乘法
    uint64_t z0 = gf64_mult(a0, b0);
    uint64_t z2 = gf64_mult(a1, b1);
    uint64_t z1 = gf64_mult(a0^a1, b0^b1) ^ z0 ^ z2;
    
    // 约简模p(x) = x^128 + x^7 + x^2 + x + 1
    uint64_t t = z2 >> 57;
    result[0] = z0 ^ (z1 << 64) ^ (t << 7) ^ (t << 2) ^ (t << 1) ^ t;
    result[1] = (z1 >> 64) ^ (z2 << 7) ^ (z2 << 2) ^ (z2 << 1) ^ z2;
}
```

### C. 性能优化矩阵
| 优化技术   | 加速比 | 内存开销 | 适用平台       | 实现复杂度 |
| ---------- | ------ | -------- | -------------- | ---------- |
| 循环展开   | 1.2×   | +0%      | 所有平台       | 低         |
| T-Table    | 2.0×   | +4KB     | x86/ARMv8      | 中         |
| SIMD并行   | 3.5×   | +0%      | 支持AVX2平台   | 高         |
| AES-NI映射 | 4.0×   | +0%      | 支持AES-NI平台 | 高         |

---

**项目作者**：韩丁