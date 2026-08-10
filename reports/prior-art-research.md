# Prior-Art Research

- Researched at: 2026-08-11
- Queries: `multimedia learning notes webpage`; `ppt video transcript study notes`; `educational website generator`
- Catalogs: SkillsMP completed; skills.sh unavailable because Node/npx is not installed in the current Windows environment
- Rating evidence: unavailable; SkillsMP values below are repository stars, not ratings or skill-specific quality

| Candidate | Relevance | SkillsMP repo stars (2026-08-11 catalog result) | Quality/trust evidence | Adopt | Reject | License |
|---|---|---:|---|---|---|---|
| [AwesomeWebpageMetaSkill](https://github.com/opensquilla/opensquilla/tree/main/src/opensquilla/skills/bundled/AwesomeWebpageMetaSkill) | Multimedia webpage pipeline | 6,576 | Source inspected; explicit media binding, accessibility and validation stages | Outline before assets; text-first degradation; delivery validation | Provider-specific generators, repeated confirmations, broad write/network surface | Apache-2.0 declared in source |
| [ai-multimodal](https://github.com/mrgoonie/claudekit-skills/tree/main/.claude/skills/ai-multimodal) | Video/document extraction | 2,193 | Source inspected; explicit formats, timestamps, limits and failure handling | Timestamp-aware extraction and modality-specific degradation | Gemini/API-key dependency, unsupported cost claims as stable defaults | Source repository license not verified; principles only |
| [multimedia-learning-design](https://github.com/a5c-ai/babysitter/tree/main/library/specializations/domains/social-sciences-humanities/education/skills/multimedia-learning-design) | Educational visual design | 1,652 | Source inspected; named cognitive-load and accessibility criteria | Signaling, contiguity, segmentation, purposeful media | Generic six-step guidance without source provenance or webpage verification | License not verified; principles only |
| [ship-learn-next](https://github.com/davila7/claude-code-templates/tree/main/cli-tool/components/skills/productivity/ship-learn-next) | Turn learning content into action | 30,146 | Source inspected; concrete output and reflection structure | Active recall and a small next-action block | Mandatory 4–8 week quest and five reps; too heavy for every note | License not verified; principles only |

## Contribution ledger

- **keep**: outline-before-assets, explicit accessibility, timestamps, cognitive-load reduction, and actionable learning prompts.
- **adapt**: replace provider-specific multimodal APIs with capability-based input branches; replace generic “multimedia page” with a source-grounded study-note contract.
- **reject**: automatic audio/video generation, broad remote execution, forced multi-round confirmation, decorative media quotas, and mandatory long learning quests.
- **invent**: a claim-to-source locator matrix across TXT lines, PPTX slide numbers and video timestamps; a deterministic safe HTML renderer; a fail-loud “no transcript, no invented video summary” gate.

## Created skill advantages

- **Design advantage**: one workflow covers mixed TXT/PPTX/video inputs while keeping a consistent locator syntax.
- **Design advantage**: visuals are selected by instructional role rather than by a fixed asset count.
- **Validated advantage**: local tests cover Chinese encoding extraction, schema rendering, HTML escaping and dangerous URL blocking.
- **Hypothesis**: active recall and purposeful visuals should make the note more useful for learning, but provider-backed comparison and learner review are missing evidence.

## Missing evidence

- skills.sh install metrics were unavailable because `node`/`npx` is absent.
- No user rating/review source was available.
- No live public-video transcript provider run was performed.
- No blind learner study, accessibility audit, or cross-browser human review was performed.
