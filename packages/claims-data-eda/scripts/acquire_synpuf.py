#!/usr/bin/env python3
"""Acquire the CMS 2008-2010 DE-SynPUF, Sample 1 (all 5 file types / 8 ZIPs).

Sources, verified 2026-08:
  * 4 archives still served live from the legacy CMS SynPUFs path.
  * Sample-1's 2010 Beneficiary Summary, Carrier Claims (A/B split), and
    Prescription Drug Events are gone from CMS's servers entirely -- they are
    recovered from Internet Archive Wayback Machine captures of the original
    downloads.cms.gov / www.cms.gov locations.

Every archive is sha256-manifested (data/raw/MANIFEST.json) and zip-tested
before extraction. Idempotent: verified files are skipped; interrupted
downloads resume (only when the server honors byte ranges).

Usage:
    python scripts/acquire_synpuf.py            # full run
    python scripts/acquire_synpuf.py --dry-run  # list sources, probe remote
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

import urllib.request

CMS_BASE = (
    "https://www.cms.gov/Research-Statistics-Data-and-Systems/"
    "Downloadable-Public-Use-Files/SynPUFs/Downloads"
)
CDN_BASE = "http://downloads.cms.gov/files"

def _cms(name: str) -> str:
    return f"{CMS_BASE}/{name}"

def _wayback(ts: str, original: str) -> str:
    # id_ suffix serves the original bytes without wayback banner injection.
    return f"https://web.archive.org/web/{ts}id_/{original}"

FILES: dict[str, list[str]] = {
    # name -> candidate URLs in priority order (first success wins)
    "DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip": [_cms("DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip")],
    "DE1_0_2009_Beneficiary_Summary_File_Sample_1.zip": [_cms("DE1_0_2009_Beneficiary_Summary_File_Sample_1.zip")],
    "DE1_0_2010_Beneficiary_Summary_File_Sample_1.zip": [
        _wayback("20170529061306", _cms("DE1_0_2010_Beneficiary_Summary_File_Sample_1.zip")),
        f"{CDN_BASE}/DE1_0_2010_Beneficiary_Summary_File_Sample_1.zip",
    ],
    "DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.zip": [
        _cms("DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.zip")
    ],
    "DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.zip": [
        _cms("DE1_0_2008_to_2010_Outpatient_Claims_Sample_1.zip")
    ],
    "DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip": [
        _wayback("20130516184110", f"{CDN_BASE}/DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip"),
    ],
    "DE1_0_2008_to_2010_Carrier_Claims_Sample_1B.zip": [
        _wayback("20130516184434", f"{CDN_BASE}/DE1_0_2008_to_2010_Carrier_Claims_Sample_1B.zip"),
    ],
    "DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_1.zip": [
        _wayback("2013", f"{CDN_BASE}/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_1.zip"),
        f"{CDN_BASE}/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_1.zip",
        _cms("DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_1.zip"),
    ],
}

REPO = Path(__file__).resolve().parents[1]
RAW_DIR = REPO / "data" / "raw"
MANIFEST_PATH = RAW_DIR / "MANIFEST.json"
CHUNK = 1 << 20
UA = {"User-Agent": "claims-data-eda/0.1 (research; synthetic public data)"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"acquired_utc": None, "files": {}}


def save_manifest(m: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(m, indent=2, sort_keys=True) + "\n")


def probe(url: str) -> int | None:
    req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-30"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            cr = resp.headers.get("Content-Range")
            if cr and "/" in cr:
                return int(cr.rsplit("/", 1)[1])
            cl = resp.headers.get("Content-Length")
            return int(cl) if cl else None
    except OSError:
        return None


def download(urls: list[str], dest: Path) -> tuple[str, int]:
    """Try each url until one yields a complete file at dest."""
    last_err: Exception | None = None
    for url in urls:
        part = dest.with_suffix(dest.suffix + ".part")
        try:
            for attempt in range(4):
                try:
                    offset = part.stat().st_size if part.exists() else 0
                    headers = {**UA}
                    if offset:
                        headers["Range"] = f"bytes={offset}-"
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=180) as resp:
                        resumed = offset > 0 and getattr(resp, "status", 200) == 206
                        mode = "ab" if resumed else "wb"
                        t0 = time.time()
                        with part.open(mode) as out:
                            while True:
                                chunk = resp.read(CHUNK)
                                if not chunk:
                                    break
                                out.write(chunk)
                    break
                except OSError as exc:
                    print(f"    retry {attempt + 1}/4: {exc}", flush=True)
                    time.sleep(min(60, 5 * (attempt + 1)))
            else:
                raise RuntimeError("retries exhausted")
            # sanity: must be a readable zip
            with zipfile.ZipFile(part) as zf:
                bad = zf.testzip()
                if bad is not None:
                    raise RuntimeError(f"corrupt member {bad}")
            part.rename(dest)
            print(f"    ok ({dest.stat().st_size / 1048576:.1f} MB in {time.time() - t0:.0f}s)", flush=True)
            return url, time.time() - t0
        except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
            print(f"    source failed: {url}\n    -> {exc}", flush=True)
            last_err = exc
    raise RuntimeError(f"all sources failed for {dest.name}: {last_err}")


def extract(zip_path: Path, dest_dir: Path) -> list[str]:
    names = []
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            target = dest_dir / Path(info.filename).name
            if not target.exists() or target.stat().st_size != info.file_size:
                with zf.open(info) as src, target.open("wb") as out:
                    for chunk in iter(lambda: src.read(CHUNK), b""):
                        out.write(chunk)
            names.append(target.name)
    return sorted(names)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="probe sources without downloading")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    if args.dry_run:
        for name, urls in FILES.items():
            primary = probe(urls[0])
            print(f"{name}: {'%d MB' % (primary / 1048576) if primary else 'unreachable'} <- {urls[0]}")
        return 0

    for name, urls in FILES.items():
        dest = RAW_DIR / name
        entry = manifest["files"].get(name)
        if dest.exists() and entry and entry.get("size") == dest.stat().st_size:
            print(f"[skip] {name} already verified", flush=True)
            continue

        print(f"[get ] {name}", flush=True)
        url_used, _ = download(urls, dest)
        members = extract(dest, RAW_DIR)

        manifest["files"][name] = {
            "url": url_used,
            "size": dest.stat().st_size,
            "sha256": sha256_file(dest),
            "members": members,
        }
        manifest.setdefault("acquired_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        save_manifest(manifest)
        print(f"[done] {name} -> {', '.join(members)}", flush=True)

    n_ok = len(manifest["files"])
    print(f"\nACQUIRE COMPLETE: {n_ok}/{len(FILES)} archives verified under {RAW_DIR}")
    return 0 if n_ok == len(FILES) else 1


if __name__ == "__main__":
    sys.exit(main())
