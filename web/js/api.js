/* The-Mailroom API client: Langfuse-backed fetch endpoints + WebSocket
 * with reconnect. All display data flows through this module; nothing is
 * fabricated client-side.
 *
 * GH Pages edition additions:
 *  - Configurable API base URL: ?api=<url> (persisted to localStorage)
 *    -> lets the static site talk to any reachable Mailroom API server,
 *       including one running locally next to Phoenix.
 *  - Static snapshot mode: when no live API answers, bundled JSON under
 *    ./data/ (built by scripts/export_snapshot.py) is served instead.
 *  - Debug capture ring buffer exposed to agents at
 *    window.__MAILROOM_DEBUG__ ({ dump(), export(), clear(), setVerbose() }).
 */

const Mailroom = (() => {
  const qs = new URLSearchParams(location.search);

  // ---- API base resolution ---------------------------------------------
  // ?api= wins and persists so a Pages visitor only configures once.
  // ?api= (empty) CLEARS a stale persisted base — previously qs.get("api")
  // was falsy for "" so localStorage could never be unset, and a dead
  // localhost base blanked the GH Pages snapshot fallback.
  let BASE = "";
  if (qs.has("api")) {
    BASE = (qs.get("api") || "").trim().replace(/\/+$/, "");
    try { localStorage.setItem("mailroom.api", BASE); } catch (e) { /* private mode */ }
  } else {
    BASE = (localStorage.getItem("mailroom.api") || "").trim().replace(/\/+$/, "");
  }
  const url = (path) => {
    if (!BASE) return path;
    const p = path.startsWith("/") ? path : `/${path}`;
    return `${BASE}${p}`;
  };
  // Bundled snapshots always live next to the SPA (GH Pages docs/ or a local
  // export). Never prefix them with the live API BASE.
  const snapUrl = (path) => String(path).replace(/^\/+/, "");
  const safeId = (id) => String(id).replace(/[^A-Za-z0-9._-]/g, "_");

  // ---- debug capture -----------------------------------------------------
  const MAX_DEBUG_EVENTS = 500;
  const dbgEvents = [];
  let debugVerbose = qs.has("debug") || localStorage.getItem("mailroom.debug") === "1";

  function capture(kind, fields) {
    dbgEvents.push({ t: new Date().toISOString(), kind, ...fields });
    while (dbgEvents.length > MAX_DEBUG_EVENTS) dbgEvents.shift();
    if (debugVerbose) console.debug(`[mailroom:${kind}]`, fields);
  }
  function dumpDebug(pretty = true) {
    const payload = {
      generated_at: new Date().toISOString(),
      location: location.href,
      api_base: BASE,
      static_mode: staticMode,
      debug_verbose: debugVerbose,
      user_agent: navigator.userAgent,
      events: dbgEvents.slice(),
    };
    return pretty ? JSON.stringify(payload, null, 2) : JSON.stringify(payload);
  }
  function exportDebug() {
    const text = dumpDebug();
    try { navigator.clipboard.writeText(text); } catch (e) { /* clipboard denied */ }
    const blob = new Blob([text], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "mailroom-debug.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
    capture("debug-export", {});
  }

  window.__MAILROOM_DEBUG__ = {
    events: dbgEvents,
    dump: dumpDebug,
    export: exportDebug,
    clear: () => { dbgEvents.length = 0; },
    setVerbose: (v) => {
      debugVerbose = !!v;
      try { localStorage.setItem("mailroom.debug", v ? "1" : "0"); } catch (e) {}
    },
    get verbose() { return debugVerbose; },
    get apiBase() { return BASE; },
  };

  // ---- static snapshot mode ----------------------------------------------
  let staticMode = false;
  const snapCache = new Map();

  async function enableStaticMode() {
    if (staticMode) return true;
    try {
      const res = await fetch(snapUrl("data/meta.json"), { cache: "no-store" });
      if (!res.ok) return false;
      snapCache.set("meta", { data: await res.json(), fetched: Date.now() });
      staticMode = true;
      capture("static-mode", { enabled: true });
      return true;
    } catch (e) {
      capture("static-mode", { enabled: false, error: String(e) });
      return false;
    }
  }

  async function snap(name) {
    if (snapCache.has(name)) {
      const hit = snapCache.get(name);
      // Static files can be refreshed by a re-deploy or local exporter run —
      // serve from memory briefly, then re-fetch.
      if (Date.now() - hit.fetched < 30000) return hit.data;
    }
    const t0 = performance.now();
    const path = snapUrl(`data/${name}.json`);
    const res = await fetch(path, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status} data/${name}.json`);
    const data = await res.json();
    snapCache.set(name, { data, fetched: Date.now() });
    capture("fetch", { url: path, status: res.status, ms: Math.round(performance.now() - t0), mode: "static" });
    return data;
  }

  async function snapRun(id) {
    // Must match scripts/export_snapshot.py _safe_id, NOT encodeURIComponent
    // (a slug with ':' would 404 the sanitized filename on Pages).
    return snap(`runs/${safeId(id)}`);
  }

  // ---- remote API calls ---------------------------------------------------
  async function get(path) {
    const t0 = performance.now();
    let res;
    try {
      res = await fetch(url(path), { headers: { "Accept": "application/json" } });
    } catch (err) {
      capture("fetch", { url: path, error: String(err), ms: Math.round(performance.now() - t0) });
      throw err;
    }
    capture("fetch", { url: path, status: res.status, ms: Math.round(performance.now() - t0) });
    if (!res.ok) {
      // V-18: the server's 503/500 bodies carry a `detail` the SPA silently
      // discarded before — surface it in the error so screens can show why.
      let detail = "";
      try {
        const body = await res.json();
        detail = body && body.detail ? ` — ${body.detail}` : "";
      } catch (e) { /* non-JSON error body */ }
      throw new Error(`HTTP ${res.status} ${path}${detail}`);
    }
    return res.json();
  }

  const remote = {
    health: () => get("/api/health"),
    meta: () => get("/api/meta"),
    traces: (since = 1800, limit = 200) => get(`/api/traces?since=${since}&limit=${limit}`),
    run: (id) => get(`/api/traces/${encodeURIComponent(id)}`),
    metrics: (since = 3600) => get(`/api/metrics?since=${since}`),
    sessions: (limit = 50) => get(`/api/sessions?limit=${limit}`),
    reviewQueue: (since = 604800) => get(`/api/review-queue?since=${since}`),
  };

  const snapshots = {
    health: async () => ({
      ok: true, langfuse: true, mode: "snapshot", source: "snapshot",
      generated_at: (await snap("meta")).generated_at,
    }),
    meta: () => snap("meta"),
    traces: () => snap("traces"),
    run: (id) => snapRun(id),
    metrics: () => snap("metrics"),
    sessions: () => snap("sessions"),
    reviewQueue: () => snap("review-queue"),
  };

  function dispatch(name, ...args) {
    return staticMode ? snapshots[name](...args) : remote[name](...args);
  }

  const api = {
    health: (...a) => dispatch("health", ...a),
    meta: (...a) => dispatch("meta", ...a),
    traces: (...a) => dispatch("traces", ...a),
    run: (...a) => dispatch("run", ...a),
    metrics: (...a) => dispatch("metrics", ...a),
    sessions: (...a) => dispatch("sessions", ...a),
    reviewQueue: (...a) => dispatch("reviewQueue", ...a),
  };

  const fmt = {
    // Pipeline costs are sub-cent at qwen/deepseek pricing — 2 decimals
    // rendered every run as "$0.00". Show 4 decimals below a cent.
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
    time: (iso) => {
      if (!iso) return "—";
      const d = new Date(iso);
      return isNaN(d) ? "—" : d.toLocaleTimeString("en-US", { hour12: false });
    },
    dateTime: (iso) => {
      if (!iso) return "—";
      const d = new Date(iso);
      return isNaN(d) ? "—" : d.toLocaleString("en-US", { month: "short", day: "2-digit", hour12: false });
    },
    short: (s, n = 26) => {
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

  let ws = null;
  let wsTimer = null;
  let wsRetry = 0;
  let connected = false;
  let errTimer = null;

  // V-18: one global error banner. Every silent `.catch(() => {})` across the
  // SPA is routed here, plus window.onerror for unhandled exceptions.
  function showError(msg) {
    const el = document.getElementById("error-banner");
    const text = msg && msg.message ? msg.message : String(msg || "unknown error");
    capture("error", { message: text });
    if (!el) {
      console.error(`[mailroom] ${text}`);
      return;
    }
    el.textContent = `ERROR — ${text}`;
    el.hidden = false;
    clearTimeout(errTimer);
    errTimer = setTimeout(() => { el.hidden = true; }, 8000);
  }

  window.addEventListener("error", (ev) => {
    const msg = ev.message || "unhandled script error";
    // Browser-noise that used to paint the error banner on an otherwise
    // healthy floor (ResizeObserver loop, cross-origin "Script error.").
    if (/ResizeObserver|Script error\.?$/i.test(msg)) return;
    showError(msg);
  });
  window.addEventListener("unhandledrejection", (ev) => {
    if (ev && ev.reason) showError(ev.reason);
  });

  function wsURL() {
    if (BASE) {
      const u = new URL(BASE, location.href);
      const proto = u.protocol === "https:" ? "wss" : "ws";
      return `${proto}//${u.host}/ws`;
    }
    const proto = location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://${location.host}/ws`;
  }

  function connectWS(onMessage) {
    clearTimeout(wsTimer);
    try {
      if (ws) ws.close();
    } catch (e) { /* noop */ }
    capture("ws", { event: "connect-attempt", url: wsURL() });
    ws = new WebSocket(wsURL());
    ws.onopen = () => {
      wsRetry = 0;
      connected = true;
      capture("ws", { event: "open" });
      onMessage({ type: "status", connected: true });
    };
    ws.onmessage = (ev) => {
      capture("ws-frame", { bytes: ev.data ? ev.data.length : 0 });
      try {
        const parsed = JSON.parse(ev.data);
        onMessage(parsed);
      } catch (e) {
        // V-18: non-JSON WS frames were dropped silently — log them so protocol
        // drift from the server is visible instead of an unexplained stall.
        console.error(`[mailroom] non-JSON WS frame dropped: ${String(ev.data).slice(0, 200)}`);
        capture("ws-frame", { event: "non-json-dropped" });
      }
    };
    ws.onclose = () => {
      connected = false;
      capture("ws", { event: "close", retry: wsRetry });
      onMessage({ type: "status", connected: false });
      const delay = Math.min(30000, 1000 * 2 ** wsRetry++);
      wsTimer = setTimeout(() => connectWS(onMessage), delay);
    };
    ws.onerror = () => {
      try { ws.close(); } catch (e) { /* noop */ }
    };
  }

  function envFromTags(tags) {
    if (!Array.isArray(tags)) return null;
    const known = new Set(["live", "pilot", "dev", "test", "demo", "prod", "staging"]);
    for (const t of tags) if (known.has(t)) return t;
    return null;
  }

  const exports = {
    api, fmt, esc, connectWS, envFromTags, showError,
    get wsConnected() { return connected; },
    get staticMode() { return staticMode; },
    enableStaticMode,
    get apiBase() { return BASE; },
    get debugVerbose() { return debugVerbose; },
    capture,
  };
  // Publish to window explicitly: a top-level `const` does NOT attach to
  // window, so window.Mailroom stayed undefined and any code touching it
  // (metrics.js demo-mode flag set by main.js) crashed in live mode.
  window.Mailroom = exports;
  return exports;
})();
