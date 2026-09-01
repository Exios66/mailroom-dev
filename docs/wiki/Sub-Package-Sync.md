# Sub-package sync

Every package under `packages/` mirrors an independent `Exios66/*`
repository (git subtree). **The monorepo is the development source of
truth**; the standalone repos remain standalone and operational.

## The doctrine (HUB-004, human-confirmed)

- **Current-only pulls** — only import upstream code that is current; stale
  code never regresses the monorepo (the sync driver has no rewind path —
  it only reports *forward* drift).
- **Monorepo truth wins** — on conflict, monorepo-side fixes win unless
  upstream genuinely supersedes them.
- **No merge tangles** — pulls are squashed; if subtree ancestry can't
  fast-forward (snapshot-based cursors), publish monorepo fixes upstream as
  clean patch commits instead of forcing grafts.
- **No silent drift** — `status` always recomputes real drift against live
  upstreams, so a stale manifest is visible at a glance.

## The driver

```bash
python scripts/sync_packages.py status                       # drift report (fetches upstreams; --json for machines)
python scripts/sync_packages.py pull  --package <name> --squash   # import upstream commits
python scripts/sync_packages.py push  --package <name>       # publish monorepo commits upstream
python scripts/sync_packages.py snapshot [--package <name>]  # re-baseline the manifest at current upstream tips
```

- `pull`/`push` refuse to run on a dirty worktree (`--allow-dirty` overrides).
- `pull --squash` keeps upstream history out of the monorepo log.
- Per-package cursors live in `scripts/packages_sync.json`.
- After a pull, **re-apply monorepo-side prunes** the merge may resurrect
  (e.g. `packages/llm-entity-extraction/docs/{data,posit,posit-src}/` are
  gitignored-heavy-asset paths; gitignore does not apply to tracked files,
  so `git rm -r --cached` + tree removal is the fix — HUB-004).

## Verification contract for a sync session

1. `status` → all packages in sync (or the drift is the work).
2. Post-pull: the pulled package's FULL suite green (a subtree pull is a
   significant change).
3. Monorepo-side guards/skip-fixes intact.
4. Cursor advanced; `git status` clean; board card closed with Evidence.
