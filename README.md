# Champagne Club – website

Static website (plain HTML, CSS and JavaScript) for a private collection of champagne accessories.
Test version: https://by-myslf.github.io

## Folders

| Folder | What it holds |
|---|---|
| `data/` | Item details (one file per item) and the list of copied posts |
| `templates/` | The page templates (design) |
| `tools/` | Small scripts: copying from the old site, building the pages |
| `img/` | Photos in web format (WebP) |
| `assets/` | Stylesheet, JavaScript, fonts |
| everything else | The finished pages that visitors see |

## How pages are made

`python3 tools/build.py` reads the item data and the templates and writes one HTML page
per item per language. Hungarian item pages keep their old champagneclub.hu addresses;
English pages live under `/en/`.
