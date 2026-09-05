// GET /api/board — live kanban cards from GitHub issues (labels=kanban).
// POST /api/board — create a new card (opens a GitHub issue).
"use strict";

const ghx = require("../lib/gh.js");

function sendJson(res, status, obj) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(obj));
}

module.exports = async function handler(req, res) {
  try {
    if (req.method === "GET") {
      const cards = await ghx.listKanbanIssues();
      return sendJson(res, 200, {
        schema: 1,
        generatedAt: new Date().toISOString(),
        repo: ghx.repo(),
        cards,
      });
    }

    if (req.method === "POST") {
      const body = await readBody(req);
      const title = (body.title || "").trim();
      const desc = (body.desc || "").trim();
      const lane = (body.lane || "assigned").trim();
      const priority = (body.priority || "medium").trim();
      const agents = Array.isArray(body.agents) ? body.agents.map((a) => String(a).trim()).filter(Boolean) : [];
      if (!title) return sendJson(res, 400, { error: "title is required" });

      const laneObj = ghx.LANES.find((l) => l.id === lane) || ghx.LANES[0];
      const id = await ghx.nextCardId();
      const labels = ["kanban", "type/task", laneObj.label, `priority/${priority}`];

      const issueBody = [
        "## Board card — the issue is the mirror, the board is the truth",
        "",
        "Synced from the Mailroom Dispatch Board (served site).",
        "",
        `### Card ID\n\n${id}`,
        "",
        `### Lane\n\n${lane}`,
        "",
        `### Priority\n\n${priority}`,
        "",
        `### Task\n\n${desc || "—"}`,
        "",
        `### Evidence plan\n\n—`,
      ].join("\n");

      const created = await ghx.gh(`/repos/${ghx.repo()}/issues`, {
        method: "POST",
        body: {
          title: `${id}: ${title}`,
          body: issueBody,
          labels,
          assignees: agents,
        },
      });
      return sendJson(res, 201, ghx.toCard(created));
    }

    return sendJson(res, 405, { error: "method not allowed" });
  } catch (err) {
    const status = err.status || 500;
    return sendJson(res, status, { error: err.message || String(err) });
  }
};

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
      if (data.length > 1_000_000) {
        reject(new ghx.HttpError(413, "payload too large"));
        req.destroy();
      }
    });
    req.on("end", () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        reject(new ghx.HttpError(400, "invalid JSON body"));
      }
    });
    req.on("error", reject);
  });
}