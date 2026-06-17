from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def summarize_values(values: Any) -> dict[str, Any]:
    flat: list[float] = []

    def collect(item: Any) -> None:
        if hasattr(item, "tolist"):
            collect(item.tolist())
            return
        if isinstance(item, (list, tuple)):
            for sub in item:
                collect(sub)
            return
        try:
            value = float(item)
        except Exception:
            return
        if math.isfinite(value):
            flat.append(value)

    collect(values)

    if not flat:
        return {"count": 0, "min": None, "max": None, "mean": None}

    return {
        "count": len(flat),
        "min": min(flat),
        "max": max(flat),
        "mean": sum(flat) / len(flat),
    }


def run(mph_path: Path, output_dir: Path, cores: int, comsol_bin: str) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_report = output_dir / f"ssd_enclosure_esd_results_{stamp}.json"

    report: dict[str, Any] = {
        "schema": "ssd_enclosure_comsol_esd_results.v0",
        "timestamp": stamp,
        "source_mph": str(mph_path),
        "status": "started",
        "expressions": {},
        "warnings": [
            "Field values are first-pass sampled COMSOL expression evaluations, not certified breakdown margins.",
            "Maximum electric field may be mesh-dependent and can spike at sharp CAD edges.",
        ],
    }

    client = mph.Client(cores=cores, version="6.3")
    model = None
    try:
        model = client.load(str(mph_path))
        for expr, unit in [("V", "V"), ("es.normE", "V/m")]:
            try:
                values = model.evaluate(expr, unit=unit)
                report["expressions"][expr] = {
                    "unit": unit,
                    "status": "success",
                    **summarize_values(values),
                }
            except Exception as exc:
                report["expressions"][expr] = {
                    "unit": unit,
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
        report["status"] = "success"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        out_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                try:
                    client.clear()
                except Exception:
                    pass

    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mph", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    args = parser.parse_args()
    report = run(args.mph.resolve(), args.out.resolve(), args.cores, args.comsol_bin)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
