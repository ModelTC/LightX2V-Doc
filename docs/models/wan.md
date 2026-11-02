# Wan2.1 与 VACE

本目录提供 Wan2.1 与 VACE 的推理、服务和蒸馏示例。

设置脚本中的 `lightx2v_path`、`model_path` 和 `CUDA_VISIBLE_DEVICES`。以下命令使用仓库相对路径，也可改用脚本绝对路径。

## 使用路径

1. [选择任务](#choose-task)：确认文生视频、图生视频、首尾帧或 VACE。
2. [准备环境与权重](#环境与权重)：安装依赖，下载所选任务对应的模型。
3. [首次生成](#first-run)：以 T2V 1.3B 为例，配置路径并检查输出。
4. [调整推理性能](#next-steps)：根据显存、延迟和多卡需求选择配置。
5. [接入推理服务](#server-服务)：启动对应任务的服务，再提交请求。

## 环境与权重

先完成[环境安装](../getting_started/quickstart.md)。首次运行 T2V 1.3B 时下载：

```bash
hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir Wan-AI/Wan2.1-T2V-1.3B
```

其他任务按需选择以下下载命令，蒸馏权重仅在使用对应配置时准备：

```bash
# 其他基础模型
hf download Wan-AI/Wan2.1-T2V-14B --local-dir Wan-AI/Wan2.1-T2V-14B
hf download Wan-AI/Wan2.1-I2V-14B-480P --local-dir Wan-AI/Wan2.1-I2V-14B-480P
hf download Wan-AI/Wan2.1-I2V-14B-720P --local-dir Wan-AI/Wan2.1-I2V-14B-720P

# 下载蒸馏模型
hf download lightx2v/Wan2.1-Distill-Models --local-dir lightx2v/Wan2.1-Distill-Models
hf download lightx2v/Wan2.1-Distill-Loras --local-dir lightx2v/Wan2.1-Distill-Loras
```

`model_path` 指向完整基础模型目录。所选 JSON 中的 checkpoint 和 LoRA 路径填写下载后的本地文件路径。

<a id="choose-task"></a>

## 基础任务

| 任务 | 脚本 | 示例权重 | 配置 |
| --- | --- | --- | --- |
| 文生视频 | [run_wan_t2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_t2v.sh) | [Wan2.1-T2V-1.3B](https://huggingface.co/Wan-AI/Wan2.1-T2V-1.3B) | [wan_t2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v.json) |
| 图生视频 | [run_wan_i2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_i2v.sh) | [Wan2.1-I2V-14B-480P](https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P) | [wan_i2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_i2v.json) |
| 首尾帧生视频 | [run_wan_flf2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_flf2v.sh) | [Wan2.1-FLF2V-14B-720P](https://huggingface.co/Wan-AI/Wan2.1-FLF2V-14B-720P) | [wan_flf2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_flf2v.json) |
| 参考图／视频条件生成 | [run_wan_vace.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_vace.sh) | [Wan2.1-VACE-14B](https://huggingface.co/Wan-AI/Wan2.1-VACE-14B) | [wan_vace.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_vace.json) |

<a id="first-run"></a>

### 首次生成：T2V 1.3B

完成环境安装并下载 T2V 1.3B 后，打开 [run_wan_t2v.sh](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/run_wan_t2v.sh)，设置：

| 设置 | 如何填写 |
| --- | --- |
| `lightx2v_path` | 当前 LightX2V 仓库的绝对路径 |
| `model_path` | 下载后的 Wan2.1-T2V-1.3B 目录绝对路径 |
| `CUDA_VISIBLE_DEVICES` | 实际使用的 GPU 编号 |
| `--prompt`、`--save_result_path` | 生成内容和输出文件位置 |

默认 [wan_t2v.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v.json) 使用 `flash_attn3`，关闭 CPU offload。先按[注意力机制](../method_tutorials/attention.md)确认算子兼容性；需要卸载时，参考[低资源部署](../deploy_guides/for_low_resource.md)选择匹配配置。

从仓库根目录运行：

```bash
bash scripts/wan/run_wan_t2v.sh
```

完成后查看 `--save_result_path` 指定的视频，脚本默认保存到仓库内的 `save_results/output_lightx2v_wan_t2v.mp4`。完整安装到生成的分步说明见[生成第一个视频](../getting_started/first_generation.md)。

输入、提示词、seed 和输出路径在 sh 中修改；采样参数在 `--config_json` 指定的 JSON 中修改。`num_frames`、`size` 是未传入时的默认值，`size` 为 `[高, 宽]`。

## Server 服务

入口位于 `server/`，权重选择同上，默认监听 `0.0.0.0:8000`。

| 任务 | 启动服务 | 提交请求 |
| --- | --- | --- |
| T2V | `start_server_t2v.sh` | `post_t2v.py` |
| I2V | `start_server_i2v.sh` | `post_i2v.py` |
| FLF2V | `start_server_flf2v.sh` | `post_flf2v.py` |
| VACE | `start_server_vace.sh` | `post_vace.py` |
| T2V Reuse | `start_server_t2v_reuse.sh` | `post_t2v_reuse.py` |

以 T2V 为例：

```bash
# 终端 1：启动服务
bash scripts/wan/server/start_server_t2v.sh
```

```bash
# 终端 2：模型加载完成后提交请求
python scripts/wan/server/post_t2v.py
```

客户端修改 `url` 和 `message`。图片可传 Base64 或绝对路径，VACE 视频通过 `video_path` 传绝对路径；绝对路径须服务端可访问。输出位置通过 `save_result_path` 设置。

### Reuse：复用输入编码

T2V 使用上表 Reuse 入口。I2V 在基础 JSON 中添加 `"enable_reuse": true`、`"reuse_cache_path": "save_results/reuse_cache/wan_i2v"`，使用普通服务，在客户端 `message` 中添加 `reuse`。不同模型或服务使用独立缓存目录。

首次请求 `reuse=False`，复用输入编码时 `reuse=True`。提示词、负面提示词、帧数、尺寸及 I2V 图片路径和内容保持一致，可修改 seed；更换输入先用 `False`。

## 多卡

两卡 Ulysses 示例沿用基础 T2V 的权重和输入，配置为 [wan_t2v_parallel.json](https://github.com/ModelTC/LightX2V/blob/main/configs/wan/wan_t2v_parallel.json)：

```bash
bash scripts/wan/run_wan_t2v_parallel.sh
```

其他任务使用对应权重和基础 JSON，参照示例添加 `parallel` 并改用 `torchrun`。显卡数、`--nproc_per_node`、`parallel.seq_p_size` 保持一致，Ulysses 卡数须整除模型注意力头数。

## 进阶功能

以下入口位于 `inference/`。蒸馏和 Lazy loading 的额外权重路径需在对应 JSON 中设置。

| 功能 | 入口 |
| --- | --- |
| Compile | `run_wan_t2v_compile.sh` |
| Lazy loading | `run_wan_i2v_lazy_load.sh` |
| Sol-Attn | `run_wan_i2v_sol_attn.sh` |
| 共享 CPU offload | [使用说明](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/shared_offload/README_CN.md) |
| 连续内存布局与 baseline 对比 | [使用说明](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/offload_layout/README_CN.md) |

T2V／I2V 在基础 JSON 中添加 `"use_compile": true` 开启编译、`"warmup": true` 开启预热。I2V 使用普通入口；服务配置修改后需重启。

### 蒸馏

`inference/distill/` 提供单卡 4 步示例，按权重形式选择；model、LoRA、FP8 的多卡设置参照上一节。

| 权重形式 | T2V | I2V |
| --- | --- | --- |
| 完整蒸馏 DiT | `run_wan_t2v_distill_model.sh` | `run_wan_i2v_distill_model.sh` |
| 原始模型 + 蒸馏 LoRA | `run_wan_t2v_distill_lora.sh` | `run_wan_i2v_distill_lora.sh` |
| FP8 蒸馏 DiT | `run_wan_t2v_distill_fp8.sh` | `run_wan_i2v_distill_fp8.sh` |
| INT8 蒸馏 DiT | — | `run_wan_i2v_distill_int8.sh` |

- `run_wan_i2v_distill_single_file.sh`：蒸馏 DiT 单文件与配置、编码器、VAE 位于同一模型目录。
- `run_wan_t2v_distill_dynamic_cfg.sh`：dynamic CFG 模型，JSON 中的 `cfg_scale` 控制引导强度。
- `run_wan_t2v_distill_model_ulysses.sh`：完整蒸馏 T2V 模型的 8 卡 Ulysses 示例。

## Python API 示例

生成器创建、配置优先级、卸载和多次生成见 [Python API 指南](../getting_started/python_api.md)。
安装后，修改所选文件中的路径，从仓库根目录运行。各示例保留各自的模型、采样和注意力设置；
改用 Shell 入口的 JSON 属于显式切换配置。

| 用法 | Python 入口 |
| --- | --- |
| Wan2.1 T2V 14B | [wan_t2v.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/wan_t2v.py) |
| Wan2.1 FLF2V | [wan_flf2v.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/wan_flf2v.py) |
| Wan2.1 VACE | [wan_vace.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/wan_vace.py) |
| Wan2.1 T2V 1.3B NVFP4, 4-step | [wan_t2v_nvfp4.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/distill/wan_t2v_nvfp4.py) |
| Wan2.1 I2V 14B NVFP4, 4-step | [wan_i2v_nvfp4.py](https://github.com/ModelTC/LightX2V/blob/main/scripts/wan/inference/distill/wan_i2v_nvfp4.py) |

T2V Python 示例使用 14B 模型、`sage_attn2`、guidance 5、shift 5；基础 Shell 入口使用
1.3B 模型和其 JSON 设置。比较输出时需明确这些区别。NVFP4 使用
[Wan-NVFP4](https://huggingface.co/lightx2v/Wan-NVFP4) 中对应的四步权重，
保留 `distill_method="dmd2"`，并安装[量化算子](https://github.com/ModelTC/LightX2V/blob/main/lightx2v_kernel/nvidia/README.md)。

需要 CPU offload 时，在 JSON 中设置 `cpu_offload` 和支持的 `offload_granularity`，
见[参数卸载](../deploy_guides/for_low_resource.md)。

<a id="next-steps"></a>

## 继续优化与部署

| 目标 | 模型入口与通用指南 |
| --- | --- |
| 降低显存占用 | [低资源部署](../deploy_guides/for_low_resource.md)、[参数卸载](../method_tutorials/offload.md) |
| 使用低精度权重 | [模型量化](../method_tutorials/quantization.md)，并选择与权重匹配的后端 |
| 减少推理步数或加载 LoRA | 本页[蒸馏示例](#蒸馏)、[步数蒸馏原理](../method_tutorials/step_distill.md)、[LoRA 配置与组合限制](../deploy_guides/lora_deploy.md) |
| 使用多张 GPU | 本页[多卡示例](#多卡)、[并行推理指南](../method_tutorials/parallel.md) |
| 接入应用 | 本页 [Server 服务](#server-服务)、[服务化部署](../deploy_guides/deploy_service.md)、[Python API](../getting_started/python_api.md) |
