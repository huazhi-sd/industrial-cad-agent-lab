from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def to_list(value: Any) -> list[int] | None:
    if value is None:
        return None
    return [int(item) for item in list(value)]


def try_call(label: str, func, warnings: list[str]) -> list[int] | int | bool | None:
    try:
        value = func()
        if isinstance(value, (int, bool)):
            return value
        return to_list(value)
    except Exception as exc:
        warnings.append(f"{label}: {type(exc).__name__}: {exc}")
        return None


def make_boundary_selection(comp, tag: str, domains: list[int], kind: str, warnings: list[str]) -> dict:
    try:
        comp.selection().create(tag, "Explicit")
    except Exception:
        pass

    sel = comp.selection(tag)
    report: dict[str, Any] = {
        "tag": tag,
        "kind": kind,
        "input_domains": domains,
        "warnings": [],
    }

    try:
        sel.geom("geom1", 3, 2, [kind])
        sel.set(domains)
        report["entities_2"] = try_call(f"{tag}.entities(2)", lambda: sel.entities(2), report["warnings"])
        report["entities"] = try_call(f"{tag}.entities()", lambda: sel.entities(), report["warnings"])
        report["interior_entities_2"] = try_call(
            f"{tag}.interiorEntities(2)", lambda: sel.interiorEntities(2), report["warnings"]
        )
        report["input_dimension"] = try_call(f"{tag}.inputDimension()", lambda: sel.inputDimension(), report["warnings"])
        report["input_entities"] = try_call(f"{tag}.inputEntities()", lambda: sel.inputEntities(), report["warnings"])
        sel.label(f"{tag} from domains {domains}")
    except Exception as exc:
        msg = f"{tag}: failed to create {kind} boundary selection: {type(exc).__name__}: {exc}"
        report["warnings"].append(msg)
        warnings.append(msg)

    return report


def run(mph_path: Path, material_report_path: Path, output_dir: Path, cores: int, comsol_bin: str) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")

    material_report = json.loads(material_report_path.read_text(encoding="utf-8"))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_report = output_dir / f"ssd_enclosure_boundary_probe_{stamp}.json"

    report: dict[str, Any] = {
        "schema": "ssd_enclosure_comsol_boundary_probe.v0",
        "timestamp": stamp,
        "source_mph": str(mph_path),
        "material_report": str(material_report_path),
        "status": "started",
        "groups": [],
        "warnings": [
            "Boundary IDs are probed from COMSOL selections and still require visual verification before final ESD solve.",
            "The exterior boundary of a conductor domain includes all faces exposed to neighboring domains, not necessarily only the intended electrode face.",
        ],
    }

    client = mph.Client(cores=cores, version="6.3")
    model = None
    try:
        model = client.load(str(mph_path))
        comp = model.java.component("comp1")

        for selection in material_report["selections"]:
            domains = [int(domain) for domain in selection["domains"]]
            base_tag = selection["tag"]
            group = {
                "source_selection": base_tag,
                "label": selection["label"],
                "role": selection["role"],
                "material": selection["material"],
                "voltage_V": selection["voltage_V"],
                "domains": domains,
                "existing_selection_probe": {},
                "boundary_selections": [],
            }

            existing = comp.selection(base_tag)
            group["existing_selection_probe"] = {
                "entities_3": try_call(f"{base_tag}.entities(3)", lambda: existing.entities(3), report["warnings"]),
                "entities_2": try_call(f"{base_tag}.entities(2)", lambda: existing.entities(2), report["warnings"]),
                "entities": try_call(f"{base_tag}.entities()", lambda: existing.entities(), report["warnings"]),
                "input_dimension": try_call(
                    f"{base_tag}.inputDimension()", lambda: existing.inputDimension(), report["warnings"]
                ),
                "input_entities": try_call(
                    f"{base_tag}.inputEntities()", lambda: existing.inputEntities(), report["warnings"]
                ),
            }

            for kind in ("exterior", "interior"):
                probe_tag = f"{base_tag}_bnd_{kind}"[:60]
                group["boundary_selections"].append(
                    make_boundary_selection(comp, probe_tag, domains, kind, report["warnings"])
                )

            report["groups"].append(group)

        report["status"] = "success"
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        out_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        report["output_report"] = str(out_report)
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
    parser.add_argument("--material-report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    args = parser.parse_args()
    report = run(
        args.mph.resolve(),
        args.material_report.resolve(),
        args.out.resolve(),
        args.cores,
        args.comsol_bin,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
