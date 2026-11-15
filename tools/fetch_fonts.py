#!/usr/bin/env python3
"""Download the site fonts once, so they are served from our own server
(no requests to Google when visitors open the site).

Writes assets/fonts/*.woff2 and assets/css/fonts.css.
Keeps the 'latin' and 'latin-ext' character sets (latin-ext has ő and ű).
"""
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
CSS_OUT = ROOT / "assets" / "css" / "fonts.css"
URL = ("https://fonts.googleapis.com/css2?"
       "family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400"
       "&family=Inter:wght@400;500;600&display=swap")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    if CSS_OUT.exists() and any(FONTS.glob("*.woff2")):
        print("fonts already present")
        return
    FONTS.mkdir(parents=True, exist_ok=True)
    CSS_OUT.parent.mkdir(parents=True, exist_ok=True)
    css = get(URL).decode()
    out = []
    for subset, block in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*{[^}]*})", css):
        if subset not in ("latin", "latin-ext"):
            continue
        fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
        style = re.search(r"font-style:\s*(\w+)", block).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
        src = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        name = f"{fam.lower().replace(' ', '-')}-{weight}-{style}-{subset}.woff2"
        (FONTS / name).write_bytes(get(src))
        out.append(f"/* {fam} {weight} {style} {subset} */\n" +
                   block.replace(src, f"../fonts/{name}"))
        print("saved", name)
    CSS_OUT.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
