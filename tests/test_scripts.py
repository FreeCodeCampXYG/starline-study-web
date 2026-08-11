"""验证本地来源提取与 HTML 安全渲染。"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    """从技能目录加载待测脚本模块。"""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extractor = load_module("extract_local_sources", ROOT / "scripts" / "extract_local_sources.py")
renderer = load_module("render_study_note", ROOT / "scripts" / "render_study_note.py")
packer = load_module("pack_standalone_html", ROOT / "scripts" / "pack_standalone_html.py")


class ExtractTests(unittest.TestCase):
    """覆盖中文文本编码与行号分块。"""

    def test_gb18030_text_is_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "课程.txt"
            path.write_bytes("第一行\n第二行".encode("gb18030"))
            result = extractor.extract_txt(path, "S1")
            self.assertEqual(result["encoding"], "gb18030")
            self.assertIn("第二行", result["segments"][0]["text"])
            self.assertEqual(result["segments"][0]["locator"], "lines 1-2")
            self.assertEqual(result["path"], "课程.txt")
            self.assertNotIn(str(Path(tmp).resolve()), json.dumps(result, ensure_ascii=False))

    def test_resource_path_is_relative_or_filename_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            delivery = root / "delivery"
            asset = delivery / "assets" / "diagram.png"
            external = root / "external.png"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"asset")
            external.write_bytes(b"external")
            self.assertEqual(extractor.portable_resource_path(asset, delivery), "assets/diagram.png")
            self.assertEqual(extractor.portable_resource_path(external, delivery), "external.png")

    def test_pdf_text_keeps_page_locator(self) -> None:
        try:
            from pypdf import PdfWriter
        except ImportError:
            self.skipTest("未安装 pypdf")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "讲义.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=320, height=180)
            with path.open("wb") as stream:
                writer.write(stream)
            result = extractor.extract_pdf(path, "S1", None)
            self.assertEqual(result["page_count"], 1)
            self.assertEqual(result["segments"][0]["locator"], "page 1")
            self.assertTrue(result["segments"][0]["needs_visual_review"])

    def test_package_contains_no_developer_specific_home_path(self) -> None:
        extensions = {".md", ".json", ".yaml", ".yml", ".py", ".html"}
        windows_home = "C:" + "\\Users\\" + "xia" + "oy"
        slash_home = "C:/Users/" + "xia" + "oy"
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(windows_home, text, str(path))
            self.assertNotIn(slash_home, text, str(path))


class RenderTests(unittest.TestCase):
    """覆盖 HTML 转义和危险 URL 阻断。"""

    def test_render_escapes_text_and_blocks_script_url(self) -> None:
        payload = {
            "title": "<script>alert(1)</script>",
            "sections": [{
                "title": "核心",
                "conclusion": "结论",
                "visual": {"type": "image", "src": "javascript:alert(1)", "alt": "图"},
                "source_refs": ["S1:slide 1"]
            }],
            "sources": []
        }
        page = renderer.render(payload)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertNotIn("javascript:alert(1)", page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)

    def test_example_schema_renders(self) -> None:
        payload = json.loads((ROOT / "references" / "note-schema.example.json").read_text(encoding="utf-8"))
        page = renderer.render(payload)
        self.assertIn("主动回忆", page)
        self.assertIn("S1:slide 2", page)


class PackTests(unittest.TestCase):
    """覆盖单文件资源内嵌和无视频轻量模式。"""

    def test_light_mode_keeps_poster_and_removes_video(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "poster.png").write_bytes(b"poster")
            (root / "demo.mp4").write_bytes(b"video")
            source = root / "index.html"
            output = root / "lite.html"
            source.write_text(
                '<video poster="poster.png"><source src="demo.mp4"></video>',
                encoding="utf-8",
            )
            packer.pack_html(source, output, exclude_video=True)
            page = output.read_text(encoding="utf-8")
            self.assertIn("data:image/png;base64,", page)
            self.assertNotIn("video/mp4", page)
            self.assertIn("轻量版未内嵌视频", page)

    def test_dynamic_json_image_path_is_embedded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / "assets" / "page-001.webp"
            asset.parent.mkdir()
            asset.write_bytes(b"webp")
            source = root / "index.html"
            output = root / "standalone.html"
            source.write_text('<script type="application/json">{"image":"assets/page-001.webp"}</script>', encoding="utf-8")
            count, _, _ = packer.pack_html(source, output)
            page = output.read_text(encoding="utf-8")
            self.assertEqual(count, 1)
            self.assertIn("data:image/webp;base64,", page)
            self.assertNotIn("assets/page-001.webp", page)


if __name__ == "__main__":
    unittest.main()
