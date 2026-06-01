from pathlib import Path
import importlib.util
import re


ROOT = Path(__file__).resolve().parent
FORBIDDEN_CAD_OPS = re.compile(r"(\.mirror\s*\(|\bmirror\s*\(|\.scale\s*\(|\bscale\s*\()")


def fail(msg: str):
    raise SystemExit(f"HANDEDNESS CHECK FAILED: {msg}")


def load_module(script_name: str):
    path = ROOT / script_name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def check_no_forbidden_ops():
    for path in ROOT.glob("*.py"):
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8")
        match = FORBIDDEN_CAD_OPS.search(text)
        if match:
            fail(f"forbidden mirror/scale-like CAD operation in {path.name}: {match.group(0)}")


def bbox_center(shape):
    bb = shape.bounding_box()
    return (
        (bb.min.X + bb.max.X) / 2,
        (bb.min.Y + bb.max.Y) / 2,
        (bb.min.Z + bb.max.Z) / 2,
    )


def approx(value, target, tol=0.05):
    return abs(value - target) <= tol


def main():
    check_no_forbidden_ops()
    final = load_module("matx_tray_board_gpu_final_3part.py")

    holes = {name: (x, z) for name, x, z in final.MATX_8_HOLE_PATTERN}
    required = {"B", "C", "F", "R", "H", "J", "L", "M"}
    if set(holes) != required:
        fail(f"expected 8 mATX holes {sorted(required)}, got {sorted(holes)}")

    if not (final.BOARD_FRONT_Y < final.BOARD_BACK_Y < final.TRAY_Y_MIN):
        fail("front-view Y convention is wrong: component side must be negative Y, tray side positive Y")

    io_x = final.semantic_x_box(0.0, 9.0)
    pcie_x = final.semantic_x_box(final.PCIE_X16_SLOT_X, final.PCIE_X16_SLOT_LENGTH)
    atx24_x = final.semantic_x_box(228.0, 11.0)
    eps_x = final.semantic_x_box(72.0, 18.0)
    dimm_x = final.semantic_x_box(154.0, 3.4)

    # Raw CAD front view contract:
    # screen-left = low X, screen-right = high X.
    if not (io_x < pcie_x < dimm_x < atx24_x):
        fail("raw front X order is wrong: rear I/O, PCIe, DIMM, 24-pin must read left-to-right")
    if not (io_x < eps_x < atx24_x):
        fail("EPS/24-pin X order is wrong")
    if not (final.PCIE_X16_SLOT_Z < 100 and 226.0 > 220):
        fail("PCIe must stay lower and EPS must stay upper in raw front view")

    tray = final.make_tray_part()
    board = final.make_motherboard_part()
    gpu = final.make_gpu_part()

    tray_bb = tray.bounding_box()
    board_bb = board.bounding_box()
    gpu_bb = gpu.bounding_box()

    if not approx(board_bb.max.Y, final.BOARD_BACK_Y):
        fail("motherboard back face is not located on the standoff plane")
    if not approx(tray_bb.min.Y, final.BOARD_BACK_Y):
        fail("tray standoffs do not reach the motherboard back face")
    if not (board_bb.min.Y < tray_bb.min.Y and gpu_bb.min.Y < board_bb.min.Y):
        fail("component/front side is not on the raw CAD front side")
    if not (gpu_bb.max.X > board_bb.max.X):
        fail("GPU must extend to the right/front side in raw front view")

    assembly = final.make_matx_tray_board_gpu_final_3part()
    if len(assembly.children) != 3:
        fail(f"final assembly must have exactly 3 top-level parts, got {len(assembly.children)}")

    print("HANDEDNESS CHECK PASSED")
    print("Raw CAD front-view contract:")
    print("- motherboard component side is the only motherboard front")
    print("- rear I/O: left / low X")
    print("- 24-pin ATX: right / high X")
    print("- PCIe x16 and GPU: lower / low Z, GPU extends right")
    print("- tray is behind the board on positive Y")
    print("- final assembly top-level parts: tray, motherboard, GPU")


if __name__ == "__main__":
    main()
