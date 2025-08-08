#!/usr/bin/env python3
"""
SwinIR 缺失模型下载脚本
根据优先级下载缺失的预训练模型
"""

import os
import requests
import sys
from pathlib import Path
from tqdm import tqdm

# GitHub releases 基础URL
BASE_URL = "https://github.com/JingyunLiang/SwinIR/releases/download/v0.0/"

# 模型保存目录
MODEL_DIR = "model_zoo/swinir"

# 按优先级排序的缺失模型列表
MISSING_MODELS = {
    # 高优先级模型
    "high_priority": [
        # 轻量级超分辨率 - 完全缺失
        "002_lightweightSR_DIV2K_s64w8_SwinIR-S_x2.pth",
        "002_lightweightSR_DIV2K_s64w8_SwinIR-S_x3.pth", 
        "002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4.pth",
        
        # 真实世界超分辨率大型模型
        "003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth",
        
        # 经典超分辨率常用倍数
        "001_classicalSR_DF2K_s64w8_SwinIR-M_x2.pth",
        "001_classicalSR_DF2K_s64w8_SwinIR-M_x8.pth",
        
        # 修复损坏的模型
        "006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth",
    ],
    
    # 中优先级模型  
    "medium_priority": [
        # 不同噪声水平的去噪模型
        "004_grayDN_DFWB_s128w8_SwinIR-M_noise15.pth",
        "004_grayDN_DFWB_s128w8_SwinIR-M_noise50.pth",
        "005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth",
        "005_colorDN_DFWB_s128w8_SwinIR-M_noise50.pth",
        
        # 经典超分辨率3x
        "001_classicalSR_DF2K_s64w8_SwinIR-M_x3.pth",
        
        # JPEG压缩伪影减少
        "006_CAR_DFWB_s126w7_SwinIR-M_jpeg10.pth",
        "006_CAR_DFWB_s126w7_SwinIR-M_jpeg20.pth", 
        "006_CAR_DFWB_s126w7_SwinIR-M_jpeg40.pth",
        "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg10.pth",
        "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg20.pth",
        "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg40.pth",
    ],
    
    # 低优先级模型
    "low_priority": [
        # DIV2K单独训练的模型 (与DF2K功能重复)
        "001_classicalSR_DIV2K_s48w8_SwinIR-M_x2.pth",
        "001_classicalSR_DIV2K_s48w8_SwinIR-M_x3.pth",
        "001_classicalSR_DIV2K_s48w8_SwinIR-M_x4.pth", 
        "001_classicalSR_DIV2K_s48w8_SwinIR-M_x8.pth",
    ]
}

def download_file(url, filepath, desc=None):
    """下载文件并显示进度条"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f, tqdm(
            desc=desc or filepath.name,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ 成功下载: {filepath.name}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 下载失败: {filepath.name} - {e}")
        if filepath.exists():
            filepath.unlink()  # 删除不完整的文件
        return False

def check_existing_models():
    """检查已存在的模型"""
    model_dir = Path(MODEL_DIR)
    if not model_dir.exists():
        model_dir.mkdir(parents=True, exist_ok=True)
        return set()
    
    existing = set()
    for model_file in model_dir.glob("*.pth"):
        existing.add(model_file.name)
    
    return existing

def main():
    print("🔍 SwinIR 缺失模型下载工具")
    print("=" * 50)
    
    # 检查现有模型
    existing_models = check_existing_models()
    print(f"📁 当前已有模型数量: {len(existing_models)}")
    
    # 询问用户下载优先级
    print("\n请选择下载优先级:")
    print("1. 仅高优先级模型 (推荐)")
    print("2. 高+中优先级模型")
    print("3. 全部缺失模型")
    print("4. 自定义选择")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    models_to_download = []
    
    if choice == "1":
        models_to_download = MISSING_MODELS["high_priority"]
        print("📥 将下载高优先级模型")
    elif choice == "2":
        models_to_download = MISSING_MODELS["high_priority"] + MISSING_MODELS["medium_priority"]
        print("📥 将下载高+中优先级模型")
    elif choice == "3":
        models_to_download = (MISSING_MODELS["high_priority"] + 
                            MISSING_MODELS["medium_priority"] + 
                            MISSING_MODELS["low_priority"])
        print("📥 将下载全部缺失模型")
    elif choice == "4":
        print("\n可用模型列表:")
        all_models = (MISSING_MODELS["high_priority"] + 
                     MISSING_MODELS["medium_priority"] + 
                     MISSING_MODELS["low_priority"])
        
        for i, model in enumerate(all_models, 1):
            status = "✅ 已有" if model in existing_models else "❌ 缺失"
            print(f"{i:2d}. {model} - {status}")
        
        selected = input("\n请输入要下载的模型编号 (用逗号分隔，如: 1,3,5): ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in selected.split(",")]
            models_to_download = [all_models[i] for i in indices if 0 <= i < len(all_models)]
        except (ValueError, IndexError):
            print("❌ 输入格式错误")
            return
    else:
        print("❌ 无效选择")
        return
    
    # 过滤已存在的模型
    models_to_download = [m for m in models_to_download if m not in existing_models]
    
    if not models_to_download:
        print("✅ 所有选择的模型都已存在，无需下载")
        return
    
    print(f"\n📋 准备下载 {len(models_to_download)} 个模型:")
    for model in models_to_download:
        print(f"  - {model}")
    
    confirm = input(f"\n确认下载? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消下载")
        return
    
    # 开始下载
    print(f"\n🚀 开始下载...")
    model_dir = Path(MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    for model_name in models_to_download:
        url = BASE_URL + model_name
        filepath = model_dir / model_name
        
        print(f"\n📥 下载: {model_name}")
        if download_file(url, filepath, model_name):
            success_count += 1
    
    print(f"\n🎉 下载完成!")
    print(f"✅ 成功: {success_count}/{len(models_to_download)}")
    print(f"❌ 失败: {len(models_to_download) - success_count}")
    
    if success_count > 0:
        print(f"\n💡 现在你可以使用这些新下载的模型进行图像复原任务了!")
        print(f"   模型保存位置: {MODEL_DIR}")

if __name__ == "__main__":
    main()
