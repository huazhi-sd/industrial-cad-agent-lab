from pathlib import Path
import importlib.util
import re


ROOT = Path(__file__).resolve().parent
FORBIDDEN_CAD_OPS = re.compile(r"(\.mirror\s*\(|\bmirror\s*\(|\.scale\s*\(|\bscale\s*\()")


def fail(message: str):
    raise SystemExit(f"TRAY+BOARD V1 CHECK FAILED: {message}")


def load_module(script_name: str):
    path = ROOT / script_name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def approx(value: float, target: float, tol: float = 0.05):
    return abs(value - target) <= tol


def main():
    for script_name in ("motherboard_datum_v1.py", "motherboard_tray_board_v1.py"):
        text = (ROOT / script_name).read_text(encoding="utf-8")
        match = FORBIDDEN_CAD_OPS.search(text)
        if match:
            fail(f"forbidden mirror/scale-like CAD operation in {script_name}: {match.group(0)}")

    tray_mod = load_module("motherboard_tray_v1.py")
    board_mod = load_module("motherboard_datum_v1.py")
    assembly_mod = load_module("motherboard_tray_board_v1.py")

    holes = {name: (x, z) for name, x, z in board_mod.MATX_8_HOLE_PATTERN}
    required = {"B", "C", "F", "R", "H", "J", "L", "M"}
    if set(holes) != required:
        fail(f"expected 8 mATX holes {sorted(required)}, got {sorted(holes)}")

    if tray_mod.MATX_8_HOLE_PATTERN != board_mod.MATX_8_HOLE_PATTERN:
        fail("tray and motherboard hole patterns must be identical")

    if not approx(board_mod.BOARD_BACK_Y, -tray_mod.STANDOFF_HEIGHT):
        fail("motherboard back plane must sit on the standoff tips")

    if not (board_mod.BOARD_FRONT_Y < board_mod.BOARD_BACK_Y < 0.0):
        fail("component side must be negative Y and tray side must be positive/back")

    if not (0.0 < board_mod.PCIE_X16_SLOT_X < board_mod.ATX24_X < board_mod.MATX_SIZE):
        fail("raw front X order must keep PCIe left of 24-pin")

    if not (board_mod.PCIE_X16_SLOT_Z < 100.0 and board_mod.EPS_Z > 220.0):
        fail("PCIe must stay lower and EPS must stay upper in raw front view")

    if not (board_mod.IO_CUTOUT_HEIGHT > 44.0 and board_mod.IO_CUTOUT_WIDTH > 158.0):
        fail("rear I/O envelope dimensions are below ATX datum")

    tray = tray_mod.make_motherboard_tray_v1()
    board = board_mod.make_motherboard_datum_v1()
    assembly = assembly_mod.make_motherboard_tray_board_v1()

    tray_bb = tray.bounding_box()
    board_bb = board.bounding_box()

    if not approx(tray_bb.min.Y, board_mod.BOARD_BACK_Y):
        fail("tray standoffs do not reach the motherboard back plane")

    if not approx(board_bb.max.Y, board_mod.BOARD_BACK_Y):
        fail("motherboard back face is not on the standoff plane")

    if len(assembly.children) != 2:
        fail(f"assembly must have exactly 2 top-level parts, got {len(assembly.children)}")

    print("TRAY+BOARD V1 CHECK PASSED")
    print("- top-level parts: tray, motherboard datum")
    print("- raw front: rear I/O low X, 24-pin high X, PCIe lower Z")
    print(f"- board back plane: Y={board_mod.BOARD_BACK_Y:.2f} mm")
    print(f"- rear I/O envelope: {board_mod.IO_CUTOUT_WIDTH:.2f} x {board_mod.IO_CUTOUT_HEIGHT:.2f} mm")


if __name__ == "__main__":
    main()
