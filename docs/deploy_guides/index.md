---
title: 部署总览
description: 选择 LightX2V 的 API、Python 或图形界面接入方式，并按资源与延迟需求配置部署。
---

# 部署与应用集成

<p class="lx-page-lead">从一次生成走向应用：选择接入方式，再按资源与性能需求配置运行环境。</p>

先通过[模型指南](../models/index.md)完成一次离线生成，确认权重、算子和配置可用。随后选择适合应用的入口。

## <span class="lx-heading-icon" aria-hidden="true">:material-connection:</span> 选择接入方式 { #选择接入方式 .lx-icon-heading data-toc-label="选择接入方式" }

<div class="lx-destinations" markdown>

[:material-console-network-outline: **HTTP API 服务**<span>独立运行模型服务，提交生成任务，查询状态并获取结果。</span><span class="lx-destination-action">查看服务部署</span>](deploy_service.md)
[:material-code-braces: **Python 应用**<span>在代码中创建 Pipeline，复用已加载的模型进行生成。</span><span class="lx-destination-action">查看 Python API</span>](../getting_started/python_api.md)
[:material-monitor-dashboard: **Gradio 界面**<span>通过独立 Gradio 应用进行交互，按应用说明安装与启动。</span><span class="lx-destination-action">查看 Gradio 入口</span>](deploy_gradio.md)
[:material-vector-polyline: **ComfyUI 工作流**<span>使用独立集成节点，把 LightX2V 推理接入可视化工作流。</span><span class="lx-destination-action">查看 ComfyUI 集成</span>](deploy_comfyui.md)

</div>

Gradio 与 ComfyUI 集成分别维护在独立仓库中，支持的模型和安装要求以各自仓库为准。

## <span class="lx-heading-icon" aria-hidden="true">:material-tune-variant:</span> 按运行需求选择 { #按运行需求选择 .lx-icon-heading data-toc-label="按运行需求选择" }

| 当前需求 | 从哪里开始 | 需要确认 |
| --- | --- | --- |
| 显存或内存受限 | [Wan 低资源部署](for_low_resource.md) | 该指南面向 Wan2.1；量化权重、卸载设置与主机资源需匹配 |
| 缩短单次生成时间 | [低延迟部署](for_low_latency.md) | 使用匹配的蒸馏权重或评估其他加速方法，同时比较生成效果 |
| 多张 GPU 协作生成 | [并行推理](../method_tutorials/parallel.md) | 并行配置、进程数与可用 GPU 一致 |
| 运行多个独立服务 | [多 GPU 与多服务](deploy_service.md#多-gpu-与多服务) | 为各服务分别分配 GPU、API 端口和指标端口 |
| 在 Windows 上运行 | [Windows 本地部署](deploy_local_windows.md) | 使用 Windows 对应的环境、依赖和启动脚本 |

尚不确定瓶颈时，先阅读[选择加速方案](../method_tutorials/index.md)，区分显存、单次延迟与多请求需求。

## <span class="lx-heading-icon" aria-hidden="true">:material-cog-outline:</span> 进阶配置 { #进阶配置 .lx-icon-heading data-toc-label="进阶配置" }

<div class="lx-choice-list" markdown>

<div class="lx-choice" markdown>

### 使用 LoRA

<div markdown>

将 LoRA 权重加入模型配置，并检查命名与组合限制。

[阅读 LoRA 部署](lora_deploy.md)

</div>
</div>

<div class="lx-choice" markdown>

### 拆分推理阶段

<div markdown>

分别部署编码、Transformer 与解码阶段，按模型配置通信和设备。

[阅读分离式推理](disagg.md)

</div>
</div>

<div class="lx-choice" markdown>

### 单独部署 Qwen 组件

<div markdown>

查看 Qwen Image 编码器与 VAE 的独立部署路径。

[编码器部署](qwen_image_encoder.md) · [VAE TensorRT](qwen_image_vae_tensorrt.md)

</div>
</div>

</div>
