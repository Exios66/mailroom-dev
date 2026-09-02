<div align="center">

# 🧪 Evaluation Scripts

**Evaluation scripts for the llm-entity-extraction package.**

</div>

---

## Scripts

| Script | Purpose |
|:---|:---|
| `run_eval.py` | Run evaluation pipeline |
| `run_agent_eval.py` | Run agent-specific evaluation |
| `run_quality_judges.py` | Run quality judge evaluation |

## Usage

```bash
cd packages/llm-entity-extraction
python scripts/eval/run_eval.py --mock
python scripts/eval/run_agent_eval.py --agent sorter --mock
```

## Related Files

- `../reporting/` — Report generation
- `../datasets/` — Dataset scripts
- `data/gt/` — Ground truth data
- `reports/` — Generated reports
