# Windows Local Deployment Guide

Run a service from the current checkout in a dedicated Python environment, then generate through HTTP requests. Use [standalone integrations](interfaces.md) for graphical interfaces.

## Prepare the environment and model

Follow the [Windows installation instructions](../getting_started/installation.md#windows-environment-setup) first. These commands use **Windows CMD / Anaconda Prompt**, not PowerShell or Bash. Activate the LightX2V environment and enter the inference repository root.

This example uses a BF16-capable NVIDIA GPU, original Wan2.1-T2V-1.3B weights and CPU offload. Host and GPU memory must still hold the components and intermediate results; the 1.3B parameter count alone does not determine memory requirements. Download the complete model and copy the config:

```bat
python -m pip install -U huggingface_hub
hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir models/Wan2.1-T2V-1.3B
copy configs\wan\wan_t2v.json configs\wan\wan_t2v_windows.json
```

Open `configs/wan/wan_t2v_windows.json` and merge in these fields, retaining the original 50-step sampling settings and CFG. Do not replace the entire file with this fragment:

```json
{
  "self_attn_1_type": "torch_sdpa",
  "cross_attn_1_type": "torch_sdpa",
  "cpu_offload": true,
  "offload_granularity": "block",
  "t5_cpu_offload": true,
  "vae_cpu_offload": true
}
```

This selects PyTorch SDPA, so the example does not need an additional FlashAttention installation.

## Start a service and send a request

Start the service in terminal 1 and leave it running:

```bat
set CUDA_VISIBLE_DEVICES=0
python -m lightx2v.server ^
  --model_cls wan2.1 --task t2v ^
  --model_path models/Wan2.1-T2V-1.3B ^
  --config_json configs/wan/wan_t2v_windows.json ^
  --host 127.0.0.1 --port 8080 --metric_port 8081
```

Wait for `Application startup complete.`. Open another CMD terminal on the same computer, check readiness and submit a request:

```bat
curl.exe --fail http://localhost:8080/health
curl.exe --fail -X POST http://localhost:8080/v1/tasks/video/ ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"A cat walking on a sunny beach.\",\"seed\":42,\"save_result_path\":\"windows_first_video.mp4\"}"
```

Keep the returned `task_id` and replace `TASK_ID` below. Query status first; run the download command only once `status` is `completed`:

```bat
curl.exe --fail http://localhost:8080/v1/tasks/TASK_ID/status
curl.exe --fail http://localhost:8080/v1/tasks/TASK_ID/result -o first_video.mp4
```

The result is downloaded to `first_video.mp4` in terminal 2's current directory. For `failed` tasks, inspect the response error and service logs. See the [service API reference](deploy_service.md) for task management.

## Other entry points

- [Python Pipeline](../getting_started/python_api.md): reuse a model in a Python process.
- [Windows batch scripts](https://github.com/ModelTC/LightX2V/tree/main/scripts/win): edit repository and model paths and check the matching config first. The config referenced by `run_wan_t2v.bat` uses four steps and requires quantized T5 weights; it is not the original model's 50-step example.
- [Gradio and ComfyUI](interfaces.md): install in the application's required environment and check its supported models.

<a id="legacy-bundle-one-click-gradio-startup"></a>

The old bundle's download, configuration and startup records are in [Legacy Windows bundle](windows_legacy.md).
