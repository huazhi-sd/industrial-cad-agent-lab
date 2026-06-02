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


def _target_metrics(report: dict[str, Any], target: Any) -> dict[str, Any]:
    if target in (None, "shape", "overall"):
        return report["shape"]
    if target in ("all", "all_solids"):
        raise ValueError("Target all_solids is only valid for validity checks")
    if isinstance(target, dict) and "solid" in target:
        index = int(target["solid"])
        try:
            return report["solids"][index]
        except IndexError as exc:
            raise ValueError(f"Solid index out of range: {index}") from exc
    raise ValueError(f"Unsupported target: {target!r}")


def _bbox_dimension(metrics: dict[str, Any], axis: str) -> float:
    axis = axis.lower()
    if axis not in ("x", "y", "z"):
        raise ValueError(f"Unsupported bbox dimension axis: {axis}")
    return float(metrics["bbox"]["dimensions"][axis])


def _bbox_edge(metrics: dict[str, Any], edge: str) -> float:
    aliases = {
        "xmin": "x_min",
        "xmax": "x_max",
        "ymin": "y_min",
        "ymax": "y_max",
        "zmin": "z_min",
        "zmax": "z_max",
    }
    edge = aliases.get(edge.lower(), edge.lower())
    if edge not in ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max"):
        raise ValueError(f"Unsupported bbox edge: {edge}")
    axis, side = edge.split("_")
    values = metrics["bbox"][axis]
    return float(values[0] if side == "min" else values[1])


def _normalise_expected_bbox(value: Any) -> dict[str, float]:
    if isinstance(value, list):
        if len(value) != 3:
            raise ValueError("BBox list must contain exactly 3 values")
        return {"x": float(value[0]), "y": float(value[1]), "z": float(value[2])}
    if isinstance(value, dict):
        return {axis: float(value[axis]) for axis in ("x", "y", "z") if axis in value}
    raise ValueError("Expected bbox must be a list or object")


def _compare(actual: float, op: str, expected: float, tolerance: float) -> bool:
    if op == "==":
        return _check_close(actual, expected, tolerance)
    if op == "!=":
        return not _check_close(actual, expected, tolerance)
    if op == ">":
        return actual > expected - tolerance
    if op == ">=":
        return actual >= expected - tolerance
    if op == "<":
        return actual < expected + tolerance
    if op == "<=":
        return actual <= expected + tolerance
    raise ValueError(f"Unsupported comparison operator: {op}")


def _check_rule(report: dict[str, Any], rule: dict[str, Any]) -> list[dict[str, Any]]:
    rule_type = rule["type"]
    name = rule.get("name", rule_type)
    tolerance = float(rule.get("tolerance", rule.get("tol", 0.05)))

    if rule_type == "solid_count":
        actual = int(report["shape"]["solids"])
        expected = int(rule["expected"])
        return [
            {
                "name": name,
                "type": rule_type,
                "status": "pass" if actual == expected else "fail",
                "expected": expected,
                "actual": actual,
            }
        ]

    if rule_type == "bbox_dimensions":
        metrics = _target_metrics(report, rule.get("target"))
        expected_bbox = _normalise_expected_bbox(rule["expected"])
        checks = []
        for axis, expected in expected_bbox.items():
            actual = _bbox_dimension(metrics, axis)
            checks.append(
                {
                    "name": f"{name}_{axis}",
                    "type": rule_type,
                    "status": "pass" if _check_close(actual, expected, tolerance) else "fail",
                    "expected": expected,
                    "actual": actual,
                    "tolerance": tolerance,
                }
            )
        return checks

    if rule_type == "bbox_dimension_range":
        metrics = _target_metrics(report, rule.get("target"))
        axis = rule["axis"]
        actual = _bbox_dimension(metrics, axis)
        checks = []
        if "min" in rule:
            expected = float(rule["min"])
            checks.append(
                {
                    "name": f"{name}_{axis}_min",
                    "type": rule_type,
                    "status": "pass" if actual >= expected - tolerance else "fail",
                    "expected": f">= {expected}",
                    "actual": actual,
                    "tolerance": tolerance,
                }
            )
        if "max" in rule:
            expected = float(rule["max"])
            checks.append(
                {
                    "name": f"{name}_{axis}_max",
                    "type": rule_type,
                    "status": "pass" if actual <= expected + tolerance else "fail",
                    "expected": f"<= {expected}",
                    "actual": actual,
                    "tolerance": tolerance,
                }
            )
        return checks

    if rule_type == "bbox_edge_relation":
        a_metrics = _target_metrics(report, rule["a"])
        b_metrics = _target_metrics(report, rule["b"])
        a_value = _bbox_edge(a_metrics, rule["a_edge"])
        b_value = _bbox_edge(b_metrics, rule["b_edge"])
        op = rule.get("op", ">=")
        return [
            {
                "name": name,
                "type": rule_type,
                "status": "pass" if _compare(a_value, op, b_value, tolerance) else "fail",
                "expected": f"{rule['a_edge']} {op} {rule['b_edge']} ({b_value})",
                "actual": a_value,
                "tolerance": tolerance,
            }
        ]

    if rule_type == "validity":
        target = rule.get("target", "shape")
        checks = []
        if target in ("all", "all_solids"):
            items = [("shape", report["shape"])] + [
                (f"solid_{solid['index']}", solid) for solid in report["solids"]
            ]
        else:
            items = [(name, _target_metrics(report, target))]
        for item_name, metrics in items:
            checks.append(
                {
                    "name": item_name if item_name == name else f"{name}_{item_name}",
                    "type": rule_type,
                    "status": "pass" if metrics["is_valid"] else "fail",
                    "expected": True,
                    "actual": bool(metrics["is_valid"]),
                }
            )
        return checks

    raise ValueError(f"Unsupported rule type: {rule_type}")


def _rules_from_cli(
    expect_solids: int | None,
    expect_bbox: list[float] | None,
    bbox_tolerance: float,
    fail_on_invalid: bool,
) -> list[dict[str, Any]]:
    rules = []
    if expect_solids is not None:
        rules.append({"type": "solid_count", "name": "solid_count", "expected": expect_solids})
    if expect_bbox is not None:
        rules.append(
            {
                "type": "bbox_dimensions",
                "name": "overall_bbox",
                "target": "shape",
                "expected": expect_bbox,
                "tolerance": bbox_tolerance,
            }
        )
    if fail_on_invalid:
        rules.append({"type": "validity", "name": "validity", "target": "all_solids"})
    return rules


def _load_rules(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("checks"), list):
        return data["checks"]
    raise ValueError("Rules file must be a list or an object with a checks list")


def _validation_result(
    report: dict[str, Any],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for rule in rules:
        try:
            checks.extend(_check_rule(report, rule))
        except Exception as exc:
            checks.append(
                {
                    "name": rule.get("name", rule.get("type", "rule_error")),
                    "type": rule.get("type", "unknown"),
                    "status": "fail",
                    "expected": "valid rule",
                    "actual": str(exc),
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
    parser.add_argument("--rules", help="Optional JSON rules file for validation checks")
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
    rules = []
    if args.rules:
        rules_path = Path(args.rules).expanduser().resolve()
        rules.extend(_load_rules(rules_path))
    rules.extend(
        _rules_from_cli(
            expect_solids=args.expect_solids,
            expect_bbox=args.expect_bbox,
            bbox_tolerance=args.bbox_tol,
            fail_on_invalid=args.fail_on_invalid,
        )
    )
    report["validation"] = _validation_result(report=report, rules=rules)

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
