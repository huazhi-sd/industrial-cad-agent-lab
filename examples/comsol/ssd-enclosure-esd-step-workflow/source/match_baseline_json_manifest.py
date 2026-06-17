from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SOLID_RE = re.compile(r"imp1\.SOLID\((\d+)\)")


def bbox_delta(a: list[float], b: list[float]) -> float:
    return max(abs(x - y) for x, y in zip(a, b))


def load_baseline_objects(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    objects = []
    for obj in data["geometry"]["objects"]:
        bbox = obj["bbox"]
        if not bbox.get("ok"):
            continue
        name = obj["name"]
        domain_guess = None
        match = SOLID_RE.fullmatch(name)
        if match:
            domain_guess = int(match.group(1))
        elif name == "air_after_import":
            domain_guess = data["geometry"]["domains"]
        objects.append(
            {
                "comsol_object": name,
                "domain_guess": domain_guess,
                "bbox_mm": bbox["value"],
            }
        )
    return objects


def load_manifest_solids(path: Path) -> list[dict]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    solids = []
    for domain in manifest["domains"]:
        # The baseline imports product-only STEP and creates air inside COMSOL,
        # so the old CAD-side air solid is not matched against imp1.SOLID(*).
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


def match_objects(comsol_objects: list[dict], manifest_solids: list[dict], tolerance: float) -> list[dict]:
    product_objects = [obj for obj in comsol_objects if obj["comsol_object"].startswith("imp1.SOLID(")]
    air_objects = [obj for obj in comsol_objects if obj["comsol_object"] == "air_after_import"]

    unmatched = manifest_solids[:]
    matches = []
    for obj in product_objects:
        ranked = sorted(
            (
                (bbox_delta(obj["bbox_mm"], candidate["bbox_mm"]), idx, candidate)
                for idx, candidate in enumerate(unmatched)
            ),
            key=lambda item: item[0],
        )
        if not ranked:
            matches.append({**obj, "match_status": "no_manifest_candidate"})
            continue

        delta, idx, candidate = ranked[0]
        status = "matched" if delta <= tolerance else "bbox_delta_too_large"
        matches.append(
            {
                **obj,
                "match_status": status,
                "max_bbox_delta_mm": round(delta, 6),
                **{key: candidate[key] for key in ("cad_domain", "material", "role", "voltage_V", "manifest_expected_comsol_object")},
            }
        )
        if status == "matched":
            unmatched.pop(idx)

    for obj in air_objects:
        matches.append(
            {
                **obj,
                "match_status": "matched",
                "max_bbox_delta_mm": 0.0,
                "cad_domain": "air_domain_esd_clearance_box",
                "material": "air",
                "role": "simulation_air_domain",
                "voltage_V": None,
                "manifest_expected_comsol_object": "air_after_import",
            }
        )

    for candidate in unmatched:
        matches.append(
            {
                "match_status": "manifest_solid_not_found_in_baseline",
                **candidate,
            }
        )

    return matches


def group_matches(matches: list[dict]) -> dict[str, dict]:
    groups: dict[str, dict] = {}
    for item in matches:
        if item.get("match_status") != "matched":
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
        groups[key]["comsol_objects"].append(item["comsol_object"])
        if item.get("domain_guess") is not None:
            groups[key]["domain_guesses"].append(item["domain_guess"])
    return groups


def normalize_air_domains_for_union(groups: dict[str, dict], baseline_geometry: dict) -> None:
    air_group = groups.get("air_domain_esd_clearance_box")
    if not air_group:
        return

    total_domains = int(baseline_geometry["domains"])
    product_domain_ids = sorted(
        domain
        for key, group in groups.items()
        if key != "air_domain_esd_clearance_box"
        for domain in group["domain_guesses"]
    )
    if not product_domain_ids:
        return

    first_air_domain = max(product_domain_ids) + 1
    if total_domains >= first_air_domain:
        air_group["domain_guesses"] = list(range(first_air_domain, total_domains + 1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=0.01)
    args = parser.parse_args()

    baseline_data = json.loads(args.baseline.read_text(encoding="utf-8"))
    objects = load_baseline_objects(args.baseline)
    solids = load_manifest_solids(args.manifest)
    matches = match_objects(objects, solids, args.tolerance)
    all_matched = all(item["match_status"] == "matched" for item in matches)
    groups = group_matches(matches)
    normalize_air_domains_for_union(groups, baseline_data["geometry"])
    result = {
        "schema": "ssd_enclosure_baseline_domain_mapping.v0",
        "tolerance_mm": args.tolerance,
        "baseline_object_count": len(objects),
        "manifest_product_solid_count": len(solids),
        "all_matched": all_matched,
        "note": "Product domain_guesses assume imported STEP object order. For Form Union, the air domain is expanded to all remaining domains after the product solids. Verify in COMSOL before final simulation.",
        "groups": list(groups.values()),
        "matches": matches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"baseline_object_count={len(objects)}")
    print(f"manifest_product_solid_count={len(solids)}")
    print(f"all_matched={all_matched}")
    print(args.output)
    return 0 if all_matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
