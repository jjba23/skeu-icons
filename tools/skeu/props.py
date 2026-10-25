"""Props: the working objects the projects and categories are built from.

These are the things you would find on a desk in 2009 - an anchor on a rope, a
chrome chain, a walnut metronome, a bench vise, a snow globe, an alembic, a
letterpress block, a mug of cocoa, a stack of hard-drive platters.  Each is one
silhouette, lit by the shared key light, with the accent carried by one material
rather than by a coloured background.
"""

from __future__ import annotations

import math

import numpy as np

from . import materials as M
from .motifs import bead, blob, ribbon
from .objects import CX, CY, mark, rivet, screw
from .paint import (SIZE, Capsule, Circle, Ellipse, Moved, Poly, RRect, Rotated,
                    blur, clamp01, dots_mask, hsl, polyline_mask, ring, smoothstep)

__all__ = [
    "anchor", "chain", "metronome", "vise", "snowflake", "snow_globe",
    "glass_cloud", "alembic", "inkwell", "drafting_compass", "press",
    "spec_sheet", "type_stamps", "mug", "platter_stack", "wrench_lens",
    "combination_lock", "planner", "desk_lamp", "crystal_ball", "parcel",
    "drawer", "spectacles", "chart_recorder", "multitool", "lady_justice",
    "conductor", "floppy_lambda",
]


def _oval_ring(cx: float, cy: float, rx: float, ry: float, width: float):
    """An elliptical link: outer ellipse minus inner ellipse."""
    return Ellipse(cx, cy, rx, ry) - Ellipse(cx, cy, rx - width, ry - width)


# --------------------------------------------------------------------------- #
# carvoeiro-water-fun - the anchor
# --------------------------------------------------------------------------- #

def anchor(c, hue: float = 206, cy: float = CY) -> None:
    """A polished anchor with hemp rope, one enamelled band on the shank."""
    cx = CX
    # rope: a coil behind the crown, then a couple of turns on the shank
    for i, (dx, dy, rot) in enumerate(((-176, 236, -18), (-120, 288, 8), (-20, 316, -6))):
        c.paint(Rotated(_oval_ring(cx + dx, cy + dy, 96, 46, 30), rot,
                        cx + dx, cy + dy), M.enamel, profile=("sphere", 20),
                hue=36, sat=0.32, light=0.62, shadow=True, contact=0.18)
    # arms and flukes
    arms = ribbon([(cx - 268, cy + 84), (cx - 292, cy + 192), (cx - 218, cy + 272),
                   (cx - 92, cy + 314), (cx + 92, cy + 314), (cx + 218, cy + 272),
                   (cx + 292, cy + 192), (cx + 268, cy + 84)], (66, 60, 54, 46, 46,
                                                               54, 60, 66))
    c.paint(Moved(arms, 0, 18), M.flat("#3a4048"), profile=("bevel", 10, 16))
    c.paint(arms, M.chrome, profile=("sphere", 46), shadow=True, contact=0.26)
    for side in (-1, 1):
        fluke = Poly([(cx + side * 292, cy + 176), (cx + side * 372, cy + 96),
                      (cx + side * 350, cy + 246), (cx + side * 300, cy + 300)],
                     rounding=18)
        c.paint(Moved(fluke, 0, 12), M.flat("#3a4048"), profile=("bevel", 8, 12))
        c.paint(fluke, M.chrome, profile=("sphere", 34), shadow=True, contact=0.24)
    # shank
    shank = RRect(cx, cy - 30, 66, 470, 26)
    c.paint(Moved(shank, 0, 20), M.flat("#3a4048"), profile=("bevel", 10, 14))
    c.paint(shank, M.chrome, profile=("bevel", 26, 38), shadow=True, contact=0.28)
    # enamelled band, the only colour
    c.paint(RRect(cx, cy - 128, 74, 74, 18), M.enamel, profile=("bevel", 10, 14),
            hue=hue, sat=0.70, light=0.50, contact=0.22)
    c.paint(Capsule(cx - 22, cy - 128, cx + 22, cy - 128, 3), M.flat("#ffffff"),
            profile=("bevel", 2, 2), alpha=0.25)
    # stock and ring
    c.paint(Capsule(cx - 196, cy - 296, cx + 196, cy - 296, 27), M.chrome,
            profile=("sphere", 22), shadow=True, contact=0.24)
    for side in (-1, 1):
        c.paint(Circle(cx + side * 200, cy - 296, 36), M.chrome,
                profile=("sphere", 30), contact=0.26)
    c.paint(ring(cx, cy - 382, 56, 22), M.chrome, profile=("sphere", 14),
            shadow=True, contact=0.22)
    # rope turns on the shank
    for i, dy in enumerate((-232, -206)):
        c.paint(Capsule(cx - 40, cy + dy, cx + 40, cy + dy, 12), M.enamel,
                profile=("sphere", 10), hue=36, sat=0.30, light=0.66, contact=0.18)


# --------------------------------------------------------------------------- #
# lenkesamler - the link
# --------------------------------------------------------------------------- #

def chain(c, hue: float = 206, cy: float = CY) -> None:
    """Two interlocking chrome links, one with a blue enamel sleeve."""
    cx = CX
    back = _oval_ring(cx + 118, cy + 54, 214, 118, 58)
    c.paint(Moved(back, 0, 16), M.flat("#2b3038"), profile=("bevel", 8, 12))
    c.paint(back, M.chrome, profile=("sphere", 34), shadow=True, contact=0.24)
    c.paint(_oval_ring(cx + 118, cy + 54, 196, 100, 10), M.flat("#ffffff"),
            profile=("bevel", 3, 4), alpha=0.22)
    front = _oval_ring(cx - 108, cy - 24, 132, 252, 62)
    c.paint(Moved(front, 0, 18), M.flat("#2b3038"), profile=("bevel", 10, 14))
    c.paint(front, M.chrome, profile=("sphere", 40), shadow=True, contact=0.26)
    c.paint(_oval_ring(cx - 108, cy - 24, 112, 232, 10), M.flat("#ffffff"),
            profile=("bevel", 3, 4), alpha=0.26)
    # enamel sleeve across the front link's waist
    c.paint(RRect(cx - 108, cy - 24, 168, 76, 30), M.enamel, profile=("bevel", 12, 16),
            hue=hue, sat=0.74, light=0.50, contact=0.22)
    c.paint(Capsule(cx - 148, cy - 40, cx + 148, cy - 40, 4), M.flat("#ffffff"),
            profile=("bevel", 2, 2), alpha=0.22)
    for dx, dy in ((-108, -262), (-108, 214)):
        c.paint(Circle(cx + dx, cy + dy, 4), M.flat("#ffffff"),
                profile=("bevel", 1, 1), alpha=0.0)


# --------------------------------------------------------------------------- #
# byggsteg - the metronome
# --------------------------------------------------------------------------- #

def metronome(c, hue: float = 30, cy: float = CY) -> None:
    """A walnut metronome: ivory scale, brass pendulum, steel weight."""
    cx = CX
    base = RRect(cx, cy + 292, 450, 78, 18)
    c.paint(Moved(base, 0, 16), M.flat("#2a1a0c"), profile=("bevel", 8, 12))
    c.paint(base, M.wood, profile=("bevel", 14, 20), hue=22, sat=0.60, light=0.28,
            shadow=True, contact=0.26)
    body = Poly([(cx - 168, cy - 268), (cx + 168, cy - 268), (cx + 236, cy + 268),
                 (cx - 236, cy + 268)], rounding=22)
    c.paint(Moved(body, 0, 22), M.flat("#2a1a0c"), profile=("bevel", 12, 18))
    c.paint(body, M.wood, profile=("bevel", 30, 44), hue=22, sat=0.62, light=0.34,
            shadow=True, contact=0.28)
    # front face: a lighter veneer panel
    face = Poly([(cx - 136, cy - 236), (cx + 136, cy - 236), (cx + 190, cy + 236),
                 (cx - 190, cy + 236)], rounding=16)
    c.paint(face, M.wood, profile=("bevel", 12, 18), hue=28, sat=0.52, light=0.46,
            contact=0.20)
    c.paint(RRect(cx, cy - 198, 200, 54, 12), M.brass, profile=("bevel", 6, 9),
            contact=0.24)
    # ivory scale with ticks
    scale = Poly([(cx - 104, cy - 150), (cx + 104, cy - 150), (cx + 148, cy + 190),
                  (cx - 148, cy + 190)], rounding=10)
    c.paint(scale, M.ivory, profile=("bevel", 6, 9), contact=0.28)
    for i in range(9):
        y = cy - 120 + i * 36
        w = 42 if i % 2 == 0 else 26
        c.paint(Capsule(cx - w, y, cx + w, y, 3), M.flat("#3a3a34"),
                profile=("bevel", 1.5, 2), alpha=0.55)
    # pendulum: steel rod with a brass weight, swinging right
    pivot = (cx, cy - 210)
    rod = Rotated(Capsule(pivot[0], pivot[1] + 20, pivot[0] + 86, pivot[1] + 470, 8),
                  0, pivot[0], pivot[1])
    c.paint(rod, M.steel, profile=("bevel", 4, 6), shadow=True, contact=0.18)
    weight = Rotated(RRect(pivot[0] + 58, pivot[1] + 290, 92, 120, 16), 10,
                     pivot[0], pivot[1])
    c.paint(Moved(weight, 0, 8), M.flat("#2a1a0c"), profile=("bevel", 6, 9))
    c.paint(weight, M.brass, profile=("sphere", 40), shadow=True, contact=0.24)
    c.paint(Circle(pivot[0], pivot[1], 26), M.chrome, profile=("sphere", 20),
            shadow=True, contact=0.24)
    # brass hinge and feet
    c.paint(Capsule(cx, cy - 286, cx, cy - 302, 6), M.brass, profile=("sphere", 5))
    for side in (-1, 1):
        c.paint(Capsule(cx + side * 186, cy + 306, cx + side * 186, cy + 330, 10),
                M.brass, profile=("sphere", 8), contact=0.2)


# --------------------------------------------------------------------------- #
# kracht - the bench vise
# --------------------------------------------------------------------------- #

def vise(c, hue: float = 206, cy: float = CY) -> None:
    """A blue-enamelled bench vise with machined jaws and a wooden handle."""
    cx = CX
    # bench plate and bolts
    plate = RRect(cx, cy + 292, 470, 64, 14)
    c.paint(Moved(plate, 0, 14), M.flat("#1b1e23"), profile=("bevel", 8, 12))
    c.paint(plate, M.gunmetal, profile=("bevel", 10, 16), shadow=True, contact=0.24)
    for side in (-1, 1):
        screw(c, cx + side * 196, cy + 292, 15)
    # fixed jaw
    fixed = RRect(cx - 10, cy + 116, 404, 268, 26)
    c.paint(Moved(fixed, 0, 24), M.flat("#12253a"), profile=("bevel", 12, 18))
    c.paint(fixed, M.enamel, profile=("bevel", 26, 38), hue=hue, sat=0.68, light=0.42,
            shadow=True, contact=0.28)
    c.paint(RRect(cx - 10, cy + 246, 380, 52, 12), M.enamel, profile=("bevel", 8, 12),
            hue=hue, sat=0.70, light=0.52, contact=0.24)
    # sliding front jaw, a little lower and forward
    slide = RRect(cx - 10, cy - 96, 360, 190, 22)
    c.paint(Moved(slide, 0, 20), M.flat("#12253a"), profile=("bevel", 10, 16))
    c.paint(slide, M.enamel, profile=("bevel", 24, 34), hue=hue, sat=0.66, light=0.46,
            shadow=True, contact=0.26)
    # jaws: hardened steel faces with serrations
    for dy in (-4, 32):
        c.paint(RRect(cx - 10, cy + dy, 330, 36, 6), M.steel,
                profile=("bevel", 6, 9), contact=0.26)
    c.paint_mask(dots_mask(SIZE, 26, 4.5, bounds=(cx - 160, cy - 16, cx + 160, cy - 12)),
                 M.flat("#0d1014"), emboss=0.8, alpha=0.4)
    c.paint_mask(dots_mask(SIZE, 26, 4.5, bounds=(cx - 160, cy + 20, cx + 160, cy + 24)),
                 M.flat("#0d1014"), emboss=0.8, alpha=0.4)
    # screw, handle and knob
    c.paint(Capsule(cx, cy - 210, cx, cy - 96, 20), M.steel,
            profile=("sphere", 16), contact=0.22)
    for i in range(4):
        c.paint(Rotated(ring(cx, cy - 196 + i * 26, 20, 5), 0, cx, cy),
                M.engraved, profile=("bevel", 2, 2), alpha=0.35)
    handle = Rotated(Capsule(cx - 230, cy - 250, cx + 230, cy - 214, 13), 5, cx, cy)
    c.paint(Moved(handle, 0, 8), M.flat("#2a1a0c"), profile=("bevel", 5, 8))
    c.paint(handle, M.chrome, profile=("sphere", 11), shadow=True, contact=0.2)
    for side in (-1, 1):
        c.paint(Circle(cx + side * 228, cy - 232 - side * 16, 34), M.wood,
                profile=("sphere", 28), shadow=True, contact=0.24, hue=24, sat=0.56,
                light=0.34)
    # maker's plate
    c.paint(RRect(cx + 96, cy + 150, 116, 52, 8), M.brass,
            profile=("bevel", 4, 6), contact=0.2)
    for i in range(4):
        c.paint(Capsule(cx + 60 + i * 24, cy + 150, cx + 70 + i * 24, cy + 150, 3),
                M.engraved, profile=("bevel", 1.5, 2), alpha=0.4)


# --------------------------------------------------------------------------- #
# nixpkgs / nix-jointhefreeworld - the snowflake
# --------------------------------------------------------------------------- #

def snowflake(c, hue: float = 200, cy: float = CY, sealed: bool = False) -> None:
    """A machined steel snowflake with a blue crystal at its heart."""
    cx = CX
    size = 300
    # six arms, each with two side branches
    for i in range(6):
        a = math.radians(i * 60 + 30)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        tip = (cx + ux * size, cy + uy * size)
        arm = ribbon([(cx, cy), (cx + ux * size * 0.55, cy + uy * size * 0.55), tip],
                     (74, 56, 26))
        c.paint(Moved(arm, 0, 16), M.flat("#2b3038"), profile=("bevel", 8, 12))
        c.paint(arm, M.chrome, profile=("sphere", 34), shadow=True, contact=0.22)
        for t, length in ((0.44, 84), (0.67, 64)):
            bx, by = cx + ux * size * t, cy + uy * size * t
            for side in (-1, 1):
                end = (bx + (ux * 0.58 + px * side * 0.81) * length,
                       by + (uy * 0.58 + py * side * 0.81) * length)
                branch = ribbon([(bx, by), end], (40, 16))
                c.paint(Moved(branch, 0, 10), M.flat("#2b3038"),
                        profile=("bevel", 6, 9))
                c.paint(branch, M.chrome, profile=("sphere", 22), shadow=True,
                        contact=0.18)
        c.paint(Circle(tip[0], tip[1], 20), M.chrome, profile=("sphere", 15),
                contact=0.2)
    # hub: blue crystal in a chrome collar
    c.paint(Circle(cx, cy, 112), M.chrome, profile=("sphere", 70), shadow=True,
            contact=0.3)
    c.paint(Circle(cx, cy, 88), M.gunmetal, profile=("bevel", 8, 12), contact=0.3)
    c.paint(Circle(cx, cy, 76), M.crystal, profile=("sphere", 50), hue=hue, sat=0.72,
            light=0.50, contact=0.3)
    for i in range(6):
        a = math.radians(i * 60 + 30)
        c.paint(Capsule(cx + math.cos(a) * 30, cy + math.sin(a) * 30,
                        cx + math.cos(a) * 60, cy + math.sin(a) * 60, 4),
                M.flat("#ffffff"), profile=("bevel", 1.5, 2), alpha=0.30)
    if sealed:
        ribbon_ = Poly([(cx - 92, cy + 96), (cx + 92, cy + 96), (cx + 82, cy + 140),
                        (cx, cy + 172), (cx - 82, cy + 140)], rounding=6)
        c.paint(ribbon_, M.enamel, profile=("bevel", 5, 8), hue=hue, sat=0.62,
                light=0.46, shadow=True, contact=0.2)
        c.paint(Circle(cx, cy + 138, 38), M.enamel, profile=("sphere", 28), hue=hue,
                sat=0.70, light=0.44, shadow=True, contact=0.28)
        mark(c, "check", cx, cy + 138, 38, M.brass, emboss=1.8)


# --------------------------------------------------------------------------- #
# wolkenschloss - the snow globe
# --------------------------------------------------------------------------- #

def snow_globe(c, hue: float = 200, cy: float = CY) -> None:
    """A glass dome over a tiny castle on a cloud, on a turned brass base."""
    cx = CX
    # base: turned brass, two steps
    c.paint(Ellipse(cx, cy + 300, 268, 92), M.brass, profile=("bevel", 14, 20),
            shadow=True, contact=0.26)
    c.paint(RRect(cx, cy + 250, 400, 110, 26), M.brass, profile=("bevel", 18, 26),
            contact=0.26)
    c.paint(Ellipse(cx, cy + 196, 174, 46), M.brass, profile=("bevel", 8, 12),
            contact=0.30)
    # the castle, on a cloud, inside
    cloud = Circle(cx - 84, cy + 110, 86) | Circle(cx + 84, cy + 110, 86) | \
        Circle(cx, cy + 96, 104) | Circle(cx - 40, cy + 140, 76) | \
        Circle(cx + 48, cy + 140, 76)
    c.paint(Moved(cloud, 0, 10), M.flat("#4a5560"), profile=("sphere", 40))
    c.paint(cloud, M.ceramic, profile=("sphere", 70), sat=0.03, shadow=True,
            contact=0.24)
    for dx, dy, w, h in ((-72, -6, 74, 150), (0, -40, 92, 210), (74, -4, 70, 138)):
        tower = RRect(cx + dx, cy + dy, w, h, 8)
        c.paint(tower, M.enamel, profile=("sphere", 24), hue=36, sat=0.30, light=0.80,
                shadow=True, contact=0.2)
        roof = Poly([(cx + dx - w * 0.66, cy + dy - h / 2 + 6),
                     (cx + dx + w * 0.66, cy + dy - h / 2 + 6),
                     (cx + dx, cy + dy - h / 2 - 74)], rounding=4)
        c.paint(roof, M.enamel, profile=("bevel", 6, 9), hue=hue, sat=0.62, light=0.42,
                shadow=True, contact=0.2)
        c.paint(Capsule(cx + dx, cy + dy - h / 2 - 84, cx + dx, cy + dy - h / 2 - 110,
                        3), M.brass, profile=("sphere", 2))
    # falling snow: dots inside the glass
    for dx, dy, r in ((-140, -30, 5), (-90, -120, 4), (30, -160, 5), (120, -60, 4),
                      (150, 40, 5), (-30, 60, 4), (80, 120, 4), (-150, 120, 4)):
        c.paint(Circle(cx + dx, cy + dy, r), M.flat("#ffffff"),
                profile=("sphere", r), alpha=0.75)
    # glass dome, translucent over all of it
    dome = Circle(cx, cy - 10, 256)
    c.paint(dome, M.glass, profile=("sphere", 190), hue=hue, sat=0.14, light=0.62,
            alpha=0.30, contact=0.26)
    c.paint(dome, M.flat("#ffffff"), profile=("sphere", 190), alpha=0.10)
    c.paint(Ellipse(cx - 92, cy - 118, 74, 52), M.flat("#ffffff"),
            profile=("sphere", 40), alpha=0.30)
    c.paint(Circle(cx - 128, cy - 146, 26), M.flat("#ffffff"),
            profile=("sphere", 18), alpha=0.65)
    c.paint(ring(cx, cy - 10, 254, 6), M.flat("#ffffff"), profile=("bevel", 2, 2),
            alpha=0.35)


# --------------------------------------------------------------------------- #
# wolk-jjba - the cloud
# --------------------------------------------------------------------------- #

def glass_cloud(c, hue: float = 205, cy: float = CY) -> None:
    """A porcelain cumulus: white wool above, blue shadow below, chrome glint.

    The old version was a blue glass bubble.  A cloud reads as a bright white
    puff with a cool blue belly - the blue is the shading, not the body - and
    that says *cloud* at 16 px where a bubble read as a marble.
    """
    cx = CX
    cloud = (Circle(cx - 176, cy + 54, 146) | Circle(cx - 30, cy - 30, 186) |
             Circle(cx + 132, cy + 40, 158) | Circle(cx + 256, cy + 112, 96) |
             Circle(cx - 276, cy + 126, 88) | Circle(cx + 40, cy + 150, 118) |
             Circle(cx - 60, cy + 140, 120))
    c.paint(Moved(cloud, 0, 30), M.flat("#5c6b7a"), profile=("sphere", 100))
    c.paint(cloud, M.ceramic, profile=("sphere", 210), sat=0.03, light=0.97,
            shadow=True, contact=0.30)
    # the cool belly: the same silhouette tinted glass, cut off above the equator
    belly = cloud & RRect(cx, cy + 320, 1500, 460, 40)
    c.paint(belly, M.glass, profile=("sphere", 210), hue=hue, sat=0.46, light=0.64,
            alpha=0.34)
    # one broad key-light shape over the crown, one small specular
    c.paint(Ellipse(cx - 60, cy - 130, 210, 108), M.flat("#ffffff"),
            profile=("sphere", 60), alpha=0.22)
    c.paint(Ellipse(cx - 118, cy - 178, 62, 34), M.flat("#ffffff"),
            profile=("sphere", 20), alpha=0.55)
    c.paint(Ellipse(cx + 208, cy + 150, 74, 40), M.flat("#ffffff"),
            profile=("sphere", 24), alpha=0.12)


# --------------------------------------------------------------------------- #
# orgwebalchemy - the alembic
# --------------------------------------------------------------------------- #

def alembic(c, hue: float = 34, cy: float = CY) -> None:
    """A glass retort with amber liquid, corked, on a copper tripod."""
    cx = CX
    # tripod
    for side in (-1, 1):
        c.paint(Rotated(Capsule(cx + side * 150, cy + 250, cx + side * 250, cy + 400,
                                12), 0, cx, cy), M.brass, profile=("sphere", 10),
                shadow=True, contact=0.2)
    c.paint(Ellipse(cx, cy + 250, 180, 40), M.brass, profile=("bevel", 6, 9),
            contact=0.26)
    bulb = Circle(cx, cy + 40, 224)
    c.paint(Moved(bulb, 0, 24), M.flat("#243040"), profile=("sphere", 120))
    c.paint(bulb, M.glass, profile=("sphere", 190), hue=200, sat=0.30, light=0.72,
            alpha=0.55, shadow=True, contact=0.26)
    # liquid in the lower half
    liquid_mask = ((bulb.sdf(c.X, c.Y) < 0.5) & (c.Y > cy + 76)).astype(np.float32)
    c.paint(bulb, M.enamel, profile=("sphere", 150), mask=liquid_mask, hue=hue,
            sat=0.78, light=0.48, contact=0.2)
    c.paint(Capsule(cx - 190, cy + 78, cx + 190, cy + 78, 4), M.flat("#ffe9b0"),
            profile=("bevel", 2, 2), alpha=0.5)
    for dx, dy, r in ((-70, 150, 10), (10, 184, 7), (86, 148, 9)):
        c.paint(Circle(cx + dx, cy + dy, r), M.flat("#fff3cd"),
                profile=("sphere", r * 0.7), alpha=0.55)
    # neck, cork, copper collar
    neck = Rotated(RRect(cx + 28, cy - 210, 108, 300, 20), -18, cx, cy + 40)
    c.paint(neck, M.glass, profile=("bevel", 14, 20), hue=200, sat=0.20, light=0.80,
            alpha=0.65, contact=0.2)
    cork = Rotated(RRect(cx + 74, cy - 344, 118, 62, 12), -18, cx, cy + 40)
    c.paint(cork, M.wood, profile=("bevel", 6, 9), hue=30, sat=0.48, light=0.56,
            shadow=True, contact=0.22)
    c.paint(Rotated(ring(cx + 60, cy - 306, 60, 16), -18, cx, cy + 40), M.brass,
            profile=("sphere", 10), contact=0.2)
    # copper coil around the neck
    for i in range(3):
        c.paint(Rotated(ring(cx + 40 - i * 10, cy - 230 + i * 46, 46, 11), -18,
                        cx, cy + 40), M.brass, profile=("sphere", 9), contact=0.18)
    # glass highlight
    c.paint(Ellipse(cx - 96, cy - 40, 56, 92), M.flat("#ffffff"),
            profile=("sphere", 40), alpha=0.28)
    c.paint(Circle(cx - 126, cy - 84, 22), M.flat("#ffffff"),
            profile=("sphere", 14), alpha=0.55)


# --------------------------------------------------------------------------- #
# scriba - the inkwell and quill
# --------------------------------------------------------------------------- #

def inkwell(c, hue: float = 206, cy: float = CY) -> None:
    """A brass inkwell with a blue glass well and a white quill."""
    cx = CX
    # brass tray and well
    c.paint(Ellipse(cx, cy + 268, 220, 62), M.brass, profile=("bevel", 10, 14),
            shadow=True, contact=0.24)
    c.paint(RRect(cx, cy + 220, 300, 76, 20), M.brass, profile=("bevel", 12, 18),
            contact=0.26)
    body = Poly([(cx - 128, cy + 196), (cx + 128, cy + 196), (cx + 104, cy - 20),
                 (cx - 104, cy - 20)], rounding=34)
    c.paint(body, M.glass, profile=("sphere", 90), hue=hue, sat=0.68, light=0.34,
            shadow=True, contact=0.26)
    c.paint(RRect(cx, cy + 200, 236, 40, 14), M.brass, profile=("bevel", 6, 9),
            contact=0.22)
    c.paint(Ellipse(cx, cy - 18, 106, 30), M.brass, profile=("bevel", 8, 12),
            contact=0.24)
    c.paint(Ellipse(cx, cy - 14, 84, 22), M.flat("#141c26"),
            profile=("sphere", 12), contact=0.2)
    c.paint(Ellipse(cx - 36, cy + 70, 18, 44), M.flat("#ffffff"),
            profile=("sphere", 12), alpha=0.25)
    # the quill: a white feather standing in the well
    shaft = Rotated(Capsule(cx + 10, cy - 30, cx + 110, cy - 400, 9), 0, cx, cy)
    c.paint(shaft, M.ivory, profile=("bevel", 4, 6), shadow=True, contact=0.16)
    vane = Poly([(cx + 18, cy - 120), (cx + 150, cy - 322), (cx + 214, cy - 402),
                 (cx + 186, cy - 300), (cx + 118, cy - 172)], rounding=30)
    c.paint(vane, M.ivory, profile=("bevel", 8, 14), shadow=True, contact=0.18)
    for i in range(5):
        c.paint(Rotated(Capsule(cx + 34 + i * 26, cy - 150 - i * 46,
                                cx + 92 + i * 26, cy - 190 - i * 46, 3), 0, cx, cy),
                M.engraved, profile=("bevel", 1.5, 2), alpha=0.25)
    nib = Poly([(cx + 6, cy - 10), (cx + 2, cy + 96), (cx + 16, cy + 150),
                (cx + 30, cy + 96), (cx + 22, cy - 10)], rounding=6)
    c.paint(nib, M.brass, profile=("bevel", 5, 8), shadow=True, contact=0.2)
    c.paint(Capsule(cx + 16, cy + 30, cx + 16, cy + 96, 2), M.flat("#2a1e08"),
            profile=("bevel", 1, 1), alpha=0.5)
    # a spill of ink and a wax-sealed letter? keep one object: a folded blotter
    c.paint(Capsule(cx - 60, cy + 250, cx + 60, cy + 250, 5), M.flat("#3a2a12"),
            profile=("bevel", 2, 2), alpha=0.25)


# --------------------------------------------------------------------------- #
# skapa - the drafting compass
# --------------------------------------------------------------------------- #

def drafting_compass(c, hue: float = 206, cy: float = CY) -> None:
    """A brass drafting compass with a blue pencil and a knurled adjuster."""
    cx = CX
    hinge = (cx, cy - 286)
    # legs
    for side, foot in ((-1, (cx - 196, cy + 300)), (1, (cx + 208, cy + 296))):
        leg = ribbon([hinge, (cx + side * 96, cy + 10), foot], (54, 34, 12))
        c.paint(Moved(leg, 0, 14), M.flat("#2a1e08"), profile=("bevel", 6, 9))
        c.paint(leg, M.brass, profile=("sphere", 22), shadow=True, contact=0.22)
        c.paint(Circle(foot[0], foot[1], 14), M.steel, profile=("sphere", 10),
                contact=0.2)
    # needle point
    c.paint(Poly([(cx - 196, cy + 290), (cx - 210, cy + 408), (cx - 182, cy + 290)],
                 rounding=3), M.steel, profile=("bevel", 3, 4), contact=0.18)
    # pencil in the other leg
    c.paint(Rotated(RRect(cx + 208, cy + 210, 34, 240, 6), 6, cx + 208, cy + 210),
            M.enamel, profile=("bevel", 5, 8), hue=hue, sat=0.74, light=0.48,
            shadow=True, contact=0.2)
    c.paint(Poly([(cx + 186, cy + 316), (cx + 230, cy + 316), (cx + 208, cy + 382)],
                 rounding=3), M.wood, profile=("bevel", 3, 4), hue=34, sat=0.40,
            light=0.62)
    c.paint(Poly([(cx + 198, cy + 370), (cx + 218, cy + 370), (cx + 208, cy + 382)],
                 rounding=2), M.flat("#1b1f25"), profile=("bevel", 2, 2))
    # hinge, knurled adjuster and arc
    c.paint(Circle(hinge[0], hinge[1], 46), M.brass, profile=("sphere", 30),
            shadow=True, contact=0.28)
    c.paint(Capsule(hinge[0], hinge[1] - 46, hinge[0], hinge[1] - 108, 12),
            M.brass, profile=("sphere", 10), contact=0.2)
    c.paint(Circle(hinge[0], hinge[1] - 118, 30), M.brass, profile=("sphere", 22),
            contact=0.24)
    c.paint(ring(cx + 12, cy - 120, 74, 12), M.chrome, profile=("bevel", 4, 6),
            shadow=True, contact=0.2, alpha=0.0)
    adjust = Rotated(Capsule(cx - 40, cy - 190, cx + 74, cy - 60, 12), 0, cx, cy)
    c.paint(adjust, M.steel, profile=("sphere", 10), shadow=True, contact=0.2)
    c.paint(Circle(cx + 60, cy - 46, 26), M.brass, profile=("sphere", 20),
            contact=0.24)


# --------------------------------------------------------------------------- #
# the die press - the build/republishing tool
# --------------------------------------------------------------------------- #

def press(c, hue: float = 206, cy: float = CY) -> None:
    """A chrome die press stamping a blue glass token out of a stack."""
    cx = CX
    base = RRect(cx, cy + 298, 620, 92, 20)
    c.paint(Moved(base, 0, 18), M.flat("#1b1e23"), profile=("bevel", 10, 14))
    c.paint(base, M.steel, profile=("bevel", 18, 26), shadow=True, contact=0.28)
    c.paint(RRect(cx, cy + 254, 540, 42, 10), M.gunmetal, profile=("bevel", 6, 9),
            contact=0.26)
    for side in (-1, 1):
        c.paint(RRect(cx + side * 210, cy + 40, 62, 430, 16), M.chrome,
                profile=("bevel", 14, 20), shadow=True, contact=0.22)
        c.paint(Capsule(cx + side * 210, cy - 150, cx + side * 210, cy + 240, 6),
                M.flat("#ffffff"), profile=("bevel", 2, 3), alpha=0.20)
    c.paint(RRect(cx, cy - 178, 540, 82, 18), M.chrome, profile=("bevel", 16, 22),
            shadow=True, contact=0.24)
    # ram and die
    c.paint(RRect(cx, cy - 40, 260, 190, 16), M.steel, profile=("bevel", 16, 24),
            shadow=True, contact=0.26)
    c.paint(RRect(cx, cy + 58, 180, 34, 8), M.chrome, profile=("bevel", 6, 9),
            contact=0.28)
    # the token being pressed
    c.paint(Ellipse(cx, cy + 96, 132, 40), M.flat("#0f2c4a"), profile=("bevel", 6, 9),
            contact=0.22)
    c.paint(Circle(cx, cy + 84, 82), M.crystal, profile=("sphere", 44), hue=hue,
            sat=0.74, light=0.50, shadow=True, contact=0.26)
    c.paint(Circle(cx - 26, cy + 60, 18), M.flat("#ffffff"),
            profile=("sphere", 12), alpha=0.35)
    # lever with a red ball knob
    lever = ribbon([(cx + 250, cy - 214), (cx + 320, cy - 330), (cx + 392, cy - 392)],
                   (44, 30, 14))
    c.paint(Moved(lever, 0, 10), M.flat("#2a1a0c"), profile=("bevel", 6, 9))
    c.paint(lever, M.chrome, profile=("sphere", 16), shadow=True, contact=0.2)
    c.paint(Circle(cx + 408, cy - 404, 48), M.enamel, profile=("sphere", 36), hue=4,
            sat=0.78, light=0.46, shadow=True, contact=0.28)
    # input stack at the left, output tray at the right
    for i in range(3):
        c.paint(Ellipse(cx - 286, cy + 236 - i * 18, 62, 20), M.chrome,
                profile=("bevel", 4, 6), contact=0.18)
        c.paint(Ellipse(cx - 286, cy + 226 - i * 18, 52, 14), M.crystal,
                profile=("bevel", 4, 6), hue=hue, sat=0.70, light=0.50, contact=0.16)
    c.paint(RRect(cx + 250, cy + 236, 150, 18, 6), M.steel,
            profile=("bevel", 4, 6), contact=0.2)
    for i in range(2):
        c.paint(Ellipse(cx + 250 + i * 40, cy + 222, 44, 14), M.crystal,
                profile=("bevel", 3, 5), hue=hue, sat=0.70, light=0.52, contact=0.16)
    # maker's plate
    c.paint(RRect(cx - 180, cy + 292, 150, 40, 6), M.brass,
            profile=("bevel", 4, 6), contact=0.2)


# --------------------------------------------------------------------------- #
# guile-openapi-generator - the printed spec
# --------------------------------------------------------------------------- #

def spec_sheet(c, hue: float = 212, cy: float = CY) -> None:
    """A printed API specification with a chrome clip and a blue seal."""
    cx = CX
    w, h = 520, 660
    x0, y0 = cx - w / 2, cy - h / 2 - 10
    sheet = RRect(cx + 10, cy + 4, w, h, 8)
    c.paint(Moved(sheet, 0, 16), M.flat("#b9b1a2"), profile=("flat",))
    c.paint(sheet, M.paper, profile=("bevel", 6, 10), shadow=True, contact=0.2)
    # printed title rule
    c.paint(Capsule(x0 + 62, y0 + 74, x0 + 320, y0 + 74, 6), M.flat("#3d4650"),
            profile=("bevel", 2, 3), alpha=0.85)
    c.paint(Capsule(x0 + 62, y0 + 108, x0 + 240, y0 + 108, 4), M.flat("#6b7480"),
            profile=("bevel", 2, 2), alpha=0.7)
    # schema: printed boxes joined by rules
    boxes = ((x0 + 128, y0 + 210), (x0 + 340, y0 + 210), (x0 + 128, y0 + 344),
             (x0 + 340, y0 + 344), (x0 + 234, y0 + 476))
    for bx, by in boxes:
        c.paint(RRect(bx, by, 140, 86, 6), M.flat("#d9d5c9"),
                profile=("bevel", 2, 3), alpha=0.95)
        for dy in (-39, 39):
            c.paint(Capsule(bx - 62, by + dy, bx + 62, by + dy, 3),
                    M.flat("#5a646f"), profile=("bevel", 1.2, 1.6), alpha=0.55)
        for i in range(3):
            c.paint(Capsule(bx - 52, by - 16 + i * 16, bx + 30 - i * 12, by - 16 + i * 16,
                            3), M.flat("#6b7480"), profile=("bevel", 1.2, 1.6),
                    alpha=0.5)
    for i in range(4):
        c.paint(Capsule(boxes[0][0] - 46, boxes[0][1] - 20 + i * 14,
                        boxes[0][0] - 6, boxes[0][1] - 20 + i * 14, 3),
                M.flat("#7d848e"), profile=("bevel", 1, 1), alpha=0.5)
    for (ax, ay), (bx, by) in ((boxes[0], boxes[1]), (boxes[0], boxes[2]),
                               (boxes[1], boxes[3]), (boxes[2], boxes[4]),
                               (boxes[3], boxes[4])):
        c.paint(Capsule(ax + 70, ay, bx + 70, by, 3), M.flat("#7d848e"),
                profile=("bevel", 1.4, 2), alpha=0.45)
    for i in range(6):
        c.paint(Capsule(x0 + 62, y0 + 560 + i * 22, x0 + 300 - i * 12, y0 + 560 + i * 22,
                        3), M.flat("#8a9099"), profile=("bevel", 1.2, 1.6),
                alpha=0.40)
    # chrome clip
    clip = Poly([(x1 := cx + w / 2 - 26, y0 + 10), (x1 - 34, y0 - 34),
                 (x1 - 52, y0 + 30), (x1 - 20, y0 + 96), (x1 + 4, y0 + 40)],
                rounding=10)
    c.paint(Moved(clip, 0, 8), M.flat("#3a4048"), profile=("bevel", 4, 6))
    c.paint(clip, M.chrome, profile=("bevel", 8, 12), shadow=True, contact=0.2)
    # wax seal, the accent
    c.paint(Circle(x0 + 132, y0 + h - 96, 58), M.enamel, profile=("sphere", 42),
            hue=hue, sat=0.72, light=0.44, shadow=True, contact=0.28)
    c.paint(ring(x0 + 132, y0 + h - 96, 40, 6), M.brass, profile=("bevel", 2, 3),
            alpha=0.45)
    mark(c, "check", x0 + 132, y0 + h - 96, 44, M.brass, emboss=1.6)


# --------------------------------------------------------------------------- #
# ggg - the glyph stamps
# --------------------------------------------------------------------------- #

def type_stamps(c, hue: float = 206, cy: float = CY) -> None:
    """A walnut composing block holding three brass glyph stamps."""
    cx = CX
    block = RRect(cx, cy + 150, 640, 260, 18)
    c.paint(Moved(block, 0, 22), M.flat("#2a1a0c"), profile=("bevel", 10, 14))
    c.paint(block, M.wood, profile=("bevel", 18, 26), hue=24, sat=0.60, light=0.34,
            shadow=True, contact=0.26)
    c.paint(RRect(cx, cy + 44, 600, 54, 8), M.wood, profile=("bevel", 8, 12),
            hue=20, sat=0.50, light=0.24, contact=0.22)
    for i, glyph in enumerate(("star", "nib", "gear")):
        bx = cx - 200 + i * 200
        angle = (-6, 3, -2)[i]
        body = Rotated(RRect(bx, cy - 70, 152, 190, 12), angle, bx, cy - 70)
        c.paint(Moved(body, 0, 14), M.flat("#2a1e08"), profile=("bevel", 6, 9))
        c.paint(body, M.brass, profile=("bevel", 12, 18), shadow=True, contact=0.24)
        top = Rotated(RRect(bx, cy - 178, 152, 40, 10), angle, bx, cy - 70)
        c.paint(top, M.brass, profile=("bevel", 8, 12), contact=0.22)
        c.paint(Rotated(RRect(bx, cy - 96, 118, 108, 8), angle, bx, cy - 70),
                M.enamel, profile=("bevel", 4, 6), hue=hue, sat=0.66, light=0.44,
                contact=0.2)
        mark(c, glyph, bx, cy - 96, 84, M.brass, emboss=5.0)
    # a scatter of brass shavings on the block
    for dx, dy, rot in ((-250, 196, 12), (-30, 210, -8), (210, 200, 16)):
        c.paint(Rotated(Capsule(cx + dx, cy + dy, cx + dx + 54, cy + dy, 5), rot,
                        cx + dx, cy + dy), M.brass, profile=("sphere", 4),
                contact=0.1)


# --------------------------------------------------------------------------- #
# hygguile - the mug
# --------------------------------------------------------------------------- #

def mug(c, hue: float = 28, cy: float = CY) -> None:
    """A mug of cocoa on a knitted coaster, steam rising."""
    cx = CX
    # coaster: felt with a ribbed edge
    coaster = Ellipse(cx, cy + 300, 236, 74)
    c.paint(Moved(coaster, 0, 14), M.flat("#4a3a30"), profile=("bevel", 8, 12))
    c.paint(coaster, M.felt, profile=("sphere", 40), hue=24, sat=0.42, light=0.34,
            shadow=True, contact=0.24)
    for i in range(7):
        c.paint(Rotated(Capsule(cx - 150 + i * 50, cy + 290, cx - 130 + i * 50,
                                cy + 312, 4), 0, cx, cy), M.flat("#ffffff"),
                profile=("bevel", 1.5, 2), alpha=0.10)
    # handle
    c.paint(ring(cx + 186, cy + 40, 108, 40), M.enamel, profile=("sphere", 24),
            hue=40, sat=0.22, light=0.86, shadow=True, contact=0.22)
    # body: a tapered cup
    body = Poly([(cx - 172, cy - 110), (cx + 172, cy - 110), (cx + 140, cy + 264),
                 (cx - 140, cy + 264)], rounding=46)
    c.paint(Moved(body, 0, 20), M.flat("#6a5a44"), profile=("sphere", 80))
    c.paint(body, M.ceramic, profile=("sphere", 190), sat=0.05, light=0.95,
            shadow=True, contact=0.26)
    # cocoa: dark glossy surface, a crema ring
    c.paint(Ellipse(cx, cy - 104, 158, 44), M.flat("#2a1508"),
            profile=("sphere", 26), contact=0.2)
    c.paint(Ellipse(cx, cy - 108, 150, 38), M.enamel, profile=("sphere", 22), hue=24,
            sat=0.62, light=0.24, contact=0.18)
    c.paint(Ellipse(cx - 40, cy - 118, 54, 16), M.flat("#8a5a32"),
            profile=("sphere", 10), alpha=0.45)
    # rim band
    c.paint(ring(cx, cy - 110, 174, 14), M.ceramic, profile=("bevel", 5, 7),
            contact=0.18)
    # steam: two soft ribbons, visible against any background
    for side, dx in ((-1, -58), (1, 48)):
        steam = ribbon([(cx + dx, cy - 140), (cx + dx + side * 30, cy - 246),
                        (cx + dx - side * 24, cy - 356), (cx + dx + side * 12, cy - 452)],
                       (52, 40, 30, 12))
        c.paint(steam, M.flat("#ffffff"), profile=("bevel", 6, 10), alpha=0.34)
        c.paint(steam, M.flat("#dfe9f2"), profile=("bevel", 6, 10), alpha=0.18)
    # a spoon resting on the coaster
    c.paint(Rotated(Capsule(cx + 130, cy + 236, cx + 320, cy + 290, 12), 0, cx, cy),
            M.chrome, profile=("sphere", 10), shadow=True, contact=0.18)
    c.paint(Rotated(Ellipse(cx + 336, cy + 292, 30, 20), 0, cx, cy), M.chrome,
            profile=("sphere", 16), contact=0.18)


# --------------------------------------------------------------------------- #
# mutastructura - the platter stack
# --------------------------------------------------------------------------- #

def platter_stack(c, hue: float = 206, cy: float = CY) -> None:
    """Three mirror-finished platters on a spindle, with a read arm."""
    cx = CX
    base = RRect(cx, cy + 292, 420, 62, 18)
    c.paint(Moved(base, 0, 16), M.flat("#1b1e23"), profile=("bevel", 8, 12))
    c.paint(base, M.steel, profile=("bevel", 14, 20), shadow=True, contact=0.26)
    for side in (-1, 1):
        screw(c, cx + side * 168, cy + 292, 13)
    c.paint(RRect(cx, cy - 30, 54, 600, 12), M.chrome, profile=("bevel", 8, 12),
            contact=0.22)
    for i, y in enumerate((208, 20, -168)):
        c.paint(Ellipse(cx, cy + y + 34, 282, 74), M.flat("#1b1e23"),
                profile=("bevel", 8, 12))
        c.paint(Ellipse(cx, cy + y, 282, 70), M.chrome, profile=("sphere", 40),
                shadow=True, contact=0.24)
        c.paint(Ellipse(cx, cy + y, 268, 58), M.aluminium,
                profile=("bevel", 12, 18), contact=0.22, brush=0.03)
        c.paint(ring(cx, cy + y - 6, 70, 6), M.flat("#7a828c"),
                profile=("bevel", 2, 3), alpha=0.45)
        c.paint(Circle(cx, cy + y, 34), M.gunmetal, profile=("bevel", 5, 8),
                contact=0.24)
        c.paint(Capsule(cx - 232, cy + y + 6, cx - 100, cy + y + 16, 3),
                M.flat("#ffffff"), profile=("bevel", 1.5, 2), alpha=0.18)
    # read arm over the top platter
    arm = ribbon([(cx + 300, cy - 196), (cx + 190, cy - 118), (cx + 60, cy - 96)],
                 (44, 30, 18))
    c.paint(Moved(arm, 0, 10), M.flat("#1b1e23"), profile=("bevel", 6, 9))
    c.paint(arm, M.chrome, profile=("sphere", 18), shadow=True, contact=0.22)
    c.paint(Circle(cx + 292, cy - 194, 36), M.steel, profile=("sphere", 26),
            contact=0.24)
    c.paint(Circle(cx + 50, cy - 92, 18), M.enamel, profile=("sphere", 14), hue=hue,
            sat=0.70, light=0.50)
    c.paint(Capsule(cx + 300, cy - 196, cx + 352, cy - 292, 16), M.steel,
            profile=("sphere", 12), contact=0.2)
    # activity LEDs on the base
    for i in range(3):
        c.paint(Circle(cx - 120 + i * 30, cy + 292, 8), M.lamp,
                profile=("sphere", 6), hue=hue, alpha=0.9)


# --------------------------------------------------------------------------- #
# maak - the wrench with a glass socket
# --------------------------------------------------------------------------- #

def wrench_lens(c, hue: float = 206, cy: float = CY) -> None:
    """A machined wrench lying at 15 degrees, its socket a blue glass lens."""
    cx = CX
    angle = 15.0
    pivot = (cx, cy)

    def R(shape):
        return Rotated(shape, angle, pivot[0], pivot[1])

    # handle, open jaw at the far end
    handle = R(RRect(cx + 60, cy + 122, 430, 92, 42))
    c.paint(Moved(handle, 0, 20), M.flat("#20252c"), profile=("bevel", 8, 12))
    c.paint(handle, M.steel, profile=("bevel", 18, 26), shadow=True, contact=0.24)
    head = R(RRect(cx + 300, cy + 96, 220, 200, 74))
    jaw = head - R(RRect(cx + 392, cy + 60, 118, 96, 40))
    c.paint(Moved(jaw, 0, 16), M.flat("#20252c"), profile=("bevel", 8, 12))
    c.paint(jaw, M.steel, profile=("bevel", 14, 20), shadow=True, contact=0.24)
    for side in (-1, 1):
        c.paint(R(Ellipse(cx + 356, cy + 96 + side * 62, 34, 16)), M.chrome,
                profile=("sphere", 12), contact=0.18)
    # balance hole at the butt
    c.paint(R(Circle(cx - 168, cy + 158, 30)), M.gunmetal,
            profile=("bevel", 4, 6), contact=0.2)
    # the socket replaced by a glass lens in a chrome bezel
    bezel = R(Circle(cx - 96, cy - 6, 150))
    c.paint(Moved(R(Circle(cx - 96, cy - 18, 156)), 0, 18), M.flat("#20252c"),
            profile=("bevel", 8, 12))
    c.paint(bezel, M.chrome, profile=("sphere", 80), shadow=True, contact=0.26)
    c.paint(R(Circle(cx - 96, cy - 6, 122)), M.gunmetal,
            profile=("bevel", 8, 12), contact=0.3)
    c.paint(R(Circle(cx - 96, cy - 6, 112)), M.crystal, profile=("sphere", 60),
            hue=hue, sat=0.72, light=0.50, contact=0.3)
    c.paint(R(Ellipse(cx - 150, cy - 60, 44, 28)), M.flat("#ffffff"),
            profile=("sphere", 16), alpha=0.35)
    # machined flats on the handle
    for i in range(3):
        c.paint(R(Capsule(cx - 40 + i * 92, cy + 106, cx + 20 + i * 92, cy + 106, 4)),
                M.engraved, profile=("bevel", 2, 2), alpha=0.28)
    c.paint(R(Capsule(cx - 10, cy + 150, cx + 240, cy + 150, 4)), M.flat("#ffffff"),
            profile=("bevel", 1.5, 2), alpha=0.14)


# --------------------------------------------------------------------------- #
# consceal - the combination padlock
# --------------------------------------------------------------------------- #

def combination_lock(c, hue: float = 206, cy: float = CY) -> None:
    """A brass combination padlock with three knurled dials."""
    cx = CX
    arch = ring(cx, cy - 232, 132, 54) & RRect(cx, cy - 400, 460, 280)
    arch = arch | Capsule(cx - 132, cy - 246, cx - 132, cy - 96, 27) \
                | Capsule(cx + 132, cy - 246, cx + 132, cy - 96, 27)
    c.paint(Moved(arch, 0, 22), M.flat("#2a1e08"), profile=("bevel", 10, 14))
    c.paint(arch, M.chrome, profile=("sphere", 20), shadow=True, contact=0.24)
    body = RRect(cx, cy + 116, 420, 380, 40)
    c.paint(Moved(body, 0, 26), M.flat("#3a2608"), profile=("bevel", 12, 18))
    c.paint(body, M.brass, profile=("bevel", 30, 44), shadow=True, contact=0.28)
    c.paint(RRect(cx, cy + 116, 384, 344, 28), M.brass, profile=("bevel", 10, 16),
            contact=0.24)
    # three dials
    for i in range(3):
        dy = cy + 8 + i * 96
        c.paint(RRect(cx - 300, dy, 58, 96, 18), M.steel,
                profile=("bevel", 8, 12), contact=0.24, alpha=0.0)
        c.paint(RRect(cx, dy, 392, 88, 26), M.steel, profile=("bevel", 12, 18),
                contact=0.3)
        for k in range(9):
            c.paint(Capsule(cx - 160 + k * 40, dy - 30, cx - 160 + k * 40, dy + 30, 4),
                    M.flat("#1b1e23"), profile=("bevel", 1.5, 2), alpha=0.45)
        c.paint(RRect(cx, dy, 360, 60, 20), M.chrome, profile=("bevel", 8, 12),
                contact=0.26)
    # enamel ring on the body's face, the accent
    c.paint(ring(cx, cy + 116, 168, 16), M.enamel, profile=("bevel", 5, 8), hue=hue,
            sat=0.70, light=0.48, contact=0.2)
    c.paint(Circle(cx, cy + 116, 132), M.brass, profile=("bevel", 10, 16),
            contact=0.22)
    mark(c, "keyhole", cx, cy + 116, 62, M.gunmetal, emboss=4.0)


# --------------------------------------------------------------------------- #
# lucidplan - the planner
# --------------------------------------------------------------------------- #

def planner(c, hue: float = 206, cy: float = CY) -> None:
    """An open leather planner with a ribbon, tabs and a fountain pen."""
    cx = CX
    cover = RRect(cx, cy + 40, 640, 560, 22)
    c.paint(Moved(cover, 0, 24), M.flat("#0d1a26"), profile=("bevel", 10, 14))
    c.paint(cover, M.leather, profile=("bevel", 18, 26), hue=hue, sat=0.40, light=0.24,
            shadow=True, contact=0.26)
    for side in (-1, 1):
        page = RRect(cx + side * 148, cy + 24, 268, 500, 8)
        c.paint(page, M.paper, profile=("bevel", 6, 10), contact=0.2)
        for i in range(9):
            c.paint(Capsule(cx + side * 148 - 88, cy - 150 + i * 44,
                            cx + side * 148 + 88, cy - 150 + i * 44, 3),
                    M.flat("#8c96a2"), profile=("bevel", 1.2, 1.6), alpha=0.45)
        # printed checkbox column
        for i in range(4):
            c.paint(RRect(cx + side * 148 - 82, cy - 146 + i * 88, 18, 18, 3),
                    M.flat("#9aa4ae"), profile=("bevel", 1.5, 2), alpha=0.5)
    # spine and ribbon
    c.paint(RRect(cx, cy + 24, 42, 520, 12), M.leather, profile=("bevel", 6, 9),
            hue=hue, sat=0.36, light=0.18, contact=0.3)
    c.paint(Rotated(Capsule(cx + 86, cy - 90, cx + 118, cy + 240, 16), 0, cx, cy),
            M.enamel, profile=("bevel", 5, 8), hue=hue, sat=0.66, light=0.48,
            shadow=True, contact=0.18)
    # sticky tabs down the right edge
    for i, dy in enumerate((-150, -60, 30)):
        c.paint(RRect(cx + 300, cy + dy, 52, 74, 10), M.enamel,
                profile=("bevel", 4, 6), hue=hue, sat=0.60, light=0.58 - i * 0.06,
                contact=0.18)
    # fountain pen lying in the gutter
    pen = Rotated(Capsule(cx - 10, cy + 210, cx + 250, cy + 96, 18), 0, cx, cy)
    c.paint(Moved(pen, 0, 12), M.flat("#0d1a26"), profile=("bevel", 5, 8))
    c.paint(pen, M.enamel, profile=("bevel", 8, 12), hue=hue, sat=0.64, light=0.34,
            shadow=True, contact=0.2)
    c.paint(Rotated(Capsule(cx + 236, cy + 102, cx + 292, cy + 78, 16), 0, cx, cy),
            M.brass, profile=("bevel", 4, 6), contact=0.2)
    c.paint(Rotated(Capsule(cx + 268, cy + 92, cx + 320, cy + 70, 4), 0, cx, cy),
            M.flat("#2a1e08"), profile=("bevel", 1.5, 2), alpha=0.7)


# --------------------------------------------------------------------------- #
# welkomscherm.el - the desk lamp
# --------------------------------------------------------------------------- #

def desk_lamp(c, hue: float = 40, cy: float = CY) -> None:
    """A chrome architect lamp, its warm shade one bright accent."""
    cx = CX
    c.paint(Ellipse(cx - 90, cy + 320, 190, 54), M.steel,
            profile=("bevel", 10, 14), shadow=True, contact=0.26)
    lower = ribbon([(cx - 90, cy + 300), (cx + 40, cy + 40)], (46, 30))
    c.paint(Moved(lower, 0, 14), M.flat("#20252c"), profile=("bevel", 6, 9))
    c.paint(lower, M.chrome, profile=("sphere", 20), shadow=True, contact=0.22)
    upper = ribbon([(cx + 40, cy + 40), (cx + 240, cy - 240)], (30, 22))
    c.paint(Moved(upper, 0, 12), M.flat("#20252c"), profile=("bevel", 6, 9))
    c.paint(upper, M.chrome, profile=("sphere", 16), shadow=True, contact=0.22)
    for jx, jy, r in ((cx + 40, cy + 40, 34), (cx + 240, cy - 240, 26)):
        c.paint(Circle(jx, jy, r), M.chrome, profile=("sphere", r * 0.8),
                shadow=True, contact=0.24)
        c.paint(Circle(jx, jy, r * 0.42), M.steel, profile=("sphere", 10),
                contact=0.2)
    # shade: a wide cone with a warm interior facing the desk
    shade = Poly([(cx + 214, cy - 286), (cx + 372, cy - 250), (cx + 452, cy + 6),
                  (cx + 250, cy - 26)], rounding=34)
    c.paint(Moved(shade, 0, 20), M.flat("#20252c"), profile=("bevel", 8, 12))
    c.paint(shade, M.chrome, profile=("sphere", 70), shadow=True, contact=0.22)
    opening = Poly([(cx + 258, cy - 30), (cx + 448, cy - 2), (cx + 420, cy + 62),
                    (cx + 274, cy + 30)], rounding=26)
    c.paint(opening, M.lamp, profile=("sphere", 34), hue=hue, contact=0.2)
    c.paint(Ellipse(cx + 344, cy + 16, 74, 34), M.lamp, profile=("sphere", 20),
            hue=hue, alpha=0.55)
    # glow pooling on the desk
    c.paint(Ellipse(cx + 250, cy + 316, 210, 62), M.lamp, profile=("sphere", 30),
            hue=hue, alpha=0.22)
    c.paint(Ellipse(cx + 250, cy + 316, 150, 40), M.lamp, profile=("sphere", 20),
            hue=hue, alpha=0.24)
    # switch
    c.paint(RRect(cx - 160, cy + 250, 56, 34, 10), M.brass,
            profile=("bevel", 4, 6), contact=0.2)


# --------------------------------------------------------------------------- #
# screensaver - the crystal ball
# --------------------------------------------------------------------------- #

def crystal_ball(c, hue: float = 258, cy: float = CY) -> None:
    """A glass orb full of stars on a three-claw brass stand."""
    cx = CX
    # stand: ring and claws
    c.paint(Ellipse(cx, cy + 314, 198, 56), M.brass, profile=("bevel", 10, 14),
            shadow=True, contact=0.26)
    c.paint(RRect(cx, cy + 270, 300, 66, 18), M.brass, profile=("bevel", 12, 18),
            contact=0.26)
    for i in range(3):
        a = math.radians(-90 + i * 120)
        x, y = cx + math.cos(a) * 168, cy + 124 + math.sin(a) * 60
        c.paint(ribbon([(x, cy + 268), (x * 0.9 + cx * 0.1, cy + 180), (x, y)],
                       (30, 24, 26)), M.brass, profile=("sphere", 12),
                shadow=True, contact=0.2)
    orb = Circle(cx, cy - 10, 254)
    # starfield inside
    c.paint(orb, M.flat("#0b1220"), profile=("sphere", 180), contact=0.2)
    for dx, dy, r in ((-120, -80, 5), (-40, -150, 4), (70, -120, 6), (140, -20, 4),
                      (60, 60, 5), (-80, 80, 4), (-160, 30, 3), (20, 140, 4),
                      (120, 130, 3)):
        c.paint(Circle(cx + dx, cy - 10 + dy, r), M.flat("#ffffff"),
                profile=("sphere", r), alpha=0.85)
    c.paint(Circle(cx + 30, cy - 150, 40), M.flat("#9fc4ff"),
            profile=("sphere", 26), alpha=0.20)
    # glass over it
    c.paint(orb, M.glass, profile=("sphere", 200), hue=hue, sat=0.30, light=0.52,
            alpha=0.22, contact=0.26)
    c.paint(Ellipse(cx - 96, cy - 118, 72, 50), M.flat("#ffffff"),
            profile=("sphere", 34), alpha=0.28)
    c.paint(Circle(cx - 132, cy - 146, 24), M.flat("#ffffff"),
            profile=("sphere", 16), alpha=0.65)
    c.paint(ring(cx, cy - 10, 252, 5), M.flat("#dce8ff"), profile=("bevel", 2, 2),
            alpha=0.35)


# --------------------------------------------------------------------------- #
# software update - the parcel
# --------------------------------------------------------------------------- #

def parcel(c, hue: float = 210, cy: float = CY) -> None:
    """A kraft-paper parcel tied with twine, a blue shipping label."""
    cx = CX
    body = RRect(cx, cy + 70, 520, 470, 14)
    c.paint(Moved(body, 0, 26), M.flat("#6a5334"), profile=("bevel", 10, 14))
    c.paint(body, M.enamel, profile=("bevel", 16, 22), hue=34, sat=0.34, light=0.58,
            shadow=True, contact=0.26)
    # folded top flaps
    c.paint(Poly([(cx - 260, cy - 166), (cx, cy - 88), (cx + 260, cy - 166),
                  (cx + 260, cy - 118), (cx, cy - 34), (cx - 260, cy - 118)],
                 rounding=8), M.enamel, profile=("bevel", 8, 12), hue=34, sat=0.36,
            light=0.52, contact=0.22)
    c.paint(Poly([(cx - 210, cy - 160), (cx, cy - 96), (cx + 210, cy - 160),
                  (cx + 210, cy - 142), (cx, cy - 76), (cx - 210, cy - 142)],
                 rounding=6), M.flat("#e8d9b8"), profile=("bevel", 3, 4), alpha=0.4)
    # twine: two turns crossing
    for x in (cx - 120, cx + 120):
        c.paint(Capsule(x, cy - 150, x, cy + 296, 11), M.enamel,
                profile=("sphere", 9), hue=36, sat=0.36, light=0.72, contact=0.18)
    c.paint(Capsule(cx - 260, cy + 50, cx + 260, cy + 50, 10), M.enamel,
            profile=("sphere", 8), hue=36, sat=0.36, light=0.70, contact=0.16)
    c.paint(Circle(cx, cy + 50, 26), M.enamel, profile=("sphere", 20), hue=36,
            sat=0.40, light=0.66, shadow=True, contact=0.22)
    # label
    label = Rotated(RRect(cx + 110, cy + 150, 190, 120, 6), -4, cx, cy)
    c.paint(Moved(label, 0, 8), M.flat("#b9b1a2"), profile=("bevel", 4, 6))
    c.paint(label, M.paper, profile=("bevel", 4, 6), shadow=True, contact=0.2)
    c.paint(Rotated(RRect(cx + 110, cy + 116, 150, 22, 4), -4, cx, cy),
            M.enamel, profile=("bevel", 2, 3), hue=hue, sat=0.64, light=0.46,
            contact=0.16)
    for i in range(3):
        c.paint(Rotated(Capsule(cx + 60, cy + 152 + i * 18, cx + 160, cy + 152 + i * 18,
                                3), -4, cx, cy), M.flat("#5a646f"),
                profile=("bevel", 1.2, 1.6), alpha=0.5)


# --------------------------------------------------------------------------- #
# applications-other - the drawer
# --------------------------------------------------------------------------- #

def drawer(c, hue: float = 34, cy: float = CY) -> None:
    """An oak card drawer, open a finger's width, with a brass pull."""
    cx = CX
    case = RRect(cx, cy + 20, 560, 480, 20)
    c.paint(Moved(case, 0, 24), M.flat("#2a1a0c"), profile=("bevel", 10, 14))
    c.paint(case, M.wood, profile=("bevel", 20, 30), hue=24, sat=0.62, light=0.36,
            shadow=True, contact=0.28)
    c.paint(RRect(cx, cy + 20, 500, 420, 14), M.wood, profile=("bevel", 10, 16),
            hue=28, sat=0.56, light=0.30, contact=0.24)
    front = RRect(cx, cy + 30, 466, 300, 12)
    c.paint(Moved(front, 0, 10), M.flat("#2a1a0c"), profile=("bevel", 6, 9))
    c.paint(front, M.wood, profile=("bevel", 12, 18), hue=26, sat=0.60, light=0.44,
            shadow=True, contact=0.22)
    # a strip of index cards peeking out of the open top
    for i in range(4):
        c.paint(Rotated(RRect(cx - 30 + i * 18, cy - 136, 300, 130, 4), -2 + i * 1.2,
                        cx, cy), M.paper, profile=("bevel", 3, 4), contact=0.14)
        c.paint(Rotated(Capsule(cx - 150 + i * 18, cy - 160, cx + 90 + i * 18,
                                cy - 160, 3), -2 + i * 1.2, cx, cy),
                M.flat("#8c96a2"), profile=("bevel", 1.2, 1.6), alpha=0.4)
    # brass cup pull and a label holder
    c.paint(RRect(cx, cy + 34, 190, 46, 20), M.brass, profile=("bevel", 8, 12),
            shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 34, 150, 24, 10), M.gunmetal, profile=("bevel", 4, 6),
            contact=0.24)
    c.paint(RRect(cx, cy + 120, 210, 64, 8), M.brass, profile=("bevel", 4, 6),
            contact=0.2)
    c.paint(RRect(cx, cy + 120, 186, 46, 6), M.paper, profile=("bevel", 2, 3),
            contact=0.18)
    for i in range(3):
        c.paint(Capsule(cx - 56 + i * 56, cy + 120, cx - 30 + i * 56, cy + 120, 3),
                M.flat("#6b7480"), profile=("bevel", 1.2, 1.6), alpha=0.5)
    # dovetail detail at the corners
    for side in (-1, 1):
        for i in range(3):
            c.paint(Capsule(cx + side * 286, cy - 20 + i * 46,
                            cx + side * 262, cy - 20 + i * 46, 6),
                    M.engraved, profile=("bevel", 2, 3), alpha=0.30)


# --------------------------------------------------------------------------- #
# accessibility - the spectacles
# --------------------------------------------------------------------------- #

def spectacles(c, hue: float = 210, cy: float = CY) -> None:
    """Reading glasses in brass with blue-tinted lenses."""
    cx = CX
    for side in (-1, 1):
        frame = Circle(cx + side * 172, cy - 20, 168)
        c.paint(Moved(frame, 0, 18), M.flat("#2a1e08"), profile=("bevel", 8, 12))
        c.paint(frame, M.brass, profile=("sphere", 40), shadow=True, contact=0.24)
        c.paint(Circle(cx + side * 172, cy - 20, 132), M.gunmetal,
                profile=("bevel", 6, 9), contact=0.3)
        c.paint(Circle(cx + side * 172, cy - 20, 126), M.glass,
                profile=("sphere", 80), hue=hue, sat=0.34, light=0.70, alpha=0.55,
                contact=0.2)
        c.paint(Ellipse(cx + side * 172 - 46, cy - 66, 44, 30), M.flat("#ffffff"),
                profile=("sphere", 18), alpha=0.35)
        c.paint(Capsule(cx + side * 172, cy - 210, cx + side * 320, cy - 250, 20),
                M.brass, profile=("sphere", 14), shadow=True, contact=0.18)
    c.paint(Capsule(cx - 20, cy - 30, cx + 20, cy - 30, 12), M.brass,
            profile=("sphere", 10), shadow=True, contact=0.2)
    c.paint(Capsule(cx - 168, cy - 26, cx - 60, cy - 30, 9), M.brass,
            profile=("sphere", 7), alpha=0.0)


# --------------------------------------------------------------------------- #
# symbanta - the chart recorder
# --------------------------------------------------------------------------- #

def chart_recorder(c, hue: float = 204, cy: float = CY, pens: int = 1) -> None:
    """A strip-chart recorder: brushed housing, a roll of paper, one inked line.

    Analytics should look like a measurement, not a clock: the paper carries a
    printed grid and a rising trace, and the pen arm is a real chrome arm with a
    red nib.  ``pens=2`` adds a second, lighter trace for the dashboard.
    """
    cx = CX
    # housing
    body = RRect(cx, cy + 150, 660, 300, 30)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 28), shadow=True, contact=0.24)
    c.paint(RRect(cx, cy + 30, 560, 60, 14), M.flat("#2b3038"),
            profile=("bevel", 4, 6), contact=0.3)
    for i in range(7):
        c.paint(RRect(cx - 240 + i * 80, cy + 216, 54, 90, 8), M.flat("#20242b"),
                profile=("bevel", 3, 4), alpha=0.55)
    c.paint(Capsule(cx + 254, cy + 254, cx + 254, cy + 254, 8), M.lamp,
            profile=("sphere", 6), hue=140)
    c.paint(Circle(cx - 258, cy + 250, 26), M.chrome, profile=("sphere", 18),
            contact=0.2)
    # paper roll, end-on, sitting in the well
    roll = Capsule(cx - 30, cy - 132, cx + 250, cy - 132, 226)
    c.paint(Moved(roll, 0, 22), M.flat("#7d7568"), profile=("sphere", 70))
    c.paint(roll, M.paper, profile=("sphere", 113), shadow=True, contact=0.24)
    c.paint(Ellipse(cx - 30, cy - 132, 104, 104), M.paper, profile=("bevel", 6, 9),
            contact=0.2)
    c.paint(Circle(cx - 30, cy - 132, 34), M.gunmetal, profile=("sphere", 26),
            contact=0.24)
    c.paint(Circle(cx - 30, cy - 132, 12), M.flat("#0d1014"), profile=("sphere", 8))
    # the sheet, hanging over the front of the housing
    sheet = Poly([(cx - 236, cy + 46), (cx + 196, cy + 24), (cx + 212, cy + 280),
                  (cx - 222, cy + 296)], rounding=3)
    c.paint(Moved(sheet, 0, 18), M.flat("#8d867a"), profile=("bevel", 4, 6))
    c.paint(sheet, M.paper, profile=("flat",), shadow=True, contact=0.20)
    # printed grid and axes, clipped to the sheet
    cover = smoothstep(0.0, 1.3, 0.6 - sheet.sdf(c.X, c.Y))
    grid = np.zeros((SIZE, SIZE), dtype=np.float32)
    for i in range(1, 6):
        y = cy + 46 + i * 40
        grid += polyline_mask([(cx - 232, y), (cx + 204, y - 10)], 2.0)
        vx = cx - 226 + i * 70
        grid += polyline_mask([(vx, cy + 42), (vx + 8, cy + 292)], 2.0)
    c.paint_mask(grid * cover, M.flat("#2f333a"), emboss=0.5, alpha=0.35)
    trace = polyline_mask([(cx - 218, cy + 250), (cx - 144, cy + 212),
                           (cx - 92, cy + 232), (cx - 24, cy + 154),
                           (cx + 48, cy + 178), (cx + 118, cy + 88),
                           (cx + 192, cy + 110)], 10.0)
    c.paint_mask(trace * cover, M.flat(hsl(hue, 0.72, 0.42)), emboss=2.0, alpha=0.95)
    if pens > 1:
        trace2 = polyline_mask([(cx - 218, cy + 274), (cx - 144, cy + 266),
                                (cx - 70, cy + 220), (cx + 6, cy + 236),
                                (cx + 78, cy + 176), (cx + 150, cy + 192),
                                (cx + 192, cy + 168)], 7.0)
        c.paint_mask(trace2 * cover, M.flat(hsl(hue + 38, 0.62, 0.52)), emboss=1.4,
                     alpha=0.9)
    # pen arm and nib
    tip = (cx + 192, cy + 110)
    c.paint(Capsule(cx + 250, cy - 60, tip[0], tip[1] + 2, 9), M.chrome,
            profile=("bevel", 4, 5), shadow=True, contact=0.2)
    c.paint(Circle(tip[0], tip[1] + 4, 11), M.enamel, profile=("sphere", 8), hue=2,
            sat=0.68, light=0.44, contact=0.2)


# --------------------------------------------------------------------------- #
# maak - the multitool
# --------------------------------------------------------------------------- #

def multitool(c, hue: float = 204, cy: float = CY) -> None:
    """An open pocket knife: anodised scales, four steel tools, one glass inlay.

    "Infinitely extensible command runner" as the object it actually is - the
    thing you reach for instead of a bag of separate tools.
    """
    cx = CX
    pivot = (cx - 196, cy + 150)
    # handle, lying at a slight angle
    handle = Rotated(RRect(cx + 120, cy + 178, 500, 188, 84), 10, cx + 120, cy + 178)
    c.paint(Moved(handle, 0, 26), M.flat("#14171c"), profile=("bevel", 14, 18))
    c.paint(handle, M.aluminium, profile=("bevel", 26, 34), shadow=True, contact=0.26)
    inset = Rotated(RRect(cx + 120, cy + 172, 430, 126, 58), 10, cx + 120, cy + 172)
    c.paint(inset, M.rubber, profile=("bevel", 10, 14), contact=0.28)
    shield = Rotated(Poly([(cx + 84, cy + 112), (cx + 158, cy + 96),
                           (cx + 196, cy + 164), (cx + 122, cy + 208),
                           (cx + 50, cy + 180)], rounding=18), 10, cx + 120, cy + 172)
    c.paint(shield, M.glass, profile=("bevel", 6, 9), hue=hue, sat=0.66, light=0.50,
            contact=0.2)
    for x, y in ((cx - 96, cy + 122), (cx + 328, cy + 214)):
        c.paint(Circle(x, y, 19), M.chrome, profile=("sphere", 13), shadow=True,
                contact=0.25)
    hole = (cx + 320, cy + 216)
    c.paint(Circle(hole[0], hole[1], 20), M.chrome, profile=("sphere", 14),
            contact=0.22)
    c.paint(Circle(hole[0], hole[1], 12), M.flat("#0d1014"), profile=("bevel", 3, 4))
    # the large blade: a drop point, broad at the pivot, tapering to the tip
    blade = Poly([(pivot[0] + 74, pivot[1] + 34), (pivot[0] + 6, pivot[1] - 130),
                  (pivot[0] - 64, pivot[1] - 262), (pivot[0] - 142, pivot[1] - 368),
                  (pivot[0] - 168, pivot[1] - 330), (pivot[0] - 96, pivot[1] - 176),
                  (pivot[0] - 26, pivot[1] - 6)], rounding=10)
    c.paint(Moved(blade, 0, 14), M.flat("#1b1f25"), profile=("bevel", 6, 9))
    c.paint(blade, M.chrome, profile=("bevel", 12, 16), shadow=True, contact=0.24)
    c.paint_mask(polyline_mask([(pivot[0] + 8, pivot[1] - 140),
                                (pivot[0] - 130, pivot[1] - 356)], 8.0),
                 M.flat("#ffffff"), emboss=2.4, alpha=0.45)
    # a shorter saw blade beside it, teeth along the spine
    saw = Poly([(pivot[0] - 8, pivot[1] + 6), (pivot[0] - 108, pivot[1] - 178),
                (pivot[0] - 158, pivot[1] - 158), (pivot[0] - 70, pivot[1] + 26)],
               rounding=5)
    c.paint(Moved(saw, 0, 20), M.flat("#1b1f25"), profile=("bevel", 5, 8))
    c.paint(saw, M.steel, profile=("bevel", 8, 11), shadow=True, contact=0.24)
    for i in range(7):
        x = pivot[0] - 26 - i * 19
        y = pivot[1] - 30 - i * 24
        c.paint(Poly([(x, y), (x - 14, y - 8), (x - 6, y - 22), (x + 6, y - 10)],
                     rounding=2), M.chrome, profile=("bevel", 3, 4), contact=0.15)
    # bottle opener, folded out below the saw
    opener = Poly([(pivot[0] - 26, pivot[1] + 20), (pivot[0] - 146, pivot[1] + 86),
                   (pivot[0] - 178, pivot[1] + 150), (pivot[0] - 120, pivot[1] + 154),
                   (pivot[0] - 60, pivot[1] + 98), (pivot[0] - 6, pivot[1] + 44)],
                  rounding=14)
    c.paint(Moved(opener, 0, 14), M.flat("#1b1f25"), profile=("bevel", 5, 8))
    c.paint(opener, M.steel, profile=("bevel", 8, 11), shadow=True, contact=0.22)
    c.paint(Circle(pivot[0] - 142, pivot[1] + 108, 26), M.flat("#0d1014"),
            profile=("bevel", 5, 7), contact=0.2)
    c.paint(Circle(pivot[0], pivot[1], 34), M.chrome, profile=("bevel", 9, 11),
            shadow=True, contact=0.26)
    c.paint(Circle(pivot[0], pivot[1], 11), M.flat("#0d1014"), profile=("sphere", 6))


# --------------------------------------------------------------------------- #
# veritas - Lady Justice
# --------------------------------------------------------------------------- #

def lady_justice(c, hue: float = 44, cy: float = CY, bronze: bool = False) -> None:
    """A small statuette: blindfolded Justice with a sword and a brass balance.

    The figure is deliberately simple - a plinth, a robe, a head, one arm out -
    because at 32 px it is the scales and the swordsilhouette that identify it.
    ``bronze`` swaps the marble for patinated bronze (the .el twin).
    """
    cx = CX
    body_mat = M.enamel
    body_opts = dict(hue=28, sat=0.16, light=0.28) if bronze else dict(hue=42, sat=0.07,
                                                                        light=0.88)
    trim = M.enamel
    trim_opts = dict(hue=150, sat=0.44, light=0.42) if bronze else dict(hue=hue, sat=0.45,
                                                                        light=0.46)
    # plinth
    c.paint(Moved(RRect(cx, cy + 366, 520, 96, 14), 0, 18), M.flat("#262b32"),
            profile=("bevel", 8, 12))
    c.paint(RRect(cx, cy + 366, 520, 96, 14), M.ceramic, profile=("bevel", 12, 18),
            sat=0.03, light=0.86, shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 302, 420, 44, 10), M.ceramic, profile=("bevel", 6, 9),
            sat=0.03, light=0.92, contact=0.24)
    c.paint(RRect(cx - 150, cy + 356, 170, 26, 5), M.brass, profile=("bevel", 3, 5),
            contact=0.2)
    # robe: a tapered column with a hem
    robe = Poly([(cx - 128, cy + 288), (cx - 96, cy + 40), (cx - 40, cy - 20),
                 (cx + 40, cy - 20), (cx + 96, cy + 40), (cx + 132, cy + 288)],
                rounding=40)
    c.paint(Moved(robe, 0, 14), M.flat("#101317"), profile=("bevel", 8, 12))
    c.paint(robe, body_mat, profile=("sphere", 120), shadow=True, contact=0.26,
            **body_opts)
    for i in range(4):
        x = cx - 66 + i * 44
        c.paint(Capsule(x, cy + 60, x + (i - 1.5) * 12, cy + 270, 4), M.flat("#ffffff"),
                profile=("bevel", 2, 2), alpha=0.14)
    # sash, the one accent on the body
    c.paint(Capsule(cx - 118, cy + 92, cx + 110, cy + 132, 26), trim,
            profile=("bevel", 6, 9), contact=0.2, **trim_opts)
    # neck and head
    c.paint(Capsule(cx, cy - 26, cx, cy + 16, 46), body_mat, profile=("sphere", 22),
            contact=0.2, **body_opts)
    head = Circle(cx, cy - 90, 74)
    c.paint(Moved(head, 0, 10), M.flat("#101317"), profile=("sphere", 40))
    c.paint(head, body_mat, profile=("sphere", 74), shadow=True, contact=0.24,
            **body_opts)
    # hair, then the blindfold across the eyes
    # a low chignon, tucked behind the head rather than a cap on top of it
    c.paint(Circle(cx + 34, cy - 128, 46), M.enamel, profile=("sphere", 40),
            hue=28 if not bronze else 22, sat=0.24, light=0.22 if bronze else 0.14,
            contact=0.2)
    c.paint(Capsule(cx - 62, cy - 96, cx + 62, cy - 96, 22), M.leather,
            profile=("bevel", 5, 7), hue=28, sat=0.35, light=0.24, contact=0.2)
    c.paint(Capsule(cx - 62, cy - 104, cx + 62, cy - 104, 4), trim,
            profile=("bevel", 2, 2), **trim_opts)
    c.paint(Capsule(cx + 64, cy - 100, cx + 96, cy - 120, 7), M.leather,
            profile=("bevel", 3, 4), hue=28, sat=0.35, light=0.24)
    # sword arm, hanging straight down
    c.paint(Capsule(cx + 86, cy - 6, cx + 168, cy + 60, 26), body_mat,
            profile=("sphere", 14), contact=0.2, **body_opts)
    c.paint(Circle(cx + 172, cy + 66, 22), body_mat, profile=("sphere", 16),
            contact=0.2, **body_opts)
    c.paint(Capsule(cx + 168, cy + 92, cx + 180, cy + 342, 18), M.chrome,
            profile=("bevel", 6, 9), shadow=True, contact=0.2)
    c.paint(Capsule(cx + 168, cy + 300, cx + 180, cy + 344, 4), M.flat("#ffffff"),
            profile=("bevel", 2, 2), alpha=0.5)
    c.paint(Capsule(cx + 128, cy + 96, cx + 220, cy + 96, 14), M.brass,
            profile=("bevel", 5, 7), shadow=True, contact=0.2)
    c.paint(Circle(cx + 174, cy + 74, 12), M.flat("#0d1014"), profile=("sphere", 8))
    # the balance, held out to the left
    c.paint(Capsule(cx - 96, cy - 4, cx - 190, cy - 176, 24), body_mat,
            profile=("sphere", 14), contact=0.2, **body_opts)
    beam_y = cy - 214
    c.paint(Capsule(cx - 190, beam_y, cx - 190, cy - 20, 7), M.brass,
            profile=("bevel", 3, 4), contact=0.2)
    c.paint(Capsule(cx - 330, beam_y - 6, cx - 50, beam_y + 12, 9), M.brass,
            profile=("bevel", 4, 6), shadow=True, contact=0.2)
    c.paint(Circle(cx - 190, beam_y, 18), M.brass, profile=("sphere", 12), contact=0.2)
    for side, drop in ((-1, 0.0), (1, 14.0)):
        x = cx - 190 + side * 132
        for j in (-1, 1):
            c.paint(Capsule(x + j * 30, beam_y + 6, x + j * 20, beam_y + 96, 3),
                    M.brass, profile=("bevel", 2, 2), alpha=0.9)
        pan = Ellipse(x, beam_y + 96 + drop, 62, 18)
        c.paint(Moved(pan, 0, 8), M.brass, profile=("bevel", 4, 6))
        c.paint(pan, M.brass, profile=("bevel", 8, 12), shadow=True, contact=0.2)
    c.paint(Circle(cx - 330, beam_y - 6, 10), M.brass, profile=("sphere", 6))
    c.paint(Circle(cx - 50, beam_y + 12, 10), M.brass, profile=("sphere", 6))


# --------------------------------------------------------------------------- #
# wikimusic - the conductor
# --------------------------------------------------------------------------- #

def conductor(c, hue: float = 30, cy: float = CY) -> None:
    """A porcelain conductor on a walnut podium, baton raised over a score.

    A black tailcoat figure is mostly silhouette - exactly what survives 16 px -
    and the white baton is the one bright internal shape.
    """
    cx = CX
    # podium
    c.paint(Moved(Ellipse(cx + 20, cy + 344, 276, 66), 0, 20), M.flat("#2a1d0f"),
            profile=("bevel", 10, 14))
    c.paint(Ellipse(cx + 20, cy + 344, 276, 66), M.wood, profile=("sphere", 40),
            shadow=True, contact=0.24)
    c.paint(RRect(cx + 20, cy + 300, 480, 54, 12), M.wood, profile=("bevel", 8, 12),
            contact=0.26)
    # music stand behind, on a chrome column
    c.paint(Capsule(cx + 250, cy + 40, cx + 250, cy + 290, 12), M.chrome,
            profile=("bevel", 4, 6), contact=0.2)
    c.paint(Ellipse(cx + 250, cy + 292, 96, 26), M.chrome,
            profile=("bevel", 6, 9), shadow=True, contact=0.2)
    stand = Rotated(RRect(cx + 250, cy - 20, 260, 200, 8), -12, cx + 250, cy - 20)
    c.paint(Moved(stand, 0, 14), M.flat("#5d6470"), profile=("bevel", 6, 9))
    c.paint(stand, M.paper, profile=("flat",), shadow=True, contact=0.2)
    staves = np.zeros((SIZE, SIZE), dtype=np.float32)
    for row in range(5):
        y = cy - 78 + row * 22
        staves += polyline_mask([(cx + 148, y + 40), (cx + 344, y - 6)], 2.0)
    c.paint_mask(staves, M.flat("#2f333a"), emboss=0.4, alpha=0.55)
    # the figure: tailcoat, shirt front, ivory head
    coat = Poly([(cx - 106, cy + 300), (cx - 96, cy + 20), (cx - 30, cy - 24),
                 (cx + 30, cy - 24), (cx + 96, cy + 20), (cx + 108, cy + 300)],
                rounding=44)
    c.paint(Moved(coat, 0, 16), M.flat("#08090c"), profile=("bevel", 8, 12))
    c.paint(coat, M.rubber, profile=("sphere", 140), shadow=True, contact=0.28)
    c.paint(Poly([(cx - 40, cy + 6), (cx + 40, cy + 6), (cx + 26, cy + 250),
                  (cx - 26, cy + 250)], rounding=10), M.flat("#f4f2ec"),
            profile=("bevel", 4, 6), contact=0.2)
    c.paint(Poly([(cx - 34, cy - 6), (cx + 34, cy - 6), (cx, cy + 54)], rounding=6),
            M.flat("#111419"), profile=("bevel", 3, 5))
    c.paint(Poly([(cx - 14, cy - 16), (cx + 14, cy - 16), (cx + 20, cy + 10),
                  (cx - 20, cy + 10)], rounding=4), M.flat("#ffffff"),
            profile=("sphere", 6))
    # head and hair
    head = Circle(cx, cy - 84, 66)
    c.paint(Moved(head, 0, 10), M.flat("#0a0b0e"), profile=("sphere", 40))
    c.paint(head, M.ceramic, profile=("sphere", 66), sat=0.03, light=0.93,
            shadow=True, contact=0.26)
    c.paint(Ellipse(cx, cy - 122, 70, 40), M.flat("#17181c"), profile=("sphere", 30),
            contact=0.2)
    # arms and baton
    c.paint(Capsule(cx - 90, cy + 10, cx - 200, cy - 130, 26), M.rubber,
            profile=("sphere", 14), contact=0.22)
    c.paint(Circle(cx - 204, cy - 136, 20), M.ceramic, profile=("sphere", 14),
            sat=0.03, light=0.93, contact=0.2)
    c.paint(Capsule(cx + 90, cy + 10, cx + 210, cy - 150, 26), M.rubber,
            profile=("sphere", 14), contact=0.22)
    c.paint(Circle(cx + 214, cy - 156, 20), M.ceramic, profile=("sphere", 14),
            sat=0.03, light=0.93, contact=0.2)
    c.paint(Capsule(cx + 214, cy - 156, cx + 330, cy - 300, 8), M.ivory,
            profile=("sphere", 5), shadow=True, contact=0.2)
    c.paint(Capsule(cx + 214, cy - 152, cx + 246, cy - 190, 12), M.wood,
            profile=("bevel", 4, 5), hue=26, sat=0.5, light=0.30, contact=0.2)
    # a warm brass baton butt, the accent
    c.paint(Circle(cx + 332, cy - 302, 10), M.brass, profile=("sphere", 7))


# --------------------------------------------------------------------------- #
# maak - the disk
# --------------------------------------------------------------------------- #

def _lambda_marks(cx: float, cy: float, height: float, width: float,
                  stroke: float):
    """A lowercase lambda: one long diagonal, a leg branching from its middle."""
    left, right = cx - width / 2, cx + width / 2
    top, bottom = cy - height / 2, cy + height / 2
    apex = (left + width * 0.12, top)
    foot = (right, bottom)
    joint = (apex[0] + (foot[0] - apex[0]) * 0.46, top + height * 0.46)
    return (Capsule(apex[0], apex[1], foot[0], foot[1], stroke / 2)
            | Capsule(joint[0], joint[1], left + width * 0.16, bottom, stroke / 2)
            | Circle(joint[0], joint[1], stroke / 2))


def floppy_lambda(c, hue: float = 204, cy: float = CY) -> None:
    """A 3.5-inch disk, its label carrying one printed lambda: maak itself.

    A command runner should be the medium the artefact arrives on.  Graphite
    shell with the floppy's chamfered corner and its chrome shutter, a cream
    label whose only mark is the lambda, and the same 2.5D extrusion as the
    drive family so it sits in a Finder window with them.
    """
    cx = CX
    front_w, front_h = 616, 596
    chamfer = 104
    left, right = cx - front_w / 2, cx + front_w / 2
    top, bottom = cy - front_h / 2, cy + front_h / 2
    shell = Poly([(left + 24, top), (right - chamfer, top), (right, top + chamfer),
                  (right, bottom - 24), (right - 24, bottom), (left + 24, bottom),
                  (left, bottom - 24), (left, top + 24)], rounding=10)
    c.paint(Moved(shell, 0, 24), M.flat("#0a0e13"), profile=("bevel", 8, 12))
    c.paint(shell, M.enamel, profile=("bevel", 22, 30), hue=212, sat=0.22, light=0.26,
            shadow=True, contact=0.26)
    # a moulded lip along the top edge, just inside the silhouette
    c.paint(Capsule(left + 46, top + 30, right - chamfer - 8, top + 30, 7),
            M.flat("#3a4654"), profile=("bevel", 4, 6), alpha=0.5)
    # the shutter, flush with the top edge, and the head window under it
    c.paint(RRect(cx + 26, top + 64, 250, 80, 8), M.flat("#080b0f"),
            profile=("bevel", 5, 8), contact=0.3)
    shutter = RRect(cx + 26, top + 62, 258, 86, 8)
    c.paint(shutter, M.chrome, profile=("bevel", 8, 12), shadow=True, contact=0.24)
    c.paint(RRect(cx + 70, top + 62, 74, 46, 5), M.flat("#0d1116"),
            profile=("bevel", 3, 4), contact=0.22)
    c.paint(Capsule(cx - 76, top + 60, cx - 76, top + 60, 9), M.flat("#aeb7c1"),
            profile=("sphere", 7), alpha=0.45)
    # the write-protect slider in its slot, top-left
    c.paint(RRect(cx - 232, top + 62, 64, 46, 6), M.flat("#0b1015"),
            profile=("bevel", 4, 6), contact=0.26)
    c.paint(RRect(cx - 236, top + 62, 44, 32, 4), M.chrome,
            profile=("bevel", 4, 6), contact=0.22)
    # the label well and its paper
    c.paint(RRect(cx - 4, cy + 54, 578, 430, 12), M.flat("#0c1116"),
            profile=("bevel", 8, 12), contact=0.32)
    label = RRect(cx - 4, cy + 50, 552, 402, 6)
    c.paint(Moved(label, 0, 8), M.flat("#8b8272"), profile=("flat",))
    c.paint(label, M.paper, profile=("bevel", 6, 9), shadow=True, contact=0.24)
    c.paint(Capsule(cx - 216, cy - 118, cx + 208, cy - 118, 5),
            M.flat(hsl(hue, 0.55, 0.34)), profile=("bevel", 2, 3), contact=0.15)
    lambda_shape = _lambda_marks(cx - 4, cy + 44, 208, 172, 56)
    c.paint(Moved(lambda_shape, 0, 5), M.flat("#a29a8a"), profile=("bevel", 2, 3))
    c.paint(lambda_shape, M.flat(hsl(hue, 0.60, 0.29)), profile=("bevel", 4, 5),
            contact=0.18)
    for i, width in enumerate((188, 122)):
        c.paint(Capsule(cx - 216, cy + 186 + i * 30, cx - 216 + width, cy + 186 + i * 30,
                        4), M.ink, profile=("bevel", 2, 3), alpha=0.34)
    # the label lifts at its bottom-right corner
    curl = Poly([(cx + 268, cy + 196), (cx + 268, cy + 246), (cx + 214, cy + 246)],
                rounding=5)
    c.paint(Moved(curl, 0, 6), M.flat("#8b8375"), profile=("bevel", 3, 4))
    c.paint(curl, M.paper, profile=("bevel", 5, 8), shadow=True, contact=0.22)
    c.paint_mask(polyline_mask([(cx + 212, cy + 248), (cx + 268, cy + 246)], 4.0),
                 M.ink, emboss=0.8, alpha=0.35)
