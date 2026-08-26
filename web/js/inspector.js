/* The-Mailroom inspector: drill-down overlay for one trace (full run detail
 * from /api/traces/{id}: spans, generations, scores). */

const Inspector = (() => {
  const overlay = document.getElementById("inspector");
  const titleEl = document.getElementById("insp-title");
  const bodyEl = document.getElementById("insp-body");

  function stageChip(stage) {
    const bucket = {
      inbox: "stage-intake",
      ingest: "stage-intake",
      classify: "stage-intake",
      retry_classify: "stage-intake",
      review_classify: "stage-intake",
      extract: "stage-extract",
      retry_extract: "stage-extract",
      judge_verify: "stage-judge",
      arbiter: "stage-judge",
      boss: "stage-extract",
      report: "stage-report",
      catalog: "stage-report",
      archive: "stage-report",
      review: "stage-review",
      archived: "stage-archived",
      failed: "stage-failed",
    };
    return `<span class="chip ${bucket[stage] || ""}">${Mailroom.esc((stage || "unknown").toUpperCase())}</span>`;
  }

  function docLabel(docType) {
    if (!docType) return null;
    const classes = (Mailroom.meta && Mailroom.meta.doc_classes) || {};
    return classes[docType] || docType;
  }

  function obsTypeChip(t) {
    if (!t) return "";
    const kind = String(t).toUpperCase();
    const cls = {
      CHAIN: "obs-chain",
      AGENT: "obs-agent",
      EVALUATOR: "obs-evaluator",
      RETRIEVER: "obs-retriever",
      SPAN: "obs-span",
      EVENT: "obs-span",
      GENERATION: "obs-generation",
    }[kind] || "obs-span";
    return `<span class="chip ${cls}">${Mailroom.esc(kind)}</span>`;
  }

  function spanStatusDot(status) {
    const cls = status === "SUCCESS" ? "ok" : status === "ERROR" ? "bad" : status === "PENDING" ? "warn" : "idle";
    return `<span class="dot ${cls}"></span>`;
  }

  function fmtScore(v) {
    if (v == null) return "—";
    if (typeof v === "object") {
      try { return JSON.stringify(v); } catch (e) { return String(v); }
    }
    return String(v);
  }

  function scoreEntries(scores) {
    if (!scores) return [];
    if (Array.isArray(scores)) {
      return scores
        .filter((s) => s && s.name != null && s.value != null)
        .map((s) => [s.name, s.value]);
    }
    if (typeof scores === "object") {
      return Object.entries(scores).filter(([, v]) => v != null);
    }
    return [];
  }

  function render(run) {
    const title = run.filename || run.trace_id;
    titleEl.textContent = `${Mailroom.fmt.short(title, 60)} — ${run.stage || "unknown"}`;

    const doc = docLabel(run.doc_type);
    const parts = [];
    parts.push(stageChip(run.stage));
    parts.push(`<span class="chip">PHASE ${Mailroom.esc((run.phase || "").toUpperCase())}</span>`);
    if (doc) parts.push(`<span class="chip">${Mailroom.esc(doc)}</span>`);
    if (run.environment) parts.push(`<span class="chip">ENV ${Mailroom.esc(run.environment)}</span>`);
    if (run.release) parts.push(`<span class="chip">REL ${Mailroom.esc(run.release)}</span>`);
    if (run.user_id) parts.push(`<span class="chip">USER ${Mailroom.esc(run.user_id)}</span>`);
    if (run.attempt != null) parts.push(`<span class="chip">ATTEMPT ${run.attempt}</span>`);
    if (run.retried) parts.push(`<span class="chip">RETRIED</span>`);

    let verdict = "—";
    let vcls = "";
    if (run.verdict) {
      verdict = run.verdict;
      vcls = `verdict-${run.verdict}`;
    }
    const verdictChip = run.verdict
      ? `<span class="chip ${vcls}">VERDICT ${Mailroom.esc(run.verdict)}</span>`
      : `<span class="chip">VERDICT —</span>`;
    const quality = run.quality != null
      ? `<span class="chip">QUALITY ${Number(run.quality).toFixed(2)}</span>`
      : "";

    const rows = [
      ["trace id", run.trace_id],
      ["session / matter", run.session_id || run.matter_id || "—"],
      ["user", run.user_id || "—"],
      ["release", run.release || "—"],
      ["filename", run.filename || "—"],
      ["classification conf.", Mailroom.fmt.conf(run.classification_confidence)],
      ["extraction conf.", Mailroom.fmt.conf(run.extraction_confidence)],
      ["latency", Mailroom.fmt.latency(run.latency)],
      ["llm calls", run.llm_call_count != null ? String(run.llm_call_count) : "—"],
      ["tokens", Mailroom.fmt.tokens(run.total_tokens)],
      ["cost", Mailroom.fmt.cost(run.cost_usd)],
      ["created", Mailroom.fmt.dateTime(run.created_at)],
    ];
    if (run.review_decision) rows.push(["review decision", run.review_decision]);
    if (run.escalation_reason) rows.push(["escalation", run.escalation_reason]);

    const kv = rows.map(([k, v]) => `<div class="k">${Mailroom.esc(k)}</div><div class="v">${Mailroom.esc(v)}</div>`).join("");

    let errorBlock = "";
    if (run.error_message) {
      errorBlock = `<div class="insp-error">ERROR — ${Mailroom.esc(run.error_message)}</div>`;
    }

    const spans = Array.isArray(run.spans) ? run.spans : [];
    const spansHtml = spans.length
      ? spans.map((s) => {
          const err = s.error_message ? `<div class="span-meta">${Mailroom.esc(s.error_message)}</div>` : "";
          const typeChip = obsTypeChip(s.observation_type);
          const rootMark = s.is_root ? `<span class="chip obs-chain">ROOT</span>` : "";
          return `<div class="span-row ${s.status === "ERROR" ? "span-err" : ""} ${s.is_root ? "span-root" : ""}">
            ${spanStatusDot(s.status)}
            <span class="span-name">${Mailroom.esc(s.name)}</span>
            ${typeChip}${rootMark}
            <div class="span-meta">${Mailroom.esc(s.status || "")} · ${Mailroom.fmt.latency(s.latency)}</div>
            ${err}
          </div>`;
        }).join("")
      : `<div class="c-dim" style="color:var(--gray-dim)">no span detail on this trace</div>`;

    const gens = Array.isArray(run.generations) ? run.generations : [];
    const gensHtml = gens.length
      ? gens.map((g) => `<div class="gen-row">
          <div class="gen-model">${Mailroom.esc(g.name || g.model || g.agent || "generation")} ${obsTypeChip(g.observation_type || "GENERATION")}</div>
          <div class="gen-meta">
            ${Mailroom.esc(g.agent || "")}${g.agent ? " · " : ""}
            ${Mailroom.fmt.latency(g.latency)}
            ${g.usage_total_tokens != null ? ` · ${Mailroom.fmt.tokens(g.usage_total_tokens)} tok` : ""}
            ${g.usage_input_tokens != null ? ` (${Mailroom.fmt.tokens(g.usage_input_tokens)} in / ${Mailroom.fmt.tokens(g.usage_output_tokens)} out)` : ""}
            ${g.cost_usd ? ` · ${Mailroom.fmt.cost(g.cost_usd)}` : ""}
            ${g.prompt_version ? ` · v${Mailroom.esc(g.prompt_version)}` : ""}
          </div>
        </div>`).join("")
      : `<div style="color:var(--gray-dim)">no generations on this trace</div>`;

    const scores = scoreEntries(run.scores);
    const scoresHtml = scores.length
      ? scores.map(([k, v]) => `<div class="score-row">
          <span class="score-name">${Mailroom.esc(k)}</span>
          <span class="score-val">${Mailroom.esc(fmtScore(v))}</span>
        </div>`).join("")
      : `<div style="color:var(--gray-dim)">no scores attached to this trace</div>`;

    bodyEl.innerHTML = `
      <div class="insp-chips">${parts.join("")} ${verdictChip} ${quality}</div>
      <div class="insp-section">
        <h3>RUN</h3>
        <div class="insp-kv">${kv}</div>
      </div>
      ${errorBlock}
      <div class="insp-section">
        <h3>OBSERVATIONS</h3>
        <div class="insp-spans">${spansHtml}</div>
      </div>
      <div class="insp-section">
        <h3>LLM GENERATIONS</h3>
        ${gensHtml}
      </div>
      <div class="insp-section">
        <h3>SCORES</h3>
        ${scoresHtml}
      </div>`;
  }

  function open(traceId) {
    titleEl.textContent = "LOADING TRACE…";
    bodyEl.innerHTML = `<div style="color:var(--gray-dim)">fetching ${Mailroom.esc(traceId)} …</div>`;
    overlay.hidden = false;
    Mailroom.api.run(traceId)
      .then((run) => {
        if (run && run.error) throw new Error(run.error);
        render(run);
      })
      .catch((err) => {
        titleEl.textContent = "TRACE UNAVAILABLE";
        bodyEl.innerHTML = `<div class="insp-error">${Mailroom.esc(err.message || String(err))}</div>`;
      });
  }

  function close() {
    overlay.hidden = true;
  }

  document.getElementById("insp-close").addEventListener("click", close);
  overlay.addEventListener("click", (ev) => {
    if (ev.target === overlay) close();
  });
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && !overlay.hidden) close();
  });

  return { open, close };
})();
