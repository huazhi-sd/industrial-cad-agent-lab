#!/usr/bin/env python3
"""Generate a close-coiled torsion spring STEP with a continuous swept wire."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.gp import gp_Pnt


def parse_vec(text: str) -> cq.Vector:
    parts = [float(p.strip()) for p in text.split(",")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("vector must be x,y,z")
    vec = cq.Vector(*parts)
    if vec.Length <= 1e-9:
        raise argparse.ArgumentTypeError("vector length must be non-zero")
    return vec.normalized()


def angle_between(a: cq.Vector, b: cq.Vector) -> float:
    dot = max(-1.0, min(1.0, a.normalized().dot(b.normalized())))
    return math.acos(dot)


def helix_edge(pitch: float, coil_width: float, radius: float, phase_deg: float):
    helix = cq.Wire.makeHelix(
        pitch=pitch,
        height=coil_width,
        radius=radius,
        center=(0, 0, 0),
        dir=(1, 0, 0),
    )
    if phase_deg:
        helix = helix.rotate((0, 0, 0), (1, 0, 0), phase_deg)
    return helix.Edges()[0]


def best_phase(
    pitch: float,
    coil_width: float,
    radius: float,
    leg_a_dir: cq.Vector | None,
    leg_b_dir: cq.Vector | None,
) -> float:
    if leg_a_dir is None and leg_b_dir is None:
        return 0.0

    best = (float("inf"), 0.0)
    for phase in [i * 0.5 for i in range(720)]:
        edge = helix_edge(pitch, coil_width, radius, phase)
        tan_start = edge.tangentAt(0).normalized()
        tan_end = edge.tangentAt(1).normalized()
        err = 0.0
        if leg_a_dir is not None:
            err += angle_between(-tan_start, leg_a_dir)
        if leg_b_dir is not None:
            err += angle_between(tan_end, leg_b_dir)
        if err < best[0]:
            best = (err, phase)
    return best[1]


def make_spring(
    wire_d: float,
    coil_od: float,
    turns: float,
    leg_a_len: float,
    leg_b_len: float,
    pitch: float | None = None,
    phase_deg: float | None = None,
    leg_a_dir: cq.Vector | None = None,
    leg_b_dir: cq.Vector | None = None,
) -> cq.Workplane:
    if wire_d <= 0 or coil_od <= wire_d:
        raise ValueError("coil_od must be greater than wire_d, and both must be positive")
    if turns <= 0 or leg_a_len < 0 or leg_b_len < 0:
        raise ValueError("turns must be positive and leg lengths must be non-negative")

    wire_r = wire_d / 2.0
    radius = (coil_od - wire_d) / 2.0
    pitch = wire_d if pitch is None else pitch
    coil_width = pitch * turns
    phase = best_phase(pitch, coil_width, radius, leg_a_dir, leg_b_dir) if phase_deg is None else phase_deg

    edge = helix_edge(pitch, coil_width, radius, phase)
    start = edge.positionAt(0)
    end = edge.positionAt(1)
    tan_start = edge.tangentAt(0).normalized()
    tan_end = edge.tangentAt(1).normalized()

    a_tip = start - tan_start * leg_a_len
    b_tip = end + tan_end * leg_b_len

    wire_builder = BRepBuilderAPI_MakeWire()
    wire_builder.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*a_tip.toTuple()), gp_Pnt(*start.toTuple())).Edge())
    wire_builder.Add(edge.wrapped)
    wire_builder.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*end.toTuple()), gp_Pnt(*b_tip.toTuple())).Edge())
    path = wire_builder.Wire()

    profile_normal = (start - a_tip).normalized()
    profile = cq.Wire.makeCircle(wire_r, center=a_tip, normal=profile_normal)

    pipe = BRepOffsetAPI_MakePipeShell(path)
    pipe.Add(profile.wrapped)
    pipe.Build()
    if not pipe.IsDone():
        raise RuntimeError("spring sweep failed")
    pipe.MakeSolid()

    solid = cq.Shape.cast(pipe.Shape()).Solids()[0].clean()
    return cq.Workplane(obj=solid)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wire-d", type=float, required=True, help="wire diameter")
    parser.add_argument("--coil-od", type=float, required=True, help="coil outside diameter")
    parser.add_argument("--turns", type=float, required=True, help="effective coil turns")
    parser.add_argument("--leg-a-len", type=float, required=True, help="first leg length")
    parser.add_argument("--leg-b-len", type=float, required=True, help="second leg length")
    parser.add_argument("--pitch", type=float, help="coil pitch; defaults to wire diameter")
    parser.add_argument("--phase-deg", type=float, help="rotation phase around coil axis")
    parser.add_argument("--leg-a-dir", type=parse_vec, help="desired first leg direction as x,y,z")
    parser.add_argument("--leg-b-dir", type=parse_vec, help="desired second leg direction as x,y,z")
    parser.add_argument("--output", type=Path, default=Path("torsion_spring.step"))
    args = parser.parse_args()

    spring = make_spring(
        wire_d=args.wire_d,
        coil_od=args.coil_od,
        turns=args.turns,
        leg_a_len=args.leg_a_len,
        leg_b_len=args.leg_b_len,
        pitch=args.pitch,
        phase_deg=args.phase_deg,
        leg_a_dir=args.leg_a_dir,
        leg_b_dir=args.leg_b_dir,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(spring, str(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
