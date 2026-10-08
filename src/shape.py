"""Shape src/raw/paintings.json into the page payload, src/payload.json.

    python -P shape.py

Every statistic on the page is computed in the browser from these arrays. This script only
encodes, checks, and prints the expected values that REBUILD.md quotes.
"""
import base64, json, os, struct, sys
from array import array

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

NATS = ["other", "French", "American", "British", "Spanish", "Italian", "Dutch", "German", "Belgian", "Russian",
        "Flemish", "Swiss"]
NAT_ALIAS = {"English": "British", "Scottish": "British", "Welsh": "British", "Irish": "British",
             "British, Scottish": "British"}
SUBJECTS = ["untagged", "other", "portrait", "landscape", "sea"]

# The French stock sizes, long x short in cm (figure, paysage, marine), as charted on English
# Wikipedia "French standard sizes for oil paintings" (CC BY-SA), after Haaf 1987.
FRENCH = {0: (18, 14, 12, 10), 1: (22, 16, 14, 12), 2: (24, 19, 16, 14), 3: (27, 22, 19, 16), 4: (33, 24, 22, 19),
          5: (35, 27, 24, 22), 6: (41, 33, 27, 24), 8: (46, 38, 33, 27), 10: (55, 46, 38, 33), 12: (61, 50, 46, 38),
          15: (65, 54, 50, 46), 20: (73, 60, 54, 50), 25: (81, 65, 60, 54), 30: (92, 73, 65, 60),
          40: (100, 81, 73, 65), 50: (116, 89, 81, 73), 60: (130, 97, 89, 81), 80: (146, 114, 97, 89),
          100: (162, 130, 114, 97), 120: (195, 130, 114, 97)}
# Stretched canvas sizes in inches, F. W. Devoe & Co., Priced catalogue of artists' materials (New
# York, c.1900), p.16-17, "Single Prime, Smooth, or Roman Canvas on Stretchers". 6x8 is OCR'd "Gx 8".
DEVOE = [(6, 8), (6, 11), (7, 12), (8, 10), (8, 14), (9, 12), (10, 12), (10, 14), (10, 18), (12, 14), (12, 16),
         (12, 18), (12, 20), (12, 22), (14, 17), (14, 20), (14, 24), (16, 20), (16, 22), (16, 24), (16, 28),
         (17, 21), (18, 24), (18, 30), (18, 33), (20, 24), (20, 26), (20, 30), (20, 36), (22, 27), (22, 30),
         (22, 36), (22, 38), (24, 34), (24, 42), (25, 30), (26, 36), (27, 34), (28, 40), (29, 36), (30, 40),
         (30, 46), (34, 44), (36, 42), (40, 50)]


def b64(typecode, values):
    a = array(typecode, values)
    if sys.byteorder != "little":
        a.byteswap()
    return base64.b64encode(a.tobytes()).decode()


def nat_code(n):
    n = n.strip()
    n = NAT_ALIAS.get(n, n)
    head = n.split(",")[0].strip()
    head = NAT_ALIAS.get(head, head)
    return NATS.index(head) if head in NATS else 0


def main():
    rows = json.load(open(os.path.join(HERE, "raw", "paintings.json"), encoding="utf-8"))
    rows = [r for r in rows if 5 <= r["S"] and r["L"] <= 1000]
    rows.sort(key=lambda r: (r["museum"], r["year"] or 0, r["L"]))
    artists = sorted({r["artist"] for r in rows})
    aidx = {a: i for i, a in enumerate(artists)}
    meta = json.load(open(os.path.join(HERE, "raw", "aic_paintings.json"), encoding="utf-8"))["fetched"]

    payload = {
        "n": len(rows),
        "museum": b64("B", [0 if r["museum"] == "met" else 1 for r in rows]),
        "year": b64("h", [r["year"] if isinstance(r["year"], int) and -3000 < r["year"] < 2100 else -32768 for r in rows]),
        "nat": b64("B", [nat_code(r["nat"]) for r in rows]),
        "L": b64("H", [round(r["L"] * 10) for r in rows]),
        "S": b64("H", [round(r["S"] * 10) for r in rows]),
        "subj": b64("B", [SUBJECTS.index(r["subject"]) for r in rows]),
        "alt": b64("B", [1 if r["altered"] else 0 for r in rows]),
        "artist": b64("H", [aidx[r["artist"]] for r in rows]),
        "oid": b64("I", [int(r["id"]) for r in rows]),
        "title": [r["title"][:90] for r in rows],
        "artists": artists, "nats": NATS, "subjects": SUBJECTS,
        "french": [[n, *v] for n, v in FRENCH.items()],
        "devoe": DEVOE,
        "fetched": {"aic": meta, "met": "2026-10-08"},
    }
    with open(os.path.join(HERE, "payload.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    # checks and the expected values REBUILD.md quotes
    grid = [(L, s, n, f) for n, (L, F, P, M) in FRENCH.items() for s, f in ((F, "F"), (P, "P"), (M, "M"))]
    assert len(grid) == 60

    def hit(r, k=1.0):
        return min(max(abs(r["L"] - g[0] * k), abs(r["S"] - g[1] * k)) for g in grid) <= 1.0

    dec = [0.90, 0.92, 0.94, 0.96, 1.04, 1.06, 1.08, 1.10]
    for m in ("met", "aic"):
        g = [r for r in rows if r["museum"] == m and nat_code(r["nat"]) == 1 and isinstance(r["year"], int)
             and 1840 <= r["year"] <= 1929 and not r["altered"]]
        real = sum(map(hit, g)) / len(g)
        d = sum(sum(hit(r, k) for r in g) / len(g) for k in dec) / len(dec)
        print(f"{m}: French 1840-1929 n={len(g)} on grid {real:.3f}, decoy mean {d:.3f}")
    print("rows", len(rows), "artists", len(artists), "payload %.0f kB" % (os.path.getsize(os.path.join(HERE, "payload.json")) / 1e3))


if __name__ == "__main__":
    main()
