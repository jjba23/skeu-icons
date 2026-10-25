# Hand-authored icons

Eleven app icons — **Emacs**, **IntelliJ IDEA** (two designs), **Signal**, **WhatsApp**, **1Password**
plus an `Alt` material variant of each — drawn as original vector artwork in the skeuomorphic
relief idiom and shipped in every format the pack produces. The 46
project icons in [`project-icons/`](project-icons/README.md) are generated from the same vocabulary.

```
svg/<Name>.svg                                hand-drawn vector source (1024×1024, real paths)
skeu-icons/<16…512>x<N>/apps/<slug>.png       one render per size
skeu-icons/scalable/apps/<slug>.svg           the vector itself (the theme prefers svg/ over
                                              the generated SVG wrappers, so these stay vectors)
```

Rebuild the Alt variants with:

```sh
python3 tools/make_alt_icons.py                  # derive the Alt variants from the bases
```

Requirements: `inkscape` (rasteriser) and `Pillow`.

## Design rules

This pack has **no shape mandate** — every icon is its own object, whatever silhouette that object
needs. A compass is a compass, a speech bubble a speech bubble, a paper pad a paper pad, a calculator
a calculator, an arrow-in-a-key an arrow-in-a-key, a glass puck a glass puck; only the badge icons are
chrome-rimmed discs.

So each icon here is **its own physical object**, sharing a material vocabulary rather than a
silhouette:

* enamelled faces over chrome rims (discs), milled aluminium plinths, dark glass key-caps;
* a hard specular highlight on the upper ~50 %, a soft gloss dome with a visible equator;
* inner top highlight / inner bottom shadow on every face, 1–3 px dark keyline plus a white bevel;
* two-layer cast shadows (tight contact shadow + wide ambient shadow);
* glyphs are embossed: light face gradient, dark offset shadow, no outline.

No flat colours, no centred-flat-glyph-on-gradient look, no uniform squircle grid.

## The five icons

### Emacs — chrome-rimmed purple enamel badge

Faithful: the white flowing script **E** on a purple ground is the official GNU Emacs icon (FSF,
drawn by Nicolas Petton, GPLv3+). Its geometry is reused unchanged from
[`EmacsIcon.svg`](https://commons.wikimedia.org/wiki/File:EmacsIcon.svg).
Re-created: the flat purple circle becomes an enamelled disc inside a machined chrome rim — the same
construction as this pack's other badge icons.

### IntelliJ IDEA — dark glass key-cap on a brushed aluminium plinth

Historical evidence: JetBrains' 2010s product icons were rounded tiles carrying a diagonal gradient
with the product initials in white — "IJ" for IntelliJ IDEA — while the *IntelliJ Platform* mark is the
boxed "IJ". That lettering is kept (geometric I bar + J with a hook, embossed white).
Re-imagined: a flat tile is a modern shape, so the mark sits on a **key-cap** — dark glass top,
moulded side walls, a highlight along the front lip — resting on a milled aluminium plinth, following
the same recipe as this pack's other puck icons.

### IntelliJ IDEA Xcode — chrome hammer with an enamelled handle

Asked for as "inspired by the hammer metaphor, but a little different": a **steel hammer** carries the
"beat metal into shape" idea. Kept: a forged chrome head with machined chamfers, a turned striking
face and a steel collar where the handle is socketed in. Deliberately different: the handle is
**JetBrains navy enamel**, the head carries the engraved white **IJ** maker's mark instead of a blank
face, the handle carries a riveted brass nameplate, and a small impact spark sits at the striking
face. The hammer is a free-standing object with a single cast shadow — no plate, no mask — like the
pack's other tool icons.

### Signal — enamelled Signal-blue speech bubble with a stitched outline

Historical evidence: the 2015–2018 Signal mark was a **white speech bubble with a dashed outline** on
Signal blue `#3A76F0` ([`Signal Blue Icon.png`](https://commons.wikimedia.org/wiki/File:Signal_Blue_Icon.png));
its predecessor, TextSecure/Signal, was a blue badge holding a speech bubble and keyhole
([`TextSecure Blue Icon.png`](https://commons.wikimedia.org/wiki/File:TextSecure_Blue_Icon.png)).
Re-created: the dashed outline becomes real **stitching** — an inset dashed seam with its own drop
shadow — on a glossy blue enamel bubble with an integrated, bezelled tail (one continuous outline, so
the bevel and gloss run around the tail too).

### WhatsApp — chrome-rimmed green enamel badge with white bubble and handset

Historical evidence: the 2011–2013 app icon was a green tile with a **white filled speech bubble and a
green handset** (the current mark is the same handset inside an outlined bubble). The handset geometry
is reused unchanged from the official mark
([`WhatsApp Logo green.svg`](https://commons.wikimedia.org/wiki/File:WhatsApp_Logo_green.svg)).
Re-imagined: green enamel disc with a chrome rim (the pack's established badge idiom) carrying a glossy
white bubble with the green handset embossed on it.

### 1Password — chrome-and-enamel padlock with a white keyhole

Historical evidence: 1Password has used the **keyhole** as its mark for over a decade, and its
desktop icon of the 2010s was a chrome-ringed circular badge with a blue face and a white keyhole
([`1Password icon.png`](https://commons.wikimedia.org/wiki/File:1Password_icon.png), 1024 px).
Re-imagined as the most literal skeuomorphic reading of the mark: a real **padlock** — chrome shackle,
brushed chrome frame, blue enamelled face with a gloss, white keyhole with a bevel and a cast
shadow.

## Alt variants

`tools/make_alt_icons.py` derives `… Alt` icons from the bases by re-materialing them: gradient stops
are replaced **positionally per gradient id**, so a spec cannot silently miss a recolour (it aborts if a
gradient id or stop count disagrees). Geometry is inherited, with one deliberate tweak each:

| Alt | Materials | Tweak |
|---|---|---|
| `Emacs Alt` | graphite enamel, gold script E | E set slightly larger on the face |
| `IntelliJ IDEA Alt` | pearl glass key-cap in a graphite plinth, navy IJ | inverted light-on-dark lettering |
| `Signal Alt` | midnight slate enamel, silver stitching | denser stitch spacing |
| `WhatsApp Alt` | pearl badge, emerald bubble, white handset | inverted bubble/handset, softer gloss |
| `1Password Alt` | graphite padlock, brass keyhole, darker shackle | warm keyhole bevel |

## Project icons

`project-icons/` holds one icon per personal project — 46 of them, each a free-standing physical
object chosen from what the project does (a stopwatch for the CI orchestrator, a keyring for the
secrets tool, a balance for the test framework, a funnel for the ingester), rendered by
`tools/make_project_icons.py` with the relief renderer in `tools/skeu/`. See
[`project-icons/README.md`](project-icons/README.md) for the full object table and the `--install`
option that drops a `.directory` stub into each project folder.

## Places context and coloured folders

The theme implements the freedesktop **Places** context: `skeu-icons/<size>/places/`
carries the standard names (`folder`, `inode-directory`, `user-home`, `folder-documents`,
`folder-download`, `folder-drag-accept`, `folder-saved-search`, …), `index.theme` declares
`Context=Places` plus `ScaledDirectories` for `@2x`, and the folder family ships in 14 colourways
(`folder-red`, `folder-teal-documents`, …) produced by a CIELAB recolour that keeps L\* intact so the
gloss, bevels and shadows survive. Details, name table and the palette live in
[`PLACES.md`](PLACES.md).

## Installed-application icons

`app-icons/` holds one icon per **installed GUI application** on this machine — 164 of them, discovered
from the freedesktop desktop entries (`/usr/share/applications`, `~/.local/share/applications`,
flatpak exports …) by `tools/make_app_icons.py`. Each app becomes one physical object from
`tools/skeu/apps.py`, drawn through the same relief renderer: a terminal is a CRT shell, a browser a
steel desk globe, mail an envelope with a wax seal, chat a stitched enamel bubble, an IDE a glass key on
a milled plinth, a database a brass-handled card catalogue. Music is split by how it is played — a
brass-horn gramophone, a smoked cassette, a tuning fork, headphones — so the players stop sharing one
sleeve. The GTK/GNOME apps get their own subjects too: a jigsaw piece for extensions, a loupe for image
viewing, an oscilloscope for system load, a prism for colour management, a paint tube and a pen nib for
the graphics tools, a magnet for torrents, a pallet for the package warehouse, glass cubes for virtual
machines, a screen-and-keyboard for VNC, a moored mine for minesweeper and a squared pad for sudoku.
`1Password`, `Emacs`, `IntelliJ IDEA` and `Signal` reuse their hand-authored icons from `svg/`. There
are no monograms anywhere in the set; brand colour survives only as the one accent. See
[`app-icons/README.md`](app-icons/README.md).

## Contexts: places, mimetypes, emblems, categories, devices

The theme fills the contexts desktop environments actually query. Coverage, measured against
Adwaita's 16x16 counts:

| context | names | Adwaita | coverage |
|---|---|---|---|
| `apps` | 322 | — | the full app set plus the hand-authored icons |
| `places` | 171 | 37 | 462% |
| `mimetypes` | 618 | 47 | 1315% |
| `emblems` | 17 | 5 | 340% |
| `categories` | 27 | 20 | 135% |
| `devices` | 68 | 87 | 78% |

`categories` and `devices` are drawn by `tools/make_context_icons.py` into `generated/` (through the
same relief renderer as the project and app icons). `devices` is still partial (68/87) — the rest need
hardware artwork that has not been drawn yet, and missing names are listed in `theme-manifest.json`
rather than faked. `status`, `actions` and `emotes` are intentionally absent: they are symbolic UI
glyphs, and they do not survive translation into a skeuomorphic material language.

## The relief renderer

Categories, devices, project icons and the generated app icons all come
from `tools/skeu/`, a small numpy renderer built for this pack rather than a vector host vocabulary.
Each icon is assembled from *parts*: a signed-distance silhouette, a height field (bevel, chamfer,
dome), normals derived from that height, one key light from the upper left, and a material. That is
what gives a bevel a horizon, a lens a real specular highlight and a sheet of paper a fold shadow.

* `skeu/paint.py` — shapes, canvas, premultiplied compositing, contact and cast shadows, noise.
* `skeu/materials.py` — anodised aluminium keyed to the surface normal (so chamfers read as
  chamfers), chrome with a hard studio horizon, tinted glass with a curved gloss, enamel, brass,
  steel, paper, leather with grain, oiled wood, rubber, an off display, and embossed/engraved marks.
* `skeu/objects.py` — devices, cameras, displays, storage, network gear and the category medallions.
* `skeu/toolkit.py` — stationery, tools and instruments: books, sheets, crates, dials, lamps.
* `skeu/desk.py` — the desk vocabulary the apps needed: CRT terminal, desk globe,
  envelope with wax seal, stitched speech bubble, calendar pad, calculator, address book, ledger,
  typewriter, slide tray, film reel, clapperboard, album sleeve, valve radio, card catalogue, patch
  panel, anvil-free tooling, a chrome hammer, a glass display case, the chrome folder — plus the
  modern-app set: jigsaw piece, loupe, gramophone, cassette, tuning fork, oscilloscope, paper
  plane, pickaxe, mahjong tile, reversi discs, tetromino, prism, paint tube, pen nib, horseshoe magnet,
  pallet, remote screen, naval mine, pencil pad and glass cubes.
* `skeu/catalog.py` — one line per shipped name for categories, devices and projects.
* `skeu/apps.py` — one line per installed application.

Every icon is finished the same way: a tight contact shadow plus a wide, cool cast shadow, a
silhouette normalised to ~80 % of the canvas, and a single accent hue over a neutral metal, glass or
paper body.

## Measurements

The set is built to these numbers: subject occupancy 0.62 of the canvas, body saturation 0.05,
coloured pixels ~10 % of the icon, accent saturation ~0.42, surface-detail share ~0.10, and a plate
corner radius of 3.5–6.5 % (a plain arc). The objects follow from that: mostly neutral metal, glass or
paper, one accent, one key light, and a cast shadow that fades before the canvas edge.

## Gallery

`gallery.html` in the pack root is a single self-contained file — inline CSS/JS, no CDN — indexing
everything on disk: the six theme contexts at every size plus the `app-icons/` and `project-icons/`
sets, with a live filter, a size switcher (16/22/24/32/48/64/128/256/512 and "all sizes" rows), a
light/dark/checkerboard background toggle and per-icon tooltips. It is generated by
`tools/make_gallery.py` (`maak gallery`), which reads the theme directories and both `index.json`
files — so it never carries a stale count. `tools/check_theme.py` (`maak check`) re-runs the
generator in memory and fails if the committed file has drifted. Every icon is pinned to the size it
claims, so the switcher shows the real 16 px bitmap rather than a scaled 512 px one.

## Notes on fidelity

Items above marked *historical evidence* are backed by the linked reference images; the exact
`IntelliJ IDEA` and `WhatsApp` desktop-era bitmaps could not be verified from a primary source, so
their silhouettes are re-imaginings built on their documented marks and on this pack's own material
vocabulary. Everything is hand-authored SVG — nothing is traced, stretched or upscaled from a bitmap.

## Credits and licence

* Emacs "E": © Free Software Foundation, Nicolas Petton — GPLv3+.
* WhatsApp handset: from the official WhatsApp mark; WhatsApp is a trademark of Meta Platforms.
* Signal mark / Signal blue: Signal Foundation.
* 1Password keyhole: AgileBits.
* Everything else in this directory: original artwork, drawn for this pack, released under
  CC BY-SA 4.0 (see [`LICENSE`](LICENSE)). Product names and marks remain the property of their
  owners and are used only to describe the icons.
