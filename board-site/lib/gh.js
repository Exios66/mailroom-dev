// Zero-dependency GitHub REST proxy helpers for the Kanban dispatch board.
// Auth: GITHUB_TOKEN (or MAILROOM_GH_TOKEN) Vercel secret. Repo:
// MAILROOM_GITHUB_REPO (default Exios66/mailroom-dev).
//
// Lane flow: unassigned → assigned → in-progress → needs-attention → done
// Issues with no stage/* label AND no assignees land in "unassigned" (triage queue).
"use strict";

const GITHUB_API = "https://api.github.com";
const LANES = [
  { id: "unassigned",  title: "Unassigned",  label: "stage/unassigned" },
  { id: "assigned",    title: "Assigned",    label: "stage/assigned" },
  { id: "in-progress", title: "In Progress", label: "stage/in-progress" },
  { id: "needs-attention", title: "Needs Attention", label: "stage/needs-attention" },
  { id: "done",        title: "Done",        label: "stage/done" },
];
const PRI_LABELS = ["priority/critical", "priority/high", "priority/medium", "priority/low"];
const STAGE_LABELS = LANES.map((l) => l.label);

// ── CORS helpers ──────────────────────────────────────────────────────
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PATCH, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Mailroom-Actor",
  "Access-Control-Max-Age": "86400",
};

function cors(res) {
  for (const [k, v] of Object.entries(CORS_HEADERS)) res.setHeader(k, v);
}

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function token() {
  const t = process.env.GITHUB_TOKEN || process.env.MAILROOM_GH_TOKEN;
  if (!t) throw new HttpError(500, "GITHUB_TOKEN not configured on the server");
  return t;
}

function repo() {
  return process.env.MAILROOM_GITHUB_REPO || "Exios66/mailroom-dev";
}

function actor(req) {
  const raw = (req.headers["x-mailroom-actor"] || "").toString().trim();
  return raw ? raw.slice(0, 60) : "anonymous";
}

async function gh(path, { method = "GET", body, query, ifNoneMatch } = {}) {
  let url = `${GITHUB_API}${path}`;
  if (query) {
    const qs = new URLSearchParams(query);
    if (qs.toString()) url += (url.includes("?") ? "&" : "?") + qs.toString();
  }
  const headers = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "mailroom-dispatch-board",
    Authorization: `Bearer ${token()}`,
  };
  if (ifNoneMatch) headers["If-None-Match"] = ifNoneMatch;
  const opts = { method, headers };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  let res;
  try {
    res = await fetch(url, { ...opts, signal: AbortSignal.timeout(8000) });
  } catch (err) {
    throw new HttpError(502, `GitHub unreachable: ${err.message}`);
  }
  // Return 304 Not Modified upstream to caller for conditional-request flow
  if (res.status === 304) return { _notModified: true, _etag: res.headers.get("etag") };
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch (_) {
    /* non-JSON body */
  }
  if (!res.ok) {
    const msg = (data && (data.message || JSON.stringify(data))) || `GitHub ${res.status}`;
    throw new HttpError(res.status, msg);
  }
  // Attach _etag metadata without corrupting arrays
  if (Array.isArray(data)) {
    data._etag = res.headers.get("etag");
    return data;
  }
  return { ...data, _etag: res.headers.get("etag") };
}

// ---- issue -> board card normalization ---------------------------------

function cardIdFromIssue(issue) {
  const t = (issue.title || "").match(/HUB-\d{3,}/i);
  if (t) return t[0].toUpperCase();
  const b = (issue.body || "").match(/HUB-\d{3,}/i);
  return b ? b[0].toUpperCase() : null;
}

// Lane detection logic:
//   1. Explicit stage/* label wins (stage/unassigned, stage/assigned, etc.)
//   2. Closed issues → done
//   3. Open issue with no stage label AND no assignees → unassigned (triage queue)
//   4. Open issue with no stage label but HAS assignees → assigned (someone claimed it)
function laneFromIssue(issue) {
  // Check for explicit stage label first
  for (const l of issue.labels || []) {
    const lane = LANES.find((x) => x.label === l.name);
    if (lane) return lane.id;
  }
  // Closed with no label = done
  if (issue.state === "closed") return "done";
  // Open, no stage label: unassigned if no one is on it, otherwise assigned
  const hasAssignees = (issue.assignees || []).length > 0;
  return hasAssignees ? "assigned" : "unassigned";
}

function priorityFromIssue(issue) {
  for (const l of issue.labels || []) if (PRI_LABELS.includes(l.name)) return l.name.split("/")[1];
  return "medium";
}

function bodySection(body, heading) {
  const re = new RegExp(`^### ${heading}\\s*\\n([\\s\\S]*?)(?=^### |\\Z)`, "m");
  const m = (body || "").match(re);
  return m ? m[1].replace(/^\s+|\s+$/g, "") : "";
}

function setBodySection(body, heading, content) {
  const clean = (content || "").trim();
  if (!body) body = "";
  const section = `### ${heading}\n${clean ? clean : "—"}`;
  const re = new RegExp(`^### ${heading}\\s*\\n[\\s\\S]*?(?=^### |\\Z)`, "m");
  if (re.test(body)) return body.replace(re, section);
  return `${body.replace(/\s*$/, "")}\n\n${section}\n`;
}

function toCard(issue) {
  return {
    id: cardIdFromIssue(issue),
    issueNumber: issue.number,
    title: (issue.title || "").replace(/^HUB-\d{3,}\s*:\s*/i, ""),
    desc: bodySection(issue.body, "Task"),
    lane: laneFromIssue(issue),
    priority: priorityFromIssue(issue),
    agents: (issue.assignees || []).map((a) => a.login),
    evidence: bodySection(issue.body, "Evidence plan"),
    date: (issue.created_at || "").slice(0, 10),
    archived: issue.state === "closed",
    createdAt: issue.created_at,
    updatedAt: issue.updated_at,
    htmlUrl: issue.html_url,
  };
}

// ── Paginated issue fetch (handles >100 issues) ────────────────────────
async function fetchAllKanbanIssues() {
  const all = [];
  let page = 1;
  while (true) {
    const batch = await gh(`/repos/${repo()}/issues`, {
      query: { labels: "kanban", state: "all", per_page: "100", page: String(page), sort: "created", direction: "asc" },
    });
    const items = Array.isArray(batch) ? batch : [];
    if (items.length === 0) break;
    all.push(...items);
    if (items.length < 100) break; // last page
    page++;
  }
  return all;
}

async function listKanbanIssues() {
  const data = await fetchAllKanbanIssues();
  return data.map(toCard).filter((c) => c.id);
}

// ── FIX: use GitHub search API for efficient single-issue lookup ──────
// Instead of listing ALL kanban issues to find one, search by title.
async function findIssueByCardId(cardId) {
  try {
    const searchResult = await gh(`/search/issues`, {
      query: {
        q: `repo:${repo()} is:issue "${cardId}" label:kanban`,
        per_page: "5",
      },
    });
    const items = searchResult.items || [];
    const hit = items.find((issue) => cardIdFromIssue(issue) === cardId);
    if (hit) {
      const issue = await gh(`/repos/${repo()}/issues/${hit.number}`);
      return issue;
    }
  } catch (_) {
    // Search API may fail on some configs; fall back to list scan
  }
  // Fallback: scan all kanban issues (slower, but reliable)
  const cards = await listKanbanIssues();
  const fallback = cards.find((c) => c.id === cardId);
  if (!fallback) throw new HttpError(404, `no kanban issue mirrors ${cardId}`);
  const issue = await gh(`/repos/${repo()}/issues/${fallback.issueNumber}`);
  return issue;
}

async function nextCardId() {
  const data = await fetchAllKanbanIssues();
  let max = 0;
  for (const issue of data || []) {
    const m = (issue.title || "").match(/HUB-(\d{3,})/i);
    if (m) max = Math.max(max, parseInt(m[1], 10));
  }
  return `HUB-${String(max + 1).padStart(3, "0")}`;
}

module.exports = {
  HttpError,
  LANES,
  PRI_LABELS,
  STAGE_LABELS,
  CORS_HEADERS,
  cors,
  repo,
  actor,
  gh,
  toCard,
  bodySection,
  setBodySection,
  listKanbanIssues,
  findIssueByCardId,
  nextCardId,
};