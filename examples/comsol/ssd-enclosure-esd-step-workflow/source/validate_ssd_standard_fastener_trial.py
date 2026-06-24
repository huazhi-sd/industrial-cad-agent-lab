from __future__ import annotations

import json
from pathlib import Path

import transparent_pc_m2_2280_ssd_enclosure_assembly as base
import ssd_enclosure_standard_fastener_trial as trial


ROOT = Path(__file__).resolve().parents[1]
JSON_OUTPUT = ROOT / "ssd_standard_fastener_validation.json"
MD_OUTPUT = ROOT / "ssd_standard_fastener_validation.md"


def status(pass_condition: bool) -> str:
    return "pass" if pass_condition else "fail"


def main() -> int:
    pcb_top_z = base.PCB_TOP_Z
    ssd_bottom_z = base.SSD_Z - base.SSD_T / 2
    ssd_top_z = base.SSD_TOP_Z
    top_lid_underside_z = base.TOP_UNDERSIDE_Z

    required_standoff_height = ssd_bottom_z - pcb_top_z
    custom_standoff_top_z = pcb_top_z + trial.CUSTOM_STANDOFF_HEIGHT
    catalog_boss_delta = trial.CATALOG_BOSS_HEIGHT - required_standoff_height

    screw_axis = (base.M2_SCREW_X, base.M2_SCREW_Y)
    ssd_tail_hole_axis = (base.SSD_TAIL_X, 0.0)
    axis_delta = (
        screw_axis[0] - ssd_tail_hole_axis[0],
        screw_axis[1] - ssd_tail_hole_axis[1],
    )

    screw_head_top_z = ssd_top_z + trial.SCREW_HEAD_HEIGHT
    screw_shank_bottom_z = ssd_top_z - trial.SCREW_NOMINAL_LENGTH
    screw_clearance_to_lid = top_lid_underside_z - screw_head_top_z
    screw_engagement_below_pcb_top = pcb_top_z - screw_shank_bottom_z

    checks = [
        {
            "name": "screw_axis_matches_ssd_tail_hole_axis",
            "status": status(abs(axis_delta[0]) <= 0.05 and abs(axis_delta[1]) <= 0.05),
            "dx_mm": round(axis_delta[0], 4),
            "dy_mm": round(axis_delta[1], 4),
        },
        {
            "name": "custom_standoff_height_matches_pcb_to_ssd_gap",
            "status": status(abs(trial.CUSTOM_STANDOFF_HEIGHT - required_standoff_height) <= 0.02),
            "required_height_mm": round(required_standoff_height, 3),
            "custom_height_mm": round(trial.CUSTOM_STANDOFF_HEIGHT, 3),
            "custom_top_z_mm": round(custom_standoff_top_z, 3),
            "ssd_bottom_z_mm": round(ssd_bottom_z, 3),
        },
        {
            "name": "catalog_h04_boss_rejected_by_height",
            "status": status(catalog_boss_delta > 0.5),
            "catalog_id": trial.REJECTED_BOSS_CATALOG_ID,
            "catalog_height_mm": trial.CATALOG_BOSS_HEIGHT,
            "required_height_mm": round(required_standoff_height, 3),
            "too_tall_by_mm": round(catalog_boss_delta, 3),
        },
        {
            "name": "m2x3_screw_has_lid_clearance",
            "status": status(screw_clearance_to_lid >= 0.5),
            "catalog_id": trial.SCREW_CATALOG_ID,
            "screw_head_top_z_mm": round(screw_head_top_z, 3),
            "top_lid_underside_z_mm": round(top_lid_underside_z, 3),
            "clearance_mm": round(screw_clearance_to_lid, 3),
        },
        {
            "name": "m2x3_screw_reaches_tail_standoff",
            "status": status(screw_engagement_below_pcb_top >= 0.3),
            "screw_shank_bottom_z_mm": round(screw_shank_bottom_z, 3),
            "pcb_top_z_mm": round(pcb_top_z, 3),
            "engagement_below_pcb_top_mm": round(screw_engagement_below_pcb_top, 3),
        },
    ]

    payload = {
        "assembly": "ssd_enclosure_standard_fastener_trial.step",
        "source": "source/ssd_enclosure_standard_fastener_trial.py",
        "standard_part_references": {
            "installed_screw": trial.SCREW_CATALOG_ID,
            "rejected_boss_candidate": trial.REJECTED_BOSS_CATALOG_ID,
        },
        "checks": checks,
        "summary": {
            "passed": sum(1 for check in checks if check["status"] == "pass"),
            "total": len(checks),
        },
    }

    JSON_OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# SSD Enclosure Standard Fastener Validation",
        "",
        "This report checks the first standard-part fit trial for the transparent PC M.2 2280 SSD enclosure.",
        "",
        "## Standard Part References",
        "",
        f"- Installed screw: `{trial.SCREW_CATALOG_ID}`",
        f"- Rejected boss candidate: `{trial.REJECTED_BOSS_CATALOG_ID}`",
        "",
        "The catalog M2 h=4 mm boss is rejected because the current PCB-to-SSD stack requires a much shorter M.2 tail standoff.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        lines.append(f"- `{check['name']}`: **{check['status']}**")
        for key, value in check.items():
            if key in {"name", "status"}:
                continue
            lines.append(f"  - `{key}`: `{value}`")
    lines.append("")
    lines.append(f"Passed {payload['summary']['passed']} / {payload['summary']['total']} checks.")
    lines.append("")
    MD_OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(JSON_OUTPUT)
    print(MD_OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
