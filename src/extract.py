"""Extract every painting on canvas from the Met and AIC dumps into one flat table.

    python -P extract.py            ->  src/raw/paintings.json

Each row: museum, id, title, artist, nationality, year, long and short side in cm (the support,
never the frame), subject class, and any note in the dimension string that says the support is
not as it left the colourman (added strips, enlargements, sight sizes).
"""
import csv, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

NUM = r"(\d+(?:\.\d+)?)"
X = r"\s*[x×]\s*"
CM_PAIR = re.compile(NUM + X + NUM + r"(?:" + X + NUM + r")?\s*cm", re.I)
H_LINE = re.compile(r"\bH\.\s[^()\n]*\(" + NUM + r"\s*cm\)")
W_LINE = re.compile(r"\bW\.\s[^()\n]*\(" + NUM + r"\s*cm\)")
FRAME_LABEL = re.compile(r"^\s*(framed|frame|with frame)\b", re.I)
OTHER_LABEL = re.compile(r"^\s*(unframed|overall|image|painting|canvas|stretcher|sight|not framed)\b", re.I)
ALTERED = re.compile(r"(added|enlarg|addition|strip|extension|original painted surface|cut down|reduced|sight)", re.I)

SEA = {"seascapes", "boats", "ships", "harbors", "beaches", "waves", "sailboats", "coasts", "coastlines",
       "ocean", "sea", "marine", "fishing boats", "sailing", "lighthouses", "shipwrecks", "seashores"}
PORTRAIT = {"portraits", "portrait", "self-portraits", "self-portrait", "portraits: male subject",
            "portraits: female subject"}
LAND = {"landscapes", "landscape", "rivers", "mountains", "forests", "fields", "valleys", "lakes"}


def subject(tags):
    t = {x.strip().lower() for x in tags if x and x.strip()}
    if t & SEA:
        return "sea"
    if t & PORTRAIT:
        return "portrait"
    if t & LAND:
        return "landscape"
    return "other" if t else "untagged"


def support_size(text):
    """First height and width in cm that are not labelled as the frame. Returns (a, b, note)."""
    if not text:
        return None
    text = text.replace("\r", "")
    segs = re.split(r"[;\n]", text)
    framed = False
    hw = {}
    for seg in segs:
        if FRAME_LABEL.search(seg):
            framed = True
        elif OTHER_LABEL.search(seg):
            framed = False
        if framed or re.search(r"including frame|with frame|framed", seg, re.I):
            continue
        m = CM_PAIR.search(seg)
        if m:
            return float(m.group(1)), float(m.group(2)), seg.strip()
        h = H_LINE.search(seg)
        if h:
            hw["h"] = float(h.group(1))
        w = W_LINE.search(seg)
        if w:
            hw["w"] = float(w.group(1))
        if "h" in hw and "w" in hw:
            return hw["h"], hw["w"], seg.strip()
    return None


def first(s, sep="|"):
    return (s or "").split(sep)[0].strip()


def met_rows():
    with open(os.path.join(RAW, "MetObjects.csv"), encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            # The American Wing leaves Classification blank on every object it holds, so a filter on
            # "Paintings" alone silently loses its 1,006 paintings on canvas. Fall back to Object Name.
            if row["Classification"] != "Paintings" and not (
                    row["Classification"] == "" and row["Object Name"].strip().lower().startswith("painting")):
                continue
            med = row["Medium"].lower()
            if "canvas" not in med:
                continue
            yield {
                "museum": "met", "id": row["Object ID"], "title": row["Title"],
                "artist": first(row["Artist Display Name"]), "nat": first(row["Artist Nationality"]),
                "year": int(row["Object Begin Date"]) if row["Object Begin Date"].lstrip("-").isdigit() else None,
                "medium": row["Medium"], "dims": row["Dimensions"],
                "tags": [t for t in row["Tags"].split("|") if t],
            }


def aic_nat(display):
    # artist_display is "Name\nFrench, 1840-1926" or "Name (French, 1840-1926)"
    if not display:
        return ""
    lines = display.split("\n")
    if len(lines) > 1:
        return lines[1].split(",")[0].strip()
    m = re.search(r"\(([^,()]+),", display)
    return m.group(1).strip() if m else ""


def aic_rows():
    recs = json.load(open(os.path.join(RAW, "aic_paintings.json"), encoding="utf-8"))["records"]
    for r in recs:
        med = (r.get("medium_display") or "").lower()
        if "canvas" not in med:
            continue
        yield {
            "museum": "aic", "id": str(r["id"]), "title": r.get("title") or "",
            "artist": r.get("artist_title") or "", "nat": aic_nat(r.get("artist_display")),
            "year": r.get("date_start"), "medium": r.get("medium_display"), "dims": r.get("dimensions") or "",
            "tags": r.get("subject_titles") or [],
        }


def main():
    out, dropped = [], {"met": 0, "aic": 0}
    for row in list(met_rows()) + list(aic_rows()):
        s = support_size(row["dims"])
        if not s or min(s[0], s[1]) <= 0:
            dropped[row["museum"]] += 1
            continue
        a, b, seg = s
        alt = ALTERED.search(row["dims"])
        out.append({
            "museum": row["museum"], "id": row["id"], "title": row["title"], "artist": row["artist"],
            "nat": row["nat"], "year": row["year"], "medium": row["medium"],
            "L": max(a, b), "S": min(a, b), "portrait": a > b,
            "subject": subject(row["tags"]), "altered": alt.group(1).lower() if alt else "",
            "dims": row["dims"],
        })
    json.dump(out, open(os.path.join(RAW, "paintings.json"), "w", encoding="utf-8", newline="\n"))
    print("kept", len(out), "dropped (no support size)", dropped)


if __name__ == "__main__":
    main()
