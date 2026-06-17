from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def unique_ints(values: list[int]) -> list[int]:
    return sorted({int(value) for value in values})


def exterior_boundaries(boundary_probe: dict[str, Any], source_selection: str) -> list[int]:
    for group in boundary_probe["groups"]:
        if group["source_selection"] != source_selection:
            continue
        for boundary_selection in group["boundary_selections"]:
            if boundary_selection["kind"] == "exterior":
                return unique_ints(boundary_selection.get("entities_2") or [])
    raise KeyError(f"Boundary probe does not contain exterior boundaries for {source_selection}")


def get_or_create_physics_feature(physics, tag: str, feature_type: str):
    try:
        return physics.feature(tag)
    except Exception:
        pass

    try:
        return physics.feature().create(tag, feature_type, 2)
    except Exception:
        pass

    try:
        return physics.create(tag, feature_type, 2)
    except Exception:
        pass

    return physics.create(tag, feature_type)


def set_feature_property(feature, name: str, value: str, warnings: list[str]) -> None:
    try:
        feature.set(name, value)
    except Exception as exc:
        warnings.append(f"Could not set {feature.tag()}.{name}={value}: {type(exc).__name__}: {exc}")


def find_boundary_overlaps(boundary_conditions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    overlaps: list[dict[str, Any]] = []
    for idx, left in enumerate(boundary_conditions):
        left_set = set(left["boundaries"])
        for right in boundary_conditions[idx + 1 :]:
            overlap = sorted(left_set.intersection(right["boundaries"]))
            if overlap:
                overlaps.append(
                    {
                        "left": left["tag"],
                        "right": right["tag"],
                        "overlap_boundaries": overlap,
                    }
                )
    return overlaps


def run(mph_path: Path, boundary_probe_path: Path, output_dir: Path, cores: int, comsol_bin: str) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")

    boundary_probe = json.loads(boundary_probe_path.read_text(encoding="utf-8"))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_mph = output_dir / f"ssd_enclosure_esd_boundary_conditions_{stamp}.mph"
    out_report = output_dir / f"ssd_enclosure_esd_boundary_conditions_{stamp}.json"

    report: dict[str, Any] = {
        "schema": "ssd_enclosure_comsol_esd_boundary_conditions.v0",
        "timestamp": stamp,
        "source_mph": str(mph_path),
        "boundary_probe": str(boundary_probe_path),
        "output_mph": str(out_mph),
        "status": "started",
        "boundary_conditions": [],
        "warnings": [
            "This is a first-pass ESD setup. Boundary IDs are API-derived and still need visual verification.",
            "SSD exposed copper is treated as grounded for this trial; change this if the real design leaves it floating.",
            "The outer air boundary is left at COMSOL's default electrical insulation/zero charge for this baseline.",
        ],
    }

    high_voltage_selection = "sel_main_pcb_high_potential_copper"
    ground_selections = [
        ("gnd_usb_c_shell", "sel_usb_c_shell_metal_ground"),
        ("gnd_main_pcb_ground_copper", "sel_main_pcb_ground_copper"),
        ("gnd_ssd_exposed_copper", "sel_ssd_exposed_copper_regions"),
        ("gnd_m2_tail_screw", "sel_m2_tail_screw"),
    ]

    client = mph.Client(cores=cores, version="6.3")
    model = None
    try:
        model = client.load(str(mph_path))
        comp = model.java.component("comp1")
        try:
            es = comp.physics("es")
        except Exception:
            es = comp.physics().create("es", "Electrostatics", "geom1")

        high_boundaries = exterior_boundaries(boundary_probe, high_voltage_selection)
        ep = get_or_create_physics_feature(es, "ep_high_potential_copper", "ElectricPotential")
        ep.selection().set(high_boundaries)
        set_feature_property(ep, "V0", "1000[V]", report["warnings"])
        ep.label("High-potential copper test electrode, 1000 V")
        report["boundary_conditions"].append(
            {
                "tag": "ep_high_potential_copper",
                "type": "ElectricPotential",
                "source_selection": high_voltage_selection,
                "boundaries": high_boundaries,
                "V0": "1000[V]",
            }
        )

        for tag, source_selection in ground_selections:
            boundaries = exterior_boundaries(boundary_probe, source_selection)
            ground = get_or_create_physics_feature(es, tag, "Ground")
            ground.selection().set(boundaries)
            ground.label(f"Ground from {source_selection}")
            report["boundary_conditions"].append(
                {
                    "tag": tag,
                    "type": "Ground",
                    "source_selection": source_selection,
                    "boundaries": boundaries,
                }
            )

        overlaps = find_boundary_overlaps(report["boundary_conditions"])
        if overlaps:
            report["status"] = "failed_boundary_overlap"
            report["boundary_overlaps"] = overlaps
            raise RuntimeError("Boundary selections overlap; refusing to save conflicting electrostatic boundary conditions.")

        model.save(str(out_mph))
        report["status"] = "success"
    except Exception as exc:
        if report["status"] == "started":
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
    parser.add_argument("--boundary-probe", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    args = parser.parse_args()
    report = run(
        args.mph.resolve(),
        args.boundary_probe.resolve(),
        args.out.resolve(),
        args.cores,
        args.comsol_bin,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
