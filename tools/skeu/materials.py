"""Material models for the relief renderer.

Every material is a function ``material(ctx, **opts) -> rgb`` where ``ctx`` is a
:class:`skeu.paint.Context`.  They follow one recipe: a base colour (a vertical
gradient in the part's own frame), a single key light, a specular lobe, and a rim
that is a *material* rather than an outline.  Colour stays in the accent; the
body is metal, glass or paper.

Reference numbers these aim at (measured from the 2000s desktop artwork this
pack follows):
median body saturation 0.05, median value 0.82, coloured pixels 10 %, accent
saturation 0.42, plate corner radius 5 % of width.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .paint import HALF, LIGHT, blur, clamp01, hexrgb, hsl, noise, smoothstep, vramp

LX, LY, LZ = (float(v) for v in LIGHT)
HX, HY, HZ = (float(v) for v in HALF)


@lru_cache(maxsize=96)
def _tex(size: int, cell: float, seed: int) -> np.ndarray:
    return noise(size, cell, seed)


def _ndl(ctx) -> np.ndarray:
    return clamp01(ctx.nx * LX + ctx.ny * LY + ctx.nz * LZ)


def _diffuse(ctx, ambient: float = 0.62, gain: float = 0.38) -> np.ndarray:
    return ambient + gain * _ndl(ctx)


def _spec(ctx, power: float, gain: float) -> np.ndarray:
    dot = clamp01(ctx.nx * HX + ctx.ny * HY + ctx.nz * HZ)
    return (dot ** power) * gain


def _rim(ctx, width: float = 3.2, gain: float = 0.55) -> np.ndarray:
    """A lit bevel just inside the silhouette, on the light side only."""
    band = np.exp(-(((ctx.d + width * 0.55) / width) ** 2))
    lit = clamp01(ctx.nx * LX + ctx.ny * LY + 0.25)
    return band * lit * gain


def _env(ctx, stops, bend: float = 0.30) -> np.ndarray:
    e = clamp01(ctx.yfrac - bend * ctx.ny)
    return vramp(e, stops)


def _studio(ctx, stops, bend: float = 0.90, mix: float = 0.22) -> np.ndarray:
    """Metal reflects the studio, so the ramp is keyed to the normal first.

    A surface facing up sees the bright sky, one facing down sees the dark floor,
    and a vertical face sits at the horizon.  That is what makes a bevel read as
    a chamfer instead of a painted stripe.
    """
    e = clamp01(0.5 - bend * ctx.ny + mix * (ctx.yfrac - 0.5))
    return vramp(e, stops)


def _edge_shade(ctx, width: float = 5.0, amount: float = 0.22) -> np.ndarray:
    """Darken the bevel that faces away from the key light (no outline stroke)."""
    away = clamp01(-(ctx.nx * LX + ctx.ny * LY))
    band = smoothstep(-width, -0.4, ctx.d)
    return 1.0 - amount * band * away


# --------------------------------------------------------------------------- #
# metals
# --------------------------------------------------------------------------- #

ALU = [
    (0.00, (0.870, 0.884, 0.906)),
    (0.34, (0.700, 0.724, 0.760)),
    (0.50, (0.640, 0.668, 0.708)),
    (0.56, (0.800, 0.820, 0.852)),
    (0.66, (0.868, 0.884, 0.908)),
    (0.86, (0.752, 0.776, 0.812)),
    (1.00, (0.652, 0.680, 0.720)),
]

CHROME = [
    (0.00, (0.190, 0.225, 0.275)),
    (0.16, (0.430, 0.468, 0.525)),
    (0.34, (0.800, 0.832, 0.875)),
    (0.45, (0.995, 1.000, 1.000)),
    (0.52, (0.585, 0.625, 0.685)),
    (0.62, (0.890, 0.912, 0.948)),
    (0.78, (0.520, 0.560, 0.620)),
    (1.00, (0.955, 0.970, 0.995)),
]

BRASS = [
    (0.00, (0.250, 0.165, 0.040)),
    (0.18, (0.540, 0.375, 0.105)),
    (0.36, (0.900, 0.715, 0.300)),
    (0.46, (1.000, 0.950, 0.720)),
    (0.54, (0.690, 0.510, 0.165)),
    (0.66, (0.950, 0.780, 0.360)),
    (0.82, (0.610, 0.440, 0.130)),
    (1.00, (0.965, 0.855, 0.545)),
]

STEEL = [
    (0.00, (0.120, 0.132, 0.150)),
    (0.18, (0.225, 0.240, 0.265)),
    (0.40, (0.360, 0.380, 0.415)),
    (0.50, (0.455, 0.475, 0.510)),
    (0.58, (0.270, 0.290, 0.320)),
    (0.78, (0.190, 0.205, 0.230)),
    (1.00, (0.330, 0.350, 0.385)),
]


ALU_SHEET = [
    (0.00, (0.945, 0.955, 0.970)),
    (0.30, (0.880, 0.895, 0.918)),
    (0.52, (0.800, 0.820, 0.848)),
    (0.66, (0.735, 0.755, 0.788)),
    (0.86, (0.640, 0.665, 0.700)),
    (1.00, (0.560, 0.585, 0.625)),
]


def aluminium(ctx, brush: float = 0.035, seed: int = 11, cool: float = 1.0, **_) -> np.ndarray:
    base = 0.42 * _studio(ctx, ALU, bend=0.62, mix=0.34) + 0.58 * vramp(ctx.yfrac, ALU_SHEET)
    streak = _tex(ctx.size, 3.0, seed).T          # vertical brush lines
    base = base * (0.99 + brush * (streak[..., None] - 0.5) * 2.0)
    rgb = base * _diffuse(ctx, 0.80, 0.24)[..., None] + _spec(ctx, 52.0, 0.26)[..., None]
    rgb *= _edge_shade(ctx, 6.0, 0.20)[..., None]
    rgb += _rim(ctx, 2.8, 0.45)[..., None]
    if cool != 1.0:
        rgb[..., 2] *= cool
        rgb[..., 0] /= cool
    return clamp01(rgb)


def chrome(ctx, brush: float = 0.0, seed: int = 12, **_) -> np.ndarray:
    base = _studio(ctx, CHROME, bend=0.95, mix=0.18)
    if brush:
        streak = _tex(ctx.size, 2.4, seed).T
        base = base * (0.98 + brush * (streak[..., None] - 0.5) * 2.0)
    rgb = base * _diffuse(ctx, 0.90, 0.14)[..., None] + _spec(ctx, 130.0, 0.55)[..., None]
    rgb *= _edge_shade(ctx, 4.5, 0.30)[..., None]
    rgb += _rim(ctx, 2.4, 0.55)[..., None]
    return clamp01(rgb)


def brass(ctx, **_) -> np.ndarray:
    base = _studio(ctx, BRASS, bend=0.88, mix=0.20)
    rgb = base * _diffuse(ctx, 0.88, 0.18)[..., None] + _spec(ctx, 110.0, 0.50)[..., None]
    rgb *= _edge_shade(ctx, 5.0, 0.26)[..., None]
    rgb += _rim(ctx, 2.4, 0.50)[..., None]
    return clamp01(rgb)


def steel(ctx, brushed: bool = True, seed: int = 13, **_) -> np.ndarray:
    base = _studio(ctx, STEEL, bend=0.72, mix=0.28)
    if brushed:
        streak = _tex(ctx.size, 2.8, seed).T
        base = base * (0.98 + 0.07 * (streak[..., None] - 0.5))
    rgb = base * _diffuse(ctx, 0.86, 0.20)[..., None] + _spec(ctx, 80.0, 0.32)[..., None]
    rgb *= _edge_shade(ctx, 5.0, 0.22)[..., None]
    rgb += _rim(ctx, 2.6, 0.32)[..., None]
    return clamp01(rgb)


def gunmetal(ctx, **_) -> np.ndarray:
    base = _env(ctx, [(0.0, (0.30, 0.32, 0.35)), (0.45, (0.20, 0.215, 0.24)),
                      (0.55, (0.34, 0.36, 0.39)), (1.0, (0.16, 0.17, 0.19))])
    rgb = base * _diffuse(ctx, 0.80, 0.30)[..., None] + _spec(ctx, 60.0, 0.35)[..., None]
    return clamp01(rgb)


# --------------------------------------------------------------------------- #
# glass and enamel
# --------------------------------------------------------------------------- #

def glass(ctx, hue: float = 212, sat: float = 0.80, light: float = 0.52,
          gloss: float = 1.0, opacity: float = 0.96, **_) -> np.ndarray:
    """Tinted glass, the pack blue by default: deep body, hard gloss, bright rim."""
    top = hsl(hue, sat * 0.74, min(0.76, light + 0.19))
    upper = hsl(hue, sat * 0.94, min(0.68, light + 0.08))
    mid = hsl(hue, sat, light)
    low = hsl(hue, min(1.0, sat * 1.08), max(0.11, light - 0.30))
    base = vramp(ctx.yfrac, [(0.00, tuple(top)), (0.26, tuple(upper)),
                             (0.50, tuple(mid)), (0.66, tuple(mid * 0.93)),
                             (1.00, tuple(low))])
    rgb = base * (0.80 + 0.34 * _ndl(ctx))[..., None]

    # a bright vertical reflection down the lit edge (the Lion/Aqua tell)
    edge = (np.exp(-(((ctx.xfrac - 0.075) / 0.045) ** 2))
            * smoothstep(0.06, 0.18, ctx.yfrac) * (1.0 - smoothstep(0.60, 0.84, ctx.yfrac)))
    rgb = rgb * (1.0 - 0.60 * gloss * edge[..., None]) + \
        hsl(hue, sat * 0.22, 0.98) * (0.60 * gloss * edge)[..., None]
    # capsule gloss: hard top edge, feathered bottom, upper 8-30 % of the part
    band = smoothstep(0.030, 0.050, ctx.yfrac) * (1.0 - smoothstep(0.20, 0.32, ctx.yfrac))
    rgb = rgb * (1.0 - 0.80 * gloss * band[..., None]) + 0.985 * (0.80 * gloss * band)[..., None]
    # the reflection of a window: a soft blob upper-left, the classic Aqua tell
    window = np.exp(-((((ctx.xfrac - 0.38) / 0.21) ** 2 + ((ctx.yfrac - 0.19) / 0.12) ** 2)))
    rgb = rgb * (1.0 - 0.26 * gloss * window[..., None]) + 0.995 * (0.26 * gloss * window)[..., None]
    # its reflection, inverted and compressed, in the lower half
    band2 = smoothstep(0.62, 0.70, ctx.yfrac) * (1.0 - smoothstep(0.78, 0.90, ctx.yfrac))
    rgb = rgb * (1.0 - 0.12 * gloss * band2[..., None]) + 0.96 * (0.12 * gloss * band2)[..., None]
    # caustic in the lower third: a warm-ish pool of light inside the glass
    caustic = (np.exp(-(((ctx.yfrac - 0.84) / 0.11) ** 2))
               * np.exp(-(((ctx.xfrac - 0.46) / 0.34) ** 2))
               * (0.55 + 0.45 * _tex(ctx.size, 90.0, 3)))
    rgb = rgb * (1.0 - 0.22 * caustic[..., None]) + \
        hsl(hue, sat * 0.34, 0.90) * (0.22 * caustic)[..., None]
    # edge deepening + lit rim
    rgb *= (1.0 - 0.42 * smoothstep(-9.0, -0.4, ctx.d))[..., None]
    rgb += hsl(hue, sat * 0.30, 0.94) * _rim(ctx, 2.6, 1.00)[..., None]
    rgb += _spec(ctx, 110.0, 0.45)[..., None]
    return clamp01(rgb)


def crystal(ctx, hue: float = 210, sat: float = 0.78, light: float = 0.50,
            **_ ) -> np.ndarray:
    """A cut gem: a saturated body with internal light and a hard highlight.

    This is the material for medallion stones and enamel-cased accents - brighter
    and more chromatic than :func:`glass`, because a gem is a small object and has
    to carry the colour of the whole icon without washing out.
    """
    top = hsl(hue, sat * 0.62, min(0.80, light + 0.26))
    upper = hsl(hue, sat * 0.92, min(0.70, light + 0.12))
    mid = hsl(hue, sat, light)
    deep = hsl(hue, min(1.0, sat * 1.16), max(0.09, light - 0.38))
    base = vramp(ctx.yfrac, [(0.00, tuple(top)), (0.24, tuple(upper)),
                             (0.46, tuple(mid)), (0.64, tuple(mid * 0.90)),
                             (1.00, tuple(deep))])
    rgb = base * (0.78 + 0.36 * _ndl(ctx))[..., None]
    # light scattered inside the stone: a broad glow in the upper-left quadrant
    inner = np.exp(-((((ctx.xfrac - 0.40) / 0.30) ** 2 +
                      ((ctx.yfrac - 0.32) / 0.26) ** 2)))
    rgb = rgb * (1.0 - 0.24 * inner[..., None]) + \
        hsl(hue, sat * 0.42, 0.88) * (0.24 * inner)[..., None]
    # a caustic fan at the bottom, where the light leaves the stone
    fan = (np.exp(-(((ctx.yfrac - 0.80) / 0.10) ** 2))
           * (0.55 + 0.45 * _tex(ctx.size, 70.0, 5)))
    rgb = rgb * (1.0 - 0.30 * fan[..., None]) + \
        hsl(hue, sat * 0.30, 0.92) * (0.30 * fan)[..., None]
    # hard specular: the highlight that reads as polished stone at any size
    dot = clamp01(ctx.nx * HX + ctx.ny * HY + ctx.nz * HZ)
    rgb += (dot ** 48.0)[..., None] * 0.45
    rgb += np.exp(-((((ctx.xfrac - 0.30) / 0.085) ** 2 +
                     ((ctx.yfrac - 0.24) / 0.055) ** 2)))[..., None] * 0.55
    # deep edge, bright rim
    rgb *= (1.0 - 0.46 * smoothstep(-10.0, -0.4, ctx.d))[..., None]
    rgb += hsl(hue, sat * 0.26, 0.97) * _rim(ctx, 3.0, 0.95)[..., None]
    return clamp01(rgb)


def enamel(ctx, hue: float = 210, sat: float = 0.64, light: float = 0.54,
           gloss: float = 0.58, **_) -> np.ndarray:
    """Baked enamel paint: a lit dome, a hard hotspot, a dark terminator."""
    top = hsl(hue, sat * 0.74, min(0.88, light + 0.17))
    upper = hsl(hue, sat * 0.94, min(0.74, light + 0.06))
    mid = hsl(hue, sat, light)
    low = hsl(hue, min(1.0, sat * 1.06), max(0.12, light - 0.20))
    base = vramp(ctx.yfrac, [(0.00, tuple(top)), (0.30, tuple(upper)),
                             (0.52, tuple(mid)), (0.62, tuple(mid * 0.94)),
                             (1.00, tuple(low))])
    rgb = base * _diffuse(ctx, 0.64, 0.46)[..., None]
    hotspot = (smoothstep(0.06, 0.14, ctx.yfrac) * (1.0 - smoothstep(0.22, 0.40, ctx.yfrac))
               * (1.0 - smoothstep(0.26, 0.78, ctx.xfrac))
               * (0.35 + 0.65 * np.exp(-(((ctx.xfrac - 0.30) / 0.22) ** 2))))
    rgb = rgb * (1.0 - 0.34 * gloss * hotspot[..., None]) + 0.99 * (0.34 * gloss * hotspot)[..., None]
    term = smoothstep(0.82, 1.0, ctx.yfrac) * (1.0 - smoothstep(-8.0, -1.0, ctx.d))
    rgb *= (1.0 - 0.16 * term)[..., None]
    rgb += _rim(ctx, 3.0, 0.55)[..., None] * hsl(hue, 0.28, 0.97)
    rgb += _spec(ctx, 55.0, 0.42)[..., None]
    return clamp01(rgb)


def ceramic(ctx, hue: float = 210, sat: float = 0.04, light: float = 0.95,
            **_) -> np.ndarray:
    """Glazed porcelain: near-white, soft body shading, one tight highlight."""
    top = hsl(hue, sat * 0.5, min(0.99, light + 0.03))
    mid = hsl(hue, sat, light)
    low = hsl(hue, sat * 1.4, max(0.55, light - 0.13))
    base = vramp(ctx.yfrac, [(0.0, tuple(top)), (0.45, tuple(mid)),
                             (0.72, tuple(mid * 0.985)), (1.0, tuple(low))])
    rgb = base * _diffuse(ctx, 0.82, 0.24)[..., None]
    rgb += _spec(ctx, 80.0, 0.50)[..., None]
    rgb += _rim(ctx, 2.6, 0.55)[..., None]
    rgb *= _edge_shade(ctx, 5.0, 0.12)[..., None]
    return clamp01(rgb)


def optic(ctx, hue: float = 212, **_) -> np.ndarray:
    """A camera lens: near-black glass, a faint blue iris, one hard highlight."""
    base = vramp(ctx.yfrac, [(0.0, (0.075, 0.105, 0.165)), (0.45, (0.030, 0.045, 0.080)),
                             (1.0, (0.085, 0.115, 0.190))])
    rgb = base * (0.82 + 0.36 * _ndl(ctx))[..., None]
    r = np.hypot(ctx.xfrac - 0.5, ctx.yfrac - 0.5)
    iris = np.exp(-(((r - 0.40) / 0.10) ** 2))
    rgb += hsl(hue, 0.62, 0.52) * (0.16 * iris)[..., None]
    spot = np.exp(-(((ctx.xfrac - 0.32) ** 2 + (ctx.yfrac - 0.30) ** 2) / 0.012))
    rgb += 0.85 * spot[..., None]
    spark = np.exp(-(((ctx.xfrac - 0.60) ** 2 + (ctx.yfrac - 0.62) ** 2) / 0.0035))
    rgb += 0.35 * spark[..., None]
    rgb += _rim(ctx, 1.6, 0.30)[..., None]
    return clamp01(rgb)


def paint(ctx, hue: float = 30, sat: float = 0.5, light: float = 0.5, **_) -> np.ndarray:
    """Matte paint, no gloss: rubber pads, felt, plastic bodies."""
    return enamel(ctx, hue=hue, sat=sat, light=light, gloss=0.18)


# --------------------------------------------------------------------------- #
# natural materials
# --------------------------------------------------------------------------- #

def paper(ctx, warm: bool = 1.0, seed: int = 21, **_) -> np.ndarray:
    base = vramp(ctx.yfrac, [(0.0, (0.996, 0.992, 0.980)),
                             (0.72, (0.978, 0.972, 0.952)),
                             (1.0, (0.950, 0.940, 0.915))])
    fiber = _tex(ctx.size, 8.0, seed) * 0.012
    rgb = base * (1.0 - fiber[..., None] * warm)
    edge = smoothstep(-3.0, -0.6, ctx.d)
    rgb *= (1.0 - 0.10 * edge)[..., None]
    rgb += 0.05 * _rim(ctx, 2.0, 0.5)[..., None]
    return clamp01(rgb)


def leather(ctx, hue: float = 205, sat: float = 0.32, light: float = 0.26, seed: int = 31,
            **_) -> np.ndarray:
    base = vramp(ctx.yfrac, [(0.0, tuple(hsl(hue, sat, light + 0.07))),
                             (0.5, tuple(hsl(hue, sat, light))),
                             (1.0, tuple(hsl(hue, sat, max(0.06, light - 0.08))))])
    grain = _tex(ctx.size, 4.5, seed) * 0.10 + _tex(ctx.size, 1.6, seed + 1) * 0.05
    rgb = base * (0.94 + grain[..., None])
    rgb *= _diffuse(ctx, 0.80, 0.28)[..., None]
    rgb += _spec(ctx, 30.0, 0.10)[..., None]
    rgb += _rim(ctx, 3.0, 0.10)[..., None]
    return clamp01(rgb)


def wood(ctx, hue: float = 25, sat: float = 0.66, light: float = 0.40, seed: int = 41,
         **_) -> np.ndarray:
    base = vramp(ctx.yfrac, [(0.0, tuple(hsl(hue, sat, light + 0.10))),
                             (0.45, tuple(hsl(hue, sat, light))),
                             (1.0, tuple(hsl(hue, sat, max(0.08, light - 0.12))))])
    warp = _tex(ctx.size, 190.0, seed)
    grain = 0.5 + 0.5 * np.sin((ctx.Y / 15.0) + warp * 9.0)
    rgb = base * (0.90 + 0.16 * grain[..., None])
    rgb *= _diffuse(ctx, 0.84, 0.22)[..., None]
    sheen = smoothstep(0.18, 0.42, ctx.yfrac) * (1.0 - smoothstep(0.45, 0.72, ctx.yfrac))
    rgb += 0.10 * sheen[..., None]
    rgb += _spec(ctx, 26.0, 0.12)[..., None]
    return clamp01(rgb)


def rubber(ctx, seed: int = 51, **_) -> np.ndarray:
    base = np.array([0.135, 0.145, 0.162], dtype=np.float32)
    speckle = _tex(ctx.size, 2.0, seed) * 0.05
    rgb = base * (1.0 + speckle[..., None] + (ctx.yfrac[..., None] - 0.5) * 0.10)
    return clamp01(rgb * _diffuse(ctx, 0.92, 0.12)[..., None])


def felt(ctx, hue: float = 145, sat: float = 0.46, light: float = 0.34, seed: int = 61,
         **_) -> np.ndarray:
    base = hsl(hue, sat, light)
    fibers = _tex(ctx.size, 2.4, seed) * 0.12 + _tex(ctx.size, 9.0, seed + 1) * 0.08
    rgb = base * (0.86 + fibers[..., None])
    shade = 1.0 - 0.18 * (1.0 - smoothstep(0.0, 1.0, ctx.yfrac))
    return clamp01(rgb * shade[..., None])


def ivory(ctx, seed: int = 71, **_) -> np.ndarray:
    base = vramp(ctx.yfrac, [(0.0, (0.996, 0.984, 0.936)), (0.55, (0.972, 0.950, 0.880)),
                             (1.0, (0.906, 0.874, 0.790))])
    grain = _tex(ctx.size, 6.0, seed) * 0.02
    rgb = base * (1.0 - grain[..., None]) * _diffuse(ctx, 0.86, 0.20)[..., None]
    rgb += 0.10 * _rim(ctx, 2.4, 0.5)[..., None]
    rgb += _spec(ctx, 40.0, 0.14)[..., None]
    return clamp01(rgb)


def screen(ctx, hue: float = 212, streak: float = 1.0, seed: int = 81, **_) -> np.ndarray:
    """An off/ambient display: dark glass, blue-grey, with a window reflection."""
    top = np.array([0.105, 0.145, 0.200], dtype=np.float32)
    low = np.array([0.045, 0.070, 0.105], dtype=np.float32)
    base = vramp(ctx.yfrac, [(0.0, tuple(top)), (0.55, tuple(low * 1.25)), (1.0, tuple(low))])
    rgb = base * (0.80 + 0.30 * _ndl(ctx))[..., None]
    glow = np.exp(-((ctx.xfrac - 0.42) ** 2 + ((ctx.yfrac - 0.55) * 1.3) ** 2) / 0.10)
    rgb += hsl(hue, 0.6, 0.55) * (0.10 * glow)[..., None]
    # the diagonal reflection of a window/sky
    diag = smoothstep(-0.15, 0.05, ctx.xfrac - ctx.yfrac * 0.55 - 0.02) * \
        (1.0 - smoothstep(0.22, 0.42, ctx.xfrac - ctx.yfrac * 0.55))
    rgb += 0.10 * streak * diag[..., None]
    rgb += _rim(ctx, 1.6, 0.35)[..., None]
    return clamp01(rgb)


# --------------------------------------------------------------------------- #
# mark materials (glyphs, printing, engraving)
# --------------------------------------------------------------------------- #

def embossed_white(ctx, tone: float = 0.92, **_) -> np.ndarray:
    """White enamel mark raised off a coloured face: light top-left, shade below.

    Stops short of pure white so the relief still has somewhere to go; the last
    stop of the highlight is the specular, not the body.
    """
    lit = _diffuse(ctx, 0.46, 0.50)
    rgb = np.array([tone, tone, tone * 0.985], dtype=np.float32) * lit[..., None]
    rgb += (_spec(ctx, 34.0, 0.35) + _rim(ctx, 2.2, 0.55))[..., None]
    rgb += 0.05 * _rim(ctx, 5.0, 0.5)[..., None]
    return clamp01(rgb)


def engraved(ctx, hue: float = 40, sat: float = 0.25, light: float = 0.86, **_) -> np.ndarray:
    """A mark cut into a surface: the light catches the far wall, not the near one."""
    reveal = _diffuse(ctx, 0.62, 0.30)
    rgb = hsl(hue, sat, light) * reveal[..., None]
    rgb *= (1.0 - 0.35 * smoothstep(0.35, 1.0, ctx.yfrac))[..., None]
    return clamp01(rgb)


def ink(ctx, tone: float = 0.24, warm: float = 1.0, **_) -> np.ndarray:
    """Print on paper: dark grey, slightly soft, ~70 % opacity by the caller."""
    base = np.array([tone * 1.05 * warm, tone, tone * (1.02 - 0.04 * warm)], dtype=np.float32)
    fleck = _tex(ctx.size, 3.0, 99) * 0.05
    return clamp01(base * (0.94 + fleck[..., None]))


def label_red(ctx, **_) -> np.ndarray:
    return enamel(ctx, hue=2, sat=0.72, light=0.46, gloss=0.2)


def lamp(ctx, hue: float = 44, **_) -> np.ndarray:
    """Warm light behind frosted glass (indicator LEDs, lampshades)."""
    base = hsl(hue, 0.85, 0.62)
    rgb = base * (0.9 + 0.3 * _ndl(ctx))[..., None]
    core = np.exp(-(((ctx.xfrac - 0.5) ** 2 + (ctx.yfrac - 0.45) ** 2) / 0.06))
    rgb = rgb * (1.0 - 0.4 * core[..., None]) + 1.0 * (0.6 * core)[..., None]
    return clamp01(rgb)


def shadow_only(ctx, **_) -> np.ndarray:
    return np.zeros((ctx.size, ctx.size, 3), dtype=np.float32)


def flat(colour, **opts):
    """A constant colour, for detail masks (vent lines, legends, seams).

    ``colour`` may be an rgb triplet or a hex string; ``opts`` are ignored so the
    result can be passed wherever a material is expected.
    """
    rgb = hexrgb(colour) if isinstance(colour, str) else np.array(colour, dtype=np.float32)

    def material(ctx, **_):
        out = np.empty((ctx.size, ctx.size, 3), dtype=np.float32)
        out[:] = rgb
        return out

    return material


def iridescent(ctx, base=None, amount: float = 0.10, **_) -> np.ndarray:
    """Dye sublimation sheen: the rainbow on a pressed optical disc."""
    t = ctx.xfrac * 0.85 + ctx.yfrac * 0.55
    phase = np.stack([np.sin(t * 9.0), np.sin(t * 9.0 + 2.09), np.sin(t * 9.0 + 4.18)], axis=-1)
    rainbow = 0.5 + 0.5 * phase
    body = base if base is not None else vramp(ctx.yfrac, [(0.0, (0.86, 0.88, 0.91)),
                                                           (0.5, (0.955, 0.962, 0.975)),
                                                           (1.0, (0.80, 0.83, 0.87))])
    rgb = body * (1.0 - amount) + rainbow * amount
    rgb *= _diffuse(ctx, 0.92, 0.12)[..., None]
    rgb += _spec(ctx, 40.0, 0.22)[..., None]
    return clamp01(rgb)
