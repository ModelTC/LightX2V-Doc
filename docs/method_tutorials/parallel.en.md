# Parallel Inference

Multiple GPUs can cooperate on one generation. Choose a parallel mode supported by the model and match the `torchrun` process count to the config. To process independent requests on different GPUs, use [multiple independent services](../deploy_guides/deploy_service.md#multiple-gpus-and-multiple-services).

## Choose a parallel mode

| Mode | Config fields | Work distribution | Main constraints |
| --- | --- | --- | --- |
| Sequence parallelism (SP) | `seq_p_size`, `seq_p_attn_type` | Splits sequences across ranks using Ulysses or Ring communication | Requires model and attention support; does not imply that all weights are sharded |
| CFG parallelism | `cfg_p_size` | Separates conditional and unconditional branches | Usually 2; requires `enable_cfg=true` and model support |
| Tensor parallelism (TP) | `tensor_p_size` | Shards supported weights and operators | Model, quantization and offload paths must be compatible; adding the field alone is insufficient |

### Model entry points and limits

| Model | Example | Explicit constraints |
| --- | --- | --- |
| Wan2.1 | [Ulysses / Ring / CFG configs](https://github.com/ModelTC/LightX2V/tree/main/configs/dist_infer) | Select `wan_*` configs; CFG-disabled distilled models cannot use CFG parallelism |
| Wan2.2 MoE | [TP4 server](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan22/server/start_server_t2v_tp.sh), [SP / CFG configs](https://github.com/ModelTC/LightX2V/tree/main/configs/dist_infer) | MoE, TI2V and S2V need different tasks and configs; use the [model guide](../models/wan22.md) |
| Qwen-Image-2.1 | [Two-GPU 5090 config](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21_5090_2k_sp2.json) | SP supports Ulysses only; CFG parallelism is unsupported. With TP, the attention heads local to each rank must also divide evenly by SP size |
| SeedVR2 | [7B SP config](https://github.com/ModelTC/LightX2V/blob/main/configs/seedvr/seedvr2_7b_sp.json) | SP supports `ulysses` / `ulysses-4090`; requires TP=1, CFG=1 and `parallel.vae_parallel` enabled. SP requests do not accept `image_path` |

These entry points do not guarantee every combination. The Qwen 5090 config also includes model-specific quantization settings; check its weights and dependencies before using it.

## Process count and devices

With TP, SP and CFG only, and no pipeline parallelism:

```text
N = tensor_p_size × seq_p_size × cfg_p_size
```

Unset sizes count as 1. SP4 needs 4 processes, SP4 + CFG2 needs 8, and TP4 needs 4. Match `CUDA_VISIBLE_DEVICES`, `--nproc_per_node` and the JSON; models may also impose attention-head divisibility constraints.

More GPUs are not always faster: communication, interconnect and input size affect the result. Verify a single-GPU baseline first, then compare identical workloads.

## DiT Parallel Configuration

Merge the following JSON fragments into a complete model config.

### 1. Ulysses Parallel

```json
{
  "parallel": {
    "seq_p_size": 4,
    "seq_p_attn_type": "ulysses"
  }
}
```

### 2. Ring Parallel

Use only with a model and attention backend supporting Ring:

```json
{
  "parallel": {
    "seq_p_size": 4,
    "seq_p_attn_type": "ring"
  }
}
```

## Cfg Parallel Configuration

Requires a model supporting CFG parallelism with CFG enabled; do not use it with CFG-disabled distillation configs:

```json
{
  "enable_cfg": true,
  "parallel": {"cfg_p_size": 2}
}
```

## Tensor parallel configuration

For example, the [complete Wan2.2 MoE TP4 config](https://github.com/ModelTC/LightX2V/blob/main/configs/wan22/wan_moe_t2v_tp.json) includes:

```json
{
  "parallel": {"tensor_p_size": 4}
}
```

## Hybrid Parallel Configuration

SP4 + CFG2 requires 8 processes and a model supporting this combination:

```json
{
  "enable_cfg": true,
  "parallel": {
    "seq_p_size": 4,
    "seq_p_attn_type": "ulysses",
    "cfg_p_size": 2
  }
}
```

## Usage

### Four-GPU Wan2.1 service

Complete [environment and model setup](../getting_started/index.md#prepare). From the repository root, use original Wan2.1-T2V-1.3B weights and `configs/dist_infer/wan_t2v_dist_ulysses.json`: 50 steps, CFG enabled, SP4, and CPU offload disabled by default.

Check `self_attn_1_type` and `cross_attn_1_type` first. Their default `flash_attn3` targets Hopper. On other GPUs, set both to `torch_sdpa` or select an installed backend supporting this model. Stop previous inference services using the same ports or GPUs, then run:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun --standalone --nproc_per_node=4 \
  -m lightx2v.server \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/dist_infer/wan_t2v_dist_ulysses.json \
  --host 0.0.0.0 --port 8080 --metric_port 8081
```

Once ready, use the [first-request client](../getting_started/index.md#send-request) to submit and download. Send one request to this service; the ranks cooperate on it. Do not submit a separate request to every GPU. Docker still needs API port 8080 published.

### Offline generation

After stopping the service, run the same config offline:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun --standalone --nproc_per_node=4 \
  -m lightx2v.infer \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/dist_infer/wan_t2v_dist_ulysses.json \
  --prompt "A cat walking on a sunny beach." \
  --seed 42 --save_result_path save_results/wan_parallel.mp4
```

The output is `save_results/wan_parallel.mp4`. When switching models, select a complete config from its [model guide](../models/index.md). For world-size, head-divisibility or unsupported-mode errors, fix the config first instead of only increasing the GPU count.
