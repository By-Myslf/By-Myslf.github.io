#!/usr/bin/env python3
"""Copy posts and photos from the current WordPress site (champagneclub.hu).

Runs on GitHub's computers (GitHub Actions), because it needs internet access.

What it does, for every post listed in data/sample.json:
  * downloads the post (title, text, categories, tags, dates) from the WordPress data feed
  * removes prices and buyer locations, which must never appear on the new site
  * downloads every product photo in its original size and saves web versions
    (WebP, 3 widths) under img/items/<post id>/
  * writes the cleaned post to data/raw/<post id>.json

Usage:  python tools/fetch_wp.py data/sample.json
"""
import html as htmllib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

BASE = "https://champagneclub.hu"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
IMG = ROOT / "img" / "items"
WIDTHS = (480, 960, 1600)
QUALITY = 82

# --- money and buyer-location cleaning -------------------------------------
CURRENCY = re.compile(
    r"(\d[\d\s.,]*\s?(?:\.-\s?)?(?:Ft|HUF|EUR|USD|GBP|€|£|\$)(?![a-zA-Z]))"
    r"|((?:€|£|NZ\$|US\$|\$)\s?\d)"
    r"|(\d[\d.]*\.-)",
)
TITLE_PRICE = re.compile(r"\s*[–\-]\s*\d[\d\s.]*\.?-?\s*(?:Ft|HUF)\b\.?", re.I)
SOLD_LINE = re.compile(r"^\s*(?:ELADVA|SOLD)\s*[–\-—]", re.I)
BLOCK = re.compile(r"<(p|li|h[1-6]|figcaption|td)\b[^>]*>.*?</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")


def text_of(html):
    return re.sub(r"\s+", " ", TAG.sub(" ", html)).strip()


def clean_html(html):
    removed = []

    def repl(m):
        t = text_of(m.group(0))
        if CURRENCY.search(t) or SOLD_LINE.match(t):
            removed.append(t[:120])
            return ""
        return m.group(0)

    return BLOCK.sub(repl, html), removed


def clean_title(t):
    return TITLE_PRICE.sub("", htmllib.unescape(t)).strip()


# --- network ------------------------------------------------------------------
def get(url, binary=False, tries=4):
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except Exception as e:  # noqa: BLE001
            err = e
        time.sleep(2 * (i + 1))
    print(f"  ! failed {url}: {err}")
    return None


# --- photos -------------------------------------------------------------------
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
ATTR = lambda name: re.compile(name + r'\s*=\s*"([^"]*)"', re.I)  # noqa: E731
SRC, SRCSET, ALT = ATTR("src"), ATTR("srcset"), ATTR("alt")
SIZE_SUFFIX = re.compile(r"-(\d+)x(\d+)(\.[a-z]+)$", re.I)


def candidates(tag):
    """Original-size URL first, then the largest listed size."""
    urls = []
    src = SRC.search(tag)
    srcset = SRCSET.search(tag)
    best = None
    if srcset:
        best_w = 0
        for part in srcset.group(1).split(","):
            bits = part.strip().split()
            if len(bits) == 2 and bits[1].endswith("w"):
                w = int(bits[1][:-1])
                if w > best_w:
                    best_w, best = w, bits[0]
    for u in (best, src.group(1) if src else None):
        if not u:
            continue
        u = u.replace("http://", "https://")
        orig = SIZE_SUFFIX.sub(r"\3", u).replace("-scaled.", ".")
        for c in (orig, u):
            if c not in urls:
                urls.append(c)
    return urls


def save_photo(data, post_id, n):
    im = Image.open(io.BytesIO(data))
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    ratio = w / h
    if min(w, h) < 300 or ratio > 2.0 or ratio < 0.4:
        return None  # banners, logos, tiny images
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    out_dir = IMG / str(post_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    sizes = []
    for target in WIDTHS:
        tw = min(target, w)
        if sizes and tw == sizes[-1]:
            continue
        th = round(h * tw / w)
        im.resize((tw, th), Image.LANCZOS).save(
            out_dir / f"{n:02d}-{tw}.webp", "WEBP", quality=QUALITY, method=5)
        sizes.append(tw)
    return {"n": n, "w": w, "h": h, "sizes": sizes}


def fetch_photos(post, html):
    photos, seen = [], set()
    tags = IMG_TAG.findall(html)
    feat = post.get("featured_media")
    if feat:
        m = get(f"{BASE}/wp-json/wp/v2/media/{feat}?_fields=source_url,alt_text")
        if m and m.get("source_url"):
            tags.insert(0, f'<img src="{m["source_url"]}" alt="{m.get("alt_text", "")}">')
    for tag in tags:
        urls = candidates(tag)
        if not urls or urls[0] in seen:
            continue
        seen.update(urls)
        for u in urls:
            data = get(u, binary=True)
            if not data:
                continue
            try:
                info = save_photo(data, post["id"], len(photos) + 1)
            except Exception as e:  # noqa: BLE001
                print(f"  ! could not read image {u}: {e}")
                break
            if info:
                alt = ALT.search(tag)
                info["alt"] = alt.group(1) if alt else ""
                info["source"] = u
                photos.append(info)
            break
    return photos


# --- main ---------------------------------------------------------------------
def main(sample_path):
    sample = json.loads(Path(sample_path).read_text())
    RAW.mkdir(parents=True, exist_ok=True)
    meta = {
        "categories": get(f"{BASE}/wp-json/wp/v2/categories?per_page=100&_fields=id,name,slug,count"),
        "tags": get(f"{BASE}/wp-json/wp/v2/tags?per_page=100&_fields=id,name,slug,count"),
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (RAW / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))

    jobs = [(i, "item") for i in sample["items"]] + \
           [(i, "article") for i in sample["articles"]] + \
           [(i, "page") for i in sample["pages"]]
    for pid, role in jobs:
        out = RAW / f"{pid}.json"
        if out.exists() and (IMG / str(pid)).exists():
            print(f"skip {pid} (already copied)")
            continue
        post = get(f"{BASE}/wp-json/wp/v2/posts/{pid}?_fields=id,date,modified,slug,link,"
                   "title,content,excerpt,categories,tags,featured_media")
        if not post:
            print(f"! post {pid} not found")
            continue
        html, removed = clean_html(post["content"]["rendered"])
        photos = fetch_photos(post, html)
        html = IMG_TAG.sub("", html)
        rec = {
            "id": post["id"], "role": role, "date": post["date"], "modified": post["modified"],
            "slug": post["slug"], "link": post["link"],
            "title": clean_title(post["title"]["rendered"]),
            "categories": post["categories"], "tags": post["tags"],
            "html": html, "photos": photos, "removed_for_privacy": len(removed),
        }
        out.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
        print(f"ok {pid} {role}: {len(photos)} photos, {len(removed)} blocks removed")
        time.sleep(0.3)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/sample.json")
