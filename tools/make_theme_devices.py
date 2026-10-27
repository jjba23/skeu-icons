#!/usr/bin/env python3
"""Dress the device and volume icons the way OS X drew them.

``make_context_icons.py`` draws the *devices* context as physical objects, the
same way it draws the menu categories: one relief illustration per volume,
drive, peripheral and screen.  That is the pack's own artwork, and for most of
the context it is what the theme keeps.

Storage is the exception.  Apple drew the era's volumes - the white removable
medium with the orange USB symbol, the orange USB stick, the bare mechanism of
an internal drive, the blue globe of a mounted network volume, the labelled CD
and DVD - and a desktop dressed as Leopard wants those on the desktop when a
USB key is plugged in, not a look-alike drawn in the same spirit.  ``VOLUMES``
maps a theme device name onto catalogued artwork in ``library/volumes`` (see
``library/README.org`` for its provenance); everything the era never drew - an
SSD, a Blu-ray, a tape, a USB hub, a RAID enclosure, a fingerprint pad - keeps
the pack's own drawing, and the table is the list of the trades.

Two details make the swap real rather than half-done:

* the bitmaps are written at every size the theme ships, ``@2x`` included, so a
  16 px lookup and a 1024 px one agree;
* ``skeu-icons/scalable/devices/<name>.svg`` is rewritten too.  Every one of
  these names has a scalable SVG there from the pack's own artwork, and a
  toolkit that renders a scalable SVG in preference to a bitmap - which is
  most of them - would otherwise go on showing the drawn drive while the
  bitmaps beside it changed, so the same volume would look different in two
  applications.  These SVGs wrap the artwork as a PNG, the shape
  ``make_theme_mimes.svg_wrapper`` already uses for derived scalable icons.

``make_context_icons.py`` asks ``claimed()`` for the names this table answers
for and skips them, so redrawing the device masters cannot quietly revert the
era artwork.

    python3 tools/make_theme_devices.py            # install + scalable wrappers
    python3 tools/make_theme_devices.py --check    # report drift, write nothing
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_theme_apps import recoloured  # noqa: E402
from make_theme_mimes import svg_wrapper  # noqa: E402
from render_skeu import resize, save_png, save_text  # noqa: E402

THEME = ROOT / "skeu-icons"
LIBRARY = ROOT / "library"
VOLUME_DIR = LIBRARY / "volumes"
CATALOGUE = LIBRARY / "volumes.json"

#: Sizes the theme ships as bitmaps; every name is mirrored into ``@2x``.
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "devices"
SCALABLE = THEME / "scalable" / CONTEXT

#: The size the eras artwork is resampled up to before it is cut down again.
#: The sources are 128 px, so this adds nothing but a common grid to work on -
#: the honest sizes are the ones at or below the sources' own.
MASTER = 512

#: ``theme device name -> artwork stem in library/volumes``.  A name that is not
#: here keeps the drawing the pack made for it: Apple published no artwork for
#: an SSD, a Blu-ray or a tape in that era, so those are left alone rather than
#: dressed in a disc that means something else.
#:
#: Names are the freedesktop device vocabulary, so the same volume answers in
#: the desktop's volume list, in a launcher that offers to eject it, and in the
#: file manager's sidebar.  Where two names mean the same object - two names for
#: a microphone, or a network volume and a workgroup - they share a colourway
#: rather than a picture, so a machine showing all of them does not show the
#: identical tile twice.
VOLUMES: dict[str, str] = {
    # --- storage: the era's drives and media ------------------------------- #
    "drive-harddisk": "harddisk",
    "drive-harddisk-system": "harddisk-alt",
    "drive-harddisk-usb": "removable-harddisk",
    "drive-harddisk-ieee1394": "firewire-drive",
    "drive-removable-media": "removable-drive",
    "drive-removable-media-usb": "usb-stick",
    "drive-removable-media-usb-pendrive": "usb-stick-alt",
    "media-removable": "removable-drive-alt",
    "media-optical": "optical",
    "media-optical-cd": "optical-r",
    "media-optical-cd-audio": "optical-audio",
    "media-optical-dvd": "optical-dvd",
    "media-flash": "flash-sd-alt",
    "media-flash-sd-mmc": "flash-sd",
    "media-flash-smart-media": "flash-sm",
    "media-floppy": "floppy",
    "media-zip": "zip-disk",
    # --- network shares, wired and wireless -------------------------------- #
    "network-server": "network-drive",
    "network-workgroup": "network-mount",
    "network-wired": "ethernet",
    "network-wireless": "wireless",
    "network-bluetooth": "bluetooth-alt",
    "modem": "modem",
    # --- the machine, its screens and what hangs off it -------------------- #
    "computer": "desktop-computer",
    "computer-laptop": "laptop",
    "video-display": "display",
    "video-single-display": "display-alt",
    # --- peripherals Apple drew once and never redrew ---------------------- #
    "bluetooth": "bluetooth",
    "printer": "printer",
    "printer-network": "printer-alt",
    "scanner": "scanner",
    "input-keyboard": "keyboard",
    "input-mouse": "mouse",
    "input-gaming": "game-controller",
    "input-tablet": "graphics-tablet",
    "multimedia-player": "ipod",
    "portable-media-player": "ipod-alt",
    "phone": "phone",
    "pda": "pda",
    "camera-photo": "camera",
    "camera-video": "camcorder",
    "camera-web": "webcam",
    "microphone": "microphone",
    "audio-input-microphone": "microphone",
    "battery-caution": "battery-dead",
}

#: Colourways of a volume, for the second name that means the same kind of
#: thing.  ``alt stem -> (source stem, hue, saturation, mode)``; the mode is the
#: one ``make_theme_apps.recoloured`` implements and the choice is not free:
#: these are mostly metal and glass, which carry almost no hue of their own, so
#: ``shift`` would leave a silver drive silver.  ``tint`` moves the whole object
#: onto one hue and keeps its light and shade, so an aluminium mechanism turns
#: brass, a white volume stays white while its USB symbol turns blue, and the
#: red of an SD card becomes another colour card.
VOLUME_ALTS: dict[str, tuple[str, float, float, str]] = {
    "harddisk-alt": ("harddisk", 205, 1.0, "tint"),        # the startup disk, cooled
    "removable-drive-alt": ("removable-drive", 205, 1.0, "tint"),
    "printer-alt": ("printer", 205, 1.0, "tint"),            # the network printer
    "bluetooth-alt": ("bluetooth", 25, 1.0, "tint"),        # the second radio, brass
    "usb-stick-alt": ("usb-stick", 205, 1.0, "tint"),      # a blue stick
    "display-alt": ("display", 25, 1.0, "tint"),           # a warmer screen
    "ipod-alt": ("ipod", 30, 1.0, "tint"),                 # the copper one
    "flash-sd-alt": ("flash-sd", 205, 1.0, "tint"),        # a blue card
}


def claimed() -> frozenset[str]:
    """The device names this table answers for.

    ``make_context_icons.py`` leaves them alone: its drawn master would
    otherwise land on top of the era artwork every time the device set is
    redrawn, and the theme would silently go back to the look-alike.
    """
    return frozenset(VOLUMES)


def catalogue() -> dict[str, dict]:
    """``{stem: record}`` for the era volumes, from ``library/volumes.json``."""
    if not CATALOGUE.is_file():
        return {}
    return {record["stem"]: record for record in json.loads(CATALOGUE.read_text())}


def masters(wanted: set[str]) -> dict[str, Image.Image]:
    """Resample every volume stem and colourway the table asks for, once each."""
    out: dict[str, Image.Image] = {}
    for stem in sorted(wanted):
        path = VOLUME_DIR / f"{stem}.png"
        if not path.is_file():
            continue
        with Image.open(path) as source:
            art = source.convert("RGBA")
        if max(art.size) < MASTER:
            art = art.resize((MASTER, MASTER), Image.LANCZOS)
        out[stem] = art
    for stem, (source, hue, saturation, mode) in VOLUME_ALTS.items():
        if stem not in wanted or source not in out:
            continue
        out[stem] = recoloured(out[source], hue, saturation, mode)
    return out


def plan() -> list[tuple[str, str]]:
    """``[(theme device name, artwork stem), ...]`` in table order."""
    return sorted(VOLUMES.items())


def matches_png(image: Image.Image, path: Path) -> bool:
    """Whether PATH is on disk exactly as IMAGE would be saved."""
    if not path.is_file():
        return False
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return path.read_bytes() == buffer.getvalue()


def write_names(problems: list[str], write: bool) -> int:
    """Write every mapped device at every size, plus its scalable wrapper.

    ``--check`` renders the artwork anyway and compares it with what is on disk,
    byte for byte.  Finding the file there is not enough: the pack hard-links
    icons that happen to be identical, so a write through one of those names
    changes the picture under a *different* name while every name this table
    asks for is still present.  That is exactly how the first run of this step
    left ``media-flash`` holding the SD card's red twin and three menu category
    icons wearing a USB stick and a cinema display.
    """
    art = masters(set(VOLUMES.values()))
    written = 0

    for name, stem in plan():
        image = art.get(stem)
        if image is None:
            problems.append(f"{VOLUME_DIR.relative_to(ROOT)}/{stem}.png: missing "
                            f"for {name}")
            continue
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                target = folder / f"{name}.png"
                tile = resize(image, size * factor)
                if write:
                    folder.mkdir(parents=True, exist_ok=True)
                    save_png(tile, target)
                    written += 1
                elif not matches_png(tile, target):
                    problems.append(f"{target.relative_to(ROOT)}: not this artwork - "
                                    f"run make_theme_devices.py")
        wrapper = SCALABLE / f"{name}.svg"
        text = svg_wrapper(image, name)
        if write:
            SCALABLE.mkdir(parents=True, exist_ok=True)
            save_text(text, wrapper)
            written += 1
        elif not wrapper.is_file() or wrapper.read_text() != text:
            problems.append(f"{wrapper.relative_to(ROOT)}: not this artwork - "
                            f"run make_theme_devices.py")
    return written


def check_catalogue(problems: list[str]) -> None:
    """Every artwork stem used is catalogued, and every record is used.

    The catalogue is what ``library/README.org`` documents, so a record nothing
    maps to is a claim about the pack that is not true, and a stem the table
    uses without a record is an uncleared mark.  Both are drift.

    A colourway is not a record of its own: it is cut from catalogued artwork
    at build time (``VOLUME_ALTS``), so only the stems drawn from a file in
    ``library/volumes`` have to be catalogued, and every colourway has to name
    a source that is.
    """
    records = catalogue()
    used = set(VOLUMES.values())
    drawn = used - set(VOLUME_ALTS)
    for stem in sorted(drawn - set(records)):
        problems.append(f"library/volumes.json: {stem} is used but not catalogued")
    for stem in sorted(set(records) - drawn):
        problems.append(f"library/volumes.json: {stem} is catalogued but unused")
    for stem, (source, *_rest) in sorted(VOLUME_ALTS.items()):
        if stem in used and source not in records:
            problems.append(f"{stem}: cut from {source}, which is not catalogued")
    for stem, record in sorted(records.items()):
        path = LIBRARY / record["file"]
        if not path.is_file():
            problems.append(f"{record['file']}: catalogued but missing")
            continue
        with Image.open(path) as image:
            if image.size != (record["native"], record["native"]):
                problems.append(f"{record['file']}: {image.size[0]} px, catalogue "
                                f"says {record['native']}")


def install(write: bool) -> tuple[int, list[str]]:
    problems: list[str] = []
    check_catalogue(problems)
    if any("is used but not catalogued" in problem for problem in problems):
        # Without a record the artwork is not cleared to ship; stop before it lands.
        return 0, problems
    written = write_names(problems, write)
    return written, problems


def check() -> list[str]:
    """Every mapped device in the theme, as ``library/volumes`` intends it.

    Called by ``check_theme.py``, so ``maak check`` covers the era volumes the
    same way it covers the symbolic layer and the variants.
    """
    problems: list[str] = []
    check_catalogue(problems)
    if any("used but not catalogued" in problem for problem in problems):
        return problems
    write_names(problems, write=False)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report drift instead of writing")
    args = parser.parse_args(argv)

    if args.check:
        problems = check()
        written = 0
    else:
        written, problems = install(True)

    if problems:
        for problem in problems[:40]:
            print(f"  {problem}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more", file=sys.stderr)
        print(f"\n{len(problems)} device problem(s)", file=sys.stderr)
        return 1
    if args.check:
        print(f"ok: {len(VOLUMES)} device(s) match the era volumes in "
              f"library/volumes")
    else:
        print(f"devices: {len(VOLUMES)} name(s) dressed as the era drew them, "
              f"{len(VOLUME_ALTS)} colourway(s), {written} file(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
