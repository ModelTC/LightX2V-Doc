# 特征缓存

特征缓存通过复用去噪过程中的中间结果减少计算，可能改变输出质量。先选择与模型、权重和采样设置匹配的配置，再与关闭缓存的结果比较。

## 按模型选择

| 模型 | 当前入口 | 使用前确认 |
| --- | --- | --- |
| Wan2.1 | [Tea / Mag / TaylorSeer / Ada / Custom 配置](https://github.com/ModelTC/LightX2V/tree/main/configs/caching) | 区分 T2V / I2V、1.3B / 14B、尺寸与采样步数；不能混用 Tea 系数或 Mag 比率 |
| HunyuanVideo-1.5 | [TeaCache / MagCache 配置](https://github.com/ModelTC/LightX2V/tree/main/configs/hunyuan_video_15/cache) | 使用本模型的系数和校准配置，不复用 Wan 数据 |
| MiniMax-H3 | [DPCache 示例](https://github.com/ModelTC/LightX2V/blob/main/scripts/minimax_h3/inference/run_minimax_h3_ref2av_sol_dpcache.sh) | 使用配套配置；当前不能与 DiT 磁盘流式加载组合 |
| FLUX.2 klein 局部编辑 | [缓存配置](https://github.com/ModelTC/LightX2V/blob/main/configs/flux2/flux2_klein_i2i_inpaint_mask_cache.json) | 这是该任务的专用配置，不是所有 FLUX.2 任务的通用开关 |

其他模型以各自实现与示例为准。此处是**同一次生成内部的特征复用**，与服务中复用输入编码的 `reuse` 参数不同。

## 使用方式

### 1. 准备 Wan2.1 MagCache 配置

先完成[环境与模型准备](../getting_started/index.md#prepare)，以下命令在 LightX2V 仓库根目录运行。示例使用原版 Wan2.1-T2V-1.3B、50 步、CFG 开启、480×832、81 帧。

复制配套的完整配置，仅将注意力后端改为 SDPA，避免依赖 FlashAttention 3：

```bash
python - <<'PYTHON'
import json
from pathlib import Path
source = Path("configs/caching/magcache/wan_t2v_mag_1_3b.json")
config = json.loads(source.read_text())
config.update(self_attn_1_type="torch_sdpa", cross_attn_1_type="torch_sdpa")
Path("configs/caching/wan_t2v_mag_local.json").write_text(json.dumps(config, indent=2))
PYTHON
```

这个配置默认 **关闭 CPU 卸载**，显存需求与入门配置不同。资源不足时先按[卸载指南](offload.md)调整并验证；不要直接替换成 4 步蒸馏配置。

### 2. 启动服务并请求

停止占用相同端口的旧推理服务，再启动缓存配置：

```bash
CUDA_VISIBLE_DEVICES=0 python -m lightx2v.server \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/caching/wan_t2v_mag_local.json \
  --host 0.0.0.0 --port 8080 --metric_port 8081
```

检查 `/health`，然后使用[首次请求客户端](../getting_started/index.md#send-request)提交、等待并下载结果。API 端口同为 8080；Docker 需映射该端口。修改配置后重启推理服务，使新设置生效。

### 3. 对比效果

将同一份本地配置复制一份，并设置 `"feature_caching": "NoCaching"` 作为基线。两次运行保持权重、prompt、seed、尺寸、帧数、步数和其他后端一致；分别记录预热后的耗时、显存与视频质量。

缓存比例更高不一定更合适。先验证多组代表性提示词，出现细节、运动或一致性下降时减小阈值或关闭缓存。

## MagCache 参数与校准

| 字段 | 作用 |
| --- | --- |
| `feature_caching: "Mag"` | 选择 MagCache |
| `magcache_calibration` | `true` 时执行完整计算并记录校准数据，`false` 时按比率决定复用 |
| `magcache_ratios` | 各分支、各去噪步骤的残差幅度比率 |
| `magcache_thresh` | 累积误差阈值；减小通常会减少复用 |
| `magcache_K` | 复用决策允许的连续累计步数上限 |
| `magcache_retention_ratio` | 前段保留完整计算的步数比例 |

改变权重、任务、采样步数或时间表后，应重新校准并验证，不能照搬原配置中的比率。以下是 **Wan2.1 单卡、一次请求**的校准流程；先停止前面的服务，释放 GPU。

```bash
python - <<'PYTHON'
import json
from pathlib import Path
config = json.loads(Path("configs/caching/wan_t2v_mag_local.json").read_text())
config["magcache_calibration"] = True
Path("configs/caching/wan_t2v_mag_calibration_local.json").write_text(json.dumps(config, indent=2))
PYTHON

CUDA_VISIBLE_DEVICES=0 python -m lightx2v.infer \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/caching/wan_t2v_mag_calibration_local.json \
  --prompt "A cat walking on a sunny beach." \
  --seed 42 --save_result_path save_results/mag_calibration.mp4
```

当前 Wan 实现会在工作目录写入 `wan2_1_mag_ratio.json`、`wan2_1_mag_std.json` 和 `wan2_1_cos_dis.json`。同目录下的再次校准会覆盖这些文件；保存所需结果后再继续。将比率写入推理配置：

```bash
python - <<'PYTHON'
import json
from pathlib import Path
path = Path("configs/caching/wan_t2v_mag_local.json")
config = json.loads(path.read_text())
config["magcache_calibration"] = False
config["magcache_ratios"] = json.loads(Path("wan2_1_mag_ratio.json").read_text())
path.write_text(json.dumps(config, indent=2))
PYTHON
```

重新启动服务，按前面的同条件对比流程评估。单个提示词得到的比率只是起点，需要在实际任务的输入集上验证。TeaCache 使用模型对应的 `coefficients` 与 `teacache_thresh`，不能用 Mag 比率替代。

## 原理与历史示例 { #缓存加速算法 }

以下保留原有算法说明和视频对比。TeaCache 示例注明了单卡 H200，其余记录及软件版本、测试日期、提交版本并不完整；表内耗时是历史示例，未在当前版本复测，也不用于判断哪种算法普遍最优。

### TeaCache
`TeaCache`的核心思想是通过对相邻时间步输入的**相对L1**距离进行累加，当累计距离达到设定阈值时，判定当前时间步不使用缓存复用；相反，当累计距离未达到设定阈值时则使用缓存复用加速推理过程。

- 具体来说，算法在每一步推理时计算当前输入与上一步输入的相对L1距离，并将其累加。
- 当累计距离未超过阈值，说明模型状态变化不明显，则直接复用最近一次缓存的内容，跳过部分冗余计算。这样可以显著减少模型的前向计算次数，提高推理速度。

历史单卡 H200 示例的耗时与视频对比如下；生成质量需结合输入单独评估：

<table>
  <tr>
    <td align="center">
      加速前：58s
    </td>
    <td align="center">
      加速后：17.9s
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/1781df9b-04df-4586-b22f-5d15f8e1bff6" width="100%" controls preload="none" playsinline></video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/e93f91eb-3825-4866-90c2-351176263a2f" width="100%" controls preload="none" playsinline></video>
    </td>
  </tr>
</table>


- 加速比为：**3.24**
- config：[wan_t2v_1_3b_tea_480p.json](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/teacache/wan_t2v_1_3b_tea_480p.json)
- 参考论文：[https://arxiv.org/abs/2411.19108](https://arxiv.org/abs/2411.19108)

### TaylorSeer Cache
`TaylorSeer Cache`的核心在于利用泰勒公式对缓存内容进行再次计算，作为缓存复用时间步的残差补偿。

- 具体做法是在缓存复用的时间步，不仅简单地复用历史缓存，还通过泰勒展开对当前输出进行近似重构。这样可以在减少计算量的同时，进一步提升输出的准确性。
- 泰勒展开能够有效捕捉模型状态的微小变化，使得缓存复用带来的误差得到补偿，用于减轻复用误差；实际效果仍需验证。

`TaylorSeer Cache`适用于对输出精度要求较高的场景，能够在缓存复用的基础上进一步提升模型推理的表现。

<table>
  <tr>
    <td align="center">
      加速前：57.7s
    </td>
    <td align="center">
      加速后：41.3s
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/2d04005c-853b-4752-884b-29f8ea5717d2" width="100%" controls preload="none" playsinline></video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/270e3624-c904-468c-813e-0c65daf1594d" width="100%" controls preload="none" playsinline></video>
    </td>
  </tr>
</table>


- 加速比为：**1.39**
- config：[wan_t2v_taylorseer](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/taylorseer/wan_t2v_taylorseer.json)
- 参考论文：[https://arxiv.org/abs/2503.06923](https://arxiv.org/abs/2503.06923)

### AdaCache
`AdaCache`的核心思想是根据指定block块中的部分缓存内容，动态调整缓存复用的步长。

- 算法会分析相邻两个时间步在特定 block 内的特征差异，根据差异大小自适应地决定下一个缓存复用的时间步间隔。
- 当模型状态变化较小时，步长自动加大，减少缓存更新频率；当状态变化较大时，步长缩小，以控制近似误差。

这样可以根据实际推理过程中的动态变化，灵活调整缓存策略，实现更高效的加速和更优的生成效果。AdaCache 适合对推理速度和生成质量都有较高要求的应用场景。

<table>
  <tr>
    <td align="center">
      加速前：227s
    </td>
    <td align="center">
      加速后：83s
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/33b2206d-17e6-4433-bed7-bfa890f9fa7d" width="100%" controls preload="none" playsinline></video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/084dbe3d-6ff3-4afc-9a7c-453ec53b3672" width="100%" controls preload="none" playsinline></video>
    </td>
  </tr>
</table>


- 加速比为：**2.73**
- config：[wan_i2v_ada](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/adacache/wan_i2v_ada.json)
- 参考论文：[https://arxiv.org/abs/2411.02397](https://arxiv.org/abs/2411.02397)

### CustomCache
`CustomCache`综合了`TeaCache`和`TaylorSeer Cache`的优势。

- 它结合了`TeaCache`在缓存决策上的实时性和合理性，通过动态阈值判断何时进行缓存复用.
- 同时利用`TaylorSeer`的泰勒展开方法对已缓存内容进行利用。

CustomCache 将动态复用决策与泰勒展开结合；下面是历史示例，效果取决于具体模型、阈值与输入。

<table>
  <tr>
    <td align="center">
      加速前：57.9s
    </td>
    <td align="center">
      加速后：16.6s
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/304ff1e8-ad1c-4013-bcf1-959ac140f67f" width="100%" controls preload="none" playsinline></video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/d3fb474a-79af-4f33-b965-23d402d3cf16" width="100%" controls preload="none" playsinline></video>
    </td>
  </tr>
</table>


- 加速比为：**3.49**
- config：[wan_t2v_custom_1_3b](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/custom/wan_t2v_custom_1_3b.json)
