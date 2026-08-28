# llm-mailroom-graph

Interactive knowledge graph of [llm-mailroom](https://github.com/Exios66/llm-mailroom), rebuilt 2026-08-28 from commit [`7dc57874`](https://github.com/Exios66/llm-mailroom/commit/7dc57874cd4206fa6470a887c38b566f2168daf8).

Live site: https://exios66.github.io/llm-mailroom-graph/

## How to read it

The old map dumped every test fixture and vendored OpenRouter skill into one unlabeled force-layout (2,022 nodes, communities named `conftest.py`). This rebuild is scoped to **production `src/`** and is meant to be walked, not stared at.

| Page | What it is |
|---|---|
| [Architecture map](./index.html) | Default view. Three zoom levels: **layers → modules → symbols**. Conveyor strip jumps to the 13 LangGraph nodes. Comments hidden until you ask. Double-click isolates a neighborhood. |
| [Module tree](./tree.html) | Filesystem collapsible tree of the same graph. |
| [Report](./report.html) | God nodes, communities, bridges, suggested questions. |
| [Classic vis](./graph.html) | Graphify's stock force-directed canvas, if you want the hairball. |
| [GRAPH_REPORT.md](./GRAPH_REPORT.md) | Machine-written audit trail. |

## Corpus

- **Included:** `src/agents`, `graph`, `pipeline`, `api`, `storage`, `observability`, `llm`, `schemas`, `langchain_agents`, `legalbench`, `scripts`
- **Excluded:** `src/tests`, `notebooks`, `.opencode/skills` (vendored assistant tools), docs
- **Extractor:** graphify 0.9.50, `--code-only` AST, 0 LLM tokens

## Rebuild

```bash
git clone https://github.com/Exios66/llm-mailroom.git /tmp/llm-mailroom
# copy the .graphifyignore from this repo's last rebuild notes
uv tool install graphifyy
graphify extract /tmp/llm-mailroom --code-only --force --resolution 0.4 --exclude-hubs 99
graphify cluster-only /tmp/llm-mailroom --no-label --no-viz --resolution 0.4 --exclude-hubs 99
graphify tree --graph /tmp/llm-mailroom/graphify-out/graph.json --output tree.html --label llm-mailroom
```

Then regenerate `index.html` / `report.html` from `graph.json` (community labels are architectural, not hub-file names).
