"""The stationery, tools and instruments: books, sheets, crates, dials, lamps.

These are the objects a desktop icon set spends most of its time on, and they
carry the pack's material story: paper with a fold, leather with a seam, wood
with grain, brass with a patina.  Same canvas and materials as ``objects``.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from . import materials as M
from .objects import (CX, CY, _mask_of, _scaled_mask, dots_mask, glow, grid_mask, mark,
                      radial_ticks, rivet, screw, stitch_mask, stripe_mask)
from .paint import (SIZE, Capsule, Circle, Ellipse, Moved, Poly, RRect, Rotated, blur, clamp01,
                    gear_polygon, hsl, polyline_mask, ring)
from .pictograms import glyph_mask


# --------------------------------------------------------------------------- #
# paper and print
# --------------------------------------------------------------------------- #

def _text_lines(c, box, count: int, width: float = 4.0, ink=None, ragged: bool = True,
                inset: float = 0.0) -> None:
    x0, y0, x1, y1 = box
    mask = np.zeros((SIZE, SIZE), dtype=np.float32)
    img, draw, s = _scaled_mask()
    step = (y1 - y0) / max(1, count)
    for i in range(count):
        y = y0 + step * (i + 0.6)
        end = x1 - (0.0 if not ragged or i % 3 else (x1 - x0) * 0.22)
        draw.line([((x0 + inset) * s, y * s), (end * s, y * s)], fill=255,
                  width=max(1, int(width * s)))
    mask = _mask_of(img, s)
    c.paint_mask(mask, ink or M.ink, emboss=0.8, alpha=0.62)


def _photo(c, box, hue: float = 210) -> None:
    x0, y0, x1, y1 = box
    c.paint(RRect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 6), M.flat("#2c3138"),
            profile=("bevel", 3, 4))
    c.paint(Ellipse((x0 + x1) / 2, (y0 + y1) / 2 + 8, (x1 - x0) * 0.34, (y1 - y0) * 0.30),
            M.enamel, profile=("sphere", 30), hue=hue, sat=0.35, light=0.55)


def documents(c, hue: float = 45, cy: float = CY) -> None:
    """A small pile of printed sheets with a chrome clip: the office category."""
    cx = CX
    back = Rotated(RRect(cx + 30, cy - 10, 470, 620, 8), 6, cx, cy)
    c.paint(back, M.paper, profile=("flat",), shadow=True, contact=0.15)
    _text_lines(c, (cx - 120, cy - 220, cx + 220, cy + 180), 8, 4.0)
    front = Rotated(RRect(cx - 40, cy + 20, 470, 620, 8), -5, cx, cy)
    c.paint(front, M.paper, profile=("flat",), shadow=True, contact=0.2)
    _text_lines(c, (cx - 240, cy - 190, cx + 120, cy + 220), 9, 4.4)
    c.paint(RRect(cx - 230, cy - 250, 90, 120, 8), M.paper, profile=("flat",),
            contact=0.1)
    clip = polyline_mask([(cx - 250, cy - 190), (cx - 200, cy - 290),
                          (cx - 120, cy - 270), (cx - 118, cy - 160),
                          (cx - 160, cy - 140)], 12.0)
    c.paint_mask(clip, M.chrome, emboss=4.0)
    # one enamel filing tab on the front sheet: the accent that tells two
    # offices apart without touching the paper.
    c.paint(Rotated(RRect(cx - 196, cy + 66, 56, 168, 10), -5, cx, cy), M.enamel,
            profile=("bevel", 6, 9), hue=hue, sat=0.66, light=0.48,
            shadow=True, contact=0.18)


def paper(c, hue: float = 45, printed: str = "lines", fold: bool = True, w: float = 520,
          h: float = 680, cy: float = CY, clip: bool = False, torn: bool = False) -> None:
    """A document sheet: white page, dog-ear fold, printed content."""
    cx = CX
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    sheet = RRect(cx, cy, w, h, 8)
    c.paint(Moved(sheet, 6, 14), M.paper, profile=("flat",), contact=0.1)
    c.paint(sheet, M.paper, profile=("flat",), shadow=True, contact=0.18)
    if fold:
        size = w * 0.17
        c.paint(Poly([(x1 - size, y0), (x1, y0 + size), (x1 - size, y0 + size)]),
                M.paper, profile=("flat",))
    if printed == "lines":
        _text_lines(c, (x0 + 54, y0 + 120, x1 - 54, y1 - 70), 11, 5.0)
        c.paint(Capsule(cx - 150, y0 + 82, cx + 90, y0 + 82, 6), M.flat("#3c3f45"), alpha=0.5)
    elif printed == "columns":
        _text_lines(c, (x0 + 44, y0 + 150, cx - 24, y1 - 60), 14, 3.6)
        _text_lines(c, (cx + 24, y0 + 150, x1 - 44, y1 - 60), 14, 3.6)
        c.paint(RRect(cx, y0 + 78, w * 0.72, 34, 4), M.flat("#2f333a"),
                profile=("bevel", 2, 3), alpha=0.8)
        _photo(c, (x0 + 44, y0 + 100, x1 - 44, y0 + 132), hue=hue)
    elif printed == "portrait":
        _photo(c, (cx - 120, y0 + 96, cx + 120, y0 + 330), hue=hue)
        _text_lines(c, (cx - 160, y0 + 360, cx + 160, y0 + 560), 6, 4.4)
    elif printed == "ui":
        c.paint(RRect(cx, y0 + 60, w * 0.8, 26, 6), M.flat("#3a3e46"), profile=("bevel", 2, 3))
        for i in range(3):
            c.paint(RRect(cx, y0 + 118 + i * 92, w * 0.74, 74, 8),
                    M.enamel, profile=("bevel", 4, 6), hue=(hue + i * 30) % 360,
                    sat=0.25, light=0.62)
    elif printed == "swatches":
        for i in range(3):
            for j in range(3):
                c.paint(RRect(cx - 120 + i * 120, y0 + 150 + j * 120, 92, 92, 8),
                        M.enamel, profile=("bevel", 5, 7), hue=(hue + i * 40 + j * 18) % 360,
                        sat=0.55, light=0.52)
    elif printed == "map":
        _map_print(c, (x0 + 36, y0 + 96, x1 - 36, y1 - 48), hue=hue)
    if clip:
        clip_path = [((x0 + w * 0.30, y0), (x0 + w * 0.30, y0 + 96), (x0 + w * 0.42, y0 + 78),
                      (x0 + w * 0.42, y0 + 20), (x0 + w * 0.31, y0 + 6))]
        wire = polyline_mask([(x0 + w * 0.30, y0 + 20), (x0 + w * 0.36, y0 - 10),
                              (x0 + w * 0.44, y0 + 6), (x0 + w * 0.44, y0 + 92),
                              (x0 + w * 0.40, y0 + 108)], 9.0)
        c.paint_mask(wire, M.chrome, emboss=3.0)


def _map_print(c, box, hue: float = 150) -> None:
    """A printed map: land, water, roads, a red route and a pin.

    The two ground colours are mixed from ``hue`` - a green map, a blue one and
    a sepia one are the same print, and a map of a different country should not
    be the same sheet of paper.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    c.paint(RRect((x0 + x1) / 2, (y0 + y1) / 2, w, h, 4), M.paper,
            profile=("flat",), warm=0.2)
    land = Poly([(x0, y0 + h * 0.10), (x0 + w * 0.42, y0 + h * 0.02),
                 (x0 + w * 0.62, y0 + h * 0.26), (x0 + w, y0 + h * 0.18),
                 (x1, y1), (x0 + w * 0.30, y1), (x0 + w * 0.18, y0 + h * 0.62),
                 (x0, y0 + h * 0.58)], rounding=6)
    c.paint(land, lambda ctx, **k: M.flat(tuple(hsl(hue, 0.16, 0.90)))(ctx, **k),
            profile=("flat",), alpha=0.92)
    water = Poly([(x0 + w * 0.44, y0 + h * 0.02), (x0 + w * 0.70, y0 - h * 0.02),
                  (x1 + 20, y0 - 20), (x1 + 20, y0 + h * 0.20),
                  (x0 + w * 0.66, y0 + h * 0.30)], rounding=8)
    c.paint(water & RRect((x0 + x1) / 2, (y0 + y1) / 2, w, h, 3),
            lambda ctx, **k: M.flat(tuple(hsl((hue + 180) % 360, 0.30, 0.76)))(ctx, **k),
            profile=("flat",), alpha=0.88)
    # roads, then the route in the one accent
    c.paint_mask(polyline_mask([(x0 + 20, y0 + h * 0.78), (x0 + w * 0.34, y0 + h * 0.60),
                                (x0 + w * 0.58, y0 + h * 0.72), (x1 - 24, y0 + h * 0.54)],
                               6.0), M.flat("#b0a894"), emboss=0.8, alpha=0.85)
    c.paint_mask(polyline_mask([(x0 + w * 0.24, y1 - 10), (x0 + w * 0.36, y0 + h * 0.48),
                                (x0 + w * 0.62, y0 + h * 0.34)], 4.5),
                 M.flat("#c3bbaa"), emboss=0.6, alpha=0.8)
    route = [(x0 + w * 0.10, y0 + h * 0.86), (x0 + w * 0.28, y0 + h * 0.66),
             (x0 + w * 0.52, y0 + h * 0.76), (x0 + w * 0.74, y0 + h * 0.52)]
    c.paint_mask(polyline_mask(route, 7.0), M.flat("#c04a3e"), emboss=1.0, alpha=0.9)
    c.paint(Circle(route[-1][0], route[-1][1], 15), M.enamel, profile=("sphere", 11),
            hue=6, sat=0.7, light=0.46, shadow=True, contact=0.2)
    c.paint(Circle(route[-1][0], route[-1][1], 5), M.flat("#ffffff"), profile=("flat",),
            alpha=0.85)
    # a small printed compass rose in the corner
    cx, cy = x0 + w - 54, y0 + 58
    for i in range(4):
        a = math.radians(i * 90)
        tip = (cx + 28 * math.cos(a), cy + 28 * math.sin(a))
        left = (cx + 9 * math.cos(a + math.pi / 2), cy + 9 * math.sin(a + math.pi / 2))
        right = (cx + 9 * math.cos(a - math.pi / 2), cy + 9 * math.sin(a - math.pi / 2))
        c.paint(Poly([tip, left, right], rounding=2), M.flat("#7d7566"),
                profile=("flat",), alpha=0.8)
    c.paint_mask(stripe_mask((x0 + 10, y1 - 26, x1 - 10, y1 - 20), 1, 3.0),
                 M.flat("#8c8474"), emboss=0.6, alpha=0.35)


def newspaper(c, hue: float = 205, cy: float = CY) -> None:
    paper(c, hue=hue, printed="columns", w=560, h=700, cy=cy, fold=False)
    # the fold across the middle, and the masthead
    c.paint(Capsule(CX - 260, cy - 20, CX + 260, cy - 20, 3), M.flat("#c9c4b8"),
            profile=("bevel", 1.5, 2), alpha=0.9)
    c.paint(RRect(CX, cy + 320, 520, 90, 6), M.paper, profile=("flat",),
            shadow=True, contact=0.15)


def blueprint(c, hue: float = 215, cy: float = CY) -> None:
    """A rolled plan, an unrolled sheet and a red pencil."""
    cx = CX
    sheet = Rotated(RRect(cx - 30, cy + 20, 520, 620, 6), -4, cx, cy)
    c.paint(sheet, M.paper, profile=("flat",), shadow=True, contact=0.2)
    for i, width in enumerate((420, 380, 400, 300)):
        y = cy - 200 + i * 96
        c.paint(Capsule(cx - 30, y, cx - 30 + width, y, 3), M.flat("#3f6fa8"),
                emboss=0.8, alpha=0.55)
    c.paint(RRect(cx - 160, cy - 250, 200, 130, 4), M.flat("#dfeaf6"),
            profile=("bevel", 2, 3), alpha=0.8)
    roll = Capsule(cx + 210, cy - 250, cx + 210, cy + 250, 74)
    c.paint(Moved(roll, 0, 14), M.paper, profile=("bevel", 10, 14))
    c.paint(roll, M.paper, profile=("bevel", 22, 30), shadow=True, contact=0.2)
    c.paint(Ellipse(cx + 210, cy - 250, 74, 22), M.enamel, profile=("bevel", 6, 9),
            hue=hue, sat=0.5, light=0.5, contact=0.2)
    pencil = Rotated(Capsule(cx + 320, cy + 150, cx + 400, cy - 40, 17), 14, cx + 360, cy + 50)
    c.paint(pencil, M.enamel, profile=("bevel", 6, 8), hue=6, sat=0.6, light=0.46,
            shadow=True, contact=0.2)


# --------------------------------------------------------------------------- #
# books and stationery
# --------------------------------------------------------------------------- #

def book(c, hue: float = 28, glyph: str = "note", cy: float = CY, sat: float = 0.42,
         light: float = 0.27, bands: bool = True) -> None:
    cx = CX
    pages = RRect(cx + 26, cy + 12, w := 420, 520, 10)
    c.paint(Moved(pages, 0, 10), M.paper, profile=("flat",), shadow=True, contact=0.2)
    cover = RRect(cx - 20, cy, 450, 552, 24)
    c.paint(Moved(cover, 0, 24), M.leather, profile=("bevel", 10, 14), hue=hue, sat=sat,
            light=light)
    c.paint(cover, M.leather, profile=("bevel", 16, 22), hue=hue, sat=sat, light=light,
            shadow=True, contact=0.24)
    spine = RRect(cx - 168, cy, 66, 540, 14)
    c.paint(spine, M.leather, profile=("bevel", 8, 12), hue=hue, sat=sat * 1.1,
            light=max(0.1, light - 0.05), contact=0.3)
    if bands:
        for dy in (-214, 214):
            c.paint(Capsule(cx - 200, cy + dy, cx - 136, cy + dy, 5), M.brass,
                    profile=("bevel", 3, 4), contact=0.2)
    seam = stitch_mask([(cx + 186, cy - 240), (cx + 186, cy + 240)], 18, 13, 4.0)
    c.paint_mask(seam, M.flat("#c8b48b"), emboss=1.6, alpha=0.45)
    mark(c, glyph, cx + 26, cy - 10, 210, M.brass, emboss=3.6)


def journal(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 430, 560, 22)
    c.paint(Moved(body, 0, 24), M.leather, profile=("bevel", 10, 14), hue=hue, sat=0.34,
            light=0.25)
    c.paint(body, M.leather, profile=("bevel", 16, 22), hue=hue, sat=0.34, light=0.27,
            shadow=True, contact=0.24)
    c.paint(RRect(cx + 210, cy, 20, 540, 8), M.paper, profile=("flat",), contact=0.2)
    seam = stitch_mask([(cx - 180, cy - 250), (cx - 180, cy + 250)], 16, 12, 4.0)
    c.paint_mask(seam, M.flat("#c9b68f"), emboss=1.6, alpha=0.4)
    strap = RRect(cx + 108, cy, 26, 566, 8)
    c.paint(strap, M.leather, profile=("bevel", 6, 9), hue=hue, sat=0.30, light=0.18,
            contact=0.25)
    c.paint(RRect(cx + 108, cy - 40, 46, 66, 8), M.brass, profile=("bevel", 4, 6),
            shadow=True, contact=0.2)
    mark(c, "lock", cx, cy - 150, 92, M.brass, emboss=3.0)


def folder(c, hue: float = 38, cy: float = CY) -> None:
    cx = CX
    back = Poly([(cx - 300, cy - 260), (cx + 180, cy - 260), (cx + 290, cy - 160),
                 (cx + 290, cy + 280), (cx - 300, cy + 280)], rounding=14)
    c.paint(Moved(back, 0, 14), M.enamel, profile=("bevel", 8, 12), hue=hue, sat=0.45,
            light=0.42)
    c.paint(back, M.enamel, profile=("bevel", 10, 14), hue=hue, sat=0.5, light=0.55,
            shadow=True, contact=0.2)
    for i, off in enumerate((-16, 4, 24)):
        page = Rotated(RRect(cx + 10, cy - 30 + off, 430, 470, 6), (i - 1) * 2.0, cx, cy - 30)
        c.paint(page, M.paper, profile=("flat",), contact=0.12)
    front = Poly([(cx - 290, cy + 40), (cx + 200, cy + 40), (cx + 292, cy - 60),
                  (cx + 292, cy + 280), (cx - 290, cy + 280)], rounding=12)
    c.paint(front, M.enamel, profile=("bevel", 10, 14), hue=hue, sat=0.52, light=0.60,
            contact=0.2)
    c.paint(Capsule(cx - 250, cy + 70, cx + 240, cy + 70, 3), M.flat("#8a6a2f"),
            profile=("bevel", 2, 2), alpha=0.5)


def cards(c, hue: float = 32, cy: float = CY) -> None:
    """A stack of ruled index cards in a walnut holder (kanban, reminders)."""
    cx = CX
    holder = Poly([(cx - 300, cy + 120), (cx + 300, cy + 120), (cx + 260, cy + 300),
                   (cx - 260, cy + 300)], rounding=18)
    c.paint(Moved(holder, 0, 16), M.wood, profile=("bevel", 10, 14))
    c.paint(holder, M.wood, profile=("bevel", 16, 22), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 120, 600, 40, 12), M.wood, profile=("bevel", 8, 12),
            contact=0.25)
    for i in range(4):
        card = RRect(cx + (i % 2) * 6, cy + 20 - i * 34, 470, 280, 10)
        c.paint(Moved(card, 0, 8), M.paper, profile=("flat",), contact=0.12)
        c.paint(card, M.paper, profile=("flat",), contact=0.14)
    c.paint(Capsule(cx, cy - 40, cx, cy - 160, 4), M.flat("#c8443c"),
            profile=("bevel", 2, 3), alpha=0.8)
    for j in range(3):
        c.paint(Capsule(cx - 170, cy - 60 + j * 34, cx + 170 - j * 40, cy - 60 + j * 34, 4),
                M.flat("#4a4f57"), emboss=0.8, alpha=0.5)
    c.paint(RRect(cx + 130, cy - 150, 60, 26, 6), M.enamel, profile=("bevel", 3, 4),
            hue=hue, sat=0.6, light=0.5, contact=0.15)


def bookmark(c, hue: float = 200, cy: float = CY) -> None:
    cx = CX
    ribbon = RRect(cx, cy - 20, 150, 640, 12)
    c.paint(Moved(ribbon, 0, 12), M.leather, profile=("bevel", 6, 9), hue=hue, sat=0.4,
            light=0.22)
    c.paint(ribbon, M.leather, profile=("bevel", 10, 14), hue=hue, sat=0.42, light=0.26,
            shadow=True, contact=0.2)
    c.paint(Circle(cx, cy - 250, 24), M.brass, profile=("sphere", 18), contact=0.25)
    for i in range(5):
        x = cx - 40 + i * 20
        tassel = Capsule(x, cy + 300, x + (i - 2) * 6, cy + 390, 7)
        c.paint(tassel, M.leather, profile=("bevel", 4, 5), hue=45, sat=0.5, light=0.45)
    mark(c, "star", cx, cy + 40, 84, M.brass, emboss=2.6)


def crate(c, hue: float = 26, sealed: bool = False, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 600, 480, 18)
    c.paint(Moved(body, 0, 26), M.wood, profile=("bevel", 10, 14), hue=hue)
    c.paint(body, M.wood, profile=("bevel", 16, 22), hue=hue, shadow=True, contact=0.22)
    for y in (cy - 150, cy - 50, cy + 50, cy + 150):
        c.paint(Capsule(cx - 280, y, cx + 280, y, 3.5), M.flat("#3a2410"),
                profile=("bevel", 2, 2), alpha=0.55)
    for x in (cx - 200, cx + 200):
        band = RRect(x, cy, 46, 500, 6)
        c.paint(band, M.steel, profile=("bevel", 6, 8), contact=0.3)
        for y in (cy - 200, cy + 200):
            rivet(c, x, y, 9, M.steel)
    if sealed:
        c.paint(RRect(cx, cy + 30, 150, 110, 10), M.brass, profile=("bevel", 6, 8),
                shadow=True, contact=0.2)
        c.paint(Circle(cx, cy + 30, 26), M.enamel, profile=("sphere", 18), hue=2, sat=0.7,
                light=0.45)
        mark(c, "check", cx, cy + 30, 40, M.embossed_white, emboss=2.0)
    else:
        mark(c, "box", cx, cy, 170, M.brass, emboss=3.0)


def type_block(c, hue: float = 210, glyph: str = "code", cy: float = CY) -> None:
    """A printer's type block: steel body, one enamelled face, a struck glyph."""
    cx = CX
    body = RRect(cx, cy, 520, 440, 12)
    c.paint(Moved(body, 0, 20), M.steel, profile=("bevel", 8, 12))
    c.paint(body, M.steel, profile=("bevel", 14, 18), shadow=True, contact=0.22)
    # the face is inked in the accent, so two blocks of the same shape are still
    # two different blocks - and the glyph says which kind of type it carries.
    c.paint(RRect(cx, cy - 20, 400, 300, 8), M.enamel, profile=("bevel", 6, 8),
            hue=hue, sat=0.36, light=0.30, contact=0.3)
    mark(c, glyph, cx, cy - 10, 280, M.chrome, emboss=7.0)
    for x in (cx - 230, cx + 230):
        screw(c, x, cy + 180, 11)


def tile_stack(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    tray = RRect(cx, cy + 240, 620, 90, 16)
    c.paint(tray, M.aluminium, profile=("bevel", 10, 14), shadow=True, contact=0.2)
    for i, (tilt, h) in enumerate(((-7, 0), (0, 1), (7, 2))):
        y = cy + 120 - i * 96
        tile = Rotated(RRect(cx + (i - 1) * 16, y, 380, 290, 44), tilt, cx, y)
        c.paint(Moved(tile, 0, 14), M.gunmetal, profile=("bevel", 8, 12))
        c.paint(tile, M.glass, profile=("bevel", 8, 14), hue=(hue + h * 22) % 360,
                sat=0.55, light=0.44, shadow=True, contact=0.24)
        mark(c, ("spark", "star", "nib")[i], cx + (i - 1) * 16, y, 100, emboss=3.0)


def keycap(c, glyph: str = "prompt", hue: float = 210, cy: float = CY) -> None:
    """One ivory key: the chin strip is enamelled in the accent."""
    cx = CX
    body = RRect(cx, cy, 380, 380, 60)
    c.paint(Moved(body, 0, 30), M.ivory, profile=("bevel", 12, 16))
    c.paint(body, M.ivory, profile=("bevel", 26, 34), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy - 10, 300, 300, 44), M.ivory, profile=("bevel", 10, 14), contact=0.2)
    c.paint(RRect(cx, cy + 140, 232, 34, 10), M.enamel, profile=("bevel", 5, 7),
            hue=hue, sat=0.60, light=0.46, contact=0.2)
    mark(c, glyph, cx, cy - 10, 170, lambda ctx, **k: M.engraved(ctx, light=0.42, **k),
         emboss=2.6)


def keycaps(c, hue: float = 210, cy: float = CY) -> None:
    """Three ivory keys over one enamelled plate (the keyboard preferences)."""
    cx = CX
    plate = RRect(cx, cy + 250, 800 - 60, 90, 26)
    c.paint(Moved(plate, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(plate, M.enamel, profile=("bevel", 14, 20), hue=hue, sat=0.42, light=0.42,
            shadow=True, contact=0.24)
    for i, dx in enumerate((-210, 0, 210)):
        body = Rotated(RRect(cx + dx, cy + (0 if i == 1 else 40), 300, 300, 46), (i - 1) * 6,
                       cx + dx, cy)
        c.paint(Moved(body, 0, 26), M.ivory, profile=("bevel", 10, 14))
        c.paint(body, M.ivory, profile=("bevel", 22, 30), shadow=True, contact=0.2)
        mark(c, ("prompt", "gear", "grid")[i], cx + dx, cy + (0 if i == 1 else 40), 130,
             lambda ctx, **k: M.engraved(ctx, light=0.40, **k), emboss=2.4)


def spoons(c, hue: float = 40, cy: float = CY) -> None:
    """Nested brass measuring cups: one shape that contains another."""
    cx = CX
    for i, (r, dx, dy) in enumerate(((200, -210, 30), (158, 30, 90), (116, 230, 150))):
        bowl = Circle(cx + dx, cy + dy, r)
        handle = Capsule(cx + dx, cy + dy - r * 0.55, cx + dx + r * 0.80,
                         cy + dy - r * 1.45, 15)
        c.paint(handle, M.brass, profile=("bevel", 6, 8), shadow=True, contact=0.15)
        c.paint(Moved(bowl, 0, 16), M.brass, profile=("sphere", r * 0.6))
        c.paint(bowl, M.brass, profile=("sphere", r * 0.62), shadow=True, contact=0.25)
        c.paint(Circle(cx + dx, cy + dy - 6, r * 0.66), M.brass, profile=("sphere", r * 0.5),
                contact=0.3)
        # the enamel lining is the one colour on an otherwise all-brass nest
        c.paint(Circle(cx + dx, cy + dy - 6, r * 0.50), M.enamel,
                profile=("sphere", r * 0.4), hue=(hue + i * 14) % 360, sat=0.55,
                light=0.50, contact=0.16)
        c.paint(ring(cx + dx, cy + dy - 6, r * 0.66, 8), M.brass, profile=("bevel", 4, 5),
                contact=0.2)


def dice(c, hue: float = 146, cy: float = CY) -> None:
    cx = CX
    c.paint(Circle(cx, cy, 340), M.chrome, profile=("sphere", 300), shadow=True, contact=0.2)
    c.paint(Circle(cx, cy, 292), M.felt, profile=("flat",), hue=hue, sat=0.40, light=0.28,
            contact=0.3)
    faces = {(0, 0): 3, (1, 0): 5}
    for i, (dx, dy) in enumerate(((-104, 34), (120, -18))):
        die = Rotated(RRect(cx + dx, cy + dy, 246, 246, 34), (-14, 13)[i], cx + dx, cy + dy)
        c.paint(Moved(die, 0, 24), M.ivory, profile=("bevel", 10, 14))
        c.paint(die, M.ivory, profile=("bevel", 22, 30), shadow=True, contact=0.24)
    pips = [(-104, 34, [(-58, -58), (0, 0), (58, 58)]),
            (120, -18, [(-60, -60), (60, -60), (0, 0), (-60, 60), (60, 60)])]
    for dx, dy, spots in pips:
        for px, py in spots:
            c.paint(Circle(cx + dx + px, cy + dy + py, 20), M.flat("#1d2026"),
                    profile=("sphere", 14))


def flask(c, hue: float = 32, cy: float = CY, sat: float = 0.72) -> None:
    """Erlenmeyer flask: clear glass, coloured liquid, one meniscus."""
    cx = CX
    body = Poly([(cx - 104, cy - 350), (cx + 104, cy - 350), (cx + 104, cy - 180),
                 (cx + 268, cy + 190), (cx + 252, cy + 302), (cx - 252, cy + 302),
                 (cx - 268, cy + 190), (cx - 104, cy - 180)], rounding=34)
    c.paint(Moved(body, 0, 18), M.flat("#7e8a98"), profile=("bevel", 10, 16),
            alpha=0.35)
    c.paint(body, M.glass, profile=("bevel", 22, 38), hue=200, sat=0.10, light=0.88,
            alpha=0.90, shadow=True, contact=0.24)
    # liquid: clipped to the flask so it cannot spill past the glass
    inside = np.clip(0.5 - body.sdf(c.X, c.Y), 0.0, 1.0)
    level = np.clip((c.Y - (cy + 46)) / 40.0, 0.0, 1.0)
    liquid = Poly([(cx - 236, cy + 292), (cx + 236, cy + 292), (cx + 158, cy + 96),
                   (cx + 40, cy + 60), (cx - 118, cy + 84)], rounding=30)
    c.paint(liquid, M.enamel, profile=("bevel", 14, 26), hue=hue,
            sat=max(0.80, sat), light=0.56, contact=0.18, mask=inside * level)
    c.paint(Capsule(cx - 186, cy + 92, cx + 196, cy + 92, 10), M.flat("#ffffff"),
            profile=("bevel", 3, 4), alpha=0.30, mask=inside)
    c.paint(Capsule(cx - 82, cy - 300, cx - 82, cy - 60, 14), M.flat("#ffffff"),
            profile=("bevel", 4, 6), alpha=0.55)
    c.paint(Capsule(cx - 180, cy + 210, cx - 140, cy + 60, 10), M.flat("#ffffff"),
            profile=("bevel", 3, 5), alpha=0.35)
    c.paint(ring(cx, cy - 350, 112, 26), M.glass, profile=("bevel", 8, 14), hue=202,
            sat=0.05, light=0.86, contact=0.24)
    for dx, dy, r in ((-70, 200, 12), (30, 170, 9), (-14, 132, 7)):
        c.paint(Circle(cx + dx, cy + dy, r), M.flat("#ffffff"),
                profile=("sphere", r), alpha=0.35)


def palette(c, hue: float = 22, cy: float = CY, sat: float = 0.45) -> None:
    cx = CX
    wood = Poly([(cx, cy - 320), (cx + 230, cy - 260), (cx + 330, cy - 40),
                 (cx + 250, cy + 190), (cx + 60, cy + 160), (cx - 60, cy + 240),
                 (cx - 260, cy + 200), (cx - 340, cy - 30)], rounding=40) \
        - Circle(cx + 150, cy + 80, 62)
    c.paint(Moved(wood, 0, 16), M.wood, profile=("bevel", 10, 14), hue=24, sat=0.58,
            light=0.36)
    c.paint(wood, M.wood, profile=("bevel", 18, 24), hue=26, sat=0.60, light=0.46,
            shadow=True, contact=0.22)
    for (x, y, h, r) in ((cx - 200, cy - 120, 2, 46), (cx - 60, cy - 190, (hue + 50) % 360, 40),
                         (cx + 110, cy - 150, (hue + 150) % 360, 42), (cx - 210, cy + 80, hue, 38),
                         (cx - 60, cy + 30, (hue + 300) % 360, 34)):
        c.paint(Circle(x, y, r), M.enamel, profile=("sphere", r * 0.8), hue=h, sat=0.62,
                light=0.5, shadow=True, contact=0.2)
    brush = Rotated(Capsule(cx + 180, cy - 250, cx + 330, cy - 350, 20), 0, 0, 0)
    c.paint(brush, M.wood, profile=("bevel", 6, 8), hue=32, sat=0.4, light=0.4,
            shadow=True, contact=0.15)
    c.paint(Rotated(Capsule(cx + 320, cy - 340, cx + 370, cy - 375, 22), 0, 0, 0), M.chrome,
            profile=("bevel", 6, 8), contact=0.15)
    c.paint(Rotated(Poly([(cx + 370, cy - 380), (cx + 420, cy - 400), (cx + 400, cy - 360)],
                         4), 0, 0, 0), M.enamel, profile=("bevel", 4, 6), hue=hue, sat=0.5,
            light=0.35)


def globe(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    base = Ellipse(cx, cy + 300, 220, 48)
    c.paint(base, M.wood, profile=("sphere", 40), shadow=True, contact=0.2)
    c.paint(Capsule(cx, cy + 100, cx, cy + 296, 22), M.brass, profile=("bevel", 8, 10))
    c.paint(Rotated(ring(cx, cy, 272, 18), -18, cx, cy), M.brass, profile=("bevel", 6, 8),
            shadow=True, contact=0.2)
    c.paint(Circle(cx, cy, 258), M.glass, profile=("sphere", 210), hue=hue, sat=0.62,
            light=0.46, contact=0.2)
    c.paint_mask(radial_ticks(cx, cy, 236, 252, 24, 2.4), M.flat("#0a3350"), emboss=0.8,
                 alpha=0.35)
    for dy in (-120, 0, 120):
        c.paint(Ellipse(cx, cy + dy, 250 - abs(dy) * 0.5, 12), M.flat("#0a3350"),
                profile=("bevel", 2, 3), alpha=0.25)
    c.paint(Capsule(cx, cy + 40, cx + 216, cy + 40, 5), M.brass, profile=("bevel", 3, 3))


def keyring(c, hue: float = 205, cy: float = CY) -> None:
    """A chrome ring, two brass keys and a leather fob in the accent hue."""
    cx = CX
    c.paint(Rotated(ring(cx - 40, cy - 210, 96, 22), 0, 0, 0), M.chrome,
            profile=("bevel", 6, 8), shadow=True, contact=0.2)
    for i, (dx, rot) in enumerate(((-90, -8), (70, 10))):
        key = Rotated(Capsule(cx + dx + 40, cy - 130, cx + dx + 20, cy + 120, 20), rot,
                      cx + dx, cy)
        c.paint(key, M.brass, profile=("bevel", 8, 10), shadow=True, contact=0.18)
        head = Rotated(ring(cx + dx + 40, cy - 150, 52, 20), rot, cx + dx, cy)
        c.paint(head, M.brass, profile=("bevel", 6, 8), contact=0.15)
        for j in range(2):
            c.paint(Rotated(Capsule(cx + dx + 20, cy + 80 + j * 34, cx + dx + 74,
                                    cy + 80 + j * 34, 8), rot, cx + dx, cy), M.brass,
                    profile=("bevel", 3, 4))
    # a dyed leather fob on a brass eyelet: the one coloured part of the bunch
    fob = Capsule(cx + 182, cy - 70, cx + 204, cy + 158, 34)
    c.paint(Moved(fob, 0, 14), M.flat("#2b231a"), profile=("bevel", 6, 9))
    c.paint(fob, M.leather, profile=("bevel", 12, 18), hue=hue, sat=0.62, light=0.34,
            shadow=True, contact=0.22)
    c.paint(ring(cx + 182, cy - 70, 22, 11), M.brass, profile=("bevel", 4, 6),
            contact=0.2)
    c.paint(Rotated(ring(cx + 196, cy + 30, 18, 6), -8, cx + 196, cy + 30), M.engraved,
            profile=("bevel", 2, 3), alpha=0.22)


# --------------------------------------------------------------------------- #
# more hardware
# --------------------------------------------------------------------------- #

def desktop_box(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 600, 340, 36)
    c.paint(Moved(body, 0, 30), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 24, 32), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy - 70, 300, 30, 12), M.gunmetal, profile=("bevel", 6, 8),
            contact=0.3)
    c.paint(Circle(cx, cy + 60, 40), M.aluminium, profile=("bevel", 8, 12), contact=0.2)
    c.paint(RRect(cx + 210, cy + 100, 90, 40, 6), M.rubber, profile=("bevel", 4, 5),
            contact=0.15)
    c.paint_mask(stripe_mask((cx - 150, cy + 100, cx + 150, cy + 140), 3, 4.0),
            M.flat("#20242b"), emboss=1.4, alpha=0.5)
    c.paint(Capsule(cx - 250, cy - 70, cx - 90, cy - 70, 9), M.enamel,
            profile=("bevel", 4, 6), hue=hue, sat=0.50, light=0.44, contact=0.16)
    c.paint(Capsule(cx + 220, cy - 120, cx + 220, cy - 120, 7), M.lamp,
            profile=("sphere", 5), hue=140)
    for x in (cx - 240, cx + 240):
        c.paint(Capsule(x, cy + 150, x, cy + 190, 18), M.rubber, profile=("bevel", 4, 6))


def audio_card(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    board = RRect(cx, cy, 700, 260, 14)
    c.paint(Moved(board, 0, 16), M.steel, profile=("bevel", 8, 12))
    c.paint(board, M.paint, profile=("bevel", 14, 18), hue=hue, sat=0.28, light=0.26,
            shadow=True, contact=0.2)
    for i, dx in enumerate((-60, 40, 140)):
        c.paint(Circle(cx + dx, cy, 44), M.brass, profile=("sphere", 40), contact=0.2)
        c.paint(Circle(cx + dx, cy, 22), M.flat("#12151a"), profile=("sphere", 16))
    c.paint(RRect(cx - 250, cy, 120, 120, 8), M.gunmetal, profile=("bevel", 6, 8),
            contact=0.2)
    c.paint(RRect(cx + 290, cy - 80, 60, 220, 6), M.chrome, profile=("bevel", 4, 6),
            contact=0.2)


def dongle(c, hue: float = 215, glyph: str = "bluetooth", cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 90, 280, 300, 34)
    c.paint(Moved(body, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.enamel, profile=("bevel", 20, 26), hue=hue, sat=0.5, light=0.45,
            shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 120, 150, 150, 8), M.chrome, profile=("bevel", 8, 10),
            contact=0.2)
    c.paint(RRect(cx, cy - 140, 100, 70, 4), M.flat("#2a3038"), profile=("bevel", 3, 4))
    c.paint(Circle(cx, cy + 190, 26), M.chrome, profile=("sphere", 18), contact=0.2)
    mark(c, glyph, cx, cy + 120, 120, emboss=2.6)


def network_switch(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 640, 300, 30)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 22, 30), shadow=True, contact=0.22)
    for i in range(6):
        x = cx - 220 + i * 88
        c.paint(RRect(x, cy + 40, 66, 56, 6), M.rubber, profile=("bevel", 4, 6),
                contact=0.2)
        c.paint(RRect(x, cy + 50, 46, 16, 2), M.brass, profile=("bevel", 2, 2))
    for i in range(4):
        c.paint(Capsule(cx - 200 + i * 130, cy - 80, cx - 200 + i * 130, cy - 80, 7),
                M.lamp, profile=("sphere", 6), hue=140 if i % 2 == 0 else 45)
    c.paint(RRect(cx, cy + 140, 600, 22, 8), M.enamel, profile=("bevel", 4, 6),
            hue=hue, sat=0.46, light=0.40, contact=0.16)
    c.paint(Capsule(cx, cy - 140, cx, cy - 190, 10), M.chrome, profile=("bevel", 4, 5))


def modem(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 20, 560, 240, 26)
    c.paint(Moved(body, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 26), shadow=True, contact=0.22)
    for i in range(3):
        c.paint(Capsule(cx - 160 + i * 90, cy - 40, cx - 160 + i * 90, cy - 40, 8),
                M.lamp, profile=("sphere", 6), hue=(140, 45, 200)[i])
    c.paint(RRect(cx - 60, cy + 130, 380, 20, 8), M.enamel, profile=("bevel", 4, 6),
            hue=hue, sat=0.46, light=0.40, contact=0.14)
    c.paint(RRect(cx + 180, cy + 40, 100, 66, 8), M.rubber, profile=("bevel", 5, 6),
            contact=0.2)
    c.paint(Capsule(cx - 120, cy + 160, cx - 260, cy + 300, 16), M.rubber,
            profile=("bevel", 6, 8), shadow=True, contact=0.15)


def dock(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    base = RRect(cx, cy + 220, 560, 120, 34)
    c.paint(Moved(base, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(base, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    slot = RRect(cx, cy + 190, 280, 26, 10)
    c.paint(slot, M.gunmetal, profile=("bevel", 5, 7), contact=0.3)
    c.paint(Capsule(cx - 230, cy + 200, cx - 90, cy + 200, 8), M.enamel,
            profile=("bevel", 4, 5), hue=hue, sat=0.50, light=0.44, contact=0.16)
    c.paint(RRect(cx, cy + 40, 150, 240, 16), M.chrome, profile=("bevel", 10, 14),
            shadow=True, contact=0.2)
    c.paint(Capsule(cx, cy - 80, cx, cy - 80, 10), M.lamp, profile=("sphere", 7), hue=140)
    c.paint(Capsule(cx + 240, cy + 190, cx + 340, cy + 120, 20), M.rubber,
            profile=("bevel", 6, 8), contact=0.15)


def funnel(c, hue: float = 200, cy: float = CY, paper_sheet: bool = True) -> None:
    cx = CX
    bowl = Poly([(cx - 300, cy - 210), (cx + 300, cy - 210), (cx + 300, cy - 150),
                 (cx + 70, cy + 150), (cx + 70, cy + 330), (cx - 70, cy + 330),
                 (cx - 70, cy + 150), (cx - 300, cy - 150)], rounding=8)
    c.paint(Moved(bowl, 0, 20), M.steel, profile=("bevel", 10, 14))
    c.paint(bowl, M.chrome, profile=("bevel", 20, 26), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy - 200, 600, 56, 24), M.aluminium, profile=("bevel", 14, 18),
            contact=0.25)
    # an enamel collar where the funnel narrows, and an enamelled spout: the
    # accent on the one part that is the same on every funnel, so two funnels
    # are still two funnels
    c.paint(RRect(cx, cy + 186, 164, 34, 10), M.enamel, profile=("bevel", 6, 9),
            hue=hue, sat=0.58, light=0.46, shadow=True, contact=0.2)
    c.paint(RRect(cx, cy + 268, 140, 150, 18), M.enamel, profile=("bevel", 10, 16),
            hue=hue, sat=0.52, light=0.50, shadow=True, contact=0.22)
    c.paint(Capsule(cx - 30, cy + 220, cx - 30, cy + 320, 5), M.flat("#ffffff"),
            profile=("bevel", 2, 3), alpha=0.30)
    if paper_sheet:
        sheet = Rotated(RRect(cx - 40, cy - 260, 330, 180, 6), -10, cx, cy - 260)
        c.paint(sheet, M.paper, profile=("flat",), shadow=True, contact=0.15)
        _text_lines(c, (cx - 160, cy - 320, cx + 100, cy - 210), 3, 4.0)


# --------------------------------------------------------------------------- #
# tools and instruments
# --------------------------------------------------------------------------- #

def wrench(c, hue: float = 210, cy: float = CY, angle: float = -18) -> None:
    """A combination wrench: box end, forged handle and an open jaw."""
    cx = CX
    box_end = ring(cx - 208, cy + 126, 108, 58)
    open_end = Circle(cx + 234, cy - 120, 110) - RRect(cx + 302, cy - 168, 156, 92, 12)
    handle = Capsule(cx - 160, cy + 78, cx + 168, cy - 74, 52)
    shape = Rotated(box_end | open_end | handle, angle, cx, cy)
    c.paint(Moved(shape, 0, 22), M.flat("#20252c"), profile=("bevel", 8, 12))
    c.paint(shape, M.steel, profile=("bevel", 18, 26), shadow=True, contact=0.24)
    c.paint(Rotated(ring(cx - 208, cy + 126, 92, 14), angle, cx, cy), M.gunmetal,
            profile=("bevel", 4, 6), contact=0.2)
    c.paint(Rotated(Capsule(cx - 176, cy + 120, cx + 120, cy - 42, 6), angle, cx, cy),
            M.flat("#ffffff"), profile=("bevel", 2, 2), alpha=0.18)
    c.paint(Rotated(RRect(cx - 24, cy + 8, 58, 96, 12), angle, cx, cy), M.enamel,
            profile=("bevel", 5, 8), hue=hue, sat=0.66, light=0.46, contact=0.18)


def screwdriver(c, hue: float = 210, cy: float = CY, angle: float = 16) -> None:
    cx = CX
    handle = Rotated(Capsule(cx - 110, cy + 200, cx + 40, cy + 20, 82), angle, cx, cy)
    c.paint(Moved(handle, 0, 20), M.steel, profile=("bevel", 8, 12))
    c.paint(handle, M.enamel, profile=("sphere", 96), hue=hue, sat=0.55, light=0.42,
            shadow=True, contact=0.22)
    c.paint(ring(cx - 40, cy + 110, 74, 22), M.enamel, profile=("bevel", 6, 8),
            hue=hue, sat=0.6, light=0.54, contact=0.2)
    shaft = Rotated(Capsule(cx + 70, cy - 10, cx + 250, cy - 210, 17), angle, cx, cy)
    c.paint(shaft, M.chrome, profile=("bevel", 8, 10), contact=0.2)
    c.paint(Rotated(Poly([(cx + 244, cy - 220), (cx + 300, cy - 268), (cx + 268, cy - 200),
                          (cx + 236, cy - 196)], 3), angle, cx + 270, cy - 230), M.chrome,
            profile=("bevel", 4, 6))


def toolbox(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    # a screwdriver and a hammer peeking out of the box
    shaft = Rotated(Capsule(cx - 96, cy - 60, cx - 30, cy - 300, 16), -10, cx, cy)
    c.paint(shaft, M.chrome, profile=("bevel", 6, 9), shadow=True, contact=0.15)
    grip = Rotated(Capsule(cx - 40, cy - 310, cx + 30, cy - 410, 38), -10, cx, cy)
    c.paint(Moved(grip, 0, 12), M.flat("#2b3038"), profile=("bevel", 6, 9))
    c.paint(grip, M.enamel, profile=("sphere", 34), hue=hue, sat=0.62, light=0.46,
            shadow=True, contact=0.2)
    for i in range(3):
        c.paint(Rotated(Capsule(cx - 52 + i * 14, cy - 330 - i * 12,
                                cx + 16 + i * 14, cy - 424 - i * 12, 4), -10, cx, cy),
                M.flat("#ffffff"), profile=("bevel", 2, 2), alpha=0.16)
    c.paint(Rotated(Capsule(cx + 40, cy - 120, cx + 120, cy - 340, 18), 12, cx, cy),
            M.wood, profile=("bevel", 6, 9), hue=26, sat=0.55, light=0.36,
            shadow=True, contact=0.18)
    box = RRect(cx, cy + 90, 620, 380, 28)
    c.paint(Moved(box, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(box, M.enamel, profile=("bevel", 22, 30), hue=hue, sat=0.42, light=0.40,
            shadow=True, contact=0.22)
    lid = RRect(cx, cy - 96, 640, 90, 26)
    c.paint(Moved(lid, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(lid, M.enamel, profile=("bevel", 16, 22), hue=hue, sat=0.45, light=0.46,
            shadow=True, contact=0.25)
    handle_arch = ring(cx, cy - 150, 120, 26) & RRect(cx, cy - 230, 400, 180)
    c.paint(handle_arch, M.chrome, profile=("bevel", 10, 12), shadow=True, contact=0.2)
    for x in (cx - 180, cx + 180):
        c.paint(RRect(x, cy - 96, 56, 70, 8), M.brass, profile=("bevel", 4, 6), contact=0.2)
    c.paint(Capsule(cx, cy + 60, cx, cy + 60, 14), M.brass, profile=("sphere", 10))
    c.paint(Capsule(cx, cy + 60, cx, cy + 78, 7), M.gunmetal, profile=("bevel", 3, 3))


def ladder(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    for sign in (-1, 1):
        rail = Rotated(Capsule(cx + sign * 210, cy - 260, cx + sign * 250, cy + 300, 22),
                       sign * -2, cx, cy)
        c.paint(rail, M.aluminium, profile=("bevel", 8, 10), shadow=True, contact=0.18)
        c.paint(RRect(cx + sign * 252, cy + 296, 58, 30, 10), M.enamel,
                profile=("bevel", 5, 7), hue=hue, sat=0.55, light=0.44,
                shadow=True, contact=0.18)
    for i in range(5):
        y = cy - 190 + i * 118
        step = RRect(cx, y, 440 - i * 8, 46, 10)
        c.paint(step, M.steel, profile=("bevel", 8, 10), contact=0.2)
        c.paint(Capsule(cx - 220 + i * 4, y - 18, cx + 220 - i * 4, y - 18, 3),
                M.flat("#4a5058"), profile=("bevel", 2, 2), alpha=0.6)


def gauge(c, hue: float = 205, cy: float = CY, r: float = 300) -> None:
    cx = CX
    c.paint(Moved(Circle(cx, cy, r + 26), 0, 20), M.steel, profile=("bevel", 10, 14))
    c.paint(Circle(cx, cy, r + 26), M.chrome, profile=("sphere", r * 0.5), shadow=True,
            contact=0.22)
    c.paint(Circle(cx, cy, r - 8), M.paper, profile=("bevel", 6, 10), contact=0.3)
    # the load band: safe, hot, pegged — an arc of printed ink, not a full ring
    rad = np.hypot(c.X - cx, c.Y - cy)
    ang = np.degrees(np.arctan2(c.Y - cy, c.X - cx))
    sweep = ((ang - 135.0) % 360.0) / 270.0
    band = (rad > r - 50) & (rad < r - 30) & (sweep <= 1.0)
    for lo, hi, col in ((0.0, 0.62, "#2f8f52"), (0.62, 0.84, "#c89016"), (0.84, 1.0, "#b03a2e")):
        mask = (band & (sweep >= lo) & (sweep < hi)).astype(np.float32)
        c.paint_mask(mask, M.flat(col), emboss=0.8, alpha=0.85)
    c.paint_mask(radial_ticks(cx, cy, r - 96, r - 58, 40, 3.4), M.flat("#2f333a"),
                 emboss=1.0, alpha=0.85)
    c.paint_mask(radial_ticks(cx, cy, r - 126, r - 66, 8, 6.0), M.flat("#20242b"),
                 emboss=1.2, alpha=0.9)
    c.paint(Capsule(cx, cy, cx + 176, cy - 132, 11), M.enamel, profile=("bevel", 5, 6),
            hue=hue, sat=0.70, light=0.44, contact=0.25)
    c.paint(Capsule(cx, cy, cx - 54, cy + 40, 9), M.flat("#2b3038"),
            profile=("bevel", 4, 5), contact=0.2)
    c.paint(Circle(cx, cy, 26), M.chrome, profile=("sphere", 18), contact=0.25)
    c.paint(Circle(cx, cy, r - 4), M.flat("#ffffff"), profile=("bevel", 2, 3), alpha=0.0)
    c.paint(ring(cx, cy, r + 10, 22), M.chrome, profile=("bevel", 8, 10), contact=0.2)


def gauge_cluster(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    panel = RRect(cx, cy, 760, 460, 30)
    c.paint(Moved(panel, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(panel, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    for dx, sign in ((-190, 0.7), (190, 0.4)):
        c.paint(Moved(Circle(cx + dx, cy - 20, 168), 0, 14), M.steel, profile=("bevel", 8, 10))
        c.paint(Circle(cx + dx, cy - 20, 168), M.chrome, profile=("sphere", 90), contact=0.24)
        c.paint(Circle(cx + dx, cy - 20, 144), M.paper, profile=("bevel", 5, 8), contact=0.3)
        c.paint_mask(radial_ticks(cx + dx, cy - 20, 92, 132, 24, 3.0), M.flat("#2f333a"),
                     emboss=0.9, alpha=0.8)
        ang = -50 + sign * 80
        c.paint(Capsule(cx + dx, cy - 20, cx + dx + 86 * math.cos(math.radians(ang - 90)),
                        cy - 20 + 86 * math.sin(math.radians(ang - 90)), 6),
                M.enamel, profile=("bevel", 3, 4), hue=hue, sat=0.70, light=0.45)
    for i in range(4):
        c.paint(Capsule(cx - 240 + i * 160, cy + 168, cx - 240 + i * 160, cy + 168, 7),
                M.lamp, profile=("sphere", 6), hue=(140, 45, 200, 140)[i])


def stopwatch(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    crown = Capsule(cx, cy - 320, cx, cy - 250, 26)
    c.paint(crown, M.chrome, profile=("bevel", 8, 10), shadow=True, contact=0.2)
    c.paint(Circle(cx, cy - 336, 34), M.chrome, profile=("sphere", 24), contact=0.2)
    c.paint(Rotated(Capsule(cx + 150, cy - 250, cx + 210, cy - 320, 20), 0, 0, 0),
            M.chrome, profile=("bevel", 6, 8), shadow=True)
    c.paint(Moved(Circle(cx, cy, 330), 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(Circle(cx, cy, 330), M.chrome, profile=("sphere", 300), shadow=True, contact=0.22)
    c.paint(Circle(cx, cy, 286), M.paper, profile=("bevel", 6, 10), contact=0.3)
    c.paint_mask(radial_ticks(cx, cy, 218, 272, 60, 3.0), M.flat("#2f333a"), emboss=1.0,
                 alpha=0.85)
    c.paint_mask(radial_ticks(cx, cy, 236, 272, 12, 5.0), M.flat("#20242b"), emboss=1.1,
                 alpha=0.9)
    c.paint(Capsule(cx, cy, cx + 110, cy - 150, 8), M.flat("#2a2e35"),
            profile=("bevel", 3, 4), contact=0.2)
    c.paint(Capsule(cx, cy, cx - 30, cy - 180, 5), M.flat("#a33a2f"), profile=("bevel", 2, 3))
    c.paint(ring(cx, cy, 306, 30), M.enamel, profile=("bevel", 8, 12), hue=hue, sat=0.55,
            light=0.44, contact=0.24)
    c.paint(Circle(cx, cy, 22), M.chrome, profile=("sphere", 16), contact=0.25)


def balance(c, hue: float = 40, cy: float = CY) -> None:
    cx = CX
    base = Ellipse(cx, cy + 330, 240, 54)
    c.paint(base, M.wood, profile=("sphere", 46), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy + 120, 44, 380, 10), M.brass, profile=("bevel", 8, 10))
    c.paint(Capsule(cx - 300, cy - 190, cx + 300, cy - 190, 14), M.brass,
            profile=("bevel", 8, 10), shadow=True, contact=0.2)
    c.paint(Circle(cx, cy - 190, 34), M.brass, profile=("sphere", 26), contact=0.25)
    for sign in (-1, 1):
        x = cx + sign * 288
        c.paint(Capsule(x, cy - 180, x, cy - 80, 4), M.brass, profile=("bevel", 2, 2))
        pan = Ellipse(x, cy - 40, 128, 34)
        c.paint(Moved(pan, 0, 10), M.brass, profile=("bevel", 6, 8))
        c.paint(pan, M.brass, profile=("bevel", 14, 18), shadow=True, contact=0.22)
        c.paint(Ellipse(x, cy - 44, 96, 22), M.enamel, profile=("bevel", 5, 8), hue=hue,
                sat=0.55, light=0.50, contact=0.16)
    c.paint(Capsule(cx, cy + 120, cx, cy + 300, 8), M.brass, profile=("bevel", 4, 5))


def ruler(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 780, 190, 14)
    c.paint(Moved(body, 0, 16), M.steel, profile=("bevel", 8, 12))
    c.paint(body, M.aluminium, profile=("bevel", 14, 18), shadow=True, contact=0.22)
    for i in range(28):
        x = cx - 350 + i * 26
        height = 46 if i % 5 else 76
        c.paint(Capsule(x, cy - 78, x, cy - 78 + height, 2.2), M.flat("#3a4048"), emboss=1.0,
                alpha=0.75)
    c.paint(RRect(cx + 200, cy + 24, 120, 120, 8), M.enamel, profile=("bevel", 5, 7),
            hue=hue, sat=0.52, light=0.44, shadow=True, contact=0.2)
    c.paint(Circle(cx + 200, cy + 24, 20), M.gunmetal, profile=("sphere", 14))


def pen(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = Rotated(Capsule(cx - 60, cy + 240, cx + 60, cy - 200, 46), 14, cx, cy)
    c.paint(Moved(body, 0, 16), M.steel, profile=("bevel", 8, 10))
    c.paint(body, M.enamel, profile=("sphere", 50), hue=hue, sat=0.55, light=0.32,
            shadow=True, contact=0.2)
    band = Rotated(Capsule(cx + 40, cy - 130, cx + 56, cy - 180, 48), 14, cx, cy)
    c.paint(band, M.brass, profile=("bevel", 6, 8), contact=0.2)
    nib = Rotated(Poly([(cx + 60, cy - 200), (cx + 96, cy - 250), (cx + 120, cy - 300),
                        (cx + 88, cy - 292), (cx + 58, cy - 232)], 3), 14, cx, cy)
    c.paint(nib, M.chrome, profile=("bevel", 5, 7), contact=0.2)
    clip = Rotated(Capsule(cx - 100, cy + 40, cx - 80, cy - 120, 9), 14, cx, cy)
    c.paint(clip, M.brass, profile=("bevel", 4, 5))


def lamps(c, hue: float = 42, cy: float = CY) -> None:
    cx = CX
    c.paint(Ellipse(cx + 120, cy + 330, 190, 46), M.steel, profile=("sphere", 38),
            shadow=True, contact=0.2)
    c.paint(Capsule(cx + 120, cy + 30, cx + 120, cy + 326, 18), M.chrome,
            profile=("bevel", 8, 10))
    c.paint(Rotated(Capsule(cx + 120, cy + 20, cx - 110, cy - 210, 16), 0, 0, 0), M.chrome,
            profile=("bevel", 8, 9), contact=0.15)
    shade = Rotated(Poly([(cx - 250, cy - 250), (cx - 90, cy - 420), (cx + 90, cy - 420),
                          (cx + 250, cy - 250)], rounding=24), 0, 0, 0)
    c.paint(shade, M.enamel, profile=("bevel", 20, 26), hue=hue, sat=0.5, light=0.55,
            shadow=True, contact=0.2)
    glow(c, cx, cy - 170, 300, hue=45, strength=0.22)


def service_bell(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    base = Ellipse(cx, cy + 214, 320, 58)
    c.paint(base, M.steel, profile=("bevel", 16, 20), shadow=True, contact=0.2)
    c.paint(Ellipse(cx, cy + 232, 264, 40), M.enamel, profile=("bevel", 8, 12), hue=hue,
            sat=0.58, light=0.48, contact=0.2)
    bell = Circle(cx, cy - 20, 224) & RRect(cx, cy + 76, 520, 300)
    c.paint(bell, M.chrome, profile=("bevel", 26, 40), shadow=True, contact=0.24)
    c.paint(Ellipse(cx, cy + 168, 258, 54), M.chrome, profile=("bevel", 14, 18),
            contact=0.25)
    c.paint(Capsule(cx, cy - 232, cx, cy - 268, 13), M.chrome, profile=("bevel", 6, 7))
    c.paint(Circle(cx, cy - 280, 28), M.brass, profile=("sphere", 20), contact=0.2)


def cloud_paperweight(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    base = Ellipse(cx, cy + 250, 250, 56)
    c.paint(base, M.aluminium, profile=("bevel", 12, 16), shadow=True, contact=0.2)
    shape = (Circle(cx - 120, cy + 40, 120) | Circle(cx + 40, cy - 10, 150)
             | Circle(cx + 170, cy + 50, 100) | RRect(cx + 20, cy + 110, 480, 140, 60))
    c.paint(shape, M.glass, profile=("bevel", 24, 40), hue=hue, sat=0.35, light=0.66,
            shadow=True, contact=0.24)
    c.paint(Capsule(cx, cy + 250, cx, cy + 300, 12), M.chrome, profile=("bevel", 5, 6))


def lens_turret(c, hue: float = 205, cy: float = CY) -> None:
    """A machined lens turret: one format becoming another."""
    cx = CX
    plate = RRect(cx, cy + 20, 720, 520, 60)
    c.paint(Moved(plate, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(plate, M.aluminium, profile=("bevel", 26, 36), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 20, 640, 440, 48), M.gunmetal, profile=("bevel", 12, 16),
            contact=0.3)
    for dx, r in ((-190, 96), (0, 128), (190, 96)):
        c.paint(Moved(Circle(cx + dx, cy + 10, r), 0, 12), M.gunmetal,
                profile=("bevel", 8, 10))
        c.paint(Circle(cx + dx, cy + 10, r), M.chrome, profile=("sphere", r * 0.5),
                contact=0.26)
        c.paint(Circle(cx + dx, cy + 10, r * 0.74), M.optic, profile=("sphere", r * 0.4),
                hue=hue)
    c.paint(Capsule(cx, cy + 240, cx, cy + 240, 18), M.brass, profile=("sphere", 12))
    for x in (cx - 320, cx + 320):
        screw(c, x, cy + 190, 12)


def gears(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    small = Poly(gear_polygon(cx + 250, cy - 180, 190, 150, 9), rounding=2)
    c.paint(Moved(small, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(small, M.steel, profile=("bevel", 16, 20), shadow=True, contact=0.22)
    c.paint(Circle(cx + 250, cy - 180, 150), M.steel, profile=("bevel", 12, 16), contact=0.2)
    c.paint(ring(cx + 250, cy - 180, 108, 34), M.brass, profile=("bevel", 8, 12), contact=0.25)
    c.paint(Circle(cx + 250, cy - 180, 46), M.gunmetal, profile=("sphere", 34), contact=0.2)
    big = Poly(gear_polygon(cx - 90, cy + 60, 310, 250, 15), rounding=2)
    c.paint(Moved(big, 0, 24), M.steel, profile=("bevel", 12, 16))
    c.paint(big, M.steel, profile=("bevel", 22, 28), shadow=True, contact=0.22)
    c.paint(Circle(cx - 90, cy + 60, 250), M.steel, profile=("bevel", 16, 22), contact=0.2)
    # a painted rim on the big wheel: the accent that makes one machine's gears
    # a different machine's gears
    c.paint(ring(cx - 90, cy + 60, 224, 26), M.enamel, profile=("bevel", 6, 9), hue=hue,
            sat=0.55, light=0.46, contact=0.2)
    c.paint(ring(cx - 90, cy + 60, 176, 56), M.brass, profile=("bevel", 12, 16), contact=0.25)
    c.paint(Circle(cx - 90, cy + 60, 116), M.gunmetal, profile=("sphere", 90), contact=0.3)
    c.paint(Circle(cx - 90, cy + 60, 46), M.brass, profile=("sphere", 34), contact=0.2)


def magnifier(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    sheet = Rotated(RRect(cx + 40, cy + 120, 420, 320, 6), -6, cx, cy + 120)
    c.paint(sheet, M.paper, profile=("flat",), shadow=True, contact=0.2)
    _text_lines(c, (cx - 120, cy + 20, cx + 200, cy + 250), 6, 4.0)
    lens_ring = Rotated(ring(cx - 120, cy - 120, 190, 44), 0, 0, 0)
    c.paint(lens_ring, M.chrome, profile=("bevel", 12, 16), shadow=True, contact=0.2)
    c.paint(Circle(cx - 120, cy - 120, 172), M.glass, profile=("bevel", 10, 26), hue=hue,
            sat=0.25, light=0.68, gloss=1.0, contact=0.3)
    c.paint(Rotated(Capsule(cx + 30, cy + 10, cx + 220, cy + 230, 30), 0, 0, 0), M.chrome,
            profile=("bevel", 10, 12), shadow=True, contact=0.2)


def connector(c, hue: float = 205, cy: float = CY) -> None:
    """Two cable ends meeting: a plug and its socket, chrome and enamel."""
    cx = CX
    c.paint(Capsule(cx - 330, cy + 210, cx - 170, cy + 40, 34), M.rubber,
            profile=("bevel", 10, 14), shadow=True, contact=0.15)
    c.paint(Capsule(cx + 330, cy + 210, cx + 170, cy + 40, 34), M.rubber,
            profile=("bevel", 10, 14), shadow=True, contact=0.15)
    collar = Capsule(cx - 150, cy + 30, cx - 90, cy - 20, 74)
    c.paint(Moved(collar, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(collar, M.chrome, profile=("bevel", 22, 30), shadow=True, contact=0.2)
    c.paint(ring(cx - 120, cy + 5, 66, 20), M.enamel, profile=("bevel", 8, 10),
            hue=hue, sat=0.6, light=0.46, contact=0.2)
    socket = Capsule(cx + 150, cy + 30, cx + 90, cy - 20, 74)
    c.paint(Moved(socket, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(socket, M.chrome, profile=("bevel", 22, 30), shadow=True, contact=0.2)
    c.paint(Circle(cx + 90, cy - 20, 44), M.gunmetal, profile=("sphere", 34), contact=0.2)
    for dx, dy in ((-22, 0), (22, 0), (0, 26)):
        c.paint(Circle(cx + 90 + dx, cy - 20 + dy, 9), M.brass, profile=("sphere", 6))


def cable_coil(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    for i, r in enumerate((260, 210, 160)):
        coil = ring(cx, cy + 30, r, 46)
        c.paint(Moved(coil, 0, 14 + i * 6), M.rubber, profile=("bevel", 10, 14))
        c.paint(coil, M.rubber, profile=("bevel", 14, 18), shadow=True, contact=0.18)
    c.paint(Capsule(cx + 250, cy + 40, cx + 330, cy + 250, 22), M.rubber,
            profile=("bevel", 8, 10), shadow=True, contact=0.15)
    plug = RRect(cx + 330, cy + 290, 120, 150, 18)
    c.paint(plug, M.glass, profile=("bevel", 10, 14), hue=hue, sat=0.3, light=0.55,
            shadow=True, contact=0.2)
    for i in range(3):
        c.paint(RRect(cx + 306 + i * 26, cy + 344, 16, 34, 3), M.brass,
                profile=("bevel", 2, 3))
