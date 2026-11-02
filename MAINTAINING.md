# 维护指南

本文件面向文档和网站维护者。本地环境安装与预览命令见 [README.md](README.md)。

## 内容维护

`docs/` 是本站的文档来源。LightX2V 推理仓库中的文档和模型 README 不会自动同步到本站；推理接口、配置或模型能力发生变化时，需要更新相关教程。

### 页面与语言

- 中文文件使用 `page.md`，英文使用同目录下的 `page.en.md`。
- 导航引用中文文件路径，英文导航标题配置在 `mkdocs.yml` 的 `nav_translations` 中。严格构建会报告未加入导航的页面。
- 中文页面位于站点根路径下，英文页面位于 `en/` 下，均使用 `.html` 地址。例如 `models/wan.html` 与 `en/models/wan.html`。
- 新增或修改页面时同步维护两种语言。缺少翻译时，站点会显示回退提示，语言按钮会提供相应语言的首页入口。

### 链接与资源

Markdown 内部链接使用相对路径和 `.md` 后缀，语言插件会将其解析到当前语言的页面。重命名文件或调整标题时，检查导航、交叉引用和已有锚点；模型指南中的 `choose-task`、`first-run`、`next-steps` 被首页和模型目录引用，应保持稳定。

普通插图优先使用 Markdown 图片语法。共享资源放在 `theme/assets/`，构建后使用站点的 `assets/` 路径。使用原始 HTML 图片或视频标签时，分别检查中英文页面的相对路径。

视频应提供播放控件并按需加载。外部附件和模型资源需要网络访问，站点构建不会验证这些外部资源的可用性。

## 模型目录与主题

[`theme/models.yml`](theme/models.yml) 保存模型分类、说明、标签和源码入口：

- `description_en`、`tags_en`、`source_en` 保存对应的英文内容。
- `page: models/<slug>.md` 表示使用本站指南，需要创建中英文文件并加入导航。
- 没有 `page` 的条目链接到 LightX2V 推理仓库；链接目标为目录时设置 `source_kind: tree`。

界面文案位于 `theme/i18n.yml`，模板位于 `theme/overrides/`，样式与交互脚本位于 `theme/assets/`。`theme/hooks.py` 负责生成模型目录、加入共享资源和补充语言切换逻辑。

界面调整以桌面阅读体验为主，同时保持手机端可用。检查导航、文章目录、模型筛选、深浅色主题和键盘操作；桌面端保留左右侧栏，手机端使用文章标题下的折叠目录。

模型筛选通过 URL 参数 `model` 和 `task` 保存状态，应支持刷新、浏览器返回和语言切换。全局搜索使用独立的 `q` 参数，其索引包含中英文内容。

## 验证

提交前运行 README 中的严格构建和站点检查。检查器会验证站内链接、资源、语言切换、编辑链接与 Markdown 文件的对应关系，以及搜索和 sitemap。

如果本机有对应版本的 LightX2V，可额外检查 GitHub 代码链接所引用的仓库路径：

```bash
python theme/check_site.py site --lightx2v-source ../LightX2V
```

该选项只检查本地文件是否存在，不检查远程网站或执行模型推理。

更换托管路径时，在同一个终端中使用一致的站点地址构建和检查：

```bash
export LIGHTX2V_DOCS_URL=https://docs.example.invalid/LightX2V-Doc/
python -m mkdocs build --strict
python theme/check_site.py site
unset LIGHTX2V_DOCS_URL
```

## 持续集成与发布

[Documentation 工作流](.github/workflows/docs.yml) 在 Pull Request、推送到 `main` 或手动运行时构建并检查网站。构建成功后提供 `lightx2v-docs-preview` 下载包。发布还要求仓库变量 `DOCS_PUBLISH` 为 `true`，且运行来自 `main` 的推送或手动触发；Pull Request 不执行部署。

仓库管理员首次启用 GitHub Pages 时：

1. 在 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。
2. 在 **Settings → Secrets and variables → Actions → Variables** 中设置 `DOCS_PUBLISH=true`。
3. 在 **Actions → Documentation → Run workflow** 中选择 `main` 并运行，检查构建和部署结果。

站点使用组织域名下的 `/LightX2V-Doc/` 路径。在组织主页已配置 `light-ai.top` 的前提下，本仓库保持 **Custom domain 为空**，由项目站点继承该域名。域名配置方式见 [GitHub Pages 文档](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages#using-a-custom-domain-across-multiple-repositories)。

| 配置 | 作用 |
| --- | --- |
| `DOCS_PUBLISH` | GitHub 仓库变量，控制是否执行发布任务 |
| `LIGHTX2V_DOCS_URL` | 构建环境变量，指定包含路径前缀的站点地址；发布时由 Pages 提供 |
| `LIGHTX2V_DOCS_EDIT_URI` | 构建环境变量，指定文档仓库的完整编辑地址；CI 按仓库和分支设置 |

修改默认站点地址或编辑仓库地址时，同步检查 `mkdocs.yml` 和 `theme/check_site.py` 中的默认值。将 `DOCS_PUBLISH` 设为 `false` 会停止后续自动部署，已发布的网站仍会保留。

## 依赖与升级

Python 依赖固定在 `requirements.txt` 中。升级 MkDocs、Material 或语言插件后，除严格构建外，还应手动检查两种语言的导航、搜索、语言切换、缺失翻译提示和文章目录。

`theme/overrides/main.html` 定制了页面元数据，语言对应关系写入 sitemap；`partials/content.html` 定制了手机端目录的位置。升级主题时，对照上游模板检查这些覆盖文件，保留现有的语言链接行为。

KaTeX 的分发文件、字体、许可证和来源信息位于 `theme/assets/vendor/katex/`。更新这些资源时，同步维护 `NOTICE.txt` 中的版本、来源和校验值，并检查公式与字体加载。
