# 注意力机制

先按 GPU 选择后端，再检查所选模型的配置字段和并行限制。安装了算子并不代表当前硬件、模型和输入形状都能使用它。

## 按 GPU 选择 { #按-gpu-选择 }

| 场景 | 建议起点 | 使用前确认 |
| --- | --- | --- |
| 首次运行、排查额外算子安装问题 | `torch_sdpa` | 使用 PyTorch 自带实现；仍需满足模型的设备、精度和显存要求 |
| A100 / A800、RTX 3090 / 4090 | `flash_attn2` 或 `sage_attn2` | 安装与 PyTorch、CUDA、GPU 架构匹配的版本；不要使用默认 `flash_attn3` |
| H100 / H200 | `flash_attn3`；也可对比 `sage_attn2` | FlashAttention 3 面向 Hopper；使用模型配套环境 |
| RTX 5090 | 模型专用配置中的 `sage_attn2` 或 `torch_sdpa` | 使用 SM120 环境；进一步评估 `sage_attn3` 时需单独安装 Blackwell 实现并比较画质 |
| 评估 FlashAttention 4 | `flash_attn4` | 上游面向 Hopper / Blackwell；当前 LightX2V 适配仅接受 batch size 1，不提供 varlen 路径 |

硬件要求见 [FlashAttention](https://github.com/Dao-AILab/flash-attention) 和 [SageAttention](https://github.com/thu-ml/SageAttention)。模型专用配置优先于通用选择表；Qwen-Image-2.1 的 A100、Hopper 和 5090 路径见[模型指南](../models/qwen-image-2.1.md#2-环境安装)。

## LightX2V支持的注意力机制

以下为常用配置名称，不是所有内部后端的完整列表：

| 后端 | 配置值 | 定位与限制 |
| --- | --- | --- |
| PyTorch SDPA | `torch_sdpa` | 无需额外安装 attention 包，适合作为对照起点 |
| FlashAttention 2 | `flash_attn2` | Dense attention，按已安装版本核对设备支持 |
| FlashAttention 3 | `flash_attn3` | Hopper dense attention |
| FlashAttention 4 | `flash_attn4` | CuTeDSL 实现；当前适配限制见上表 |
| SageAttention 2 | `sage_attn2` | 量化 attention；替换后比较生成效果 |
| SageAttention 3 | `sage_attn3` | Blackwell FP4 attention；不是安装 SageAttention 2 后即可使用 |
| Radial Attention | `radial_attn` | 稀疏视频 self-attention，不能用于 cross-attention |
| Sol-Attn | `sol_attn` | 需匹配模型布局和 shape，完整例子见下文 |
| Sparge Attention | `sparge_attn` | 稀疏后端，需要配套依赖与模型设置 |

注册实现见 [attention 后端目录](https://github.com/ModelTC/LightX2V/tree/main/lightx2v/common/ops/attn)。不要把这些名称直接替换到所有模型或并行模式中；稀疏布局、mask、varlen 和分布式通信可能要求专用实现。

## 配置示例

以下均为字段片段，合并到完整 JSON 中，再将服务或 CLI 的 `--config_json` 指向该文件。

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

    这只替换 DiT attention。希望一并使用 Torch RoPE、归一化等算子时，标准版可从 [qwen_image_21_torch.json](https://github.com/ModelTC/LightX2V/blob/main/configs/qwen_image_21/qwen_image_21_torch.json) 开始；Turbo 需保留自身采样配置。

Wan 的 `cross_attn_2_type` 用于图像交叉注意力。Wan2.1 I2V/FLF2V 和 Wan2.2 Animate/Animate2 需要保留；T2V/VACE，以及关闭图像编码器的 Wan2.2 MoE、TI2V、S2V 无需此字段。用 SDPA 运行前一组任务时，也将此字段设为 `torch_sdpa`。

运行前查看 GPU 和软件环境：

```bash
python -c "import torch; print(torch.__version__, torch.version.cuda); print(torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))"
```

再用同一模型、seed、尺寸与采样设置完成一次请求，检查日志及输出。性能比较应排除模型加载、首次编译和预热；稀疏或量化后端还应比较画质。仅成功导入包不足以证明 kernel 可运行。

### 在 Wan2.1 上使用 Sol-Attn

Sol-Attn 是仅支持前向计算的非因果 self-attention 后端，要求连续的 BF16 张量和 128 维 attention head。RTX 5090（SM120）可使用仓库提供的固定版本环境：

```bash
docker build -f dockerfiles/Dockerfile_5090_cu130_sol_attn -t lightx2v-sol-attn:sm120 .
```

按[快速入门](../getting_started/installation.md)启动容器，将镜像替换为 `lightx2v-sol-attn:sm120`。H100/H200（SM90）按 [Sol-Attn 上游说明](https://github.com/NVlabs/Sana/tree/sol-engine/techniques/sparse_backends)安装后端。

运行前，修改 `scripts/wan/inference/run_wan_i2v_sol_attn.sh` 中的 `lightx2v_path`、`model_path` 和 `CUDA_VISIBLE_DEVICES`。再编辑 `configs/attentions/wan_i2v_sol_attn.json`，按 GPU 选择后端：

| GPU | `sol_attn_setting.dense_backend` | `cross_attn_1_type` / `cross_attn_2_type` |
| --- | --- | --- |
| H100/H200 | `flash_attn3`（默认） | `flash_attn3`（默认） |
| RTX 5090 | 改为 `sage_attn2` 或 `torch_sdpa` | 改为 `flash_attn2` 等已安装且支持的实现 |

```bash
bash scripts/wan/inference/run_wan_i2v_sol_attn.sh
```

首次调用会编译对应 shape 的 kernel，性能计时应排除该次调用。

#### 调整与实现说明

- 默认 40 步配置中，前 8 步和第 0 个 Transformer 层使用 dense 后端，其余使用 Sol-Attn。通过 `dense_steps` 和 `dense_layers` 调整；后者支持 `[0, 1]` 或 `"0-1"`。
- 示例使用 `tau=0.8`；减小该值可采用更保守的稀疏率，增大则可能降低画质。`sample_shift=3` 与标准 Wan2.1 I2V 配置一致。
- Morton3D 重排在整个 Transformer block stack 外执行一次，并同步 RoPE；strict 模式下，安装无效会直接报错。
- SM120 使用 `kv_splits=1`，`"auto"` 也会解析为 1。

### 在 MiniMax-H3 上使用 Sol-Attn

MiniMax-H3 的示例沿用 15 秒、768p、block CPU offload 配置：

运行前，将 `scripts/minimax_h3/run_minimax_h3_t2av.sh` 中的 `lightx2v_path` 和 `model_path` 改为本地目录，并将其 `--config_json` 参数改为 `"${lightx2v_path}/configs/minimax_h3/minimax_h3_sol_block_offload.json"`。

```bash
bash scripts/minimax_h3/run_minimax_h3_t2av.sh
```

对应配置为 `configs/minimax_h3/minimax_h3_sol_block_offload.json`。Sol-Attn 仅用于 50 层主 Transformer，短文本 refiner 使用 dense Torch SDPA；前 6 个去噪步骤和第 0 层通过 `dense_backend=sage_attn2` 使用 SageAttention2。H3 的 attention 序列按 `[text | audio | video]` 混合打包，不是单一的三维视频网格，因此该配置使用 `reorder=none`，不能直接启用 Wan 的 Morton3D 重排。
