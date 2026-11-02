# 低延迟场景部署

低延迟部署以缩短单次生成耗时为目标，同时仍需满足显存和主机内存要求。尚未确定优化方向时，可先阅读[选择加速方案](../method_tutorials/index.md)。以下按是否使用蒸馏权重介绍两条路径。

## 💡 方案一：步数蒸馏模型的推理

该方案可以参考[步数蒸馏文档](../method_tutorials/step_distill.md)

**步数蒸馏**使用匹配的蒸馏权重，以更少的采样步数完成生成。从 50 步减少到 4 步可减少去噪计算，但总耗时还包含编码、VAE 解码和数据传输，不能直接按 4/50 估算整体耗时。请使用与权重配套的采样步数和 CFG 设置，并检查生成效果；仅降低原始模型的步数不等同于使用蒸馏模型。按具体模型的支持情况，还可评估以下组合：

1. [高效注意力机制方案](../method_tutorials/attention.md)
2. [模型量化](../method_tutorials/quantization.md)

## 💡 方案二：非步数蒸馏模型的推理

没有适用的蒸馏权重，或蒸馏结果不满足质量要求时，可以保留原始模型，再评估其他优化方法。使用已有蒸馏权重进行推理不需要自行训练。

对于非步数蒸馏的原始模型，我们可以使用以下方案或者多种方案结合的方式进行加速：

1. [并行推理](../method_tutorials/parallel.md) 进行多卡并行加速。
2. [特征缓存](../method_tutorials/cache.md) 复用部分时间步的中间结果，减少重复计算。
3. [高效注意力机制方案](../method_tutorials/attention.md) 加速 Attention 的推理。
4. [模型量化](../method_tutorials/quantization.md) 加速 Linear 层的推理。
5. [变分辨率推理](../method_tutorials/changing_resolution.md) 降低中间推理步的分辨率。

## 💡 使用Tiny VAE

在某些情况下，VAE部分耗时会比较大，可以使用轻量级VAE进行加速，同时也可以降低一部分显存。

```json
{
    "use_tae": true,
    "tae_path": "/path to taew2_1.pth"
}
```
taew2_1.pth 权重可以从[这里](https://github.com/madebyollin/taehv/raw/refs/heads/main/taew2_1.pth)下载


## ⚠️ 注意

有一部分的加速方案之间目前无法结合使用，我们目前正在致力于解决这一问题。

如有问题，欢迎在 [🐛 GitHub Issues](https://github.com/ModelTC/lightx2v/issues) 中进行错误报告或者功能请求
