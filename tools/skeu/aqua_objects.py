"""Aqua-style glyphs for objects: devices, places, status, weather and faces.

Same rules as :mod:`skeu.aqua_glyphs` --- every shape is built from the motifs
in :mod:`skeu.aqua` so the whole symbolic layer shares one weight, one corner
radius and one light direction.
"""

from __future__ import annotations

import math

from . import aqua as A
from . import aqua_glyphs as G
from .aqua import HAIRLINE, STROKE, Glyph, Point

# --------------------------------------------------------------------------- #
# hardware
# --------------------------------------------------------------------------- #


def chip(g: Glyph, cx: float = 8.0, cy: float = 8.0, size: float = 8.0) -> None:
    """A processor: a square die with pins on all four sides."""
    half = size / 2
    g.stroke(A.rr(cx - half, cy - half, size, size, 1.0), STROKE)
    g.bar(cx - half + 2.0, cy - half + 2.0, size - 4.0, size - 4.0, 0.6)
    for index in range(3):
        offset = -half / 2 + index * half / 2
        g.bar(cx + offset - 0.5, cy - half - 1.2, 1.0, 1.4, 0.3)
        g.bar(cx + offset - 0.5, cy + half - 0.2, 1.0, 1.4, 0.3)
        g.bar(cx - half - 1.2, cy + offset - 0.5, 1.4, 1.0, 0.3)
        g.bar(cx + half - 0.2, cy + offset - 0.5, 1.4, 1.0, 0.3)


def motherboard(g: Glyph) -> None:
    g.stroke(A.rr(1.8, 2.4, 12.4, 11.2, 1.0), STROKE)
    chip(g, 6.0, 6.4, 4.6)
    g.bar(9.6, 9.4, 3.6, 1.2, 0.4)
    g.bar(9.6, 11.4, 2.4, 1.2, 0.4)
    g.erase(A.polyline([(3.2, 10.4), (3.2, 12.2), (8.0, 12.2)]), 1.0)


def ram(g: Glyph) -> None:
    """A memory stick with cut contacts and two chips."""
    g.stroke(A.rr(1.7, 4.6, 12.6, 6.8, 0.9), STROKE)
    g.bar(3.0, 6.0, 4.0, 4.0, 0.5)
    g.bar(8.4, 6.0, 4.4, 4.0, 0.5)
    for index in range(4):
        g.erase(A.polyline([(3.4 + index * 1.6, 11.4), (3.4 + index * 1.6, 12.4)]), 1.0)


def graphics_card(g: Glyph) -> None:
    g.stroke(A.rr(1.8, 3.4, 12.4, 8.4, 0.9), STROKE)
    g.dot(5.0, 6.4, 1.9)
    g.erase(A.circ(5.0, 6.4, 0.8))
    for index in range(3):
        g.erase(A.polyline([(10.0, 5.4 + index * 1.4), (12.6, 5.4 + index * 1.4)]), 1.0)
    g.bar(3.4, 10.6, 6.0, 1.4, 0.4)
    return None


def server(g: Glyph) -> None:
    for index in range(3):
        y = 2.2 + index * 4.0
        g.stroke(A.rr(1.9, y, 12.2, 3.4, 0.8), STROKE)
        g.bar(3.2, y + 1.0, 5.0, 1.3, 0.4)
        g.dot(12.0, y + 1.7, 0.75)


def computer(g: Glyph) -> None:
    A.display(g, 1.7, 2.8, 12.6, 8.2)


def laptop(g: Glyph) -> None:
    """A clamshell: a lid and a splayed base."""
    g.stroke(A.rr(2.4, 2.4, 11.2, 7.4, 1.1), STROKE)
    g.erase(A.rr(3.4, 3.3, 9.2, 5.6, 0.6))
    g.stroke(A.polyline([(1.4, 12.0), (14.6, 12.0), (13.2, 14.2), (2.8, 14.2),
                         (1.4, 12.0)]), STROKE)


def projector(g: Glyph) -> None:
    g.stroke(A.rr(2.2, 5.4, 11.6, 6.2, 1.2), STROKE)
    g.ring(6.0, 8.5, 2.0, 1.3)
    g.erase(A.rr(9.6, 7.0, 2.8, 1.4, 0.5))
    g.stroke(A.polyline([(6.0, 5.4), (6.0, 4.0)]), 1.2)
    return g.bar(7.6, 3.2, 1.8, 1.2, 0.3)


def tv(g: Glyph) -> None:
    g.stroke(A.rr(1.7, 3.4, 12.6, 8.6, 1.6), STROKE)
    g.erase(A.rr(3.0, 4.7, 10.0, 6.0, 0.9))
    g.stroke(A.polyline([(5.0, 14.0), (11.0, 14.0)]), 1.3)
    return g.stroke(A.polyline([(8.0, 12.0), (8.0, 14.0)]), 1.3)


def joined_displays(g: Glyph) -> None:
    g.stroke(A.rr(1.7, 3.4, 6.2, 7.0, 1.0), STROKE)
    g.stroke(A.rr(8.1, 3.4, 6.2, 7.0, 1.0), STROKE)
    g.bar(7.0, 9.0, 2.0, 1.6, 0.4)
    g.stroke(A.polyline([(2.0, 14.0), (14.0, 14.0)]), 1.3)


def single_display(g: Glyph) -> None:
    A.display(g, 2.6, 2.6, 10.8, 8.2)


def drive_harddisk(g: Glyph, **kw) -> None:
    A.drive(g, **kw)


def drive_removable(g: Glyph) -> None:
    """A drive bay with its cartridge half out: removable media."""
    A.drive(g, 1.7, 4.4, 12.6, 7.0, vents=False)
    g.erase(A.rr(3.0, 5.4, 5.6, 5.0, 0.6))
    g.bar(4.2, 6.4, 3.4, 1.3, 0.5)
    g.bar(4.2, 8.4, 3.4, 1.3, 0.5)


def drive_solid_state(g: Glyph) -> None:
    """A solid-state drive: a drive case with a lightning mark cut into the face."""
    A.drive(g, vents=False)
    bolt = [(10.4, 5.0), (6.4, 10.2), (8.4, 10.2), (7.4, 12.4), (11.6, 7.4),
            (9.6, 7.4)]
    g.hole(A.rpoly(bolt, 0.25, True))


def drive_multidisk(g: Glyph) -> None:
    A.drive(g, 1.7, 2.4, 12.6, 4.6, vents=False)
    A.drive(g, 1.7, 9.0, 12.6, 4.6, vents=False)


def drive_optical(g: Glyph) -> None:
    g.stroke(A.rr(1.9, 3.2, 12.2, 9.2, 1.4), STROKE)
    g.hole(A.rr(3.0, 4.4, 10.0, 1.4, 0.6))
    return A.disc(g, 8.0, 8.6, 3.4, gloss=False)


def optical_disc(g: Glyph, label: str = "") -> None:
    """An optical disc; ``audio`` adds the note that tells it from data."""
    A.disc(g, 8.0, 8.0, 6.2)
    if label == "audio":
        g.bar(9.4, 3.8, 1.3, 4.4, 0.4)
        g.dot(8.4, 8.2, 1.5)
        g.stroke(A.polyline([(10.7, 4.0), (11.8, 4.5), (11.8, 5.6)]), 1.2)
    elif label:
        g.erase(A.rr(6.1, 6.4, 3.8, 2.2, 0.6))
        g.bar(6.1, 6.4, 3.8, 2.2, 0.6)


def floppy(g: Glyph, width: float = STROKE) -> None:
    g.stroke(A.rr(2.2, 2.2, 11.6, 11.6, 1.9), width)
    g.bar(4.6, 2.6, 6.8, 4.0, 0.5)
    g.erase(A.rr(6.1, 2.9, 2.2, 2.5, 0.3))
    g.stroke(A.rr(4.4, 9.0, 7.2, 4.4, 0.7), HAIRLINE + 0.35)
    g.erase(A.rr(6.4, 10.4, 3.2, 1.2, 0.4))


def memory_card(g: Glyph, kind: str = "sd") -> None:
    if kind == "sim":
        g.stroke(A.rr(3.4, 2.0, 9.2, 12.0, 1.8), STROKE)
        chip(g, 8.0, 8.6, 4.4)
        return
    A.card(g)
    if kind == "smart":
        for index in range(3):
            g.erase(A.polyline([(6.6 + index * 1.8, 9.4), (6.6 + index * 1.8, 11.8)]),
                    1.0)


def tape(g: Glyph) -> None:
    g.stroke(A.rr(1.9, 4.0, 12.2, 8.2, 1.3), STROKE)
    g.ring(5.8, 8.1, 2.1, 1.25)
    g.ring(10.2, 8.1, 2.1, 1.25)
    g.bar(6.6, 10.4, 2.8, 1.0, 0.5)


def zip_disk(g: Glyph) -> None:
    g.ring(8.0, 8.0, 6.2, STROKE)
    g.ring(8.0, 8.0, 2.2, 1.2)
    g.stroke(A.arc(8.0, 8.0, 4.4, 200, 340), 1.1)
    g.bar(6.4, 2.2, 3.2, 1.4, 0.6)


def removable_media(g: Glyph) -> None:
    """A USB stick: a body, a cap line and a connector."""
    g.stroke(A.rr(2.2, 4.6, 11.6, 7.0, 1.3), STROKE)
    g.bar(3.4, 5.8, 4.0, 4.6, 0.5)
    g.erase(A.polyline([(9.0, 5.4), (9.0, 10.8)]), 1.3)
    return g.bar(10.4, 6.8, 2.4, 2.6, 0.4)


def usb_stick(g: Glyph) -> None:
    g.stroke(A.rr(2.4, 3.4, 8.8, 8.4, 1.2), STROKE)
    g.bar(3.8, 4.8, 4.0, 5.6, 0.4)
    g.bar(10.8, 5.6, 2.8, 4.0, 0.5)
    g.erase(A.polyline([(11.6, 7.0), (13.4, 7.0)]), 1.1)
    g.erase(A.polyline([(11.6, 8.2), (13.4, 8.2)]), 1.1)


def keyboard(g: Glyph) -> None:
    A.keyboard(g)


def mouse(g: Glyph) -> None:
    A.mouse(g)


def touchpad(g: Glyph) -> None:
    """A trackpad: a slab with a click strip along the bottom."""
    g.stroke(A.rr(2.2, 3.4, 11.6, 9.2, 1.6), STROKE)
    g.stroke(A.rr(3.2, 4.4, 9.6, 4.6, 0.8), HAIRLINE + 0.3)
    g.bar(3.2, 10.2, 9.6, 1.4, 0.7)


def graphics_tablet(g: Glyph) -> None:
    g.stroke(A.rr(1.9, 2.6, 12.2, 10.8, 1.2), STROKE)
    g.bar(10.4, 3.8, 2.6, 8.4, 0.7)
    g.erase(A.polyline([(11.7, 5.4), (11.7, 10.4)]), 1.0)
    g.solid([(3.4, 9.4), (7.6, 6.0), (7.6, 11.6), (3.4, 12.4)], 0.6)


def dialpad(g: Glyph) -> None:
    for row in range(3):
        for column in range(3):
            g.dot(3.6 + column * 4.4, 3.6 + row * 4.4, 1.5)


def gamepad(g: Glyph) -> None:
    """A pad: a rounded wing-to-wing body with a d-pad and one button."""
    g.stroke(A.rr(1.7, 5.2, 12.6, 5.8, 2.8), STROKE)
    A.cross(g, 5.2, 8.1, 1.6, 1.25)
    g.dot(10.9, 7.2, 0.95)
    g.dot(12.4, 9.2, 0.95)


def rollout_phone(g: Glyph) -> None:
    """A candybar handset with a small aerial: the "old phone"."""
    g.stroke(A.rr(4.0, 3.4, 8.0, 10.6, 1.5), STROKE)
    g.erase(A.rr(5.2, 5.0, 5.6, 4.4, 0.5))
    for row in range(2):
        for column in range(3):
            g.dot(6.2 + column * 1.8, 10.6 + row * 1.6, 0.5)
    return g.stroke(A.polyline([(11.4, 3.4), (12.6, 2.0)]), 1.4)


def pda(g: Glyph) -> None:
    g.stroke(A.rr(3.2, 2.4, 9.6, 11.6, 1.4), STROKE)
    g.erase(A.rr(4.4, 3.6, 7.2, 6.0, 0.6))
    g.bar(5.4, 11.0, 3.2, 1.4, 0.5)


def watch(g: Glyph) -> None:
    g.stroke(A.rr(4.8, 4.4, 6.4, 7.2, 1.8), STROKE)
    g.bar(6.2, 1.4, 3.6, 3.0, 0.9)
    g.bar(6.2, 11.6, 3.6, 3.0, 0.9)
    g.erase(A.polyline([(8.0, 6.4), (8.0, 8.4), (9.6, 8.9)]), 1.1)


def modem(g: Glyph) -> None:
    g.stroke(A.rr(2.0, 7.0, 12.0, 6.2, 1.1), STROKE)
    g.erase(A.rr(3.4, 8.2, 4.6, 1.2, 0.4))
    g.erase(A.rr(3.4, 10.2, 3.0, 1.2, 0.4))
    g.stroke(A.polyline([(10.4, 7.0), (10.4, 3.4)]), 1.3)
    return g.dot(10.4, 2.6, 1.0)


def ac_adapter(g: Glyph) -> None:
    """A mains adapter: brick, two pins and the cable."""
    g.stroke(A.rr(1.9, 5.2, 8.8, 6.6, 1.3), STROKE)
    g.bar(3.3, 6.6, 4.0, 3.8, 0.5)
    for x in (4.6, 7.8):
        g.bar(x, 2.4, 1.5, 3.2, 0.7)
    g.stroke(A.polyline([(10.7, 8.5), (12.6, 8.5)]), 1.4)
    g.bar(12.4, 7.4, 1.8, 2.2, 0.5)


def thunderbolt(g: Glyph, acquiring: bool = False) -> None:
    g.solid([(9.4, 1.4), (4.6, 8.8), (7.5, 8.8), (6.6, 14.6), (11.4, 7.2),
             (8.5, 7.2)], 0.5)
    if acquiring:
        for index in range(2):
            g.stroke(A.arc(11.9, 4.4, 1.2 + index * 1.1, 20, 250), 1.0)


def network_wired(g: Glyph) -> None:
    """An RJ45 plug on a short cable."""
    g.stroke(A.rr(3.6, 5.6, 8.8, 6.6, 1.0), STROKE)
    g.erase(A.rr(5.0, 7.0, 6.0, 3.4, 0.4))
    for index in range(4):
        g.bar(5.4 + index * 1.5, 7.6, 0.9, 2.2, 0.2)
    g.stroke(A.polyline([(8.0, 5.6), (8.0, 3.2), (11.0, 2.0)]), 1.4)


def network_wireless(g: Glyph) -> None:
    A.wifi(g, 3)


def network_cellular(g: Glyph) -> None:
    """A mast with a signal ladder."""
    A.bars(g, (4.2, 6.0, 7.8, 9.6), x=2.0, bottom=13.4, width=2.2, gap=2.7)
    g.dot(13.4, 5.0, 0.9)


def printer(g: Glyph) -> None:
    A.printer(g)


def printer_network(g: Glyph) -> None:
    """A printer with a signal badge: shared on the wire."""
    A.printer(g, 7.6, 7.6)
    G._badge(g, 11.9, 11.9, 2.8)
    g.hole(A.circ(10.7, 12.7, 0.5))
    for index in range(2):
        g.erase(A.arc(10.7, 12.7, 1.4 + index * 1.3, 270, 360), 0.85)


def scanner(g: Glyph) -> None:
    g.stroke(A.rr(1.9, 6.4, 12.2, 5.4, 1.0), STROKE)
    g.stroke(A.rr(4.6, 2.2, 7.0, 3.4, 0.6), STROKE)
    g.bar(3.4, 8.2, 6.4, 1.2, 0.5)
    g.bar(10.4, 8.2, 2.2, 1.2, 0.5)
    g.solid([(11.2, 9.6), (14.0, 9.6), (12.6, 13.0)], 0.4)


def audio_card(g: Glyph) -> None:
    g.stroke(A.rr(1.8, 3.0, 12.4, 10.0, 1.0), STROKE)
    g.ring(6.0, 8.0, 2.4, 1.3)
    g.bar(10.2, 5.4, 2.6, 1.4, 0.4)
    g.bar(10.2, 9.2, 2.6, 1.4, 0.4)
    return None


def speakers(g: Glyph) -> None:
    g.stroke(A.rr(4.0, 1.8, 8.0, 12.4, 1.4), STROKE)
    g.ring(8.0, 5.4, 1.7, 1.15)
    g.ring(8.0, 10.6, 2.4, 1.15)


def headphones(g: Glyph) -> None:
    A.headphones(g)


def headset(g: Glyph) -> None:
    A.headphones(g)
    g.stroke(A.polyline([(13.2, 11.6), (9.6, 12.4)]), 1.2)
    g.stroke(A.arc(8.0, 12.0, 1.8, 200, 340), 1.1)


def microphone(g: Glyph) -> None:
    A.microphone(g)


def webcam(g: Glyph) -> None:
    g.stroke(A.rr(3.2, 3.0, 9.6, 7.6, 3.4), STROKE)
    g.ring(8.0, 6.8, 2.0, 1.3)
    g.bar(6.4, 11.4, 3.2, 1.4, 0.5)
    return g.bar(3.6, 12.6, 8.8, 1.6, 0.8)


def camera_photo(g: Glyph) -> None:
    A.camera(g)


def camera_disabled(g: Glyph) -> None:
    """A camera with the lens barred: the camera is off-limits."""
    A.camera(g)
    A.slash(g)


def camera_video(g: Glyph) -> None:
    A.camera(g, video=True)


def player(g: Glyph) -> None:
    g.stroke(A.rr(3.0, 1.8, 10.0, 12.4, 1.5), STROKE)
    g.bar(4.5, 3.5, 7.0, 6.4, 0.6)
    g.hole(A.circ(8.0, 12.2, 1.3))
    g.ring(8.0, 12.2, 1.3, 1.0)


def ipod_touch(g: Glyph) -> None:
    A.phone(g, 8.0, 8.2, 6.8, 12.0)


def iphone(g: Glyph) -> None:
    A.phone(g, 8.0, 8.2, 6.8, 12.0)


def ipad(g: Glyph) -> None:
    A.tablet(g, 8.0, 8.0, 9.6, 12.4)


def ebook_reader(g: Glyph) -> None:
    A.tablet(g, 8.0, 8.0, 8.8, 12.4)


def ups(g: Glyph) -> None:
    g.stroke(A.rr(2.2, 3.4, 11.6, 10.2, 1.2), STROKE)
    g.stroke(A.arc(8.0, 7.6, 2.6, 200, 160), 1.3)
    g.bar(7.2, 5.4, 1.6, 2.4, 0.5)
    A.plus(g, 8.0, 11.6, 1.8, 1.2)


def colorimeter(g: Glyph) -> None:
    """A colour meter: shell, optic lens and a readout."""
    g.stroke(A.rr(1.8, 3.9, 12.4, 8.2, 3.0), STROKE)
    g.ring(6.0, 8.0, 2.3, 1.25)
    g.dot(6.0, 8.0, 0.85)
    g.bar(9.8, 6.2, 2.9, 1.25, 0.6)
    g.bar(9.8, 8.7, 2.9, 1.25, 0.6)


def fingerprint(g: Glyph) -> None:
    """Nested ridges: the Aqua biometric mark.

    Circular arcs off a common centre are a wireless signal, not a print.  The
    ridges have to be tall, nested and anchored on a flat foot, with a core
    running down the middle, to read as a fingertip at any size.
    """
    g.dot(8.0, 10.4, 0.85)
    for index, (rx, ry) in enumerate(((1.8, 3.4), (3.3, 5.6), (4.8, 7.8))):
        foot = 11.9 - index * 0.55
        g.stroke(f"M{8.0 - rx} {foot}A{rx} {ry} 0 0 1 {8.0 + rx} {foot}",
                 STROKE - index * 0.3)
    # One ridge breaks early on the right, the way a print frays.
    g.stroke(f"M12.4 8.6A4.4 6.6 0 0 1 13.2 11.4", 1.0)


def face_id(g: Glyph) -> None:
    """A face scan: corner brackets around two eyes and a mouth."""
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        g.stroke(A.polyline([(8.0 + sx * 6.2, 8.0 + sy * 2.6),
                             (8.0 + sx * 6.2, 8.0 + sy * 6.2),
                             (8.0 + sx * 2.6, 8.0 + sy * 6.2)]), 1.4)
    g.dot(5.8, 6.6, 0.95)
    g.dot(10.2, 6.6, 0.95)
    return g.stroke(A.arc(8.0, 7.6, 2.4, 30, 150), 1.2)


def smartcard(g: Glyph) -> None:
    g.stroke(A.rr(2.0, 3.4, 12.0, 9.2, 1.4), STROKE)
    chip(g, 5.4, 7.4, 3.4)
    g.bar(9.4, 6.4, 3.0, 1.1, 0.4)
    return g.bar(9.4, 8.4, 2.2, 1.1, 0.4)


def sim(g: Glyph) -> None:
    memory_card(g, kind="sim")


def thunderbolt_cable(g: Glyph) -> None:
    thunderbolt(g)


# --------------------------------------------------------------------------- #
# status: batteries, signals, sound
# --------------------------------------------------------------------------- #


def battery_status(g: Glyph, level: float = 1.0, bolt: bool = False,
                   plug: bool = False, charged: bool = False) -> None:
    """A battery at LEVEL; charging cuts a bolt out of the fill, or sits in the
    empty cell at low levels so the mark never disappears into the fill."""
    A.battery(g, level)
    if bolt:
        shape = A.rpoly([(8.6, 4.2), (5.6, 8.8), (7.6, 8.8), (6.8, 12.6),
                         (10.2, 7.4), (8.2, 7.4)], 0.25, True)
        if level >= 0.5:
            g.hole(shape)
        else:
            g.fill(shape)
    if plug:
        g.stroke(A.polyline([(8.0, 3.4), (8.0, 1.8)]), 1.3)
    if charged:
        # A plug over the terminal: full, and still on the cable.  Without this
        # the icon was byte-for-byte the charging one.
        g.bar(5.6, 1.5, 4.8, 1.5, 0.5)
        g.stroke(A.polyline([(8.0, 3.0), (8.0, 3.9)]), 1.2)


def battery_missing(g: Glyph) -> None:
    A.battery(g, 0.0)
    g.erase(A.polyline([(2.6, 12.6), (13.4, 3.4)]), 1.8)
    g.stroke(A.polyline([(2.6, 12.6), (13.4, 3.4)]), STROKE)


def battery_action(g: Glyph) -> None:
    """A battery with a bolt: action is needed."""
    A.battery(g, 0.22)
    bolt = [(9.4, 4.4), (6.4, 9.0), (8.2, 9.0), (7.4, 12.4), (10.6, 7.4), (8.6, 7.4)]
    g.hole(A.rpoly(bolt, 0.2, True))


def volume(g: Glyph, level: str = "medium", muted: bool = False) -> None:
    waves = {"muted": 0, "low": 1, "medium": 2, "high": 3, "overamplified": 4}[level]
    A.speaker(g, waves=waves, muted=muted or level == "muted")


def microphone_sensitivity(g: Glyph, level: str = "medium") -> None:
    A.microphone(g)
    waves = {"muted": 0, "low": 1, "medium": 2, "high": 3}[level]
    for index in range(waves):
        g.stroke(A.arc(8.0, 6.2, 3.0 + index * 1.3, 20, 160), 1.1)
    if level == "muted":
        g.erase(A.polyline([(3.4, 12.6), (12.6, 3.4)]), 1.9)
        g.stroke(A.polyline([(3.4, 12.6), (12.6, 3.4)]), STROKE)


def microphone_disabled(g: Glyph) -> None:
    microphone_sensitivity(g, "muted")


def signal_bars(g: Glyph, strength: int, total: int = 5) -> None:
    """A ladder of bars, ``strength`` of them solid."""
    heights = [3.0 + index * 2.2 for index in range(total)]
    for index, height in enumerate(heights):
        if index < strength:
            g.bar(1.8 + index * 2.5, 13.4 - height, 1.9, height, 0.5)
        else:
            g.hole(A.rr(1.8 + index * 2.5, 13.4 - height, 1.9, height, 0.5))
            g.stroke(A.rr(1.8 + index * 2.5, 13.4 - height, 1.9, height, 0.5), 1.0)


def wifi_signal(g: Glyph, strength: int) -> None:
    g.dot(8.0, 11.8, 1.1)
    for index in range(strength):
        g.stroke(A.arc(8.0, 11.8, 2.8 + index * 2.0, 214, 326), STROKE)
    for index in range(3 - strength):
        radius = 2.8 + (strength + index) * 2.0
        g.stroke(A.arc(8.0, 11.8, radius, 214, 326), 0.9)


def wifi_badge(g: Glyph, badge: str = "") -> None:
    """Wireless arcs with a state badge in the corner."""
    wifi_signal(g, 3)
    if not badge:
        return
    if badge == "acquiring":
        # Three dots on the plate: weak signal and a connection in progress
        # were the same drawing, which is a lie to anyone watching the trayloop.
        G._badge(g, 12.0, 12.0, 2.7, 1.0)
        for offset in (-1.2, 0.0, 1.2):
            g.hole(A.circ(12.0 + offset, 12.0, 0.55))
        return
    G._badge(g, 12.0, 12.0, 2.7, 1.0)
    if badge == "lock":
        g.erase(A.rr(10.9, 11.6, 2.3, 2.0, 0.5))
        g.erase(A.arc(12.05, 11.6, 0.9, 180, 360), 0.75)
        g.stroke(A.arc(12.05, 11.6, 0.9, 180, 360), 0.75)
    elif badge == "off":
        G._cut_cross(g, 12.0, 12.0, 1.4, 1.2)
    elif badge == "hotspot":
        G._cut_plus(g, 12.0, 12.0, 1.3, 1.2)
    elif badge == "warn":
        g.solid([(12.0, 10.2), (13.9, 13.6), (10.1, 13.6)], 0.5)
        g.erase(A.rr(11.5, 11.8, 1.0, 1.2, 0.3))
    elif badge == "question":
        g.hole(A.circ(12.0, 11.5, 0.65))
        g.erase(A.arc(12.0, 11.0, 0.9, 200, 20), 0.9)
        g.erase(A.polyline([(12.0, 11.9), (12.0, 12.4)]), 0.9)


def cellular_signal(g: Glyph, strength: int, generation: str = "",
                    badge: str = "") -> None:
    signal_bars(g, strength)
    if generation:
        text = generation
        g.erase(A.rr(8.4, 1.6, 6.0, 3.0, 1.0))
        g.bar(8.4, 1.6, 6.0, 3.0, 1.0)
        if text == "2G":
            _digit(g, 9.4, 2.4, "2")
            _digit(g, 11.0, 2.4, "G", width=2.0)
        elif text == "3G":
            _digit(g, 9.4, 2.4, "3")
            _digit(g, 11.0, 2.4, "G", width=2.0)
        elif text == "4G":
            _digit(g, 9.4, 2.4, "4")
            _digit(g, 11.0, 2.4, "G", width=2.0)
        elif text == "5G":
            _digit(g, 9.4, 2.4, "5")
            _digit(g, 11.0, 2.4, "G", width=2.0)
        elif text == "E":
            _digit(g, 10.2, 2.4, "E", width=2.2)
        elif text == "G":
            _digit(g, 10.2, 2.4, "G", width=2.2)
        elif text == "H":
            _digit(g, 10.2, 2.4, "H", width=2.2)
    if badge == "acquiring":
        # A dashed ring tight around the bars; at 7.6 units of radius it ran
        # out past the tile on both sides.
        g.stroke(A.arc(8.0, 12.8, 6.2, 196, 344), 0.9)
        return
    if badge:
        G._badge(g, 12.2, 12.4, 2.6, 1.0)
        if badge == "off":
            G._cut_cross(g, 12.2, 12.4, 1.3, 1.15)
        elif badge == "warn":
            g.solid([(12.2, 10.7), (14.0, 14.0), (10.4, 14.0)], 0.5)
        elif badge == "lock":
            g.erase(A.rr(11.1, 12.2, 2.2, 1.9, 0.5))
            g.stroke(A.arc(12.2, 12.2, 0.85, 180, 360), 0.7)


#: A five-by-seven stroke font, just enough for the cellular counters.
_DIGITS: dict[str, list[list[str]]] = {
    "2": [["a", "b", "c"], ["c"], ["a", "b", "c"], ["d"], ["a", "b", "c"]],
    "3": [["a", "b", "c"], ["c"], ["a", "b", "c"], ["c"], ["a", "b", "c"]],
    "4": [["a", "d", "c"], ["a", "d", "c"], ["a", "b", "c"], ["c"], ["c"]],
    "5": [["a", "b", "c"], ["d"], ["a", "b", "c"], ["c"], ["a", "b", "c"]],
    "E": [["a", "b", "c"], ["d"], ["a", "b"], ["d"], ["a", "b", "c"]],
    "G": [["a", "b", "c"], ["d"], ["a", "d", "c"], ["c"], ["a", "b", "c"]],
    "H": [["a", "d"], ["a", "d"], ["a", "b", "c"], ["c"], ["c"]],
}


def _digit(g: Glyph, x: float, y: float, char: str, width: float = 0.9) -> None:
    """Draw one letter of the counter font in a 2.2 x 3.4 box."""
    rows = _DIGITS.get(char)
    if not rows:
        return
    height = 3.4
    step = height / 4.0
    x1 = x + 2.2
    for row, sides in enumerate(rows):
        yy = y + row * step
        for side in sides:
            if side == "a":
                g.bar(x, yy, 2.2, 0.55, 0.2)
            elif side == "b":
                g.bar(x, yy + step - 0.6, 2.2, 0.55, 0.2)
            elif side == "c":
                g.bar(x1 - 0.55, yy, 0.55, step + 0.15, 0.2)
            elif side == "d":
                g.bar(x, yy, 0.55, step + 0.15, 0.2)


def network_state(g: Glyph, kind: str = "wired", state: str = "") -> None:
    """The wired / VPN / generic network marks used by the status context.

    ``state`` differentiates the five VPN names, which used to share one
    drawing: acquiring spins, disabled is barred, disconnected is unlocked.
    """
    if kind == "wired":
        network_wired(g)
        if state == "acquiring":
            for index in range(2):
                g.stroke(A.arc(11.7, 12.0, 1.3 + index * 1.2, 180, 330), 1.0)
        elif state == "disconnected":
            A.slash(g)
    elif kind == "vpn":
        if state == "acquiring":
            # A dashed shackle: the tunnel is connecting, not connected.  A
            # spinner in the corner only collided with the lock's own arch.
            g.bar(3.5, 8.4, 9.0, 6.6, 1.7)
            g.hole(A.rr(6.5, 11.6, 3.0, 1.4, 0.7))
            for angle in (198, 228, 258, 288):
                turn = math.radians(angle)
                g.dot(8.0 + 2.9 * math.cos(turn), 6.6 + 2.9 * math.sin(turn), 0.8)
            return
        A.lock(g, 8.0, 9.6, open=state == "disconnected")
        if state == "disabled":
            A.slash(g)
        elif state == "no-route":
            G._badge(g, 12.4, 12.4, 2.6)
            G._cut_cross(g, 12.4, 12.4, 1.35, 1.15)
    elif kind == "error":
        # A cut only rubs out ink that is already there, and a ring is a
        # stroke: the cross has to be *drawn*, or the icon is a bare circle.
        g.ring(8.0, 8.0, 5.6, STROKE)
        A.cross(g, 8.0, 8.0, 2.4, 1.7)
    elif kind == "offline":
        g.ring(8.0, 8.0, 5.6, STROKE)
        g.erase(A.polyline([(3.0, 13.0), (13.0, 3.0)]), 2.2)
        g.stroke(A.polyline([(3.0, 13.0), (13.0, 3.0)]), STROKE)
    elif kind == "idle":
        g.ring(8.0, 8.0, 5.6, STROKE)
        g.dot(8.0, 8.0, 2.2)
    elif kind == "transmit":
        A.arrow(g, 270, 8.0, 7.0, 0.72)
        g.bar(3.4, 12.6, 9.2, 1.6, 0.8)
    elif kind == "receive":
        A.arrow(g, 90, 8.0, 9.0, 0.72)
        g.bar(3.4, 1.8, 9.2, 1.6, 0.8)
    elif kind == "transmit-receive":
        A.arrow(g, 270, 5.4, 7.4, 0.62)
        A.arrow(g, 90, 10.6, 8.6, 0.62)
    elif kind == "no-route":
        G._badge(g, 8.0, 8.0, 6.2, 0.0)
        g.hole(A.circ(8.0, 8.0, 4.4))
        A.cross(g, 8.0, 8.0, 1.8, 1.2)


def bluetooth_state(g: Glyph, kind: str = "active") -> None:
    A.bluetooth(g, 8.0, 7.6)
    if kind == "active":
        g.dot(8.0, 13.6, 1.0)
    elif kind == "disabled":
        g.erase(A.polyline([(2.6, 13.4), (13.4, 2.6)]), 2.0)
        g.stroke(A.polyline([(2.6, 13.4), (13.4, 2.6)]), STROKE)
    elif kind == "acquiring":
        for index in range(2):
            g.stroke(A.arc(8.0, 7.6, 4.2 + index * 1.8, 200, 340), 1.1)
    elif kind == "disconnected":
        g.stroke(A.polyline([(5.4, 4.2), (10.6, 4.2)]), 1.2)
    elif kind == "hardware-disabled":
        g.erase(A.polyline([(2.6, 13.4), (13.4, 2.6)]), 2.0)
        g.stroke(A.polyline([(2.6, 13.4), (13.4, 2.6)]), STROKE)
        g.bar(2.4, 12.6, 3.0, 1.6, 0.6)


def airplane(g: Glyph, off: bool = False) -> None:
    """A plane seen from above, the Aqua travel mark."""
    plane = [(8.0, 1.6), (9.4, 3.2), (9.4, 6.4), (14.2, 9.4), (14.2, 11.0),
             (9.4, 9.0), (9.4, 11.8), (11.0, 13.2), (11.0, 14.2),
             (8.0, 13.4), (5.0, 14.2), (5.0, 13.2), (6.6, 11.8),
             (6.6, 9.0), (1.8, 11.0), (1.8, 9.4), (6.6, 6.4), (6.6, 3.2)]
    g.solid(plane, 0.5)
    if off:
        g.erase(A.polyline([(1.8, 14.2), (14.2, 1.8)]), 2.2)
        g.stroke(A.polyline([(1.8, 14.2), (14.2, 1.8)]), STROKE)


def rotation(g: Glyph, locked: bool = False) -> None:
    """A device with the screen-turn arrow around it."""
    g.stroke(A.rr(6.0, 4.6, 4.0, 6.8, 1.0), STROKE)
    g.stroke(A.arc(8.0, 8.0, 6.0, -30, 205), 1.5)
    g.solid([(12.6, 2.3), (13.9, 5.9), (10.3, 5.6)], 0.5)
    if locked:
        g.dot(11.9, 11.7, 2.7)
        g.hole(A.rr(11.1, 11.5, 1.6, 1.5, 0.4))
        g.erase(A.arc(11.9, 11.3, 0.85, 180, 360), 0.9)


def orientation(g: Glyph, kind: str = "landscape") -> None:
    """A device plate turned to the requested orientation."""
    if kind.startswith("landscape"):
        rect = (1.7, 4.4, 12.6, 7.2)
    else:
        rect = (4.4, 1.7, 7.2, 12.6)
    g.stroke(A.rr(*rect, 1.2), STROKE)
    g.erase(A.rr(rect[0] + 1.1, rect[1] + 1.1, rect[2] - 2.2, rect[3] - 2.2, 0.6))
    if kind.endswith("inverse"):
        g.dot(rect[0] + rect[2] / 2, rect[1] + rect[3] - 1.0, 0.55)


def brightness(g: Glyph, kind: str = "display") -> None:
    """A sun disc with a level meter: brightness."""
    g.dot(8.0, 7.0, 3.2)
    for index in range(8):
        angle = math.radians(index * 45)
        g.stroke(A.polyline([(8.0 + 4.1 * math.cos(angle), 7.0 + 4.1 * math.sin(angle)),
                             (8.0 + 5.4 * math.cos(angle), 7.0 + 5.4 * math.sin(angle))]),
                 1.1)
    if kind == "keyboard":
        g.bar(2.4, 13.0, 11.2, 1.6, 0.8)
        g.bar(2.4, 13.0, 7.0, 1.6, 0.8)


def night_light(g: Glyph, off: bool = False) -> None:
    """A crescent moon over a horizon."""
    g.hole(A.circ(8.0, 7.0, 4.6))
    g.stroke(A.circ(8.0, 7.0, 4.6), STROKE + 0.3)
    g.hole(A.circ(9.9, 6.0, 3.9))
    g.bar(1.8, 13.2, 12.4, 1.7, 0.85)
    if off:
        g.erase(A.polyline([(2.0, 13.0), (14.0, 2.0)]), 2.1)
        g.stroke(A.polyline([(2.0, 13.0), (14.0, 2.0)]), STROKE)


def power_profile(g: Glyph, kind: str = "balanced") -> None:
    """A gauge face with a needle: the power profile."""
    g.stroke(A.arc(8.0, 9.6, 5.8, 180, 360), 1.7)
    g.stroke(A.polyline([(2.2, 9.6), (2.2, 12.6)]), 1.3)
    g.stroke(A.polyline([(13.8, 9.6), (13.8, 12.6)]), 1.3)
    angle = {"power-saver": 200, "balanced": 235, "performance": 285}[kind]
    tip = (8.0 + 3.6 * math.cos(math.radians(angle)),
           9.6 + 3.6 * math.sin(math.radians(angle)))
    g.line((8.0, 9.6), tip, 1.7)
    return g.dot(8.0, 9.6, 1.2)


def touch_disabled(g: Glyph) -> None:
    g.dot(8.0, 6.0, 3.0)
    g.stroke(A.arc(8.0, 9.0, 3.4, 0, 180), 1.4)
    g.erase(A.polyline([(2.4, 13.4), (13.6, 2.6)]), 2.1)
    g.stroke(A.polyline([(2.4, 13.4), (13.6, 2.6)]), STROKE)


def screen_shared(g: Glyph) -> None:
    A.display(g, 1.7, 2.8, 12.6, 8.2)
    g.bar(4.4, 6.0, 7.2, 1.4, 0.6)
    G._badge(g, 12.0, 11.8, 2.9)
    g.solid([(11.0, 11.8), (12.6, 10.4), (12.6, 13.2)], 0.4)


def content_loading(g: Glyph) -> None:
    """A dashed ring: content is loading."""
    for start in range(0, 360, 45):
        g.stroke(A.arc(8.0, 8.0, 5.6, start + 4, start + 30), 1.9)


def image_loading(g: Glyph) -> None:
    """A dashed frame: the picture is still arriving."""
    g.stroke(A.rr(1.9, 3.0, 12.2, 10.0, 1.3), STROKE)
    for start in range(0, 360, 60):
        g.stroke(A.arc(8.0, 8.0, 3.0, start + 6, start + 32), 1.6)


def image_missing(g: Glyph) -> None:
    g.stroke(A.rr(1.9, 3.0, 12.2, 10.0, 1.3), STROKE)
    g.erase(A.polyline([(2.4, 12.4), (13.0, 3.4)]), 2.2)
    g.stroke(A.polyline([(2.4, 12.4), (13.0, 3.4)]), STROKE)


def computer_fail(g: Glyph) -> None:
    A.display(g, 1.7, 2.4, 12.6, 8.0)
    G._badge(g, 8.0, 8.0, 3.0)
    G._cut_cross(g, 8.0, 8.0, 1.5, 1.3)


def dialog(g: Glyph, kind: str = "information") -> None:
    """The Aqua dialog plate: a solid rounded sign with its mark cut in."""
    if kind == "warning":
        g.solid([(8.0, 1.9), (14.4, 13.4), (1.6, 13.4)], 1.1)
        g.erase(A.rr(7.1, 5.9, 1.8, 4.2, 0.9))
        g.hole(A.circ(8.0, 11.7, 1.05))
        return
    g.bar(1.9, 1.9, 12.2, 12.2, 3.2)
    if kind == "error":
        G._cut_cross(g, 8.0, 8.0, 3.0, 1.9)
    elif kind == "question":
        G.question_mark(g, 8.0, 6.4, 1.05, 1.7, cut=True)
    elif kind == "password":
        # A key cut out of the plate: the padlock already means "locked", and
        # this dialog is the one asking for the keyword.
        g.hole(A.circ(5.2, 11.0, 2.4))
        g.stroke(A.circ(5.2, 11.0, 2.4), 1.4)
        g.erase(A.polyline([(7.0, 9.2), (12.6, 3.6)]), 1.6)
        g.erase(A.polyline([(11.0, 5.2), (12.5, 6.7)]), 1.4)
        g.erase(A.polyline([(9.4, 6.8), (10.9, 8.3)]), 1.4)
    else:
        g.erase(A.rr(7.05, 6.4, 1.9, 6.0, 0.9))
        g.hole(A.circ(8.0, 4.3, 1.15))


def security(g: Glyph, level: str = "medium") -> None:
    """A shield with a bore: security level."""
    shield = [(8.0, 1.6), (13.8, 3.6), (13.8, 8.4), (8.0, 14.4),
              (2.2, 8.4), (2.2, 3.6)]
    g.stroke(A.rpoly(shield, 1.2, True), STROKE + 0.1)
    if level == "low":
        A.minus(g, 8.0, 7.6, 1.9, 1.6)
    elif level == "medium":
        for y in (5.6, 8.0, 10.4):
            g.dot(8.0, y, 0.85)
    else:
        A.check(g, 8.0, 7.8, 2.4, 1.7)


def channel_security(g: Glyph, secure: bool = True) -> None:
    """A padlock, closed or lifted: is this conversation private?

    Squeezing a full-size lock into a speech bubble made both marks collide;
    the lock alone is what these names mean, and it is legible at 16 px.
    """
    A.lock(g, 8.0, 9.2, open=not secure)


def changes(g: Glyph, allow: bool = True) -> None:
    """A sheet with an allow/deny seal."""
    A.sheet(g, 2.8, 1.8, 9.0, 11.0)
    G._badge(g, 11.5, 11.6, 3.0)
    if allow:
        G._cut_check(g, 11.5, 11.6, 1.7, 1.3)
    else:
        G._cut_cross(g, 11.5, 11.6, 1.5, 1.25)


def notifications_disabled(g: Glyph) -> None:
    """The Aqua bell, with a slash when off."""
    g.solid([(4.2, 10.4), (4.2, 6.8), (8.0, 3.0), (11.8, 6.8), (11.8, 10.4)], 1.1)
    g.bar(2.6, 10.2, 10.8, 1.8, 0.9)
    g.hole(A.circ(8.0, 13.2, 1.4))
    g.dot(8.0, 2.2, 1.0)
    g.erase(A.polyline([(2.4, 13.6), (13.6, 2.4)]), 2.1)
    g.stroke(A.polyline([(2.4, 13.6), (13.6, 2.4)]), STROKE)


def bell(g: Glyph) -> None:
    """A dome, its rim and the clapper: the notification bell."""
    g.solid([(4.8, 10.0), (4.8, 7.0), (6.2, 4.0), (8.0, 3.1), (9.8, 4.0),
             (11.2, 7.0), (11.2, 10.0)], 1.5)
    g.bar(3.4, 9.8, 9.2, 1.7, 0.85)
    g.dot(8.0, 1.9, 0.95)
    g.dot(8.0, 12.7, 1.2)


def alarm(g: Glyph) -> None:
    """A clock with two bells: the alarm."""
    g.ring(8.0, 8.6, 5.0, STROKE + 0.2)
    g.stroke(A.polyline([(8.0, 5.4), (8.0, 8.6), (10.4, 9.8)]), 1.4)
    g.dot(8.0, 8.6, 0.8)
    # The bells used to hang off the tile: their arcs reached 0.1 and 15.9.
    for x in (3.1, 12.9):
        g.stroke(A.arc(x, 4.4, 1.4, 180, 360), 1.3)
    g.solid([(2.4, 5.1), (4.7, 2.8), (5.5, 3.4), (3.1, 5.7)], 0.4)
    g.solid([(13.6, 5.1), (11.3, 2.8), (10.5, 3.4), (12.9, 5.7)], 0.4)


def appointment_status(g: Glyph, kind: str = "soon") -> None:
    G.appointment_new(g)
    if kind == "missed":
        G._badge(g, 11.9, 11.6, 2.8)
        G._cut_cross(g, 11.9, 11.6, 1.4, 1.2)
    else:
        G._badge(g, 11.9, 11.6, 2.8)
        g.erase(A.circ(11.9, 11.6, 1.0))


def task_status(g: Glyph, past: bool = False) -> None:
    """A task note: two lines of work and the state of the first one.

    An empty rounded plate said nothing at all, which is what these two icons
    did before: they were the same blank box with a different dash.
    """
    g.stroke(A.rr(2.0, 2.0, 12.0, 12.0, 2.6), STROKE)
    g.bar(7.6, 4.6, 4.5, 1.3, 0.65)
    g.bar(7.6, 7.2, 3.4, 1.3, 0.65)
    if past:
        g.ring(5.3, 5.3, 1.9, 1.2)
        g.stroke(A.polyline([(5.3, 4.2), (5.3, 5.3), (6.1, 5.8)]), 1.0)
    else:
        g.stroke(A.polyline([(3.6, 5.4), (5.0, 6.8), (7.2, 3.8)]), 1.5)
    g.bar(4.6, 10.4, 7.0, 1.3, 0.65)
    g.bar(4.6, 12.6, 7.0, 1.3, 0.65)


def mail_read(g: Glyph, replied: bool = False, unread: bool = False) -> None:
    A.envelope(g, 1.9, 3.6, 12.2, 8.4)
    if replied:
        A.arrow(g, 0, 9.6, 12.4, 0.44)
        return
    if unread:
        g.dot(12.6, 11.8, 2.2)


def mail_attachment(g: Glyph) -> None:
    """A paperclip: the Aqua attachment mark."""
    g.stroke(A.rr(4.5, 1.9, 6.2, 11.2, 3.0), 1.5)
    g.stroke(A.rr(6.1, 4.6, 3.0, 9.0, 1.5), 1.4)


def media_playlist(g: Glyph, kind: str = "consecutive") -> None:
    """Playlist lines with a symbol for the mode."""
    for y in (3.2, 6.2, 9.2):
        g.bar(1.9, y - 0.9, 8.4, 1.8, 0.9)
    if kind == "shuffle":
        g.stroke(A.polyline([(11.2, 4.0), (13.9, 7.4), (11.2, 10.8)]), 1.4)
        g.stroke(A.polyline([(11.2, 10.8), (13.0, 10.8)]), 1.4)
        g.stroke(A.polyline([(11.2, 4.0), (13.0, 4.0)]), 1.4)
    elif kind in ("repeat", "repeat-song"):
        g.stroke(A.arc(12.1, 7.4, 2.1, -80, 250), 1.4)
        g.solid([(13.4, 4.9), (14.4, 7.4), (12.1, 7.2)], 0.4)
        if kind == "repeat-song":
            g.dot(12.1, 7.4, 0.9)
    else:
        for index in range(2):
            g.stroke(A.polyline([(11.2, 6.0 + index * 3.0),
                                 (13.4, 7.4 + index * 3.0)]), 1.4)


def printer_state(g: Glyph, kind: str = "printing") -> None:
    A.printer(g)
    G._badge(g, 11.9, 11.6, 2.8)
    if kind == "error":
        G._cut_cross(g, 11.9, 11.6, 1.4, 1.2)
    elif kind == "warning":
        g.solid([(11.9, 10.1), (13.6, 13.4), (10.2, 13.4)], 0.4)
    else:
        for index in range(2):
            g.erase(A.rr(10.3, 10.6 + index * 1.4, 3.2, 0.8, 0.3))


def software_update(g: Glyph, urgent: bool = False) -> None:
    G.system_software_update(g)
    if urgent:
        G._badge(g, 11.8, 4.2, 2.8)
        g.erase(A.rr(11.1, 2.7, 1.4, 2.5, 0.6))
        g.hole(A.circ(11.8, 5.7, 0.7))


def location_services(g: Glyph, active: bool = True) -> None:
    """Crosshair pin: location services."""
    g.ring(8.0, 8.0, 4.4, STROKE)
    g.line((8.0, 1.9), (8.0, 3.6), STROKE)
    g.line((8.0, 12.4), (8.0, 14.1), STROKE)
    g.line((1.9, 8.0), (3.6, 8.0), STROKE)
    g.line((12.4, 8.0), (14.1, 8.0), STROKE)
    if active:
        g.dot(8.0, 8.0, 2.0)
    else:
        g.erase(A.polyline([(2.4, 13.6), (13.6, 2.4)]), 2.1)
        g.stroke(A.polyline([(2.4, 13.6), (13.6, 2.4)]), STROKE)


def user_status(g: Glyph, kind: str = "available") -> None:
    """A contact disc with the presence mark cut in."""
    A.person_solid(g, 8.0, 7.2, 1.0)
    badge = {
        "available": "check",
        "away": "clock",
        "busy": "minus",
        "idle": "clock",
        "invisible": "none",
        "offline": "none",
        "not-tracked": "question",
        "status-pending": "dots",
    }[kind]
    G._badge(g, 11.9, 11.7, 2.9)
    if badge == "check":
        G._cut_check(g, 11.9, 11.7, 1.5, 1.25)
    elif badge == "minus":
        G._cut_minus(g, 11.9, 11.7, 1.6, 1.35)
    elif badge == "clock":
        g.hole(A.circ(11.9, 11.7, 1.9))
        g.ring(11.9, 11.7, 1.9, 1.1)
        g.erase(A.polyline([(11.9, 10.6), (11.9, 11.7), (12.7, 12.2)]), 1.0)
    elif badge == "question":
        g.hole(A.circ(11.9, 11.7, 1.8))
        g.ring(11.9, 11.7, 1.8, 1.1)
        g.erase(A.rr(11.4, 10.7, 1.0, 1.2, 0.4))
        g.hole(A.circ(11.9, 12.7, 0.55))
    elif badge == "dots":
        for offset in (-1.0, 1.0):
            g.hole(A.circ(11.9 + offset, 11.7, 0.6))
    # invisible/offline keep a plain disc, which reads as "no presence"


def avatar_default(g: Glyph) -> None:
    """A contact plate: a head and shoulders in a rounded tile."""
    g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 3.2), STROKE)
    g.dot(8.0, 6.2, 2.4)
    g.fill("M3.6 12.6A4.4 4.4 0 0 1 12.4 12.6Z")


def auth_sim_state(g: Glyph, kind: str = "locked") -> None:
    memory_card(g, kind="sim")
    G._badge(g, 11.9, 11.7, 2.9)
    if kind == "locked":
        g.erase(A.rr(10.8, 11.9, 2.2, 1.8, 0.5))
        g.stroke(A.arc(11.9, 11.9, 0.85, 180, 360), 0.7)
    else:
        G._cut_cross(g, 11.9, 11.7, 1.4, 1.2)


# --------------------------------------------------------------------------- #
# weather
# --------------------------------------------------------------------------- #


def sun(g: Glyph, cx: float = 8.0, cy: float = 8.0, r: float = 3.6,
        rays: int = 8) -> None:
    g.dot(cx, cy, r)
    for index in range(rays):
        angle = math.radians(index * (360.0 / rays))
        g.stroke(A.polyline([(cx + (r + 1.0) * math.cos(angle),
                              cy + (r + 1.0) * math.sin(angle)),
                             (cx + (r + 2.4) * math.cos(angle),
                              cy + (r + 2.4) * math.sin(angle))]), 1.5)


def moon(g: Glyph, cx: float = 8.0, cy: float = 8.0, r: float = 5.6) -> None:
    """A crescent: a disc with the sky cut out of it."""
    g.dot(cx, cy, r)
    g.hole(A.circ(cx + r * 0.72, cy - r * 0.42, r * 0.98))


def cloud(g: Glyph, cx: float = 8.0, cy: float = 8.6, scale: float = 1.0,
          width: float = STROKE) -> None:
    """The Aqua cloud: three lobes on a flat base, as one solid silhouette."""
    for x, y, r in ((cx - 3.0 * scale, cy + 0.4 * scale, 2.6 * scale),
                    (cx, cy - 1.2 * scale, 3.4 * scale),
                    (cx + 3.2 * scale, cy + 0.3 * scale, 2.5 * scale)):
        g.dot(x, y, r)
    g.bar(cx - 5.9 * scale, cy + 0.2 * scale, 11.8 * scale, 2.6 * scale,
          width / 2 + 0.6)


def rain(g: Glyph, drops: int = 3, scattered: bool = False) -> None:
    cloud(g, 8.0, 6.4, 0.86)
    xs = (4.4, 8.0, 11.6) if not scattered else (3.6, 8.4, 12.0)
    for index, x in enumerate(xs[:drops]):
        g.stroke(A.polyline([(x, 10.4 + (index % 2) * 0.8),
                             (x - 1.0, 13.4 + (index % 2) * 0.8)]), 1.5)


def snow(g: Glyph) -> None:
    cloud(g, 8.0, 6.0, 0.82)
    for x in (4.4, 8.0, 11.6):
        for angle in (0, 60, 120):
            a = math.radians(angle)
            g.stroke(A.polyline([(x - 1.5 * math.cos(a), 11.6 - 1.5 * math.sin(a)),
                                 (x + 1.5 * math.cos(a), 11.6 + 1.5 * math.sin(a))]),
                     1.1)


def storm(g: Glyph) -> None:
    cloud(g, 8.0, 5.8, 0.82)
    bolt = [(9.0, 9.2), (6.0, 12.8), (7.8, 12.8), (7.0, 15.0), (10.2, 11.0),
            (8.4, 11.0)]
    g.hole(A.ell(10.0, 12.0, 3.4, 3.2))
    g.solid(bolt, 0.2)


def fog(g: Glyph) -> None:
    cloud(g, 8.0, 5.4, 0.82)
    for index, y in enumerate((10.6, 12.6)):
        width = 12.0 - index * 2.4
        g.bar(8.0 - width / 2, y, width, 1.7, 0.85)


def wind(g: Glyph) -> None:
    """Three curling gusts."""
    for index, y in enumerate((4.6, 8.0, 11.4)):
        length = 7.6 + index * 1.4
        g.stroke(A.polyline([(1.8, y), (1.8 + length, y)]), 1.6)
        g.stroke(A.arc(1.8 + length, y - 1.3, 1.3, 90, 360), 1.5)


def tornado(g: Glyph) -> None:
    """A funnel of gusts, narrowing as it reaches the ground."""
    rows = ((2.8, 10.6), (4.3, 9.0), (5.8, 7.4), (7.3, 5.8),
            (8.8, 4.2), (10.3, 2.6))
    for index, (y, width) in enumerate(rows):
        offset = 0.0 if index % 2 == 0 else 0.8
        g.stroke(A.polyline([(3.0 + offset, y), (3.0 + offset + width, y)]), 1.6)


def few_clouds(g: Glyph, night: bool = False) -> None:
    if night:
        moon(g, 5.8, 5.8, 3.2)
    else:
        sun(g, 6.6, 6.4, 2.2, 8)
    cloud(g, 9.2, 10.2, 0.82)


def overcast(g: Glyph) -> None:
    cloud(g, 6.4, 6.2, 0.72)
    cloud(g, 9.4, 10.4, 0.86)


def severe_alert(g: Glyph) -> None:
    cloud(g, 8.0, 5.6, 0.8)
    g.solid([(8.0, 8.6), (12.6, 14.6), (3.4, 14.6)], 0.8)
    g.erase(A.rr(7.3, 10.4, 1.4, 2.0, 0.6))
    g.hole(A.circ(8.0, 13.2, 0.75))


def sunrise(g: Glyph, rising: bool = True) -> None:
    """The sun on a horizon, with an arrow for rise or set."""
    g.dot(8.0, 9.4, 3.3)
    for index in range(5):
        angle = math.radians(180 + index * 45)
        g.stroke(A.polyline([(8.0 + 4.6 * math.cos(angle), 9.4 + 4.6 * math.sin(angle)),
                             (8.0 + 5.8 * math.cos(angle), 9.4 + 5.8 * math.sin(angle))]),
                 1.4)
    g.bar(1.8, 10.6, 12.4, 1.8, 0.9)
    if rising:
        g.solid([(8.0, 12.8), (10.3, 15.0), (5.7, 15.0)], 0.5)
    else:
        g.solid([(8.0, 14.9), (10.3, 12.8), (5.7, 12.8)], 0.5)


# --------------------------------------------------------------------------- #
# faces
# --------------------------------------------------------------------------- #

_EYES = {
    "dot": "dot",
    "happy": "happy",
    "wide": "ring",
    "sleepy": "lid",
    "shut": "shut",
    "wink": "wink",
}

_MOUTH = {
    "smile": "smile",
    "big": "big",
    "frown": "frown",
    "flat": "flat",
    "open": "open",
    "smirk": "smirk",
    "wave": "wave",
    "tongue": "tongue",
    "yawn": "yawn",
    "crooked": "crooked",
    "small": "small",
}


def face(g: Glyph, eyes: str = "dot", mouth: str = "smile",
         brows: str = "", extra: str = "") -> None:
    """The Aqua face: one plate, a pair of eyes and a mouth, plus an accent."""
    g.ring(8.0, 8.0, 6.1, STROKE)

    style = _EYES.get(eyes, "dot")
    for x in (5.7, 10.3):
        if style == "dot":
            g.dot(x, 6.4, 0.95)
        elif style == "happy":
            g.stroke(A.arc(x, 7.0, 1.5, 200, 340), 1.3)
        elif style == "ring":
            g.ring(x, 6.4, 1.25, 1.15)
        elif style == "lid":
            g.stroke(A.polyline([(x - 1.5, 6.2), (x + 1.5, 6.2)]), 1.3)
        elif style == "shut":
            g.stroke(A.polyline([(x - 1.4, 6.4), (x + 1.4, 6.4)]), 1.3)
        elif style == "wink" and x > 8:
            g.stroke(A.polyline([(x - 1.4, 6.4), (x + 1.4, 6.4)]), 1.3)
        elif style == "wink":
            g.dot(x, 6.4, 0.95)

    shape = _MOUTH.get(mouth, "smile")
    if shape == "smile":
        g.stroke(A.arc(8.0, 8.6, 2.6, 25, 155), 1.5)
    elif shape == "big":
        g.stroke(A.arc(8.0, 8.4, 3.2, 20, 160), 1.6)
    elif shape == "frown":
        g.stroke(A.arc(8.0, 11.6, 2.6, 205, 335), 1.5)
    elif shape == "flat":
        g.stroke(A.polyline([(5.6, 10.2), (10.4, 10.2)]), 1.5)
    elif shape == "open":
        g.fill(A.ell(8.0, 10.2, 1.7, 1.3))
    elif shape == "smirk":
        g.stroke(A.arc(8.8, 9.0, 1.9, 30, 150), 1.5)
    elif shape == "wave":
        g.stroke(A.polyline([(5.4, 10.0), (6.8, 9.2), (8.0, 10.2), (9.4, 9.2),
                             (10.6, 10.0)]), 1.4)
    elif shape == "tongue":
        g.stroke(A.arc(8.0, 8.8, 2.6, 25, 155), 1.5)
        g.bar(6.8, 10.0, 2.4, 2.0, 1.0)
    elif shape == "yawn":
        g.fill(A.ell(8.0, 10.4, 1.5, 2.0))
    elif shape == "crooked":
        g.stroke(A.arc(8.0, 9.8, 2.1, 5, 155), 1.5)
        g.stroke(A.polyline([(9.9, 9.3), (10.7, 8.6)]), 1.2)
    elif shape == "small":
        g.stroke(A.polyline([(6.6, 10.0), (9.4, 10.0)]), 1.5)

    if brows == "angry":
        for sx in (-1, 1):
            g.stroke(A.polyline([(8.0 + sx * 3.4, 3.6), (8.0 + sx * 1.4, 4.6)]), 1.3)
    elif brows == "worried":
        for sx in (-1, 1):
            g.stroke(A.polyline([(8.0 + sx * 3.4, 4.6), (8.0 + sx * 1.4, 3.6)]), 1.3)
    elif brows == "askew":
        g.stroke(A.polyline([(4.2, 4.6), (6.6, 3.2)]), 1.3)
        g.stroke(A.polyline([(9.4, 4.4), (11.6, 4.4)]), 1.3)

    if extra == "glasses":
        for x in (5.7, 10.3):
            g.ring(x, 6.4, 1.9, 1.2)
        g.stroke(A.polyline([(7.6, 6.4), (8.4, 6.4)]), 1.1)
    elif extra == "shades":
        g.bar(3.4, 5.2, 9.2, 2.4, 1.1)
        g.hole(A.rr(4.4, 5.8, 3.6, 1.1, 0.55))
        g.hole(A.rr(8.0, 5.8, 3.6, 1.1, 0.55))
    elif extra == "tears":
        for x in (4.6, 11.4):
            g.stroke(A.polyline([(x, 7.6), (x, 11.0)]), 1.2)
            g.dot(x, 11.8, 0.9)
    elif extra == "heart":
        for x in (5.7, 10.3):
            g.solid([(x - 1.7, 6.0), (x - 0.6, 5.1), (x, 5.8), (x + 0.6, 5.1),
                     (x + 1.7, 6.0), (x, 8.0)], 0.35)
    elif extra == "blush":
        for x in (4.6, 11.4):
            g.bar(x - 1.3, 8.6, 2.6, 1.3, 0.65)
    elif extra == "halo":
        g.stroke(A.ell(8.0, 2.6, 3.2, 0.9), 1.15)
    elif extra == "horns":
        for sx in (-1, 1):
            g.solid([(8.0 + sx * 4.4, 2.6), (8.0 + sx * 6.2, 0.8),
                     (8.0 + sx * 5.6, 4.0)], 0.4)
    elif extra == "monkey":
        for sx in (-1, 1):
            g.ring(8.0 + sx * 4.9, 8.0, 1.5, 1.15)
        g.dot(8.0, 9.6, 0.75)


# --------------------------------------------------------------------------- #
# categories, preferences and legacy marks
# --------------------------------------------------------------------------- #


def emoji_tile(g: Glyph, kind: str = "people") -> None:
    """A round face plate carrying the category mark."""
    g.ring(8.0, 8.0, 6.1, STROKE)
    if kind == "people":
        g.dot(5.8, 6.6, 1.0)
        g.dot(10.2, 6.6, 1.0)
        g.stroke(A.arc(8.0, 8.4, 2.6, 30, 150), 1.4)
    elif kind == "nature":
        g.solid([(3.2, 12.6), (3.8, 8.6), (6.2, 5.0), (9.6, 3.4), (12.8, 4.0),
                 (12.0, 7.8), (9.2, 11.2), (5.8, 12.8)], 1.4)
        g.erase(A.polyline([(4.4, 11.8), (11.6, 4.6)]), 1.2)
    elif kind == "food":
        g.stroke(A.arc(8.0, 8.0, 2.6, 200, 340), 1.4)
        g.bar(5.6, 8.6, 4.8, 1.4, 0.7)
    elif kind == "activities":
        # A ball with seams: sport, not a crossed-out ring.
        g.dot(8.0, 8.0, 4.7)
        g.erase(A.polyline([(8.0, 3.5), (8.0, 12.5)]), 0.95)
        for sx in (-1, 1):
            g.erase(f"M{8.0 + sx * 4.1} 4.9A5.6 5.6 0 0 {0 if sx > 0 else 1} "
                    f"{8.0 + sx * 4.1} 11.1", 0.95)
    elif kind == "travel":
        airplane(g)
    elif kind == "objects":
        # A lightbulb: the object that best survives a 10 px bore.
        g.ring(8.0, 7.0, 2.9, 1.5)
        g.bar(6.7, 9.4, 2.6, 1.5, 0.7)
        g.bar(7.0, 11.2, 2.0, 1.2, 0.6)
        g.erase(A.polyline([(8.0, 5.4), (8.0, 8.6)]), 0.9)
    elif kind == "symbols":
        for x in (5.6, 9.4):
            g.bar(x, 4.6, 1.5, 6.8, 0.7)
        for y in (6.6, 9.4):
            g.bar(3.4, y, 9.2, 1.5, 0.7)
    elif kind == "flags":
        g.bar(5.2, 3.4, 1.6, 9.2, 0.8)
        g.fill("M6.8 3.8L12.6 5.6L6.8 7.6Z")
    elif kind == "body":
        # A standing figure: head, shoulders, arms out, two legs.
        g.dot(8.0, 4.8, 1.5)
        g.stroke(A.polyline([(8.0, 6.4), (8.0, 9.8)]), 2.2)
        g.stroke(A.polyline([(4.8, 7.4), (11.2, 7.4)]), 1.5)
        g.stroke(A.polyline([(8.0, 9.8), (6.2, 12.4)]), 1.6)
        g.stroke(A.polyline([(8.0, 9.8), (9.8, 12.4)]), 1.6)
    elif kind == "recent":
        g.ring(8.0, 8.0, 5.2, STROKE)
        g.stroke(A.polyline([(8.0, 5.0), (8.0, 8.0), (10.4, 9.4)]), 1.4)
        g.dot(8.0, 8.0, 0.75)


def category_mark(g: Glyph, kind: str = "system") -> None:
    """Category medallions for the menu: squared plates with a motif."""
    if kind == "engineering":
        # A drafting compass, not a second gear: "system" already owns that
        # mark, and two identical gears told the menu nothing.
        g.dot(8.0, 3.0, 1.4)
        g.stroke(A.polyline([(8.0, 4.2), (4.0, 13.2)]), 1.6)
        g.stroke(A.polyline([(8.0, 4.2), (12.0, 13.2)]), 1.6)
        g.stroke(A.arc(8.0, 4.2, 9.4, 66, 114), 1.0)
    elif kind == "games":
        gamepad(g)
    elif kind == "graphics":
        g.stroke(A.rr(1.9, 3.2, 12.2, 10.0, 1.3), STROKE)
        g.solid([(2.8, 12.2), (6.4, 7.4), (8.6, 10.6), (10.0, 8.6), (13.4, 12.2)], 0.5)
        g.dot(4.6, 6.0, 1.1)
    elif kind == "multimedia":
        g.stroke(A.rr(1.9, 3.6, 12.2, 8.8, 1.0), STROKE)
        for x in (3.4, 10.4):
            g.erase(A.rr(x, 4.6, 1.6, 1.6, 0.4))
            g.erase(A.rr(x, 9.8, 1.6, 1.6, 0.4))
        g.stroke(A.polyline([(5.0, 5.4), (5.0, 10.6)]), 1.1)
        g.stroke(A.polyline([(11.0, 5.4), (11.0, 10.6)]), 1.1)
    elif kind == "science":
        g.stroke(A.polyline([(6.4, 2.0), (6.4, 6.0), (2.6, 13.2),
                             (13.4, 13.2), (9.6, 6.0), (9.6, 2.0)]), 1.6)
        g.bar(5.4, 1.4, 5.2, 1.6, 0.8)
        g.dot(6.6, 10.6, 0.9)
        g.dot(9.8, 11.6, 0.7)
    elif kind == "system":
        A.gear(g, 8.0, 8.0, 8, 6.2, 4.3, 1.9)
    elif kind == "utilities":
        g.stroke(A.rr(2.2, 5.4, 11.6, 8.2, 1.2), STROKE)
        g.bar(5.4, 3.0, 5.2, 2.6, 0.8)
        g.erase(A.polyline([(8.0, 6.6), (8.0, 9.0)]), 1.3)
        A.cross(g, 8.0, 10.8, 1.6, 1.2)
    else:
        g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 3.0), STROKE)
        g.dot(8.0, 4.9, 1.1)
        g.bar(7.1, 7.0, 1.8, 5.4, 0.9)


def preferences(g: Glyph, kind: str = "desktop") -> None:
    """The preferences family: a plate with the setting's own mark."""
    if kind == "keyboard":
        A.keyboard(g)
    elif kind == "keyboard-shortcuts":
        A.keyboard(g)
        G._badge(g, 12.2, 11.8, 2.8)
        G._cut_plus(g, 12.2, 11.8, 1.4, 1.2)
    elif kind == "mouse":
        A.mouse(g)
    elif kind == "display":
        A.display(g, 1.7, 2.8, 12.6, 8.2)
    elif kind == "desktop":
        # The universal preferences mark: three rails with their knobs.
        for y, x in ((4.2, 10.0), (8.0, 5.8), (11.8, 9.2)):
            g.bar(1.9, y - 0.8, 12.2, 1.6, 0.8)
            g.hole(A.circ(x, y, 1.9))
            g.stroke(A.circ(x, y, 1.9), 1.2)
    elif kind == "appearance":
        g.stroke(A.circ(8.0, 8.0, 5.6), STROKE)
        g.fill("M8 2.6A5.4 5.4 0 0 1 8 13.4Z")
    elif kind == "wallpaper":
        G.mime_generic(g, "image")
    elif kind == "font":
        G.font_select(g)
    elif kind == "locale":
        A.globe(g, 8.0, 8.0, 6.0)
    elif kind == "accessibility":
        A.person(g, 8.0, 5.2, 1.9, 1.5, 3.6)
        g.stroke(A.arc(8.0, 10.4, 3.2, 200, 340), 1.4)
    elif kind == "screensaver":
        moon(g, 8.0, 8.0, 5.4)
    elif kind == "multitasking":
        G.view_dual(g)
    elif kind == "remote-desktop":
        A.display(g, 1.7, 2.8, 12.6, 8.2)
        g.bar(6.4, 9.4, 3.2, 1.4, 0.6)
    elif kind == "time":
        g.ring(8.0, 8.0, 5.8, STROKE)
        g.stroke(A.polyline([(8.0, 4.6), (8.0, 8.0), (11.0, 9.6)]), 1.5)
        g.dot(8.0, 8.0, 0.85)
    elif kind == "notifications":
        bell(g)
    elif kind == "sharing":
        for cx, cy in ((5.4, 8.6), (10.6, 5.8), (10.6, 11.4)):
            g.dot(cx, cy, 1.5)
        g.line((6.6, 7.9), (9.4, 6.4), 1.1)
        g.line((6.6, 9.3), (9.4, 10.8), 1.1)
    elif kind == "privacy":
        A.lock(g, 8.0, 9.4, open=False)
    elif kind == "parental-controls":
        g.ring(8.0, 5.6, 2.6, STROKE)
        g.stroke(A.arc(8.0, 12.0, 4.2, 180, 360), STROKE)
        g.erase(A.rr(3.2, 11.0, 9.6, 2.2, 1.0))
        g.stroke(A.polyline([(3.8, 12.1), (12.2, 12.1)]), STROKE)
    elif kind == "details":
        g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 3.0), STROKE)
        for y in (5.4, 8.0, 10.6):
            g.bar(4.0, y - 0.7, 1.6, 1.4, 0.7)
            g.bar(6.6, y - 0.7, 5.4, 1.4, 0.7)
    elif kind == "devices":
        g.stroke(A.rr(1.9, 3.6, 6.4, 6.0, 0.8), STROKE)
        A.phone(g, 11.6, 9.4, 4.6, 7.4)
    elif kind == "network":
        network_wired(g)
    elif kind == "network-proxy":
        network_wired(g)
        G._badge(g, 12.2, 11.8, 2.8)
        g.hole(A.rr(11.0, 11.0, 2.4, 1.6, 0.5))
    elif kind == "search":
        A.magnifier(g)
    elif kind == "apps":
        G.view_app_grid(g)
    elif kind == "color":
        g.ring(8.0, 8.0, 5.8, STROKE)
        g.dot(8.0, 8.0, 2.4)
    else:
        A.gear(g, 8.0, 8.0, 8, 6.2, 4.3, 1.9)


def legacy_app(g: Glyph, kind: str = "terminal") -> None:
    """The legacy app marks: calculator, terminal, editor, browser, help."""
    if kind == "terminal":
        g.stroke(A.rr(1.9, 2.6, 12.2, 10.8, 1.3), STROKE)
        g.stroke(A.polyline([(4.0, 6.6), (6.2, 8.6), (4.0, 10.6)]), 1.5)
        g.bar(7.6, 10.0, 4.4, 1.4, 0.7)
    elif kind == "calculator":
        # Keys are painted, never cut: a hole only rubs out ink that is already
        # there, and the body of the calculator is an outline.
        g.stroke(A.rr(3.2, 1.9, 9.6, 12.2, 1.3), STROKE)
        g.bar(4.6, 3.4, 6.8, 2.2, 0.5)
        for row in range(3):
            for column in range(3):
                g.dot(5.4 + column * 2.6, 7.5 + row * 2.3, 0.75)
    elif kind == "text-editor":
        A.sheet(g, 2.8, 1.8, 9.2, 11.4)
        G._text_rows(g, [5.2, 7.2, 9.2], 4.6, 10.4)
    elif kind == "browser":
        A.globe(g, 8.0, 8.0, 6.0)
    elif kind == "help":
        g.ring(8.0, 8.0, 6.0, STROKE)
        G.question_mark(g, 8.0, 6.2, 0.92, 1.55)
    elif kind == "character-map":
        for row in range(2):
            for column in range(3):
                g.stroke(A.rr(1.9 + column * 4.2, 2.4 + row * 5.6, 3.6, 5.0, 0.7),
                         1.2)
    elif kind == "dictionary":
        g.stroke(A.rr(2.2, 2.2, 11.6, 11.6, 1.2), STROKE)
        g.erase(A.polyline([(8.0, 2.2), (8.0, 13.8)]), 1.5)
        G._text_rows(g, [5.0, 7.2, 9.4], 3.4, 7.2)
        G._text_rows(g, [5.0, 7.2, 9.4], 8.8, 12.6)
    elif kind == "screenshot":
        g.stroke(A.rr(1.9, 3.4, 12.2, 9.4, 1.3), STROKE)
        g.ring(8.0, 8.0, 2.6, 1.4)
        g.bar(9.6, 4.6, 2.4, 1.4, 0.5)
    elif kind == "file-manager":
        A.folder(g, 1.7, 4.0, 12.6, 9.4)
        g.bar(4.6, 6.4, 4.4, 1.4, 0.6)
    elif kind == "software-install":
        g.stroke(A.rr(1.9, 1.9, 12.2, 12.2, 1.4), STROKE)
        g.bar(1.9, 1.9, 12.2, 2.6, 1.2)
        A.arrow(g, 90, 8.0, 8.4, 0.62)
    elif kind == "users":
        A.person(g, 5.6, 5.6, 2.0, 1.4, 4.0)
        A.person(g, 11.0, 6.4, 1.6, 1.3, 3.2)
    elif kind == "power-manager":
        A.battery(g, 0.7)
        g.solid([(9.4, 4.4), (6.4, 9.0), (8.2, 9.0), (7.4, 12.4), (10.6, 7.4),
                 (8.6, 7.4)], 0.2)
    elif kind == "volume-control":
        volume(g, "medium")
    elif kind == "user-info":
        g.ring(8.0, 8.0, 6.0, STROKE)
        g.dot(8.0, 5.8, 1.8)
        g.fill("M4.8 12.4A3.2 3.2 0 0 1 11.2 12.4Z")
    elif kind == "panel":
        g.stroke(A.rr(1.9, 2.9, 12.2, 9.8, 1.2), STROKE)
        g.bar(1.9, 2.9, 12.2, 2.6, 1.0)
        A.person(g, 5.4, 6.2, 1.3, 1.2, 2.6)
        return g.bar(9.0, 7.4, 3.6, 1.4, 0.6)
    elif kind == "emblem-important":
        g.solid([(8.0, 1.8), (14.2, 8.0), (8.0, 14.2), (1.8, 8.0)], 1.2)
        G._cut_plus(g, 8.0, 8.0, 2.0, 1.5)
        return
    elif kind == "emblem-system":
        A.gear(g, 8.0, 8.0, 8, 6.2, 4.3, 1.9)
