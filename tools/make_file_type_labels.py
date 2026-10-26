#!/usr/bin/env python3
"""Repaint the printed word on a file-type icon.

The mimetype artwork is drawn elsewhere and committed as bitmaps: a page or a
carton with one word printed across the bottom (``PNG``, ``PDF``, ``ZIP``,
``AI``, ``DVD``).  A handful of names were filed under a document that prints
the wrong word, because they were hardlinked to a neighbour's artwork:

* ``image-svg+xml``, ``application-x-svg`` and ``application-x-svgz`` were the
  Illustrator page, so an SVG file announced itself as ``AI``;
* ``application-x-iso`` was the disc-image page, so an ISO announced itself as
  ``DVD``.

This programme repaints that one word instead of redrawing the object: it finds
the label as the bottom-most short run of ink on the sheet, rebuilds the paper
underneath from the rows above and below the letters, and prints the new word in
the same place, weight and letterpress.  Everything else in the bitmap - the
photographs, the disc, the fold, the shadow - is untouched.

The letterforms come from a mask rendered large and scaled down, so the small
sizes get the same anti-aliased shape the pack's own labels have instead of a
six-pixel hinting accident.

    python3 tools/make_file_type_labels.py            # repaint the labels
    python3 tools/make_file_type_labels.py --check    # report what is wrong

The ``scalable/`` SVG for each name is rewritten too, since it wraps the 512 px
bitmap.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_theme_mimes import svg_wrapper  # noqa: E402

THEME = ROOT / "skeu-icons"
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "mimetypes"

FONT = "/usr/share/fonts/truetype/DejaVuSans-Bold.ttf"

#: The word each name should print, and the neighbour whose artwork it was
#: filed under.  The neighbour is only used by ``--check``: a target that is
#: still the same inode as it has not been repainted.
WORDS: dict[str, tuple[str, str]] = {
    "image-svg+xml": ("SVG", "application-illustrator"),
    "application-x-svg": ("SVG", "application-illustrator"),
    "application-x-svgz": ("SVG", "application-illustrator"),
    "application-x-iso": ("ISO", "application-x-cd-image"),
}


def read(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.array(image.convert("RGBA")).astype(np.float32)


def save(array: np.ndarray, path: Path) -> None:
    """Write through a temporary name so a hardlink is broken, not shared."""
    temporary = path.with_name(path.name + ".new")
    Image.fromarray(array.clip(0, 255).astype(np.uint8), "RGBA").save(
        temporary, format="PNG")
    temporary.replace(path)


def page_box(array: np.ndarray) -> tuple[int, int, int, int]:
    """The opaque sheet the label is printed on."""
    ys, xs = np.nonzero(array[..., 3] > 200)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def plausible(box: tuple[int, int, int, int],
              page: tuple[int, int, int, int]) -> bool:
    """Whether BOX is where a printed word can be: centred, near the bottom."""
    x0, y0, x1, y1 = box
    px0, py0, px1, py1 = page
    width, height = px1 - px0 + 1, py1 - py0 + 1
    if y1 - y0 + 1 < 1 or x1 - x0 + 1 < 1:
        return False
    if y0 < py0 + 0.55 * height:
        return False
    if abs((x0 + x1) / 2 - (px0 + px1) / 2) > 0.12 * width:
        return False
    return 0.6 <= (x1 - x0 + 1) / (y1 - y0 + 1) <= 5.0


def label_box(array: np.ndarray) -> tuple[int, int, int, int] | None:
    """Bounding box of the printed word: the bottom-most short run of ink."""
    grey = array[..., :3].mean(axis=2)
    alpha = array[..., 3]
    x0, y0, x1, y1 = page_box(array)
    width, height = x1 - x0 + 1, y1 - y0 + 1
    inset_x, inset_y = max(2, int(width * 0.06)), max(2, int(height * 0.05))
    left, right = x0 + inset_x, x1 - inset_x
    top, bottom = y0 + inset_y, y1 - int(height * 0.04)
    sheet = grey[top:bottom + 1, left:right + 1]
    opaque = alpha[top:bottom + 1, left:right + 1] > 200
    tone = np.array([np.median(row[opaque[i]]) if opaque[i].any() else 255.0
                     for i, row in enumerate(sheet)])
    ink = (sheet < (tone[:, None] - 45)) & opaque
    # A row that is mostly ink is a photograph, the disc or the sheet's edge.
    ink[ink.sum(axis=1) > 0.70 * (right - left)] = False
    rows = np.nonzero(ink.any(axis=1))[0]
    if not len(rows):
        return None
    groups, current = [], [rows[0]]
    for row in rows[1:]:
        if row - current[-1] <= 2:
            current.append(row)
        else:
            groups.append(current)
            current = [row]
    groups.append(current)
    for group in reversed(groups):  # bottom-most run short enough to be type
        run = group[-1] - group[0] + 1
        if 0.02 * height <= run <= 0.25 * height:
            band = ink[group[0]:group[-1] + 1]
            columns = np.nonzero(band.any(axis=0))[0]
            box = (left + int(columns.min()), top + int(group[0]),
                   left + int(columns.max()), top + int(group[-1]))
            if plausible(box, (x0, y0, x1, y1)):
                return box
    return None


def ink_colour(array: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
    """The colour the old word was printed in."""
    x0, y0, x1, y1 = box
    patch = array[y0:y1 + 1, x0:x1 + 1]
    grey = patch[..., :3].mean(axis=2)
    darkest = grey <= np.percentile(grey.ravel(), 12)
    mask = darkest & (patch[..., 3] > 200)
    if not mask.any():
        return np.array([92.0, 96.0, 102.0])
    return np.median(patch[mask][:, :3], axis=0)


def erase(array: np.ndarray, box: tuple[int, int, int, int]) -> np.ndarray:
    """Rebuild the sheet under the word from the rows above and below it.

    The samples stay inside the sheet: a row past its bottom edge is the cast
    shadow, and blending towards it drags a grey band down the page.
    """
    px0, py0, px1, py1 = page_box(array)
    pad_y = max(1, round((py1 - py0 + 1) * 0.02))
    # The old word's softest edge and its letterpress halo reach past the ink
    # box; take a little of the sheet on either side or a fragment survives.
    pad_x = max(2, round((px1 - px0 + 1) * 0.02))
    left, right = max(px0 + 1, box[0] - pad_x), min(px1 - 1, box[2] + pad_x)
    top, bottom = max(py0 + 1, box[1] - pad_y), min(py1 - 1, box[3] + pad_y)
    above = array[top - 1].copy() if top - 1 >= py0 else array[top].copy()
    below = array[bottom + 1].copy() if bottom + 1 <= py1 else above.copy()
    span = max(1, (bottom + 1) - (top - 1))
    for row in range(top, bottom + 1):
        t = (row - (top - 1)) / span
        array[row, left:right + 1] = (above[left:right + 1] * (1 - t)
                                      + below[left:right + 1] * t)
    return array


def word_mask(word: str, height: int) -> Image.Image:
    """WORD as an anti-aliased ink mask exactly HEIGHT pixels tall."""
    # Render big and scale down: six-pixel type drawn directly is a smudge.
    big = max(64, height * 8)
    font = ImageFont.truetype(FONT, big)
    canvas = Image.new("L", (big * (len(word) + 2), big * 2), 0)
    ImageDraw.Draw(canvas).text((big, big // 2), word, font=font, fill=255)
    bbox = canvas.getbbox()
    if bbox is None:
        raise SystemExit(f"{word}: the font produced no ink")
    mask = canvas.crop(bbox)
    scale = height / mask.height
    return mask.resize((max(1, round(mask.width * scale)), height), Image.LANCZOS)


def print_word(array: np.ndarray, mask: Image.Image, box: tuple[int, int, int, int],
               colour: np.ndarray) -> np.ndarray:
    """Lay MASK over the sheet, centred where the old word was."""
    page = page_box(array)
    centre_x = (page[0] + page[2]) / 2
    width, height = mask.size
    left = int(round(centre_x - width / 2))
    top = int(round((box[1] + box[3]) / 2 - height / 2))
    weights = np.array(mask).astype(np.float32) / 255.0
    ink = np.array([colour[0], colour[1], colour[2], 255.0], dtype=np.float32)
    light = np.array([min(255.0, c + 74.0) for c in colour] + [255.0], dtype=np.float32)
    offset = max(1, round(height * 0.06))
    for dy, layer, strength in ((offset, light, 0.55), (0, ink, 1.0)):
        for y in range(height):
            row = top + y + dy
            if not 0 <= row < array.shape[0]:
                continue
            for x in range(width):
                column = left + x
                if not (page[0] <= column <= page[2] and page[1] <= row <= page[3] - 1):
                    continue
                if array[row, column, 3] < 200:
                    continue
                weight = weights[y, x] * strength
                if weight <= 0.02:
                    continue
                array[row, column, :4] = (array[row, column, :4] * (1 - weight)
                                          + layer * weight)
    return array


def source(name: str, alias: str, size: str) -> Path:
    """The pristine artwork NAME was filed under, at SIZE.

    Always repaint from the neighbour's bitmap, never from a previous run's
    output: reading our own result makes every re-run erase and reprint on top
    of the last pass, and the small sizes slowly lose their word that way.
    """
    path = THEME / size / CONTEXT / f"{name}.png"
    neighbour = THEME / size / CONTEXT / f"{alias}.png"
    if neighbour.is_file() and not (path.exists()
                                    and path.samefile(neighbour)):
        return neighbour
    return path


def relabel(name: str, word: str, size: str, alias: str) -> np.ndarray | None:
    """The artwork for NAME at SIZE, with its printed word repainted.

    ``None`` when the size carries no legible word - below about 24 px the
    artwork only has a grey smudge there, and erasing it would cost more than
    the wrong word does.
    """
    array = read(source(name, alias, size))
    box = label_box(array)
    if box is None:
        return None
    cap = box[3] - box[1] + 1
    colour = ink_colour(array, box)
    array = erase(array, box)
    return print_word(array, word_mask(word, cap), box, colour)


def targets() -> list[tuple[str, str, str, str]]:
    """``[(name, size directory, word, alias)]`` for every bitmap to repaint."""
    out: list[tuple[str, str, str, str]] = []
    for name, (word, alias) in WORDS.items():
        for size in SIZES:
            for suffix in ("", "@2x"):
                directory = f"{size}x{size}{suffix}"
                if (THEME / directory / CONTEXT / f"{name}.png").is_file():
                    out.append((name, directory, word, alias))
    return out


def write_scalable(name: str, word: str) -> None:
    """Rewrite the scalable SVG, which wraps the 512 px bitmap.

    Remove the old path first, whether it is a symlink to another name or a
    hardlink to an icon that the app themes share: writing through it would
    relabel the Illustrator and disc media icons along with this one.
    """
    with Image.open(THEME / "512x512" / CONTEXT / f"{name}.png") as master:
        wrapped = svg_wrapper(master.convert("RGBA"), word)
    path = THEME / "scalable" / CONTEXT / f"{name}.svg"
    if os.path.lexists(path):
        path.unlink()
    path.write_text(wrapped)


def check() -> list[str]:
    """Problems with the repainted labels, as sentences."""
    problems: list[str] = []
    for name, (word, alias) in WORDS.items():
        for size in SIZES:
            for suffix in ("", "@2x"):
                directory = f"{size}x{size}{suffix}"
                path = THEME / directory / CONTEXT / f"{name}.png"
                if not path.is_file():
                    problems.append(f"{path.relative_to(ROOT)}: missing")
                    continue
                box = label_box(read(path))
                if box is None:
                    continue  # too small to print a legible word
                neighbour = THEME / directory / CONTEXT / f"{alias}.png"
                if neighbour.is_file() and path.stat().st_ino == neighbour.stat().st_ino:
                    problems.append(f"{path.relative_to(ROOT)}: still the "
                                    f"{alias} artwork")
                    continue
                if box[3] - box[1] + 1 < 4:
                    continue  # three pixels of type cannot be measured
                have = (box[2] - box[0] + 1) / (box[3] - box[1] + 1)
                want = word_mask(word, 100)
                want = want.width / want.height
                if abs(have - want) > 0.12 * want:
                    problems.append(f"{path.relative_to(ROOT)}: the printed word "
                                    f"is {have:.1f}x as wide as it is tall, "
                                    f"{word!r} is {want:.1f}x")
        scalable = THEME / "scalable" / CONTEXT / f"{name}.svg"
        if not scalable.is_file():
            problems.append(f"{scalable.relative_to(ROOT)}: missing")
        elif scalable.stat().st_nlink > 1:
            problems.append(f"{scalable.relative_to(ROOT)}: shares its file with "
                            f"another icon, so repainting it relabels that "
                            f"one too")
        elif word not in scalable.read_text()[:400]:
            problems.append(f"{scalable.relative_to(ROOT)}: does not wrap the "
                            f"{word} bitmap")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report what is wrong instead of painting")
    args = parser.parse_args(argv)
    if args.check:
        problems = check()
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} problem(s) found", file=sys.stderr)
            return 1
        print("ok: the relabelled file types print their own word")
        return 0
    painted = skipped = 0
    for name, directory, word, alias in targets():
        repainted = relabel(name, word, directory, alias)
        if repainted is None:
            skipped += 1
            continue
        save(repainted, THEME / directory / CONTEXT / f"{name}.png")
        painted += 1
    for name, (word, _alias) in WORDS.items():
        write_scalable(name, word)
    print(f"labels: {painted} bitmap(s) repainted, {skipped} too small to print, "
          f"{len(WORDS)} scalable icon(s) rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
