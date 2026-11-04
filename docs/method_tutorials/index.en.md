---
title: Choose an acceleration approach
description: Choose LightX2V optimizations for memory, latency or multiple GPUs, then verify speed and output quality.
---

# Choose an acceleration approach

<p class="lx-page-lead">Start with the problem you need to solve.</p>

<div class="lx-reading-note" markdown>

**Get a working baseline first.** Complete a generation using the [model guides](../models/index.md) and save the inputs, configuration and output. Change one setting at a time to compare latency, resource use and generation quality.

</div>

## Choose by goal

<div class="lx-choice-list" markdown>

<div class="lx-choice" markdown>

### :material-memory: Fit available memory

<div markdown>

Start with [parameter offload](offload.md) and [model quantization](quantization.md). Offload trades GPU memory for host memory and transfer latency; quantization needs compatible weight formats and compute backends.

For Wan2.1, start from a complete configuration in [low-resource deployment](../deploy_guides/for_low_resource.md).

</div>
</div>

<div class="lx-choice" markdown>

### :material-lightning-bolt-outline: Reduce generation latency

<div markdown>

Use [low-latency deployment](../deploy_guides/for_low_latency.md) to explore the options: use fewer sampling steps with matching distilled weights, or evaluate [attention backends](attention.md) and [feature caching](cache.md) with the original model.

If the bottleneck is unclear, inspect time spent in each stage with [performance profiling](torch_profiling.md).

</div>
</div>

<div class="lx-choice" markdown>

### :material-server-network: Use multiple GPUs

<div markdown>

To have multiple GPUs work on one generation, see [parallel inference](parallel.md). To run separate services, see [inference services](../deploy_guides/deploy_service.md).

The first approach needs matching parallel settings and process counts. The second needs separate model, GPU and port configurations.

</div>
</div>

</div>

## Compare the main methods

<p class="lx-table-hint">Scroll horizontally to see the full comparison.</p>

<div class="lx-comparison" role="region" aria-label="Acceleration methods comparison" tabindex="0" markdown>

| Method | What it changes | Check before using it |
| --- | --- | --- |
| [Model quantization](quantization.md) | Weight and compute precision | Compatible weight formats, backends and GPUs; compare output quality |
| [Parameter offload](offload.md) | Weights resident on the GPU | Host memory, disk throughput and transfer overhead; activations still need GPU memory |
| [Attention](attention.md) | The Attention implementation | Support for the chosen backend in your GPU, model and dependencies |
| [Feature caching](cache.md) | Repeated computation during denoising | Supported algorithms, reuse thresholds and output differences |
| [Step distillation](step_distill.md) | Sampling steps and model weights | Matching distilled weights, step counts and CFG settings |
| [Parallel inference](parallel.md) | Computation across GPUs | Process counts must match the parallel configuration; CFG parallelism requires CFG |
| [Variable resolution](changing_resolution.md) | Resolution in intermediate denoising stages | Model support, resolution transitions and output quality |

</div>

Check each guide and model example for supported configurations and combination limits. Validate individual changes before combining them.

## Verify the result

1. **Record a baseline.** Fix the model, input, seed, dimensions and frame count. Keep the full configuration and output.
2. **Compare the same timing scope.** Separate model loading, the first run and subsequent generations. Also observe peak GPU and host memory. Less denoising computation does not imply a proportional reduction in total latency.
3. **Inspect the output.** Compare detail, motion consistency and adherence to the prompt before changing another setting.

Once results are reproducible, use [performance profiling](torch_profiling.md) to identify bottlenecks.
