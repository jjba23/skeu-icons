#!/usr/bin/env bash
# Install the "Skeu Icons" icon theme.
#
#   ./install.sh                  install for the current user (~/.local/share/icons)
#   sudo ./install.sh --system    install for every user (/usr/share/icons)
#   ./install.sh --dry-run        show what would happen, change nothing
#   ./install.sh --uninstall      remove the theme again
#
# After installing, pick "Skeu Icons" in your desktop's icon settings:
#   GNOME   Tweaks -> Appearance -> Icons
#   XFCE    Settings -> Appearance -> Icons
#   KDE     System Settings -> Appearance -> Icons
#   Cinnamon/MATE/LXQt: the equivalent Appearance dialog
set -euo pipefail

theme_dir="skeu-icons"
theme_name="Skeu Icons"
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source_dir="$here/$theme_dir"

dest_root="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
dry_run=0
uninstall=0

for arg in "$@"; do
    case "$arg" in
        --system)    dest_root="/usr/share/icons" ;;
        --dry-run)   dry_run=1 ;;
        --uninstall) uninstall=1 ;;
        -h|--help)   sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)           printf 'error: unknown option %s (try --help)\n' "$arg" >&2; exit 2 ;;
    esac
done

target="$dest_root/$theme_dir"

if [ "$dest_root" = "/usr/share/icons" ] && [ "$(id -u)" -ne 0 ] && [ "$dry_run" -eq 0 ]; then
    echo "error: --system installs into /usr/share/icons and needs root" >&2
    exit 1
fi

refresh_cache() {
    local dir=$1
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t "$dir" >/dev/null 2>&1 || true
    fi
    if command -v kbuildsycoca6 >/dev/null 2>&1; then kbuildsycoca6 >/dev/null 2>&1 || true
    elif command -v kbuildsycoca5 >/dev/null 2>&1; then kbuildsycoca5 >/dev/null 2>&1 || true
    fi
}

run() {
    if [ "$dry_run" -eq 1 ]; then printf '  would: %s\n' "$*"; else "$@"; fi
}

if [ "$uninstall" -eq 1 ]; then
    if [ ! -d "$target" ]; then
        echo "nothing to remove: $target does not exist"
        exit 0
    fi
    echo "removing $target"
    run rm -rf -- "$target"
    run refresh_cache "$dest_root"
    exit 0
fi

if [ ! -f "$source_dir/index.theme" ]; then
    echo "error: $source_dir/index.theme not found — run this from the pack root" >&2
    exit 1
fi

echo "installing \"$theme_name\" into $target"
run mkdir -p -- "$dest_root"
# Replace a previous install wholesale so stale icons never linger.
if [ -d "$target" ]; then run rm -rf -- "$target"; fi
run cp -a -- "$source_dir" "$dest_root/"
run refresh_cache "$target"

if [ "$dry_run" -eq 0 ]; then
    icons=$(find "$target" -name '*.png' | wc -l)
    echo "done: $icons PNG files installed"
    echo "now select \"$theme_name\" in your desktop's icon settings"
fi
