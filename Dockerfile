# Mailroom Observatory — public hosted edition.
# Works on Hugging Face Spaces (Docker SDK, port 7860), Fly, Render, or any
# host that runs a container and injects Langfuse secrets. This is NOT the
# GitHub Pages snapshot and NOT the local pixel-art console.
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY mailroom_ui ./mailroom_ui
COPY server ./server
COPY hosted ./hosted
COPY web ./web
COPY tui ./tui

RUN pip install --no-cache-dir .

ENV MAILROOM_EDITION=hosted
ENV MAILROOM_HOST=0.0.0.0
ENV MAILROOM_PORT=7860
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["python", "-m", "server.hosted"]
