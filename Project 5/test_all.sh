#!/bin/bash
# 测试脚本 - 验证所有 SM2 实现和安全演示的正确性

echo "=== 1. 测试 SM2 基础实现 ==="
echo "--- 测试 SM2 数字签名 ---"
python SM2_IMPL/SM2_Sign.py
echo ""
echo "--- 测试 SM2 公钥加密 ---"
python SM2_IMPL/SM2_Enc.py
echo ""
echo "--- 测试 SM2 PGP 协议 ---"
python SM2_PGP/SM2_PGP.py
echo ""

echo "=== 2. 测试 SM2 性能优化 ==="
echo "--- 测试优化后的 SM2 工具函数 ---"
python SM2_OPTIMIZATION/optimized_sm2_utils.py
echo ""
echo "--- 测试优化后的 SM2 数字签名 ---"
python SM2_OPTIMIZATION/optimized_sm2_sign.py
echo ""
echo "--- 测试优化后的 SM2 公钥加密 ---"
python SM2_OPTIMIZATION/optimized_sm2_enc.py
echo ""

echo "=== 3. 运行安全漏洞演示 ==="
echo "--- 演示 k-Reuse 攻击 ---"
python SIGNATURE_MISUSE_POC/k_reuse_attack.py
echo ""
echo "--- 演示 ECDSA 签名伪造 ---"
python SATOSHI_SIGNATURE_FORGE/satoshi_forge.py
echo ""

echo "✅ 所有测试和演示完成！"
