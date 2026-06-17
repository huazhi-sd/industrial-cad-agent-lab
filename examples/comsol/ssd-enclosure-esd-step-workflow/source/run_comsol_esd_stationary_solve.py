from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import mph


DEFAULT_COMSOL_BIN = r"D:\comsol\COMSOL63\Multiphysics\bin\win64"


def java_tags(java_list: Any) -> list[str]:
    try:
        return [str(item) for item in list(java_list)]
    except Exception:
        return []


def run(mph_path: Path, output_dir: Path, cores: int, comsol_bin: str, mesh_size: int) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PATH"] = comsol_bin + os.pathsep + os.environ.get("PATH", "")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_mph = output_dir / f"ssd_enclosure_esd_stationary_solved_{stamp}.mph"
    out_report = output_dir / f"ssd_enclosure_esd_stationary_solved_{stamp}.json"

    report: dict[str, Any] = {
        "schema": "ssd_enclosure_comsol_esd_stationary_solve.v0",
        "timestamp": stamp,
        "source_mph": str(mph_path),
        "output_mph": str(out_mph),
        "status": "started",
        "mesh_size": mesh_size,
        "steps": [],
        "warnings": [
            "This is a first-pass stationary electrostatics solve, not a qualified breakdown model.",
            "The imported geometry and boundary selections still require visual verification.",
        ],
    }

    client = mph.Client(cores=cores, version="6.3")
    model = None
    try:
        model = client.load(str(mph_path))
        jm = model.java
        comp = jm.component("comp1")

        try:
            mesh = comp.mesh("mesh1")
            report["steps"].append("Reused mesh1.")
        except Exception:
            mesh = comp.mesh().create("mesh1")
            report["steps"].append("Created mesh1.")

        try:
            mesh.autoMeshSize(int(mesh_size))
            report["steps"].append(f"Set automatic mesh size {mesh_size}.")
        except Exception as exc:
            report["warnings"].append(f"Could not set mesh size: {type(exc).__name__}: {exc}")

        mesh.run()
        report["steps"].append("Mesh run completed.")

        try:
            study = jm.study("std1")
            report["steps"].append("Reused std1.")
        except Exception:
            study = jm.study().create("std1")
            study.create("stat", "Stationary")
            report["steps"].append("Created std1 Stationary study.")

        try:
            study.run()
            report["steps"].append("Study run completed through Java study.run().")
        except Exception as exc:
            report["steps"].append("Study run failed.")
            report["solver_error"] = f"{type(exc).__name__}: {exc}"
            try:
                model.save(str(out_mph))
                report["steps"].append("Saved failed solve model for inspection.")
            except Exception as save_exc:
                report["warnings"].append(f"Could not save failed solve model: {type(save_exc).__name__}: {save_exc}")
            raise

        report["studies"] = java_tags(jm.study().tags())
        report["meshes"] = java_tags(comp.mesh().tags())
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
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cores", type=int, default=2)
    parser.add_argument("--comsol-bin", default=DEFAULT_COMSOL_BIN)
    parser.add_argument("--mesh-size", type=int, default=5, help="COMSOL automatic mesh size, 1=fine, 9=coarse.")
    args = parser.parse_args()
    report = run(args.mph.resolve(), args.out.resolve(), args.cores, args.comsol_bin, args.mesh_size)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
