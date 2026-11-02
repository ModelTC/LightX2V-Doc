---
title: 欢迎使用 LightX2V
description: 从第一次生成，到更高效的图像与视频推理。
home: true
hide:
  - toc
---

<div class="lx-hero" markdown>

<div class="lx-hero-copy" markdown>

# LightX2V 文档

<p class="lx-hero-lead">让图像与视频推理，更轻、更快。</p>

从文本、图像到视觉内容。LightX2V 将模型运行、推理加速与部署整合到一个轻量级框架中，帮助你从第一次生成走向实际应用。

<div class="lx-hero-actions" markdown>

[快速开始 :material-arrow-right:](getting_started/index.md){ .md-button .md-button--primary }
[选择模型](models/index.md){ .md-button }

</div>

</div>

<!-- hero-visual -->

</div>

<div class="lx-capabilities" markdown>

<div class="lx-capability" markdown>

:material-movie-open-outline:{ .lx-feature-icon }

### 图像与视频生成

从文生图、图像编辑，到视频与音视频生成，按任务找到合适的模型。

[浏览模型 →](models/index.md){ .lx-card-action }

</div>

<div class="lx-capability" markdown>

:material-lightning-bolt-outline:{ .lx-feature-icon }

### 组合推理加速

结合量化、特征缓存、注意力优化与步数蒸馏，调整推理性能。

[选择加速方案 →](method_tutorials/index.md){ .lx-card-action }

</div>

<div class="lx-capability" markdown>

:material-memory:{ .lx-feature-icon }

### 适配可用显存

通过参数卸载、量化与并行配置，让模型适应你的硬件资源。

[查看低资源部署 →](deploy_guides/for_low_resource.md){ .lx-card-action }

</div>

<div class="lx-capability" markdown>

:material-console-network-outline:{ .lx-feature-icon }

### 接入应用与服务

使用 Python API、推理服务、Gradio 或 ComfyUI 构建生成工作流。

[查看服务部署 →](deploy_guides/deploy_service.md){ .lx-card-action }

</div>

</div>

## 从这里开始

选择一个入口，完成你的第一次生成。

<div class="lx-start-grid" markdown>

<div class="lx-start-main" markdown>

### 运行第一个视频示例

准备环境，下载 [Wan2.1-T2V-1.3B](models/wan.md#first-run)，并通过现有脚本生成一段视频。

<ol class="lx-steps">
<li><span>1</span>安装环境</li>
<li><span>2</span>下载模型</li>
<li><span>3</span>运行生成</li>
</ol>

[打开快速入门 :material-arrow-right:](getting_started/index.md){ .lx-text-link }

</div>

<div class="lx-start-links" markdown>

[:material-code-braces: **在 Python 中调用**<br><span>创建 Pipeline，在应用中复用模型。</span>](getting_started/python_api.md)

[:material-view-grid-outline: **按任务选择模型**<br><span>找到模型对应的权重、脚本与配置。</span>](models/index.md)

[:material-monitor: **使用图形界面**<br><span>通过 Gradio 搭建可交互的生成界面。</span>](deploy_guides/deploy_gradio.md)

</div>

</div>

## 按任务探索模型 { #探索模型生态 }

从想要生成的内容出发，查看对应模型与运行示例。

<div class="lx-task-shortcuts" markdown>

[:material-video-outline: **视频与音视频**<span>Wan、MiniMax-H3、LTX 等</span>](models/index.md?task=video#model-catalog)
[:material-image-outline: **图像生成与编辑**<span>Qwen-Image、Z-Image、FLUX.2 等</span>](models/index.md?task=image#model-catalog)
[:material-auto-fix: **修复与超分**<span>SeedVR2、SwiftVR、RelayVSR</span>](models/index.md?task=restore#model-catalog)
[:material-cube-outline: **交互与空间**<span>EdenLive、WorldMirror、WorldPlay</span>](models/index.md?task=world#model-catalog)

</div>

[查看模型总览 :material-arrow-right:](models/index.md){ .lx-text-link }

## 近期更新

<div class="lx-updates" markdown>

<div markdown><time datetime="2026-10-26">2026.10.26</time><p markdown>[新增自回归视频模型运行入口](https://github.com/ModelTC/LightX2V/blob/main/README_zh.md)<br><span>TaoMate-H3、StreamRender-H3、Matrix-Game-4 等模型的脚本与配置。</span></p></div>
<div markdown><time datetime="2026-10-18">2026.10.18</time><p markdown>[EdenLive 交互视频生成](https://github.com/ModelTC/LightX2V/blob/main/scripts/edenlive/README_zh.md)<br><span>结合文本、首帧和代理录屏控制视频生成。</span></p></div>
<div markdown><time datetime="2026-10-13">2026.10.13</time><p markdown>[在 MacBook 上运行 LightX2V](https://github.com/ModelTC/LightX2V-Mac-App)<br><span>使用原生 macOS 应用在本地生成与编辑图像。</span></p></div>

</div>

<div class="lx-community" markdown>

**一起完善 LightX2V**

[文档反馈](https://github.com/ModelTC/LightX2V-Doc/issues) · [推理问题](https://github.com/ModelTC/LightX2V/issues) · [获取模型权重](https://huggingface.co/lightx2v) · [阅读技术博客](https://light-ai.top/LightX2V-BLOG/)

</div>
