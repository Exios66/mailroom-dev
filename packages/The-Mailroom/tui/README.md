<div align="center">

# 💻 The-Mailroom TUI

**Terminal User Interface for The-Mailroom visualizer.**

</div>

---

## Purpose

The TUI provides a terminal-based interface for the Mailroom pipeline, featuring:
- AgentLab banners and tables
- Live pipeline status
- Review queue management

## Running

```bash
cd packages/The-Mailroom
pip install -e ".[dev]"
mailroom-tui
```

## Features

- Terminal-optimized layout
- Keyboard-first navigation
- Color-coded status indicators
- Responsive to terminal size

## Related Files

- `web/` — Pixel console (CRT canvas)
- `hosted/` — Observatory (hosted edition)
- `server/` — Backend server
