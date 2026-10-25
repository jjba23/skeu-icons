"""Physical objects for devices, categories and projects.

Every function here draws one object in the 1024 px canvas, centred slightly
above the middle so the cast shadow has room.  They share a material vocabulary
(aluminium, chrome, glass, enamel, paper, leather, wood, rubber) and a lighting
model, but each has its own silhouette - which is the whole point: these icons
are photographs of things, not glyphs in a mask.

    from skeu.objects import medallion
    c = Canvas(); medallion(c, hue=206, glyph="gear"); c.save("out.png")
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from . import materials as M
from .paint import (SIZE, Canvas, Capsule, Circle, Ellipse, Moved, Poly, RRect, Rotated,
                    blur, cast_shadow, clamp01, dots_mask, gear_polygon, hsl, polyline_mask,
                    ring, smoothstep)
from .pictograms import glyph_mask

CX, CY = 512.0, 468.0


# --------------------------------------------------------------------------- #
# shared detail helpers
# --------------------------------------------------------------------------- #

def _scaled_mask(smooth: int = 2):
    img = Image.new("L", (SIZE * smooth, SIZE * smooth), 0)
    return img, ImageDraw.Draw(img), smooth


def _mask_of(img, smooth: int) -> np.ndarray:
    return np.asarray(img.resize((SIZE, SIZE), Image.LANCZOS), dtype=np.float32) / 255.0


def radial_ticks(cx: float, cy: float, r0: float, r1: float, count: int,
                 width: float = 3.0, phase: float = 0.0) -> np.ndarray:
    img, draw, s = _scaled_mask()
    for i in range(count):
        a = phase + 2 * math.pi * i / count
        draw.line([((cx + r0 * math.cos(a)) * s, (cy + r0 * math.sin(a)) * s),
                   ((cx + r1 * math.cos(a)) * s, (cy + r1 * math.sin(a)) * s)],
                  fill=255, width=max(1, int(width * s)))
    return _mask_of(img, s)


def stripe_mask(box, count: int, width: float, vertical: bool = False,
                inset: float = 0.0) -> np.ndarray:
    """Parallel machined slots (drive vents, speaker slats)."""
    img, draw, s = _scaled_mask()
    x0, y0, x1, y1 = box
    if vertical:
        step = (x1 - x0 - 2 * inset) / count
        for i in range(count):
            x = x0 + inset + step * (i + 0.5)
            draw.line([(x * s, (y0 + inset) * s), (x * s, (y1 - inset) * s)], fill=255,
                      width=max(1, int(width * s)))
    else:
        step = (y1 - y0 - 2 * inset) / count
        for i in range(count):
            y = y0 + inset + step * (i + 0.5)
            draw.line([((x0 + inset) * s, y * s), ((x1 - inset) * s, y * s)], fill=255,
                      width=max(1, int(width * s)))
    return _mask_of(img, s)


def stitch_mask(points, dash: float = 18.0, gap: float = 12.0, width: float = 5.0) -> np.ndarray:
    """A dashed seam, for leather."""
    img, draw, s = _scaled_mask()
    carry = 0.0
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-6:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        t = 0.0
        while t < length:
            start = t + (dash + gap - carry) % (dash + gap) if carry else t
            if start > t:
                carry = 0.0
                t = start
            end = min(length, t + dash)
            draw.line([((x0 + ux * t) * s, (y0 + uy * t) * s),
                       ((x0 + ux * end) * s, (y0 + uy * end) * s)],
                      fill=255, width=max(1, int(width * s)))
            t = end + gap
    return _mask_of(img, s)


def grid_mask(box, cols: int, rows: int, gap: float) -> np.ndarray:
    img, draw, s = _scaled_mask()
    x0, y0, x1, y1 = box
    cw = (x1 - x0 - gap * (cols - 1)) / cols
    ch = (y1 - y0 - gap * (rows - 1)) / rows
    for r in range(rows):
        for col in range(cols):
            x = x0 + col * (cw + gap)
            y = y0 + r * (ch + gap)
            draw.rounded_rectangle([x * s, y * s, (x + cw) * s, (y + ch) * s],
                                   radius=max(1, int(min(cw, ch) * 0.22 * s)), fill=255)
    return _mask_of(img, s)


def mark(c, name: str, cx: float, cy: float, width: float, material=None,
         emboss: float = 4.0, alpha: float = 1.0, height: float | None = None) -> None:
    """Emboss a pictogram (never printed flat on a colour field).

    The mark gets a real cast shadow into the face it sits on, which is what
    separates an embossed stamp from a white sticker.
    """
    mask = glyph_mask(name, cx, cy, width, height)
    # a tight contact shadow, so the mark sits on the face rather than on top of it
    c.multiply(blur(_shift_mask(mask, 3.0, 6.0), 4.0), 0.62 if alpha else 0.0)
    c.paint_mask(mask, material or M.embossed_white, emboss=emboss, soft=1.2, alpha=alpha)


def _shift_mask(mask: np.ndarray, dx: float, dy: float) -> np.ndarray:
    out = np.zeros_like(mask)
    ix, iy = int(round(dx)), int(round(dy))
    ys = slice(max(0, iy), mask.shape[0] + min(0, iy))
    xs = slice(max(0, ix), mask.shape[1] + min(0, ix))
    sy = slice(max(0, -iy), mask.shape[0] + min(0, -iy))
    sx = slice(max(0, -ix), mask.shape[1] + min(0, -ix))
    out[ys, xs] = mask[sy, sx]
    return out


def screw(c, x: float, y: float, r: float = 11.0, material=None) -> None:
    c.paint(Circle(x, y, r), material or M.chrome, profile=("sphere", r * 0.7))
    mask = polyline_mask([(x - r * 0.62, y), (x + r * 0.62, y)], max(1.6, r * 0.28))
    c.paint_mask(mask, M.flat("#2a2f38"), emboss=0.8, alpha=0.85)


def rivet(c, x: float, y: float, r: float = 9.0, material=None) -> None:
    c.paint(Circle(x, y, r), material or M.brass, profile=("sphere", r))


def lens(c, cx: float, cy: float, r: float, hue: float = 212) -> None:
    c.paint(Moved(Circle(cx, cy, r), 0, 10), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(Circle(cx, cy, r), M.chrome, profile=("sphere", r * 0.55),
            shadow=True, contact=0.28)
    c.paint(ring(cx, cy, r * 0.86, r * 0.16), M.gunmetal, profile=("bevel", 5, 8))
    c.paint(Circle(cx, cy, r * 0.76), M.optic, profile=("sphere", r * 0.36), hue=hue)
    c.paint(ring(cx, cy, r * 0.74, 3.0), M.flat("#0a1220"), profile=("bevel", 1.5, 2.5))


def glow(c, cx: float, cy: float, r: float, hue: float, strength: float = 0.5) -> None:
    """A soft coloured light spill, only where the artwork already exists."""
    d = np.hypot(c.X - cx, c.Y - cy) / r
    mask = np.exp(-(d ** 2) * 2.2) * strength * c.alpha
    c.rgb += hsl(hue, 0.65, 0.55) * mask[..., None]


# --------------------------------------------------------------------------- #
# categories: medallions
def _shape_mask(c, shape) -> np.ndarray:
    d = shape.sdf(c.X, c.Y)
    return np.clip(0.55 - d, 0.0, 1.0).astype(np.float32)


def _gloss(c, region, peak: float = 0.20, fade=(0.0, 0.55), colour: str = "#ffffff") -> None:
    """A soft curved highlight: mask by shape, then fade it down the canvas."""
    ramp = 1.0 - smoothstep(fade[0], fade[1], c.Y / c.size)
    c.paint_mask(_shape_mask(c, region) * ramp, M.flat(colour), alpha=peak)


def _inner_shadow(c, cx: float, cy: float, r: float, width: float, strength: float) -> None:
    d = np.hypot(c.X - cx, c.Y - cy) - r
    band = smoothstep(-width, 0.0, d) * (1.0 - smoothstep(0.0, 1.5, d))
    c.multiply(blur(band, width * 0.35), strength)


def medallion(c, hue: float = 210, glyph: str = "gear", ring_kind: str = "chrome",
              r: float = 288.0, cy: float = CY, sat: float = 0.76, light: float = 0.50,
              glyph_w: float | None = None, glyph_material=None) -> None:
    """A domed gem seated in a machined ring, with one embossed mark.

    The ring has thickness: an outer bezel that catches the key light, a knurled
    edge, a dark groove, and a bright seat under the stone.  The stone is a real
    dome (a sphere height field), so the specular moves as the surface turns, and
    the mark is embossed into it rather than printed on it.
    """
    cx = CX
    outer = r + 48
    if ring_kind == "gear":
        outline = Poly(gear_polygon(cx, cy, outer + 34, outer - 16, 16, tooth=0.52),
                       rounding=4)
        c.paint(Moved(outline, 0, 24), M.steel, profile=("bevel", 10, 16))
        c.paint(outline, M.aluminium, profile=("bevel", 14, 26), shadow=True,
                contact=0.30, brush=0.03)
        c.paint(Circle(cx, cy, outer - 2), M.aluminium, profile=("bevel", 16, 26),
                brush=0.02, contact=0.24)
        c.paint(ring(cx, cy, outer - 14, 11), M.chrome, profile=("sphere", 8),
                contact=0.25)
    else:
        c.paint(Moved(Circle(cx, cy, outer), 0, 26), M.steel, profile=("bevel", 12, 18))
        c.paint(Circle(cx, cy, outer), M.chrome, profile=("sphere", outer * 0.22),
                shadow=True, contact=0.26)
        # knurling: a milled band of fine radial cuts just inside the rim
        c.paint_mask(radial_ticks(cx, cy, outer - 17, outer - 5, 132, 2.1),
                     M.flat("#ffffff"), emboss=0.8, alpha=0.32)
        c.paint_mask(radial_ticks(cx, cy, outer - 17, outer - 5, 132, 1.1),
                     M.flat("#242a33"), emboss=0.5, alpha=0.28)
        c.paint(ring(cx, cy, outer - 22, 18), M.gunmetal, profile=("bevel", 6, 10),
                contact=0.40)
        for angle in (232.0, 308.0):
            a = math.radians(angle)
            screw(c, cx + (outer - 11) * math.cos(a), cy + (outer - 11) * math.sin(a),
                  r=9.0)

    # dark groove, then the bright seat the stone sits in
    c.paint(Circle(cx, cy, r + 10), M.gunmetal, profile=("bevel", 9, 14), contact=0.50)
    c.paint(ring(cx, cy, r + 4, 4.5), M.chrome, profile=("sphere", 3.5), contact=0.35)

    # the stone: a dome, saturated, with an internal glow and a hard highlight
    c.paint(Circle(cx, cy, r), M.crystal, profile=("sphere", r * 0.28),
            hue=hue, sat=sat, light=light, contact=0.55)
    _inner_shadow(c, cx, cy, r, 30.0, 0.45)

    # reflections are Gaussian, never masked arcs: a soft halo, a small sparkle
    # and a low bounce.  Hard-edged highlight shapes read as a lid on the stone.
    inside = np.clip(0.55 - (np.hypot(c.X - cx, c.Y - cy) - r), 0.0, 1.0) * c.alpha
    halo = np.exp(-(((c.X - (cx - r * 0.30)) / (r * 0.46)) ** 2
                    + ((c.Y - (cy - r * 0.50)) / (r * 0.30)) ** 2)) * inside
    c.rgb += halo[..., None] * 0.20
    spark = np.exp(-(((c.X - (cx - r * 0.34)) / (r * 0.10)) ** 2
                    + ((c.Y - (cy - r * 0.56)) / (r * 0.065)) ** 2)) * inside
    c.rgb += spark[..., None] * 0.55
    bounce = np.exp(-(((c.X - (cx + r * 0.14)) / (r * 0.40)) ** 2
                     + ((c.Y - (cy + r * 0.70)) / (r * 0.20)) ** 2)) * inside
    c.rgb += bounce[..., None] * 0.12
    c.paint(ring(cx, cy, r - 1, 2.5), M.flat("#07223c"), profile=("bevel", 2, 3),
            alpha=0.45)

    mark(c, glyph, cx, cy + r * 0.01, glyph_w or r * 0.70,
         material=glyph_material, emboss=16.0)


def gem_disc(c, hue: float = 205, glyph: str = "star", r: float = 330.0) -> None:
    """A flatter gem, for the 'other'/abstract categories."""
    medallion(c, hue=hue, glyph=glyph, ring_kind="chrome", r=r, sat=0.66, light=0.52)


# --------------------------------------------------------------------------- #
# locks and security
# --------------------------------------------------------------------------- #

def padlock(c, hue: float = 210, body: str = "glass", cy: float = CY) -> None:
    cx = CX
    top = cy - 70
    # shackle
    arch = ring(cx, top - 96, 116, 54) & RRect(cx, top - 240, 400, 240)
    arch = arch | Capsule(cx - 116, top - 110, cx - 116, top + 8, 27) \
                | Capsule(cx + 116, top - 110, cx + 116, top + 8, 27)
    c.paint(arch, M.chrome, profile=("bevel", 18, 20), shadow=True, contact=0.2)

    body_shape = RRect(cx, top + 168, 396, 344, r=40)
    c.paint(Moved(body_shape, 0, 24), M.steel, profile=("bevel", 12, 18))
    c.paint(body_shape, M.chrome, profile=("bevel", 30, 34), shadow=True, contact=0.24)
    face = RRect(cx, top + 160, 300, 252, r=30)
    if body == "glass":
        c.paint(face, M.glass, profile=("bevel", 12, 30), hue=hue, sat=0.72, light=0.48,
                contact=0.4)
    else:
        c.paint(face, M.aluminium, profile=("bevel", 12, 18), contact=0.3)
    # brass escutcheon
    keyhole = Circle(cx, top + 128, 36) | Poly([(cx - 17, top + 140), (cx + 17, top + 140),
                                                (cx + 26, top + 226), (cx - 26, top + 226)],
                                               rounding=5)
    c.paint(keyhole, M.brass, profile=("bevel", 5, 7), contact=0.25)
    slot = Circle(cx, top + 126, 15) | Poly([(cx - 7, top + 132), (cx + 7, top + 132),
                                             (cx + 11, top + 206), (cx - 11, top + 206)],
                                            rounding=3)
    c.paint(slot, M.flat("#1b1f26"), profile=("bevel", 3, 4))
    for x in (cx - 158, cx + 158):
        rivet(c, x, top + 60, 9)


def safe_dial(c, hue: float = 42, cy: float = CY) -> None:
    """A brass combination dial on brushed steel: secrets, keys, encryption."""
    cx = CX
    plate = RRect(cx, cy, 620, 620, r=48)
    c.paint(Moved(plate, 0, 24), M.steel, profile=("bevel", 12, 18))
    c.paint(plate, M.aluminium, profile=("bevel", 22, 30), shadow=True, contact=0.22)
    c.paint(ring(cx, cy, 214, 30), M.brass, profile=("bevel", 12, 16), contact=0.3)
    c.paint(Circle(cx, cy, 196), M.brass, profile=("sphere", 150), contact=0.2)
    c.paint_mask(radial_ticks(cx, cy, 168, 190, 40, 3.0), M.flat("#4a3a18"), emboss=1.2, alpha=0.8)
    c.paint(Circle(cx, cy, 78), M.steel, profile=("sphere", 46), contact=0.3)
    c.paint(Capsule(cx, cy - 20, cx, cy - 168, 9), M.flat("#2b2415"), profile=("bevel", 3, 4))
    for x in (cx - 266, cx + 266):
        for y in (cy - 266, cy + 266):
            screw(c, x, y, 13)


def shield(c, hue: float = 210, glyph: str = "check", cy: float = CY) -> None:
    cx = CX
    outline = Poly([(cx, cy - 330), (cx + 250, cy - 226), (cx + 238, cy + 40),
                    (cx + 150, cy + 220), (cx, cy + 320), (cx - 150, cy + 220),
                    (cx - 238, cy + 40), (cx - 250, cy - 226)], rounding=26)
    c.paint(Moved(outline, 0, 24), M.steel, profile=("bevel", 12, 18))
    c.paint(outline, M.aluminium, profile=("bevel", 26, 32), shadow=True, contact=0.22)
    inner = Poly([(cx, cy - 268), (cx + 196, cy - 182), (cx + 186, cy + 22),
                  (cx + 118, cy + 168), (cx, cy + 252), (cx - 118, cy + 168),
                  (cx - 186, cy + 22), (cx - 196, cy - 182)], rounding=20)
    c.paint(inner, M.enamel, profile=("bevel", 12, 18), hue=hue, sat=0.55, light=0.42,
            contact=0.3)
    mark(c, glyph, cx, cy - 12, 260, emboss=4.5)


# --------------------------------------------------------------------------- #
# cameras and optics
# --------------------------------------------------------------------------- #

def camera(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 6, 636, 394, r=48)
    c.paint(Moved(body, 0, 26), M.gunmetal, profile=("bevel", 12, 18))
    c.paint(body, M.gunmetal, profile=("bevel", 26, 34), shadow=True, contact=0.22)
    top = RRect(cx, cy - 158, 566, 104, r=26)
    c.paint(top, M.aluminium, profile=("bevel", 10, 15), contact=0.25)
    grip = RRect(cx - 214, cy + 18, 156, 300, r=42)
    c.paint(grip, M.leather, profile=("bevel", 12, 20), hue=hue, sat=0.18, light=0.20,
            contact=0.3)
    lens(c, cx + 52, cy + 12, 138, hue=hue)
    c.paint(RRect(cx - 214, cy - 176, 104, 62, r=7), M.optic, profile=("bevel", 4, 6))
    c.paint(RRect(cx + 236, cy - 178, 84, 44, r=6), M.ivory, profile=("bevel", 4, 6))
    c.paint(Circle(cx + 258, cy - 132, 28), M.brass, profile=("sphere", 16), contact=0.25)
    c.paint(RRect(cx + 210, cy - 132, 44, 18, r=6), M.steel, profile=("bevel", 3, 4))
    for x in (cx - 316, cx + 316):
        c.paint(Circle(x, cy - 40, 15), M.chrome, profile=("sphere", 10))


def camcorder(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx + 40, cy - 40, 500, 320, r=60)
    c.paint(Moved(body, 0, 24), M.gunmetal, profile=("bevel", 12, 18))
    c.paint(body, M.gunmetal, profile=("bevel", 26, 34), shadow=True, contact=0.22)
    barrel = Capsule(cx - 300, cy - 60, cx - 150, cy - 60, 112)
    c.paint(Moved(barrel, 0, 18), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(barrel, M.chrome, profile=("bevel", 22, 30), contact=0.24)
    lens(c, cx - 300, cy - 60, 86, hue=hue)
    c.paint(RRect(cx + 20, cy - 250, 260, 90, r=26), M.aluminium,
            profile=("bevel", 10, 14), shadow=True, contact=0.2)
    c.paint(RRect(cx + 190, cy - 300, 120, 66, r=10), M.optic, profile=("bevel", 4, 6))
    c.paint(RRect(cx + 120, cy - 158, 150, 74, r=8), M.screen, profile=("bevel", 4, 6),
            contact=0.25)
    c.paint(Circle(cx + 290, cy + 40, 26), M.brass, profile=("sphere", 14))
    c.paint_mask(stripe_mask((cx - 130, cy + 40, cx + 250, cy + 120), 3, 5.0), M.flat("#14181f"),
            emboss=1.4, alpha=0.6)


def webcam(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    base = Ellipse(cx, cy + 250, 210, 52)
    c.paint(base, M.steel, profile=("sphere", 40), shadow=True, contact=0.2)
    c.paint(Capsule(cx, cy + 60, cx, cy + 246, 26), M.aluminium, profile=("bevel", 8, 10))
    ball = Circle(cx, cy - 20, 210)
    c.paint(ball, M.chrome, profile=("sphere", 190), shadow=True, contact=0.24)
    c.paint(Circle(cx, cy - 30, 122), M.gunmetal, profile=("sphere", 100), contact=0.4)
    lens(c, cx, cy - 30, 96, hue=hue)
    c.paint(Circle(cx + 132, cy - 122, 18), M.lamp, profile=("sphere", 14), hue=140)


# --------------------------------------------------------------------------- #
# displays and handhelds
# --------------------------------------------------------------------------- #

def _display(c, w: float, h: float, r: float, hue: float = 212, bezel: float = 0.93,
             stand: bool = False, cy: float = CY) -> None:
    cx = CX
    if stand:
        c.paint(Ellipse(cx, cy + h * 0.62, w * 0.34, 46), M.aluminium,
                profile=("sphere", 38), shadow=True, contact=0.2)
        c.paint(Capsule(cx, cy + h * 0.18, cx, cy + h * 0.60, 32), M.aluminium,
                profile=("bevel", 8, 11), contact=0.15)
    body = RRect(cx, cy, w, h, r)
    c.paint(Moved(body, 0, 26), M.aluminium, profile=("bevel", 12, 18))
    c.paint(body, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    inner = RRect(cx, cy - h * 0.02, w * bezel, h * bezel * 0.97, r * 0.72)
    c.paint(inner, M.screen, profile=("bevel", 6, 9), hue=hue, contact=0.35)
    c.paint(RRect(cx, cy + h * bezel * 0.43, w * 0.30, max(6.0, h * 0.012), 3),
            M.gunmetal, profile=("bevel", 2, 3), alpha=0.8)


def monitor(c, hue: float = 212, cy: float = CY) -> None:
    _display(c, 720, 480, 34, hue=hue, stand=True, cy=cy - 40)


def tv(c, hue: float = 212, cy: float = CY) -> None:
    _display(c, 800, 500, 26, hue=hue, stand=True, cy=cy - 34)


def laptop(c, hue: float = 212, cy: float = CY) -> None:
    cx = CX
    deck = Poly([(cx - 372, cy + 214), (cx + 372, cy + 214), (cx + 320, cy + 336),
                 (cx - 320, cy + 336)], rounding=12)
    c.paint(Moved(deck, 0, 22), M.steel, profile=("bevel", 8, 12))
    c.paint(deck, M.aluminium, profile=("bevel", 12, 18), shadow=True, contact=0.2)
    c.paint_mask(stripe_mask((cx - 290, cy + 236, cx + 290, cy + 262), 1, 10.0),
            M.flat("#9aa1ab"), emboss=1.2, alpha=0.5)
    lid = RRect(cx, cy - 50, 660, 430, 28)
    c.paint(Moved(lid, 0, 18), M.aluminium, profile=("bevel", 10, 16))
    c.paint(lid, M.aluminium, profile=("bevel", 16, 24), shadow=True, contact=0.24)
    c.paint(RRect(cx, cy - 58, 606, 380, 20), M.screen, profile=("bevel", 6, 9),
            hue=hue, contact=0.3)
    c.paint(Circle(cx, cy - 254, 6), M.optic, profile=("sphere", 5))
    c.paint(Capsule(cx - 240, cy + 208, cx + 240, cy + 208, 9), M.gunmetal,
            profile=("bevel", 3, 4), alpha=0.7)


def tablet(c, hue: float = 212, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 540, 700, 46)
    c.paint(Moved(body, 0, 20), M.aluminium, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 16, 24), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 24, 470, 596, 24), M.screen, profile=("bevel", 6, 9), hue=hue,
            contact=0.3)
    c.paint(ring(cx, cy + 300, 24, 6), M.gunmetal, profile=("bevel", 3, 4))
    c.paint(Circle(cx, cy - 302, 7), M.optic, profile=("sphere", 6))


def phone(c, hue: float = 212, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 340, 640, 56)
    c.paint(Moved(body, 0, 20), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 22, 30), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 48, 284, 470, 22), M.screen, profile=("bevel", 6, 9), hue=hue,
            contact=0.35)
    c.paint(ring(cx, cy + 262, 32, 5), M.chrome, profile=("bevel", 3, 4))
    c.paint(Capsule(cx, cy - 274, cx, cy - 274, 4), M.gunmetal, profile=("bevel", 2, 2),
            alpha=0.8)
    c.paint(Capsule(cx, cy - 262, cx, cy - 262, 2.5), M.flat("#12151b"))


def watch(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    strap = RRect(cx, cy, 150, 700, 64)
    c.paint(strap, M.leather, profile=("bevel", 12, 18), hue=hue, sat=0.35, light=0.22,
            shadow=True, contact=0.2)
    seam = stitch_mask([(cx - 52, cy - 320), (cx - 52, cy + 320)], 16, 12, 4.0)
    c.paint_mask(seam, M.flat("#8b7a5f"), emboss=1.6, alpha=0.5)
    c.paint_mask(np.flipud(seam), M.flat("#141619"), alpha=0.0)
    case = Circle(cx, cy, 196)
    c.paint(Moved(case, 0, 16), M.steel, profile=("bevel", 10, 14))
    c.paint(case, M.chrome, profile=("sphere", 170), shadow=True, contact=0.26)
    c.paint(Circle(cx, cy, 158), M.optic, profile=("sphere", 110), hue=hue)
    c.paint_mask(radial_ticks(cx, cy, 132, 148, 12, 4.0), M.flat("#dfe6ef"), emboss=1.4, alpha=0.7)
    c.paint(Capsule(cx, cy, cx, cy - 92, 7), M.flat("#f2f5f8"), profile=("bevel", 2.5, 3))
    c.paint(Capsule(cx, cy, cx + 64, cy + 26, 6), M.flat("#d7dee7"), profile=("bevel", 2, 3))
    c.paint(Circle(cx + 196, cy - 46, 22), M.chrome, profile=("sphere", 14), contact=0.2)
    c.paint(Capsule(cx + 196, cy + 40, cx + 196, cy + 70, 9), M.chrome, profile=("bevel", 4, 5))


def player(c, hue: float = 212, cy: float = CY) -> None:
    """Portable media player: aluminium body, glass face, click wheel."""
    cx = CX
    body = RRect(cx, cy, 400, 640, 54)
    c.paint(Moved(body, 0, 20), M.aluminium, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 112, 320, 300, 20), M.screen, profile=("bevel", 5, 8), hue=hue,
            contact=0.35)
    c.paint(Circle(cx, cy + 166, 96), M.ivory, profile=("sphere", 70), contact=0.35)
    c.paint(ring(cx, cy + 166, 76, 3), M.flat("#b9b2a6"), profile=("bevel", 1.5, 2), alpha=0.7)
    c.paint(Circle(cx, cy + 166, 34), M.aluminium, profile=("sphere", 24), contact=0.2)
    mark(c, "play", cx, cy + 166, 24, M.engraved, emboss=1.4)


def ebook(c, hue: float = 200, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 480, 660, 30)
    c.paint(Moved(body, 0, 22), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 20, 28), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy, 428, 606, 14), M.paper, profile=("bevel", 4, 6), contact=0.3)
    for i in range(9):
        y = cy - 220 + i * 46
        c.paint(Capsule(cx - 170, y, cx + 170 - (i % 3) * 60, y, 4), M.flat("#3a3d42"),
                emboss=0.8, alpha=0.55)
    c.paint(Circle(cx + 168, cy + 262, 16), M.gunmetal, profile=("sphere", 10))


def pda(c, hue: float = 205, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 420, 620, 34)
    c.paint(Moved(body, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 140, 350, 260, 12), M.screen, profile=("bevel", 5, 8), hue=hue,
            contact=0.3)
    c.paint_mask(grid_mask((cx - 160, cy + 20, cx + 160, cy + 250), 4, 4, 10), M.ivory,
                 emboss=3.0)
    c.paint(Circle(cx, cy + 300, 12), M.gunmetal, profile=("sphere", 8))


def projector(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 30, 660, 320, 34)
    c.paint(Moved(body, 0, 26), M.gunmetal, profile=("bevel", 12, 18))
    c.paint(body, M.aluminium, profile=("bevel", 24, 32), shadow=True, contact=0.22)
    lens(c, cx - 140, cy + 30, 118, hue=hue)
    c.paint_mask(stripe_mask((cx + 60, cy - 40, cx + 280, cy + 80), 4, 5.0), M.flat("#171b22"),
            emboss=1.5, alpha=0.6)
    c.paint(RRect(cx + 150, cy + 130, 180, 44, 10), M.brass, profile=("bevel", 5, 7),
            contact=0.2)
    for x in (cx - 250, cx + 250):
        c.paint(Capsule(x, cy + 180, x, cy + 220, 16), M.rubber, profile=("bevel", 4, 6))


# --------------------------------------------------------------------------- #
# input devices
# --------------------------------------------------------------------------- #

def keyboard(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    tray = RRect(cx, cy + 20, 800, 300, 30)
    c.paint(Moved(tray, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(tray, M.aluminium, profile=("bevel", 14, 20), shadow=True, contact=0.22)
    rows = 5
    top = cy - 96
    key_h = 38
    gap = 7
    for r in range(rows):
        y = top + r * (key_h + gap)
        count = 14 if r < 4 else 12
        width = 40 if r < 4 else 44
        total = count * width + (count - 1) * gap
        x = cx - total / 2 + width / 2
        if r == 0:
            count = 14
        for i in range(count):
            w = width
            if r == 4:
                if i == 3:
                    w = width * 2.2
                elif i == 8:
                    w = width * 2.2
            key = RRect(x, y, w, key_h, 7)
            c.paint(key, M.ivory, profile=("bevel", 7, 9), contact=0.35)
            x += w + gap


def mouse(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 30, 400, 610, 190)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 14, 20))
    c.paint(body, M.aluminium, profile=("bevel", 34, 64), shadow=True, contact=0.24)
    c.paint(RRect(cx, cy - 60, 330, 400, 150), M.ivory, profile=("bevel", 18, 40),
            contact=0.3)
    c.paint(Capsule(cx, cy - 250, cx, cy - 30, 3.0), M.flat("#8d8272"),
            profile=("bevel", 2, 2), alpha=0.45)
    c.paint(RRect(cx, cy - 150, 70, 110, 30), M.ivory, profile=("bevel", 8, 12), contact=0.3)
    c.paint(Capsule(cx, cy - 186, cx, cy - 116, 9), M.gunmetal, profile=("bevel", 4, 5))


def trackpad(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 640, 470, 34)
    c.paint(Moved(body, 0, 22), M.aluminium, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy, 560, 390, 20), M.glass, profile=("bevel", 6, 9), hue=hue,
            sat=0.25, light=0.36, gloss=0.5, contact=0.3)


def graphics_tablet(c, hue: float = 210, cy: float = CY) -> None:
    trackpad(c, hue=hue, cy=cy + 30)
    stylus = Rotated(Capsule(CX + 210, CY - 240, CX + 330, CY - 330, 22), 32, CX + 270, CY - 285)
    c.paint(stylus, M.chrome, profile=("bevel", 10, 14), shadow=True, contact=0.2)
    c.paint(Rotated(Capsule(CX + 330, CY - 330, CX + 356, CY - 350, 10), 32, CX + 340, CY - 340),
            M.brass, profile=("bevel", 4, 5))


def gamepad(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = (RRect(cx, cy - 10, 620, 300, 120)
            | Capsule(cx - 210, cy + 90, cx - 280, cy + 190, 90)
            | Capsule(cx + 210, cy + 90, cx + 280, cy + 190, 90))
    c.paint(Moved(body, 0, 24), M.gunmetal, profile=("bevel", 12, 18))
    c.paint(body, M.aluminium, profile=("bevel", 26, 34), shadow=True, contact=0.22)
    c.paint(Circle(cx - 160, cy + 10, 74), M.gunmetal, profile=("sphere", 60), contact=0.25)
    c.paint(Capsule(cx - 208, cy + 10, cx - 112, cy + 10, 16), M.gunmetal, profile=("bevel", 5, 6))
    c.paint(Capsule(cx - 160, cy - 38, cx - 160, cy + 58, 16), M.gunmetal, profile=("bevel", 5, 6))
    for dx, dy, hue_b in ((150, -30, 0), (210, 10, 140), (150, 50, 210), (90, 10, 40)):
        c.paint(Circle(cx + dx, cy + dy, 30), M.enamel, profile=("sphere", 24),
                hue=hue_b, sat=0.65, light=0.5, contact=0.25)
    c.paint(Capsule(cx - 40, cy + 30, cx + 20, cy + 30, 20), M.gunmetal,
            profile=("bevel", 6, 8))
    for x in (cx - 60, cx + 10):
        c.paint(Circle(x, cy - 40, 26), M.ivory, profile=("sphere", 20), contact=0.2)


def joystick(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    base = Poly([(cx - 320, cy + 250), (cx + 320, cy + 250), (cx + 230, cy + 60),
                 (cx - 230, cy + 60)], rounding=30)
    c.paint(Moved(base, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(base, M.gunmetal, profile=("bevel", 22, 30), shadow=True, contact=0.2)
    c.paint(Capsule(cx, cy - 150, cx, cy + 100, 26), M.chrome, profile=("bevel", 10, 12),
            contact=0.2)
    c.paint(Ellipse(cx, cy - 190, 90, 108), M.rubber, profile=("sphere", 90), contact=0.3)
    c.paint(Ellipse(cx, cy - 226, 60, 26), M.steel, profile=("sphere", 24), alpha=0.8)
    for dx in (-120, 90):
        c.paint(Circle(cx + dx, cy + 140, 26), M.enamel, profile=("sphere", 20), hue=hue,
                sat=0.6, light=0.5, contact=0.2)


def dialpad(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 420, 620, 46)
    c.paint(Moved(body, 0, 22), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 22, 30), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 190, 330, 150, 12), M.screen, profile=("bevel", 5, 8), hue=hue,
            contact=0.3)
    for r in range(4):
        for col in range(3):
            x = cx - 110 + col * 110
            y = cy - 20 + r * 82
            c.paint(Circle(x, y, 36), M.ivory, profile=("sphere", 30), contact=0.3)
            c.paint(ring(x, y, 26, 3), M.flat("#b6afa2"), profile=("bevel", 1.5, 2), alpha=0.6)
    c.paint(Circle(cx, cy + 290, 14), M.gunmetal, profile=("sphere", 10))


def usb_hub(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 520, 230, 34)
    c.paint(Moved(body, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    for i in range(4):
        x = cx - 180 + i * 120
        c.paint(RRect(x, cy + 10, 78, 46, 5), M.rubber, profile=("bevel", 3, 4), contact=0.2)
        c.paint(RRect(x, cy + 16, 62, 12, 2), M.steel, profile=("bevel", 2, 2))
    c.paint(Capsule(cx - 20, cy - 60, cx + 20, cy - 60, 8), M.lamp, profile=("bevel", 4, 5),
            hue=140)
    c.paint(Capsule(cx - 20, cy - 88, cx - 210, cy - 170, 11), M.rubber,
            profile=("bevel", 5, 6))
    c.paint(RRect(cx - 300, cy - 250, 120, 150, 18), M.aluminium,
            profile=("bevel", 10, 14), shadow=True, contact=0.2)
    c.paint(RRect(cx - 300, cy - 310, 120, 90, 12), M.aluminium, profile=("bevel", 8, 10))


# --------------------------------------------------------------------------- #
# storage media
# --------------------------------------------------------------------------- #

def drive(c, hue: float = 210, cy: float = CY, depth: float = 0.0,
          vents: bool = True, ports: int = 1, solid: bool = False) -> None:
    """A bare 3.5-inch drive, drawn the way a desktop drive always looked.

    Front face, top face and the right cheek in one box: the top carries a
    printed label, the face carries the grille and the activity LED.  This is the
    silhouette every classic desktop knew, not a flat slab.
    """
    cx = CX
    front_w, front_h = 470, 330
    top_dx, top_dy = 54, -80
    left, right = cx - front_w / 2, cx + front_w / 2
    top, bottom = cy - 85, cy + 245
    # right cheek, darker, then the top face, then the lit front
    side = Poly([(right, top), (right + top_dx, top + top_dy),
                 (right + top_dx, bottom + top_dy - 6), (right, bottom)], rounding=10)
    c.paint(side, M.aluminium, profile=("bevel", 8, 12), contact=0.24)
    back = Poly([(left, top), (left + top_dx, top + top_dy),
                 (right + top_dx, top + top_dy), (right, top)], rounding=10)
    c.paint(Moved(back, 0, 4), M.steel, profile=("bevel", 8, 10))
    c.paint(back, M.aluminium, profile=("bevel", 6, 9), contact=0.24)
    # printed label sitting on the top face, in the same perspective
    label = Poly([(left + 54, top - 16), (left + 88, top + top_dy + 16),
                  (left + 300, top + top_dy + 16), (left + 266, top - 16)], rounding=4)
    c.paint(label, M.paper, profile=("flat",), contact=0.2)
    for i in range(3):
        y = top - 4 + i * 20
        c.paint(Capsule(left + 78, y, left + 244, y - 8, 4), M.ink,
                profile=("bevel", 2, 2), alpha=0.5)
    body = RRect(cx, (top + bottom) / 2, front_w, front_h, 22)
    c.paint(Moved(body, 0, 24), M.steel, profile=("bevel", 12, 16))
    c.paint(body, M.aluminium, profile=("bevel", 22, 30), shadow=True, contact=0.24)
    if solid:
        c.paint(RRect(cx, cy + 40, 420, 250, 16), M.gunmetal,
                profile=("bevel", 8, 12), contact=0.24)
        for i in range(4):
            c.paint(RRect(cx - 150 + i * 100, cy + 30, 84, 150, 6), M.steel,
                    profile=("bevel", 4, 6), contact=0.15)
    # grille: machined slots across the lower half
    if vents:
        c.paint_mask(stripe_mask((left + 46, cy + 116, right - 46, cy + 196), 3, 5.0),
                     M.flat("#20242b"), emboss=1.6, alpha=0.55)
    for i in range(ports):
        c.paint(RRect(left + 88 + i * 140, cy + 226, 78, 26, 5), M.rubber,
                profile=("bevel", 3, 4), contact=0.2)
    # the label window on the face, and the LED
    c.paint(RRect(cx + 30, cy - 20, 250, 62, 8), M.paper,
            profile=("bevel", 3, 5), contact=0.22)
    for i in range(2):
        c.paint(Capsule(cx - 40, cy - 34 + i * 22, cx + 120, cy - 34 + i * 22, 4),
                M.ink, profile=("bevel", 2, 2), alpha=0.45)
    c.paint(Capsule(right - 58, bottom - 38, right - 58, bottom - 38, 8), M.lamp,
            profile=("sphere", 6), hue=140)
    if ports > 1:
        c.paint(Capsule(right - 58, bottom - 82, right - 58, bottom - 82, 8), M.lamp,
                profile=("sphere", 6), hue=45)


def multidrive(c, hue: float = 210, cy: float = CY) -> None:
    """Two drives stacked: the back one peeks over the front one."""
    drive(c, hue=hue, cy=cy - 210, vents=False, ports=1)
    drive(c, hue=hue, cy=cy + 120, vents=True, ports=1)


def solid_state(c, hue: float = 210, cy: float = CY) -> None:
    """A solid-state drive: a black anodised box with a printed label."""
    cx = CX
    front_w, front_h = 520, 340
    top_dx, top_dy = 58, -86
    left, right = cx - front_w / 2, cx + front_w / 2
    top, bottom = cy - 96, cy + 244
    side = Poly([(right, top), (right + top_dx, top + top_dy),
                 (right + top_dx, bottom + top_dy - 6), (right, bottom)], rounding=10)
    c.paint(side, M.gunmetal, profile=("bevel", 8, 12), contact=0.24)
    back = Poly([(left, top), (left + top_dx, top + top_dy),
                 (right + top_dx, top + top_dy), (right, top)], rounding=10)
    c.paint(back, M.gunmetal, profile=("bevel", 6, 9), contact=0.26)
    label = Poly([(left + 60, top - 18), (left + 96, top + top_dy + 14),
                  (left + 330, top + top_dy + 14), (left + 294, top - 18)], rounding=4)
    c.paint(label, M.enamel, profile=("flat",), hue=hue, sat=0.42, light=0.52,
            contact=0.2)
    body = RRect(cx, (top + bottom) / 2, front_w, front_h, 18)
    c.paint(Moved(body, 0, 24), M.flat("#14171c"), profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 18, 26), shadow=True, contact=0.26)
    c.paint_mask(stripe_mask((left + 50, cy + 70, right - 50, cy + 176), 3, 5.0),
                 M.flat("#0b0d11"), emboss=1.4, alpha=0.5)
    c.paint(Capsule(right - 60, bottom - 40, right - 60, bottom - 40, 8), M.lamp,
            profile=("sphere", 6), hue=140)


def optical_disc(c, hue: float = 210, label: float | None = None, cy: float = CY) -> None:
    cx = CX
    c.paint(Circle(cx, cy, 340), M.iridescent, profile=("bevel", 6, 12), shadow=True,
            contact=0.2)
    c.paint(ring(cx, cy, 320, 8), M.flat("#f0f3f7"), profile=("bevel", 2, 3), alpha=0.75)
    if label is not None:
        # printed band near the rim, not a coloured centre: it is still a silver disc
        c.paint(ring(cx, cy, 268, 62), M.enamel, profile=("bevel", 2, 4),
                hue=label, sat=0.38, light=0.66, contact=0.1)
        c.paint(ring(cx, cy, 206, 4), M.flat("#b6bcc5"), profile=("bevel", 2, 2), alpha=0.7)
        c.paint(ring(cx, cy, 298, 3), M.flat("#b6bcc5"), profile=("bevel", 2, 2), alpha=0.7)
    c.paint(Circle(cx, cy, 74), M.iridescent, profile=("sphere", 56), contact=0.2)
    c.paint(Circle(cx, cy, 32), M.gunmetal, profile=("sphere", 24))
    c.paint(ring(cx, cy, 128, 3), M.flat("#9aa1aa"), profile=("bevel", 1.5, 2), alpha=0.5)


def jewel_case(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    case = RRect(cx + 26, cy + 20, 600, 620, 26)
    c.paint(Moved(case, 0, 20), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(case, M.gunmetal, profile=("bevel", 16, 22), shadow=True, contact=0.2)
    c.paint(RRect(cx + 26, cy + 20, 540, 560, 18), M.flat("#2b3038"),
            profile=("bevel", 6, 8))
    optical_disc(c, hue=hue, label=hue, cy=cy - 6)
    c.paint(Capsule(cx + 300, cy - 300, cx + 300, cy - 260, 8), M.chrome,
            profile=("bevel", 3, 4))


def memory_card(c, kind: str = "sd", hue: float = 205, cy: float = CY) -> None:
    cx = CX
    if kind == "sim":
        w, h, cut = 330, 350, 74
    elif kind == "smart":
        w, h, cut = 380, 280, 26
    else:
        w, h, cut = 340, 440, 62
    x0, y0 = cx - w / 2, cy - h / 2
    outline = Poly([(x0, y0), (x0 + w - cut, y0), (x0 + w, y0 + cut), (x0 + w, y0 + h),
                    (x0, y0 + h)], rounding=10)
    c.paint(Moved(outline, 0, 22), M.gunmetal, profile=("bevel", 8, 12))
    c.paint(outline, M.gunmetal, profile=("bevel", 12, 18), shadow=True, contact=0.2)
    # the label: a slim band across the upper third
    c.paint(Rect := RRect(cx, y0 + h * 0.26, w - 34, h * 0.30, 6), M.enamel,
            profile=("bevel", 4, 7), hue=hue, sat=0.5, light=0.58, contact=0.15)
    for i in range(4):
        c.paint(Capsule(x0 + 34, y0 + h * 0.20 + i * 26, x0 + w * 0.55, y0 + h * 0.20 + i * 26,
                        3), M.flat("#3a3f47"), emboss=0.8, alpha=0.35)
    # gold contacts along the bottom, plus the write-protect notch
    for i in range(6):
        c.paint(RRect(x0 + 44 + i * ((w - 96) / 6), y0 + h - 52, (w - 108) / 6 - 10, 74, 3),
                M.brass, profile=("bevel", 3, 4), contact=0.12)
    c.paint(RRect(x0 + w - 22, y0 + h * 0.62, 22, 60, 4), M.gunmetal,
            profile=("bevel", 3, 4), contact=0.1)


def floppy(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 440, 440, 22)
    c.paint(Moved(body, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 18, 24), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy - 130, 250, 150, 10), M.aluminium, profile=("bevel", 6, 9),
            contact=0.2)
    c.paint(RRect(cx - 44, cy - 178, 90, 90, 6), M.flat("#2a3038"),
            profile=("bevel", 3, 4))
    c.paint(RRect(cx, cy + 62, 330, 250, 8), M.paper, profile=("bevel", 4, 6), contact=0.2)
    for i in range(5):
        c.paint(Capsule(cx - 120, cy - 10 + i * 42, cx + 120, cy - 10 + i * 42, 3),
                M.flat("#555a62"), emboss=0.6, alpha=0.45)


def tape_cartridge(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 560, 400, 24)
    c.paint(Moved(body, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 20, 28), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 30, 460, 250, 14), M.flat("#1a1e24"),
            profile=("bevel", 6, 9), contact=0.3)
    for dx in (-110, 110):
        c.paint(ring(cx + dx, cy + 30, 66, 12), M.steel, profile=("bevel", 5, 7), contact=0.25)
        c.paint(Circle(cx + dx, cy + 30, 42), M.paper, profile=("sphere", 32))
    c.paint(RRect(cx, cy - 140, 400, 90, 8), M.paper, profile=("bevel", 3, 5), contact=0.15)


def zip_disc(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 520, 520, 40)
    c.paint(Moved(body, 0, 26), M.gunmetal, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 22, 30), shadow=True, contact=0.22)
    c.paint(Circle(cx, cy, 210), M.aluminium, profile=("sphere", 170), contact=0.3)
    c.paint(Circle(cx, cy, 60), M.gunmetal, profile=("sphere", 40), contact=0.2)
    c.paint_mask(radial_ticks(cx, cy, 150, 196, 48, 3.0), M.flat("#3a414b"), emboss=1.4, alpha=0.6)


def usb_stick(c, hue: float = 210, cy: float = CY) -> None:
    """A USB stick on the diagonal: steel body, rubber grip, chrome connector."""
    cx = CX
    angle = 14.0
    a = math.radians(angle)
    centre = (cx + 10, cy + 70)

    def at(x: float, y: float) -> tuple[float, float]:
        """Local (x, y) offset from the body centre, rotated with the object."""
        return (centre[0] + x * math.cos(a) - y * math.sin(a),
                centre[1] + x * math.sin(a) + y * math.cos(a))

    body = Rotated(RRect(centre[0], centre[1], 214, 430, 30), angle, centre[0], centre[1])
    c.paint(Moved(body, 0, 24), M.flat("#14171c"), profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 28), shadow=True, contact=0.24)
    # rubber grip at the tail, then a slim enamelled band across the body
    gx, gy = at(0, 118)
    c.paint(Rotated(RRect(gx, gy, 190, 180, 24), angle, gx, gy), M.rubber,
            profile=("bevel", 12, 16), contact=0.26)
    bx, by = at(0, -26)
    c.paint(Rotated(RRect(bx, by, 178, 86, 10), angle, bx, by), M.enamel,
            profile=("bevel", 6, 8), hue=hue, sat=0.54, light=0.50, contact=0.2)
    # the connector: chrome shell with its four gold contacts, joined to the body
    sx, sy = at(0, -268)
    c.paint(Moved(Rotated(RRect(sx, sy, 172, 128, 6), angle, sx, sy), 0, 12),
            M.flat("#1b1f25"), profile=("bevel", 6, 9))
    c.paint(Rotated(RRect(sx, sy, 172, 128, 6), angle, sx, sy), M.chrome,
            profile=("bevel", 10, 14), shadow=True, contact=0.24)
    px, py = at(0, -282)
    c.paint(Rotated(RRect(px, py, 124, 84, 3), angle, px, py), M.flat("#2a3038"),
            profile=("bevel", 3, 4))
    for i in range(4):
        ox, oy = at(-42 + i * 28, -268)
        c.paint(Rotated(RRect(ox, oy, 11, 54, 3), angle, ox, oy), M.brass,
                profile=("bevel", 2, 3), alpha=0.9)
    lx, ly = at(66, 6)
    c.paint(Capsule(lx, ly, lx, ly, 8), M.lamp, profile=("sphere", 6), hue=140)


def battery(c, hue: float = 210, cy: float = CY, level: float = 0.8) -> None:
    cx = CX
    body = RRect(cx, cy + 30, 260, 500, 34)
    c.paint(Moved(body, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 28), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 30, 210, 440, 24), M.enamel, profile=("bevel", 6, 9),
            hue=hue, sat=0.55, light=0.45, contact=0.2)
    fill = int(380 * level / 40)
    for i in range(fill):
        y = cy + 210 - i * 40
        c.paint(RRect(cx, y, 170, 28, 6), M.enamel, profile=("bevel", 4, 6),
                hue=140 if level > 0.25 else 30, sat=0.62, light=0.52)
    c.paint(RRect(cx, cy - 250, 90, 46, 10), M.brass, profile=("bevel", 6, 8),
            shadow=True, contact=0.2)


def optical_drive(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 720, 200, 20)
    c.paint(Moved(body, 0, 24), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 16, 22), shadow=True, contact=0.22)
    c.paint(RRect(cx - 60, cy + 10, 440, 34, 8), M.flat("#20242b"),
            profile=("bevel", 4, 6), contact=0.25)
    c.paint(RRect(cx + 250, cy + 4, 110, 46, 8), M.brass, profile=("bevel", 5, 7),
            contact=0.2)
    c.paint(Capsule(cx - 300, cy - 50, cx - 300, cy - 50, 7), M.lamp, profile=("sphere", 5),
            hue=140)


# --------------------------------------------------------------------------- #
# printing, audio, network, internals
# --------------------------------------------------------------------------- #

def printer(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 40, 620, 360, 30)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 28), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 120, 520, 130, 12), M.flat("#22262d"),
            profile=("bevel", 6, 9), contact=0.3)
    sheet = RRect(cx, cy - 190, 420, 320, 8)
    c.paint(Moved(sheet, 0, 10), M.paper, profile=("bevel", 3, 5),
            shadow=True, contact=0.2)
    for i in range(8):
        c.paint(Capsule(cx - 150, cy - 300 + i * 30, cx + 150 - (i % 3) * 40,
                        cy - 300 + i * 30, 4), M.flat("#4a4d54"), emboss=0.9, alpha=0.5)
    c.paint(RRect(cx + 200, cy - 120, 120, 46, 8), M.ivory, profile=("bevel", 5, 7),
            contact=0.2)
    c.paint(Capsule(cx - 200, cy - 120, cx - 200, cy - 120, 8), M.lamp,
            profile=("sphere", 6), hue=140)


def scanner(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 40, 640, 300, 26)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 20, 28), shadow=True, contact=0.22)
    lid = RRect(cx, cy - 130, 620, 190, 22)
    c.paint(Moved(lid, 0, 18), M.aluminium, profile=("bevel", 8, 12))
    c.paint(lid, M.ivory, profile=("bevel", 14, 20), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy + 60, 540, 90, 8), M.glass, profile=("bevel", 4, 6), hue=hue,
            sat=0.2, light=0.55, gloss=0.8, contact=0.2)
    c.paint(RRect(cx + 240, cy + 130, 90, 30, 6), M.brass, profile=("bevel", 4, 5))


def speakers(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    for dx in (-206, 206):
        box = RRect(cx + dx, cy, 340, 560, 24)
        c.paint(Moved(box, 0, 26), M.steel, profile=("bevel", 10, 14))
        c.paint(box, M.leather, profile=("bevel", 18, 24), hue=hue, sat=0.18, light=0.20,
                shadow=True, contact=0.2)
        c.paint(RRect(cx + dx, cy + 40, 290, 420, 18), M.rubber,
                profile=("bevel", 6, 9), contact=0.2)
        c.paint_mask(dots_mask(SIZE, 19, 5.0, bounds=(cx + dx - 145, cy - 168, cx + dx + 145,
                                                cy + 250)),
                M.flat("#59616c"), emboss=2.2, alpha=0.70)
        c.paint(Circle(cx + dx, cy - 214, 42), M.chrome, profile=("sphere", 30), contact=0.2)
        c.paint(Circle(cx + dx, cy - 214, 24), M.brass, profile=("sphere", 18))


def headphones(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    band = ring(cx, cy - 40, 226, 40)
    c.paint(band, M.aluminium, profile=("bevel", 14, 18), shadow=True, contact=0.2)
    c.paint(ring(cx, cy - 40, 226, 10), M.rubber, profile=("bevel", 5, 6), alpha=0.8)
    for dx in (-238, 238):
        cup = Ellipse(cx + dx, cy + 120, 108, 138)
        c.paint(Moved(cup, 0, 18), M.steel, profile=("bevel", 8, 12))
        c.paint(cup, M.aluminium, profile=("sphere", 110), shadow=True, contact=0.24)
        c.paint(Ellipse(cx + dx, cy + 124, 74, 100), M.leather,
                profile=("sphere", 80), hue=hue, sat=0.2, light=0.22, contact=0.3)
        c.paint(Capsule(cx + dx, cy - 10, cx + dx + (60 if dx > 0 else -60), cy - 34, 14),
                M.steel, profile=("bevel", 6, 7))


def headset(c, hue: float = 210, cy: float = CY) -> None:
    headphones(c, hue=hue, cy=cy - 20)
    boom = Capsule(CX + 238, CY + 150, CX + 120, CY + 190, 13)
    c.paint(boom, M.rubber, profile=("bevel", 6, 7), shadow=True, contact=0.2)
    c.paint(Ellipse(CX + 108, CY + 194, 34, 26), M.gunmetal,
            profile=("sphere", 24), contact=0.2)


def microphone(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    base = Ellipse(cx, cy + 290, 210, 46)
    c.paint(base, M.steel, profile=("sphere", 36), shadow=True, contact=0.2)
    c.paint(Capsule(cx, cy + 40, cx, cy + 280, 20), M.chrome, profile=("bevel", 8, 10))
    c.paint(ring(cx, cy + 40, 120, 20), M.chrome, profile=("bevel", 8, 10), contact=0.2)
    body = Capsule(cx, cy - 220, cx, cy + 30, 86)
    c.paint(Moved(body, 0, 14), M.gunmetal, profile=("bevel", 8, 11))
    c.paint(body, M.chrome, profile=("sphere", 120), shadow=True, contact=0.24)
    c.paint_mask(dots_mask(SIZE, 13, 3.0, bounds=(cx - 80, cy - 286, cx + 80, cy - 60)),
            M.flat("#20242b"), emboss=2.0, alpha=0.7)
    c.paint(ring(cx, cy - 60, 82, 12), M.brass, profile=("bevel", 5, 7))


def server(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 400, 620, 24)
    c.paint(Moved(body, 0, 28), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    for i in range(4):
        y = cy - 210 + i * 118
        c.paint(RRect(cx, y, 340, 98, 10), M.gunmetal, profile=("bevel", 6, 9), contact=0.25)
        c.paint_mask(stripe_mask((cx - 150, y - 30, cx + 60, y + 30), 3, 4.0),
                M.flat("#1c2027"), emboss=1.2, alpha=0.6)
        c.paint(Capsule(cx + 118, y - 18, cx + 118, y - 18, 7), M.lamp,
                profile=("sphere", 5), hue=140)
        c.paint(Capsule(cx + 148, y - 18, cx + 148, y - 18, 7), M.lamp,
                profile=("sphere", 5), hue=30)
    c.paint(RRect(cx - 210, cy - 250, 26, 500, 8), M.steel, profile=("bevel", 4, 6))
    c.paint(RRect(cx + 210, cy - 250, 26, 500, 8), M.steel, profile=("bevel", 4, 6))


def router(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    for dx, rot in ((-210, -22), (0, 0), (210, 22)):
        c.paint(Rotated(Capsule(cx + dx, cy + 30, cx + dx + rot * 3, cy - 320, 18), rot,
                        cx + dx, cy - 140), M.rubber, profile=("bevel", 9, 12),
                shadow=True, contact=0.15)
    body = RRect(cx, cy + 130, 680, 280, 56)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.aluminium, profile=("bevel", 26, 38), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy + 96, 600, 90, 26), M.aluminium, profile=("bevel", 12, 16),
            contact=0.25)
    for i in range(5):
        c.paint(Capsule(cx - 190 + i * 96, cy + 190, cx - 190 + i * 96, cy + 190, 8),
                M.lamp, profile=("sphere", 6), hue=140 if i < 4 else 45)
    for i in range(4):
        c.paint(RRect(cx - 180 + i * 100, cy + 236, 74, 20, 4), M.rubber,
                profile=("bevel", 3, 4), contact=0.1)
    c.paint(Circle(cx, cy + 96, 22), M.chrome, profile=("sphere", 16), contact=0.2)


def ethernet_plug(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 40, 300, 260, 26)
    c.paint(Moved(body, 0, 22), M.steel, profile=("bevel", 8, 12))
    c.paint(body, M.aluminium, profile=("bevel", 16, 22), shadow=True, contact=0.2)
    c.paint(RRect(cx, cy - 130, 180, 180, 8), M.glass, profile=("bevel", 6, 8),
            hue=hue, sat=0.2, light=0.55, gloss=0.9, contact=0.2)
    for i in range(8):
        c.paint(RRect(cx - 66 + (i % 4) * 44, cy - 196 + (i // 4) * 54, 16, 40, 3),
                M.brass, profile=("bevel", 2, 3))
    c.paint(RRect(cx, cy - 236, 70, 60, 6), M.gunmetal, profile=("bevel", 4, 5),
            contact=0.15)
    cable = Capsule(cx, cy + 170, cx + 40, cy + 340, 22)
    c.paint(cable, M.rubber, profile=("bevel", 10, 12), shadow=True, contact=0.15)


def chip(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    pcb = RRect(cx, cy, 520, 520, 26)
    c.paint(Moved(pcb, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(pcb, M.paint, profile=("bevel", 16, 22), hue=hue, sat=0.30, light=0.26,
            shadow=True, contact=0.2)
    for i in range(9):
        off = -228 + i * 57
        for x in (off, -off):
            c.paint(RRect(cx + x, cy - 292, 34, 40, 3), M.brass, profile=("bevel", 2, 3))
            c.paint(RRect(cx + x, cy + 292, 34, 40, 3), M.brass, profile=("bevel", 2, 3))
    ihs = RRect(cx, cy - 10, 300, 300, 16)
    c.paint(ihs, M.chrome, profile=("bevel", 16, 20), contact=0.25)
    c.paint(RRect(cx, cy - 10, 240, 240, 10), M.aluminium, profile=("bevel", 10, 14))
    mark(c, "grid", cx, cy - 14, 120, M.engraved, emboss=2.0)


def ram_stick(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 660, 210, 16)
    c.paint(Moved(body, 0, 18), M.steel, profile=("bevel", 8, 12))
    c.paint(body, M.paint, profile=("bevel", 12, 16), hue=hue, sat=0.28, light=0.28,
            shadow=True, contact=0.2)
    for i in range(4):
        c.paint(RRect(cx - 220 + i * 148, cy - 20, 112, 96, 8), M.gunmetal,
                profile=("bevel", 6, 8), contact=0.2)
    for i in range(16):
        c.paint(RRect(cx - 310 + i * 40, cy + 86, 24, 46, 2), M.brass,
                profile=("bevel", 2, 3))
    c.paint(RRect(cx + 300, cy - 40, 40, 80, 6), M.ivory, profile=("bevel", 3, 4))


def graphics_card(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy + 20, 720, 300, 22)
    c.paint(Moved(body, 0, 22), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 18, 26), shadow=True, contact=0.22)
    for dx in (-170, 150):
        c.paint(Circle(cx + dx, cy + 10, 118), M.flat("#22262d"),
                profile=("sphere", 100), contact=0.25)
        c.paint(Circle(cx + dx, cy + 10, 108), M.chrome, profile=("sphere", 96), contact=0.2)
        c.paint(ring(cx + dx, cy + 10, 58, 16), M.gunmetal, profile=("bevel", 6, 8))
        c.paint_mask(radial_ticks(cx + dx, cy + 10, 70, 104, 9, 26.0), M.flat("#4b525c"),
                emboss=1.5, alpha=0.55)
    c.paint(RRect(cx + 320, cy - 20, 50, 220, 8), M.chrome, profile=("bevel", 4, 6),
            contact=0.2)
    c.paint(RRect(cx, cy + 150, 520, 44, 4), M.brass, profile=("bevel", 3, 4))


def motherboard(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    board = RRect(cx, cy, 620, 620, 20)
    c.paint(Moved(board, 0, 20), M.steel, profile=("bevel", 8, 12))
    c.paint(board, M.paint, profile=("bevel", 14, 18), hue=hue, sat=0.34, light=0.27,
            shadow=True, contact=0.2)
    c.paint(RRect(cx - 140, cy - 120, 220, 220, 8), M.gunmetal,
            profile=("bevel", 6, 8), contact=0.2)
    c.paint(RRect(cx - 140, cy - 120, 120, 120, 6), M.chrome, profile=("bevel", 4, 6))
    for i in range(3):
        c.paint(RRect(cx + 60 + i * 70, cy - 60, 40, 260, 4), M.ivory,
                profile=("bevel", 3, 4), contact=0.15)
    for i in range(4):
        c.paint(RRect(cx - 250 + i * 60, cy + 190, 44, 60, 4), M.aluminium,
                profile=("bevel", 3, 4))
    for x, y in ((cx - 270, cy - 270), (cx + 270, cy - 270), (cx - 270, cy + 270),
                 (cx + 270, cy + 270)):
        screw(c, x, y, 14)


def ups(c, hue: float = 210, cy: float = CY) -> None:
    cx = CX
    body = RRect(cx, cy, 520, 560, 30)
    c.paint(Moved(body, 0, 26), M.steel, profile=("bevel", 10, 14))
    c.paint(body, M.gunmetal, profile=("bevel", 20, 28), shadow=True, contact=0.22)
    c.paint(RRect(cx, cy - 150, 380, 150, 10), M.screen, profile=("bevel", 5, 8), hue=hue,
            contact=0.25)
    for i in range(3):
        c.paint(RRect(cx - 140 + i * 140, cy + 80, 100, 46, 6), M.rubber,
                profile=("bevel", 4, 5), contact=0.15)
    c.paint(Capsule(cx, cy + 190, cx, cy + 190, 9), M.lamp, profile=("sphere", 7), hue=45)
