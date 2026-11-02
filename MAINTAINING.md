# 维护约定

## 内容与来源

本仓库在 2026-11-02 从 LightX2V 的本地文档预览迁入内容，包含当时的文档改进。初始教程来自 `docs/ZH_CN/source/`、`docs/EN/source/`，三组模型指南来自对应的 `scripts/*/README*.md`。迁移后，本仓库的 `docs/` 是新版网站的正文来源，不再在构建时读取推理仓库。

每种语言的 benchmark、cache 包装页与其完整内容合并为一个页面。旧 MyST 锚点转换为显式 HTML 锚点，文档内部链接改为本站路径，引用的仓库图片已复制到 `theme/assets/repository/`。原文中的行内代码和代码块保留；GitHub 附件视频保留远程地址，按需加载并提供原生播放控件。运行命令的正确性仍需要对应推理环境验证。

原 LightX2V 仓库的 Sphinx 文档和 Read the Docs 配置继续保留；它们与本站不自动同步。推理代码发生变化时，请同时更新受影响的新站说明。

内容继承 LightX2V 的许可，见根目录 `LICENSE`。KaTeX 的许可、版本和归档校验信息位于 `theme/assets/vendor/katex/`。

## 页面、语言与链接

- 中文文件使用 `page.md`，英文使用同目录的 `page.en.md`，例如 `docs/models/wan.md` 和 `docs/models/wan.en.md`。
- 导航引用中文文件路径，英文标题写在 `mkdocs.yml` 的 `nav_translations` 中。严格构建会报告遗漏的导航项。
- Markdown 内部链接使用相对路径和 `.md` 后缀；语言插件会让链接保持在当前语言。
- 中文 URL 为根路径下的 `.html`，英文为对应的 `en/` 路径，现有页面地址不因这次拆分而改变。
- 保持模型指南中的 `choose-task`、`first-run`、`next-steps` 锚点，首页和模型目录使用了这些入口。
- 普通插图优先写成 Markdown 图片链接。原文保留的 HTML 图片和视频需要手动确认中英文输出路径；离线检查会检查本站文件和锚点。

语言按钮跳转到同一篇文章。缺少翻译时，按钮明确提供另一个语言的首页入口，回退页面也显示原始语言提示。新页面应同时补齐两种语言。

搜索使用一个共享的中英文索引，包含教程、模型指南和模板生成的模型目录；`jieba` 在构建阶段进行中文分词。

## 模型目录与主题

`theme/models.yml` 保存模型分类、说明、标签和外部源码路径。`page: models/<slug>.md` 表示使用本地指南，必须提供中英文文件并加入导航；没有 `page` 的条目使用推理仓库的外部入口，目录入口显式设置 `source_kind: tree`。英文内容使用 `description_en`、`tags_en`、`source_en`。

筛选状态使用 URL 参数 `model` 和 `task`，支持刷新、返回和切换语言；不占用 Material 全局搜索使用的 `q`。禁用 JavaScript 时仍显示全部模型和普通链接。

电脑端优先保留模型目录三列入口、左侧导航和右侧文章目录。低于 960 CSS 像素时，在标题后增加可折叠文章目录。`partials/content.html` 定制了这个位置，升级 Material 时需要复查。

`theme/hooks.py` 只处理模型目录、共享资源和少量语言展示逻辑。全部文档都是普通 Markdown 文件，不再使用跨仓库虚拟页面。模板复用 Material；框架通过 `requirements.txt` 安装，不存放完整框架源码。

## 验证与升级

严格构建后运行 `theme/check_site.py`。有 `LIGHTX2V_DOCS_EDIT_URI` 时，检查器还会校验每页的编辑链接与本仓库的中英文 Markdown 文件对应。

默认检查不需要推理仓库；如果本机有对应版本的 LightX2V，可额外传入 `--lightx2v-source /path/to/LightX2V`，检查外部 GitHub 代码链接对应的仓库路径是否存在。这不会验证远程网站或模型推理。

升级 `mkdocs-static-i18n` 或 Material 后，需要一起检查两种语言的导航、搜索、语言切换、sitemap 和缺失翻译回退。当前模板省略 HTML head 中的 alternate 链接，避免 Material 9.8 将每个文章地址当作独立站点根目录请求 sitemap；语言对应关系由 sitemap 和页面语言按钮提供。

当前锁定的 Material 9.8.0 提示维护至 2027-05-05。正式迁移前应结合上线时间复查依赖的维护情况；现有 Markdown 内容与样式分开，便于后续升级。
