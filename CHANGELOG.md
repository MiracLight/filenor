# Changelog / Değişiklik günlüğü

## 2.0.1

**EN** — Security review fixes from the CarotOS 1.4 audit, a new icon and a safer way to install missing Python modules.

- Images open only as raster formats (the EPS/Ghostscript route is closed). ffmpeg input is limited to the `file` protocol and the allowed containers.
- The worker always finishes, and a ZIP error is shown instead of being swallowed. Helper processes and work folders are cleaned up when you quit.
- The `qpdf` password no longer appears on the command line. File names are trimmed by byte length, and a name that starts with a dot is never passed to LibreOffice as an option.
- Folder scans, animation frames, page counts and disk use have limits.
- Installing a missing module from PyPI now asks first and no longer uses `--break-system-packages` (`pip --user`, or a virtual environment in your own folder if that fails).
- New icon.

**TR** — CarotOS 1.4 güvenlik denetiminden gelen düzeltmeler, yeni simge ve eksik Python modüllerini kurmanın daha güvenli yolu.

- Görseller yalnızca raster biçimlerle açılır (EPS/Ghostscript yolu kapatıldı). ffmpeg girdisi `file` protokolü ve izin verilen kapsayıcılarla sınırlandı.
- Çalışan iş parçacığı her durumda biter ve ZIP hatası yutulmak yerine gösterilir. Kapanırken yardımcı süreçler ve iş klasörleri temizlenir.
- `qpdf` parolası artık komut satırında görünmez. Dosya adları bayta göre kırpılır, noktayla başlayan bir ad LibreOffice'e hiçbir zaman seçenek olarak gitmez.
- Klasör taraması, animasyon kareleri, sayfa sayısı ve disk kullanımı sınırlandı.
- Eksik bir modülü PyPI'dan kurmadan önce onay istenir ve `--break-system-packages` kullanılmaz (`pip --user`, olmazsa kendi klasöründe sanal ortam).
- Yeni simge.

## 2.0.0

**EN** — Complete rewrite on a GTK 3 interface (the CarotOS design language) with a new, shared conversion engine.

- New interface: drag & drop, batch queue, per-file progress, cancel, dark/light theme, Turkish/English.
- New engine: every conversion goes through a hidden work folder and never overwrites existing files (`name (1).ext`); external programs run in their own process group and are stopped on cancel or timeout.
- More formats: images (incl. HEIC, camera RAW, SVG, AVIF), audio, video, GIF, PDF ↔ images/text, Office documents/sheets/slides (via LibreOffice), fonts (TTF/OTF/WOFF/WOFF2).
- Tools: merge / split / select pages / rotate / shrink / lock / unlock PDFs, OCR, image shrink + metadata removal, audio/video trim.
- One-click installation of missing tools (Settings → Install): `apt` on Debian/Ubuntu, `winget` on Windows.
- Command line: `filenor-cli` (convert, tools, status, install).
- Runs on Debian/Ubuntu (`.deb`) and Windows (zip + installer).
- Fixed in the original: `txt → html` crash, impossible `pdf → xlsx` / `docx → pptx` routes (removed), wrong import filters for `pdf → docx` / `html → docx`, same-name outputs overwriting each other, ignored EXIF orientation, transparent PNG → JPG turning black, odd-sized video failing in libx264, Turkish characters in `txt → pdf`, fake `ttf → otf`, Windows-only `os.startfile`, missing cancel/progress/timeout, unsafe temp paths.

**TR** — GTK 3 arayüzüne (CarotOS tasarım dili) ve yeni ortak dönüştürme motoruna tam yeniden yazım.

- Yeni arayüz: sürükle-bırak, toplu kuyruk, dosya başına ilerleme, iptal, koyu/açık tema, Türkçe/İngilizce.
- Yeni motor: her dönüşüm gizli bir çalışma klasöründe yapılır ve var olan dosyaların üzerine yazmaz (`ad (1).uzantı`); dış programlar kendi süreç grubunda çalışır, iptalde ya da zaman aşımında durdurulur.
- Daha çok biçim: görsel (HEIC, kamera RAW, SVG, AVIF dahil), ses, video, GIF, PDF ↔ görsel/metin, ofis belgeleri/tablolar/sunumlar (LibreOffice ile), yazı tipleri.
- Araçlar: PDF birleştir / böl / sayfa seç / döndür / küçült / kilitle / kilidi aç, OCR, görsel küçült + üstveri temizle, ses/video kırp.
- Eksik araçların tek tıkla kurulumu (Ayarlar → Kur): Debian/Ubuntu'da `apt`, Windows'ta `winget`.
- Komut satırı: `filenor-cli`.
- Debian/Ubuntu (`.deb`) ve Windows (zip + kurulum sihirbazı).
- Özgün sürümdeki hatalar giderildi: `txt → html` çökmesi, mümkün olmayan `pdf → xlsx` / `docx → pptx` yolları (kaldırıldı), `pdf → docx` / `html → docx` için yanlış içe aktarma süzgeci, aynı adlı çıktıların birbirini ezmesi, EXIF yönünün yok sayılması, saydam PNG → JPG'de siyah zemin, tek sayılı boyutlu videonun libx264'te hata vermesi, `txt → pdf`'te Türkçe karakterler, sahte `ttf → otf`, yalnızca Windows'ta çalışan `os.startfile`, iptal/ilerleme/zaman aşımı eksikliği, güvensiz geçici yollar.

## 1.0

Original single-file version (`legacy/Filenor_v1.py`, customtkinter, Windows).
