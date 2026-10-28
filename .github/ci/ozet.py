#!/usr/bin/env python3
"""CI yardimcisi: bir gunluk dosyasinin son satirlarini GitHub 'annotation' olarak yazar.

Gunluk metni genel API'den (check-runs/<id>/annotations) okunabilir; boylece bir adim
basarisiz oldugunda nedeni, oturum acmadan gunlugu indirmeden gorulebilir.

Kullanim:  python3 ozet.py GUNLUK_DOSYASI "baslik" [SATIR_SAYISI]
"""
import sys


def kac(m: str) -> str:
    return m.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Windows konsolu cp1252 olabilir
    except (AttributeError, ValueError):
        pass
    yol = sys.argv[1]
    baslik = sys.argv[2] if len(sys.argv) > 2 else "gunluk"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            satirlar = f.read().splitlines()
    except OSError as e:
        import os
        satirlar = ["(gunluk okunamadi: %s)" % e, "cwd=" + os.getcwd(), "dosyalar: " + ", ".join(sorted(os.listdir("."))[:40])]
    if len(sys.argv) > 4:                      # yalniz kalibe uyan satirlar (ornegin FAIL/ERROR adlari)
        import re
        kalip = re.compile(sys.argv[4])
        satirlar = [s for s in satirlar if kalip.search(s)]
    son = [s[:300] for s in satirlar[-n:]]
    import os as _os
    seviye = _os.environ.get("OZET_SEVIYE", "error")          # error | notice | warning
    print("::%s title=%s::%s" % (seviye, kac(baslik), kac("\n".join(son))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
