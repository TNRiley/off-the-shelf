"""Fetch every painting record from the Art Institute of Chicago public API.

Writes src/raw/aic_paintings.json. The API caps search pagination at 10,000 results, so the
query is split by date_start ranges small enough to stay under it.
"""
import json, os, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "raw", "aic_paintings.json")
FIELDS = ("id,title,artist_title,artist_display,date_start,date_end,date_display,place_of_origin,"
          "medium_display,dimensions,dimensions_detail,subject_titles,classification_titles,"
          "term_titles,artwork_type_title,credit_line,main_reference_number")
URL = "https://api.artic.edu/api/v1/artworks/search"
# The API refuses (403) any page past offset 1,000, so every range must hold fewer than 1,000.
RANGES = [(-5000, 1399), (1400, 1499), (1500, 1599), (1600, 1649), (1650, 1699), (1700, 1749),
          (1750, 1799), (1800, 1829), (1830, 1849), (1850, 1864), (1865, 1879), (1880, 1889),
          (1890, 1899), (1900, 1909), (1910, 1919), (1920, 1929), (1930, 1944), (1945, 1959),
          (1960, 1974), (1975, 1989), (1990, 2100)]


def get(params):
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(URL + "?" + q, headers={"User-Agent": "off-the-shelf research (TNRiley)",
                                                         "AIC-User-Agent": "off-the-shelf (TNRiley)"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(3 + attempt * 3)
    raise SystemExit("gave up")


def main():
    rows = {}
    for lo, hi in RANGES:
        page = 1
        while True:
            params = {
                "query[bool][must][0][term][artwork_type_title.keyword]": "Painting",
                "query[bool][must][1][range][date_start][gte]": lo,
                "query[bool][must][2][range][date_start][lte]": hi,
                "fields": FIELDS, "limit": 100, "page": page,
            }
            d = get(params)
            for rec in d["data"]:
                rows[rec["id"]] = rec
            tp = d["pagination"]["total_pages"]
            if d["pagination"]["total"] > 1000:
                raise SystemExit(f"range {lo}-{hi} holds {d['pagination']['total']}; split it")
            print(lo, hi, "page", page, "/", tp, "total", d["pagination"]["total"], len(rows), file=sys.stderr)
            if page >= tp:
                break
            page += 1
            time.sleep(0.4)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"fetched": time.strftime("%Y-%m-%d"), "records": list(rows.values())}, f)
    print("wrote", len(rows), "records")


if __name__ == "__main__":
    main()
