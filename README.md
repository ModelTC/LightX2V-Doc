# LightX2V 文档

[LightX2V](https://github.com/ModelTC/LightX2V) 的中英文文档网站，涵盖快速入门、模型使用、推理加速和部署指南。网站使用 MkDocs Material 构建，文档与主题配置在本仓库独立维护。

文档地址：[light-ai.top/LightX2V-Doc/](http://light-ai.top/LightX2V-Doc/)

## 本地预览

需要 Python 3.10 或更新版本。以下命令适用于 Bash，文档构建无需安装 LightX2V 推理依赖。

```bash
git clone https://github.com/ModelTC/LightX2V-Doc.git
cd LightX2V-Doc

python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8000
```

启动后访问：

- 中文：<http://127.0.0.1:8000/LightX2V-Doc/>
- English：<http://127.0.0.1:8000/LightX2V-Doc/en/index.html>

修改文档或主题文件后，预览会自动刷新；在终端按 `Ctrl+C` 停止服务。在远程服务器上运行时，需要将端口 8000 转发到本机。

## 目录结构

| 路径 | 内容 |
| --- | --- |
| [`docs/`](docs/) | 首页、教程和模型指南；英文文件使用 `.en.md` 后缀 |
| [`mkdocs.yml`](mkdocs.yml) | 站点配置、导航和语言设置 |
| [`theme/models.yml`](theme/models.yml) | 模型目录的数据与入口 |
| [`theme/i18n.yml`](theme/i18n.yml) | 界面中英文文案 |
| [`theme/overrides/`](theme/overrides/) | 主题模板 |
| [`theme/assets/`](theme/assets/) | 样式、脚本、图片和字体 |
| [`theme/hooks.py`](theme/hooks.py) | 模型目录渲染、共享资源与语言切换逻辑 |
| [`theme/check_site.py`](theme/check_site.py) | 构建结果检查 |
| [`.github/workflows/docs.yml`](.github/workflows/docs.yml) | 自动构建、检查与发布 |

## 贡献文档

直接修改 `docs/` 下的 Markdown 文件，并保持中英文内容一致。例如，Wan2.2 指南对应 [`docs/models/wan22.md`](docs/models/wan22.md) 和 [`docs/models/wan22.en.md`](docs/models/wan22.en.md)。新增页面时，同时更新 `mkdocs.yml` 中的导航和英文标题。

文档中的命令、参数和模型能力应与 LightX2V 对应实现一致。提交 Pull Request 前，请运行构建检查；涉及页面样式或交互时，请手动检查电脑和手机尺寸下的显示效果。

## 构建检查

在仓库根目录、已激活的虚拟环境中执行：

```bash
python -m mkdocs build --strict
python theme/check_site.py site
```

生成的网站位于 `site/`，该目录已加入 Git 忽略规则。检查涵盖站内链接与锚点、资源文件、语言切换、编辑链接、搜索索引和 sitemap；外部网站可访问性及模型推理需要单独验证。

页面约定、主题维护和发布配置见 [MAINTAINING.md](MAINTAINING.md)。

## 许可证

本项目采用 [Apache License 2.0](LICENSE)。随站点分发的 KaTeX 使用 [MIT 许可证](theme/assets/vendor/katex/LICENSE)。
