from build123d import *


# Final three-part datum assembly for the mATX case project.
# Coordinate convention follows VIEW_CONVENTIONS.md:
# X: low X is the screen-left/rear I/O side in the raw front view.
#    high X is the screen-right/front side in the raw front view.
# Y: tray normal. Negative Y is motherboard component/front side.
#    Positive Y is tray/back side.
# Z: bottom PCIe side -> top CPU power side
#
# This file intentionally exports only three top-level solids:
# 1. motherboard tray with integrated standoffs
# 2. motherboard datum with integrated connectors/armor
# 3. installed 3-slot GPU with integrated bracket/goldfinger

MATX_SIZE = 243.84
BOARD_THICKNESS = 1.6
TRAY_MARGIN = 5.0
TRAY_THICKNESS = 1.0
STANDOFF_HEIGHT = 6.5
STANDOFF_OD = 6.0
M3_CLEARANCE_D = 3.2

IO_CUTOUT_WIDTH = 158.75
IO_CUTOUT_HEIGHT = 44.45
IO_ARMOR_HEIGHT = 30.0
IO_ARMOR_BEVEL_HEIGHT = 3.0
PCIE_X16_SLOT_X = 34.0
PCIE_X16_SLOT_Z = 72.5
PCIE_X16_SLOT_LENGTH = 90.0
GPU_PCIE_CENTER_OFFSET_Z = 4.0

GPU_LENGTH = 335.0
GPU_SLOT_THICKNESS = 70.0
GPU_HEIGHT_FROM_BOARD = 145.0
PCI_FINGER_LENGTH = 89.0
PCI_FINGER_HEIGHT = 7.2
PCI_FINGER_X_FROM_BRACKET = PCIE_X16_SLOT_X + 0.5
PCI_SLOT_PITCH = 20.32

TRAY_Y_MIN = 0.0
BOARD_BACK_Y = -STANDOFF_HEIGHT
BOARD_FRONT_Y = -(STANDOFF_HEIGHT + BOARD_THICKNESS)

MATX_8_HOLE_PATTERN = [
    ("B", 10.16, 30.48),
    ("C", 10.16, 83.72),
    ("F", 22.86, 233.68),
    ("R", 165.10, 30.48),
    ("H", 165.10, 83.72),
    ("J", 165.10, 233.68),
    ("L", 233.68, 83.72),
    ("M", 233.68, 233.68),
]


def box_at(x: float, y: float, z: float, dx: float, dy: float, dz: float):
    return Box(dx, dy, dz).translate((x + dx / 2, y + dy / 2, z + dz / 2))


def semantic_x_box(x_from_rear: float, dx: float):
    """Convert a rear-to-front motherboard X coordinate into model X."""
    return x_from_rear


def semantic_x_center(x_from_rear: float):
    return x_from_rear


def sem_box_at(x_from_rear: float, y: float, z: float, dx: float, dy: float, dz: float):
    return box_at(semantic_x_box(x_from_rear, dx), y, z, dx, dy, dz)


def component_box_at(x_from_rear: float, y_from_board_front: float, z: float, dx: float, dy: float, dz: float):
    return sem_box_at(x_from_rear, BOARD_FRONT_Y - y_from_board_front - dy, z, dx, dy, dz)


def prism_xz(vertices: list[tuple[float, float]], plane_offset: float, dy: float):
    with BuildPart() as part:
        with BuildSketch(Plane.XZ.offset(plane_offset)):
            with BuildLine():
                Polyline(*vertices, close=True)
            make_face()
        extrude(amount=dy)
    return part.part


def component_prism_xz(vertices: list[tuple[float, float]], y_from_board_front: float, dy: float):
    # build123d's XZ plane offset is signed opposite the exported Y location.
    # Use the plane that extrudes back to the motherboard front face.
    plane_offset = -(BOARD_FRONT_Y - y_from_board_front)
    return prism_xz(vertices, plane_offset, dy).solid()


def cyl_y(x: float, y: float, z: float, radius: float, length: float):
    return Cylinder(radius=radius, height=length, rotation=(90, 0, 0)).translate(
        (x, y + length / 2, z)
    )


def sem_cyl_y(x_from_rear: float, y: float, z: float, radius: float, length: float):
    return cyl_y(semantic_x_center(x_from_rear), y, z, radius, length)


def make_tray_part():
    tray = box_at(
        -TRAY_MARGIN,
        TRAY_Y_MIN,
        -TRAY_MARGIN,
        MATX_SIZE + 2 * TRAY_MARGIN,
        TRAY_THICKNESS,
        MATX_SIZE + 2 * TRAY_MARGIN,
    )

    for _, x, z in MATX_8_HOLE_PATTERN:
        # Standoffs overlap the tray by 0.05mm so the STEP imports as one tray part.
        tray += sem_cyl_y(x, -STANDOFF_HEIGHT, z, STANDOFF_OD / 2, STANDOFF_HEIGHT + 0.05)
        tray -= sem_cyl_y(x, -STANDOFF_HEIGHT - 0.2, z, M3_CLEARANCE_D / 2, STANDOFF_HEIGHT + TRAY_THICKNESS + 0.6)

    tray.label = "01 motherboard tray integrated standoffs"
    tray.color = Color(0.62, 0.64, 0.66, 1.0)
    return tray


def make_motherboard_part():
    board = box_at(0, BOARD_FRONT_Y, 0, MATX_SIZE, BOARD_THICKNESS, MATX_SIZE)

    for _, x, z in MATX_8_HOLE_PATTERN:
        board -= sem_cyl_y(x, BOARD_FRONT_Y - 0.2, z, 2.0, BOARD_THICKNESS + 0.4)

    io_z0 = MATX_SIZE - IO_CUTOUT_WIDTH

    # Rear I/O and VRM armor, restored from the earlier accepted board concept.
    # The rear I/O strip uses the ATX I/O cutout height as its side-view datum.
    board += component_box_at(0.0, 0.0, io_z0, 10.0, IO_CUTOUT_HEIGHT, IO_CUTOUT_WIDTH)
    board += component_prism_xz(
        [(0.0, 90.0), (18.0, 90.0), (50.0, 152.0), (50.0, 214.0), (30.0, 222.0), (0.0, 222.0)],
        0.0,
        IO_ARMOR_HEIGHT,
    )
    board += component_prism_xz(
        [(5.0, 98.0), (20.0, 98.0), (43.0, 150.0), (43.0, 207.0), (26.0, 214.0), (5.0, 214.0)],
        IO_ARMOR_HEIGHT,
        IO_ARMOR_BEVEL_HEIGHT,
    )
    # Simplified rear I/O ports recessed into the rear I/O block.
    for z in (105.0, 121.0, 140.0, 159.0, 182.0, 205.0):
        board -= component_box_at(0.6, 0.6, z, 2.6, IO_CUTOUT_HEIGHT - 1.2, 9.5)
    board -= component_box_at(0.6, 0.6, 223.0, 2.6, IO_CUTOUT_HEIGHT - 1.2, 14.0)

    # Board-level layout datums: first x16 slot and cable connectors.
    board += component_box_at(PCIE_X16_SLOT_X, 0.0, PCIE_X16_SLOT_Z, PCIE_X16_SLOT_LENGTH, 5.0, 8.5)
    board += component_box_at(PCIE_X16_SLOT_X + PCIE_X16_SLOT_LENGTH - 2.0, 0.0, PCIE_X16_SLOT_Z - 1.6, 8.0, 5.6, 11.7)
    board += component_box_at(58.0, 0.0, 229.5, 18.0, 8.5, 12.5)
    board += component_box_at(80.0, 0.0, 229.5, 18.0, 8.5, 12.5)
    board += component_box_at(228.0, 0.0, 118.0, 11.0, 8.5, 52.0)

    # Keep only coarse DIMM datum ribs; detailed slots are not chassis-critical.
    for x in (154.0, 164.0, 174.0, 184.0):
        board += component_box_at(x, 0.0, 116.0, 3.4, 5.0, 92.0)

    board.label = "02 mATX motherboard datum integrated features"
    board.color = Color(0.02, 0.40, 0.16, 1.0)
    return board


def make_gpu_part():
    slot_z0 = PCIE_X16_SLOT_Z - GPU_SLOT_THICKNESS
    slot_z1 = PCIE_X16_SLOT_Z

    gpu = component_box_at(0, 24.0, slot_z0, GPU_LENGTH, GPU_HEIGHT_FROM_BOARD - 24.0, GPU_SLOT_THICKNESS)
    # Single PCB/web datum that ties the goldfinger, backplate, and cooler body
    # together. This replaces the previous two erroneous loose blue thin plates.
    gpu += component_box_at(0, 0.0, slot_z0 + 2.0, GPU_LENGTH, 25.0, GPU_SLOT_THICKNESS + 6.0)
    # One backplate only. It sits slightly away from the motherboard/goldfinger
    # datum plane, closer to the lower edge of the rear I/O armor in side view.
    gpu += component_box_at(0, 11.0, slot_z0 + 4.0, GPU_LENGTH, 2.0, GPU_SLOT_THICKNESS - 8.0)

    # PCIe goldfinger is the mating datum: aligned to the motherboard x16 slot.
    gpu += component_box_at(
        PCI_FINGER_X_FROM_BRACKET,
        0.0,
        PCIE_X16_SLOT_Z - PCI_FINGER_HEIGHT / 2,
        PCI_FINGER_LENGTH,
        7.2,
        PCI_FINGER_HEIGHT,
    )
    bracket_span = 3 * PCI_SLOT_PITCH
    gpu += component_box_at(-1.5, 0.0, PCIE_X16_SLOT_Z - bracket_span, 1.6, 128.0, bracket_span)

    gpu.label = "03 three slot GPU 335x70x145 integrated bracket"
    gpu.color = Color(0.02, 0.18, 0.88, 1.0)
    return gpu


def make_matx_tray_board_gpu_final_3part():
    assembly = Compound(children=[make_tray_part(), make_motherboard_part(), make_gpu_part()])
    assembly.label = "matx_tray_board_gpu_final_3part"
    return assembly


def gen_step():
    return make_matx_tray_board_gpu_final_3part()


if __name__ == "__main__":
    export_step(gen_step(), "matx_tray_board_gpu_final_3part.step")
