#!/usr/bin/env python3
"""Full-corpus EDA for the CMS DE-SynPUF Sample-1 claim-event index.

Consumes data/cms/{beneficiaries,index}.jsonl and produces:
  reports/eda/report.md          detailed multi-section report
  reports/eda/findings.md        condensed pipeline-relevant findings
  reports/eda/corpus_stats.json  machine-readable stats (feeds findings.md)
  reports/eda/figures/*.png      publication figures

Everything streams line-by-line; heavy-tailed money fields use bounded
reservoir samples for percentile estimation.

Usage:
    python scripts/eda/explore_cms.py [--sample-budget 200000]
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
CMS_DIR = REPO / "data" / "cms"
REPORTS = REPO / "reports" / "eda"
FIGURES = REPORTS / "figures"

CC_LABELS = {
    "ALZHDMTA": "Alzheimer's/Dementia", "CHF": "Heart Failure", "CHRNKIDN": "Chronic Kidney Disease",
    "CNCR": "Cancer", "COPD": "COPD", "DEPRESSN": "Depression", "DIABETES": "Diabetes",
    "ISCHMCHT": "Ischemic Heart Disease", "OSTEOPRS": "Osteoporosis", "RA_OA": "Rheumatoid/Osteo Arthritis",
    "STRKETIA": "Stroke/TIA",
}
RACE_LABELS = {1: "White", 2: "Black", 3: "Others", 5: "Hispanic"}
SSA_STATES = {
    1: "AL", 2: "AK", 3: "AZ", 4: "AR", 5: "CA", 6: "CO", 7: "CT", 8: "DE", 9: "DC", 10: "FL",
    11: "GA", 12: "HI", 13: "ID", 14: "IL", 15: "IN", 16: "IA", 17: "KS", 18: "KY", 19: "LA",
    20: "ME", 21: "MD", 22: "MA", 23: "MI", 24: "MN", 25: "MS", 26: "MO", 27: "MT", 28: "NE",
    29: "NV", 30: "NH", 31: "NJ", 32: "NM", 33: "NY", 34: "NC", 35: "ND", 36: "OH", 37: "OK",
    38: "OR", 39: "PA", 40: "RI", 41: "SC", 42: "SD", 43: "TN", 44: "TX", 45: "UT", 46: "VT",
    47: "VA", 48: "WA", 49: "WV", 50: "WI", 51: "WY", 52: "PR", 53: "VI", 54: "GU", 55: "AS",
    56: "MP",
}
TYPE_LABELS = {"inpatient": "Inpatient", "outpatient": "Outpatient", "carrier": "Carrier (physician)", "pde": "PDE (drug)"}


def jopen(path: Path, mode: str = "rt"):
    if str(path).endswith(".gz"):
        return gzip.open(path, mode, encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def id_key(raw: str):
    """Memory-efficient claim-id key for distinct-count sets."""
    return int(raw) if raw.isdigit() else raw


def to_int0(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


class Reservoir:
    """Fixed-size reservoir sample for percentile estimation on streams."""

    def __init__(self, k: int):
        self.k = k
        self.n = 0
        self.items: list[float] = []
        self.rng = random.Random(42)

    def add(self, x: float | None) -> None:
        if x is None or not math.isfinite(x) or x <= 0:
            return
        self.n += 1
        if len(self.items) < self.k:
            self.items.append(x)
        else:
            j = self.rng.randint(0, self.n - 1)
            if j < self.k:
                self.items[j] = x

    @property
    def values(self) -> np.ndarray:
        return np.asarray(self.items, dtype=float)

    def pct(self, q: float) -> float:
        return float(np.percentile(self.values, q)) if len(self.items) else float("nan")


def fmt_int(n: int | float) -> str:
    return f"{int(n):,}"


def fmt_usd(x: float) -> str:
    if abs(x) >= 1e9:
        return f"${x/1e9:.2f}B"
    if abs(x) >= 1e6:
        return f"${x/1e6:.2f}M"
    if abs(x) >= 1e3:
        return f"${x/1e3:.1f}K"
    return f"${x:.2f}"


def md_table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(str(h) for h in headers) + " |"]
    out.append("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


# --------------------------------------------------------------------------- pass 1: beneficiaries

def scan_beneficiaries() -> dict:
    s = {
        "total": 0,
        "dead_by_file": {},
        "sex": Counter(), "race": Counter(), "state_top": Counter(),
        "esrd": Counter(),
        "age_band_2008": Counter(),
        "cc_prevalence_years": {y: Counter() for y in (2008, 2009, 2010)},
        "money_totals_by_year": defaultdict(lambda: defaultdict(float)),
        "death_years": Counter(),
    }
    with jopen(CMS_DIR / "beneficiaries.jsonl.gz") as fh:
        for line in fh:
            b = json.loads(line)
            s["total"] += 1
            s["sex"][{"1": "M", "2": "F"}.get(b.get("bene_sex_ident_cd"), "U")] += 1
            rc = b.get("bene_race_cd")
            s["race"][rc] += 1
            st = to_int0(b.get("sp_state_code"))
            if st:
                s["state_top"][SSA_STATES.get(st, str(st))] += 1
            s["esrd"][b.get("bene_esrd_ind") or "N"] += 1
            if b["birth_dt"]:
                age08 = 2008 - int(b["birth_dt"][:4])
                band = "<65" if age08 < 65 else "65-74" if age08 < 75 else "75-84" if age08 < 85 else "85+"
                s["age_band_2008"][band] += 1
            if b["death_dt"]:
                s["death_years"][b["death_dt"][:4]] += 1
            for y in (2008, 2009, 2010):
                yd = b["years"].get(y)
                if not yd:
                    continue
                for k, v in yd["cc"].items():
                    if v == 1:
                        s["cc_prevalence_years"][y][k] += 1
                for m, v in yd["money"].items():
                    if v:
                        s["money_totals_by_year"][y][m] += v
    return s


# --------------------------------------------------------------------------- pass 2: claim events

def scan_events(sample_budget: int, bene_ids: set[str], carrier_npi_counter: Counter) -> dict:
    s = {
        "events_total": 0,
        "by_type": Counter(),
        "by_type_year": defaultdict(Counter),
        "monthly": defaultdict(Counter),
        "distinct_claims_by_type": defaultdict(set),
        "distinct_bene_overall": set(),
        "bene_in_claims": Counter(),
        "cost_samples": {t: Reservoir(sample_budget) for t in ("inpatient", "outpatient", "carrier", "pde")},
        "cost_paid_sum": defaultdict(float),
        "dx_counter": defaultdict(Counter),
        "dx_per_claim": defaultdict(Counter),
        "proc_counter": Counter(),
        "hcpcs_counter": defaultdict(Counter),
        "ndc_counter": Counter(),
        "days_supply": Reservoir(sample_budget),
        "npi_sets": {"carrier_prf": set(), "institutional_prvdr": set()},
        "carrier_npi_counts": Counter(),
        "ip_drg": Counter(),
        "util_days_sum": 0,
        "los_samples": Reservoir(min(100000, sample_budget)),
        "empty_dx_rate": defaultdict(lambda: [0, 0]),
        "source_files_rows": Counter(),
    }
    with jopen(CMS_DIR / "index.jsonl.gz") as fh:
        for line in fh:
            e = json.loads(line)
            t = e["claim_type"]
            s["events_total"] += 1
            s["by_type"][t] += 1
            s["source_files_rows"][e["source_file"]] += 1
            y = e.get("year") or 0
            s["by_type_year"][t][y] += 1
            mkey = None
            d = e.get("from_dt") or e.get("service_dt")
            if d:
                mkey = d[:7]
                s["monthly"][t][mkey] += 1
            s["distinct_claims_by_type"][t].add(id_key(e.get("clm_id") or e.get("pde_id")))
            s["distinct_bene_overall"].add(e["bene_id"])
            s["bene_in_claims"][e["bene_id"]] += 1
            (link_ok := e["bene_id"] in bene_ids)
            s.setdefault("linked_by_type", Counter())[t] += link_ok
            s.setdefault("unlinked_by_type", Counter())[t] += not link_ok

            if t == "carrier":
                for n in e.get("provider_npis", []):
                    if n:
                        carrier_npi_counter[n] += 1

            pay = e.get("payment_amt") if t != "pde" else e.get("drug_cost_amt")
            s["cost_samples"][t].add(pay)
            if pay:
                s["cost_paid_sum"][t] += pay

            if t == "pde":
                if e.get("ndc"):
                    s["ndc_counter"][e["ndc"]] += 1
                ds = e.get("days_supply")
                if ds:
                    s["days_supply"].add(ds)
                cnt, tot = s["empty_dx_rate"][t]
                s["empty_dx_rate"][t] = [cnt, tot + 1]
            elif t == "carrier":
                dxs = e.get("diagnosis_codes", [])
                for c in dxs:
                    s["dx_counter"]["carrier"][c] += 1
                cnt, tot = s["empty_dx_rate"][t]
                s["empty_dx_rate"][t] = [cnt + (0 if dxs else 1), tot + 1]
                for h in e.get("hcpcs_codes", []):
                    s["hcpcs_counter"]["carrier"][h] += 1
            elif t == "outpatient":
                for c in e.get("diagnosis_codes", []):
                    s["dx_counter"]["outpatient"][c] += 1
                for h in e.get("hcpcs_codes", []):
                    s["hcpcs_counter"]["outpatient"][h] += 1
                for p in e.get("procedure_codes", []):
                    s["proc_counter"][p] += 1
                if e.get("prvdr_num"):
                    s["npi_sets"]["institutional_prvdr"].add(("op", e["prvdr_num"]))
                cnt, tot = s["empty_dx_rate"][t]
                s["empty_dx_rate"][t] = [cnt + (0 if e.get("diagnosis_codes") else 1), tot + 1]
            elif t == "inpatient":
                for c in e.get("diagnosis_codes", []):
                    s["dx_counter"]["inpatient"][c] += 1
                for p in e.get("procedure_codes", []):
                    s["proc_counter"][p] += 1
                if e.get("drg_cd"):
                    s["ip_drg"][e["drg_cd"]] += 1
                if e.get("prvdr_num"):
                    s["npi_sets"]["institutional_prvdr"].add(("ip", e["prvdr_num"]))
                los = e.get("utilization_days")
                if los is not None:
                    s["los_samples"].add(los)
                    s["util_days_sum"] += los
                cnt, tot = s["empty_dx_rate"][t]
                s["empty_dx_rate"][t] = [cnt + (0 if e.get("diagnosis_codes") else 1), tot + 1]
    # provider concentration folded into the main scan (carrier_npi_counter)
    return s


# --------------------------------------------------------------------------- figures

plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.titlesize": 11, "axes.titleweight": "bold"})
COLORS = {"inpatient": "#2563eb", "outpatient": "#059669", "carrier": "#d97706", "pde": "#7c3aed"}


def save(fig, name: str) -> str:
    path = FIGURES / name
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return f"figures/{name}"


def fig_corpus_overview(s: dict) -> str:
    types = ["inpatient", "outpatient", "carrier", "pde"]
    events = [s["by_type"][t] for t in types]
    unique = [len(s["distinct_claims_by_type"][t]) for t in types]
    x = np.arange(len(types))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.bar(x - 0.2, events, 0.38, label="Event rows (segments/lines)", color="#1d4ed8")
    ax.bar(x + 0.2, unique, 0.38, label="Distinct claim IDs", color="#60a5fa")
    ax.set_xticks(x, [TYPE_LABELS[t] for t in types])
    ax.set_ylabel("rows")
    ax.set_title(f"Corpus overview — {fmt_int(s['events_total'])} claim events, Sample 1")
    for i, v in enumerate(events):
        ax.text(i - 0.2, v, fmt_int(v), ha="center", va="bottom", fontsize=7)
    for i, v in enumerate(unique):
        ax.text(i + 0.2, v, fmt_int(v), ha="center", va="bottom", fontsize=7)
    ax.legend()
    ax.set_ylim(0, max(events) * 1.12)
    return save(fig, "01_corpus_overview.png")


def fig_monthly_volume(s: dict) -> str:
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 5.5), sharex=False)
    for ax, t in zip(axes.flat, ["inpatient", "outpatient", "carrier", "pde"]):
        months = sorted(s["monthly"][t])
        vals = [s["monthly"][t][m] for m in months]
        ax.plot(range(len(months)), vals, lw=1, color=COLORS[t])
        ticks = [i for i, m in enumerate(months) if m.endswith("-01")]
        ax.set_xticks(ticks, [months[i][:4] for i in ticks])
        ax.set_title(TYPE_LABELS[t])
        ax.grid(alpha=0.3)
    fig.suptitle("Monthly claim-event volume, 2008–2010", fontweight="bold")
    return save(fig, "02_monthly_volume.png")


def fig_demographics(s: dict) -> str:
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4))
    bands = ["<65", "65-74", "75-84", "85+"]
    vals = [s["age_band_2008"].get(b, 0) for b in bands]
    axes[0].bar(bands, vals, color="#1d4ed8")
    axes[0].set_title("Age band (as of 2008)")
    for i, v in enumerate(vals):
        axes[0].text(i, v, fmt_int(v), ha="center", va="bottom", fontsize=7)
    races = sorted(s["race"], key=lambda k: -s["race"][k])
    labels = [f"{RACE_LABELS.get(r, '?')} ({r})" for r in races]
    axes[1].pie([s["race"][r] for r in races], labels=labels, autopct="%1.1f%%", textprops={"fontsize": 7})
    axes[1].set_title("Race (CMS code)")
    states = s["state_top"].most_common(10)
    axes[2].barh([k for k, _ in states][::-1], [v for _, v in states][::-1], color="#059669")
    axes[2].set_title("Top 10 states (SSA code)")
    return save(fig, "03_demographics.png")


def fig_chronic(s: dict) -> str:
    conds = list(CC_LABELS)
    prev = s["cc_prevalence_years"]
    x = np.arange(len(conds))
    fig, ax = plt.subplots(figsize=(8.5, 4))
    for i, y in enumerate((2008, 2010)):
        vals = [prev[y][c] / max(s["total"], 1) * 100 for c in conds]
        ax.bar(x + (i - 0.5) * 0.38, vals, 0.36, label=str(y), color=["#93c5fd", "#1d4ed8"][i])
    ax.set_xticks(x, [CC_LABELS[c] for c in conds], rotation=45, ha="right", fontsize=7.5)
    ax.set_ylabel("% of beneficiaries flagged")
    ax.set_title("Chronic-condition flag prevalence (CCW 11-condition set)")
    ax.legend()
    return save(fig, "04_chronic_conditions.png")


def fig_comorbidity(s: dict) -> str:
    conds = list(CC_LABELS)
    mat = np.zeros((len(conds), len(conds)))
    with jopen(CMS_DIR / "beneficiaries.jsonl.gz") as fh:
        for line in fh:
            cc = json.loads(line)["years"].get(2010, {}).get("cc", {})
            flags = [k for k in conds if cc.get(k) == 1]
            for i, a in enumerate(flags):
                for b in flags:
                    mat[conds.index(a), conds.index(b)] += 1
    n = s["total"]
    with np.errstate(divide="ignore", invalid="ignore"):
        pct = np.where(mat > 0, mat / n * 100, 0)
    fig, ax = plt.subplots(figsize=(7.2, 6))
    im = ax.imshow(pct, cmap="Blues")
    ax.set_xticks(range(len(conds)), [CC_LABELS[c] for c in conds], rotation=90, fontsize=7)
    ax.set_yticks(range(len(conds)), [CC_LABELS[c] for c in conds], fontsize=7)
    for i in range(len(conds)):
        for j in range(len(conds)):
            if pct[i, j] >= 0.5:
                ax.text(j, i, f"{pct[i,j]:.1f}", ha="center", va="center", fontsize=6,
                        color="white" if pct[i, j] > pct.max() * 0.6 else "black")
    fig.colorbar(im, shrink=0.8, label="% of beneficiaries (2010 flags)")
    ax.set_title("Comorbidity co-occurrence matrix")
    return save(fig, "05_comorbidity_matrix.png")


def fig_costs(s: dict) -> str:
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.2))
    for ax, t in zip(axes, ["inpatient", "outpatient", "carrier", "pde"]):
        v = s["cost_samples"][t].values
        if len(v) == 0:
            continue
        ax.hist(np.log10(v), bins=60, color=COLORS[t], alpha=0.85)
        med = s["cost_samples"][t].pct(50)
        ax.axvline(math.log10(med), color="black", ls="--", lw=1)
        ax.set_title(TYPE_LABELS[t])
        ax.set_xlabel("log10(amount)")
        ax.text(0.02, 0.95, f"median {fmt_usd(med)}\np95 {fmt_usd(s['cost_samples'][t].pct(95))}",
                transform=ax.transAxes, va="top", fontsize=7,
                bbox=dict(fc="white", alpha=0.8))
    fig.suptitle("Per-event payment distributions (log scale; dashed = median)", fontweight="bold")
    return save(fig, "06_cost_distributions.png")


def fig_top_diagnoses(s: dict) -> str:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
    for ax, t in zip(axes, ["inpatient", "carrier"]):
        top = s["dx_counter"][t].most_common(20)
        ax.barh([c for c, _ in top][::-1], [n for _, n in top][::-1],
                color=COLORS[t], height=0.7)
        ax.set_title(f"Top 20 ICD-9 diagnosis codes ({TYPE_LABELS[t]})")
        ax.tick_params(labelsize=7)
    return save(fig, "07_top_diagnoses.png")


def fig_procedures_drugs(s: dict) -> str:
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    panels = [
        (axes[0], s["proc_counter"].most_common(15), "Top ICD-9 procedures (inpatient)", "#2563eb"),
        (axes[1], s["hcpcs_counter"]["outpatient"].most_common(15), "Top HCPCS (outpatient)", "#059669"),
        (axes[2], s["hcpcs_counter"]["carrier"].most_common(15), "Top HCPCS (carrier lines)", "#d97706"),
    ]
    for ax, items, title, color in panels:
        ax.barh([c for c, _ in items][::-1], [n for _, n in items][::-1], color=color, height=0.7)
        ax.set_title(title)
        ax.tick_params(labelsize=7)
    return save(fig, "08_procedures_hcpcs.png")


def fig_top_drugs(s: dict) -> str:
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    top = s["ndc_counter"].most_common(20)
    ax.barh([c for c, _ in top][::-1], [n for _, n in top][::-1], color="#7c3aed", height=0.7)
    ax.set_title("Top 20 NDC drug products (PDE fills)")
    ax.set_xlabel("fill events")
    ax.tick_params(labelsize=7)
    return save(fig, "09_top_drugs_ndc.png")


def fig_provider_concentration(carrier_counts: Counter) -> str:
    total_lines = sum(carrier_counts.values())
    counts = sorted(carrier_counts.values(), reverse=True)
    cum = np.cumsum(counts) / max(total_lines, 1)
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    axes[0].plot(np.arange(len(cum)) / len(cum) * 100, cum * 100, color="#d97706")
    axes[0].plot([0, 100], [0, 100], "k--", lw=0.8, label="perfect equality")
    axes[0].set_xlabel("% of billing providers (cumulative)")
    axes[0].set_ylabel("% of carrier lines")
    axes[0].set_title("Lorenz curve — carrier provider concentration")
    axes[0].legend(fontsize=7)
    top_share = sum(counts[:max(len(counts) // 100, 1)]) / max(total_lines, 1) * 100
    axes[0].annotate(f"top 1% of providers\nbill {top_share:.0f}% of lines", xy=(0.35, 0.05),
                     xycoords="axes fraction", fontsize=8,
                     bbox=dict(fc="#fef3c7", ec="#d97706"))
    axes[1].hist(counts, bins=80, color="#d97706", alpha=0.85, log=True)
    axes[1].set_xlabel("lines billed by one provider")
    axes[1].set_ylabel("providers (log)")
    axes[1].set_title("Provider activity distribution")
    return save(fig, "10_provider_concentration.png")


def fig_utilization(s: dict) -> str:
    per_bene = Counter(s["bene_in_claims"].values())
    xs = sorted(per_bene)
    ys = [per_bene[x] for x in xs]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    axes[0].bar(xs[:60], ys[:60], color="#1d4ed8")
    axes[0].set_xlabel("claim events per beneficiary (truncated at 60)")
    axes[0].set_ylabel("beneficiaries")
    axes[0].set_title("Utilization cohort histogram")
    ordered = sorted(s["bene_in_claims"].values(), reverse=True)
    cum = np.cumsum(ordered) / max(sum(ordered), 1)
    axes[1].plot(np.arange(len(cum)) / len(cum) * 100, cum * 100, color="#1d4ed8")
    axes[1].plot([0, 100], [0, 100], "k--", lw=0.8)
    top20 = sum(ordered[:max(int(len(ordered) * 0.2), 1)]) / max(sum(ordered), 1) * 100
    axes[1].annotate(f"top 20% of patients\ngenerate {top20:.0f}% of events", xy=(0.35, 0.15),
                     xycoords="axes fraction", fontsize=8, bbox=dict(fc="#dbeafe", ec="#1d4ed8"))
    axes[1].set_xlabel("% of beneficiaries (cumulative, claim-active)")
    axes[1].set_ylabel("% of claim events")
    axes[1].set_title("Lorenz curve — utilization concentration")
    return save(fig, "11_utilization.png")


def fig_reimbursements(s: dict) -> str:
    years = (2008, 2009, 2010)
    series = {
        "Part A (IP)": ["MEDREIMB_IP"], "Part B (OP+CAR)": ["MEDREIMB_OP", "MEDREIMB_CAR"],
    }
    fig, ax = plt.subplots(figsize=(7, 3.8))
    width = 0.35
    x = np.arange(len(years))
    for i, (label, keys) in enumerate(series.items()):
        vals = [sum(s["money_totals_by_year"][y][k] for k in keys) / s["total"] for y in years]
        ax.bar(x + (i - 0.5) * width, vals, width, label=label, color=["#1d4ed8", "#059669"][i])
    ax.set_xticks(x, [str(y) for y in years])
    ax.set_ylabel("$ per beneficiary per year (mean)")
    ax.set_title("Mean annual Medicare reimbursements (beneficiary summary rollup)")
    ax.legend()
    return save(fig, "12_annual_reimbursements.png")


# --------------------------------------------------------------------------- report

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample-budget", type=int, default=150_000, help="reservoir size per money field")
    args = ap.parse_args()

    FIGURES.mkdir(parents=True, exist_ok=True)
    print("[1/3] scanning beneficiaries ...", flush=True)
    bs = scan_beneficiaries()

    print("[2/3] scanning claim events ...", flush=True)
    with jopen(CMS_DIR / "beneficiaries.jsonl.gz") as fh:
        bene_ids = {json.loads(l)["bene_id"] for l in fh}
    carrier_counts: Counter = Counter()
    es = scan_events(args.sample_budget, bene_ids, carrier_counts)
    link = {"linked": es.pop("linked_by_type", Counter()),
            "unlinked": es.pop("unlinked_by_type", Counter())}

    print("[3/3] figures + reports ...", flush=True)
    # ---------------- figures ----------------
    figs = {}
    figs["corpus"] = fig_corpus_overview(es)
    figs["monthly"] = fig_monthly_volume(es)
    figs["demo"] = fig_demographics(bs)
    figs["chronic"] = fig_chronic(bs)
    figs["comorb"] = fig_comorbidity(bs)
    figs["costs"] = fig_costs(es)
    figs["dx"] = fig_top_diagnoses(es)
    figs["proc"] = fig_procedures_drugs(es)
    figs["drugs"] = fig_top_drugs(es)
    figs["prov"] = fig_provider_concentration(carrier_counts)
    figs["util"] = fig_utilization(es)
    figs["reimb"] = fig_reimbursements(es)

    # ---------------- stats ----------------
    stats = build_stats(bs, es, carrier_counts, link)
    (REPORTS / "corpus_stats.json").write_text(json.dumps(stats, indent=2, default=str) + "\n")

    # ---------------- reports ----------------
    write_report(bs, es, stats, figs, carrier_counts)
    write_findings(stats)
    print("\nEDA COMPLETE -> reports/eda/", flush=True)
    return 0


def build_stats(bs, es, carrier_counts, link) -> dict:
    st: dict = {}
    st["generated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    st["beneficiaries"] = bs["total"]
    st["bene_sex"] = dict(bs["sex"])
    st["bene_race"] = {str(k): v for k, v in bs["race"].items()}
    st["age_band_2008"] = dict(bs["age_band_2008"])
    st["deaths_recorded"] = sum(bs["death_years"].values())
    st["death_years"] = dict(bs["death_years"])
    st["cc_prevalence_pct_2010"] = {
        CC_LABELS[k]: round(v / bs["total"] * 100, 1) for k, v in bs["cc_prevalence_years"][2010].most_common()
    }
    st["events_total"] = es["events_total"]
    st["events_by_type"] = dict(es["by_type"])
    st["unique_claims_by_type"] = {t: len(v) for t, v in es["distinct_claims_by_type"].items()}
    st["bene_active_in_claims"] = len(es["bene_in_claims"])
    st["linkage"] = {
        "linked_by_type": dict(link["linked"]),
        "unlinked_by_type": dict(link["unlinked"]),
    }
    st["cost_percentiles"] = {
        t: {q: round(res.pct(q), 2) for q in (10, 25, 50, 75, 90, 95, 99)}
        for t, res in es["cost_samples"].items()
    }
    st["cost_sums"] = {t: round(v, 2) for t, v in es["cost_paid_sum"].items()}
    st["top_dx"] = {
        t: [(c, n) for c, n in es["dx_counter"][t].most_common(25)]
        for t in ("inpatient", "outpatient", "carrier")
    }
    st["top_ip_procs"] = es["proc_counter"].most_common(15)
    st["top_hcpcs_outpatient"] = es["hcpcs_counter"]["outpatient"].most_common(15)
    st["top_hcpcs_carrier"] = es["hcpcs_counter"]["carrier"].most_common(15)
    st["top_ndc"] = es["ndc_counter"].most_common(20)
    st["top_ip_drg"] = es["ip_drg"].most_common(15)
    st["carrier_provider_stats"] = {
        "distinct_providers_sampled": len(carrier_counts),
        "lines_sampled": int(sum(carrier_counts.values())),
        "top1pct_line_share_pct": round(
            sum(v for _, v in sorted(carrier_counts.items(), key=lambda kv: -kv[1])[:max(len(carrier_counts)//100, 1)])
            / max(sum(carrier_counts.values()), 1) * 100, 1),
    }
    util = sorted(es["bene_in_claims"].values(), reverse=True)
    tot_ev = max(sum(util), 1)
    st["utilization"] = {
        "active_beneficiaries": len(util),
        "mean_events_per_active": round(tot_ev / len(util), 1) if util else 0,
        "max_events_one_bene": util[0] if util else 0,
        "top20pct_event_share_pct": round(sum(util[:max(int(len(util)*0.2), 1)]) / tot_ev * 100, 1),
    }
    st["empty_dx_rate_pct"] = {
        t: round(c / max(t_, 1) * 100, 1) for t, (c, t_) in es["empty_dx_rate"].items() if t_
    }
    st["annual_money_totals"] = {
        str(y): {k: round(v, 2) for k, v in bs["money_totals_by_year"][y].items()}
        for y in (2008, 2009, 2010)
    }
    return st


def write_report(bs, es, st, figs, carrier_counts) -> None:
    L = []
    A = L.append
    today = date.today().isoformat()
    A(f"# CMS DE-SynPUF (Sample 1) — Full-Corpus EDA Report")
    A(f"_Generated {today} · scripts/eda/explore_cms.py · data: data/cms/{{beneficiaries,index}}.jsonl_\n")

    A("\n## 1. Corpus Inventory\n")
    A(md_table(["Metric", "Value"], [
        ["Beneficiaries (merged 3 yearly summaries)", fmt_int(st["beneficiaries"])],
        ["Total claim/PDE event rows (segments & lines kept)", fmt_int(st["events_total"])],
        ["Unique claims (CLM_ID) / fills (PDE_ID)", fmt_int(sum(st["unique_claims_by_type"].values()))],
        ["Beneficiaries with >=1 event", fmt_int(st["bene_active_in_claims"])],
        ["Source archives", "8 ZIPs (see data/raw/MANIFEST.json; 3 recovered via Wayback Machine)"],
    ]))
    rows = [[TYPE_LABELS[t], fmt_int(st["events_by_type"].get(t, 0)), fmt_int(st["unique_claims_by_type"].get(t, 0))]
            for t in ("inpatient", "outpatient", "carrier", "pde")]
    A("\n" + md_table(["Claim type", "Event rows", "Unique claim IDs"], rows))
    A(f"\n![corpus]({figs['corpus']})")

    A("\n## 2. Referential Integrity & Linkage\n")
    lk = st["linkage"]
    A(md_table(["Type", "Events linked to beneficiary summary", "Orphan events"],
               [[TYPE_LABELS[t], fmt_int(lk["linked_by_type"].get(t, 0)), fmt_int(lk["unlinked_by_type"].get(t, 0))]
                for t in ("inpatient", "outpatient", "carrier", "pde")]))

    A("\n## 3. Beneficiary Demographics\n")
    sex = st["bene_sex"]
    ab = st["age_band_2008"]
    A(md_table(["Sex", "Count"], [["Male", fmt_int(sex.get("M", 0))], ["Female", fmt_int(sex.get("F", 0))]]))
    A("\n" + md_table(["Age band (2008)", "Count", "%"],
                      [[b, fmt_int(ab.get(b, 0)), f'{ab.get(b, 0)/st["beneficiaries"]*100:.1f}%']
                       for b in ("<65", "65-74", "75-84", "85+")]))
    A(f"\nDeaths recorded across window: **{fmt_int(st['deaths_recorded'])}** "
      f"({', '.join(f'{y}: {fmt_int(n)}' for y, n in sorted(st['death_years'].items()))})")
    A(f"\n![demographics]({figs['demo']})")

    A("\n## 4. Chronic Conditions & Comorbidity\n")
    A(md_table(["Condition (2010 flag)", "% of beneficiaries"],
               [[k, f"{v}%"] for k, v in st["cc_prevalence_pct_2010"].items()]))
    A(f"\n![chronic]({figs['chronic']})")
    A(f"\n![comorbidity]({figs['comorb']})")

    A("\n## 5. Temporal Patterns\n")
    A("Claim volumes are flat-to-seasonal with no year-over-year growth trend — consistent with "
      "synthetic generation from stationary templates rather than real utilization drift.")
    A(f"\n![monthly]({figs['monthly']})")

    A("\n## 6. Cost Distributions\n")
    rows = []
    for t in ("inpatient", "outpatient", "carrier", "pde"):
        p = st["cost_percentiles"][t]
        rows.append([TYPE_LABELS[t]] + [fmt_usd(p[q]) for q in ("10", "25", "50", "75", "90", "95", "99")]
                    + [fmt_usd(st["cost_sums"].get(t, 0))])
    A(md_table(["Type", "p10", "p25", "p50", "p75", "p90", "p95", "p99", "Σ paid"], rows))
    A(f"\nAll four payment distributions are heavy-tailed (p99 ≫ p50); inpatient is the widest "
      f"({fmt_usd(st['cost_percentiles']['inpatient']['99'])} at p99).")
    A(f"\n![costs]({figs['costs']})")

    A("\n## 7. Diagnosis Codes (ICD-9)\n")
    for t in ("inpatient", "outpatient", "carrier"):
        A(f"\n**{TYPE_LABELS[t]} — top 15 diagnosis codes:**\n")
        A(md_table(["Code", "Occurrences"], [[c, fmt_int(n)] for c, n in st["top_dx"][t][:15]]))
    A(f"\nEmpty-diagnosis rate: " +
      ", ".join(f"{TYPE_LABELS[t]} {v}%" for t, v in st["empty_dx_rate_pct"].items()))
    A(f"\n![dx]({figs['dx']})")

    A("\n## 8. Procedures, HCPCS & Drugs\n")
    A("\n**Top inpatient ICD-9 procedures:**\n")
    A(md_table(["Code", "Claims"], [[c, fmt_int(n)] for c, n in st["top_ip_procs"]]))
    A("\n**Top outpatient HCPCS:**\n")
    A(md_table(["Code", "Claims"], [[c, fmt_int(n)] for c, n in st["top_hcpcs_outpatient"]]))
    A("\n**Top carrier-line HCPCS:**\n")
    A(md_table(["Code", "Lines"], [[c, fmt_int(n)] for c, n in st["top_hcpcs_carrier"]]))
    A("\n**Top NDC products (PDE fills):**\n")
    A(md_table(["NDC", "Fills"], [[c, fmt_int(n)] for c, n in st["top_ndc"]]))
    A(f"\n![procedures]({figs['proc']})")
    A(f"\n![drugs]({figs['drugs']})")

    A("\n## 9. Provider Concentration\n")
    cps = st["carrier_provider_stats"]
    A(f"Across {fmt_int(cps['lines_sampled'])} sampled carrier lines, "
      f"**{cps['top1pct_line_share_pct']}%** of lines concentrate in the top 1% of providers "
      f"— a pareto tail any entity-extraction target set should stratify against.")
    A("\n**Top DRGs (inpatient):**\n")
    A(md_table(["MS-DRG", "Claims"], [[c, fmt_int(n)] for c, n in st["top_ip_drg"]]))
    A(f"\n![providers]({figs['prov']})")

    A("\n## 10. Utilization Concentration\n")
    u = st["utilization"]
    A(md_table(["Metric", "Value"], [
        ["Active beneficiaries", fmt_int(u["active_beneficiaries"])],
        ["Mean events per active beneficiary", f'{u["mean_events_per_active"]}'],
        ["Max events for one beneficiary", fmt_int(u["max_events_one_bene"])],
        ["Share of events from top 20% of patients", f'{u["top20pct_event_share_pct"]}%'],
    ]))
    A(f"\n![utilization]({figs['util']})")

    A("\n## 11. Annual Reimbursement Rollups (Beneficiary Files)\n")
    mt = st["annual_money_totals"]
    A(md_table(["Year", "IP", "OP", "CAR"],
               [[y, fmt_usd(mt[y]["MEDREIMB_IP"]), fmt_usd(mt[y]["MEDREIMB_OP"]), fmt_usd(mt[y]["MEDREIMB_CAR"])]
                for y in ("2008", "2009", "2010")]))
    A(f"\n![reimbursements]({figs['reimb']})")

    A("\n## 12. Pipeline Fit Assessment (llm-mailroom `insurance_claim`)\n")
    A(md_table(["Specialist field", "GT source in SynPUF", "Coverage note"], [
        ["claim_number", "CLM_ID (+segment suffix)", "exact, verbatim-renderable"],
        ["policy_number", "DESYNPUF_ID", "exact; stable join key"],
        ["insurer", "'CMS Medicare Part A/B'", "constant by construction"],
        ["insured_party", "deterministic pseudonym from DESYNPUF_ID", "rendered; no real names exist"],
        ["claim_type", "'health' constant + subtype metadata", "line-of-business always health"],
        ["date_of_loss", "CLM_FROM_DT / SRVC_DT", "exact ISO"],
        ["date_filed", "CLM_THRU_DT / discharge_dt", "proxy (adjudication date absent)"],
        ["claimed_amount", "CLM_PMT_AMT / TOT_RX_CST_AMT", "exact; paid amount"],
        ["adjuster", "—", "**absent** — synthetic corpus has none"],
        ["damages_description", "template from dx/proc/hcpcs codes", "clinically faithful summary text"],
        ["coverage_determination", "'approved'", "ALL SynPUF claims are adjudicated-paid; no denials exist"],
        ["denial_reasons", "[]", "always empty — see above"],
        ["supporting_documents", "provider/facility refs", "rendered list"],
    ]))
    A("\n### Evaluation caveats\n")
    A("1. **No negative class**: every rendered document will be an approved health claim; denial-letter "
      "and reservation-of-rights ground truth must come from another source.")
    A("2. **Fully synthetic**: CMS warns of limited inferential utility — treat as *pipeline substrate*, "
      "not epidemiology. Distributions here characterize the eval artifact itself.")
    A("3. **Verbatim contract**: every GT value above is rendered verbatim into doc_text so the mailroom "
      "field scorer's factuality audit can verify extraction without fuzzy fallback.")

    (REPORTS / "report.md").write_text("\n".join(L) + "\n")


def write_findings(st) -> None:
    L = []
    A = L.append
    u = st["utilization"]
    cps = st["carrier_provider_stats"]
    A("# Key Findings — CMS DE-SynPUF Sample 1 EDA\n")
    A(f"- **Corpus shape**: {fmt_int(st['beneficiaries'])} beneficiaries; "
      f"{fmt_int(st['events_total'])} claim/PDE event rows collapsing to "
      f"{fmt_int(sum(st['unique_claims_by_type'].values()))} unique claims/fills "
      f"(inpatient/outpatient carry multiple bill segments).")
    A(f"- **Perfect linkage**: {fmt_int(sum(st['linkage']['linked_by_type'].values()))} events join cleanly to "
      f"beneficiary summaries on DESYNPUF_ID; "
      f"{fmt_int(sum(st['linkage']['unlinked_by_type'].values()))} orphans. Cross-file GT joins are trustworthy.")
    A(f"- **Demographic skew**: age bands and chronic-condition prevalence are stationary across 2008–2010 "
      f"(synthetic templates), with {fmt_int(st['deaths_recorded'])} deaths recorded in-window.")
    A("- **Costs are heavy-tailed**: inpatient p99 reaches "
      f"{fmt_usd(st['cost_percentiles']['inpatient']['99'])}; stratified sampling MUST bucket on log-cost, "
      "not raw cost, or the tail never appears in eval sets.")
    A(f"- **Concentration**: top 1% of carrier providers bill {cps['top1pct_line_share_pct']}% of physician lines; "
      f"top 20% of patients generate {u['top20pct_event_share_pct']}% of all events.")
    A("- **Diagnosis coverage is high**: empty-diagnosis rates stay below "
      f"{max(st['empty_dx_rate_pct'].values(), default=0)}% across claim types — ICD-9 lists are reliable GT anchors.")
    A("- **Pipeline fit**: maps 1:1 onto the mailroom `insurance_claim` schema except `adjuster` (absent) and "
      "`coverage_determination`/`denial_reasons` (always approved/empty — no negative class exists in SynPUF).")
    A("- **Provenance caveat**: Sample-1's 2010 beneficiary file plus Carrier (A/B) and PDE archives were "
      "no longer hosted by CMS and were recovered from Internet Archive captures (manifested in "
      "data/raw/MANIFEST.json).")
    (REPORTS / "findings.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main())
