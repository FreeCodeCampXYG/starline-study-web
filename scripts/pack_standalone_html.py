#!/usr/bin/env python3
"""将学习网页引用的本地资源内嵌为 Data URI，生成可独立分发的 HTML。"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ATTRIBUTE_RE = re.compile(
    r"(?P<prefix>\b(?:src|poster)\s*=\s*)(?P<quote>['\"])(?P<url>.*?)(?P=quote)",
    re.IGNORECASE,
)
HREF_RE = re.compile(
    r"(?P<prefix>\bhref\s*=\s*)(?P<quote>['\"])(?P<url>.*?)(?P=quote)",
    re.IGNORECASE,
)
CSS_URL_RE = re.compile(
    r"(?P<prefix>url\(\s*)(?P<quote>['\"]?)(?P<url>.*?)(?P=quote)(?P<suffix>\s*\))",
    re.IGNORECASE,
)
VIDEO_RE = re.compile(r"<video\b(?P<attrs>[^>]*)>.*?</video>", re.IGNORECASE | re.DOTALL)
POSTER_RE = re.compile(r"\bposter\s*=\s*(?P<quote>['\"])(?P<url>.*?)(?P=quote)", re.IGNORECASE)
SKIP_SCHEMES = {"http", "https", "data", "mailto", "tel", "javascript"}


def local_path(url: str, base_dir: Path) -> Path | None:
    """把可内嵌的本地 URL 解析为文件路径，外部链接和锚点返回 None。"""
    candidate = url.strip()
    if not candidate or candidate.startswith(("#", "//")):
        return None
    parsed = urlsplit(candidate)
    if parsed.scheme.lower() in SKIP_SCHEMES or parsed.netloc:
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    path = Path(raw_path)
    if not path.is_absolute():
        path = base_dir / path
    path = path.resolve()
    return path if path.is_file() else None


def to_data_uri(path: Path) -> str:
    """读取本地文件并转换为带 MIME 类型的 Base64 Data URI。"""
    mime, _ = mimetypes.guess_type(path.name)
    mime = mime or "application/octet-stream"
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def pack_html(source: Path, output: Path, exclude_video: bool = False) -> tuple[int, int, int]:
    """内嵌 HTML 展示所需资源，返回资源数量与原始资源总字节数。"""
    html = source.read_text(encoding="utf-8")
    base_dir = source.parent.resolve()
    cache: dict[Path, str] = {}
    neutralized_links = 0

    if exclude_video:
        def replace_video(match: re.Match[str]) -> str:
            """用静态封面替代视频，避免轻量版产生不可播放的空控件。"""
            poster_match = POSTER_RE.search(match.group("attrs"))
            poster = poster_match.group("url") if poster_match else ""
            image = (
                f'<img src="{poster}" alt="视频演示静态预览" '
                'style="display:block;width:100%;border-radius:16px">'
                if poster else ""
            )
            return (
                '<figure style="margin:0">'
                f'{image}<figcaption style="margin-top:.65rem;color:#667085">'
                '飞书轻量版未内嵌视频；这里保留演示封面与课程摘要。'
                '</figcaption></figure>'
            )

        html = VIDEO_RE.sub(replace_video, html)

    def embed(url: str) -> str:
        path = local_path(url, base_dir)
        if path is None:
            return url
        if path not in cache:
            cache[path] = to_data_uri(path)
        return cache[path]

    def replace_attribute(match: re.Match[str]) -> str:
        embedded = embed(match.group("url"))
        return f'{match.group("prefix")}{match.group("quote")}{embedded}{match.group("quote")}'

    def replace_css_url(match: re.Match[str]) -> str:
        embedded = embed(match.group("url"))
        return (
            f'{match.group("prefix")}{match.group("quote")}'
            f'{embedded}{match.group("quote")}{match.group("suffix")}'
        )

    def replace_local_href(match: re.Match[str]) -> str:
        """移除上传后必然失效的本地附件链接，保留外部链接与页内锚点。"""
        nonlocal neutralized_links
        url = match.group("url").strip()
        parsed = urlsplit(url)
        if url.startswith(("#", "//")) or parsed.scheme.lower() in SKIP_SCHEMES:
            return match.group(0)
        neutralized_links += 1
        return f'{match.group("prefix")}{match.group("quote")}#sources{match.group("quote")}'

    html = ATTRIBUTE_RE.sub(replace_attribute, html)
    html = CSS_URL_RE.sub(replace_css_url, html)
    html = HREF_RE.sub(replace_local_href, html)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8", newline="")
    return len(cache), sum(path.stat().st_size for path in cache), neutralized_links


def main() -> int:
    parser = argparse.ArgumentParser(description="把学习网页打包为单文件离线 HTML")
    parser.add_argument("input", type=Path, help="入口 HTML 文件")
    parser.add_argument("--output", "-o", type=Path, required=True, help="输出 HTML 文件")
    parser.add_argument(
        "--exclude-video",
        action="store_true",
        help="不内嵌视频，改用静态封面，适合有上传大小限制的平台",
    )
    args = parser.parse_args()

    source = args.input.resolve()
    output = args.output.resolve()
    if not source.is_file():
        parser.error(f"输入文件不存在：{source}")
    if source == output:
        parser.error("输出文件不能覆盖输入文件")

    count, source_bytes, neutralized_links = pack_html(source, output, args.exclude_video)
    print(f"已生成：{output}")
    print(f"已内嵌资源：{count} 个，原始大小：{source_bytes / 1024 / 1024:.2f} MB")
    print(f"已移除失效本地附件链接：{neutralized_links} 个")
    print(f"单文件大小：{output.stat().st_size / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
