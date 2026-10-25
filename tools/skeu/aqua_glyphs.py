"""Aqua-style glyphs for the interface contexts: actions, ui and places.

Everything here is built from the motifs in :mod:`skeu.aqua`, so weight, corner
radius and cap style stay identical across the six hundred-odd names.  A glyph
function takes a :class:`~skeu.aqua.Glyph` and paints into it; the catalogue in
:mod:`skeu.aqua_catalog` decides which name gets which glyph with which
arguments.
"""

from __future__ import annotations

import math

from . import aqua as A
from .aqua import HAIRLINE, STROKE, Glyph, Point

# --------------------------------------------------------------------------- #
# private helpers: cut-out versions of the motif glyphs, for use inside badges
# --------------------------------------------------------------------------- #


def _cut_plus(g: Glyph, cx: float, cy: float, arm: float = 1.7,
              width: float = 1.3) -> None:
    g.erase(A.polyline([(cx - arm, cy), (cx + arm, cy)]), width)
    g.erase(A.polyline([(cx, cy - arm), (cx, cy + arm)]), width)


def _cut_minus(g: Glyph, cx: float, cy: float, arm: float = 1.7,
               width: float = 1.3) -> None:
    g.erase(A.polyline([(cx - arm, cy), (cx + arm, cy)]), width)


def _cut_cross(g: Glyph, cx: float, cy: float, arm: float = 1.5,
               width: float = 1.3) -> None:
    g.erase(A.polyline([(cx - arm, cy - arm), (cx + arm, cy + arm)]), width)
    g.erase(A.polyline([(cx - arm, cy + arm), (cx + arm, cy - arm)]), width)


def _cut_check(g: Glyph, cx: float, cy: float, arm: float = 1.8,
               width: float = 1.35) -> None:
    g.erase(A.polyline([(cx - arm, cy + arm * 0.08),
                        (cx - arm * 0.28, cy + arm * 0.72),
                        (cx + arm, cy - arm * 0.62)]), width)


def _badge(g: Glyph, cx: float, cy: float, r: float = 3.1,
           ring: float = 1.15) -> None:
    """A solid badge disc with a clear margin around it."""
    A.badge_hole(g, cx, cy, r + ring)
    A.badge(g, cx, cy, r)


def _rows(g: Glyph, ys: list[float], x0: float, x1: float,
          width: float = STROKE) -> None:
    for y in ys:
        g.line((x0, y), (x1, y), width)


def _text_rows(g: Glyph, ys: list[float], x0: float = 4.9, x1: float = 11.4,
               width: float = HAIRLINE) -> None:
    _rows(g, ys, x0, x1, width)


def question_mark(g: Glyph, cx: float = 8.0, cy: float = 7.0,
                  scale: float = 1.0, width: float = 1.6,
                  cut: bool = False) -> None:
    """A question mark: a hook that turns inward, a stem, a dot.

    The hook is one arc that keeps going past six o'clock on the right side.
    An arc that stops at the top reads as a letter Y, which is exactly what the
    mark looked like when this was written as a pair of short arcs.
    """
    radius = 2.4 * scale
    start, end = 205.0, 425.0
    turn = (cx + radius * math.cos(math.radians(end)),
            cy + radius * math.sin(math.radians(end)))
    inner = (cx, cy + 2.3 * scale)
    if cut:
        g.erase(A.arc(cx, cy, radius, start, end), width)
        g.erase(A.polyline([turn, inner]), width)
        g.hole(A.circ(cx, cy + 4.2 * scale, 0.9 * scale))
    else:
        g.stroke(A.arc(cx, cy, radius, start, end), width)
        g.stroke(A.polyline([turn, inner]), width)
        g.dot(cx, cy + 4.2 * scale, 0.9 * scale)


def package_box(g: Glyph, cx: float = 8.0, cy: float = 8.8,
                size: float = 5.0) -> None:
    """A shipping carton seen from above the corner: lid, front and side."""
    half, height = size, size * 0.86
    top = [(cx, cy - half), (cx + half, cy - half * 0.52),
           (cx, cy), (cx - half, cy - half * 0.52)]
    left = [(cx - half, cy - half * 0.52), (cx, cy), (cx, cy + height),
            (cx - half, cy + height - half * 0.52)]
    right = [(cx + half, cy - half * 0.52), (cx, cy), (cx, cy + height),
             (cx + half, cy + height - half * 0.52)]
    g.stroke(A.polyline(top + [top[0]]), 1.2)
    g.stroke(A.polyline(left + [left[0]]), 1.2)
    g.stroke(A.polyline(right + [right[0]]), 1.2)
    # The tape seam down the middle of the lid, painted rather than cut so it
    # survives the outline it sits on.
    g.line((cx, cy), (cx, cy + height), 1.0)


# --------------------------------------------------------------------------- #
# documents and files
# --------------------------------------------------------------------------- #


def document_new(g: Glyph) -> None:
    """A sheet with a plus badge: the Aqua "new document"."""
    A.sheet(g, 2.6, 1.6, 8.6, 11.4)
    _rows(g, [5.4, 7.6, 9.8], 4.6, 9.2, HAIRLINE)
    _badge(g, 11.7, 11.6, 2.9)
    _cut_plus(g, 11.7, 11.6, 1.6, 1.35)


def document_open(g: Glyph) -> None:
    """An open folder with a sheet rising out of it."""
    g.stroke(A.polyline([(1.9, 12.0), (1.9, 4.4), (5.9, 4.4), (7.1, 6.2),
                         (12.4, 6.2)]), STROKE)
    A.sheet(g, 5.2, 1.9, 6.6, 5.6, 1.8, 0.7, STROKE)
    g.stroke(A.polyline([(1.9, 12.0), (4.2, 7.4), (14.1, 7.4), (11.8, 12.0),
                         (1.9, 12.0)]), STROKE)


def document_save(g: Glyph) -> None:
    """The Aqua floppy: a rounded square with a shutter and a label."""
    g.stroke(A.rr(2.2, 2.2, 11.6, 11.6, 1.9), STROKE)
    g.bar(4.6, 2.6, 6.8, 4.0, 0.5)
    g.erase(A.rr(6.1, 2.9, 2.2, 2.5, 0.3))
    g.stroke(A.rr(4.4, 9.0, 7.2, 4.4, 0.7), HAIRLINE + 0.35)
    g.erase(A.rr(6.4, 10.4, 3.2, 1.2, 0.4))
    return None


def document_save_as(g: Glyph) -> None:
    """A floppy with a pencil at its corner."""
    g.stroke(A.rr(1.9, 1.9, 10.2, 10.2, 1.7), STROKE)
    g.bar(3.8, 2.3, 6.0, 3.4, 0.4)
    g.erase(A.rr(5.1, 2.6, 2.0, 2.2, 0.3))
    g.stroke(A.rr(3.7, 7.7, 6.4, 4.0, 0.6), HAIRLINE + 0.35)
    g.erase(A.rr(5.5, 9.0, 2.8, 1.0, 0.4))
    A.badge_hole(g, 12.3, 12.3, 4.1)
    g.solid([(9.6, 14.6), (10.2, 12.6), (13.5, 9.2), (14.8, 10.5),
             (11.4, 13.7)], 0.4)


def document_send(g: Glyph) -> None:
    A.envelope(g, 1.9, 3.4, 12.2, 8.2)
    A.arrow(g, -35, 9.4, 10.2, 0.5)


def document_print(g: Glyph) -> None:
    A.printer(g)


def document_print_preview(g: Glyph) -> None:
    """A printer with a magnifier over the sheet it produced."""
    A.printer(g)
    A.badge_hole(g, 11.0, 11.0, 3.6)
    A.magnifier(g, 10.9, 10.9, 1.65, 1.3)


def document_page_setup(g: Glyph) -> None:
    """A sheet with crop marks: the page-setup dialog."""
    A.sheet(g, 3.4, 1.9, 9.2, 12.2)
    for x in (3.4, 12.6):
        g.line((x, 1.9), (x, 4.3), HAIRLINE + 0.25)
        g.line((x, 11.7), (x, 14.1), HAIRLINE + 0.25)
    for y in (1.9, 14.1):
        g.line((3.4, y), (5.6, y), HAIRLINE + 0.25)
        g.line((10.4, y), (12.6, y), HAIRLINE + 0.25)
    _text_rows(g, [6.4, 8.4], 5.4, 10.6)


def document_properties(g: Glyph) -> None:
    """A sheet with a gear: the "properties" inspector."""
    A.sheet(g, 2.4, 1.8, 8.4, 11.2)
    _text_rows(g, [5.0, 7.0], 4.2, 8.0)
    _badge(g, 11.6, 11.6, 3.0)
    _cut_gear(g, 11.6, 11.6, 1.75)


def _cut_gear(g: Glyph, cx: float, cy: float, r: float) -> None:
    points = []
    for index in range(8):
        angle = index * 45.0
        for offset, radius in ((0.0, r * 0.72), (10.0, r), (33.0, r), (43.0, r * 0.72)):
            a = math.radians(angle + offset)
            points.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    g.erase(A.rpoly(points, 0.2, True), 0.9)
    g.hole(A.circ(cx, cy, r * 0.3))


def document_revert(g: Glyph) -> None:
    """A sheet with a circular arrow: reload the saved copy."""
    A.sheet(g, 2.4, 1.8, 8.4, 11.2)
    _text_rows(g, [5.0, 7.0], 4.2, 8.0)
    A.badge_hole(g, 11.5, 11.5, 4.0)
    g.ring(11.5, 11.5, 2.5, 1.35)
    g.hole(A.rr(11.0, 9.2, 3.0, 2.4, 0.0))
    A.arrow(g, -140, 9.3, 9.3, 0.26)


def document_edit(g: Glyph) -> None:
    """A sheet with a pencil across its foot."""
    A.sheet(g, 3.2, 1.7, 9.4, 9.4)
    _text_rows(g, [4.9, 6.7, 8.5], 5.0, 11.0)
    g.solid([(2.2, 14.0), (2.9, 11.6), (10.6, 3.9), (12.6, 5.9), (4.9, 13.7)], 0.4)
    g.erase(A.polyline([(9.6, 4.9), (11.6, 6.9)]), HAIRLINE + 0.3)


def document_open_recent(g: Glyph) -> None:
    """A folder with a clock badge: recently used files."""
    A.folder(g, 1.7, 4.0, 10.6, 9.4)
    _badge(g, 12.0, 11.6, 3.0)
    g.hole(A.circ(12.0, 11.6, 1.9))
    g.ring(12.0, 11.6, 1.9, 1.15)
    g.erase(A.polyline([(12.0, 10.6), (12.0, 11.6), (12.9, 12.1)]), 1.15)


def folder_new(g: Glyph) -> None:
    """A folder with a plus badge."""
    A.folder(g, 1.7, 4.0, 10.4, 9.4)
    _badge(g, 11.9, 11.6, 3.0)
    _cut_plus(g, 11.9, 11.6, 1.65, 1.35)


def insert_image(g: Glyph) -> None:
    """A framed picture with a hill and a sun, plus a plus badge."""
    g.stroke(A.rr(1.9, 3.4, 10.6, 9.0, 1.2), STROKE)
    g.hole(A.rr(2.9, 4.4, 8.6, 7.0, 0.6))
    g.bar(2.9, 9.2, 8.6, 2.2, 0.3)
    g.hole(A.polyline([(2.9, 11.4), (5.6, 8.0), (7.8, 10.6), (9.4, 8.6),
                       (11.5, 11.4), (2.9, 11.4)]))
    g.dot(4.6, 6.2, 1.05)
    _badge(g, 11.9, 11.9, 2.8)
    _cut_plus(g, 11.9, 11.9, 1.55, 1.3)


def insert_link(g: Glyph) -> None:
    """The Aqua chain link, two interlocking capsules."""
    g.stroke(A.rr(1.9, 6.2, 8.0, 3.6, 1.8), STROKE)
    g.stroke(A.rr(6.1, 6.2, 8.0, 3.6, 1.8), STROKE)
    g.hole(A.rr(6.4, 7.4, 3.2, 1.2, 0.6))
    _badge(g, 12.0, 11.8, 2.7)
    _cut_plus(g, 12.0, 11.8, 1.5, 1.3)


def insert_object(g: Glyph) -> None:
    """A dashed frame holding a solid square: an embedded object."""
    for a, b in (((4.0, 2.1), (12.0, 2.1)), ((4.0, 13.9), (12.0, 13.9)),
                 ((2.1, 4.0), (2.1, 12.0)), ((13.9, 4.0), (13.9, 12.0))):
        g.stroke(A.polyline([a, b]), STROKE)
    return g.bar(5.0, 5.0, 6.0, 6.0, 1.0)


def insert_text(g: Glyph) -> None:
    """Four text rows with a caret: insert plain text."""
    g.bar(2.4, 3.0, 1.8, 10.0, 0.9)
    _rows(g, [4.4, 7.4, 10.4], 5.6, 12.4, STROKE)
    g.line((5.6, 12.9), (10.0, 12.9), STROKE)


# --------------------------------------------------------------------------- #
# editing
# --------------------------------------------------------------------------- #


def edit_copy(g: Glyph) -> None:
    """Two offset sheets: the Aqua copy."""
    g.stroke(A.rr(2.0, 4.6, 8.8, 8.8, 1.4), STROKE)
    g.hole(A.rr(3.4, 5.8, 6.0, 6.2, 0.6))
    g.stroke(A.rr(5.4, 2.2, 8.6, 8.6, 1.4), STROKE)


def edit_cut(g: Glyph) -> None:
    """Scissors: two blades crossing over two rings."""
    g.ring(4.3, 11.3, 2.2, STROKE)
    g.ring(11.7, 11.3, 2.2, STROKE)
    g.line((5.8, 9.6), (12.1, 2.4), STROKE)
    g.line((10.2, 9.6), (3.9, 2.4), STROKE)
    g.dot(8.0, 6.7, 1.1)


def edit_paste(g: Glyph) -> None:
    """A clipboard: a board, a clip and three rows."""
    g.stroke(A.rr(2.6, 2.6, 10.8, 11.4, 1.6), STROKE)
    g.bar(5.6, 1.6, 4.8, 2.4, 0.9)
    _text_rows(g, [6.4, 8.6, 10.8], 4.8, 11.2)


def edit_delete(g: Glyph) -> None:
    A.trash(g)


def edit_clear(g: Glyph) -> None:
    """A sheet being emptied: a page and a sweeping arrow."""
    A.sheet(g, 3.6, 1.9, 8.8, 9.6)
    _text_rows(g, [5.0, 7.0], 5.2, 10.8)
    A.arrow(g, 8, 8.4, 11.6, 0.72)


def edit_clear_all(g: Glyph) -> None:
    """Three stacked sheets struck through: empty the whole list."""
    A.sheet(g, 1.9, 1.6, 7.2, 8.4)
    A.sheet(g, 3.4, 2.6, 7.2, 8.4)
    A.sheet(g, 4.9, 3.6, 7.2, 8.4)
    g.erase(A.polyline([(1.9, 13.4), (14.0, 2.6)]), 2.6)
    g.stroke(A.polyline([(1.9, 13.4), (14.0, 2.6)]), STROKE)


def edit_undo(g: Glyph, forward: bool = False) -> None:
    """The Aqua undo arrow: a fat hooked capsule, mirrored for redo."""
    points = [(2.2, 8.6), (5.6, 5.2), (5.6, 7.2), (9.4, 7.2),
              (13.4, 11.2), (11.2, 11.6), (8.8, 9.4), (5.6, 9.4), (5.6, 12.0)]
    if forward:
        points = A.flip(points)
    return g.fill(A.rpoly(points, 0.55, True))


def edit_redo(g: Glyph) -> None:
    edit_undo(g, forward=True)


def edit_select(g: Glyph) -> None:
    """An arrow cursor over a selection: the Aqua pointer."""
    g.solid([(4.0, 2.0), (11.8, 8.4), (8.4, 8.8), (10.4, 13.4), (8.4, 14.2),
             (6.6, 9.8), (4.2, 12.0)], 0.5)


def edit_select_all(g: Glyph) -> None:
    """A dashed selection frame with a solid square in it."""
    g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 1.4), STROKE)
    for start in range(0, 360, 30):
        g.erase(A.arc(8.0, 8.0, 6.5, start + 5, start + 21), 1.9)
    return g.bar(4.0, 4.0, 8.0, 8.0, 1.0)


def edit_find(g: Glyph) -> None:
    A.magnifier(g)


def edit_find_replace(g: Glyph) -> None:
    """A magnifier with a pencil at its corner: find and replace."""
    A.magnifier(g, 6.2, 6.2, 4.1, STROKE)
    A.badge_hole(g, 12.0, 12.2, 4.0)
    g.solid([(9.4, 14.6), (10.0, 12.5), (13.3, 9.2), (14.6, 10.5),
             (11.3, 13.9)], 0.4)


def system_search(g: Glyph) -> None:
    A.magnifier(g)


def find_location(g: Glyph) -> None:
    """A locator: crosshair with a bore in the middle."""
    g.ring(8.0, 8.0, 5.0, STROKE)
    for tail, head in (((8.0, 1.0), (8.0, 3.4)), ((8.0, 12.6), (8.0, 15.0)),
                       ((1.0, 8.0), (3.4, 8.0)), ((12.6, 8.0), (15.0, 8.0))):
        g.line(tail, head, STROKE)
    return g.dot(8.0, 8.0, 1.2)


def mark_location(g: Glyph) -> None:
    """A solid pin with a cut bore: a saved place."""
    g.solid([(8.0, 14.2), (3.0, 7.8), (3.0, 5.9), (8.0, 2.0),
             (13.0, 5.9), (13.0, 7.8)], 1.5)
    return g.hole(A.circ(8.0, 7.0, 1.9))


def color_select(g: Glyph) -> None:
    """An eyedropper with a drop: pick a colour."""
    g.solid([(9.4, 2.2), (13.8, 6.6), (12.4, 8.0), (8.0, 3.6)], 0.6)
    g.solid([(8.6, 3.0), (13.0, 7.4), (7.4, 13.0), (4.4, 13.4), (2.4, 12.2),
             (2.8, 9.4)], 0.7)
    return g.hole(A.rr(4.6, 9.4, 3.4, 1.2, 0.5))


def font_select(g: Glyph) -> None:
    """A serif capital A in a frame: choose a font."""
    g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 1.4), STROKE)
    g.stroke(A.polyline([(4.4, 11.6), (8.0, 4.6), (11.6, 11.6)]), STROKE)
    return g.line((5.8, 8.8), (10.2, 8.8), STROKE)


def error_correct(g: Glyph) -> None:
    """A cross turning into a tick: automatic correction."""
    g.line((2.6, 5.0), (6.2, 8.6), STROKE)
    g.line((2.6, 8.6), (6.2, 5.0), STROKE)
    A.arrow(g, 0, 9.4, 6.8, 0.42)
    g.stroke(A.polyline([(8.4, 11.6), (10.4, 13.4), (13.6, 9.2)]), STROKE)


def tools_check_spelling(g: Glyph) -> None:
    """An A over a squiggle: the spell-check mark.

    Three letters plus a tick was four marks fighting for ten pixels and read
    as a bowl of shapes.  One letter and the underline say it on their own.
    """
    g.stroke(A.polyline([(3.0, 10.2), (7.0, 2.4), (11.0, 10.2)]), STROKE + 0.4)
    g.line((4.6, 7.4), (9.4, 7.4), STROKE + 0.2)
    # A coarse squiggle: at 16 px a fine wave turns into a grey smear.
    wave = [(2.0, 13.4), (4.4, 12.2), (6.8, 13.6), (9.2, 12.2), (11.6, 13.4),
            (13.6, 12.6)]
    return g.stroke(A.polyline(wave), 1.8)


# --------------------------------------------------------------------------- #
# views
# --------------------------------------------------------------------------- #


def view_app_grid(g: Glyph) -> None:
    """Nine rounded tiles: the application grid."""
    for row in range(3):
        for column in range(3):
            g.bar(1.7 + column * 4.35, 1.7 + row * 4.35, 3.9, 3.9, 1.1)


def view_grid(g: Glyph) -> None:
    """Four large tiles."""
    for row in range(2):
        for column in range(2):
            g.bar(1.8 + column * 7.0, 1.8 + row * 7.0, 5.6, 5.6, 1.2)


def view_list(g: Glyph) -> None:
    for y in (4.0, 8.0, 12.0):
        g.bar(2.0, y - 1.1, 12.0, 2.2, 1.1)


def view_list_bullet(g: Glyph) -> None:
    for y in (3.8, 8.0, 12.2):
        g.dot(3.0, y, 1.2)
        g.bar(5.8, y - 0.95, 8.2, 1.9, 0.95)


def view_list_ordered(g: Glyph) -> None:
    for index, y in enumerate((3.8, 8.0, 12.2), start=1):
        g.stroke(A.polyline([(2.1, y - 1.4), (3.1, y - 1.9), (3.1, y + 1.1)]), 1.15)
        if index == 2:
            g.stroke(A.polyline([(2.1, y - 1.6), (3.2, y - 1.6)]), 1.15)
        if index == 3:
            g.stroke(A.circ(2.7, y - 1.3, 0.65), 1.05)
        g.bar(5.8, y - 0.95, 8.2, 1.9, 0.95)


def view_continuous(g: Glyph) -> None:
    """One long sheet with a second peeking behind."""
    g.stroke(A.rr(3.4, 2.0, 10.2, 9.4, 1.2), STROKE)
    g.stroke(A.rr(2.0, 3.4, 10.2, 9.4, 1.2), STROKE)


def view_dual(g: Glyph) -> None:
    g.stroke(A.rr(1.8, 2.4, 5.4, 11.2, 1.1), STROKE)
    return g.stroke(A.rr(8.8, 2.4, 5.4, 11.2, 1.1), STROKE)


def view_paged(g: Glyph) -> None:
    """A spread with a fold: two pages, one seam."""
    g.stroke(A.rr(1.7, 2.6, 12.6, 10.8, 1.2), STROKE)
    g.erase(A.polyline([(8.0, 2.6), (8.0, 13.4)]), 1.9)
    return g.stroke(A.polyline([(8.0, 3.4), (8.0, 12.6)]), HAIRLINE + 0.4)


def view_more(g: Glyph, horizontal: bool = False) -> None:
    if horizontal:
        for x in (3.4, 8.0, 12.6):
            g.dot(x, 8.0, 1.35)
    else:
        for y in (3.4, 8.0, 12.6):
            g.dot(8.0, y, 1.35)


def view_more_horizontal(g: Glyph) -> None:
    view_more(g, horizontal=True)


def open_menu(g: Glyph) -> None:
    """Three stacked bars: the hamburger, at Aqua weight."""
    for y in (4.2, 8.0, 11.8):
        g.bar(2.2, y - 1.15, 11.6, 2.3, 1.15)


def view_fullscreen(g: Glyph) -> None:
    """Four corner brackets."""
    for sx, sy in ((1.0, 1.0), (-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0)):
        g.stroke(A.polyline([(8.0 + sx * 6.4, 8.0 + sy * 2.2),
                             (8.0 + sx * 6.4, 8.0 + sy * 6.4),
                             (8.0 + sx * 2.2, 8.0 + sy * 6.4)]), STROKE)


def view_restore(g: Glyph) -> None:
    """Inward corner brackets: leave fullscreen."""
    for sx, sy in ((1.0, 1.0), (-1.0, 1.0), (1.0, -1.0), (-1.0, -1.0)):
        g.stroke(A.polyline([(8.0 + sx * 2.0, 8.0 + sy * 6.4),
                             (8.0 + sx * 2.0, 8.0 + sy * 2.0),
                             (8.0 + sx * 6.4, 8.0 + sy * 2.0)]), STROKE)


def view_pin(g: Glyph) -> None:
    """A thumbtack: head, waist and needle."""
    g.bar(5.4, 2.0, 5.2, 2.2, 1.1)
    g.solid([(6.4, 4.6), (9.6, 4.6), (9.0, 8.8), (7.0, 8.8)], 0.5)
    g.line((8.0, 8.8), (8.0, 13.8), 1.3)


def view_mirror(g: Glyph) -> None:
    """Two half-sheets mirrored about a dashed axis."""
    g.stroke(A.rr(1.7, 3.4, 5.0, 9.2, 1.1), STROKE)
    g.stroke(A.rr(9.3, 3.4, 5.0, 9.2, 1.1), STROKE)
    g.erase(A.polyline([(8.0, 2.2), (8.0, 13.8)]), 2.0)
    return g.stroke(A.polyline([(8.0, 3.0), (8.0, 13.0)]), HAIRLINE + 0.3)


def view_refresh(g: Glyph, angle: float = 0.0) -> None:
    """A thick circular arrow: reload."""
    g.stroke(A.arc(8.0, 8.0, 5.4, -60, 220), 2.0)
    A.arrow(g, 0, 0.0, 0.0, 0.0) if False else None
    head = [(12.6, 2.4), (14.2, 7.4), (9.6, 6.4)]
    g.solid(A.rotate(head, angle, 8.0, 8.0), 0.5)


def view_reveal(g: Glyph) -> None:
    A.eye(g)


def view_conceal(g: Glyph) -> None:
    """The eye struck through: looking is turned off."""
    A.eye(g, 8.0, 8.0)
    g.erase(A.polyline([(1.6, 14.4), (14.4, 1.6)]), 2.8)
    return g.stroke(A.polyline([(2.7, 13.3), (13.3, 2.7)]), 1.5)


def view_sort(g: Glyph, descending: bool = False) -> None:
    """Three shrinking bars and a direction arrow."""
    heights = (10.0, 7.0, 4.0)
    for index, height in enumerate(heights):
        g.bar(1.7 + index * 3.4, 13.2 - height, 2.4, height, 0.7)
    angle = 0 if descending else 180
    A.arrow(g, angle, 11.6, 4.4, 0.34)


def view_sort_ascending(g: Glyph) -> None:
    view_sort(g, descending=False)


def view_sort_descending(g: Glyph) -> None:
    view_sort(g, descending=True)


def view_wrapped(g: Glyph) -> None:
    """A line that turns back on itself: wrapped text."""
    _rows(g, [3.4, 8.6], 2.2, 13.8, 1.7)
    g.stroke(A.polyline([(13.8, 6.4), (5.4, 6.4), (3.0, 8.6), (5.4, 10.8),
                         (11.0, 10.8)]), 1.7)


def sidebar(g: Glyph, right: bool = False) -> None:
    """A window whose side column is solid."""
    g.stroke(A.rr(1.8, 2.6, 12.4, 10.8, 1.2), STROKE)
    left = 9.4 if right else 3.2
    g.bar(left, 3.4, 4.4, 9.2, 0.9)
    for y in (5.4, 8.0, 10.6):
        g.erase(A.polyline([(left + 1.0, y), (left + 3.4, y)]), 1.2)


def sidebar_show(g: Glyph) -> None:
    sidebar(g, right=False)


def sidebar_show_right(g: Glyph) -> None:
    sidebar(g, right=True)


def tab_new(g: Glyph) -> None:
    """A browser tab with a plus."""
    g.stroke(A.rr(1.8, 2.4, 12.4, 11.2, 1.3), STROKE)
    g.erase(A.polyline([(1.8, 6.4), (14.2, 6.4)]), 1.9)
    g.stroke(A.polyline([(1.8, 6.4), (14.2, 6.4)]), HAIRLINE + 0.3)
    return A.plus(g, 8.0, 10.4, 2.6, STROKE)


def window_new(g: Glyph) -> None:
    """A window with a plus in its title bar."""
    g.stroke(A.rr(1.7, 2.6, 12.6, 10.8, 1.3), STROKE)
    g.erase(A.polyline([(1.7, 6.6), (14.3, 6.6)]), 1.9)
    g.stroke(A.polyline([(1.7, 6.6), (14.3, 6.6)]), HAIRLINE + 0.3)
    for x in (3.6, 5.6):
        g.hole(A.circ(x, 4.6, 0.75))
    return A.plus(g, 8.6, 10.6, 2.5, STROKE)


def selection_mode(g: Glyph) -> None:
    """A pointer with a dashed box: pick several items."""
    g.stroke(A.rr(1.8, 1.8, 9.4, 9.4, 1.2), STROKE)
    for start in range(0, 360, 30):
        g.erase(A.arc(6.5, 6.5, 4.7, start + 5, start + 21), 1.9)
    return edit_select(g)


def view_reveal_password(g: Glyph) -> None:
    A.eye(g)


# --------------------------------------------------------------------------- #
# navigation
# --------------------------------------------------------------------------- #


def go(g: Glyph, angle: float = 0.0, scale: float = 0.92) -> None:
    A.arrow(g, angle, 8.0, 8.0, scale)


def go_first(g: Glyph) -> None:
    A.arrow(g, 180, 9.6, 8.0, 0.80)
    A.wall(g, 2.1, 3.2, 12.8)


def go_last(g: Glyph) -> None:
    A.arrow(g, 0, 6.4, 8.0, 0.80)
    A.wall(g, 12.1, 3.2, 12.8)


def go_jump(g: Glyph) -> None:
    A.arrow(g, 0, 5.4, 8.0, 0.72)
    A.wall(g, 11.4, 3.2, 12.8)


def go_home(g: Glyph) -> None:
    A.house(g)


def go_top(g: Glyph) -> None:
    """An up arrow stopped by the top of the list.

    The arrow is short enough to clear the wall: a full-height arrow has its
    head swallowed by the bar and the pair reads as a letter T.
    """
    A.arrow(g, 270, 8.0, 8.6, 0.68)
    g.bar(2.6, 1.9, 10.8, 1.8, 0.9)


def go_bottom(g: Glyph) -> None:
    A.arrow(g, 90, 8.0, 7.4, 0.68)
    g.bar(2.6, 12.3, 10.8, 1.8, 0.9)


# --------------------------------------------------------------------------- #
# media
# --------------------------------------------------------------------------- #


def media_play(g: Glyph) -> None:
    A.play(g)


def media_pause(g: Glyph) -> None:
    A.pause(g)


def media_stop(g: Glyph) -> None:
    A.stop(g)


def media_record(g: Glyph) -> None:
    A.recording(g)


def media_eject(g: Glyph) -> None:
    A.eject(g)


def media_seek(g: Glyph, forward: bool = True) -> None:
    A.seek(g, forward)


def media_skip(g: Glyph, forward: bool = True) -> None:
    A.skip(g, forward)


def media_view_subtitles(g: Glyph) -> None:
    """A screen with two subtitle lines: the Aqua caption plate."""
    g.stroke(A.rr(1.8, 2.6, 12.4, 10.8, 1.3), STROKE)
    g.bar(4.0, 9.0, 5.4, 1.8, 0.9)
    return g.bar(10.2, 9.0, 2.0, 1.8, 0.9)


# --------------------------------------------------------------------------- #
# objects: flip, rotate, select
# --------------------------------------------------------------------------- #


def object_flip(g: Glyph, vertical: bool = False) -> None:
    """A shape beside its mirror image across a dashed axis."""
    shape = [(2.2, 4.0), (6.4, 4.0), (6.4, 12.6), (2.2, 12.6)]
    g.solid(shape, 0.8)
    mirrored = A.flip(shape, vertical)
    for x, y in mirrored:
        del x, y
    g.solid(A.grow(mirrored, 8.0, 8.0, 1.0), 0.8)
    axis = [(8.0, 1.6), (8.0, 14.4)] if not vertical else [(1.6, 8.0), (14.4, 8.0)]
    g.erase(A.polyline(axis), 2.0)
    return g.stroke(A.polyline(axis), HAIRLINE + 0.3)


def object_flip_horizontal(g: Glyph) -> None:
    object_flip(g, vertical=False)


def object_flip_vertical(g: Glyph) -> None:
    object_flip(g, vertical=True)


def object_rotate(g: Glyph, left: bool = True) -> None:
    """A rounded arrow circling a solid block."""
    g.bar(4.6, 4.6, 6.8, 6.8, 1.4)
    start, end = (-20, 250) if left else (-70, 200)
    g.stroke(A.arc(8.0, 8.0, 6.1, start, end), STROKE)
    tip = (13.2, 4.6) if left else (2.8, 4.6)
    step = 1 if left else -1
    points = [(tip[0] + 0.2 * step, tip[1] + 2.8), (tip[0] + 2.4 * step, tip[1]),
              (tip[0] - 2.0 * step, tip[1] - 1.3)]
    return g.solid(points, 0.5)


def object_rotate_left(g: Glyph) -> None:
    object_rotate(g, left=True)


def object_rotate_right(g: Glyph) -> None:
    object_rotate(g, left=False)


def object_select(g: Glyph) -> None:
    """A check inside a rounded square: the Aqua confirmation."""
    g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 2.6), STROKE)
    return A.check(g, 8.0, 8.0, 3.9, STROKE + 0.1)


def send_to(g: Glyph) -> None:
    """A sheet flying off an arrow: send elsewhere."""
    A.sheet(g, 4.6, 1.8, 7.4, 8.0)
    A.arrow(g, 0, 8.0, 11.8, 0.66)


# --------------------------------------------------------------------------- #
# mail
# --------------------------------------------------------------------------- #


def mail_message_new(g: Glyph) -> None:
    A.envelope(g, 1.9, 3.4, 10.0, 8.2)
    _badge(g, 12.0, 11.6, 2.9)
    _cut_plus(g, 12.0, 11.6, 1.55, 1.3)


def mail_send(g: Glyph) -> None:
    """The Aqua paper plane: a dart split along its spine by one crease.

    The seam has to stop where the two wings meet.  Carving it out to the tail
    as well leaves nothing but two slivers at this size.
    """
    g.solid([(1.5, 7.3), (14.5, 1.8), (7.3, 8.4)], 0.45)
    return g.solid([(7.9, 8.8), (14.5, 1.8), (9.1, 14.2)], 0.45)


def mail_send_receive(g: Glyph) -> None:
    A.arrow(g, 0, 7.0, 5.2, 0.52)
    A.arrow(g, 180, 9.0, 10.8, 0.52)


def mail_reply(g: Glyph) -> None:
    """An envelope with a hooked reply arrow over it."""
    A.envelope(g, 1.9, 6.2, 12.2, 7.4)
    path = A.rpoly([(2.0, 5.4), (5.0, 2.2), (5.0, 3.9), (8.6, 3.9), (11.8, 6.6),
                    (9.6, 6.6), (8.0, 5.5), (5.0, 5.5), (5.0, 8.2)], 0.5, True)
    return g.fill(path)


def mail_reply_all(g: Glyph) -> None:
    A.envelope(g, 2.6, 6.4, 11.4, 7.2)
    for offset in (0.0, 3.4):
        path = A.rpoly([(1.0 + offset, 5.6), (3.6 + offset, 2.8),
                        (3.6 + offset, 4.3), (6.2 + offset, 4.3),
                        (6.2 + offset, 6.9), (3.6 + offset, 6.9),
                        (3.6 + offset, 8.4)], 0.45, True)
        g.fill(path)


def mail_forward(g: Glyph) -> None:
    A.envelope(g, 1.9, 6.2, 12.2, 7.4)
    path = A.rpoly([(14.0, 5.4), (11.0, 2.2), (11.0, 3.9), (7.4, 3.9),
                    (4.2, 6.6), (6.4, 6.6), (8.0, 5.5), (11.0, 5.5),
                    (11.0, 8.2)], 0.5, True)
    return g.fill(path)


def mail_mark_important(g: Glyph) -> None:
    A.envelope(g, 1.9, 3.6, 10.2, 8.4)
    _badge(g, 12.2, 11.4, 3.0)
    g.erase(A.rr(11.4, 9.4, 1.6, 3.4, 0.75))
    return g.hole(A.circ(12.2, 12.7, 0.85))


def mail_mark_junk(g: Glyph) -> None:
    A.envelope(g, 1.9, 3.6, 10.2, 8.4)
    _badge(g, 12.2, 11.4, 3.0)
    _cut_cross(g, 12.2, 11.4, 1.5, 1.3)


def mail_mark_notjunk(g: Glyph, angle: float = 0.0) -> None:
    """A flame beside the envelope: a message rescued from the junk pile."""
    A.envelope(g, 1.9, 3.6, 10.2, 8.4)
    g.solid(A.rotate([(12.2, 9.0), (14.6, 12.0), (12.2, 14.4), (9.8, 12.0)], angle),
            0.9)


# --------------------------------------------------------------------------- #
# zoom
# --------------------------------------------------------------------------- #


def zoom_in(g: Glyph) -> None:
    A.magnifier(g, 6.6, 6.4, 4.4, STROKE)
    A.plus(g, 6.6, 6.4, 2.2, STROKE)


def zoom_out(g: Glyph) -> None:
    A.magnifier(g, 6.6, 6.4, 4.4, STROKE)
    A.minus(g, 6.6, 6.4, 2.2, STROKE)


def zoom_fit_best(g: Glyph) -> None:
    """A lens with inward arrows: fit to window."""
    A.magnifier(g, 6.4, 6.2, 4.2, STROKE)
    A.arrow(g, 135, 6.0, 5.8, 0.28)
    return A.arrow(g, -45, 7.4, 7.2, 0.28)


def zoom_original(g: Glyph) -> None:
    """A lens with an equals sign: 1:1, the size it already is.

    Two figures and a colon turn to mush in a 6 px bore; a single broad mark
    is the only thing that survives the small sizes this icon lives at.
    """
    A.magnifier(g, 6.6, 6.4, 4.4, STROKE)
    for y in (5.4, 7.6):
        g.bar(4.6, y - 0.65, 4.0, 1.3, 0.65)


# --------------------------------------------------------------------------- #
# system
# --------------------------------------------------------------------------- #


def system_run(g: Glyph) -> None:
    """A play wedge inside a rounded window."""
    g.stroke(A.rr(1.8, 2.4, 12.4, 11.2, 1.4), STROKE)
    return A.play(g, 8.6, 8.0, 3.6)


def system_reboot(g: Glyph) -> None:
    """A circular arrow with a power stub."""
    g.stroke(A.arc(8.0, 8.6, 5.3, -40, 220), 2.0)
    g.solid([(11.9, 2.6), (13.9, 7.2), (9.2, 6.4)], 0.5)
    return g.bar(7.1, 1.6, 1.8, 6.4, 0.9)


def system_shutdown(g: Glyph) -> None:
    """The Aqua power ring: a gap at twelve and a stem."""
    g.stroke(A.arc(8.0, 8.6, 5.4, -55, 235), 2.1)
    return g.bar(7.1, 1.7, 1.9, 6.6, 0.95)


def system_log_out(g: Glyph) -> None:
    """An arrow leaving a doorway."""
    g.stroke(A.polyline([(9.0, 2.2), (2.4, 2.2), (2.4, 13.8), (9.0, 13.8)]), STROKE)
    A.arrow(g, 0, 8.8, 8.0, 0.72)


def system_switch_user(g: Glyph) -> None:
    """Two contacts with a swap arrow between them."""
    A.person(g, 4.9, 5.4, 2.0, STROKE, 4.2)
    A.person(g, 11.1, 5.4, 2.0, STROKE, 4.2)
    g.stroke(A.polyline([(4.0, 12.4), (12.0, 12.4)]), STROKE)
    g.solid([(10.6, 10.6), (13.4, 12.4), (10.6, 14.2)], 0.5)


def system_lock_screen(g: Glyph) -> None:
    A.lock(g, 8.0, 9.6, open=False)


def help_about(g: Glyph) -> None:
    """An i in a rounded tile: the Aqua about panel."""
    g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 3.0), STROKE)
    g.dot(8.0, 4.9, 1.15)
    return g.bar(7.0, 7.0, 2.0, 5.4, 1.0)


def process_stop(g: Glyph) -> None:
    """The Aqua stop sign: an octagon with a cross."""
    points = []
    for index in range(8):
        a = math.radians(22.5 + index * 45)
        points.append((8.0 + 6.2 * math.cos(a), 8.0 + 6.2 * math.sin(a)))
    g.solid(points, 0.9)
    A.cross(g, 8.0, 8.0, 2.6, 1.8)
    return None


def action_unavailable(g: Glyph) -> None:
    """A disc with a diagonal bar: the standard "not available"."""
    g.ring(8.0, 8.0, 6.0, STROKE + 0.2)
    g.erase(A.polyline([(3.2, 12.8), (12.8, 3.2)]), 2.6)
    return g.stroke(A.polyline([(3.2, 12.8), (12.8, 3.2)]), STROKE)


def system_software_update(g: Glyph) -> None:
    """A downward arrow into a tray: an update is waiting."""
    A.arrow(g, 90, 8.0, 6.4, 0.72)
    return g.stroke(A.polyline([(2.6, 11.0), (2.6, 13.4), (13.4, 13.4), (13.4, 11.0)]),
                    STROKE)


def camera_switch(g: Glyph) -> None:
    """A camera with a circular swap arrow."""
    A.camera(g, video=False)
    g.stroke(A.arc(6.6, 9.0, 2.9, 40, 320), 1.15)
    return g.solid([(9.3, 6.9), (9.9, 8.9), (7.8, 8.4)], 0.4)


def handset(g: Glyph, cx: float = 8.0, cy: float = 8.0,
            scale: float = 1.0) -> None:
    """The telephone receiver: an upright grip, a quarter turn, a mouth grip.

    Every phone glyph is this one shape - a vertical earpiece, a bend, a
    horizontal mouthpiece - and it is what makes the mark read as a handset
    instead of the horseshoe an upright U turned into.
    """
    def at(points):
        return [(cx + scale * (x - 7.8), cy + scale * (y - 7.8))
                for x, y in points]

    path = [(12.2, 3.2), (12.2, 6.4)]
    path += [(6.4 + 5.8 * math.cos(math.radians(a)),
              6.4 + 5.8 * math.sin(math.radians(a))) for a in range(0, 91, 3)]
    path += [(3.2, 12.2)]
    g.stroke(A.polyline(at(path)), 3.0 * scale)


def call_start(g: Glyph) -> None:
    """A handset: the call is up."""
    handset(g)


def call_direction(g: Glyph, kind: str = "incoming") -> None:
    """A handset in the corner with the arrow that says which way the call went.

    Rotating the whole receiver by 135 degrees, as this used to do, put the
    earpieces at odd angles and the icons stopped looking like phones.
    """
    handset(g, 6.0, 9.8, 0.74)
    if kind == "missed":
        _badge(g, 12.6, 3.6, 2.4)
        _cut_cross(g, 12.6, 3.6, 1.1, 1.05)
        return
    A.arrow(g, 135 if kind == "incoming" else -45, 12.6, 3.6, 0.42)


def call_stop(g: Glyph) -> None:
    """A handset behind a bar: hang up."""
    handset(g)
    A.slash(g, width=1.4, gap=0.9)


def chat_message_new(g: Glyph) -> None:
    A.speech(g)
    _badge(g, 12.2, 12.0, 2.7)
    _cut_plus(g, 12.2, 12.0, 1.45, 1.25)


def contact_new(g: Glyph) -> None:
    """A contact card: a person in a rounded frame, plus a badge."""
    g.stroke(A.rr(1.8, 2.6, 10.4, 10.8, 1.4), STROKE)
    A.person(g, 7.0, 6.4, 1.9, STROKE, 4.0)
    _badge(g, 12.2, 11.6, 2.8)
    _cut_plus(g, 12.2, 11.6, 1.5, 1.3)


def address_book_new(g: Glyph) -> None:
    """A book with a tab edge and a plus badge."""
    g.stroke(A.rr(3.0, 1.9, 9.4, 12.2, 1.2), STROKE)
    g.erase(A.polyline([(5.4, 1.9), (5.4, 14.1)]), 1.9)
    g.stroke(A.polyline([(5.4, 1.9), (5.4, 14.1)]), 1.15)
    _badge(g, 12.2, 11.6, 2.8)
    _cut_plus(g, 12.2, 11.6, 1.5, 1.3)


def appointment_new(g: Glyph) -> None:
    """A desk calendar: a bound block with a marked day."""
    g.stroke(A.rr(1.9, 3.2, 12.2, 10.8, 1.4), STROKE)
    g.erase(A.polyline([(1.9, 6.8), (14.1, 6.8)]), 1.9)
    g.stroke(A.polyline([(1.9, 6.8), (14.1, 6.8)]), 1.15)
    for x in (5.2, 10.8):
        g.bar(x - 0.8, 1.8, 1.6, 3.0, 0.8)
    g.bar(4.4, 8.8, 3.0, 2.8, 0.7)
    return g.bar(9.0, 8.8, 2.6, 2.8, 0.7)


def bookmark_new(g: Glyph) -> None:
    """A bookmark ribbon with a plus badge."""
    g.solid([(3.6, 1.9), (12.4, 1.9), (12.4, 13.9), (8.0, 10.4), (3.6, 13.9)], 1.0)
    g.hole(A.rr(5.4, 3.4, 5.2, 1.5, 0.7))
    _badge(g, 12.2, 11.6, 2.7)
    _cut_plus(g, 12.2, 11.6, 1.45, 1.25)


def star_new(g: Glyph) -> None:
    A.star(g, 6.8, 6.6, 5.0)
    _badge(g, 12.4, 11.8, 2.6)
    _cut_plus(g, 12.4, 11.8, 1.4, 1.2)


def list_remove_all(g: Glyph) -> None:
    """Every row struck through: clear the list."""
    for y in (3.6, 8.0, 12.4):
        g.bar(2.0, y - 1.0, 7.6, 2.0, 1.0)
        g.erase(A.polyline([(1.6, y + 1.4), (8.0, y - 1.4)]), 1.15)
    G_minus = A.minus(g, 12.0, 8.0, 2.2, 1.6)
    return G_minus


def value(g: Glyph, up: bool = True) -> None:
    """A stepper plate with one chevron: raise or lower a value."""
    g.stroke(A.rr(3.0, 1.9, 10.0, 12.2, 2.4), STROKE)
    g.erase(A.polyline([(3.0, 8.0), (13.0, 8.0)]), 1.9)
    g.stroke(A.polyline([(3.6, 8.0), (12.4, 8.0)]), HAIRLINE + 0.3)
    A.chevron(g, 270 if up else 90, 8.0, 5.0 if up else 11.0, 1.9, 1.6)


def format_text_bold(g: Glyph) -> None:
    """A chunky B: bold."""
    g.stroke(A.polyline([(4.4, 2.8), (4.4, 13.2)]), 2.0)
    g.stroke(A.rpoly([(4.4, 2.8), (8.4, 2.8), (10.4, 3.8), (10.4, 6.4),
                      (8.4, 7.6), (4.4, 7.6)], 1.0, False), 1.9)
    g.stroke(A.rpoly([(4.4, 7.6), (9.0, 7.6), (11.2, 9.0), (11.2, 11.8),
                      (9.0, 13.2), (4.4, 13.2)], 1.0, False), 1.9)


def format_text_italic(g: Glyph) -> None:
    """A slanted I with serifs."""
    g.stroke(A.polyline([(6.6, 3.0), (11.4, 3.0)]), 1.7)
    g.stroke(A.polyline([(4.6, 13.0), (9.4, 13.0)]), 1.7)
    g.stroke(A.polyline([(9.6, 3.0), (6.4, 13.0)]), 1.7)


def format_text_underline(g: Glyph) -> None:
    """U with a thick rule below."""
    g.stroke(A.polyline([(4.2, 2.6), (4.2, 8.4)]), 1.9)
    g.stroke(A.arc(8.0, 8.4, 3.8, 0, 180), 1.9)
    g.stroke(A.polyline([(11.8, 2.6), (11.8, 8.4)]), 1.9)
    g.bar(3.6, 12.6, 8.8, 1.8, 0.9)


def format_text_strikethrough(g: Glyph) -> None:
    """S with a bar through it."""
    g.stroke(A.polyline([(11.4, 4.6), (9.6, 3.0), (6.4, 3.0), (4.6, 4.9),
                         (4.8, 6.6), (11.2, 7.8), (11.4, 10.0), (9.4, 12.4),
                         (6.2, 12.4), (4.4, 10.8)]), 1.8)
    g.bar(2.4, 7.2, 11.2, 1.9, 0.95)


def format_text_plaintext(g: Glyph) -> None:
    """Four ruled rows: plain text."""
    for y in (2.8, 6.0, 9.2, 12.4):
        g.bar(2.0, y, 12.0, 1.7, 0.85)


def format_text_rich(g: Glyph) -> None:
    """A ruled page with one emphasised block."""
    for y in (2.8, 6.0, 9.2, 12.4):
        g.bar(2.0, y, 6.4, 1.7, 0.85)
    g.bar(9.6, 2.8, 4.4, 1.7, 0.85)
    g.bar(2.0, 6.0, 12.0, 1.7, 0.85)
    g.bar(9.6, 9.2, 4.4, 1.7, 0.85)
    return g.bar(2.0, 12.4, 9.0, 1.7, 0.85)


def format_text_direction(g: Glyph, rtl: bool = False) -> None:
    """Four ragged rows under a direction arrow: left-to-right or right-to-left."""
    for index, y in enumerate((6.2, 9.2, 12.2)):
        length = (10.2, 7.0, 11.4)[index]
        x = 14.0 - length if rtl else 2.0
        g.bar(x, y - 0.85, length, 1.7, 0.85)
    A.arrow(g, 180 if rtl else 0, 8.0, 2.8, 0.46)


def format_justify(g: Glyph, mode: str = "left") -> None:
    """Four rows with a justification: left, right, centre or fill."""
    if mode == "fill":
        widths = (12.0, 12.0, 12.0, 12.0)
    elif mode == "center":
        widths = (8.4, 11.4, 6.8, 10.0)
    else:
        widths = (12.0, 8.4, 12.0, 7.2)
    for index, y in enumerate((2.8, 6.1, 9.4, 12.7)):
        width = widths[index]
        if mode == "left" or mode == "fill":
            x = 2.0
        elif mode == "right":
            x = 14.0 - width
        else:
            x = 8.0 - width / 2
        g.bar(x, y - 0.9, width, 1.8, 0.9)


def format_indent(g: Glyph, more: bool = True, rtl: bool = False) -> None:
    """Full-width edge rows with an indented pair and a chevron between them."""
    g.bar(2.0, 1.8, 12.0, 1.8, 0.9)
    g.bar(2.0, 12.4, 12.0, 1.8, 0.9)
    x = 6.6 if not rtl else 2.0
    g.bar(x, 5.9, 14.0 - x - 2.0, 1.8, 0.9)
    g.bar(x, 9.9, 14.0 - x - 2.0, 1.8, 0.9)
    A.chevron(g, 0 if more else 180, 3.6 if not rtl else 12.4, 8.0, 1.9, 1.7)


# --------------------------------------------------------------------------- #
# ui widgets
# --------------------------------------------------------------------------- #


def checkbox(g: Glyph, state: str = "off") -> None:
    """The Aqua checkbox: a rounded square, with the mark cut out when set."""
    g.stroke(A.rr(2.0, 2.0, 12.0, 12.0, 3.0), STROKE + 0.2)
    if state == "on":
        g.fill(A.rr(3.2, 3.2, 9.6, 9.6, 2.2))
        g.erase(A.polyline([(5.2, 8.2), (7.2, 10.4), (10.8, 6.0)]), 1.9)
    elif state == "mixed":
        g.fill(A.rr(3.2, 3.2, 9.6, 9.6, 2.2))
        g.erase(A.polyline([(5.4, 8.0), (10.6, 8.0)]), 1.9)


def radio(g: Glyph, state: str = "off") -> None:
    """The Aqua radio: a ring with a solid bore when set."""
    g.ring(8.0, 8.0, 5.9, STROKE + 0.2)
    if state == "on":
        g.dot(8.0, 8.0, 3.1)
    elif state == "mixed":
        g.ring(8.0, 8.0, 5.9, STROKE + 0.2)
        g.bar(5.0, 7.2, 6.0, 1.6, 0.8)


def pan(g: Glyph, angle: float = 90.0) -> None:
    """A solid pull-down triangle with a slim stem: the pan handle.

    Centred a little high, because the stem swings a full half-turn around the
    triangle: hung lower, "pan-up" lost its grip off the bottom of the tile.
    """
    A.triangle(g, angle, 8.0, 8.4, 4.2)
    base = [(6.7, 2.9), (9.3, 2.9), (9.3, 6.2), (6.7, 6.2)]
    return g.solid(A.rotate(base, angle - 90.0, 8.0, 8.4), 0.6)


def focus(g: Glyph, kind: str = "windows") -> None:
    """Focus brackets around a panel."""
    g.stroke(A.rr(4.6, 3.0, 6.8, 10.0, 1.0), STROKE)
    if kind == "top-bar":
        g.bar(1.6, 1.4, 12.8, 2.6, 1.0)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        g.stroke(A.polyline([(8.0 + sx * 6.6, 8.0 + sy * 2.4),
                             (8.0 + sx * 6.6, 8.0 + sy * 6.6),
                             (8.0 + sx * 2.4, 8.0 + sy * 6.6)]), 1.6)


def list_drag_handle(g: Glyph) -> None:
    """Two columns of three dots: the drag grip."""
    for row in range(3):
        for column in range(2):
            g.dot(6.0 + column * 4.0, 4.0 + row * 4.0, 1.15)


def selection_edge(g: Glyph, start: bool = True) -> None:
    """A text caret with a handle: selection start or end."""
    x = 9.0 if start else 7.0
    g.bar(x - 1.1, 1.9, 2.2, 12.2, 1.1)
    g.solid([(4.4, 8.0), (7.6, 5.6), (7.6, 10.4)] if start
            else [(11.6, 8.0), (8.4, 5.6), (8.4, 10.4)], 0.5)


def window_button(g: Glyph, which: str = "close") -> None:
    A.traffic(g, which)


def window_maximize(g: Glyph) -> None:
    window_button(g, "maximize")


def window_minimize(g: Glyph) -> None:
    """A window folded down to its title bar: minimise."""
    g.stroke(A.rr(1.9, 2.6, 12.2, 10.8, 1.4), STROKE)
    g.bar(3.2, 10.2, 9.6, 1.8, 0.9)


def window_close(g: Glyph) -> None:
    window_button(g, "close")


def window_restore(g: Glyph) -> None:
    window_button(g, "restore")


# --------------------------------------------------------------------------- #
# places
# --------------------------------------------------------------------------- #


def place_folder(g: Glyph, emblem: str = "") -> None:
    """The Aqua tabbed folder, optionally with an emblem on the face."""
    A.folder(g, 1.7, 4.0, 12.6, 9.4)
    if not emblem:
        return
    drawer = {
        "documents": _emblem_documents,
        "download": _emblem_download,
        "music": _emblem_music,
        "pictures": _emblem_pictures,
        "videos": _emblem_videos,
        "projects": _emblem_projects,
        "publicshare": _emblem_share,
        "remote": _emblem_remote,
        "search": _emblem_search,
        "templates": _emblem_templates,
        "desktop": _emblem_desktop,
        "applications": _emblem_applications,
        "development": _emblem_development,
        "library": _emblem_library,
        "utilities": _emblem_utilities,
        "system": _emblem_system,
        "burn": _emblem_burn,
        "sites": _emblem_sites,
        "visiting": _emblem_visiting,
        "drag-accept": _emblem_drag,
    }[emblem]
    drawer(g)


def _emblem_documents(g: Glyph) -> None:
    for offset, top in ((0.0, 4.9), (1.5, 6.0)):
        g.stroke(A.rr(4.4 + offset, top, 5.6, 6.4, 0.7), 1.15)
        g.erase(A.rr(5.0 + offset, top + 0.6, 4.4, 5.2, 0.4))
        g.bar(5.0 + offset, top + 2.0, 4.4, 0.9, 0.45)
        g.bar(5.0 + offset, top + 3.6, 4.4, 0.9, 0.45)


def _emblem_download(g: Glyph) -> None:
    A.arrow(g, 90, 8.0, 7.4, 0.62)
    g.bar(4.4, 11.4, 7.2, 1.7, 0.85)


def _emblem_music(g: Glyph) -> None:
    g.bar(9.4, 5.2, 1.5, 5.2, 0.4)
    g.dot(7.4, 10.6, 2.1)
    g.stroke(A.polyline([(10.9, 5.4), (12.2, 5.9), (12.2, 7.0)]), 1.4)


def _emblem_pictures(g: Glyph) -> None:
    g.solid([(4.2, 11.2), (7.0, 7.0), (9.0, 10.0), (10.4, 8.2), (12.0, 11.2)], 0.4)
    g.dot(6.0, 6.4, 1.05)


def _emblem_videos(g: Glyph) -> None:
    A.play(g, 8.4, 8.8, 3.4)


def _emblem_projects(g: Glyph) -> None:
    """Three stacked tiles: a project shelf."""
    g.stroke(A.rr(3.4, 6.6, 5.6, 5.6, 1.0), 1.1)
    g.stroke(A.rr(4.6, 5.2, 5.6, 5.6, 1.0), 1.1)
    g.bar(5.8, 3.8, 5.6, 5.6, 1.0)
    g.hole(A.rr(6.6, 4.6, 4.0, 4.0, 0.7))


def _emblem_share(g: Glyph) -> None:
    """Three linked dots, kept clear of the folder's own outline."""
    for cx, cy in ((5.4, 9.4), (10.2, 7.0), (10.2, 11.8)):
        g.dot(cx, cy, 1.35)
    g.line((6.6, 8.8), (9.2, 7.4), 1.2)
    g.line((6.6, 10.0), (9.2, 11.4), 1.2)


def _emblem_remote(g: Glyph) -> None:
    """A cloud on the folder face: the share lives somewhere else."""
    for cx, cy, r in ((6.4, 10.0, 1.8), (8.9, 9.0, 2.4), (10.7, 10.1, 1.6)):
        g.dot(cx, cy, r)
    g.bar(5.0, 10.0, 6.6, 1.6, 0.8)


def _emblem_search(g: Glyph) -> None:
    A.magnifier(g, 7.4, 7.8, 2.9, 1.35)


def _emblem_templates(g: Glyph) -> None:
    g.stroke(A.rr(4.6, 5.6, 6.6, 6.4, 0.8), 1.2)
    for y in (7.4, 9.0, 10.6):
        g.stroke(A.polyline([(5.8, y), (10.0, y)]), 1.0)


def _emblem_desktop(g: Glyph) -> None:
    g.stroke(A.rr(3.4, 4.8, 9.2, 6.2, 0.9), 1.2)
    g.bar(7.0, 11.2, 2.0, 1.8, 0.5)
    g.bar(5.0, 12.8, 6.0, 1.2, 0.6)


def _emblem_applications(g: Glyph) -> None:
    for row in range(2):
        for column in range(2):
            g.bar(4.4 + column * 3.9, 5.6 + row * 3.9, 3.1, 3.1, 0.9)


def _emblem_development(g: Glyph) -> None:
    g.stroke(A.polyline([(6.4, 5.6), (3.6, 8.6), (6.4, 11.6)]), 1.3)
    g.stroke(A.polyline([(9.6, 5.6), (12.4, 8.6), (9.6, 11.6)]), 1.3)


def _emblem_library(g: Glyph) -> None:
    for index in range(3):
        g.bar(4.6 + index * 2.3, 5.4, 1.7, 6.6, 0.4)


def _emblem_utilities(g: Glyph) -> None:
    A.gear(g, 8.0, 8.6, 8, 3.6, 2.5, 1.1)


def _emblem_system(g: Glyph) -> None:
    for index in range(2):
        A.gear(g, 6.4 + index * 3.4, 9.4 - index * 2.2, 8, 3.0, 2.0, 0.9)


def _emblem_burn(g: Glyph) -> None:
    A.disc(g, 8.0, 8.6, 3.9, gloss=False)
    g.dot(8.0, 8.6, 0.9)


def _emblem_sites(g: Glyph) -> None:
    A.globe(g, 8.0, 8.6, 3.6)


def _emblem_visiting(g: Glyph) -> None:
    A.arrow(g, 0, 8.0, 8.6, 0.55)


def _emblem_drag(g: Glyph) -> None:
    A.arrow(g, 90, 8.0, 7.0, 0.55)
    g.bar(4.6, 11.2, 6.8, 1.6, 0.8)


def user_home(g: Glyph) -> None:
    """A house on a folder: the home directory."""
    A.folder(g, 1.7, 6.4, 12.6, 7.4)
    A.house(g)


def user_desktop(g: Glyph) -> None:
    A.folder(g, 1.7, 5.4, 12.6, 8.2)
    g.stroke(A.rr(3.6, 2.0, 8.8, 5.6, 0.8), 1.2)
    g.erase(A.polyline([(8.0, 7.6), (8.0, 9.0)]), 1.2)


def user_bookmarks(g: Glyph) -> None:
    g.solid([(3.4, 1.9), (12.6, 1.9), (12.6, 14.1), (8.0, 10.2), (3.4, 14.1)], 1.1)
    g.hole(A.rr(5.4, 3.6, 5.2, 1.4, 0.7))


def user_trash(g: Glyph) -> None:
    A.trash(g, full=False)


def user_trash_full(g: Glyph) -> None:
    A.trash(g, full=True)


def place_network_server(g: Glyph) -> None:
    """Two stacked trays with lit faces: a server."""
    for index in range(2):
        g.stroke(A.rr(2.4, 3.0 + index * 5.4, 11.2, 4.4, 0.9), STROKE)
        g.erase(A.rr(3.6, 4.2 + index * 5.4, 6.0, 1.6, 0.5))
        g.dot(12.2, 5.2 + index * 5.4, 0.8)


def place_network_workgroup(g: Glyph) -> None:
    """Two monitors on a shared bus: a workgroup."""
    g.stroke(A.rr(1.8, 2.2, 6.0, 5.0, 0.8), STROKE)
    g.stroke(A.rr(8.2, 2.2, 6.0, 5.0, 0.8), STROKE)
    g.stroke(A.polyline([(4.8, 7.2), (4.8, 9.4), (11.2, 9.4), (11.2, 7.2)]), 1.15)
    return g.stroke(A.rr(4.4, 10.4, 7.2, 4.2, 0.7), 1.15)


def place_start_here(g: Glyph) -> None:
    """A starred disc: the session start icon."""
    A.star(g, 8.0, 8.0, 6.2)


def place_folder_shared(g: Glyph) -> None:
    place_folder(g, "publicshare")


# --------------------------------------------------------------------------- #
# mimetypes
# --------------------------------------------------------------------------- #


def mime_generic(g: Glyph, kind: str = "text") -> None:
    """The generic file sheet, with a band that names the family."""
    if kind == "package":
        package_box(g, 8.0, 8.0, 5.2)
        return
    A.sheet(g, 2.8, 1.6, 9.2, 12.0)
    band = {
        "text": (4.6, 5.4, 8.0),
        "image": (4.6, 5.4, 8.0),
        "video": (4.6, 5.4, 8.0),
        "audio": (4.6, 5.4, 8.0),
        "font": (4.6, 5.4, 8.0),
    }[kind]
    x, y, w = band
    g.bar(x, y, w, 2.0, 0.6)
    if kind == "text":
        _text_rows(g, [9.4, 11.0], 4.6, 10.4)
    elif kind == "image":
        g.solid([(4.6, 11.4), (7.2, 8.6), (8.8, 10.6), (10.0, 9.2), (11.4, 11.4)], 0.4)
    elif kind == "video":
        A.play(g, 8.2, 9.6, 2.4)
    elif kind == "audio":
        g.bar(9.4, 7.6, 1.3, 4.0, 0.4)
        g.dot(7.8, 11.0, 1.7)
    else:
        g.stroke(A.polyline([(5.4, 11.2), (6.4, 8.4), (8.0, 10.4), (9.6, 7.6),
                             (11.0, 11.2)]), 1.3)


def mime_office(g: Glyph, kind: str = "document") -> None:
    """The office family: a sheet with a marker band and the family glyph."""
    A.sheet(g, 2.8, 1.6, 9.2, 12.0)
    if kind == "spreadsheet":
        g.bar(4.8, 5.2, 7.4, 1.8, 0.5)
        for x in (4.8, 7.2, 9.6):
            g.erase(A.polyline([(x, 7.4), (x, 11.6)]), 0.9)
        for y in (7.4, 9.2, 11.0, 12.0):
            g.erase(A.polyline([(4.8, y), (11.0, y)]), 0.9)
        return
    if kind == "presentation":
        g.bar(4.4, 5.0, 7.2, 5.0, 0.6)
        g.erase(A.polyline([(8.0, 10.0), (8.0, 11.6)]), 1.0)
        g.erase(A.polyline([(5.6, 12.4), (10.4, 12.4)]), 1.0)
        return
    if kind == "drawing":
        g.solid([(5.0, 11.8), (5.6, 10.0), (10.4, 5.2), (12.0, 6.8), (7.2, 11.6)], 0.4)
        g.erase(A.polyline([(9.8, 5.8), (11.4, 7.4)]), 1.0)
        return
    if kind == "calendar":
        g.bar(4.8, 5.2, 7.2, 1.6, 0.5)
        for y in (8.4, 10.0, 11.6):
            g.erase(A.polyline([(4.8, y), (12.0, y)]), 0.9)
        return
    if kind == "address-book":
        A.person(g, 8.0, 7.2, 1.6, 1.2, 3.4)
        g.bar(5.4, 11.0, 5.2, 1.2, 0.6)
        return
    _text_rows(g, [5.4, 7.2, 9.0, 10.8], 4.8, 10.6)


def mime_special(g: Glyph, kind: str = "executable") -> None:
    """Certificates, firmware, addons, shared libraries and appliances."""
    if kind == "certificate":
        A.sheet(g, 2.8, 1.6, 9.2, 9.4)
        _text_rows(g, [4.6, 6.2], 4.8, 10.6)
        g.ring(8.0, 11.4, 2.4, 1.3)
        return g.solid([(9.6, 12.8), (11.0, 14.4), (10.2, 13.0)], 0.3)
    if kind == "executable":
        g.stroke(A.rr(2.0, 2.4, 12.0, 11.2, 1.4), STROKE)
        g.bar(2.0, 2.4, 12.0, 2.6, 1.2)
        g.stroke(A.polyline([(5.6, 8.4), (3.8, 10.2), (5.6, 12.0)]), 1.3)
        return g.stroke(A.polyline([(8.4, 12.2), (10.6, 8.2)]), 1.3)
    if kind == "sharedlib":
        for index in range(2):
            g.stroke(A.rr(1.9, 3.0 + index * 5.4, 12.2, 4.4, 0.9), STROKE)
            g.erase(A.rr(3.4, 4.0 + index * 5.4, 3.6, 1.5, 0.5))
        return None
    if kind == "firmware":
        A.chip(g, 8.0, 8.0, 7.0)
        return None
    if kind == "addon":
        g.bar(2.6, 2.6, 10.8, 10.8, 1.8)
        g.erase(A.polyline([(5.4, 8.0), (10.6, 8.0)]), 1.6)
        g.erase(A.polyline([(8.0, 5.4), (8.0, 10.6)]), 1.6)
        return None
    if kind == "appliance":
        g.stroke(A.rr(1.9, 4.4, 12.2, 8.4, 1.4), STROKE)
        g.erase(A.rr(3.2, 5.6, 6.0, 3.0, 0.6))
        return g.bar(4.6, 10.4, 2.0, 1.4, 0.5)
    if kind == "rss":
        # A feed is anchored in its corner, not centred: the arcs have to open
        # away from the dot, and the dot sits at the foot of the two rings.
        g.dot(3.0, 13.0, 1.4)
        g.stroke(A.arc(3.0, 13.0, 4.2, 270, 360), 1.7)
        return g.stroke(A.arc(3.0, 13.0, 8.2, 270, 360), 1.7)
    return None


def mime_inode(g: Glyph) -> None:
    A.folder(g, 1.7, 4.2, 12.6, 9.0)


def mime_font(g: Glyph) -> None:
    """A framed A: the generic font file."""
    g.stroke(A.rr(2.0, 2.0, 12.0, 12.0, 1.4), STROKE)
    g.stroke(A.polyline([(4.6, 11.8), (8.0, 4.4), (11.4, 11.8)]), STROKE)
    return g.line((6.0, 9.0), (10.0, 9.0), STROKE)
