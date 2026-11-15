#!/usr/bin/env python3
"""Unpack the ZIP files saved by the browser copy (cc-sample-*.zip).

Each ZIP holds raw WordPress posts (raw/<id>.json) and photos already converted to
WebP at up to 1600 px wide (img/<id>/<nn>.webp). This script:
  * removes prices, buyer locations and phone numbers from the text (tools/cleaning.py)
  * leaves out banners, logos and repeated photos
  * writes data/raw/<id>.json
  * saves each photo 480 and 960 px wide and in the size it arrived, under img/items/<id>/<nn>-<width>.webp

With --text-only the photos already imported are left alone and only the text is read again.

Usage: python3 tools/import_zips.py path/to/cc-sample-1.zip [more.zip …]
"""
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cleaning import IMG_TAG, clean_html, clean_title  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
IMG = ROOT / "img" / "items"
WIDTHS = (480, 960)
TEXT_ONLY = "--text-only" in sys.argv
# promotional banners and logos that are not photos of the item
NOT_PHOTO = re.compile(r"bubbles-fade|champagneclub\.hu-budapest|magangyujtemenye|champagne-luxury-accessories|"
                       r"logo|instagram|banner|facebook", re.I)


def dhash(im, size=8):
    g = im.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.tobytes())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | (px[r * (size + 1) + c] > px[r * (size + 1) + c + 1])
    return bits


def main(paths):
    RAW.mkdir(parents=True, exist_ok=True)
    count = 0
    for zp in paths:
        with zipfile.ZipFile(zp) as z:
            names = z.namelist()
            if "raw/_meta.json" in names:
                (RAW / "_meta.json").write_bytes(z.read("raw/_meta.json"))
            for name in names:
                if not (name.startswith("raw/") and name.endswith(".json")) or name.endswith("_meta.json"):
                    continue
                post = json.loads(z.read(name))
                pid = post["id"]
                html, removed = clean_html(post["content"]["rendered"])
                out_dir = IMG / str(pid)
                if TEXT_ONLY and (RAW / f"{pid}.json").exists():
                    rec = json.loads((RAW / f"{pid}.json").read_text())
                    rec.update(title=clean_title(post["title"]["rendered"]), html=IMG_TAG.sub("", html),
                               removed_for_privacy=len(removed))
                    (RAW / f"{pid}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
                    count += 1
                    continue
                shutil.rmtree(out_dir, ignore_errors=True)
                out_dir.mkdir(parents=True, exist_ok=True)
                photos, hashes, skipped = [], [], 0
                for ph in post["photos"]:
                    if NOT_PHOTO.search(ph["source"].rsplit("/", 1)[-1]):
                        skipped += 1
                        continue
                    data = z.read(f"img/{pid}/{ph['n']:02d}.webp")
                    im = Image.open(io.BytesIO(data))
                    h_ = dhash(im)
                    if any(bin(h_ ^ o).count("1") <= 5 for o in hashes):
                        skipped += 1
                        continue
                    hashes.append(h_)
                    n = len(photos) + 1
                    ph = dict(ph, n=n)
                    W, H = im.size
                    sizes = []
                    for w in WIDTHS:
                        if w < W:
                            im.resize((w, round(H * w / W)), Image.LANCZOS).save(
                                out_dir / f"{ph['n']:02d}-{w}.webp", "WEBP", quality=82, method=5)
                            sizes.append(w)
                    im.save(out_dir / f"{ph['n']:02d}-{W}.webp", "WEBP", quality=80, method=5)
                    sizes.append(W)
                    photos.append({"n": ph["n"], "w": W, "h": H, "sizes": sizes, "alt": ph.get("alt", ""),
                                   "original_size": [ph["w"], ph["h"]], "source": ph["source"]})
                rec = {
                    "id": pid, "role": post["role"], "date": post["date"], "modified": post["modified"],
                    "slug": post["slug"], "link": post["link"], "title": clean_title(post["title"]["rendered"]),
                    "categories": post["categories"], "tags": post["tags"],
                    "html": IMG_TAG.sub("", html), "photos": photos, "removed_for_privacy": len(removed),
                }
                (RAW / f"{pid}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))
                count += 1
                print(f"{pid} {post['role']}: {len(photos)} photos ({skipped} duplicates/banners skipped), {len(removed)} blocks removed")
    print(f"{count} posts imported")


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")])
