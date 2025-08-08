# SwinIR: 基于 Swin Transformer 的图像复原
[Jingyun Liang](https://jingyunliang.github.io), [Jiezhang Cao](https://www.jiezhangcao.com/), [Guolei Sun](https://vision.ee.ethz.ch/people-details.MjYzMjMw.TGlzdC8zMjg5LC0xOTcxNDY1MTc4.html), [Kai Zhang](https://cszn.github.io/), [Luc Van Gool](https://scholar.google.com/citations?user=TwMib_QAAAAJ&hl=en), [Radu Timofte](http://people.ee.ethz.ch/~timofter/)

苏黎世联邦理工学院计算机视觉实验室

---

[![arXiv](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)](https://arxiv.org/abs/2108.10257)
[![GitHub Stars](https://img.shields.io/github/stars/JingyunLiang/SwinIR?style=social)](https://github.com/JingyunLiang/SwinIR)
[![download](https://img.shields.io/github/downloads/JingyunLiang/SwinIR/total.svg)](https://github.com/JingyunLiang/SwinIR/releases)
![visitors](https://visitor-badge.glitch.me/badge?page_id=jingyunliang/SwinIR)
[ <a href="https://colab.research.google.com/gist/JingyunLiang/a5e3e54bc9ef8d7bf594f6fee8208533/swinir-demo-on-real-world-image-sr.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="google colab logo"></a>](https://colab.research.google.com/gist/JingyunLiang/a5e3e54bc9ef8d7bf594f6fee8208533/swinir-demo-on-real-world-image-sr.ipynb)
<a href="https://replicate.ai/jingyunliang/swinir"><img src="https://img.shields.io/static/v1?label=Replicate&message=Demo and Docker Image&color=blue"></a>
[![PlayTorch Demo](https://github.com/facebookresearch/playtorch/blob/main/website/static/assets/playtorch_badge.svg)](https://playtorch.dev/snack/@playtorch/swinir/)
[Gradio Web Demo](https://huggingface.co/spaces/akhaliq/SwinIR)

本仓库是 SwinIR: Image Restoration Using Shifted Window Transformer 的官方 PyTorch 实现
([论文](https://arxiv.org/pdf/2108.10257.pdf), [补充材料](https://github.com/JingyunLiang/SwinIR/releases), [预训练模型](https://github.com/JingyunLiang/SwinIR/releases), [视觉结果](https://github.com/JingyunLiang/SwinIR/releases))。SwinIR 在以下任务上实现了**最先进的性能**：
- 双三次/轻量级/真实世界图像超分辨率
- 灰度/彩色图像去噪
- 灰度/彩色JPEG压缩伪影减少

## 🚀 最新消息

- **2022年8月16日**: 添加了在移动设备上运行真实世界图像超分辨率模型的 PlayTorch 演示 [![PlayTorch Demo](https://github.com/facebookresearch/playtorch/blob/main/website/static/assets/playtorch_badge.svg)](https://playtorch.dev/snack/@playtorch/swinir/)。
- **2022年8月1日**: 添加了彩色图像JPEG压缩伪影减少的预训练模型和结果。
- **2022年6月10日**: 查看我们在视频复原方面的工作 🔥🔥🔥 [VRT: A Video Restoration Transformer](https://github.com/JingyunLiang/VRT) 
[![GitHub Stars](https://img.shields.io/github/stars/JingyunLiang/VRT?style=social)](https://github.com/JingyunLiang/VRT)
[![download](https://img.shields.io/github/downloads/JingyunLiang/VRT/total.svg)](https://github.com/JingyunLiang/VRT/releases)
和 [RVRT: Recurrent Video Restoration Transformer](https://github.com/JingyunLiang/RVRT) 
[![GitHub Stars](https://img.shields.io/github/stars/JingyunLiang/RVRT?style=social)](https://github.com/JingyunLiang/RVRT)
[![download](https://img.shields.io/github/downloads/JingyunLiang/RVRT/total.svg)](https://github.com/JingyunLiang/RVRT/releases)
用于视频超分辨率、视频去模糊、视频去噪、视频帧插值和时空视频超分辨率。
- **2021年9月7日**: 我们提供了一个交互式在线 Colab 演示用于真实世界图像超分辨率 <a href="https://colab.research.google.com/gist/JingyunLiang/a5e3e54bc9ef8d7bf594f6fee8208533/swinir-demo-on-real-world-image-sr.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="google colab logo"></a>🔥 与 [第一个实用退化模型 BSRGAN (ICCV2021) ![GitHub Stars](https://img.shields.io/github/stars/cszn/BSRGAN?style=social)](https://github.com/cszn/BSRGAN) 和最近的模型 RealESRGAN 进行比较。在 Colab 上尝试超分辨率您自己的图像！

## 模型概述

> 图像复原是一个长期存在的低级视觉问题，旨在从低质量图像（例如，缩小、有噪声和压缩的图像）中恢复高质量图像。虽然最先进的图像复原方法基于卷积神经网络，但很少有人尝试使用在高级视觉任务上表现出色的 Transformer。在本文中，我们提出了一个基于 Swin Transformer 的强基线模型 SwinIR 用于图像复原。SwinIR 包含三个部分：浅层特征提取、深层特征提取和高质量图像重建。特别地，深层特征提取模块由几个残差 Swin Transformer 块（RSTB）组成，每个块有几个 Swin Transformer 层以及残差连接。我们在三个代表性任务上进行实验：图像超分辨率（包括经典、轻量级和真实世界图像超分辨率）、图像去噪（包括灰度和彩色图像去噪）和 JPEG 压缩伪影减少。实验结果表明，SwinIR 在不同任务上优于最先进的方法高达 0.14~0.45dB，而总参数数量可以减少高达 67%。

<p align="center">
  <img width="800" src="figs/SwinIR_archi.png">
</p>

## 📋 目录

1. [训练](#训练)
2. [测试](#测试)
3. [结果](#结果)
4. [引用](#引用)
5. [许可证和致谢](#许可证和致谢)

## 🏋️‍♂️ 训练

可以按照以下方式下载用于训练和测试的数据集：

| 任务 | 训练集 | 测试集 | 视觉结果 |
|:---|:---:|:---:|:---:|
| 经典/轻量级图像超分辨率 | [DIV2K](https://cv.snu.ac.kr/research/EDSR/DIV2K.tar) (800张训练图像) 或 DIV2K +[Flickr2K](https://cv.snu.ac.kr/research/EDSR/Flickr2K.tar) (2650张图像) | Set5 + Set14 + BSD100 + Urban100 + Manga109 [下载全部](https://drive.google.com/drive/folders/1B3DJGQKB6eNdwuQIhdskA64qUuVKLZ9u) | [这里](https://github.com/JingyunLiang/SwinIR/releases) |
| 真实世界图像超分辨率 | SwinIR-M (中等大小): [DIV2K](https://cv.snu.ac.kr/research/EDSR/DIV2K.tar) + [Flickr2K](https://cv.snu.ac.kr/research/EDSR/Flickr2K.tar) + [OST](https://openmmlab.oss-cn-hangzhou.aliyuncs.com/datasets/OST_dataset.zip) <br/> SwinIR-L (大尺寸): DIV2K + Flickr2K + OST + [WED](http://ivc.uwaterloo.ca/database/WaterlooExploration/exploration_database_and_code.rar) + [FFHQ](https://drive.google.com/drive/folders/1tZUcXDBeOibC6jcMCtgRRz67pzrAHeHL) + Manga109 + [SCUT-CTW1500](https://universityofadelaide.box.com/shared/static/py5uwlfyyytbb2pxzq9czvu6fuqbjdh8.zip) | [RealSRSet+5images](https://github.com/JingyunLiang/SwinIR/releases/download/v0.0/RealSRSet+5images.zip) | [这里](https://github.com/JingyunLiang/SwinIR/releases) |
| 彩色/灰度图像去噪 | [DIV2K](https://cv.snu.ac.kr/research/EDSR/DIV2K.tar) + [Flickr2K](https://cv.snu.ac.kr/research/EDSR/Flickr2K.tar) + [BSD500](http://www.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/BSR/BSR_bsds500.tgz) + [WED](http://ivc.uwaterloo.ca/database/WaterlooExploration/exploration_database_and_code.rar) | 灰度: Set12 + BSD68 + Urban100 <br/> 彩色: CBSD68 + Kodak24 + McMaster + Urban100 [下载全部](https://github.com/cszn/FFDNet/tree/master/testsets) | [这里](https://github.com/JingyunLiang/SwinIR/releases) |
| 灰度/彩色JPEG压缩伪影减少 | [DIV2K](https://cv.snu.ac.kr/research/EDSR/DIV2K.tar) + [Flickr2K](https://cv.snu.ac.kr/research/EDSR/Flickr2K.tar) + [BSD500](http://www.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/BSR/BSR_bsds500.tgz) + [WED](http://ivc.uwaterloo.ca/database/WaterlooExploration/exploration_database_and_code.rar) | 灰度: Classic5 +LIVE1 [下载全部](https://github.com/cszn/DnCNN/tree/master/testsets) | [这里](https://github.com/JingyunLiang/SwinIR/releases) |

训练代码位于 [KAIR](https://github.com/cszn/KAIR/blob/master/docs/README_SwinIR.md)。

## 🧪 测试（无需准备数据集）

为了您的方便，我们在 `/testsets` 中提供了一些示例数据集（约20Mb）。
如果您只想要代码，下载 `models/network_swinir.py`、`utils/util_calculate_psnr_ssim.py` 和 `main_test_swinir.py` 就足够了。
以下命令将**自动**下载[预训练模型](https://github.com/JingyunLiang/SwinIR/releases)并将它们放在 `model_zoo/swinir` 中。
**[SwinIR 的所有视觉结果可以在这里下载](https://github.com/JingyunLiang/SwinIR/releases)**。

我们还提供了一个[真实世界图像超分辨率在线 Colab 演示  <a href="https://colab.research.google.com/gist/JingyunLiang/a5e3e54bc9ef8d7bf594f6fee8208533/swinir-demo-on-real-world-image-sr.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="google colab logo"></a>](https://colab.research.google.com/gist/JingyunLiang/a5e3e54bc9ef8d7bf594f6fee8208533/swinir-demo-on-real-world-image-sr.ipynb) 与 [第一个实用退化模型 BSRGAN (ICCV2021)  ![GitHub Stars](https://img.shields.io/github/stars/cszn/BSRGAN?style=social)](https://github.com/cszn/BSRGAN) 和最近的模型 [RealESRGAN](https://github.com/xinntao/Real-ESRGAN) 进行比较。在 Colab 上尝试测试您自己的图像！

我们提供了一个 PlayTorch 演示 [![PlayTorch Demo](https://github.com/facebookresearch/playtorch/blob/main/website/static/assets/playtorch_badge.svg)](https://playtorch.dev/snack/@playtorch/swinir/) 用于真实世界图像超分辨率，展示如何在使用 React Native 构建的移动应用程序中运行 SwinIR 模型。

### 使用示例

```bash
# 001 经典图像超分辨率（中等大小）
# 注意 --training_patch_size 仅用于区分论文表2中的两种不同设置。图像不是逐块测试的。
# (设置1: 当模型在 DIV2K 上训练且 training_patch_size=48 时)
python main_test_swinir.py --task classical_sr --scale 2 --training_patch_size 48 --model_path model_zoo/swinir/001_classicalSR_DIV2K_s48w8_SwinIR-M_x2.pth --folder_lq testsets/Set5/LR_bicubic/X2 --folder_gt testsets/Set5/HR

# (设置2: 当模型在 DIV2K+Flickr2K 上训练且 training_patch_size=64 时)
python main_test_swinir.py --task classical_sr --scale 4 --training_patch_size 64 --model_path model_zoo/swinir/001_classicalSR_DF2K_s64w8_SwinIR-M_x4.pth --folder_lq testsets/Set5/LR_bicubic/X4 --folder_gt testsets/Set5/HR

# 002 轻量级图像超分辨率（小尺寸）
python main_test_swinir.py --task lightweight_sr --scale 4 --model_path model_zoo/swinir/002_lightweightSR_DIV2K_s64w8_SwinIR-S_x4.pth --folder_lq testsets/Set5/LR_bicubic/X4 --folder_gt testsets/Set5/HR

# 003 真实世界图像超分辨率（如果内存不足，使用 --tile 400）
# (中等大小)
python main_test_swinir.py --task real_sr --scale 4 --model_path model_zoo/swinir/003_realSR_BSRGAN_DFO_s64w8_SwinIR-M_x4_GAN.pth --folder_lq testsets/RealSRSet+5images --tile

# (更大尺寸 + 在更多数据集上训练)
python main_test_swinir.py --task real_sr --scale 4 --large_model --model_path model_zoo/swinir/003_realSR_BSRGAN_DFOWMFC_s64w8_SwinIR-L_x4_GAN.pth --folder_lq testsets/RealSRSet+5images

# 004 灰度图像去噪（中等大小）
python main_test_swinir.py --task gray_dn --noise 25 --model_path model_zoo/swinir/004_grayDN_DFWB_s128w8_SwinIR-M_noise25.pth --folder_gt testsets/Set12

# 005 彩色图像去噪（中等大小）
python main_test_swinir.py --task color_dn --noise 25 --model_path model_zoo/swinir/005_colorDN_DFWB_s128w8_SwinIR-M_noise25.pth --folder_gt testsets/McMaster

# 006 JPEG压缩伪影减少（中等大小，使用 window_size=7，因为JPEG编码使用8x8块）
# 灰度
python main_test_swinir.py --task jpeg_car --jpeg 20 --model_path model_zoo/swinir/006_CAR_DFWB_s126w7_SwinIR-M_jpeg20.pth --folder_gt testsets/classic5

# 彩色
python main_test_swinir.py --task color_jpeg_car --jpeg 20 --model_path model_zoo/swinir/006_colorCAR_DFWB_s126w7_SwinIR-M_jpeg20.pth --folder_gt testsets/LIVE1
```

## 📊 结果

我们在经典/轻量级/真实世界图像超分辨率、灰度/彩色图像去噪和JPEG压缩伪影减少方面取得了最先进的性能。详细结果可以在[论文](https://arxiv.org/abs/2108.10257)中找到。SwinIR 的所有视觉结果可以在[这里](https://github.com/JingyunLiang/SwinIR/releases)下载。

### 主要性能亮点

- **经典图像超分辨率**: 在多个数据集上比现有方法提升0.14~0.45dB
- **轻量级模型**: 参数量减少高达67%，同时保持优越性能
- **真实世界超分辨率**: 在实际降质图像上表现出色
- **图像去噪**: 在灰度和彩色图像去噪任务上均达到最先进水平
- **JPEG伪影减少**: 有效去除JPEG压缩产生的块效应和振铃伪影

<p align="center">
  <img width="800" src="figs/classic_image_sr_visual.png">
</p>

## 📚 引用

如果您发现我们的工作有用，请考虑引用：

```bibtex
@article{liang2021swinir,
  title={SwinIR: Image Restoration Using Swin Transformer},
  author={Liang, Jingyun and Cao, Jiezhang and Sun, Guolei and Zhang, Kai and Van Gool, Luc and Timofte, Radu},
  journal={arXiv preprint arXiv:2108.10257},
  year={2021}
}
```

## 📄 许可证和致谢

本项目根据 Apache 2.0 许可证发布。代码基于 [Swin Transformer](https://github.com/microsoft/Swin-Transformer) 和 [KAIR](https://github.com/cszn/KAIR)。请同时遵循它们的许可证。感谢他们的出色工作。

## 🔗 相关工作

- [Swin Transformer](https://github.com/microsoft/Swin-Transformer): 用于一般视觉任务的分层视觉Transformer
- [KAIR](https://github.com/cszn/KAIR): 图像复原工具箱
- [BSRGAN](https://github.com/cszn/BSRGAN): 实用的退化模型用于盲超分辨率
- [VRT](https://github.com/JingyunLiang/VRT): 视频复原Transformer
- [RVRT](https://github.com/JingyunLiang/RVRT): 循环视频复原Transformer

## 🤝 贡献

欢迎提交问题和拉取请求。对于重大更改，请先开启issue讨论您想要更改的内容。