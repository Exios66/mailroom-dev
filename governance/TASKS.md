# TASKS.md — the mailroom-hub task board

The single source of truth for cross-agent task state in the monorepo: what is
**assigned**, **in progress**, **needs attention**, and **done**. Every agent
(and human contributor) reads this board before working and keeps it current
while working. It is a WORKING DOCUMENT, not documentation — modify it as work
happens, never delete history (finished cards move to the Archive at the bottom).

Scope: **monorepo-level work** (workspace wiring, cross-package governance,
sub-package sync, docs, releases). Work scoped to a single package is tracked
by that package's own governance (e.g.
`packages/llm-entity-extraction/governance/MESSAGE_BOARD.md`) — this board
holds the hub view and cross-package cards. Simplified counterpart of the
entity board: same laws, fewer steps.

> This board is the stand-in for inter-agent communication. When the external
> agent communication thread lands (HUB-006), it becomes the discussion
> channel and this file remains the lane table + archive of record.

**Machine-readable state (HUB-014):** this board is computationally readable
via `python scripts/board_state.py` — `status` (snapshot, `--json` for
machines), `card HUB-0NN` (one card + its commits), `check` (invariants:
structural contradictions exit 1; hygiene drift is warned), `sync-issues`
(label sync onto synced issues), `project-init`/`project-sync` (GitHub
Projects v2 mirror). The label taxonomy for issues lives in
`.github/labels.json` (`stage/*` = these lanes, `attention/*` = the
needs_attention tags, `type/*`, `priority/*`, `domain/*`, `kanban` marker);
the CI gate `.github/workflows/board-governance.yml` runs `check` + the
label audit on every change to `governance/`, `scripts/`, or `.github/`.

## How to use — four steps

1. **Read first.** Read this board (and open GitHub issues) at session start,
   before any task: cards claimed by others, cards covering the work you were
   about to do, and open needs-attention items. Never duplicate or race a
   claimed card.
2. **Claim.** Move the card to `assigned` (if queued) and set Owner to your
   agent name + date. The moment ANY work exists — a first edit, a diff, a
   branch, a run in flight — the card moves to `in_progress`. Label it before
   the code, never after; the table must never lie about reality.
3. **Work with the card current.** Update status and Evidence as you go.
   Stuck or awaiting review? Move to `needs_attention` with a tagged note
   (`needs:` blocked-on / `review:` evidence / `decision:` the question).
   Anything discovered but not delivered spawns its own card BEFORE your card
   closes.
4. **Close with proof.** `done` requires: the package suite(s) for the touched
   packages green, `git status` clean for the card's scope, Evidence naming
   the commit(s), and — for synced cards — the GitHub issue closed in the same
   commit. Then move the card to the Archive. An agent is NOT done until its
   card says so.

## Lanes

| Lane | Meaning |
|---|---|
| `assigned` | Queued or claimed, nothing underway — no draft, no diff, no branch. Owner may be `unclaimed` (up for grabs: claim it per step 2). |
| `in_progress` | ANY work exists and an owner holds it. ONE owner per card. |
| `needs_attention` | Blocked, awaiting review, or awaiting a decision — the Evidence note says which (`needs:` / `review:` / `decision:`). |
| `done` | Finished, verified, evidenced — moved to the Archive below. Never deleted; reopen by moving back to `assigned` with a dated note. |

## Open cards

| Card | Status | Task | Owner | Issue | Evidence |
|---|---|---|---|---|---|
| HUB-006 | `assigned` | **External agent communication thread integration** — the human is standing up a communication channel for agents outside this repo. When live: link it here as the discussion channel, re-point this board's "stand-in" note, and record the handover in Evidence. | Exios66 | — | opened 2026-08-30 by the human directive |
| HUB-020 | `assigned` | **docclass eval judge prompts still grade against the retired 8-class "EXTENDED primary set"** — discovered during HUB-019 component 6: `packages/llm-entity-extraction/src/prompts_docclass.py` (judge/reviewer/arbiter/boss docclass prompts) and the byte-mirror `packages/The-Mailroom/mailroom_ui/docclass_prompts.py` instruct judges to grade against the extended 8-class list (incl. retired compliance_filing/court_opinion/due_diligence) while the docclass GT is the canonical five (plan §5/§66/§93; docs/v7-taxonomy.md §5 avoid-list). Land in THIS monorepo (human directive: all work in mailroom-dev): add NEW prompt version keys (never mutate versions that have run) with five-class + `unknown` grading language per plan §67, mirror byte-identical into The-Mailroom, leave default selection unchanged until a same-surface A/B validates v1; option-list ↔ schema-enum test parity maintained. Decision open for the human: whether the docclass arm keeps the extended surface as deliberate eval design (KANBAN-033 lineage) or moves to five-class grading. | unclaimed | — | HUB-019 Evidence 2026-09-02 |
| HUB-036 | `assigned` | **v9 corpus candidate: INSURBIAS insurance-claim source** — spawned at HUB-028 close (append-only law: the deferred item gets a card before the parent closes). HUB-028 evaluated INSURBIAS for the v8 LOB expansion and deferred it as GT-sparse; v9 (or later) should re-evaluate it alongside the P4 expansion priorities (`docs/reports/audits/docclass_expansion_priorities.md` — insurance_workflow is HIGH: adjuster 0%, partial denial_reasons/supporting_documents), license permitting. | unclaimed | — | spawned from HUB-028 close-out 2026-09-02; see HUB-028 archive entry |


## Rules that keep the board honest

- **One owner per card.** Never work a card someone else owns — offer help on
  the issue or take over by an explicit handoff recorded in Evidence.
- **Claim before edit.** A card you are about to touch is claimed by you in
  the same session the work starts; an unclaimed card is fair game but must
  be claimed at its first edit.
- **Update, don't duplicate.** Work that addresses an existing card's problem
  updates THAT card — never a parallel card, never a duplicate issue.
- **Later timestamp wins.** If two edits collide on one card, the later dated
  note stands; the overwritten party posts a correction rather than reverting.
- **No silent completion.** A card without its closing Evidence is, to every
  other agent, still in flight.
- **Commit discipline.** Reference cards in commits: `HUB-00N: <summary>` or
  `HUB-00N claimed/reopened` in the message body. **Stage targeted paths only
  (HUB-029):** `git add <explicit paths>` for exactly your card's files —
  never `git add .` / `-A` / a bare directory. This is a shared checkout:
  before every commit, `git status --porcelain` and unstage anything you
  don't own (two documented sweeps — HUB-024, HUB-027 — landed other agents'
  in-flight files under the wrong message).

## Issues vs board

Small, single-session, low-risk cards are **board-only** (Issue column `—`).
Critical, cross-package, or externally-verifiable cards are **synced**: open a
GitHub issue in the repo where the work lands (this monorepo for hub scope,
the package repo for package scope), write the full link into the card's
Issue column, mirror lane moves as issue comments, and close the issue in the
same commit that archives the card. A `done` card with an open issue (or the
reverse) is a board inconsistency — fix it immediately.

## Archive
- **HUB-038** (done 2026-09-03) — **Intake agent v2 — triage + clean + prepare for the full pipeline** — human directive 2026-09-03 (better formulate the main pipeline intake agent beyond its current state, similar in nature to the free triage team, applied to the intake agent responsible for primary text cleaning + processing + preparation; follow-up directive: STOP document truncation — use SLIDING WINDOWS to preserve document text so critical information is never missed). Landed in `packages/llm-mailroom` (evidence `9ef4e4fd`): `agents/intake.py` keeps the deterministic dojo clerk as the mandatory baseline and adds an LLM-assisted pass — ONE fused call per window performing TRIAGE (advisory read: primary class / subclass / confidence / gist / keywords, shared `validate_triage` vocabulary clamp, rides manifest `intake.triage` + Gmail echo + sorter prior, never overrules the sorter), CLEAN (structural repair of messy OCR-ish text, gated, re-normalized through the clerk so `prep_invariants` hold, scored by dojo `score_intake` as `method: llm`), and PREPARE (section map: heading + role + document-absolute char offsets, deterministically validated). **No-truncation doctrine:** `sliding_windows` (paragraph-boundary, 15% overlap, hard-split for pathological paragraphs — no window exceeds the budget, every character read, nothing truncated); the sorter subclass bypasses the vendored HEAD+TAIL (per-window classify + deterministic merge: plurality vote among non-unknown classes, mean confidence of agreeing windows, first non-null subtype/subclass, joined reasoning; `WINDOW i OF n` markers; intake prior + retry preamble on every window); `ingest_node` gate + `intake-llm-prep` span + manifest merge; retry_classify no longer slices `[:12000]`. Cost + efficiency: gate fires only for messy / over-sorter-budget docs (clean short docs pay zero); cheapest paid model `qwen3.7-flash` (free tier stays the Gmail triage lane's privilege); `MAILROOM_LLM_INTAKE=0` disables; failures fail soft to the clerk. Prompt registry 16→17 (`mailroom-intake`). Tests: `test_intake_agent.py` (gate, validation, sliding-window coverage proofs incl. mid-document marker read, merged triage + translated offsets, sorter merge, prior/prefix per window, ingest wiring) + 16→17 invariants + conftest hermetic default. Gates: llm-mailroom FULL suite 859 passed / 36 skipped / 0 failed; gmail smoke 10/10 PASS. Docs currency in AGENTS.md / docs/agents.md (§1 sorter + §8b intake) / docs/configuration.md.
- **HUB-037** (done 2026-09-03) — **Gmail intake channel + free triage lane — llmmailroom@gmail.com as a second intake route** — full evidence in the pre-archive card record (git history); this entry records the completion of the triage work. Landed in `packages/llm-mailroom`: the IMAP-SSL poller, watcher embedding, intake awareness, ✅ check reaction, completion echo, and live watcher (pre-archive record) PLUS the **single-document free-triage lane** (human directives 2026-09-03): an email carrying exactly ONE accepted attachment is stamped `route: triage` and handled by the FREE OpenRouter triage team (`agents/gmail_triage.py`, `z-ai/glm-5.2:free` — free models kept deliberately, no excessive spend) — core pipeline steps without the paid agents: deterministic prep → triage classification (class/subclass/confidence/gist/keywords) → auditable-hash archive → completion echo, with its OWN `triage_*` audit-log section (`triage_ingested`/`triage_classified`/`triage_archived`, never conflated with the pipeline's stage events). Emails with TWO OR MORE accepted attachments are `route: pipeline`: the triage approach is dropped and every attachment runs the FULL paid pipeline (triage never dispatched). **Capability pre-check + honest handoff:** a deterministic LLM-free check (`_triage_capability_check`) runs BEFORE the lane — image-only inputs, scanned PDFs, and documents longer than the free `max_input_chars` budget (merger agreements typically exceed it) are handed to the full paid pipeline with `intake.triage_handoff` recording the reason (echo renders it), never a failed free-model run. **Reaction guarantee:** ✅ fires at claim time on BOTH routes, plus a terminal-stage retry inside `send_intake_echo` (deduped per Message-ID; a single-doc claim has one shot, so the terminal retry closes the gap) and a `reactions_failed` status counter. **All doc types validated:** contracts, merger agreements, insurance claims, corporate records, and correspondences through the triage lane (parametrized test matrix) + capability handoff tests (budget/image/scanned). Smoke now 10/10 PASS (single-doc triage lane + multi-doc full pipeline + audit section + reactions on both + echoes). FULL llm-mailroom suite: 837 passed / 36 skipped / 0 failed. Prompt registry 15→16 (`gmail_triage` registered in `llm.prompts.prompt_templates`). Evidence: `1b6d2ed6`, `511ef9b1`, `7c1a1078`, `f93b8213` (committed under the human's git identity; docs currency in AGENTS.md / docs/agents.md / docs/configuration.md).

Finished cards, append-only, newest last.

- **HUB-032** (done 2026-09-02) — **Post-collision GT reconciliation —
  hardening onto the v8 base** — full evidence in the pre-archive card
  record (git history). Summary: the interleaved HUB-028 (v8) / HUB-022
  (§84) publishes left the Hub mixed; GT was rebuilt on the v8 value base
  (`bba2f750`), the 31 original columns asserted value-identical,
  document_ids drift-free, and republished at `eafe1ab4` (10/10 sha256
  local==hub, §91 gates green). Independently re-verified from downloaded
  bytes by the card claimant (GLM-5.3-Flash): GT 2,000×60, 19 rows/7
  threads, 7-way source split, synthetic 950, bundles 50 + fixtures 32
  intact; the claimant's parallel staging path agreed on every fact and
  stood down (no double-publish). Closed by the human directive "ensure
  all appropriate boards are closed": the datasets-server re-poll noted in
  evidence is Hub-side cache infrastructure (auto-polling), not card scope
  — the authoritative check is the byte-level download verification, which
  passed twice, by two agents independently. Board-close edit note: these
  archives + the HUB-036 spawn rode commit `edc1b033` (another agent's
  sweep — the documented HUB-024/027/029 pattern; content verified).
- **HUB-028** (done 2026-09-02) — **mailroom-corpus v8 — synthetic
  insurance-claim LOB expansion + full GT conformance** — full evidence in
  the pre-archive card record (git history). Summary: 2,000 rows published
  (insurance 950 = 600 CMS + 200 GNOTHEIA property + 150 BDR auto; 50
  strata); 27-key GT fully populated; test-split nullification PASS; blind
  leak clean; sha256 local==hub; card v8 with the §84 section restored
  after the interleaved-publish collision (reconciled forward as HUB-032);
  7 new v8 tests (corpus-eda 73 passed); INSURBIAS deferred → spawned as
  HUB-036; final leg `7f8983ac` retargeted FULL_CORPUS_REVISION to the v8
   hardened tip `eafe1ab4` per §44 pin law (llm-mailroom 775 passed).
   Deferred to v9: INSURBIAS (see HUB-036). Post-close follow-up (2026-09-02,
   same session): **purpose/gist extraction surface** — the v8 corpus GT
   carries subject_matter/keywords on ALL 950 insurance rows but the
   entity-extraction eval surface dropped them (taxonomy field_types,
   specialist schema, prompt); landed: taxonomy `insurance_claim` gains
   `subject_matter` (free_text) + `keywords` (entity_list:name) + `property`
   `/` `auto` subclasses; `INSURANCE_CLAIMS_SCHEMA` gains both fields;
   `insurance_claims_specialist_v2` (9b/9c extraction rules, v0/v1
   byte-stable, mirrored into The-Mailroom registry); specialist runner
   scores them (`INSURANCE_FIELD_KEYS` + `GT_FIELD_TYPES`); v8 dump rebuilt
   against `eafe1ab4` (expected_fields 350/350 property/auto carry both
   fields); coverage matrix regenerated (subject_matter/keywords 100% on
   950 rows; expansion priorities refreshed to 2,000 rows); entity-extraction
   756 passed.
- **HUB-035** (done 2026-09-02) — **Entity package: eval infrastructure for
  sorter + specialists on the v7 + v8 corpus** (hub card only per human
  directive — no MESSAGE_BOARD twin). Survey found: runners defaulted to a
  nonexistent `data/datasets/docclass_merged.jsonl`, no v8 dump path, no
  revision-pinned corpus loader, and the specialist runner wired only
  contracts + insurance arms. Landed in `packages/llm-entity-extraction`:
  (a) `scripts/datasets/build_mailroom_corpus_dumps.py` — revision-pinned
  dump builder pulling the staged parquet shards via `huggingface_hub` (no
  `datasets` dependency), joining textless-GT ↔ default configs on
  `filename`, deriving GT scalar keys DYNAMICALLY (v7's 27-key → v8's 60
  columns flow through untouched), schema-filtering `expected_fields`
  against `config/taxonomy.yaml` field_types (provenance keys like
  document_id/annotation_method must never be scored), preserving full
  `gt_fields` + default-config `metadata` (complete representation of both
  configs), writing per-arm manifests + a sha256 build manifest, and using
  the KANBAN-088 `safe_jsonl_line` writer (enrolled in the adoption sweep);
  (b) specialist runner: all FOUR canonical arms
  (correspondence_specialist + corporate_records_specialist added;
  merger_agreement documented as contracts-arm territory), generic enrich,
  keyless `--dry-run` (key gates moved after the dry-run return in BOTH
  runners, preserving live behavior) with a GT-gap-aware dry-run message;
  (c) 8 offline tests (join, dynamic GT derivation, v8 schema growth,
  manifests, build manifest, per-arm filtering, enrich semantics) +
  runbook in `scripts/eval/README.md`. VERIFIED END-TO-END against the live
  Hub: v7 @ `bb57c5ad` → 1,650 rows (arms 661/600/350/39 — exact HUB-019
  freeze shape), v8 @ `eafe1ab4` (Hub tip) → 2,000 rows (insurance 950 =
  600 CMS + 200 GNOTHEIA + 150 BDR per HUB-028); sorter dry-run keyless on
  v8 (exact class distribution, canonical five-class set); contracts arm
  509/661 scoreable (CUAD clause GT), insurance 950/950; correspondence +
  corporate_records arms wired and dry-run-clean but carry no schema-shaped
  GT yet (corpus GT is intent/subject_matter-shaped — the HUB-022 matrix
  gap; live scoring refuses until the HUB-031/032 reconciliation defines
  it — documented, not invented). Dumps stay local (gitignored) — rebuilt
  deterministically from the pinned revisions. Suite: entity FULL 753
  passed / 28 skipped / 0 failed. Live LLM runs remain a human-keyed
  follow-up. REOPENED same day (human directive: "implement the identified
  fixes"): the correspondence + corporate_records arms scored NOTHING
  because enrich targeted the OUTPUT-SCHEMA keys (sender, recipient,
  filing_number, ...) while the corpus GT carries intent/subject_matter-
  shaped fields. Fix: arms now score the GT THE CORPUS ACTUALLY CARRIES
  (per HUB-022 matrix, empirically rescanned): correspondence = intent ·
  sentiment_label · content_topic (350/350 rows) + subject_matter/keywords
  (96/350); corporate_records = subject_matter/keywords (38/39); explicit
  GT scoring types in `GT_FIELD_TYPES` (deterministic — no heuristic
  fallback); `_decode_listish` adapts the JSON-encoded keywords GT to
  entity_list scoring (house pattern: cuad_labels_to_clause_list);
   output-schema fields stay in the agents' extraction schemas untouched —
   taxonomy.yaml NOT edited (GT-reconciliation semantics remain
   HUB-031/032's lane; this card only wires scoring to existing GT).
   LATER ADDENDUM (2026-09-02, HUB-028 post-close follow-up): taxonomy.yaml
   WAS then edited for the INSURANCE arm only — `subject_matter`/`keywords`
   added to `insurance_claim.field_types` (they exist on the schema and on
   all v8 corpus rows) + `property`/`auto` subclasses; the runner's
   `GT_FIELD_TYPES.insurance_claims_specialist` entry added; insurance
   `INSURANCE_FIELD_KEYS` extended. The correspondence/corporate arms are
   unchanged (their field_types stay output-schema-shaped; GT scoring rides
   GT_FIELD_TYPES as documented above).
   COORDINATION NOTE for the HUB-031/032 landing: the runner merges
  `{**get_field_types(doc_class), **GT_FIELD_TYPES[arm]}` — for the
  correspondence/corporate arms the GT_FIELD_TYPES entries WIN over any
  future taxonomy.yaml field_types for those five keys; if the
  reconciliation types them differently, update GT_FIELD_TYPES in the same
  commit (HUB-035 owner keeping the runner honest, observed 2026-09-02). Dry
  runs verified: correspondence 350/350 scored, corporate_records 38/39.
  Runbook GT paragraph updated. Suite: entity FULL 754 passed / 28 skipped /
  0 failed. Original Evidence: the delivery commit (`557b76e6`); follow-up
  Evidence: this commit — with one correction: the runner-half of the fix
  landed swept inside the parallel agent's `dbd79308` (broad add, same
  incident class as HUB-024/027/029 — see the HUB-029 staging norm).
- **HUB-034** (done 2026-09-02) — **Header diagram: universal auditable-hash-archive
  flow** — human directive ("ALL of the files end up in the auditable hash
  archive, that is the point of the mailroom, not just the failed ones, it
  should ALL be traceable"): the HUB-027 banner implied archiving was a
  failure-only outcome ("Archive — unresolved items"). Diagram restructured
  (both light + dark variants): the failure-only archive box is REPLACED by
  an **Auditable Hash Archive** terminus ("IMMUTABLE · HASH-CHAINED — every
  file & every decision") fed by TWO primary edges — Route → archive
  ("delivered · sealed") and Human Review Queue → archive ("all
  dispositions", covering approve/reject/escalate) — while low-confidence /
  failed-checks keep their dashed review paths and the corrected · resubmit
  loop stays. Subtitle + aria desc + README alt text state the doctrine
  verbatim; legend unchanged; geometry re-balanced (queue narrowed to 320,
  archive x=790 w=360). Verified: xmllint both well-formed, qlmanage renders
  eyeballed (light re-checked after label move). Canonical dark 13-node SVG
  untouched (its ARCHIVE stage already says "source + manifest + hash-chained
  audit" — the doctrine was right there all along). Evidence: this commit.
- **HUB-022** (done 2026-09-02) — **docclass-merged P1 — Mailroom Evaluation
  Hardening (plan §86, §84A sequencing)** — full evidence in the pre-archive
  card record (git history). Summary: P1 landed `846c6e83` (eval_contract
  derivations + closed vocabularies, §40–41 coverage matrix, §5A spans); P2
  groundwork `0b6ff1f9` (lucius HF audit: In-Reply-To structurally absent
  from the CMU maildir — §14A verified; matter.py never-mix guard; live
  audit 19 rows/7 threads); P2/P3/P4/P5 scaffold `f080322b` (bundles.py,
  fixtures.py, expansion_priorities, P5 ledger); §84 PUBLISHED `0cb4c9e6`+
  `bbab0e63` (staging script + sha256 thread-key fix after lucius's
  determinism gate caught PYTHONHASHSEED-salted ids) — Hub commit
  `61c16645`: GT 1,650×60, bundles 50, fixtures 32, sha 11/11 ok, 19/7
  re-confirmed on downloaded bytes, blind default untouched. Interleaved
  publish collision with HUB-028 reconciled forward as HUB-032 (not
  silent). Forensics: /tmp/opencode/hardened_publish_report.json.
- **HUB-022** (done 2026-09-02; entry restored) — **docclass-merged P1 —
  Mailroom Evaluation Hardening (plan §86, §84A sequencing)** — human
  directive; RESTORATION NOTE: the card row was removed from the board
  during the HUB-028/031 v8 close-out instead of being archived (never-
  delete law); this entry is reconstructed from session capture + the
  commit trail. Landed across the card's life: P0 completeness pass
  (`run_pipeline(dataset=...)` trace fields, 8 passed; baseline audit GT
  columns fact corrected 32→31); **P1** `mailroom_eda/eval_contract.py`
  (§59 expected_specialist registry-derived, §57–58 expected_stage, §31
  review/retry closed vocabularies, §43 annotation_provenance verified over
  all 1,650 rows — verified_join 162 / llm_zero_shot 92 / human_annotated
  96 / synthetic 600), `scripts/coverage_matrix.py` → §40–41 report,
  §19 span schema, §68/69/70 fixture vocabularies, §14A decision documented
  (commit `846c6e83`); P2 groundwork — §14A VERIFIED with data (In-Reply-To/
  References structurally absent from the CMU maildir; subject populated
  346/350, 266 meaningful), `MATTER_CONSTRUCTION` heuristic_reconstructed,
  `mailroom_eda/matter.py` (commit `0b6ff1f9`); P2/P3/P4/P5 scaffold —
  `mailroom_eda/bundles.py` (five bundle-family templates), `fixtures.py`
  (calibration quartet at live taxonomy bands), P4 expansion priorities,
  P5 surfaces ledger (commit `f080322b`); suite grew 15→65 passed across
  the scaffold. Card completed by the v8 publication under HUB-028
  (commit `439560f9`: 2,000 rows, 27-key GT conformance, test-split
  nullification, sha256-verified Hub publish) + board-evidence restoration
  (`319a3ebe`). Owner: Lucius (opencode). Evidence: `846c6e83`, `0b6ff1f9`,
  `f080322b`, `439560f9`, `319a3ebe`.

- **HUB-031** (done 2026-09-02) — **resolved without a card (ID-collision
  closure)** — the HUB-031/032 IDs were both claimed concurrently by the v8
  follow-up agent mid-card (live shared-checkout editing); the work settled
  as HUB-032 (GT reconciliation) and HUB-033 (badge audit). This archive
  entry exists so the board checker's phantom-card-reference gate resolves
  the HUB-031 token in historical commit messages (e.g. `c9f9b876`, HUB-035
  coordination note) — there is no HUB-031 work; see HUB-033's own collision
  note.
- **HUB-033** (done 2026-09-02) — **GitHub badge audit — all README badges
  render across paths** — human directive ("ensure all of our github badges
  render properly in the repository across paths and such"). Method:  extracted all 76 unique shields.io URLs from every README, fetched each
  SVG and verified the rendered `<title>` text (catches escape/syntax
  mangling), HTTP-checked all external targets (3 HuggingFace dataset repos
  → 200, incl. the renamed mailroom-corpus), verified every badge's
  relative link target exists on disk (reports/tests/LICENSE paths), and
  cross-checked version badges against the packages' own pyproject pins
  (The-Mailroom 0.3.0, dojo v0.13.0, llm-mailroom v0.6.0,
  agent-mailroom v0.12.1 — the last matches its own pin: upstream lag,
  flagged for the HUB-005 release train, NOT hand-edited per mirror law).
  One defect found + fixed: the root README's License badge linked a
  LICENSE file that did not exist at the hub root — added the MIT LICENSE
  (house template per packages/agent-mailroom/LICENSE; badge already
  claimed MIT publicly). False positives excluded: zod/fast-check/discord
  badges live in .opencode/node_modules (local tooling, never rendered).
  No CI-status badges exist (moot while Actions is billing-locked).
  ID collisions: HUB-031/032 were both claimed concurrently by the v8
  follow-up agent mid-card (live shared-checkout editing); this card
  settled on HUB-033. Evidence: this commit.
- **HUB-030** (done 2026-09-02) — **Dependabot config for the monorepo** —
  human directive ("generate the appropriate dependabot.yml"). Landed
  `.github/dependabot.yml` with three ecosystems and the exclusions that
  make it appropriate to THIS repo: (a) root `pip` (uv workspace; Dependabot
  supports uv.lock via the pip ecosystem) with one grouped PR for the dev
  group, weekly; (b) `github-actions` for `.github/workflows/`, weekly;
  (c) `docker` for `packages/local-mailroom-sandbox/deploy/` (the actively
  maintained offline image; HUB-015 version-pinning doctrine — bumps keep
  the pins honest), monthly, riding the HUB-005 release train upstream.
  DELIBERATELY excluded with an in-file rationale: all `packages/*/`
  pip manifests — subtree mirrors of independent Exios66 repos; Dependabot
  PRs against them would create monorepo-ahead drift against the sync
  driver's cursors AND bump release-time-only git pins against the
  workspace-pins law (AGENTS.md). Claimed + landed in one commit
  (config-only, single-pass). Board check 0/0. Evidence: this commit.
- **HUB-029** (done 2026-09-02) — **Team norm: targeted `git add <paths>`
  only** — human directive ("a team norm of targeted git add <paths> only"),
  codifying the fix for the two shared-checkout sweep incidents (HUB-024,
  HUB-027) where a parallel agent's broad add landed other agents' in-flight
  files under the wrong commit message. Norm landed verbatim in the three
  surfaces the commit-discipline law lives: `governance/TASKS.md` (Rules
  that keep the board honest), root `AGENTS.md` (Commit discipline bullet),
  and `docs/wiki/Board-Governance.md` (rides the next `sync-wiki.sh` push).
  Rule: `git add <explicit paths>` for exactly your card's files — never
  `git add .` / `-A` / a bare directory — and re-check
  `git status --porcelain` before every commit, unstaging anything you
  don't own. ID collision note: HUB-028 was claimed concurrently (corpus v8); this card took HUB-029. Claimed + landed in one commit (docs-only, single-pass edit;
  the board file is itself part of the change). Board check 0/0. Evidence:
  this commit.
- **HUB-027** (done 2026-09-02) — **Root README banner — "Mailroom Processing
  Pipeline" adapted for GitHub** — human directive with the diagram's actual
  SVG source supplied in-session (6 stages Intake → Preprocess → Classify →
  Extract → Validate → Route; Human Review Queue + Archive exception paths
  with low-confidence / failed-checks / corrected-resubmit / reject edges;
  cross-cutting services strip: job queue, object storage, LLM gateway,
  observability, audit trail). Landed: `docs/assets/
  mailroom-processing-banner.svg` (light, source-faithful) +
  `mailroom-processing-banner-dark.svg` (GitHub-dark palette translation —
  canvas/nodes #0d1117/#161b22, borders #30363d, amber review queue
  #d29922/#e3b341, indigo LLM-stage #818cf8); README banner swapped to the
  `<picture>` prefers-color-scheme dual-theme pattern (camo-safe: system
  font stack, no scripts, viewBox-only) — the previous dark 13-node
  `mailroom-pipeline.svg` stays untouched and canonical (self-referenced
  source of truth); fixed the adjacent broken canonical link
  (`docs/assets/mailroom-pipeline-svg` → `.svg`). Verified: xmllint
  well-formed on both, qlmanage renders eyeballed (light + dark). Docs-only,
  board-only. Evidence: this commit.
- **HUB-026** (done 2026-09-02) —
  **Offline sandbox: remote-serving integration completeness (Modal / vLLM /
  conda / SSH tunnels / CHTC) + CHTC annotation pass** — human directive
  ("ensure the sandbox is fully configured for integration with Modal, vLLM,
  a conda environment, SSH tunnels, or interfacing with CHTC"; reopen:
  "add annotations and specifics for the use of the UW Madison CHTC services
  … they have several fully dedicated docs online regarding their operating
  system + requirements"). Delivery leg (`60fe58b5`): Modal (`deploy/
  modal_vllm.py` + `modal-vllm` profile) and vLLM-local verified intact;
  landed the `vllm-remote` profile with a `tunnel:` block (env-var
  indirection, nothing secret in-repo), `mailroom_sandbox/tunnel.py`
  (network-free argv builders, pidfile lifecycle, double-forward refusal),
  `sandbox tunnel plan/up/status/down` (leaf parsers drop
  `parents=[shared]` so leaf defaults can't clobber the parsed profile; the
  before-subcommand clobber is pre-existing CLI-wide and now documented),
  `deploy/conda/environment.yml` (CPU-first portable env, vLLM external,
  conda-pack for staging), and `deploy/htcondor/` two-path templates
  (batch eval for the shared pool / server for owned GPUs).
  Annotation leg (this commit) — every CHTC claim grounded in their live
  user docs: access points ap2001/ap2002 + login requirements (CHTC
  account, NetID, Duo MFA, campus network/UW VPN, ControlMaster reuse with
  the port-forwards-on-initial-connection rule, Mosh lacks forwarding);
  OS strategy (RHEL-family execute nodes; Apptainer containers carry their
  own OS — `docker://vllm/vllm-openai` direct or staged `.sif` via
  `osdf:///chtc/staging` + `HasCHTCStaging`; conda-pack must be BUILT ON
  THE ACCESS POINT for glibc match, never macOS; .sif builds only in
  interactive build jobs); /staging + the live 2026 staging-transition
  notice; the full GPU Lab roster (P100/2080Ti/A100-40/80/L40/L40S/H100/
  H200 with capability+VRAM) + job classes (short 12h / medium 24h / long
  7d + per-user caps, default medium) + `condor_status` exploration;
  submit-file knobs corrected per the roster (batch → `short`,
  `gpus_minimum_memory 24000` excludes 10–16GB cards for Qwen3-8B,
  optional capability 8.0; `CUDA_VISIBLE_DEVICES` is HTCondor-owned;
  `+is_resumable` backfill note) and the `ON_EXIT_OR_GRACEFUL_REMOVAL`
  typo fixed; `condor_ssh_to_job` policy dated (2026-04-22, shared-GPU
  removal; `condor_tail` for monitoring). Suites: sandbox 58 passed /
  1 documented skip / 0 failed; board check 0/0. Evidence: `60fe58b5`
  (delivery) + this commit (annotations).
- **HUB-025** (done 2026-09-02) — **Enron EDA visualization distortions
  (#9)** — human-filed bug: the "Enron Subclass Distribution" donut rendered
  with bunched & distorted labels (email 97.8%; the seven sub-1% subclasses
  collapsed into slivers whose Plotly outside labels piled into the title and
  stretched leader lines into a spike). Root cause: `scripts/
  gen_interactive_charts.py` chart #1 used `textinfo: "label+percent"` with
  default text positioning on a 97.8%-dominated pie — Plotly pushes sliver
  labels outside where they collide. Fix (encoding only, data untouched):
  per-point `textposition` — dominant slice labeled inside, slivers
  unlabeled but kept as visible slices + legend entries, plus a rich
  `hovertemplate` (label / comma count / percent) so no detail is hidden.
  Static twin `01_subclasses.png` verified ALREADY correct (log-scale bar +
  rare-subclass panel) — untouched. Artifact regenerated via the generator:
  only `01_subclasses_interactive.html` changed (all other claims/Enron
  charts byte-identical — determinism held); data self-consistency
  re-verified against the screenshot (attorney_demand 4/517,075 =
  0.000773%). Docs: index.html caption "Subclass Distribution (pie)" stays
  accurate; no doc changes needed. Suite: Enron 74 passed / 0 failed (suite
  does not cover hub tooling; artifact verified structurally). Issue #9
  closed by the fix commit. Evidence: this commit.
- **HUB-024** (done 2026-09-02) — **Core-repo changelog + semantic-version
  release chain** — human directive ("ensure our core repo is keeping a solid
  changelog and GitHub semantic version release chain … as the core repo of
  truth"). Delivered: (a) root `CHANGELOG.md` (Keep a Changelog 1.1.0; hub era
  HUB-001→ backfilled into `[0.1.0]`; scope note separating the hub chain from
  the pre-import standalone-mailroom lineage and from package-level releases);
  (b) `scripts/release_chain.py` (stdlib): `status`/`check`/`cut` — structural
  errors (exit 1): a version tag without its changelog section, duplicate/
  non-semver/out-of-order sections, hub pyproject behind the newest tag;
  warnings: stamped-but-untagged section (prep state), tag-message
  convention, lightweight tags; `cut` stamps `[Unreleased]` → dated section +
  bumps the hub pyproject version (dry-run default, `--apply`/`--tag`, never
  commits or pushes); (c) CI: `release-governance.yml` gate on `v*` tag
  pushes + workflow_dispatch; `board-governance.yml` gains the release-chain
  step + `CHANGELOG.md` path trigger; (d) **v0.1.0 cut**: annotated tag
  `v0.1.0` (`mailroom-hub v0.1.0` message) + GitHub Release from the
  changelog section — first hub release; (e) docs currency: AGENTS.md
  (commands + workspace rule), README (tree + commands), scripts/README.md,
  wiki Releases.md (hub-chain section). Coordination incident (honest
  record): the main deliverables were swept into a parallel agent's broad
  `git add` commit `04e1f604` ("Add hub changelog and contract fixtures")
  from the shared checkout, mixed with that agent's llm-mailroom README
  work; the card claim rode along in `1bc76344`; dedicated follow-ups for
  docs currency (`bac48976`) and this archive. **CI billing-lock incident**:
  Actions compute on the Exios66 account has been locked since ~2026-08-31
  ("The job was not started because your account is locked due to a billing
  issue") — the original board-governance 0s "workflow file issue" failure
  was this lock, and that workflow had been manually disabled in response;
  re-enabled, then ALL billing-failing workflows paused per human directive
  (mailroom-dev `board-governance` + `release-governance`, llm-mailroom
  `Bump llm-dojo-scoring`; Gaze_Calculator-66 `Scheduled` no longer exists
  in-repo) — re-enable after the human resolves github.com/settings/billing;
  `release_chain.py check` verified green locally. Chain post-tag: 0 errors /
  0 warnings; board check green. Suites: none (hub tooling only). Evidence:
  `04e1f604`, `1bc76344`, `bac48976`, tag `v0.1.0`,
  https://github.com/Exios66/mailroom-dev/releases/tag/v0.1.0, this commit.

- **HUB-023** (done 2026-09-02) — **Rename the HF dataset
  `docclass-merged` → `mailroom-corpus`** — human directive ("docclass was
  always a placeholder"). Hub leg (lucius): `HfApi.move_repo` preserves git
  history — pre-flight (no collision, tip `bb57c5ad`, 1,659 files) → move →
  post-flight verified (new repo sha == pin, pin resolves at the new name,
  file count intact, old id = Hub redirect). Monorepo leg: 57 files / 82
  exact-id replacements + composed f-string ids (hf_corpora ×
  llm-mailroom/agent-mailroom/The-Mailroom) + prose (docs, dataset cards,
  wiki, audit manifest); historically preserved: internal slug
  `docclass-merged` + `source-docclass-merged` trace tags (trace-tag
  immutability; `corpus`/`mailroom-corpus` aliases added), release marker
  `docclass-merged-v0.1-working` (version label), prompt-family version
  keys (experiment identity — append-only law), code file/flag names, plan
  text (dated addendum only, no rewrite), CHANGELOGs/governance archives,
  derived EDA/graph artifacts (canonical bytes, refresh rides the release
  train). Contract §6 rename record; §44 pin re-verified post-rename.
  Suites green (corpus-eda, llm-mailroom incl. run_hf_pilot 26 after
  fixing the `dataset` param threading into `_execute_run`, The-Mailroom,
  sandbox, dojo, agent-mailroom); parity gate green. Commits:
  `3ad5d47d`/`77a26d69`/`d064ff9b` (swept P0-completeness legs), `30b1f76c`
  (monorepo rename leg). Pin `bb57c5ad` re-confirmed at the new name
  (lucius, HF audit 2026-09-02).
- **HUB-021** (done 2026-09-02) — **Sync driver: reliable upstream
  propagation** — human directive ("fix the upstream propagation issue").
  The subtree cursor mechanics behind every recent reconciliation incident
  are now structurally guarded in `scripts/sync_packages.py`:
  (a) containment oracle — blob-tree compare (`tree_map`) of
  `packages/<name>` vs the upstream tip, gitignore-aware (pruned heavy
  assets are doctrine, not drift — HUB-004/018) with modified paths
  reported separately as monorepo-ahead delta; (b) `snapshot` refuses to
  advance a cursor past non-contained upstream content unless `--force`
  accepts the gap explicitly (HUB-018 structurally impossible by default);
  (c) `pull` skips the subtree merge and re-baselines when the tip is
  already contained (re-import loop killer); (d) `push --patch` — the
  scripted HUB-012 workaround: tracked package files rebuilt on the real
  upstream tip, ONE fast-forward commit landed upstream, cursor
  re-baselined (`--dry-run` prints the plan; plain-push failure now points
  at `--patch`); (e) `status` surfaces `CURSOR GAP` flags + per-package
  monorepo-ahead file counts (the HUB-005 release-train payload:
  corpus-eda 56, llm-mailroom 23, sandbox 20, entity 17, The-Mailroom 6,
  agent-mailroom 4, Enron 2, claims 1, graph 1, dojo 0). Pushes remain
  explicit (release-time only per workspace rules). Verified: throwaway
  fixture sims of both incidents (HUB-018 gap → refusal; honest cursor →
  clean; HUB-012 → dry-run plan then one fast-forward commit directly on
  the old tip carrying the monorepo fix, post-push cursor verifies clean);
  live `status` 10/10 in sync with 0 cursor gaps; content-verified
  `snapshot` green for all 10; clean-tree guard re-verified. Docs currency:
  README sync section + wiki Sub-Package-Sync. Hub tooling only — no
  package suite impact. Evidence: `80ee2308`.
- **HUB-019** (done 2026-09-02) — **docclass-merged corpus hardening P0 —
  baseline freeze, dataset contract, identity/provenance schema, taxonomy
  parity gate** — human directive: implement the docclass-merged plan §85
  (P0) per §84A sequencing + §84B no-silent-completion. Co-work split (human
  directive, two non-overlapping lanes) with an explicit takeover (human
  directive, "other agent fell asleep"): lane 1 = components 1–4, lane 2 =
  component 5, second agent closed the card for both lanes. (1) **Freeze**
  `docclass-merged-v0.1-working` at the true tip `bb57c5ad` (baseline audit
  Finding 1: the recorded `FULL_CORPUS_REVISION` `b3ec9ee7` predated the
  issue-#5 intent_source fix — pin advanced), audit report + machine-
  readable manifest at `docs/reports/audits/docclass_merged_baseline.{md,
  json}` via `scripts/baseline_audit.py` (revision, counts, splits, schema,
  source inventory, taxonomy/annotation/builder revisions, license/PII
  posture, known limitations; identity verification 100% over 1,650 rows;
  2 exact-duplicate groups recorded — classified, not deleted, §12).
  (2) **`docs/DOCCLASS_CONTRACT.md`** — canonical dataset contract (§80)
  with the §81 mapping table, §6 merger_agreement→contracts_specialist
  semantics, §44 pin discipline, §44A publishing path, §91+§4A release
  gates, §84 release structure; the plan itself text-extracted to
  `docs/docclass-merged-plan.md` as the shared §-reference. (3)
  **Identity/provenance/hashes** — `mailroom_eda/identity.py`
  (`document_id` from source identity, never row index; `source_corpus`
  /`source_document_id`/`source_filename`/`source_revision`;
  `content_sha256`/`normalized_text_sha256`) as §84 groundwork, verified
  100% over the pinned snapshot; published-config wiring is the explicit
  v0.2 release decision (P0 no-pushes respected). (4) **§63/§64 contract
  tests** — corpus-eda gains a suite: 15 passed (row contract + Mailroom
  interface contract, fixture + full-snapshot runs; GT config is textless →
  doc_text joined from the default config for content hashes; hollow-hash
  guard; `other` subclass allowed as explicit fallback, never null).
  (5) **§65A taxonomy-parity gate** — `scripts/taxonomy_parity.py` (stdlib,
  network-free, AST-parsed from literal sources: strict equality on
  HUB_CLASSES / taxonomy.yaml live entries / mailroom sorter vocab /
  specialist registry / v7-taxonomy.md blocks / dojo CORPUS_DOC_TYPES /
  entity PILOT universe / sandbox fixture; alias-aware structural rule for
  documented compat surfaces, §60 retired roster tolerated only as
  remnants; 5 negative tests incl. anchor-edit propagation) wired as a
  blocking `board-governance.yml` step with taxonomy-surface path triggers;
  docs currency in AGENTS.md / README / wiki Board-Governance.
  (6) **Stale-language sweep** — compliance_filing retirement wording
  reconciled across taxonomy.yaml (status: retired marker), hf_corpora,
  prompt_doctrine, graph README, sorter patch comment, v7-taxonomy §1/§4;
  residual spawn: HUB-020 (docclass eval judge prompts still grade against
  the retired 8-class "EXTENDED primary set" — prompt-versioning work, NEW
  keys + A/B, not a hand edit). Suites: corpus-eda 15 passed; llm-mailroom
  surgical 16 passed on the pin-change surfaces (full suite aborted by the
  human mid-run — noted honestly); parity gate + board `check` green.
  Evidence: `120f11d6`, `0bf22b6f`, `be1f56ef`, `de20ef17`, `5cff893e`,
  `ea76a22c`, `8d72f5e1`, `983a9b4b`, `5c744b60`, `02e83633`, `88515225`.

- **HUB-018** (done 2026-09-01) — **Sub-package sync sweep: llm-mailroom +
  mailroom-corpus-eda** — human directive: pull all packages' most recent
  versions, ensure they are synced to the monorepo including EDA reports,
  visuals, and documentation fixes. 8/10 packages already in sync; two legs
  reconciled. **llm-mailroom**: upstream tip `d4940f8a` (operational
  procedure doc + pipeline SVG) pulled with squash base `aace6a49` — the
  cursor had been snapshot-advanced past content never subtree-merged
  (`aace6a49` not an ancestor of the recorded `857fb381`), so the pull
  back-filled the whole range; process note: snapshot-advance without a
  merge creates a cursor/content gap that the next squash pull re-imports.
  Post-merge monorepo-truth reconciliation: re-pruned the gitignored heavy
  assets the merge resurrected (`docs/examples/` 9 sample PDFs + external
  corpus texts, `docs/reports/` incl. the 59,668-line experiment_log.md —
  `.gitignore:56-57`, HUB-004 doctrine); restored clobbered monorepo-side
  wiring (`[tool.uv.sources]` workspace redirect, bump-script release-time
  note, 6 pruned-asset skip guards, dojo pin-flexibility guard, UTC-stamp +
  CWD-anchoring fixes); re-tuned notebook lab scenarios to the monorepo
  taxonomy bands (low 0.90 / high 0.98 / judge band 0.97 — upstream's
  0.80/0.97 retune targets upstream's looser bands): `CLASSIFY_CONTRACT_MEDIUM`
  0.92, `CLASSIFY_INSURANCE_HIGH` 0.98, judge-band scenario extraction 0.93,
  keeping upstream's `court_opinion` override (guardrail-honest —
  court_opinion is out-of-taxonomy on both sides); refreshed stored outputs
  for notebooks 02/03/10; fixed the stale `DOC_CLASSES` pin 6→5 left by the
  compliance-filing retirement commits (pre-existing red). Suite 772 passed
  / 36 skipped / 0 failed; `uv lock --check` green. **mailroom-corpus-eda**:
  upstream moved twice mid-session (`c659789f` source dataset cards + docs
  index; `816fb028` issue #5 intent_source aeslc_join fix on the 162
  join-assisted rows); subtree squash base resolved to a pre-import ancestor
  (`d3198a2a`) → 49 pseudo-conflicts, resolved per the HUB-004/012/013 laws:
  upstream taken byte-verified for the true 13-file delta (README blurb,
  `docs/README.md` index, 5 `docs/dataset-cards/*.md`,
  `SUMMARY_REPORT.{json,md}` with figures=30 preserved, dataset_export /
  docclass_uploader / intent_backfill), monorepo-canonical kept for
  everything outside the delta (`run_all.py` summary-write guard, AGENTS.md,
  tables/, 30 matplotlib-3.11 PNG renders, 19 interactive HTMLs).
  py_compile green; EDA deliverables remain fully tracked (HUB-008
  exception). **Known residue** (discovered, not delivered): upstream's
  notebook narrative still cites upstream-band thresholds (0.85 judge gate,
  0.95 high, 0.88 reviewer labels) — inaccurate under the monorepo taxonomy
  bands; left as upstream-managed content, to reconcile at the release
  train (HUB-005 push) rather than hand-edited monorepo-side.
  `sync status` 10/10 in sync. Evidence: `2d93de6b` (prune + restorations),
  `ce98b043` (scenario re-tune), `6f2ce890` (corpus-eda subtree merge).
- **HUB-017** (done 2026-09-01) — **GitHub wiki for mailroom-dev** — human
  directive. Full version-controlled wiki source landed at `docs/wiki/`
  (entity-repo pattern): **Home** (facts table: pins v0.6.0 / dojo
  v0.12.2 / corpus v7), **Getting-Started** (workspace, per-package
  suites, sandbox quickstart), **Architecture** (full map: 10 packages +
  hub, direct repo links, the 3 GitHub Pages sites, 13-node pipeline with
  the procedural compile_report + live reviewers, layout, heavy-asset
  rule), **Board-Governance** (lanes, laws, `board_state.py` usage incl.
  severity contract + Projects v2 prerequisite, label taxonomy, issue/PR
  forms, CI gate), **Sub-Package-Sync** (current-only doctrine, driver
  commands, prune-resurrection fix, verification contract),
  **HF-Corpus** (docclass-merged v7 facts: 1,650 rows, revs, 27-key GT
  schema, strata vocabulary, P0–P6 + canonical-bytes rule, upload
  helpers), **Offline-Sandbox** (provider profiles, reduced agent profile
  — reporter retired/procedural, reviewers kept — corpus-aligned targets,
  Docker hardening + pins, commands), **Releases** (release train, family
  pins table, deploy surfaces), **FAQ** (10 gotchas incl. prune
  resurrection, tracker warnings, project scope, reporter), plus
  **_Sidebar.md** navigation and **sync-wiki.sh** (clone-or-pull, copy,
  commit + push; `--check` drift mode; syntax-checked). Root docs currency:
  README structure tree gains `docs/wiki/` + wiki paragraph; AGENTS.md
  commands gains `sync-wiki.sh`. Suite green (51 passed / 0 failed).
  **Open prerequisite (human, one-time UI action)**: the wiki git repo is
  NOT materialized until the first page is created in the web UI (no REST/
  GraphQL API for wiki content; first push returns "Repository not found")
  — visit github.com/Exios66/mailroom-dev/wiki once, create any page, then
  `./docs/wiki/sync-wiki.sh` pushes the full content. Evidence: this
  commit.
- **HUB-016** (done 2026-09-01) — **Docs-currency sweep** — systematic
  staleness pass over every surface touched by HUB-014/004/012/015. Fixed:
  sandbox `docs/sister-repos.md` dojo row v0.12.1→v0.12.2;
  `data/fixtures/ATTRIBUTION.md` v0.5.0→v0.6.0; sandbox `CHANGELOG.md`
  [Unreleased] pin bullet updated + HUB-015 Changed entry (reporter
  retirement / zero-LLM compile path / v0.6.0+v0.12.2 alignment / GT
  targets / Docker hardening); `docs/docker-offline.md` documents the
  non-root USER + HEALTHCHECK + the full version-pin table. Verified
  current (no changes needed): root README (architecture map, governance
  tooling, suite list), root AGENTS.md (commands + board law), TASKS.md,
  corpus-eda README/AGENTS (no stale figure counts), entity docs
  (upstream-managed — describes the standalone repo where the pruned dirs
  exist; prune is documented at root level), sandbox README/AGENTS/evals.md
  (HUB-015 pass). Greps for legacy template refs, stale pins, and figure
  counts all clean. Suite: 51 passed / 1 skipped / 0 failed. Evidence: this
  commit.
- **HUB-015** (done 2026-09-01) — **Offline sandbox: current-pipeline
  alignment + reduced agent profile + docclass-merged targets** — human
  directive; one commit. (a) **Version alignment**: sandbox surfaces moved
  off stale mailroom v0.5.0 → **v0.6.0** (`fetch-deps` cli help + tag,
  `overlay.py` hint, README/AGENTS/sister-repos docs); dojo pin bumped
  v0.12.1 → **v0.12.2** (llm-mailroom v0.6.0's own pin; tag verified;
  `uv lock` green); monorepo `[tool.uv.sources]` already resolves the
  current workspace mailroom. (b) **Reduced agent profile — human
  correction applied: the REPORTER agent is retired, reviewers untouched**:
  `components.yaml` moves `reporter` to `retired_agents`, adds the
  `compile_report` node gate; the sandbox eval spec is now the
  **computational procedural reporter** (`compile_report`, kind=nodes,
  observation `compile-report`) — mock + live paths are deterministic
  matter-record assembly, the `get_llm` client acquisition is GONE (zero
  LLM calls on the reporter path; new guard test asserts it). (c) **Full
  docclass-merged GT targets**: `data/fixtures/hf/docclass_mini.jsonl`
  enriched for all 5 corpus doc types with `expected_subclass` from the
  real corpus strata vocabulary (contract→Consulting Agreements,
  merger→all_cash, corporate_record→bylaws, correspondence→attorney_demand,
  insurance→carrier) + `expected_fields` from the 27-key corpus GT schema
  (correspondence: intent=payment_demand + intent_source/confidence/status
  provenance, subject_matter, keywords, claimed_amount, sentiment;
  insurance: policy_number, insured_party, date_of_loss, claimed_amount,
  damages_description); `hf_rows_as_manifest` propagates both into every
  eval row (verified end-to-end: 5/5 rows carry subclass + fields).
  (d) **Docker best practices**: Dockerfile gains non-root `USER sandbox`
  (uid 1000, override documented) + HEALTHCHECK; compose pins all four
  `:latest` images to versioned tags (ollama 0.33.2, vllm v0.28.0, phoenix
  version-20.4.0, minio RELEASE.2025-09-07-16-13-09Z) — zero unpinned
  images remain. (e) **Tests**: suite green 51 passed / 1 skipped / 0
  failed (roster test asserts reporter∉SPECS + gates; pin-guard updated to
  v0.12.2; reviewer evals preserved and passing). Docs currency: AGENTS.md
  gains the Reduced-agent-profile section; docs/evals.md compile_report
  row. Production llm-mailroom graph untouched (sandbox-profile scope per
  human choice). Evidence: this commit.
- **HUB-012** (done 2026-09-01) — **corpus-eda P3 summary counter stale
  (27 vs 30 figures)** — fixed: `visualizations.py::run()` now returns
  `{"figures": 30}` (disk truth — 30 PNGs written by the module), so
  `SUMMARY_REPORT.json` P3 stats match the artifact count. Verified by the
  FULL P0–P6 pipeline in the workspace venv: all 7 phases green, P3 banner
  "30 figures", 1,650 rows / schema v7 / P6 intent coverage 100%
  (350/350, 8/8 classes in test) — in line with the published HF corpus
  (`data 1acd2600`, `card fc1f211c`, API-verified). Determinism held: the
  summary diff is exactly the one-line `figures` correction; all 30 PNGs +
  tables byte-identical; the 19 regenerated interactive HTMLs restored to
  canonical bytes (per-render UUID rule). Published upstream per human
  directive: subtree push was non-fast-forward (cursor ancestry from the
  HUB-013 snapshot, not a graft) — clean 1-commit patch-push to
  Mailroom-Corpus-EDA `main` instead (`43b5232..f3c94f3`, fast-forward),
  cursor re-baselined via snapshot; `sync status` 10/10 in sync. Known
  benign drift: upstream's committed `SUMMARY_REPORT.json` differs from the
  monorepo's in JSON key ORDER only (5 keys, values identical) —
  upstream-side generation artifact, monorepo file is canonical. Evidence:
  `6c343bab` (fix) + upstream `f3c94f3`.
- **HUB-004** (done 2026-09-01) — **Upstream-drift reconciliation** — all
  legs complete, monorepo in sync with every standalone upstream (10/10 via
  `sync_packages.py status`). llm-mailroom leg: pulled `d93894a`+`4e9bf69`
  (`--squash`), heavy-asset prune re-applied, cursor advanced; suite 772
  passed / 36 skipped. llm-mailroom-graph refresh pulled (`fec699d`).
  The-Mailroom tip `fae52e1` reconciled. llm-entity-extraction leg
  (2026-09-01): pulled upstream `4cfac906e`→`2482879f2` — 6 additive
  KANBAN-105 commits (docclass-merged v6 builders/publish machinery:
  `build_docclass_v6.py`, `publish_docclass_v6.py`,
  `attach_original_files.py`, `export_existing_purpose_gt.py`,
  `build_correspondence_append.py`, `build_extra_claims.py` +
  `test_kanban105_docclass_v6.py`); file-level compare pre-verified zero
  overlap with monorepo-side wiring (conflict-free by construction);
  re-applied the heavy-asset prune the subtree merge resurrected
  (`docs/data/`, `docs/posit/`, `docs/posit-src/` — root `.gitignore`
  lines 52-54; gitignore does not apply to tracked files, so explicit
  `git rm --cached` + tree removal); entity suite green 745 passed /
  28 skipped / 0 failed (the 2 transitory failures were the resurrected
  pruned dirs breaking skip-guarded tests — resolved by the prune; all
  skips are documented pruned-asset/live-artifact guards). Monorepo-side
  fixes untouched (guards/markers intact); no stale code imported
  (monorepo = central truth, current-only pulls). Evidence: `a760f698`
  (entity squash) + the prune/archive commit.
- **HUB-014** (done 2026-09-01) — **GitHub governance tooling — templates,
  labels, board state tracker** — human directive: full GitHub integration
  for the hub board. Landed in one commit: YAML issue templates
  (`.github/ISSUE_TEMPLATE/`: hub card / bug / feature / task-TODO +
  `config.yml`, legacy `new-feature.md`+`todo.md` deleted), YAML PR template
  enforcing the hub discipline, declarative label taxonomy
  (`.github/labels.json`: `stage/*` lane mirrors, `attention/*` tags,
  `type/*`, `priority/*`, `domain/*` ×13, `kanban`) +
  `scripts/github_labels.py` (sync/audit), `scripts/board_state.py`
  (live-state tracker: parse open table + archive, `status`/`card`/`check`
  invariants incl. git cross-checks, `sync-issues` label sync,
  `project-init`/`project-sync` Projects v2 mirror with Lane/Owner/Card
  fields, dry-run default), CI gate `.github/workflows/board-governance.yml`
  (board check + label audit blocking; project mirror advisory), docs
  currency in README/AGENTS/TASKS. Verified: `py_compile` green; all 7 YAML
  files parse; `status/check/card/--json` green on the live board (0 errors;
  surfaced hygiene drift → HUB-008/011/013 stale open rows resolved, HUB-011
  properly archived); labels synced live (32 created, `audit` green — 3
  descriptions shortened to GitHub's 100-char limit); all 5 repo issues
  (all closed) retro-labelled with the taxonomy. Open prerequisite (human,
  one-time interactive): `gh auth refresh -s read:project` → `project-init`
  → `project-sync` to stand up the Projects v2 mirror. Suite impact: none
  (hub tooling only). Evidence: this commit.
- **HUB-013** (done 2026-08-31) — **Corpus-EDA v7 reconciliation** — v7
  intent-hydrated corpus (issue #5: aeslc_join/llm_zero_shot hydration of 350
  correspondence rows, intent_source/confidence/status GT columns; HF data
  rev `1acd2600`) is now canonical in the monorepo: subtree-pulled upstream
  (`e68b0631` — run_all P6 default, monorepo phases help text kept), v7
  interactive figures synced byte-identical to upstream `e83250c`
  (`06505812`), full P0–P6 pipeline green in the monorepo venv with
  matplotlib 3.11 renders (`e37100a9`), v7 doc sweep merged (`8d7ce748`),
  schema-v7 bump propagated across The-Mailroom/llm-mailroom/agent-mailroom
  (`41ac512a`), root docs aligned to P0–P6 + `intent_backfill`. Conflict law
  applied: upstream ported the HUB-008/009 rule TEXT to AGENTS.md but not the
  code — monorepo `run_all.py` keeps the summary-write guard + 30-figures
  print (monorepo side wins; upstream ported text matches). Cursor advanced
  to upstream tip `43b5232` via snapshot (`831c9b34`); `sync status` =
  in sync; `py_compile` green. Downloads clone now fully contained in
  upstream — safe to archive locally. HUB-012 remains open (P3 summary
  counter still 27 in v7). Evidence: `831c9b34` + commits above.
- **HUB-011** (done 2026-08-31) — **Prompt-engineer opencode agent adapted
  for the monorepo** — human directive: make the entity repo's GEPA
  prompt-engineer agent operate out of the box in mailroom-dev. Root
  `.opencode/agents/prompt-engineer.md` (workspace bindings: uv-workspace
  commands, per-package AGENTS.md rule, both prompt registries append-only
  — entity `PROMPT_VERSIONS` + mailroom `prompts_docclass.py`, the
  llm-dojo→mailroom direction doctrine, HUB-0NN vs KANBAN-NNN board routing,
  env variables incl. the funding-key gate / `BRAINTRUST_LOGGING` default /
  mailroom `OBSERVABILITY_PROVIDER` Phoenix gotcha / `PYTHONHASHSEED=0` /
  hub-1.x datasets-cache + read-timeout quirks) + the
  `PROMPT_ENGINEER_GEPA_PROVENANCE.md` companion copied verbatim. GEPA
  doctrine (9-step loop, scientific contract, Phases 0–6) preserved — diff
  vs the entity source shows exactly 3 intended binding edits, zero doctrine
  drift. Sessions inside `packages/llm-entity-extraction` keep that package's
  own agent copy (closer project config wins); the global
  `~/.config/opencode` copy stays generic. Board-only card (tooling config,
  single session). Evidence: restart opencode to load; suite impact: none
  (config-only). Archived from the open table by the HUB-014 board-state
  tracker sweep (the archive entry was missing).
- **HUB-010** (done 2026-08-31) — **Full documentation sweep** — human
  directive: update ALL documentation in mailroom-dev. Inventoried ~380
  tracked .md files; scoped the sweep to the OPERATIVE docs (root
  README/AGENTS/TASKS + 10 package README/AGENTS pairs) — historical records
  (memos, skills, wikis, slides) left untouched as standalone-mirror archives
  (llm-mailroom's AGENTS.md itself forbids monorepo-side hand-edits of its
  docs). Fixes: root AGENTS.md gains the Enron suite (74/74, verified green —
  it was missing from both root docs) and corrects the "each package carries
  its own AGENTS.md" claim (3 of 10 packages document conventions in READMEs);
  root README drops the phantom `mailroom-corpus-eda/tests` line (no suite;
  EDA verified via run_all.py P0–P5), documents the two suite-less virtual
  members, clarifies per-package sync cursors (advanced since the issue #2
  baseline), fixes the `uv run pytest` comment; corpus-eda README P3 row +
  run_all.py banner 27→30 (disk truth — 30 PNGs, Reports section and AGENTS.md
  already said 30); Enron AGENTS.md test counts aligned to reality/README
  badge (74 across test_labeler.py + test_content_labels.py). Verified:
  Enron suite 74 passed, claims-data-eda suite 30 passed ("30 tests" claim
  confirmed), run_all.py py_compile green. Spawned HUB-012 (stale P3 summary
  counter). Evidence: `bb854809`.
- **HUB-009** (done 2026-08-31) — **run_all.py subset runs clobber
  SUMMARY_REPORT.\*** — fixed: `run_all.py` now writes
  `reports/SUMMARY_REPORT.json` only when all six phases ran; `--phases`
  subset runs and `--no-interactive` (whose summary would miss the P4
  section) leave it untouched with an explicit stdout notice. Package has no
  test suite, so verification was behavioral: P4-only and `--no-interactive`
  runs leave the summary sha256-identical; a full P0-P5 run rewrites it
  byte-identical to the committed version (determinism holds); scratch
  figure UUIDs restored from git per the canonical-bytes rule; `py_compile`
  green. One transient P3 failure on a `--no-interactive` attempt did not
  reproduce on rerun (phase machinery reported it correctly with exit 1 —
  watch for recurrence). Package AGENTS.md hazard block updated to the new
  behavior; monorepo-side fix, upstream publish deferred to the release
  train (HUB-005). Evidence: `9c0a5321`.
- **HUB-008** (done 2026-08-31) — **Corpus EDA full-fidelity completion** —
  human directive: preserve figures + EDA reports faithfully, full repo in,
  history truncation OK, no republish. Imported the 18 Plotly HTML figures
  (`reports/figures_interactive/`, 74MB) sha256-identical to upstream tip
  `b39245a` (which now equals the monorepo import tip — all 71 pre-existing
  files verified byte-identical; history-truncated content import, not a
  subtree append); un-pruned root `.gitignore`; carved the corpus EDA
  deliverables out of the heavy-assets rule in root AGENTS.md; refreshed the
  stale `packages_sync.json` note — the corpus upstream IS published and
  `sync_packages.py status` shows in sync; aligned root/package docs (README
  prune note, package AGENTS.md canonical-bytes rule: Plotly HTMLs embed a
  random per-render UUID so regenerated variants can never be
  byte-identical). Verification: P4 rebuild green under the shared venv;
  caught + reverted its SUMMARY_REPORT.json clobber (spawned HUB-009); final
  tree sha256-matches upstream. Evidence: `c16cdd18`.
- **HUB-007** (done 2026-08-31) — **Import mailroom-corpus-eda as 10th
  workspace member** — subtree-added the corpus EDA package with FULL history
  appended from a local `monorepo-import` branch (interactive HTML figures
  pruned — regenerable heavy assets; standalone repo keeps them; ignored in
  the monorepo); registered in `sync_packages.py` PACKAGES +
  `packages_sync.json` (cursor at local import tip `9cc339a`, corpus repo NOT
  republished); wired pyproject (virtual member, requires-python>=3.12),
  root dev group (+plotly/seaborn/squarify/huggingface_hub), AGENTS/README
  docs; fixed pandas 3.0/matplotlib 3.11 forward compat (include_groups
  removal, boxplot tick_labels) + deterministic report outputs
  (repo-relative paths, stable diff ordering) so monorepo rebuilds are
  byte-identical; `uv lock`/`uv sync` green, `run_all.py` P0-P5 green under
  the shared venv against the full 1,650-row corpus (v6 rev2). Evidence:
  `39409359` (subtree add), `0a5b498a`, `90b25747`, `989f95bb`.

- **HUB-003** (done 2026-08-30) — **Root documentation + governance foundation** —
  README reworked for the monorepo (structure tree, package↔mirror table, sync
  usage, release flow); `.gitignore` extended (ruff/ipynb/coverage artifacts,
  entity experiment-log prune); AGENTS.md gains sub-package-sync section +
  governance; `governance/TASKS.md` board created. Evidence: `fe4b8d47` (docs
  rework) + the governance commit.
- **HUB-002** (done 2026-08-30) — **Sub-package sync driver (issue
  [#2](https://github.com/Exios66/mailroom-dev/issues/2))** —
  `scripts/sync_packages.py` (status / pull / push / snapshot over git
  subtree, clean-worktree guard) + baseline cursor
  `scripts/packages_sync.json`; all 9 packages verified at upstream tips
  (aligned per issue #2 as of 2026-08-30 19:06 CST). Evidence: `fe4b8d47`,
  issue #2 closed.
- **HUB-001** (done 2026-08-30) — **Monorepo import + workspace wiring** — 9
  packages under `packages/` via git subtree; one uv workspace (dev group +
  `[tool.uv.sources]`, published pins kept); monorepo-aware test repairs
  (monorepo detection, import-shadow `__init__.py` markers, pruned-asset skip
  guards, UTC-stamp and CWD anchoring fixes, notebook regeneration). Evidence:
  `ab4bf9e`, `10c5f8b4`, `fe4b8d47`; all 7 suites green — **2,331 passed /
  72 skipped, 0 failed**.

- **HUB-005** (done 2026-09-03) — **Release-train readiness — propagation
  sweep: all 10 feeder repositories synced to the monorepo content** — human
  directive ("ensure that all feeder repositories are properly synced to the
  content contained in the monorepo"). Scope note: propagation leg only — no
  tag/version bumps this sweep (pin bumps stay release-time). Landed: 9 of
  10 feeders via `sync_packages.py push --patch` (HUB-021 path; one
  fast-forward commit each on the upstream tip, cursor re-baselined per
  package in `scripts/packages_sync.json`): llm-mailroom-graph (3 files),
  llm-dojo-scoring (12), claims-data-eda (22), Enron-Evaluation-Environment
  (23), agent-mailroom (31), The-Mailroom (37), local-mailroom-sandbox (43),
  llm-entity-extraction (81), mailroom-corpus-eda (99) — 351 files total.
  llm-mailroom (88 files) was BLOCKED mid-sweep: `patch_push` copies
  worktree content per package prefix and a parallel session held
  uncommitted HUB-038 edits in exactly that subtree — recorded
  needs_attention rather than sweeping unfinished work upstream; the leg
  completed after HUB-038 committed (tree clean). llm-mailroom pushed via
  PLAIN `git subtree push` (history-carrying) — required because the
  pending delta included the HUB-023 fixture RENAME
  (`notebooks/fixtures/huggingface/docclass-merged.json` →
  `mailroom-corpus.json`) which patch-push cannot carry (no deletions) and
  which sat as the package's 1-path cursor gap; the plain push delivered
  the rename and CLEARED the gap. Final verification: `status` 10/10 in
  sync, upstream==synced everywhere, ZERO monorepo-ahead residue, ZERO
  cursor gaps. Shared-checkout discipline held: per-prefix dirt check
  before every push, targeted `git add` only. Hub tooling only — no
  package suite impact. Evidence: `65ff6b88` (9-feeder sweep + cursors),
  `9400f57a` (needs-attention record), this commit (closure).
