# The skeu icon prompt

A single prompt for generating a skeuomorphic, pre-flat-design icon.
Paste it, replace the `SUBJECT:` line with one sentence, and nothing else.

The numbers in it are measured from the 311 reference icons this pack's style was modelled on,
and compared against the 103 icons this pack draws itself. The comparison is at the bottom, with
what it means.

---

```text
ROLE
You are a senior icon designer working in 2009, in the glossy skeuomorphic language of the
2000s desktop (before the flat redesign that followed).

SUBJECT: <one sentence: what the icon is for, and the one thing that must be recognisable at 16 px>

Everything below is a hard constraint. Do not modernise it, do not "clean it up", do not
reinterpret it as flat design.

CANVAS
- 1024×1024 px, RGBA, transparent background, sRGB. No background rectangle, no colour field.
- The icon is a physical object photographed/rendered on an invisible surface, not a masked tile.
- Its silhouette spans roughly 70–90 % of the canvas width and sits optically centred, its
  visual centre at about 47 % of the canvas height (slightly high, so the cast shadow fits).
- Its cast shadow fades out before the bottom edge, leaving 0–3 % of air.
- NEVER a rounded-square app-icon mask, never artwork clipped into a rounded square.
  If the object genuinely is a plate or panel, its corner radius is 5 % of its width
  (3.5–6.5 %), a plain circular arc — not continuous-curvature geometry.

STEP 1 — PICK ONE ARCHETYPE (state which)
A. Still-life object (default, most traditional): render the actual physical thing — padlock,
   camera, alarm clock, wrench, envelope, chess piece, gear, pencil, compass, toolbox.
B. Document sheet: white page in 8.5:11 proportion, dog-ear fold at the top-right, printed
   content (a photo, a page thumbnail, a type sample), plus one small type badge or printed
   label. For files, formats, media, archives.
C. Medallion: a tinted glass gem (sphere or lens) set in a chrome ring or a machined gear, with
   ONE embossed white pictogram. For categories, preferences, devices, abstract verbs.
D. Plate/panel: a bevelled anodised-metal or enamel tile that itself is the product (a control
   panel, a hardware face, a brand tile). One object or one embossed glyph on it — never a flat
   letter centred on a coloured field.

Decision rule: physical thing → A. File/format → B. Category/setting/abstract → C. Brand tile
→ D only if it reads as hardware, not as a sticker. Prefer A whenever the subject has a body.

STEP 2 — COMPOSE
- One subject, one silhouette. Real parts are allowed (a camera = body + lens + shutter), a
  collage is not.
- Eye level; mild three-quarter perspective (10–20°) for chunky objects; dead-on for sheets
  and plates.
- Optical balance, not geometric: heavier mass slightly below centre, small details gathered
  away from the visual centre of mass.
- The silhouette must still read at 16 px as one shape in two tones.

STEP 3 — LIGHT (one key, one fill, no more)
- Key light upper-left, ~30° elevation, ~20° to the left. Fill from the right at 10–15 % of the
  key. No backlight; at most a 1–2 px specular rim on the lit edge.
- Every curved surface: bright band in the upper 20–30 %, mid-tone body, darkening through the
  lower 20–30 %, and a 1 px darker terminator where it turns away from the light.
- Contact shadow wherever two parts meet: multiply, 20–35 % black, 1–2 % blur.
- Cast shadow: soft ellipse below the object, offset down 2–4 %, blur 4–8 % of the icon size,
  25–45 % opacity, cool grey — never pure black.
- Ambient occlusion in crevices, under ledges, inside rings.
- NO outline stroke around the silhouette. The edge is a material (a lit rim on one side, a
  darker bevel on the other), not a line.

STEP 4 — MATERIALS (pick one to three; every surface needs at least three tones)
- Anodised aluminium: vertical gradient #d8dbe0 → #a7acb6 → #cfd3da with the horizon at ~55 %;
  1 px #f2f4f7 rim on the lit edge, 1 px #6c727c on the shadow edge; faint vertical brush
  streaks at 1–2 % contrast.
- Polished chrome: five stops — #6f7681 → #e9edf2 → #ffffff (hard horizon at 45–55 %) →
  #8e949e → #c9ced6. Dark studio above the horizon, bright floor below.
- Tinted glass (the pack's blue): body #3f8fd8 → #1a5b9c, edges deepening to #0e3f74; a capsule
  gloss band from 8 % to 30 % of the height, white at 55–75 %, hard top edge, feathered bottom;
  a caustic highlight in the lower third; 2 px rim #bfe0ff on the lit side, #0a2f57 on the
  shadow side; the gloss reflected, inverted and compressed, in the lower half.
- Enamel paint: hue at 35–60 % saturation, 45–60 % lightness; top 30 % raised 8–12 %; bottom
  20 % dropped 10–15 %; one specular hotspot at ~25 % height; dark terminator line.
- Paper: #fdfdfb with a warm gradient down to #f7f5ef; 1 px #d9d5cb edge; top-right fold of
  12–16 % width with a shadow line under the flap; print at ~70 % opacity in #4a4a4a.
- Leather and stitching: base #2d4a63 with ~3 % noise; a dashed seam 3–4 % wide, each stitch
  with a 1 px dark underside and a 1 px light top (the Signal speech-bubble trick).
- Oiled wood: #8a5a2b → #6d431c with 4–6 wavy grain streaks at 10–15 % contrast, sheen in the
  upper third, darker at the ends.
- Rubber/plastic: #23262b, matte, ~2 % speckle, no specular at all.

STEP 5 — COLOUR (this is where modern icons give themselves away)
- 75–90 % of the icon is neutral: steel, graphite, white, paper. The reference art has a median
  body saturation of 0.05 and a median value of 0.82 — it is bright and mostly colourless.
- Colour is an accent covering only 10–25 % of the icon (reference median: 10 %). If a quarter of
  your icon is coloured, the material failed and colour is doing its job.
- One accent hue only. Default to blue/cyan (hue 200–230°); 68 % of the reference set's chromatic
  pixels live between 180° and 240°.
- Accent saturation 0.40–0.75 (a saturated gem or enamel is correct); accent lightness
  0.45–0.60. No neon, no pastel, no two-hue gradients on one surface.
- Highlights are pure white. Shadows are blue-grey (#2b3440 family), never neutral black.

STEP 6 — DETAIL
- Machined detail belongs in the upper third and around the edges: screw threads, gear teeth,
  knurling, tick marks, bevels, seams, rivets.
- Detail covers 10–15 % of the area at 1024 px (the reference median high-frequency share is 10 %;
  this is what makes the icon look photographed rather than drawn).
- Nothing hairline-thin: every detail is at least 3 px wide at 1024 px so it survives 32 px.
- At 16 px the icon should simplify to a silhouette plus one or two internal shapes — simplify
  the small sizes, never just blur them.

STEP 7 — TEXT
- No captions, no labels, no two-letter monograms stamped on a colour.
- Printed content on a document sheet is correct and should look printed: small, dark grey,
  slightly soft, with a type label in the usual place for one (bottom-right of a document icon).
- If the subject's identity genuinely is typographic (a code editor, a brand wordmark), emboss
  the letterform in metal or glass with a highlight and a shadow — never print it flat.

STEP 8 — OUTPUT
- 1024×1024 PNG, RGBA, transparent, sRGB.
- If asked for a vector instead: layered linear/radial gradients and blurred shapes only — no
  flat fills, no strokes standing in for shading.
- Finish with one line: archetype → materials → accent hue. Keep it short.

NEVER (each of these reads as 2014, not 2009)
- rounded-square app-icon mask or icon grid, artwork clipped to a rounded square
- flat vector or line-art glyph on a coloured disc; a two-stop radial "plastic" ball as the
  whole icon; a flat glyph on a gradient
- initials or monograms centred on a coloured circle, rounded square or book spine
- neon, pastel, mesh gradients, glassmorphism, frosted blur, dark-mode UI
- cartoon mascots, emoji-face 3D characters
- hard-offset drop shadow with no blur
- isometric or orthographic-flat illustration
- more than one accent hue, or colour over more than ~25 % of the icon
- the object touching the canvas edge, or any opaque background

SANITY TEST — answer before you finish
1. Is it one physical object? 2. Is the body mostly neutral metal/glass/paper? 3. Is there a
specular band, a contact shadow and a soft cast shadow? 4. Does it still read at 16 px?
5. Would it sit comfortably next to a chrome calculator, a compass in a steel case and a chrome
padlock? If any answer is no, fix it before answering.

EXAMPLES
SUBJECT: a command-line build tool called "maak".
→ Archetype A: a machined steel wrench lying at 15°, its socket replaced by a small blue glass
lens; anodised body, one blue accent, cast shadow to the lower right.

SUBJECT: the "games" menu category.
→ Archetype C: a pair of ivory enamel dice on a charcoal rubber pad inside a chrome ring;
embossed pips, one warm accent, no text.

SUBJECT: the PDF document type.
→ Archetype B: white sheet with a top-right fold, a printed page thumbnail, and "PDF" printed
as the type label; a chrome paperclip detail, red accent only in the print.

SUBJECT: a password manager called "1Password".
→ Archetype D/A hybrid: a chrome-rimmed steel padlock with a blue glass body and a brass
keyhole, standing on a soft shadow; steel, glass, brass; one blue accent.
```

---

## Why these numbers

Measured on the 311 reference icons the style is modelled on, against the 103 icons this pack
draws itself:

| property | reference set (n=311) | this pack's own art (n=11 + 92) | what it means |
|---|---|---|---|
| subject occupancy of the canvas | **0.62** | 0.49 | our subjects are too small, with dead margin |
| median body saturation | **0.05** | 0.33 / 0.39 | the reference icons are metal, glass and paper; ours are coloured |
| share of the icon that is coloured | **10 %** | 47 % / 59 % | colour is an accent in the reference set, the whole body for us |
| median value (brightness) | **0.82** | 0.63 / 0.68 | ours are a stop darker and read as "dark mode" |
| high-frequency detail share | **0.100** | 0.072 / 0.075 | ours are smoother, flatter, less photographed |
| plate-like icons (fills its bbox, closed corners) | **2 %** | 18 % / 37 % | we draw tiles with glyphs where the reference draws objects |
| accent-pixel saturation | 0.42 | 0.64 / 0.65 | *not* the problem — our accents are fine |
| plate corner radius | 0.051 (0.036–0.063) | 0.066 | the reference plates are a 5 % arc, not a rounded square |

The diagnosis is narrow: our accents are not too saturated, and our corner radius is fine. What
is wrong is that **the body of the icon is colour instead of a material**, the subject is **too
small**, the icon is **too dark**, it has **too little surface detail**, and it is twice as
likely to be a plate with a glyph on it instead of a physical object.

The 11 hand-drawn icons that work (1Password's padlock, Emacs' glass orb in a chrome ring,
Signal's stitched bubble, WhatsApp's gem, IntelliJ's steel plate) follow the same rules by
instinct: neutral metal and glass with one accent, a real bevel, a real specular band, a real
shadow, and one crisp mark.

## Worked examples, full size

- `SUBJECT: a personal wiki note app.` → B: cream paper sheet, top-right fold, a printed index
  card with three ruled lines and one tab, a small blue paperclip; paper + steel; blue accent.
- `SUBJECT: the "development" category.` → C: a machined gear in anodised aluminium with a
  blue-tinted glass lens in the centre and an embossed angle-bracket; steel + glass; blue.
- `SUBJECT: a backup utility called "tijdmachine".` → A: a brushed-steel clock face with an
  enamel dial, chrome bezel and a blued steel hand, sitting on a soft shadow; steel + enamel;
  one blue accent on the hand.
- `SUBJECT: the "multimedia" category.` → C: a chrome-ringed amber glass lens with an embossed
  film-strip segment inside; warm glass in cold chrome; amber accent (hue ~35°).

## Reviewing a result

Reject it if any of these is true: the subject is a monogram on a coloured shape; more than a
quarter of the icon is coloured; there is no visible specular band; the shadow is a hard grey
ellipse; the silhouette needs an outline to be legible; it looks like a 2016-era flat app icon;
the corner is continuous-curvature; the icon is a flat glyph on a gradient.
