"""Pictograms: bold, geometric marks for embossing and for small hardware detail.

The rules are blunt about text: no monograms on a coloured field, no hairlines.
So every glyph here is a *symbol* drawn as solid geometry with strokes at least
3 % of its width, meant to be embossed into glass or struck into metal, never
printed flat.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from .paint import SIZE

SS = 4  # supersample factor for mask drawing


def _canvas(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("L", (size * SS, size * SS), 0)
    return img, ImageDraw.Draw(img)


def _finish(img: Image.Image) -> np.ndarray:
    return np.asarray(img.resize((img.width // SS, img.height // SS), Image.LANCZOS),
                      dtype=np.float32) / 255.0


class Pen:
    """Draws in a unit box, mapped onto the icon canvas."""

    def __init__(self, size: int = SIZE):
        self.size = size
        self.img, self.d = _canvas(size)

    def x(self, u: float) -> float:
        return u * self.size * SS

    def width(self, w: float) -> int:
        return max(1, int(round(w * self.size * SS)))

    def line(self, points, w: float = 0.05, fill: int = 255):
        self.d.line([(self.x(p[0]), self.x(p[1])) for p in points], fill=fill,
                    width=self.width(w), joint="curve")

    def poly(self, points, fill: int = 255):
        self.d.polygon([(self.x(p[0]), self.x(p[1])) for p in points], fill=fill)

    def circle(self, cx: float, cy: float, r: float, fill: int = 255):
        self.d.ellipse([self.x(cx - r), self.x(cy - r), self.x(cx + r), self.x(cy + r)], fill=fill)

    def ring(self, cx: float, cy: float, r: float, w: float, fill: int = 255):
        self.d.ellipse([self.x(cx - r), self.x(cy - r), self.x(cx + r), self.x(cy + r)],
                       outline=fill, width=self.width(w))

    def rect(self, x0: float, y0: float, x1: float, y1: float, fill: int = 255,
             radius: float = 0.0, outline: float = 0.0):
        box = [self.x(x0), self.x(y0), self.x(x1), self.x(y1)]
        if radius > 0:
            self.d.rounded_rectangle(box, radius=self.x(radius), fill=fill if not outline else None,
                                     outline=fill if outline else None,
                                     width=self.width(outline) if outline else 0)
        elif outline:
            self.d.rectangle(box, outline=fill, width=self.width(outline))
        else:
            self.d.rectangle(box, fill=fill)

    def arc(self, x0: float, y0: float, x1: float, y1: float, start: float, end: float,
            w: float = 0.05, fill: int = 255):
        self.d.arc([self.x(x0), self.x(y0), self.x(x1), self.x(y1)], start=start, end=end,
                   fill=fill, width=self.width(w))

    def paw(self, cx: float, cy: float, r: float, fill: int = 255):
        self.circle(cx, cy, r, fill)

    def mask(self) -> np.ndarray:
        return _finish(self.img)


# --------------------------------------------------------------------------- #
# the glyphs
# --------------------------------------------------------------------------- #

def _code(p: Pen):
    p.line([(0.34, 0.28), (0.10, 0.50), (0.34, 0.72)], 0.085)
    p.line([(0.66, 0.28), (0.90, 0.50), (0.66, 0.72)], 0.085)
    p.line([(0.58, 0.24), (0.42, 0.76)], 0.075)


def _brackets(p: Pen):
    p.line([(0.34, 0.20), (0.16, 0.20), (0.16, 0.80), (0.34, 0.80)], 0.075)
    p.line([(0.66, 0.20), (0.84, 0.20), (0.84, 0.80), (0.66, 0.80)], 0.075)


def _prompt(p: Pen):
    p.line([(0.18, 0.32), (0.40, 0.50), (0.18, 0.68)], 0.09)
    p.line([(0.46, 0.70), (0.82, 0.70)], 0.075)


def _pipe(p: Pen):
    for i, (y, x1) in enumerate(((0.28, 0.86), (0.50, 0.70), (0.72, 0.80))):
        p.rect(0.12, y - 0.035, x1, y + 0.035, radius=0.035)


def _gear(p: Pen):
    pts = []
    teeth = 12
    for i in range(teeth):
        a = i * 2 * math.pi / teeth
        for r, off in ((0.30, -0.16), (0.46, -0.10), (0.46, 0.10), (0.30, 0.16)):
            ang = a + off
            pts.append((0.5 + r * math.cos(ang), 0.5 + r * math.sin(ang)))
    p.poly(pts)
    p.circle(0.5, 0.5, 0.14, fill=0)


def _wrench(p: Pen):
    p.poly([(0.24, 0.20), (0.40, 0.20), (0.47, 0.52), (0.40, 0.56), (0.86, 0.86),
            (0.82, 0.92), (0.34, 0.47), (0.30, 0.40), (0.24, 0.20)])
    p.circle(0.30, 0.24, 0.10, fill=0)


def _wire_globe(p: Pen):
    p.ring(0.5, 0.5, 0.40, 0.055)
    p.line([(0.10, 0.50), (0.90, 0.50)], 0.045)
    for y in (0.28, 0.72):
        half = math.sqrt(max(0.0, 0.40 ** 2 - (y - 0.5) ** 2))
        p.line([(0.5 - half, y), (0.5 + half, y)], 0.038)
    for rx in (0.17, 0.33):
        p.d.ellipse([p.x(0.5 - rx), p.x(0.10), p.x(0.5 + rx), p.x(0.90)],
                    outline=255, width=p.width(0.042))


def _play(p: Pen):
    p.poly([(0.30, 0.18), (0.84, 0.50), (0.30, 0.82)])


def _spark(p: Pen):
    pts = []
    for i in range(16):
        a = i * math.pi / 8 - math.pi / 2
        r = 0.50 if i % 2 == 0 else 0.20
        pts.append((0.5 + r * math.cos(a), 0.5 + r * math.sin(a)))
    p.poly(pts)


def _star(p: Pen):
    pts = []
    for i in range(10):
        a = i * math.pi / 5 - math.pi / 2
        r = 0.48 if i % 2 == 0 else 0.21
        pts.append((0.5 + r * math.cos(a), 0.5 + r * math.sin(a)))
    p.poly(pts)


def _pen_nib(p: Pen):
    p.poly([(0.50, 0.06), (0.66, 0.30), (0.78, 0.52), (0.62, 0.62), (0.56, 0.94),
            (0.44, 0.94), (0.38, 0.62), (0.22, 0.52), (0.34, 0.30)])
    p.line([(0.50, 0.24), (0.50, 0.52)], 0.05, fill=0)
    p.circle(0.50, 0.34, 0.06, fill=0)


def _eye(p: Pen):
    p.poly([(0.08, 0.50), (0.30, 0.30), (0.50, 0.24), (0.70, 0.30), (0.92, 0.50),
            (0.70, 0.70), (0.50, 0.76), (0.30, 0.70)])
    p.circle(0.50, 0.50, 0.17, fill=0)
    p.circle(0.50, 0.50, 0.07)


def _monitor(p: Pen):
    p.rect(0.10, 0.16, 0.90, 0.68, radius=0.06, outline=0.055)
    p.rect(0.44, 0.68, 0.56, 0.80)
    p.rect(0.28, 0.80, 0.72, 0.86, radius=0.03)


def _person(p: Pen):
    p.circle(0.50, 0.32, 0.16)
    p.poly([(0.18, 0.88), (0.22, 0.66), (0.38, 0.54), (0.62, 0.54), (0.78, 0.66), (0.82, 0.88)])


def _moon(p: Pen):
    p.circle(0.50, 0.50, 0.38)
    p.circle(0.64, 0.40, 0.32, fill=0)


def _palette(p: Pen):
    p.poly([(0.50, 0.10), (0.74, 0.16), (0.90, 0.38), (0.88, 0.62), (0.70, 0.78),
            (0.56, 0.70), (0.44, 0.74), (0.46, 0.90), (0.24, 0.88), (0.10, 0.62),
            (0.12, 0.34), (0.28, 0.16)])
    p.circle(0.36, 0.40, 0.10, fill=0)
    for cx, cy in ((0.60, 0.32), (0.72, 0.50), (0.56, 0.56)):
        p.circle(cx, cy, 0.055, fill=0)


def _keyhole(p: Pen):
    p.circle(0.50, 0.38, 0.16)
    p.poly([(0.42, 0.44), (0.58, 0.44), (0.64, 0.82), (0.36, 0.82)])


def _sliders(p: Pen):
    for y, knob in ((0.24, 0.34), (0.50, 0.66), (0.76, 0.44)):
        p.line([(0.14, y), (0.86, y)], 0.075)
        p.circle(knob, y, 0.115)


def _download(p: Pen):
    p.line([(0.50, 0.12), (0.50, 0.62)], 0.10)
    p.poly([(0.26, 0.44), (0.74, 0.44), (0.50, 0.76)])
    p.line([(0.16, 0.80), (0.16, 0.90), (0.84, 0.90), (0.84, 0.80)], 0.075)


def _question(p: Pen):
    p.arc(0.24, 0.12, 0.76, 0.62, 150, 20, 0.11)
    p.line([(0.66, 0.50), (0.66, 0.58), (0.50, 0.66), (0.50, 0.72)], 0.11)
    p.circle(0.50, 0.88, 0.075)


def _question_bold(p: Pen):
    """The same question mark with a mark that survives an orb at 16 px."""
    p.arc(0.20, 0.08, 0.80, 0.62, 150, 20, 0.16)
    p.line([(0.68, 0.48), (0.68, 0.58), (0.50, 0.67), (0.50, 0.73)], 0.16)
    p.circle(0.50, 0.89, 0.095)


def _cards(p: Pen):
    p.rect(0.20, 0.22, 0.58, 0.86, radius=0.06)
    p.rect(0.42, 0.14, 0.80, 0.78, radius=0.06, fill=0)
    p.rect(0.46, 0.18, 0.76, 0.74, radius=0.05)
    p.circle(0.61, 0.40, 0.06)
    p.circle(0.61, 0.56, 0.06)
    p.circle(0.51, 0.48, 0.06)
    p.circle(0.71, 0.48, 0.06)


def _feather(p: Pen):
    p.poly([(0.78, 0.10), (0.88, 0.22), (0.60, 0.72), (0.30, 0.90), (0.12, 0.92),
            (0.22, 0.74), (0.56, 0.44)])
    p.line([(0.20, 0.86), (0.74, 0.22)], 0.045, fill=0)


def _atom(p: Pen):
    p.circle(0.50, 0.50, 0.12)
    for angle in (0, 60, 120):
        # an ellipse drawn as a stroked arc pair, rotated by re-drawing on a temp layer
        layer, draw = _canvas(SIZE)
        draw.ellipse([0.18 * SIZE * SS, 0.38 * SIZE * SS, 0.82 * SIZE * SS, 0.62 * SIZE * SS],
                     outline=255, width=int(0.05 * SIZE * SS))
        layer = layer.rotate(angle, resample=Image.BICUBIC)
        p.img.paste(255, (0, 0), layer)


def _droplet(p: Pen):
    p.poly([(0.50, 0.08), (0.66, 0.30), (0.78, 0.50), (0.80, 0.64), (0.72, 0.82),
            (0.58, 0.92), (0.42, 0.92), (0.28, 0.82), (0.20, 0.64), (0.22, 0.50),
            (0.34, 0.30)])


def _circuit(p: Pen):
    for pts in (((0.14, 0.30), (0.46, 0.30), (0.46, 0.66), (0.86, 0.66)),
                ((0.14, 0.70), (0.34, 0.70), (0.34, 0.46), (0.62, 0.46), (0.62, 0.22),
                 (0.86, 0.22))):
        p.line(list(pts), 0.06)
    for cx, cy in ((0.14, 0.30), (0.86, 0.66), (0.14, 0.70), (0.86, 0.22)):
        p.circle(cx, cy, 0.075)


def _bird(p: Pen):
    p.poly([(0.12, 0.56), (0.34, 0.40), (0.56, 0.34), (0.72, 0.22), (0.78, 0.30),
            (0.90, 0.28), (0.84, 0.44), (0.88, 0.52), (0.66, 0.60), (0.50, 0.74),
            (0.34, 0.80), (0.20, 0.74), (0.30, 0.64)])
    p.circle(0.70, 0.36, 0.035, fill=0)


def _wave(p: Pen):
    pts = []
    for i in range(0, 101):
        t = i / 100
        pts.append((0.08 + 0.84 * t, 0.50 + 0.20 * math.sin(t * 4 * math.pi)))
    p.line(pts, 0.085)


def _box(p: Pen):
    p.rect(0.14, 0.30, 0.86, 0.88, radius=0.05, outline=0.055)
    p.line([(0.14, 0.48), (0.86, 0.48)], 0.055)
    p.rect(0.44, 0.16, 0.56, 0.48)


def _leaf(p: Pen):
    p.poly([(0.50, 0.10), (0.78, 0.26), (0.86, 0.52), (0.70, 0.78), (0.46, 0.90),
            (0.22, 0.76), (0.14, 0.50), (0.28, 0.24)])
    p.line([(0.24, 0.80), (0.76, 0.22)], 0.05, fill=0)


def _film(p: Pen):
    p.rect(0.10, 0.24, 0.90, 0.76, radius=0.04, outline=0.05)
    for i in range(4):
        x = 0.16 + i * 0.18
        p.rect(x, 0.30, x + 0.10, 0.38, radius=0.02)
        p.rect(x, 0.62, x + 0.10, 0.70, radius=0.02)


def _note(p: Pen):
    p.circle(0.34, 0.74, 0.14)
    p.rect(0.44, 0.20, 0.52, 0.78)
    p.poly([(0.50, 0.18), (0.84, 0.10), (0.84, 0.30), (0.50, 0.38)])


def _clock(p: Pen):
    p.ring(0.50, 0.50, 0.40, 0.06)
    p.line([(0.50, 0.50), (0.50, 0.24)], 0.06)
    p.line([(0.50, 0.50), (0.70, 0.58)], 0.06)


def _lock(p: Pen):
    p.rect(0.18, 0.44, 0.82, 0.90, radius=0.06)
    p.arc(0.28, 0.10, 0.72, 0.60, 180, 360, 0.08)
    p.circle(0.50, 0.64, 0.07, fill=0)
    p.rect(0.46, 0.64, 0.54, 0.78, fill=0)


def _shield(p: Pen):
    p.poly([(0.50, 0.08), (0.86, 0.22), (0.86, 0.52), (0.68, 0.78), (0.50, 0.92),
            (0.32, 0.78), (0.14, 0.52), (0.14, 0.22)])


def _camera(p: Pen):
    p.rect(0.08, 0.30, 0.92, 0.82, radius=0.08)
    p.rect(0.34, 0.20, 0.66, 0.34, radius=0.04)
    p.circle(0.50, 0.56, 0.18, fill=0)
    p.circle(0.50, 0.56, 0.10)


def _speaker(p: Pen):
    p.poly([(0.16, 0.36), (0.34, 0.36), (0.58, 0.16), (0.58, 0.84), (0.34, 0.64),
            (0.16, 0.64)])
    p.arc(0.52, 0.26, 0.78, 0.74, -60, 60, 0.05)


def _wifi(p: Pen):
    p.arc(0.16, 0.26, 0.84, 0.94, 205, 335, 0.075)
    p.arc(0.28, 0.38, 0.72, 0.92, 205, 335, 0.075)
    p.circle(0.50, 0.78, 0.085)


def _bluetooth(p: Pen):
    p.line([(0.50, 0.06), (0.50, 0.94)], 0.075)
    p.line([(0.50, 0.06), (0.74, 0.28), (0.26, 0.68)], 0.075)
    p.line([(0.50, 0.94), (0.74, 0.72), (0.26, 0.32)], 0.075)


def _battery(p: Pen):
    p.rect(0.10, 0.32, 0.82, 0.68, radius=0.05, outline=0.055)
    p.rect(0.84, 0.42, 0.92, 0.58, radius=0.02)
    p.rect(0.18, 0.40, 0.52, 0.60, radius=0.02)


def _usb(p: Pen):
    p.line([(0.50, 0.14), (0.50, 0.80)], 0.07)
    p.poly([(0.50, 0.06), (0.58, 0.20), (0.42, 0.20)])
    p.circle(0.50, 0.86, 0.10)
    p.line([(0.50, 0.58), (0.30, 0.44)], 0.06)
    p.rect(0.24, 0.34, 0.36, 0.44, radius=0.02)
    p.line([(0.50, 0.48), (0.70, 0.36)], 0.06)
    p.circle(0.72, 0.32, 0.075)


def _phone(p: Pen):
    p.poly([(0.22, 0.12), (0.42, 0.20), (0.46, 0.36), (0.34, 0.48), (0.56, 0.72),
            (0.68, 0.60), (0.82, 0.66), (0.88, 0.84), (0.74, 0.92), (0.30, 0.84),
            (0.10, 0.44)])


def _headphones(p: Pen):
    p.arc(0.12, 0.12, 0.88, 0.92, 180, 360, 0.08)
    p.rect(0.10, 0.50, 0.28, 0.86, radius=0.07)
    p.rect(0.72, 0.50, 0.90, 0.86, radius=0.07)


def _mic(p: Pen):
    p.rect(0.34, 0.08, 0.66, 0.56, radius=0.16)
    p.arc(0.18, 0.24, 0.82, 0.80, 0, 180, 0.065)
    p.line([(0.50, 0.80), (0.50, 0.92)], 0.06)
    p.line([(0.32, 0.92), (0.68, 0.92)], 0.06)


def _magnifier(p: Pen):
    p.ring(0.44, 0.44, 0.32, 0.09)
    p.line([(0.66, 0.66), (0.90, 0.90)], 0.13)


def _key(p: Pen):
    p.ring(0.26, 0.30, 0.16, 0.06)
    p.line([(0.38, 0.40), (0.86, 0.86)], 0.08)
    p.line([(0.66, 0.72), (0.78, 0.60)], 0.07)
    p.line([(0.76, 0.82), (0.88, 0.70)], 0.07)


def _tag(p: Pen):
    p.poly([(0.14, 0.14), (0.56, 0.14), (0.88, 0.50), (0.50, 0.88), (0.14, 0.56)])
    p.circle(0.36, 0.36, 0.075, fill=0)


def _folder(p: Pen):
    p.poly([(0.10, 0.24), (0.40, 0.24), (0.48, 0.34), (0.90, 0.34), (0.90, 0.84),
            (0.10, 0.84)])


def _book(p: Pen):
    p.rect(0.16, 0.14, 0.84, 0.88, radius=0.04)
    p.line([(0.26, 0.14), (0.26, 0.88)], 0.05, fill=0)


def _home(p: Pen):
    p.poly([(0.50, 0.10), (0.92, 0.46), (0.80, 0.46), (0.80, 0.88), (0.20, 0.88),
            (0.20, 0.46), (0.08, 0.46)])
    p.rect(0.42, 0.62, 0.58, 0.88, fill=0)


def _sun(p: Pen):
    p.circle(0.50, 0.50, 0.20)
    for i in range(8):
        a = i * math.pi / 4
        p.line([(0.50 + 0.30 * math.cos(a), 0.50 + 0.30 * math.sin(a)),
                (0.50 + 0.42 * math.cos(a), 0.50 + 0.42 * math.sin(a))], 0.06)


def _grid(p: Pen):
    for x in (0.10, 0.52):
        for y in (0.10, 0.52):
            p.rect(x, y, x + 0.38, y + 0.38, radius=0.06)


def _cube(p: Pen):
    p.poly([(0.50, 0.08), (0.90, 0.30), (0.90, 0.70), (0.50, 0.92), (0.10, 0.70), (0.10, 0.30)])
    p.line([(0.50, 0.08), (0.50, 0.50)], 0.05, fill=0)
    p.line([(0.10, 0.30), (0.50, 0.52), (0.90, 0.30)], 0.05, fill=0)


def _check(p: Pen):
    p.line([(0.14, 0.54), (0.38, 0.78), (0.86, 0.22)], 0.13)


def _arrow_right(p: Pen):
    p.line([(0.12, 0.50), (0.78, 0.50)], 0.10)
    p.poly([(0.66, 0.26), (0.92, 0.50), (0.66, 0.74)])


def _refresh(p: Pen):
    p.arc(0.12, 0.12, 0.88, 0.88, 40, 330, 0.09)
    p.poly([(0.62, 0.06), (0.92, 0.22), (0.66, 0.36)])


def _flask(p: Pen):
    p.poly([(0.38, 0.10), (0.62, 0.10), (0.62, 0.38), (0.86, 0.82), (0.80, 0.90),
            (0.20, 0.90), (0.14, 0.82), (0.38, 0.38)])


def _printer_glyph(p: Pen):
    p.rect(0.16, 0.44, 0.84, 0.80, radius=0.05, outline=0.055)
    p.rect(0.28, 0.12, 0.72, 0.44, outline=0.05)
    p.rect(0.28, 0.64, 0.72, 0.90, radius=0.02)


def _disk(p: Pen):
    p.rect(0.10, 0.10, 0.90, 0.90, radius=0.04, outline=0.05)
    p.rect(0.30, 0.10, 0.70, 0.36, radius=0.02)
    p.ring(0.50, 0.66, 0.16, 0.05)


GLYPHS = {
    "code": _code,
    "brackets": _brackets,
    "prompt": _prompt,
    "pipe": _pipe,
    "gear": _gear,
    "wrench": _wrench,
    "wire-globe": _wire_globe,
    "globe": _wire_globe,
    "play": _play,
    "spark": _spark,
    "star": _star,
    "nib": _pen_nib,
    "eye": _eye,
    "monitor": _monitor,
    "person": _person,
    "moon": _moon,
    "palette": _palette,
    "keyhole": _keyhole,
    "sliders": _sliders,
    "download": _download,
    "question": _question,
    "question-bold": _question_bold,
    "cards": _cards,
    "feather": _feather,
    "atom": _atom,
    "droplet": _droplet,
    "circuit": _circuit,
    "bird": _bird,
    "wave": _wave,
    "box": _box,
    "leaf": _leaf,
    "film": _film,
    "note": _note,
    "clock": _clock,
    "lock": _lock,
    "shield": _shield,
    "camera": _camera,
    "speaker": _speaker,
    "wifi": _wifi,
    "bluetooth": _bluetooth,
    "battery": _battery,
    "usb": _usb,
    "phone": _phone,
    "headphones": _headphones,
    "mic": _mic,
    "magnifier": _magnifier,
    "key": _key,
    "tag": _tag,
    "folder": _folder,
    "book": _book,
    "home": _home,
    "sun": _sun,
    "grid": _grid,
    "cube": _cube,
    "check": _check,
    "arrow": _arrow_right,
    "refresh": _refresh,
    "flask": _flask,
    "printer": _printer_glyph,
    "disk": _disk,
}


def glyph_mask(name: str, cx: float, cy: float, width: float, height: float | None = None,
               size: int = SIZE) -> np.ndarray:
    """Rasterise ``name`` inside the box centred on ``(cx, cy)``."""
    if name not in GLYPHS:
        raise KeyError(f"unknown glyph {name!r}")
    height = width if height is None else height
    # draw in a unit canvas, then scale into the requested box
    pen = Pen(size)
    GLYPHS[name](pen)
    mask = pen.mask()
    img = Image.fromarray((mask * 255).astype(np.uint8), mode="L")
    target = max(2, int(round(width)))
    img = img.resize((target, max(2, int(round(height)))), Image.LANCZOS)
    canvas = Image.new("L", (size, size), 0)
    canvas.paste(img, (int(round(cx - width / 2)), int(round(cy - height / 2))))
    return np.asarray(canvas, dtype=np.float32) / 255.0
