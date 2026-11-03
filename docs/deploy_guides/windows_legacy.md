# Windows 旧整合包（历史参考）

本页保留旧 Gradio 整合包的使用记录，适用于已经下载该版本的用户。它不代表当前 LightX2V 或独立 Gradio 应用的安装方式。新安装请使用 [Windows 部署](deploy_local_windows.md)或[图形界面集成](interfaces.md)。

**📦 下载软件包**

- [夸克网盘](https://pan.quark.cn/s/f44023dcf8c8)


**📁 目录结构**
解压后，确保目录结构如下：

```
├── env/                        # LightX2V 环境目录
├── LightX2V/                   # LightX2V 项目目录
├── start_lightx2v.bat          # 一键启动脚本
├── lightx2v_config.txt         # 配置文件
├── LightX2V使用说明.txt         # LightX2V使用说明
├── outputs/                    # 生成的视频保存目录
└── models/                     # 模型存放目录
```

**旧包的 RTX 50 系环境**：原记录提供了单独的运行环境。请从[夸克网盘](https://pan.quark.cn/s/52b9a8c8f07a)下载，解压后替换软件包中的 `env/` 目录即可。

**📥 下载模型**:

可直接从gradio前端下载，提供了两个下载源，huggingface和modelscope，可根据自己情况选择，或参考[模型结构文档](../getting_started/model_structure.md)手动下载


**📋 配置参数**

编辑 `lightx2v_config.txt` 文件，根据需要修改以下参数：

```ini

# 界面语言 (zh: 中文, en: 英文)
lang=zh

# 服务器端口
port=8032

# GPU设备ID (0, 1, 2...)
gpu=0

# 模型路径
model_path=models/
```

**🚀 启动服务**

双击运行 `start_lightx2v.bat` 文件，脚本将：

1. 自动读取配置文件
2. 验证模型路径和文件完整性
3. 启动 Gradio Web 界面
4. 自动打开浏览器访问服务


![Gradio中文界面](../assets/repository/figs/portabl_windows/pic_gradio_zh.png)

**⚠️ 重要提示**:

- **页面显示问题**: 旧版整合包请按随包说明排查。当前应用的依赖版本以其仓库说明为准。
