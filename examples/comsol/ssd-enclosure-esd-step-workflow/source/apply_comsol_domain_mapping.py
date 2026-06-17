from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"

TAG_RE = re.compile(r"[^A-Za-z0-9_]+")


MATERIAL_PROPERTIES = {
    "air": {
        "label": "Air",
        "relpermittivity": ["1"],
    },
    "polycarbonate": {
        "label": "Polycarbonate first-pass",
        "relpermittivity": ["2.9"],
    },
    "FR4_simplified": {
        "label": "FR4 first-pass",
        "relpermittivity": ["4.3"],
    },
    "copper": {
        "label": "Copper conductor placeholder",
        "relpermittivity": ["1"],
        "electricconductivity": ["5.8e7[S/m]"],
    },
    "steel": {
        "label": "Steel conductor placeholder",
        "relpermittivity": ["1"],
        "electricconductivity": ["1.45e6[S/m]"],
    },
    "stainless_steel_or_shell_metal": {
        "label": "Stainless steel shell placeholder",
        "relpermittivity": ["1"],
        "electricconductivity": ["1.4e6[S/m]"],
    },
}


def make_tag(prefix: str, name: str) -> str:
    tag = TAG_RE.sub("_", name).strip("_").lower()
    return f"{prefix}_{tag}"[:60]


def set_property_if_supported(mat, name: str, values: list[str], warnings: list[str]) -> None:
    try:
        mat.propertyGroup("def").set(name, values)
    except Exception as exc:
        warnings.append(f"Could not set material property {name}: {type(exc).__name__}: {exc}")


def run(mph_path: Path, mapping_path: Path, output_dir: Path, cores: int, comsol_bin: str) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_mph = output_dir / f"ssd_enclosure_material_selections_{stamp}.mph"
    out_report = output_dir / f"ssd_enclosure_material_selections_{stamp}.json"

    client = mph.Client(cores=cores, version="6.3")
    model = None
    report = {
        "schema": "ssd_enclosure_comsol_material_selection.v0",
        "timestamp": stamp,
        "source_mph": str(mph_path),
        "mapping": str(mapping_path),
        "output_mph": str(out_mph),
        "status": "started",
        "selections": [],
        "materials": [],
        "warnings": [
            "Conductor materials are placeholders. Final electrostatic setup should use boundary potentials/grounds on conductor surfaces.",
            "Domain numbers are based on assembly object order and bbox mapping; verify in COMSOL before final solve.",
        ],
    }

    try:
        model = client.load(str(mph_path))
        jm = model.java
        comp = jm.component("comp1")

        for group in mapping["groups"]:
            domains = [int(d) for d in group["domain_guesses"]]
            if not domains:
                continue
            sel_tag = make_tag("sel", group["cad_domain"])
            try:
                comp.selection().create(sel_tag, "Explicit")
            except Exception:
                pass
            sel = comp.selection(sel_tag)
            sel.geom("geom1", 3)
            sel.set(domains)
            sel.label(group["cad_domain"])
            report["selections"].append(
                {
                    "tag": sel_tag,
                    "label": group["cad_domain"],
                    "domains": domains,
                    "material": group["material"],
                    "role": group["role"],
                    "voltage_V": group["voltage_V"],
                }
            )

        material_to_domains: dict[str, list[int]] = {}
        for group in mapping["groups"]:
            material_to_domains.setdefault(group["material"], []).extend(int(d) for d in group["domain_guesses"])

        for material, domains in material_to_domains.items():
            mat_tag = make_tag("mat", material)
            try:
                comp.material().create(mat_tag, "Common")
            except Exception:
                pass
            mat = comp.material(mat_tag)
            props = MATERIAL_PROPERTIES.get(material, {"label": material, "relpermittivity": ["1"]})
            mat.label(props.get("label", material))
            mat.selection().set(sorted(domains))
            for prop_name, prop_value in props.items():
                if prop_name == "label":
                    continue
                set_property_if_supported(mat, prop_name, prop_value, report["warnings"])
            report["materials"].append(
                {
                    "tag": mat_tag,
                    "label": props.get("label", material),
                    "material_key": material,
                    "domains": sorted(domains),
                    "properties": {k: v for k, v in props.items() if k != "label"},
                }
            )

        model.save(str(out_mph))
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
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    args = parser.parse_args()
    report = run(args.mph.resolve(), args.mapping.resolve(), args.out.resolve(), args.cores, args.comsol_bin)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
