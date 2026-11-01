#!/usr/bin/env python3
"""Fill the generic file-type slots and link the near-miss mimetype names.

Two problems keep a file type from finding its artwork:

* **The generics are absent.**  A toolkit does not look up ``application/x-xz-
  compressed-tar`` and give up - it walks a chain, and for archives every step
  of that chain ends at ``package-x-generic``.  The theme shipped ``text``,
  ``image``, ``audio``, ``video`` and ``font`` generics but no package and no
  ``application-x-generic`` at all, so every tar, deb, cab and unknown binary
  fell through to Adwaita's symbolic icon - the monochrome shapes in the tray.
* **The name drifted.**  ``application-vnd.rar`` is what GIO asks for; the pack
  has ``application-vnd-rar``.  One character, no icon.  The same goes for the
  tar-compressor families: ``.tar.xz`` asks for ``application-x-xz-compressed-
  tar``, which the pack never drew, so it is linked to the xz artwork.

``package-x-generic`` is derived from the pack's own archive artwork
(``application-x-tar``) by lifting its printed label off the page, so the
generic belongs to the same family as the specific icons instead of looking
like a stranger.

    python3 tools/make_theme_mimes.py            # draw the generics + link names
    python3 tools/make_theme_mimes.py --check    # report gaps, write nothing
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_skeu import resize  # noqa: E402

THEME = ROOT / "skeu-icons"
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "mimetypes"

#: The page every specific archive icon in the pack is built on.
SOURCE = "application-x-tar"

#: Names to fill in, and the file their artwork lives in (paths are relative to
#: the mimetypes folder).  ``None`` means "draw it from SOURCE".
GENERICS: dict[str, str | None] = {
    "package-x-generic": None,
    # A plain file of unknown kind is a document, not a carton.
    "application-x-generic": "text-x-generic.png",
    "application-octet-stream": "text-x-generic.png",
    # The generic for every inode without art of its own (empty file, socket,
    # device node) is a plain sheet, not a folder: a directory already asks for
    # ``inode-directory``, which lives in places/.
    "inode-x-generic": "text-x-generic.png",
    # Families GIO routes every member of through one generic name.  Without
    # it the whole family lands in Adwaita's monochrome set.
    "text-x-generic-template": "text-x-generic.png",
    "multipart-x-generic": "text-x-generic.png",
    "message-rfc822": "text-x-generic.png",
    "model-x-generic": "image-x-generic.png",
    "application-x-addon": "application-x-executable.png",
    # Removable media (a CD, a phone, an install DVD) shares the disc art.
    "x-content-x-generic": "../devices/media-optical.png",
}

#: The pack has better art than the generic for these - the name just drifted.
ALIASES: dict[str, str] = {
    "application-x-bzip2-compressed-tar": "application-x-bzip-compressed-tar.png",
    "application-x-bzip1-compressed-tar": "application-x-bzip-compressed-tar.png",
    "application-x-bzip3-compressed-tar": "application-x-bzip-compressed-tar.png",
    "application-vnd.rar": "application-vnd-rar.png",
    "application-vnd.bzip3": "application-x-bzip.png",
    "application-x-bzip1": "application-x-bzip.png",
    "application-x-bzip3": "application-x-bzip.png",
    # Mail archives are text files of messages; the drawn sheet beats Adwaita's
    # emblem, which is the only other name in their chain.
    "application-mbox": "text-x-generic.png",
    "message-x-gnu-rmail": "text-x-generic.png",
    "application-vnd.stardivision.mail": "text-x-generic.png",
    "application-x-starmail": "text-x-generic.png",
    # The package managers ask for a dotted name; the pack drew the dashed one.
    "application-vnd.debian.binary-package": "application-x-deb.png",
    "application-vnd.appimage": "application-x-appimage.png",
    "application-vnd.efi.iso": "application-x-iso.png",
    "application-vnd.efi.img": "application-x-img.png",
    "application-x-tarz": "application-x-compressed-tar.png",
    "application-x-archive": "application-x-tar.png",
    "application-x-ustar": "application-x-tar.png",
    # A tar changes only its compressor, so reuse the compressor's own artwork:
    # GIO asks for these names for .tar.xz, .tar.zst and friends, and without
    # them the whole chain ends at package-x-generic.
    "application-x-xz-compressed-tar": "application-x-xz.png",
    "application-x-zstd-compressed-tar": "application-x-zst.png",
    "application-x-lz4-compressed-tar": "application-x-lz4.png",
    "application-x-lzma-compressed-tar": "application-x-lzma.png",
    "application-x-brotli-compressed-tar": "application-x-compressed-tar.png",
    "application-x-lzip-compressed-tar": "application-x-compressed-tar.png",
    "application-x-lrzip-compressed-tar": "application-x-compressed-tar.png",
    "application-x-rzip-compressed-tar": "application-x-compressed-tar.png",
    # ... and a lone .lz, .lrz, .rz or .br is the same compressor without the
    # tar, so it gets the same carton rather than falling to the generic one.
    "application-x-lzip": "application-x-compressed-tar.png",
    "application-x-lrzip": "application-x-compressed-tar.png",
    "application-x-rzip": "application-x-compressed-tar.png",
    "application-x-brotli": "application-x-compressed-tar.png",
    "application-x-compress": "application-gzip.png",
    # These three are the same drift in a different direction: the pack drew
    # the dashed spelling, GIO asks for the vendor one.
    "application-x-xpinstall": "application-x-xpi.png",
    "application-vnd.snap": "application-x-snap.png",
    "application-vnd.flatpak": "application-x-appimage.png",
    # The media families drifted the other way: the pack filed its artwork
    # under the old ``application/x-<subtype>`` spelling and GIO now asks for
    # ``<family>-<subtype>``, so a .flac in Nautilus fell all the way back to
    # audio-x-generic.  Found by tools/check_mapping.py, which maps real file
    # names through GIO and reports what each one would draw.
    "audio-flac": "audio-x-flac.png",
    "audio-mp2": "application-x-mp2.png",
    "audio-webm": "application-x-webm.png",
    "video-matroska": "video-x-matroska.png",
    "image-apng": "application-x-apng.png",
    "image-ktx": "application-x-ktx.png",
    "image-heif": "application-x-heif.png",
    "image-jpx": "application-x-jpx.png",
    "image-vnd.microsoft.icon": "image-vnd-microsoft-icon.png",
    "font-woff2": "application-x-woff2.png",
    "model-obj": "application-x-obj.png",
    "application-json5": "application-x-json5.png",
    # Source code: the text family, not the application one.
    "text-rust": "text-x-rust.png",
    "text-javascript": "text-x-javascript.png",
    "text-julia": "text-x-julia.png",
    "text-tcl": "text-x-tcl.png",
    "text-org": "text-x-org.png",
    "text-x-common-lisp": "application-x-lisp.png",
}


def strip_label(image: Image.Image) -> Image.Image:
    """Lift the printed label off the page, leaving the object standing.

    The label is flat grey type on flat paper, so every letter pixel is
    repainted with the paper colour at that row.  The paper colour is taken
    from the nearest *bright* pixel on either side of the letter in the same
    row, then blended across, so the page's vertical shading survives; the
    letters never end up darker than the page they sit on.  Only the letter
    pixels are touched - a blanket rectangle would eat the bottom of the box.
    """
    a = np.array(image.convert("RGBA")).astype(np.float32)
    height, width = a.shape[:2]
    red, blue = a[..., 0], a[..., 2]
    alpha = a[..., 3]

    cardboard = (red - blue > 18) & (alpha > 200)
    rows = np.nonzero(cardboard.any(axis=1))[0]
    if not len(rows):
        raise SystemExit(f"{SOURCE}: could not find the artwork in the page")
    band = a[int(rows.max()) + 3:height - 4]

    opaque = band[..., 3] > 200
    grey = band[..., :3].mean(axis=2)
    # Ignore the page's own cut edge and cast shadow at either side of a row;
    # the label lives well inside them.
    interior = np.zeros_like(opaque)
    for y in range(opaque.shape[0]):
        columns = np.nonzero(opaque[y])[0]
        if len(columns) > 24:
            interior[y, columns.min() + 8:columns.max() - 7] = True
    if not interior.any():
        return image

    # Type is whatever sits well below the page's own tone in a row; the row
    # median is that tone, because the label covers only a fraction of it.
    tone = np.full(opaque.shape[0], 255.0)
    for y in np.nonzero(interior.any(axis=1))[0]:
        tone[y] = float(np.median(grey[y, interior[y]]))
    letters = (grey < tone[:, None] - 30) & opaque & interior
    if not letters.any():
        return image

    # Grow the letters by two pixels so the anti-aliased fringe goes with them.
    grown = letters.copy()
    for dy in (-2, -1, 1, 2):
        grown |= np.roll(letters, dy, axis=0)
    for dx in (-2, -1, 1, 2):
        grown |= np.roll(letters, dx, axis=1)
    grown &= interior & opaque

    # Nearest untouched page pixel to the left and to the right, per row.
    page = ~grown & opaque & interior
    index = np.arange(width)
    left = np.where(page, index, -1)
    left = np.maximum.accumulate(left, axis=1)
    right = np.where(page, index, width)
    right = np.minimum.accumulate(right[:, ::-1], axis=1)[:, ::-1]

    rows_with_letters = np.nonzero(grown.any(axis=1))[0]
    for y in rows_with_letters:
        columns = np.nonzero(grown[y])[0]
        usable = (left[y, columns] >= 0) & (right[y, columns] < width)
        columns = columns[usable]
        if not len(columns):
            continue
        x0, x1 = left[y, columns], right[y, columns]
        span = np.maximum(1, x1 - x0)
        t = ((columns - x0) / span)[:, None]
        band[y, columns, :3] = (band[y, x0, :3] * (1 - t)
                                + band[y, x1, :3] * t)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def svg_wrapper(png: Image.Image, title: str) -> str:
    """The same shape the pack's other scalable mimetypes use: a PNG in an SVG."""
    buffer = io.BytesIO()
    png.save(buffer, format="PNG", optimize=True)
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
            "<svg xmlns=\"http://www.w3.org/2000/svg\" "
            "xmlns:xlink=\"http://www.w3.org/1999/xlink\" version=\"1.1\" "
            "width=\"512\" height=\"512\" viewBox=\"0 0 512 512\">\n"
            f"  <title>{title}</title>\n"
            "  <image x=\"0\" y=\"0\" width=\"512\" height=\"512\" "
            "preserveAspectRatio=\"none\" xlink:href=\"data:image/png;base64,"
            f"{data}\"/>\n</svg>\n")


def draw_generic(write: bool) -> list[str]:
    """Derive ``package-x-generic`` from the archive page and install it."""
    problems: list[str] = []
    master_path = THEME / "512x512" / CONTEXT / f"{SOURCE}.png"
    with Image.open(master_path) as source:
        page = strip_label(source.convert("RGBA"))
    if not write:
        for size in SIZES:
            for suffix in ("", "@2x"):
                path = THEME / f"{size}x{size}{suffix}" / CONTEXT / "package-x-generic.png"
                if not path.is_file():
                    problems.append(f"{path.relative_to(ROOT)}: missing")
        return problems

    for size in SIZES:
        for suffix, factor in (("", 1), ("@2x", 2)):
            folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
            folder.mkdir(parents=True, exist_ok=True)
            resize(page, size * factor).save(folder / "package-x-generic.png")
    scalable = THEME / "scalable" / CONTEXT / "package-x-generic.svg"
    scalable.parent.mkdir(parents=True, exist_ok=True)
    scalable.write_text(svg_wrapper(page, "Package"))
    return problems


def link(path: Path, target: str, problems: list[str], write: bool) -> bool:
    """Make PATH a relative symlink to TARGET; never replace real artwork."""
    if path.is_symlink():
        if os.readlink(path) == target:
            return False
        if not write:
            problems.append(f"{path.relative_to(ROOT)}: points at {os.readlink(path)}")
            return False
        path.unlink()
    elif path.exists():
        return False
    if write:
        path.symlink_to(target)
    return write


def link_names(write: bool) -> tuple[int, list[str]]:
    """Link every alias to its artwork, at every size and in ``scalable``."""
    problems: list[str] = []
    made = 0
    table = {name: target for name, target in GENERICS.items() if target}
    table.update(ALIASES)
    for alias, target in table.items():
        for size in SIZES:
            for suffix in ("", "@2x"):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                path = folder / f"{alias}.png"
                if not write and not path.exists() and not path.is_symlink():
                    problems.append(f"{path.relative_to(ROOT)}: missing")
                target_file = folder / target
                if not target_file.is_file():
                    problems.append(f"{target_file.relative_to(ROOT)}: target missing")
                    continue
                if write and link(path, target, problems, write):
                    made += 1
        # A crisp alias for the 96 px-and-up lookups, when the target ships one.
        if "/" not in target:
            scalable = THEME / "scalable" / CONTEXT
            source = scalable / f"{Path(target).stem}.svg"
            if source.is_file() and write:
                if link(scalable / f"{alias}.svg", source.name, problems, write):
                    made += 1
    return made, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report what is missing instead of writing")
    args = parser.parse_args(argv)
    write = not args.check

    problems = draw_generic(write)
    made, more = link_names(write)
    problems += more
    if problems:
        for problem in problems[:40]:
            print(f"  {problem}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more", file=sys.stderr)
        print(f"\n{len(problems)} mimetype problem(s)", file=sys.stderr)
        return 1
    if write:
        print(f"mimetypes: package-x-generic drawn, {made} alias link(s) added")
    else:
        print("ok: generic mimetypes and alias names are in the theme")
    return 0


if __name__ == "__main__":
    sys.exit(main())
