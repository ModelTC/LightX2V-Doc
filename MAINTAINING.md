# 维护指南

本文件面向文档和网站维护者。本地环境安装与预览命令见 [中文 README](README_zh.md)。

仓库首页使用英文 `README.md`，中文版本为 `README_zh.md`。修改说明或命令时，请同步更新两份文件。

## 内容维护

`docs/` 是本站的文档来源。LightX2V 推理仓库中的文档和模型 README 不会自动同步到本站；推理接口、配置或模型能力发生变化时，需要更新相关教程。

直接修改 `docs/` 下的 Markdown 文件，确保文档中的命令、参数和模型能力与 LightX2V 对应实现一致。

### 页面与语言

- 中文文件使用 `page.md`，英文使用同目录下的 `page.en.md`。
- 导航引用中文文件路径，英文导航标题配置在 `mkdocs.yml` 的 `nav_translations` 中。严格构建会报告未加入导航的页面。
- 中文页面位于站点根路径下，英文页面位于 `en/` 下，均使用 `.html` 地址。例如 `models/wan.html` 与 `en/models/wan.html`。
- 新增或修改页面时同步维护两种语言。缺少翻译时，站点会显示回退提示，语言按钮会提供相应语言的首页入口。

例如，Wan2.2 指南对应 [`docs/models/wan22.md`](docs/models/wan22.md) 和 [`docs/models/wan22.en.md`](docs/models/wan22.en.md)。新增页面时，同时更新 `mkdocs.yml` 中的导航和英文标题。

快速入门内容统一放在 `docs/getting_started/`：`index.md` 以“准备环境与模型 → 启动服务 → 发送请求并获取结果”为推荐路径；`installation.md` 是完整安装指南，`offline_inference.md` 和 `python_api.md` 分别介绍离线命令行与进程内 Pipeline，权重组织页明确以 Wan 为范围，性能基准保留为历史参考。英文文件使用相同文件名加 `.en.md` 后缀。

完整安装指南的三种方式通过 `lx-method-links` 直达对应章节，详细步骤保留在同一页面，便于链接与搜索。服务 API 参考仍保留 `docs/deploy_guides/deploy_service.md` 的网址，导航入口放在“快速入门”；它负责请求参数、任务状态和队列。`docs/deploy_guides/index.md` 是部署总览，按接入方式和运行需求连接已有指南；新增部署入口时同步维护英文版本与导航。

部署入口统一维护在 `docs/deploy_guides/interfaces.md`：Gradio 与 ComfyUI 的旧网址通过 redirects 跳转到该页，修改时保留旧锚点。Windows 当前源码流程位于 `deploy_local_windows.md`，旧整合包说明仅从该页末尾链接进入。Wan2.1 历史性能保留首页示例等正文链接。这两个参考页面保留原网址，通过 `mkdocs.yml` 的 `not_in_nav` 声明不加入导航；其他页面仍需通过导航完整性检查。

优化教程先给模型适用范围与可执行流程，再放原理和历史数据。修改缓存、并行或注意力设置时，对照推理仓库的 runner、后端注册、完整配置和启动脚本；不能把某个模型的能力写成所有模型均支持。TensorRT 页目前只介绍已有引擎接入，补齐可验证的导出或下载流程后再扩展为完整教程。

### 链接与资源

Markdown 内部链接使用相对路径和 `.md` 后缀，语言插件会将其解析到当前语言的页面。重命名文件或调整标题时，检查导航、交叉引用和已有锚点；模型指南中的 `choose-task`、`first-run`、`next-steps` 被首页和模型目录引用，应保持稳定。

已发布页面改名时，在 `mkdocs.yml` 的 `extra.redirects` 中登记旧 `.html` 地址到新 `.md` 文件的映射，并更新站内引用。构建钩子会为中英文生成跳转页；启用 JavaScript 时会保留查询参数和锚点，禁用时仍可跳转到新页面。跳转页不进入导航、搜索或 sitemap，无需在 `docs/` 中保留旧文件。

首次生成统一维护在 `docs/getting_started/index.md` 及英文版本；`first_generation.html` 通过跳转保留旧地址。入门配置使用 SDPA 与 CPU 卸载，首页服务启动与离线示例复用该配置；变更时同步检查推理仓库的参数与实现。

入门视频请求客户端使用 HTTP 提交任务、轮询 `status` 并流式下载完成的结果；提交响应的字段为 `task_status`。检查成功、失败、取消、等待超时和 HTTP 错误，确保超时不会被误写成任务已取消；GPU 真实推理需单独验证。

普通插图优先使用 Markdown 图片语法。共享资源放在 `theme/assets/`，构建后使用站点的 `assets/` 路径。使用原始 HTML 图片或视频标签时，分别检查中英文页面的相对路径。

页头使用一体式透明标识 `theme/assets/lightx2v-logo.svg`，沿用原图中圆润、直立的字标和图文比例，去掉底部小字。SVG 内嵌优化后的透明位图，无需加载字体；`#dark` 仅调亮字标，`#mark` 供手机菜单单独显示图标。`partials/logo.html` 与 CSS 控制显示尺寸。独立透明图标 `lightx2v-mark.png` 同时用作浏览器标签页图标（favicon）。

视频应提供播放控件并按需加载。外部附件和模型资源需要网络访问，站点构建不会验证这些外部资源的可用性。

## 模型目录与主题

[`theme/models.yml`](theme/models.yml) 保存模型分类、说明、标签和源码入口：

- `description_en`、`tags_en`、`source_en` 保存对应的英文内容。
- `page: models/<slug>.md` 表示使用本站指南，需要创建中英文文件并加入导航。
- 没有 `page` 的条目链接到 LightX2V 推理仓库；链接目标为目录时设置 `source_kind: tree`。

界面文案位于 `theme/i18n.yml`，模板位于 `theme/overrides/`，样式与交互脚本位于 `theme/assets/`。`theme/hooks.py` 负责生成模型目录、加入共享资源和补充语言切换逻辑。

构建时，自定义样式、脚本和品牌图片会生成带内容哈希的文件名，并自动更新页面引用，避免发布后加载旧缓存。维护时仍使用原文件名，无需手动改版本号；构建检查会验证资源引用和哈希。

外观菜单提供跟随系统、浅色、深色三种选择，首次访问默认跟随系统，之后保留用户选择。`partials/palette.html` 定制菜单，主题保存和系统变化仍由 Material 处理；`partials/javascripts/palette.html` 在正文显示前应用偏好，并将旧版双模式记录映射到新选项。修改时检查刷新、语言切换、系统主题变化和键盘操作。

中英文首页共用 `theme/overrides/partials/hero-visual.html` 中的 SVG 插画，由构建钩子替换首页的 `<!-- hero-visual -->` 标记。插画与主题颜色联动，不需要额外图片依赖。

首页沿用 `lx-examples` 的三种运行方式标签页：服务与请求、命令行、Python，默认选中服务与请求。桌面端标签在左侧，手机端放在代码上方；服务标签中依次展示两个终端的命令。首页与快速入门统一使用 API 端口 8080、指标端口 8081；模型专用脚本沿用其默认 8000 端口，文中明确区别。修改时检查中英文代码一致、复制按钮、Docker 端口映射和第二个终端的环境。提示框的图标与侧边线保留语义颜色，标题背景使用统一的浅灰或深色表面。

首页生成示例使用性能基准中的 Wan2.1 I2V 视频（`LightX2V_1`），原视频地址为 `https://github.com/user-attachments/assets/7bffe48f-e433-430b-91dc-ac745908ba3a`。本地封面 `theme/assets/showcase/wan-i2v.webp` 取自该视频第 1 秒，视频本体留在外部，使用 `preload="none"`、本地封面按钮和来源链接，点击后才加载并显示原生播放器；无 JavaScript 时直接显示原生控件，加载失败时提供原视频链接。首页示例不代表快速入门的 T2V 输出；更换视频时同步更新封面、模型与来源。

首页模型入口同时说明任务用途与代表模型，并通过分类参数进入模型总览。页尾并排展示近期更新与资源反馈入口，窄屏改为纵向排列；修改标题时保留已有锚点。模型总览优先展示搜索和任务筛选，使用指南与 GitHub 示例的区别在结果列表前说明。

界面调整以桌面阅读体验为主，同时保持手机端可用。检查导航、文章目录、模型筛选、深浅色主题和键盘操作；桌面端保留左右侧栏，手机端使用文章标题下的折叠目录。

正文页限制阅读宽度，以细分隔线区分二级章节；模型总览保留宽布局。安装、Wan2.2 和服务部署页的 `lx-guide-path` 是链接到章节的步骤导读，修改时同步维护中英文锚点。代码块可通过 `title` 标明用途或执行终端，不要将说明混入可复制的命令。

锚点跳转使用 Material 提供的 `scroll-margin-top` 避让固定页头，不再叠加全局 `scroll-padding-top`，避免跳转位置与右侧目录高亮不一致。

目录展示到三级标题；四级及更深的步骤标题仍保留正文锚点，避免长教程的右侧目录过于拥挤。

标题图标按内容含义选择，目前在完整安装指南与部署总览试用。使用主题已有的 Material SVG，配合 `lx-heading-icon` 和 `aria-hidden="true"`；标题设置 `lx-icon-heading`、原有锚点 ID 和纯文字 `data-toc-label`，让电脑和手机目录保持简洁。普通标题无需统一加图标，提示与警告优先使用带语义图标的原生提示框。

前后篇链接由 `partials/page-navigation.html` 渲染在正文末尾，遵循 `navigation.footer` 和页面的 `hide: [footer]` 配置；`partials/footer.html` 仅保留版权和社区链接。升级主题时检查这两个覆盖模板。

模型筛选通过 URL 参数 `model` 和 `task` 保存状态，应支持刷新、浏览器返回和语言切换。全局搜索使用独立的 `q` 参数，其索引包含中英文内容。

`catalog.js` 仅在模型目录页加载，`reading.js` 提供全站交互；`main.html` 负责按页面内容加载专用脚本。

全站搜索保留 Material 的搜索引擎。`partials/search.html` 提供搜索入口与弹层；`reading.js` 补充 Ctrl/⌘ K 快捷键，以及结果的文档位置和语言标记。桌面端使用胶囊入口和居中弹层，手机端沿用全屏搜索。升级主题时核对 `data-md-component`，并检查 `/`、Ctrl/⌘ K 打开、方向键选择、Enter 跳转、清空、Esc 关闭及触屏操作。

搜索配置使用 `pipeline: []` 保留技术术语原词，避免英文词干处理导致 `cache` 等前缀查询漏搜；中英文分词与结果排序仍由主题处理。

构建钩子按 `search.lang` 保留搜索语言模块及其依赖，省去主题附带的其他语言资源。升级主题时核对搜索 worker 的语言加载逻辑，并验证中英文查询、更多匹配和滚动加载。

模型目录从 `models.yml` 的中英文名称、描述和标签生成同一份搜索文本。分类按钮的数量表示当前关键词在各分类中的匹配数；空结果页可以清除分类而保留关键词。首页任务入口使用 `?task=<分类>#model-catalog` 直达筛选结果，无 JavaScript 时仍可浏览完整模型列表。

`docs/method_tutorials/index.md` 及其英文版本是加速优化的总览入口。调整优化方法或适用条件时，同步更新总览中的目标入口和对照表。

## 验证

提交 Pull Request 前，在仓库根目录使用已安装文档依赖的 Python 环境执行严格构建和站点检查：

```bash
python -m mkdocs build --strict
python theme/check_site.py site
```

生成的网站位于 `site/`，该目录已加入 Git 忽略规则。检查器会验证站内链接与锚点、资源、语言切换、旧地址跳转、Markdown 源文件、编辑链接（若启用）与源文件的对应关系，以及搜索索引和 sitemap。外部网站可访问性及模型推理需要单独验证。

涉及页面样式或交互时，还需手动检查电脑和手机尺寸下的显示效果与操作。

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

KaTeX 的分发文件、字体、许可证和来源信息位于 `theme/assets/vendor/katex/`。字体仅保留 WOFF2，CSS 的 `@font-face` 同步去掉 WOFF/TTF 回退项，其余样式保持上游原样。更新时沿用此规则，同步维护 `NOTICE.txt` 中的版本、来源和校验值，并检查公式与字体加载。

`main.html` 根据正文中 Arithmatex 生成的公式标记加载 KaTeX 样式与脚本；无公式的页面不加载这些资源。升级 Markdown 扩展或主题后，检查普通页面的资源请求与中英文公式页的渲染。
