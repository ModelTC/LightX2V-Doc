# Qwen-Image-2.1 Deployment Guide

Generate images from text, or edit reference images with a prompt. The standard and Turbo models use their own weights, scripts and sampling configurations.

## Reading path

1. [Choose a task and model](#choose-task): text-to-image or image editing, standard or Turbo.
2. [Prepare the environment](#2-environment-setup) and [weights](#1-model-download) for your GPU and model.
3. [Generate your first image](#first-run): set paths and output, then run the text-to-image example.
4. [Tune inference](#next-steps): see RTX 5090 configurations, quantization and parallel inference.
5. [Start a service](#4-service-deployment-and-api-usage): submit generation or editing requests with the clients.

<a id="choose-task"></a>

## Choose a task and model

| Model | Task entry points | Default configuration |
| --- | --- | --- |
| Qwen-Image-2.1 | [Text-to-image](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_t2i.sh) / [Image editing](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_i2i.sh) | [qwen_image_21.json](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21.json), 40 steps |
| Qwen-Image-2.1-Turbo | [Text-to-image](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_turbo_t2i.sh) / [Image editing](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_turbo_i2i.sh) | [qwen_image_21_turbo.json](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21_turbo.json), 8 steps |

Image editing also requires a reference image in `--image_path`. Turbo uses its matching weights and sampling schedule: switch the model directory, script and JSON together. For quantized and multi-GPU entry points, see the [RTX 5090 examples](#32-rtx-5090-examples).

## 1. Model Download

Download the official weights from [Qwen/Qwen-Image-2.1](https://huggingface.co/Qwen/Qwen-Image-2.1):

```bash
hf download Qwen/Qwen-Image-2.1 --local-dir Qwen/Qwen-Image-2.1
```

Download the Turbo weights from [Qwen/Qwen-Image-2.1-Turbo](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo):

```bash
hf download Qwen/Qwen-Image-2.1-Turbo --local-dir Qwen/Qwen-Image-2.1-Turbo
```

## 2. Environment Setup

For an existing environment, check dependencies against the [full installation guide](../getting_started/quickstart.md). General configurations use `flash_attn3`; see the [attention guide](../method_tutorials/attention.md) for backend selection. RTX 5090 uses its corresponding image and dedicated configurations below.

Choose the [LightX2V Docker image](https://hub.docker.com/r/lightx2v/lightx2v/tags) for your GPU. Pull the corresponding image in a working directory on the host:

```bash
# H100, A100, etc.
docker pull lightx2v/lightx2v:26062001

# RTX 5090
docker pull lightx2v/lightx2v:26062001-cu130-5090-fix-260921
```

Start a container using the selected image:

```bash
docker run --gpus all -itd --ipc=host --name [container_name] -v [mount_settings] --entrypoint /bin/bash [image_id]
```

Clone the LightX2V source inside the container:

```bash
git clone https://github.com/ModelTC/LightX2V.git
```

Run the following commands from the LightX2V repository root inside the container.

## 3. Offline Inference

<a id="first-run"></a>

### 3.1 General examples

For a first image with the standard model, use [qwen_image_21_t2i.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/qwen_image_21/qwen_image_21_t2i.sh). Prepare the environment and download `Qwen-Image-2.1`, then set `lightx2v_path` (absolute repository path), `model_path` (absolute model directory), and `CUDA_VISIBLE_DEVICES` (GPU ID). Run from the repository root. If you downloaded Turbo weights, use the [Turbo entry points](#qwen-image-21-turbo).

```bash
# Text-to-image
bash scripts/qwen_image_21/qwen_image_21_t2i.sh

# Image-to-image
bash scripts/qwen_image_21/qwen_image_21_i2i.sh
```

The standard text-to-image script defaults to `save_results/qwen_image_21_t2i.png` inside the repository; use the location specified by `--save_result_path`. Open the generated image and check the prompt, dimensions and output location before adjusting other settings.

Edit `--prompt`, `--image_path`, `--size`, `--seed`, and `--save_result_path` directly in the script as needed.

Use `--size HEIGHT WIDTH`. Both dimensions must be at least 32; non-multiples of 32 are rounded down automatically.

For image-to-image, remove the script's `--size` argument to determine the output size from the reference image's aspect ratio. The pixel count is approximately `resolution²` (`resolution` defaults to `1024` in the config), with each dimension rounded to the nearest multiple of 32.

Pass `--resolution 2048` to override the config for one request; omit it to use the config. The value must be a positive integer. It controls reference-image resizing and automatic output sizing; an explicit `--size` still determines the output dimensions.

The default config already enables the general optimization path: FlashAttention3, FlashInfer RoPE, Triton LayerNorm and modulation, fused QK RMSNorm, fused transformer-block operators, CFG-disabled inference, and OpenCV result saving.

### Qwen-Image-2.1-Turbo

Qwen-Image-2.1-Turbo is the official accelerated version of Qwen-Image-2.1. It supports text-to-image generation and image editing with 8 denoising steps.

Set `lightx2v_path`, `model_path` (the Qwen-Image-2.1-Turbo directory), and `CUDA_VISIBLE_DEVICES` in the scripts, then run:

```bash
# Text-to-image
bash scripts/qwen_image_21/qwen_image_21_turbo_t2i.sh

# Image-to-image
bash scripts/qwen_image_21/qwen_image_21_turbo_i2i.sh
```

For image-to-image, edit `--image_path` and `--prompt` as needed. The default input is the model's `assets/turbo-boat-input.png`.

### 3.2 RTX 5090 examples

The examples use these optimization techniques:

- FP8 DiT linears with FP16 accumulation and FP8 QwenVL language weights.
- SageAttention2 and FlashInfer RoPE.
- Triton LayerNorm/modulation, fused QK RMSNorm and transformer-block operators.
- Text encoder offload and VAE torch.compile.
- Ulysses SP, FP8 communication, grouped head parallelism, language TP and VAE parallelism.

Convert the DiT weights:

```bash
python tools/convert/converter.py \
    --source /path/to/Qwen-Image-2.1/transformer \
    --output /path/to/Qwen-Image-2.1-fp8-f16-accum \
    --output_name qwen_image_21_fp8_f16_accum \
    --model_type qwen_image_21_dit \
    --quantization_profile qwen-image-21-fp8-f16-accum \
    --quantized --linear_type fp8 --device cuda:0 --single_file
```

For QwenVL FP8 conversion, see the example in `convert_qwen_image_21_text_encoder_fp8` in [converter.py](https://github.com/ModelTC/LightX2V/blob/main/tools/convert/converter.py). Set `dit_quantized_ckpt` and `text_encoder_quantized_ckpt` in the corresponding JSON, and set the repository path, original model path and GPU IDs in the scripts.

```bash
# Single GPU, 1K: text-to-image / image-to-image
bash scripts/qwen_image_21/qwen_image_21_t2i_5090_1k.sh
bash scripts/qwen_image_21/qwen_image_21_i2i_5090_1k.sh

# Single GPU, 2K: text-to-image / image-to-image
bash scripts/qwen_image_21/qwen_image_21_t2i_5090_2k.sh
bash scripts/qwen_image_21/qwen_image_21_i2i_5090_2k.sh

# Dual GPU, 2K: text-to-image / image-to-image
bash scripts/qwen_image_21/qwen_image_21_t2i_5090_2k_sp2.sh
bash scripts/qwen_image_21/qwen_image_21_i2i_5090_2k_sp2.sh
```

| GPU | Task | Output resolution | End-to-end latency |
| --- | --- | ---: | ---: |
| RTX 5090 ×1 | T2I | 1024×1024 | **5.586 s** |
| RTX 5090 ×1 | I2I | 1024×1024 | **6.804 s** |
| RTX 5090 ×1 | T2I | 2048×2048 | **30.333 s** |
| RTX 5090 ×1 | I2I | 2048×2048 | **42.787 s** |
| RTX 5090 ×2 | T2I | 2048×2048 | **16.868 s** |
| RTX 5090 ×2 | I2I | 2048×2048 | **25.212 s** |

Tests use PyTorch 2.11.0+cu130, 40 steps, seed 42, CFG disabled, and the example prompts. I2I uses `assets/inputs/imgs/girl.png`, preprocessed at the corresponding resolution.

Latency is the median of three consecutive requests after the first request in the same instance; dual-GPU samples use the slower rank. End-to-end timing includes image saving and excludes model loading and one-time initialization.

Search the runtime log for **`RUN pipeline cost`** to find the pipeline latency in seconds.

## 4. Service Deployment and API Usage

Set the repository path, model path, and GPU ID in `server/start_server.sh`, then start the server:

```bash
bash scripts/qwen_image_21/server/start_server.sh
```

The default port is `8000`. The server supports both text-to-image and image-to-image requests.

Once the server is ready, open a new terminal in the same container and send requests:

```bash
# Text-to-image
python scripts/qwen_image_21/server/post_t2i.py

# Image-to-image
python scripts/qwen_image_21/server/post_i2i.py
```

Edit `url`, `message`, and `output_path` directly; for image-to-image, also set `image_path`. The scripts already specify `task: "t2i"` and `task: "i2i"`, respectively.

Service requests follow the same size rules. For automatic image-to-image sizing, remove `size` from `message`.

Set `"resolution": 2048` in `message` to override the startup config for that request; omit it or use `null` to keep the config. The image form endpoint and `/v1/images/generations` and `/v1/images/edits` also accept `resolution`.

<a id="next-steps"></a>

## Acceleration and deployment

| Goal | Model examples and general guides |
| --- | --- |
| Use Turbo | [Turbo examples](#qwen-image-21-turbo) with matching Turbo weights and configuration |
| Use quantization or two RTX 5090 GPUs | [RTX 5090 examples](#32-rtx-5090-examples), [model quantization](../method_tutorials/quantization.md), [parallel inference](../method_tutorials/parallel.md) |
| Understand offload settings | [Parameter offload](../method_tutorials/offload.md); see this model's RTX 5090 configurations for encoder offload settings |
| Use LoRA tools | [LoRA deployment and tools](../deploy_guides/lora_deploy.md), including extraction and reconstruction entry points for Qwen-Image 2.1 |
| Integrate an application | [Service deployment and API calls](#4-service-deployment-and-api-usage), [general service guide](../deploy_guides/deploy_service.md) |

## Recent Work: LightX2V APP (macOS)

Our recently released [LightX2V APP](https://github.com/ModelTC/LightX2V-Mac-App) is a native macOS app for Apple Silicon Macs running macOS 14 or later. It uses LightX2V to run [Qwen-Image-2.1-Turbo](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo) locally, with a graphical interface for text-to-image generation and image editing.

LightX2V APP also offers optional prompt enhancement with the accompanying [Qwen-Image-2.1-PE-T2I-GGUF-Q8_0](https://huggingface.co/lightx2v/Qwen-Image-2.1-PE-T2I-GGUF-Q8_0) and [Qwen-Image-2.1-PE-I2I-GGUF-Q8_0](https://huggingface.co/lightx2v/Qwen-Image-2.1-PE-I2I-GGUF-Q8_0) models.
