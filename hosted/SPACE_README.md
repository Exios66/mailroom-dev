---
title: Mailroom Observatory
emoji: 📬
colorFrom: rose
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Live accessible desk for the llm-mailroom pipeline
---

# Mailroom Observatory

Hosted edition of [The-Mailroom](https://github.com/Exios66/The-Mailroom):
a public, accessible operations desk for the `llm-mailroom` legal-document
pipeline. It reads **Langfuse only** (keys are Space secrets, never the
browser).

This Space is **not** the GitHub Pages snapshot and **not** the local
pixel-art console.

Required secrets: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`.
Optional: `LANGFUSE_HOST`, `MAILROOM_SOURCE`, `MAILROOM_TRACE_TAGS`,
`MAILROOM_TRACE_ENVIRONMENTS`.

Copy this file to the Space's `README.md` if you deploy from a dedicated
Space repo; the container build uses the repository `Dockerfile`.
