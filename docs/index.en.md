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

[Get started](getting_started/index.md){ .md-button .md-button--primary }
[Browse models](models/index.md){ .lx-hero-link }

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

<div class="lx-section-heading" markdown>

## Explore what you can create { #explore-the-model-ecosystem }

[Browse all models](models/index.md){ .lx-text-link }

</div>

Choose what you want to create or process, then find a model and its examples.

<div class="lx-capabilities" markdown>

<figure class="lx-showcase" data-showcase>
<button class="lx-showcase-play" type="button" hidden>
<img src="../assets/showcase/wan-i2v.webp" width="768" height="496" alt="" loading="lazy">
<span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>Play example</span>
</button>
<video controls preload="none" playsinline width="768" height="496" poster="../assets/showcase/wan-i2v.webp" src="https://github.com/user-attachments/assets/7bffe48f-e433-430b-91dc-ac745908ba3a" aria-label="A generated video of vegetables being stirred in a pan"></video>
<p class="lx-showcase-error" role="status" hidden>Video unavailable. <a href="https://github.com/user-attachments/assets/7bffe48f-e433-430b-91dc-ac745908ba3a">Open the source video</a></p>
<figcaption>
<strong>Wan2.1 · Image to video</strong>
<span>A generation example from the LightX2V benchmarks.</span>
<a href="getting_started/benchmark.html">View configuration and comparisons</a>
</figcaption>
</figure>

<div class="lx-task-shortcuts" markdown>

[:material-video-outline: **Video and audio**<span class="lx-task-description">Generate video from text or images, with options for synchronized audio.</span><span class="lx-task-models">Wan, MiniMax-H3, LTX</span>](models/index.md?task=video#model-catalog)
[:material-image-outline: **Image generation and editing**<span class="lx-task-description">Create images from prompts or edit existing images.</span><span class="lx-task-models">Qwen-Image, Z-Image, FLUX.2</span>](models/index.md?task=image#model-catalog)
[:material-auto-fix: **Restoration and upscaling**<span class="lx-task-description">Restore images and videos, and improve resolution and detail.</span><span class="lx-task-models">SeedVR2, SwiftVR, RelayVSR</span>](models/index.md?task=restore#model-catalog)
[:material-cube-outline: **Interaction and spatial tasks**<span class="lx-task-description">Explore interactive video, world models, and 3D reconstruction.</span><span class="lx-task-models">EdenLive, WorldMirror, WorldPlay</span>](models/index.md?task=world#model-catalog)

</div>

</div>

## Run and integrate { #start-here }

Complete [environment and model setup](getting_started/index.md#prepare), then start with the service API. Offline CLI and in-process Python examples are also available.

<div class="lx-examples" markdown>

=== ":material-api: Service API"

    ### Start a service and send a request

    Use the model and configuration from the [quickstart](getting_started/index.md#prepare). Keep terminal 1 running; send the request from terminal 2 after the service is ready.

    ```bash title="Terminal 1 · start the service"
    CUDA_VISIBLE_DEVICES=0 python -m lightx2v.server \
      --model_cls wan2.1 --task t2v \
      --model_path models/Wan2.1-T2V-1.3B \
      --config_json configs/wan/wan_t2v_quickstart.json \
      --host 0.0.0.0 --port 8080 --metric_port 8081
    ```

    ```bash title="Terminal 2 · send a request"
    curl --fail-with-body http://localhost:8080/v1/tasks/video/ \
      -H 'Content-Type: application/json' \
      -d '{
        "prompt": "A cat walking on a sunny beach.",
        "negative_prompt": "blurry, low quality",
        "seed": 42,
        "save_result_path": "first_video.mp4"
      }'
    ```

    The response contains a `task_id`. [Wait for completion and download the video :material-arrow-right:](getting_started/index.md#send-request){ .lx-text-link }

=== ":material-console: CLI"

    ### Generate your first video

    After the [quickstart setup](getting_started/index.md), reuse its model directory and starter configuration to generate a video.

    ```bash title="Terminal"
    python -m lightx2v.infer \
      --model_cls wan2.1 \
      --task t2v \
      --model_path models/Wan2.1-T2V-1.3B \
      --config_json configs/wan/wan_t2v_quickstart.json \
      --prompt "A cat walking on a sunny beach." \
      --negative_prompt "blurry, low quality" \
      --seed 42 \
      --save_result_path save_results/first_video.mp4
    ```

    [Read the offline inference guide :material-arrow-right:](getting_started/offline_inference.md){ .lx-text-link }

=== ":material-code-braces: Python"

    ### Call inference from your app

    Reuse the model and configuration created in the [quickstart](getting_started/index.md). Create a pipeline, load the model, then call `generate()`.

    ```python title="generate.py"
    from lightx2v import LightX2VPipeline

    pipe = LightX2VPipeline(
        model_path="models/Wan2.1-T2V-1.3B",
        model_cls="wan2.1",
        task="t2v",
    )
    pipe.create_generator(config_json="configs/wan/wan_t2v_quickstart.json")
    pipe.generate(
        prompt="A cat walking on a sunny beach.",
        negative_prompt="blurry, low quality",
        seed=42,
        save_result_path="save_results/first_video.mp4",
    )
    ```

    [Explore Python Pipeline :material-arrow-right:](getting_started/python_api.md){ .lx-text-link }

</div>

<div class="lx-home-bottom" markdown>

<section class="lx-home-updates" markdown>

## Recent updates

<div class="lx-updates" markdown>

<div markdown>

<time datetime="2026-10-26">2026.10.26</time>

[New autoregressive video model entry points](models/index.md)<br><span>Scripts and configurations for TaoMate-H3, StreamRender-H3, Matrix-Game-4 and more.</span>

</div>
<div markdown>

<time datetime="2026-10-18">2026.10.18</time>

[Interactive video generation with EdenLive](https://github.com/ModelTC/LightX2V/blob/main/scripts/edenlive/README.md)<br><span>Control generation with text, a target first frame and proxy recordings.</span>

</div>
<div markdown>

<time datetime="2026-10-13">2026.10.13</time>

[Run LightX2V on a MacBook](https://github.com/ModelTC/LightX2V-Mac-App)<br><span>Generate and edit images locally with a native macOS app.</span>

</div>

</div>

</section>

<aside class="lx-resource-links" markdown>

## Resources and feedback

[**Get model weights**<span>Find quantized, distilled, and other model weights.</span>](https://huggingface.co/lightx2v)
[**Read the technical blog**<span>Explore inference optimizations and engineering notes.</span>](https://light-ai.top/LightX2V-BLOG/)
[**Report a documentation issue**<span>Flag an error or suggest a clearer explanation.</span>](https://github.com/ModelTC/LightX2V-Doc/issues)
[**Report an inference issue**<span>Include your environment, configuration, and steps to reproduce.</span>](https://github.com/ModelTC/LightX2V/issues)

</aside>

</div>
