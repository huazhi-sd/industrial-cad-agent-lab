from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run_step(label: str, args: list[str], cwd: Path) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(
        [sys.executable, *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
    )
    report = {
        "label": label,
        "args": args,
        "returncode": proc.returncode,
        "duration_s": round(time.time() - started, 3),
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }
    if proc.returncode != 0:
        raise RuntimeError(f"{label} failed with code {proc.returncode}:\n{proc.stderr[-4000:]}")
    return report


def latest_file(directory: Path, pattern: str, since: float) -> Path:
    candidates = [
        item
        for item in directory.glob(pattern)
        if item.is_file() and item.stat().st_mtime >= since - 1.0
    ]
    if not candidates:
        raise FileNotFoundError(f"No file matching {pattern} in {directory} after timestamp {since}")
    return max(candidates, key=lambda item: item.stat().st_mtime)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_pipeline(
    workflow_dir: Path,
    step_path: Path,
    manifest_path: Path,
    output_dir: Path,
    delivery_dir: Path | None,
    cores: int,
    comsol_bin: str,
    mesh_size: int,
    tolerance: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pipeline_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_dir = workflow_dir / "source"

    summary: dict[str, Any] = {
        "schema": "ssd_enclosure_comsol_esd_pipeline.v1",
        "timestamp": pipeline_stamp,
        "note": "This orchestrator intentionally launches each COMSOL/mph step in a separate Python process because mph allows only one client per Python session.",
        "step_path": str(step_path),
        "manifest_path": str(manifest_path),
        "output_dir": str(output_dir),
        "delivery_dir": str(delivery_dir) if delivery_dir else None,
        "steps": [],
        "status": "started",
    }

    step_started = time.time()
    summary["steps"].append(
        run_step(
            "step_import_union",
            [
                str(source_dir / "run_comsol_step_import_baseline.py"),
                "--step",
                str(step_path),
                "--out",
                str(output_dir),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
                "--finalization-action",
                "union",
            ],
            workflow_dir,
        )
    )
    baseline_report_path = latest_file(output_dir, "ssd_enclosure_step_import_baseline_*.json", step_started)
    baseline = read_json(baseline_report_path)
    baseline_mph = Path(baseline["mph_path"])

    mapping_path = output_dir / f"ssd_enclosure_measured_domain_mapping_union_{baseline['timestamp']}.json"
    summary["steps"].append(
        run_step(
            "measured_domain_mapping",
            [
                str(source_dir / "match_union_domains_by_measure.py"),
                "--mph",
                str(baseline_mph),
                "--manifest",
                str(manifest_path),
                "--output",
                str(mapping_path),
                "--tolerance",
                str(tolerance),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
            ],
            workflow_dir,
        )
    )
    mapping = read_json(mapping_path)

    step_started = time.time()
    summary["steps"].append(
        run_step(
            "domain_material_mapping",
            [
                str(source_dir / "apply_comsol_domain_mapping.py"),
                "--mph",
                str(baseline_mph),
                "--mapping",
                str(mapping_path),
                "--out",
                str(output_dir),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
            ],
            workflow_dir,
        )
    )
    material_report_path = latest_file(output_dir, "ssd_enclosure_material_selections_*.json", step_started)
    materials = read_json(material_report_path)
    material_mph = Path(materials["output_mph"])

    step_started = time.time()
    summary["steps"].append(
        run_step(
            "boundary_probe",
            [
                str(source_dir / "probe_comsol_boundary_mapping.py"),
                "--mph",
                str(material_mph),
                "--material-report",
                str(material_report_path),
                "--out",
                str(output_dir),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
            ],
            workflow_dir,
        )
    )
    boundary_probe_path = latest_file(output_dir, "ssd_enclosure_boundary_probe_*.json", step_started)

    step_started = time.time()
    summary["steps"].append(
        run_step(
            "boundary_conditions",
            [
                str(source_dir / "apply_comsol_esd_boundary_conditions.py"),
                "--mph",
                str(material_mph),
                "--boundary-probe",
                str(boundary_probe_path),
                "--out",
                str(output_dir),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
            ],
            workflow_dir,
        )
    )
    boundary_conditions_path = latest_file(output_dir, "ssd_enclosure_esd_boundary_conditions_*.json", step_started)
    boundary_conditions = read_json(boundary_conditions_path)
    boundary_mph = Path(boundary_conditions["output_mph"])

    step_started = time.time()
    summary["steps"].append(
        run_step(
            "mesh_and_stationary_solve",
            [
                str(source_dir / "run_comsol_esd_stationary_solve.py"),
                "--mph",
                str(boundary_mph),
                "--out",
                str(output_dir),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
                "--mesh-size",
                str(mesh_size),
            ],
            workflow_dir,
        )
    )
    solved_report_path = latest_file(output_dir, "ssd_enclosure_esd_stationary_solved_*.json", step_started)
    solved = read_json(solved_report_path)
    solved_mph = Path(solved["output_mph"])

    step_started = time.time()
    summary["steps"].append(
        run_step(
            "result_extraction",
            [
                str(source_dir / "extract_comsol_esd_results.py"),
                "--mph",
                str(solved_mph),
                "--out",
                str(output_dir),
                "--cores",
                str(cores),
                "--comsol-bin",
                comsol_bin,
            ],
            workflow_dir,
        )
    )
    results_report_path = latest_file(output_dir, "ssd_enclosure_esd_results_*.json", step_started)
    results = read_json(results_report_path)

    summary["reports"] = {
        "baseline": str(baseline_report_path),
        "mapping": str(mapping_path),
        "materials": str(material_report_path),
        "boundary_probe": str(boundary_probe_path),
        "boundary_conditions": str(boundary_conditions_path),
        "solve": str(solved_report_path),
        "results": str(results_report_path),
    }
    summary["domain_count"] = baseline["geometry"]["domains"]
    summary["boundary_count"] = baseline["geometry"]["boundaries"]
    summary["all_product_matched"] = mapping["all_product_matched"]
    summary["final_mph"] = str(solved_mph)
    summary["field_summary"] = results.get("expressions", {})

    if delivery_dir:
        delivery_dir.mkdir(parents=True, exist_ok=True)
        for child in delivery_dir.iterdir():
            if child.is_file():
                try:
                    child.unlink()
                except PermissionError:
                    summary.setdefault("warnings", []).append(f"Could not remove locked delivery file: {child}")
        delivery_mph = delivery_dir / f"ssd_enclosure_esd_baseline_{pipeline_stamp}.mph"
        shutil.copy2(solved_mph, delivery_mph)
        summary["delivery_mph"] = str(delivery_mph)

    summary["status"] = "success"
    summary_path = output_dir / f"ssd_enclosure_esd_pipeline_{pipeline_stamp}.json"
    write_json(summary_path, summary)
    summary["summary_path"] = str(summary_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=Path, default=Path("transparent_pc_m2_2280_ssd_enclosure_assembly.step"))
    parser.add_argument("--manifest", type=Path, default=Path("ssd_enclosure_esd_manifest.json"))
    parser.add_argument("--out", type=Path, default=Path("comsol/baseline-runs"))
    parser.add_argument("--delivery-dir", type=Path, default=None)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    parser.add_argument("--mesh-size", type=int, default=8)
    parser.add_argument("--tolerance", type=float, default=0.1)
    args = parser.parse_args()

    workflow_dir = Path(__file__).resolve().parents[1]
    summary = run_pipeline(
        workflow_dir=workflow_dir,
        step_path=(workflow_dir / args.step).resolve() if not args.step.is_absolute() else args.step.resolve(),
        manifest_path=(workflow_dir / args.manifest).resolve() if not args.manifest.is_absolute() else args.manifest.resolve(),
        output_dir=(workflow_dir / args.out).resolve() if not args.out.is_absolute() else args.out.resolve(),
        delivery_dir=args.delivery_dir.resolve() if args.delivery_dir else None,
        cores=args.cores,
        comsol_bin=args.comsol_bin,
        mesh_size=args.mesh_size,
        tolerance=args.tolerance,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
