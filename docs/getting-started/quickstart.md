---
title: 安装与首次生成
description: 安装 LightX2V，下载 Wan2.1 模型，运行第一个视频生成示例。
---

# 安装与首次生成

<p class="lx-page-lead">从环境准备到一段生成的视频，走通 LightX2V 的基本使用流程。</p>

本页以 **Wan2.1-T2V-1.3B** 为例。所有推理命令均在 LightX2V 仓库根目录运行。其他模型的入口见[模型总览](../models/index.md)。

## 开始之前

| 项目 | 本教程使用的环境 |
| --- | --- |
| 操作系统 | Linux；Windows 用户可参考[专用指南](../deploy_guides/deploy_local_windows.md) |
| GPU | NVIDIA GPU，驱动与所选 CUDA 环境兼容 |
| Python | 3.10 或更高版本；本页 Conda 示例使用 3.11 |
| 资源 | 显存、内存和磁盘需求随模型及配置变化，预留模型权重与输出空间 |

!!! tip "已有可用环境？"
    直接前往[下载模型](#download-model)。显存受限时，结合[低资源部署指南](../deploy_guides/for_low_resource.md)选择配置。

## 1. 准备运行环境

先在宿主机获取仓库。已有仓库时直接进入其根目录。

```bash
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

=== "Docker（推荐）"

    使用仓库安装指南中的 CUDA 13.0 镜像示例。启动前需安装 Docker 和 NVIDIA Container Toolkit，并确认宿主机驱动兼容该镜像。

    ```bash
    docker pull lightx2v/lightx2v:26052801-cu130

    docker run --gpus all -it --ipc=host --name lightx2v \
      -v "$PWD":/workspace/LightX2V \
      -w /workspace/LightX2V \
      --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
    ```

    在容器中安装当前仓库：

    ```bash
    pip install -v -e .
    ```

    后续命令均在容器内执行。镜像的其他 CUDA 版本和国内镜像源见[完整安装指南](../getting_started/quickstart.md)。

=== "Conda"

    创建环境，并在仓库根目录安装依赖与代码：

    ```bash
    conda create -n lightx2v python=3.11 -y
    conda activate lightx2v
    pip install -v -e .
    ```

    然后按照[完整安装指南](../getting_started/quickstart.md)安装与 GPU、CUDA、PyTorch 匹配的注意力算子。使用量化模型时，还需安装对应量化算子。

    安装完成后检查是否能导入：

    ```bash
    python -c 'import lightx2v; print(lightx2v.__version__)'
    ```

## 2. 下载模型 { #download-model }

使用 Hugging Face CLI 下载完整的模型目录。将路径替换为你实际存放模型的位置。

```bash
hf download Wan-AI/Wan2.1-T2V-1.3B \
  --local-dir /path/to/models/Wan2.1-T2V-1.3B
```

如果环境中没有 `hf` 命令，可先安装 CLI：

```bash
pip install -U huggingface_hub
```

也可通过 ModelScope 下载同名模型，并将下载后的目录作为 `model_path`。

## 3. 配置生成参数

打开仓库内的 [`scripts/wan/run_wan_t2v.sh`](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_t2v.sh)，修改以下设置：

| 设置 | 如何填写 |
| --- | --- |
| `lightx2v_path` | 当前仓库的绝对路径 |
| `model_path` | 刚刚下载的模型目录绝对路径 |
| `CUDA_VISIBLE_DEVICES` | 使用的 GPU 编号，例如 `0` |
| `--prompt` | 想要生成的场景描述 |
| `--negative_prompt` | 希望避免出现的内容 |
| `--size` | 按“高 宽”填写；示例脚本为 `480 832` |
| `--num_frames` | 输出帧数；示例脚本为 `81` |
| `--save_result_path` | 生成的视频保存位置 |

采样步数、引导强度和注意力算子等启动设置由 [`configs/wan/wan_t2v.json`](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v.json) 配置。

!!! warning "检查注意力算子"
    该 JSON 使用 `flash_attn3`。运行前请根据显卡与安装环境选择支持的算子，详见[注意力机制指南](../method_tutorials/attention.md)。

??? info "脚本参数与 JSON 的优先级"
    脚本显式传入的 `--size` 和 `--num_frames` 会覆盖 JSON 中的同名默认值。若希望由 JSON 统一控制，先删除脚本中的这两个参数，再设置 JSON 的 `size`（`[高, 宽]`）与 `num_frames`。

## 4. 运行并查看结果

```bash
bash scripts/wan/run_wan_t2v.sh
```

推理完成后，打开 `--save_result_path` 指定的视频。脚本默认输出到：

```text
save_results/output_lightx2v_wan_t2v.mp4
```

## 下一步

继续使用 Wan 时，可进入 [Wan2.1 与 VACE 指南](../models/wan.md)选择其他任务、蒸馏配置或服务入口；也可以查看 [Wan2.2](../models/wan22.md) 和 [Qwen-Image-2.1](../models/qwen-image-2.1.md) 的使用路径。

<div class="grid cards" markdown>

-   :material-view-grid-outline: **尝试其他模型**

    按视频、图像、超分或交互任务查找示例。

    [打开模型总览](../models/index.md)

-   :material-code-braces: **接入 Python 应用**

    创建 Pipeline，复用已加载的模型进行生成。

    [阅读 Python API](../getting_started/python_api.md)

</div>
