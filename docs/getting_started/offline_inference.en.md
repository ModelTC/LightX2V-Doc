# Offline inference

Run generation directly from the command line for one-off jobs and debugging. For repeated requests or application integration, start with the [service quickstart](index.md).

## Generate a video

Complete the [environment, model, and configuration setup](index.md#prepare), then run from the LightX2V repository root in that environment. This command loads the model in its own process; it does not call a running service.

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

Open `save_results/first_video.mp4` when generation finishes. `--size` is `HEIGHT WIDTH`; explicit request arguments override the matching defaults in JSON.

Running this alongside a model service uses additional GPU memory. Stop the service or select another GPU if necessary.

## Use a Python Pipeline

To load and reuse a model directly in your Python process, see [Python Pipeline](python_api.md). To call a model in a separate service process, use the [Python HTTP client](index.md#send-request).
