#!/usr/bin/env python3
"""
SwinIR 训练任务分析工具
分析当前缺失的模型，识别需要训练的任务
"""

import os
from pathlib import Path
from collections import defaultdict

# 模型目录
MODEL_DIR = "model_zoo/swinir"

# 完整的官方模型列表及其训练配置
OFFICIAL_MODELS = {
    # 经典图像超分辨率
    "classical_sr": {
        "DIV2K_s48": {
            "001_classicalSR_DIV2K_s48w8_SwinIR-M_x2.pth": {
                "scale": 2, "dataset": "DIV2K", "patch_size": 48, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Middle"
            },
            "001_classicalSR_DIV2K_s48w8_SwinIR-M_x3.pth": {
                "scale": 3, "dataset": "DIV2K", "patch_size": 48, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Middle"
            },
            "001_classicalSR_DIV2K_s48w8_SwinIR-M_x4.pth": {
                "scale": 4, "dataset": "DIV2K", "patch_size": 48, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Middle"
            },
            "001_classicalSR_DIV2K_s48w8_SwinIR-M_x8.pth": {
                "scale": 8, "dataset": "DIV2K", "patch_size": 48, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Middle"
            },
        },
        "DF2K_s64": {
            "001_classicalSR_DF2K_s64w8_SwinIR-M_x2.pth": {
                "scale": 2, "dataset": "DF2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K + Flickr2K (2650 images)", "model_size": "Middle"
            },
            "001_classicalSR_DF2K_s64w8_SwinIR-M_x3.pth": {
                "scale": 3, "dataset": "DF2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K + Flickr2K (2650 images)", "model_size": "Middle"
            },
            "001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth": {
                "scale": 4, "dataset": "DF2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K + Flickr2K (2650 images)", "model_size": "Middle"
            },
            "001_classicalSR_DF2K_s64w8_SwinIR-M_x8.pth": {
                "scale": 8, "dataset": "DF2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K + Flickr2K (2650 images)", "model_size": "Middle"
            },
        }
    },
    
    # 轻量级图像超分辨率
    "lightweight_sr": {
        "DIV2K_s64": {
            "002_lightweightSR_DIV2K_s64w8_SwinIR-S_x2.pth": {
                "scale": 2, "dataset": "DIV2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Small"
            },
            "002_lightweightSR_DIV2K_s64w8_SwinIR-S_x3.pth": {
                "scale": 3, "dataset": "DIV2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Small"
            },
            "002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4.pth": {
                "scale": 4, "dataset": "DIV2K", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K (800 images)", "model_size": "Small"
            },
        }
    },
    
    # 真实世界图像超分辨率
    "real_sr": {
        "BSRGAN_DFO": {
            "003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth": {
                "scale": 4, "dataset": "DFO", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + OST", "model_size": "Middle", "use_gan": True
            },
        },
        "BSRGAN_DFOWMFC": {
            "003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth": {
                "scale": 4, "dataset": "DFOWMFC", "patch_size": 64, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + OST + WED + FFHQ + Manga109 + SCUT-CTW1500", 
                "model_size": "Large", "use_gan": True
            },
        }
    },
    
    # 灰度图像去噪
    "gray_denoising": {
        "DFWB_s128": {
            "004_grayDN_DFWB_s128w8_SwinIR-M_noise15.pth": {
                "noise_level": 15, "dataset": "DFWB", "patch_size": 128, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle"
            },
            "004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth": {
                "noise_level": 25, "dataset": "DFWB", "patch_size": 128, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle"
            },
            "004_grayDN_DFWB_s128w8_SwinIR-M_noise50.pth": {
                "noise_level": 50, "dataset": "DFWB", "patch_size": 128, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle"
            },
        }
    },
    
    # 彩色图像去噪
    "color_denoising": {
        "DFWB_s128": {
            "005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth": {
                "noise_level": 15, "dataset": "DFWB", "patch_size": 128, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle"
            },
            "005_colorDN_DFWB_s128w8_SwinIR-M_noise25.pth": {
                "noise_level": 25, "dataset": "DFWB", "patch_size": 128, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle"
            },
            "005_colorDN_DFWB_s128w8_SwinIR-M_noise50.pth": {
                "noise_level": 50, "dataset": "DFWB", "patch_size": 128, "window_size": 8,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle"
            },
        }
    },
    
    # JPEG压缩伪影减少
    "jpeg_car": {
        "grayscale": {
            "006_CAR_DFWB_s126w7_SwinIR-M_jpeg10.pth": {
                "jpeg_quality": 10, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "grayscale"
            },
            "006_CAR_DFWB_s126w7_SwinIR-M_jpeg20.pth": {
                "jpeg_quality": 20, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "grayscale"
            },
            "006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth": {
                "jpeg_quality": 30, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "grayscale"
            },
            "006_CAR_DFWB_s126w7_SwinIR-M_jpeg40.pth": {
                "jpeg_quality": 40, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "grayscale"
            },
        },
        "color": {
            "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg10.pth": {
                "jpeg_quality": 10, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "color"
            },
            "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg20.pth": {
                "jpeg_quality": 20, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "color"
            },
            "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg30.pth": {
                "jpeg_quality": 30, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "color"
            },
            "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg40.pth": {
                "jpeg_quality": 40, "dataset": "DFWB", "patch_size": 126, "window_size": 7,
                "training_data": "DIV2K + Flickr2K + BSD500 + WED", "model_size": "Middle", "color": "color"
            },
        }
    }
}

def check_existing_models():
    """检查已存在的模型"""
    model_dir = Path(MODEL_DIR)
    if not model_dir.exists():
        return set()
    
    existing = set()
    for model_file in model_dir.glob("*.pth"):
        # 检查文件大小，过滤掉可能损坏的文件
        if model_file.stat().st_size < 1024 * 1024:  # 小于1MB的文件可能损坏
            print(f"⚠️  发现可能损坏的模型文件: {model_file.name} (大小: {model_file.stat().st_size} bytes)")
        else:
            existing.add(model_file.name)
    
    return existing

def analyze_missing_tasks():
    """分析缺失的训练任务"""
    existing_models = check_existing_models()
    
    print("🔍 SwinIR 训练任务分析报告")
    print("=" * 60)
    print(f"📁 当前已有有效模型: {len(existing_models)} 个")
    print()
    
    missing_by_task = defaultdict(list)
    total_models = 0
    missing_count = 0
    
    # 分析每个任务类别
    for task_name, task_configs in OFFICIAL_MODELS.items():
        print(f"📋 {task_name.upper().replace('_', ' ')} 任务:")
        print("-" * 40)
        
        task_total = 0
        task_missing = 0
        
        for config_name, models in task_configs.items():
            for model_name, model_info in models.items():
                total_models += 1
                task_total += 1
                
                if model_name in existing_models:
                    status = "✅ 已有"
                else:
                    status = "❌ 缺失"
                    missing_count += 1
                    task_missing += 1
                    missing_by_task[task_name].append({
                        "model_name": model_name,
                        "config": model_info
                    })
                
                # 显示模型信息
                print(f"  {model_name}")
                print(f"    状态: {status}")
                
                # 显示训练配置
                config_str = []
                for key, value in model_info.items():
                    if key != "training_data":
                        config_str.append(f"{key}={value}")
                print(f"    配置: {', '.join(config_str)}")
                print(f"    数据: {model_info.get('training_data', 'N/A')}")
                print()
        
        completion_rate = ((task_total - task_missing) / task_total * 100) if task_total > 0 else 0
        print(f"  📊 完成度: {task_total - task_missing}/{task_total} ({completion_rate:.1f}%)")
        print()
    
    # 总体统计
    print("📊 总体统计:")
    print("-" * 40)
    print(f"官方模型总数: {total_models}")
    print(f"已有模型数量: {total_models - missing_count}")
    print(f"缺失模型数量: {missing_count}")
    print(f"总体完成度: {(total_models - missing_count) / total_models * 100:.1f}%")
    print()
    
    # 训练优先级建议
    print("🎯 训练优先级建议:")
    print("-" * 40)
    
    # 高优先级：完全缺失的任务类型
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for task_name, missing_models in missing_by_task.items():
        task_configs = OFFICIAL_MODELS[task_name]
        total_in_task = sum(len(models) for models in task_configs.values())
        missing_in_task = len(missing_models)
        
        if missing_in_task == total_in_task:
            # 完全缺失
            high_priority.extend(missing_models)
        elif missing_in_task > total_in_task * 0.5:
            # 大部分缺失
            medium_priority.extend(missing_models)
        else:
            # 少部分缺失
            low_priority.extend(missing_models)
    
    if high_priority:
        print("🔴 高优先级 (完全缺失的任务类型):")
        for item in high_priority:
            print(f"  - {item['model_name']}")
        print()
    
    if medium_priority:
        print("🟡 中优先级 (大部分缺失的任务类型):")
        for item in medium_priority:
            print(f"  - {item['model_name']}")
        print()
    
    if low_priority:
        print("🟢 低优先级 (少部分缺失的任务类型):")
        for item in low_priority:
            print(f"  - {item['model_name']}")
        print()
    
    # 训练建议
    print("💡 训练建议:")
    print("-" * 40)
    print("1. 优先训练轻量级超分辨率模型 (完全缺失)")
    print("2. 补充经典超分辨率的常用倍数 (2x, 8x)")
    print("3. 训练真实世界超分辨率大型模型")
    print("4. 补充不同噪声水平的去噪模型")
    print("5. 补充不同JPEG质量的压缩伪影减少模型")
    print()
    print("📚 训练代码位置: https://github.com/cszn/KAIR")
    print("📖 训练文档: https://github.com/cszn/KAIR/blob/master/docs/README_SwinIR.md")

if __name__ == "__main__":
    analyze_missing_tasks()
