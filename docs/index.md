---
title: 欢迎来到 LightX2V
description: 轻量、高效的图像与视频生成推理框架。
home: true
hide:
  - toc
---

<div class="lx-hero" markdown>

<div class="lx-hero-copy" markdown>

# 欢迎来到 LightX2V

<p class="lx-hero-lead">轻量、高效的图像与视频生成推理框架。</p>

LightX2V 支持多种主流模型，覆盖图像生成与编辑、视频生成等任务。通过量化、蒸馏、缓存与并行推理等优化技术，提升生成速度、降低显存需求，并提供 Python 接口与服务 API，便于模型部署和应用集成。

<div class="lx-hero-actions" markdown>

[快速开始](getting_started/index.md){ .md-button .md-button--primary }
[浏览模型](models/index.md){ .lx-hero-link }

</div>

</div>

<!-- hero-visual -->

</div>

<div class="lx-entry-links" markdown>

[:material-rocket-launch-outline: **首次运行**<span>从安装到第一个视频</span>](getting_started/index.md)
[:material-view-grid-outline: **选择模型**<span>按生成任务查找示例</span>](models/index.md)
[:material-lightning-bolt-outline: **推理加速**<span>权衡速度、显存与质量</span>](method_tutorials/index.md)
[:material-console-network-outline: **部署服务**<span>接入 API 与应用</span>](deploy_guides/deploy_service.md)

</div>

## 从这里开始

先完成[环境与权重准备](getting_started/index.md)，再选择调用方式。命令行和 Python 示例均在 LightX2V 仓库根目录运行。

<div class="lx-examples" markdown>

=== ":material-console: 命令行"

    ### 生成第一个视频

    以 Wan2.1-T2V-1.3B 为例。将模型路径替换为本地目录，并在配置中选择与 GPU 匹配的[注意力算子](method_tutorials/attention.md)。

    ```bash title="Terminal"
    python -m lightx2v.infer \
      --model_cls wan2.1 \
      --task t2v \
      --model_path /path/to/Wan2.1-T2V-1.3B \
      --config_json configs/wan/wan_t2v.json \
      --prompt "A cat walking on a sunny beach." \
      --negative_prompt "blurry, low quality" \
      --seed 42 \
      --save_result_path save_results/first_video.mp4
    ```

    [查看完整生成流程 :material-arrow-right:](getting_started/first_generation.md){ .lx-text-link }

=== ":material-code-braces: Python"

    ### 在应用中调用

    创建 Pipeline，加载模型后调用 `generate()`。替换模型路径，并确认配置中的[注意力算子](method_tutorials/attention.md)适用于当前 GPU。

    ```python title="generate.py"
    from lightx2v import LightX2VPipeline

    pipe = LightX2VPipeline(
        model_path="/path/to/Wan2.1-T2V-1.3B",
        model_cls="wan2.1",
        task="t2v",
    )
    pipe.create_generator(config_json="configs/wan/wan_t2v.json")
    pipe.generate(
        prompt="A cat walking on a sunny beach.",
        negative_prompt="blurry, low quality",
        seed=42,
        save_result_path="save_results/first_video.mp4",
    )
    ```

    [了解 Python API :material-arrow-right:](getting_started/python_api.md){ .lx-text-link }

=== ":material-api: 服务 API"

    ### 通过 HTTP 提交任务

    先按[服务部署指南](deploy_guides/deploy_service.md)启动 Wan2.1 T2V 服务。请求返回 `task_id`，用于查询进度和获取生成结果。

    ```bash title="Terminal"
    curl -X POST http://localhost:8000/v1/tasks/video/ \
      -H 'Content-Type: application/json' \
      -d '{
        "prompt": "A cat walking on a sunny beach.",
        "negative_prompt": "blurry, low quality",
        "seed": 42,
        "save_result_path": "first_video.mp4"
      }'
    ```

    [查看服务与客户端指南 :material-arrow-right:](deploy_guides/deploy_service.md){ .lx-text-link }

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
