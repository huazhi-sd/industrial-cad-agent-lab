from __future__ import annotations

import json
import re
import sys
from pathlib import Path


OBJECT_RE = re.compile(r"object_info name=(?P<name>\S+) bbox=\[(?P<bbox>[^\]]+)\]")


def parse_bbox(raw: str) -> list[float]:
    return [float(part.strip()) for part in raw.split(",")]


def bbox_delta(a: list[float], b: list[float]) -> float:
    return max(abs(x - y) for x, y in zip(a, b))


def load_comsol_objects(stdout_path: Path) -> list[dict]:
    objects = []
    raw = stdout_path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16", errors="replace")
    else:
        text = raw.decode("utf-8", errors="replace")
    for line in text.splitlines():
        match = OBJECT_RE.search(line)
        if match:
            objects.append(
                {
                    "comsol_object": match.group("name"),
                    "bbox_mm": parse_bbox(match.group("bbox")),
                }
            )
    return objects


def load_manifest_solids(manifest_path: Path) -> list[dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    solids = []
    for domain in manifest["domains"]:
        for solid in domain["solid_bboxes_mm"]:
            solids.append(
                {
                    "cad_domain": domain["name"],
                    "material": domain["material"],
                    "role": domain["role"],
                    "voltage_V": domain["voltage_V"],
                    "expected_comsol_object": solid["expected_comsol_object"],
                    "bbox_mm": solid["bbox_mm"],
                }
            )
    return solids


def match_objects(comsol_objects: list[dict], manifest_solids: list[dict], tolerance: float) -> list[dict]:
    unmatched = manifest_solids[:]
    matches = []
    for obj in comsol_objects:
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
                "cad_domain": candidate["cad_domain"],
                "material": candidate["material"],
                "role": candidate["role"],
                "voltage_V": candidate["voltage_V"],
                "manifest_expected_comsol_object": candidate["expected_comsol_object"],
            }
        )
        if status == "matched":
            unmatched.pop(idx)
    for candidate in unmatched:
        matches.append(
            {
                "match_status": "manifest_solid_not_found_in_comsol",
                "cad_domain": candidate["cad_domain"],
                "material": candidate["material"],
                "role": candidate["role"],
                "voltage_V": candidate["voltage_V"],
                "manifest_expected_comsol_object": candidate["expected_comsol_object"],
                "bbox_mm": candidate["bbox_mm"],
            }
        )
    return matches


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: python match_comsol_step_manifest.py "
            "<manifest.json> <comsol_batch_stdout.txt> <output_mapping.json> [tolerance_mm]"
        )
        return 2

    manifest_path = Path(sys.argv[1])
    stdout_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    tolerance = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01

    comsol_objects = load_comsol_objects(stdout_path)
    manifest_solids = load_manifest_solids(manifest_path)
    matches = match_objects(comsol_objects, manifest_solids, tolerance)
    ok = all(item["match_status"] == "matched" for item in matches)

    result = {
        "schema": "cad_to_comsol_esd_object_mapping.v0",
        "tolerance_mm": tolerance,
        "comsol_object_count": len(comsol_objects),
        "manifest_solid_count": len(manifest_solids),
        "all_matched": ok,
        "matches": matches,
    }
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"comsol_object_count={len(comsol_objects)}")
    print(f"manifest_solid_count={len(manifest_solids)}")
    print(f"all_matched={ok}")
    print(output_path)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
