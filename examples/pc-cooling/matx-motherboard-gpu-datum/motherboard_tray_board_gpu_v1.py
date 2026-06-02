from build123d import *

from motherboard_tray_v1 import make_motherboard_tray_v1
from motherboard_datum_v1 import make_motherboard_datum_v1
from gpu_3slot_datum_v1 import make_gpu_3slot_datum_v1


def make_motherboard_tray_board_gpu_v1():
    assembly = Compound(
        children=[
            make_motherboard_tray_v1(),
            make_motherboard_datum_v1(),
            make_gpu_3slot_datum_v1(),
        ]
    )
    assembly.label = "motherboard_tray_board_gpu_v1"
    return assembly


def gen_step():
    return make_motherboard_tray_board_gpu_v1()


if __name__ == "__main__":
    export_step(gen_step(), "motherboard_tray_board_gpu_v1.step")
