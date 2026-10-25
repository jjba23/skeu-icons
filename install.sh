#!/usr/bin/env bash
# Install the "Skeu Icons" icon themes.
#
#   ./install.sh                  install for the current user (~/.local/share/icons)
#   sudo ./install.sh --system    install for every user (/usr/share/icons)
#   ./install.sh --dry-run        show what would happen, change nothing
#   ./install.sh --uninstall      remove the themes again (same as ./uninstall.sh)
#
# Every theme in the pack is installed together, because the variants are symlink
# trees that inherit from the base theme and must sit beside it:
#
#   skeu-icons                     the pack as drawn
#   skeu-icons-dark                the same artwork, light-ink symbolic icons
#   skeu-icons-<accent>            one per accent: red, orange, yellow, lime,
#   skeu-icons-<accent>-dark       green, teal, cyan, blue, indigo, violet,
#                                  magenta, pink, brown, graphite
#
# Pick one in your desktop's icon settings:
#   GNOME   Tweaks -> Appearance -> Icons
#   XFCE    Settings -> Appearance -> Icons
#   KDE     System Settings -> Appearance -> Icons
#   Cinnamon/MATE/LXQt: the equivalent Appearance dialog
set -euo pipefail

base_dir="skeu-icons"
theme_name="Skeu Icons"
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

dest_root="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
dry_run=0
uninstall=0

for arg in "$@"; do
    case "$arg" in
        --system)    dest_root="/usr/share/icons" ;;
        --dry-run)   dry_run=1 ;;
        --uninstall) uninstall=1 ;;
        -h|--help)   sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)           printf 'error: unknown option %s (try --help)\n' "$arg" >&2; exit 2 ;;
    esac
done

if [ "$dest_root" = "/usr/share/icons" ] && [ "$(id -u)" -ne 0 ] && [ "$dry_run" -eq 0 ]; then
    echo "error: --system installs into /usr/share/icons and needs root" >&2
    exit 1
fi

refresh_cache() {
    local dir=$1
    for tool in gtk-update-icon-cache gtk4-update-icon-cache; do
        if command -v "$tool" >/dev/null 2>&1; then
            "$tool" -f -t "$dir" >/dev/null 2>&1 || true
        fi
    done
    if command -v kbuildsycoca6 >/dev/null 2>&1; then kbuildsycoca6 >/dev/null 2>&1 || true
    elif command -v kbuildsycoca5 >/dev/null 2>&1; then kbuildsycoca5 >/dev/null 2>&1 || true
    fi
}

run() {
    if [ "$dry_run" -eq 1 ]; then printf '  would: %s\n' "$*"; else "$@"; fi
}

# The uninstaller owns removal, so the two scripts cannot drift apart.
if [ "$uninstall" -eq 1 ]; then
    extra=()
    if [ "$dry_run" -eq 1 ]; then extra+=(--dry-run); fi
    exec "$here/uninstall.sh" "--root=$dest_root" "${extra[@]}"
fi

# Every theme the pack builds, base first: the variants link into it.
themes=()
while IFS= read -r name; do
    themes+=("$name")
done < <(find "$here" -maxdepth 2 -name index.theme -printf '%h\n' | xargs -r -n1 basename)
themes=("$base_dir" $(printf '%s\n' "${themes[@]}" | grep -v -x "$base_dir" | sort))

for theme in "${themes[@]}"; do
    if [ ! -f "$here/$theme/index.theme" ]; then
        echo "error: $here/$theme/index.theme not found — run this from the pack root" >&2
        exit 1
    fi
done

echo "installing \"$theme_name\" (${#themes[@]} themes) into $dest_root"
run mkdir -p -- "$dest_root"

for theme in "${themes[@]}"; do
    source_dir="$here/$theme"
    target="$dest_root/$theme"
    # Replace a previous install wholesale so stale icons never linger.
    if [ -e "$target" ] || [ -L "$target" ]; then run rm -rf -- "$target"; fi
    run cp -a -- "$source_dir" "$dest_root/"
    run refresh_cache "$target"
done

if [ "$dry_run" -eq 0 ]; then
    count() { find "$1" \( -type f -o -type l \) | wc -l; }
    for theme in "${themes[@]}"; do
        printf '  %-28s %6s files  %s\n' \
            "$theme" "$(count "$dest_root/$theme")" \
            "$(grep -m1 '^Name=' "$dest_root/$theme/index.theme" | cut -d= -f2-)"
    done
    echo "done: select one of them in your desktop's icon settings"
fi
