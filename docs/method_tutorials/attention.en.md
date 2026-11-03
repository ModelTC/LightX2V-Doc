# Attention Mechanisms

Choose a backend for your GPU, then check the model's config fields and parallelism constraints. An installed operator is not necessarily compatible with every device, model or input shape.

## Choose by GPU

| Scenario | Starting point | Check before use |
| --- | --- | --- |
| First run or troubleshooting optional operators | `torch_sdpa` | Uses PyTorch's implementation; model device, precision and memory requirements still apply |
| A100 / A800, RTX 3090 / 4090 | `flash_attn2` or `sage_attn2` | Match the build to PyTorch, CUDA and GPU architecture; do not retain `flash_attn3` |
| H100 / H200 | `flash_attn3`, with `sage_attn2` as another candidate | FlashAttention 3 targets Hopper; use the model's matching environment |
| RTX 5090 | `sage_attn2` or `torch_sdpa` from the model-specific config | Use an SM120 environment; `sage_attn3` needs the separate Blackwell implementation and output-quality evaluation |
| Evaluating FlashAttention 4 | `flash_attn4` | Upstream targets Hopper / Blackwell; the current LightX2V adapter requires batch size 1 and has no varlen path |

See [FlashAttention](https://github.com/Dao-AILab/flash-attention) and [SageAttention](https://github.com/thu-ml/SageAttention) for hardware requirements. Prefer model-specific configs over this general table. For Qwen-Image-2.1 on A100, Hopper or 5090, see the [model guide](../models/qwen-image-2.1.md#2-environment-setup).

## Attention Mechanisms Supported by LightX2V

These are common config names, not an exhaustive list of internal backends:

| Backend | Config value | Purpose and limits |
| --- | --- | --- |
| PyTorch SDPA | `torch_sdpa` | No extra attention package; useful as a baseline |
| FlashAttention 2 | `flash_attn2` | Dense attention; check the installed version's device support |
| FlashAttention 3 | `flash_attn3` | Hopper dense attention |
| FlashAttention 4 | `flash_attn4` | CuTeDSL implementation; current adapter limits are listed above |
| SageAttention 2 | `sage_attn2` | Quantized attention; compare output quality after switching |
| SageAttention 3 | `sage_attn3` | Blackwell FP4 attention; installing SageAttention 2 alone is insufficient |
| Radial Attention | `radial_attn` | Sparse video self-attention, not cross-attention |
| Sol-Attn | `sol_attn` | Requires a matching model layout and shape; see the complete examples below |
| Sparge Attention | `sparge_attn` | Sparse backend with its own dependencies and model settings |

See the registered [attention implementations](https://github.com/ModelTC/LightX2V/tree/main/lightx2v/common/ops/attn). Do not substitute these names across every model or parallel mode: sparse layouts, masks, variable lengths and distributed communication may require dedicated implementations.

## Configuration Examples

Merge these fragments into a complete JSON config and pass it to the service or CLI with `--config_json`.

=== "Wan2.1 T2V"

    ```json
    {
      "self_attn_1_type": "torch_sdpa",
      "cross_attn_1_type": "torch_sdpa"
    }
    ```

=== "Qwen-Image-2.1"

    ```json
    {
      "attn_type": "torch_sdpa"
    }
    ```

    This replaces only DiT attention. For Torch RoPE, normalization and other operators, start the standard model from [qwen_image_21_torch.json](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21_torch.json). Turbo must retain its own sampling config.

Wan's `cross_attn_2_type` controls image cross-attention. Keep it for Wan2.1 I2V/FLF2V and Wan2.2 Animate/Animate2; T2V/VACE and Wan2.2 MoE, TI2V and S2V with the image encoder disabled do not need it. Set it to `torch_sdpa` as well when using SDPA for the first group.

Check the GPU and software environment before running:

```bash
python -c "import torch; print(torch.__version__, torch.version.cuda); print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
```

Complete a request with the same model, seed, dimensions and sampling settings, and inspect logs and output. Exclude model loading, first compilation and warmup from timing. Also compare quality for sparse or quantized backends. Importing a package alone does not verify that its kernel runs.

### Sol-Attn on Wan2.1

Sol-Attn is a forward-only, non-causal self-attention backend requiring contiguous BF16 tensors and head dimension 128. For RTX 5090 (SM120), use the repository's pinned environment:

```bash
docker build -f dockerfiles/Dockerfile_5090_cu130_sol_attn -t lightx2v-sol-attn:sm120 .
```

Follow [Quick Start](../getting_started/installation.md) to run a container, replacing the image with `lightx2v-sol-attn:sm120`. For H100/H200 (SM90), install the backend using the [upstream Sol-Attn instructions](https://github.com/NVlabs/Sana/tree/sol-engine/techniques/sparse_backends).

Before running, set `lightx2v_path`, `model_path`, and `CUDA_VISIBLE_DEVICES` in `scripts/wan/inference/run_wan_i2v_sol_attn.sh`. Then edit `configs/attentions/wan_i2v_sol_attn.json` to match your GPU:

| GPU | `sol_attn_setting.dense_backend` | `cross_attn_1_type` / `cross_attn_2_type` |
| --- | --- | --- |
| H100/H200 | `flash_attn3` (default) | `flash_attn3` (default) |
| RTX 5090 | Change to `sage_attn2` or `torch_sdpa` | Change to an installed, supported backend such as `flash_attn2` |

```bash
bash scripts/wan/inference/run_wan_i2v_sol_attn.sh
```

The first call compiles the shape-specific kernel; exclude it from performance timing.

#### Tuning and implementation

- In the default 40-step config, the first 8 steps and Transformer layer 0 use the dense backend; other calls use Sol-Attn. Adjust `dense_steps` and `dense_layers`; the latter accepts `[0, 1]` or `"0-1"`.
- The example uses `tau=0.8`. Lower it for more conservative sparsity; increasing it may reduce visual quality. `sample_shift=3` matches the standard Wan2.1 I2V config.
- Morton3D ordering is applied once around the entire Transformer block stack, with RoPE kept aligned. Strict mode fails on an invalid installation.
- SM120 uses `kv_splits=1`; `"auto"` also resolves to 1.

### Sol-Attn on MiniMax-H3

The MiniMax-H3 example retains the 15-second, 768p, block CPU-offload setup:

Set `lightx2v_path` and `model_path` in `scripts/minimax_h3/run_minimax_h3_t2av.sh` to your local directories, and change its `--config_json` argument to `"${lightx2v_path}/configs/minimax_h3/minimax_h3_sol_block_offload.json"` before running.

```bash
bash scripts/minimax_h3/run_minimax_h3_t2av.sh
```

Its config is `configs/minimax_h3/minimax_h3_sol_block_offload.json`. Sol-Attn is used only by the 50-layer main transformer; the short text refiner uses dense Torch SDPA. The first six denoising steps and transformer layer 0 use SageAttention2 through `dense_backend=sage_attn2`. H3 attention uses a mixed `[text | audio | video]` packed sequence rather than one 3D video grid, so this config uses `reorder=none`; Wan's Morton3D reorder must not be enabled directly.
