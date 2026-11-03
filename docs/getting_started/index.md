---
title: 启动服务与首次请求
description: 启动 LightX2V 模型服务，通过 HTTP 请求生成并下载第一个视频。
---

# 启动服务与首次请求

<a id="安装与首次生成"></a>
<a id="生成第一个视频"></a>
<p class="lx-page-lead">启动一次模型服务，通过请求生成并下载视频。</p>

<div class="lx-run-summary" markdown>

**本次运行** <span>Wan2.1-T2V-1.3B</span><span>480 × 832 · 81 帧</span><span>HTTP API</span>

</div>

<a id="开始之前"></a>
本教程面向 **Linux + 支持 BF16 的 NVIDIA GPU**。Docker 需配置 NVIDIA Container Toolkit，驱动需兼容镜像的 CUDA 13.0。其他环境见[安装指南](installation.md)。

已有模型与[入门配置](#starter-config)？直接[启动服务](#start-server)。已有运行中的同类服务？直接[发送请求](#send-request)。

<nav class="lx-guide-path lx-quickstart-path" aria-label="服务入门流程" markdown>

1. [**准备环境**<span>安装依赖，下载模型。</span>](#prepare)
2. [**启动服务**<span>在终端 1 加载模型。</span>](#start-server)
3. [**发送请求**<span>在终端 2 生成并下载结果。</span>](#send-request)

</nav>

## 1. 准备环境与模型 { #prepare }

<a id="1-准备运行环境"></a>
在 GPU 宿主机的终端 1 获取仓库，已有仓库则进入对应目录。后续仓库内命令均从根目录执行：

```bash
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

启动容器；首次运行会自动下载镜像：

```bash
docker run --gpus all -it --ipc=host --name lightx2v-quickstart \
  -p 127.0.0.1:8080:8080 \
  -v "$PWD":/workspace/LightX2V \
  -w /workspace/LightX2V \
  --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
```

**环境准备与服务启动命令在容器内执行。** 安装当前仓库：

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

### 下载模型 { #download-model }

<a id="下载模型"></a>
安装下载工具，获取包含文本编码器和 VAE 的完整模型目录：

```bash
python -m pip install -U huggingface_hub
hf download Wan-AI/Wan2.1-T2V-1.3B \
  --local-dir models/Wan2.1-T2V-1.3B
```

已有权重时可跳过下载，将下方命令中的 `--model_path` 改为实际目录。也可通过 ModelScope 下载同名模型。

<a id="3-配置生成参数"></a>
<a id="配置并运行"></a>
<a id="准备入门配置"></a>
### 准备入门配置 { #starter-config }

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

<a id="运行生成"></a>
## 2. 启动服务 { #start-server }

保持终端 1 运行。在容器内，或已有的 LightX2V 环境中执行：

```bash title="终端 1 · 保持运行"
CUDA_VISIBLE_DEVICES=0 python -m lightx2v.server \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/wan/wan_t2v_quickstart.json \
  --host 0.0.0.0 --port 8080 --metric_port 8081
```

等待日志出现 `Application startup complete.`。在**同一台 GPU 主机**另开终端，检查接口是否可用：

```bash title="终端 2 · GPU 宿主机"
curl --fail --silent --show-error http://localhost:8080/health
```

正常返回 `{"status":"ok"}`。首次启动需要加载模型，请耐心等待。本教程使用 API 端口 **8080**、指标端口 **8081**；仓库已有启动脚本通常使用 **8000**，请求地址需与实际服务端口一致。

## 3. 发送请求并获取结果 { #send-request }

使用上面的 Docker 环境时，在终端 2 进入正在运行的容器：

```bash title="终端 2 · 进入已有容器"
docker exec -it lightx2v-quickstart /bin/bash
```

使用已有 Python 环境时，在终端 2 激活同一环境并进入 LightX2V 仓库。下面的 **Python HTTP 客户端**会提交请求、等待完成并下载视频。它只依赖环境中已有的 `requests`，不加载模型。

```bash title="终端 2 · 提交、等待并下载"
python - <<'PYTHON'
import time
import uuid
from pathlib import Path

import requests

base_url = "http://localhost:8080"
response = requests.post(f"{base_url}/v1/tasks/video/", json={
    "prompt": "A cat walking on a sunny beach.",
    "negative_prompt": "blurry, low quality",
    "seed": 42,
    "size": [480, 832],
    "num_frames": 81,
    "save_result_path": f"quickstart_{uuid.uuid4().hex}.mp4",
}, timeout=30)
response.raise_for_status()
task_id = response.json()["task_id"]
print(f"Task: {task_id}", flush=True)

deadline = time.monotonic() + 1800
while time.monotonic() < deadline:
    response = requests.get(f"{base_url}/v1/tasks/{task_id}/status", timeout=30)
    response.raise_for_status()
    task = response.json()
    if task["status"] == "completed":
        break
    if task["status"] in {"failed", "cancelled"}:
        raise RuntimeError(f"{task['status']}: {task.get('error') or task_id}")
    print(task["status"], flush=True)
    time.sleep(2)
else:
    raise TimeoutError(f"Timed out waiting for task {task_id}; query its status before retrying.")

output = Path("save_results/first_video.mp4")
output.parent.mkdir(parents=True, exist_ok=True)
with requests.get(f"{base_url}/v1/tasks/{task_id}/result", stream=True, timeout=(10, 300)) as response:
    response.raise_for_status()
    with output.with_suffix(".mp4.part").open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            file.write(chunk)
output.with_suffix(".mp4.part").replace(output)
print(f"Saved to: {output.resolve()}")
PYTHON
```

客户端先输出任务 ID，再显示 `pending`（排队）或 `processing`（生成中），完成后输出本地文件路径。默认最多轮询 30 分钟；超时只停止等待，不会取消服务端任务。请保留任务 ID，[查询或取消任务](../deploy_guides/deploy_service.md#查询下载与取消)后再决定是否重新提交。

<a id="4-运行并查看结果"></a>
<a id="查看结果"></a>
### 查看视频

打开 LightX2V 仓库中的 **`save_results/first_video.mp4`**。按本页方式启动 Docker 时，该目录已挂载到宿主机；远程服务器上的文件可下载到本机播放。

请求中的 `save_result_path` 是服务端输出文件名，客户端的 `output` 是下载位置。修改 `prompt` 后再次运行客户端，即可继续生成，服务无需重启。`size` 按 `[高, 宽]` 填写；请求中指定的 `num_frames` 等字段会覆盖启动默认值。

在**终端 1 按 Ctrl+C** 停止服务。接口参数可查看 [http://localhost:8080/docs](http://localhost:8080/docs)，cURL、队列及其他模型的用法见[服务 API 参考](../deploy_guides/deploy_service.md)。从其他电脑打开接口页面时，先转发服务的 8080 端口。

## 遇到问题

| 现象 | 先检查这里 |
| --- | --- |
| GPU 检查失败 | 检查 `nvidia-smi`、驱动与 Docker GPU 挂载，参考[安装指南](installation.md) |
| 找不到权重 | 确认下载完成与 `--model_path` 正确；请求使用服务已加载的模型 |
| `/health` 无法连接 | 查看终端 1 是否仍在加载或已报错，核对端口与 Docker 的 `-p` 映射 |
| 端口被占用 | 停止冲突进程，或按需更换 API / 指标端口；同步修改 Docker 映射和请求地址 |
| `CUDA out of memory` 或 `Killed` | 检查显存、主机内存及入门配置，参考[低资源部署](../deploy_guides/for_low_resource.md) |
| 任务失败 | 查看返回的错误和终端 1 日志，状态为 `completed` 后再下载结果 |

<a id="继续使用"></a>
## 下一步

<div class="lx-next-links" markdown>

[**换一个模型**<span>查找配套的服务与请求示例。</span>](../models/index.md)
[**接入服务 API**<span>请求参数、任务状态与队列。</span>](../deploy_guides/deploy_service.md)
[**提升推理效率**<span>量化、蒸馏、缓存与并行。</span>](../method_tutorials/index.md)

</div>

其他运行方式：[离线命令行](offline_inference.md)或 [Python Pipeline](python_api.md)。
