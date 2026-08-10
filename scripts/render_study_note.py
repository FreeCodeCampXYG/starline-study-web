#!/usr/bin/env python3
"""将结构化学习笔记 JSON 安全渲染为响应式单文件 HTML。"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


def esc(value: object) -> str:
    """把任意值转为安全 HTML 文本。"""
    return html.escape(str(value or ""), quote=True)


def safe_id(value: object, fallback: str) -> str:
    """生成可用于页面锚点的稳定 ID。"""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value or "")).strip("-")
    return cleaned or fallback


def safe_url(value: object) -> str:
    """只允许 HTTP(S) 或相对资源路径，阻断脚本协议和本机绝对路径。"""
    raw = str(value or "").strip()
    if not raw or raw.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:[\\/]", raw):
        return ""
    parsed = urlparse(raw)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return ""
    return raw


def list_html(items: object, css_class: str = "") -> str:
    """渲染纯文本列表。"""
    values = items if isinstance(items, list) else []
    cls = f' class="{esc(css_class)}"' if css_class else ""
    return f"<ul{cls}>" + "".join(f"<li>{esc(item)}</li>" for item in values) + "</ul>"


def visual_html(visual: object) -> str:
    """按视觉类型渲染图片、流程、对比或概念关系图。"""
    if not isinstance(visual, dict) or not visual:
        return ""
    kind = str(visual.get("type", "")).lower()
    title = esc(visual.get("title", "知识图示"))
    caption = esc(visual.get("caption", ""))
    alt = esc(visual.get("alt", title))
    items = visual.get("items", []) if isinstance(visual.get("items", []), list) else []
    if kind == "image":
        src = safe_url(visual.get("src", ""))
        if not src:
            return ""
        body = f'<img src="{esc(src)}" alt="{alt}" loading="lazy">'
    elif kind == "process":
        body = '<ol class="process">' + "".join(f"<li><span>{i}</span>{esc(item)}</li>" for i, item in enumerate(items, 1)) + "</ol>"
    elif kind == "comparison":
        body = '<div class="comparison">' + "".join(f'<div class="compare-card">{esc(item)}</div>' for item in items) + "</div>"
    elif kind == "concept-map":
        body = '<div class="concept-map">' + f'<strong>{title}</strong>' + "".join(f"<span>{esc(item)}</span>" for item in items) + "</div>"
    else:
        return ""
    return f'<figure aria-label="{alt}"><div class="figure-title">{title}</div>{body}' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>"


def render(payload: dict[str, object]) -> str:
    """依据内容契约生成完整 HTML。"""
    title = esc(payload.get("title", "学习笔记"))
    subtitle = esc(payload.get("subtitle", ""))
    sections = payload.get("sections", []) if isinstance(payload.get("sections", []), list) else []
    nav = []
    section_blocks = []
    for index, raw in enumerate(sections, 1):
        section = raw if isinstance(raw, dict) else {}
        section_id = safe_id(section.get("id"), f"section-{index}")
        section_title = esc(section.get("title", f"第 {index} 节"))
        nav.append(f'<a href="#{section_id}"><span>{index:02d}</span>{section_title}</a>')
        refs = section.get("source_refs", []) if isinstance(section.get("source_refs", []), list) else []
        refs_html = " ".join(f'<code>[{esc(ref)}]</code>' for ref in refs)
        example = section.get("example", "")
        section_blocks.append(
            f'<section id="{section_id}" class="chapter">'
            f'<div class="chapter-number">{index:02d}</div><div class="chapter-body">'
            f'<h2>{section_title}</h2><p class="conclusion">{esc(section.get("conclusion", ""))}</p>'
            f'<p>{esc(section.get("explanation", ""))}</p>{list_html(section.get("key_points", []), "key-points")}'
            f'{visual_html(section.get("visual"))}'
            + (f'<div class="example"><strong>例子 / 类比</strong><p>{esc(example)}</p></div>' if example else "")
            + (f'<div class="refs"><strong>来源定位</strong> {refs_html}</div>' if refs_html else "")
            + "</div></section>"
        )

    glossary = payload.get("glossary", []) if isinstance(payload.get("glossary", []), list) else []
    glossary_html = "".join(
        f'<div><dt>{esc(item.get("term", ""))}</dt><dd>{esc(item.get("definition", ""))}</dd></div>'
        for item in glossary if isinstance(item, dict)
    )
    sources = payload.get("sources", []) if isinstance(payload.get("sources", []), list) else []
    sources_html = "".join(
        f'<tr><td>{esc(item.get("id", ""))}</td><td>{esc(item.get("title", ""))}</td><td>{esc(item.get("type", ""))}</td><td>{esc(item.get("location", ""))}</td></tr>'
        for item in sources if isinstance(item, dict)
    )
    recall = payload.get("recall_questions", []) if isinstance(payload.get("recall_questions", []), list) else []
    recall_html = "".join(
        f'<label class="check"><input type="checkbox"><span><strong>Q{i}</strong>{esc(question)}</span></label>'
        for i, question in enumerate(recall, 1)
    )
    actions = payload.get("action_items", []) if isinstance(payload.get("action_items", []), list) else []
    action_html = "".join(
        f'<label class="check"><input type="checkbox"><span>{esc(action)}</span></label>' for action in actions
    )
    css = """
:root{--ink:#14213d;--muted:#5f6b7a;--paper:#f7f3ea;--card:#fffdf8;--accent:#e4572e;--accent2:#2a9d8f;--line:#d9d3c7;--shadow:0 18px 50px rgba(20,33,61,.10)}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:radial-gradient(circle at 8% 0%,#fbd8c8 0,transparent 24rem),radial-gradient(circle at 95% 8%,#ccebe5 0,transparent 22rem),var(--paper);font-family:Inter,"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.75}a{color:inherit}.wrap{width:min(1160px,calc(100% - 40px));margin:auto}.hero{padding:76px 0 42px}.eyebrow{font:700 12px/1.2 ui-monospace,monospace;letter-spacing:.18em;text-transform:uppercase;color:var(--accent)}h1{font-size:clamp(42px,8vw,88px);line-height:1.02;max-width:960px;margin:18px 0}.subtitle{font-size:clamp(18px,2vw,25px);max-width:760px;color:var(--muted)}.meta{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}.pill{padding:7px 12px;border:1px solid var(--line);border-radius:99px;background:rgba(255,255,255,.55)}.evidence{margin:30px 0 0;padding:18px 20px;border-left:5px solid var(--accent);background:#fff3eb;border-radius:0 12px 12px 0}.layout{display:grid;grid-template-columns:250px 1fr;gap:36px;align-items:start}.side{position:sticky;top:20px;padding:20px;background:rgba(255,253,248,.86);border:1px solid var(--line);border-radius:18px;backdrop-filter:blur(10px)}.side a{display:flex;gap:10px;padding:10px 4px;text-decoration:none;border-bottom:1px solid #ebe5d9;font-size:14px}.side span{color:var(--accent);font-family:ui-monospace,monospace}.panel,.chapter{background:var(--card);border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow)}.panel{padding:30px;margin-bottom:24px}.takeaways{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;list-style:none;padding:0}.takeaways li{padding:17px;border-radius:14px;background:#eef8f5;border-left:4px solid var(--accent2)}.chapter{display:grid;grid-template-columns:82px 1fr;margin:0 0 28px;overflow:hidden}.chapter-number{padding:30px 18px;background:var(--ink);color:white;font:700 24px ui-monospace,monospace}.chapter-body{padding:30px 34px}.chapter h2{font-size:clamp(26px,4vw,42px);line-height:1.2;margin:0 0 18px}.conclusion{font-size:20px;font-weight:700;border-bottom:1px solid var(--line);padding-bottom:16px}.key-points li::marker{color:var(--accent)}figure{margin:28px 0;padding:24px;background:#f1f6f5;border-radius:18px;overflow:hidden}.figure-title{font-weight:800;margin-bottom:14px}figure img{display:block;width:100%;max-height:540px;object-fit:contain;border-radius:12px}.process{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;padding:0;list-style:none}.process li{position:relative;padding:16px;background:white;border:1px solid #c9ded9;border-radius:12px}.process span{display:block;color:var(--accent);font:700 12px ui-monospace,monospace}.comparison{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.compare-card{padding:18px;background:white;border-top:4px solid var(--accent2);border-radius:12px}.concept-map{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:12px}.concept-map strong{padding:18px;background:var(--ink);color:white;border-radius:50%}.concept-map span{padding:10px 14px;background:white;border:1px solid var(--accent2);border-radius:99px}figcaption{margin-top:12px;color:var(--muted);font-size:13px}.example{padding:18px 20px;background:#fff5d6;border-radius:14px}.example p{margin:4px 0}.refs{margin-top:18px;color:var(--muted)}code{padding:3px 7px;background:#efeae0;border-radius:6px}.checks{display:grid;gap:10px}.check{display:flex;gap:12px;align-items:flex-start;padding:14px;border:1px solid var(--line);border-radius:12px;background:white}.check input{margin-top:7px;accent-color:var(--accent2)}.check strong{display:inline-block;margin-right:9px;color:var(--accent)}dl>div{display:grid;grid-template-columns:180px 1fr;padding:12px 0;border-bottom:1px solid var(--line)}dt{font-weight:800}dd{margin:0;color:var(--muted)}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line);vertical-align:top}footer{padding:40px 0 70px;color:var(--muted)}@media(max-width:800px){.layout{grid-template-columns:1fr}.side{position:static}.chapter{grid-template-columns:1fr}.chapter-number{padding:12px 24px}.takeaways{grid-template-columns:1fr}.wrap{width:min(100% - 24px,1160px)}.hero{padding-top:48px}dl>div{grid-template-columns:1fr}.panel,.chapter-body{padding:22px}}@media print{body{background:white}.side{display:none}.layout{display:block}.panel,.chapter{box-shadow:none;break-inside:avoid}.check input{display:none}}
"""
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body>
<header class="hero"><div class="wrap"><div class="eyebrow">ILLUSTRATED STUDY NOTE</div><h1>{title}</h1><p class="subtitle">{subtitle}</p><div class="meta"><span class="pill">受众：{esc(payload.get("audience", "一般学习者"))}</span><span class="pill">来源：{len(sources)} 项</span><span class="pill">章节：{len(sections)} 节</span></div><div class="evidence"><strong>证据范围</strong><br>{esc(payload.get("evidence_note", "请结合来源表核验。"))}</div></div></header>
<main class="wrap layout"><nav class="side"><div class="eyebrow">CONTENTS</div>{''.join(nav)}<a href="#recall"><span>?</span>主动回忆</a><a href="#sources"><span>§</span>来源</a></nav><div>
<section class="panel"><div class="eyebrow">QUICK GRASP</div><h2>快速掌握</h2><p>{esc(payload.get("overview", ""))}</p>{list_html(payload.get("key_takeaways", []), "takeaways")}</section>
{''.join(section_blocks)}
<section class="panel"><div class="eyebrow">WATCH OUT</div><h2>易错点与争议</h2>{list_html(payload.get("misconceptions", []))}</section>
<section class="panel"><div class="eyebrow">GLOSSARY</div><h2>术语表</h2><dl>{glossary_html}</dl></section>
<section id="recall" class="panel"><div class="eyebrow">ACTIVE RECALL</div><h2>主动回忆</h2><div class="checks">{recall_html}</div></section>
<section class="panel"><div class="eyebrow">NEXT ACTION</div><h2>行动清单</h2><div class="checks">{action_html}</div></section>
<section id="sources" class="panel"><div class="eyebrow">PROVENANCE</div><h2>来源表</h2><div style="overflow:auto"><table><thead><tr><th>ID</th><th>标题</th><th>类型</th><th>位置</th></tr></thead><tbody>{sources_html}</tbody></table></div></section>
</div></main><footer class="wrap">由 Starline Study Web 生成 · 核心结论请回到原始材料核验</footer></body></html>'''


def main() -> None:
    """读取 JSON 并写出 HTML。"""
    parser = argparse.ArgumentParser(description="把学习笔记 JSON 渲染为响应式 HTML。")
    parser.add_argument("input", help="符合内容契约的 JSON 文件")
    parser.add_argument("--output", "-o", required=True, help="输出 HTML 路径")
    args = parser.parse_args()
    source = Path(args.input)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("输入 JSON 顶层必须是对象")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(payload), encoding="utf-8")
    print(f"已生成网页：{output.resolve()}")


if __name__ == "__main__":
    main()
