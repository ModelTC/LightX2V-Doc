---
title: Welcome to LightX2V
description: A lightweight, efficient inference framework for image and video generation.
home: true
hide:
  - toc
---

<div class="lx-hero" markdown>

<div class="lx-hero-copy" markdown>

# Welcome to LightX2V

<p class="lx-hero-lead">A lightweight, efficient inference framework for image and video generation.</p>

LightX2V supports a range of popular models for image generation, image editing, and video generation. Optimizations such as quantization, distillation, caching, and parallel inference improve generation speed and reduce GPU memory requirements. Python and service APIs simplify model deployment and application integration.

<div class="lx-hero-actions" markdown>

[Get started :material-arrow-right:](getting_started/index.md){ .md-button .md-button--primary }
[Choose a model](models/index.md){ .md-button }

</div>

</div>

<!-- hero-visual -->

</div>

<div class="lx-entry-links" markdown>

[:material-rocket-launch-outline: **First generation**<span>From setup to your first video</span>](getting_started/index.md)
[:material-view-grid-outline: **Choose a model**<span>Find examples by task</span>](models/index.md)
[:material-lightning-bolt-outline: **Accelerate inference**<span>Balance speed, memory, and quality</span>](method_tutorials/index.md)
[:material-console-network-outline: **Deploy a service**<span>Connect APIs and applications</span>](deploy_guides/deploy_service.md)

</div>

## Start here

Complete [environment and model setup](getting_started/index.md), then choose how to run inference. Run CLI and Python examples from the LightX2V repository root.

<div class="lx-examples" markdown>

=== ":material-console: CLI"

    ### Generate your first video

    This example uses Wan2.1-T2V-1.3B. Replace the model path with your local directory and select an [attention backend](method_tutorials/attention.md) compatible with your GPU.

    ```bash title="Terminal"
    python -m lightx2v.infer \
      --model_cls wan2.1 \
      --task t2v \
      --model_path /path/to/Wan2.1-T2V-1.3B \
      --config_json configs/wan/wan_t2v.json \
      --prompt "A cat walking on a sunny beach." \
      --negative_prompt "blurry, low quality" \
      --seed 42 \
      --save_result_path save_results/first_video.mp4
    ```

    [Read the generation walkthrough :material-arrow-right:](getting_started/first_generation.md){ .lx-text-link }

=== ":material-code-braces: Python"

    ### Call inference from your app

    Create a pipeline, load the model, then call `generate()`. Replace the model path and check that the configured [attention backend](method_tutorials/attention.md) supports your GPU.

    ```python title="generate.py"
    from lightx2v import LightX2VPipeline

    pipe = LightX2VPipeline(
        model_path="/path/to/Wan2.1-T2V-1.3B",
        model_cls="wan2.1",
        task="t2v",
    )
    pipe.create_generator(config_json="configs/wan/wan_t2v.json")
    pipe.generate(
        prompt="A cat walking on a sunny beach.",
        negative_prompt="blurry, low quality",
        seed=42,
        save_result_path="save_results/first_video.mp4",
    )
    ```

    [Explore the Python API :material-arrow-right:](getting_started/python_api.md){ .lx-text-link }

=== ":material-api: Service API"

    ### Submit a task over HTTP

    Start a Wan2.1 T2V service using the [deployment guide](deploy_guides/deploy_service.md). The response includes a `task_id` for checking progress and retrieving the result.

    ```bash title="Terminal"
    curl -X POST http://localhost:8000/v1/tasks/video/ \
      -H 'Content-Type: application/json' \
      -d '{
        "prompt": "A cat walking on a sunny beach.",
        "negative_prompt": "blurry, low quality",
        "seed": 42,
        "save_result_path": "first_video.mp4"
      }'
    ```

    [Read the service and client guide :material-arrow-right:](deploy_guides/deploy_service.md){ .lx-text-link }

</div>

## Explore models by task { #explore-the-model-ecosystem }

Start with what you want to create, then find the models and examples for that task.

<div class="lx-task-shortcuts" markdown>

[:material-video-outline: **Video and audio**<span>Wan, MiniMax-H3, LTX and more</span>](models/index.md?task=video#model-catalog)
[:material-image-outline: **Image generation and editing**<span>Qwen-Image, Z-Image, FLUX.2 and more</span>](models/index.md?task=image#model-catalog)
[:material-auto-fix: **Restoration and upscaling**<span>SeedVR2, SwiftVR, RelayVSR</span>](models/index.md?task=restore#model-catalog)
[:material-cube-outline: **Interaction and spatial tasks**<span>EdenLive, WorldMirror, WorldPlay</span>](models/index.md?task=world#model-catalog)

</div>

[View the model catalog :material-arrow-right:](models/index.md){ .lx-text-link }

## Recent updates

<div class="lx-updates" markdown>

<div markdown><time datetime="2026-10-26">2026.10.26</time><p markdown>[New autoregressive video model entry points](https://github.com/ModelTC/LightX2V/blob/main/README.md)<br><span>Scripts and configurations for TaoMate-H3, StreamRender-H3, Matrix-Game-4 and more.</span></p></div>
<div markdown><time datetime="2026-10-18">2026.10.18</time><p markdown>[Interactive video generation with EdenLive](https://github.com/ModelTC/LightX2V/blob/main/scripts/edenlive/README.md)<br><span>Control generation with text, a target first frame and proxy recordings.</span></p></div>
<div markdown><time datetime="2026-10-13">2026.10.13</time><p markdown>[Run LightX2V on a MacBook](https://github.com/ModelTC/LightX2V-Mac-App)<br><span>Generate and edit images locally with a native macOS app.</span></p></div>

</div>

<div class="lx-community" markdown>

**Help improve LightX2V**

[Documentation issues](https://github.com/ModelTC/LightX2V-Doc/issues) · [Inference issues](https://github.com/ModelTC/LightX2V/issues) · [Get model weights](https://huggingface.co/lightx2v) · [Read the technical blog](https://light-ai.top/LightX2V-BLOG/)

</div>
