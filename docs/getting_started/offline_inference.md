# 离线推理

通过命令行直接运行一次生成，适合单次任务和调试。重复请求或接入应用时，推荐从[服务入门](index.md)开始。

## 生成视频

先完成[环境、模型与配置准备](index.md#prepare)，再在该环境的 LightX2V 仓库根目录运行。此命令在独立进程中加载模型，不调用已运行的服务。

```bash
mkdir -p save_results
CUDA_VISIBLE_DEVICES=0 python -m lightx2v.infer \
  --model_cls wan2.1 \
  --task t2v \
  --model_path models/Wan2.1-T2V-1.3B \
  --config_json configs/wan/wan_t2v_quickstart.json \
  --prompt "A cat walking on a sunny beach." \
  --negative_prompt "blurry, low quality" \
  --size 480 832 \
  --num_frames 81 \
  --seed 42 \
  --save_result_path save_results/first_video.mp4
```

完成后打开 `save_results/first_video.mp4`。`--size` 按“高 宽”填写；显式传入的请求参数会覆盖 JSON 中的对应默认值。

与模型服务同时运行会额外占用显存，按需先停止服务或选择其他 GPU。

## 使用 Python Pipeline

在 Python 进程内加载并复用模型，见 [Python Pipeline](python_api.md)。调用独立服务进程中的模型，使用 [Python HTTP 客户端](index.md#send-request)。
