#!/bin/sh
# Filenor .deb paketini uretir.   Kullanim:  packaging/debian/build-deb.sh SURUM [CIKTI_DIZINI]
# Ornek:  packaging/debian/build-deb.sh 2.0.0 dist
# Gerekli: dpkg-deb (dpkg), fakeroot gerekmez (--root-owner-group).
set -eu

SURUM="${1:?kullanim: build-deb.sh SURUM [CIKTI_DIZINI]}"
SURUM="${SURUM#v}"
CIKTI="${2:-dist}"
KOK="$(cd "$(dirname "$0")/../.." && pwd)"
GECICI="$(mktemp -d)"
trap 'rm -rf "$GECICI"' EXIT
PAKET="$GECICI/filenor_${SURUM}_all"

install -d "$PAKET/DEBIAN" "$PAKET/usr/lib/filenor" "$PAKET/usr/bin" \
    "$PAKET/usr/share/applications" "$PAKET/usr/share/doc/filenor" \
    "$PAKET/usr/share/icons/hicolor/scalable/apps"

# uygulama kodu (bayt kodu ve onbellek disarida)
( cd "$KOK/filenor" && find . -type f ! -name '*.pyc' ! -path '*/__pycache__/*' ! -name '*.ico' ! -name 'filenor-[0-9]*.png' -print ) |
while read -r d; do
    install -D -m 644 "$KOK/filenor/$d" "$PAKET/usr/lib/filenor/$d"
done
chmod 755 "$PAKET/usr/lib/filenor/filenor_uygulama.py" "$PAKET/usr/lib/filenor/filenor_cli.py" "$PAKET/usr/lib/filenor/filenor-cli"

# komutlar
cat > "$PAKET/usr/bin/filenor" <<'EOT'
#!/bin/sh
exec /usr/bin/python3 /usr/lib/filenor/filenor_uygulama.py "$@"
EOT
cat > "$PAKET/usr/bin/filenor-cli" <<'EOT'
#!/bin/sh
exec /usr/bin/python3 /usr/lib/filenor/filenor_cli.py "$@"
EOT
chmod 755 "$PAKET/usr/bin/filenor" "$PAKET/usr/bin/filenor-cli"

# menu girdisi ve simgeler
install -m 644 "$KOK/packaging/linux/filenor.desktop" "$PAKET/usr/share/applications/filenor.desktop"
install -m 644 "$KOK/filenor/simge/filenor.svg" "$PAKET/usr/share/icons/hicolor/scalable/apps/filenor.svg"
for b in 16 22 24 32 48 64 128 256; do
    install -D -m 644 "$KOK/filenor/simge/filenor-$b.png" "$PAKET/usr/share/icons/hicolor/${b}x${b}/apps/filenor.png"
done

# belgeler
install -m 644 "$KOK/LICENSE" "$PAKET/usr/share/doc/filenor/copyright"
gzip -9nc "$KOK/CHANGELOG.md" > "$PAKET/usr/share/doc/filenor/changelog.gz"
chmod 644 "$PAKET/usr/share/doc/filenor/changelog.gz"

# kontrol dosyasi
BOYUT="$(du -sk "$PAKET" | cut -f1)"
cat > "$PAKET/DEBIAN/control" <<EOT
Package: filenor
Version: $SURUM
Section: utils
Priority: optional
Architecture: all
Installed-Size: $BOYUT
Maintainer: MiracLight <MiracLight@users.noreply.github.com>
Homepage: https://github.com/MiracLight/filenor
Depends: python3 (>= 3.9), python3-gi, python3-gi-cairo, gir1.2-gtk-3.0, python3-pil, librsvg2-common
Recommends: ffmpeg, poppler-utils, qpdf, tesseract-ocr, tesseract-ocr-tur, python3-reportlab, python3-fonttools, python3-brotli, python3-cairosvg, python3-pypdf, fonts-dejavu-core, pkexec | policykit-1
Suggests: libreoffice-writer, libreoffice-calc, libreoffice-impress, ghostscript, python3-pillow-heif, python3-pip
Description: Dosya ve medya donusturucu / File and media converter
 Filenor converts images, audio, video, documents, spreadsheets, slides and
 fonts, and merges, splits, locks and OCRs PDFs. Everything runs on your own
 computer; files are never uploaded.
 .
 Eksik araclar uygulamanin Ayarlar sayfasindan tek tikla kurulabilir.
 Missing tools can be installed with one click from the Settings page.
EOT

mkdir -p "$CIKTI"
dpkg-deb --build --root-owner-group "$PAKET" "$CIKTI/filenor_${SURUM}_all.deb" >/dev/null
echo "$CIKTI/filenor_${SURUM}_all.deb"
