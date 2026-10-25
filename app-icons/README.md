# Application icons

One skeuomorphic icon per GUI application — 251 of them: the 164 installed on the machine that built
this set, discovered from the freedesktop desktop entries, plus a roster of programs that a desktop is
likely to have whether or not that machine does (Chromium, VS Code, Obsidian, Lutris, GParted, …).

```
app-icons/
  index.json            one record per app: desktop file, categories, object, hue
  contact-sheet.png     all of them at 256 px
  <slug>/
    icon-16.png … icon-1024.png
    icon.svg            only for the five hand-authored apps (copied from svg/)
```

## How the list is produced

`tools/make_app_icons.py` reads every `.desktop` entry from

```
/usr/share/applications  /usr/local/share/applications  ~/.local/share/applications
~/.local/share/flatpak/exports/share/applications  /var/lib/flatpak/exports/share/applications
/var/lib/snapd/desktop/applications
```

skips `NoDisplay=true` and non-`Application` entries, and de-duplicates by name (system entries win over
flatpak ones). Trailing version numbers (`2026.2.6`, `5.2`, `Patch 1`) are stripped so slugs stay stable
across upgrades — `IntelliJ IDEA 2026.2.3` → `intellij-idea`.

```sh
python3 tools/make_app_icons.py --list              # print the table (name → object, hue)
python3 tools/make_app_icons.py                     # build everything (~2 min, 10 workers)
python3 tools/make_app_icons.py --only GIMP VLC
```

The roster travels with the artwork so a user on Fedora or Arch meets the same icons as one on
openSUSE: `ROSTER` in `tools/skeu/apps.py` lists the programs and *every name they answer to*, and is
unioned with whatever discovery finds. `EXTRA_NAMES` does the same for spellings of apps that are
drawn anyway — `gnome-calculator` next to `org.gnome.Calculator`, `eog` next to `org.gnome.Loupe`,
`firefox-esr`, `google-chrome-stable`, `transmission-gtk`.

## How each app is designed

No icon mask, no squircle, no monogram on a coloured disc: every icon is **one physical object**,
rendered by the relief renderer in `tools/skeu/` (silhouette → height field → one key light → material),
with a tight contact shadow and a cast shadow that fades before the canvas edge.

1. **Hand-authored where it already exists.** `1Password`, `Emacs`, `Emacs (Client)`, `IntelliJ IDEA`
   and `Signal` reuse the vectors in `svg/` — no reason to re-invent a design we already made.
2. **Object by function** — a terminal is a CRT shell with the prompt lit in its glass; a browser is a
   steel desk globe with one enamelled band; mail is a laid-paper envelope with a wax seal; chat is a
   stitched enamel speech bubble; video editors get a slate or a film reel; IDEs a key on a milled
   plinth; databases a brass-handled card catalogue; package managers a crate or a display case; games a
   cartridge, a chess piece or a rack of playing tiles; documents an open book, a pad or a typewriter.
   Music is deliberately split by *how it is played*: an amberol-era player is a brass-horn gramophone,
   a tape-based one a smoked cassette, a tuner a chrome tuning fork, an equaliser-style player a pair of
   headphones, and only the album-oriented players keep a sleeve.
3. **No borrowed ancestry, no borrowed palette** — the GTK and GNOME apps get their own
   subjects rather than a recoloured sprite: extensions a jigsaw piece, image viewing a chrome loupe
   over a print, system load a benchtop oscilloscope, colour management a glass prism, painting a dented
   paint tube, vector drawing a fountain-pen nib, torrents a horseshoe magnet, package storage a loaded
   pallet, virtual machines stacked glass cubes, VNC a screen with a keyboard and a patch lead,
   minesweeper a moored mine, sudoku a squared pad and a pencil. Two apps only share an object family
   when the job really is the same.
4. **Accent, not body** — the body is anodised aluminium, chrome, gunmetal, ivory, paper, leather or
   wood. The brand hue is carried by one glass gem, enamel panel or painted detail covering roughly a
   tenth of the icon, so the set stays bright and mostly colourless next to the neutral body it sits on.
5. **Detail where it belongs** — knurling, screws, seams, wire binding, stitching, printed rules: at
   least 3 px wide at 1024 px so it survives the 32 px render.

The mapping lives in `tools/skeu/apps.py` (`APP_ICONS`), one line per app:

```python
"Calculator": (D.desk_calculator, dict(hue=206)),   # object, accent
"Alacritty":  (D.terminal, dict(hue=192)),
```

Apps without an explicit entry fall through category `RULES` (browser, terminal, player, office,
graphics, game, security, network, system, utility) and then to a neutral object — never a letter on a
disc. `design()` in that module is the whole policy.

## Notes

* `Emacs (Client)` deliberately shares the Emacs icon; `Myrlyn (read‑only)` shares Myrlyn's design
  (different slug, so both exist).
* Runs of related apps share an object family only where the function is identical (terminals are
  CRTs, editors key-caps) — the differences are the glyph struck into the key, the material, the shape
  of the cap and the accent. Related applications keep that family resemblance on purpose: terminals
  look alike. Everything else was split apart: the seven music players no longer share one sleeve, the six
  puzzle games no longer share one tile rack, and the four remote-desktop clients are screens with
  keyboards rather than four identical monitors.
* At 16 px an icon reduces to its silhouette plus one internal shape; anything finer is detail that
  only appears from 32 px up.
* Icons are generated artwork in the pack's skeuomorphic style; app names and marks belong to their
  owners, and the artwork itself is released under CC BY-SA 4.0 (see [`LICENSE`](../LICENSE)).
