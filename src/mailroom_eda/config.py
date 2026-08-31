"""Central configuration for the Mailroom Corpus EDA."""
from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

REPO_ID = "Lucius-Morningstar/docclass-merged"
REPO_URL = f"https://huggingface.co/datasets/{REPO_ID}"

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
DATA_DIR = ROOT / "data"
PARQUET_DIR = DATA_DIR / "parquet"
FIG_DIR = ROOT / "reports" / "figures"
TABLE_DIR = ROOT / "reports" / "tables"
REPORT_DIR = ROOT / "reports"

MANIFEST_PATH = DATA_DIR / "manifest.txt"
JSONL_PATH = DATA_DIR / "docclass_merged.jsonl"

DOC_TYPES = ["contract", "merger_agreement", "corporate_record", "correspondence", "insurance_claim"]
TYPE_COLORS = {
    "contract": "#4C72B0",
    "merger_agreement": "#DD8452",
    "corporate_record": "#55A868",
    "correspondence": "#C44E52",
    "insurance_claim": "#8172B3",
}

TOKEN_BUDGETS = [4_096, 8_192, 16_384, 32_768, 65_536, 131_072, 200_000]
CHARS_PER_TOKEN = 4  # heuristic; tiktoken o200k used for accurate estimates

RANDOM_STATE = 42


def split_rule(filename: str, encoding: str = "utf-8") -> str:
    """Family split rule: md5(filename) % 10 == 0 -> test else train."""
    h = hashlib.md5(filename.encode(encoding)).hexdigest()
    return "test" if int(h, 16) % 10 == 0 else "train"


def setup_matplotlib() -> None:
    mpl.use("Agg")
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
            "axes.titlesize": 11,
            "figure.facecolor": "white",
        }
    )


def ensure_dirs() -> None:
    for d in (DATA_DIR, FIG_DIR, TABLE_DIR, REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)
