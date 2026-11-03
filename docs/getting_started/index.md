---
title: 安装与首次生成
description: 安装 LightX2V，下载 Wan2.1 模型，用一组连续命令生成第一个视频。
---

# 安装与首次生成

<a id="生成第一个视频"></a>
<p class="lx-page-lead">用 Wan2.1-T2V-1.3B，从一句提示词生成第一个视频。</p>

<div class="lx-run-summary" markdown>

**本次运行** <span>文本生成视频</span><span>480 × 832 · 81 帧</span><span>单张 NVIDIA GPU</span>

</div>

<a id="开始之前"></a>
本教程面向 **Linux + 支持 BF16 的 NVIDIA GPU**，使用 Docker 准备环境。需先安装 Docker 和 NVIDIA Container Toolkit，且驱动兼容所选镜像的 CUDA 13.0。使用 Conda、其他 CUDA 版本或 Windows，请先完成[完整安装指南](installation.md)。

已有 LightX2V 环境？直接从[下载模型](#download-model)开始。以下命令均在 **LightX2V 仓库根目录**执行。

<nav class="lx-guide-path lx-quickstart-path" aria-label="首次生成流程" markdown>

1. [**准备环境**<span>进入容器，检查 GPU。</span>](#1-准备运行环境)
2. [**下载模型**<span>获取完整的 1.3B 权重。</span>](#download-model)
3. [**生成视频**<span>运行命令，查看输出。</span>](#3-配置生成参数)

</nav>

## 1. 准备运行环境

在宿主机下载仓库，已有仓库则进入对应目录：

```bash
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

启动容器；首次运行会自动下载镜像：

```bash
docker run --gpus all -it --ipc=host \
  -v "$PWD":/workspace/LightX2V \
  -w /workspace/LightX2V \
  --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
```

**后续命令在容器内执行。** 安装当前仓库：

```bash
python -m pip install -v -e .
```

检查 GPU 是否可用：

```bash
python - <<'PYTHON'
import torch
assert torch.cuda.is_available(), "CUDA is not available"
assert torch.cuda.is_bf16_supported(), "This example requires BF16 support"
print("GPU:", torch.cuda.get_device_name(0))
print("PyTorch:", torch.__version__, "CUDA:", torch.version.cuda)
print("VRAM (GiB):", round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1))
PYTHON
```

??? info "需要多少显存和内存？"
    本例使用原版 1.3B 权重，并启用 CPU 卸载以降低 GPU 显存占用，主机内存需容纳卸载的权重和缓冲区。实际占用随 PyTorch、算子、尺寸和帧数变化；1.3B 仅指生成模型的参数规模，不包含文本编码器与 VAE，不能据此估算整个流程的显存需求。

    模型下载与解压也需要磁盘空间。资源受限时，请先阅读[低资源部署](../deploy_guides/for_low_resource.md)，不要直接套用面向其他权重的量化或蒸馏配置。

## 2. 下载模型 { #download-model }

<a id="下载模型"></a>
安装下载工具，获取包含文本编码器和 VAE 的完整模型目录：

```bash
python -m pip install -U huggingface_hub
hf download Wan-AI/Wan2.1-T2V-1.3B \
  --local-dir models/Wan2.1-T2V-1.3B
```

已有权重时可跳过下载，将下方命令中的 `--model_path` 改为实际目录。也可通过 ModelScope 下载同名模型。

## 3. 生成视频 { #3-配置生成参数 }

<a id="配置并运行"></a>
### 准备入门配置

复制仓库配置，使用 PyTorch 自带的 `torch_sdpa` 注意力实现，并开启 CPU 卸载。新配置写入独立文件，原配置保留。

```bash
python - <<'PYTHON'
import json
from pathlib import Path
config = json.loads(Path("configs/wan/wan_t2v.json").read_text())
config.update(
    self_attn_1_type="torch_sdpa",
    cross_attn_1_type="torch_sdpa",
    cpu_offload=True,
    offload_granularity="block",
    t5_cpu_offload=True,
    vae_cpu_offload=True,
)
Path("configs/wan/wan_t2v_quickstart.json").write_text(json.dumps(config, indent=2))
PYTHON
```

本例无需额外安装 FlashAttention。CPU 卸载会增加数据搬运时间；跑通后可根据显卡选择[注意力算子](../method_tutorials/attention.md)与[加速方案](../method_tutorials/index.md)。

### 运行生成

```bash
mkdir -p save_results
CUDA_VISIBLE_DEVICES=0 python -m lightx2v.infer \
  --model_cls wan2.1 \
  --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/wan/wan_t2v_quickstart.json \
  --prompt "A cat walking on a sunny beach." \
  --negative_prompt "blurry, low quality" \
  --size 480 832 \
  --num_frames 81 \
  --seed 42 \
  --save_result_path save_results/first_video.mp4
```

<a id="4-运行并查看结果"></a>
### 查看结果

推理完成后，打开仓库中的 **`save_results/first_video.mp4`**。在远程服务器运行时，将文件下载到本机播放。首次运行包含模型加载，耗时随硬件和配置变化。

修改 `--prompt` 可以更换场景，`--seed` 控制随机种子。命令中的 `--size`（高、宽）与 `--num_frames` 会覆盖 JSON 中的同名默认值；其他生成参数见 [Wan2.1 指南](../models/wan.md)。

## 遇到问题

| 现象 | 先检查这里 |
| --- | --- |
| GPU 检查失败 | 在宿主机运行 `nvidia-smi`，检查驱动与容器的 GPU 挂载；参考[安装指南](installation.md) |
| 找不到模型文件 | 确认下载完成，`--model_path` 指向完整模型目录 |
| `CUDA out of memory` | 确认使用本页生成的配置，并检查其他进程占用；更多方法见[低资源部署](../deploy_guides/for_low_resource.md) |
| 进程被系统终止（`Killed`） | 查看主机内存是否不足；CPU 卸载仍需要足够内存 |

<a id="继续使用"></a>
## 下一步

<div class="lx-next-links" markdown>

[**换一个模型**<span>视频、图像编辑、超分与交互任务。</span>](../models/index.md)
[**提升推理效率**<span>选择量化、蒸馏、缓存或并行方案。</span>](../method_tutorials/index.md)
[**接入应用**<span>复用 Pipeline，调用 Python API。</span>](python_api.md)

</div>
