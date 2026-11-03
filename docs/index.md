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

<div class="lx-section-heading" markdown>

## 看看 LightX2V 能做什么 { #探索模型生态 }

[浏览全部模型](models/index.md){ .lx-text-link }

</div>

先确定要生成或处理的内容，再选择对应模型与运行示例。

<div class="lx-capabilities" markdown>

<figure class="lx-showcase" data-showcase>
<button class="lx-showcase-play" type="button" hidden>
<img src="assets/showcase/wan-i2v.webp" width="768" height="496" alt="" loading="lazy">
<span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>播放生成示例</span>
</button>
<video controls preload="none" playsinline width="768" height="496" poster="assets/showcase/wan-i2v.webp" src="https://github.com/user-attachments/assets/7bffe48f-e433-430b-91dc-ac745908ba3a" aria-label="生成视频：在锅中翻炒蔬菜"></video>
<p class="lx-showcase-error" role="status" hidden>暂时无法加载视频。<a href="https://github.com/user-attachments/assets/7bffe48f-e433-430b-91dc-ac745908ba3a">打开原视频</a></p>
<figcaption>
<strong>Wan2.1 · 图像生成视频</strong>
<span>来自 LightX2V 性能基准的生成示例。</span>
<a href="getting_started/benchmark.html">查看配置与效果对比</a>
</figcaption>
</figure>

<div class="lx-task-shortcuts" markdown>

[:material-video-outline: **视频与音视频**<span class="lx-task-description">从文本或图像生成视频，或生成同步音视频。</span><span class="lx-task-models">Wan、MiniMax-H3、LTX</span>](models/index.md?task=video#model-catalog)
[:material-image-outline: **图像生成与编辑**<span class="lx-task-description">从提示词生成图像，或对已有图像进行编辑。</span><span class="lx-task-models">Qwen-Image、Z-Image、FLUX.2</span>](models/index.md?task=image#model-catalog)
[:material-auto-fix: **修复与超分**<span class="lx-task-description">修复图像与视频，提升分辨率和细节。</span><span class="lx-task-models">SeedVR2、SwiftVR、RelayVSR</span>](models/index.md?task=restore#model-catalog)
[:material-cube-outline: **交互与空间**<span class="lx-task-description">探索交互视频、世界模型与三维重建。</span><span class="lx-task-models">EdenLive、WorldMirror、WorldPlay</span>](models/index.md?task=world#model-catalog)

</div>

</div>

## 运行与集成 { #从这里开始 }

先完成[环境与模型准备](getting_started/index.md)，再选择命令行、Python 或 HTTP API。命令行和 Python 示例均在 LightX2V 仓库根目录运行。

<div class="lx-examples" markdown>

=== ":material-console: 命令行"

    ### 生成第一个视频

    完成[快速入门中的准备步骤](getting_started/index.md)后，复用模型目录与入门配置，直接运行生成。

    ```bash title="Terminal"
    python -m lightx2v.infer \
      --model_cls wan2.1 \
      --task t2v \
      --model_path models/Wan2.1-T2V-1.3B \
      --config_json configs/wan/wan_t2v_quickstart.json \
      --prompt "A cat walking on a sunny beach." \
      --negative_prompt "blurry, low quality" \
      --seed 42 \
      --save_result_path save_results/first_video.mp4
    ```

    [查看完整生成流程 :material-arrow-right:](getting_started/index.md){ .lx-text-link }

=== ":material-code-braces: Python"

    ### 在应用中调用

    复用[快速入门](getting_started/index.md)中下载的模型和生成的配置。创建 Pipeline，加载模型后调用 `generate()`。

    ```python title="generate.py"
    from lightx2v import LightX2VPipeline

    pipe = LightX2VPipeline(
        model_path="models/Wan2.1-T2V-1.3B",
        model_cls="wan2.1",
        task="t2v",
    )
    pipe.create_generator(config_json="configs/wan/wan_t2v_quickstart.json")
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

<div class="lx-home-bottom" markdown>

<section class="lx-home-updates" markdown>

## 近期更新

<div class="lx-updates" markdown>

<div markdown>

<time datetime="2026-10-26">2026.10.26</time>

[新增自回归视频模型运行入口](https://github.com/ModelTC/LightX2V/blob/main/README_zh.md)<br><span>TaoMate-H3、StreamRender-H3、Matrix-Game-4 等模型的脚本与配置。</span>

</div>
<div markdown>

<time datetime="2026-10-18">2026.10.18</time>

[EdenLive 交互视频生成](https://github.com/ModelTC/LightX2V/blob/main/scripts/edenlive/README_zh.md)<br><span>结合文本、首帧和代理录屏控制视频生成。</span>

</div>
<div markdown>

<time datetime="2026-10-13">2026.10.13</time>

[在 MacBook 上运行 LightX2V](https://github.com/ModelTC/LightX2V-Mac-App)<br><span>使用原生 macOS 应用在本地生成与编辑图像。</span>

</div>

</div>

</section>

<aside class="lx-resource-links" markdown>

## 资源与反馈

[**获取模型权重**<span>查找量化、蒸馏与其他模型权重。</span>](https://huggingface.co/lightx2v)
[**阅读技术博客**<span>了解推理优化方法与工程实践。</span>](https://light-ai.top/LightX2V-BLOG/)
[**反馈文档问题**<span>报告错误、补充说明或提出建议。</span>](https://github.com/ModelTC/LightX2V-Doc/issues)
[**反馈推理问题**<span>提供环境、配置和复现步骤。</span>](https://github.com/ModelTC/LightX2V/issues)

</aside>

</div>
