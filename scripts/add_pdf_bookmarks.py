#!/usr/bin/env python3
"""为重建或压缩后的 PDF 添加可验证的章节书签。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter


def validate_nodes(nodes: Any, page_count: int) -> list[dict[str, Any]]:
    """校验 1 基页码书签树并返回规范化节点。"""
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("书签 JSON 必须是非空数组")
    result: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("title"), str) or not node["title"].strip():
            raise ValueError("每个书签必须包含非空 title")
        page = node.get("page")
        if not isinstance(page, int) or not 1 <= page <= page_count:
            raise ValueError(f"书签页码必须在 1 到 {page_count} 之间")
        children = validate_nodes(node["children"], page_count) if node.get("children") else []
        result.append({"title": node["title"].strip(), "page": page, "children": children})
    return result


def add_bookmarks(source: Path, output: Path, nodes: list[dict[str, Any]]) -> None:
    """复制 PDF 页面和元数据，并写入章节书签树。"""
    source = source.resolve()
    output = output.resolve()
    if source == output:
        raise ValueError("输出文件不能覆盖输入文件")
    reader = PdfReader(source)
    normalized = validate_nodes(nodes, len(reader.pages))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    if reader.metadata:
        writer.add_metadata({key: str(value) for key, value in reader.metadata.items() if value is not None})

    def append(items: list[dict[str, Any]], parent=None) -> None:
        """递归写入书签并保留父子层级。"""
        for item in items:
            bookmark = writer.add_outline_item(item["title"], item["page"] - 1, parent=parent)
            append(item["children"], bookmark)

    append(normalized)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as stream:
        writer.write(stream)


def main() -> None:
    """解析命令行参数并输出带书签 PDF。"""
    parser = argparse.ArgumentParser(description="为压缩或重建 PDF 添加章节书签")
    parser.add_argument("input", type=Path)
    parser.add_argument("bookmarks", type=Path, help="UTF-8 JSON，页码从 1 开始")
    parser.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args()
    nodes = json.loads(args.bookmarks.read_text(encoding="utf-8"))
    add_bookmarks(args.input, args.output, nodes)
    print(f"已生成带书签 PDF：{args.output.resolve()}")


if __name__ == "__main__":
    main()
