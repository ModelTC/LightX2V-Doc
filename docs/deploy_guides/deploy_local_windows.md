# Windows 本地部署指南

使用当前源码与独立 Python 环境运行服务，再通过 HTTP 请求生成。图形界面使用[独立应用](interfaces.md)。

## 准备环境与模型

先按[Windows 安装说明](../getting_started/installation.md#windows-environment-setup)配置依赖。本页命令使用 **Windows CMD / Anaconda Prompt**，不是 PowerShell 或 Bash；激活 LightX2V 环境并进入推理仓库根目录后执行。

以下示例使用支持 BF16 的 NVIDIA GPU、Wan2.1-T2V-1.3B 原始权重与 CPU 卸载。主机内存和显存仍需容纳模型组件及中间结果，不能仅按“1.3B”估算容量。下载完整模型并复制配置：

```bat
python -m pip install -U huggingface_hub
hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir models/Wan2.1-T2V-1.3B
copy configs\wan\wan_t2v.json configs\wan\wan_t2v_windows.json
```

打开 `configs/wan/wan_t2v_windows.json`，将以下字段合并进去，保留原配置的 50 步、CFG 和其他采样设置。不要用下面的片段覆盖整个文件：

```json
{
  "self_attn_1_type": "torch_sdpa",
  "cross_attn_1_type": "torch_sdpa",
  "cpu_offload": true,
  "offload_granularity": "block",
  "t5_cpu_offload": true,
  "vae_cpu_offload": true
}
```

这使用 PyTorch 自带的 SDPA，无需为该示例额外安装 FlashAttention。

## 启动服务并发送请求

终端 1 启动服务，保持运行：

```bat
set CUDA_VISIBLE_DEVICES=0
python -m lightx2v.server ^
  --model_cls wan2.1 --task t2v ^
  --model_path models/Wan2.1-T2V-1.3B ^
  --config_json configs/wan/wan_t2v_windows.json ^
  --host 127.0.0.1 --port 8080 --metric_port 8081
```

等待日志出现 `Application startup complete.`。在同一台电脑另开 CMD 终端，检查就绪并提交一次请求：

```bat
curl.exe --fail http://localhost:8080/health
curl.exe --fail -X POST http://localhost:8080/v1/tasks/video/ ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"A cat walking on a sunny beach.\",\"seed\":42,\"save_result_path\":\"windows_first_video.mp4\"}"
```

保存返回的 `task_id`，将下面的 `TASK_ID` 替换为它。先查询状态；只有 `status` 为 `completed` 时才执行下载命令：

```bat
curl.exe --fail http://localhost:8080/v1/tasks/TASK_ID/status
curl.exe --fail http://localhost:8080/v1/tasks/TASK_ID/result -o first_video.mp4
```

结果下载到终端 2 当前目录的 `first_video.mp4`。若状态为 `failed`，查看响应错误与服务日志；任务管理见[服务 API 参考](deploy_service.md)。

## 其他使用方式

- [Python Pipeline](../getting_started/python_api.md)：在 Python 进程中复用模型。
- [Windows 批处理脚本](https://github.com/ModelTC/LightX2V/tree/main/scripts/win)：运行前修改脚本内仓库与模型路径，同时检查配套配置。`run_wan_t2v.bat` 引用的配置为 4 步，并要求 T5 量化权重，不能直接当作原始权重的 50 步示例。
- [Gradio 与 ComfyUI](interfaces.md)：分别在应用要求的环境中安装，模型支持范围以集成仓库为准。

<a id="旧版整合包一键启动-gradio"></a>

旧包的下载、配置文件和启动记录见 [Windows 旧整合包](windows_legacy.md)。
