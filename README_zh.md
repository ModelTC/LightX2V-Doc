# LightX2V 文档

[English](README.md) | **中文**

[LightX2V](https://github.com/ModelTC/LightX2V) 的在线文档，涵盖入门、模型使用、推理加速与部署。基于 MkDocs Material 构建。

在线文档：[light-ai.top/LightX2V-Doc/](https://light-ai.top/LightX2V-Doc/)

## 本地预览

在可安装依赖的 Python 3.11+ 环境中执行，无需安装 LightX2V：

```bash
git clone https://github.com/ModelTC/LightX2V-Doc.git
cd LightX2V-Doc

python -m pip install -r requirements.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8000
```

打开 <http://127.0.0.1:8000/LightX2V-Doc/>，可在页面内切换中英文。

修改文档或主题后预览会自动刷新，按 `Ctrl+C` 停止。远程预览需将端口 `8000` 转发到本机。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| [`docs/`](docs/) | 文档正文 |
| [`mkdocs.yml`](mkdocs.yml) | 站点与导航配置 |
| [`theme/`](theme/) | 主题、资源与构建脚本 |
| [`requirements.txt`](requirements.txt) | 文档构建依赖 |
| [`.github/workflows/docs.yml`](.github/workflows/docs.yml) | 自动构建、检查与发布 |

修改文档、检查构建或发布网站，请参阅 [维护指南](MAINTAINING.md)。

## 许可证

本项目采用 [Apache License 2.0](LICENSE)，KaTeX 采用 [MIT](theme/assets/vendor/katex/LICENSE)。
