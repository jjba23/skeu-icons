"""A small relief renderer for skeuomorphic icon artwork.

The icons in this pack are *objects*, not glyphs on a plate, so the drawing code
needs what a vector editor is bad at: a height field per part, normals derived
from it, one key light, environment reflections, contact shadows and a cast
shadow.  Everything is numpy, everything is deterministic, and a 1024 px icon
takes a fraction of a second.

Vocabulary
----------
``Shape``      signed distance field (negative inside) -> coverage, bevel profile
``Canvas``     premultiplied RGBA accumulator with ``paint`` / ``multiply``
``Material``   a shading function ``f(ctx, **opts) -> rgb`` (see materials.py)

A part is ``canvas.paint(shape, material, profile=("bevel", 9, 14), ...)``:
the SDF gives the silhouette and the bevel, the profile gives the height field,
the material turns normals into colour.  Glyphs are painted from masks (PIL),
so text-like marks can be embossed with the same machinery.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

SIZE = 1024

#: direction *towards* the key light: upper left, ~25 deg elevation
LIGHT = np.array([-0.46, -0.56, 0.69], dtype=np.float32)
LIGHT /= np.linalg.norm(LIGHT)
#: halfway vector for a viewer straight on
HALF = LIGHT + np.array([0.0, 0.0, 1.0], dtype=np.float32)
HALF /= np.linalg.norm(HALF)


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #

def hexrgb(value: str) -> np.ndarray:
    value = value.lstrip("#")
    return np.array([int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


def hsl(h: float, s: float, l: float) -> np.ndarray:
    """``h`` degrees, ``s``/``l`` 0..1 -> rgb float array."""
    h = (h % 360.0) / 360.0
    s = float(np.clip(s, 0.0, 1.0))
    l = float(np.clip(l, 0.0, 1.0))
    if s == 0:
        return np.array([l, l, l], dtype=np.float32)

    def f(n: float) -> float:
        k = (n + h * 12) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1.0, min(k - 3, min(9 - k, 1.0)))

    return np.array([f(0), f(8), f(4)], dtype=np.float32)


def clamp01(a: np.ndarray) -> np.ndarray:
    return np.clip(a, 0.0, 1.0)


def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def vramp(t: np.ndarray, stops: list[tuple[float, tuple[float, float, float]]]) -> np.ndarray:
    """Vertical gradient lookup: ``t`` in 0..1 -> (h, w, 3)."""
    ts = np.array([s[0] for s in stops], dtype=np.float32)
    cols = np.array([s[1] for s in stops], dtype=np.float32)
    t = np.clip(t, 0.0, 1.0)
    out = np.empty(t.shape + (3,), dtype=np.float32)
    for ch in range(3):
        out[..., ch] = np.interp(t, ts, cols[:, ch]).astype(np.float32)
    return out


def _box(a: np.ndarray, radius: int, axis: int) -> np.ndarray:
    if radius < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (radius + 1, radius)
    padded = np.pad(a, pad, mode="edge")
    acc = np.cumsum(padded, axis=axis, dtype=np.float32)
    width = 2 * radius + 1
    hi = np.take(acc, np.arange(width, acc.shape[axis]), axis=axis)
    lo = np.take(acc, np.arange(0, acc.shape[axis] - width), axis=axis)
    return (hi - lo) / width


def blur(a: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian-ish blur (three box passes); ``sigma`` in pixels."""
    if sigma <= 0.4:
        return a.astype(np.float32)
    radius = max(1, int(round(sigma - 0.5)))
    out = a.astype(np.float32)
    for _ in range(3):
        out = _box(_box(out, radius, 0), radius, 1)
    return out


def noise(size: int, cell: float, seed: int, octaves: int = 2) -> np.ndarray:
    """Smooth value noise in 0..1, ``cell`` pixels per feature."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((size, size), dtype=np.float32)
    weight = 1.0
    total = 0.0
    for octave in range(octaves):
        cells = max(2, int(size / max(1.0, cell) * (2 ** octave)))
        small = rng.random((cells, cells)).astype(np.float32)
        layer = np.asarray(
            Image.fromarray(small, mode="F").resize((size, size), Image.BICUBIC),
            dtype=np.float32,
        )
        acc += layer * weight
        total += weight
        weight *= 0.5
    acc /= total
    lo, hi = float(acc.min()), float(acc.max())
    return (acc - lo) / max(1e-6, hi - lo)


def streak_noise(size: int, seed: int, along: str = "y") -> np.ndarray:
    """1-D noise stretched into brush streaks / grain."""
    rng = np.random.default_rng(seed)
    n = rng.random(size).astype(np.float32)
    line = np.asarray(Image.fromarray(n[None, :], mode="F").resize((size, size), Image.BICUBIC),
                      dtype=np.float32)
    line = (line - line.min()) / max(1e-6, float(line.max() - line.min()))
    return line if along == "y" else line.T.copy()


# --------------------------------------------------------------------------- #
# shapes: signed distance fields
# --------------------------------------------------------------------------- #

class Shape:
    """Signed distance field, negative inside."""

    def sdf(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:  # pragma: no cover - abstract
        raise NotImplementedError

    def bounds(self) -> tuple[float, float, float, float]:
        return (0.0, 0.0, float(SIZE), float(SIZE))

    def __or__(self, other: "Shape") -> "Shape":
        return Compound("union", self, other)

    def __and__(self, other: "Shape") -> "Shape":
        return Compound("intersect", self, other)

    def __sub__(self, other: "Shape") -> "Shape":
        return Compound("subtract", self, other)

    def offset(self, r: float) -> "Shape":
        return Offset(self, r)

    def rotated(self, degrees: float, cx: float, cy: float) -> "Shape":
        return Rotated(self, degrees, cx, cy)


class Circle(Shape):
    def __init__(self, cx: float, cy: float, r: float):
        self.cx, self.cy, self.r = cx, cy, r

    def sdf(self, X, Y):
        return np.hypot(X - self.cx, Y - self.cy).astype(np.float32) - self.r

    def bounds(self):
        return (self.cx - self.r, self.cy - self.r, self.cx + self.r, self.cy + self.r)


class Ellipse(Shape):
    def __init__(self, cx: float, cy: float, rx: float, ry: float):
        self.cx, self.cy, self.rx, self.ry = cx, cy, rx, ry

    def sdf(self, X, Y):
        k = np.sqrt(((X - self.cx) / self.rx) ** 2 + ((Y - self.cy) / self.ry) ** 2)
        return ((k - 1.0) * min(self.rx, self.ry)).astype(np.float32)

    def bounds(self):
        return (self.cx - self.rx, self.cy - self.ry, self.cx + self.rx, self.cy + self.ry)


class RRect(Shape):
    def __init__(self, cx: float, cy: float, w: float, h: float, r: float = 0.0):
        self.cx, self.cy, self.hw, self.hh, self.r = cx, cy, w / 2, h / 2, min(r, min(w, h) / 2)

    def sdf(self, X, Y):
        qx = np.abs(X - self.cx) - (self.hw - self.r)
        qy = np.abs(Y - self.cy) - (self.hh - self.r)
        outside = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0))
        inside = np.minimum(np.maximum(qx, qy), 0)
        return (outside + inside - self.r).astype(np.float32)

    def bounds(self):
        return (self.cx - self.hw, self.cy - self.hh, self.cx + self.hw, self.cy + self.hh)


class Capsule(Shape):
    def __init__(self, x0: float, y0: float, x1: float, y1: float, r: float):
        self.x0, self.y0, self.x1, self.y1, self.r = x0, y0, x1, y1, r

    def sdf(self, X, Y):
        ax, ay = self.x1 - self.x0, self.y1 - self.y0
        px, py = X - self.x0, Y - self.y0
        t = np.clip((px * ax + py * ay) / max(1e-6, ax * ax + ay * ay), 0.0, 1.0)
        return (np.hypot(px - ax * t, py - ay * t) - self.r).astype(np.float32)

    def bounds(self):
        return (min(self.x0, self.x1) - self.r, min(self.y0, self.y1) - self.r,
                max(self.x0, self.x1) + self.r, max(self.y0, self.y1) + self.r)


class Poly(Shape):
    """Polygon; ``rounding`` dilates it, which rounds every corner."""

    def __init__(self, points, rounding: float = 0.0):
        self.points = [(float(x), float(y)) for x, y in points]
        self.rounding = rounding

    def sdf(self, X, Y):
        pts = self.points
        n = len(pts)
        d = np.full(X.shape, 1e9, dtype=np.float32)
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            px, py = X - ax, Y - ay
            t = np.clip((px * ex + py * ey) / max(1e-6, ex * ex + ey * ey), 0.0, 1.0)
            d = np.minimum(d, np.hypot(px - ex * t, py - ey * t).astype(np.float32))
        inside = np.zeros(X.shape, dtype=bool)
        j = n - 1
        for i in range(n):
            xi, yi = pts[i]
            xj, yj = pts[j]
            cond = ((yi > Y) != (yj > Y)) & (X < (xj - xi) * (Y - yi) / (yj - yi + 1e-12) + xi)
            inside ^= cond
            j = i
        return (np.where(inside, -d, d) - self.rounding).astype(np.float32)

    def bounds(self):
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        r = self.rounding
        return (min(xs) - r, min(ys) - r, max(xs) + r, max(ys) + r)


class Compound(Shape):
    def __init__(self, op: str, a: Shape, b: Shape):
        self.op, self.a, self.b = op, a, b

    def sdf(self, X, Y):
        da = self.a.sdf(X, Y)
        db = self.b.sdf(X, Y)
        if self.op == "union":
            return np.minimum(da, db)
        if self.op == "intersect":
            return np.maximum(da, db)
        return np.maximum(da, -db)

    def bounds(self):
        ax0, ay0, ax1, ay1 = self.a.bounds()
        bx0, by0, bx1, by1 = self.b.bounds()
        return (min(ax0, bx0), min(ay0, by0), max(ax1, bx1), max(ay1, by1))


class Offset(Shape):
    def __init__(self, inner: Shape, r: float):
        self.inner, self.r = inner, r

    def sdf(self, X, Y):
        return self.inner.sdf(X, Y) - self.r

    def bounds(self):
        x0, y0, x1, y1 = self.inner.bounds()
        return (x0 - self.r, y0 - self.r, x1 + self.r, y1 + self.r)


class Moved(Shape):
    def __init__(self, inner: Shape, dx: float, dy: float):
        self.inner, self.dx, self.dy = inner, dx, dy

    def sdf(self, X, Y):
        return self.inner.sdf(X - self.dx, Y - self.dy)

    def bounds(self):
        x0, y0, x1, y1 = self.inner.bounds()
        return (x0 + self.dx, y0 + self.dy, x1 + self.dx, y1 + self.dy)


class Rotated(Shape):
    def __init__(self, inner: Shape, degrees: float, cx: float, cy: float):
        self.inner, self.degrees, self.cx, self.cy = inner, degrees, cx, cy
        self.angle = math.radians(degrees)
        self.cos, self.sin = math.cos(self.angle), math.sin(self.angle)

    def sdf(self, X, Y):
        dx, dy = X - self.cx, Y - self.cy
        xr = dx * self.cos + dy * self.sin + self.cx
        yr = -dx * self.sin + dy * self.cos + self.cy
        return self.inner.sdf(xr, yr)

    def bounds(self):
        x0, y0, x1, y1 = self.inner.bounds()
        return (self.cx - max(abs(x0 - self.cx), abs(x1 - self.cx)),
                self.cy - max(abs(y0 - self.cy), abs(y1 - self.cy)),
                self.cx + max(abs(x0 - self.cx), abs(x1 - self.cx)),
                self.cy + max(abs(y0 - self.cy), abs(y1 - self.cy)))


# --------------------------------------------------------------------------- #
# shape kit
# --------------------------------------------------------------------------- #

def ring(cx: float, cy: float, r: float, width: float) -> Shape:
    """A circular band of the given width centred on radius ``r``."""

    class _Ring(Shape):
        def sdf(self, X, Y):
            d = np.hypot(X - cx, Y - cy) - r
            return (np.abs(d) - width / 2).astype(np.float32)

        def bounds(self):
            return (cx - r - width, cy - r - width, cx + r + width, cy + r + width)

    return _Ring()


def gear_polygon(cx: float, cy: float, r_out: float, r_in: float, teeth: int,
                 phase: float = 0.0, tooth: float = 0.55) -> list[tuple[float, float]]:
    """A machined gear outline: ``teeth`` trapezoid teeth around a hub."""
    pts: list[tuple[float, float]] = []
    step = 2 * math.pi / teeth
    for i in range(teeth):
        a = phase + i * step
        half = step * tooth / 2
        for radius, offset in ((r_in, -1.25), (r_out, -1.0), (r_out, 0.62), (r_in, 0.92)):
            angle = a + half * offset
            pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts


def polyline_mask(points, width: float, size: int = SIZE, closed: bool = False,
                  smooth: int = 2) -> np.ndarray:
    """Rasterise a stroke into an anti-aliased mask (0..1)."""
    scale = smooth
    img = Image.new("L", (size * scale, size * scale), 0)
    draw = ImageDraw.Draw(img)
    seq = [(x * scale, y * scale) for x, y in points]
    if closed:
        seq = seq + [seq[0]]
    draw.line(seq, fill=255, width=max(1, int(round(width * scale))), joint="curve")
    img = img.resize((size, size), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32) / 255.0


def dots_mask(size: int, spacing: float, radius: float, offset: tuple[float, float] = (0.0, 0.0),
              bounds: tuple[float, float, float, float] | None = None, smooth: int = 3) -> np.ndarray:
    """A regular dot grid (speaker grille, perforated metal)."""
    scale = smooth
    img = Image.new("L", (size * scale, size * scale), 0)
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = bounds or (0, 0, size, size)
    y = y0 - spacing
    row = 0
    while y < y1 + spacing:
        x = x0 - spacing + (spacing / 2 if row % 2 else 0) + offset[0]
        while x < x1 + spacing:
            draw.ellipse([(x - radius + offset[0]) * scale, (y - radius + offset[1]) * scale,
                          (x + radius + offset[0]) * scale, (y + radius + offset[1]) * scale],
                         fill=255)
            x += spacing
        y += spacing * 0.86
        row += 1
    return np.asarray(img.resize((size, size), Image.LANCZOS), dtype=np.float32) / 255.0


# --------------------------------------------------------------------------- #
# canvas
# --------------------------------------------------------------------------- #

def _height(d: np.ndarray, profile, radius: float) -> np.ndarray:
    """Height field (in pixels) from the SDF ``d`` and a profile."""
    if profile is None:
        return np.zeros_like(d)
    kind = profile[0]
    if kind == "flat":
        return np.zeros_like(d)
    if kind == "bevel":
        amp, width = float(profile[1]), float(profile[2])
        u = np.clip(-d / width, 0.0, 1.0)
        return (amp * np.sqrt(np.clip(2 * u - u * u, 0.0, 1.0))).astype(np.float32)
    if kind == "sphere":
        amp = float(profile[1])
        r = max(1.0, radius)
        return (amp * np.sqrt(np.clip(-2 * r * d - d * d, 0.0, r * r)) / r).astype(np.float32)
    if kind == "tilt":
        return np.zeros_like(d)
    raise ValueError(f"unknown profile {profile!r}")


def _normals(height: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gy, gx = np.gradient(height.astype(np.float32))
    nx = -gx
    ny = -gy
    nz = np.ones_like(nx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx / length).astype(np.float32), (ny / length).astype(np.float32), (nz / length).astype(np.float32)


@dataclass
class Context:
    X: np.ndarray
    Y: np.ndarray
    nx: np.ndarray
    ny: np.ndarray
    nz: np.ndarray
    d: np.ndarray
    cover: np.ndarray
    yfrac: np.ndarray
    xfrac: np.ndarray
    size: int
    bbox: tuple[float, float, float, float]
    seed: int


class Canvas:
    """Premultiplied RGBA accumulator at ``size`` x ``size``."""

    def __init__(self, size: int = SIZE, seed: int = 7):
        self.size = size
        self.rgb = np.zeros((size, size, 3), dtype=np.float32)   # premultiplied
        self.alpha = np.zeros((size, size), dtype=np.float32)
        y, x = np.mgrid[0:size, 0:size].astype(np.float32)
        self.X = x + 0.5
        self.Y = y + 0.5
        self.seed = seed
        self._noise: dict[tuple[int, int, float], np.ndarray] = {}
        self.shadow_opts: dict = {
            "offset": (0.0, 26.0), "sigma": 42.0, "opacity": 0.40,
            "contact_sigma": 9.0, "contact_opacity": 0.30,
            "colour": (0.17, 0.21, 0.29),
        }

    # -- noise cache ------------------------------------------------------- #
    def noise(self, cell: float, seed: int | None = None) -> np.ndarray:
        key = (seed if seed is not None else self.seed, 0, cell)
        if key not in self._noise:
            self._noise[key] = noise(self.size, cell, key[0])
        return self._noise[key]

    # -- painting ---------------------------------------------------------- #
    def context(self, shape: Shape, cover: np.ndarray | None = None,
                height: np.ndarray | None = None) -> Context:
        d = shape.sdf(self.X, self.Y)
        x0, y0, x1, y1 = shape.bounds()
        if cover is None:
            cover = smoothstep(0.0, 1.2, 0.6 - d)
        if height is None:
            height = np.zeros_like(d)
        nx, ny, nz = _normals(height)
        width = max(1.0, x1 - x0)
        height_px = max(1.0, y1 - y0)
        return Context(
            X=self.X, Y=self.Y, nx=nx, ny=ny, nz=nz, d=d, cover=cover,
            yfrac=np.clip((self.Y - y0) / height_px, 0.0, 1.0),
            xfrac=np.clip((self.X - x0) / width, 0.0, 1.0),
            size=self.size, bbox=(x0, y0, x1, y1), seed=self.seed,
        )

    def paint(self, shape: Shape, material, *, profile=("flat",), alpha: float = 1.0,
              shadow: bool = False, shadow_offset: tuple[float, float] = (0.0, 7.0),
              shadow_sigma: float = 13.0, shadow_alpha: float = 0.34,
              contact: float = 0.0, mask: np.ndarray | None = None,
              height_scale: float = 1.0, **opts) -> np.ndarray:
        """Shade one part and composite it.

        ``contact`` darkens the area just outside the part (a tight ambient
        occlusion ring), which is what keeps stacked parts from floating.
        """
        d = shape.sdf(self.X, self.Y)
        cover = smoothstep(0.0, 1.3, 0.6 - d)
        if mask is not None:
            cover = np.minimum(cover, mask)
        height = _height(d, profile, self._radius(shape, profile)) * height_scale
        if mask is not None:
            height = height * np.maximum(mask, 0.0)
        ctx = self.context(shape, cover=cover, height=height)
        rgb = material(ctx, **opts).astype(np.float32)

        if shadow:
            self.cast(cover, offset=shadow_offset, sigma=shadow_sigma, opacity=shadow_alpha)
        if contact:
            ring = smoothstep(0.0, 6.0, d + 5.0) * smoothstep(14.0, 2.0, d)
            self.multiply(blur(ring, 3.0), contact)

        a = (cover * alpha).astype(np.float32)
        self.rgb = self.rgb * (1.0 - a)[..., None] + rgb * a[..., None]
        self.alpha = a + self.alpha * (1.0 - a)
        return rgb

    @staticmethod
    def _radius(shape: Shape, profile) -> float:
        if not profile or profile[0] != "sphere":
            return 1.0
        x0, y0, x1, y1 = shape.bounds()
        return max(1.0, min(x1 - x0, y1 - y0) / 2)

    def paint_mask(self, mask: np.ndarray, material, *, emboss: float = 3.0,
                   soft: float = 1.0, alpha: float = 1.0, **opts) -> None:
        """Paint a rasterised mark, optionally embossed (raised by ``emboss`` px)."""
        cover = blur(mask, soft) * alpha
        height = blur(mask, max(1.0, soft * 2.2)) * emboss
        shape = _Masked(cover)
        ctx = self.context(shape, cover=cover, height=height)
        rgb = material(ctx, **opts).astype(np.float32)
        a = cover.astype(np.float32)
        self.rgb = self.rgb * (1.0 - a)[..., None] + rgb * a[..., None]
        self.alpha = a + self.alpha * (1.0 - a)

    def multiply(self, mask: np.ndarray, strength: float,
                 colour: tuple[float, float, float] = (0.16, 0.20, 0.28)) -> None:
        """Darken the destination through ``mask`` (ambient occlusion / contact)."""
        amount = np.clip(mask * strength, 0.0, 1.0).astype(np.float32)
        tint = np.array(colour, dtype=np.float32)
        self.rgb *= (1.0 - amount[..., None]) + amount[..., None] * tint
        self.alpha *= 1.0  # alpha is owned by the artwork, not by shading

    def cast(self, cover: np.ndarray, *, offset=(0.0, 7.0), sigma: float = 13.0,
             opacity: float = 0.34, colour=(0.17, 0.21, 0.29)) -> None:
        """Soft cast shadow of ``cover``, composited *under* what is already there."""
        shadow = np.zeros_like(cover)
        dx, dy = int(round(offset[0])), int(round(offset[1]))
        ys = slice(max(0, dy), self.size + min(0, dy))
        xs = slice(max(0, dx), self.size + min(0, dx))
        sy = slice(max(0, -dy), self.size + min(0, -dy))
        sx = slice(max(0, -dx), self.size + min(0, -dx))
        shadow[ys, xs] = cover[sy, sx]
        shadow = blur(shadow, sigma) * opacity
        # shadow sits behind: un-premultiply what is there, darken, re-premultiply
        base_a = np.maximum(self.alpha, 1e-6)
        base = self.rgb / base_a[..., None]
        tint = np.array(colour, dtype=np.float32)
        lit = base * (1.0 - shadow[..., None]) + tint * shadow[..., None]
        self.rgb = lit * base_a[..., None]

    def finish(self, background: tuple[float, float, float] | None = None,
               shadow: bool = True) -> Image.Image:
        alpha = np.clip(self.alpha, 0.0, 1.0)
        rgb = np.where(alpha[..., None] > 1e-5, self.rgb / np.maximum(alpha, 1e-6)[..., None], 0.0)
        if shadow:
            opts = self.shadow_opts
            sh = _shift(alpha, *opts["offset"])
            wide = blur(sh, opts["sigma"]) * opts["opacity"]
            tight = blur(_shift(alpha, opts["offset"][0] * 0.3, 10.0),
                         opts["contact_sigma"]) * opts["contact_opacity"]
            shade = np.clip(wide + tight * (1.0 - wide), 0.0, 1.0) * (1.0 - alpha)
            tint = np.array(opts["colour"], dtype=np.float32)
            out_a = alpha + shade
            rgb = (rgb * alpha[..., None] + tint * shade[..., None]) / np.maximum(out_a, 1e-6)[..., None]
            alpha = out_a
        rgb = np.clip(rgb, 0.0, 1.0)
        if background is not None:
            bg = np.array(background, dtype=np.float32)
            rgb = rgb * alpha[..., None] + bg * (1.0 - alpha[..., None])
            alpha = np.ones_like(alpha)
        out = np.concatenate([rgb, alpha[..., None]], axis=2)
        return Image.fromarray((out * 255.0 + 0.5).astype(np.uint8), mode="RGBA")

    def save(self, path, background=None) -> None:
        image = self.finish(background)
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        image.save(path)


class _Masked(Shape):
    """A shape whose membership is already known; only ``bounds`` is needed."""

    def __init__(self, cover: np.ndarray):
        self.cover = cover

    def sdf(self, X, Y):
        # Scale the coverage ramp into an approximate distance so edge effects
        # (rim light, terminator, inner shadow) stay a few pixels wide instead of
        # washing over the whole glyph.
        return ((0.5 - self.cover) * 12.0).astype(np.float32)


# --------------------------------------------------------------------------- #
# canvas-level effects
# --------------------------------------------------------------------------- #

def _shift(a: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Move an array by whole pixels, filling with zero."""
    out = np.zeros_like(a)
    ix, iy = int(round(dx)), int(round(dy))
    ys = slice(max(0, iy), a.shape[0] + min(0, iy))
    xs = slice(max(0, ix), a.shape[1] + min(0, ix))
    sy = slice(max(0, -iy), a.shape[0] + min(0, -iy))
    sx = slice(max(0, -ix), a.shape[1] + min(0, -ix))
    out[ys, xs] = a[sy, sx]
    return out


def cast_shadow(canvas: Canvas, *, offset=(0.0, 26.0), sigma: float = 42.0,
                opacity: float = 0.40, contact_sigma: float = 9.0,
                contact_opacity: float = 0.30) -> None:
    """Configure the two-layer shadow the icon finishes with (applied in finish)."""
    canvas.shadow_opts.update(offset=offset, sigma=sigma, opacity=opacity,
                              contact_sigma=contact_sigma,
                              contact_opacity=contact_opacity)


def vignette(canvas: Canvas, strength: float = 0.05) -> None:
    """Very slight edge falloff, as if the object sat in a lit room."""
    y, x = np.mgrid[0:canvas.size, 0:canvas.size].astype(np.float32)
    r = np.hypot(x - canvas.size / 2, y - canvas.size / 2) / (canvas.size / 2)
    canvas.multiply(smoothstep(0.55, 1.35, r), strength)
