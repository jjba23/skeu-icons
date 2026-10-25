"""The desk: app-icon subjects that are not hardware, books or tools.

A terminal is a terminal, not a letter on a disc; a browser is a desk globe, a
mail client an envelope with a wax seal, a chat client a stitched enamel bubble.
Every builder here follows the same recipe as ``objects`` and ``toolkit``: one
silhouette, a bevel or sphere height field, one key light, contact shadows where
parts meet, and the accent on at most a quarter of the icon.
"""

from __future__ import annotations

import math

import numpy as np

from . import materials as M
from .objects import (CX, CY, dots_mask, grid_mask, mark, radial_ticks, stitch_mask,
                      stripe_mask)
from .motifs import ribbon
from .paint import (SIZE, Capsule, Circle, Ellipse, Moved, Poly, RRect, Rotated, blur,
                    clamp01, hsl, polyline_mask, ring)
from .pictograms import glyph_mask
from .toolkit import _photo, _text_lines


# --------------------------------------------------------------------------- #
# displays and windows
# --------------------------------------------------------------------------- #

def terminal(c, hue: float = 196, glyph: str = "prompt", cy: float = CY,
             light: float = 0.84) -> None:
    """A compact CRT terminal: ivory-plastic case, dark glass, one lit prompt."""
    cx = CX
    body = RRect(cx, cy + 20, 660, 540, 34)
    c.paint(Moved(body, 0, 30), M.ivory, profile=("bevel", 12, 16), hue=40, sat=0.10,
            light=light - 0.14)
    c.paint(body, M.ivory, profile=("bevel", 24, 32), hue=40, sat=0.10, light=light,
            shadow=True, contact=0.24)
    # moulded inner bezel, recessed a couple of millimetres
    c.paint(RRect(cx, cy - 30, 566, 388, 40), M.ivory, profile=("bevel", 8, 12),
            hue=40, sat=0.10, light=light - 0.08, contact=0.35)
    c.paint(RRect(cx, cy - 34, 512, 330, 32), M.screen, profile=("bevel", 8, 14),
            hue=hue, contact=0.4)
    c.paint_mask(glyph_mask_soft(glyph, cx - 40, cy - 40, 250),
                 lambda ctx, **k: M.engraved(ctx, light=0.60, **k), emboss=2.4, alpha=0.9)
    # power lamp and a row of vent slots on the chin
    c.paint(Circle(cx + 250, cy + 224, 13), M.lamp, profile=("sphere", 10), hue=140)
    c.paint_mask(stripe_mask((cx - 250, cy + 212, cx - 30, cy + 236), 5, 4.0, vertical=False),
                 M.flat("#4a4740"), emboss=1.2, alpha=0.45)
    c.paint(RRect(cx - 190, cy + 224, 120, 26, 8), M.gunmetal, profile=("bevel", 4, 6),
            alpha=0.55)


def glyph_mask_soft(name: str, cx: float, cy: float, width: float) -> np.ndarray:
    from .pictograms import glyph_mask
    return glyph_mask(name, cx, cy, width)


def window_pane(c, hue: float = 208, cy: float = CY) -> None:
    """A chrome-sash window: glass, a title bar and a lit roll-up blind."""
    cx = CX
    outer = RRect(cx, cy, 640, 560, 16)
    c.paint(Moved(outer, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(outer, M.chrome, profile=("bevel", 20, 28), shadow=True, contact=0.24)
    c.paint(RRect(cx, cy + 8, 580, 500, 10), M.flat("#20252c"),
            profile=("bevel", 4, 6), contact=0.3)
    c.paint(RRect(cx, cy + 8, 566, 486, 8), M.glass, profile=("flat",), hue=hue, sat=0.34,
            light=0.38, gloss=0.55, contact=0.2)
    bar = RRect(cx, cy - 218, 600, 84, 12)
    c.paint(bar, M.aluminium, profile=("bevel", 12, 18), contact=0.3)
    c.paint(Circle(cx - 266, cy - 218, 15), M.enamel, profile=("sphere", 11), hue=6, sat=0.6,
            light=0.55)
    c.paint(Circle(cx - 220, cy - 218, 15), M.enamel, profile=("sphere", 11), hue=44, sat=0.6,
            light=0.55)
    c.paint(Circle(cx - 174, cy - 218, 15), M.enamel, profile=("sphere", 11), hue=140, sat=0.5,
            light=0.45)
    # the blind: horizontal slats in the upper half of the pane
    c.paint(RRect(cx, cy - 62, 540, 214, 6), M.ivory, profile=("bevel", 6, 10), hue=40,
            sat=0.12, light=0.88, contact=0.2)
    c.paint_mask(stripe_mask((cx - 266, cy - 160, cx + 266, cy + 42), 7, 3.0), M.flat("#b9b3a4"),
                 emboss=1.4, alpha=0.55)
    c.paint(Capsule(cx, cy - 168, cx, cy - 240, 4), M.brass, profile=("bevel", 2, 3))


def window_fan(c, hue: float = 208, cy: float = CY) -> None:
    """Three glass windows fanned on a chrome rail: an overview of windows."""
    cx = CX
    rail = RRect(cx, cy + 304, 560, 54, 14)
    c.paint(rail, M.aluminium, profile=("bevel", 10, 14), shadow=True, contact=0.22)
    for i, (dx, dy, rot, h) in enumerate(((-176, 96, -9, 206), (0, 0, 0, 226), (176, 92, 9, 206))):
        pane = Rotated(RRect(cx + dx, cy + dy - 60, 380, 400, 12), rot, cx + dx, cy + dy)
        c.paint(Moved(pane, 0, 20), M.gunmetal, profile=("bevel", 8, 12))
        c.paint(pane, M.chrome, profile=("bevel", 14, 20), shadow=True, contact=0.22)
        inner = Rotated(RRect(cx + dx, cy + dy - 60, 330, 344, 8), rot, cx + dx, cy + dy)
        c.paint(inner, M.glass, profile=("flat",), hue=(hue + i * 14) % 360, sat=0.42,
                light=0.42, gloss=0.5, contact=0.25)
        c.paint_mask(stripe_mask((cx + dx - 160, cy + dy - 200, cx + dx + 160,
                                  cy + dy - 96), 3, 5.0), M.flat("#ffffff"), emboss=1.0,
                     alpha=0.30)


# --------------------------------------------------------------------------- #
# paper, mail and print
# --------------------------------------------------------------------------- #

def envelope(c, hue: float = 208, cy: float = CY, seal: bool = True,
             stamp_hue: float = 8) -> None:
    """A laid-paper envelope, flap open behind, wax seal and one stamp."""
    cx = CX
    w, h = 660, 440
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2 + 20, cx + w / 2, cy + h / 2 + 20
    back = Poly([(x0, y0 + 60), (cx, y0 - 90), (x1, y0 + 60), (x1, y1), (x0, y1)],
                rounding=6)
    c.paint(Moved(back, 0, 12), M.paper, profile=("flat",))
    c.paint(back, M.paper, profile=("flat",), shadow=True, contact=0.18)
    c.paint(Poly([(x0 + 6, y1 - 4), (cx, y0 + 150), (x1 - 6, y1 - 4)], rounding=4),
            M.paper, profile=("flat",), contact=0.2)
    for i in range(2):
        c.paint(Poly([(x0 + 6, y0 + 70 + i * 6), (x0 + 6, y1 - 6),
                      (cx - 30, y0 + 120)], rounding=4), M.paper, profile=("flat",),
                alpha=0.35)
    # stamp: a perforated ivory square with the accent on its engraving only
    sx, sy = x1 - 92, y0 + 92
    c.paint(RRect(sx, sy, 96, 112, 4), M.paper, profile=("bevel", 2, 3), contact=0.2)
    c.paint_mask(dots_mask(SIZE, 12, 2.0, bounds=(sx - 48, sy - 56, sx + 48, sy + 56)),
                 M.flat("#b7ab92"), emboss=0.6, alpha=0.55)
    c.paint(Ellipse(sx, sy, 27, 33), M.enamel, profile=("sphere", 20), hue=stamp_hue,
            sat=0.5, light=0.5, alpha=0.85)
    if seal:
        c.paint(Circle(cx, cy + 118, 52), M.enamel, profile=("sphere", 34), hue=stamp_hue,
                sat=0.52, light=0.42, shadow=True, contact=0.3)
        mark(c, "star", cx, cy + 118, 40, M.brass, emboss=2.0)
    c.paint(Capsule(cx - 210, cy + 40, cx + 100, cy + 40, 3), M.flat("#8c8577"),
            profile=("bevel", 1.5, 2), alpha=0.35)


def notes_pad(c, hue: float = 48, cy: float = CY, print_lines: bool = True,
              yellow: bool = False) -> None:
    """A ruled paper pad with a curled corner and a pencil resting on it."""
    cx = CX
    w, h = 560, 660
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    block = RRect(cx, cy, w, h, 10)
    if yellow:
        sheet, sheet_opts = M.enamel, dict(hue=52, sat=0.30, light=0.86, gloss=0.22)
    else:
        sheet, sheet_opts = M.paper, dict(warm=1.0)
    c.paint(Moved(block, 0, 14), sheet, profile=("bevel", 6, 10), **sheet_opts)
    c.paint(block, sheet, profile=("bevel", 10, 16), shadow=True, contact=0.2,
            **sheet_opts)
    # glued pad edge at the top
    c.paint(RRect(cx, y0 + 18, w, 40, 8), sheet, profile=("bevel", 4, 6),
            contact=0.2, **sheet_opts)
    c.paint_mask(stripe_mask((x0 + 10, y0 + 30, x1 - 10, y0 + 36), 18, 3.0, vertical=True),
                 M.flat("#c9c0aa"), emboss=0.8, alpha=0.35)
    if print_lines:
        _text_lines(c, (x0 + 58, y0 + 120, x1 - 52, y1 - 70), 12, 4.4, ink=M.flat("#4a5464"))
        c.paint(Capsule(x0 + 62, y0 + 92, x1 - 62, y0 + 92, 3), M.flat("#9fbfd8"),
                profile=("bevel", 1.4, 2), alpha=0.45)
    # curled lower-right corner, lifted
    curl = Poly([(x1 - 150, y1), (x1, y1 - 150), (x1 - 14, y1 - 20), (x1 - 20, y1 - 14)],
                rounding=6)
    c.paint(curl, sheet, profile=("bevel", 8, 12), shadow=True, contact=0.25, **sheet_opts)
    pencil = Rotated(Capsule(cx + 40, cy - 250, cx + 300, cy + 210, 17), 0, cx, cy)
    c.paint(pencil, M.enamel, profile=("bevel", 6, 9), hue=44, sat=0.62, light=0.52,
            shadow=True, contact=0.18)
    c.paint(Rotated(Poly([(cx + 288, cy + 178), (cx + 330, cy + 260), (cx + 258, cy + 214)],
                         rounding=4), 0, cx, cy), M.wood, profile=("bevel", 4, 6), hue=32,
            sat=0.45, light=0.42)
    c.paint(Rotated(Capsule(cx + 34, cy - 244, cx + 74, cy - 160, 17), 0, cx, cy),
            M.leather, profile=("bevel", 5, 7), hue=8, sat=0.4, light=0.36, contact=0.2)
    c.paint(Rotated(Capsule(cx + 26, cy - 258, cx + 36, cy - 240, 17), 0, cx, cy),
            M.chrome, profile=("bevel", 4, 6), contact=0.2)


def calendar_pad(c, hue: float = 8, cy: float = CY, day: int = 0) -> None:
    """A desk calendar on a wire binding: printed grid, one accent day."""
    cx = CX
    w, h = 560, 520
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2 + 40, cx + w / 2, cy + h / 2 + 40
    c.paint(Moved(RRect(cx, cy + 60, w, h, 10), 6, 16), M.paper, profile=("flat",))
    c.paint(RRect(cx, cy + 60, w, h, 10), M.paper, profile=("bevel", 8, 12), shadow=True,
            contact=0.2)
    # red header band with the month, printed rather than lettered
    c.paint(RRect(cx, y0 + 46, w - 24, 96, 8), M.enamel, profile=("bevel", 5, 8), hue=hue,
            sat=0.55, light=0.44, contact=0.22)
    for i in range(3):
        c.paint(Capsule(x0 + 56 + i * 26, y0 + 46, x0 + 56 + i * 26, y0 + 46, 4),
                M.flat("#ffffff"), alpha=0.0)
    for i in range(7):
        y = y0 + 112 + i * 58
        c.paint(Capsule(x0 + 34, y, x1 - 34, y, 2), M.flat("#9aa0a8"),
                profile=("bevel", 1, 1.5), alpha=0.35)
    for j in range(1, 7):
        x = x0 + 34 + j * ((w - 68) / 7)
        c.paint(Capsule(x, y0 + 112, x, y1 - 30, 2), M.flat("#9aa0a8"),
                profile=("bevel", 1, 1.5), alpha=0.30)
    # the day itself, one printed enamel block in the second row
    c.paint(RRect(x0 + 34 + ((w - 68) / 7) * 1.5, y0 + 141, 74, 50, 6), M.enamel,
            profile=("bevel", 4, 6), hue=hue, sat=0.6, light=0.52, contact=0.2)
    # wire binding
    for i in range(9):
        x = x0 + 34 + i * ((w - 68) / 8)
        c.paint(Rotated(ring(x, y0 + 6, 17, 7), 0, x, y0), M.chrome, profile=("bevel", 3, 4),
                shadow=True, contact=0.2)


def photo_print(c, hue: float = 208, cy: float = CY) -> None:
    """A glossy print with a white border, stacked with two more behind."""
    cx = CX
    for i, (dx, rot) in enumerate(((-30, 7), (16, -3), (0, 0))):
        frame = Rotated(RRect(cx + dx, cy + 10, 560, 660, 6), rot, cx, cy)
        c.paint(Moved(frame, 0, 14), M.paper, profile=("flat",), contact=0.1)
        c.paint(frame, M.paper, profile=("bevel", 4, 6), shadow=True, contact=0.16)
        if i == 2:
            inner = Rotated(RRect(cx, cy - 10, 500, 560, 3), rot, cx, cy)
            c.paint(inner, M.flat("#2b313a"), profile=("bevel", 2, 3))
            _landscape(c, (cx - 250, cy - 290, cx + 250, cy + 270), hue=hue)
            # gloss across the print, the way a lab print catches the light
            c.paint_mask(np.clip((inner.sdf(c.X, c.Y) < 0).astype(np.float32)
                                 * (1.0 - clamp01((c.Y - (cy - 330)) / 380.0)) * 0.16, 0, 1),
                         M.flat("#ffffff"), alpha=0.5)


def _landscape(c, box, hue: float = 208) -> None:
    """A small printed photograph: graded sky, two hills and a low sun."""
    x0, y0, x1, y1 = box
    cxp, cyp = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = x1 - x0, y1 - y0
    c.paint(RRect(cxp, cyp, w, h, 4), M.flat("#20252c"), profile=("bevel", 2, 3))
    inside = np.clip(0.5 - (RRect(cxp, cyp, w - 8, h - 8, 3).sdf(c.X, c.Y)), 0.0, 1.0)
    sky = RRect(cxp, cyp, w - 8, h - 8, 3)
    c.paint(sky, M.enamel, profile=("flat",), hue=(hue + 8) % 360, sat=0.34,
            light=0.70, gloss=0.0, mask=inside)
    horizon = y0 + h * 0.62
    c.paint_mask(inside * clamp01((c.Y - horizon) / (h * 0.5)), M.flat("#7d9a86"),
                 alpha=0.85)
    for ex, ey, rx, ry, tone in ((-0.22, 0.0, 0.40, 0.16, "#3f5a4c"),
                                 (0.24, 0.04, 0.44, 0.19, "#2e463a")):
        c.paint(Ellipse(cxp + w * ex, horizon + h * ey - ry * 0.2, w * rx, h * ry),
                M.enamel, profile=("sphere", 18), hue=136, sat=0.26, light=0.34,
                gloss=0.1, mask=inside)
    c.paint(Circle(x0 + w * 0.72, y0 + h * 0.22, max(8.0, w * 0.06)),
            M.flat("#fff6da"), profile=("sphere", 10), alpha=0.9)
    c.paint_mask(inside * clamp01((horizon - c.Y) / (h * 0.55)), M.flat("#ffffff"),
                 alpha=0.10)


def paper_stack(c, hue: float = 208, cy: float = CY, printed: str = "lines") -> None:
    """One sheet lying on a small pile, folded corner and printed content."""
    from .toolkit import paper
    paper(c, hue=hue, printed=printed, w=540, h=690, cy=cy)


def book_open(c, hue: float = 40, cy: float = CY, glyph: str = "book") -> None:
    """A thick book lying open: two pages of print over a leather spine."""
    cx = CX
    for sign in (-1, 1):
        page = Poly([(cx + sign * 24, cy - 150), (cx + sign * 420, cy - 210),
                     (cx + sign * 400, cy + 200), (cx + sign * 20, cy + 240)], rounding=8)
        c.paint(Moved(page, 0, 10), M.paper, profile=("flat",))
        c.paint(page, M.paper, profile=("bevel", 6, 10), shadow=True, contact=0.2)
        _text_lines(c, (min(cx + sign * 76, cx + sign * 356), cy - 150,
                        max(cx + sign * 76, cx + sign * 356), cy + 150), 7, 3.8)
    c.paint(Ellipse(cx, cy + 40, 60, 200), M.leather, profile=("sphere", 40), hue=hue,
            sat=0.36, light=0.24, contact=0.3)
    c.paint(Capsule(cx, cy + 190, cx, cy + 246, 6), M.brass, profile=("bevel", 3, 4))
    mark(c, glyph, cx, cy + 30, 54, M.brass, emboss=2.0)


# --------------------------------------------------------------------------- #
# music and video
# --------------------------------------------------------------------------- #

def record_sleeve(c, hue: float = 330, cy: float = CY, record: bool = True) -> None:
    """A card album sleeve with the record half out of it (or still inside)."""
    cx = CX
    sleeve = RRect(cx - 30, cy, 540, 560, 6)
    c.paint(Moved(sleeve, 0, 18), M.paper, profile=("flat",))
    c.paint(sleeve, M.paper, profile=("bevel", 6, 10), shadow=True, contact=0.2)
    c.paint(RRect(cx - 30, cy - 180, 500, 170, 4), M.enamel, profile=("bevel", 4, 6),
            hue=hue, sat=0.34, light=0.42, contact=0.15)
    c.paint_mask(stripe_mask((cx - 270, cy - 120, cx + 210, cy - 112), 3, 3.0),
                 M.flat("#ffffff"), emboss=0.8, alpha=0.25)
    if not record:
        c.paint(RRect(cx - 30, cy + 60, 470, 300, 4), M.flat("#20242b"),
                profile=("bevel", 3, 4), alpha=0.75)
        _photo(c, (cx - 240, cy - 40, cx + 120, cy + 190), hue=(hue + 160) % 360)
        c.paint(RRect(cx - 30, cy + 6, 470, 26, 3), M.flat("#f2eee4"),
                profile=("bevel", 2, 3), alpha=0.85)
        return
    disc = Circle(cx + 96, cy + 6, 248)
    c.paint(Moved(disc, 0, 16), M.gunmetal, profile=("bevel", 8, 12))
    c.paint(disc, M.flat("#14171c"), profile=("bevel", 6, 10), shadow=True, contact=0.24)
    c.paint_mask(radial_ticks(cx + 96, cy + 6, 96, 240, 72, 1.4), M.flat("#3d444e"),
                 emboss=0.6, alpha=0.5)
    c.paint(Circle(cx + 96, cy + 6, 92), M.enamel, profile=("bevel", 4, 6), hue=hue,
            sat=0.40, light=0.46, contact=0.2)
    c.paint(Circle(cx + 96, cy + 6, 14), M.chrome, profile=("sphere", 10), contact=0.2)
    c.paint(ring(cx + 96, cy + 6, 34, 5), M.flat("#0c0f13"), profile=("bevel", 2, 3),
            alpha=0.6)


def film_reel(c, hue: float = 208, cy: float = CY) -> None:
    """A 35 mm film reel with a strip of frames running out of it."""
    cx = CX
    strip = Poly([(cx - 320, cy + 250), (cx + 300, cy + 96), (cx + 320, cy + 150),
                  (cx - 300, cy + 306)], rounding=6)
    c.paint(strip, M.flat("#2a2622"), profile=("bevel", 4, 6), shadow=True, contact=0.18)
    for i in range(5):
        x = cx - 250 + i * 130
        y = cy + 236 - i * 40
        c.paint(Rotated(RRect(x, y, 74, 60, 4), -14, x, y), M.optic,
                profile=("bevel", 3, 4), hue=hue)
        c.paint(Rotated(RRect(x, y - 44, 62, 12, 3), -14, x, y), M.flat("#0d0f12"))
        c.paint(Rotated(RRect(x, y + 42, 62, 12, 3), -14, x, y), M.flat("#0d0f12"))
    reel = Circle(cx - 20, cy - 60, 268)
    c.paint(Moved(reel, 0, 20), M.steel, profile=("bevel", 10, 14))
    c.paint(reel, M.aluminium, profile=("sphere", 220), shadow=True, contact=0.24)
    c.paint(ring(cx - 20, cy - 60, 238, 26), M.gunmetal, profile=("bevel", 8, 12),
            contact=0.24)
    c.paint(Circle(cx - 20, cy - 60, 74), M.steel, profile=("bevel", 8, 12), contact=0.3)
    c.paint(Circle(cx - 20, cy - 60, 34), M.chrome, profile=("sphere", 24), contact=0.3)
    for i in range(6):
        a = math.radians(i * 60 + 15)
        hx, hy = cx - 20 + 168 * math.cos(a), cy - 60 + 168 * math.sin(a)
        c.paint(Circle(hx, hy, 46), M.flat("#171b20"), profile=("bevel", 3, 4), contact=0.2)


def clapper(c, hue: float = 208, cy: float = CY) -> None:
    """A slate: chalked board, hinged clapstick raised a little."""
    cx = CX
    board = Rotated(RRect(cx, cy + 60, 600, 430, 12), -4, cx, cy)
    c.paint(Moved(board, 0, 18), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(board, M.flat("#23262b"), profile=("bevel", 14, 20), shadow=True, contact=0.22)
    c.paint(Rotated(RRect(cx, cy + 52, 560, 380, 8), -4, cx, cy), M.flat("#2b2f35"),
            profile=("bevel", 6, 10), contact=0.25)
    for i in range(4):
        c.paint_mask(stripe_mask((cx - 240, cy - 80 + i * 92, cx + 250, cy - 40 + i * 92), 3,
                                 12.0), M.flat("#d8d4c8"), emboss=0.8, alpha=0.28)
    stick = Rotated(RRect(cx - 10, cy - 300, 620, 96, 10), -14, cx, cy - 300)
    c.paint(Moved(stick, 0, 12), M.gunmetal, profile=("bevel", 8, 12))
    c.paint(stick, M.flat("#1d2025"), profile=("bevel", 12, 18), shadow=True, contact=0.24)
    c.paint_mask(stripe_mask((cx - 300, cy - 340, cx + 290, cy - 262), 6, 42.0),
                 M.flat("#e6e2d6"), emboss=1.0, alpha=0.55)
    c.paint(Circle(cx - 290, cy - 262, 15), M.chrome, profile=("sphere", 11), contact=0.2)
    c.paint(Circle(cx + 290, cy - 262, 15), M.chrome, profile=("sphere", 11), contact=0.2)


def slide_carousel(c, hue: float = 24, cy: float = CY) -> None:
    """Glass-mounted transparencies standing in a walnut slide tray."""
    cx = CX
    tray = Poly([(cx - 340, cy + 90), (cx + 340, cy + 90), (cx + 306, cy + 286),
                 (cx - 306, cy + 286)], rounding=22)
    c.paint(Moved(tray, 0, 18), M.wood, profile=("bevel", 10, 14), hue=hue)
    c.paint(tray, M.wood, profile=("bevel", 18, 24), hue=hue, shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 88, 660, 30, 10), M.felt, profile=("bevel", 5, 7), hue=hue,
            sat=0.30, light=0.24, contact=0.3)
    for i, (dx, dy, rot) in enumerate(((-206, 26, -8), (0, -34, 0), (206, 26, 8))):
        glass = Rotated(RRect(cx + dx, cy + dy - 96, 300, 210, 8), rot, cx + dx, cy + dy)
        c.paint(Moved(glass, 0, 14), M.flat("#4a4136"), profile=("bevel", 5, 7))
        c.paint(glass, M.flat("#d8cfb6"), profile=("bevel", 6, 10), shadow=True, contact=0.2)
        inner = Rotated(RRect(cx + dx, cy + dy - 96, 250, 160, 4), rot, cx + dx, cy + dy)
        c.paint(inner, M.paper, profile=("flat",), alpha=0.4)
        _photo(c, (cx + dx - 124, cy + dy - 176, cx + dx + 124, cy + dy - 18),
               hue=(hue + 160 + i * 30) % 360)
        c.paint_mask(np.clip(0.55 - inner.sdf(c.X, c.Y), 0, 1)
                     * (1.0 - clamp01((c.Y - (cy + dy - 200)) / 170.0)) * 0.35,
                     M.flat("#ffffff"), alpha=0.5)
    c.paint(Capsule(cx - 300, cy + 236, cx + 300, cy + 236, 5), M.brass,
            profile=("bevel", 2, 3), alpha=0.35)


# --------------------------------------------------------------------------- #
# hardware and instruments
# --------------------------------------------------------------------------- #

def glass_keycap(c, glyph: str = "code", hue: float = 206, cy: float = CY,
                 shape: str = "key", tone: str = "glass") -> None:
    """A key on a milled plinth: dark glass, ivory or navy (the editor family)."""
    cx = CX
    if shape == "round":
        body, top = Circle(cx, cy + 10, 214), Circle(cx, cy - 18, 180)
        plinth_w = 500
    elif shape == "wide":
        body, top = RRect(cx, cy + 10, 520, 330, 52), RRect(cx, cy - 16, 448, 262, 40)
        plinth_w = 600
    else:
        body, top = RRect(cx, cy + 10, 440, 400, 56), RRect(cx, cy - 16, 372, 328, 44)
        plinth_w = 560
    plinth = RRect(cx, cy + 240, plinth_w, 96, 16)
    c.paint(Moved(plinth, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(plinth, M.aluminium, profile=("bevel", 16, 24), shadow=True, contact=0.22)
    c.paint(Moved(body, 0, 30), M.gunmetal, profile=("bevel", 12, 18))
    c.paint(body, M.rubber, profile=("bevel", 22, 30), shadow=True, contact=0.24)
    if tone == "ivory":
        cap = lambda ctx, **k: M.ivory(ctx, **k)
        c.paint(top, cap, profile=("bevel", 22, 30), shadow=True, contact=0.26)
        mark(c, glyph, cx, cy - 16, 160, lambda ctx, **k: M.engraved(ctx, light=0.42, **k),
             emboss=3.0)
    else:
        light = 0.24 if tone == "glass" else 0.30
        sat = 0.36 if tone == "glass" else 0.46
        c.paint(top, M.glass, profile=("bevel", 16, 24), hue=hue, sat=sat, light=light,
                gloss=0.75, contact=0.3)
        inner = top if shape == "round" else RRect(cx, cy - 16, top.bounds()[2] - top.bounds()[0] - 36,
                                                   top.bounds()[3] - top.bounds()[1] - 36, 38)
        c.paint(inner, M.glass, profile=("bevel", 10, 16), hue=hue, sat=sat - 0.06,
                light=light - 0.04, gloss=0.5, contact=0.3)
        mark(c, glyph, cx, cy - 16, 168, M.embossed_white, emboss=4.0)
    c.paint(Capsule(cx - 150, cy + 152, cx + 150, cy + 152, 4), M.flat("#8d949e"),
            profile=("bevel", 2, 3), alpha=0.45)


def cartridge(c, hue: float = 30, cy: float = CY) -> None:
    """A moulded game cartridge standing in its sleeve."""
    cx = CX
    sleeve = RRect(cx - 30, cy + 10, 480, 500, 14)
    c.paint(Moved(sleeve, 0, 18), M.rubber, profile=("bevel", 10, 14))
    c.paint(sleeve, M.rubber, profile=("bevel", 16, 22), shadow=True, contact=0.22)
    c.paint(RRect(cx - 30, cy - 150, 420, 120, 8), M.paper, profile=("bevel", 4, 6),
            hue=40, sat=0.10, light=0.84, contact=0.2)
    _text_lines(c, (cx - 210, cy - 190, cx + 150, cy - 110), 3, 4.0)
    shell = RRect(cx + 30, cy + 6, 400, 460, 22)
    c.paint(Moved(shell, 0, 20), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(shell, M.enamel, profile=("bevel", 18, 24), hue=hue, sat=0.38, light=0.46,
            shadow=True, contact=0.24)
    c.paint(RRect(cx + 30, cy - 120, 330, 170, 12), M.paper, profile=("bevel", 4, 6),
            hue=40, sat=0.10, light=0.86, contact=0.2)
    _photo(c, (cx - 100, cy - 175, cx + 160, cy - 40), hue=(hue + 180) % 360)
    c.paint_mask(stripe_mask((cx - 70, cy + 90, cx + 130, cy + 170), 5, 5.0),
                 M.flat("#1b1e23"), emboss=1.2, alpha=0.55)
    for i in range(6):
        c.paint(Capsule(cx - 130 + i * 54, cy + 186, cx - 130 + i * 54, cy + 206, 5),
                M.brass, profile=("bevel", 2, 3), contact=0.2)


def chess_knight(c, hue: float = 34, cy: float = CY) -> None:
    """A turned ivory pawn: foot, collar, tapered body and a ball head."""
    cx = CX
    c.paint(Ellipse(cx, cy + 302, 256, 62), M.ivory, profile=("sphere", 52), shadow=True,
            contact=0.24)
    c.paint(RRect(cx, cy + 268, 430, 74, 28), M.ivory, profile=("bevel", 14, 20),
            contact=0.26)
    c.paint(Ellipse(cx, cy + 226, 196, 40), M.ivory, profile=("bevel", 10, 14), contact=0.25)
    body = Poly([(cx - 122, cy + 220), (cx - 96, cy + 40), (cx - 54, cy - 20),
                 (cx + 54, cy - 20), (cx + 96, cy + 40), (cx + 122, cy + 220)],
                rounding=30)
    c.paint(Moved(body, 0, 24), M.ivory, profile=("sphere", 140))
    c.paint(body, M.ivory, profile=("sphere", 150), shadow=True, contact=0.26)
    c.paint(Circle(cx, cy - 96, 74), M.ivory, profile=("bevel", 10, 14), contact=0.3)
    c.paint(Circle(cx, cy - 176, 118), M.ivory, profile=("sphere", 104), shadow=True,
            contact=0.28)
    c.paint(ring(cx, cy - 92, 78, 14), M.ivory, profile=("bevel", 6, 9), contact=0.25)
    c.paint(Capsule(cx, cy + 150, cx + 74, cy + 150, 4), M.engraved, emboss=1.4, alpha=0.35)
    c.paint_mask(radial_ticks(cx, cy + 272, 128, 166, 48, 2.0), M.engraved, emboss=0.8,
                 alpha=0.25)


def game_tiles(c, hue: float = 150, cy: float = CY) -> None:
    """Three ivory playing tiles in a walnut rack (puzzles and board games)."""
    cx = CX
    rack = Poly([(cx - 330, cy + 150), (cx + 330, cy + 150), (cx + 290, cy + 312),
                 (cx - 290, cy + 312)], rounding=20)
    c.paint(Moved(rack, 0, 18), M.wood, profile=("bevel", 10, 14))
    c.paint(rack, M.wood, profile=("bevel", 16, 22), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 148, 640, 32, 10), M.felt, profile=("bevel", 6, 8), hue=hue,
            sat=0.35, light=0.28, contact=0.3)
    for i, (dx, dy, rot) in enumerate(((-176, 0, -5), (0, -34, 0), (176, 0, 5))):
        tile = Rotated(RRect(cx + dx, cy + dy - 40, 250, 280, 26), rot, cx + dx, cy + dy)
        c.paint(Moved(tile, 0, 20), M.ivory, profile=("bevel", 10, 14), hue=40, sat=0.06,
                light=0.70)
        c.paint(tile, M.ivory, profile=("bevel", 22, 30), hue=40, sat=0.06, light=0.86,
                shadow=True, contact=0.24)
        for r in range(3):
            for col in range(3):
                if (i * 3 + r + col) % 4 == 3:
                    continue
                c.paint(Rotated(Circle(cx + dx - 62 + col * 62, cy + dy - 148 + r * 66, 13),
                                rot, cx + dx, cy + dy),
                        M.engraved, profile=("sphere", 10), hue=hue, sat=0.5, light=0.35)
    c.paint(Capsule(cx, cy + 286, cx, cy + 286, 6), M.brass, profile=("sphere", 5),
            contact=0.2)


def clock_dial(c, hue: float = 208, cy: float = CY) -> None:
    """A brass-rimmed glass clock: printed minute track, blued steel hands."""
    cx = CX
    case = Circle(cx, cy, 330)
    c.paint(Moved(case, 0, 26), M.brass, profile=("bevel", 12, 16))
    c.paint(case, M.brass, profile=("sphere", 280), shadow=True, contact=0.24)
    c.paint(Circle(cx, cy, 292), M.paper, profile=("bevel", 8, 12), contact=0.35)
    c.paint_mask(radial_ticks(cx, cy, 248, 276, 60, 3.0), M.flat("#2b313a"), emboss=1.0,
                 alpha=0.85)
    c.paint_mask(radial_ticks(cx, cy, 216, 272, 12, 7.0), M.flat("#1f242b"), emboss=1.4,
                 alpha=0.9)
    c.paint(Rotated(Capsule(cx, cy + 20, cx - 40, cy - 150, 11), 0, cx, cy),
            M.enamel, profile=("bevel", 4, 6), hue=hue, sat=0.30, light=0.26, contact=0.3)
    c.paint(Rotated(Capsule(cx, cy + 20, cx + 130, cy + 60, 8), 0, cx, cy),
            M.enamel, profile=("bevel", 3, 5), hue=hue, sat=0.30, light=0.26, contact=0.3)
    c.paint(Capsule(cx, cy + 30, cx, cy - 90, 3), M.flat("#a8432f"),
            profile=("bevel", 1.5, 2), alpha=0.8)
    c.paint(Circle(cx, cy, 26), M.chrome, profile=("sphere", 18), contact=0.3)
    c.paint(ring(cx, cy, 330, 16), M.chrome, profile=("sphere", 12), contact=0.2)
    # the glass dome, one soft highlight in the upper left
    c.paint_mask(np.clip((Circle(cx, cy, 292).sdf(c.X, c.Y) < 0).astype(np.float32)
                         * (1.0 - clamp01((c.Y - (cy - 260)) / 230.0)) * 0.20, 0, 1),
                 M.flat("#ffffff"), alpha=0.55)


def volume_knob(c, hue: float = 208, cy: float = CY) -> None:
    """A machined volume knob on a brush-finished faceplate."""
    cx = CX
    plate = RRect(cx, cy + 150, 640, 290, 24)
    c.paint(Moved(plate, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(plate, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22,
            brush=0.03)
    knob = Circle(cx, cy - 40, 220)
    c.paint(Moved(knob, 0, 26), M.steel, profile=("sphere", 190))
    c.paint(knob, M.chrome, profile=("sphere", 210), shadow=True, contact=0.3)
    c.paint(ring(cx, cy - 40, 150, 26), M.gunmetal, profile=("bevel", 6, 9), contact=0.3)
    c.paint_mask(radial_ticks(cx, cy - 40, 164, 206, 60, 3.0), M.flat("#4b525c"),
                 emboss=0.8, alpha=0.45)
    c.paint(Rotated(Capsule(cx, cy - 40, cx, cy - 196, 9), 18, cx, cy - 40),
            M.enamel, profile=("bevel", 4, 6), hue=hue, sat=0.55, light=0.48, contact=0.2)
    for i in range(3):
        c.paint(Capsule(cx - 250 + i * 250, cy + 210, cx - 210 + i * 250, cy + 210, 6),
                M.brass, profile=("bevel", 3, 4), contact=0.2)
    c.paint(Circle(cx + 250, cy + 140, 12), M.lamp, profile=("sphere", 9), hue=140)


def barometer(c, hue: float = 200, cy: float = CY) -> None:
    """A brass barometer: dual scale, a needle and a small weather dial."""
    cx = CX
    plate = Circle(cx, cy, 320)
    c.paint(Moved(plate, 0, 24), M.brass, profile=("bevel", 12, 16))
    c.paint(plate, M.brass, profile=("sphere", 270), shadow=True, contact=0.24)
    c.paint(Circle(cx, cy, 278), M.paper, profile=("bevel", 6, 10), warm=0.4, contact=0.35)
    c.paint_mask(radial_ticks(cx, cy, 232, 262, 72, 2.6), M.flat("#2f333a"), emboss=0.9,
                 alpha=0.8)
    c.paint_mask(radial_ticks(cx, cy, 206, 258, 12, 6.0), M.flat("#1f242b"), emboss=1.2,
                 alpha=0.9)
    c.paint(Circle(cx, cy + 70, 84), M.ivory, profile=("bevel", 6, 9), contact=0.3)
    c.paint(Rotated(Capsule(cx, cy + 70, cx + 34, cy + 6, 9), 0, cx, cy),
            M.enamel, profile=("bevel", 3, 5), hue=200, sat=0.4, light=0.35)
    c.paint(Rotated(Capsule(cx, cy, cx - 60, cy - 180, 8), -20, cx, cy),
            M.flat("#8a2f22"), profile=("bevel", 3, 4), contact=0.25)
    c.paint(Circle(cx, cy, 22), M.chrome, profile=("sphere", 15), contact=0.3)
    c.paint(ring(cx, cy, 320, 18), M.chrome, profile=("sphere", 14), contact=0.2)


def brass_compass(c, hue: float = 205, cy: float = CY) -> None:
    """A surveyor's compass in a brass case: needle, rose and folding sight."""
    cx = CX
    case = Circle(cx, cy + 10, 316)
    c.paint(Moved(case, 0, 26), M.brass, profile=("bevel", 12, 16))
    c.paint(case, M.brass, profile=("sphere", 280), shadow=True, contact=0.24)
    c.paint(Circle(cx, cy + 10, 268), M.paper, profile=("bevel", 6, 10), warm=0.2,
            contact=0.35)
    c.paint_mask(radial_ticks(cx, cy + 10, 210, 252, 72, 2.6), M.flat("#2f333a"),
                 emboss=0.9, alpha=0.8)
    for i in range(4):
        a = math.radians(i * 90)
        x, y = cx + 168 * math.sin(a), cy + 10 - 168 * math.cos(a)
        c.paint(Rotated(Capsule(x, y, x, y, 9), 0, x, y), M.flat("#1f242b"), alpha=0.9)
    # the rose: four printed petals, one accent half
    for i in range(4):
        a = math.radians(i * 90)
        tip = (cx + 190 * math.sin(a), cy + 10 - 190 * math.cos(a))
        side = math.radians(i * 90 + 90)
        left = (cx + 44 * math.sin(side), cy + 10 - 44 * math.cos(side))
        right = (cx - 44 * math.sin(side), cy + 10 + 44 * math.cos(side))
        c.paint(Poly([tip, left, (cx, cy + 10)], rounding=4),
                M.enamel, profile=("bevel", 3, 4), hue=hue if i == 0 else 220,
                sat=0.55 if i == 0 else 0.10, light=0.42 if i == 0 else 0.55,
                contact=0.2)
        c.paint(Poly([tip, right, (cx, cy + 10)], rounding=4), M.paper,
                profile=("bevel", 3, 4), contact=0.15)
    c.paint(Circle(cx, cy + 10, 26), M.chrome, profile=("sphere", 18), contact=0.3)
    # hinged sight at the top
    c.paint(Rotated(RRect(cx, cy - 330, 60, 90, 8), 0, cx, cy), M.brass,
            profile=("bevel", 5, 7), shadow=True, contact=0.2)
    c.paint(Rotated(ring(cx, cy, 316, 12), 0, cx, cy), M.chrome, profile=("sphere", 9),
            contact=0.2)


def _local(cx: float, cy: float, deg: float, dx: float, dy: float):
    """Point in a frame rotated by ``deg`` around ``(cx, cy)``."""
    a = math.radians(deg)
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def hammer(c, hue: float = 208, cy: float = CY) -> None:
    """A forged chrome hammer with an enamelled handle, lying at an angle."""
    cx = CX
    tilt = -34.0
    low = _local(cx, cy, tilt, -10, 330)
    high = _local(cx, cy, tilt, 8, -150)
    handle = Capsule(low[0], low[1], high[0], high[1], 34)
    c.paint(Moved(handle, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(handle, M.enamel, profile=("bevel", 12, 16), hue=hue, sat=0.48, light=0.40,
            shadow=True, contact=0.22)
    for dy in (250, 292):
        a = _local(cx, cy, tilt, -6, dy)
        b = _local(cx, cy, tilt, 26, dy)
        c.paint(Capsule(a[0], a[1], b[0], b[1], 10), M.leather, profile=("bevel", 4, 6),
                hue=hue, sat=0.28, light=0.24, contact=0.2)
    collar = _local(cx, cy, tilt, 4, -108)
    c.paint(Rotated(RRect(collar[0], collar[1], 132, 74, 14), tilt + 90, collar[0],
                    collar[1]), M.gunmetal, profile=("bevel", 8, 12), contact=0.35)
    u = (math.cos(math.radians(tilt)), math.sin(math.radians(tilt)))
    w = (-u[1], u[0])
    hc = _local(cx, cy, tilt, 0, -196)

    def at(across: float, along: float):
        return (hc[0] + u[0] * across + w[0] * along,
                hc[1] + u[1] * across + w[1] * along)

    head = [at(-196, -70), at(196, -70), at(196, 70), at(-196, 70)]
    c.paint(Poly(head, rounding=18), M.chrome, profile=("bevel", 20, 28),
            shadow=True, contact=0.3)
    face = [at(196, -78), at(252, -78), at(252, 78), at(196, 78)]
    c.paint(Poly(face, rounding=8), M.chrome, profile=("bevel", 8, 12), contact=0.35)
    claw = [at(-196, -70), at(-268, -46), at(-276, 62), at(-196, 70)]
    c.paint(Poly(claw, rounding=12), M.chrome, profile=("bevel", 10, 14),
            contact=0.3)
    for i in range(3):
        a = at(-150 + i * 70, -32)
        b = at(-150 + i * 70, 32)
        c.paint(Capsule(a[0], a[1], b[0], b[1], 4), M.engraved, alpha=0.3)


def patch_panel(c, hue: float = 200, cy: float = CY) -> None:
    """A patch panel: jacks, one plugged cable and a row of link lamps."""
    cx = CX
    panel = RRect(cx, cy, 680, 420, 30)
    c.paint(Moved(panel, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(panel, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22,
            brush=0.02)
    for r in range(2):
        for i in range(6):
            x = cx - 250 + i * 100
            y = cy - 90 + r * 160
            c.paint(RRect(x, y, 74, 66, 10), M.gunmetal, profile=("bevel", 5, 8),
                    contact=0.3)
            c.paint(Circle(x, y, 20), M.flat("#14181e"), profile=("bevel", 3, 4),
                    contact=0.25)
            c.paint(Capsule(x - 26, y + 26, x + 26, y + 26, 3), M.brass,
                    profile=("bevel", 2, 2), alpha=0.4)
    for i in range(3):
        c.paint(Circle(cx - 250 + i * 34, cy + 172, 10), M.lamp, profile=("sphere", 8),
                hue=(140, 44, 140)[i])
    plug = RRect(cx + 176, cy + 96, 96, 128, 14)
    c.paint(plug, M.enamel, profile=("bevel", 8, 12), hue=hue, sat=0.55, light=0.48,
            shadow=True, contact=0.3)
    c.paint(RRect(cx + 176, cy + 158, 44, 60, 8), M.rubber, profile=("bevel", 5, 7),
            contact=0.25)
    cable = Poly([(cx + 176, cy + 186), (cx + 250, cy + 300), (cx + 330, cy + 330)],
                 rounding=14)
    c.paint_mask(polyline_mask([(cx + 176, cy + 186), (cx + 250, cy + 300),
                               (cx + 340, cy + 320)], 26.0), M.rubber, emboss=4.0)


def pipe_branch(c, hue: float = 30, cy: float = CY) -> None:
    """A brass Y-junction: one line in, two out (a branch, a merge)."""
    cx = CX
    stem = Capsule(cx, cy + 60, cx, cy + 300, 46)
    arm_l = Capsule(cx, cy + 60, cx - 210, cy - 140, 46)
    arm_r = Capsule(cx, cy + 60, cx + 210, cy - 140, 46)
    c.paint(Moved(arm_l | arm_r | stem, 0, 26), M.brass, profile=("bevel", 10, 14))
    for shape in (arm_l, arm_r, stem):
        c.paint(shape, M.brass, profile=("sphere", 60), shadow=True, contact=0.2)
    for x, y in ((cx - 210, cy - 140), (cx + 210, cy - 140), (cx, cy + 300)):
        c.paint(Circle(x, y, 66), M.brass, profile=("sphere", 50), contact=0.25)
        c.paint(ring(x, y, 48, 12), M.engraved, profile=("bevel", 5, 7), alpha=0.5)
    c.paint(Circle(cx, cy + 54, 78), M.brass, profile=("sphere", 60), contact=0.3)
    c.paint(ring(cx, cy + 54, 60, 14), M.engraved, profile=("bevel", 5, 7), alpha=0.45)
    for i in range(3):
        a = math.radians(30 + i * 120)
        c.paint(Circle(cx + 60 * math.cos(a), cy + 54 + 60 * math.sin(a), 9), M.gunmetal,
                profile=("sphere", 7), contact=0.2)
    c.paint(Circle(cx + 160, cy + 250, 16), M.lamp, profile=("sphere", 12), hue=140)


def browser_globe(c, hue: float = 208, cy: float = CY) -> None:
    """A blue-glass globe with chrome meridians, on a brass meridian ring."""
    cx = CX
    c.paint(Ellipse(cx, cy + 300, 232, 54), M.wood, profile=("sphere", 42),
            shadow=True, contact=0.22)
    c.paint(Ellipse(cx, cy + 268, 150, 34), M.brass, profile=("bevel", 8, 12),
            contact=0.24)
    c.paint(Capsule(cx, cy + 110, cx, cy + 262, 24), M.brass,
            profile=("bevel", 8, 10))
    # meridian ring behind the globe
    c.paint(Rotated(_ring_oval(cx, cy, 292, 292, 20), -16, cx, cy), M.brass,
            profile=("bevel", 6, 8), shadow=True, contact=0.2)
    sphere = Circle(cx, cy, 250)
    c.paint(Moved(sphere, 0, 20), M.flat("#123a63"), profile=("sphere", 120))
    c.paint(sphere, M.glass, profile=("sphere", 210), hue=hue, sat=0.72, light=0.46,
            shadow=True, contact=0.22)
    # chrome graticule: meridians and parallels
    for rx in (86, 168, 248):
        c.paint(_ring_oval(cx, cy, max(6, rx), 250, 9), M.chrome,
                profile=("bevel", 3, 5), contact=0.2, alpha=0.85)
    for y in (-172, -96, 0, 96, 172):
        rx = math.sqrt(max(1.0, 250 ** 2 - y ** 2))
        c.paint(_ring_oval(cx, cy + y, rx, max(7.0, rx * 0.17), 8), M.chrome,
                profile=("bevel", 3, 5), contact=0.18, alpha=0.8)
    # one enamelled equator band
    c.paint(Ellipse(cx, cy, 250, 26), M.enamel, profile=("bevel", 6, 9), hue=hue,
            sat=0.70, light=0.46, contact=0.2)
    c.paint(Ellipse(cx, cy - 4, 244, 16), M.enamel, profile=("bevel", 4, 6), hue=hue,
            sat=0.60, light=0.56, alpha=0.85)
    # highlight
    c.paint(Ellipse(cx - 96, cy - 120, 64, 92), M.flat("#ffffff"),
            profile=("sphere", 40), alpha=0.22)
    c.paint(Circle(cx - 128, cy - 156, 22), M.flat("#ffffff"),
            profile=("sphere", 14), alpha=0.5)


def _ring_oval(cx: float, cy: float, rx: float, ry: float, width: float):
    return Ellipse(cx, cy, rx, ry) - Ellipse(cx, cy, max(1.0, rx - width),
                                             max(1.0, ry - width))


def desk_calculator(c, hue: float = 208, cy: float = CY) -> None:
    """A desk calculator: aluminium case, LCD window, ivory keys."""
    cx = CX
    body = RRect(cx, cy + 10, 470, 640, 30)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 28), shadow=True, contact=0.24,
            brush=0.025)
    c.paint(RRect(cx, cy - 210, 390, 150, 12), M.gunmetal, profile=("bevel", 6, 9),
            contact=0.32)
    c.paint(RRect(cx, cy - 216, 350, 112, 8), M.screen, profile=("bevel", 4, 6),
            hue=140, contact=0.3)
    c.paint(Capsule(cx + 120, cy - 216, cx + 150, cy - 216, 5), M.lamp,
            profile=("sphere", 4), hue=140, alpha=0.9)
    for r in range(4):
        for i in range(4):
            x = cx - 156 + i * 104
            y = cy - 84 + r * 100
            wide = r == 3 and i == 0
            key = RRect(x + (52 if wide else 0), y, 190 if wide else 84, 76, 16)
            c.paint(Moved(key, 0, 5), M.ivory, profile=("bevel", 4, 6), hue=40, sat=0.06,
                    light=0.66)
            c.paint(key, M.ivory, profile=("bevel", 9, 12), hue=40, sat=0.06, light=0.86,
                    shadow=True, contact=0.2)
            accent = r == 0 and i == 3
            if accent:
                c.paint(RRect(x + (52 if wide else 0), y, 190 if wide else 84, 76, 16),
                        M.enamel, profile=("bevel", 9, 12), hue=hue, sat=0.55, light=0.50,
                        contact=0.2)
    c.paint_mask(stripe_mask((cx - 200, cy + 292, cx + 200, cy + 300), 8, 3.0),
                 M.flat("#7d848e"), emboss=0.8, alpha=0.4)


def address_book(c, hue: float = 205, cy: float = CY) -> None:
    """A leather address book with thumb tabs and a ribbon marker."""
    cx = CX
    body = RRect(cx, cy, 470, 600, 20)
    c.paint(Moved(body, 0, 24), M.leather, profile=("bevel", 10, 14), hue=hue, sat=0.36,
            light=0.24)
    c.paint(body, M.leather, profile=("bevel", 16, 22), hue=hue, sat=0.28, light=0.28,
            shadow=True, contact=0.24)
    c.paint(RRect(cx - 206, cy, 20, 570, 8), M.paper, profile=("flat",), contact=0.2)
    for i in range(5):
        y = cy - 210 + i * 108
        tab = RRect(cx + 238, y, 34, 74, 8)
        c.paint(tab, M.enamel, profile=("bevel", 4, 6), hue=(hue + i * 14) % 360,
                sat=0.26, light=0.52, shadow=True, contact=0.2)
    seam = stitch_mask([(cx + 210, cy - 260), (cx + 210, cy + 260)], 16, 12, 4.0)
    c.paint_mask(seam, M.flat("#c9b68f"), emboss=1.6, alpha=0.4)
    c.paint(Rotated(RRect(cx, cy + 120, 150, 26, 8), 0, cx, cy), M.brass,
            profile=("bevel", 4, 6), contact=0.2)
    ribbon = Poly([(cx - 40, cy + 300), (cx - 40, cy + 420), (cx - 10, cy + 392),
                   (cx + 20, cy + 420), (cx + 20, cy + 300)], rounding=4)
    c.paint(ribbon, M.leather, profile=("bevel", 4, 6), hue=8, sat=0.45, light=0.34,
            shadow=True, contact=0.18)
    mark(c, "person", cx + 20, cy - 60, 130, M.brass, emboss=2.6)


def bubble(c, hue: float = 210, cy: float = CY, stitched: bool = True,
           tail: str = "left") -> None:
    """A glossy enamel speech bubble: integrated tail, bezel, optional stitching."""
    cx = CX
    body = RRect(cx, cy - 20, 580, 380, 90)
    if tail == "left":
        body = body | Poly([(cx - 210, cy + 120), (cx - 250, cy + 270),
                            (cx - 60, cy + 140)], rounding=14)
    else:
        body = body | Poly([(cx + 210, cy + 120), (cx + 250, cy + 270),
                            (cx + 60, cy + 140)], rounding=14)
    c.paint(Moved(body, 0, 26), M.gunmetal, profile=("bevel", 12, 18))
    c.paint(body, M.enamel, profile=("bevel", 22, 30), hue=hue, sat=0.30, light=0.52,
            gloss=0.85, shadow=True, contact=0.26)
    c.paint(RRect(cx, cy - 30, 510, 310, 74), M.enamel, profile=("bevel", 10, 16),
            hue=hue, sat=0.26, light=0.46, gloss=0.5, contact=0.3)
    _gloss_bubble(c, body, cy)
    if stitched:
        seam = stitch_mask([(cx - 236, cy - 150), (cx - 236, cy + 100)], 20, 14, 5.0)
        seam += stitch_mask([(cx + 236, cy - 150), (cx + 236, cy + 100)], 20, 14, 5.0)
        c.paint_mask(np.clip(seam, 0, 1), M.flat("#f4efe4"), emboss=2.0, alpha=0.55)


def _gloss_bubble(c, body, cy: float) -> None:
    mask = np.clip(0.55 - body.sdf(c.X, c.Y), 0.0, 1.0)
    ramp = 1.0 - clamp01((c.Y - (cy - 230)) / 190.0)
    c.paint_mask(mask * ramp * 0.55, M.flat("#ffffff"), alpha=0.45)


def ledger(c, hue: float = 112, cy: float = CY) -> None:
    """A bound ledger, open to a ruled page with a column of totals."""
    cx = CX
    page = Rotated(RRect(cx + 30, cy, 560, 680, 8), 3, cx, cy)
    c.paint(Moved(page, 0, 14), M.paper, profile=("flat",))
    c.paint(page, M.paper, profile=("bevel", 6, 10), shadow=True, contact=0.2)
    cover = Rotated(RRect(cx - 60, cy + 30, 170, 700, 12), 3, cx, cy)
    c.paint(cover, M.leather, profile=("bevel", 10, 14), hue=hue, sat=0.36, light=0.26,
            shadow=True, contact=0.2)
    c.paint_mask(grid_mask((cx - 150, cy - 260, cx + 270, cy + 250), 4, 14, 4.0),
                 M.flat("#5b6068"), emboss=0.8, alpha=0.45)
    for i in range(6):
        c.paint(Capsule(cx - 120, cy - 190 + i * 74, cx + 210 - i * 14, cy - 190 + i * 74,
                        4), M.ink, emboss=0.7, alpha=0.55)
    c.paint(Capsule(cx + 208, cy - 250, cx + 208, cy + 240, 4), M.enamel,
            profile=("bevel", 2, 3), hue=hue, sat=0.5, light=0.44, alpha=0.7)
    for i in range(4):
        c.paint(Circle(cx - 60 + 0, cy - 220 + i * 150, 12), M.brass,
                profile=("sphere", 9), contact=0.2)


def radio(c, hue: float = 34, cy: float = CY) -> None:
    """A valve radio: walnut case, cloth grille, glass dial and one knob."""
    cx = CX
    body = RRect(cx, cy + 20, 660, 470, 40)
    c.paint(Moved(body, 0, 26), M.wood, profile=("bevel", 12, 16), hue=hue)
    c.paint(body, M.wood, profile=("bevel", 22, 30), hue=hue, shadow=True, contact=0.24)
    c.paint(RRect(cx - 130, cy + 40, 340, 340, 24), M.flat("#3a3129"),
            profile=("bevel", 8, 12), contact=0.3)
    c.paint_mask(dots_mask(SIZE, 14, 4.0, bounds=(cx - 290, cy - 120, cx + 30, cy + 200)),
                 M.flat("#c9b48c"), emboss=1.2, alpha=0.35)
    c.paint(RRect(cx + 176, cy - 110, 260, 150, 12), M.glass, profile=("bevel", 8, 12),
            hue=hue + 160, sat=0.30, light=0.42, gloss=0.7, contact=0.3)
    c.paint(Capsule(cx + 60, cy - 60, cx + 290, cy - 60, 4), M.brass,
            profile=("bevel", 2, 3), alpha=0.6)
    c.paint(Capsule(cx + 170, cy - 40, cx + 170, cy - 120, 3), M.flat("#8a2f22"),
            profile=("bevel", 1.5, 2), alpha=0.7)
    for i, dy in enumerate((90, 160)):
        knob = Circle(cx + 110 + i * 130, cy + dy, 46)
        c.paint(Moved(knob, 0, 10), M.gunmetal, profile=("sphere", 38))
        c.paint(knob, M.chrome, profile=("sphere", 42), shadow=True, contact=0.26)
        c.paint(ring(cx + 110 + i * 130, cy + dy, 26, 6), M.engraved,
                profile=("bevel", 3, 4), alpha=0.4)
    for i in range(5):
        c.paint(Capsule(cx - 290, cy + 220 - i * 12, cx + 30, cy + 220 - i * 12, 3),
                M.flat("#2a231c"), alpha=0.5)


def paint_tin(c, hue: float = 20, cy: float = CY) -> None:
    """A paint tin with a brush laid across the rim and a drip of accent."""
    cx = CX
    tin = RRect(cx, cy + 40, 470, 470, 26)
    c.paint(Moved(tin, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(tin, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.24,
            brush=0.02)
    c.paint(Ellipse(cx, cy - 190, 235, 62), M.steel, profile=("bevel", 8, 12), contact=0.3)
    c.paint(Ellipse(cx, cy - 190, 210, 50), M.enamel, profile=("flat",), hue=hue, sat=0.62,
            light=0.42, contact=0.35)
    c.paint(Capsule(cx - 210, cy - 250, cx + 210, cy - 250, 12), M.chrome,
            profile=("bevel", 5, 7), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy + 110, 300, 200, 12), M.paper, profile=("flat",), contact=0.15)
    _text_lines(c, (cx - 130, cy + 40, cx + 130, cy + 180), 4, 4.0)
    brush = Capsule(cx - 190, cy - 300, cx + 170, cy - 330, 20)
    c.paint(brush, M.wood, profile=("bevel", 6, 9), hue=30, sat=0.42, light=0.38,
            shadow=True, contact=0.2)
    c.paint(Rotated(RRect(cx + 150, cy - 350, 90, 90, 16), 8, cx + 150, cy - 350),
            M.chrome, profile=("bevel", 6, 8), contact=0.2)
    c.paint(Rotated(Capsule(cx + 196, cy - 344, cx + 260, cy - 336, 22), 0, cx, cy),
            M.enamel, profile=("bevel", 6, 8), hue=hue, sat=0.6, light=0.44, contact=0.2)


def wire_cube(c, hue: float = 208, cy: float = CY) -> None:
    """A chrome rod cube with ball joints: modelling in three dimensions."""
    cx = CX
    plinth = RRect(cx, cy + 300, 520, 100, 22)
    c.paint(Moved(plinth, 0, 20), M.steel, profile=("bevel", 10, 14))
    c.paint(plinth, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    r = 250
    front = [(cx - r, cy - r * 0.95), (cx + r * 0.62, cy - r * 0.60),
             (cx + r * 0.62, cy + r * 0.72), (cx - r, cy + r * 0.44)]
    back = [(cx - r * 0.34, cy - r * 1.34), (cx + r * 0.94, cy - r),
            (cx + r * 0.94, cy + r * 0.34), (cx - r * 0.34, cy + r * 0.06)]
    rods = [(back[i], back[(i + 1) % 4]) for i in range(4)]
    rods += [(front[i], front[(i + 1) % 4]) for i in range(4)]
    rods += [(front[i], back[i]) for i in range(4)]
    for a, b in rods:
        c.paint(Capsule(a[0], a[1], b[0], b[1], 15), M.chrome,
                profile=("bevel", 7, 9), shadow=True, contact=0.18)
    for i in range(4):
        for pts, mat in ((front, M.aluminium), (back, M.gunmetal)):
            c.paint(Circle(pts[i][0], pts[i][1], 34), M.chrome,
                    profile=("sphere", 26), contact=0.3)
    face = [front[0], front[1], front[2], front[3]]
    c.paint(Poly(face, rounding=2), M.glass, profile=("flat",), hue=hue, sat=0.30,
            light=0.40, gloss=0.6, alpha=0.55)
    c.paint(Capsule(cx - r * 0.7, cy - r * 0.55, cx + r * 0.34, cy - r * 0.24, 3),
            M.flat("#ffffff"), profile=("bevel", 1.5, 2), alpha=0.35)


# --------------------------------------------------------------------------- #
# files, databases and cases
# --------------------------------------------------------------------------- #

def chrome_folder(c, hue: float = 210, cy: float = CY) -> None:
    """A brushed-steel folder with a tab, papers inside and a glass label."""
    cx = CX
    # back board with a tab on the left third
    back = Poly([(cx - 306, cy - 176), (cx - 150, cy - 176), (cx - 110, cy - 302),
                 (cx + 60, cy - 302), (cx + 106, cy - 176), (cx + 306, cy - 176),
                 (cx + 306, cy + 274), (cx - 306, cy + 274)], rounding=20)
    c.paint(Moved(back, 0, 22), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(back, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.24,
            brush=0.03)
    for i, off in enumerate((-30, -12, 6)):
        c.paint(Rotated(RRect(cx + 6, cy - 70 + off, 486, 400, 6), (i - 1) * 2.0, cx, cy),
                M.paper, profile=("flat",), contact=0.10)
        c.paint(Rotated(Capsule(cx - 170, cy - 190 + off, cx + 170, cy - 190 + off, 4),
                        (i - 1) * 2.0, cx, cy), M.flat("#8c96a2"),
                profile=("bevel", 1.5, 2), alpha=0.35)
    # front board, lower half, with a bright chrome lip
    front = Poly([(cx - 300, cy - 20), (cx + 300, cy - 20), (cx + 300, cy + 268),
                  (cx - 300, cy + 268)], rounding=22)
    c.paint(Moved(front, 0, 18), M.gunmetal, profile=("bevel", 8, 12))
    c.paint(front, M.aluminium, profile=("bevel", 22, 32), shadow=True, contact=0.26,
            brush=0.02)
    c.paint(Capsule(cx - 274, cy - 16, cx + 274, cy - 16, 6), M.chrome,
            profile=("sphere", 4), contact=0.2)
    # enamel label plate, the one colour
    label = RRect(cx - 188, cy + 116, 200, 92, 16)
    c.paint(Moved(label, 0, 8), M.gunmetal, profile=("bevel", 6, 9))
    c.paint(label, M.glass, profile=("sphere", 40), hue=hue, sat=0.68, light=0.48,
            shadow=True, contact=0.26)
    c.paint(Capsule(cx - 248, cy + 92, cx - 136, cy + 92, 5), M.flat("#ffffff"),
            profile=("bevel", 2, 2), alpha=0.30)
    # a paperclip holding the sheets
    clip = Poly([(cx + 214, cy - 250), (cx + 250, cy - 316), (cx + 286, cy - 306),
                 (cx + 262, cy - 210), (cx + 236, cy - 150), (cx + 216, cy - 164),
                 (cx + 238, cy - 222), (cx + 258, cy - 296), (cx + 248, cy - 300),
                 (cx + 226, cy - 230), (cx + 208, cy - 176)], rounding=10)
    c.paint(Moved(clip, 0, 6), M.flat("#2b3038"), profile=("bevel", 4, 6))
    c.paint(clip, M.chrome, profile=("bevel", 6, 9), shadow=True, contact=0.2)


def display_case(c, hue: float = 208, cy: float = CY) -> None:
    """A glass display case with a wrapped parcel on a plinth (a store)."""
    cx = CX
    base = RRect(cx, cy + 300, 560, 90, 16)
    c.paint(Moved(base, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(base, M.aluminium, profile=("bevel", 14, 20), shadow=True, contact=0.22)
    # the vitrine: a chrome frame, a glass front and a shelf of wrapped parcels
    case = RRect(cx, cy - 30, 500, 580, 14)
    c.paint(case, M.gunmetal, profile=("bevel", 8, 12), shadow=True, contact=0.24)
    inner = RRect(cx, cy - 30, 462, 542, 10)
    c.paint(inner, M.glass, profile=("flat",), hue=hue, sat=0.12, light=0.74, gloss=0.7,
            contact=0.3)
    for rect in (RRect(cx, cy - 312, 500, 22, 6), RRect(cx, cy + 252, 500, 22, 6),
                 RRect(cx - 244, cy - 30, 22, 580, 6), RRect(cx + 244, cy - 30, 22, 580, 6)):
        c.paint(rect, M.chrome, profile=("bevel", 6, 9), contact=0.2)
    c.paint(Capsule(cx + 216, cy + 30, cx + 216, cy + 30, 9), M.brass,
            profile=("sphere", 7), contact=0.2)
    shelf = RRect(cx, cy + 106, 462, 22, 6)
    c.paint(shelf, M.enamel, profile=("bevel", 5, 7), hue=hue, sat=0.34, light=0.44,
            contact=0.25)
    # lower shelf: two parcels; upper shelf: one, with twine and a bow
    c.paint(Rotated(RRect(cx - 110, cy + 190, 210, 150, 10), -4, cx - 110, cy + 190),
            M.paper, profile=("bevel", 8, 12), warm=0.4, shadow=True, contact=0.24)
    c.paint(Rotated(RRect(cx + 104, cy + 214, 150, 112, 10), 5, cx + 104, cy + 214),
            M.enamel, profile=("bevel", 8, 12), hue=hue, sat=0.34, light=0.52,
            shadow=True, contact=0.24)
    parcel = Rotated(RRect(cx + 10, cy - 96, 260, 210, 10), -5, cx + 10, cy - 96)
    c.paint(parcel, M.paper, profile=("bevel", 8, 12), warm=0.9, shadow=True, contact=0.24)
    c.paint_mask(polyline_mask([(cx - 90, cy - 200), (cx - 52, cy + 2)], 11.0), M.brass,
                 emboss=2.0)
    c.paint_mask(polyline_mask([(cx + 20, cy - 198), (cx + 52, cy + 0)], 11.0), M.brass,
                 emboss=2.0)
    c.paint(ring(cx + 6, cy - 190, 26, 9), M.brass, profile=("bevel", 4, 6), contact=0.2)
    for i in range(3):
        c.paint_mask(polyline_mask([(cx - 214 + i * 10, cy - 280 + i * 4),
                                    (cx - 140 + i * 10, cy - 240 + i * 4)], 5.0),
                     M.flat("#ffffff"), alpha=0.30)
    c.paint_mask(polyline_mask([(cx + 180, cy + 130), (cx + 180, cy + 200)], 3.0),
                 M.brass, emboss=1.2, alpha=0.6)


def card_catalog(c, hue: float = 44, cy: float = CY) -> None:
    """A brass-handled card-catalogue drawer, half open with index cards."""
    cx = CX
    body = RRect(cx, cy, 620, 540, 20)
    c.paint(Moved(body, 0, 24), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(body, M.wood, profile=("bevel", 18, 26), hue=28, sat=0.42, light=0.30,
            shadow=True, contact=0.24)
    for i in range(3):
        y = cy - 150 + i * 150
        drawer = RRect(cx, y, 540, 124, 12)
        c.paint(drawer, M.wood, profile=("bevel", 8, 12), hue=28, sat=0.45, light=0.34,
                contact=0.3)
        c.paint(RRect(cx, y, 470, 96, 8), M.gunmetal, profile=("bevel", 5, 8),
                contact=0.25)
        c.paint(Capsule(cx - 60, y, cx + 60, y, 16), M.brass, profile=("bevel", 6, 8),
                contact=0.2)
        c.paint(Capsule(cx - 40, y, cx + 40, y, 8), M.flat("#2a2620"),
                profile=("bevel", 3, 4), contact=0.2)
    drawer = RRect(cx + 40, cy + 180, 500, 96, 10)
    c.paint(drawer, M.wood, profile=("bevel", 8, 12), hue=28, sat=0.45, light=0.38,
            shadow=True, contact=0.24)
    for i in range(4):
        c.paint(Rotated(RRect(cx + 40 + i * 8, cy + 150 - i * 8, 430, 66, 6), 0, cx, cy),
                M.paper, profile=("flat",), contact=0.14)
    c.paint_mask(stripe_mask((cx - 150, cy + 130, cx + 210, cy + 136), 14, 3.0, vertical=True),
                 M.flat("#8c8474"), emboss=0.7, alpha=0.4)


# --------------------------------------------------------------------------- #
# misc
# --------------------------------------------------------------------------- #

def typewriter(c, hue: float = 208, cy: float = CY) -> None:
    """A portable typewriter with a sheet in the platen."""
    cx = CX
    deck = Poly([(cx - 340, cy + 120), (cx + 340, cy + 120), (cx + 290, cy + 280),
                 (cx - 290, cy + 280)], rounding=24)
    c.paint(Moved(deck, 0, 26), M.rubber, profile=("bevel", 12, 16))
    c.paint(deck, M.enamel, profile=("bevel", 20, 28), hue=hue, sat=0.32, light=0.34,
            shadow=True, contact=0.24)
    # platen and paper
    c.paint(Capsule(cx - 300, cy - 150, cx + 300, cy - 150, 52), M.rubber,
            profile=("bevel", 10, 14), contact=0.3)
    sheet = RRect(cx + 50, cy - 400, 470, 500, 6)
    c.paint(Moved(sheet, 0, 8), M.paper, profile=("flat",), contact=0.1)
    c.paint(sheet, M.paper, profile=("bevel", 4, 6), shadow=True, contact=0.16)
    _text_lines(c, (cx - 120, cy - 590, cx + 250, cy - 330), 8, 4.0)
    c.paint(RRect(cx + 50, cy - 200, 420, 60, 6), M.paper, profile=("flat",), warm=0.4,
            contact=0.2)
    # key rows and the type bars
    for r in range(3):
        for i in range(11 - r):
            x = cx - 230 + i * 46 + r * 22
            y = cy + 40 + r * 52
            c.paint(Rotated(RRect(x, y, 36, 36, 10), 0, x, y), M.ivory,
                    profile=("bevel", 5, 7), hue=40, sat=0.08, light=0.80, contact=0.2)
    c.paint(RRect(cx, cy + 226, 380, 30, 8), M.chrome, profile=("bevel", 5, 7),
            contact=0.25)
    c.paint(Circle(cx - 300, cy - 150, 26), M.chrome, profile=("sphere", 18), contact=0.2)
    c.paint(Circle(cx + 300, cy - 150, 26), M.chrome, profile=("sphere", 18), contact=0.2)


# --------------------------------------------------------------------------- #
# subjects for the GNOME and GTK families
# --------------------------------------------------------------------------- #

def puzzle_piece(c, hue: float = 206, cy: float = CY) -> None:
    """One ceramic jigsaw piece, its knob in blue glass: extensions, add-ons."""
    cx = CX
    base = RRect(cx - 30, cy + 20, 600, 620, 34)
    knob = Circle(cx + 300, cy + 20, 118)
    notch = Circle(cx - 30, cy - 290, 114)
    piece = (base | knob) - notch
    c.paint(Moved(piece, 0, 34), M.gunmetal, profile=("bevel", 12, 16))
    c.paint(piece, M.aluminium, profile=("bevel", 40, 52), shadow=True, contact=0.26)
    c.paint(Circle(cx + 300, cy + 20, 112), M.glass, profile=("sphere", 104), hue=hue,
            sat=0.56, light=0.48, gloss=0.72, contact=0.34)
    c.paint(Ellipse(cx + 268, cy - 22, 30, 40), M.flat("#ffffff"),
            profile=("sphere", 20), alpha=0.45)
    c.paint_mask(np.clip(5.0 - np.abs(piece.sdf(c.X, c.Y) + 26.0), 0, 1) * 0.4,
                 M.engraved, emboss=0.8, alpha=0.5)


def loupe(c, hue: float = 206, cy: float = CY) -> None:
    """A chromed magnifier lying across a printed photograph."""
    cx = CX
    sheet = Rotated(RRect(cx - 20, cy + 40, 560, 470, 8), -4, cx, cy)
    c.paint(Moved(sheet, 0, 16), M.flat("#8b8272"), profile=("flat",))
    c.paint(sheet, M.paper, profile=("bevel", 6, 10), shadow=True, contact=0.2)
    _photo(c, (cx - 230, cy - 120, cx + 160, cy + 180), hue=(hue + 150) % 360)
    _text_lines(c, (cx - 230, cy + 206, cx + 120, cy + 240), 2, 4.0)
    lx, ly, r = cx + 96, cy - 60, 238
    hx, hy = lx - r * 0.70, ly + r * 0.70
    c.paint(Moved(Capsule(hx, hy, hx - 190, hy + 190, 46), 0, 18), M.steel,
            profile=("bevel", 8, 12))
    c.paint(Capsule(hx, hy, hx - 190, hy + 190, 46), M.chrome, profile=("bevel", 16, 22),
            shadow=True, contact=0.2)
    c.paint(Capsule(hx - 60, hy + 60, hx - 170, hy + 170, 44), M.rubber,
            profile=("bevel", 10, 14), contact=0.25)
    c.paint(Moved(Circle(lx, ly, r), 0, 30), M.steel, profile=("bevel", 12, 16))
    c.paint(ring(lx, ly, r - 18, 38), M.chrome, profile=("bevel", 16, 22), shadow=True,
            contact=0.24)
    lens = Circle(lx, ly, r - 40)
    c.paint(lens, M.paper, profile=("bevel", 12, 18), contact=0.3)
    inside = np.clip(0.6 - lens.sdf(c.X, c.Y), 0.0, 1.0)
    c.paint_mask(inside * np.clip(0.5 - RRect(lx, ly - 78, 360, 250, 10).sdf(c.X, c.Y),
                                 0, 1), M.flat("#6ba7cd"), alpha=0.90)
    c.paint_mask(inside * np.clip(0.5 - Ellipse(lx + 24, ly + 128, 292, 210).sdf(c.X, c.Y),
                                 0, 1), M.flat("#6f8b5d"), alpha=0.92)
    c.paint_mask(inside * np.clip(0.5 - Ellipse(lx - 92, ly + 76, 190, 130).sdf(c.X, c.Y),
                                 0, 1), M.flat("#4f6b46"), alpha=0.75)
    c.paint_mask(inside * np.clip(0.5 - Circle(lx - 74, ly - 54, 36).sdf(c.X, c.Y), 0, 1),
                 M.flat("#f7f0d8"), alpha=0.95)
    c.paint_mask(inside, M.flat("#ffffff"), alpha=0.10)
    c.paint(lens, M.glass, profile=("bevel", 10, 16), hue=hue, sat=0.10, light=0.88,
            gloss=0.20, alpha=0.10, contact=0.2)
    c.paint(Ellipse(lx - 80, ly - 104, 104, 40), M.flat("#ffffff"),
            profile=("sphere", 30), alpha=0.55)


def gramophone(c, hue: float = 32, cy: float = CY) -> None:
    """A brass horn gramophone on a walnut plinth: music players."""
    cx = CX
    base = RRect(cx, cy + 292, 516, 196, 26)
    c.paint(Moved(base, 0, 18), M.flat("#3a2a18"), profile=("bevel", 10, 14))
    c.paint(base, M.wood, profile=("bevel", 22, 28), hue=hue, light=0.42, shadow=True,
            contact=0.22)
    c.paint(RRect(cx, cy + 198, 556, 30, 10), M.brass, profile=("bevel", 6, 9), contact=0.3)
    c.paint_mask(stripe_mask((cx - 240, cy + 246, cx + 240, cy + 336), 6, 4.0),
                 M.flat("#2b1c0c"), emboss=1.0, alpha=0.35)
    c.paint(Ellipse(cx - 30, cy + 190, 206, 66), M.flat("#16191d"),
            profile=("bevel", 8, 12), contact=0.24)
    c.paint(Ellipse(cx - 30, cy + 182, 146, 46), M.enamel, profile=("sphere", 90), hue=hue,
            sat=0.44, light=0.46, contact=0.2)
    c.paint(Circle(cx - 30, cy + 182, 13), M.chrome, profile=("sphere", 9))
    horn = ribbon([(cx + 96, cy + 176), (cx + 150, cy - 10), (cx + 262, cy - 190),
                   (cx + 356, cy - 330)], [56, 96, 158, 258], rounding=34)
    c.paint(Moved(horn, 0, 22), M.flat("#6b5220"), profile=("bevel", 10, 14))
    c.paint(horn, M.brass, profile=("sphere", 220), shadow=True, contact=0.22)
    bell = Rotated(Ellipse(cx + 350, cy - 336, 168, 120), -40, cx + 350, cy - 336)
    c.paint(Moved(bell, 0, 18), M.flat("#5d4519"), profile=("bevel", 8, 12))
    c.paint(bell, M.brass, profile=("bevel", 18, 24), contact=0.28)
    c.paint(Rotated(Ellipse(cx + 350, cy - 336, 134, 88), -40, cx + 350, cy - 336),
            M.flat("#33281630"), profile=("sphere", 60), contact=0.2)
    c.paint(Capsule(cx - 250, cy + 188, cx - 332, cy + 188, 12), M.brass,
            profile=("bevel", 4, 6))
    c.paint(Circle(cx - 340, cy + 188, 26), M.wood, profile=("sphere", 18), hue=hue,
            light=0.34, contact=0.2)


def cassette(c, hue: float = 206, cy: float = CY) -> None:
    """A smoked-plastic compact cassette with a hand-written label."""
    cx = CX
    shell = Poly([(cx - 372, cy - 216), (cx + 372, cy - 216), (cx + 372, cy + 132),
                  (cx + 300, cy + 222), (cx - 300, cy + 222), (cx - 372, cy + 132)],
                 rounding=18)
    c.paint(Moved(shell, 0, 24), M.rubber, profile=("bevel", 12, 16))
    c.paint(shell, M.glass, profile=("bevel", 26, 34), hue=hue, sat=0.12, light=0.34,
            gloss=0.55, shadow=True, contact=0.24)
    c.paint(RRect(cx, cy - 96, 636, 190, 10), M.paper, profile=("bevel", 6, 10),
            contact=0.26)
    _text_lines(c, (cx - 268, cy - 160, cx + 210, cy - 52), 1, 12.0)
    _text_lines(c, (cx - 268, cy - 40, cx + 268, cy - 12), 3, 4.4)
    c.paint(RRect(cx, cy + 84, 486, 182, 16), M.flat("#15181d"),
            profile=("bevel", 8, 12), contact=0.35)
    c.paint(RRect(cx, cy + 84, 486, 182, 16), M.flat("#2b3037"), alpha=0.5)
    for dx in (-126, 126):
        c.paint(Circle(cx + dx, cy + 84, 66), M.flat("#0f1216"), profile=("bevel", 4, 6))
        c.paint(ring(cx + dx, cy + 84, 52, 15), M.ivory, profile=("bevel", 4, 6),
                contact=0.24)
        c.paint(Circle(cx + dx, cy + 84, 30), M.flat("#e6e1d4"), profile=("sphere", 22),
                contact=0.28)
        c.paint_mask(radial_ticks(cx + dx, cy + 84, 12, 27, 6, 3.0), M.flat("#6d7278"),
                     emboss=1.0, alpha=0.8)
    c.paint(RRect(cx, cy + 84, 118, 74, 4), M.flat("#2a1d17"), alpha=0.95)
    c.paint(Capsule(cx - 190, cy + 152, cx + 190, cy + 152, 4), M.flat("#4b3a30"),
            alpha=0.55)
    for sx in (-320, 320):
        for sy in (-176, 178):
            c.paint(Circle(cx + sx, cy + sy, 17), M.chrome, profile=("sphere", 12),
                    contact=0.2)
    c.paint(RRect(cx, cy + 214, 250, 22, 6), M.flat("#0d1013"), alpha=0.75)


def tuning_fork(c, hue: float = 206, cy: float = CY) -> None:
    """A chrome tuning fork planted in a walnut block: instruments, tuners."""
    cx = CX
    block = RRect(cx, cy + 300, 300, 96, 28)
    c.paint(Moved(block, 0, 18), M.flat("#3a2a18"), profile=("bevel", 8, 12))
    c.paint(block, M.wood, profile=("bevel", 18, 24), hue=30, light=0.42, shadow=True,
            contact=0.22)
    c.paint(RRect(cx, cy + 288, 330, 26, 10), M.flat("#2b1e10"), profile=("bevel", 4, 6),
            contact=0.28)
    fork = (Capsule(cx - 92, cy - 340, cx - 92, cy - 20, 50)
            | Capsule(cx + 92, cy - 340, cx + 92, cy - 20, 50)
            | RRect(cx, cy + 8, 284, 236, 96)
            | Capsule(cx, cy + 70, cx, cy + 268, 48))
    c.paint(Moved(fork, 0, 30), M.flat("#4a5058"), profile=("bevel", 12, 16))
    c.paint(fork, M.chrome, profile=("sphere", 260), shadow=True, contact=0.24)
    for dx in (-92, 92):
        c.paint(Circle(cx + dx, cy - 344, 50), M.aluminium, profile=("sphere", 40),
                contact=0.3)
        c.paint(Capsule(cx + dx - 24, cy - 300, cx + dx - 24, cy - 150, 7),
                M.flat("#ffffff"), profile=("bevel", 3, 4), alpha=0.45)
    c.paint(Capsule(cx - 26, cy + 120, cx - 26, cy + 250, 6), M.flat("#ffffff"),
            profile=("bevel", 2, 3), alpha=0.28)
    c.paint(Circle(cx, cy + 30, 15), M.engraved, profile=("sphere", 11), alpha=0.55)


def oscilloscope(c, hue: float = 206, cy: float = CY) -> None:
    """A benchtop scope: ivory case, green CRT, one glowing trace."""
    cx = CX
    body = RRect(cx, cy + 26, 660, 580, 30)
    c.paint(Moved(body, 0, 32), M.flat("#6f6a5c"), profile=("bevel", 14, 18))
    c.paint(body, M.ivory, profile=("bevel", 26, 34), shadow=True, contact=0.24)
    c.paint(RRect(cx - 40, cy - 66, 512, 396, 34), M.ivory, profile=("bevel", 10, 14),
            hue=40, sat=0.06, light=0.78, contact=0.35)
    c.paint(RRect(cx - 40, cy - 70, 452, 344, 30), M.screen,
            profile=("bevel", 12, 18), hue=142, sat=0.34, light=0.20, contact=0.4)
    c.paint_mask(grid_mask((cx - 246, cy - 226, cx + 166, cy + 100), 8, 6, 8),
                 M.flat("#5fe08a"), emboss=0.4, alpha=0.30)
    pts = [(cx - 244 + i * 8.4, cy - 62 + 68 * math.sin(i / 4.4)) for i in range(50)]
    c.paint_mask(blur(polyline_mask(pts, 6.0), 1.2), M.flat("#9df7b4"), emboss=0.0,
                 alpha=0.95)
    c.paint_mask(blur(polyline_mask(pts, 16.0), 7.0), M.flat("#4fd07c"), emboss=0.0,
                 alpha=0.45)
    for i, dx in enumerate((-190, -60, 70, 200)):
        c.paint(Circle(cx + dx, cy + 172, 46), M.ivory, profile=("bevel", 8, 12),
                hue=40, sat=0.06, light=0.74, contact=0.3)
        c.paint(ring(cx + dx, cy + 172, 40, 10), M.flat("#8c8474"), profile=("bevel", 3, 4),
                contact=0.2)
        ang = math.radians(-40 + i * 22)
        c.paint(Capsule(cx + dx, cy + 172, cx + dx + 30 * math.cos(ang),
                        cy + 172 + 30 * math.sin(ang), 6),
                M.flat("#2b2f35"), profile=("bevel", 2, 3), contact=0.15)
    c.paint(Circle(cx + 250, cy + 250, 12), M.lamp, profile=("sphere", 8), hue=120)
    c.paint(Capsule(cx + 120, cy + 286, cx + 250, cy + 286, 5), M.flat("#9a9384"),
            profile=("bevel", 2, 3), alpha=0.6)


def paper_plane(c, hue: float = 206, cy: float = CY) -> None:
    """A folded paper dart in flight: messaging, sends, dispatches."""
    cx = CX
    tip = (cx + 402, cy - 322)
    upper = Poly([tip, (cx - 372, cy - 70), (cx + 14, cy + 40)], rounding=8)
    lower = Poly([tip, (cx + 14, cy + 40), (cx - 306, cy + 262)], rounding=8)
    c.paint(Moved(lower, 0, 26), M.flat("#8d8677"), profile=("bevel", 4, 6))
    c.paint(lower, lambda ctx, **k: M.ceramic(ctx, hue=hue, sat=0.18, light=0.64, **k),
            profile=("bevel", 12, 18), shadow=True, contact=0.2)
    c.paint(upper, M.paper, profile=("bevel", 10, 16), shadow=True, contact=0.26)
    c.paint_mask(polyline_mask([tip, (cx + 14, cy + 40)], 7.0), M.engraved, emboss=2.0,
                 alpha=0.55)
    c.paint_mask(polyline_mask([(cx - 306, cy + 262), (cx + 14, cy + 40)], 5.0),
                 M.flat("#ffffff"), emboss=1.2, alpha=0.30)
    c.paint_mask(polyline_mask([(cx - 372, cy - 70), (cx + 14, cy + 40)], 4.0),
                 M.engraved, emboss=1.0, alpha=0.30)


def pickaxe(c, hue: float = 202, cy: float = CY) -> None:
    """A steel pick on a hickory handle: launchers, miners, extractors."""
    cx = CX
    handle = Rotated(Capsule(cx - 40, cy - 120, cx + 110, cy + 380, 34), 0, cx, cy)
    c.paint(Moved(handle, 0, 26), M.flat("#3f2a14"), profile=("bevel", 8, 12))
    c.paint(handle, M.wood, profile=("sphere", 200), hue=32, light=0.44, shadow=True,
            contact=0.22)
    head = ribbon([(cx - 300, cy - 60), (cx - 210, cy - 246), (cx - 40, cy - 320),
                   (cx + 140, cy - 300), (cx + 268, cy - 196)],
                  [26, 62, 84, 66, 30], rounding=16)
    c.paint(Moved(head, 0, 30), M.flat("#3d434b"), profile=("bevel", 10, 14))
    c.paint(head, M.steel, profile=("sphere", 190), shadow=True, contact=0.26)
    c.paint(RRect(cx - 40, cy - 130, 132, 132, 26), M.gunmetal, profile=("bevel", 10, 14),
            contact=0.3)
    c.paint(RRect(cx - 40, cy - 146, 110, 26, 8), M.chrome, profile=("bevel", 5, 7),
            contact=0.2)
    c.paint(Circle(cx - 40, cy - 130, 20), M.chrome, profile=("sphere", 15), contact=0.2)
    c.paint_mask(polyline_mask([(cx - 290, cy - 74), (cx - 200, cy - 240)], 5.0),
                 M.flat("#ffffff"), emboss=1.6, alpha=0.35)
    c.paint_mask(stripe_mask((cx + 50, cy + 110, cx + 130, cy + 330), 4, 5.0, vertical=True),
                 M.flat("#2a1c0d"), emboss=0.8, alpha=0.4)


def mahjong_tile(c, hue: float = 148, cy: float = CY) -> None:
    """Two ivory mahjong tiles, the front engraved with a bamboo suit."""
    cx = CX
    back = Rotated(RRect(cx - 150, cy - 10, 300, 430, 30), -9, cx, cy)
    c.paint(Moved(back, 0, 30), M.flat("#4d5a4a"), profile=("bevel", 10, 14))
    c.paint(back, M.ivory, profile=("bevel", 24, 32), shadow=True, contact=0.22)
    c.paint(Rotated(RRect(cx - 150, cy - 10, 252, 384, 26), -9, cx, cy),
            M.flat("#1f5e3c"), profile=("bevel", 12, 18), contact=0.25)
    front = Rotated(RRect(cx + 96, cy + 24, 316, 446, 30), 7, cx + 96, cy + 24)
    c.paint(Moved(front, 0, 34), M.flat("#4d5a4a"), profile=("bevel", 10, 14))
    c.paint(front, M.ivory, profile=("bevel", 28, 36), shadow=True, contact=0.24)
    for i in range(3):
        bx = cx + 96 - 78 + i * 78
        c.paint(Rotated(Capsule(bx, cy - 96, bx, cy + 128, 19), 7, cx + 96, cy + 24),
                M.enamel, profile=("bevel", 8, 12), hue=hue, sat=0.52, light=0.42,
                contact=0.2)
        for j in range(3):
            yy = cy - 60 + j * 74
            c.paint(Rotated(Capsule(bx - 26, yy, bx + 26, yy, 8), 7, cx + 96, cy + 24),
                    M.flat("#e8efe4"), profile=("bevel", 3, 4), alpha=0.8)
    c.paint(Rotated(Circle(cx + 96, cy + 148, 26), 7, cx + 96, cy + 24), M.enamel,
            hue=hue, sat=0.5, light=0.40, profile=("sphere", 18), contact=0.2)


def reversi_discs(c, hue: float = 206, cy: float = CY) -> None:
    """Two lacquered Othello discs, one flipped white side up."""
    cx = CX
    for dx, dy, r in ((-120, 210, 250), (140, 116, 236)):
        c.paint(Ellipse(cx + dx, cy + dy, r, r * 0.34), M.flat("#1b1e23"),
                profile=("bevel", 10, 14), alpha=0.55)
    white = (cx - 120, cy + 190, 254)
    c.paint(Moved(Ellipse(white[0], white[1] + 34, white[2], white[2] * 0.36), 0, 20),
            M.ivory, profile=("bevel", 16, 22))
    c.paint(RRect(white[0], white[1] + 18, white[2] * 2, 76, 24), M.ivory,
            profile=("bevel", 10, 14), contact=0.28)
    c.paint(Ellipse(white[0], white[1] - 20, white[2], white[2] * 0.36), M.ivory,
            profile=("sphere", 200), shadow=True, contact=0.3)
    c.paint(Ellipse(white[0] - 90, white[1] - 60, 92, 34), M.flat("#ffffff"),
            profile=("sphere", 30), alpha=0.45)
    black = (cx + 148, cy + 88, 240)
    c.paint(Moved(Ellipse(black[0], black[1] + 32, black[2], black[2] * 0.36), 0, 20),
            M.flat("#101318"), profile=("bevel", 12, 16))
    c.paint(RRect(black[0], black[1] + 16, black[2] * 2, 72, 22), M.flat("#181c22"),
            profile=("bevel", 10, 14), contact=0.3)
    c.paint(Ellipse(black[0], black[1] - 22, black[2], black[2] * 0.36),
            M.flat("#15181d"), profile=("sphere", 210), shadow=True, contact=0.32)
    c.paint(Ellipse(black[0] - 88, black[1] - 58, 86, 30), M.flat("#ffffff"),
            profile=("sphere", 28), alpha=0.18)


def tetromino(c, hue: float = 206, cy: float = CY) -> None:
    """Four glossed enamel blocks in an S-tetromino: falling-block puzzles."""
    cx = CX
    mat = RRect(cx, cy + 60, 720, 600, 34)
    c.paint(Moved(mat, 0, 26), M.flat("#161a1f"), profile=("bevel", 10, 14))
    c.paint(mat, M.felt, profile=("bevel", 22, 28), hue=214, sat=0.06, light=0.19,
            shadow=True, contact=0.22)
    cells = ((-1, 0), (0, 0), (0, 1), (1, 1))
    size, gap = 176, 8
    for i, (col, row) in enumerate(cells):
        x = cx + col * (size + gap) - (size + gap) / 2
        y = cy + row * (size + gap) - (size + gap) / 2 + 20
        block = RRect(x, y, size, size, 26)
        c.paint(Moved(block, 0, 22), M.flat("#0d1013"), profile=("bevel", 8, 12))
        c.paint(block, M.enamel, profile=("bevel", 22, 30), hue=hue,
                sat=0.70, light=(0.56 if i % 2 else 0.50), gloss=0.4, shadow=True,
                contact=0.24)
        c.paint(RRect(x, y - size * 0.28, size * 0.62, size * 0.22, 12),
                lambda ctx, **k: M.enamel(ctx, hue=hue, sat=0.50, light=0.66, **k),
                profile=("bevel", 8, 12), alpha=0.55)


def prism(c, hue: float = 204, cy: float = CY) -> None:
    """A glass prism splitting a beam: colour management, profiles."""
    cx = CX
    body = Poly([(cx + 24, cy - 276), (cx + 300, cy + 216), (cx - 270, cy + 216)],
                rounding=22)
    c.paint(Moved(body, 0, 28), M.flat("#3f4a52"), profile=("bevel", 8, 12))
    c.paint(body, M.crystal, profile=("bevel", 46, 60), hue=hue, sat=0.18, light=0.78,
            shadow=True, contact=0.26)
    c.paint_mask(polyline_mask([(cx + 22, cy - 258), (cx - 252, cy + 206)], 8.0),
                 M.flat("#ffffff"), emboss=1.8, alpha=0.65)
    c.paint_mask(polyline_mask([(cx + 22, cy - 258), (cx + 282, cy + 206)], 6.0),
                 M.flat("#ffffff"), emboss=1.4, alpha=0.30)
    c.paint_mask(polyline_mask([(cx - 248, cy + 206), (cx + 280, cy + 206)], 5.0),
                 M.flat("#8d969f"), emboss=1.0, alpha=0.55)
    # the white beam enters through the left face
    c.paint_mask(blur(polyline_mask([(cx - 470, cy - 20), (cx - 30, cy + 44)], 32.0), 7.0),
                 M.flat("#ffffff"), emboss=0.0, alpha=0.60)
    # and leaves as a fan, blue through violet
    for i, dh in enumerate((0, 18, 36, 54, 72)):
        cls = hsl((hue + dh) % 360, 0.66, 0.62)
        path_pts = [(cx - 20, cy + 40), (cx + 120, cy + 16 + i * 22),
                    (cx + 310, cy - 40 + i * 50), (cx + 462, cy - 120 + i * 82)]
        c.paint_mask(blur(polyline_mask(path_pts, 30.0), 9.0), M.flat(cls), emboss=0.0,
                     alpha=0.46)


def paint_tube(c, hue: float = 30, cy: float = CY) -> None:
    """An artist's paint tube, label out, cap up: painters, GIMP."""
    cx = CX
    body = RRect(cx, cy + 54, 366, 456, 48)
    c.paint(Moved(body, 0, 26), M.flat("#565d66"), profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("sphere", 250), shadow=True, contact=0.24)
    # shoulder and threaded neck
    shoulder = Poly([(cx - 182, cy - 120), (cx + 182, cy - 120), (cx + 92, cy - 224),
                     (cx - 92, cy - 224)], rounding=44)
    c.paint(shoulder, M.aluminium, profile=("bevel", 20, 28), contact=0.26)
    c.paint(RRect(cx, cy - 246, 80, 56, 14), M.gunmetal, profile=("bevel", 6, 9),
            contact=0.24)
    c.paint(RRect(cx, cy - 288, 112, 58, 20), M.brass, profile=("bevel", 10, 14),
            contact=0.28)
    c.paint_mask(stripe_mask((cx - 48, cy - 312, cx + 48, cy - 266), 6, 5.0,
                             vertical=True), M.flat("#6b5220"), emboss=1.0, alpha=0.5)
    # rolled, crimped tail
    c.paint(RRect(cx, cy + 302, 402, 52, 8), M.aluminium, profile=("bevel", 8, 12),
            contact=0.3)
    c.paint_mask(stripe_mask((cx - 186, cy + 286, cx + 186, cy + 320), 11, 4.0,
                             vertical=True), M.flat("#7d848c"), emboss=1.4, alpha=0.55)
    # printed label wrapped round the barrel
    c.paint(RRect(cx, cy + 76, 306, 330, 10), M.paper, profile=("bevel", 6, 9),
            contact=0.28)
    c.paint(RRect(cx, cy - 34, 306, 24, 4), M.flat("#8d8577"), profile=("bevel", 3, 4),
            alpha=0.5)
    _text_lines(c, (cx - 118, cy + 4, cx + 108, cy + 96), 4, 5.0)
    c.paint(RRect(cx, cy + 176, 306, 76, 6), M.enamel, profile=("bevel", 4, 6), hue=hue,
            sat=0.66, light=0.50, contact=0.2)
    _text_lines(c, (cx - 118, cy + 214, cx + 40, cy + 232), 1, 9.0, ink=M.flat("#f4efe4"))
    # a smear of paint at the nozzle mouth, and the drip it left on the label
    c.paint(Moved(Circle(cx + 62, cy - 258, 38), 0, 12), M.flat("#8a3d0e"),
            profile=("sphere", 32))
    c.paint(Circle(cx + 62, cy - 258, 38), M.enamel, profile=("sphere", 34), hue=hue,
            sat=0.66, light=0.52, shadow=True, contact=0.22)
    c.paint(Ellipse(cx + 50, cy - 272, 15, 8), M.flat("#ffffff"),
            profile=("sphere", 7), alpha=0.5)
    drip = Poly([(cx + 68, cy - 226), (cx + 96, cy - 226), (cx + 88, cy - 176),
                 (cx + 76, cy - 176)], rounding=12)
    c.paint(Moved(drip, 0, 10), M.flat("#8a3d0e"), profile=("bevel", 5, 7))
    c.paint(drip, M.enamel, profile=("sphere", 40), hue=hue, sat=0.66, light=0.50,
            contact=0.2)


def pen_nib(c, hue: float = 206, cy: float = CY) -> None:
    """A fountain-pen nib standing point-down: vector drawing, Inkscape."""
    cx = CX
    nib = Poly([(cx - 128, cy - 254), (cx + 128, cy - 254), (cx + 104, cy - 20),
                (cx + 22, cy + 262), (cx - 22, cy + 262), (cx - 104, cy - 20)],
               rounding=24)
    barrel = Capsule(cx, cy - 430, cx, cy - 318, 80)
    c.paint(Moved(barrel, 0, 22), M.flat("#0e1116"), profile=("bevel", 10, 14))
    c.paint(barrel, M.flat("#1c2129"), profile=("sphere", 150), shadow=True,
            contact=0.24)
    c.paint(ring(cx, cy - 300, 74, 30), M.brass, profile=("bevel", 8, 12), contact=0.3)
    c.paint(Circle(cx, cy - 300, 62), M.flat("#141922"), profile=("bevel", 8, 12),
            contact=0.28)
    c.paint(Circle(cx, cy - 300, 46), M.glass, profile=("sphere", 40), hue=hue,
            sat=0.50, light=0.40, gloss=0.62, contact=0.24)
    c.paint(Moved(nib, 0, 26), M.flat("#3f464f"), profile=("bevel", 10, 14))
    c.paint(nib, M.chrome, profile=("bevel", 32, 42), shadow=True, contact=0.26)
    c.paint(RRect(cx, cy - 212, 210, 44, 20), M.brass, profile=("bevel", 8, 12),
            contact=0.3)
    c.paint(Circle(cx, cy - 104, 34), M.flat("#0e1116"), profile=("bevel", 4, 6),
            contact=0.22)
    c.paint(Capsule(cx, cy - 70, cx, cy + 250, 6), M.flat("#0e1116"),
            profile=("bevel", 2, 3), contact=0.12)
    c.paint_mask(polyline_mask([(cx - 150, cy - 300), (cx - 118, cy - 40)], 5.0),
                 M.flat("#ffffff"), emboss=1.6, alpha=0.5)
    c.paint_mask(radial_ticks(cx, cy + 130, 30, 60, 12, 2.0), M.flat("#6a7078"),
                 emboss=0.6, alpha=0.35)


def magnet(c, hue: float = 4, cy: float = CY) -> None:
    """A horseshoe magnet on a steel keeper: torrents, pull, attraction."""
    cx = CX
    body = (ring(cx, cy - 60, 218, 148)
            | Capsule(cx - 218, cy - 40, cx - 218, cy + 210, 74)
            | Capsule(cx + 218, cy - 40, cx + 218, cy + 210, 74))
    c.paint(Moved(body, 0, 30), M.flat("#3a1210"), profile=("bevel", 12, 16))
    c.paint(body, M.enamel, profile=("bevel", 30, 40), hue=hue, sat=0.62, light=0.46,
            shadow=True, contact=0.26)
    for dx in (-218, 218):
        c.paint(RRect(cx + dx, cy + 208, 148, 44, 10), M.chrome,
                profile=("bevel", 6, 9), contact=0.28)
        c.paint(RRect(cx + dx, cy + 176, 120, 20, 8), M.flat("#8f959d"),
                profile=("bevel", 4, 6), contact=0.2)
    keeper = RRect(cx, cy + 232, 470, 56, 14)
    c.paint(Moved(keeper, 0, 18), M.flat("#3c424a"), profile=("bevel", 8, 12))
    c.paint(keeper, M.steel, profile=("bevel", 12, 18), shadow=True, contact=0.24)
    c.paint_mask(polyline_mask([(cx - 180, cy - 200), (cx - 210, cy - 120)], 8.0),
                 M.flat("#ffffff"), emboss=2.0, alpha=0.40)


def pallet(c, hue: float = 206, cy: float = CY) -> None:
    """A loaded wooden pallet, strapped: package archives and warehouses."""
    cx = CX
    deck = RRect(cx, cy + 236, 660, 76, 15)
    c.paint(Moved(deck, 0, 22), M.flat("#43301a"), profile=("bevel", 8, 12))
    c.paint(deck, M.wood, profile=("bevel", 16, 22), hue=30, light=0.44, shadow=True,
            contact=0.24)
    for i in range(3):
        c.paint(RRect(cx - 240 + i * 240, cy + 276, 120, 84, 12), M.wood,
                profile=("bevel", 10, 15), hue=30, light=0.36, contact=0.22)
    c.paint_mask(stripe_mask((cx - 320, cy + 210, cx + 320, cy + 232), 8, 10.0),
                 M.flat("#2b1d0e"), emboss=1.0, alpha=0.4)
    c.paint(Moved(RRect(cx - 130, cy + 66, 380, 340, 10), 0, 26), M.flat("#5c4a30"),
            profile=("bevel", 8, 12))
    c.paint(RRect(cx - 130, cy + 66, 380, 340, 10), M.paper, profile=("bevel", 12, 18),
            hue=36, sat=0.30, light=0.68, shadow=True, contact=0.24)
    c.paint(RRect(cx - 130, cy - 40, 380, 34, 6), M.flat("#b8a888"),
            profile=("bevel", 4, 6), contact=0.3)
    c.paint_mask(stripe_mask((cx - 100, cy + 20, cx - 30, cy + 210), 5, 5.0),
                 M.flat("#8d7c5e"), emboss=1.0, alpha=0.55)
    c.paint(Moved(RRect(cx + 176, cy + 116, 210, 250, 8), 0, 22), M.flat("#4b3c28"))
    c.paint(RRect(cx + 176, cy + 116, 210, 250, 8), M.paper,
            profile=("bevel", 10, 16), hue=34, sat=0.34, light=0.74, shadow=True,
            contact=0.22)
    for sx in (-214, 46):
        c.paint(RRect(cx + sx, cy + 66, 44, 340, 6), M.flat("#33404e"),
                profile=("bevel", 4, 6), alpha=0.80)
        c.paint(RRect(cx + sx, cy + 66, 44, 340, 6), M.flat("#5d7085"),
                profile=("bevel", 6, 9), alpha=0.25)
    c.paint(RRect(cx, cy + 214, 380, 26, 4), M.flat("#3b4a5a"), alpha=0.75)
    c.paint(RRect(cx - 130, cy + 214, 380, 22, 4), M.flat("#9a8562"),
            profile=("bevel", 3, 4), alpha=0.7)


def glass_cubes(c, hue: float = 206, cy: float = CY) -> None:
    """Three blue glass cubes stacked like machines: virtual machines."""
    cx = CX
    cells = ((-1, 0, 0.52), (1, 0, 0.46), (0, -1, 0.40))
    size, gap = 246, 22
    for col, row, light in cells:
        x = cx + col * (size + gap) - 26
        y = cy + row * (size + gap) + 34
        cube = RRect(x, y, size, size, 34)
        c.paint(Moved(cube, 0, 26), M.flat("#10202c"), profile=("bevel", 8, 12))
        c.paint(cube, M.glass, profile=("bevel", 28, 38), hue=hue, sat=0.40, light=light,
                gloss=0.75, shadow=True, contact=0.24)
        c.paint(RRect(x, y - size * 0.33, size * 0.62, size * 0.14, 12),
                M.flat("#ffffff"), profile=("bevel", 5, 7), alpha=0.50)
        c.paint(Capsule(x - size * 0.36, y - size * 0.24, x - size * 0.36,
                        y + size * 0.24, 7), M.flat("#e6f6ff"),
                profile=("bevel", 3, 4), alpha=0.55)
        c.paint(Capsule(x - size * 0.24, y + size * 0.36, x + size * 0.24,
                        y + size * 0.36, 6), M.flat("#8fc7ec"),
                profile=("bevel", 3, 4), alpha=0.40)


def naval_mine(c, hue: float = 4, cy: float = CY) -> None:
    """A moored contact mine, horns out: minesweeper and 'danger' games."""
    cx = CX
    for i in range(3):
        c.paint(Moved(ring(cx - 150 - i * 52, cy + 322 + i * 12, 40, 13), 0, 8),
                M.steel, profile=("bevel", 5, 7), contact=0.18)
    sphere = Circle(cx, cy - 20, 264)
    c.paint(Moved(sphere, 0, 34), M.flat("#20242b"), profile=("sphere", 250))
    c.paint(sphere, M.flat("#2b3038"), profile=("sphere", 280), shadow=True, contact=0.26)
    for i in range(8):
        a = math.radians(i * 45 + 14)
        x0, y0 = cx + 236 * math.cos(a), cy - 20 + 236 * math.sin(a)
        x1, y1 = cx + 352 * math.cos(a), cy - 20 + 352 * math.sin(a)
        c.paint(Capsule(x0, y0, x1, y1, 24), M.gunmetal, profile=("bevel", 8, 12),
                contact=0.22)
        c.paint(Circle(x1, y1, 26), M.brass, profile=("sphere", 20), contact=0.2)
    c.paint(ring(cx, cy - 20, 248, 46) & RRect(cx, cy - 20, 700, 128), M.steel,
            profile=("bevel", 10, 14), contact=0.3)
    c.paint_mask(radial_ticks(cx, cy - 20, 240, 258, 24, 3.0), M.flat("#6e757e"),
                 emboss=1.0, alpha=0.55)
    c.paint(Circle(cx, cy - 274, 26), M.flat("#0e1116"), profile=("bevel", 4, 6),
            contact=0.2)
    c.paint(Circle(cx, cy - 274, 16), M.lamp, profile=("sphere", 12), hue=4,
            contact=0.2)
    c.paint_mask(polyline_mask([(cx - 196, cy - 106), (cx - 168, cy - 158)], 9.0),
                 M.flat("#ffffff"), emboss=1.6, alpha=0.30)


def pencil_pad(c, hue: float = 44, cy: float = CY) -> None:
    """A squared exercise pad with a pencil across it: sudoku, drills, practice."""
    cx = CX
    pad = Rotated(RRect(cx - 26, cy + 56, 560, 620, 12), -3, cx, cy)
    c.paint(Moved(pad, 0, 20), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(pad, M.paper, profile=("bevel", 14, 20), shadow=True, contact=0.22)
    cover = np.clip(0.9 - pad.sdf(c.X, c.Y), 0.0, 1.0)
    grid = grid_mask((cx - 240, cy - 190, cx + 196, cy + 246), 9, 9, 3)
    c.paint_mask(grid * cover, M.flat("#7d8794"), emboss=0.6, alpha=0.55)
    heavy = np.zeros((SIZE, SIZE), dtype=np.float32)
    for i in range(4):
        gx = cx - 240 + i * (436 / 3)
        gy = cy - 190 + i * (436 / 3)
        heavy += polyline_mask([(gx, cy - 192), (gx + 6, cy + 248)], 5.0)
        heavy += polyline_mask([(cx - 242, gy), (cx + 198, gy - 6)], 5.0)
    c.paint_mask(heavy * cover, M.flat("#3f4750"), emboss=1.0, alpha=0.6)
    for i, (gx, gy) in enumerate(((-1, -1), (0, 1), (1, -1), (-1, 0))):
        c.paint_mask(glyph_mask("box", cx + gx * 146, cy + gy * 146, 40) * cover,
                     M.flat(hsl(hue, 0.55, 0.42)), emboss=1.4, alpha=0.65)
    pivot = (cx, cy + 130)
    angle = -28.0
    body = Rotated(RRect(pivot[0], pivot[1], 560, 66, 22), angle, *pivot)
    c.paint(Moved(body, 0, 26), M.flat("#6b5312"), profile=("bevel", 8, 12))
    c.paint(body, M.enamel, profile=("bevel", 14, 20), hue=hue, sat=0.78, light=0.52,
            shadow=True, contact=0.24)
    tip = Rotated(Poly([(pivot[0] + 278, pivot[1] - 34), (pivot[0] + 278, pivot[1] + 34),
                        (pivot[0] + 392, pivot[1])], rounding=4), angle, *pivot)
    c.paint(tip, M.wood, profile=("bevel", 8, 12), hue=38, light=0.68, contact=0.24)
    lead = Rotated(Poly([(pivot[0] + 356, pivot[1] - 13), (pivot[0] + 356, pivot[1] + 13),
                         (pivot[0] + 394, pivot[1])], rounding=3), angle, *pivot)
    c.paint(lead, M.flat("#2b2f35"), profile=("bevel", 4, 6), contact=0.2)
    ferrule = Rotated(RRect(pivot[0] - 302, pivot[1], 58, 68, 10), angle, *pivot)
    c.paint(ferrule, M.brass, profile=("bevel", 8, 12), contact=0.28)
    eraser = Rotated(RRect(pivot[0] - 350, pivot[1], 52, 62, 18), angle, *pivot)
    c.paint(eraser, M.flat("#d98d86"), profile=("sphere", 46), contact=0.26)
    c.paint_mask(polyline_mask([(cx - 200, cy + 200), (cx + 60, cy + 100)], 5.0),
                 M.flat("#ffffff"), emboss=1.2, alpha=0.25)


def remote_desktop(c, hue: float = 202, cy: float = CY) -> None:
    """A screen, a keyboard and a patch lead: remote sessions, VNC."""
    cx = CX
    screen = RRect(cx, cy - 130, 660, 420, 24)
    c.paint(Moved(screen, 0, 28), M.flat("#3f444c"), profile=("bevel", 10, 14))
    c.paint(screen, M.aluminium, profile=("bevel", 24, 32), shadow=True, contact=0.24)
    c.paint(RRect(cx, cy - 134, 588, 348, 16), M.screen, profile=("bevel", 10, 16),
            hue=205, sat=0.20, light=0.16, contact=0.38)
    c.paint(RRect(cx - 40, cy - 150, 336, 224, 10), M.glass, profile=("bevel", 8, 12),
            hue=hue, sat=0.30, light=0.42, gloss=0.5, contact=0.25)
    c.paint(RRect(cx - 40, cy - 246, 336, 40, 8), M.flat("#dfe6ee"),
            profile=("bevel", 4, 6), contact=0.25)
    for i in range(3):
        c.paint(Circle(cx - 186 + i * 20, cy - 246, 7), M.lamp, profile=("sphere", 5),
                hue=(6, 40, 132)[i])
    c.paint(RRect(cx + 190, cy - 60, 168, 244, 10), M.flat("#c9d2dc"),
            profile=("bevel", 8, 12), contact=0.25)
    c.paint_mask(stripe_mask((cx + 122, cy - 160, cx + 258, cy + 50), 7, 5.0),
                 M.flat("#8d99a6"), emboss=0.8, alpha=0.55)
    c.paint(Capsule(cx + 60, cy + 20, cx + 104, cy + 76, 8),
            M.flat("#f2f6fa"), profile=("bevel", 3, 4), alpha=0.85)
    c.paint(Capsule(cx, cy + 96, cx, cy + 170, 22), M.steel, profile=("bevel", 8, 12))
    c.paint(Ellipse(cx, cy + 180, 150, 30), M.aluminium, profile=("sphere", 26),
            shadow=True, contact=0.22)
    base = RRect(cx, cy + 292, 640, 170, 20)
    c.paint(Moved(base, 0, 26), M.flat("#6d7683"), profile=("bevel", 10, 14))
    c.paint(base, M.ivory, profile=("bevel", 18, 24), shadow=True, contact=0.22)
    keys = np.zeros((SIZE, SIZE), dtype=np.float32)
    for row in range(4):
        for col in range(12):
            keys += np.clip(0.6 - RRect(cx - 264 + col * 48, cy + 234 + row * 34, 40, 27,
                                        5).sdf(c.X, c.Y), 0.0, 1.0)
    c.paint_mask(keys, M.flat("#4a5260"), emboss=2.0, alpha=0.55)
    c.paint(RRect(cx, cy + 368, 240, 30, 8), M.aluminium, profile=("bevel", 4, 6),
            contact=0.2)
    lead = ribbon([(cx + 300, cy + 300), (cx + 380, cy + 226), (cx + 356, cy + 96)],
                  [26, 24, 20], rounding=10)
    c.paint(lead, M.rubber, profile=("bevel", 6, 9), shadow=True, contact=0.2)
    c.paint(RRect(cx + 348, cy + 60, 34, 46, 8), M.chrome, profile=("bevel", 4, 6),
            contact=0.2)
