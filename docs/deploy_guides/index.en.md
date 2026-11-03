---
title: Deployment overview
description: Choose an API, Python or graphical interface for LightX2V, then configure deployment for your resources and latency needs.
---

# Deployment and integration

<p class="lx-page-lead">Take generation into an application: choose an interface, then configure for your resources and performance needs.</p>

Complete an offline generation using a [model guide](../models/index.md) to verify the weights, kernels and configuration. Then choose an entry point for your application.

## <span class="lx-heading-icon" aria-hidden="true">:material-connection:</span> Choose an interface { #choose-an-interface .lx-icon-heading data-toc-label="Choose an interface" }

<div class="lx-destinations" markdown>

[:material-console-network-outline: **HTTP API service**<span>Run a model service, submit generation tasks, check their status and retrieve results.</span><span class="lx-destination-action">Read the service guide</span>](deploy_service.md)
[:material-code-braces: **Python application**<span>Create a pipeline in your code and reuse the loaded model across generation calls.</span><span class="lx-destination-action">Explore the Python API</span>](../getting_started/python_api.md)
[:material-monitor-dashboard: **Gradio interface**<span>Use the standalone Gradio application, following its installation and startup instructions.</span><span class="lx-destination-action">Find the Gradio application</span>](deploy_gradio.md)
[:material-vector-polyline: **ComfyUI workflow**<span>Add LightX2V inference to a visual workflow through the standalone integration nodes.</span><span class="lx-destination-action">Explore the ComfyUI integration</span>](deploy_comfyui.md)

</div>

Gradio and ComfyUI integrations are maintained in separate repositories. Check each repository for supported models and installation requirements.

## <span class="lx-heading-icon" aria-hidden="true">:material-tune-variant:</span> Match your runtime needs { #match-your-runtime-needs .lx-icon-heading data-toc-label="Match your runtime needs" }

| Your goal | Start here | Check before running |
| --- | --- | --- |
| Fit limited GPU or host memory | [Wan low-resource deployment](for_low_resource.md) | These configurations target Wan2.1; match quantized weights, offload settings and host resources |
| Reduce generation latency | [Low-latency deployment](for_low_latency.md) | Use matching distilled weights or evaluate other optimizations, and compare output quality |
| Use multiple GPUs for one generation | [Parallel inference](../method_tutorials/parallel.md) | Match the parallel configuration, process count and available GPUs |
| Run independent services | [Multiple GPUs and services](deploy_service.md#multiple-gpus-and-multiple-services) | Assign GPUs, API ports and metrics ports to each service |
| Run on Windows | [Windows deployment](deploy_local_windows.md) | Use the Windows environment, dependencies and startup scripts |

If the bottleneck is unclear, [choose an acceleration approach](../method_tutorials/index.md) first. Distinguish memory constraints, single-request latency and multi-request workloads.

## <span class="lx-heading-icon" aria-hidden="true">:material-cog-outline:</span> Advanced configuration { #advanced-configuration .lx-icon-heading data-toc-label="Advanced configuration" }

<div class="lx-choice-list" markdown>

<div class="lx-choice" markdown>

### Use LoRA

<div markdown>

Add LoRA weights to the model configuration and check naming and combination constraints.

[Read the LoRA guide](lora_deploy.md)

</div>
</div>

<div class="lx-choice" markdown>

### Separate inference stages

<div markdown>

Deploy encoding, Transformer and decoding stages separately, configuring communication and devices for the model.

[Read the disaggregated inference guide](disagg.md)

</div>
</div>

<div class="lx-choice" markdown>

### Deploy Qwen components

<div markdown>

Explore standalone deployment paths for the Qwen Image encoder and VAE.

[Encoder deployment](qwen_image_encoder.md) · [VAE TensorRT](qwen_image_vae_tensorrt.md)

</div>
</div>

</div>
