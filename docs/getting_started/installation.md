# 完整安装指南 { #lightx2v-快速入门指南 }

<p class="lx-page-lead">选择安装方式，准备运行环境、镜像和算子依赖。</p>

本页提供 Linux 与 Windows 的完整安装说明。希望先走通一次生成流程，可从[安装与首次生成](index.md)开始。

<div class="lx-method-links" id="目录" markdown>

[:material-docker: **Linux Docker**<span>推荐使用预置镜像，减少环境准备工作。</span>](#docker-environment-recommended){ .lx-method-recommended }
[:material-console: **Linux Conda**<span>自行管理 Python 环境，按需安装算子。</span>](#conda-environment-setup)
[:material-microsoft-windows: **Windows**<span>使用 Conda，安装匹配的 Windows 依赖。</span>](#windows-environment-setup)

</div>

<a id="system-requirements"></a>
## <span class="lx-heading-icon" aria-hidden="true">:material-memory:</span> 系统要求 { #系统要求 .lx-icon-heading data-toc-label="系统要求" }

- **操作系统**: Linux (Ubuntu 18.04+) 或 Windows 10/11
- **Python**: 3.10 或更高版本
- **GPU**: 支持 CUDA 的 NVIDIA GPU；显存需求取决于模型与配置
- **内存**: 需容纳所选模型及 CPU offload 缓冲区
- **存储**: 至少 50GB 可用空间

<a id="linux-environment-setup"></a>
## <span class="lx-heading-icon" aria-hidden="true">:material-console:</span> Linux 系统环境搭建 { #linux-系统环境搭建 .lx-icon-heading data-toc-label="Linux 系统环境搭建" }

<a id="docker-environment-recommended"></a>
### Docker 环境（推荐）

使用预置镜像准备运行环境，然后在容器中安装当前仓库。

#### 1. 拉取镜像

访问 LightX2V 的 [Docker Hub](https://hub.docker.com/r/lightx2v/lightx2v/tags)，选择一个最新日期的 tag，比如 `26052801-cu130`：

```bash
docker pull lightx2v/lightx2v:26052801-cu130
```

我们推荐使用`cuda130`环境，以获得更快的推理速度，若需要使用`cuda128`和`cuda124`环境，可以使用带`-cu128`和`-cu124`后缀的镜像版本：

```bash
docker pull lightx2v/lightx2v:26011201-cu128
docker pull lightx2v/lightx2v:25101501-cu124
```

#### 2. 启动并进入容器

在宿主机下载仓库；已有仓库时直接进入其根目录：

```bash
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

将仓库挂载到容器中，并直接进入该目录。使用其他镜像时，替换最后一行的镜像名称：

```bash
docker run --gpus all -it --ipc=host --name lightx2v \
  -v "$PWD":/workspace/LightX2V -w /workspace/LightX2V \
  --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
```

在容器内安装当前仓库，然后继续[生成第一个视频](first_generation.md)：

```bash
pip install -v -e .
```

仓库目录中的模型和输出文件会保留在宿主机。退出容器后，可用 `docker start -ai lightx2v` 再次进入。

#### 3. 中国镜像源（可选）

对于中国大陆地区，如果拉取镜像时网络不稳定，可以从阿里云上拉取：

```bash
# cuda130
docker pull registry.cn-hangzhou.aliyuncs.com/yongyang/lightx2v:26052801-cu130

# cuda128
docker pull registry.cn-hangzhou.aliyuncs.com/yongyang/lightx2v:26011201-cu128

# cuda124
docker pull registry.cn-hangzhou.aliyuncs.com/yongyang/lightx2v:25101501-cu124
```

<a id="conda-environment-setup"></a>
### Conda 环境搭建

使用 Conda 创建环境，再按 GPU 和模型配置安装所需算子。

#### 步骤 1: 克隆项目

```bash
# 下载项目代码
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

#### 步骤 2: 创建 conda 虚拟环境

```bash
# 创建并激活 conda 环境
conda create -n lightx2v python=3.11 -y
conda activate lightx2v
```

#### 步骤 3: 安装依赖及代码

```bash
pip install -v -e .
```

#### 步骤 4: 安装注意力机制算子

**选项 A: Flash Attention 2**
```bash
test -d flash-attention || git clone https://github.com/Dao-AILab/flash-attention.git --recursive
(cd flash-attention && python setup.py install)
```

**选项 B: Flash Attention 3（用于 Hopper 架构显卡）**
```bash
test -d flash-attention || git clone https://github.com/Dao-AILab/flash-attention.git --recursive
(cd flash-attention/hopper && python setup.py install)
```

**选项 C: SageAttention 2（推荐）**
```bash
git clone https://github.com/thu-ml/SageAttention.git
(cd SageAttention && CUDA_ARCHITECTURES="8.0,8.6,8.9,9.0,12.0" EXT_PARALLEL=4 NVCC_APPEND_FLAGS="--threads 8" MAX_JOBS=32 pip install -v -e .)
```

#### 步骤 5: 安装量化算子（可选）

量化算子用于支持模型量化功能，可以显著降低显存占用并加速推理。根据您的需求选择合适的量化算子：

**选项 A: VLLM Kernels（推荐）**
适用于多种量化方案，支持 FP8 等量化格式。

```bash
pip install vllm
```

或者从源码安装以获得最新功能：

```bash
git clone https://github.com/vllm-project/vllm.git
(cd vllm && pip install -e .)
```

**选项 B: SGL Kernels**
适用于 SGL 量化方案。请选择与当前 PyTorch、CUDA 匹配的版本；不同 sgl-kernel 版本的依赖要求不同，详见 [SGL Kernel 安装说明](https://github.com/sgl-project/sglang/tree/main/sgl-kernel)。

```bash
pip install sgl-kernel --upgrade
```

**选项 C: Q8 Kernels**
适用于 Ada 架构显卡（如 RTX 4090、L40S 等）。

```bash
git clone https://github.com/KONAKONA666/q8_kernels.git
(cd q8_kernels && git submodule update --init --recursive && python setup.py install)
```

!!! tip "量化算子按需安装"
    不使用量化时可跳过此步骤。权重见 [LightX2V Hugging Face](https://huggingface.co/lightx2v)，模式与后端选择见[量化指南](../method_tutorials/quantization.md)。

#### 步骤 6: 验证安装
```python
import lightx2v
print(f"LightX2V 版本: {lightx2v.__version__}")
```

<a id="windows-environment-setup"></a>
## <span class="lx-heading-icon" aria-hidden="true">:material-microsoft-windows:</span> Windows 系统环境搭建 { #windows-系统环境搭建 .lx-icon-heading data-toc-label="Windows 系统环境搭建" }

以下使用 Conda 准备 Windows 环境。

### Conda 环境搭建

#### 步骤 1: 检查 CUDA 版本

首先确认您的 GPU 驱动和 CUDA 版本：

```bat
nvidia-smi
```

`nvidia-smi` 中的 **CUDA Version** 表示驱动支持的最高 CUDA 版本，不一定是本机安装的 Toolkit 版本。用 `nvcc --version` 查看本地 Toolkit，用 `python -c "import torch; print(torch.version.cuda)"` 查看 PyTorch 使用的 CUDA 版本。选择相互兼容的包即可，不要求这三个值完全一致，详见 [NVIDIA 定义](https://docs.nvidia.com/deploy/nvidia-smi/index.html#cuda-umd-version)。

#### 步骤 2: 创建 Python 环境

```bat
REM 创建新环境（推荐 Python 3.12）
conda create -n lightx2v python=3.12 -y

REM 激活环境
conda activate lightx2v
```

!!! tip "Python 版本"
    建议使用 Python 3.10 或更高版本以获得最佳兼容性。

#### 步骤 3: 安装 PyTorch 框架

**方法一：下载官方 wheel 包（推荐）**

1. 访问 [PyTorch 官方下载页面](https://download.pytorch.org/whl/torch/)
2. 选择对应版本的 wheel 包，注意匹配以下参数：
   - **Python 版本**: 与您的环境一致
   - **CUDA 版本**: 与您的 GPU 驱动匹配
   - **平台**: 选择 Windows 版本

**示例（Python 3.12 + PyTorch 2.6 + CUDA 12.4）：**

```bat
REM 下载并安装 PyTorch
pip install torch-2.6.0+cu124-cp312-cp312-win_amd64.whl

REM 安装配套包
pip install torchvision==0.21.0 torchaudio==2.6.0
```

**方法二：使用 pip 直接安装**

```bat
REM CUDA 12.4 版本示例
pip install torch==2.6.0+cu124 torchvision==0.21.0+cu124 torchaudio==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
```

#### 步骤 4: 克隆项目并安装依赖

```bat
REM 克隆项目代码
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V

REM 安装 Windows 专用依赖
pip install -r requirements_win.txt
pip install -v -e .
```

#### 步骤 5: 安装注意力机制算子

**选项 A: Flash Attention 2**

```bat
pip install flash-attn==2.7.2.post1
```

**选项 B: SageAttention 2（强烈推荐）**

**下载源：**

- [Windows 专用版本 1](https://github.com/woct0rdho/SageAttention/releases)
- [Windows 专用版本 2](https://github.com/sdbds/SageAttention-for-windows/releases)

```bat
REM 安装 SageAttention（请根据实际文件名调整）
pip install sageattention-2.1.1+cu126torch2.6.0-cp312-cp312-win_amd64.whl
```

!!! warning "SageAttention 版本匹配"
    SageAttention 的 CUDA 版本可以不严格对齐，但 Python 和 PyTorch 版本必须匹配。

#### 步骤 6 (可选): 安装量化算子

默认使用 Triton kernel 进行量化推理，实现高效且无需安装额外依赖，只需确保已安装 `triton-windows` 即可。

如需使用其他量化算子，可安装以下选项：

**1. 安装 Windows 版 vLLM**

从 [vllm-windows releases](https://github.com/SystemPanic/vllm-windows/releases) 下载对应的 wheel 包。

**版本匹配要求：**

- Python 版本匹配
- PyTorch 版本匹配
- CUDA 版本匹配

```bat
REM 安装 vLLM（请根据实际文件名调整）
pip install vllm-0.9.1+cu124-cp312-cp312-win_amd64.whl
```

**2. 安装 q8-kernels**

对于 RTX 40 系显卡，推荐安装 `q8_kernel==0.1.0`：

```bat
git clone https://github.com/KONAKONA666/q8_kernels.git
pushd q8_kernels
git submodule update --init --recursive
python setup.py install
popd
```

对于其他显卡，推荐安装 `q8_kernel==0.5.0`，请参考 [LTX-Video-Q8-Kernels](https://github.com/Lightricks/LTX-Video-Q8-Kernels)。

!!! tip "量化与权重"
    - 建议使用默认的 Triton kernel 进行推理
    - 量化模型可以从 [LightX2V HuggingFace](https://huggingface.co/lightx2v) 下载
    - 更多量化相关信息请参考 [量化文档](../method_tutorials/quantization.md)

#### 步骤 7: 验证安装
```python
import lightx2v
print(f"LightX2V 版本: {lightx2v.__version__}")
```

<a id="inference-usage"></a>
## <span class="lx-heading-icon" aria-hidden="true">:material-play-circle-outline:</span> 推理使用 { #推理使用 .lx-icon-heading data-toc-label="推理使用" }

### 模型准备

在开始推理之前，您需要提前下载好模型文件。我们推荐：

- **下载源**: 从 [LightX2V 官方 Hugging Face](https://huggingface.co/lightx2v/)或者其他开源模型库下载模型
- **存储位置**: 建议将模型存储在 SSD 磁盘上以获得更好的读取性能
- **可用模型**: 包括 Wan2.1-I2V、Wan2.1-T2V 等多种模型，支持不同分辨率和功能

### 配置文件与脚本

推理会用到的配置文件都在[这里](https://github.com/ModelTC/LightX2V/tree/main/configs)，脚本都在[这里](https://github.com/ModelTC/LightX2V/tree/main/scripts)。

需要将下载的模型路径配置到运行脚本中。除了脚本中的输入参数，`--config_json` 指向的配置文件中也会包含一些必要参数，您可以根据需要自行修改。

### 开始推理

#### Linux 环境

```bash
# 修改脚本中的路径后运行
bash scripts/wan/run_wan_t2v.sh
```

#### Windows 环境

```bat
REM 使用 Windows 批处理脚本
scripts\win\run_wan_t2v.bat
```
#### Python脚本启动

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


## <span class="lx-heading-icon" aria-hidden="true">:material-lifebuoy:</span> 获取帮助 { #获取帮助 .lx-icon-heading data-toc-label="获取帮助" }

如果您在安装或使用过程中遇到问题，请：

1. 在 [GitHub Issues](https://github.com/ModelTC/LightX2V/issues) 中搜索相关问题
2. 提交新的 Issue 描述您的问题

环境准备完成后，继续[生成第一个视频](first_generation.md)，或通过 [Python API](python_api.md) 接入应用。
