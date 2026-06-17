from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def bbox_delta(a: list[float], b: list[float]) -> float:
    return max(abs(float(x) - float(y)) for x, y in zip(a, b))


def load_manifest_solids(path: Path) -> list[dict[str, Any]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    solids = []
    for domain in manifest["domains"]:
        if domain["role"] == "simulation_air_domain":
            continue
        for solid in domain["solid_bboxes_mm"]:
            solids.append(
                {
                    "cad_domain": domain["name"],
                    "material": domain["material"],
                    "role": domain["role"],
                    "voltage_V": domain["voltage_V"],
                    "manifest_expected_comsol_object": solid["expected_comsol_object"],
                    "bbox_mm": solid["bbox_mm"],
                }
            )
    return solids


def measure_domains(mph_path: Path, cores: int, comsol_bin: str) -> list[dict[str, Any]]:
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")
    client = mph.Client(cores=cores, version="6.3")
    model = None
    try:
        model = client.load(str(mph_path))
        geom = model.java.component("comp1").geom("geom1")
        total_domains = int(geom.getNDomains())
        meas = geom.measureFinal()
        measured = []
        for domain_id in range(1, total_domains + 1):
            meas.selection().geom("geom1", 3)
            meas.selection().set([domain_id])
            measured.append(
                {
                    "domain_id": domain_id,
                    "bbox_mm": [float(value) for value in list(meas.getBoundingBox())],
                    "volume_mm3": float(meas.getVolume()),
                }
            )
        return measured
    finally:
        if model is not None:
            try:
                client.remove(model)
            except Exception:
                try:
                    client.clear()
                except Exception:
                    pass


def match_domains(measured_domains: list[dict[str, Any]], manifest_solids: list[dict[str, Any]], tolerance: float) -> list[dict[str, Any]]:
    unmatched_domains = measured_domains[:]
    matches = []
    for solid in manifest_solids:
        ranked = sorted(
            (
                (bbox_delta(domain["bbox_mm"], solid["bbox_mm"]), idx, domain)
                for idx, domain in enumerate(unmatched_domains)
            ),
            key=lambda item: item[0],
        )
        if not ranked:
            matches.append({**solid, "match_status": "no_domain_candidate"})
            continue

        delta, idx, domain = ranked[0]
        status = "matched" if delta <= tolerance else "bbox_delta_too_large"
        matches.append(
            {
                **solid,
                "match_status": status,
                "max_bbox_delta_mm": round(delta, 6),
                "domain_id": domain["domain_id"],
                "domain_bbox_mm": domain["bbox_mm"],
                "domain_volume_mm3": domain["volume_mm3"],
            }
        )
        if status == "matched":
            unmatched_domains.pop(idx)

    for domain in unmatched_domains:
        matches.append(
            {
                "match_status": "unmatched_comsol_domain",
                "cad_domain": "air_domain_esd_clearance_box",
                "material": "air",
                "role": "simulation_air_domain",
                "voltage_V": None,
                "domain_id": domain["domain_id"],
                "domain_bbox_mm": domain["bbox_mm"],
                "domain_volume_mm3": domain["volume_mm3"],
            }
        )

    return matches


def group_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for item in matches:
        if item["match_status"] not in {"matched", "unmatched_comsol_domain"}:
            continue
        key = item["cad_domain"]
        groups.setdefault(
            key,
            {
                "cad_domain": key,
                "material": item.get("material"),
                "role": item.get("role"),
                "voltage_V": item.get("voltage_V"),
                "comsol_objects": [],
                "domain_guesses": [],
            },
        )
        if item["match_status"] == "matched":
            groups[key]["comsol_objects"].append(item["manifest_expected_comsol_object"])
        groups[key]["domain_guesses"].append(int(item["domain_id"]))
    for group in groups.values():
        group["domain_guesses"] = sorted(set(group["domain_guesses"]))
    return list(groups.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mph", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=0.01)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    args = parser.parse_args()

    manifest_solids = load_manifest_solids(args.manifest)
    measured_domains = measure_domains(args.mph.resolve(), args.cores, args.comsol_bin)
    matches = match_domains(measured_domains, manifest_solids, args.tolerance)
    all_product_matched = all(
        item["match_status"] == "matched" for item in matches if item["match_status"] != "unmatched_comsol_domain"
    )
    result = {
        "schema": "ssd_enclosure_measured_domain_mapping.v0",
        "tolerance_mm": args.tolerance,
        "mph": str(args.mph.resolve()),
        "manifest": str(args.manifest.resolve()),
        "measured_domain_count": len(measured_domains),
        "manifest_product_solid_count": len(manifest_solids),
        "all_product_matched": all_product_matched,
        "note": "Domain IDs are matched by COMSOL-measured final-domain bounding boxes, intended for Form Union geometry.",
        "groups": group_matches(matches),
        "matches": matches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"measured_domain_count={len(measured_domains)}")
    print(f"manifest_product_solid_count={len(manifest_solids)}")
    print(f"all_product_matched={all_product_matched}")
    print(args.output)
    return 0 if all_product_matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
