/* Mailroom Observatory app shell: views, live board, replay, inspector. */
const App = (() => {
  const STATIONS = [
    { key: "sorter", label: "Sorter", stages: ["inbox", "ingest", "classify", "retry_classify", "review_classify", "unknown"] },
    { key: "extract", label: "Extract", stages: ["extract", "retry_extract"] },
    { key: "judge", label: "Judge", stages: ["judge_verify", "arbiter"] },
    { key: "boss", label: "Boss", stages: ["boss"] },
    { key: "report", label: "Report", stages: ["report"] },
    { key: "archive", label: "Archive", stages: ["catalog", "archive"] },
    { key: "review", label: "Review", stages: ["review"] },
    { key: "done", label: "Completed", stages: ["archived", "failed"] },
  ];

  const SPAN_STAGE = {
    "ingest-document": "ingest",
    "classify-document": "classify",
    "judge-verify": "judge_verify",
    "arbitrate-verdict": "arbiter",
    "extract-fields": "extract",
    "adjudicate-conflict": "boss",
    "route-for-review": "review",
    "compile-report": "report",
    "write-catalog": "catalog",
    "archive-document": "archive",
  };

  const views = ["pipeline", "review", "history", "matters", "metrics"];
  let runs = [];
  let meta = null;
  let filter = "all";
  let replay = null;
  let replayTimers = [];
  let lastFocus = null;

  const $ = (id) => document.getElementById(id);
  const announce = (msg) => { $("announce").textContent = msg; };

  function stationFor(run) {
    const st = run && run.stage;
    if (run && run.needs_human && st !== "failed") return "review";
    for (const s of STATIONS) {
      if (s.stages.includes(st)) return s.key;
    }
    return "sorter";
  }

  function verdictClass(v) {
    if (v === "CORRECT") return "badge-ok";
    if (v === "PARTIAL") return "badge-warn";
    if (v === "MISS") return "badge-bad";
    return "badge-info";
  }

  function setSource(kind, text) {
    const el = $("source-status");
    el.className = `source-status is-${kind}`;
    el.textContent = text;
  }

  function showAlert(msg) {
    const el = $("alert-region");
    if (!msg) { el.hidden = true; el.textContent = ""; return; }
    el.hidden = false;
    el.textContent = msg;
  }

  function switchView(name) {
    if (!views.includes(name)) name = "pipeline";
    for (const v of views) {
      const sec = $(`view-${v}`);
      if (sec) sec.hidden = v !== name;
    }
    for (const a of document.querySelectorAll(".view-nav a")) {
      const on = a.dataset.view === name;
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    }
    if (location.hash.replace("#", "") !== name) {
      history.replaceState(null, "", `#${name}`);
    }
    if (name === "review") refreshReview();
    if (name === "history") refreshHistory();
    if (name === "matters") refreshMatters();
    if (name === "metrics") refreshMetrics();
  }

  function cardHTML(run, { replayId } = {}) {
    const title = Obs.esc(run.filename || run.trace_id);
    const replayCls = replayId && run.trace_id === replayId ? " is-replay" : "";
    const verdict = run.verdict
      ? `<span class="badge ${verdictClass(run.verdict)}">${Obs.esc(run.verdict)}</span>`
      : "";
    const stage = `<span class="badge badge-info">${Obs.esc((run.stage || "unknown").replaceAll("_", " "))}</span>`;
    return `<button type="button" class="card${replayCls}" data-trace="${Obs.esc(run.trace_id)}">
      <p class="card-title">${title}</p>
      <p class="card-meta">${Obs.esc((run.doc_type || "untyped").replaceAll("_", " "))}
        · ${Obs.fmt.conf(run.classification_confidence)} cls
        · ${Obs.fmt.conf(run.extraction_confidence)} ext</p>
      <p class="card-meta">${stage} ${verdict}</p>
    </button>`;
  }

  function matchesFilter(run) {
    if (filter === "all") return true;
    const tray = stationFor(run);
    if (filter === "review") return tray === "review";
    if (filter === "done") return tray === "done";
    if (filter === "inflight") return tray !== "done" && tray !== "review";
    return true;
  }

  function renderBoard() {
    const replayId = replay && replay.id;
    const shown = runs.filter(matchesFilter);
    const groups = Object.fromEntries(STATIONS.map((s) => [s.key, []]));
    for (const r of shown) groups[stationFor(r)].push(r);
    $("pipeline-board").innerHTML = STATIONS.map((s) => {
      const items = groups[s.key] || [];
      const body = items.length
        ? items.map((r) => cardHTML(r, { replayId })).join("")
        : `<p class="empty">Empty tray</p>`;
      return `<section class="tray" aria-labelledby="tray-${s.key}">
        <h3 id="tray-${s.key}">${s.label} <span class="tray-count">(${items.length})</span></h3>
        ${body}
      </section>`;
    }).join("");
    bindCards($("pipeline-board"));
    $("run-count").textContent = `${runs.length} run${runs.length === 1 ? "" : "s"} in the live window`;
  }

  function bindCards(root) {
    for (const btn of root.querySelectorAll("[data-trace]")) {
      btn.addEventListener("click", () => openInspect(btn.dataset.trace));
    }
  }

  function applyRuns(next) {
    runs = Array.isArray(next) ? next : [];
    renderBoard();
  }

  function table(caption, headers, rows) {
    if (!rows.length) return `<p class="empty">Nothing in this view.</p>`;
    return `<div class="table-wrap"><table class="data">
      <caption>${Obs.esc(caption)}</caption>
      <thead><tr>${headers.map((h) => `<th scope="col">${Obs.esc(h)}</th>`).join("")}</tr></thead>
      <tbody>${rows.join("")}</tbody>
    </table></div>`;
  }

  async function refreshReview() {
    const el = $("review-list");
    el.innerHTML = `<p class="empty">Loading review queue…</p>`;
    try {
      const data = await Obs.api.reviewQueue();
      const rows = (data.runs || []).map((r) => `<tr>
        <th scope="row"><button type="button" class="row-btn" data-trace="${Obs.esc(r.trace_id)}">${Obs.esc(r.filename || r.trace_id)}</button></th>
        <td>${Obs.esc((r.doc_type || "—").replaceAll("_", " "))}</td>
        <td>${Obs.esc(r.escalation_reason || r.review_decision || "—")}</td>
        <td>${Obs.fmt.conf(r.extraction_confidence)}</td>
        <td>${r.verdict ? `<span class="badge ${verdictClass(r.verdict)}">${Obs.esc(r.verdict)}</span>` : "—"}</td>
      </tr>`);
      el.innerHTML = table("Runs waiting on a human", ["Document", "Type", "Why", "Extract", "Verdict"], rows);
      bindCards(el);
    } catch (err) {
      el.innerHTML = `<p class="empty" role="alert">Review queue unavailable — ${Obs.esc(err.message)}</p>`;
    }
  }

  async function refreshHistory() {
    const el = $("history-list");
    el.innerHTML = `<p class="empty">Loading history…</p>`;
    try {
      const data = await Obs.api.traces(604800, 200);
      const rows = (data.runs || []).map((r) => `<tr>
        <th scope="row"><button type="button" class="row-btn" data-trace="${Obs.esc(r.trace_id)}">${Obs.esc(r.filename || r.trace_id)}</button></th>
        <td>${Obs.esc((r.stage || "—").replaceAll("_", " "))}</td>
        <td>${Obs.esc((r.doc_type || "—").replaceAll("_", " "))}</td>
        <td>${r.verdict ? `<span class="badge ${verdictClass(r.verdict)}">${Obs.esc(r.verdict)}</span>` : "—"}</td>
        <td>${Obs.fmt.when(r.updated_at || r.created_at)}</td>
        <td><button type="button" class="btn" data-replay="${Obs.esc(r.trace_id)}">Replay</button></td>
      </tr>`);
      el.innerHTML = table("Recent runs", ["Document", "Stage", "Type", "Verdict", "Updated", "Replay"], rows);
      bindCards(el);
      for (const btn of el.querySelectorAll("[data-replay]")) {
        btn.addEventListener("click", () => startReplay(btn.dataset.replay));
      }
    } catch (err) {
      el.innerHTML = `<p class="empty" role="alert">History unavailable — ${Obs.esc(err.message)}</p>`;
    }
  }

  async function refreshMatters() {
    const el = $("matters-list");
    el.innerHTML = `<p class="empty">Loading matters…</p>`;
    try {
      const data = await Obs.api.sessions(50);
      const sessions = data.sessions || [];
      if (!sessions.length) { el.innerHTML = `<p class="empty">No sessions in the recent window.</p>`; return; }
      el.innerHTML = sessions.map((s) => {
        const runsHtml = (s.runs || []).map((r) =>
          `<li><button type="button" class="row-btn" data-trace="${Obs.esc(r.trace_id)}">${Obs.esc(r.filename || r.trace_id)}</button>
           — ${Obs.esc((r.stage || "").replaceAll("_", " "))} ${r.verdict ? `· ${Obs.esc(r.verdict)}` : ""}</li>`).join("");
        return `<article class="matter">
          <h3>${Obs.esc(s.name || s.id || "matter")}</h3>
          <p>${s.trace_count || 0} traces · updated ${Obs.esc(Obs.fmt.when(s.updated_at))}</p>
          <ul>${runsHtml || "<li>No run detail on this session</li>"}</ul>
        </article>`;
      }).join("");
      bindCards(el);
    } catch (err) {
      el.innerHTML = `<p class="empty" role="alert">Matters unavailable — ${Obs.esc(err.message)}</p>`;
    }
  }

  function metricTile(label, value) {
    return `<div class="metric"><dt>${Obs.esc(label)}</dt><dd>${value}</dd></div>`;
  }

  async function refreshMetrics() {
    const el = $("metrics-grid");
    el.innerHTML = `<p class="empty">Loading metrics…</p>`;
    try {
      const m = await Obs.api.metrics(604800);
      const verdicts = Object.entries(m.verdict_counts || {});
      const docs = Object.entries(m.per_doc_type || {});
      const maxV = Math.max(1, ...verdicts.map(([, v]) => v));
      const maxD = Math.max(1, ...docs.map(([, v]) => v));
      const bars = (title, entries, max) => {
        if (!entries.length) return "";
        return `<div class="bar-list"><h3>${Obs.esc(title)}</h3>${entries.map(([k, v]) => {
          const label = (meta && meta.doc_classes && meta.doc_classes[k]) || k;
          const pct = Math.round((v / max) * 100);
          return `<div class="bar"><span>${Obs.esc(label)}</span>
            <span class="bar-track"><span class="bar-fill" style="width:${pct}%"></span></span>
            <span>${v}</span></div>`;
        }).join("")}</div>`;
      };
      el.innerHTML = metricTile("Documents", m.total_docs ?? "—")
        + metricTile("Archived", m.archived ?? "—")
        + metricTile("Review", m.review ?? "—")
        + metricTile("Failed", m.failed ?? "—")
        + metricTile("In flight", m.in_flight ?? "—")
        + metricTile("Total cost", Obs.fmt.cost(m.total_cost_usd))
        + metricTile("Tokens", Obs.fmt.tokens(m.total_tokens))
        + metricTile("LLM calls", Obs.fmt.tokens(m.llm_calls))
        + metricTile("Avg quality", m.avg_quality == null ? "—" : Number(m.avg_quality).toFixed(2))
        + bars("Judge verdicts", verdicts, maxV)
        + bars("Document types", docs, maxD);
    } catch (err) {
      el.innerHTML = `<p class="empty" role="alert">Metrics unavailable — ${Obs.esc(err.message)}</p>`;
    }
  }

  function scoreEntries(scores) {
    if (!scores) return [];
    if (Array.isArray(scores)) {
      return scores.filter((s) => s && s.name != null && s.value != null).map((s) => [s.name, s.value]);
    }
    if (typeof scores === "object") return Object.entries(scores).filter(([, v]) => v != null);
    return [];
  }

  function fmtScore(v) {
    if (v == null) return "—";
    if (typeof v === "object") {
      try { return JSON.stringify(v); } catch (e) { return String(v); }
    }
    return String(v);
  }

  async function openInspect(traceId) {
    lastFocus = document.activeElement;
    const dlg = $("inspect-dialog");
    $("inspect-title").textContent = "Loading trace…";
    $("inspect-body").innerHTML = `<p>Fetching ${Obs.esc(traceId)} from the live source…</p>`;
    dlg.showModal();
    try {
      const run = await Obs.api.run(traceId);
      if (run && run.error) throw new Error(run.error);
      $("inspect-title").textContent = run.filename || run.trace_id;
      const rows = [
        ["Trace", run.trace_id],
        ["Stage", run.stage],
        ["Phase", run.phase],
        ["Type", run.doc_type],
        ["Matter", run.session_id || run.matter_id],
        ["Classification", Obs.fmt.conf(run.classification_confidence)],
        ["Extraction", Obs.fmt.conf(run.extraction_confidence)],
        ["Verdict", run.verdict || "—"],
        ["Quality", run.quality == null ? "—" : Number(run.quality).toFixed(2)],
        ["Latency", Obs.fmt.latency(run.latency)],
        ["Tokens", Obs.fmt.tokens(run.total_tokens)],
        ["Cost", Obs.fmt.cost(run.cost_usd)],
        ["Created", Obs.fmt.when(run.created_at)],
      ];
      if (run.escalation_reason) rows.push(["Escalation", run.escalation_reason]);
      if (run.error_message) rows.push(["Error", run.error_message]);
      const spans = (run.spans || []).map((s) =>
        `<div class="span"><strong>${Obs.esc(s.name)}</strong> — ${Obs.esc(s.status || "")} · ${Obs.fmt.latency(s.latency)}
         ${s.error_message ? `<div>${Obs.esc(s.error_message)}</div>` : ""}</div>`).join("")
        || `<p class="empty">No span detail on this trace</p>`;
      const gens = (run.generations || []).map((g) =>
        `<div class="gen"><strong>${Obs.esc(g.model || g.agent || "generation")}</strong>
         · ${Obs.fmt.latency(g.latency)}
         ${g.usage_total_tokens != null ? ` · ${Obs.fmt.tokens(g.usage_total_tokens)} tok` : ""}
         ${g.cost_usd ? ` · ${Obs.fmt.cost(g.cost_usd)}` : ""}</div>`).join("")
        || `<p class="empty">No generations on this trace</p>`;
      const scores = scoreEntries(run.scores).map(([k, v]) =>
        `<div class="span"><strong>${Obs.esc(k)}</strong> · ${Obs.esc(fmtScore(v))}</div>`).join("")
        || `<p class="empty">No scores attached</p>`;
      $("inspect-body").innerHTML = `
        <dl class="kv">${rows.map(([k, v]) => `<dt>${Obs.esc(k)}</dt><dd>${Obs.esc(v == null ? "—" : v)}</dd>`).join("")}</dl>
        <h3>Node spans</h3><div class="stack">${spans}</div>
        <h3>LLM generations</h3><div class="stack">${gens}</div>
        <h3>Scores</h3><div class="stack">${scores}</div>`;
    } catch (err) {
      $("inspect-title").textContent = "Trace unavailable";
      $("inspect-body").innerHTML = `<p role="alert">${Obs.esc(err.message)}</p>`;
    }
  }

  function closeInspect() {
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function clearReplayTimers() {
    for (const t of replayTimers) clearTimeout(t);
    replayTimers = [];
  }

  function setReplayButtons(on) {
    $("replay-play").disabled = !on;
    $("replay-step").disabled = !on;
    $("replay-stop").disabled = !on;
  }

  function sequenceFrom(run) {
    const spans = (run.spans || [])
      .filter((s) => s && SPAN_STAGE[s.name])
      .slice()
      .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
    const steps = [];
    let prev = null;
    for (const s of spans) {
      let st = SPAN_STAGE[s.name];
      if (prev && st === prev) {
        if (st === "classify") st = "retry_classify";
        else if (st === "extract") st = "retry_extract";
        if (steps.length && steps[steps.length - 1].stage === st) continue;
      }
      prev = SPAN_STAGE[s.name];
      const d = s.latency != null && s.latency > 0
        ? Math.min(Math.max(s.latency * 1000, 250), 4000)
        : 700;
      steps.push({ stage: st, delay: d });
    }
    if (!steps.length) {
      const path = run.routing_path && run.routing_path.length
        ? run.routing_path
        : ["classify", "extract", "archived"];
      return path.map((stage) => ({ stage, delay: 700 }));
    }
    return steps;
  }

  function applyReplayStage(stage) {
    if (!replay) return;
    replay.stage = stage;
    const idx = runs.findIndex((r) => r.trace_id === replay.id);
    const overlay = {
      ...(idx >= 0 ? runs[idx] : { trace_id: replay.id, filename: replay.filename, doc_type: replay.doc_type }),
      stage,
      needs_human: stage === "review",
    };
    if (idx >= 0) runs[idx] = overlay;
    else runs = [overlay, ...runs];
    renderBoard();
    $("replay-status").textContent = `Replay · ${replay.filename} · ${stage.replaceAll("_", " ")}`;
    announce(`Replay moved to ${stage.replaceAll("_", " ")}`);
  }

  function reducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  async function startReplay(traceId) {
    clearReplayTimers();
    $("replay-status").textContent = "Loading replay…";
    try {
      const run = await Obs.api.run(traceId);
      if (run && run.error) throw new Error(run.error);
      replay = {
        id: run.trace_id,
        filename: run.filename || run.trace_id,
        doc_type: run.doc_type,
        steps: sequenceFrom(run),
        index: 0,
        playing: false,
      };
      setReplayButtons(true);
      switchView("pipeline");
      applyReplayStage(replay.steps[0] ? replay.steps[0].stage : "classify");
      if (!reducedMotion()) playReplay();
    } catch (err) {
      $("replay-status").textContent = `Replay failed — ${err.message}`;
      showAlert(`Replay failed — ${err.message}`);
    }
  }

  function playReplay() {
    if (!replay || !replay.steps.length) return;
    replay.playing = true;
    $("replay-play").textContent = "Pause replay";
    scheduleReplay();
  }

  function pauseReplay() {
    if (!replay) return;
    replay.playing = false;
    clearReplayTimers();
    $("replay-play").textContent = "Play replay";
  }

  function scheduleReplay() {
    clearReplayTimers();
    if (!replay || !replay.playing) return;
    const next = replay.index + 1;
    if (next >= replay.steps.length) {
      finishReplay();
      return;
    }
    const delay = reducedMotion() ? 0 : replay.steps[replay.index].delay;
    replayTimers.push(setTimeout(() => {
      replay.index = next;
      applyReplayStage(replay.steps[next].stage);
      scheduleReplay();
    }, delay));
  }

  function stepReplay() {
    if (!replay) return;
    pauseReplay();
    const next = Math.min(replay.index + 1, replay.steps.length - 1);
    replay.index = next;
    applyReplayStage(replay.steps[next].stage);
    if (next === replay.steps.length - 1) finishReplay();
  }

  function finishReplay() {
    pauseReplay();
    if (replay) applyReplayStage("archived");
    $("replay-status").textContent = replay
      ? `Replay complete — ${replay.filename}`
      : "Replay complete";
    announce("Replay complete");
    setReplayButtons(true);
    $("replay-play").textContent = "Play replay";
  }

  function stopReplay() {
    pauseReplay();
    replay = null;
    setReplayButtons(false);
    $("replay-play").textContent = "Play replay";
    $("replay-status").textContent = "No replay loaded";
    refreshTraces();
  }

  async function refreshTraces() {
    try {
      const data = await Obs.api.traces(604800, 200);
      applyRuns(data.runs || []);
      showAlert("");
    } catch (err) {
      showAlert(`Could not load traces — ${err.message}`);
    }
  }

  async function checkHealth() {
    try {
      const h = await Obs.api.health();
      const ok = !!(h.ok ?? h.langfuse);
      if (ok) {
        setSource("live", `Live · source ${h.source || "langfuse"}`);
        if (!meta) {
          try { meta = await Obs.api.meta(); } catch (e) { /* non-fatal */ }
        }
        return true;
      }
      setSource("down", "Trace source reported offline");
      return false;
    } catch (err) {
      setSource("down", `No live connection — ${err.message}`);
      showAlert("The Observatory needs the Mailroom API (Langfuse-backed) on this host. This is not the GitHub Pages snapshot.");
      return false;
    }
  }

  function onMessage(msg) {
    if (msg.type === "status") {
      if (msg.connected) setSource("live", "Live · WebSocket connected");
      else setSource("stale", "Socket disconnected — reconnecting");
    } else if (msg.type === "snapshot") {
      if (replay && replay.playing) return;
      applyRuns(msg.runs || []);
      if (msg.stale) setSource("stale", "Live · last snapshot is stale");
    }
  }

  function tick() {
    const d = new Date();
    $("clock").textContent = d.toLocaleTimeString(undefined, { hour12: false });
  }

  function boot() {
    tick();
    setInterval(tick, 1000);

    for (const a of document.querySelectorAll(".view-nav a")) {
      a.addEventListener("click", (ev) => {
        ev.preventDefault();
        switchView(a.dataset.view);
      });
    }
    for (const radio of document.querySelectorAll("input[name=pipe-filter]")) {
      radio.addEventListener("change", () => {
        if (radio.checked) { filter = radio.value; renderBoard(); }
      });
    }
    $("replay-play").addEventListener("click", () => {
      if (!replay) return;
      if (replay.playing) pauseReplay();
      else playReplay();
    });
    $("replay-step").addEventListener("click", stepReplay);
    $("replay-stop").addEventListener("click", stopReplay);
    $("inspect-dialog").addEventListener("close", closeInspect);

    window.addEventListener("hashchange", () => {
      switchView(location.hash.replace("#", "") || "pipeline");
    });

    document.addEventListener("keydown", (ev) => {
      if (ev.target && ["INPUT", "TEXTAREA", "SELECT"].includes(ev.target.tagName)) return;
      const map = { "1": "pipeline", "2": "review", "3": "history", "4": "matters", "5": "metrics" };
      if (map[ev.key]) switchView(map[ev.key]);
    });

    switchView(location.hash.replace("#", "") || "pipeline");

    checkHealth().then((ok) => {
      if (!ok) return;
      refreshTraces();
      Obs.connectWS(onMessage);
    });
    setInterval(checkHealth, 10000);
  }

  document.addEventListener("DOMContentLoaded", boot);
  return { openInspect, startReplay, switchView };
})();
