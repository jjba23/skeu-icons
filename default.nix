# default.nix --- skeu-icons, built and installed the Nix way.

# Copyright © Josep Bigorra <jjbigorra@gmail.com>

# skeu-icons is licensed under the Creative Commons Attribution-ShareAlike 4.0
# International licence; see LICENSE for the terms.

{
  lib,
  stdenv,
}:

stdenv.mkDerivation (finalAttrs: {
  pname = "skeu-icons";
  version = "1.9.1";

  src = ./.;

  # The themes are committed artwork, not something compiled here: the drawing
  # programmes run when a set is redrawn, and `maak check' verifies them.
  dontConfigure = true;
  dontBuild = true;

  installPhase = ''
    runHook preInstall

    # Every directory with an index.theme is one theme.  The accent and dark
    # variants are trees of relative symlinks into skeu-icons, so they are
    # copied as links (`cp -a', never `cp -r') and keep pointing at their
    # parent once they sit side by side under share/icons.
    mkdir -p "$out/share/icons"
    for theme in skeu-icons*/; do
      test -f "$theme/index.theme" || continue
      cp -a "$theme" "$out/share/icons/"
    done

    runHook postInstall
  '';

  doInstallCheck = true;
  installCheckPhase = ''
    runHook preInstallCheck

    # A theme without index.theme is invisible to the toolkit, a theme that is
    # missing a size answers at the wrong scale, and a dangling alias is an
    # icon that silently falls back to Adwaita.  All three are cheap to ask.
    for theme in "$out"/share/icons/*/; do
      test -f "''${theme}index.theme" || {
        echo "missing index.theme in ''${theme}" >&2
        exit 1
      }
    done

    test -f "$out/share/icons/skeu-icons/48x48/mimetypes/application-zip.png"
    test -f "$out/share/icons/skeu-icons/scalable/mimetypes/application-x-compressed-tar.svg"
    test -f "$out/share/icons/skeu-icons/512x512/apps/org.mozilla.firefox.png"
    test "$(readlink "$out/share/icons/skeu-icons/512x512/apps/org.mozilla.firefox.png")" = "firefox.png"

    if [ -n "$(find "$out/share/icons" -xtype l)" ]; then
      echo "dangling symlinks in the installed themes:" >&2
      find "$out/share/icons" -xtype l >&2
      exit 1
    fi

    runHook postInstallCheck
  '';

  meta = with lib; {
    description = "Skeuomorphic icon theme for Linux desktops, with symbolic and accent variants";
    homepage = "https://codeberg.org/jjba23/skeu-icons";
    license = licenses.cc-by-sa-40;
    platforms = platforms.linux;
  };
})
