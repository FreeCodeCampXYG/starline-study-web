# Starline Study Web

作者：**墨点星痕**｜英文名：**starline**

把客户提供的 TXT、PDF、PPT/PPTX、公开视频链接或它们的组合，整理成一份按用户任务进入、有来源定位、主动回忆、复述练习、间隔复习和行动清单的单文件 HTML 学习笔记。第一步先写体验简报，确定用户、场景、10 秒成功、唯一主行动和移动端首屏，再提炼内容与生成页面；需要压缩 PDF 时同步保留或重建章节书签。

## 你可以直接这样说

- “把这份 PPT 和 TXT 整理成图文并茂的网页学习笔记。”
- “分析这个课程视频链接，做成适合新人复习的 HTML 专题页。”
- “综合这三个资料，保留页码和时间戳，生成学习笔记网页。”
- “这段公开视频没有字幕也没关系，先告诉我能可靠提取到什么，不要脑补。”

## 输入与输出

支持本地 `.txt`、`.pdf`、`.pptx`，以及代理环境能够只读访问的公开视频页面。旧 `.ppt` 需先转为 `.pptx` 或提供 LibreOffice。单个本地文档默认在源文件同级交付一个可独立打开的 HTML；辅助目录可包含：

- `source-packet.json`：按行、幻灯片或字幕段保存的来源材料；
- `note.json`：结构化学习笔记与视觉计划；
- `index.html`：任务导向、响应式、可打印的网页工作稿；
- `assets/`：经授权复用或生成的图片素材。
- 压缩 PDF（如请求）：页数、章节书签标题与目标页均需验证。

## 安装

发布后可直接安装：

```bash
npx skills add FreeCodeCampXYG/starline-study-web --skill starline-study-web
```

### 前置条件

- [ ] 已安装支持 Agent Skills 的客户端或编码代理；
- [ ] 本机具有 Python 3.10 或更高版本；
- [ ] TXT、PPTX 和视频链接均由用户授权访问；
- [ ] 旧版 `.ppt` 已转换为 `.pptx`，或本机具备 LibreOffice；
- [ ] 安装前已审查 Skill 的脚本、网络访问与输出目录权限。

## 设计边界

- 不下载付费、受 DRM 保护或无权访问的视频。
- 无字幕时不根据标题编造视频内容。
- 不把来源不明图片塞进网页；优先使用 PPT 自带图、HTML/CSS 图示或许可清晰素材。
- 不自动部署、上传或公开客户资料。
- “图文并茂”意味着图片承担解释任务，不意味着每屏强塞装饰图。

## UX 从第一步开始

Skill 不再等首版生成后才考虑体验。开始整理前先产出 `experience-brief.md`，从“开始学习、继续上次、搜索定位、理解重点、回到证据”中选择一个首要任务，定义首屏、主行动、信息密度、渐进披露和移动端目标。对于实质设计任务，联网可用时在这一阶段核对当前 Apple 官方设计指南、Kimi 官方公开界面和可信设计 Skill/开源先例；只吸收清晰、内容优先、安静工作区和熟悉控件等原则，不复刻品牌外观。首版生成后只做对照简报的回归修正。

## 默认学习闭环

页面不以“读到页尾”为完成标准。默认路径是：`2 分钟抓核心 → 按需深读 → 合上页面主动回忆 → 向具体对象复述 → 完成一个真实动作 → 安排下次复习`。参考答案默认折叠；复述草稿与复习状态只保存在本地浏览器，并允许清除。二八法则只用于安排阅读优先级，不宣称等同于掌握。真人长期保持效果仍是 `missing evidence`。

## 设计先例

主要网页流水线先例为 [AwesomeWebpageMetaSkill](https://github.com/opensquilla/opensquilla/tree/main/src/opensquilla/skills/bundled/AwesomeWebpageMetaSkill)。其他已审阅的多模态解析、学习设计和行动学习先例，以及具体取舍，记录在 `reports/prior-art-research.md`。

## 本地验证

在 `starline-study-web` 根目录运行。默认按当前用户主目录查找元 Skill；若安装在其他位置，通过 `STARLINE_META_SKILL_ROOT` 显式覆盖：

```powershell
$studySkillRoot = (Resolve-Path .).Path
$metaSkillRoot = if ($env:STARLINE_META_SKILL_ROOT) {
    (Resolve-Path $env:STARLINE_META_SKILL_ROOT).Path
} else {
    Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex/skills/starline-meta-skill'
}

python (Join-Path $metaSkillRoot 'scripts/validate_skill.py') $studySkillRoot
python (Join-Path $metaSkillRoot 'scripts/trigger_eval.py') $studySkillRoot `
    --cases (Join-Path $studySkillRoot 'evals/trigger_cases.json') `
    --output (Join-Path $studySkillRoot 'reports/trigger-eval.json')
python -m unittest discover -s tests -v
```

Skill 自身脚本和交付产物统一使用相对路径。`source-packet.json` 只记录输入文件名，以及相对于交付目录的资源路径，不写入客户或开发者的用户主目录。

## Troubleshooting

- `.ppt` 无法读取：另存为 `.pptx`，或安装 LibreOffice 后转换。
- 视频只得到标题和简介：提供字幕、讲稿或本地视频；现有信息只能生成有限摘要。
- 中文 TXT 乱码：转为 UTF-8；提取脚本会依次尝试 UTF-8、GB18030 和 UTF-16。
- 图片不显示：检查 `note.json` 中路径是否相对 `index.html`，并确认文件位于交付目录内。

## 许可证

MIT License，Copyright (c) Starline。详见 `LICENSE`。
