# mailroom-dev — the LLM-Mailroom monorepo wiki

**mailroom-dev** is the central checkout of the LLM-Mailroom constellation:
one uv workspace, one lockfile, one virtualenv, ten packages under
[`packages/`](https://github.com/Exios66/mailroom-dev/tree/main/packages) —
each mirroring an independent, standalone-operational `Exios66/*` repository.

The monorepo is the **development source of truth**; the standalone repos
remain the release vehicles for the deployed surfaces.

## Start here

- [[Getting-Started]] — workspace setup, suites, offline sandbox quickstart
- [[Architecture]] — every repository, with direct links + GitHub Pages sites
- [[Board-Governance]] — the task board, its laws, and the tooling that keeps it honest
- [[Sub-Package-Sync]] — the current-only sync doctrine and the sync driver
- [[HF-Corpus]] — the mailroom-corpus corpus family and its EDA pipeline
- [[Offline-Sandbox]] — local providers, reduced agent profile, Docker
- [[Releases]] — release train, pins, upstream publish
- [[FAQ]] — gotchas and common questions

## Key facts

| Thing | Value |
| --- | --- |
| Hub repo | [Exios66/mailroom-dev](https://github.com/Exios66/mailroom-dev) |
| Task board | [`governance/TASKS.md`](https://github.com/Exios66/mailroom-dev/blob/main/governance/TASKS.md) — machine-readable via `scripts/board_state.py` |
| Conventions | [`AGENTS.md`](https://github.com/Exios66/mailroom-dev/blob/main/AGENTS.md) — read first, every session |
| Packages | 10 (7 built + 3 virtual members) |
| Python | 3.11+ (workspace `requires-python >= 3.11`) |
| Family pins | llm-mailroom **v0.6.0** · llm-dojo-scoring **v0.12.2** · llm-entity-extraction **v0.20.0** |
| HF corpus | [mailroom-corpus](https://huggingface.co/datasets/Lucius-Morningstar/mailroom-corpus) — schema v7, 1,650 rows |
| CI gate | `.github/workflows/board-governance.yml` — board invariants + label drift |
