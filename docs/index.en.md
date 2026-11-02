---
title: Welcome to LightX2V
description: From your first generation to faster image and video inference.
home: true
hide:
  - toc
---

<div class="lx-hero" markdown>

# LightX2V Documentation

<p class="lx-hero-lead">Lighter, faster image and video inference.</p>

Turn text and images into visual content. LightX2V brings model execution, inference acceleration and deployment into a lightweight framework, from your first generation to a working application.

<div class="lx-hero-actions" markdown>

[Get started :material-arrow-right:](getting-started/quickstart.md){ .md-button .md-button--primary }
[Choose a model](models/index.md){ .md-button }

</div>

</div>

<div class="lx-capabilities" markdown>

<div class="lx-capability" markdown>

:material-movie-open-outline:{ .lx-feature-icon }

### Generate images and videos

Find a model for text-to-image, image editing, video or audiovisual generation.

[Browse models →](models/index.md){ .lx-card-action }

</div>

<div class="lx-capability" markdown>

:material-lightning-bolt-outline:{ .lx-feature-icon }

### Combine acceleration methods

Tune inference with quantization, feature caching, attention optimization and step distillation.

[Explore acceleration →](method_tutorials/quantization.md){ .lx-card-action }

</div>

<div class="lx-capability" markdown>

:material-memory:{ .lx-feature-icon }

### Work with available memory

Use parameter offload, quantization and parallel configurations to fit your hardware.

[See low-resource deployment →](deploy_guides/for_low_resource.md){ .lx-card-action }

</div>

<div class="lx-capability" markdown>

:material-console-network-outline:{ .lx-feature-icon }

### Connect apps and services

Build generation workflows with the Python API, inference services, Gradio or ComfyUI.

[Choose a deployment path →](deploy_guides/deploy_service.md){ .lx-card-action }

</div>

</div>

## Start here

Choose an entry point for your first generation.

<div class="lx-start-grid" markdown>

<div class="lx-start-main" markdown>

### Generate your first video

Prepare the environment, download [Wan2.1-T2V-1.3B](models/wan.md#first-run), and generate a video with the provided script.

<ol class="lx-steps">
<li><span>1</span>Set up</li>
<li><span>2</span>Get weights</li>
<li><span>3</span>Generate</li>
</ol>

[Open the quickstart :material-arrow-right:](getting-started/quickstart.md){ .lx-text-link }

</div>

<div class="lx-start-links" markdown>

[:material-code-braces: **Use the Python API**<br><span>Create a pipeline and reuse it in your application.</span>](getting_started/python_api.md)

[:material-view-grid-outline: **Choose a model by task**<br><span>Find its weights, scripts and configurations.</span>](models/index.md)

[:material-monitor: **Use a graphical interface**<br><span>Set up an interactive generation UI with Gradio.</span>](deploy_guides/deploy_gradio.md)

</div>

</div>

## Explore the model ecosystem

<div class="lx-model-shortcuts" markdown>

[**Wan2.2**<span>Video generation</span>](models/wan22.md)
[**Qwen-Image-2.1**<span>Image generation and editing</span>](models/qwen-image-2.1.md)
[**MiniMax-H3**<span>Audiovisual generation</span>](https://github.com/ModelTC/LightX2V/blob/main/scripts/minimax_h3/README.md)
[**SeedVR2**<span>Restoration and upscaling</span>](https://github.com/ModelTC/LightX2V/blob/main/scripts/seedvr2/README.md)

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
