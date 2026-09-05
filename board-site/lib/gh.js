// Zero-dependency GitHub REST proxy helpers for the Kanban dispatch board.
// Auth: GITHUB_TOKEN (or MAILROOM_GH_TOKEN) Vercel secret. Repo:
// MAILROOM_GITHUB_REPO (default Exios66/mailroom-dev).
"use strict";

const GITHUB_API = "https://api.github.com";
const LANES = [
  { id: "assigned", title: "Assigned", label: "stage/assigned" },
  { id: "in-progress", title: "In Progress", label: "stage/in-progress" },
  { id: "needs-attention", title: "Needs Attention", label: "stage/needs-attention" },
  { id: "done", title: "Done", label: "stage/done" },
];
const PRI_LABELS = ["priority/critical", "priority/high", "priority/medium", "priority/low"];
const STAGE_LABELS = LANES.map((l) => l.label);

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

async function gh(path, { method = "GET", body, query } = {}) {
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
  return data;
}

// ---- issue -> board card normalization ---------------------------------

function cardIdFromIssue(issue) {
  const t = (issue.title || "").match(/HUB-\d{3,}/i);
  if (t) return t[0].toUpperCase();
  const b = (issue.body || "").match(/HUB-\d{3,}/i);
  return b ? b[0].toUpperCase() : null;
}

function laneFromIssue(issue) {
  for (const l of issue.labels || []) {
    const lane = LANES.find((x) => x.label === l.name);
    if (lane) return lane.id;
  }
  return issue.state === "closed" ? "done" : "assigned";
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

async function listKanbanIssues() {
  const data = await gh(`/repos/${repo()}/issues`, {
    query: { labels: "kanban", state: "all", per_page: 100, sort: "created", direction: "asc" },
  });
  return (data || []).map(toCard).filter((c) => c.id);
}

async function findIssueByCardId(cardId) {
  const cards = await listKanbanIssues();
  const hit = cards.find((c) => c.id === cardId);
  if (!hit) throw new HttpError(404, `no kanban issue mirrors ${cardId}`);
  const issue = await gh(`/repos/${repo()}/issues/${hit.issueNumber}`);
  return issue;
}

async function nextCardId() {
  const data = await gh(`/repos/${repo()}/issues`, {
    query: { labels: "kanban", state: "all", per_page: 100 },
  });
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