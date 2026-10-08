# src

The pipeline that builds `../index.html`. Run from the repository root, in order:

```bash
curl -L -o src/raw/MetObjects.csv https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv   # 318 MB
python src/fetch_aic.py      # every AIC painting       -> src/raw/aic_paintings.json  (~3.8 MB, ~1 min)
python -P src/extract.py     # canvas paintings, sizes  -> src/raw/paintings.json
python -P src/shape.py       # encode, check            -> src/payload.json
python src/inject.py         # splice into template     -> index.html (+ Pages wrapper, breadcrumb)
```

`fetch_gallica.py` is kept for the record: it is how the 1860 Menier catalogue was read page by
page through Gallica's ALTO endpoint, before that lead turned out to be a druggist's list (see
REBUILD.md). The page does not depend on it.

`src/raw/` and `payload.json` are not committed; the scripts regenerate them. `shape.py` prints
the two headline rates and their decoy levels, which should match REBUILD.md.

`inject.py` expects to sit inside the Quick Projects workspace (it calls the catalog's
`wrap_for_pages.py` and `add_catalog_link.py`). Outside it, splice `payload.json` into
`template.html` at `__PAYLOAD__` by hand.

Needs Python 3.11+, standard library only.
