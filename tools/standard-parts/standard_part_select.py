#!/usr/bin/env python3
"""Select standard CAD parts from step.parts with engineering filters.

This is a small prototype for an agent-facing standard-part selection layer.
It deliberately avoids fuzzy ranking alone: first query step.parts, then filter
structured attributes such as thread, length, family, category, and tags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ORIGIN = "https://api.step.parts"


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def query_parts(
    origin: str,
    query: str | None,
    page_size: int,
    category: str | None = None,
    family: str | None = None,
    tag: list[str] | None = None,
    standard: str | None = None,
) -> dict[str, Any]:
    params: list[tuple[str, str | int]] = [("pageSize", page_size)]
    if query:
        params.append(("q", query))
    if category:
        params.append(("category", category))
    if family:
        params.append(("family", family))
    if standard:
        params.append(("standard", standard))
    for value in tag or []:
        params.append(("tag", value))
    url = f"{origin.rstrip('/')}/v1/parts?{urllib.parse.urlencode(params)}"
    return fetch_json(url)


def get_nested(record: dict[str, Any], dotted_key: str) -> Any:
    value: Any = record
    for part in dotted_key.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def normalize(value: Any) -> str:
    return str(value).strip().lower()


def matches(record: dict[str, Any], filters: dict[str, str]) -> bool:
    for key, expected in filters.items():
        actual = get_nested(record, key)
        if normalize(actual) != normalize(expected):
            return False
    return True


def rank_record(record: dict[str, Any], preferred_lengths: set[float]) -> tuple[int, str]:
    score = 0
    attrs = record.get("attributes") or {}
    if "lengthMm" in attrs:
        try:
            if float(attrs["lengthMm"]) in preferred_lengths:
                score -= 20
        except (TypeError, ValueError):
            pass
    if record.get("standard"):
        score -= 5
    if record.get("stepUrl"):
        score -= 3
    return score, record.get("id", "")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_step(record: dict[str, Any], out_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    step_url = record.get("stepUrl")
    if not step_url:
        raise ValueError(f"record {record.get('id')} has no stepUrl")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{record['id']}.step"
    if out_path.exists() and not overwrite:
        file_hash = sha256_file(out_path)
    else:
        with urllib.request.urlopen(step_url, timeout=60) as response:
            out_path.write_bytes(response.read())
        file_hash = sha256_file(out_path)
    expected_hash = record.get("sha256")
    return {
        "path": str(out_path),
        "sha256": file_hash,
        "expectedSha256": expected_hash,
        "checksumVerified": expected_hash is None or file_hash == expected_hash,
    }


def parse_filter(values: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"Invalid --filter value {item!r}; use dotted.key=value")
        key, value = item.split("=", 1)
        filters[key.strip()] = value.strip()
    return filters


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="step.parts text query, e.g. 'M2 screw'")
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--category")
    parser.add_argument("--family")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--standard")
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Structured exact filter, e.g. attributes.thread=M2",
    )
    parser.add_argument(
        "--prefer-length",
        action="append",
        type=float,
        default=[],
        help="Preferred lengthMm value for ranking.",
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--out-dir", default="standard-parts-downloads")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    data = query_parts(
        origin=args.origin,
        query=args.query,
        page_size=args.page_size,
        category=args.category,
        family=args.family,
        tag=args.tag,
        standard=args.standard,
    )
    filters = parse_filter(args.filter)
    records = [item for item in data.get("items", []) if matches(item, filters)]
    preferred_lengths = set(args.prefer_length)
    records.sort(key=lambda item: rank_record(item, preferred_lengths))
    selected = records[: args.limit]

    output: dict[str, Any] = {
        "query": args.query,
        "catalog": data.get("catalog"),
        "apiTotal": data.get("total"),
        "filters": {
            "category": args.category,
            "family": args.family,
            "tag": args.tag,
            "standard": args.standard,
            "structured": filters,
        },
        "matched": len(records),
        "items": selected,
    }
    if args.download:
        out_dir = Path(args.out_dir)
        output["downloads"] = [
            download_step(record, out_dir=out_dir, overwrite=args.overwrite)
            for record in selected
        ]

    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
