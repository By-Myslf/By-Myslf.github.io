#!/usr/bin/env python3
"""Privacy cleaning applied when posts are copied from the old WordPress site.

Used by tools/import_zips.py. Removes what must never reach the new site or this
repository: prices, buyer locations ("ELADVA – …") and phone numbers.
"""
import html as htmllib
import re

# --- money and buyer-location cleaning -------------------------------------
CURRENCY = re.compile(
    r"(\d[\d\s.,]*\s?(?:\.-\s?)?(?:Ft|HUF|EUR|USD|GBP|€|£|\$)(?![a-zA-Z]))"
    r"|((?:€|£|NZ\$|US\$|\$)\s?\d)"
    r"|(\d[\d.]*\.-)"
    r"|(\d[\d\s.,]*\s?(?:eur[oó]\w*|forint\w*|doll[aá]r\w*|ft-?\w*\b)(?![a-z]))",
    re.I,
)
TITLE_PRICE = re.compile(r"\s*[–\-]\s*\d[\d\s.]*\.?-?\s*(?:Ft|HUF)\b\.?", re.I)
SOLD_LINE = re.compile(r"^\s*(?:ELADVA|SOLD)\s*[–\-—]", re.I)
BLOCK = re.compile(r"<(p|pre|li|h[1-6]|figcaption|td)\b[^>]*>.*?</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
SOLD_SEGMENT = re.compile(r"(?:ELADVA|SOLD)\s*(?:&#8211;|&#8212;|&ndash;|[–\-—])\s*[^<\n]{0,80}", re.I)
PHONE = re.compile(r"(?:\+36|06)[\s/-]?\d{1,2}[\s/-]?\d{3}[\s/-]?\d{3,4}[^<\n]{0,40}")
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)


def text_of(html):
    return re.sub(r"\s+", " ", htmllib.unescape(TAG.sub(" ", html))).strip()


def clean_html(html):
    """Returns (cleaned html, list of what was removed)."""
    removed = []
    for rx in (SOLD_SEGMENT, PHONE):
        for m in rx.findall(html):
            removed.append(m[:120])
        html = rx.sub("", html)

    def repl(m):
        t = text_of(m.group(0))
        if CURRENCY.search(t) or SOLD_LINE.match(t):
            removed.append(t[:120])
            return ""
        return m.group(0)

    return BLOCK.sub(repl, html), removed


def clean_title(t):
    return TITLE_PRICE.sub("", htmllib.unescape(t)).strip()
