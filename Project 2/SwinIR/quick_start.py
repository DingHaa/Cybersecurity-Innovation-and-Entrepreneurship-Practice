#!/usr/bin/env python3
"""
SwinIR 快速启动脚本
提供模型分析、下载和测试的一站式解决方案
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🎯 SwinIR 项目管理工具")
    print("   基于Swin Transformer的图像复原模型")
    print("=" * 60)

def check_environment():
    """检查环境依赖"""
    print("🔍 检查环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 需要Python 3.6或更高版本")
        return False
    
    # 检查必要的包
    required_packages = ['torch', 'torchvision', 'numpy', 'opencv-python', 'tqdm', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少以下包: {', '.join(missing_packages)}")
        print(f"   请运行: pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 环境检查通过")
    return True

def show_menu():
    """显示主菜单"""
    print("\n📋 请选择操作:")
    print("1. 📊 分析当前模型状态")
    print("2. 📥 下载缺失的模型")
    print("3. 🧪 测试模型功能")
    print("4. 📖 查看使用说明")
    print("5. 🔧 环境诊断")
    print("0. 🚪 退出")
    print("-" * 40)

def analyze_models():
    """分析模型状态"""
    print("\n🔍 分析当前模型状态...")
    if Path("analyze_training_tasks.py").exists():
        subprocess.run([sys.executable, "analyze_training_tasks.py"])
    else:
        print("❌ 分析脚本不存在")

def download_models():
    """下载模型"""
    print("\n📥 启动模型下载工具...")
    if Path("download_missing_models.py").exists():
        subprocess.run([sys.executable, "download_missing_models.py"])
    else:
        print("❌ 下载脚本不存在")

def test_models():
    """测试模型功能"""
    print("\n🧪 模型功能测试")
    print("请选择测试类型:")
    print("1. 真实世界图像超分辨率")
    print("2. 经典图像超分辨率")
    print("3. 图像去噪")
    print("4. JPEG压缩伪影减少")
    
    choice = input("请选择 (1-4): ").strip()
    
    # 检查测试图像目录
    testsets_dir = Path("testsets")
    if not testsets_dir.exists():
        print("❌ 测试数据集目录不存在，请先下载测试数据")
        return
    
    # 根据选择运行相应的测试
    if choice == "1":
        # 真实世界超分辨率测试
        model_path = "model_zoo/swinir/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth"
        if Path(model_path).exists():
            cmd = [
                sys.executable, "main_test_swinir.py",
                "--task", "real_sr",
                "--scale", "4",
                "--model_path", model_path,
                "--folder_lq", "testsets/RealSRSet+5images",
                "--tile", "400"
            ]
            print(f"🚀 运行命令: {' '.join(cmd)}")
            subprocess.run(cmd)
        else:
            print(f"❌ 模型文件不存在: {model_path}")
    
    elif choice == "2":
        # 经典超分辨率测试
        model_path = "model_zoo/swinir/001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth"
        if Path(model_path).exists():
            cmd = [
                sys.executable, "main_test_swinir.py",
                "--task", "classical_sr",
                "--scale", "4",
                "--training_patch_size", "64",
                "--model_path", model_path,
                "--folder_lq", "testsets/Set5/LR_bicubic/X4",
                "--folder_gt", "testsets/Set5/HR"
            ]
            print(f"🚀 运行命令: {' '.join(cmd)}")
            subprocess.run(cmd)
        else:
            print(f"❌ 模型文件不存在: {model_path}")
    
    elif choice == "3":
        # 图像去噪测试
        model_path = "model_zoo/swinir/004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth"
        if Path(model_path).exists():
            cmd = [
                sys.executable, "main_test_swinir.py",
                "--task", "gray_dn",
                "--noise", "25",
                "--model_path", model_path,
                "--folder_gt", "testsets/Set12"
            ]
            print(f"🚀 运行命令: {' '.join(cmd)}")
            subprocess.run(cmd)
        else:
            print(f"❌ 模型文件不存在: {model_path}")
    
    elif choice == "4":
        # JPEG压缩伪影减少测试
        model_path = "model_zoo/swinir/006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg30.pth"
        if Path(model_path).exists():
            cmd = [
                sys.executable, "main_test_swinir.py",
                "--task", "color_jpeg_car",
                "--jpeg", "30",
                "--model_path", model_path,
                "--folder_gt", "testsets/classic5"
            ]
            print(f"🚀 运行命令: {' '.join(cmd)}")
            subprocess.run(cmd)
        else:
            print(f"❌ 模型文件不存在: {model_path}")
    
    else:
        print("❌ 无效选择")

def show_usage():
    """显示使用说明"""
    print("\n📖 SwinIR 使用说明")
    print("=" * 50)
    print("""
🎯 项目概述:
SwinIR是基于Swin Transformer的图像复原模型，支持以下任务：
- 经典图像超分辨率 (2x, 3x, 4x, 8x)
- 轻量级图像超分辨率 (参数更少)
- 真实世界图像超分辨率 (处理真实降质)
- 灰度/彩色图像去噪 (noise15, 25, 50)
- JPEG压缩伪影减少 (quality10, 20, 30, 40)

📁 项目结构:
- model_zoo/swinir/     # 预训练模型存放目录
- testsets/             # 测试数据集
- results/              # 处理结果输出目录
- main_test_swinir.py   # 主要测试脚本

🚀 快速开始:
1. 运行本脚本分析当前模型状态
2. 下载需要的预训练模型
3. 使用测试功能验证模型效果

📚 更多信息:
- 官方项目: https://github.com/JingyunLiang/SwinIR
- 训练代码: https://github.com/cszn/KAIR
- 论文: SwinIR: Image Restoration Using Swin Transformer
""")

def diagnose_environment():
    """环境诊断"""
    print("\n🔧 环境诊断")
    print("-" * 40)
    
    # Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查GPU
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA可用: {torch.cuda.get_device_name(0)}")
            print(f"   显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        else:
            print("⚠️  CUDA不可用，将使用CPU")
    except ImportError:
        print("❌ PyTorch未安装")
    
    # 检查关键文件
    key_files = [
        "main_test_swinir.py",
        "models/network_swinir.py",
        "utils/util_calculate_psnr_ssim.py",
        "analyze_training_tasks.py",
        "download_missing_models.py"
    ]
    
    print("\n📁 关键文件检查:")
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    # 检查模型目录
    model_dir = Path("model_zoo/swinir")
    if model_dir.exists():
        models = list(model_dir.glob("*.pth"))
        print(f"\n📦 当前模型数量: {len(models)}")
        for model in models[:5]:  # 只显示前5个
            size_mb = model.stat().st_size / 1024 / 1024
            print(f"   {model.name} ({size_mb:.1f}MB)")
        if len(models) > 5:
            print(f"   ... 还有{len(models)-5}个模型")
    else:
        print("\n❌ 模型目录不存在")

def main():
    """主函数"""
    print_banner()
    
    if not check_environment():
        print("\n❌ 环境检查失败，请先安装必要的依赖")
        return
    
    while True:
        show_menu()
        choice = input("请选择操作 (0-5): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == "1":
            analyze_models()
        elif choice == "2":
            download_models()
        elif choice == "3":
            test_models()
        elif choice == "4":
            show_usage()
        elif choice == "5":
            diagnose_environment()
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()
