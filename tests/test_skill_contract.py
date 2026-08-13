"""验证 Skill 的生成后 UX 优化契约不会在后续版本中丢失。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    """覆盖生成后优化阶段、研究边界和版本门禁。"""

    def test_post_generation_ux_gate_is_wired_end_to_end(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        interface = (ROOT / "agents" / "interface.yaml").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

        self.assertIn("生成后 UX 优化 gate", skill)
        self.assertIn("post-generation UX optimization gate", interface)
        self.assertIn("post_generation_ux_optimization", manifest["release_gates"])
        self.assertEqual(manifest["version"], "1.3.0")

    def test_design_lenses_require_research_without_brand_imitation(self) -> None:
        contract = (ROOT / "references" / "visual-ux-contract.md").read_text(encoding="utf-8")

        self.assertIn("从第一性原则重新审视页面", contract)
        self.assertIn("Apple 与 Kimi 设计视角的转译", contract)
        self.assertIn("keep / adapt / reject", contract)
        self.assertIn("禁止复制 Logo", contract)
        self.assertIn("missing evidence", contract)


if __name__ == "__main__":
    unittest.main()
