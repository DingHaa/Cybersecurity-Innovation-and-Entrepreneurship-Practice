#!/usr/bin/env python3
"""
基于现有测试数据和模型的SwinIR测试脚本
只使用项目中已有的测试图片，不需要额外下载
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🧪 SwinIR 现有模型测试工具")
    print("   基于现有测试数据，无需额外下载")
    print("=" * 60)

def check_existing_models():
    """检查现有的有效模型"""
    model_dir = Path("model_zoo/swinir")
    if not model_dir.exists():
        return {}
    
    models = {}
    for model_file in model_dir.glob("*.pth"):
        # 检查文件大小，过滤损坏文件
        size_mb = model_file.stat().st_size / 1024 / 1024
        if size_mb > 1:  # 大于1MB才认为是有效模型
            models[model_file.name] = {
                'path': str(model_file),
                'size_mb': size_mb
            }
    
    return models

def check_test_datasets():
    """检查现有的测试数据集"""
    datasets = {}
    testsets_dir = Path("testsets")
    
    if not testsets_dir.exists():
        return datasets
    
    # Set5 - 经典超分辨率测试集
    set5_hr = testsets_dir / "Set5" / "HR"
    set5_lr_x4 = testsets_dir / "Set5" / "LR_bicubic" / "X4"
    if set5_hr.exists() and set5_lr_x4.exists():
        datasets['Set5'] = {
            'type': 'classical_sr',
            'hr_path': str(set5_hr),
            'lr_x4_path': str(set5_lr_x4),
            'description': '经典超分辨率测试集 (5张图片)',
            'images': len(list(set5_hr.glob("*.png")))
        }
    
    # Set12 - 灰度去噪测试集
    set12 = testsets_dir / "Set12"
    if set12.exists():
        datasets['Set12'] = {
            'type': 'gray_denoising',
            'path': str(set12),
            'description': '灰度图像去噪测试集 (12张图片)',
            'images': len(list(set12.glob("*.png")))
        }
    
    # McMaster - 彩色去噪测试集
    mcmaster = testsets_dir / "McMaster"
    if mcmaster.exists():
        datasets['McMaster'] = {
            'type': 'color_denoising',
            'path': str(mcmaster),
            'description': '彩色图像去噪测试集 (18张图片)',
            'images': len(list(mcmaster.glob("*.tif")))
        }
    
    # RealSRSet+5images - 真实世界超分辨率测试集
    real_sr = testsets_dir / "RealSRSet+5images"
    if real_sr.exists():
        datasets['RealSRSet+5images'] = {
            'type': 'real_sr',
            'path': str(real_sr),
            'description': '真实世界超分辨率测试集 (25张图片)',
            'images': len(list(real_sr.glob("*.*")))
        }
    
    # classic5 - JPEG压缩伪影测试集
    classic5 = testsets_dir / "classic5"
    if classic5.exists():
        datasets['classic5'] = {
            'type': 'jpeg_car',
            'path': str(classic5),
            'description': 'JPEG压缩伪影减少测试集 (5张图片)',
            'images': len(list(classic5.glob("*.bmp")))
        }
    
    return datasets

def run_test(model_path, task, test_config):
    """运行单个测试"""
    print(f"\n🚀 开始测试: {task}")
    print(f"   模型: {Path(model_path).name}")
    print(f"   数据: {test_config['description']}")
    
    # 构建命令
    cmd = [sys.executable, "main_test_swinir.py"]
    
    if task == "classical_sr_x4":
        cmd.extend([
            "--task", "classical_sr",
            "--scale", "4",
            "--training_patch_size", "64",
            "--model_path", model_path,
            "--folder_lq", test_config['lr_x4_path'],
            "--folder_gt", test_config['hr_path']
        ])
    
    elif task == "real_sr_x4":
        cmd.extend([
            "--task", "real_sr",
            "--scale", "4",
            "--model_path", model_path,
            "--folder_lq", test_config['path'],
            "--tile", "400"  # 使用tile避免内存不足
        ])
    
    elif task == "gray_denoising_25":
        cmd.extend([
            "--task", "gray_dn",
            "--noise", "25",
            "--model_path", model_path,
            "--folder_gt", test_config['path']
        ])
    
    elif task == "color_jpeg_car_30":
        cmd.extend([
            "--task", "color_jpeg_car",
            "--jpeg", "30",
            "--model_path", model_path,
            "--folder_gt", test_config['path']
        ])
    
    print(f"   命令: {' '.join(cmd)}")
    
    # 运行测试
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ 测试成功完成 (耗时: {end_time-start_time:.1f}秒)")
            # 查找结果目录
            results_dir = Path("results")
            if results_dir.exists():
                latest_result = max(results_dir.glob("swinir_*"), key=os.path.getctime, default=None)
                if latest_result:
                    result_images = len(list(latest_result.glob("*.*")))
                    print(f"   结果保存在: {latest_result} ({result_images}张图片)")
            return True
        else:
            print(f"❌ 测试失败")
            print(f"   错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ 测试超时 (>5分钟)")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查现有模型
    print("🔍 检查现有模型...")
    models = check_existing_models()
    if not models:
        print("❌ 未找到有效的预训练模型")
        return
    
    print(f"✅ 找到 {len(models)} 个有效模型:")
    for name, info in models.items():
        print(f"   - {name} ({info['size_mb']:.1f}MB)")
    
    # 检查测试数据集
    print("\n🔍 检查测试数据集...")
    datasets = check_test_datasets()
    if not datasets:
        print("❌ 未找到测试数据集")
        return
    
    print(f"✅ 找到 {len(datasets)} 个测试数据集:")
    for name, info in datasets.items():
        print(f"   - {name}: {info['description']}")
    
    # 定义可执行的测试任务
    available_tests = []
    
    # 经典4x超分辨率
    classical_model = "001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth"
    if classical_model in models and "Set5" in datasets:
        available_tests.append({
            'id': 'classical_sr_x4',
            'name': '经典4x图像超分辨率',
            'model': models[classical_model]['path'],
            'dataset': datasets['Set5'],
            'description': 'Set5数据集，5张经典测试图片'
        })
    
    # 真实世界4x超分辨率
    real_sr_model = "003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth"
    if real_sr_model in models and "RealSRSet+5images" in datasets:
        available_tests.append({
            'id': 'real_sr_x4',
            'name': '真实世界4x图像超分辨率',
            'model': models[real_sr_model]['path'],
            'dataset': datasets['RealSRSet+5images'],
            'description': 'RealSRSet数据集，25张真实降质图片'
        })
    
    # 灰度图像去噪
    gray_dn_model = "004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth"
    if gray_dn_model in models and "Set12" in datasets:
        available_tests.append({
            'id': 'gray_denoising_25',
            'name': '灰度图像去噪 (noise25)',
            'model': models[gray_dn_model]['path'],
            'dataset': datasets['Set12'],
            'description': 'Set12数据集，12张灰度图片'
        })
    
    # 彩色JPEG压缩伪影减少
    color_car_model = "006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg30.pth"
    if color_car_model in models and "classic5" in datasets:
        available_tests.append({
            'id': 'color_jpeg_car_30',
            'name': '彩色JPEG压缩伪影减少 (quality30)',
            'model': models[color_car_model]['path'],
            'dataset': datasets['classic5'],
            'description': 'classic5数据集，5张经典图片'
        })
    
    if not available_tests:
        print("\n❌ 没有可执行的测试任务")
        print("   请确保模型和对应的测试数据都存在")
        return
    
    # 显示可用测试
    print(f"\n📋 可执行的测试任务 ({len(available_tests)}个):")
    for i, test in enumerate(available_tests, 1):
        print(f"{i}. {test['name']}")
        print(f"   {test['description']}")
    print(f"{len(available_tests)+1}. 运行所有测试")
    print("0. 退出")
    
    # 用户选择
    while True:
        try:
            choice = int(input(f"\n请选择测试任务 (0-{len(available_tests)+1}): "))
            if choice == 0:
                print("👋 退出测试")
                return
            elif choice == len(available_tests) + 1:
                # 运行所有测试
                print(f"\n🚀 开始运行所有 {len(available_tests)} 个测试...")
                success_count = 0
                for test in available_tests:
                    if run_test(test['model'], test['id'], test['dataset']):
                        success_count += 1
                
                print(f"\n🎉 测试完成!")
                print(f"✅ 成功: {success_count}/{len(available_tests)}")
                print(f"❌ 失败: {len(available_tests) - success_count}")
                break
                
            elif 1 <= choice <= len(available_tests):
                # 运行单个测试
                test = available_tests[choice - 1]
                run_test(test['model'], test['id'], test['dataset'])
                break
            else:
                print("❌ 无效选择，请重新输入")
        except ValueError:
            print("❌ 请输入数字")
        except KeyboardInterrupt:
            print("\n👋 用户取消")
            return
    
    print(f"\n💡 提示:")
    print(f"   - 结果保存在 results/ 目录下")
    print(f"   - 可以对比处理前后的图片效果")
    print(f"   - 如需更多模型，可运行 download_missing_models.py")

if __name__ == "__main__":
    main()
