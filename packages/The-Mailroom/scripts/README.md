<div align="center">

# ⚙️ The-Mailroom Scripts

**Utility scripts for The-Mailroom visualizer package.**

</div>

---

## Scripts

| Script | Purpose |
|:---|:---|
| `publish_space.py` | Publish Observatory to Hugging Face Spaces |
| `gen_interactive_charts.py` | Generate interactive Plotly charts |

## Usage

```bash
cd packages/The-Mailroom

# Publish to HF Spaces
python scripts/publish_space.py --check
python scripts/publish_space.py --repo <user>/mailroom-observatory

# Generate interactive charts
python scripts/gen_interactive_charts.py
```

## Related Files

- `hosted/` — Observatory (hosted edition)
- `web/` — Pixel console
- `server/` — Backend server
