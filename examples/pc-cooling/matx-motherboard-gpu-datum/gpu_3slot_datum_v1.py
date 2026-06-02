from build123d import *

from motherboard_datum_v1 import (
    BOARD_FRONT_Y,
    PCIE_X16_SLOT_X,
    PCIE_X16_SLOT_Z,
)


# Three-slot GPU datum for case layout.
# Coordinate convention follows VIEW_CONVENTIONS.md and motherboard_datum_v1.py.
# This is a chassis datum, not a detailed graphics card.

GPU_LENGTH = 335.0
GPU_BODY_HEIGHT = 145.0
GPU_COOLER_SLOT_WIDTH = 70.0
GPU_PCB_THICKNESS = 1.6
GPU_COOLER_NEAR_BOARD_CLEARANCE = 20.0

PCI_SLOT_PITCH = 20.32
BRACKET_THICKNESS = 0.86
BRACKET_HEIGHT = 120.11
BRACKET_SLOT_WIDTH = 63.23
BRACKET_MAIN_OPEN_WIDTH = 50.55
BRACKET_HOLE_D = 4.42
BRACKET_SLOT_SCREW_POCKET_D = 6.2
BRACKET_SLOT_SCREW_CLEARANCE_D = 3.6
BRACKET_SLOT_SCREW_FLANGE_X = 8.0
BRACKET_SLOT_SCREW_FLANGE_Y = 5.2

PCI_FINGER_LENGTH = 89.9
PCI_FINGER_VISIBLE_DEPTH = 12.06
PCI_FINGER_HEIGHT = 7.2
PCI_FINGER_X = PCIE_X16_SLOT_X + 0.5

BRACKET_X = -1.5
BRACKET_Y0 = BOARD_FRONT_Y - BRACKET_HEIGHT
BRACKET_Z0 = PCIE_X16_SLOT_Z - 3.0 * PCI_SLOT_PITCH

GPU_PCB_Z0 = PCIE_X16_SLOT_Z - GPU_PCB_THICKNESS / 2.0
COOLER_X0 = 0.0
COOLER_Y0 = BOARD_FRONT_Y - GPU_BODY_HEIGHT
COOLER_Z0 = PCIE_X16_SLOT_Z - GPU_COOLER_SLOT_WIDTH


def box_at(x: float, y: float, z: float, dx: float, dy: float, dz: float):
    return Box(dx, dy, dz).translate((x + dx / 2.0, y + dy / 2.0, z + dz / 2.0))


def cyl_x(x: float, y: float, z: float, radius: float, length: float):
    return Cylinder(radius=radius, height=length, rotation=(0, 90, 0)).translate(
        (x + length / 2.0, y, z)
    )


def cyl_y(x: float, y: float, z: float, radius: float, length: float):
    return Cylinder(radius=radius, height=length, rotation=(90, 0, 0)).translate(
        (x, y + length / 2.0, z)
    )


def make_three_slot_bracket():
    bracket = box_at(
        BRACKET_X,
        BRACKET_Y0,
        BRACKET_Z0,
        BRACKET_THICKNESS,
        BRACKET_HEIGHT,
        BRACKET_SLOT_WIDTH,
    )

    # Five screw/fixture clearance holes from the CEM three-slot bracket datum.
    # They are simplified onto a straight line so the chassis rear-panel datum is
    # visible without recreating the full stamped profile.
    hole_zs = [
        BRACKET_Z0 + 3.31,
        BRACKET_Z0 + 15.30,
        BRACKET_Z0 + 30.23,
        BRACKET_Z0 + 45.75,
        BRACKET_Z0 + 60.06,
    ]
    for z in hole_zs:
        bracket -= cyl_x(BRACKET_X - 0.2, BRACKET_Y0 + BRACKET_HEIGHT - 12.0, z, BRACKET_HOLE_D / 2.0, BRACKET_THICKNESS + 0.4)

    # Three vent/window slots. These are clearance markers for rear-panel design,
    # not a thermal optimization pattern.
    vent_width = BRACKET_MAIN_OPEN_WIDTH / 3.0 - 2.0
    vent_y0 = BRACKET_Y0 + 18.0
    vent_height = 78.0
    for i in range(3):
        z0 = BRACKET_Z0 + 5.11 + i * (BRACKET_MAIN_OPEN_WIDTH / 3.0)
        bracket -= box_at(BRACKET_X - 0.2, vent_y0, z0, BRACKET_THICKNESS + 0.4, vent_height, vent_width)

    # The case locks the GPU from the rear I/O direction. Model the folded
    # retaining flange as an X-Z feature so its three screw pockets are visible
    # in the motherboard front view, one pocket per occupied PCI slot.
    screw_flange_x0 = BRACKET_X - 6.0
    screw_flange_y0 = BRACKET_Y0
    bracket += box_at(
        screw_flange_x0,
        screw_flange_y0,
        BRACKET_Z0,
        BRACKET_SLOT_SCREW_FLANGE_X,
        BRACKET_SLOT_SCREW_FLANGE_Y,
        BRACKET_SLOT_WIDTH,
    )

    slot_screw_x = screw_flange_x0 + BRACKET_SLOT_SCREW_FLANGE_X / 2.0
    slot_screw_y0 = screw_flange_y0 - 0.2
    for i in range(3):
        slot_screw_z = BRACKET_Z0 + PCI_SLOT_PITCH * (i + 0.5)
        bracket -= cyl_y(
            slot_screw_x,
            slot_screw_y0,
            slot_screw_z,
            BRACKET_SLOT_SCREW_POCKET_D / 2.0,
            BRACKET_SLOT_SCREW_FLANGE_Y + 0.4,
        )
        bracket -= cyl_y(
            slot_screw_x,
            slot_screw_y0,
            slot_screw_z,
            BRACKET_SLOT_SCREW_CLEARANCE_D / 2.0,
            BRACKET_SLOT_SCREW_FLANGE_Y + 0.4,
        )

    return bracket


def make_gpu_3slot_datum_v1():
    gpu = make_three_slot_bracket()

    # Rear PCB/flange bridge. It forces the bracket, PCB, cooler body, and
    # finger datum to export as one GPU top-level part, while also marking the
    # rear area that controls the case PCI-slot opening.
    gpu += box_at(
        BRACKET_X,
        BOARD_FRONT_Y - 38.0,
        PCIE_X16_SLOT_Z - 58.0,
        18.0,
        30.0,
        18.0,
    )

    # Main cooler envelope: user target 335 x 70 x 145 mm. In this coordinate
    # system length=X, height away from motherboard=Y, slot width=Z. The cooler
    # is kept slightly away from the motherboard face so the x16 finger remains
    # a visible mating datum instead of being swallowed by a rectangular block.
    gpu += box_at(
        COOLER_X0,
        COOLER_Y0,
        COOLER_Z0,
        GPU_LENGTH,
        GPU_BODY_HEIGHT - GPU_COOLER_NEAR_BOARD_CLEARANCE,
        GPU_COOLER_SLOT_WIDTH,
    )

    # GPU PCB datum plane. The PCIe goldfinger is modeled on this same thin
    # board plane, which is the important mating reference for the assembly.
    gpu += box_at(
        0.0,
        COOLER_Y0,
        GPU_PCB_Z0,
        GPU_LENGTH,
        GPU_BODY_HEIGHT,
        GPU_PCB_THICKNESS,
    )

    # PCIe x16 goldfinger mating datum. It is intentionally modeled as a single
    # wide tab, not individual contacts, because case design only needs the
    # insertion envelope and slot alignment.
    gpu += box_at(
        PCI_FINGER_X,
        BOARD_FRONT_Y - PCI_FINGER_VISIBLE_DEPTH,
        PCIE_X16_SLOT_Z - PCI_FINGER_HEIGHT / 2.0,
        PCI_FINGER_LENGTH,
        PCI_FINGER_VISIBLE_DEPTH,
        PCI_FINGER_HEIGHT,
    )

    # Slightly raised backplate marker above the goldfinger/PCB datum plane. This
    # is the feature the user specifically asked to preserve for side-view
    # clearance relative to the I/O armor lower edge.
    gpu += box_at(
        0.0,
        BOARD_FRONT_Y - 24.0,
        PCIE_X16_SLOT_Z + GPU_PCB_THICKNESS / 2.0,
        GPU_LENGTH,
        2.0,
        3.0,
    )

    gpu = Compound(children=list(gpu)) if isinstance(gpu, ShapeList) else gpu
    gpu.label = "gpu 3slot datum v1 bracket goldfinger 335x70x145"
    gpu.color = Color(0.02, 0.18, 0.88, 1.0)
    return gpu


def gen_step():
    return make_gpu_3slot_datum_v1()


if __name__ == "__main__":
    export_step(gen_step(), "gpu_3slot_datum_v1.step")
