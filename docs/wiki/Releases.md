# Releases

The monorepo is the development source of truth; upstream repositories
remain the release vehicles for the deployed surfaces (HF Spaces, Railway).

## Release train (HUB-005 scope)

1. **Propagate monorepo work upstream**
   `python scripts/sync_packages.py push --package <name>` (a subtree push
   per package). If subtree ancestry can't fast-forward (snapshot-based
   cursors), publish as clean patch commits to the standalone repo and
   re-baseline the cursor with `snapshot` (see [[Sub-Package-Sync]]).
2. **Bump the consuming pins** — release-time only:
   `packages/llm-mailroom/src/scripts/bump_dojo_scoring.py` for the dojo
   pin. Never delete a pin line; bump only when cutting a release of the
   pinned package.
3. **Tag in the standalone repo** — one tag per release (`vX.Y.Z`), cut
   from the standalone repo the release ships from.
4. **Verify** — the touched packages' FULL suites green; `git status`
   clean; the board card closed with Evidence naming the commits.

## Current family pins

| Package | Pin | Consumed by |
| --- | --- | --- |
| llm-mailroom | v0.6.0 | sandbox `fetch-deps` / `[pipeline]` extra |
| llm-dojo-scoring | v0.12.2 | llm-mailroom, llm-entity-extraction, sandbox |
| llm-entity-extraction | v0.20.0 | sandbox `[evals]` extra |

## Deploy surfaces

- Deploy configs inside each package (`Dockerfile`, `nixpacks.toml`,
  `railway.json`) stay standalone-repo aware — build images from the
  package directory as before.
- GitHub Pages sites: [llm-entity-extraction](https://exios66.github.io/llm-entity-extraction/),
  [The-Mailroom](https://exios66.github.io/The-Mailroom/),
  [llm-mailroom-graph](https://exios66.github.io/llm-mailroom-graph/).
