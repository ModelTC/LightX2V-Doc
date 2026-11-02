# LightX2V 文档网站

这是独立的文档仓库：**文档正文、网站样式、构建配置和发布流程都放在这里**。克隆本仓库即可预览和构建，不需要同时克隆 LightX2V，也不需要安装推理环境或 GPU 依赖。

仓库：[ModelTC/LightX2V-Doc](https://github.com/ModelTC/LightX2V-Doc)。发布地址：[light-ai.top/LightX2V-Doc/](http://light-ai.top/LightX2V-Doc/)。

页面延续已确认的方向：参考 SGLang 的首页与内容组织，用 MkDocs Material 加定制样式实现，优先优化电脑端，同时兼顾手机端。

## 本地预览

使用 Python 3.10 或更新版本，在本仓库根目录执行：

```bash
python -m venv /path/to/tmp/lightx2v-docs-venv
/path/to/tmp/lightx2v-docs-venv/bin/python -m pip install -r requirements.txt
/path/to/tmp/lightx2v-docs-venv/bin/python -m mkdocs serve --dev-addr 127.0.0.1:8000
```

中文首页为 `http://127.0.0.1:8000/LightX2V-Doc/`，英文首页为 `http://127.0.0.1:8000/LightX2V-Doc/en/index.html`。本地预览保留正式网站的路径前缀。在远程服务器上运行时，将端口 8000 转发到本机。编辑 Markdown、主题模板或样式后，预览会自动刷新。

当前开发机器已有环境，也可以继续使用这个启动命令：

```bash
bash /data/nvme1/zhangbilang/tmp/start-lightx2v-docs.sh --dev-addr 127.0.0.1:8000
```

## 以后改哪里

| 要修改的内容 | 位置 |
| --- | --- |
| 中文首页、教程和模型指南 | `docs/**/*.md` |
| 对应的英文页面 | 同目录下的 `*.en.md` |
| 导航与主题设置 | `mkdocs.yml` |
| 首页、模型卡片和文章样式 | `theme/assets/stylesheets/lightx2v.css` |
| 模型分类、描述与入口 | `theme/models.yml` |
| 界面中英文文案 | `theme/i18n.yml` |
| 模板、语言切换与目录 | `theme/overrides/`、`theme/hooks.py` |
| 图片、字体、脚本 | `theme/assets/` |
| 构建检查与发布 | `theme/check_site.py`、`.github/workflows/docs.yml` |

例如，中文 Wan2.2 指南在 `docs/models/wan22.md`，英文在 `docs/models/wan22.en.md`。新版网站直接读取这些文件；修改旧 LightX2V 仓库中的文档或 README **不会自动同步**到这里。涉及运行命令或模型能力的更新，需要同步维护这里的说明。

现有版本共 60 个页面，中英文各 30 个；包含完整教程和 Wan2.1、Wan2.2、Qwen-Image-2.1 三组模型指南。其他模型入口，以及脚本、配置和代码链接，仍指向 [LightX2V 推理仓库](https://github.com/ModelTC/LightX2V)。这些链接不构成本地构建依赖。

## 构建检查

```bash
python -m mkdocs build --strict --site-dir /path/to/tmp/lightx2v-docs-site
python theme/check_site.py /path/to/tmp/lightx2v-docs-site
```

检查覆盖页面和锚点链接、图片和字体、语言切换、搜索索引，以及配置了站点地址时的 canonical 和 sitemap。默认不联网检查外部链接，也不运行模型推理。

测试带路径前缀的发布地址：

```bash
export LIGHTX2V_DOCS_URL=https://docs.example.invalid/LightX2V-Doc/
python -m mkdocs build --strict --site-dir /path/to/tmp/lightx2v-docs-site
python theme/check_site.py /path/to/tmp/lightx2v-docs-site --site-url "$LIGHTX2V_DOCS_URL"
unset LIGHTX2V_DOCS_URL
```

生成物是静态网站。使用 HTTP 服务查看，不要直接双击 HTML 文件，否则搜索无法正常加载。

## 上传 GitHub 并发布

发布由本仓库的 GitHub Actions 完成。首次启用时：

1. 将文档改动推送到 `https://github.com/ModelTC/LightX2V-Doc.git` 的 `main` 分支。本地 `origin` 已连接这个仓库。
2. 先看 **Actions → Documentation** 构建结果。默认只构建、检查并提供 `lightx2v-docs-preview` 下载包，不发布网站。
3. 在新仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。
4. 在 **Settings → Secrets and variables → Actions → Variables** 新增仓库变量 `DOCS_PUBLISH`，值填 `true`。
5. 到 **Actions → Documentation → Run workflow**，选择 `main` 并运行。通过检查后，部署任务会显示网站地址；以后推送到 `main` 会自动更新网站。PR 只构建检查。

发布流程使用 [GitHub 官方的 Pages Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。默认站点地址为 `http://light-ai.top/LightX2V-Doc/`；发布构建使用 Pages 返回的实际地址，开启 HTTPS 后会自动使用 HTTPS canonical。

ModelTC 的组织主页使用 `light-ai.top`，项目站点按 GitHub 的[域名继承规则](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages#using-a-custom-domain-across-multiple-repositories)使用 `/LightX2V-Doc/` 路径。在本项目的 Pages 设置中保持 **Custom domain 为空**，继承组织域名；不要把带路径的完整网址填进 Custom domain，也不要在本仓库添加覆盖组织域名的 CNAME 文件。

“编辑此页”默认指向 `ModelTC/LightX2V-Doc` 的 Markdown 文件，CI 中会按构建分支调整。通过 `LIGHTX2V_DOCS_EDIT_URI` 可覆盖这个地址。页面顶部的 GitHub 项目入口仍指向推理仓库。

将 `DOCS_PUBLISH` 改为 `false` 会停止后续自动部署，但不会删除已经发布的网站。现有旧文档站的域名和入口需要另行迁移。

更多维护约定见 [MAINTAINING.md](MAINTAINING.md)。
