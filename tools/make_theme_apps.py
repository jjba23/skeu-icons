#!/usr/bin/env python3
"""Put the drawn app icons into the theme under every name a desktop asks for.

``make_app_icons.py`` draws one icon per installed program and files it under a
slug (``app-icons/wezterm/``).  A desktop never asks for that slug: it asks for
whatever the program wrote in its desktop entry - ``org.wezfurlong.wezterm``, or
the desktop id ``com.usebruno.Bruno``, or the window class.  Without those
spellings the icon is simply not found and the toolkit falls through to
Adwaita.

This step closes that gap: it copies any app icon the theme is missing into
``skeu-icons/<size>x<size>/apps/`` and links every name the entries declare to
the artwork.  Existing artwork is never overwritten - the pack's hand-drawn
Emacs and calculator keep their place, and only the links are added.

A few programs are shown under *another* icon instead of the object drawn for
them: the theme ships macOS artwork under its own names (``finder.png``,
``xcode.png``, ``terminal.png``), and those are what IntelliJ IDEA, Nautilus and
every terminal emulator answer with.  For those apps the names are pointed at
the borrowed artwork rather than at their own slug; the artwork itself is
committed in the theme, so this step mostly writes links.  ``BORROWED`` names
the individual trades (iMovie for a video editor, Disk Utility for a
partitioner), ``BORROWED_CATEGORIES`` the whole ones (every file manager is the
Finder, every game is Game Center), and ``BORROWED_NAMES`` covers programs no
desktop entry on this machine declares.

Two of those trades want the same object in a different colour - a second
editor should not be a pixel-for-pixel copy of the first program's tile - so
``ALTS`` cuts colourways out of committed artwork and writes them beside it at
every size.

A program that ships its own icon is not part of any of this.  Its names are in
``OWN_ARTWORK`` (see ``make_app_icons.py``), and this step does not answer for
them: it links nothing under those names and takes back anything an earlier
build wrote, because a theme is looked up before the hicolor fallback, and a
file here would shadow the artwork that program ships with itself.

    python3 tools/make_theme_apps.py            # install + link
    python3 tools/make_theme_apps.py --check    # report gaps, write nothing
"""

from __future__ import annotations

import argparse
import colorsys
import os
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_app_icons import OWN_ARTWORK, discover  # noqa: E402
from render_skeu import resize, save_png, slugify  # noqa: E402

THEME = ROOT / "skeu-icons"
ICONS = ROOT / "app-icons"

#: The sizes the theme ships as bitmaps; every alias is mirrored into ``@2x``.
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "apps"

#: Programs the pack shows under another icon than the one drawn for them, the
#: way a desktop dressed as OS X would dress them: iMovie for a video editor,
#: Mail for a mail client, Game Center for a game.  Keyed by app slug, valued by
#: a committed file stem in ``apps/``.
#:
#: A family is spread over its colourways (see ``ALTS``) so that four editors on
#: one machine do not become four pixel-identical stars: the first program takes
#: the artwork as Apple drew it, the next two take the colourways cut from it.
BORROWED: dict[str, str] = {
    # --- video editing: iMovie, gold / rose / blue -------------------------- #
    "kdenlive": "imovie",
    "openshot": "imovie",
    "shotcut": "imovie-alt-2",
    # --- film players and DAWs --------------------------------------------- #
    "totem": "quicktime-player",
    "celluloid": "quicktime-player-alt",
    "ardour": "garageband",
    "lmms": "garageband-alt",
    # --- file managers: the Finder face, blue / green / violet -------------- #
    "files": "finder",
    "nemo": "finder",
    "dolphin": "finder-alt",
    "caja": "finder-alt",
    "thunar": "finder-alt-2",
    "pcmanfm": "finder-alt-2",
    # --- games: Game Center, blue / teal / magenta ------------------------- #
    # The chess set is the exception: the era drew a chess set of its own (see
    # ``CATEGORY_KEEP``), so the board game keeps the knight and everything
    # else in the menu is Game Center.
    "quadrapassel": "game-center",
    "swell-foop": "game-center",
    "mines": "game-center-alt",
    "reversi": "game-center-alt",
    "lights-off": "game-center-alt",
    "mahjongg": "game-center-alt-2",
    "sudoku": "game-center-alt-2",
    # --- chat: iMessage, green / blue / violet ----------------------------- #
    "telegram": "messages",
    "element": "messages",
    "zulip": "messages",
    "emblem": "messages",
    "discord": "messages-alt",
    "mattermost": "messages-alt",
    "zapzap": "messages-alt",
    "skype": "messages-alt",
    "slack": "messages-alt-2",
    "rocket-chat": "messages-alt-2",
    "dialect": "messages-alt-2",
    # --- mail: the airmail stamp, brass / teal / violet -------------------- #
    "thunderbird": "mail",
    "evolution": "mail-alt",
    "geary": "mail-alt-2",
    # --- video calls ------------------------------------------------------- #
    "zoom": "facetime",
    "microsoft-teams": "facetime-alt",
    # --- drives and disks -------------------------------------------------- #
    "impression": "disks-alt",     # the USB writer, on a blue drive
    "gparted": "disk-utility",     # a partitioner, shown as Disk Utility
    # --- pictures: iPhoto -------------------------------------------------- #
    "image-viewer": "iphoto",
    "shotwell": "iphoto-alt",
    "gwenview": "iphoto-alt-2",
    # --- notes: the stitched pad, yellow / green / pink -------------------- #
    "joplin": "notes",
    "obsidian": "notes-alt",
    "logseq": "notes-alt-2",
    # --- music: the silver disc, blue / red / gold -------------------------- #
    "music": "itunes",
    "rhythmbox": "itunes-alt",
    "elisa": "itunes-alt-2",
    # --- reference and the web --------------------------------------------- #
    "wordbook": "dictionary",
    "web": "safari",
    # --- viewers, backups, software, settings ------------------------------ #
    "document-viewer": "preview",
    "okular": "preview-alt",
    "timeshift": "time-machine",
    "d-j-dup-backups": "time-machine-alt",
    "software": "app-store",
    "discover": "app-store-alt",
    "settings": "system-preferences",
    "tweaks": "system-preferences-alt",
    # --- monitors, the calendar, the clock and the scratch pad ------------- #
    "gnome-system-monitor": "activity-monitor",
    "system-monitor": "activity-monitor-alt",
    "btop": "activity-monitor-alt-2",
    "resources": "system-information",
    "calendar": "ical",
    "clocks": "clock",
    "text-pieces": "stickies",
    # --- the desk calculator, the camera booth and the printer ------------- #
    # The era drew all three, and every desktop has a program that does the
    # same job; see the "everyday tools" block in ``ROSTER``, tools/skeu/apps.py.
    "cheese": "photo-booth",
    "print-settings": "printer",
    "print-editor": "printer-alt",
    # --- the office suite: the page, the slide and the spreadsheet -------- #
    "libreoffice-writer": "pages",
    "abiword": "pages-alt",
    "libreoffice-impress": "keynote",
    "libreoffice-math": "grapher",
    "libreoffice-calc": "microsoft-excel",
    "gnumeric": "microsoft-excel-alt",
    # --- passwords: the ring of keys --------------------------------------- #
    "1password": "keychain-access",
    "keepassxc": "keychain-access",
    "bitwarden": "keychain-access-alt",
    "passwords-and-keys": "keychain-access-alt-2",
    # --- archives and remote machines -------------------------------------- #
    "file-roller": "betterzip",
    "ark": "betterzip-alt",
    "remmina": "remote-desktop-connection",
    "rustdesk": "remote-desktop-connection-alt",
    "tigervnc": "screen-sharing",
    "remote-viewer": "screen-sharing-alt",
    "connections": "screen-sharing-alt-2",
    # --- the darkroom, the colour meter and the network tap ---------------- #
    "darktable": "aperture",
    "rawtherapee": "aperture-alt",
    "eyedropper": "digitalcolor-meter",
    "color-profile-viewer": "colorsync-utility",
    "wireshark": "network-utility",
    "wireshark-super-user-mode": "network-utility-alt",
    # --- the library, the type case and the graph paper -------------------- #
    "calibre": "ibooks-author",
    "webfont-bundler": "font-book",
    "graphs": "grapher-alt",
    "disk-usage-analyzer": "disks-alt",
    # --- another operating system on the same machine ---------------------- #
    "virtualbox": "boot-camp-assistant",
    "vmware-workstation": "boot-camp-assistant-alt",
    "virtual-machine-manager": "boot-camp-assistant-alt-2",
    # --- the file sender, the way Bluetooth File Exchange did it ------------ #
    "warp": "bluetooth-file-exchange-alt",
    # --- one IDE and one pane splitter ------------------------------------- #
    "intellij-idea": "xcode",
    "terminator": "terminal-red",
    # --- the graphics suite: the feather, the flower, the butterfly -------- #
    "krita": "photoshop-cs2",
    "inkscape": "illustrator-cs2",
    "libreoffice-draw": "illustrator-cs2-alt",
    "scribus": "indesign-cs2",
    # --- authoring for the web: the sphere with the d, the spark ----------- #
    "workbench": "dreamweaver-8",
    "curtail": "fireworks-8",
    # --- burning a disc, transcoding a film -------------------------------- #
    "brasero": "roxio-toast",
    "k3b": "roxio-toast-alt",
    "impression": "roxio-toast-alt-2",
    "handbrake": "roxio-popcorn",
    # --- an emulator is the Classic environment ---------------------------- #
    "boxes": "classic",
    "qemu": "classic-alt",
    # --- peer to peer: the lime --------------------------------------------- #
    "transmission": "limewire",
    "qbittorrent": "limewire-alt",
    "fragments": "limewire-alt-2",
    # --- the blue marble --------------------------------------------------- #
    "maps": "google-earth",
}

#: Every terminal emulator answers with the pack's one terminal, so a machine
#: with six emulators installed still shows a single terminal icon.  That shared
#: artwork *is* the icon drawn for TERMINAL_SOURCE, so the two stay the same
#: picture whenever this step writes one of them.
TERMINAL_ART = "terminal"
TERMINAL_SOURCE = "console"

#: Categories whose applications answer with one Apple icon, because the
#: category *is* the Mac application: every file manager is the Finder, every
#: game is Game Center.  A slug in BORROWED always wins.
BORROWED_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("TerminalEmulator", TERMINAL_ART),
    ("FileManager", "finder"),
    ("Game", "game-center"),
)

#: Programs in a mapped category that keep the object drawn for them: a game
#: store, an emulator or a Wine prefix is a shelf, not a game.  ``chess`` is
#: here for the other reason - the era drew a chess set of its own, so the
#: board game keeps its knight while the rest of the menu is Game Center.
CATEGORY_KEEP: frozenset[str] = frozenset({
    "steam", "lutris", "heroic", "prism-launcher", "cartridges", "retroarch",
    "retrodeck", "retrodeck-configurator", "bottles", "wine", "chess",
})

#: Names a launcher asks for that no desktop entry on this machine declares - a
#: program that is only a menu alias, a dock's own button, a Wine export -
#: mapped straight to artwork.  ``tmux`` is not a terminal emulator and never
#: will be, but a launcher that starts it wants a terminal's tile.
BORROWED_NAMES: dict[str, str] = {
    "tmux": "terminal-red",
    "lightworks": "imovie-alt",
    "openshot": "imovie",
    # One name of the dock's own, and not the dock: its launcher asks for the
    # *button* it draws, which is the one place a Launchpad tile is wanted.  The
    # names the dock itself answers to are in OWN_ARTWORK and stay unclaimed.
    "lambdock-launchpad": "launchpad-alt",
    # --- searching, the way Sherlock did it -------------------------------- #
    "catfish": "sherlock",
    "gnome-search-tool": "sherlock-alt",
    "recoll": "sherlock-alt-2",
    # --- two more vector editors and two more DVD tools -------------------- #
    "karbon": "illustrator-cs2-alt-2",
    "karbon14": "illustrator-cs2-alt-2",
    "winff": "roxio-popcorn-alt",
    "dvdrip": "roxio-popcorn-alt-2",
    # --- animating, authoring for the web ---------------------------------- #
    "synfig": "flash-8",
    "synfigstudio": "flash-8-alt",
    "pencil2d": "flash-8-alt-2",
    "bluefish": "dreamweaver-8-alt",
    "bluegriffon": "dreamweaver-8-alt-2",
    "kompozer": "dreamweaver-8",
    # --- the media centre: the remote on the sofa table -------------------- #
    "kodi": "front-row",
    "mythtv": "front-row-alt",
    # --- the desk calculator, the alarm clock, the scratch pad ------------- #
    # Names no desktop entry here declares, so they are mapped straight to the
    # era artwork they borrow: another distribution's calculator, another
    # clock, another sticky note.
    "qalculate-qt": "calculator-alt",
    "mate-calc": "calculator-alt-2",
    "xfce4-calculator": "calculator-alt-2",
    "kclock": "clock-alt",
    "alarm-clock-applet": "clock-alt",
    "xpad": "stickies-alt",
    "knotes": "stickies-alt",
    # --- the screenshot the era took with Grab ----------------------------- #
    "gnome-screenshot": "grab",
    "flameshot": "grab-alt",
    "spectacle": "grab-alt-2",
    # --- another archive manager, another chess set ------------------------ #
    "xarchiver": "betterzip-alt-2",
    "engrampa": "betterzip-alt-2",
    "peazip": "betterzip-alt-2",
    "pychess": "chess-alt",
    "xboard": "chess-alt-2",
    "stockfish": "chess-alt-2",
    "guvcview": "photo-booth-alt",
    "kamoso": "photo-booth-alt",
    "system-config-printer": "printer-alt",
    "gcolor2": "digitalcolor-meter-alt",
    "gcolor3": "digitalcolor-meter-alt",
    "gnome-color-chooser": "digitalcolor-meter-alt",
    "proton-pass": "keychain-access-alt-3",
    "mythfrontend": "front-row-alt",
    "jellyfin": "front-row-alt-2",
    "plex-media-player": "front-row",
    # --- an emulator, and a clone of one ----------------------------------- #
    "dosbox": "classic-alt-2",
    "scummvm": "classic",
    # --- automation, and the filesharing of the era ------------------------ #
    "autokey": "automator",
    "actiona": "automator-alt",
    "amule": "limewire-alt",
    "nicotine": "limewire-alt-2",
    # --- the globe, and the globe as a desktop app -------------------------- #
    "marble": "google-earth-alt",
    "qgis": "google-earth-alt-2",
}

#: Colourways of borrowed artwork, written into the theme beside it so a second
#: program can have the same object in its own colours instead of a copy of the
#: first program's icon.  ``alt stem -> (source stem, hue, saturation, mode)``:
#: ``shift`` turns the artwork's own hues (a gold star becomes a red one and
#: keeps its shading), ``tint`` keeps its luminance and puts everything on one
#: hue, which is what turns graphite window chrome burgundy without taking the
#: white prompt with it.
#:
#: Two colourways per family: the artwork as Apple drew it, then two answers to
#: the question "this program is the same kind of thing, why is its tile
#: identical?".  They are cut from the catalogued artwork in ``library/apps``
#: (or, for the pack's own drawings, from the theme), never redrawn by hand.
ALTS: dict[str, tuple[str, float, float, str]] = {
    # --- chat, mail, calls -------------------------------------------------- #
    "messages-alt": ("messages", 212, 1.0, "tint"),        # the blue iMessage
    "messages-alt-2": ("messages", 55, 0.95, "shift"),     # violet bubbles
    "mail-alt": ("mail", 100, 0.95, "shift"),              # teal stamp
    "mail-alt-2": ("mail", -100, 0.95, "shift"),           # violet stamp
    "facetime-alt": ("facetime", -100, 0.95, "shift"),     # green lens
    # --- drives ------------------------------------------------------------ #
    "disks-alt": ("disks", 212, 1.0, "tint"),              # blue drive
    "disks-alt-2": ("disks", 25, 1.0, "tint"),             # brass drive
    # --- pictures, notes, music, reference --------------------------------- #
    "iphoto-alt": ("iphoto", 100, 0.95, "shift"),
    "iphoto-alt-2": ("iphoto", 180, 0.95, "shift"),
    "notes-alt": ("notes", 100, 0.95, "shift"),            # green pad
    "notes-alt-2": ("notes", -100, 0.95, "shift"),         # pink pad
    "itunes-alt": ("itunes", 150, 0.95, "shift"),          # red quaver
    "itunes-alt-2": ("itunes", -150, 0.95, "shift"),       # gold quaver
    "dictionary-alt": ("dictionary", -100, 0.95, "shift"),  # violet book
    "dictionary-alt-2": ("dictionary", 55, 0.95, "shift"),  # gold book
    # --- the Finder and the games ------------------------------------------ #
    "finder-alt": ("finder", -100, 0.95, "shift"),         # green face
    "finder-alt-2": ("finder", 55, 0.95, "shift"),         # violet face
    "game-center-alt": ("game-center", 100, 0.95, "shift"),
    "game-center-alt-2": ("game-center", -100, 0.95, "shift"),
    # --- media production --------------------------------------------------- #
    "imovie-alt": ("imovie", -52, 0.95, "shift"),          # rose star
    "imovie-alt-2": ("imovie", 150, 0.95, "shift"),        # blue star
    "garageband-alt": ("garageband", -100, 0.95, "shift"),  # violet guitar
    "quicktime-player-alt": ("quicktime-player", 100, 0.95, "shift"),
    # --- system ------------------------------------------------------------ #
    "terminal-red": ("terminal", 356, 1.0, "tint"),
    "activity-monitor-alt": ("activity-monitor", 100, 0.95, "shift"),
    "time-machine-alt": ("time-machine", 100, 0.95, "shift"),
    "time-machine-alt-2": ("time-machine", -100, 0.95, "shift"),
    "preview-alt": ("preview", 28, 1.0, "tint"),            # sepia print
    "preview-alt-2": ("preview", 205, 1.0, "tint"),         # cyan print
    "app-store-alt": ("app-store", 100, 0.95, "shift"),
    "app-store-alt-2": ("app-store", -100, 0.95, "shift"),
    "system-preferences-alt": ("system-preferences", 100, 0.95, "shift"),
    "launchpad-alt": ("launchpad", 212, 1.0, "tint"),      # blue disc
    "launchpad-alt-2": ("launchpad", 20, 1.0, "tint"),     # copper disc
    "xcode-alt": ("xcode", 100, 0.95, "shift"),
    "xcode-alt-2": ("xcode", -100, 0.95, "shift"),
    # --- the graphics suite: a feather, a flower and a butterfly, recoloured #
    # The suits marks are spheres, petals and wings, so ``shift`` keeps the
    # gloss that makes them read as glass and only turns the hue.
    "photoshop-cs2-alt": ("photoshop-cs2", 150, 0.95, "shift"),       # red feather
    "photoshop-cs2-alt-2": ("photoshop-cs2", -80, 0.95, "shift"),     # green feather
    "illustrator-cs2-alt": ("illustrator-cs2", -100, 0.95, "shift"),  # magenta flower
    "illustrator-cs2-alt-2": ("illustrator-cs2", 150, 0.95, "shift"), # blue flower
    "indesign-cs2-alt": ("indesign-cs2", 150, 0.95, "shift"),         # green butterfly
    "indesign-cs2-alt-2": ("indesign-cs2", -100, 0.95, "shift"),      # violet butterfly
    # --- authoring for the web --------------------------------------------- #
    "dreamweaver-8-alt": ("dreamweaver-8", 100, 0.95, "shift"),       # teal sphere
    "dreamweaver-8-alt-2": ("dreamweaver-8", -100, 0.95, "shift"),    # crimson sphere
    "flash-8-alt": ("flash-8", 150, 0.95, "shift"),                  # green F
    "flash-8-alt-2": ("flash-8", 205, 1.0, "tint"),                  # blue F
    "fireworks-8-alt": ("fireworks-8", 150, 0.95, "shift"),          # blue spark
    "fireworks-8-alt-2": ("fireworks-8", -100, 0.95, "shift"),       # magenta spark
    # --- burning, transcoding, searching, the Classic environment ---------- #
    "roxio-toast-alt": ("roxio-toast", 60, 0.95, "shift"),           # violet discs
    "roxio-toast-alt-2": ("roxio-toast", -60, 0.95, "shift"),        # green discs
    "roxio-popcorn-alt": ("roxio-popcorn", 100, 0.95, "shift"),      # green bucket
    "roxio-popcorn-alt-2": ("roxio-popcorn", -100, 0.95, "shift"),   # violet bucket
    "sherlock-alt": ("sherlock", 205, 1.0, "tint"),                  # blue tweed
    "sherlock-alt-2": ("sherlock", 30, 1.0, "tint"),                 # amber tweed
    "classic-alt": ("classic", 205, 1.0, "tint"),                    # blue nine
    "classic-alt-2": ("classic", 275, 1.0, "tint"),                  # violet nine
    # --- the media centre, the robot, the globe, the lime ------------------ #
    "front-row-alt": ("front-row", 205, 1.0, "tint"),                # blue remote
    "front-row-alt-2": ("front-row", 25, 1.0, "tint"),               # amber remote
    "automator-alt": ("automator", 205, 1.0, "tint"),                # blue robot
    "automator-alt-2": ("automator", 25, 1.0, "tint"),               # copper robot
    "google-earth-alt": ("google-earth", 150, 0.95, "shift"),        # red marble
    "google-earth-alt-2": ("google-earth", -100, 0.95, "shift"),     # green marble
    "limewire-alt": ("limewire", 100, 0.95, "shift"),                # cyan lime
    "limewire-alt-2": ("limewire", 150, 0.95, "shift"),              # violet lime
    # --- the everyday tools of the era, and the jobs they stand in for ---- #
    # A calculator, a chess set, a clock, a note pad and a printer are all
    # metal or glass bodies with a little colour on them, so ``tint`` is what
    # gives the second program of a kind its own tile without turning the
    # keys, the knight or the paper with it.
    "calculator-alt": ("calculator", 212, 1.0, "tint"),               # blue keys
    "calculator-alt-2": ("calculator", 25, 1.0, "tint"),              # brass keys
    "chess-alt": ("chess", 205, 1.0, "tint"),                        # the blue set
    "chess-alt-2": ("chess", 25, 1.0, "tint"),                       # the amber set
    "clock-alt": ("clock", 205, 1.0, "tint"),                        # chrome again, colder
    "stickies-alt": ("stickies", 205, 1.0, "tint"),                  # a blue note
    "photo-booth-alt": ("photo-booth", 205, 1.0, "tint"),            # blue curtain
    "printer-alt": ("printer", 205, 1.0, "tint"),                    # the office printer, cooled
    "grab-alt": ("grab", 205, 1.0, "tint"),
    "grab-alt-2": ("grab", 28, 1.0, "tint"),
    "grapher-alt": ("grapher", 100, 0.95, "shift"),                  # teal graph
    # --- the office suite, the key ring and the archive box --------------- #
    "pages-alt": ("pages", 100, 0.95, "shift"),                      # teal page
    "microsoft-excel-alt": ("microsoft-excel", 150, 0.95, "shift"),  # green X
    "keychain-access-alt": ("keychain-access", 212, 1.0, "tint"),
    "keychain-access-alt-2": ("keychain-access", 100, 0.95, "shift"),
    "keychain-access-alt-3": ("keychain-access", 25, 1.0, "tint"),
    "betterzip-alt": ("betterzip", 205, 1.0, "tint"),                # blue box
    "betterzip-alt-2": ("betterzip", 25, 1.0, "tint"),               # brass box
    # --- the darkroom, the meter, the network tap, the VM ----------------- #
    "aperture-alt": ("aperture", 150, 0.95, "shift"),                # the lens, greener
    "digitalcolor-meter-alt": ("digitalcolor-meter", 205, 1.0, "tint"),
    "network-utility-alt": ("network-utility", 100, 0.95, "shift"),  # teal trace
    "activity-monitor-alt-2": ("activity-monitor", 25, 1.0, "tint"),
    "boot-camp-assistant-alt": ("boot-camp-assistant", 100, 0.95, "shift"),
    "boot-camp-assistant-alt-2": ("boot-camp-assistant", -100, 0.95, "shift"),
    # --- the remote screen and the file sender ---------------------------- #
    "remote-desktop-connection-alt": ("remote-desktop-connection", 100, 0.95, "shift"),
    "screen-sharing-alt": ("screen-sharing", 100, 0.95, "shift"),
    "screen-sharing-alt-2": ("screen-sharing", -100, 0.95, "shift"),
    "bluetooth-file-exchange-alt": ("bluetooth-file-exchange", 205, 1.0, "tint"),
}

#: Names a launcher asks for when it wants "a terminal", not a named program.
GENERIC_TERMINAL_NAMES = ("utilities-terminal",)


def lookup_names(app: dict) -> list[str]:
    """Every name a shell or launcher may ask for, slug first."""
    names = [slugify(app["name"])]
    # Names declared by the roster (installed elsewhere) and the extra spellings
    # for hand-drawn artwork, before the ones this machine's entries declare.
    for value in (*app.get("names", []),):
        value = (value or "").strip()
        if value and value not in names:
            names.append(value)
    for value in (app.get("icon", ""), app.get("wmclass", ""),
                  *app.get("desktops", [])):
        value = (value or "").strip()
        if not value:
            continue
        # A desktop entry may point straight at a file; that is not a name.
        if "/" in value or value.startswith(".") or re.search(r"\.(png|svg|xpm)$", value):
            continue
        if value not in names:
            names.append(value)
    return names


def borrowed(app: dict) -> str:
    """The theme icon this app answers with, when it is not its own artwork."""
    slug = slugify(app["name"])
    if slug in BORROWED:
        return BORROWED[slug]
    categories = {name.strip() for name in (app.get("categories") or "").split(";")
                  if name.strip()}
    for category, art in BORROWED_CATEGORIES:
        if category in categories and slug not in CATEGORY_KEEP:
            return art
    return ""


def recoloured(image: Image.Image, hue: float, saturation: float,
               mode: str) -> Image.Image:
    """One artwork in another colourway (see ``ALTS``).

    ``shift`` turns every hue by HUE degrees, so a gold star becomes a red one
    and keeps its shading and its white parts; ``tint`` puts the whole picture
    on HUE while leaving light and dark where they are, so graphite chrome
    turns burgundy and a white prompt stays white.  Alpha is untouched: the
    colourway has the same shape as the artwork it came from.
    """
    source = image.convert("RGBA")
    data = source.tobytes()          # RGBA, four bytes per pixel, row by row
    pixels = []
    for index in range(0, len(data), 4):
        red, green, blue, alpha = data[index:index + 4]
        if not alpha:
            pixels.append((red, green, blue, alpha))
            continue
        current, lightness, sat = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
        if mode == "tint":
            current = hue / 360.0
            sat = (1.0 - abs(2.0 * lightness - 1.0)) * saturation
        else:
            current = (current + hue / 360.0) % 1.0
            sat *= saturation
        painted = colorsys.hls_to_rgb(current, lightness, min(1.0, sat))
        pixels.append(tuple(round(channel * 255) for channel in painted) + (alpha,))
    out = Image.new("RGBA", source.size)
    out.putdata(pixels)
    return out


def write_alts(problems: list[str], write: bool) -> int:
    """Write every colourway in ``ALTS`` at every size; returns files written."""
    written = 0
    for stem, (source, hue, saturation, mode) in ALTS.items():
        master_path = THEME / "512x512@2x" / CONTEXT / f"{source}.png"
        if not master_path.is_file():
            problems.append(f"{master_path.relative_to(ROOT)}: missing for {stem}")
            continue
        with Image.open(master_path) as art:
            master = recoloured(art, hue, saturation, mode)
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                target = THEME / f"{size}x{size}{suffix}" / CONTEXT / f"{stem}.png"
                if write:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    save_png(resize(master, size * factor), target)
                    written += 1
                elif not target.is_file():
                    problems.append(f"{target.relative_to(ROOT)}: missing, expected "
                                    f"a colourway of {source}.png")
    return written


def refresh_terminal(problems: list[str], write: bool) -> int:
    """Keep ``terminal.png`` equal to the artwork drawn for TERMINAL_SOURCE."""
    source = ICONS / TERMINAL_SOURCE / "icon-1024.png"
    if not source.is_file():
        problems.append(f"{source.relative_to(ROOT)}: missing for {TERMINAL_ART}")
        return 0
    written = 0
    with Image.open(source) as drawn:
        master = drawn.convert("RGBA")
    for size in SIZES:
        for suffix, factor in (("", 1), ("@2x", 2)):
            folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
            if write:
                folder.mkdir(parents=True, exist_ok=True)
                save_png(resize(master, size * factor), folder / f"{TERMINAL_ART}.png")
                written += 1
            elif not (folder / f"{TERMINAL_ART}.png").is_file():
                problems.append(
                    f"{folder.relative_to(ROOT)}/{TERMINAL_ART}.png: missing")
    return written


def plan() -> list[tuple[str, list[str], bool, dict]]:
    """``[(slug, names, artwork_present, app), ...]`` for every discovered app."""
    out = []
    for app in discover():
        slug = slugify(app["name"])
        if not (ICONS / slug / "icon-1024.png").is_file():
            continue
        names = lookup_names(app)
        out.append((slug, names, (THEME / "48x48" / CONTEXT / f"{slug}.png").is_file(), app))
    return out


def owners() -> dict[str, str]:
    """``{lookup name: slug}``, first claimant wins.

    Two programs can declare the same name - ``Emacs`` and ``Emacs (Client)``
    both answer to ``emacs``, Wireshark and its super-user mode to
    ``org.wireshark.Wireshark``.  Only one icon can sit under a name, so the
    first app in catalogue order keeps it and the later ones leave it alone;
    otherwise the last app processed would silently steal it from the first
    and the check would disagree with the build.
    """
    table: dict[str, str] = {}
    for slug, names, _present, _app in plan():
        for name in names:
            table.setdefault(name, slug)
    return table


def link(path: Path, target: str, problems: list[str], write: bool,
         replace: bool = False) -> None:
    """Make PATH a relative symlink to TARGET (a sibling), without clobbering art.

    ``replace`` is set for the names of a borrowed icon: those have to move off
    the app's own artwork, so a real file in the way is the thing to replace.
    """
    if path.name == target:
        # The name *is* the artwork: a program mapped to its own icon, or the
        # borrowed file itself.  Nothing to point at.
        return
    if path.is_symlink():
        if os.readlink(path) == target:
            return
        if write:
            path.unlink()
        else:
            problems.append(f"{path.relative_to(ROOT)}: points at {os.readlink(path)}")
            return
    elif not path.exists():
        if not write:
            problems.append(f"{path.relative_to(ROOT)}: missing, expected a link "
                            f"to {target}")
            return
    else:
        if not replace:
            # A real file: hand-drawn artwork, or another app's icon. Never replace it.
            return
        if write:
            path.unlink()
        else:
            problems.append(f"{path.relative_to(ROOT)}: artwork, not a link to {target}")
            return
    if write:
        path.symlink_to(target)


def install_artwork(slug: str, present: bool, problems: list[str], write: bool) -> int:
    """Write one app's own drawing into the theme at every size.

    Returns the number of files written.  Kept apart from the linking loop so
    that the artwork a colourway is cut from is on disk before the colourway
    is (see ``install``).
    """
    with Image.open(ICONS / slug / "icon-1024.png") as source:
        master = source.convert("RGBA")
    written = 0
    for size in SIZES:
        for suffix, factor in (("", 1), ("@2x", 2)):
            folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
            target = folder / f"{slug}.png"
            if target.exists() and present:
                continue
            if write:
                folder.mkdir(parents=True, exist_ok=True)
                save_png(resize(master, size * factor), target)
                written += 1
            else:
                problems.append(f"{target.relative_to(ROOT)}: missing")
    return written


def prune_own_artwork(problems: list[str], write: bool) -> int:
    """Take the theme's answer back off the names in ``OWN_ARTWORK``.

    Returns the number of files cleared.  The scalable wrapper goes with the
    bitmaps: leaving it would keep the icon answering in the toolkits that
    prefer a scalable file, which is most of them, so the program's own icon
    would stay hidden exactly where it was.
    """
    cleared = 0
    for name in sorted(OWN_ARTWORK):
        paths = [THEME / f"{size}x{size}{suffix}" / CONTEXT / f"{name}.png"
                 for size in SIZES for suffix in ("", "@2x")]
        paths.append(THEME / "scalable" / CONTEXT / f"{name}.svg")
        for path in paths:
            if not (path.is_symlink() or path.exists()):
                continue
            if write:
                path.unlink()
                cleared += 1
            else:
                problems.append(f"{path.relative_to(ROOT)}: the theme answers for {name}, "
                                f"which ships its own icon - run make_theme_apps.py")
    return cleared


def install(write: bool) -> tuple[int, int, int, list[str]]:
    problems: list[str] = []
    written = linked = 0
    owner = owners()
    apps = plan()

    # Before anything is linked: a name this step is not allowed to answer for
    # comes off the theme, so a rebuild cannot leave an override in place.
    cleared = prune_own_artwork(problems, write)

    # The artwork goes in first, for every app that answers with its own
    # drawing.  Two later steps read it back: a colourway is cut from a
    # borrowed icon's bitmap (``write_alts``) and a name points at one, so
    # without this pass adding an icon took two runs - the first to install
    # the artwork, the second to link the names and cut the alts that needed
    # it.  A borrowed app needs nothing here: its artwork is another app's,
    # and arrives with that one.
    for slug, _names, present, app in apps:
        if borrowed(app):
            continue
        written += install_artwork(slug, present, problems, write)

    # The shared terminal artwork is the icon drawn for the terminal archetype,
    # so keep it equal to TERMINAL_SOURCE's own drawing: one emulator's icon
    # changing means all of them change, instead of a stale committed copy
    # sitting under terminal.png for years.  This runs before the colourways
    # because terminal-red is cut from it.
    written += refresh_terminal(problems, write)
    written += write_alts(problems, write)

    for slug, names, present, app in apps:
        art = borrowed(app)
        # A name the colourway table dresses is left to the loop at the end of
        # this function, which runs *after* this one and points it at the
        # alternate artwork instead.  Linking - or in check mode reporting - the
        # base target here would be describing a state the build only passes
        # through: the name is written twice in one run, so a check that looked
        # at the first target failed on every name the table has an alternate
        # for, however correct the tree on disk was.  The names in OWN_ARTWORK
        # are left alone for the other reason: they are not the theme's to link.
        dressed = frozenset(BORROWED_NAMES) | OWN_ARTWORK
        for size in SIZES:
            for suffix in ("", "@2x"):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                if art:
                    # The artwork is committed in the theme; only the names move.
                    icon = folder / f"{art}.png"
                    if not icon.is_file():
                        problems.append(f"{icon.relative_to(ROOT)}: missing for {slug}")
                        continue
                    # The app's own name always moves; a shared alias stays
                    # with the app that claimed it (see owners()).
                    wanted = [name for name in names
                              if name not in dressed
                              and (name == slug or owner.get(name) == slug)]
                else:
                    wanted = [alias for alias in names[1:]
                              if alias not in dressed and owner.get(alias) == slug]
                for name in wanted:
                    alias_path = folder / f"{name}.png"
                    before = alias_path.is_symlink() or alias_path.exists()
                    link(alias_path, f"{art or slug}.png", problems, write, replace=bool(art))
                    if write and not before:
                        linked += 1

    # "a terminal" is a name a launcher asks for without naming any program.
    for size in SIZES:
        for suffix in ("", "@2x"):
            folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
            if not (folder / f"{TERMINAL_ART}.png").is_file():
                continue
            for name in GENERIC_TERMINAL_NAMES:
                if owner.get(name):
                    continue
                path = folder / f"{name}.png"
                before = path.is_symlink() or path.exists()
                link(path, f"{TERMINAL_ART}.png", problems, write)
                if write and not before:
                    linked += 1

    # Programs no desktop entry here declares: a menu alias, a dock's own
    # button, a Wine export.  They answer with the artwork they are mapped to,
    # so a launcher that names them gets a tile instead of a generic gear.
    for name, art in sorted(BORROWED_NAMES.items()):
        for size in SIZES:
            for suffix in ("", "@2x"):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                if not (folder / f"{art}.png").is_file():
                    continue
                path = folder / f"{name}.png"
                before = path.is_symlink() or path.exists()
                link(path, f"{art}.png", problems, write, replace=True)
                if write and not before:
                    linked += 1
    return written, linked, cleared, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report what is missing instead of writing")
    args = parser.parse_args(argv)

    write = not args.check
    written, linked, cleared, problems = install(write)
    apps = plan()
    aliases = sum(len(names) - 1 for _slug, names, _present, _app in apps)

    if problems:
        for problem in problems[:40]:
            print(f"  {problem}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more", file=sys.stderr)
        print(f"\n{len(problems)} app icon problem(s)", file=sys.stderr)
        return 1
    if write:
        print(f"apps: {len(apps)} icon(s), {written} bitmap(s), "
              f"{aliases} alias name(s) in the theme"
              + (f", {cleared} own-artwork name(s) cleared" if cleared else ""))
    else:
        print(f"ok: {len(apps)} app icon(s) and {aliases} alias name(s) are in the theme")
    return 0


if __name__ == "__main__":
    sys.exit(main())
