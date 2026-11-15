# Champagne Club – website

Static website (plain HTML, CSS and JavaScript) for a private collection of champagne accessories.
Test version: https://by-myslf.github.io

## Folders

| Folder | What it holds |
|---|---|
| `data/raw/` | The posts as copied from the old site (one file per post) |
| `data/items/` | The cleaned item, article and page files the website is built from |
| `data/overrides.json` | Hand corrections: English titles, types, sets, materials, photos to leave out |
| `data/site.json`, `data/curation.json` | Types, houses, materials, text to remove; highlights and other hand-picked settings |
| `data/*-report.json` | Reports written by the tools, for checking (cleaning, sets, materials) |
| `templates/` | The page frame (header, footer) |
| `tools/` | The scripts described below |
| `img/` | Photos in web format (WebP) |
| `assets/` | Stylesheet, JavaScript, fonts, search data |
| everything else | The finished pages that visitors see |

## How pages are made

1. `python3 tools/import_zips.py cc-sample-1.zip …` unpacks the ZIP files saved by the browser copy of
   the old site into `data/raw/` and `img/items/`. Prices, buyer locations and phone numbers are removed
   here (`tools/cleaning.py`). Needs the Pillow package.
2. `python3 tools/normalize.py` turns `data/raw/` into `data/items/`: separates Hungarian and English,
   picks out the details, works out type, house, status, period and materials, and applies
   `data/overrides.json`.
3. `python3 tools/build.py` writes one HTML page per item per language, the listing pages, the search
   data, `sitemap.xml`, `robots.txt`, `llms.txt` and `.htaccess`. Add `--live` for the real domain.
   Needs Python 3.12 or newer.

Hungarian item pages keep their old champagneclub.hu addresses; English pages live under `/en/`.
`tools/fetch_fonts.py` downloaded the fonts once; it does not need to be run again.
