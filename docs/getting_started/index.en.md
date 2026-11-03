---
title: Installation and first generation
description: Install LightX2V, download Wan2.1 and run your first video generation example.
---

# Installation and first generation

<p class="lx-page-lead">Go from environment setup to a generated video.</p>

This guide uses **Wan2.1-T2V-1.3B**. Run all inference commands from the LightX2V repository root. For other models, see the [model catalog](../models/index.md).

<nav class="lx-guide-path" aria-label="First generation workflow" markdown>

1. [**Set up**<span>Choose Docker or Conda.</span>](#1-prepare-the-environment)
2. [**Get the model**<span>Download the full Wan2.1 weights.</span>](#download-model)
3. [**Configure and run**<span>Set paths and generate a video.</span>](#3-configure-generation)

</nav>

## Before you begin

| Item | Environment used in this guide |
| --- | --- |
| Operating system | Linux; Windows users can follow the [dedicated guide](../deploy_guides/deploy_local_windows.md) |
| GPU | An NVIDIA GPU with drivers compatible with the selected CUDA environment |
| Python | 3.10 or newer; the Conda example below uses 3.11 |
| Resources | GPU memory, host memory and disk requirements depend on the model and configuration; allow space for weights and outputs |

!!! tip "Already have an environment?"
    Go straight to [downloading the model](#download-model). For limited GPU memory, choose a configuration from the [low-resource deployment guide](../deploy_guides/for_low_resource.md).

## 1. Prepare the environment

Clone the repository on the host, or enter the root of your existing checkout.

```bash title="Get the LightX2V repository"
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

=== "Docker (recommended)"

    This example uses the CUDA 13.0 image from the repository installation guide. Install Docker and NVIDIA Container Toolkit first, and check that the host driver supports the image.

    ```bash title="Host: pull the image and enter the container"
    docker pull lightx2v/lightx2v:26052801-cu130

    docker run --gpus all -it --ipc=host --name lightx2v \
      -v "$PWD":/workspace/LightX2V \
      -w /workspace/LightX2V \
      --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
    ```

    Install the checked-out repository inside the container:

    ```bash
    pip install -v -e .
    ```

    Run the remaining commands inside the container. Other CUDA image versions and mirrors are listed in the [full installation guide](installation.md).

=== "Conda"

    Create an environment and install the project from the repository root:

    ```bash title="Create and install the Conda environment"
    conda create -n lightx2v python=3.11 -y
    conda activate lightx2v
    pip install -v -e .
    ```

    Follow the [full installation guide](installation.md) to install attention kernels compatible with your GPU, CUDA and PyTorch. Quantized models also require the corresponding quantization kernels.

    Check that the package imports:

    ```bash
    python -c 'import lightx2v; print(lightx2v.__version__)'
    ```

## 2. Download the model { #download-model }

Use the Hugging Face CLI to download the complete model directory. Replace the path with your local model location.

```bash title="Download Wan2.1-T2V-1.3B"
hf download Wan-AI/Wan2.1-T2V-1.3B \
  --local-dir /path/to/models/Wan2.1-T2V-1.3B
```

If `hf` is not installed, install the CLI first:

```bash
pip install -U huggingface_hub
```

You can also download the same model from ModelScope and use its local directory as `model_path`.

## 3. Configure generation

Open [`scripts/wan/run_wan_t2v.sh`](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_t2v.sh) and update these settings:

| Setting | What to enter |
| --- | --- |
| `lightx2v_path` | Absolute path to the LightX2V repository |
| `model_path` | Absolute path to the downloaded model directory |
| `CUDA_VISIBLE_DEVICES` | GPU ID to use, such as `0` |
| `--prompt` | Description of the scene to generate |
| `--negative_prompt` | Content to avoid |
| `--size` | Height followed by width; the example uses `480 832` |
| `--num_frames` | Output frame count; the example uses `81` |
| `--save_result_path` | Location for the generated video |

Sampling steps, guidance and attention settings are configured in [`configs/wan/wan_t2v.json`](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v.json).

!!! warning "Check the attention backend"
    This JSON uses `flash_attn3`. Choose a backend supported by your GPU and installed environment before running the example. See the [attention guide](../method_tutorials/attention.md).

??? info "Script arguments and JSON precedence"
    Explicit `--size` and `--num_frames` arguments override the corresponding JSON defaults. To configure them through JSON, remove these arguments from the script first, then set `size` (`[height, width]`) and `num_frames` in the JSON.

## 4. Run and inspect the result

```bash title="Run video generation"
bash scripts/wan/run_wan_t2v.sh
```

After inference completes, open the video at `--save_result_path`. The script's default output is:

```text
save_results/output_lightx2v_wan_t2v.mp4
```

## Next steps

Continue with [Wan2.1 and VACE](../models/wan.md) for other tasks, distillation or services. You can also follow the [Wan2.2](../models/wan22.md) and [Qwen-Image-2.1](../models/qwen-image-2.1.md) model guides.

<div class="grid cards" markdown>

-   :material-view-grid-outline: **Try another model**

    Find examples for video, images, upscaling or interactive tasks.

    [Open the model catalog](../models/index.md)

-   :material-code-braces: **Build a Python application**

    Create a pipeline and reuse the loaded model for generation.

    [Read the Python API guide](python_api.md)

</div>
