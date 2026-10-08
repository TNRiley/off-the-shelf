"""Download the OCR (ALTO XML) of a Gallica document page by page and flatten it to text.

    python fetch_gallica.py bpt6k946633g 690

Gallica's HTML text view (.texteBrut) now sits behind an ALTCHA proof-of-work page, but the
documented RequestDigitalElement endpoint still serves ALTO one page at a time. Pages are cached
under src/raw/gallica/<ark>/ so a rerun only fetches what is missing. Writes
src/raw/gallica/<ark>.txt with a "=== page N" line before each page.
"""
import os, re, sys, time, urllib.request
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "{http://www.loc.gov/standards/alto/ns-v3#}"


def page_text(xml):
    root = ET.fromstring(xml)
    lines = []
    for tl in root.iter(NS + "TextLine"):
        words = [s.get("CONTENT", "") for s in tl.iter(NS + "String")]
        lines.append(" ".join(words))
    return "\n".join(lines)


def main(ark, n):
    d = os.path.join(HERE, "raw", "gallica", ark)
    os.makedirs(d, exist_ok=True)
    out = []
    for p in range(1, n + 1):
        fn = os.path.join(d, f"{p:04d}.xml")
        if not os.path.exists(fn):
            url = f"https://gallica.bnf.fr/RequestDigitalElement?O={ark}&E=ALTO&Deb={p}"
            for attempt in range(4):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (off-the-shelf research)"})
                    with urllib.request.urlopen(req, timeout=90) as r:
                        data = r.read()
                    if not data.lstrip().startswith(b"<?xml"):
                        raise ValueError("not ALTO")
                    open(fn, "wb").write(data)
                    break
                except Exception as e:
                    print("page", p, "retry", attempt, e, file=sys.stderr)
                    time.sleep(5 + 10 * attempt)
            else:
                print("page", p, "skipped", file=sys.stderr)
                continue
            time.sleep(0.6)
        try:
            out.append(f"=== page {p}\n" + page_text(open(fn, "rb").read()))
        except ET.ParseError as e:
            print("page", p, "unparseable", e, file=sys.stderr)
        if p % 50 == 0:
            print("page", p, file=sys.stderr)
    with open(os.path.join(HERE, "raw", "gallica", ark + ".txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
