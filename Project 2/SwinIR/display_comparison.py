#!/usr/bin/env python3
"""
展示SwinIR处理前后的对比结果
"""

import os
from pathlib import Path
from PIL import Image

def get_image_info(image_path):
    """获取图片信息"""
    try:
        with Image.open(image_path) as img:
            return {
                'size': img.size,
                'mode': img.mode,
                'format': img.format,
                'file_size': Path(image_path).stat().st_size
            }
    except Exception as e:
        return {'error': str(e)}

def display_task_comparison(task_name, task_info, max_samples=3):
    """显示单个任务的对比结果"""
    print(f"\n{'='*60}")
    print(f"🎯 {task_info['name']}")
    print(f"{'='*60}")
    print(f"📝 描述: {task_info['description']}")
    
    results_dir = Path("results") / task_name
    if not results_dir.exists():
        print("❌ 结果目录不存在")
        return
    
    result_files = list(results_dir.glob("*_SwinIR.*"))
    print(f"📊 处理图片总数: {len(result_files)}")
    
    # 显示前几个样本的详细对比
    samples = result_files[:max_samples]
    
    for i, result_file in enumerate(samples, 1):
        print(f"\n📷 样本 {i}: {result_file.stem.replace('_SwinIR', '')}")
        print("-" * 40)
        
        # 获取输出图片信息
        output_info = get_image_info(result_file)
        if 'error' not in output_info:
            print(f"🎯 SwinIR输出:")
            print(f"   文件: {result_file.name}")
            print(f"   尺寸: {output_info['size'][0]}×{output_info['size'][1]}")
            print(f"   模式: {output_info['mode']}")
            print(f"   大小: {output_info['file_size']/1024:.1f}KB")
        
        # 根据任务类型查找对应的输入文件
        base_name = result_file.stem.replace('_SwinIR', '')
        
        if task_name == 'swinir_classical_sr_x4':
            # 经典超分辨率：有LR输入和HR真实值
            lr_file = Path(f"testsets/Set5/LR_bicubic/X4/{base_name}x4.png")
            hr_file = Path(f"testsets/Set5/HR/{base_name}.png")
            
            if lr_file.exists():
                lr_info = get_image_info(lr_file)
                if 'error' not in lr_info:
                    print(f"📥 低分辨率输入:")
                    print(f"   文件: {lr_file.name}")
                    print(f"   尺寸: {lr_info['size'][0]}×{lr_info['size'][1]}")
                    print(f"   大小: {lr_info['file_size']/1024:.1f}KB")
            
            if hr_file.exists():
                hr_info = get_image_info(hr_file)
                if 'error' not in hr_info:
                    print(f"🎯 高分辨率真实值:")
                    print(f"   文件: {hr_file.name}")
                    print(f"   尺寸: {hr_info['size'][0]}×{hr_info['size'][1]}")
                    print(f"   大小: {hr_info['file_size']/1024:.1f}KB")
                    
                    # 计算放大倍数
                    if lr_file.exists() and 'error' not in lr_info:
                        scale_x = hr_info['size'][0] / lr_info['size'][0]
                        scale_y = hr_info['size'][1] / lr_info['size'][1]
                        print(f"📈 放大倍数: {scale_x:.1f}x × {scale_y:.1f}x")
        
        elif task_name == 'swinir_real_sr_x4':
            # 真实世界超分辨率：只有输入图片
            input_file = None
            for ext in ['.png', '.jpg']:
                candidate = Path(f"testsets/RealSRSet+5images/{base_name}{ext}")
                if candidate.exists():
                    input_file = candidate
                    break
            
            if input_file:
                input_info = get_image_info(input_file)
                if 'error' not in input_info:
                    print(f"📥 真实降质输入:")
                    print(f"   文件: {input_file.name}")
                    print(f"   尺寸: {input_info['size'][0]}×{input_info['size'][1]}")
                    print(f"   大小: {input_info['file_size']/1024:.1f}KB")
                    
                    # 计算放大倍数
                    scale_x = output_info['size'][0] / input_info['size'][0]
                    scale_y = output_info['size'][1] / input_info['size'][1]
                    print(f"📈 放大倍数: {scale_x:.1f}x × {scale_y:.1f}x")
        
        elif task_name in ['swinir_gray_dn_noise25', 'swinir_color_dn_noise25']:
            # 图像去噪：输入是原始图片
            if task_name == 'swinir_gray_dn_noise25':
                input_file = Path(f"testsets/Set12/{base_name}.png")
            else:
                input_file = Path(f"testsets/McMaster/{base_name}.tif")
            
            if input_file.exists():
                input_info = get_image_info(input_file)
                if 'error' not in input_info:
                    print(f"📥 原始图片 (添加噪声前):")
                    print(f"   文件: {input_file.name}")
                    print(f"   尺寸: {input_info['size'][0]}×{input_info['size'][1]}")
                    print(f"   模式: {input_info['mode']}")
                    print(f"   大小: {input_info['file_size']/1024:.1f}KB")
                    print(f"🔧 处理: 添加σ=25高斯噪声 → SwinIR去噪")
        
        elif task_name == 'swinir_color_jpeg_car_jpeg30':
            # JPEG压缩伪影减少
            input_file = Path(f"testsets/classic5/{base_name}.bmp")
            
            if input_file.exists():
                input_info = get_image_info(input_file)
                if 'error' not in input_info:
                    print(f"📥 原始图片 (JPEG压缩前):")
                    print(f"   文件: {input_file.name}")
                    print(f"   尺寸: {input_info['size'][0]}×{input_info['size'][1]}")
                    print(f"   模式: {input_info['mode']}")
                    print(f"   大小: {input_info['file_size']/1024:.1f}KB")
                    print(f"🔧 处理: JPEG压缩(Q=30) → SwinIR伪影减少")

def main():
    """主函数"""
    print("🎯 SwinIR 处理结果详细对比")
    print("基于现有测试数据的图像复原效果展示")
    
    # 定义所有任务
    tasks = {
        'swinir_classical_sr_x4': {
            'name': '经典4x图像超分辨率',
            'description': 'Set5数据集，将64×64低分辨率图像放大到256×256高分辨率'
        },
        'swinir_real_sr_x4': {
            'name': '真实世界4x图像超分辨率', 
            'description': '处理真实降质图像的4x超分辨率，适用于复杂的真实世界场景'
        },
        'swinir_gray_dn_noise25': {
            'name': '灰度图像去噪 (σ=25)',
            'description': '去除灰度图像中的高斯噪声，噪声标准差σ=25'
        },
        'swinir_color_dn_noise25': {
            'name': '彩色图像去噪 (σ=25)',
            'description': '去除彩色图像中的高斯噪声，噪声标准差σ=25'
        },
        'swinir_color_jpeg_car_jpeg30': {
            'name': '彩色JPEG压缩伪影减少 (Q=30)',
            'description': '减少JPEG压缩产生的块效应和振铃伪影，质量因子Q=30'
        }
    }
    
    # 显示每个任务的对比结果
    for task_name, task_info in tasks.items():
        display_task_comparison(task_name, task_info, max_samples=2)
    
    # 总结
    print(f"\n{'='*60}")
    print("📊 处理结果总结")
    print(f"{'='*60}")
    
    total_processed = 0
    results_dir = Path("results")
    
    for task_name in tasks.keys():
        task_dir = results_dir / task_name
        if task_dir.exists():
            count = len(list(task_dir.glob("*_SwinIR.*")))
            total_processed += count
            print(f"✅ {tasks[task_name]['name']}: {count}张图片")
    
    print(f"\n🎉 总计成功处理: {total_processed}张图片")
    print(f"📁 所有结果保存在: results/ 目录")
    print(f"🌐 HTML报告: SwinIR_结果对比报告.html")
    
    print(f"\n💡 查看建议:")
    print(f"   1. 直接查看results/目录下的处理结果")
    print(f"   2. 对比testsets/中的原始图片")
    print(f"   3. 在浏览器中打开HTML报告查看可视化对比")

if __name__ == "__main__":
    main()
