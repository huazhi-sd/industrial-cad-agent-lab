from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def java_array_to_list(value: Any) -> list[Any]:
    try:
        return [item for item in value]
    except TypeError:
        return [str(value)]


def safe_call(label: str, func) -> dict[str, Any]:
    try:
        return {"ok": True, "value": func()}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def run(
    step_path: Path,
    output_dir: Path,
    cores: int,
    comsol_bin: str,
    finalization_action: str,
    imprint: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mph_path = output_dir / f"ssd_enclosure_step_import_baseline_{stamp}.mph"
    report_path = output_dir / f"ssd_enclosure_step_import_baseline_{stamp}.json"

    report: dict[str, Any] = {
        "schema": "ssd_enclosure_comsol_step_import_baseline.v0",
        "timestamp": stamp,
        "step_path": str(step_path),
        "comsol_bin": comsol_bin,
        "finalization_action": finalization_action,
        "imprint": imprint,
        "status": "started",
    }

    client = mph.Client(cores=cores, version="6.3")
    model = None
    try:
        model = client.create("ssd_enclosure_step_import_baseline")
        jm = model.java
        jm.label(mph_path.name)
        jm.component().create("comp1", True)
        jm.component("comp1").geom().create("geom1", 3)
        geom = jm.component("comp1").geom("geom1")
        geom.lengthUnit("mm")

        geom.create("imp1", "Import")
        imp = geom.feature("imp1")
        imp.set("filename", str(step_path))
        imp.set("selresult", True)
        imp.set("selresultshow", "all")
        imp.importData()

        geom.create("air_after_import", "Block")
        air = geom.feature("air_after_import")
        air.set("size", ["135", "64", "34"])
        air.set("base", "center")
        air.set("pos", ["0", "0", "9"])
        air.set("selresult", True)
        air.set("selresultshow", "all")

        geom.feature("fin").set("action", finalization_action)
        geom.feature("fin").set("imprint", imprint)
        geom.run()

        jm.component("comp1").physics().create("es", "Electrostatics", "geom1")

        feature_tags = java_array_to_list(geom.feature().tags())
        object_names = java_array_to_list(geom.objectNames())

        object_reports = []
        for name in object_names:
            obj = geom.object(str(name))
            object_reports.append(
                {
                    "name": str(name),
                    "bbox": safe_call("bbox", lambda obj=obj: java_array_to_list(obj.getBoundingBox())),
                    "domains": safe_call("domains", lambda obj=obj: int(obj.getNDomains())),
                    "boundaries": safe_call("boundaries", lambda obj=obj: int(obj.getNBoundaries())),
                }
            )

        report.update(
            {
                "status": "success",
                "comsol_version": client.version,
                "cores": client.cores,
                "standalone": client.standalone,
                "mph_path": str(mph_path),
                "geometry": {
                    "is_assembly": bool(geom.isAssembly()),
                    "has_cad_rep": bool(geom.hasCadRep()),
                    "features": [str(item) for item in feature_tags],
                    "object_count": len(object_names),
                    "object_names": [str(item) for item in object_names],
                    "domains": int(geom.getNDomains()),
                    "boundaries": int(geom.getNBoundaries()),
                    "edges": int(geom.getNEdges()),
                    "vertices": int(geom.getNVertices()),
                    "bbox": java_array_to_list(geom.getBoundingBox()),
                    "objects": object_reports,
                },
                "physics": {"created": ["es"], "first_pass": "Electrostatics only; no materials or boundary conditions yet."},
            }
        )
        model.save(str(mph_path))
    except Exception as exc:
        report.update({"status": "failed", "error": f"{type(exc).__name__}: {exc}"})
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
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
    parser.add_argument(
        "--step",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "transparent_pc_m2_2280_ssd_enclosure_assembly.step",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "comsol" / "baseline-runs",
    )
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    parser.add_argument("--finalization-action", default="assembly", choices=["assembly", "union"])
    parser.add_argument("--imprint", action="store_true")
    args = parser.parse_args()

    report = run(
        args.step.resolve(),
        args.out.resolve(),
        args.cores,
        args.comsol_bin,
        args.finalization_action,
        args.imprint,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
