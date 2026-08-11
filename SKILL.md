---
name: starline-study-web
description: |
  Analyze learning sources supplied as TXT, PDF, PPT/PPTX, or public video links, synthesize source-grounded tagged study notes, and create a responsive illustrated HTML learning webpage with page-level location. Use for 图文学习笔记, PDF/PPT课程整理, 网页笔记, 学习专题页, illustrated study notes, or a searchable study-note website. Do not use for ordinary webpage design without source analysis, verbatim transcription only, slide creation, video production, or unsupported claims about inaccessible media.
metadata:
  author: Starline
  version: "1.1.0"
---

# Starline Study Web

把 TXT、PDF、PPT/PPTX 和公开视频链接转成可追溯、带定位标签、可直接打开的学习笔记网页。

## Router Rules

- 只有当目标同时包含“分析学习材料”和“生成网页学习笔记”时启用。
- 输入可以是单一来源或混合来源；多个来源先分别提取，再跨来源综合。
- `.pptx` 可用内置脚本提取；旧版 `.ppt` 需要 LibreOffice 或用户先转为 `.pptx`，不可把二进制内容当文本猜测。
- `.pdf` 先提取逐页文本与页码；图片型页面导出主图并标记 `needs_visual_review`，必须经过 OCR 或视觉核验，不得把空文本页当作空白页。
- 视频链接必须是用户有权访问的公开内容。优先字幕/讲稿，其次页面元数据与描述；拿不到正文时必须说明证据不足，不得根据标题编造视频观点。
- 不为普通企业官网、落地页、PPT 制作、纯转录、纯摘要或视频下载任务触发。

## Compact Workflow

1. 明确受众、输出语言、网页标题、深度和保存位置；用户未指定时，沿用来源语言，面向一般学习者。单个本地文档默认把正式成品放在源文件同级目录；多个来源才建立独立交付目录。
2. 建立输入清单，记录每个来源的类型、可访问性、更新时间或页码/时间戳能力。只在缺少输入本身或关键访问权限时暂停。
3. 对本地 TXT/PPTX/PDF 运行 `scripts/extract_local_sources.py`。PDF 图片页按 [PDF分析与定位规则](references/pdf-analysis.md) 处理；阅读 source packet，并按 [输入分析规则](references/input-analysis.md) 处理视频链接与失败降级。生成数据只能记录文件名或相对于交付目录的 POSIX 路径，不得写入用户主目录或其他绝对路径。
4. 先逐来源提炼，再跨来源综合。为每个重要结论保留 `[Sx:定位]`；区分来源事实、合理推断和学习建议。冲突并列呈现，不强行融合。
5. 按学习目标组织内容：快速摘要、知识结构、核心章节、例子/类比、易错点、术语、主动回忆题和行动清单。为长文档建立书级、章节级、页级三级标签，并标记 `核心20%`、`支撑80%`、`行动项`、`案例`、`待验证`。遵循 [内容与视觉契约](references/content-contract.md) 和 [交互与体验契约](references/visual-ux-contract.md)。
6. 为每个核心章节选择有教学作用的视觉：优先复用 PPT 中相关图、制作安全的 HTML/CSS 流程图/对比图/概念图，其次使用许可清晰且带来源的图片。装饰图不得替代解释。
7. 写出符合 `references/note-schema.example.json` 的 UTF-8 JSON，运行 `scripts/render_study_note.py` 生成 `index.html`。不得把未转义的来源 HTML 直接写进页面。
8. 校验网页：文件存在、无 `javascript:` URL、图片路径可读、导航与移动端布局可用、所有关键结论有来源定位、无证据限制清楚可见。必要时修复后再交付。

## Decision Points

- TXT 编码不明确：按脚本检测结果继续，并在报告中记录；全部失败则要求用户提供 UTF-8 文本。
- PPTX 只有图片无可提取文字：可分析用户授权的幻灯片视觉，但必须标注 OCR/视觉识别来源；不能访问视觉工具时报告缺失证据。
- PDF 只有图片无文字层：导出逐页主图，逐页保留 `page N` 定位并做视觉识别；不确定文字标记 `待验证`，禁止默默猜测。
- 视频无字幕：可使用页面描述做“有限摘要”，明确不是视频完整内容；若用户要求完整笔记，停止并请求字幕或本地文件。
- 来源过长：分块提取后先做分块摘要，再合并；保留块与页码/时间戳映射。
- 来源冲突：建立“不同来源的说法”区块，列明各自证据，不替用户裁决。
- 找不到合适图片：使用结构化 HTML/CSS 图示或明确的占位说明，不抓取来源不明素材。

## Gate Ladder

1. 输入 gate：至少一个来源真实可读，且记录无法访问的来源。
2. 证据 gate：核心结论可回溯到文件行段、幻灯片页或视频时间戳/字幕段。
3. 学习 gate：网页不只是摘要，还包含结构、重点、主动回忆和下一步。
4. 视觉 gate：视觉与相邻知识点直接相关，具备 alt 文本和必要图注。
5. 页面 gate：本地打开不报错，响应式布局可读，脚本不依赖秘密或远程执行。

## Output Contract

- 默认正式交付一个可独立打开的单文件 HTML，名称与源文档对应并放在源文件同级目录。JSON、assets 和 source packet 属于可复现的工作产物，可放入同级辅助目录，但不能要求用户依赖它们才能打开正式网页。
- 首页必须包含标题、来源范围、证据限制、3–7 条关键收获和章节导航。
- 长文档页面必须提供搜索、标签筛选、页码跳转和原页预览；任一摘要或批注都能回到对应页。
- 每个核心章节包含：一句结论、解释、关键点、视觉或明确的无图理由、来源引用。
- 页面末尾包含术语表、主动回忆题、行动清单和来源表。
- 来源引用格式为 `[S1:slide 4]`、`[S2:lines 20-35]` 或 `[S3:12:30-14:05]`；无法精确定位时用 `[S3:description]` 并标为有限证据。
- 不嵌入 API key、Cookie、私有下载地址或受保护媒体；不自动发布、部署或上传。
- `source-packet.json`、`note.json` 和 HTML 不得包含 `C:\Users\<name>`、`/Users/<name>`、`/home/<name>` 等用户专属绝对路径；本地资源使用相对于交付目录的 `/` 分隔路径。

### Single-file delivery

- 对单个 PDF/PPT/TXT 的普通网页笔记请求，单文件 HTML 是默认成品，不需要用户额外强调“单文件”。
- 当用户需要上传飞书、邮件发送或脱离资源目录分发时，运行 `scripts/pack_standalone_html.py`，把页面引用的本地图片、二维码、音频和视频转换为 Data URI。
- 命令：`python scripts/pack_standalone_html.py index.html --output study-note-standalone.html`。
- 若平台提示文件过大，使用：`python scripts/pack_standalone_html.py index.html --output study-note-lite.html --exclude-video`。轻量版保留视频封面和课程摘要，但不包含 MP4 数据。
- 单文件版必须保留外部资料链接为普通 HTTPS 链接，不得内嵌登录凭证、Cookie、私有下载地址或受保护媒体。
- 交付前检查输出文件能够独立打开，并报告文件大小。若平台上传大小受限，优先再交付一个不内嵌视频的轻量版，而不是静默删减内容。

## Verification

```powershell
python scripts/extract_local_sources.py material.txt deck.pptx handbook.pdf --output source-packet.json --asset-dir assets
python scripts/render_study_note.py note.json --output index.html
python scripts/pack_standalone_html.py index.html --output study-note-standalone.html
python scripts/pack_standalone_html.py index.html --output study-note-lite.html --exclude-video
python -m unittest discover -s tests -v
```

以上命令默认从 `starline-study-web` 根目录运行。若由其他目录调用，先解析 Skill 根目录或传入明确路径；不得复制开发者机器上的绝对路径。

缺少网页截图、真实视频字幕 provider 运行或学习者人工评审时，明确写 `missing evidence`，不得宣称理解效果已提升。
