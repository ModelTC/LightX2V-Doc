---
title: Installation and first generation
description: Install LightX2V, download Wan2.1, and generate your first video with a continuous set of commands.
---

# Installation and first generation

<a id="generate-your-first-video"></a>
<p class="lx-page-lead">Turn a text prompt into your first video with Wan2.1-T2V-1.3B.</p>

<div class="lx-run-summary" markdown>

**This example** <span>Text to video</span><span>480 × 832 · 81 frames</span><span>One NVIDIA GPU</span>

</div>

<a id="before-you-begin"></a>
This walkthrough uses **Linux and a BF16-capable NVIDIA GPU**, with Docker for setup. Install Docker and NVIDIA Container Toolkit first, and use a driver compatible with the image's CUDA 13.0 runtime. For Conda, another CUDA version, or Windows, follow the [full installation guide](installation.md) first.

Already have a LightX2V environment? Skip to [model download](#download-model). Run all commands from the **LightX2V repository root**.

<nav class="lx-guide-path lx-quickstart-path" aria-label="First generation steps" markdown>

1. [**Set up**<span>Enter the container and check the GPU.</span>](#1-prepare-the-environment)
2. [**Download**<span>Get the complete 1.3B model.</span>](#download-model)
3. [**Generate**<span>Run inference and open the output.</span>](#3-configure-generation)

</nav>

## 1. Prepare the environment

Clone the repository on the host, or enter your existing checkout:

```bash
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

Start the container. Docker downloads the image automatically on first use:

```bash
docker run --gpus all -it --ipc=host \
  -v "$PWD":/workspace/LightX2V \
  -w /workspace/LightX2V \
  --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
```

**Run the remaining commands inside the container.** Install the current checkout:

```bash
python -m pip install -v -e .
```

Check GPU availability:

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

??? info "How much GPU and host memory do I need?"
    This example uses the original 1.3B weights with CPU offload to reduce GPU memory use. Host memory must hold offloaded weights and buffers. Actual usage depends on PyTorch, attention backends, resolution, and frame count. The 1.3B parameter count excludes the text encoder and VAE, so it does not describe the memory requirements of the full pipeline.

    Leave disk space for model downloads and extraction. For constrained hardware, read the [low-resource guide](../deploy_guides/for_low_resource.md) before choosing quantization or distillation settings intended for different weights.

## 2. Download the model { #download-model }

<a id="download-the-model"></a>
Install the download tool, then fetch the complete model including its text encoder and VAE:

```bash
python -m pip install -U huggingface_hub
hf download Wan-AI/Wan2.1-T2V-1.3B \
  --local-dir models/Wan2.1-T2V-1.3B
```

If you already have the weights, skip the download and set `--model_path` below to your local directory. You can also download the same model through ModelScope.

## 3. Generate a video { #3-configure-generation }

<a id="configure-and-run"></a>
### Prepare a starter configuration

Copy the repository configuration, select PyTorch's built-in `torch_sdpa` attention, and enable CPU offload. This creates a separate configuration file and preserves the original.

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

This example does not need a separate FlashAttention installation. CPU offload adds transfer overhead; after your first run, choose an [attention backend](../method_tutorials/attention.md) and [acceleration approach](../method_tutorials/index.md) for your hardware.

### Run generation

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

<a id="4-run-and-inspect-the-result"></a>
### Open the result

When inference finishes, open **`save_results/first_video.mp4`** in the repository. If you ran on a remote server, download the file to play it locally. The first run includes model loading; runtime depends on your hardware and configuration.

Change `--prompt` to describe another scene and `--seed` to set the random seed. The command's `--size` (height, width) and `--num_frames` override the corresponding JSON defaults. See the [Wan2.1 guide](../models/wan.md) for more generation options.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| GPU check fails | Run `nvidia-smi` on the host and check driver compatibility and GPU access in Docker; see [installation](installation.md) |
| Missing model files | Check that the download finished and `--model_path` points to the complete model directory |
| `CUDA out of memory` | Use the configuration created above and check other GPU processes; see the [low-resource guide](../deploy_guides/for_low_resource.md) |
| Process exits with `Killed` | Check available host memory; CPU offload still needs sufficient RAM |

<a id="continue"></a>
## Next steps

<div class="lx-next-links" markdown>

[**Try another model**<span>Video, image editing, upscaling, and interaction.</span>](../models/index.md)
[**Improve efficiency**<span>Choose quantization, distillation, caching, or parallelism.</span>](../method_tutorials/index.md)
[**Build an application**<span>Reuse a pipeline with the Python API.</span>](python_api.md)

</div>
