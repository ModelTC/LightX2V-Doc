# Feature Caching

Feature caching reuses intermediate results during denoising to reduce computation and may change output quality. Choose a config matching the model, weights and sampling settings, then compare against caching disabled.

## Choose by model

| Model | Current entry point | Check before use |
| --- | --- | --- |
| Wan2.1 | [Tea / Mag / TaylorSeer / Ada / Custom configs](https://github.com/ModelTC/LightX2V/tree/main/configs/caching) | Match T2V / I2V, 1.3B / 14B, dimensions and steps; Tea coefficients and Mag ratios are not interchangeable |
| HunyuanVideo-1.5 | [TeaCache / MagCache configs](https://github.com/ModelTC/LightX2V/tree/main/configs/hunyuan_video_15/cache) | Use this model's coefficients and calibration configs, not Wan data |
| MiniMax-H3 | [DPCache example](https://github.com/ModelTC/LightX2V/blob/main/scripts/minimax_h3/inference/run_minimax_h3_ref2av_sol_dpcache.sh) | Use the matching config; DiT disk streaming cannot currently be combined with caching |
| FLUX.2 klein inpainting | [Caching config](https://github.com/ModelTC/LightX2V/blob/main/configs/flux2/flux2_klein_i2i_inpaint_mask_cache.json) | Task-specific configuration, not a universal switch for all FLUX.2 tasks |

For other models, consult their implementations and examples. This page covers **feature reuse within one generation**, distinct from the service's `reuse` option for input encodings.

## Usage

### 1. Prepare a Wan2.1 MagCache config

Complete [environment and model setup](../getting_started/index.md#prepare), then run these commands from the LightX2V repository root. This example uses original Wan2.1-T2V-1.3B weights, 50 steps, CFG enabled, 480×832 and 81 frames.

Copy the matching complete config and switch only the attention backend to SDPA to avoid requiring FlashAttention 3:

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

This config **disables CPU offload** by default, so its memory requirements differ from the quickstart. If needed, adjust and validate [offload settings](offload.md); do not substitute a four-step distillation config.

### 2. Start a service and send a request

Stop any previous inference service using the same ports, then launch:

```bash
CUDA_VISIBLE_DEVICES=0 python -m lightx2v.server \
  --model_cls wan2.1 --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/caching/wan_t2v_mag_local.json \
  --host 0.0.0.0 --port 8080 --metric_port 8081
```

Check `/health`, then use the [first-request client](../getting_started/index.md#send-request) to submit, wait and download. The API also uses port 8080; publish it when using Docker. Restart the inference service after changing the config.

### 3. Compare results

Copy the same local config and set `"feature_caching": "NoCaching"` for a baseline. Keep weights, prompt, seed, dimensions, frames, steps and other backends identical. Compare warmed-up latency, memory use and video quality.

More reuse is not always better. Evaluate representative prompts; lower the threshold or disable caching if detail, motion or consistency degrades.

## MagCache parameters and calibration

| Field | Purpose |
| --- | --- |
| `feature_caching: "Mag"` | Selects MagCache |
| `magcache_calibration` | `true` runs full computation and records calibration data; `false` uses ratios to decide reuse |
| `magcache_ratios` | Residual magnitude ratios for each branch and denoising step |
| `magcache_thresh` | Accumulated-error threshold; lowering it generally reduces reuse |
| `magcache_K` | Upper bound on accumulated consecutive steps allowed by the reuse decision |
| `magcache_retention_ratio` | Fraction of initial steps retaining full computation |

Recalibrate and validate after changing weights, task, step count or sampling schedule. The following is a **single-GPU, single-request Wan2.1** calibration workflow. Stop the service above first to release GPU memory.

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

The current Wan implementation writes `wan2_1_mag_ratio.json`, `wan2_1_mag_std.json` and `wan2_1_cos_dis.json` in the working directory. Another calibration in the same directory overwrites them; keep any results you need first. Apply the ratios to the inference config:

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

Restart the service and compare under identical conditions as above. Ratios from one prompt are a starting point; validate on inputs representative of the intended workload. TeaCache uses model-specific `coefficients` and `teacache_thresh`, not Mag ratios.

## Principles and historical examples { #cache-acceleration-algorithm }

The original algorithm explanations and video comparisons are retained below. The TeaCache example identifies a single H200; other records and software versions, dates and commit revisions are incomplete. These timings have not been remeasured on the current version and do not establish a universally best algorithm.

### TeaCache
The core idea of `TeaCache` is to accumulate the **relative L1** distance between adjacent time step inputs. When the accumulated distance reaches a set threshold, it determines that the current time step should not use cache reuse; conversely, when the accumulated distance does not reach the set threshold, cache reuse is used to accelerate the inference process.

- Specifically, the algorithm calculates the relative L1 distance between the current input and the previous step input at each inference step and accumulates it.
- When the accumulated distance does not exceed the threshold, it indicates that the model state change is not obvious, so the most recently cached content is directly reused, skipping some redundant calculations. This can significantly reduce the number of forward computations of the model and improve inference speed.

The historical single-H200 timing and video comparison follows; evaluate quality on the intended inputs:

<table>
  <tr>
    <td align="center">
      Before acceleration: 58s
    </td>
    <td align="center">
      After acceleration: 17.9s
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


- Acceleration ratio: **3.24**
- Config: [wan_t2v_1_3b_tea_480p.json](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/teacache/wan_t2v_1_3b_tea_480p.json)
- Reference paper: [https://arxiv.org/abs/2411.19108](https://arxiv.org/abs/2411.19108)

### TaylorSeer Cache
The core of `TaylorSeer Cache` lies in using Taylor's formula to recalculate cached content as residual compensation for cache reuse time steps.

- The specific approach is to not only simply reuse historical cache at cache reuse time steps, but also approximately reconstruct the current output through Taylor expansion. This can further improve output accuracy while reducing computational load.
- Taylor expansion approximates changes in the cached features to reduce reuse error; validate the actual output quality.

`TaylorSeer Cache` is suitable for scenarios with high output accuracy requirements and can further improve model inference performance based on cache reuse.

<table>
  <tr>
    <td align="center">
      Before acceleration: 57.7s
    </td>
    <td align="center">
      After acceleration: 41.3s
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


- Acceleration ratio: **1.39**
- Config: [wan_t2v_taylorseer](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/taylorseer/wan_t2v_taylorseer.json)
- Reference paper: [https://arxiv.org/abs/2503.06923](https://arxiv.org/abs/2503.06923)

### AdaCache
The core idea of `AdaCache` is to dynamically adjust the step size of cache reuse based on partial cached content in specified block chunks.

- The algorithm analyzes feature differences between two adjacent time steps within specific blocks and adaptively determines the next cache reuse time step interval based on the difference magnitude.
- When model state changes are small, the step size automatically increases, reducing cache update frequency; when state changes are large, the step size decreases to limit approximation error.

This allows flexible adjustment of caching strategies based on dynamic changes in the actual inference process, achieving more efficient acceleration and better generation results. AdaCache is suitable for application scenarios that have high requirements for both inference speed and generation quality.

<table>
  <tr>
    <td align="center">
      Before acceleration: 227s
    </td>
    <td align="center">
      After acceleration: 83s
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


- Acceleration ratio: **2.73**
- Config: [wan_i2v_ada](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/adacache/wan_i2v_ada.json)
- Reference paper: [https://arxiv.org/abs/2411.02397](https://arxiv.org/abs/2411.02397)

### CustomCache
`CustomCache` combines the advantages of `TeaCache` and `TaylorSeer Cache`.

- It combines the real-time and reasonable cache decision-making of `TeaCache`, determining when to perform cache reuse through dynamic thresholds.
- At the same time, it utilizes `TaylorSeer`'s Taylor expansion method to make use of cached content.

CustomCache combines dynamic reuse decisions with Taylor expansion. The historical example below depends on its model, thresholds and inputs.

<table>
  <tr>
    <td align="center">
      Before acceleration: 57.9s
    </td>
    <td align="center">
      After acceleration: 16.6s
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


- Acceleration ratio: **3.49**
- Config: [wan_t2v_custom_1_3b](https://github.com/ModelTC/lightx2v/tree/main/configs/caching/custom/wan_t2v_custom_1_3b.json)
