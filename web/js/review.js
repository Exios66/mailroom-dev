/* The-Mailroom review queue: runs waiting on a human (needs_human). */

const ReviewView = (() => {
  const listEl = document.getElementById("review-queue");

  function chip(run) {
    if (run.stage === "review") return `<span class="chip stage-review">REVIEW</span>`;
    if (run.stage === "failed") return `<span class="chip stage-failed">FAILED</span>`;
    return `<span class="chip">${Mailroom.esc((run.stage || "unknown").toUpperCase())}</span>`;
  }

  function verdictChip(run) {
    if (!run.verdict) return "";
    return `<span class="chip verdict-${Mailroom.esc(run.verdict)}">${Mailroom.esc(run.verdict)}</span>`;
  }

  function render(runs) {
    if (!runs.length) {
      listEl.innerHTML = `<div class="hint mono">REVIEW SIDING EMPTY — NO RUNS WAITING ON A HUMAN</div>`;
      return;
    }
    listEl.innerHTML = runs
      .map(
        (r) => `<div class="session-card run-row-solo" data-trace="${Mailroom.esc(r.trace_id)}">
        <div class="session-head">
          <span class="ses-id">${Mailroom.esc(r.filename || r.trace_id)}</span>
          ${chip(r)}
          ${verdictChip(r)}
          <span class="ses-count">${Mailroom.fmt.time(r.created_at)}</span>
        </div>
        <div class="session-runs" style="padding:8px 10px">
          <div style="color:var(--paper-dim)">doc: <span style="color:var(--paper)">${Mailroom.esc(r.doc_type || "—")}</span></div>
          ${
            r.escalation_reason
              ? `<div style="color:var(--amber);margin-top:4px">why: ${Mailroom.esc(r.escalation_reason)}</div>`
              : ""
          }
          ${
            r.error_message
              ? `<div style="color:var(--red-light);margin-top:4px">error: ${Mailroom.esc(r.error_message)}</div>`
              : ""
          }
          <div style="color:var(--gray-dim);margin-top:4px">
            cls ${Mailroom.fmt.conf(r.classification_confidence)} · ext ${Mailroom.fmt.conf(
              r.extraction_confidence,
            )} · ${r.llm_call_count ?? 0} calls · ${Mailroom.fmt.tokens(r.total_tokens)} tok · ${Mailroom.fmt.cost(r.cost_usd)}
          </div>
        </div>
      </div>`,
      )
      .join("");
    for (const card of listEl.querySelectorAll(".session-card")) {
      card.addEventListener("click", () => {
        Inspector.open(card.dataset.trace);
      });
    }
  }

  async function refresh() {
    listEl.innerHTML = `<div class="hint mono">LOADING REVIEW QUEUE FROM LANGFUSE…</div>`;
    try {
      const data = await Mailroom.api.reviewQueue();
      render(data.runs || []);
      return data;
    } catch (err) {
      listEl.innerHTML = `<div class="insp-error">review queue unavailable — ${Mailroom.esc(err.message || String(err))}</div>`;
      throw err;
    }
  }

  return { refresh };
})();
