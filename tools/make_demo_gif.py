#!/usr/bin/env python3
"""Render the animated demo the README opens with: docs/demo.gif.

The pack is thirty themes that differ only in their folder enamel, so the demo
shows exactly that - one row of icons standing on the same paper the contact
sheets use, with the folder changing colour theme by theme.  Nothing is
redrawn: the frames are the committed PNGs, arranged.

    python3 tools/make_demo_gif.py          # -> docs/demo.gif

Deliberately small and loopable (a dozen frames, an adaptive palette), because
it sits at the top of the README and loads before anything else does.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_doc_images import (  # noqa: E402
    DIM,
    FONT,
    FONT_BOLD,
    INK,
    background,
    place,
)

BASE = ROOT / "skeu-icons" / "256x256"
OUT = ROOT / "docs" / "demo.gif"

SIZE = (1200, 420)
ICON = 176
MARGIN = 84

#: A GIF holds 256 colours.  The paper ramp is posterised to this many tones
#: first, so its shading is a set of exact palette entries - quantise a smooth
#: gradient straight into 256 colours and the leftover levels draw contour
#: lines across the sheet - and the rest of the palette stays for the icons.
TONES = 32

#: The enamels, in the order the pack names them.
ACCENTS = ("red", "orange", "yellow", "lime", "green", "teal", "cyan",
           "blue", "indigo", "violet", "magenta", "pink", "brown", "graphite")

#: The row is the folder plus four objects every desktop shows.  Only the
#: folder changes between frames: that is what an accent theme is.
ROW = (("mimetypes", "text-x-generic"),
       ("mimetypes", "application-zip"),
       ("mimetypes", "image-x-generic"),
       ("apps", "firefox"))


def icon(context: str, name: str, pixels: int = ICON) -> Image.Image:
    """One committed icon, scaled for the stage."""
    path = BASE / context / f"{name}.png"
    with Image.open(path) as source:
        return source.convert("RGBA").resize((pixels, pixels), Image.LANCZOS)


def stage(accent: str) -> Image.Image:
    """One frame: the row with that accent, and the theme name under it."""
    canvas = (background(*SIZE).convert("RGB")
              .quantize(colors=TONES, dither=Image.NONE)
              .convert("RGBA"))
    sprites = [icon("places", f"folder-{accent}")]
    sprites += [icon(context, name) for context, name in ROW]

    step = (SIZE[0] - 2 * MARGIN) / len(sprites)
    top = (SIZE[1] - ICON) // 2 - 26
    for index, sprite in enumerate(sprites):
        left = int(MARGIN + step * (index + 0.5) - sprite.width / 2)
        place(canvas, sprite, left, top)

    draw = ImageDraw.Draw(canvas)
    draw.text((MARGIN, 34), "Skeu Icons", font=ImageFont.truetype(FONT_BOLD, 40),
              fill=INK)
    caption = f"skeu-icons-{accent}"
    font = ImageFont.truetype(FONT, 27)
    width = draw.textlength(caption, font=font)
    draw.text(((SIZE[0] - width) / 2, SIZE[1] - 58), caption, font=font, fill=DIM)
    return canvas


def final_frame() -> Image.Image:
    """The closing card: what changed, and how many themes there are."""
    canvas = stage("blue")
    draw = ImageDraw.Draw(canvas)
    note = "fourteen enamels, thirty themes - one install"
    font = ImageFont.truetype(FONT, 23)
    width = draw.textlength(note, font=font)
    draw.text(((SIZE[0] - width) / 2, SIZE[1] - 26), note, font=font, fill=DIM)
    return canvas


def main() -> int:
    pictures = [stage(accent) for accent in ACCENTS] + [final_frame()]
    # No dither: the paper is already a handful of exact tones, so ordered noise
    # would only speckle the enamel for the sake of a gradient that is there.
    frames = [picture.convert("RGB").quantize(colors=256, dither=Image.NONE)
              for picture in pictures]
    durations = [260] * len(ACCENTS) + [1800]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=2)
    print(f"wrote {OUT.relative_to(ROOT)} "
          f"({OUT.stat().st_size / 1e6:.2f} MB, {len(frames)} frames)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
