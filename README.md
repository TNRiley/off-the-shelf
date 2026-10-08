# 🖼️ Off the Shelf

**Half the French paintings of 1840 to 1929 in two American museums sit within a centimetre of a colourman's numbered stock canvas. Shrink or stretch that catalogue by four per cent and they stop fitting.**

→ **[Open it](https://tnriley.github.io/off-the-shelf/)**

Paris colourmen sold primed canvas ready-stretched in sixty numbered sizes, in three shapes called figure, paysage and marine. Every painting on canvas at the Met and the Art Institute of Chicago was measured against that grid, each museum kept apart: 49% and 47% of the French paintings fit, against 7% for decoy catalogues a few per cent too big or small, and a New York price list of about 1900 catches them only at the decoy level while catching a quarter of the American paintings. Bonnard, who cut his pictures from a roll pinned to the wall, scores none of sixteen. The shape names turn out not to name subjects: the near-square figure held most seascapes in both museums.

## Running it

One self-contained HTML file. No build step, no server, no network access at runtime — open `index.html` in a browser, or serve the directory with any static host.

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Rebuilding it from scratch

[REBUILD.md](REBUILD.md) is written for an LLM with a shell and nothing else: the data sources and their quirks, the processing decisions, the page's structure and interactions, and a table of expected values to check the result against.

## Source

The full build pipeline is in [`src/`](src/), with a README describing how to regenerate the page from scratch.

## Data

- **[The Metropolitan Museum of Art, Open Access CSV (MetObjects.csv): every painting on canvas, with its dimension label, artist nationality, date and subject tags, read 2026-10-08](https://github.com/metmuseum/openaccess)** — CC0
- **[Art Institute of Chicago public API: every artwork typed Painting, with its dimension label, artist, date and subject terms, read 2026-10-07](https://api.artic.edu/docs/)** — CC0
- **[English Wikipedia, French standard sizes for oil paintings: the table of the sixty figure, paysage and marine stock sizes in centimetres](https://en.wikipedia.org/wiki/French_standard_sizes_for_oil_paintings)** — CC BY-SA 4.0
- **[F. W. Devoe and Co., Priced catalogue of artists' materials (New York and Chicago, about 1900), the stretched-canvas size list on pages 16 and 17, read from the Internet Archive's OCR of a Columbia University Libraries scan](https://archive.org/details/pricedcatalogueo00fwde)** — Public domain

Every figure on the page is computed from the data shipped with it. Check the page's own methods panel for how each number is derived and where it should not be pushed.

## Built with

Python, Art Institute of Chicago API, archive.org full-text search, vanilla JS, SVG, base64 typed-array payload, in-page decoy controls.

## Licence

Code is MIT (see [LICENSE](LICENSE)). Data keeps the licence of its source, listed above.

---

Part of [Quick Projects](https://github.com/TNRiley/quick-projects) — one self-contained thing, built in one session. First published 2026-10-08.
