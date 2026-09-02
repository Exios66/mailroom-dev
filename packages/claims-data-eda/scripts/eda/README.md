<div align="center">

# 📁 Claims EDA Scripts

**Exploratory Data Analysis scripts for the CMS DE-SynPUF insurance claims dataset.**

</div>

---

## Scripts

| Script | Description |
|:---|:---|
| `generate_figures.py` | Static matplotlib/seaborn charts |
| `generate_interactive.py` | Interactive Plotly HTML charts |

## Usage

```bash
cd packages/claims-data-eda
python scripts/eda/generate_figures.py
python scripts/eda/generate_interactive.py
```

## Output

Generated charts are saved to:
- `reports/eda/figures/` — Static PNGs
- `reports/eda/figures_interactive/` — Interactive HTMLs

## Related Files

- `reports/eda/` — Generated reports
- `scripts/gen_interactive_charts.py` — Alternative interactive generator
