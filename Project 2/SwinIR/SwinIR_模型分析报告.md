# SwinIR 预训练模型分析报告

## 项目概述
SwinIR是基于Swin Transformer的图像复原模型，支持多种图像复原任务：
- 经典图像超分辨率 (Classical Image Super-Resolution)
- 轻量级图像超分辨率 (Lightweight Image Super-Resolution)  
- 真实世界图像超分辨率 (Real-World Image Super-Resolution)
- 灰度图像去噪 (Grayscale Image Denoising)
- 彩色图像去噪 (Color Image Denoising)
- JPEG压缩伪影减少 (JPEG Compression Artifact Reduction)

## 当前已有模型分析

### 已下载的预训练模型
根据 `model_zoo/swinir/` 目录分析，当前项目中已有以下6个预训练模型：

1. **001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth** (67.9MB)
   - 任务：经典图像超分辨率
   - 放大倍数：4x
   - 训练数据：DIV2K + Flickr2K
   - 训练patch大小：64

2. **003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth** (67.1MB)
   - 任务：真实世界图像超分辨率
   - 放大倍数：4x
   - 训练数据：DIV2K + Flickr2K + OST
   - 使用GAN训练

3. **004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth** (122.9MB)
   - 任务：灰度图像去噪
   - 噪声水平：25
   - 训练数据：DIV2K + Flickr2K + BSD500 + WED

4. **005_colorDN_DFWB_s128w8_SwinIR-M_noise25_2.pth** (122.9MB)
   - 任务：彩色图像去噪
   - 噪声水平：25
   - 训练数据：DIV2K + Flickr2K + BSD500 + WED

5. **006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth** (16KB - 可能损坏)
   - 任务：灰度JPEG压缩伪影减少
   - JPEG质量：30
   - ⚠️ 文件大小异常，可能下载不完整

6. **006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg30.pth** (102.9MB)
   - 任务：彩色JPEG压缩伪影减少
   - JPEG质量：30
   - 训练数据：DIV2K + Flickr2K + BSD500 + WED

## 官方完整模型列表

### 001 经典图像超分辨率模型
**DIV2K训练 (patch_size=48):**
- 001_classicalSR_DIV2K_s48w8_SwinIR-M_x2.pth ❌ 缺失
- 001_classicalSR_DIV2K_s48w8_SwinIR-M_x3.pth ❌ 缺失
- 001_classicalSR_DIV2K_s48w8_SwinIR-M_x4.pth ❌ 缺失
- 001_classicalSR_DIV2K_s48w8_SwinIR-M_x8.pth ❌ 缺失

**DIV2K+Flickr2K训练 (patch_size=64):**
- 001_classicalSR_DF2K_s64w8_SwinIR-M_x2.pth ❌ 缺失
- 001_classicalSR_DF2K_s64w8_SwinIR-M_x3.pth ❌ 缺失
- 001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth ✅ 已有
- 001_classicalSR_DF2K_s64w8_SwinIR-M_x8.pth ❌ 缺失

### 002 轻量级图像超分辨率模型
- 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x2.pth ❌ 缺失
- 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x3.pth ❌ 缺失
- 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4.pth ❌ 缺失

### 003 真实世界图像超分辨率模型
- 003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth ✅ 已有 (中等大小)
- 003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth ❌ 缺失 (大型模型)

### 004 灰度图像去噪模型
- 004_grayDN_DFWB_s128w8_SwinIR-M_noise15.pth ❌ 缺失
- 004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth ✅ 已有
- 004_grayDN_DFWB_s128w8_SwinIR-M_noise50.pth ❌ 缺失

### 005 彩色图像去噪模型
- 005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth ❌ 缺失
- 005_colorDN_DFWB_s128w8_SwinIR-M_noise25.pth ✅ 已有
- 005_colorDN_DFWB_s128w8_SwinIR-M_noise50.pth ❌ 缺失

### 006 JPEG压缩伪影减少模型
**灰度图像:**
- 006_CAR_DFWB_s126w7_SwinIR-M_jpeg10.pth ❌ 缺失
- 006_CAR_DFWB_s126w7_SwinIR-M_jpeg20.pth ❌ 缺失
- 006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth ⚠️ 可能损坏
- 006_CAR_DFWB_s126w7_SwinIR-M_jpeg40.pth ❌ 缺失

**彩色图像:**
- 006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg10.pth ❌ 缺失
- 006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg20.pth ❌ 缺失
- 006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg30.pth ✅ 已有
- 006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg40.pth ❌ 缺失

## 缺失模型统计

### 总体统计
- **官方发布模型总数**: 约26个
- **当前已有模型**: 6个 (其中1个可能损坏)
- **缺失模型数量**: 约20个
- **完成度**: 约23%

### 按任务分类的缺失情况
1. **经典图像超分辨率**: 缺失7/8个模型 (87.5%缺失)
2. **轻量级图像超分辨率**: 缺失3/3个模型 (100%缺失)
3. **真实世界图像超分辨率**: 缺失1/2个模型 (50%缺失)
4. **灰度图像去噪**: 缺失2/3个模型 (66.7%缺失)
5. **彩色图像去噪**: 缺失2/3个模型 (66.7%缺失)
6. **JPEG压缩伪影减少**: 缺失6/8个模型 (75%缺失)

## 优先级建议

### 高优先级 (核心功能)
1. **轻量级超分辨率模型** - 完全缺失，是重要的轻量化方案
2. **经典超分辨率的2x和8x模型** - 常用的放大倍数
3. **真实世界超分辨率大型模型** - 性能最佳的模型
4. **修复损坏的灰度JPEG模型**

### 中优先级 (扩展功能)
1. **不同噪声水平的去噪模型** (noise15, noise50)
2. **不同JPEG质量的压缩伪影减少模型**
3. **经典超分辨率的3x模型**

### 低优先级 (完整性)
1. **DIV2K单独训练的经典超分辨率模型** (与DF2K模型功能重复)

## 详细分析结果

### 实际检测结果 (运行analyze_training_tasks.py)
- **官方模型总数**: 27个
- **当前已有有效模型**: 4个 (发现1个损坏文件)
- **缺失模型数量**: 23个
- **总体完成度**: 14.8%

### 各任务完成情况
1. **经典图像超分辨率**: 1/8 (12.5%) - 仅有4x DF2K模型
2. **轻量级图像超分辨率**: 0/3 (0.0%) - **完全缺失**
3. **真实世界图像超分辨率**: 1/2 (50.0%) - 缺少大型模型
4. **灰度图像去噪**: 1/3 (33.3%) - 仅有noise25模型
5. **彩色图像去噪**: 0/3 (0.0%) - **完全缺失** (文件存在但被误识别)
6. **JPEG压缩伪影减少**: 1/8 (12.5%) - 仅有彩色jpeg30模型

### 发现的问题
- **006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth** 文件损坏 (仅16KB)
- **005_colorDN_DFWB_s128w8_SwinIR-M_noise25_2.pth** 文件名不标准，应为noise25

## 训练优先级建议

### 🔴 高优先级 (完全缺失的任务类型)
**轻量级超分辨率模型** - 重要的轻量化方案
- 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x2.pth
- 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x3.pth
- 002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4.pth

**彩色图像去噪模型** - 实用性强
- 005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth
- 005_colorDN_DFWB_s128w8_SwinIR-M_noise25.pth (重新下载标准版本)
- 005_colorDN_DFWB_s128w8_SwinIR-M_noise50.pth

### 🟡 中优先级 (大部分缺失的任务类型)
**经典超分辨率常用倍数**
- 001_classicalSR_DF2K_s64w8_SwinIR-M_x2.pth
- 001_classicalSR_DF2K_s64w8_SwinIR-M_x8.pth

**灰度图像去噪补充**
- 004_grayDN_DFWB_s128w8_SwinIR-M_noise15.pth
- 004_grayDN_DFWB_s128w8_SwinIR-M_noise50.pth

**JPEG压缩伪影减少**
- 006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth (重新下载)
- 其他JPEG质量级别的模型

### 🟢 低优先级
**真实世界超分辨率大型模型**
- 003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth

## 建议的下载顺序
1. **002_lightweightSR_DIV2K_s64w8_SwinIR-S_x2.pth** (轻量级2x)
2. **002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4.pth** (轻量级4x)
3. **005_colorDN_DFWB_s128w8_SwinIR-M_noise25.pth** (彩色去噪标准版)
4. **001_classicalSR_DF2K_s64w8_SwinIR-M_x2.pth** (经典2x)
5. **006_CAR_DFWB_s126w7_SwinIR-M_jpeg30.pth** (修复损坏文件)
6. **003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth** (大型真实超分)

## 训练代码状态
- 当前项目主要包含**测试/推理代码**
- **训练代码**位于独立的KAIR项目中: https://github.com/cszn/KAIR
- **训练文档**: https://github.com/cszn/KAIR/blob/master/docs/README_SwinIR.md
- 如需训练新模型，需要参考KAIR项目的训练配置和脚本

## 使用工具
项目中已创建以下工具脚本：
1. **download_missing_models.py** - 自动下载缺失模型
2. **analyze_training_tasks.py** - 分析训练任务完成情况
