"""Aqua symbolic glyphs: the drawing engine behind ``skeu-icons/symbolic/``.

The symbolic layer is *monochrome by contract*: GTK and libadwaita recolour a
``-symbolic`` icon from its alpha channel, so any colour we painted would be
thrown away.  The Aqua character therefore has to live in the geometry, and it
does:

* **weight** --- strokes are 1.5 px on the 16 px grid, not Adwaita's 1 px, which
  is what makes a Mac OS X toolbar glyph read as *chunky* without being heavy;
* **capsules** --- every arrow is a rounded polygon with 0.9 px corners, every
  chevron is a round-capped polyline: no sharp tips anywhere;
* **the Aqua vocabulary** --- tabbed folders, a notched sheet with a folded
  corner, a globe with two meridians, a five-lobed gear, pill search fields,
  traffic-light window buttons, perforated seams;
* **specular cut-outs** --- large solids carry a transparent crescent where the
  upper-left gloss would be.  Because it is a *hole* rather than a lighter fill
  it reads as a highlight on light backgrounds and as an engraved bevel on dark
  ones, which is the only way a monochrome icon can look glossy.

Everything is drawn into one ``<mask>``: white paints, black cuts, no colour in
the artwork itself.  ``Glyph.svg()`` wraps the result in a single
``fill="<ink>"`` rectangle, so the shipped file is a normal, recolourable
symbolic icon.

Coordinates are a 16x16 grid with the artwork kept inside a 0.9 px margin, so a
round cap never lands on the edge and nothing has to be anti-aliased into it.
``make_symbolic.py --audit`` is what enforces that margin.
"""

from __future__ import annotations

import math
import re
from typing import Callable, Iterable, Sequence

Point = tuple[float, float]

#: Stroke weight for a 16 px grid.  Aqua toolbar glyphs are heavier than
#: Adwaita's 1 px; 1.5 px is the weight that survives 16, 24 and 32 px alike.
STROKE = 1.5
#: Hairline weight, for seams inside a solid that must not close up at 16 px.
HAIRLINE = 1.0

#: The ink a symbolic icon is shipped in.  GTK replaces it with the theme
#: foreground colour; these values only matter to viewers that do not recolour.
INK_LIGHT = "#2e3436"
INK_DARK = "#deddda"

SIZE = 16.0


# --------------------------------------------------------------------------- #
# geometry: every helper returns an SVG path string
# --------------------------------------------------------------------------- #


def num(value: float) -> str:
    """Format a coordinate compactly and without negative zero."""
    text = f"{round(float(value), 2):.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def _pt(point: Point) -> str:
    return f"{num(point[0])} {num(point[1])}"


def rr(x: float, y: float, w: float, h: float, r: float = 0.0) -> str:
    """A rounded rectangle; ``r`` is clamped to half the shorter side."""
    r = max(0.0, min(r, w / 2, h / 2))
    if r <= 0.01:
        return (f"M{num(x)} {num(y)}H{num(x + w)}V{num(y + h)}"
                f"H{num(x)}Z")
    return (f"M{num(x + r)} {num(y)}"
            f"H{num(x + w - r)}A{num(r)} {num(r)} 0 0 1 {num(x + w)} {num(y + r)}"
            f"V{num(y + h - r)}A{num(r)} {num(r)} 0 0 1 {num(x + w - r)} {num(y + h)}"
            f"H{num(x + r)}A{num(r)} {num(r)} 0 0 1 {num(x)} {num(y + h - r)}"
            f"V{num(y + r)}A{num(r)} {num(r)} 0 0 1 {num(x + r)} {num(y)}Z")


def circ(cx: float, cy: float, r: float) -> str:
    """A circle as two half arcs, so it composes with the other paths."""
    return (f"M{num(cx - r)} {num(cy)}"
            f"A{num(r)} {num(r)} 0 1 0 {num(cx + r)} {num(cy)}"
            f"A{num(r)} {num(r)} 0 1 0 {num(cx - r)} {num(cy)}Z")


def ell(cx: float, cy: float, rx: float, ry: float) -> str:
    return (f"M{num(cx - rx)} {num(cy)}"
            f"A{num(rx)} {num(ry)} 0 1 0 {num(cx + rx)} {num(cy)}"
            f"A{num(rx)} {num(ry)} 0 1 0 {num(cx - rx)} {num(cy)}Z")


def arc(cx: float, cy: float, r: float, start: float, end: float) -> str:
    """An open circular arc, angles in degrees, clockwise from 3 o'clock."""
    a0, a1 = math.radians(start), math.radians(end)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(end - start) > 180 else 0
    # y points down, so an increasing angle sweeps clockwise on screen: SVG's
    # positive-sweep direction.  One flag, every curved glyph in the pack.
    sweep = 1 if end > start else 0
    return (f"M{num(x0)} {num(y0)}"
            f"A{num(r)} {num(r)} 0 {large} {sweep} {num(x1)} {num(y1)}")


def _unit(a: Point, b: Point) -> Point:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1.0
    return dx / length, dy / length


def _dist(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def polyline(points: Sequence[Point]) -> str:
    """An open path through ``points`` (round caps come from the renderer)."""
    pts = list(points)
    if len(pts) < 2:
        return ""
    return "M" + " L".join(_pt(p) for p in pts)


def rpoly(points: Sequence[Point], r: float = 0.0, closed: bool = True) -> str:
    """A polygon (or polyline) with softly rounded corners.

    This is what gives the set its Aqua feel: every arrow head, gear tooth and
    star point is a quadratic corner rather than a needle.
    """
    pts = [(float(x), float(y)) for x, y in points]
    if len(pts) < 2:
        return ""
    if not closed:
        return polyline(pts)
    if len(pts) == 2:
        return f"M{_pt(pts[0])}L{_pt(pts[1])}"
    if r <= 0.01:
        return "M" + " L".join(_pt(p) for p in pts) + "Z"

    corners = []
    for i, cur in enumerate(pts):
        prev, nxt = pts[i - 1], pts[(i + 1) % len(pts)]
        din, dout = _unit(prev, cur), _unit(cur, nxt)
        t = min(r, _dist(prev, cur) / 2, _dist(cur, nxt) / 2)
        c_in = (cur[0] - din[0] * t, cur[1] - din[1] * t)
        c_out = (cur[0] + dout[0] * t, cur[1] + dout[1] * t)
        corners.append((c_in, cur, c_out))

    out = [f"M{_pt(corners[0][2])}"]
    for i in range(1, len(pts)):
        c_in, cur, c_out = corners[i]
        out.append(f"L{_pt(c_in)}Q{_pt(cur)} {_pt(c_out)}")
    c_in, cur, c_out = corners[0]
    out.append(f"L{_pt(c_in)}Q{_pt(cur)} {_pt(c_out)}Z")
    return "".join(out)


def move(points: Iterable[Point], dx: float = 0.0, dy: float = 0.0) -> list[Point]:
    return [(x + dx, y + dy) for x, y in points]


def grow(points: Iterable[Point], cx: float = 8.0, cy: float = 8.0,
         scale: float = 1.0) -> list[Point]:
    return [(cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in points]


def rotate(points: Iterable[Point], degrees: float, cx: float = 8.0,
           cy: float = 8.0) -> list[Point]:
    a = math.radians(degrees)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa,
             cy + (x - cx) * sa + (y - cy) * ca) for x, y in points]


def flip(points: Iterable[Point], vertical: bool = False) -> list[Point]:
    """Mirror about the centre line: ``vertical=False`` mirrors left/right."""
    if vertical:
        return [(x, 16 - y) for x, y in points]
    return [(16 - x, y) for x, y in points]


# --------------------------------------------------------------------------- #
# paths: flattening, and strokes as filled outlines
# --------------------------------------------------------------------------- #

#: The absolute commands this pack emits.  Nothing else has to be understood:
#: the geometry helpers below are the only source of path data.
_TOKEN = re.compile(r"[MLHVAQZmlhvaqz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _arc_points(p0: Point, rx: float, ry: float, phi_deg: float, large: int,
                sweep: int, p1: Point, step: float = 7.0) -> list[Point]:
    """Sample an SVG elliptical arc between two points (endpoint form)."""
    phi = math.radians(phi_deg)
    rx, ry = abs(rx), abs(ry)
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1 = math.cos(phi) * dx + math.sin(phi) * dy
    y1 = -math.sin(phi) * dx + math.cos(phi) * dy
    if rx == 0 or ry == 0:
        return [p1]
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    # Identical endpoints (a full turn) leave no centre to solve for; the arc
    # is then a point, which is what flatten() wants anyway.
    coef = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1) \
        if den else 0.0
    cx1, cy1 = coef * rx * y1 / ry, -coef * ry * x1 / rx
    cx = math.cos(phi) * cx1 - math.sin(phi) * cy1 + (p0[0] + p1[0]) / 2
    cy = math.sin(phi) * cx1 + math.cos(phi) * cy1 + (p0[1] + p1[1]) / 2
    theta1 = math.atan2((y1 - cy1) / ry, (x1 - cx1) / rx)
    theta2 = math.atan2((-y1 - cy1) / ry, (-x1 - cx1) / rx)
    delta = theta2 - theta1
    if sweep and delta < 0:
        delta += 2 * math.pi
    elif not sweep and delta > 0:
        delta -= 2 * math.pi
    steps = max(2, int(abs(math.degrees(delta)) / step) + 1)
    points = []
    for index in range(1, steps + 1):
        angle = theta1 + delta * index / steps
        px = math.cos(angle) * rx
        py = math.sin(angle) * ry
        points.append((cx + math.cos(phi) * px - math.sin(phi) * py,
                       cy + math.sin(phi) * px + math.cos(phi) * py))
    return points


def flatten(path: str, step: float = 7.0) -> list[list[Point]]:
    """The subpaths of PATH as point lists, with arcs and quadratics sampled.

    Cutting a stroke out of a filled shape needs real geometry, and a fill-only
    SVG (the only kind GTK3 can recolour) needs a stroke to *be* geometry, so
    every path the pack draws is flattened to polylines here first.
    """
    tokens = _TOKEN.findall(path or "")
    subpaths: list[list[Point]] = []
    current: list[Point] | None = None
    start: Point = (0.0, 0.0)
    index = 0

    def take(count: int) -> list[float]:
        nonlocal index
        values = [float(tokens[index + step]) for step in range(count)]
        index += count
        return values

    while index < len(tokens):
        command = tokens[index]
        index += 1
        if command in ("M", "m"):
            if current and len(current) > 1:
                subpaths.append(current)
            x, y = take(2)
            current = [(x, y)]
            start = (x, y)
        elif command in ("L", "l"):
            x, y = take(2)
            if current is None:
                current = [(x, y)]
            current.append((x, y))
        elif command in ("H", "h"):
            (x,) = take(1)
            current.append((x, current[-1][1]))
        elif command in ("V", "v"):
            (y,) = take(1)
            current.append((current[-1][0], y))
        elif command in ("A", "a"):
            rx, ry, rot, large, sweep, x, y = take(7)
            current.extend(_arc_points(current[-1], rx, ry, rot, int(large),
                                       int(sweep), (x, y), step))
        elif command in ("Q", "q"):
            qx, qy, x, y = take(4)
            p0 = current[-1]
            for k in range(1, 7):
                t = k / 6
                current.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * qx + t * t * x,
                                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * qy + t * t * y))
        elif command in ("Z", "z"):
            if current:
                current.append(start)
                subpaths.append(current)
                current = None
    if current and len(current) > 1:
        subpaths.append(current)
    return subpaths


def _unit_normal(a: Point, b: Point) -> Point:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1.0
    return (-dy / length, dx / length)


# --------------------------------------------------------------------------- #
# painting, then tracing
# --------------------------------------------------------------------------- #
#
# A glyph here is painted the way a mask is: shapes go down, and later strokes
# and holes rub them out.  That model composes without surprises - overlapping
# holes, an island inside a hole, a hole in empty space all just work - but the
# file that ships cannot contain a ``stroke`` or a ``mask``, because GTK3
# recolours a symbolic icon by rewriting each ``fill`` and dropping everything
# else.
#
# So the icon is painted at high resolution and its silhouette is traced back
# into closed contours: one fill-only path, with every hole exactly where the
# paint left it.

RASTER = 64      # raster pixels per grid unit
SMOOTH = 1.6     # tracing tolerance, in raster pixels (0.025 of a grid unit)
SPECK = 12       # drop contours smaller than this many square raster pixels


def _layer(size: int, path: str, width: float | None, scale: int):
    """One painting operation, as an 8-bit coverage mask."""
    from PIL import Image, ImageDraw

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    for points in flatten(path):
        scaled = [(x * scale, y * scale) for x, y in points]
        if width is None:
            if len(scaled) >= 3:
                draw.polygon(scaled, fill=255)
            continue
        thickness = max(1, int(round(width * scale)))
        radius = thickness / 2.0
        if len(scaled) == 1:
            draw.ellipse([scaled[0][0] - radius, scaled[0][1] - radius,
                          scaled[0][0] + radius, scaled[0][1] + radius], fill=255)
            continue
        draw.line(scaled, fill=255, width=thickness, joint="curve")
        # A disc at every vertex, not just the ends: Pillow's curve joints leave
        # thin notches between nearly collinear segments, and on a long bend they
        # survive the trace as white hairlines across the stroke.
        for x, y in scaled:
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=255)
    return mask


def _simplify(points: list[Point], tolerance: float) -> list[Point]:
    """Douglas-Peucker: keep the corners, drop the staircase."""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        if last <= first + 1:
            continue
        x1, y1 = points[first]
        x2, y2 = points[last]
        dx, dy = x2 - x1, y2 - y1
        span = math.hypot(dx, dy) or 1e-9
        worst, at = -1.0, None
        for index in range(first + 1, last):
            x, y = points[index]
            off = abs(dy * (x - x1) - dx * (y - y1)) / span
            if off > worst:
                worst, at = off, index
        if at is not None and worst > tolerance:
            keep[at] = True
            stack.extend(((first, at), (at, last)))
    return [point for point, kept in zip(points, keep) if kept]


def _area(points: Sequence[Point]) -> float:
    """Shoelace area of a closed contour, in the units of its points."""
    total = 0.0
    for index, (x1, y1) in enumerate(points):
        x2, y2 = points[(index + 1) % len(points)]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def _loops(pixels) -> list[list[Point]]:
    """Walk the boundary between painted and empty pixels into closed loops."""
    import numpy as np

    height, width = pixels.shape
    blank_row = np.zeros((1, width), bool)
    blank_col = np.zeros((height, 1), bool)
    outside = {
        "up": np.vstack([blank_row, pixels[:-1]]),
        "down": np.vstack([pixels[1:], blank_row]),
        "left": np.hstack([blank_col, pixels[:, :-1]]),
        "right": np.hstack([pixels[:, 1:], blank_col]),
    }
    # Each painted pixel contributes the edges it does not share with another
    # painted pixel, directed clockwise; linking them head to tail reproduces
    # every outline, exterior and hole alike.
    steps = {"up": ((0, 0), (0, 1)), "right": ((0, 1), (1, 1)),
             "down": ((1, 1), (1, 0)), "left": ((1, 0), (0, 0))}
    starts: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for side, (tail, head) in steps.items():
        rows, cols = np.nonzero(pixels & ~outside[side])
        for row, col in zip(rows.tolist(), cols.tolist()):
            starts.setdefault((row + tail[0], col + tail[1]), []).append(
                (row + head[0], col + head[1]))

    loops = []
    while starts:
        start = next(iter(starts))
        path = [start]
        heading = (0, 0)
        here = start
        while True:
            options = starts.get(here)
            if not options:
                break
            if len(options) > 1:
                # Two pixels meeting at a corner: turning right keeps their two
                # outlines apart instead of knitting them into one.
                options.sort(key=lambda nxt: (heading[1] * (nxt[0] - here[0])
                                              - heading[0] * (nxt[1] - here[1])))
                nxt = options[-1]
            else:
                nxt = options[0]
            options.remove(nxt)
            if not options:
                del starts[here]
            heading = (nxt[0] - here[0], nxt[1] - here[1])
            here = nxt
            if here == start:
                break
            path.append(here)
        if len(path) >= 4:
            loops.append(path)
    return loops


def trace(mask) -> list[list[Point]]:
    """The contours of MASK, in grid units, ready to be filled even-odd."""
    import numpy as np

    pixels = np.asarray(mask) > 127
    loops = []
    for loop in _loops(pixels):
        # A closed ring has no chord to simplify against, so cut it in two at
        # the point furthest from its start and simplify each half.
        turn = min(range(len(loop)), key=lambda i: loop[i])
        ring = loop[turn:] + loop[:turn]
        far = max(range(len(ring)),
                  key=lambda i: (ring[i][0] - ring[0][0]) ** 2
                  + (ring[i][1] - ring[0][1]) ** 2)
        first = _simplify(ring[:far + 1], SMOOTH)
        second = _simplify(ring[far:] + [ring[0]], SMOOTH)
        contour = first[:-1] + second[:-1]
        if len(contour) < 3 or abs(_area(contour)) < SPECK:
            continue
        loops.append([(x / RASTER, y / RASTER) for x, y in contour])
    return loops


def _contour(points: Sequence[Point]) -> str:
    head = f"M{num(points[0][0])} {num(points[0][1])}"
    return head + "".join(f"L{num(x)} {num(y)}" for x, y in points[1:]) + "Z"


# --------------------------------------------------------------------------- #
# the canvas
# --------------------------------------------------------------------------- #


class Glyph:
    """The paint operations of one icon, in order.

    Nothing here reaches the file as a stroke or a mask: the glyph is painted,
    then traced, so that what ships is a single fill-only path - the only kind
    of paint GTK3 leaves alone when it recolours a symbolic icon.
    """

    def __init__(self) -> None:
        self._ops: list[tuple[str, str, float | None]] = []
        self.mirror = False

    # -- painting ---------------------------------------------------------- #
    def fill(self, path: str) -> "Glyph":
        """Paint PATH solid."""
        if path:
            self._ops.append(("ink", path, None))
        return self

    def stroke(self, path: str, width: float = STROKE) -> "Glyph":
        """Paint a round-capped, round-joined line along PATH."""
        if path:
            self._ops.append(("ink", path, width))
        return self

    def hole(self, path: str) -> "Glyph":
        """Rub PATH out of everything painted so far."""
        if path:
            self._ops.append(("cut", path, None))
        return self

    def erase(self, path: str, width: float = STROKE) -> "Glyph":
        """Rub a round-capped line out of everything painted so far."""
        if path:
            self._ops.append(("cut", path, width))
        return self

    def tone(self, path: str, opacity: float = 0.55) -> "Glyph":
        """Paint PATH as a lighter second tone.

        A symbolic icon is a mask: the toolkit paints it in whatever colour the
        theme asks for, so a second tone only survives where a toolkit honours
        ``fill-opacity``.  Aqua's gloss is a highlight inside an already solid
        shape, which costs nothing to draw as solid ink.
        """
        return self.fill(path)

    # -- convenience shapes ------------------------------------------------ #
    def bar(self, x: float, y: float, w: float, h: float, r: float = 0.0) -> "Glyph":
        return self.fill(rr(x, y, w, h, r))

    def dot(self, cx: float, cy: float, r: float) -> "Glyph":
        return self.fill(circ(cx, cy, r))

    def ring(self, cx: float, cy: float, r: float, width: float = STROKE) -> "Glyph":
        return self.stroke(circ(cx, cy, r), width)

    def line(self, a: Point, b: Point, width: float = STROKE) -> "Glyph":
        return self.stroke(polyline([a, b]), width)

    def outline(self, points: Sequence[Point], r: float = 0.0,
                width: float = STROKE, closed: bool = False) -> "Glyph":
        return self.stroke(rpoly(points, r, closed), width)

    def solid(self, points: Sequence[Point], r: float = 0.0) -> "Glyph":
        return self.fill(rpoly(points, r, True))

    def cut_solid(self, points: Sequence[Point], r: float = 0.0) -> "Glyph":
        return self.hole(rpoly(points, r, True))

    # -- output ------------------------------------------------------------ #
    def mask(self, scale: int = RASTER):
        """The painted glyph, as a greyscale coverage mask."""
        from PIL import Image, ImageChops

        size = 16 * scale
        canvas = Image.new("L", (size, size), 0)
        for kind, path, width in self._ops:
            painting = _layer(size, path, width, scale)
            canvas = (ImageChops.lighter(canvas, painting) if kind == "ink"
                      else ImageChops.subtract(canvas, painting))
        return canvas

    def contours(self) -> list[list[Point]]:
        return trace(self.mask())

    def png(self, size: int = 256):
        """The glyph as a preview image, for the gallery and for review.

        The mirror is part of the drawing, not of the file format - ``svg()``
        writes it as a transform because that is cheapest there - so a preview
        has to flip its own pixels, or the ``-rtl`` names would look the same
        as the names they mirror.
        """
        from PIL import Image, ImageDraw

        mask = self.mask()
        if self.mirror:
            mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
        image = mask.resize((size, size), Image.LANCZOS)
        preview = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ink = Image.new("RGBA", (size, size), (46, 52, 54, 255))
        preview.paste(ink, (0, 0), image)
        return preview

    def svg(self, ink: str = INK_LIGHT, title: str = "") -> str:
        """The finished icon: one fill-only path, holes included.

        ``fill`` is the one attribute GTK3 rewrites when it recolours a
        symbolic icon, so it is the only paint the file uses.  The contours are
        traced from the painted mask, which is why holes land exactly where the
        glyph rubbed them out.
        """
        body = " ".join(_contour(loop) for loop in self.contours())
        transform = ' transform="matrix(-1 0 0 1 16 0)"' if self.mirror else ""
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
                'viewBox="0 0 16 16">\n')
        note = f"<title>{title}</title>\n" if title else ""
        return (head + note + f'<g{transform}>\n'
                f'<path fill="{ink}" fill-rule="evenodd" d="{body}"/>\n'
                '</g>\n</svg>\n')


# --------------------------------------------------------------------------- #
# the Aqua motifs: the vocabulary every glyph is built from
# --------------------------------------------------------------------------- #

#: A right-pointing capsule arrow, in grid units, before scaling.
_ARROW = [(2.4, 6.3), (8.7, 6.3), (8.7, 3.4), (14.0, 8.0),
          (8.7, 12.6), (8.7, 9.7), (2.4, 9.7)]


def arrow(g: Glyph, angle: float = 0.0, cx: float = 8.0, cy: float = 8.0,
          scale: float = 1.0, corner: float = 0.9) -> Glyph:
    """The Aqua navigation arrow: a fat shaft with a rounded head.

    ``angle`` is clockwise, 0 = pointing right, 90 = down.

    The template sits on the centre of the grid, so it has to be carried to
    ``cx, cy`` *before* it is turned: rotating it in place about a point it is
    not standing on threw the head off the canvas.
    """
    points = move(grow(_ARROW, scale=scale), cx - 8.0, cy - 8.0)
    return g.solid(rotate(points, angle, cx, cy), corner)


def chevron(g: Glyph, angle: float = 90.0, cx: float = 8.0, cy: float = 8.0,
            reach: float = 3.9, width: float = STROKE) -> Glyph:
    """A round-capped chevron, the Aqua disclosure triangle.

    ``angle`` 90 points down, 0 points right.
    """
    points = rotate([(-reach, -reach), (0.0, 0.0), (0.0, 0.0), (-reach, reach)],
                    angle, 0.0, 0.0)
    path = polyline(move([points[0], points[1], points[3]], cx, cy))
    return g.stroke(path, width)


def triangle(g: Glyph, angle: float = 90.0, cx: float = 8.0, cy: float = 8.0,
             reach: float = 4.2, filled: bool = True, corner: float = 0.7) -> Glyph:
    """The Aqua pull-down triangle: an equilateral-ish wedge, softly cornered."""
    base = [(-reach, -reach * 0.86), (reach, -reach * 0.86), (0.0, reach * 1.05)]
    points = move(rotate(base, angle - 90.0, 0.0, 0.0), cx, cy)
    if filled:
        return g.solid(points, corner * 0.45)
    return g.outline(points, corner * 0.45, closed=True)


def plus(g: Glyph, cx: float = 8.0, cy: float = 8.0, arm: float = 4.6,
         width: float = STROKE) -> Glyph:
    g.line((cx - arm, cy), (cx + arm, cy), width)
    return g.line((cx, cy - arm), (cx, cy + arm), width)


def minus(g: Glyph, cx: float = 8.0, cy: float = 8.0, arm: float = 4.6,
          width: float = STROKE) -> Glyph:
    return g.line((cx - arm, cy), (cx + arm, cy), width)


def cross(g: Glyph, cx: float = 8.0, cy: float = 8.0, arm: float = 3.9,
          width: float = STROKE) -> Glyph:
    g.line((cx - arm, cy - arm), (cx + arm, cy + arm), width)
    return g.line((cx - arm, cy + arm), (cx + arm, cy - arm), width)


def check(g: Glyph, cx: float = 8.0, cy: float = 8.0, arm: float = 4.4,
          width: float = STROKE) -> Glyph:
    path = polyline([(cx - arm, cy + arm * 0.10), (cx - arm * 0.30, cy + arm * 0.78),
                     (cx + arm, cy - arm * 0.68)])
    return g.stroke(path, width)


def bars(g: Glyph, heights: Sequence[float], x: float = 2.8, bottom: float = 13.2,
         width: float = 1.9, gap: float = 1.55, r: float = 0.55) -> Glyph:
    """A signal-strength ladder; ``heights`` are the bar heights, shortest first."""
    for index, height in enumerate(heights):
        if height <= 0:
            continue
        g.bar(x + index * gap, bottom - height, width, height, min(r, width / 2))
    return g


def dot_matrix(g: Glyph, cx: float = 8.0, cy: float = 8.0, columns: int = 3,
               rows: int = 3, step: float = 4.3, radius: float = 0.85) -> Glyph:
    for row in range(rows):
        for column in range(columns):
            g.dot(cx + (column - (columns - 1) / 2) * step,
                  cy + (row - (rows - 1) / 2) * step, radius)
    return g


def gloss(g: Glyph, cx: float, cy: float, rx: float, ry: float) -> Glyph:
    """Cut the Aqua specular crescent: the only gloss a monochrome icon can have."""
    return g.hole(ell(cx, cy, rx, ry))


def seam(g: Glyph, points: Sequence[Point], width: float = HAIRLINE) -> Glyph:
    """A perforated seam: a cut line, so it reads on light and dark alike."""
    return g.erase(polyline(points), width)


def badge(g: Glyph, cx: float, cy: float, r: float = 3.4) -> Glyph:
    """A solid disc used as the backing plate for a small overlay."""
    return g.dot(cx, cy, r)


def badge_hole(g: Glyph, cx: float, cy: float, r: float = 2.55) -> Glyph:
    """Erase a clearance disc so a badge reads as its own plate.

    A badge that overlaps the artwork has to *replace* what is underneath it.
    Without the hole the disc and the body become one silhouette, and the plus
    or cross cut into the badge is the only thing separating them - on a
    bookmark or a speech bubble that reads as a blob.  Cutting the disc first
    leaves the ring of background an emblem needs, and costs nothing where the
    badge already sits on empty tile.
    """
    return g.hole(circ(cx, cy, r))


def slash(g: Glyph, start: Point = (2.6, 13.4), end: Point = (13.4, 2.6),
          width: float = STROKE, gap: float = 0.9) -> Glyph:
    """The universal "disabled" bar: a gap bitten out of the body, then the bar.

    The gap is deliberately narrow.  A wide one is right for a solid body, but
    most of what gets barred here is a 1.5 px line drawing - a rune, an eye, a
    bell - and a 3 px band through it erases the drawing instead of separating
    it, leaving a diagonal with stubs beside it.  0.45 px of clearance each
    side is enough to keep the bar distinct at 16 px and keeps the art whole.
    """
    g.erase(polyline([start, end]), width + gap)
    return g.stroke(polyline([start, end]), width)


def sheet(g: Glyph, x: float = 3.4, y: float = 1.9, w: float = 9.2, h: float = 12.2,
          fold: float = 2.8, corner: float = 1.2, width: float = STROKE) -> Glyph:
    """The Aqua document: a softly rounded sheet with a folded top-right corner.

    ``y`` is clamped to the top margin the rest of the pack keeps: several
    callers asked for 1.6, which left the sheet's stroke 0.84 of the way to
    the tile edge, where it reads as artwork falling off the tile.
    """
    y = max(y, 1.9)
    right, bottom = x + w, y + h
    path = (f"M{num(x + corner)} {num(y)}H{num(right - fold)}L{num(right)} {num(y + fold)}"
            f"V{num(bottom - corner)}A{num(corner)} {num(corner)} 0 0 1 {num(right - corner)} {num(bottom)}"
            f"H{num(x + corner)}A{num(corner)} {num(corner)} 0 0 1 {num(x)} {num(bottom - corner)}"
            f"V{num(y + corner)}A{num(corner)} {num(corner)} 0 0 1 {num(x + corner)} {num(y)}Z")
    g.stroke(path, width)
    g.stroke(polyline([(right - fold, y), (right - fold, y + fold), (right, y + fold)]),
             width)
    return g


def folder(g: Glyph, x: float = 1.7, y: float = 4.2, w: float = 12.6, h: float = 9.2,
           tab: float = 4.6, corner: float = 1.5, width: float = STROKE) -> Glyph:
    """The Aqua tabbed folder: a wide tab on the left, a rounded body below."""
    right, bottom = x + w, y + h
    path = (f"M{num(x + corner)} {num(y)}H{num(x + tab)}"
            f"L{num(x + tab + 1.5)} {num(y + 2.0)}H{num(right - corner)}"
            f"A{num(corner)} {num(corner)} 0 0 1 {num(right)} {num(y + 2.0 + corner)}"
            f"V{num(bottom - corner)}A{num(corner)} {num(corner)} 0 0 1 {num(right - corner)} {num(bottom)}"
            f"H{num(x + corner)}A{num(corner)} {num(corner)} 0 0 1 {num(x)} {num(bottom - corner)}"
            f"V{num(y + corner)}A{num(corner)} {num(corner)} 0 0 1 {num(x + corner)} {num(y)}Z")
    return g.stroke(path, width)


def globe(g: Glyph, cx: float = 8.0, cy: float = 8.0, r: float = 6.1,
          filled: bool = False) -> Glyph:
    """The Aqua internet globe: a disc, an equator and one meridian ellipse."""
    if filled:
        g.dot(cx, cy, r)
        g.erase(polyline([(cx - r - 0.3, cy), (cx + r + 0.3, cy)]), 1.0)
        g.erase(ell(cx, cy, r * 0.46, r), 1.0)
    else:
        g.ring(cx, cy, r)
        g.stroke(polyline([(cx - r, cy), (cx + r, cy)]), HAIRLINE + 0.2)
        g.stroke(ell(cx, cy, r * 0.46, r), HAIRLINE + 0.2)
    return g


def gear(g: Glyph, cx: float = 8.0, cy: float = 8.0, teeth: int = 8,
         outer: float = 6.2, inner: float = 4.3, hole: float = 1.9) -> Glyph:
    """A five-lobed Aqua gear: rounded teeth, generous centre bore."""
    points = []
    step = 360.0 / teeth
    for index in range(teeth):
        angle = index * step
        for offset, radius in ((0.0, inner), (step * 0.22, outer),
                               (step * 0.46, outer), (step * 0.68, inner)):
            a = math.radians(angle + offset)
            points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    g.solid(points, 0.55)
    g.hole(circ(cx, cy, hole))
    return g


def person(g: Glyph, cx: float = 8.0, cy: float = 6.2, head: float = 2.5,
           width: float = STROKE, shoulders: float = 5.6) -> Glyph:
    """A head and shoulders, the Aqua contact glyph (stroked)."""
    g.ring(cx, cy, head, width)
    path = (f"M{num(cx - shoulders / 2)} {num(cy + 8.0)}"
            f"A{num(shoulders / 2)} {num(shoulders / 2 * 0.95)} 0 0 1 "
            f"{num(cx + shoulders / 2)} {num(cy + 8.0)}")
    return g.stroke(path, width)


def person_solid(g: Glyph, cx: float = 8.0, cy: float = 8.0, scale: float = 1.0) -> Glyph:
    """The filled contact silhouette, for badges and avatar tiles."""
    head_r = 2.5 * scale
    g.dot(cx, cy - 2.8 * scale, head_r)
    body = (f"M{num(cx - 4.6 * scale)} {num(cy + 6.2 * scale)}"
            f"A{num(4.6 * scale)} {num(4.6 * scale)} 0 0 1 "
            f"{num(cx + 4.6 * scale)} {num(cy + 6.2 * scale)}Z")
    return g.fill(body)


def lock(g: Glyph, cx: float = 8.0, cy: float = 9.4, open: bool = False,
         width: float = STROKE) -> Glyph:
    """A padlock: rounded body, shackle either closed or lifted."""
    g.bar(cx - 4.5, cy - 1.2, 9.0, 6.6, 1.7)
    g.hole(rr(cx - 1.5, cy + 1.8, 3.0, 1.4, 0.7))
    if open:
        g.erase(arc(cx - 1.6, cy - 3.2, 2.9, 180, 360), width)
        g.stroke(arc(cx - 1.6, cy - 3.2, 2.9, 180, 320), width)
    else:
        g.erase(arc(cx, cy - 3.0, 2.9, 180, 360), width)
        g.stroke(arc(cx, cy - 3.0, 2.9, 180, 360), width)
        g.erase(polyline([(cx - 2.9, cy - 3.0), (cx - 2.9, cy - 1.0)]), width)
        g.erase(polyline([(cx + 2.9, cy - 3.0), (cx + 2.9, cy - 1.0)]), width)
    return g


def eye(g: Glyph, cx: float = 8.0, cy: float = 8.0, width: float = STROKE,
        pupil: bool = True) -> Glyph:
    """An almond eye with a solid pupil."""
    outline = (f"M{num(cx - 6.3)} {num(cy)}"
               f"Q{num(cx)} {num(cy - 5.4)} {num(cx + 6.3)} {num(cy)}"
               f"Q{num(cx)} {num(cy + 5.4)} {num(cx - 6.3)} {num(cy)}Z")
    g.stroke(outline, width)
    if pupil:
        g.dot(cx, cy, 2.1)
    return g


def envelope(g: Glyph, x: float = 1.9, y: float = 3.6, w: float = 12.2,
             h: float = 8.8, width: float = STROKE) -> Glyph:
    """The Aqua mail envelope: rounded, with the classic folded flap."""
    g.stroke(rr(x, y, w, h, 1.5), width)
    a = (x + 0.7, y + 0.9)
    b = (x + w / 2, y + h * 0.58)
    c = (x + w - 0.7, y + 0.9)
    return g.stroke(polyline([a, b, c]), width)


def speech(g: Glyph, x: float = 1.9, y: float = 2.6, w: float = 12.2,
           h: float = 9.0, tail: float = 2.5, width: float = STROKE) -> Glyph:
    """A rounded speech bubble with a tail cut into its lower-left corner.

    The tail belongs to the outline: it leaves the bottom edge, comes to a
    point below the bubble and returns to it, so the two are one continuous
    line.  Drawn as a separate V over the bubble it looked like a squiggle - a
    single stroked outline was the fix.
    """
    right, bottom = x + w, y + h
    corner = 2.6
    t0, tip, t1 = x + 5.4, (x + 1.2, bottom + tail), x + 1.6
    path = (f"M{num(x + corner)} {num(y)}H{num(right - corner)}"
            f"A{num(corner)} {num(corner)} 0 0 1 {num(right)} {num(y + corner)}"
            f"V{num(bottom - corner)}"
            f"A{num(corner)} {num(corner)} 0 0 1 {num(right - corner)} {num(bottom)}"
            f"H{num(t0)}L{num(tip[0])} {num(tip[1])}L{num(t1)} {num(bottom)}"
            f"H{num(x + corner)}"
            f"A{num(corner)} {num(corner)} 0 0 1 {num(x)} {num(bottom - corner)}"
            f"V{num(y + corner)}"
            f"A{num(corner)} {num(corner)} 0 0 1 {num(x + corner)} {num(y)}Z")
    return g.stroke(path, width)


def star_shape(cx: float = 8.0, cy: float = 8.0, outer: float = 6.2,
               inner: float = 2.7) -> list[Point]:
    points = []
    for index in range(10):
        radius = outer if index % 2 == 0 else inner
        angle = math.radians(-90 + index * 36)
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def star(g: Glyph, cx: float = 8.0, cy: float = 8.0, outer: float = 6.2,
         filled: bool = True, width: float = STROKE) -> Glyph:
    points = star_shape(cx, cy, outer)
    if filled:
        return g.solid(points, 0.6)
    return g.outline(points, 0.6, width, closed=True)


def half_star(g: Glyph, cx: float = 8.0, cy: float = 8.0, outer: float = 6.2) -> Glyph:
    """The "semi-starred" rating: solid on the left, outline on the right.

    The fill is clipped on the centre line in geometry rather than with a cut,
    because a cut wider than the star would fill the area around it instead of
    clearing it.
    """
    points = star_shape(cx, cy, outer)
    left = [(min(x, cx), y) for x, y in points]
    g.solid(left, 0.2)
    return g.outline(points, 0.6, closed=True)


def traffic(g: Glyph, which: str = "close", cx: float = 8.0, cy: float = 8.0,
            r: float = 4.9) -> Glyph:
    """The Aqua window button: a disc with its glyph cut out."""
    g.dot(cx, cy, r)
    if which == "close":
        g.erase(polyline([(cx - 2.3, cy - 2.3), (cx + 2.3, cy + 2.3)]), 1.4)
        g.erase(polyline([(cx - 2.3, cy + 2.3), (cx + 2.3, cy - 2.3)]), 1.4)
    elif which == "minimize":
        g.erase(rr(cx - 2.5, cy - 0.7, 5.0, 1.4, 0.7))
    elif which == "maximize":
        g.hole(rr(cx - 2.3, cy - 2.3, 4.6, 4.6, 0.9))
        g.fill(rr(cx - 1.0, cy - 1.0, 2.0, 2.0, 0.3))
    elif which == "restore":
        # Two panes, the way the button is drawn everywhere else: the bore is
        # the back window's plate and the bar is the front one, overlapping its
        # lower-right corner.  Drawn as a ring inside a ring it read as a solid
        # box; the overlap is what makes the pair of windows legible.
        g.hole(rr(cx - 2.5, cy - 3.1, 4.4, 4.4, 0.9))
        g.bar(cx - 1.0, cy - 1.6, 4.4, 4.4, 0.9)
    return g


def magnifier(g: Glyph, cx: float = 7.0, cy: float = 6.6, r: float = 4.1,
              width: float = STROKE) -> Glyph:
    """The Aqua search lens: a generous circle on a fat diagonal handle."""
    g.ring(cx, cy, r, width)
    return g.line((cx + r * 0.72, cy + r * 0.72), (cx + r + 2.4, cy + r + 2.4),
                  width + 0.35)


def speaker(g: Glyph, cx: float = 5.2, cy: float = 8.0, waves: int = 0,
            muted: bool = False) -> Glyph:
    """A speaker cone with zero or more sound arcs."""
    body = [(2.1, 6.4), (4.2, 6.4), (7.0, 3.3), (7.0, 12.7), (4.2, 9.6), (2.1, 9.6)]
    g.solid(body, 0.7)
    for index in range(waves):
        # Four arcs (the "overamplified" level) used to end 15.2 of 16 out.
        g.stroke(arc(7.2, cy, 1.8 + index * 1.6, -48, 48), STROKE - 0.1)
    if muted:
        g.line((9.9, 5.9), (13.2, 10.1), STROKE)
        g.line((9.9, 10.1), (13.2, 5.9), STROKE)
    return g


def microphone(g: Glyph, cx: float = 8.0, cy: float = 6.2) -> Glyph:
    """The Aqua microphone: a capsule head over a rounded cradle."""
    g.bar(cx - 2.1, cy - 3.8, 4.2, 7.6, 2.1)
    g.hole(rr(cx - 1.0, cy - 2.4, 2.0, 3.0, 1.0))
    g.stroke(arc(cx, cy + 2.2, 3.5, 0, 180), STROKE)
    # The stem stops short of the tile edge: it used to run to 15.5 of 16, which
    # looked clipped next to glyphs that keep a margin.
    return g.line((cx, cy + 5.7), (cx, cy + 7.9), STROKE)


def battery(g: Glyph, level: float = 1.0, cx: float = 8.0, cy: float = 8.0,
            w: float = 12.4, h: float = 7.2, width: float = STROKE) -> Glyph:
    """A battery outline with a proportional fill and a terminal nub."""
    x = cx - w / 2
    y = cy - h / 2
    g.stroke(rr(x, y, w - 1.6, h, 1.5), width)
    g.bar(x + w - 1.2, cy - 1.6, 1.2, 3.2, 0.5)
    inner_w = (w - 1.6) - 3.0
    if level > 0:
        g.bar(x + 1.5, y + 1.5, inner_w * level, h - 3.0, 0.7)
    return g


def waveform(g: Glyph, cx: float = 8.0, cy: float = 8.0, bars: int = 5,
             height: float = 5.4) -> Glyph:
    """A level meter: five rounded bars waxing toward the middle."""
    step = 2.1
    start = cx - (bars - 1) * step / 2
    for index in range(bars):
        factor = 0.42 + 0.58 * math.sin((index + 0.6) / bars * math.pi)
        g.bar(start + index * step - 0.75, cy - height * factor / 2, 1.5,
              height * factor, 0.75)
    return g


def house(g: Glyph, width: float = STROKE) -> Glyph:
    """The Aqua home: a wide roof over a small door."""
    g.stroke(rpoly([(1.8, 7.6), (8.0, 2.0), (14.2, 7.6)], 0.9, False), width)
    g.stroke(polyline([(3.6, 6.6), (3.6, 13.4), (12.4, 13.4), (12.4, 6.6)]), width)
    g.stroke(rr(6.2, 9.4, 3.6, 4.0, 0.6), width)
    return g


def trash(g: Glyph, full: bool = False, width: float = STROKE) -> Glyph:
    """The Aqua wastebasket: a solid tapered bin with two ribs cut out of it."""
    body = [(4.0, 4.6), (5.0, 13.6), (11.0, 13.6), (12.0, 4.6)]
    if full:
        g.solid([(4.4, 3.0), (11.6, 3.0), (10.4, 1.4), (5.6, 1.4)], 0.6)
    g.solid(body, 0.7)
    g.erase(polyline([(6.4, 6.6), (6.9, 12.2)]), 1.7)
    g.erase(polyline([(9.6, 6.6), (9.1, 12.2)]), 1.7)
    g.stroke(polyline([(2.9, 4.4), (13.1, 4.4)]), width + 0.3)
    g.stroke(rr(5.4, 2.0, 5.2, 1.6, 0.7), width - 0.4)
    return g


def display(g: Glyph, x: float = 1.7, y: float = 3.1, w: float = 12.6,
            h: float = 8.6, stand: bool = True, width: float = STROKE) -> Glyph:
    """A monitor: rounded panel, cut inner screen, a small stand."""
    g.stroke(rr(x, y, w, h, 1.6), width)
    g.bar(x + 1.5, y + 1.5, w - 3.0, h - 3.0, 0.8)
    if stand:
        g.stroke(polyline([(8.0, y + h), (8.0, y + h + 2.0)]), width)
        g.stroke(polyline([(5.0, y + h + 2.4), (11.0, y + h + 2.4)]), width)
    return g


def drive(g: Glyph, x: float = 1.8, y: float = 4.3, w: float = 12.4,
          h: float = 8.2, vents: bool = True, ports: int = 0) -> Glyph:
    """An external hard disk: a case, a seam, a lit face and vents."""
    g.stroke(rr(x, y, w, h, 1.7), STROKE)
    g.stroke(rr(x + 1.1, y + 1.1, w - 2.2, h - 2.2, 1.2), HAIRLINE)
    g.bar(x + 2.4, y + 2.6, w - 4.8, 2.4, 0.7)
    if vents:
        for index in range(3):
            g.bar(x + 2.6 + index * 2.2, y + h - 2.6, 1.6, 0.9, 0.4)
    for index in range(ports):
        g.bar(x + w - 3.6 - index * 2.0, y + 2.9, 1.3, 1.3, 0.3)
    return g


def disc(g: Glyph, cx: float = 8.0, cy: float = 8.0, r: float = 6.2,
         gloss: bool = True) -> Glyph:
    """An optical disc: an outer ring, a bore ring, and the Aqua sheen."""
    g.ring(cx, cy, r, STROKE)
    g.ring(cx, cy, 1.7, HAIRLINE + 0.5)
    if gloss:
        g.erase(arc(cx, cy, r - 1.5, 200, 260), 1.2)
    return g


def card(g: Glyph, x: float = 2.2, y: float = 4.2, w: float = 11.6,
         h: float = 8.0, notch: float = 2.3) -> Glyph:
    """A memory card: rounded body with a notched top-left corner."""
    body = [(x + notch, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y + notch)]
    g.stroke(rpoly(body, 0.9, True), STROKE)
    g.bar(x + 2.4, y + 2.4, 3.2, 1.6, 0.4)
    return g


def keyboard(g: Glyph, x: float = 1.9, y: float = 5.0, w: float = 12.2,
             h: float = 7.0) -> Glyph:
    """A keypad: a rounded deck with solid key rows and a space bar."""
    g.stroke(rr(x, y, w, h, 1.4), STROKE)
    for row in range(2):
        for column in range(4):
            g.bar(x + 1.7 + column * 2.45, y + 1.6 + row * 1.8, 1.7, 1.0, 0.35)
    g.bar(x + 3.4, y + h - 2.4, 5.2, 1.0, 0.45)
    return g


def mouse(g: Glyph, cx: float = 8.0, cy: float = 8.1) -> Glyph:
    """The Aqua mouse: a rounded shell and a solid scroll slot."""
    g.stroke(rr(cx - 3.6, cy - 6.2, 7.2, 12.4, 3.5), STROKE)
    g.bar(cx - 0.65, cy - 4.9, 1.3, 3.2, 0.65)
    return g


def phone(g: Glyph, cx: float = 8.0, cy: float = 8.4, w: float = 7.4,
          h: float = 11.2) -> Glyph:
    """A smartphone: a rounded slab with a solid screen and a home button."""
    g.stroke(rr(cx - w / 2, cy - h / 2, w, h, 2.2), STROKE)
    g.bar(cx - w / 2 + 1.4, cy - h / 2 + 1.9, w - 2.8, h - 4.8, 0.7)
    g.hole(circ(cx, cy + h / 2 - 1.5, 0.8))
    return g


def tablet(g: Glyph, cx: float = 8.0, cy: float = 8.0, w: float = 10.4,
           h: float = 12.2) -> Glyph:
    """A tablet: a broad slab with a solid display, no home button."""
    g.stroke(rr(cx - w / 2, cy - h / 2, w, h, 1.9), STROKE)
    g.bar(cx - w / 2 + 1.5, cy - h / 2 + 1.8, w - 3.0, h - 3.6, 0.7)
    return g


def camera(g: Glyph, video: bool = False) -> Glyph:
    """A compact camera; the video version gets a lens hood on the right."""
    g.stroke(rr(1.8, 5.4, 9.6, 7.2, 1.6), STROKE)
    g.stroke(rr(4.6, 3.2, 3.6, 2.2, 0.7), STROKE - 0.2)
    g.ring(6.6, 9.0, 2.4, STROKE)
    if video:
        g.stroke(rpoly([(11.6, 8.1), (14.3, 6.3), (14.3, 11.7), (11.6, 9.9)],
                       0.5, True), STROKE)
    return g


def printer(g: Glyph, cx: float = 8.0, cy: float = 8.4) -> Glyph:
    """A desktop printer: a paper feed, a rounded body, an output sheet."""
    g.stroke(rr(4.3, 1.9, 7.4, 4.2, 0.7), STROKE)
    g.stroke(rr(1.9, 5.2, 12.2, 5.6, 1.6), STROKE)
    g.stroke(rr(4.1, 9.4, 7.8, 4.7, 0.8), STROKE)
    g.hole(circ(12.0, 7.0, 0.85))
    return g


def headphones(g: Glyph) -> Glyph:
    """An over-ear headset: a band and two rounded cups."""
    g.stroke(arc(8.0, 9.2, 5.6, 180, 360), STROKE + 0.2)
    g.bar(1.7, 8.4, 2.9, 5.0, 1.3)
    g.bar(11.4, 8.4, 2.9, 5.0, 1.3)
    return g


def usb(g: Glyph) -> Glyph:
    """The USB trident, drawn at Aqua weight."""
    g.stroke(polyline([(8.0, 13.4), (8.0, 3.0)]), STROKE)
    g.solid([(8.0, 1.5), (9.4, 3.6), (6.6, 3.6)], 0.4)
    g.stroke(polyline([(8.0, 10.2), (4.2, 7.6), (4.2, 6.2)]), STROKE - 0.2)
    g.stroke(polyline([(8.0, 8.6), (11.9, 6.0), (11.9, 4.8)]), STROKE - 0.2)
    g.dot(4.2, 5.2, 1.0)
    g.bar(11.0, 3.0, 1.9, 1.9, 0.3)
    return g


def bluetooth(g: Glyph, cx: float = 8.0, cy: float = 8.0) -> Glyph:
    """The Bluetooth rune: a stem, two wings and the crossing bar."""
    g.stroke(polyline([(cx, cy - 5.9), (cx + 4.0, cy - 2.4), (cx - 4.0, cy + 2.4),
                       (cx, cy + 5.9), (cx, cy - 5.9)]), STROKE)
    return g.stroke(polyline([(cx - 4.0, cy - 2.4), (cx + 4.0, cy + 2.4)]), STROKE)


def wifi(g: Glyph, level: int = 3, cx: float = 8.0, cy: float = 11.4) -> Glyph:
    """Wireless arcs above a dot; ``level`` 0..3 decides how many arcs."""
    g.dot(cx, cy, 1.2)
    radii = (2.6, 4.5, 6.4)
    for index in range(level):
        g.stroke(arc(cx, cy, radii[index], 214, 326), STROKE)
    return g


def play(g: Glyph, cx: float = 8.4, cy: float = 8.0, reach: float = 4.9) -> Glyph:
    """The Aqua play wedge, softly cornered."""
    return g.solid([(cx - reach * 0.72, cy - reach), (cx + reach, cy),
                    (cx - reach * 0.72, cy + reach)], 0.9)


def pause(g: Glyph, cx: float = 8.0, cy: float = 8.0, gap: float = 1.9,
          w: float = 2.5, h: float = 9.6) -> Glyph:
    g.bar(cx - gap / 2 - w, cy - h / 2, w, h, 0.7)
    g.bar(cx + gap / 2, cy - h / 2, w, h, 0.7)
    return g


def stop(g: Glyph, cx: float = 8.0, cy: float = 8.0, size: float = 8.4,
         r: float = 1.3) -> Glyph:
    g.bar(cx - size / 2, cy - size / 2, size, size, r)
    return g


def eject(g: Glyph, cx: float = 8.0, cy: float = 9.0) -> Glyph:
    g.solid([(cx, cy - 6.4), (cx + 5.1, cy - 0.4), (cx - 5.1, cy - 0.4)], 0.9)
    g.bar(cx - 5.1, cy + 1.6, 10.2, 1.9, 0.8)
    return g


def skip(g: Glyph, forward: bool = True, cx: float = 8.0, cy: float = 8.0) -> Glyph:
    """Skip-to-end: a wedge plus a bar, mirrored for "backward"."""
    wedge = [(cx - 4.6, cy - 5.0), (cx + 1.4, cy), (cx - 4.6, cy + 5.0)]
    bar = rr(cx + 2.2, cy - 5.0, 2.2, 10.0, 0.8)
    if not forward:
        wedge = flip(wedge)
        bar = rr(16.0 - (cx + 4.4), cy - 5.0, 2.2, 10.0, 0.8)
    g.solid(wedge, 0.8)
    g.fill(bar)
    return g


def seek(g: Glyph, forward: bool = True, cx: float = 8.0, cy: float = 8.0) -> Glyph:
    """Fast-forward / rewind: two wedges, softly cornered."""
    if forward:
        g.solid([(cx - 5.4, cy - 4.8), (cx - 0.2, cy), (cx - 5.4, cy + 4.8)], 0.8)
        g.solid([(cx, cy - 4.8), (cx + 5.2, cy), (cx, cy + 4.8)], 0.8)
    else:
        g.solid([(cx + 5.4, cy - 4.8), (cx + 0.2, cy), (cx + 5.4, cy + 4.8)], 0.8)
        g.solid([(cx, cy - 4.8), (cx - 5.2, cy), (cx, cy + 4.8)], 0.8)
    return g


def recording(g: Glyph, cx: float = 8.0, cy: float = 8.0) -> Glyph:
    g.ring(cx, cy, 6.0, STROKE)
    return g.dot(cx, cy, 3.2)


def arrow_into(g: Glyph, angle: float = 180.0, cx: float = 8.0, cy: float = 8.0,
               scale: float = 0.82) -> Glyph:
    """An arrow stopped by a wall: "first", "last", "jump"."""
    arrow(g, angle, cx, cy, scale)
    return g


def wall(g: Glyph, x: float, y0: float = 3.0, y1: float = 13.0) -> Glyph:
    return g.bar(x, y0, 1.8, y1 - y0, 0.9)


#: Handy for glyph functions that want a consistent inner panel.
PANEL = (2.2, 2.2, 11.6, 11.6)


def panel(g: Glyph, x: float = 2.2, y: float = 2.2, w: float = 11.6,
          h: float = 11.6, r: float = 2.2) -> Glyph:
    """A filled tile, the backing plate for a two-tone glyph."""
    return g.fill(rr(x, y, w, h, r))
