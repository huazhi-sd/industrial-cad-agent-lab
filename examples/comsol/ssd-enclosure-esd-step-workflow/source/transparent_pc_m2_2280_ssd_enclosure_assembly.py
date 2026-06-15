from pathlib import Path

from build123d import *

# M.2 2280 transparent PC external SSD enclosure concept.
# Units: mm.
# Export rule: one assembly STEP with top-level material/potential domains:
# PC shells, PCB/SSD dielectric boards, coarse conductor regions, USB-C shell, and screw.

CASE_L = 112.0
CASE_W = 38.0
CASE_H = 12.0
WALL = 1.8
BASE_T = 1.8
LID_T = 1.8
BOTTOM_WALL_H = 8.45
BOTTOM_DAM_T = 0.8
BOTTOM_DAM_H = 7.2
TOP_TONGUE_T = 1.0
TOP_TONGUE_H = 4.1
SEAM_CLEARANCE = 0.0
CONTACT_RELIEF = 0.35
USB_C_PORT_W = 9.0
USB_C_PORT_H = 3.4
USB_C_FRAME_W = 12.2
USB_C_FRAME_H = 6.4
USB_C_FRAME_T = 1.0
USB_C_SHELL_W = 8.8
USB_C_SHELL_H = 3.2
USB_C_SHELL_INNER_W = 6.7
USB_C_SHELL_INNER_H = 1.8
TOP_USB_RELIEF_W = 15.0
TOP_USB_RELIEF_H = 8.0
USB_FRONT_OPENING_W = USB_C_PORT_W
SNAP_XS = [-34.0, 34.0]
SNAP_WINDOW_L = 8.0
SNAP_WINDOW_H = 1.35
SNAP_LUG_L = 6.0
SNAP_LUG_H = 0.85
PCB_L = 100.0
PCB_W = 28.0
PCB_T = 1.2
SSD_L = 80.0
SSD_W = 22.0
SSD_T = 1.0
COPPER_T = 0.08
EPS = 0.05
PCB_Z = BASE_T + 1.0 + PCB_T / 2
PCB_TOP_Z = PCB_Z + PCB_T / 2
SSD_CENTER_X = 5.0
SSD_TAIL_X = SSD_CENTER_X + SSD_L / 2
SSD_Z = PCB_TOP_Z + 1.1 + SSD_T / 2
SSD_TOP_Z = SSD_Z + SSD_T / 2
PCB_MOUNT_POINTS = [(-42.0, -10.5), (-42.0, 10.5), (42.0, -10.5), (42.0, 10.5)]
M2_SCREW_X = SSD_TAIL_X
M2_SCREW_Y = 0.0
USB_C_CENTER_Z = PCB_TOP_Z + 1.6
TOP_UNDERSIDE_Z = CASE_H - LID_T
TOP_TONGUE_Y = CASE_W / 2 - WALL - SEAM_CLEARANCE - TOP_TONGUE_T / 2
BOTTOM_DAM_Y = CASE_W / 2 - WALL - 1.0 - BOTTOM_DAM_T / 2
TOP_REAR_TONGUE_X = CASE_L / 2 - WALL - SEAM_CLEARANCE - TOP_TONGUE_T / 2
BOTTOM_REAR_DAM_X = CASE_L / 2 - WALL - 1.0 - BOTTOM_DAM_T / 2
TOP_FRONT_TONGUE_X = -TOP_REAR_TONGUE_X
BOTTOM_FRONT_DAM_X = -BOTTOM_REAR_DAM_X
SNAP_Z = BASE_T - EPS + 4.6


def box_at(size, loc):
    return Box(*size).translate(loc)


def capsule_x(depth, width, height, loc):
    """Rounded-rectangle prism along X for simplified USB-C openings/shells."""
    radius = height / 2
    mid_width = max(width - height, 0.01)
    core = Box(depth, mid_width, height)
    left_round = Cylinder(radius=radius, height=depth).rotate(Axis.Y, 90).translate((0, -mid_width / 2, 0))
    right_round = Cylinder(radius=radius, height=depth).rotate(Axis.Y, 90).translate((0, mid_width / 2, 0))
    return (core + left_round + right_round).translate(loc)


def usb_c_plastic_frame(depth, loc):
    """PC reinforcement around the Type-C opening; the center remains open."""
    outer = capsule_x(depth, USB_C_FRAME_W, USB_C_FRAME_H, loc)
    inner = capsule_x(depth + 0.6, USB_C_PORT_W, USB_C_PORT_H, loc)
    return outer - inner


def fuse_all(shapes, label):
    fused = shapes[0]
    for shape in shapes[1:]:
        fused = fused + shape
    if isinstance(fused, ShapeList):
        return Part(fused, label=label)
    return Part([fused], label=label)


def make_bottom_shell():
    base = box_at((CASE_L, CASE_W, BASE_T), (0, 0, BASE_T / 2))
    wall_z = BASE_T - EPS + BOTTOM_WALL_H / 2

    def side_wall(sign):
        wall = box_at((CASE_L, WALL, BOTTOM_WALL_H), (0, sign * (CASE_W / 2 - WALL / 2), wall_z))
        for x in SNAP_XS:
            window = box_at(
                (SNAP_WINDOW_L, WALL + 1.0, SNAP_WINDOW_H),
                (x, sign * (CASE_W / 2 - WALL / 2), SNAP_Z),
            )
            wall = wall - window
        return wall

    left_wall = side_wall(-1)
    right_wall = side_wall(1)
    rear_wall = box_at((WALL, CASE_W, BOTTOM_WALL_H), (CASE_L / 2 - WALL / 2, 0, wall_z))

    usb_port_cut = capsule_x(
        WALL + 1.2,
        USB_C_PORT_W,
        USB_C_PORT_H,
        (-CASE_L / 2 + WALL / 2, 0, USB_C_CENTER_Z),
    )
    front_wall = box_at((WALL, CASE_W, BOTTOM_WALL_H), (-CASE_L / 2 + WALL / 2, 0, wall_z)) - usb_port_cut

    dam_z = BASE_T - EPS + BOTTOM_DAM_H / 2
    side_dam_l = 2 * (BOTTOM_REAR_DAM_X + BOTTOM_DAM_T / 2)
    left_inner_dam = box_at((side_dam_l, BOTTOM_DAM_T, BOTTOM_DAM_H), (0.0, -BOTTOM_DAM_Y, dam_z))
    right_inner_dam = box_at((side_dam_l, BOTTOM_DAM_T, BOTTOM_DAM_H), (0.0, BOTTOM_DAM_Y, dam_z))
    dam_cross_w = 2 * (BOTTOM_DAM_Y + BOTTOM_DAM_T / 2)
    rear_inner_dam = box_at((BOTTOM_DAM_T, dam_cross_w, BOTTOM_DAM_H), (BOTTOM_REAR_DAM_X, 0, dam_z))
    front_inner_dam = box_at((BOTTOM_DAM_T, dam_cross_w, BOTTOM_DAM_H), (BOTTOM_FRONT_DAM_X, 0, dam_z))
    front_inner_dam = front_inner_dam - capsule_x(
        BOTTOM_DAM_T + 1.2,
        USB_C_PORT_W,
        USB_C_PORT_H,
        (BOTTOM_FRONT_DAM_X, 0, USB_C_CENTER_Z),
    )
    front_usb_frame = usb_c_plastic_frame(
        WALL + 0.7,
        (-CASE_L / 2 + WALL / 2, 0, USB_C_CENTER_Z),
    )
    front_dam_usb_frame = usb_c_plastic_frame(
        BOTTOM_DAM_T + 0.5,
        (BOTTOM_FRONT_DAM_X, 0, USB_C_CENTER_Z),
    )
    dam_corner_blocks = [
        box_at(
            (BOTTOM_DAM_T, BOTTOM_DAM_T, BOTTOM_DAM_H),
            (x, y, dam_z),
        )
        for x in [BOTTOM_FRONT_DAM_X, BOTTOM_REAR_DAM_X]
        for y in [-BOTTOM_DAM_Y, BOTTOM_DAM_Y]
    ]

    rail_l = box_at((92.0, 1.2, 1.0), (4.0, -PCB_W / 2 - 1.4, BASE_T - EPS + 0.5))
    rail_r = box_at((92.0, 1.2, 1.0), (4.0, PCB_W / 2 + 1.4, BASE_T - EPS + 0.5))

    bosses = []
    for x, y in PCB_MOUNT_POINTS:
        boss = Cylinder(radius=2.8, height=1.0).translate((x, y, BASE_T - EPS + 0.5))
        hole = Cylinder(radius=1.15, height=1.6).translate((x, y, BASE_T - EPS + 0.8))
        bosses.append(boss - hole)

    return fuse_all(
        [
            base,
            left_wall,
            right_wall,
            rear_wall,
            front_wall,
            left_inner_dam,
            right_inner_dam,
            rear_inner_dam,
            front_inner_dam,
            *dam_corner_blocks,
            front_usb_frame,
            front_dam_usb_frame,
            rail_l,
            rail_r,
            *bosses,
        ],
        "bottom_shell_transparent_pc",
    )


def make_top_shell():
    top_plate = box_at((CASE_L, CASE_W, LID_T), (0, 0, CASE_H - LID_T / 2))
    tongue_z = TOP_UNDERSIDE_Z + EPS - TOP_TONGUE_H / 2
    tongue_outer_l = 2 * (TOP_REAR_TONGUE_X + TOP_TONGUE_T / 2)
    tongue_outer_w = 2 * (TOP_TONGUE_Y + TOP_TONGUE_T / 2)
    tongue_inner_l = tongue_outer_l - 2 * TOP_TONGUE_T
    tongue_inner_w = tongue_outer_w - 2 * TOP_TONGUE_T
    tongue_frame = box_at((tongue_outer_l, tongue_outer_w, TOP_TONGUE_H), (0, 0, tongue_z))
    tongue_frame = tongue_frame - box_at((tongue_inner_l, tongue_inner_w, TOP_TONGUE_H + 0.4), (0, 0, tongue_z))
    tongue_frame = tongue_frame - capsule_x(
        TOP_TONGUE_T + 1.2,
        TOP_USB_RELIEF_W,
        TOP_USB_RELIEF_H,
        (TOP_FRONT_TONGUE_X, 0, USB_C_CENTER_Z),
    )

    snap_lugs = []
    for x in SNAP_XS:
        snap_lugs.append(box_at((SNAP_LUG_L, 0.55, SNAP_LUG_H), (x, TOP_TONGUE_Y + 0.48, SNAP_Z)))
        snap_lugs.append(box_at((SNAP_LUG_L, 0.55, SNAP_LUG_H), (x, -TOP_TONGUE_Y - 0.48, SNAP_Z)))

    return fuse_all(
        [
            top_plate,
            tongue_frame,
            *snap_lugs,
        ],
        "top_shell_transparent_pc",
    )


def make_main_pcb():
    board = Box(PCB_L, PCB_W, PCB_T).translate((0, 0, PCB_Z))
    for x, y in PCB_MOUNT_POINTS:
        board = board - Cylinder(radius=1.25, height=3.0).translate((x, y, PCB_Z))

    m2_socket = box_at((8.5, 24.0, 0.8), (-31.0, 0, PCB_TOP_Z + 0.4 - EPS))
    usb_c_tongue = capsule_x(5.7, 5.2, 0.72, (-CASE_L / 2 + 1.4, 0, USB_C_CENTER_Z))
    controller = box_at((9.0, 9.0, 0.9), (-12.0, -7.5, PCB_TOP_Z + 0.45 - EPS))
    regulator = box_at((5.0, 4.0, 0.8), (-8.0, 8.0, PCB_TOP_Z + 0.4 - EPS))
    led = box_at((1.8, 1.2, 0.5), (-46.0, 10.0, PCB_TOP_Z + 0.25 - EPS))
    standoff = Cylinder(radius=1.5, height=1.05).translate((M2_SCREW_X, M2_SCREW_Y, PCB_TOP_Z + 0.525 - EPS))
    standoff = standoff - Cylinder(radius=0.75, height=1.4).translate((M2_SCREW_X, M2_SCREW_Y, PCB_TOP_Z + 0.7))

    passives = []
    for x in [-22, -18, -14, -10, -6]:
        passives.append(box_at((2.0, 1.0, 0.45), (x, 11.0, PCB_TOP_Z + 0.225 - EPS)))
    for x in [4, 8, 12, 16]:
        passives.append(box_at((1.6, 0.9, 0.4), (x, -11.0, PCB_TOP_Z + 0.2 - EPS)))

    return fuse_all(
        [board, m2_socket, usb_c_tongue, controller, regulator, led, standoff, *passives],
        "main_pcb_fr4_and_components",
    )


def make_usb_c_shell_metal():
    outer = capsule_x(7.5, USB_C_SHELL_W, USB_C_SHELL_H, (-CASE_L / 2 + 3.75, 0, USB_C_CENTER_Z))
    inner = capsule_x(8.2, USB_C_SHELL_INNER_W, USB_C_SHELL_INNER_H, (-CASE_L / 2 + 3.75, 0, USB_C_CENTER_Z))
    return Part([outer - inner], label="usb_c_shell_metal_ground")


def make_main_pcb_high_voltage_copper():
    z = PCB_TOP_Z + COPPER_T / 2
    usb_vbus_pads = []
    for y in [-2.4, -1.2, 0.0, 1.2, 2.4]:
        usb_vbus_pads.append(box_at((2.8, 0.45, COPPER_T), (-48.0, y, z)))

    trace = box_at((30.0, 1.2, COPPER_T), (-31.5, -2.2, z))
    regulator_pad = box_at((8.0, 5.2, COPPER_T), (-14.0, 7.8, z))
    test_pad = Cylinder(radius=1.2, height=COPPER_T).translate((-5.0, 9.8, z))
    m2_power_fingers = []
    for y in [-8.0, -7.0, -6.0, -5.0]:
        m2_power_fingers.append(box_at((2.2, 0.45, COPPER_T), (-33.6, y, z)))

    return fuse_all(
        [*usb_vbus_pads, trace, regulator_pad, test_pad, *m2_power_fingers],
        "main_pcb_high_potential_copper",
    )


def make_main_pcb_ground_copper():
    z = PCB_TOP_Z + COPPER_T / 2
    regions = [
        box_at((88.0, 1.4, COPPER_T), (2.0, -12.0, z)),
        box_at((88.0, 1.4, COPPER_T), (2.0, 12.0, z)),
        box_at((12.0, 20.0, COPPER_T), (-45.0, 0, z)),
        box_at((22.0, 3.0, COPPER_T), (-27.0, 8.6, z)),
    ]
    for x, y in PCB_MOUNT_POINTS:
        pad = Cylinder(radius=2.1, height=COPPER_T).translate((x, y, z))
        hole = Cylinder(radius=1.25, height=COPPER_T + 0.3).translate((x, y, z))
        regions.append(pad - hole)

    m2_tail_pad = Cylinder(radius=2.7, height=COPPER_T).translate((M2_SCREW_X, M2_SCREW_Y, z))
    m2_tail_hole = Cylinder(radius=0.9, height=COPPER_T + 0.3).translate((M2_SCREW_X, M2_SCREW_Y, z))
    regions.append(m2_tail_pad - m2_tail_hole)

    return fuse_all(regions, "main_pcb_ground_copper")


def make_ssd_2280():
    board = Box(SSD_L, SSD_W, SSD_T).translate((SSD_CENTER_X, 0, SSD_Z))
    board = board - Cylinder(radius=1.75, height=2.0).translate((SSD_TAIL_X, 0, SSD_Z))

    notch_mark = box_at((1.0, 3.5, 0.22), (SSD_CENTER_X - SSD_L / 2 + 0.8, 7.0, SSD_TOP_Z + 0.11 - EPS))
    packages = [
        box_at((8.0, 8.0, 0.9), (-10.0, -5.5, SSD_TOP_Z + 0.45 - EPS)),
        box_at((12.0, 10.0, 0.9), (8.0, -5.5, SSD_TOP_Z + 0.45 - EPS)),
        box_at((12.0, 10.0, 0.9), (25.0, -5.5, SSD_TOP_Z + 0.45 - EPS)),
        box_at((5.5, 5.5, 0.7), (0.0, 6.0, SSD_TOP_Z + 0.35 - EPS)),
    ]

    return fuse_all([board, notch_mark, *packages], "m2_2280_ssd_fr4_and_components")


def make_ssd_exposed_copper():
    z = SSD_TOP_Z + COPPER_T / 2
    regions = [
        box_at((5.2, SSD_W - 2.0, COPPER_T), (SSD_CENTER_X - SSD_L / 2 + 3.6, 0, z)),
        box_at((18.0, 16.0, COPPER_T), (-12.0, 0.0, z)),
        box_at((22.0, 16.0, COPPER_T), (16.0, 0.0, z)),
    ]
    tail_pad = Cylinder(radius=3.0, height=COPPER_T).translate((SSD_TAIL_X, 0, z))
    tail_cut = Cylinder(radius=1.75, height=COPPER_T + 0.3).translate((SSD_TAIL_X, 0, z))
    regions.append(tail_pad - tail_cut)
    return fuse_all(regions, "ssd_exposed_copper_regions")


def make_m2_tail_screw():
    shaft = Cylinder(radius=0.85, height=2.8).translate((M2_SCREW_X, M2_SCREW_Y, PCB_TOP_Z + 1.45))
    head = Cylinder(radius=2.15, height=0.75).translate((M2_SCREW_X, M2_SCREW_Y, SSD_TOP_Z + 0.55))
    drive_slot = box_at((2.6, 0.45, 0.25), (M2_SCREW_X, M2_SCREW_Y, SSD_TOP_Z + 0.95))
    screw = fuse_all([shaft, head], "m2_tail_screw")
    screw = Part([screw - drive_slot], label="m2_tail_screw")
    return screw


bottom_shell = make_bottom_shell()
top_shell = make_top_shell()
main_pcb = make_main_pcb()
usb_c_shell_metal = make_usb_c_shell_metal()
main_pcb_high_voltage_copper = make_main_pcb_high_voltage_copper()
main_pcb_ground_copper = make_main_pcb_ground_copper()
ssd_2280 = make_ssd_2280()
ssd_exposed_copper = make_ssd_exposed_copper()
m2_tail_screw = make_m2_tail_screw()

assembly = Compound(
    children=[
        bottom_shell,
        top_shell,
        main_pcb,
        usb_c_shell_metal,
        main_pcb_high_voltage_copper,
        main_pcb_ground_copper,
        ssd_2280,
        ssd_exposed_copper,
        m2_tail_screw,
    ],
    label="transparent_pc_m2_2280_ssd_enclosure_assembly",
)

if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "transparent_pc_m2_2280_ssd_enclosure_assembly.step"
    export_step(assembly, output)
    print(output)
