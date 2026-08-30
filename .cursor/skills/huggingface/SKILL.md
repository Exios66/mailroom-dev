---
name: huggingface
description: Hugging Face usage for The-Mailroom eval/pilot scripts (docclass-merged GT, HF_TOKEN, run_production_pilot, eval_pipeline). Use for Hub datasets and copied dojo catalogs; prefer offline pytest fixtures; never import llm-dojo-scoring at runtime or start a live Qwen/Hub pilot unless the user explicitly asks.
---

# Hugging Face (eval + catalogs, not serving)

**When:** `scripts/eval_pipeline.py`, `scripts/run_production_pilot.py`,
`HF_TOKEN`, `Lucius-Morningstar/docclass-merged`, or Hub subclass catalogs.  
**This visualizer does not download weights or serve models.** Serving is
[ollama](../ollama/SKILL.md) / [modal](../modal/SKILL.md) in sister repos.

## Offline first

| Asset | Where | Network? |
| --- | --- | --- |
| Pytest traces | `tests/fake_langfuse.py` | No |
| Copied Hub subclass / CUAD keys | `mailroom_ui/pipeline_schema.py` | No |
| Dojo scoring pin | docs + copied constants (`@v0.11.0`) | No runtime import |
| Live `docclass-merged` eval | `scripts/eval_pipeline.py` | **Yes** (explicit) |
| Live Qwen 3.7-Flash pilot | `scripts/run_production_pilot.py --real` | **Yes** (explicit) |

```bash
# needs sibling llm-mailroom
python scripts/run_production_pilot.py --check
python scripts/eval_pipeline.py --session pilot-hf-...
# --real only when the user asked for a live Hub/Qwen run
```

`.env`: `HF_TOKEN` and `MAILROOM_PIPELINE_ROOT` are for those scripts, not
`mailroom-web`.

**Live Observatory on a Space** is a different job — Docker
`mailroom-hosted` via `scripts/publish_space.py` (see
[observatory](../observatory/SKILL.md)). Do not add a Gradio/FastAPI
Space SDK or a Hub model server here.

## Boundaries

- **Do not** `import llm_dojo_scoring` in this process — catalogs stay copied.
- **Do not** start a live Langfuse/HF/Qwen pilot unless explicitly requested.
- Default pytest: no Hub calls.
- For Hub CLI depth, follow the Cursor **hf-cli** plugin skill; this skill stays
  visualizer-scoped.

## Related

- Schema mirror: [pipeline-schema-sync](../pipeline-schema-sync/SKILL.md)
- Router: [mailroom-tool-router](../mailroom-tool-router/SKILL.md)
- Pin: README constellation table (`llm-dojo-scoring` `@v0.11.0`;
  llm-mailroom dist `mailroom` `@3cf9fb9` / v0.6.0 via extra `[pipeline]`)
