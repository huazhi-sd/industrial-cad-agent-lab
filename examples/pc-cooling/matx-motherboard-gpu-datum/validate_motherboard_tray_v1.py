from pathlib import Path
import importlib.util
import re


ROOT = Path(__file__).resolve().parent
FORBIDDEN_CAD_OPS = re.compile(r"(\.mirror\s*\(|\bmirror\s*\(|\.scale\s*\(|\bscale\s*\()")


def fail(message: str):
    raise SystemExit(f"TRAY V1 CHECK FAILED: {message}")


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
    script = ROOT / "motherboard_tray_v1.py"
    text = script.read_text(encoding="utf-8")
    match = FORBIDDEN_CAD_OPS.search(text)
    if match:
        fail(f"forbidden mirror/scale-like CAD operation: {match.group(0)}")

    tray_mod = load_module("motherboard_tray_v1.py")

    holes = {name: (x, z) for name, x, z in tray_mod.MATX_8_HOLE_PATTERN}
    required = {"B", "C", "F", "R", "H", "J", "L", "M"}
    if set(holes) != required:
        fail(f"expected 8 mATX holes {sorted(required)}, got {sorted(holes)}")

    tray = tray_mod.make_motherboard_tray_v1()
    bb = tray.bounding_box()

    expected_size = tray_mod.MATX_SIZE + 2 * tray_mod.TRAY_MARGIN
    if not approx(bb.size.X, expected_size):
        fail(f"tray X size {bb.size.X:.3f} != {expected_size:.3f}")
    if not approx(bb.size.Z, expected_size):
        fail(f"tray Z size {bb.size.Z:.3f} != {expected_size:.3f}")
    if not approx(bb.min.Y, -tray_mod.STANDOFF_HEIGHT):
        fail(f"standoffs must extend to Y=-{tray_mod.STANDOFF_HEIGHT}, got {bb.min.Y:.3f}")
    if not (bb.max.Y > tray_mod.TRAY_THICKNESS):
        fail("back-side board-envelope markers are missing")

    print("TRAY V1 CHECK PASSED")
    print(f"- mATX holes: {', '.join(sorted(holes))}")
    print(f"- tray envelope: {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm")
    print(f"- standoff height: {tray_mod.STANDOFF_HEIGHT:.2f} mm")
    print("- rear I/O side marker: low X")


if __name__ == "__main__":
    main()
