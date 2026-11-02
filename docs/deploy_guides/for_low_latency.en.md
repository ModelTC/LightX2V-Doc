# Deployment for Low Latency Scenarios

In low latency scenarios, we pursue faster speed, ignoring issues such as video memory and RAM overhead. We provide two solutions:

## 💡 Solution 1: Inference with Step Distillation Model

This solution can refer to the [Step Distillation Documentation](../method_tutorials/step_distill.md)

🧠 **Step Distillation** is a very direct acceleration inference solution for video generation models. By distilling from 50 steps to 4 steps, the time consumption will be reduced to 4/50 of the original. At the same time, under this solution, it can still be combined with the following solutions:

1. [Efficient Attention Mechanism Solution](../method_tutorials/attention.md)
2. [Model Quantization](../method_tutorials/quantization.md)

## 💡 Solution 2: Inference with Non-Step Distillation Model

Step distillation requires relatively large training resources, and the model after step distillation may have degraded video dynamic range.

For the original model without step distillation, we can use the following solutions or a combination of multiple solutions for acceleration:

1. [Parallel Inference](../method_tutorials/parallel.md) for multi-GPU parallel acceleration.
2. [Feature Caching](../method_tutorials/cache.md) to reduce the actual inference steps.
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
