from pathlib import Path

from build123d import *

import transparent_pc_m2_2280_ssd_enclosure_assembly as base

# Standard-part trial for the M.2 tail fastener stack.
# Units: mm.
#
# Catalog candidates used as traceable references:
# - screw: iso4762_socket_head_cap_screw_m2x3
# - boss candidate checked but rejected by height: pcb_standoff_boss_m2_h04
#
# The M2x3 screw can fit the current stack, but a 4 mm PCB boss is too tall for
# this compact enclosure. The installed boss is therefore an application-sized
# M.2 tail standoff derived from the PCB-to-SSD gap.

SCREW_CATALOG_ID = "iso4762_socket_head_cap_screw_m2x3"
REJECTED_BOSS_CATALOG_ID = "pcb_standoff_boss_m2_h04"

SCREW_THREAD_DIAMETER = 2.0
SCREW_SHANK_RADIUS = SCREW_THREAD_DIAMETER / 2
SCREW_HEAD_DIAMETER = 3.8
SCREW_HEAD_HEIGHT = 2.0
SCREW_NOMINAL_LENGTH = 3.0
SCREW_DRIVE_SLOT_W = 2.35
SCREW_DRIVE_SLOT_D = 0.42
SCREW_DRIVE_SLOT_H = 0.35

CATALOG_BOSS_HEIGHT = 4.0
CUSTOM_STANDOFF_HEIGHT = (base.SSD_Z - base.SSD_T / 2) - base.PCB_TOP_Z
CUSTOM_STANDOFF_RADIUS = 2.5
CUSTOM_STANDOFF_HOLE_RADIUS = 1.05


def make_main_pcb_without_tail_standoff():
    board = Box(base.PCB_L, base.PCB_W, base.PCB_T).translate((0, 0, base.PCB_Z))
    for x, y in base.PCB_MOUNT_POINTS:
        board = board - Cylinder(radius=1.25, height=3.0).translate((x, y, base.PCB_Z))

    m2_socket = base.box_at((8.5, 24.0, 0.8), (-31.0, 0, base.PCB_TOP_Z + 0.4 - base.EPS))
    controller = base.box_at((9.0, 9.0, 0.9), (-12.0, -7.5, base.PCB_TOP_Z + 0.45 - base.EPS))
    regulator = base.box_at((5.0, 4.0, 0.8), (-8.0, 8.0, base.PCB_TOP_Z + 0.4 - base.EPS))
    led = base.box_at((1.8, 1.2, 0.5), (-46.0, 10.0, base.PCB_TOP_Z + 0.25 - base.EPS))

    passives = []
    for x in [-22, -18, -14, -10, -6]:
        passives.append(base.box_at((2.0, 1.0, 0.45), (x, 11.0, base.PCB_TOP_Z + 0.225 - base.EPS)))
    for x in [4, 8, 12, 16]:
        passives.append(base.box_at((1.6, 0.9, 0.4), (x, -11.0, base.PCB_TOP_Z + 0.2 - base.EPS)))

    return base.fuse_all(
        [board, m2_socket, controller, regulator, led, *passives],
        "main_pcb_fr4_and_components_no_tail_standoff",
    )


def make_m2_tail_standoff():
    center_z = base.PCB_TOP_Z + CUSTOM_STANDOFF_HEIGHT / 2
    boss = Cylinder(radius=CUSTOM_STANDOFF_RADIUS, height=CUSTOM_STANDOFF_HEIGHT).translate(
        (base.M2_SCREW_X, base.M2_SCREW_Y, center_z)
    )
    pilot = Cylinder(radius=CUSTOM_STANDOFF_HOLE_RADIUS, height=CUSTOM_STANDOFF_HEIGHT + 0.6).translate(
        (base.M2_SCREW_X, base.M2_SCREW_Y, center_z)
    )
    return Part([boss - pilot], label="m2_ssd_tail_standoff_custom_1p10mm")


def make_iso4762_m2x3_tail_screw():
    head_center_z = base.SSD_TOP_Z + SCREW_HEAD_HEIGHT / 2
    shank_center_z = base.SSD_TOP_Z - SCREW_NOMINAL_LENGTH / 2

    head = Cylinder(radius=SCREW_HEAD_DIAMETER / 2, height=SCREW_HEAD_HEIGHT).translate(
        (base.M2_SCREW_X, base.M2_SCREW_Y, head_center_z)
    )
    shank = Cylinder(radius=SCREW_SHANK_RADIUS, height=SCREW_NOMINAL_LENGTH).translate(
        (base.M2_SCREW_X, base.M2_SCREW_Y, shank_center_z)
    )
    slot = base.box_at(
        (SCREW_DRIVE_SLOT_W, SCREW_DRIVE_SLOT_D, SCREW_DRIVE_SLOT_H),
        (base.M2_SCREW_X, base.M2_SCREW_Y, base.SSD_TOP_Z + SCREW_HEAD_HEIGHT - SCREW_DRIVE_SLOT_H / 2),
    )
    screw = (head + shank) - slot
    return Part([screw], label="standard_iso4762_m2x3_tail_screw")


def gen_step():
    bottom_shell = base.make_bottom_shell()
    top_shell = base.make_top_shell()
    main_pcb = make_main_pcb_without_tail_standoff()
    usb_c_shell_metal = base.make_usb_c_shell_metal()
    main_pcb_high_voltage_copper = base.make_main_pcb_high_voltage_copper()
    main_pcb_ground_copper = base.make_main_pcb_ground_copper()
    ssd_2280 = base.make_ssd_2280()
    ssd_exposed_copper = base.make_ssd_exposed_copper()
    tail_standoff = make_m2_tail_standoff()
    tail_screw = make_iso4762_m2x3_tail_screw()

    return Compound(
        children=[
            bottom_shell,
            top_shell,
            main_pcb,
            usb_c_shell_metal,
            main_pcb_high_voltage_copper,
            main_pcb_ground_copper,
            ssd_2280,
            ssd_exposed_copper,
            tail_standoff,
            tail_screw,
        ],
        label="transparent_pc_m2_2280_ssd_enclosure_standard_fastener_trial",
    )


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "ssd_enclosure_standard_fastener_trial.step"
    export_step(gen_step(), output)
    print(output)
