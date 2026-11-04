---
title: 选择加速方案
description: 从显存、延迟与多卡需求出发，选择 LightX2V 的优化方法，并验证速度和生成效果。
---

# 选择加速方案

<p class="lx-page-lead">先明确要解决的问题，再选择优化方法。</p>

<div class="lx-reading-note" markdown>

**先跑通，再优化。** 从[模型指南](../models/index.md)完成一次基础生成，保留输入、配置与输出。后续每次只调整一项设置，便于比较耗时、资源占用和生成效果。

</div>

## 按目标选择

<div class="lx-choice-list" markdown>

<div class="lx-choice" markdown>

### :material-memory: 显存不足

<div markdown>

先查看[参数卸载](offload.md)和[模型量化](quantization.md)。卸载需要权衡主机内存与传输延迟；量化需要匹配权重格式和计算后端。

使用 Wan2.1 时，可从[低资源部署](../deploy_guides/for_low_resource.md)中的完整配置开始。

</div>
</div>

<div class="lx-choice" markdown>

### :material-lightning-bolt-outline: 单次生成太慢

<div markdown>

从[低延迟部署](../deploy_guides/for_low_latency.md)了解不同路径：有匹配的蒸馏权重时考虑减少采样步数；使用原始模型时，再评估[注意力后端](attention.md)与[特征缓存](cache.md)。

还不清楚瓶颈时，先用[性能分析](torch_profiling.md)观察各阶段耗时。

</div>
</div>

<div class="lx-choice" markdown>

### :material-server-network: 使用多张 GPU

<div markdown>

希望多张卡协同完成一次生成，查看[并行推理](parallel.md)；希望运行多个独立服务，查看[服务化部署](../deploy_guides/deploy_service.md)。

前者需要匹配并行配置与进程数，后者需要分别配置模型、GPU 和服务端口。

</div>
</div>

</div>

## 对比主要方法

<p class="lx-table-hint">左右滑动查看完整对照表。</p>

<div class="lx-comparison" role="region" aria-label="加速方法对照表" tabindex="0" markdown>

| 方法 | 主要调整什么 | 使用前确认 |
| --- | --- | --- |
| [模型量化](quantization.md) | 权重与计算精度 | 权重格式、后端和 GPU 是否匹配；比较输出质量 |
| [参数卸载](offload.md) | GPU 上驻留的权重规模 | CPU 内存、磁盘吞吐量和传输开销；激活显存仍需预留 |
| [注意力机制](attention.md) | Attention 的计算实现 | 当前 GPU、模型与依赖是否支持所选后端 |
| [特征缓存](cache.md) | 去噪过程中的重复计算 | 当前模型支持的算法、复用阈值与输出差异 |
| [步数蒸馏](step_distill.md) | 采样步数与对应模型权重 | 使用匹配的蒸馏权重、步数和 CFG 配置 |
| [并行推理](parallel.md) | 多 GPU 之间的计算分配 | 启动进程数与并行规模一致；CFG 并行需要开启 CFG |
| [变分辨率推理](changing_resolution.md) | 中间去噪阶段的分辨率 | 模型支持情况、分辨率切换设置与生成效果 |

</div>

各方法的适用范围和组合限制以对应指南及模型示例为准。先验证单项变化，再逐步组合。

## 如何验证优化效果

1. **记录基线。** 固定模型、输入、随机种子、尺寸和帧数，记录完整配置及输出。
2. **比较同一范围的耗时。** 区分模型加载、首次运行与后续生成；同时观察峰值显存和主机内存。减少去噪计算不代表总耗时会按相同比例下降。
3. **检查生成结果。** 对比细节、运动连贯性和提示词符合程度，确认效果后再调整下一项设置。

已有可复现的结果时，可以通过[性能分析](torch_profiling.md)进一步定位瓶颈。
