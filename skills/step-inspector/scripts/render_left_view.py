#!/usr/bin/env python3
"""Render a STEP file as a simple Y-Z left-view projection.

This is an inspection helper, not a photorealistic CAD renderer. It reads STEP
solids with CadQuery/OCP, tessellates them, projects to the Y-Z plane, and draws
triangles sorted by X depth. It is meant for quick layout conversations where a
human engineer needs to see side-view space relationships.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cadquery as cq
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


DEFAULT_PALETTE = [
    "#9dcfed",
    "#a5a5a5",
    "#3b61b4",
    "#eaeaea",
    "#c4e2f3",
    "#f88701",
    "#7f7f7f",
    "#fab601",
    "#6cc04a",
    "#d9534f",
]


def parse_indices(text: str) -> set[int]:
    if not text.strip():
        return set()
    return {int(item.strip()) for item in text.split(",") if item.strip()}


def load_solids(step_path: Path):
    return cq.importers.importStep(str(step_path)).solids().vals()


def render_left_view(
    step_path: Path,
    output_path: Path,
    hide_indices: set[int],
    title: str,
    label_solids: bool,
    view_from: str,
    mirror_y: bool,
    tolerance: float,
) -> None:
    solids = load_solids(step_path)

    triangles: list[tuple[float, list[tuple[float, float]], str]] = []
    bboxes = []
    for idx, solid in enumerate(solids):
        bbox = solid.BoundingBox()
        bboxes.append(bbox)
        if idx in hide_indices:
            continue

        verts, faces = solid.tessellate(tolerance)
        color = DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)]
        for face in faces:
            pts = [verts[i] for i in face]
            # Project to Y-Z. Horizontal = depth Y, vertical = height Z.
            poly = [((-p.y if mirror_y else p.y), p.z) for p in pts]
            mean_x = sum(p.x for p in pts) / len(pts)
            triangles.append((mean_x, poly, color))

    # Painter order: far first, near last. For view from x-min, near is smaller X.
    reverse = view_from == "xmax"
    triangles.sort(key=lambda item: item[0], reverse=reverse)

    polys = [item[1] for item in triangles]
    colors = [item[2] for item in triangles]

    all_y = []
    all_z = []
    for bbox in bboxes:
        all_y += [-bbox.ymax, -bbox.ymin] if mirror_y else [bbox.ymin, bbox.ymax]
        all_z += [bbox.zmin, bbox.zmax]

    fig, ax = plt.subplots(figsize=(10, 12), dpi=160)
    collection = PolyCollection(
        polys,
        facecolors=colors,
        edgecolors=(0, 0, 0, 0.38),
        linewidths=0.18,
        alpha=0.96,
    )
    ax.add_collection(collection)

    if label_solids:
        for idx, bbox in enumerate(bboxes):
            if idx in hide_indices:
                continue
            cy = (bbox.ymin + bbox.ymax) / 2
            cz = (bbox.zmin + bbox.zmax) / 2
            ax.text(
                cy,
                cz,
                str(idx),
                fontsize=6,
                ha="center",
                va="center",
                color="black",
                bbox={"facecolor": "white", "alpha": 0.55, "edgecolor": "none", "pad": 0.8},
            )

    margin_y = max(4.0, (max(all_y) - min(all_y)) * 0.04)
    margin_z = max(4.0, (max(all_z) - min(all_z)) * 0.04)
    ax.set_xlim(min(all_y) - margin_y, max(all_y) + margin_y)
    ax.set_ylim(min(all_z) - margin_z, max(all_z) + margin_z)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Y depth / mm")
    ax.set_ylabel("Z height / mm")
    ax.set_title(title)
    ax.grid(True, linestyle=":", linewidth=0.5, alpha=0.45)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--hide", default="")
    parser.add_argument("--title", default="STEP left view")
    parser.add_argument("--label-solids", action="store_true")
    parser.add_argument("--view-from", choices=["xmin", "xmax"], default="xmin")
    parser.add_argument("--mirror-y", action="store_true")
    parser.add_argument("--tolerance", type=float, default=0.8)
    args = parser.parse_args()

    render_left_view(
        step_path=args.step,
        output_path=args.output,
        hide_indices=parse_indices(args.hide),
        title=args.title,
        label_solids=args.label_solids,
        view_from=args.view_from,
        mirror_y=args.mirror_y,
        tolerance=args.tolerance,
    )


if __name__ == "__main__":
    main()
