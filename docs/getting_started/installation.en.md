# Full installation guide { #lightx2v-quick-start-guide }

<p class="lx-page-lead">Choose an installation method and prepare the environment, images and kernels.</p>

This page provides full setup instructions for Linux and Windows. For a walkthrough to your first output, start with [Start a service and send your first request](index.md).

<div class="lx-method-links" id="table-of-contents" markdown>

[:material-docker: **Linux Docker**<span>Recommended: use a prebuilt image to simplify setup.</span>](#docker-environment-recommended){ .lx-method-recommended }
[:material-console: **Linux Conda**<span>Manage your Python environment and install the kernels you need.</span>](#conda-environment-setup)
[:material-microsoft-windows: **Windows**<span>Use Conda with matching Windows dependencies.</span>](#windows-environment-setup)

</div>

## <span class="lx-heading-icon" aria-hidden="true">:material-memory:</span> System Requirements { #system-requirements .lx-icon-heading data-toc-label="System Requirements" }

- **Operating System**: Linux (Ubuntu 18.04+) or Windows 10/11
- **Python**: 3.10 or higher
- **GPU**: NVIDIA GPU with CUDA support; required VRAM depends on the model and configuration
- **Memory**: Enough host RAM for the selected model, including CPU offload buffers
- **Storage**: At least 50GB available space

## <span class="lx-heading-icon" aria-hidden="true">:material-console:</span> Linux Environment Setup { #linux-environment-setup .lx-icon-heading data-toc-label="Linux Environment Setup" }

<a id="docker-environment-recommended"></a>
### Docker Environment (Recommended)

Prepare the environment with a prebuilt image, then install the checked-out repository inside the container.

#### 1. Pull Image

Visit LightX2V's [Docker Hub](https://hub.docker.com/r/lightx2v/lightx2v/tags), select a tag with the latest date, such as `26052801-cu130`:

```bash
docker pull lightx2v/lightx2v:26052801-cu130
```

We recommend using the `cuda130` environment for faster inference speed. If you need to use the `cuda128` and `cuda124` environment, you can use image versions with the `-cu128` and `-cu124` suffix:

```bash
docker pull lightx2v/lightx2v:26011201-cu128
docker pull lightx2v/lightx2v:25101501-cu124
```

#### 2. Start and enter the container

Clone the repository on the host, or enter its root directory if it already exists:

```bash
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

Mount the repository and open a shell in its directory. Replace the image name on the last line if you selected another image:

```bash
docker run --gpus all -it --ipc=host --name lightx2v-quickstart \
  -p 127.0.0.1:8080:8080 \
  -v "$PWD":/workspace/LightX2V -w /workspace/LightX2V \
  --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
```

Inside the container, install the current checkout, then continue with [Start a service and generate your first video](index.md#download-model):

```bash
pip install -v -e .
```

Models and outputs stored in the repository directory persist on the host. After exiting, use `docker start -ai lightx2v-quickstart` to enter it again. This shares the quickstart's container name and port 8080; reuse an existing container instead of creating it again. For model scripts using port 8000, publish `-p 127.0.0.1:8000:8000` when creating the container and use the matching request address.

#### 3. China Mirror Source (Optional)

For mainland China, if the network is unstable when pulling images, you can pull from Alibaba Cloud:

```bash
# cuda130
docker pull registry.cn-hangzhou.aliyuncs.com/yongyang/lightx2v:26052801-cu130

# cuda128
docker pull registry.cn-hangzhou.aliyuncs.com/yongyang/lightx2v:26011201-cu128

# cuda124
docker pull registry.cn-hangzhou.aliyuncs.com/yongyang/lightx2v:25101501-cu124
```

<a id="conda-environment-setup"></a>
### Conda Environment Setup

Create a Conda environment, then install the kernels required by your GPU and model configuration.

#### Step 1: Clone Repository

```bash
# Download project code
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

#### Step 2: Create Conda Virtual Environment

```bash
# Create and activate conda environment
conda create -n lightx2v python=3.11 -y
conda activate lightx2v
```

#### Step 3: Install Dependencies

```bash
pip install -v -e .
```

#### Step 4: Install Attention Operators

**Option A: Flash Attention 2**
```bash
test -d flash-attention || git clone https://github.com/Dao-AILab/flash-attention.git --recursive
(cd flash-attention && python setup.py install)
```

**Option B: Flash Attention 3 (for Hopper architecture GPUs)**
```bash
test -d flash-attention || git clone https://github.com/Dao-AILab/flash-attention.git --recursive
(cd flash-attention/hopper && python setup.py install)
```

**Option C: SageAttention 2 (Recommended)**
```bash
git clone https://github.com/thu-ml/SageAttention.git
(cd SageAttention && CUDA_ARCHITECTURES="8.0,8.6,8.9,9.0,12.0" EXT_PARALLEL=4 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32 pip install -v -e .)
```

#### Step 5: Install Quantization Operators (Optional)

Quantization operators are used to support model quantization, which can significantly reduce memory usage and accelerate inference. Choose the appropriate quantization operator based on your needs:

**Option A: VLLM Kernels (Recommended)**
Suitable for various quantization schemes, supports FP8 and other quantization formats.

```bash
pip install vllm
```

Or install from source for the latest features:

```bash
git clone https://github.com/vllm-project/vllm.git
(cd vllm && pip install -e .)
```

**Option B: SGL Kernels**
For SGL quantization, choose a release compatible with your PyTorch and CUDA versions; requirements vary by sgl-kernel release. See the [SGL Kernel installation guide](https://github.com/sgl-project/sglang/tree/main/sgl-kernel).

```bash
pip install sgl-kernel --upgrade
```

**Option C: Q8 Kernels**
Suitable for Ada architecture GPUs (such as RTX 4090, L40S, etc.).

```bash
git clone https://github.com/KONAKONA666/q8_kernels.git
(cd q8_kernels && git submodule update --init --recursive && python setup.py install)
```

!!! tip "Install quantization kernels as needed"
    Skip this step if you do not use quantization. Find weights on [LightX2V Hugging Face](https://huggingface.co/lightx2v) and choose modes and kernels using the [quantization guide](../method_tutorials/quantization.md).

#### Step 6: Verify Installation

```python
import lightx2v
print(f"LightX2V Version: {lightx2v.__version__}")
```

## <span class="lx-heading-icon" aria-hidden="true">:material-microsoft-windows:</span> Windows Environment Setup { #windows-environment-setup .lx-icon-heading data-toc-label="Windows Environment Setup" }

The following instructions use Conda to prepare a Windows environment.

### Conda Environment Setup

#### Step 1: Check CUDA Version

First, confirm your GPU driver and CUDA version:

```bat
nvidia-smi
```

The **CUDA Version** shown by `nvidia-smi` is the maximum CUDA version supported by the driver, not necessarily the installed toolkit. Use `nvcc --version` for the local toolkit and `python -c "import torch; print(torch.version.cuda)"` for the CUDA version used by PyTorch. Select compatible packages rather than requiring all three values to be identical. See [NVIDIA's definition](https://docs.nvidia.com/deploy/nvidia-smi/index.html#cuda-umd-version).

#### Step 2: Create Python Environment

```bat
REM Create new environment (Python 3.12 recommended)
conda create -n lightx2v python=3.12 -y

REM Activate environment
conda activate lightx2v
```

!!! tip "Python version"
    Python 3.10 or higher is recommended for best compatibility.

#### Step 3: Install PyTorch Framework

**Method 1: Download Official Wheel Package (Recommended)**

1. Visit the [PyTorch Official Download Page](https://download.pytorch.org/whl/torch/)
2. Select the corresponding version wheel package, paying attention to matching:
   - **Python Version**: Consistent with your environment
   - **CUDA Version**: Matches your GPU driver
   - **Platform**: Select Windows version

**Example (Python 3.12 + PyTorch 2.6 + CUDA 12.4):**

```bat
REM Download and install PyTorch
pip install torch-2.6.0+cu124-cp312-cp312-win_amd64.whl

REM Install supporting packages
pip install torchvision==0.21.0 torchaudio==2.6.0
```

**Method 2: Direct Installation via pip**

```bat
REM CUDA 12.4 version example
pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 torchaudio==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
```

#### Step 4: Clone Repository and Install Dependencies

```bat
REM Clone project code
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V

REM Install Windows-specific dependencies
pip install -r requirements_win.txt
pip install -v -e .
```

#### Step 5: Install Attention Mechanism Operators

**Option A: Flash Attention 2**

```bat
pip install flash-attn==2.7.2.post1
```

**Option B: SageAttention 2 (Strongly Recommended)**

**Download Sources:**

- [Windows Special Version 1](https://github.com/woct0rdho/SageAttention/releases)
- [Windows Special Version 2](https://github.com/sdbds/SageAttention-for-windows/releases)

```bat
REM Install SageAttention (please adjust according to actual filename)
pip install sageattention-2.1.1+cu126torch2.6.0-cp312-cp312-win_amd64.whl
```

!!! warning "SageAttention version compatibility"
    SageAttention's CUDA version doesn't need to be strictly aligned, but Python and PyTorch versions must match.

#### Step 6: Install Quantization Operators (Optional)

By default, LightX2V uses Triton kernel for quantization inference, which is efficient and requires no additional dependencies. Just ensure that `triton-windows` is installed.

If you need to use other quantization operators, you can install the following options:

**1. Install Windows Version of vLLM**

Download the corresponding wheel package from [vllm-windows releases](https://github.com/SystemPanic/vllm-windows/releases).

**Version Matching Requirements:**

- Python version match
- PyTorch version match
- CUDA version match

```bat
REM Install vLLM (please adjust according to actual filename)
pip install vllm-0.9.1+cu124-cp312-cp312-win_amd64.whl
```

**2. Install q8-kernels**

For RTX 40 series GPUs, it is recommended to install `q8_kernel==0.1.0`:

```bat
git clone https://github.com/KONAKONA666/q8_kernels.git
pushd q8_kernels
git submodule update --init --recursive
python setup.py install
popd
```

For other GPUs, it is recommended to install `q8_kernel==0.5.0`. Please refer to [LTX-Video-Q8-Kernels](https://github.com/Lightricks/LTX-Video-Q8-Kernels).

!!! tip "Quantization and weights"
    - It is recommended to use the default Triton kernel for inference
    - Quantized models can be downloaded from [LightX2V HuggingFace](https://huggingface.co/lightx2v)
    - For more quantization information, please refer to the [Quantization Documentation](../method_tutorials/quantization.md)

#### Step 7: Verify Installation

```python
import lightx2v
print(f"LightX2V Version: {lightx2v.__version__}")
```

## <span class="lx-heading-icon" aria-hidden="true">:material-play-circle-outline:</span> Inference Usage { #inference-usage .lx-icon-heading data-toc-label="Inference Usage" }

### Model Preparation

Before starting inference, you need to download the model files in advance. We recommend:

- **Download Source**: Download models from [LightX2V Official Hugging Face](https://huggingface.co/lightx2v/) or other open-source model repositories
- **Storage Location**: It's recommended to store models on SSD disks for better read performance
- **Available Models**: Including Wan2.1-I2V, Wan2.1-T2V, and other models supporting different resolutions and functionalities

### Configuration Files and Scripts

The configuration files used for inference are available [here](https://github.com/ModelTC/LightX2V/tree/main/configs), and scripts are available [here](https://github.com/ModelTC/LightX2V/tree/main/scripts).

You need to configure the downloaded model path in the run script. In addition to the input arguments in the script, there are also some necessary parameters in the configuration file specified by `--config_json`. You can modify them as needed.

### Start Inference

#### Linux Environment

```bash
# Run after modifying the path in the script
bash scripts/wan/run_wan_t2v.sh
```

#### Windows Environment

```bat
REM Use Windows batch script
scripts\win\run_wan_t2v.bat
```

#### Python Script Launch

```python
from lightx2v import LightX2VPipeline

pipe = LightX2VPipeline(
    model_path="/path/to/Wan2.1-T2V-14B",
    model_cls="wan2.1",
    task="t2v",
)

pipe.create_generator(
    attn_mode="sage_attn2",
    infer_steps=50,
    size=(480, 832),  # Height, width; use (720, 1280) for 720p
    num_frames=81,
    guidance_scale=5.0,
    sample_shift=5.0,
)

seed = 42
prompt = "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage."
negative_prompt = "镜头晃动，色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走"
save_result_path="/path/to/save_results/output.mp4"

pipe.generate(
    seed=seed,
    prompt=prompt,
    negative_prompt=negative_prompt,
    save_result_path=save_result_path,
)
```

!!! tip "More examples"
    For more usage examples including quantization, offloading, caching, and other advanced configurations, please refer to the [Python Pipeline guide](python_api.md).

## <span class="lx-heading-icon" aria-hidden="true">:material-lifebuoy:</span> Get Help { #get-help .lx-icon-heading data-toc-label="Get Help" }

If you encounter problems during installation or usage, please:

1. Search for related issues in [GitHub Issues](https://github.com/ModelTC/LightX2V/issues)
2. Submit a new Issue describing your problem

Once the environment is ready, [start a service and generate your first video](index.md#download-model) or integrate with the [Python Pipeline](python_api.md).
