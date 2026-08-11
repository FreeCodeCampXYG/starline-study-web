#!/usr/bin/env python3
"""提取 TXT、PPTX 和 PDF 为带定位信息的 source packet。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "utf-16")


def portable_resource_path(path: Path, base_dir: Path) -> str:
    """返回相对交付目录的资源路径，目录外资源仅保留文件名。"""
    resolved = path.resolve()
    try:
        return resolved.relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return path.name


def read_text(path: Path) -> tuple[str, str]:
    """按常见中文文本编码读取文件，并返回文本与实际编码。"""
    errors: list[str] = []
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeError as exc:
            errors.append(f"{encoding}: {exc}")
    raise ValueError(f"无法识别文本编码：{path}；尝试结果：{' | '.join(errors)}")


def chunk_lines(text: str, max_chars: int = 4000) -> list[dict[str, str]]:
    """按行合并为稳定分块，同时保留原始行号范围。"""
    lines = text.splitlines()
    segments: list[dict[str, str]] = []
    current: list[str] = []
    start = 1

    def flush(end: int) -> None:
        nonlocal current, start
        body = "\n".join(current).strip()
        if body:
            segments.append({"locator": f"lines {start}-{end}", "text": body})
        current = []

    for number, line in enumerate(lines, 1):
        projected = sum(len(item) + 1 for item in current) + len(line)
        if current and projected > max_chars:
            flush(number - 1)
            start = number
        current.append(line)
    if current:
        flush(len(lines))
    return segments


def extract_txt(path: Path, source_id: str) -> dict[str, object]:
    """提取 TXT 文本和行号定位。"""
    text, encoding = read_text(path)
    return {
        "id": source_id,
        "type": "txt",
        "title": path.stem,
        "path": path.name,
        "encoding": encoding,
        "segments": chunk_lines(text),
        "assets": [],
    }


def slide_number(name: str) -> int:
    """从 PPTX 内部 slide 文件名提取页码。"""
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def extract_pptx(
    path: Path,
    source_id: str,
    asset_dir: Path | None,
    packet_dir: Path | None = None,
) -> dict[str, object]:
    """从 PPTX 提取逐页文字，并可导出媒体资源。"""
    if not zipfile.is_zipfile(path):
        raise ValueError(f"文件不是有效 PPTX：{path}")
    segments: list[dict[str, str]] = []
    assets: list[str] = []
    with zipfile.ZipFile(path) as archive:
        slides = sorted(
            (name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
            key=slide_number,
        )
        for name in slides:
            root = ElementTree.fromstring(archive.read(name))
            texts = [node.text.strip() for node in root.iter() if node.tag.endswith("}t") and node.text and node.text.strip()]
            segments.append({"locator": f"slide {slide_number(name)}", "text": "\n".join(texts)})
        if asset_dir:
            asset_dir.mkdir(parents=True, exist_ok=True)
            for name in archive.namelist():
                if not name.startswith("ppt/media/") or name.endswith("/"):
                    continue
                original = Path(name).name
                target = asset_dir / f"{source_id.lower()}-{original}"
                with archive.open(name) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
                assets.append(portable_resource_path(target, packet_dir or target.parent))
    return {
        "id": source_id,
        "type": "pptx",
        "title": path.stem,
        "path": path.name,
        "segments": segments,
        "assets": assets,
    }


def extract_pdf(
    path: Path,
    source_id: str,
    asset_dir: Path | None,
    packet_dir: Path | None = None,
) -> dict[str, object]:
    """提取 PDF 逐页文字；图片型页面可同时导出整页主图供视觉识别。"""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("提取 PDF 需要安装 pypdf：python -m pip install pypdf") from exc

    reader = PdfReader(path)
    renderer = None
    render_module = None
    if asset_dir:
        try:
            import pymupdf
            render_module = pymupdf
            renderer = pymupdf.open(path)
        except ImportError:
            renderer = None
    segments: list[dict[str, object]] = []
    assets: list[str] = []
    for page_number, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        page_asset = ""
        if asset_dir and renderer is not None:
            target = asset_dir / f"{source_id.lower()}-page-{page_number:03d}.jpg"
            target.parent.mkdir(parents=True, exist_ok=True)
            rendered_page = renderer[page_number - 1]
            pixmap = rendered_page.get_pixmap(matrix=render_module.Matrix(1.5, 1.5), alpha=False)
            pixmap.save(target)
            page_asset = portable_resource_path(target, packet_dir or target.parent)
            assets.append(page_asset)
        segments.append({
            "locator": f"page {page_number}",
            "text": text,
            "page_asset": page_asset,
            "needs_visual_review": not bool(text),
        })
    return {
        "id": source_id,
        "type": "pdf",
        "title": path.stem,
        "path": path.name,
        "page_count": len(reader.pages),
        "segments": segments,
        "assets": assets,
        "visual_rendering": "full_page" if renderer is not None else "unavailable",
    }


def main() -> None:
    """解析命令行参数并输出 source packet JSON。"""
    parser = argparse.ArgumentParser(description="提取 TXT/PPTX/PDF 内容并保留行号或页码。")
    parser.add_argument("inputs", nargs="+", help="一个或多个 .txt/.pptx/.pdf 文件")
    parser.add_argument("--output", "-o", required=True, help="输出 JSON 路径")
    parser.add_argument("--asset-dir", help="可选：导出 PPTX 内媒体的目录")
    args = parser.parse_args()

    output = Path(args.output)
    packet_dir = output.parent.resolve()
    sources: list[dict[str, object]] = []
    asset_dir = Path(args.asset_dir).resolve() if args.asset_dir else None
    for index, raw in enumerate(args.inputs, 1):
        path = Path(raw)
        if not path.is_file():
            raise SystemExit(f"输入文件不存在：{path}")
        source_id = f"S{index}"
        suffix = path.suffix.lower()
        if suffix == ".txt":
            sources.append(extract_txt(path, source_id))
        elif suffix == ".pptx":
            sources.append(extract_pptx(path, source_id, asset_dir, packet_dir))
        elif suffix == ".pdf":
            sources.append(extract_pdf(path, source_id, asset_dir, packet_dir))
        elif suffix == ".ppt":
            raise SystemExit(f"不支持旧版 .ppt：{path}；请先转换为 .pptx")
        else:
            raise SystemExit(f"不支持的输入类型：{path.suffix}（仅支持 .txt/.pptx/.pdf）")

    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": "1.0", "sources": sources}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已提取 {len(sources)} 个来源：{output.resolve()}")


if __name__ == "__main__":
    main()
