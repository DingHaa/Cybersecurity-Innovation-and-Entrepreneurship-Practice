#!/usr/bin/env python3
"""
SwinIR 结果查看工具
对比处理前后的图片效果，生成简单的HTML报告
"""

import os
from pathlib import Path
import base64
from PIL import Image
import io

def encode_image_to_base64(image_path):
    """将图片编码为base64字符串"""
    try:
        with Image.open(image_path) as img:
            # 如果图片太大，调整大小
            if max(img.size) > 800:
                try:
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                except AttributeError:
                    # 兼容旧版本PIL
                    img.thumbnail((800, 800), Image.LANCZOS)
            
            # 转换为RGB模式（如果需要）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 保存为base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"处理图片失败 {image_path}: {e}")
        return None

def analyze_results():
    """分析结果目录"""
    results_dir = Path("results")
    if not results_dir.exists():
        print("❌ 结果目录不存在")
        return {}
    
    results = {}
    
    # 经典超分辨率结果
    classical_sr_dir = results_dir / "swinir_classical_sr_x4"
    if classical_sr_dir.exists():
        results['classical_sr'] = {
            'name': '经典4x图像超分辨率',
            'description': 'Set5数据集，5张经典测试图片的4x超分辨率结果',
            'input_dir': Path("testsets/Set5/LR_bicubic/X4"),
            'gt_dir': Path("testsets/Set5/HR"),
            'output_dir': classical_sr_dir,
            'images': []
        }
        
        # 匹配输入输出图片
        for output_file in classical_sr_dir.glob("*_SwinIR.png"):
            base_name = output_file.stem.replace("_SwinIR", "")
            input_file = results['classical_sr']['input_dir'] / f"{base_name}x4.png"
            gt_file = results['classical_sr']['gt_dir'] / f"{base_name}.png"
            
            if input_file.exists() and gt_file.exists():
                results['classical_sr']['images'].append({
                    'name': base_name,
                    'input': input_file,
                    'gt': gt_file,
                    'output': output_file
                })
    
    # 真实世界超分辨率结果
    real_sr_dir = results_dir / "swinir_real_sr_x4"
    if real_sr_dir.exists():
        results['real_sr'] = {
            'name': '真实世界4x图像超分辨率',
            'description': 'RealSRSet数据集，25张真实降质图片的4x超分辨率结果',
            'input_dir': Path("testsets/RealSRSet+5images"),
            'output_dir': real_sr_dir,
            'images': []
        }
        
        # 匹配输入输出图片
        for output_file in real_sr_dir.glob("*_SwinIR.png"):
            base_name = output_file.stem.replace("_SwinIR", "")
            # 尝试不同的扩展名
            input_file = None
            for ext in ['.png', '.jpg']:
                candidate = results['real_sr']['input_dir'] / f"{base_name}{ext}"
                if candidate.exists():
                    input_file = candidate
                    break
            
            if input_file:
                results['real_sr']['images'].append({
                    'name': base_name,
                    'input': input_file,
                    'output': output_file
                })
    
    # 灰度去噪结果
    gray_dn_dir = results_dir / "swinir_gray_dn_noise25"
    if gray_dn_dir.exists():
        results['gray_dn'] = {
            'name': '灰度图像去噪 (noise25)',
            'description': 'Set12数据集，12张灰度图片的去噪结果',
            'input_dir': Path("testsets/Set12"),
            'output_dir': gray_dn_dir,
            'images': []
        }
        
        # 匹配输入输出图片
        for output_file in gray_dn_dir.glob("*_SwinIR.png"):
            base_name = output_file.stem.replace("_SwinIR", "")
            input_file = results['gray_dn']['input_dir'] / f"{base_name}.png"
            
            if input_file.exists():
                results['gray_dn']['images'].append({
                    'name': base_name,
                    'input': input_file,
                    'output': output_file
                })
    
    # 彩色去噪结果
    color_dn_dir = results_dir / "swinir_color_dn_noise25"
    if color_dn_dir.exists():
        results['color_dn'] = {
            'name': '彩色图像去噪 (noise25)',
            'description': 'McMaster数据集，18张彩色图片的去噪结果',
            'input_dir': Path("testsets/McMaster"),
            'output_dir': color_dn_dir,
            'images': []
        }
        
        # 匹配输入输出图片
        for output_file in color_dn_dir.glob("*_SwinIR.png"):
            base_name = output_file.stem.replace("_SwinIR", "")
            input_file = results['color_dn']['input_dir'] / f"{base_name}.tif"
            
            if input_file.exists():
                results['color_dn']['images'].append({
                    'name': base_name,
                    'input': input_file,
                    'output': output_file
                })
    
    # JPEG压缩伪影减少结果
    jpeg_car_dir = results_dir / "swinir_color_jpeg_car_jpeg30"
    if jpeg_car_dir.exists():
        results['jpeg_car'] = {
            'name': '彩色JPEG压缩伪影减少 (quality30)',
            'description': 'classic5数据集，5张经典图片的JPEG伪影减少结果',
            'input_dir': Path("testsets/classic5"),
            'output_dir': jpeg_car_dir,
            'images': []
        }
        
        # 匹配输入输出图片
        for output_file in jpeg_car_dir.glob("*_SwinIR.png"):
            base_name = output_file.stem.replace("_SwinIR", "")
            input_file = results['jpeg_car']['input_dir'] / f"{base_name}.bmp"
            
            if input_file.exists():
                results['jpeg_car']['images'].append({
                    'name': base_name,
                    'input': input_file,
                    'output': output_file
                })
    
    return results

def generate_html_report(results, max_images_per_task=3):
    """生成HTML报告"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SwinIR 处理结果对比</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .task-section { background: white; margin-bottom: 30px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .task-title { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        .task-description { color: #666; margin-bottom: 20px; }
        .image-comparison { display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }
        .image-group { flex: 1; min-width: 300px; }
        .image-item { margin-bottom: 15px; }
        .image-label { font-weight: bold; margin-bottom: 5px; color: #555; }
        .image-container { border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }
        .image-container img { width: 100%; height: auto; display: block; }
        .stats { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 20px; }
        .stats-item { display: inline-block; margin-right: 20px; }
        .footer { text-align: center; margin-top: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SwinIR 处理结果对比报告</h1>
            <p>基于现有测试数据的图像复原效果展示</p>
        </div>
"""
    
    for task_id, task_info in results.items():
        if not task_info['images']:
            continue
            
        html_content += f"""
        <div class="task-section">
            <h2 class="task-title">{task_info['name']}</h2>
            <p class="task-description">{task_info['description']}</p>
"""
        
        # 只显示前几张图片
        images_to_show = task_info['images'][:max_images_per_task]
        
        for img_info in images_to_show:
            html_content += f"""
            <div class="image-comparison">
                <div class="image-group">
                    <div class="image-item">
                        <div class="image-label">输入图片: {img_info['name']}</div>
                        <div class="image-container">
"""
            
            # 编码输入图片
            input_b64 = encode_image_to_base64(img_info['input'])
            if input_b64:
                html_content += f'<img src="{input_b64}" alt="输入图片">'
            
            html_content += """
                        </div>
                    </div>
                </div>
"""
            
            # 如果有GT图片（经典超分辨率）
            if 'gt' in img_info:
                html_content += """
                <div class="image-group">
                    <div class="image-item">
                        <div class="image-label">真实高分辨率 (GT)</div>
                        <div class="image-container">
"""
                gt_b64 = encode_image_to_base64(img_info['gt'])
                if gt_b64:
                    html_content += f'<img src="{gt_b64}" alt="GT图片">'
                
                html_content += """
                        </div>
                    </div>
                </div>
"""
            
            # 输出图片
            html_content += """
                <div class="image-group">
                    <div class="image-item">
                        <div class="image-label">SwinIR 处理结果</div>
                        <div class="image-container">
"""
            
            output_b64 = encode_image_to_base64(img_info['output'])
            if output_b64:
                html_content += f'<img src="{output_b64}" alt="处理结果">'
            
            html_content += """
                        </div>
                    </div>
                </div>
            </div>
"""
        
        # 统计信息
        total_images = len(task_info['images'])
        html_content += f"""
            <div class="stats">
                <div class="stats-item"><strong>总图片数:</strong> {total_images}</div>
                <div class="stats-item"><strong>显示数量:</strong> {len(images_to_show)}</div>
                <div class="stats-item"><strong>输出目录:</strong> {task_info['output_dir']}</div>
            </div>
        </div>
"""
    
    html_content += """
        <div class="footer">
            <p>📊 报告生成时间: """ + str(Path().cwd()) + """</p>
            <p>💡 提示: 可以在浏览器中查看完整的对比效果</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def main():
    """主函数"""
    print("🔍 分析SwinIR处理结果...")
    
    results = analyze_results()
    if not results:
        print("❌ 未找到处理结果")
        return
    
    print(f"✅ 找到 {len(results)} 个任务的结果:")
    total_images = 0
    for task_id, task_info in results.items():
        image_count = len(task_info['images'])
        total_images += image_count
        print(f"   - {task_info['name']}: {image_count} 张图片")
    
    print(f"\n📊 总计处理了 {total_images} 张图片")
    
    # 生成HTML报告
    print("\n📝 生成HTML对比报告...")
    html_content = generate_html_report(results)
    
    report_path = Path("SwinIR_结果对比报告.html")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 报告已生成: {report_path}")
    print(f"💡 在浏览器中打开该文件即可查看对比效果")
    
    # 显示简单的文本统计
    print(f"\n📋 处理结果统计:")
    print("-" * 50)
    for task_id, task_info in results.items():
        print(f"\n🎯 {task_info['name']}")
        print(f"   描述: {task_info['description']}")
        print(f"   图片数量: {len(task_info['images'])}")
        print(f"   输出目录: {task_info['output_dir']}")
        
        # 显示前3张图片的文件名
        for i, img_info in enumerate(task_info['images'][:3]):
            print(f"   [{i+1}] {img_info['name']}")
        
        if len(task_info['images']) > 3:
            print(f"   ... 还有 {len(task_info['images'])-3} 张图片")

if __name__ == "__main__":
    main()
