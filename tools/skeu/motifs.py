"""Mascots: the creatures the project icons are made of.

A mascot is still a *physical thing* - an enamel penguin, a china sheep, a bronze
gnu bust mounted on walnut, a carved woodpecker, a black-widow spider in polished
gunmetal.  They are sculptures and figurines, not cartoon characters: no faces
with expressions, no emoji eyes, no outlines.

Shared helpers live here too: a tapered ribbon for horns and flippers, a smooth
blob for bodies, and a glass bead for eyes and joints.
"""

from __future__ import annotations

import math

import numpy as np

from . import materials as M
from .paint import Capsule, Circle, Ellipse, Moved, Poly, RRect, Rotated, ring
from .objects import CX, CY, mark

__all__ = ["spider", "penguin", "sheep", "gnu", "woodpecker", "ribbon", "blob", "bead"]


# --------------------------------------------------------------------------- #
# geometry helpers
# --------------------------------------------------------------------------- #

def ribbon(points, widths, rounding: float = 2.0) -> Poly:
    """A tapered strip along ``points`` (the widths are full widths)."""
    pts = np.array(points, dtype=float)
    half = np.array(widths, dtype=float) / 2.0
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for i, point in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == len(pts) - 1:
            d = pts[-1] - pts[-2]
        else:
            d = pts[i + 1] - pts[i - 1]
        d = d / max(1e-6, float(np.hypot(*d)))
        n = np.array([-d[1], d[0]])
        left.append(tuple(point + n * half[i]))
        right.append(tuple(point - n * half[i]))
    return Poly(left + right[::-1], rounding=rounding)


def blob(cx: float, cy: float, radius, squash: float = 1.0, n: int = 96) -> Poly:
    """A smooth closed body; ``radius`` is a callable of the angle in radians."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = radius(a) if callable(radius) else float(radius)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * squash))
    return Poly(pts, rounding=2)


def bead(c, x: float, y: float, r: float, material=None, hue: float = 210) -> None:
    """A dark glossy bead: an eye, a joint, a rivet head."""
    c.paint(Moved(Circle(x, y, r), 0, 2), M.flat("#20242b"), profile=("bevel", 2, 3),
            alpha=0.55)
    c.paint(Circle(x, y, r), material or M.optic, profile=("sphere", r * 0.9),
            hue=hue, contact=0.25)
    c.paint(Circle(x - r * 0.32, y - r * 0.36, r * 0.26), M.flat("#ffffff"),
            profile=("sphere", r * 0.2), alpha=0.85)


# --------------------------------------------------------------------------- #
# araneola - the crawler
# --------------------------------------------------------------------------- #

def spider(c, hue: float = 4, cy: float = CY) -> None:
    """A black-widow spider in polished gunmetal, hourglass in red enamel."""
    cx = CX
    # eight jointed legs radiating from the cephalothorax, knees held high
    for side in (-1, 1):
        for root_x, root_y, knee_x, knee_y, foot_x, foot_y in (
                (-150, -52, -300, -250, -470, -150),
                (-172, -14, -382, -152, -512, 10),
                (-176, 26, -378, 156, -500, 268),
                (-152, 68, -292, 268, -436, 356)):
            root = (cx + side * root_x, cy + root_y)
            knee = (cx + side * knee_x, cy + knee_y)
            foot = (cx + side * foot_x, cy + foot_y)
            c.paint(ribbon([root, knee, foot], (50, 26, 9)), M.gunmetal,
                    profile=("sphere", 16), shadow=True, contact=0.14)
            c.paint(Circle(knee[0], knee[1], 25), M.steel, profile=("sphere", 18),
                    contact=0.22)
            c.paint(Circle(foot[0], foot[1], 13), M.steel, profile=("sphere", 9),
                    contact=0.2)
    abdomen = blob(cx + 78, cy + 6, lambda a: 204 + 30 * math.cos(a * 2 + 0.6), 0.84)
    c.paint(Moved(abdomen, 0, 24), M.flat("#0c0e12"), profile=("sphere", 110))
    c.paint(abdomen, M.gunmetal, profile=("sphere", 170), shadow=True, contact=0.32)
    mark_hourglass(c, cx + 78, cy + 20, 168, hue)
    c.paint(Ellipse(cx + 30, cy - 92, 66, 44), M.flat("#ffffff"),
            profile=("sphere", 34), alpha=0.20)
    c.paint(Circle(cx - 118, cy + 4, 142), M.steel, profile=("sphere", 110),
            shadow=True, contact=0.34)
    c.paint(Ellipse(cx - 118, cy + 30, 124, 104), M.gunmetal, profile=("sphere", 74),
            contact=0.26)
    for dx, dy, r in ((-46, -38, 16), (-6, -44, 12), (-74, -14, 9), (-22, -12, 8)):
        for sx in (-1, 1):
            bead(c, cx - 118 + sx * abs(dx), cy + dy, r, hue=hue)
    for side in (-1, 1):
        c.paint(ribbon([(cx - 142 + side * 30, cy + 112),
                        (cx - 138 + side * 44, cy + 176)], (26, 6)),
                M.steel, profile=("sphere", 9), contact=0.2)


def mark_hourglass(c, cx: float, cy: float, size: float, hue: float = 4) -> None:
    """A red enamel hourglass, painted into the abdomen rather than printed."""
    w, h = size * 0.46, size * 1.02
    top = Poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
                (cx + 5, cy - 3), (cx - 5, cy - 3)], rounding=3)
    bottom = Poly([(cx - 5, cy + 3), (cx + 5, cy + 3),
                   (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], rounding=3)
    for part in (top, bottom):
        c.paint(Moved(part, 2, 4), M.flat("#3a0808"), profile=("bevel", 3, 4),
                alpha=0.55)
        c.paint(part, M.enamel, profile=("bevel", 6, 9), hue=hue, sat=0.80,
                light=0.42, contact=0.18)


# --------------------------------------------------------------------------- #
# heks-linux - the penguin
# --------------------------------------------------------------------------- #

def penguin(c, hue: float = 30, cy: float = CY) -> None:
    """A glazed penguin figurine: black back, china-white front, orange bill."""
    cx = CX
    for side in (-1, 1):
        foot = Rotated(Ellipse(cx + side * 112, cy + 306, 94, 40), side * 9,
                       cx + side * 112, cy + 306)
        c.paint(Moved(foot, 0, 12), M.flat("#5c2c07"), profile=("bevel", 6, 9))
        c.paint(foot, M.enamel, profile=("sphere", 26), hue=hue, sat=0.76, light=0.52,
                shadow=True, contact=0.22)
        for toe in (-1, 0, 1):
            c.paint(Capsule(cx + side * 112 + toe * 32, cy + 310,
                            cx + side * 112 + toe * 62, cy + 326, 8),
                    M.enamel, profile=("sphere", 7), hue=hue, sat=0.70, light=0.50)

    body = blob(cx, cy + 16, lambda a: 252 + 44 * math.cos(a * 2 + math.pi), 1.02)
    c.paint(Moved(body, 0, 26), M.flat("#08090c"), profile=("sphere", 130))
    c.paint(body, M.gunmetal, profile=("sphere", 250), shadow=True, contact=0.30)
    # the white front: narrow at the chin, wide at the feet
    front = blob(cx, cy + 96, lambda a: 174 + 24 * math.cos(a * 2 + math.pi), 1.04)
    c.paint(Moved(front, 0, 4), M.flat("#2a2f36"), profile=("sphere", 90), alpha=0.45)
    c.paint(front, M.ceramic, profile=("sphere", 220), sat=0.03, contact=0.18)
    # head: black, two small eyes with a glass catchlight
    for side in (-1, 1):
        bead(c, cx + side * 46, cy - 188, 15)
        c.paint(Circle(cx + side * 46, cy - 196, 24), M.flat("#ffffff"),
                profile=("sphere", 16), alpha=0.10)
    # bill: a short orange wedge, the one warm accent
    bill = Poly([(cx - 38, cy - 148), (cx + 38, cy - 148), (cx + 30, cy - 84),
                 (cx - 30, cy - 84)], rounding=14)
    c.paint(Moved(bill, 0, 6), M.flat("#5c2c07"), profile=("bevel", 4, 6))
    c.paint(bill, M.enamel, profile=("sphere", 46), hue=hue, sat=0.82, light=0.52,
            shadow=True, contact=0.24)
    c.paint(Capsule(cx - 18, cy - 112, cx + 18, cy - 112, 4), M.flat("#7a3a06"),
            profile=("bevel", 2, 2), alpha=0.4)
    # flippers, held against the body
    for side in (-1, 1):
        flip = ribbon([(cx + side * 194, cy - 150), (cx + side * 252, cy + 20),
                       (cx + side * 218, cy + 186)], (86, 58, 18))
        c.paint(Moved(flip, 0, 8), M.flat("#08090c"), profile=("bevel", 8, 12))
        c.paint(flip, M.gunmetal, profile=("sphere", 80), shadow=True, contact=0.20)
        c.paint(ribbon([(cx + side * 216, cy - 110), (cx + side * 244, cy + 26),
                        (cx + side * 222, cy + 132)], (14, 9, 4)),
                M.flat("#ffffff"), profile=("bevel", 2, 3), alpha=0.16)
    # a soft sheen down the back
    c.paint(Ellipse(cx - 104, cy - 236, 58, 40), M.flat("#ffffff"),
            profile=("sphere", 34), alpha=0.12)


# --------------------------------------------------------------------------- #
# lambdock - the sheep
# --------------------------------------------------------------------------- #

def sheep(c, hue: float = 206, cy: float = CY) -> None:
    """A plush sheep: a fleece of round curls, a charcoal face, a brass bell.

    The fleece is one union of circles rather than a lumpy polygon, so the
    silhouette is woolly but never spiky; the face is a proper sheep face with
    two ears, a forelock and a muzzle that reaches left, and the four legs are
    stout enough to read at 16 px.
    """
    cx = CX
    # legs: four stout tapered limbs with hooves, behind and in front of the body
    for dx, dy, w in ((-118, 182, 44), (-44, 206, 42), (128, 202, 42), (206, 176, 44)):
        c.paint(Capsule(cx + dx, cy + dy - 30, cx + dx + (8 if dx > 0 else -6),
                        cy + dy + 72, w), M.gunmetal, profile=("sphere", 24),
                shadow=True, contact=0.2)
        c.paint(Ellipse(cx + dx + (4 if dx > 0 else -2), cy + dy + 78, w * 0.92, 24),
                M.flat("#101317"), profile=("bevel", 5, 7), contact=0.22)
    # fleece: a union of curls, one shape so no seams show between the lobes
    fleece = (Circle(cx - 120, cy + 60, 118) | Circle(cx - 10, cy + 96, 108) |
              Circle(cx + 120, cy + 66, 112) | Circle(cx + 178, cy - 30, 102) |
              Circle(cx + 70, cy - 96, 128) | Circle(cx - 70, cy - 78, 126) |
              Circle(cx - 168, cy - 6, 104) | Circle(cx + 216, cy + 86, 74) |
              Circle(cx - 222, cy + 90, 70))
    c.paint(Moved(fleece, 0, 30), M.flat("#8b8577"), profile=("sphere", 80))
    c.paint(fleece, M.ceramic, profile=("sphere", 200), sat=0.03, light=0.96,
            shadow=True, contact=0.30)
    # curls: shallow engraved arcs, the wool's only detail
    for dx, dy, r, rot in ((-90, -60, 44, 30), (44, -104, 52, -20), (150, -18, 42, 50),
                           (10, 40, 46, 10), (-160, 44, 40, -40), (110, 96, 36, 20)):
        c.paint(Rotated(ring(cx + dx, cy + dy, r, 7), rot, cx + dx, cy + dy),
                M.engraved, profile=("bevel", 3, 4), alpha=0.16)
    c.paint(Ellipse(cx - 74, cy - 128, 104, 52), M.flat("#ffffff"),
            profile=("sphere", 40), alpha=0.28)
    # neck, head and muzzle, facing left
    neck = Capsule(cx - 196, cy - 30, cx - 122, cy + 40, 80)
    c.paint(neck, M.enamel, profile=("sphere", 40), hue=26, sat=0.16, light=0.30,
            shadow=True, contact=0.22)
    head = Circle(cx - 268, cy - 62, 90)
    c.paint(Moved(head, 0, 12), M.flat("#0b0c10"), profile=("sphere", 50))
    c.paint(head, M.enamel, profile=("sphere", 90), hue=26, sat=0.16, light=0.30,
            shadow=True, contact=0.26)
    muzzle = Poly([(cx - 292, cy - 116), (cx - 356, cy - 74), (cx - 372, cy - 12),
                   (cx - 340, cy + 22), (cx - 272, cy + 6), (cx - 252, cy - 66)],
                  rounding=34)
    c.paint(Moved(muzzle, 0, 10), M.flat("#0b0c10"), profile=("bevel", 6, 9))
    c.paint(muzzle, M.enamel, profile=("sphere", 54), hue=26, sat=0.18, light=0.38,
            shadow=True, contact=0.22)
    # ears: one up, one back
    ear_l = Rotated(Ellipse(cx - 296, cy - 148, 66, 28), -22, cx - 296, cy - 148)
    c.paint(Moved(ear_l, 0, 8), M.flat("#08090c"), profile=("bevel", 5, 8))
    c.paint(ear_l, M.enamel, profile=("sphere", 28), hue=26, sat=0.18, light=0.32,
            shadow=True, contact=0.22)
    ear_r = Rotated(Ellipse(cx - 196, cy - 150, 58, 24), 26, cx - 196, cy - 150)
    c.paint(ear_r, M.enamel, profile=("sphere", 24), hue=26, sat=0.18, light=0.30,
            shadow=True, contact=0.22)
    # a white forelock over the brow, and the eyes
    tuft = (Circle(cx - 306, cy - 126, 34) | Circle(cx - 268, cy - 146, 38) |
            Circle(cx - 230, cy - 128, 32) | Circle(cx - 286, cy - 156, 30))
    c.paint(tuft, M.ceramic, profile=("sphere", 60), sat=0.03, light=0.96,
            shadow=True, contact=0.2)
    bead(c, cx - 322, cy - 56, 13)
    bead(c, cx - 258, cy - 66, 12)
    c.paint(Capsule(cx - 348, cy + 6, cx - 314, cy + 12, 5), M.flat("#000000"),
            profile=("bevel", 2, 2), alpha=0.42)
    bead(c, cx - 336, cy - 4, 6)
    # brass bell on a leather collar
    c.paint(Capsule(cx - 160, cy + 34, cx - 96, cy + 74, 16), M.leather,
            profile=("bevel", 5, 7), hue=30, sat=0.45, light=0.28, contact=0.22)
    c.paint(Circle(cx - 120, cy + 104, 40), M.brass, profile=("sphere", 32),
            shadow=True, contact=0.28)
    c.paint(ring(cx - 120, cy + 124, 13, 6), M.flat("#3d2a0d"),
            profile=("bevel", 2, 3), alpha=0.5)
    c.paint(Capsule(cx - 120, cy + 68, cx - 120, cy + 80, 7), M.chrome,
            profile=("sphere", 5), contact=0.16)


# --------------------------------------------------------------------------- #
# guix - the gnu
# --------------------------------------------------------------------------- #

def gnu(c, hue: float = 34, cy: float = CY, sealed: bool = False) -> None:
    """A cast-bronze gnu head mounted on a walnut plaque, horns and beard cast."""
    cx = CX
    # shield plaque: brass rim, dark walnut field, pointed foot
    outline = [(cx - 292, cy - 240), (cx + 292, cy - 240), (cx + 292, cy + 54),
               (cx + 264, cy + 146), (cx + 194, cy + 228), (cx + 98, cy + 290),
               (cx, cy + 316), (cx - 98, cy + 290), (cx - 194, cy + 228),
               (cx - 264, cy + 146), (cx - 292, cy + 54)]
    rim = Poly([(cx + (x - cx) * 1.045, cy + (y - cy) * 1.035 + 8) for x, y in outline],
               rounding=16)
    c.paint(Moved(rim, 0, 26), M.flat("#1b120a"), profile=("bevel", 14, 20))
    c.paint(rim, M.brass, profile=("bevel", 18, 28), shadow=True, contact=0.28)
    field = Poly([(cx + (x - cx) * 0.94, cy + (y - cy) * 0.93 + 6) for x, y in outline],
                 rounding=14)
    c.paint(field, M.wood, profile=("bevel", 12, 18), hue=17, sat=0.60, light=0.20,
            contact=0.32)

    # neck and shoulders in bronze
    neck = Poly([(cx - 188, cy + 330), (cx - 150, cy + 40), (cx - 92, cy - 40),
                 (cx + 92, cy - 40), (cx + 150, cy + 40), (cx + 188, cy + 330)],
                rounding=64)
    c.paint(Moved(neck, 0, 18), M.flat("#2c1d0c"), profile=("bevel", 10, 14))
    c.paint(neck, M.brass, profile=("sphere", 90), shadow=True, contact=0.26)

    # long face, narrower muzzle
    head = blob(cx, cy - 132, lambda a: 138 + 30 * math.cos(a * 2), 1.12)
    c.paint(head, M.brass, profile=("sphere", 130), shadow=True, contact=0.30)
    # beard: one cast tuft under the chin, behind the muzzle
    tuft = ribbon([(cx, cy + 54), (cx + 4, cy + 150), (cx, cy + 244)], (78, 58, 10))
    c.paint(Moved(tuft, 0, 10), M.flat("#241708"), profile=("bevel", 6, 9))
    c.paint(tuft, M.brass, profile=("sphere", 30), shadow=True, contact=0.2)
    c.paint(ring(cx, cy + 150, 26, 6), M.engraved, profile=("bevel", 2, 3), alpha=0.25)
    muzzle = RRect(cx, cy + 22, 156, 122, 52)
    c.paint(Moved(muzzle, 0, 10), M.flat("#3a270e"), profile=("bevel", 8, 12))
    c.paint(muzzle, M.brass, profile=("sphere", 74), shadow=True, contact=0.26)
    for side in (-1, 1):
        c.paint(Rotated(Ellipse(cx + side * 40, cy + 24, 12, 22), side * 18,
                        cx + side * 40, cy + 24), M.flat("#20160a"),
                profile=("sphere", 10), contact=0.2)
    c.paint(Capsule(cx - 34, cy + 74, cx + 34, cy + 74, 4), M.flat("#241708"),
            profile=("bevel", 2, 2), alpha=0.5)
    # ears, drooping under the horns
    for side in (-1, 1):
        ear = Rotated(Ellipse(cx + side * 190, cy - 128, 66, 30), side * 30,
                      cx + side * 190, cy - 128)
        c.paint(Moved(ear, 0, 8), M.flat("#2c1d0c"), profile=("bevel", 5, 8))
        c.paint(ear, M.brass, profile=("sphere", 24), shadow=True, contact=0.24)
    # horns: out, up and back, ridged and tapering to a point
    for side in (-1, 1):
        points = [(cx + side * 88, cy - 192), (cx + side * 196, cy - 262),
                  (cx + side * 250, cy - 356), (cx + side * 214, cy - 442),
                  (cx + side * 150, cy - 470)]
        horn = ribbon(points, (94, 72, 44, 20, 5))
        c.paint(Moved(horn, 0, 10), M.flat("#2c1d0c"), profile=("bevel", 8, 12))
        c.paint(horn, M.brass, profile=("sphere", 44), shadow=True, contact=0.22)
        for t in (0.26, 0.44, 0.60, 0.74):
            px = cx + side * (88 + 166 * t)
            py = cy - 196 - 262 * t + 26 * math.sin(t * 5)
            c.paint(Rotated(ring(px, py, 30 - 18 * t, 5), side * 55, px, py),
                    M.engraved, profile=("bevel", 2, 2), alpha=0.26)
        bead(c, cx + side * 78, cy - 122, 16, M.flat("#1b1206"))
    # nameplate on the plaque's foot
    plate = RRect(cx, cy + 258, 214, 56, 8)
    c.paint(Moved(plate, 0, 6), M.flat("#2a1c11"), profile=("bevel", 4, 6))
    c.paint(plate, M.brass, profile=("bevel", 8, 12), shadow=True, contact=0.24)
    for i in range(7):
        c.paint(Capsule(cx - 68 + i * 22, cy + 258, cx - 56 + i * 22, cy + 258, 4),
                M.engraved, profile=("bevel", 2, 2), alpha=0.45)

    if sealed:
        rib = Poly([(cx - 130, cy + 296), (cx + 130, cy + 296), (cx + 118, cy + 344),
                    (cx, cy + 380), (cx - 118, cy + 344)], rounding=6)
        c.paint(rib, M.enamel, profile=("bevel", 5, 8), hue=hue, sat=0.62, light=0.46,
                shadow=True, contact=0.2)
        c.paint(Circle(cx, cy + 344, 48), M.enamel, profile=("sphere", 36), hue=hue,
                sat=0.72, light=0.44, shadow=True, contact=0.3)
        mark(c, "check", cx, cy + 344, 48, M.brass, emboss=2.0)


# --------------------------------------------------------------------------- #
# byggsteg-woodpecker - the CI bird
# --------------------------------------------------------------------------- #

def woodpecker(c, hue: float = 4, cy: float = CY) -> None:
    """A carved woodpecker on a branch: cream body, black wing, red crest."""
    cx = CX
    branch = Capsule(cx + 30, cy + 296, cx + 352, cy + 240, 30)
    c.paint(Moved(branch, 0, 14), M.flat("#3a2412"), profile=("bevel", 8, 12))
    c.paint(branch, M.wood, profile=("sphere", 26), shadow=True, contact=0.24)
    branch2 = Capsule(cx - 300, cy + 252, cx + 56, cy + 302, 24)
    c.paint(branch2, M.wood, profile=("sphere", 22), shadow=True, contact=0.2)

    tail = ribbon([(cx + 118, cy + 184), (cx + 224, cy + 258), (cx + 272, cy + 288)],
                  (70, 48, 18))
    c.paint(tail, M.flat("#16181c"), profile=("sphere", 22), shadow=True, contact=0.2)
    c.paint(ribbon([(cx + 150, cy + 206), (cx + 218, cy + 252)], (12, 5)),
            M.flat("#e8e2d0"), profile=("bevel", 2, 3), alpha=0.30)
    for dx in (-44, 26):
        c.paint(Capsule(cx + dx, cy + 240, cx + dx + 6, cy + 292, 11),
                M.gunmetal, profile=("sphere", 9), contact=0.2)
        for toe in (-1, 1):
            c.paint(Capsule(cx + dx + 6, cy + 290, cx + dx + 6 + toe * 32, cy + 304, 8),
                    M.gunmetal, profile=("sphere", 7), contact=0.2)
    body = blob(cx, cy + 40, lambda a: 150 + 32 * math.cos(a * 2 - 0.4), 1.30)
    c.paint(Moved(body, 0, 20), M.flat("#3c2f22"), profile=("sphere", 60))
    c.paint(body, M.enamel, profile=("sphere", 150), hue=44, sat=0.24, light=0.80,
            shadow=True, contact=0.26)
    belly = blob(cx - 42, cy + 98, lambda a: 84 + 14 * math.cos(a * 2), 1.24)
    c.paint(belly, M.ceramic, profile=("sphere", 90), sat=0.03, contact=0.15)
    wing = Rotated(Ellipse(cx + 76, cy + 24, 60, 138), 14, cx + 76, cy + 24)
    c.paint(Moved(wing, 0, 6), M.flat("#0d0f13"), profile=("sphere", 50))
    c.paint(wing, M.gunmetal, profile=("sphere", 64), shadow=True, contact=0.22)
    c.paint(Capsule(cx + 50, cy - 46, cx + 86, cy + 90, 8), M.flat("#e8e2d0"),
            profile=("bevel", 2, 3), alpha=0.60)
    head = Circle(cx - 110, cy - 148, 112)
    c.paint(Moved(head, 0, 10), M.flat("#3c2f22"), profile=("sphere", 50))
    c.paint(head, M.enamel, profile=("sphere", 100), hue=44, sat=0.22, light=0.80,
            shadow=True, contact=0.26)
    crest = ribbon([(cx - 152, cy - 240), (cx - 214, cy - 286), (cx - 176, cy - 322),
                    (cx - 96, cy - 292), (cx - 62, cy - 246)], (48, 40, 26, 30, 44))
    c.paint(Moved(crest, 0, 6), M.flat("#5c0a0a"), profile=("sphere", 16))
    c.paint(crest, M.enamel, profile=("sphere", 24), hue=hue, sat=0.82, light=0.46,
            shadow=True, contact=0.2)
    c.paint(RRect(cx - 116, cy - 202, 112, 66, 18), M.gunmetal,
            profile=("sphere", 28), contact=0.18)
    bead(c, cx - 142, cy - 176, 15)
    bead(c, cx - 82, cy - 176, 13)
    bill = ribbon([(cx - 214, cy - 160), (cx - 292, cy - 130)], (46, 10))
    c.paint(Moved(bill, 0, 5), M.flat("#2a2622"), profile=("bevel", 5, 8))
    c.paint(bill, M.steel, profile=("sphere", 16), shadow=True, contact=0.22)
    c.paint(Capsule(cx - 240, cy - 154, cx - 286, cy - 132, 4), M.flat("#0f1114"),
            profile=("bevel", 1.5, 2), alpha=0.5)
    for dx, dy, rot in ((-252, 296, 20), (-216, 310, -12), (-270, 322, 8)):
        c.paint(Rotated(RRect(cx + dx, cy + dy, 54, 12, 6), rot, cx + dx, cy + dy),
                M.wood, profile=("bevel", 2, 3), hue=40, sat=0.30, light=0.70,
                contact=0.1)
