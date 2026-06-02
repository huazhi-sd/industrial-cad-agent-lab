"""Inspect STEP geometry with FreeCAD.

Run with FreeCAD's bundled Python or FreeCADCmd:

    python.exe tools/freecad/inspect_step.py input.step --json out.json
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import FreeCAD as App  # type: ignore
import Part  # type: ignore


def _round(value: float) -> float:
    return round(float(value), 6)


def _bbox_dict(bound_box: Any) -> dict[str, Any]:
    return {
        "x": [_round(bound_box.XMin), _round(bound_box.XMax)],
        "y": [_round(bound_box.YMin), _round(bound_box.YMax)],
        "z": [_round(bound_box.ZMin), _round(bound_box.ZMax)],
        "dimensions": {
            "x": _round(bound_box.XLength),
            "y": _round(bound_box.YLength),
            "z": _round(bound_box.ZLength),
        },
    }


def _shape_metrics(shape: Any) -> dict[str, Any]:
    return {
        "bbox": _bbox_dict(shape.BoundBox),
        "volume": _round(shape.Volume),
        "area": _round(shape.Area),
        "solids": len(shape.Solids),
        "shells": len(shape.Shells),
        "faces": len(shape.Faces),
        "edges": len(shape.Edges),
        "vertices": len(shape.Vertexes),
        "is_null": bool(shape.isNull()),
        "is_valid": bool(shape.isValid()),
    }


def _check_close(actual: float, expected: float, tolerance: float) -> bool:
    return abs(actual - expected) <= tolerance


def _validation_result(
    report: dict[str, Any],
    expect_solids: int | None,
    expect_bbox: list[float] | None,
    bbox_tolerance: float,
    fail_on_invalid: bool,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    shape = report["shape"]

    if expect_solids is not None:
        actual = int(shape["solids"])
        checks.append(
            {
                "name": "solid_count",
                "status": "pass" if actual == expect_solids else "fail",
                "expected": expect_solids,
                "actual": actual,
            }
        )

    if expect_bbox is not None:
        dims = shape["bbox"]["dimensions"]
        actual_dims = [float(dims["x"]), float(dims["y"]), float(dims["z"])]
        for axis, actual, expected in zip(["x", "y", "z"], actual_dims, expect_bbox):
            checks.append(
                {
                    "name": f"bbox_{axis}",
                    "status": "pass" if _check_close(actual, expected, bbox_tolerance) else "fail",
                    "expected": expected,
                    "actual": actual,
                    "tolerance": bbox_tolerance,
                }
            )

    if fail_on_invalid:
        checks.append(
            {
                "name": "shape_validity",
                "status": "pass" if shape["is_valid"] else "fail",
                "expected": True,
                "actual": bool(shape["is_valid"]),
            }
        )
        for solid in report["solids"]:
            checks.append(
                {
                    "name": f"solid_{solid['index']}_validity",
                    "status": "pass" if solid["is_valid"] else "fail",
                    "expected": True,
                    "actual": bool(solid["is_valid"]),
                }
            )

    failed = [check for check in checks if check["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "check_count": len(checks),
        "failed_count": len(failed),
        "checks": checks,
    }


def inspect_step(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    shape = Part.Shape()
    shape.read(str(path))

    solids = []
    for index, solid in enumerate(shape.Solids):
        solids.append(
            {
                "index": index,
                **_shape_metrics(solid),
            }
        )

    return {
        "tool": "freecad-inspect-step",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "freecad_version": App.Version(),
        "input": {
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "extension": path.suffix.lower(),
            "contains_non_ascii_path": any(ord(ch) > 127 for ch in str(path)),
        },
        "shape": _shape_metrics(shape),
        "solids": solids,
    }


def write_markdown(report: dict[str, Any], output: Path) -> None:
    shape = report["shape"]
    dims = shape["bbox"]["dimensions"]
    validation = report.get("validation")
    lines = [
        "# STEP Inspection Report",
        "",
        f"- Input: `{report['input']['path']}`",
        f"- FreeCAD: `{report['freecad_version']}`",
        f"- File size: `{report['input']['size_bytes']}` bytes",
        f"- Non-ASCII path: `{report['input']['contains_non_ascii_path']}`",
        "",
        "## Overall Shape",
        "",
        f"- Solids: `{shape['solids']}`",
        f"- Shells: `{shape['shells']}`",
        f"- Faces: `{shape['faces']}`",
        f"- Edges: `{shape['edges']}`",
        f"- Vertices: `{shape['vertices']}`",
        f"- Valid: `{shape['is_valid']}`",
        f"- Volume: `{shape['volume']}` mm^3",
        f"- Area: `{shape['area']}` mm^2",
        f"- Bounding box: `{dims['x']} x {dims['y']} x {dims['z']}` mm",
        "",
    ]

    if validation:
        lines.extend(
            [
                "## Validation",
                "",
                f"- Status: `{validation['status']}`",
                f"- Checks: `{validation['check_count']}`",
                f"- Failed: `{validation['failed_count']}`",
                "",
                "| Check | Status | Expected | Actual |",
                "| --- | :---: | ---: | ---: |",
            ]
        )
        for check in validation["checks"]:
            lines.append(
                "| {name} | {status} | {expected} | {actual} |".format(
                    name=check["name"],
                    status=check["status"],
                    expected=check["expected"],
                    actual=check["actual"],
                )
            )
        lines.append("")

    lines.extend(
        [
        "## Solids",
        "",
        "| Index | Valid | BBox X | BBox Y | BBox Z | Volume | Faces | Edges |",
        "| ---: | :---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for solid in report["solids"]:
        solid_dims = solid["bbox"]["dimensions"]
        lines.append(
            "| {index} | {valid} | {x} | {y} | {z} | {volume} | {faces} | {edges} |".format(
                index=solid["index"],
                valid="yes" if solid["is_valid"] else "no",
                x=solid_dims["x"],
                y=solid_dims["y"],
                z=solid_dims["z"],
                volume=solid["volume"],
                faces=solid["faces"],
                edges=solid["edges"],
            )
        )

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if os.environ.get("FREECAD_INSPECT_DEBUG_ARGV") == "1":
        print("sys.argv:", repr(sys.argv))
        print("argv:", repr(argv))

    if argv and len(argv) == 1 and (" --" in argv[0] or " -" in argv[0]):
        argv = shlex.split(argv[0], posix=False)

    parser = argparse.ArgumentParser(description="Inspect STEP/STP files with FreeCAD.")
    parser.add_argument("input", help="STEP/STP file path")
    parser.add_argument("--json", dest="json_output", help="Optional JSON output path")
    parser.add_argument("--md", dest="md_output", help="Optional Markdown output path")
    parser.add_argument("--expect-solids", type=int, help="Fail if the STEP solid count differs")
    parser.add_argument(
        "--expect-bbox",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        help="Expected overall bounding-box dimensions in mm",
    )
    parser.add_argument("--bbox-tol", type=float, default=0.05, help="Bounding-box tolerance in mm")
    parser.add_argument("--fail-on-invalid", action="store_true", help="Fail if the shape or any solid is invalid")
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    report = inspect_step(input_path)
    report["validation"] = _validation_result(
        report=report,
        expect_solids=args.expect_solids,
        expect_bbox=args.expect_bbox,
        bbox_tolerance=args.bbox_tol,
        fail_on_invalid=args.fail_on_invalid,
    )

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)

    if args.json_output:
        json_path = Path(args.json_output).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(text + "\n", encoding="utf-8")

    if args.md_output:
        md_path = Path(args.md_output).expanduser().resolve()
        md_path.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, md_path)

    return 0 if report["validation"]["status"] == "pass" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception:
        traceback.print_exc()
        raise
