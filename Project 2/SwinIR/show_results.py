#!/usr/bin/env python3
"""
展示SwinIR处理结果的简单脚本
"""

import os
from pathlib import Path

def show_results_summary():
    """显示处理结果总结"""
    print("🎯 SwinIR 处理结果展示")
    print("=" * 60)
    
    results_dir = Path("results")
    if not results_dir.exists():
        print("❌ 结果目录不存在")
        return
    
    # 统计各任务的结果
    tasks = {
        'swinir_classical_sr_x4': {
            'name': '经典4x图像超分辨率',
            'input_dir': 'testsets/Set5/LR_bicubic/X4',
            'gt_dir': 'testsets/Set5/HR',
            'description': 'Set5数据集，将64x64低分辨率图像放大到256x256'
        },
        'swinir_real_sr_x4': {
            'name': '真实世界4x图像超分辨率', 
            'input_dir': 'testsets/RealSRSet+5images',
            'description': '真实降质图像的4x超分辨率，处理复杂的真实世界降质'
        },
        'swinir_gray_dn_noise25': {
            'name': '灰度图像去噪 (σ=25)',
            'input_dir': 'testsets/Set12',
            'description': '去除灰度图像中的高斯噪声，噪声标准差σ=25'
        },
        'swinir_color_dn_noise25': {
            'name': '彩色图像去噪 (σ=25)',
            'input_dir': 'testsets/McMaster', 
            'description': '去除彩色图像中的高斯噪声，噪声标准差σ=25'
        },
        'swinir_color_jpeg_car_jpeg30': {
            'name': '彩色JPEG压缩伪影减少 (Q=30)',
            'input_dir': 'testsets/classic5',
            'description': '减少JPEG压缩产生的块效应和振铃伪影，质量因子Q=30'
        }
    }
    
    total_processed = 0
    
    for task_dir, task_info in tasks.items():
        result_path = results_dir / task_dir
        if result_path.exists():
            result_files = list(result_path.glob("*_SwinIR.*"))
            count = len(result_files)
            total_processed += count
            
            print(f"\n🎯 {task_info['name']}")
            print(f"   描述: {task_info['description']}")
            print(f"   处理图片数量: {count}")
            print(f"   输入目录: {task_info['input_dir']}")
            print(f"   输出目录: {result_path}")
            
            # 显示前3个处理结果的文件名
            if result_files:
                print("   处理结果示例:")
                for i, result_file in enumerate(result_files[:3]):
                    base_name = result_file.stem.replace("_SwinIR", "")
                    print(f"     [{i+1}] {base_name} → {result_file.name}")
                
                if count > 3:
                    print(f"     ... 还有 {count-3} 张图片")
    
    print(f"\n📊 总结:")
    print(f"   ✅ 成功处理了 {total_processed} 张图片")
    print(f"   ✅ 涵盖 {len([t for t in tasks.keys() if (results_dir / t).exists()])} 种图像复原任务")
    print(f"   ✅ 所有结果保存在 results/ 目录下")
    
    print(f"\n💡 查看结果的方法:")
    print(f"   1. 直接查看 results/ 目录下的图片文件")
    print(f"   2. 运行 python view_results.py 生成HTML对比报告")
    print(f"   3. 在浏览器中打开 SwinIR_结果对比报告.html")
    
    # 显示一些具体的文件路径示例
    print(f"\n📁 文件路径示例:")
    
    # 经典超分辨率示例
    classical_result = results_dir / "swinir_classical_sr_x4"
    if classical_result.exists():
        sample_files = list(classical_result.glob("*_SwinIR.png"))[:2]
        for sample in sample_files:
            base_name = sample.stem.replace("_SwinIR", "")
            input_file = f"testsets/Set5/LR_bicubic/X4/{base_name}x4.png"
            gt_file = f"testsets/Set5/HR/{base_name}.png"
            print(f"   📷 {base_name}:")
            print(f"      输入 (64x64):  {input_file}")
            print(f"      真实 (256x256): {gt_file}")
            print(f"      输出 (256x256): {sample}")
    
    # 真实世界超分辨率示例
    real_sr_result = results_dir / "swinir_real_sr_x4"
    if real_sr_result.exists():
        sample_files = list(real_sr_result.glob("*_SwinIR.png"))[:2]
        for sample in sample_files:
            base_name = sample.stem.replace("_SwinIR", "")
            # 尝试不同扩展名
            input_file = None
            for ext in ['.png', '.jpg']:
                candidate = f"testsets/RealSRSet+5images/{base_name}{ext}"
                if Path(candidate).exists():
                    input_file = candidate
                    break
            
            if input_file:
                print(f"   📷 {base_name}:")
                print(f"      输入 (真实降质): {input_file}")
                print(f"      输出 (4x放大):   {sample}")

def show_file_sizes():
    """显示文件大小信息"""
    print(f"\n📏 文件大小统计:")
    print("-" * 40)
    
    results_dir = Path("results")
    if not results_dir.exists():
        return
    
    total_size = 0
    for task_dir in results_dir.iterdir():
        if task_dir.is_dir():
            task_size = 0
            file_count = 0
            for result_file in task_dir.glob("*.*"):
                size = result_file.stat().st_size
                task_size += size
                file_count += 1
            
            if file_count > 0:
                avg_size = task_size / file_count / 1024 / 1024  # MB
                total_size += task_size
                print(f"   {task_dir.name}: {file_count}张图片, 平均{avg_size:.1f}MB")
    
    total_size_mb = total_size / 1024 / 1024
    print(f"   总大小: {total_size_mb:.1f}MB")

def main():
    """主函数"""
    show_results_summary()
    show_file_sizes()
    
    print(f"\n🚀 下一步建议:")
    print(f"   python view_results.py  # 生成详细的HTML对比报告")
    print(f"   open SwinIR_结果对比报告.html  # 在浏览器中查看")

if __name__ == "__main__":
    main()
