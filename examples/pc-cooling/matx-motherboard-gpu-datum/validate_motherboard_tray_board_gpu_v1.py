from pathlib import Path
import importlib.util
import re


ROOT = Path(__file__).resolve().parent
FORBIDDEN_CAD_OPS = re.compile(r"(\.mirror\s*\(|\bmirror\s*\(|\.scale\s*\(|\bscale\s*\()")


def fail(message: str):
    raise SystemExit(f"TRAY+BOARD+GPU V1 CHECK FAILED: {message}")


def load_module(script_name: str):
    path = ROOT / script_name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def approx(value: float, target: float, tol: float = 0.08):
    return abs(value - target) <= tol


def main():
    for script_name in (
        "gpu_3slot_datum_v1.py",
        "motherboard_tray_board_gpu_v1.py",
    ):
        text = (ROOT / script_name).read_text(encoding="utf-8")
        match = FORBIDDEN_CAD_OPS.search(text)
        if match:
            fail(f"forbidden mirror/scale-like CAD operation in {script_name}: {match.group(0)}")

    board_mod = load_module("motherboard_datum_v1.py")
    gpu_mod = load_module("gpu_3slot_datum_v1.py")
    assembly_mod = load_module("motherboard_tray_board_gpu_v1.py")

    if not approx(gpu_mod.BRACKET_HEIGHT, 120.11):
        fail("three-slot bracket height datum drifted")
    if not approx(gpu_mod.BRACKET_SLOT_WIDTH, 63.23):
        fail("three-slot bracket width datum drifted")
    if not approx(gpu_mod.BRACKET_HOLE_D, 4.42):
        fail("bracket hole diameter datum drifted")
    if not approx(gpu_mod.BRACKET_SLOT_SCREW_POCKET_D, 6.2):
        fail("slot screw pocket diameter datum drifted")
    if not approx(gpu_mod.BRACKET_SLOT_SCREW_CLEARANCE_D, 3.6):
        fail("slot screw clearance diameter datum drifted")
    if not approx(gpu_mod.PCI_FINGER_LENGTH, 89.9):
        fail("PCIe x16 goldfinger length datum drifted")
    if not approx(gpu_mod.PCI_FINGER_VISIBLE_DEPTH, 12.06):
        fail("PCIe goldfinger visible depth datum drifted")

    if not approx(gpu_mod.PCI_FINGER_X, board_mod.PCIE_X16_SLOT_X + 0.5):
        fail("goldfinger X is not aligned to motherboard x16 slot")
    if not approx(gpu_mod.PCIE_X16_SLOT_Z, board_mod.PCIE_X16_SLOT_Z):
        fail("goldfinger Z is not aligned to motherboard x16 slot")

    screw_center_y = gpu_mod.BRACKET_Y0 + gpu_mod.BRACKET_SLOT_SCREW_FLANGE_Y / 2.0
    screw_offset_from_board = abs(screw_center_y - board_mod.BOARD_FRONT_Y)
    expected_offset = gpu_mod.BRACKET_HEIGHT - gpu_mod.BRACKET_SLOT_SCREW_FLANGE_Y / 2.0
    if not approx(screw_offset_from_board, expected_offset, tol=0.12):
        fail("rear screw pocket plane is not at the far bracket end away from motherboard")

    gpu = gpu_mod.make_gpu_3slot_datum_v1()
    gpu_bb = gpu.bounding_box()

    if gpu_bb.max.X < 335.0:
        fail("GPU length envelope is below 335 mm")
    if gpu_bb.size.Z < 70.0:
        fail("GPU slot-width envelope is below 70 mm")
    if gpu_bb.size.Y < 145.0:
        fail("GPU height-away-from-board envelope is below 145 mm")
    if not (gpu_bb.min.X < 0.0 and gpu_bb.max.X > board_mod.MATX_SIZE):
        fail("GPU bracket/length relation to motherboard is wrong")

    assembly = assembly_mod.make_motherboard_tray_board_gpu_v1()
    if len(assembly.children) != 3:
        fail(f"assembly must have exactly 3 top-level parts, got {len(assembly.children)}")

    print("TRAY+BOARD+GPU V1 CHECK PASSED")
    print("- top-level parts: tray, motherboard datum, GPU datum")
    print(f"- GPU envelope: {gpu_bb.size.X:.2f} x {gpu_bb.size.Y:.2f} x {gpu_bb.size.Z:.2f} mm")
    print(f"- bracket: {gpu_mod.BRACKET_HEIGHT:.2f} mm high, {gpu_mod.BRACKET_SLOT_WIDTH:.2f} mm three-slot span")
    print(f"- rear screw pockets: 3x dia {gpu_mod.BRACKET_SLOT_SCREW_POCKET_D:.2f} mm pockets on {gpu_mod.PCI_SLOT_PITCH:.2f} mm slot pitch")
    print(f"- screw pocket plane offset from board front: {screw_offset_from_board:.2f} mm")
    print(f"- goldfinger: {gpu_mod.PCI_FINGER_LENGTH:.2f} x {gpu_mod.PCI_FINGER_VISIBLE_DEPTH:.2f} mm datum")


if __name__ == "__main__":
    main()
