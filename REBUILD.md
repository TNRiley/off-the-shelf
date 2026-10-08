# Rebuilding Off the Shelf

## 1. What this is

A single self-contained page that tests whether French painters used the colourmen's numbered
stock canvases. From the early nineteenth century Paris colourmen sold primed canvas
ready-stretched in sixty fixed sizes: numbers 0 to 120, each in three shapes called *figure*,
*paysage* and *marine*. Nobody recorded who bought them, but the paintings carry their sizes,
and two American museums publish every painting's measurements.

**The finding.** Of the French paintings dated 1840 to 1929, 49% at the Met and 47% at the Art
Institute of Chicago have both sides within 1 cm of a stock size. Catalogues scaled 4 to 10% too
big or too small catch 7%. The hit rate, plotted against the catalogue's scale, is a single spike
at exactly x1.00 in both museums.

**The control (the cardinal).** Two of them, both computed in the page:

1. *Decoy catalogues.* Every stock size multiplied by a constant k from 0.80 to 1.20. If any
   k at least 0.04 from 1 catches half as many paintings as the real catalogue, the page
   withdraws its headline (it greys the finding and prints a warning). It has not: the worst
   decoy is 15% against 49% (Met, k = 1.125) and 15% against 47% (AIC, k = 1.198).
2. *The wrong catalogue.* A real price list from the other side of the Atlantic, F. W. Devoe and
   Co.'s stretched canvases in inches (New York, about 1900). French paintings fit it at the
   decoy level (11% and 8% against decoys of 12% and 11%); American paintings fit it at four to
   five times the decoy level. So the method finds a grid only where one was used.

**Two measures, never pooled.** The Met and the Art Institute catalogued their paintings
independently (the Met in inches to the eighth with centimetres in brackets, Chicago in
centimetres first). Every rate is computed per museum and shown side by side.

**The secondary result, half null.** Among French paintings on the grid, the near-square figure
shape is the commonest shape for every subject in both museums, seascapes included (23 of 28 at
the Met, 7 of 12 at AIC). Whether seascapes lean toward the marine shape the two museums disagree
(Met 0 of 28, AIC 3 of 12 against 9% overall), and forty seascapes cannot settle it. The page
says so.

## 2. Data

| source | URL | notes |
|---|---|---|
| Met Open Access CSV | `https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv` | 318 MB via Git LFS (the raw.githubusercontent URL returns an LFS pointer). CC0. UTF-8 with BOM. |
| AIC API | `https://api.artic.edu/api/v1/artworks/search` | CC0 except `description` (CC BY), which is not used. |
| French sizes | `https://en.wikipedia.org/wiki/French_standard_sizes_for_oil_paintings` | CC BY-SA. Copied into `shape.py`. Written width x height (figure 30 = 92 x 73). |
| Devoe list | `https://archive.org/download/pricedcatalogueo00fwde/pricedcatalogueo00fwde_djvu.txt` | Public domain. Lines ~2199-2600 of the OCR text; 45 sizes. `6x8` is OCR'd as `Gx 8`. Copied into `shape.py`. |

Traps:

- **Met: the American Wing has no Classification.** All 18,532 of its objects have an empty
  `Classification`; filtering on `== "Paintings"` silently drops its 1,006 paintings on canvas.
  Wrong answer: 8 American paintings 1840-99. Right answer: 474. Fall back to
  `Object Name` starting "Painting" when Classification is blank.
- **AIC: `dimensions_detail` truncates to whole centimetres** (La Grande Jatte 207.5 x 308.1 is
  stored 207 x 308). Because the stock sizes are whole centimetres, truncation *flatters* the
  result. Wrong answer from the structured field: AIC French 56.0%. Right answer from the text
  label: 46.5%. Parse `dimensions` (the text) instead.
- **AIC search refuses offsets past 1,000** with HTTP 403, not an empty page. Split the query
  into date ranges each holding fewer than 1,000 paintings; `fetch_aic.py` exits if one does not.
- **Dimension strings come in at least five shapes**: `a x b in. (c x d cm)`, `c x d cm (a x b in.)`,
  `H. 36-1/4, W. 42 inches\n(92.1 x 106.7 cm.)`, `H. ... (cm)\nW. ... (cm)` on separate lines,
  feet-and-inches, and blocks labelled `Framed:`. Take the first centimetre pair not in a frame
  block. The separator is `x` or `×`.
- `python -I` ignores `PYTHONIOENCODING`; on Windows the scripts reconfigure stdout themselves.

## 3. Processing decisions

- Canvas only: medium mentions "canvas". Panels and paper are excluded (panels also came in stock
  sizes, so they are not a clean control).
- Orientation ignored: compare sorted (long, short) against each stock (long, short).
- "On the grid": max(|L - L0|, |S - S0|) <= 1.0 cm for some stock size. The grid's closest pair of
  rectangles (paysage 5, 35 x 24, and figure 4, 33 x 24) is 2 cm apart, so tolerance boxes never
  overlap.
- Rows whose dimension label mentions an added strip, enlargement, addition, original painted
  surface, or sight size (25 rows) are drawn but excluded from every rate.
- Headline window 1840-1929 by object start date. The timeline shows the rest.
- Nationality: the first listed artist's, before any comma (`American, born France` is
  American). English, Scottish, Welsh, Irish -> British.
- Subject from the museums' own tags: any sea/boat/ship/harbour/beach tag -> seascape; else a
  portrait tag -> portrait; else landscape/river/mountain/forest -> landscape.
- Decoy level = mean over k in {0.90, 0.92, 0.94, 0.96, 1.04, 1.06, 1.08, 1.10}.

## 4. The page

Colourman's price list on primed linen: Bodoni Moda headings, Libre Franklin body, IBM Plex
Mono for numbers. Terracotta = figure, sap green = paysage, marine blue = marine; madder = Met,
ochre = Art Institute; grey = decoy. Light and dark themes.

Sections: hero with four number tiles and three nested to-scale stacks (figure, paysage,
marine, Nos 0-40); scatter of long vs short side with the 60 tolerance squares, chips for four
groups x two museums, hover for title and nearest stock size, click opens the museum page; the
k-sweep (the cardinal) with the withdrawal line; the Paris-vs-Devoe matrix; on-grid share by
twenty-year span; shape-by-subject stacked bars per museum; per-museum artist tables (n >= 6,
1840-1929); methods panel with sources and licences, measurement, instrument findings, the
failed half, and what the page does not say.

## 5. Expected values

| check | value |
|---|---|
| rows in payload | 5,975 (Met 45 and AIC 8 dropped for no parsable size) |
| altered supports excluded from rates | 25 |
| Met French 1840-1929 | n = 525, 49.0% on grid, decoy 7.5% |
| AIC French 1840-1929 | n = 318, 46.5% on grid, decoy 7.4% |
| worst decoy at least 4% off | Met 15% (k = 1.125), AIC 15% (k = 1.198) |
| American 1840-1929 on Paris grid | Met 17% (n = 831), AIC 15% (n = 317), decoys 7% |
| American 1840-1929 on Devoe grid | Met 26%, AIC 20%, decoys 5% and 6% |
| French 1840-1929 on Devoe grid | Met 11% (decoy 12%), AIC 8% (decoy 11%) |
| tolerance sweep, Met | 0.25 cm 9.5% / 0.5 cm 27.7% / 1 cm 48.8% / 2 cm 64.3% (decoys 0.4 / 1.9 / 7.6 / 25.6%) |
| median overshoot of measured over stock size | Met 1 mm (361), AIC 2 mm (219) |
| AIC rate from truncated `dimensions_detail` | 56.0% (wrong; the right one is 46.5%) |
| Pierre Bonnard, Met, 1840-1929 | 0 of 16 on the grid |
| Monet | Met 22 of 40, AIC 15 of 33 |
| Cezanne / Matisse / Pissarro, Met | 19/24, 18/21, 16/20 |
| Cassatt / Kensett / Homer, Met | 7/11, 0/22, 1/17 |
| seascapes on figure / marine | Met 23 and 0 of 28; AIC 7 and 3 of 12 |
| marine share of everything on grid | Met 4%, AIC 9% |
| Spanish (all dates), Met | 35% on grid (Paris-based moderns) |

## 6. The failed half

The French sizes were meant to come from a period colourman's catalogue, not a modern chart. A
Gallica SRU full-text search (`dc.title all "catalogue commercial" and gallica all "toiles" and
... "figure" ... "paysage" ... "marine"`) returned the 1860 Menier *Catalogue commercial ou prix
courant general* (ark:/12148/bpt6k946633g). Gallica's `.texteBrut` view now redirects to an
ALTCHA proof-of-work page; `RequestDigitalElement?O=<ark>&E=ALTO&Deb=<page>` served page 1, then
the host reset every connection from this address for the rest of the session. When it answered
again, `services/ContentSearch?ark=bpt6k946633g&query=paysage` showed the hit was false: Menier
was a wholesale druggist, its *paysages* and *marine* are painted window blinds (page 480), and
it lists no artists' canvas. The real candidates, Gustave Sennelier's catalogues of 1896, 1902
and 1912 (Bibliotheque Forney, `bibliotheques-specialisees.paris.fr/ark:/73873/pf0002006851`,
`pf0002006833`, `pf0002006843`), are served by a JavaScript viewer whose image API was not found.
That is the next thing to try. Also searched without result: archive.org full text (only modern
books reproduce the table), HathiTrust (Cloudflare check), Bouvier 1827 and Arsenne 1833.

What stands in: the paintings' own measurements peak 1-2 mm over the modern chart in both
museums, and the sweep shows a 3% error in the chart would lose most hits. That is indirect.

## 7. What the page must say about itself

A dot on the grid means the support is a stock size, not that the painter bought it stretched
(stretchers were sold separately). The museums' holdings are not a sample of French painting.
Nationality stands in for where the canvas was bought. Relining and trimming can only push
paintings off the grid. The seascape test rests on forty paintings.
