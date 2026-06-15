from pathlib import Path
import importlib.util
import json

from build123d import *


THIS_DIR = Path(__file__).resolve().parent
ASSEMBLY_SRC = THIS_DIR / "transparent_pc_m2_2280_ssd_enclosure_assembly.py"
OUT_DIR = THIS_DIR.parent


def load_assembly_module():
    spec = importlib.util.spec_from_file_location("ssd_assembly", ASSEMBLY_SRC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def box_at(size, loc):
    return Box(*size).translate(loc)


def make_air_domain():
    return Part(
        [
            box_at(
                (135.0, 64.0, 34.0),
                (0.0, 0.0, 9.0),
            )
        ],
        label="air_domain_esd_clearance_box",
    )


def bbox_values(shape):
    bbox = shape.bounding_box()
    return [
        round(bbox.min.X, 6),
        round(bbox.max.X, 6),
        round(bbox.min.Y, 6),
        round(bbox.max.Y, 6),
        round(bbox.min.Z, 6),
        round(bbox.max.Z, 6),
    ]


def solid_bbox_values(solid):
    bbox = solid.bounding_box()
    return [
        round(bbox.min.X, 6),
        round(bbox.max.X, 6),
        round(bbox.min.Y, 6),
        round(bbox.max.Y, 6),
        round(bbox.min.Z, 6),
        round(bbox.max.Z, 6),
    ]


def make_domain_manifest_entry(name, shape, material, role, voltage=None, notes=None, start_index=1):
    solids = list(shape.solids())
    end_index = start_index + len(solids) - 1
    return {
        "name": name,
        "material": material,
        "role": role,
        "voltage_V": voltage,
        "notes": notes or "",
        "bbox_mm": bbox_values(shape),
        "solid_count": len(solids),
        "expected_comsol_object_range": {
            "start": f"imp1.SOLID({start_index})",
            "end": f"imp1.SOLID({end_index})",
        },
        "solid_bboxes_mm": [
            {
                "expected_comsol_object": f"imp1.SOLID({start_index + idx})",
                "bbox_mm": solid_bbox_values(solid),
            }
            for idx, solid in enumerate(solids)
        ],
    }, end_index + 1


def write_manifest(out_path, domain_specs):
    entries = []
    next_index = 1
    for spec in domain_specs:
        entry, next_index = make_domain_manifest_entry(*spec, start_index=next_index)
        entries.append(entry)

    manifest = {
        "schema": "cad_to_comsol_esd_manifest.v0",
        "units": "mm",
        "step_file": "ssd_enclosure_esd_sim_simplified.step",
        "comsol_import_feature": "imp1",
        "domains": entries,
    }
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main():
    assembly = load_assembly_module()
    air_domain = make_air_domain()

    # This is a simulation-prep compound, not the external design assembly.
    # Domains are intentionally coarse and named for COMSOL material/BC mapping.
    domain_specs = [
        ("air_domain_esd_clearance_box", air_domain, "air", "simulation_air_domain", None, "Outer air clearance box for electrostatics."),
        ("bottom_shell_transparent_pc", assembly.bottom_shell, "polycarbonate", "dielectric_shell", None, "Bottom transparent PC housing."),
        ("top_shell_transparent_pc", assembly.top_shell, "polycarbonate", "dielectric_shell", None, "Top transparent PC cover."),
        ("main_pcb_fr4_and_components", assembly.main_pcb, "FR4_simplified", "dielectric_pcb", None, "Main PCB dielectric and simplified non-conductor components."),
        ("main_pcb_high_potential_copper", assembly.main_pcb_high_voltage_copper, "copper", "high_potential_conductor", 1000.0, "Approximate VBUS/high-potential copper regions."),
        ("main_pcb_ground_copper", assembly.main_pcb_ground_copper, "copper", "ground_conductor", 0.0, "Ground copper regions on main PCB."),
        ("usb_c_shell_metal_ground", assembly.usb_c_shell_metal, "stainless_steel_or_shell_metal", "ground_conductor", 0.0, "USB-C connector metal shell."),
        ("m2_2280_ssd_fr4_and_components", assembly.ssd_2280, "FR4_simplified", "dielectric_ssd", None, "M.2 2280 SSD body and simplified components."),
        ("ssd_exposed_copper_regions", assembly.ssd_exposed_copper, "copper", "ground_or_floating_conductor", 0.0, "Simplified exposed copper on SSD; currently treated as ground for first-pass ESD."),
        ("m2_tail_screw", assembly.m2_tail_screw, "steel", "ground_conductor", 0.0, "M.2 tail screw and head."),
    ]

    sim_domains = Compound(
        children=[
            air_domain,
            assembly.bottom_shell,
            assembly.top_shell,
            assembly.main_pcb,
            assembly.main_pcb_high_voltage_copper,
            assembly.main_pcb_ground_copper,
            assembly.usb_c_shell_metal,
            assembly.ssd_2280,
            assembly.ssd_exposed_copper,
            assembly.m2_tail_screw,
        ],
        label="ssd_enclosure_esd_sim_simplified_domains",
    )

    out = OUT_DIR / "ssd_enclosure_esd_sim_simplified.step"
    manifest_out = OUT_DIR / "ssd_enclosure_esd_manifest.json"
    export_step(sim_domains, out)
    write_manifest(manifest_out, domain_specs)
    print(out)
    print(manifest_out)


if __name__ == "__main__":
    main()
