# -*- mode: python ; coding: utf-8 -*-
# PyInstaller ayari: MSYS2 MINGW64 icinde calistirilir.
#   cd packaging/windows && python -m PyInstaller --noconfirm filenor.spec
# Sonuc: dist/Filenor/  (Filenor.exe = arayuz, filenor-cli.exe = komut satiri; ayni kutuphaneleri paylasirlar)
import os

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

KOK = os.path.abspath(os.path.join(SPECPATH, "..", ".."))
UYG = os.path.join(KOK, "filenor")
IKON = os.path.join(UYG, "simge", "filenor.ico")

GI_MODULLER = [
    "gi", "gi.repository.Gtk", "gi.repository.Gdk", "gi.repository.GdkPixbuf", "gi.repository.Gio",
    "gi.repository.GLib", "gi.repository.GObject", "gi.repository.Pango", "gi.repository.PangoCairo",
    "gi.repository.Atk", "gi.repository.cairo", "gi.repository.HarfBuzz", "gi._gi_cairo", "cairo",
]
KOD_MODULLERI = [
    "filenor_araclar", "filenor_dil", "filenor_kurulum", "filenor_metin", "filenor_motor",
    "filenor_simge", "filenor_sistem", "filenor_cli", "tema",
]
# kodda islev icinde (tembel) iceri alinan paketler
TEMBEL = ["PIL", "PIL.Image", "PIL.ImageOps", "PIL.ImageSequence", "PIL.features", "reportlab", "fontTools",
          "fontTools.ttLib", "brotli", "cairosvg", "cairocffi", "pypdf"]

veriler = [
    (os.path.join(UYG, "simge"), "simge"),
    (os.path.join(UYG, "yazi"), "yazi"),
]
for paket in ("reportlab", "cairosvg", "cairocffi", "fontTools", "tinycss2", "cssselect2", "defusedxml"):
    try:
        veriler += collect_data_files(paket)
    except Exception:
        pass
gizli = GI_MODULLER + KOD_MODULLERI + TEMBEL
for paket in ("reportlab.pdfbase", "reportlab.lib", "reportlab.pdfgen", "fontTools.ttLib.tables"):
    try:
        gizli += collect_submodules(paket)
    except Exception:
        pass
GEREKSIZ = ["tkinter", "matplotlib", "numpy.testing", "pytest", "IPython", "setuptools", "pip", "wheel"]

a_gui = Analysis([os.path.join(UYG, "filenor_uygulama.py")], pathex=[UYG], datas=veriler,
                 hiddenimports=gizli, excludes=GEREKSIZ, noarchive=False)
a_cli = Analysis([os.path.join(UYG, "filenor_cli.py")], pathex=[UYG], datas=[],
                 hiddenimports=KOD_MODULLERI + TEMBEL, excludes=GEREKSIZ + ["gi"], noarchive=False)
MERGE((a_gui, "filenor_uygulama", "Filenor"), (a_cli, "filenor_cli", "filenor-cli"))

pyz_gui = PYZ(a_gui.pure)
pyz_cli = PYZ(a_cli.pure)
exe_gui = EXE(pyz_gui, a_gui.scripts, [], exclude_binaries=True, name="Filenor", console=False,
              icon=IKON, debug=False, strip=False, upx=False)
exe_cli = EXE(pyz_cli, a_cli.scripts, [], exclude_binaries=True, name="filenor-cli", console=True,
              icon=IKON, debug=False, strip=False, upx=False)
COLLECT(exe_gui, a_gui.binaries, a_gui.datas,
        exe_cli, a_cli.binaries, a_cli.datas,
        strip=False, upx=False, name="Filenor")
