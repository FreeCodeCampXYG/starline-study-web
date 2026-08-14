"""验证 Skill 的 UX-first 契约不会在后续版本中丢失。"""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    """覆盖渲染前体验定义、生成后回归和版本门禁。"""

    def test_post_generation_ux_gate_is_wired_end_to_end(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        interface = (ROOT / "agents" / "interface.yaml").read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

        self.assertIn("先定义体验，再碰内容与样式", skill)
        self.assertIn("experience-brief.md", interface)
        self.assertIn("pre_render_experience_brief", manifest["release_gates"])
        self.assertIn("post_generation_ux_optimization", manifest["release_gates"])
        self.assertEqual(manifest["version"], "1.5.0")

    def test_design_lenses_require_research_without_brand_imitation(self) -> None:
        contract = (ROOT / "references" / "visual-ux-contract.md").read_text(encoding="utf-8")

        self.assertIn("从第一性原则重新审视页面", contract)
        self.assertIn("Apple 与 Kimi 设计视角的转译", contract)
        self.assertIn("keep / adapt / reject", contract)
        self.assertIn("禁止复制 Logo", contract)
        self.assertIn("missing evidence", contract)

    def test_experience_brief_blocks_rendering_without_product_decisions(self) -> None:
        brief = (ROOT / "references" / "experience-brief.md").read_text(encoding="utf-8")

        for phrase in ["10 秒成功", "唯一主行动", "移动端首屏", "渐进披露", "视觉禁区"]:
            self.assertIn(phrase, brief)
        self.assertIn("阻断渲染", brief)

    def test_learning_loop_requires_retrieval_teachback_and_spacing(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "learning-science-contract.md").read_text(encoding="utf-8")
        output_cases = json.loads((ROOT / "evals" / "output_cases.json").read_text(encoding="utf-8"))

        for phrase in ["主动回忆", "复述", "真实动作", "间隔复习"]:
            self.assertIn(phrase, skill)
        self.assertIn("参考答案默认折叠", contract)
        self.assertIn("二八法则：只作导航", contract)
        self.assertIn("learner outcome study", contract)
        self.assertTrue(any(case["id"] == "learning-loop-not-passive-summary" for case in output_cases["cases"]))


if __name__ == "__main__":
    unittest.main()
