---
title: Service quickstart
description: Start a LightX2V model service, send an HTTP request, and download your first generated video.
---

# Service quickstart

<a id="installation-and-first-generation"></a>
<a id="generate-your-first-video"></a>
<p class="lx-page-lead">Start the model once. Send requests to generate and download videos.</p>

<div class="lx-run-summary" markdown>

**This example** <span>Wan2.1-T2V-1.3B</span><span>480 × 832 · 81 frames</span><span>HTTP API</span>

</div>

<a id="before-you-begin"></a>
This walkthrough uses **Linux and a BF16-capable NVIDIA GPU**. Docker requires NVIDIA Container Toolkit and a driver compatible with the image's CUDA 13.0 runtime. For other environments, see [installation](installation.md).

Already have the model and [starter configuration](#starter-config)? Skip to [starting the service](#start-server). Already have this service running? Go to [sending a request](#send-request).

<nav class="lx-guide-path lx-quickstart-path" aria-label="Service quickstart" markdown>

1. [**Prepare**<span>Set up the environment and model.</span>](#prepare)
2. [**Start a service**<span>Load the model in terminal 1.</span>](#start-server)
3. [**Send a request**<span>Generate and download in terminal 2.</span>](#send-request)

</nav>

## Prepare the environment and model { #prepare .lx-step-title data-step="1" }

<a id="1-prepare-the-environment"></a>
In terminal 1 on the GPU host, clone the repository or enter your existing checkout. Run the remaining repository commands from its root:

```bash title="Terminal 1 · GPU host"
git clone https://github.com/ModelTC/LightX2V.git
cd LightX2V
```

Start the container. Docker downloads the image automatically on first use:

```bash title="Terminal 1 · GPU host"
docker run --gpus all -it --ipc=host --name lightx2v-quickstart \
  -p 127.0.0.1:8080:8080 \
  -v "$PWD":/workspace/LightX2V \
  -w /workspace/LightX2V \
  --entrypoint /bin/bash lightx2v/lightx2v:26052801-cu130
```

**Run the setup and server commands inside the container.** Install the current checkout:

```bash title="Terminal 1 · inside the container"
python -m pip install -v -e .
```

Check GPU availability:

```bash title="Terminal 1 · inside the container"
python - <<'PYTHON'
import torch
assert torch.cuda.is_available(), "CUDA is not available"
assert torch.cuda.is_bf16_supported(), "This example requires BF16 support"
print("GPU:", torch.cuda.get_device_name(0))
print("PyTorch:", torch.__version__, "CUDA:", torch.version.cuda)
print("VRAM (GiB):", round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1))
PYTHON
```

<div class="lx-expected" markdown>

**Check passed**

The command finishes without errors and prints the GPU model, PyTorch / CUDA versions, and GPU memory capacity.

</div>

??? info "How much GPU and host memory do I need?"
    This example uses the original 1.3B weights with CPU offload to reduce GPU memory use. Host memory must hold offloaded weights and buffers. Actual usage depends on PyTorch, attention backends, resolution, and frame count. The 1.3B parameter count excludes the text encoder and VAE, so it does not describe the memory requirements of the full pipeline.

    Leave disk space for model downloads and extraction. For constrained hardware, read the [low-resource guide](../deploy_guides/for_low_resource.md) before choosing quantization or distillation settings intended for different weights.

### Download the model { #download-model }

<a id="download-the-model"></a>
Install the download tool, then fetch the complete model including its text encoder and VAE:

```bash title="Terminal 1 · inside the container"
python -m pip install -U huggingface_hub
hf download Wan-AI/Wan2.1-T2V-1.3B \
  --local-dir models/Wan2.1-T2V-1.3B
```

If you already have the weights, skip the download and set `--model_path` below to your local directory. You can also download the same model through ModelScope.

<a id="3-configure-generation"></a>
<a id="configure-and-run"></a>
<a id="prepare-a-starter-configuration"></a>
### Prepare a starter configuration { #starter-config }

Copy the repository configuration, select PyTorch's built-in `torch_sdpa` attention, and enable CPU offload. This creates a separate configuration file and preserves the original.

```bash title="Terminal 1 · inside the container"
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

<a id="run-generation"></a>
## Start the service { #start-server .lx-step-title data-step="2" }

Keep terminal 1 open. Run inside the container, or in your existing LightX2V environment:

```bash title="Terminal 1 · inside the container, keep running"
CUDA_VISIBLE_DEVICES=0 python -m lightx2v.server \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/wan/wan_t2v_quickstart.json \
  --host 0.0.0.0 --port 8080 --metric_port 8081
```

Wait for `Application startup complete.` in the log. In a second terminal on the **same GPU host**, check the API:

```bash title="Terminal 2 · GPU host"
curl --fail --silent --show-error http://localhost:8080/health
```

<div class="lx-expected" markdown>

**Expected result**

The API returns `{"status":"ok"}` when ready. The first startup loads the model and can take time.

</div>

This walkthrough uses API port **8080** and metrics port **8081**; existing repository launchers usually use **8000**. Always match the request URL to your server's port.

## Send a request and get the result { #send-request .lx-step-title data-step="3" }

If you used Docker above, enter that running container from terminal 2:

```bash title="Terminal 2 · GPU host"
docker exec -it lightx2v-quickstart /bin/bash
```

Otherwise, activate the same Python environment in terminal 2 and enter the LightX2V repository.

Expand and copy the complete command below, then run it in **terminal 2** (inside the container if using Docker). This HTTP client submits a task, waits for completion, and downloads the video. It only needs `requests`, included in the environment.

<details class="lx-request-example" markdown>
<summary>Expand and copy the request command</summary>

<!-- quickstart-client -->

</details>

You can also [download the Python client](../assets/examples/first_request.py){ download="first_request.py" }, save it to the LightX2V repository root on the GPU host, and run `python first_request.py` in terminal 2.

<div class="lx-expected" markdown>

**Expected result**

The client prints `Task: …`, then `pending` (queued) or `processing` (generating) while waiting. On completion, it prints `Saved to: …/save_results/first_video.mp4`.

</div>

It polls for up to 30 minutes; a timeout stops waiting without cancelling the server task. Keep the printed ID to [query or cancel it](../deploy_guides/deploy_service.md#poll-download-and-cancel) before submitting again.

<a id="4-run-and-inspect-the-result"></a>
<a id="open-the-result"></a>
### Open the video

Open **`save_results/first_video.mp4`** in the LightX2V checkout. With this Docker setup, the mounted directory also makes it available on the host. For a remote server, download the file to your computer.

The request's `save_result_path` names a server-side output file; the client's `output` is the downloaded copy. Change `prompt` and run the client again to generate another video. The service stays loaded. `size` is `[height, width]`; `num_frames` and other supplied fields override the startup defaults.

Press **Ctrl+C in terminal 1** to stop the service. Explore request schemas at [http://localhost:8080/docs](http://localhost:8080/docs), or use the [service API reference](../deploy_guides/deploy_service.md) for cURL, queues, and other models. When browsing from another computer, forward port 8080 to that computer first.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| GPU check fails | Check `nvidia-smi`, the driver and Docker GPU access; see [installation](installation.md) |
| Missing weights | Check the download and `--model_path`; requests run against the model loaded by the server |
| `/health` cannot connect | Check terminal 1 for loading progress or errors; verify the port and Docker's `-p` mapping |
| Port already in use | Stop the conflicting process or change both the API/metrics ports as needed; update Docker mapping and client URL too |
| `CUDA out of memory` or `Killed` | Check GPU/host memory and use the starter configuration; see [low-resource deployment](../deploy_guides/for_low_resource.md) |
| Task failed | Read the returned error and terminal 1 logs; do not download until the status is `completed` |

<a id="continue"></a>
## Next steps

<div class="lx-next-links" markdown>

[**Choose another model**<span>Find matching server and request examples.</span>](../models/index.md)
[**Use the service API**<span>Request fields, task status, and queues.</span>](../deploy_guides/deploy_service.md)
[**Improve efficiency**<span>Quantization, distillation, caching, and parallelism.</span>](../method_tutorials/index.md)

</div>

Other ways to run: [offline CLI](offline_inference.md) or [Python Pipeline](python_api.md).
