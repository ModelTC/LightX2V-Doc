# Wan2.1 and VACE

Start a Wan2.1 or VACE service and send video generation requests. Offline inference and distillation examples are also available.

The example scripts are in `scripts/wan/` in the [LightX2V inference repository](https://github.com/ModelTC/LightX2V). Set `lightx2v_path`, `model_path`, and `CUDA_VISIBLE_DEVICES` in the script, and run the commands below from that repository's root.

## Reading path

1. [Choose a task](#choose-task): text-to-video, image-to-video, first/last frames or VACE.
2. [Prepare the environment and weights](#environment-and-weights): install dependencies and download the matching model.
3. [Start a service and send a request](#first-run): load the model once and retrieve the generated video.
4. [Tune inference](#next-steps): choose configurations for memory, latency, or multiple GPUs.

## Environment and weights

Complete the [environment setup](../getting_started/installation.md).
For your first T2V 1.3B run, download:

```bash
hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir Wan-AI/Wan2.1-T2V-1.3B
```

Choose other download commands only for the tasks and configurations you need. Distillation weights are optional:

```bash
# Download from HuggingFace
hf download Wan-AI/Wan2.1-T2V-14B --local-dir Wan-AI/Wan2.1-T2V-14B
hf download Wan-AI/Wan2.1-I2V-14B-480P --local-dir Wan-AI/Wan2.1-I2V-14B-480P
hf download Wan-AI/Wan2.1-I2V-14B-720P --local-dir Wan-AI/Wan2.1-I2V-14B-720P

# Download distilled models
hf download lightx2v/Wan2.1-Distill-Models --local-dir lightx2v/Wan2.1-Distill-Models
hf download lightx2v/Wan2.1-Distill-Loras --local-dir lightx2v/Wan2.1-Distill-Loras
```

Keep `model_path` pointed at the complete base model directory. Set the checkpoint
and LoRA paths in the selected JSON to the downloaded local files.

<a id="choose-task"></a>

## Basic tasks

| Task | Server launcher | Example weights | Configuration |
| --- | --- | --- | --- |
| Text to video | [start_server_t2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/server/start_server_t2v.sh) | [Wan2.1-T2V-1.3B](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B) | [wan_t2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v.json) |
| Image to video | [start_server_i2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/server/start_server_i2v.sh) | [Wan2.1-I2V-14B-480P](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P) | [wan_i2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_i2v.json) |
| First and last frames to video | [start_server_flf2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/server/start_server_flf2v.sh) | [Wan2.1-FLF2V-14B-720P](https://huggingface.co/Wan-AI/Wan2.1-FLF2V-14B-720P) | [wan_flf2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_flf2v.json) |
| Reference image/video conditioning | [start_server_vace.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/server/start_server_vace.sh) | [Wan2.1-VACE-14B](https://huggingface.co/Wan-AI/Wan2.1-VACE-14B) | [wan_vace.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_vace.json) |

<a id="first-run"></a>
## Start a service and send a request { #server }

For your first Wan2.1 1.3B service, follow the [complete quickstart](../getting_started/index.md). Set repository/model paths and GPU IDs in the server script. Its default configuration uses `flash_attn3` without CPU offload; check [attention compatibility](../method_tutorials/attention.md) and [offload settings](../method_tutorials/offload.md) before starting.

Scripts and clients are in `server/`, using the weights listed above. The default listening address is `0.0.0.0:8000`.

| Task | Start server | Submit request |
| --- | --- | --- |
| T2V | `start_server_t2v.sh` | `post_t2v.py` |
| I2V | `start_server_i2v.sh` | `post_i2v.py` |
| FLF2V | `start_server_flf2v.sh` | `post_flf2v.py` |
| VACE | `start_server_vace.sh` | `post_vace.py` |
| T2V Reuse | `start_server_t2v_reuse.sh` | `post_t2v_reuse.py` |

T2V example:

```bash
# Terminal 1: start the server
bash scripts/wan/server/start_server_t2v.sh
```

Wait for `Application startup complete.`. In terminal 2, use the same environment and container (or enter it with `docker exec`), then check:

```bash
curl --fail --silent --show-error http://localhost:8000/health
```

The response should be `{"status":"ok"}`. Keep terminal 1 running.

```bash
# Terminal 2: submit a request after the model loads
python scripts/wan/server/post_t2v.py
```

The video client prints a `task_id`; it does not wait for or download the finished video. Continue with [querying status and downloading results](../deploy_guides/deploy_service.md#poll-download-and-cancel), or use the [automatic Python HTTP client](../getting_started/index.md#send-request) with `base_url` changed to `http://localhost:8000` and the request fields matched to this model and task.

Edit `url` and `message` in the client. Images accept Base64 or absolute paths; VACE videos use absolute paths in `video_path`. Files referenced by absolute paths must be accessible to the server. Set the output location with `save_result_path`.

### Reuse input encodings

T2V uses the Reuse entry above. For I2V, add `"enable_reuse": true` and `"reuse_cache_path": "save_results/reuse_cache/wan_i2v"` to the base JSON, start the regular I2V server, and add `reuse` to the client's `message`. Use a separate cache directory for each model or server.

Use `reuse=False` for the first request and `reuse=True` to reuse input encodings. Keep the prompt, negative prompt, frame count, size, and I2V image paths and contents unchanged. The seed may change; use `False` when changing inputs.

<a id="first-generation-t2v-13b"></a>
## Offline CLI { #offline-inference }

After installing the environment and downloading T2V 1.3B, open [run_wan_t2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_t2v.sh) and set:

| Setting | Value |
| --- | --- |
| `lightx2v_path` | Absolute path to your LightX2V checkout |
| `model_path` | Absolute path to the downloaded Wan2.1-T2V-1.3B directory |
| `CUDA_VISIBLE_DEVICES` | GPU ID to use |
| `--prompt`, `--save_result_path` | Generation prompt and output file location |

The default [wan_t2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v.json) uses `flash_attn3` and disables CPU offload. Check [attention backend compatibility](../method_tutorials/attention.md) first. If you need offload, choose a matching configuration from [low-resource deployment](../deploy_guides/for_low_resource.md).

Run from the repository root:

```bash
bash scripts/wan/run_wan_t2v.sh
```

Open the video at `--save_result_path` when inference finishes. The default is `save_results/output_lightx2v_wan_t2v.mp4` inside the repository. For a walkthrough, see [Offline inference](../getting_started/offline_inference.md).

Edit inputs, prompts, seed, and output paths in the shell script, and sampling parameters in the JSON selected by `--config_json`. The JSON fields `num_frames` and `size` supply defaults when omitted from the command or request. `size` is `[height, width]`.

## Multiple GPUs

The two-GPU Ulysses example uses the same weights and inputs as basic T2V, with [wan_t2v_parallel.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v_parallel.json):

```bash
bash scripts/wan/run_wan_t2v_parallel.sh
```

For other tasks, use matching weights and base JSON, add `parallel`, and switch to `torchrun` as in the example. The visible GPU count, `--nproc_per_node`, and `parallel.seq_p_size` must match. The Ulysses GPU count must divide the model's attention head count.

## Advanced features

These entries are in `inference/`. Set additional checkpoint paths for distillation and lazy loading in the corresponding JSON.

| Feature | Entry |
| --- | --- |
| Compile | `run_wan_t2v_compile.sh` |
| Lazy loading | `run_wan_i2v_lazy_load.sh` |
| Sol-Attn | `run_wan_i2v_sol_attn.sh` |
| Shared CPU offload | [Usage](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/shared_offload/README.md) |
| Contiguous memory layout vs. baseline | [Usage](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/offload_layout/README.md) |

For T2V/I2V, add `"use_compile": true` to enable compilation and `"warmup": true` to enable warmup in the base JSON. I2V uses the regular entry; restart the server after changing its configuration.

### Distillation

`inference/distill/` provides single-GPU 4-step examples. Choose the matching weight type below; model, LoRA, and FP8 examples follow the GPU setup in the previous section.

| Weight type | T2V | I2V |
| --- | --- | --- |
| Full distilled DiT | `run_wan_t2v_distill_model.sh` | `run_wan_i2v_distill_model.sh` |
| Base model + distilled LoRA | `run_wan_t2v_distill_lora.sh` | `run_wan_i2v_distill_lora.sh` |
| FP8 distilled DiT | `run_wan_t2v_distill_fp8.sh` | `run_wan_i2v_distill_fp8.sh` |
| INT8 distilled DiT | — | `run_wan_i2v_distill_int8.sh` |

- `run_wan_i2v_distill_single_file.sh`: a single distilled DiT file, its config, encoders, and VAE in the same model directory.
- `run_wan_t2v_distill_dynamic_cfg.sh`: a dynamic CFG model; `cfg_scale` in the JSON controls guidance strength.
- `run_wan_t2v_distill_model_ulysses.sh`: an eight-GPU Ulysses example for the full distilled T2V model.

## Python Pipeline examples { #python-api-examples }

See the [Python Pipeline guide](../getting_started/python_api.md) for
generator setup, configuration precedence, offload and repeated generation.
Edit paths in the selected file, then run it from the repository root after installation.
These examples retain their own model, sampling and attention settings; using a
Shell launcher's JSON is an explicit change of configuration.

| Use case | Python entry |
| --- | --- |
| Wan2.1 T2V 14B | [wan_t2v.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/wan_t2v.py) |
| Wan2.1 FLF2V | [wan_flf2v.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/wan_flf2v.py) |
| Wan2.1 VACE | [wan_vace.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/wan_vace.py) |
| Wan2.1 T2V 1.3B NVFP4, 4-step | [wan_t2v_nvfp4.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/distill/wan_t2v_nvfp4.py) |
| Wan2.1 I2V 14B NVFP4, 4-step | [wan_i2v_nvfp4.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/distill/wan_i2v_nvfp4.py) |

The T2V Python example uses the 14B model, `sage_attn2`, guidance 5 and shift 5;
the basic Shell launcher uses the 1.3B model with its JSON settings. Keep these
choices explicit when comparing outputs. For NVFP4, use the named 4-step weights
from [Wan-NVFP4](https://huggingface.co/lightx2v/Wan-NVFP4), keep `distill_method="dmd2"`,
and install the [quantization kernels](https://github.com/ModelTC/LightX2V/blob/main/lightx2v_kernel/nvidia/README.md).

For CPU offload, set `cpu_offload` and a supported `offload_granularity` in the JSON;
see the [offload guide](../deploy_guides/for_low_resource.md).

<a id="next-steps"></a>

## Acceleration and deployment

| Goal | Model examples and general guides |
| --- | --- |
| Reduce GPU memory use | [Low-resource deployment](../deploy_guides/for_low_resource.md), [parameter offload](../method_tutorials/offload.md) |
| Use low-precision weights | [Model quantization](../method_tutorials/quantization.md); choose a backend matching the weight format |
| Reduce sampling steps or use LoRA | [Distillation examples](#distillation), [step distillation](../method_tutorials/step_distill.md), [LoRA configuration and combination limits](../deploy_guides/lora_deploy.md) |
| Use multiple GPUs | [Multi-GPU examples](#multiple-gpus), [parallel inference](../method_tutorials/parallel.md) |
| Integrate an application | [Server examples](#server), [inference services](../deploy_guides/deploy_service.md), [Python Pipeline](../getting_started/python_api.md) |
