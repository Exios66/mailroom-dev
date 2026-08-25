/* Mailroom Observatory client — same-origin API + WebSocket.
 * Langfuse (or the configured source) remains the only display source. */
const Obs = (() => {
  async function get(path) {
    const res = await fetch(path, { headers: { Accept: "application/json" } });
    if (!res.ok) {
      let detail = "";
      try {
        const body = await res.json();
        detail = body && body.detail ? ` — ${body.detail}` : "";
      } catch (e) { /* non-JSON */ }
      throw new Error(`HTTP ${res.status} ${path}${detail}`);
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

  function connectWS(onMessage) {
    let ws = null;
    let retry = 0;
    let timer = null;
    function open() {
      clearTimeout(timer);
      try { if (ws) ws.close(); } catch (e) { /* noop */ }
      ws = new WebSocket(wsURL());
      ws.onopen = () => {
        retry = 0;
        onMessage({ type: "status", connected: true });
      };
      ws.onmessage = (ev) => {
        try { onMessage(JSON.parse(ev.data)); }
        catch (e) { console.error("non-JSON WS frame"); }
      };
      ws.onclose = () => {
        onMessage({ type: "status", connected: false });
        const delay = Math.min(30000, 1000 * 2 ** retry++);
        timer = setTimeout(open, delay);
      };
      ws.onerror = () => { try { ws.close(); } catch (e) { /* noop */ } };
    }
    open();
    return { close: () => { clearTimeout(timer); try { ws && ws.close(); } catch (e) { /* noop */ } } };
  }

  return { api, fmt, esc, connectWS };
})();
