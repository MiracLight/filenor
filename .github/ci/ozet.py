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
    yol = sys.argv[1]
    baslik = sys.argv[2] if len(sys.argv) > 2 else "gunluk"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            satirlar = f.read().splitlines()
    except OSError as e:
        satirlar = ["(gunluk okunamadi: %s)" % e]
    son = [s[:300] for s in satirlar[-n:]]
    print("::error title=%s::%s" % (kac(baslik), kac("\n".join(son))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
