#!/bin/bash

echo "=========================================="
echo "   Poseidon2 ZK-SNARK 完整实现流程"
echo "=========================================="

# 清理之前的输出文件
rm -f *.ptau *.zkey *.wtns proof.json public.json verification_key.json

echo "步骤 1: 编译 Poseidon2 电路"
echo "------------------------------------------"
circom poseidon2.circom --r1cs --wasm --sym
if [ $? -ne 0 ]; then
    echo "❌ 电路编译失败"
    exit 1
fi
echo "✅ 电路编译成功"

echo ""
echo "步骤 2: 计算见证(witness)"
echo "------------------------------------------"
snarkjs wtns calculate poseidon2.wasm input.json witness.wtns
if [ $? -ne 0 ]; then
    echo "❌ 见证计算失败"
    exit 1
fi
echo "✅ 见证计算成功"

echo ""
echo "步骤 3: 可信设置 - Powers of Tau 仪式"
echo "------------------------------------------"
echo "3.1 初始化 Powers of Tau..."
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
if [ $? -ne 0 ]; then
    echo "❌ Powers of Tau 初始化失败"
    exit 1
fi

echo "3.2 第一次贡献..."
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="First contribution" -v
if [ $? -ne 0 ]; then
    echo "❌ Powers of Tau 贡献失败"
    exit 1
fi

echo "3.3 准备 Phase 2..."
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
if [ $? -ne 0 ]; then
    echo "❌ Phase 2 准备失败"
    exit 1
fi
echo "✅ Powers of Tau 仪式完成"

echo ""
echo "步骤 4: Groth16 可信设置"
echo "------------------------------------------"
echo "4.1 生成初始密钥..."
snarkjs groth16 setup poseidon2.r1cs pot12_final.ptau poseidon2_0000.zkey
if [ $? -ne 0 ]; then
    echo "❌ Groth16 设置失败"
    exit 1
fi

echo "4.2 密钥贡献..."
snarkjs zkey contribute poseidon2_0000.zkey poseidon2_0001.zkey --name="Contributor" -v
if [ $? -ne 0 ]; then
    echo "❌ 密钥贡献失败"
    exit 1
fi

echo "4.3 导出验证密钥..."
snarkjs zkey export verificationkey poseidon2_0001.zkey verification_key.json
if [ $? -ne 0 ]; then
    echo "❌ 验证密钥导出失败"
    exit 1
fi
echo "✅ Groth16 设置完成"

echo ""
echo "步骤 5: 生成零知识证明"
echo "------------------------------------------"
snarkjs groth16 prove poseidon2_0001.zkey witness.wtns proof.json public.json
if [ $? -ne 0 ]; then
    echo "❌ 证明生成失败"
    exit 1
fi
echo "✅ 零知识证明生成成功"

echo ""
echo "步骤 6: 验证证明"
echo "------------------------------------------"
snarkjs groth16 verify verification_key.json public.json proof.json
if [ $? -eq 0 ]; then
    echo "✅ 证明验证成功！"
else
    echo "❌ 证明验证失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "          🎉 项目执行完成！"
echo "=========================================="
echo "隐私输入: $(cat input.json)"
echo "哈希输出: $(cat public.json)"
echo ""
echo "生成的文件:"
echo "- poseidon2.r1cs: 约束系统"
echo "- poseidon2.wasm: 见证生成器"
echo "- proof.json: 零知识证明"
echo "- public.json: 公开输出"
echo "- verification_key.json: 验证密钥"
echo "=========================================="
