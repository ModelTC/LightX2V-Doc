# 并行推理

多张 GPU 可以协作完成同一次生成。先按模型选择并行方式，再让 `torchrun` 进程数与配置一致。若要让多张卡分别处理独立请求，使用[多个独立服务](../deploy_guides/deploy_service.md#多-gpu-与多服务)。

## 选择并行方式

| 方式 | 配置字段 | 分配的计算 | 主要限制 |
| --- | --- | --- | --- |
| 序列并行 SP | `seq_p_size`、`seq_p_attn_type` | 将序列分给多个 rank，使用 Ulysses 或 Ring 通信 | 模型与 attention 后端需支持；不能据此假定所有权重都会分片 |
| CFG 并行 | `cfg_p_size` | 条件与无条件分支分别计算 | 通常为 2，要求 `enable_cfg=true`；模型自身还需支持 |
| 张量并行 TP | `tensor_p_size` | 对支持的权重与算子分片 | 模型、量化方式和卸载路径须兼容，不能只增加这个字段 |

### 模型入口与限制

| 模型 | 可参考入口 | 明确限制 |
| --- | --- | --- |
| Wan2.1 | [Ulysses / Ring / CFG 配置](https://github.com/ModelTC/LightX2V/tree/main/configs/dist_infer) | 选择 `wan_*` 配置；CFG 关闭的蒸馏模型不使用 CFG 并行 |
| Wan2.2 MoE | [TP4 服务脚本](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan22/server/start_server_t2v_tp.sh)、[SP / CFG 配置](https://github.com/ModelTC/LightX2V/tree/main/configs/dist_infer) | MoE、TI2V、S2V 的任务和配置不同，按[模型指南](../models/wan22.md)选择 |
| Qwen-Image-2.1 | [双卡 5090 配置](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21_5090_2k_sp2.json) | SP 仅支持 Ulysses；不支持 CFG 并行。启用 TP 时，每卡 attention head 数还须能被 SP 度数整除 |
| SeedVR2 | [7B SP 配置](https://github.com/ModelTC/LightX2V/blob/main/configs/seedvr/seedvr2_7b_sp.json) | SP 支持 `ulysses` / `ulysses-4090`；要求 TP=1、CFG=1，且启用 `parallel.vae_parallel`。SP 请求不接受 `image_path` |

表中入口不是各模型所有组合的保证。Qwen 的 5090 配置同时包含模型专用量化设置，不能只复制并行字段而忽略配套权重与依赖。

## 进程数与设备

仅使用 TP、SP 和 CFG、未启用流水线并行时：

```text
N = tensor_p_size × seq_p_size × cfg_p_size
```

省略的值按 1 计。例如 SP4 需要 4 个进程，SP4 + CFG2 需要 8 个进程，TP4 需要 4 个进程。`CUDA_VISIBLE_DEVICES`、`--nproc_per_node` 和 JSON 必须一致；模型还可能对 attention head 数施加整除约束。

更多 GPU 不一定更快：通信、卡间互联和输入大小会影响收益。先验证单卡结果，再比较同条件下的多卡耗时。

## DiT 并行配置

以下 JSON 均为片段，需合并到完整的模型配置中。

### 1. Ulysses 并行

```json
{
  "parallel": {
    "seq_p_size": 4,
    "seq_p_attn_type": "ulysses"
  }
}
```

### 2. Ring 并行

仅对提供 Ring 支持的模型和 attention 后端使用：

```json
{
  "parallel": {
    "seq_p_size": 4,
    "seq_p_attn_type": "ring"
  }
}
```

## Cfg 并行配置

适用于支持 CFG 并行且开启 CFG 的模型，不能套用到关闭 CFG 的蒸馏配置：

```json
{
  "enable_cfg": true,
  "parallel": {"cfg_p_size": 2}
}
```

## 张量并行配置

例如 Wan2.2 MoE 的 [TP4 完整配置](https://github.com/ModelTC/LightX2V/blob/main/configs/wan22/wan_moe_t2v_tp.json)：

```json
{
  "parallel": {"tensor_p_size": 4}
}
```

## 混合并行配置

以下 SP4 + CFG2 需要 8 个进程，且模型须支持两者组合：

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

## 使用方式

### 四卡 Wan2.1 服务

先完成[环境与完整模型准备](../getting_started/index.md#prepare)。从仓库根目录使用原版 Wan2.1-T2V-1.3B 和 `configs/dist_infer/wan_t2v_dist_ulysses.json`；该配置为 50 步、CFG 开启、SP4，默认关闭 CPU offload。

启动前核对 `self_attn_1_type`、`cross_attn_1_type`：默认 `flash_attn3` 面向 Hopper。其他 GPU 可将两者改为 `torch_sdpa`，或选择已安装且支持该模型的后端。停止占用相同端口或 GPU 的旧推理服务后运行：

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun --standalone --nproc_per_node=4 \
  -m lightx2v.server \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/dist_infer/wan_t2v_dist_ulysses.json \
  --host 0.0.0.0 --port 8080 --metric_port 8081
```

服务就绪后，使用[首次请求客户端](../getting_started/index.md#send-request)提交与下载。只向这个服务发送一次请求，各 rank 会协作执行；不需要向每张 GPU 单独发送请求。Docker 仍需映射 API 端口 8080。

### 离线生成

停止服务后，可使用同一配置运行离线示例：

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun --standalone --nproc_per_node=4 \
  -m lightx2v.infer \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/dist_infer/wan_t2v_dist_ulysses.json \
  --prompt "A cat walking on a sunny beach." \
  --seed 42 --save_result_path save_results/wan_parallel.mp4
```

输出为 `save_results/wan_parallel.mp4`。更换模型时，从[对应模型指南](../models/index.md)选择完整配置；出现进程数不匹配、head 数不能整除或不支持的并行方式时，先修正配置，不要仅增加 GPU 数量。
