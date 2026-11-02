# Deployment for Low Latency Scenarios

Low-latency deployment aims to shorten each generation while staying within GPU and host memory limits. If you have not chosen an optimization path, start with [Choose an acceleration approach](../method_tutorials/index.md). The two paths below depend on whether you use distilled weights.

## 💡 Solution 1: Inference with Step Distillation Model

This solution can refer to the [Step Distillation Documentation](../method_tutorials/step_distill.md)

**Step distillation** uses matching distilled weights to generate with fewer sampling steps. Going from 50 steps to 4 reduces denoising computation, but total latency also includes encoding, VAE decoding and data transfers; it cannot be estimated simply as 4/50 of the original. Use the sampling steps and CFG settings intended for the weights, and check output quality. Reducing the step count of the original model alone is not equivalent to using a distilled model. Depending on model support, also evaluate these combinations:

1. [Efficient Attention Mechanism Solution](../method_tutorials/attention.md)
2. [Model Quantization](../method_tutorials/quantization.md)

## 💡 Solution 2: Inference with Non-Step Distillation Model

If suitable distilled weights are unavailable or their output does not meet your quality requirements, keep the original model and evaluate other methods. Running inference with existing distilled weights does not require training your own model.

For the original model without step distillation, we can use the following solutions or a combination of multiple solutions for acceleration:

1. [Parallel Inference](../method_tutorials/parallel.md) for multi-GPU parallel acceleration.
2. [Feature Caching](../method_tutorials/cache.md) to reuse intermediate results at selected timesteps and reduce repeated computation.
3. [Efficient Attention Mechanism Solution](../method_tutorials/attention.md) to accelerate Attention inference.
4. [Model Quantization](../method_tutorials/quantization.md) to accelerate Linear layer inference.
5. [Variable Resolution Inference](../method_tutorials/changing_resolution.md) to reduce the resolution of intermediate inference steps.

## 💡 Using Tiny VAE

In some cases, the VAE component can be time-consuming. You can use a lightweight VAE for acceleration, which can also reduce some GPU memory usage.

```json
{
    "use_tae": true,
    "tae_path": "/path to taew2_1.pth"
}
```
The taew2_1.pth weights can be downloaded from [here](https://github.com/madebyollin/taehv/raw/refs/heads/main/taew2_1.pth)

## ⚠️ Note

Some acceleration solutions currently cannot be used together, and we are working to resolve this issue.

If you have any questions, feel free to report bugs or request features in [🐛 GitHub Issues](https://github.com/ModelTC/lightx2v/issues)
