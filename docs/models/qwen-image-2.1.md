# Qwen-Image-2.1 部署指南

使用文本生成图像，或结合参考图与提示词编辑图像。标准版和 Turbo 使用各自的权重、脚本和采样配置。

示例脚本位于 [LightX2V 推理仓库](https://github.com/ModelTC/LightX2V)的 `scripts/qwen_image_21/` 目录，以下推理命令在该仓库根目录执行。

## 使用路径

1. [选择任务与版本](#choose-task)：确认文生图或图像编辑，以及标准版或 Turbo。
2. [准备环境](#2-环境安装)和[模型权重](#1-模型下载)：按 GPU 和模型版本选择。
3. [首次生成](#first-run)：设置脚本路径与输出，运行文生图示例。
4. [调整推理性能](#next-steps)：查看 RTX 5090 配置、量化与并行指南。
5. [接入推理服务](#4-服务化部署与-api-调用)：通过客户端提交文生图或图像编辑请求。

<a id="choose-task"></a>

## 选择任务与版本

| 模型版本 | 任务入口 | 默认配置 |
| --- | --- | --- |
| Qwen-Image-2.1 | [文生图](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_t2i.sh) / [图像编辑](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_i2i.sh) | [qwen_image_21.json](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21.json)，40 步 |
| Qwen-Image-2.1-Turbo | [文生图](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_turbo_t2i.sh) / [图像编辑](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_turbo_i2i.sh) | [qwen_image_21_turbo.json](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21_turbo.json)，8 步 |

图像编辑额外需要参考图 `--image_path`。Turbo 使用配套权重和采样时间表，切换版本时同时更换模型目录、脚本与 JSON。RTX 5090 的量化和多卡入口见 [RTX 5090 案例](#32-rtx-5090-案例)。

## 1. 模型下载

官方模型权重：[Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1)。下载命令：

```bash
hf download Qwen/Qwen-Image-2.1 --local-dir Qwen/Qwen-Image-2.1
```

Turbo 模型权重：[Qwen/Qwen-Image-2.1-Turbo](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo)。下载命令：

```bash
hf download Qwen/Qwen-Image-2.1-Turbo --local-dir Qwen/Qwen-Image-2.1-Turbo
```

## 2. 环境安装

已有运行环境时，按[完整安装指南](../getting_started/installation.md)检查依赖。通用配置使用 `flash_attn3`；算子选择见[注意力机制](../method_tutorials/attention.md)，RTX 5090 使用下文对应的镜像与专用配置。

根据 GPU 型号选择 [LightX2V Docker 镜像](https://hub.docker.com/r/lightx2v/lightx2v/tags)。在宿主机的工作目录中拉取对应镜像：

```bash
# H100, A100等
docker pull lightx2v/lightx2v:26062001

# RTX 5090
docker pull lightx2v/lightx2v:26062001-cu130-5090-fix-260921
```

使用所选镜像启动容器：

```bash
docker run --gpus all -itd --ipc=host --name [容器名] -v [挂载设置] --entrypoint /bin/bash [镜像id]
```

在容器内下载 LightX2V 源码：

```bash
git clone https://github.com/ModelTC/LightX2V.git
```

后续命令均在容器内的 LightX2V 仓库根目录执行。

## 3. 离线推理

<a id="first-run"></a>

### 3.1 通用案例

首次生成可使用标准版文生图入口 [qwen_image_21_t2i.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_t2i.sh)。完成上述环境准备并下载 `Qwen-Image-2.1` 后，修改对应 bash 脚本中的 `lightx2v_path`（仓库绝对路径）、`model_path`（模型根目录绝对路径）和 `CUDA_VISIBLE_DEVICES`（GPU 编号），再从仓库根目录运行。使用 Turbo 权重时，前往 [Turbo 入口](#qwen-image-21-turbo)。

```bash
# 文生图
bash scripts/qwen_image_21/qwen_image_21_t2i.sh

# 图生图
bash scripts/qwen_image_21/qwen_image_21_i2i.sh
```

标准版文生图脚本默认输出到仓库内的 `save_results/qwen_image_21_t2i.png`，以 `--save_result_path` 为准。打开生成图片，确认提示词、尺寸和保存位置符合预期后，再调整其他设置。

直接在脚本中修改提示词 `--prompt`、参考图 `--image_path`、尺寸 `--size`、种子 `--seed` 和输出路径 `--save_result_path`。

使用 `--size 高 宽`。宽高均须不小于 32，非 32 倍数会自动向下对齐。

图生图可删除脚本中的 `--size` 参数，按参考图比例自动确定输出尺寸。总像素数约为配置中的 `resolution²`（`resolution` 默认为 `1024`），宽高就近对齐到 32 的倍数。

传入 `--resolution 2048` 可仅为本次请求覆盖配置值，不传则使用配置。该值须为正整数，控制参考图缩放和自动输出尺寸；显式传入 `--size` 时，输出尺寸仍由 `--size` 决定。

默认配置已经启用通用优化路径：FlashAttention3、FlashInfer RoPE、Triton LayerNorm 与 modulation、融合 QK RMSNorm、融合 Transformer block 算子、关闭 CFG 的推理路径及 OpenCV 结果保存。

### Qwen-Image-2.1-Turbo

Qwen-Image-2.1-Turbo 是 Qwen-Image-2.1 的官方加速版本，支持文生图和图像编辑，仅需 8 步去噪推理。

先设置脚本中的 `lightx2v_path`、`model_path`（Qwen-Image-2.1-Turbo 模型目录）和 `CUDA_VISIBLE_DEVICES`，然后运行：

```bash
# 文生图
bash scripts/qwen_image_21/qwen_image_21_turbo_t2i.sh

# 图生图
bash scripts/qwen_image_21/qwen_image_21_turbo_i2i.sh
```

图生图按需修改 `--image_path` 和 `--prompt`，默认参考图为模型目录下的 `assets/turbo-boat-input.png`。

### 3.2 RTX 5090 案例

示例采用的优化技术包括：

- DiT FP8 linear 与 FP16 累加、QwenVL 语言栈 FP8。
- SageAttention2、FlashInfer RoPE。
- Triton LayerNorm/modulation、融合 QK RMSNorm 与 Transformer block 算子。
- 文本编码器 offload、VAE torch.compile。
- Ulysses SP、FP8 通信、分组 head parallel、文本 TP 和 VAE 并行。

转换 DiT 权重：

```bash
python tools/convert/converter.py \
    --source /path/to/Qwen-Image-2.1/transformer \
    --output /path/to/Qwen-Image-2.1-fp8-f16-accum \
    --output_name qwen_image_21_fp8_f16_accum \
    --model_type qwen_image_21_dit \
    --quantization_profile qwen-image-21-fp8-f16-accum \
    --quantized --linear_type fp8 --device cuda:0 --single_file
```

QwenVL FP8 转换命令见 [converter.py](https://github.com/ModelTC/LightX2V/blob/main/tools/convert/converter.py) 中 `convert_qwen_image_21_text_encoder_fp8` 的示例。在对应 JSON 中设置 `dit_quantized_ckpt`、`text_encoder_quantized_ckpt`；在脚本中设置仓库路径、原始模型路径和 GPU 编号。

```bash
# 单卡 1K：文生图 / 图生图
bash scripts/qwen_image_21/qwen_image_21_t2i_5090_1k.sh
bash scripts/qwen_image_21/qwen_image_21_i2i_5090_1k.sh

# 单卡 2K：文生图 / 图生图
bash scripts/qwen_image_21/qwen_image_21_t2i_5090_2k.sh
bash scripts/qwen_image_21/qwen_image_21_i2i_5090_2k.sh

# 双卡 2K：文生图 / 图生图
bash scripts/qwen_image_21/qwen_image_21_t2i_5090_2k_sp2.sh
bash scripts/qwen_image_21/qwen_image_21_i2i_5090_2k_sp2.sh
```

| GPU | 任务 | 输出分辨率 | 端到端耗时 |
| --- | --- | ---: | ---: |
| RTX 5090 ×1 | T2I | 1024×1024 | **5.586 s** |
| RTX 5090 ×1 | I2I | 1024×1024 | **6.804 s** |
| RTX 5090 ×1 | T2I | 2048×2048 | **30.333 s** |
| RTX 5090 ×1 | I2I | 2048×2048 | **42.787 s** |
| RTX 5090 ×2 | T2I | 2048×2048 | **16.868 s** |
| RTX 5090 ×2 | I2I | 2048×2048 | **25.212 s** |

测试使用 PyTorch 2.11.0+cu130，40 步、seed 42、关闭 CFG，提示词与示例脚本一致。I2I 使用 `assets/inputs/imgs/girl.png`，参考图按对应分辨率处理。

同一实例中首次请求后，连续三次请求取中位数；双卡每次取较慢 rank 的耗时。端到端耗时包含图片保存，不包含模型加载和一次性初始化。

运行时在日志中搜索 **`RUN pipeline cost`**，查看单次 pipeline 耗时，单位为秒。

## 4. 服务化部署与 API 调用

先修改 `server/start_server.sh` 中的仓库路径、模型路径和 GPU 编号，然后启动：

```bash
bash scripts/qwen_image_21/server/start_server.sh
```

默认端口为 `8000`，同一个服务支持文生图和图生图。

服务启动完成后，在同一容器新开终端并发送请求：

```bash
# 文生图
python scripts/qwen_image_21/server/post_t2i.py

# 图生图
python scripts/qwen_image_21/server/post_i2i.py
```

直接修改代码中的 `url`、`message`、`output_path`；图生图还需设置 `image_path`。两个脚本已分别设置 `task: "t2i"` 和 `task: "i2i"`。

服务请求使用相同的尺寸规则。图生图需自动确定尺寸时，删除 `message` 中的 `size` 字段。

在 `message` 中设置 `"resolution": 2048` 可仅为本次请求覆盖启动配置；省略或传 `null` 则使用配置。图片表单接口以及 `/v1/images/generations`、`/v1/images/edits` 也支持 `resolution`。

<a id="next-steps"></a>

## 继续优化与部署

| 目标 | 模型入口与通用指南 |
| --- | --- |
| 使用 Turbo | 本页 [Turbo 示例](#qwen-image-21-turbo)，使用匹配的 Turbo 权重与配置 |
| 在 RTX 5090 上使用量化或双卡 | 本页 [RTX 5090 案例](#32-rtx-5090-案例)、[模型量化](../method_tutorials/quantization.md)、[并行推理](../method_tutorials/parallel.md) |
| 理解卸载设置 | [参数卸载](../method_tutorials/offload.md)；具体编码器卸载设置参照本模型的 RTX 5090 配置 |
| 使用 LoRA 工具 | [LoRA 部署与相关工具](../deploy_guides/lora_deploy.md)，其中包含 Qwen-Image 2.1 提取与重建入口 |
| 接入应用 | 本页[服务化部署与 API 调用](#4-服务化部署与-api-调用)、[通用服务指南](../deploy_guides/deploy_service.md) |

## 近期工作：LightX2V APP（macOS）

我们近期推出的 [LightX2V APP](https://github.com/ModelTC/LightX2V-Mac-App) 是面向 Apple Silicon Mac 的原生 macOS 应用，适用于 macOS 14 及以上版本。APP 基于 LightX2V 在本地运行 [Qwen-Image-2.1-Turbo](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo)，通过图形界面完成文生图和图像编辑。

LightX2V APP 还提供可选提示词增强功能，支持配套的 [Qwen-Image-2.1-PE-T2I-GGUF-Q8_0](https://huggingface.co/lightx2v/Qwen-Image-2.1-PE-T2I-GGUF-Q8_0) 和 [Qwen-Image-2.1-PE-I2I-GGUF-Q8_0](https://huggingface.co/lightx2v/Qwen-Image-2.1-PE-I2I-GGUF-Q8_0) 模型。
