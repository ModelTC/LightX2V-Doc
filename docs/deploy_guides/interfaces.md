# 图形界面与生态集成

选择适合的交互方式，再按对应应用的说明安装。LightX2V 推理引擎与这些应用分别维护，支持模型和依赖以各应用仓库为准。

| 需求 | 入口 | 使用方式 |
| --- | --- | --- |
| 用网页表单生成图片或视频 | [Gradio-Lightx2v](https://github.com/ModelTC/Gradio-Lightx2v) | 独立安装 Gradio 应用，配置模型后启动 Web 界面 |
| 将推理组合进节点工作流 | [ComfyUI-Lightx2vWrapper](https://github.com/ModelTC/ComfyUI-Lightx2vWrapper) | 在 ComfyUI 环境安装节点，导入匹配的示例工作流 |
| 在 Apple Silicon Mac 上使用原生应用 | [LightX2V APP](https://github.com/ModelTC/LightX2V-Mac-App) | 按应用说明安装并准备其支持的模型 |
| 自己开发客户端 | [服务与首次请求](../getting_started/index.md) | 启动 HTTP 服务，通过请求生成并下载结果 |

## Gradio { #gradio }

<a id="gradio-部署指南"></a>

适合希望通过表单输入提示词、选择输入文件和查看生成结果的用户。

1. 打开 [Gradio-Lightx2v 安装说明](https://github.com/ModelTC/Gradio-Lightx2v)，确认系统和目标模型是否支持。
2. 在应用要求的环境中安装依赖，按其说明配置基础权重及可选量化、蒸馏权重。
3. 使用该仓库的启动命令，在浏览器访问它输出的地址。

原推理仓库的 `app/` 入口已移除，安装 LightX2V 不会同时安装 Gradio 应用。

## ComfyUI { #comfyui }

<a id="comfyui-部署"></a>

### ComfyUI-Lightx2vWrapper

适合已有 ComfyUI 环境、希望把生成与其他处理步骤组合的用户。

1. 按 [节点仓库说明](https://github.com/ModelTC/ComfyUI-Lightx2vWrapper)安装插件及其依赖，确认所使用的 ComfyUI Python 环境。
2. 下载与工作流匹配的模型，设置节点中的模型路径；不要把其他模型的工作流直接套用。
3. 从仓库提供的示例工作流开始，再添加 LoRA、量化或其他优化节点。

接口与节点功能随应用版本变化。遇到节点缺失、工作流导入或界面问题，向对应集成仓库反馈；可以在 LightX2V 独立复现的推理问题，向 [LightX2V Issues](https://github.com/ModelTC/LightX2V/issues)反馈。
