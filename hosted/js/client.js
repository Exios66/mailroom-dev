/* Mailroom Observatory client — same-origin API + WebSocket.
 * Langfuse (or the configured source) remains the only display source. */
const Obs = (() => {
  function dbg(kind, payload) {
    try {
      if (window.ObservatoryDebug) window.ObservatoryDebug.record(kind, payload);
    } catch (_e) { /* debug module optional */ }
  }

  async function get(path) {
    const res = await fetch(path, { headers: { Accept: "application/json" } });
    if (!res.ok) {
      let detail = "";
      try {
        const body = await res.json();
        detail = body && body.detail ? ` — ${body.detail}` : "";
      } catch (e) { /* non-JSON error body */ }
      const err = new Error(`HTTP ${res.status} ${path}${detail}`);
      dbg("fetch-error", { url: path, status: res.status, message: err.message, where: "Obs.get" });
      throw err;
    }
    return res.json();
  }

  const api = {
    health: () => get("/api/health"),
    meta: () => get("/api/meta"),
    traces: (since = 604800, limit = 200) => get(`/api/traces?since=${since}&limit=${limit}`),
    run: (id) => get(`/api/traces/${encodeURIComponent(id)}`),
    metrics: (since = 604800) => get(`/api/metrics?since=${since}`),
    sessions: (limit = 50) => get(`/api/sessions?limit=${limit}`),
    reviewQueue: (since = 604800) => get(`/api/review-queue?since=${since}`),
    pipeline: () => get("/api/pipeline"),
  };

  const fmt = {
    cost: (v) => {
      if (v == null) return "—";
      const n = Number(v);
      if (n !== 0 && Math.abs(n) < 0.01) return `$${n.toFixed(4)}`;
      return `$${n.toFixed(2)}`;
    },
    tokens: (v) => (v == null ? "—" : Number(v).toLocaleString("en-US")),
    latency: (v) => {
      if (v == null) return "—";
      const s = Number(v);
      if (s < 60) return `${s.toFixed(1)}s`;
      return `${Math.floor(s / 60)}m ${(s % 60).toFixed(0)}s`;
    },
    conf: (v) => (v == null ? "—" : `${(Number(v) * 100).toFixed(0)}%`),
    when: (iso) => {
      if (!iso) return "—";
      const d = new Date(iso);
      return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString(undefined, { hour12: false });
    },
    short: (s, n = 42) => {
      if (s == null) return "—";
      s = String(s);
      return s.length > n ? `${s.slice(0, n - 1)}…` : s;
    },
  };

  const esc = (s) => {
    if (s == null) return "";
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  };

  function wsURL() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://${location.host}/ws`;
  }

  let lastWs = null;

  function wsState() {
    if (!lastWs) return "closed";
    const s = lastWs.readyState;
    if (s === 0) return "connecting";
    if (s === 1) return "open";
    if (s === 2) return "closing";
    return "closed";
  }

  function connectWS(onMessage) {
    let ws = null;
    let retry = 0;
    let timer = null;
    function open() {
      clearTimeout(timer);
      try { if (ws) ws.close(); } catch (e) { /* noop */ }
      ws = new WebSocket(wsURL());
      lastWs = ws;
      dbg("ws", { phase: "connecting", url: wsURL() });
      ws.onopen = () => {
        retry = 0;
        dbg("ws", { phase: "open" });
        onMessage({ type: "status", connected: true });
      };
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          const n = msg && msg.runs ? msg.runs.length : undefined;
          dbg("ws", { phase: "message", type: msg && msg.type, runs: n, stale: !!(msg && msg.stale) });
          onMessage(msg);
        } catch (e) {
          dbg("ws-error", { phase: "bad-json", message: e && e.message ? e.message : String(e) });
        }
      };
      ws.onclose = (ev) => {
        dbg("ws-error", { phase: "close", code: ev.code, reason: ev.reason || "", wasClean: ev.wasClean });
        onMessage({ type: "status", connected: false });
        const delay = Math.min(30000, 1000 * 2 ** retry++);
        timer = setTimeout(open, delay);
      };
      ws.onerror = () => {
        dbg("ws-error", { phase: "error", readyState: ws && ws.readyState });
        try { ws.close(); } catch (e) { /* noop */ }
      };
    }
    open();
    return {
      close: () => { clearTimeout(timer); try { ws && ws.close(); } catch (e) { /* noop */ } },
      state: wsState,
    };
  }

  return { api, fmt, esc, connectWS, wsState };
})();
