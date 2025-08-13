#!/bin/bash

echo "==============================================="
echo "    Poseidon2 ZK-SNARK 项目状态检查"
echo "==============================================="

# 检查主要文件是否存在
echo "🔍 检查项目文件..."

files_to_check=(
    "poseidon2.circom"
    "input.json"
    "run_poseidon2.sh"
    "package.json"
    "README.md"
    "RESULTS.md"
)

generated_files=(
    "poseidon2.r1cs"
    "poseidon2.wasm"
    "proof.json"
    "public.json"
    "verification_key.json"
    "witness.wtns"
)

echo ""
echo "核心项目文件:"
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (缺失)"
    fi
done

echo ""
echo "生成的证明文件:"
for file in "${generated_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ⚠️  $file (未生成，运行 ./run_poseidon2.sh 生成)"
    fi
done

echo ""
echo "📋 当前配置:"
if [ -f "input.json" ]; then
    echo "  输入: $(cat input.json)"
fi

if [ -f "public.json" ]; then
    echo "  输出: $(cat public.json)"
fi

echo ""
echo "🔧 环境检查:"
if command -v circom &> /dev/null; then
    echo "  ✅ Circom: $(circom --version 2>&1 | head -n1)"
else
    echo "  ❌ Circom 未安装"
fi

if command -v snarkjs &> /dev/null; then
    echo "  ✅ SnarkJS: 已安装"
else
    echo "  ❌ SnarkJS 未安装"
fi

if command -v node &> /dev/null; then
    echo "  ✅ Node.js: $(node --version)"
else
    echo "  ❌ Node.js 未安装"
fi

echo ""
echo "🚀 使用说明:"
echo "  1. 修改输入: 编辑 input.json"
echo "  2. 运行项目: ./run_poseidon2.sh"
echo "  3. 查看结果: cat RESULTS.md"
echo "  4. 验证证明: snarkjs groth16 verify verification_key.json public.json proof.json"

echo ""
echo "==============================================="
