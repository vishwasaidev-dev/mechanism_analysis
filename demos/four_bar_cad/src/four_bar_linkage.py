#!/usr/bin/env python3
"""Generate a first-pass four-bar linkage CAD assembly.

This is intentionally simple and source-first: edit parameters here, then
regenerate STEP artifacts. Units are millimeters.
"""

from __future__ import annotations

import json
from math import atan2, cos, degrees, hypot, radians, sin, sqrt
from pathlib import Path

from build123d import Box, Compound, Cylinder, Pos, Rot, export_step

ROOT = Path(__file__).resolve().parents[1]
STEP_DIR = ROOT / "STEP"
PARAMS_PATH = ROOT / "four_bar_params.json"


def load_params():
    """Load shared CAD/browser parameters, with defaults for old checkouts."""
    params = {
        "ground": 90.0,
        "crank": 28.0,
        "coupler": 80.0,
        "rocker": 55.0,
        "linkWidth": 12.0,
        "linkThickness": 6.0,
        "groundWidth": 16.0,
        "groundThickness": 5.0,
        "pivotHoleDiameter": 4.5,
        "pinBossDiameter": 10.0,
        "crankAngleDeg": 45.0,
    }
    if PARAMS_PATH.exists():
        params.update(json.loads(PARAMS_PATH.read_text(encoding="utf-8")))
    return params


PARAMS = load_params()

# Mechanism parameters, mm. These are loaded from ../four_bar_params.json.
GROUND_SPAN = float(PARAMS["ground"])
CRANK_LENGTH = float(PARAMS["crank"])
COUPLER_LENGTH = float(PARAMS["coupler"])
ROCKER_LENGTH = float(PARAMS["rocker"])
LINK_WIDTH = float(PARAMS["linkWidth"])
LINK_THICKNESS = float(PARAMS["linkThickness"])
GROUND_WIDTH = float(PARAMS["groundWidth"])
GROUND_THICKNESS = float(PARAMS["groundThickness"])
PIVOT_HOLE_DIAMETER = float(PARAMS["pivotHoleDiameter"])  # M4 clearance
PIN_BOSS_DIAMETER = float(PARAMS["pinBossDiameter"])
CRANK_ANGLE_DEG = float(PARAMS["crankAngleDeg"])


def circle_intersections(p0, r0, p1, r1):
    """Return the two intersections of circles (p0, r0) and (p1, r1)."""
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    d = hypot(dx, dy)
    if d == 0 or d > r0 + r1 or d < abs(r0 - r1):
        raise ValueError("Four-bar dimensions do not close at this crank angle")
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = sqrt(max(r0 * r0 - a * a, 0.0))
    xm = x0 + a * dx / d
    ym = y0 + a * dy / d
    rx = -dy * h / d
    ry = dx * h / d
    return (xm + rx, ym + ry), (xm - rx, ym - ry)


def make_link(length: float, width: float = LINK_WIDTH, thickness: float = LINK_THICKNESS):
    """Create a dogbone link centered on the origin, long axis along X."""
    radius = width / 2
    hole_radius = PIVOT_HOLE_DIAMETER / 2
    boss_radius = PIN_BOSS_DIAMETER / 2
    # A central web plus rounded/bossed pivot ends, then subtract through holes.
    solid = Box(length, width, thickness)
    solid += Pos(-length / 2, 0, 0) * Cylinder(radius, thickness)
    solid += Pos(length / 2, 0, 0) * Cylinder(radius, thickness)
    solid += Pos(-length / 2, 0, 0) * Cylinder(boss_radius, thickness + 1)
    solid += Pos(length / 2, 0, 0) * Cylinder(boss_radius, thickness + 1)
    solid -= Pos(-length / 2, 0, 0) * Cylinder(hole_radius, thickness + 4)
    solid -= Pos(length / 2, 0, 0) * Cylinder(hole_radius, thickness + 4)
    return solid


def place_between(shape, p0, p1, z=0):
    """Place a local-X link between two XY points."""
    x0, y0 = p0
    x1, y1 = p1
    angle = degrees(atan2(y1 - y0, x1 - x0))
    mx = (x0 + x1) / 2
    my = (y0 + y1) / 2
    return Pos(mx, my, z) * Rot(0, 0, angle) * shape


def build_model():
    """Return the assembly, individual source parts, and solved joint points."""
    # Joint positions for one valid pose.
    a = (0.0, 0.0)
    d = (GROUND_SPAN, 0.0)
    theta = radians(CRANK_ANGLE_DEG)
    b = (CRANK_LENGTH * cos(theta), CRANK_LENGTH * sin(theta))
    c_candidates = circle_intersections(b, COUPLER_LENGTH, d, ROCKER_LENGTH)
    c = max(c_candidates, key=lambda p: p[1])  # upper/open configuration

    ground = make_link(GROUND_SPAN, width=GROUND_WIDTH, thickness=GROUND_THICKNESS)
    crank = make_link(CRANK_LENGTH)
    coupler = make_link(COUPLER_LENGTH)
    rocker = make_link(ROCKER_LENGTH)

    ground.label = "ground_link"
    crank.label = "input_crank"
    coupler.label = "coupler_link"
    rocker.label = "output_rocker"

    assembly = Compound(
        label="four_bar_linkage_pose_45deg",
        children=[
            place_between(ground, a, d, z=0),
            place_between(crank, a, b, z=7),
            place_between(coupler, b, c, z=14),
            place_between(rocker, d, c, z=7),
        ],
    )
    return assembly, {"ground_link": ground, "input_crank": crank, "coupler_link": coupler, "output_rocker": rocker}, {"A": a, "B": b, "C": c, "D": d}


def gen_step():
    """Entry point used by text-to-cad's scripts/step launcher."""
    assembly, _parts, _points = build_model()
    return assembly


def main():
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    assembly, parts, points = build_model()
    a, b, c, d = points["A"], points["B"], points["C"], points["D"]

    export_step(assembly, STEP_DIR / "four_bar_linkage_pose_45deg.step")
    for name, part in parts.items():
        export_step(part, STEP_DIR / f"{name}.step")

    report = ROOT / "docs" / "four-bar-brief.md"
    report.write_text(
        "# Four-Bar Linkage CAD Brief\n\n"
        f"- Ground pivots: A={a}, D={d}\n"
        f"- Pose: crank angle {CRANK_ANGLE_DEG} deg, B=({b[0]:.3f}, {b[1]:.3f}), C=({c[0]:.3f}, {c[1]:.3f})\n"
        f"- Link lengths: ground {GROUND_SPAN} mm, crank {CRANK_LENGTH} mm, coupler {COUPLER_LENGTH} mm, rocker {ROCKER_LENGTH} mm\n"
        f"- Link section: {LINK_WIDTH} mm wide x {LINK_THICKNESS} mm thick\n"
        f"- Pivot holes: {PIVOT_HOLE_DIAMETER} mm diameter M4 clearance\n"
        "- Primary artifact: `STEP/four_bar_linkage_pose_45deg.step`\n",
        encoding="utf-8",
    )

    print(f"Wrote {STEP_DIR / 'four_bar_linkage_pose_45deg.step'}")
    print(f"Wrote {report}")


if __name__ == "__main__":
    main()
