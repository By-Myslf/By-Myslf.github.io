#!/usr/bin/env python3
"""Turn the copied WordPress posts (data/raw) into clean item files (data/items).

For each post it:
  * separates the Hungarian and English text
  * picks out the details lines (maker, material, dimensions, condition, …)
  * works out the type, champagne house, status, period and materials
  * removes shop phrases (delivery offers, slogans) that do not belong on a collectors' site
Manual corrections and translations in data/overrides/<id>.json are applied last
("drop_photos": [numbers] there leaves out photos that show other items).

Usage: python3 tools/normalize.py
"""
import html as htmllib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "items"
OVR = ROOT / "data" / "overrides"
SITE = json.loads((ROOT / "data" / "site.json").read_text())
CUR = json.loads((ROOT / "data" / "curation.json").read_text())
OVERRIDES = json.loads((ROOT / "data" / "overrides.json").read_text()) if (ROOT / "data" / "overrides.json").exists() else {}

# ---------------------------------------------------------------- language
HU_CHARS = set("őűáéíóöüúŐŰÁÉÍÓÖÜÚ")
HU_WORDS = set("a az és egy hogy van volt nem is meg de ezt ami amely mint vagy már csak még ez azt egyik több darab "
               "pezsgő pezsgőhűtő készült eredeti anyaga méret állapot jégveder palack palackos számára ahol".split())
EN_WORDS = set("the and of with for is was this that are from in on by its it as an to which has have were be "
               "champagne bucket cooler glass glasses original made condition bottle bottles designed".split())


def lang_of(text):
    words = re.findall(r"[a-zA-ZőűáéíóöüúŐŰÁÉÍÓÖÜÚ]+", text.lower())
    if not words:
        return None
    hu = sum(1 for w in words if w in HU_WORDS or any(c in HU_CHARS for c in w))
    en = sum(1 for w in words if w in EN_WORDS)
    if hu == en:
        return None
    return "hu" if hu > en else "en"


# ---------------------------------------------------------------- html blocks
BLOCK = re.compile(r"<(h[1-6]|p|pre|ul|ol|blockquote|table)\b[^>]*>(.*?)</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
ALLOWED = re.compile(r"</?(?:strong|em|b|i|br|a|li|ul|ol|sup|sub)\b[^>]*>", re.I)


def text_of(s):
    return re.sub(r"\s+", " ", htmllib.unescape(TAG.sub(" ", s))).strip()


def tidy_inline(s):
    """Keep only simple inline formatting; drop classes, styles and old links."""
    s = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", s, flags=re.S | re.I)
    s = re.sub(r"<(?!/?(?:strong|em|b|i|br|li|sup|sub)\b)[^>]+>", "", s)
    s = re.sub(r"<(strong|em|b|i|li|sup|sub)\b[^>]*>", r"<\1>", s)
    s = s.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


BOILER = [r"champagneclub", r"champagne club budapest", r"ingyenes a kiszállítás", r"kiszállítás", r"free delivery",
          r"nézze meg a kínálatunkban", r"take a look at our offer", r"buborékok elillannak",
          r"bubbles fade", r"bubbles disappear", r"vegye fel a kapcsolatot", r"contact us", r"megpróbálunk beszerezni",
          r"we will try to", r"^eladó!?$", r"^for sale!?$", r"^elad[óo]\b.*\bdarab", r"webshop", r"vásárolja meg",
          r"személyes átvétel", r"personal pickup", r"postán", r"foxpost", r"\bgls\b", r"utánvét", r"^(eladva|sold)\b", r"browse more of our", r"check out more of our",
          r"nézze meg (a )?további", r"további .{0,40}(kiegészítő|termék|kínálat)", r"\bVIP\b.{0,60}kóstoló", r"tasting.{0,40}budapest",
          r"^https?://", r"^www\.", r"^\[\d+\]", r"\+36", r"sursumvivere",
          r"időpont[ -]?egyeztetés", r"champagneclub\.hu kínálat", r"nézze meg a többi", r"check out our other", r"érdeklődés és",
          r"egyedi méretű és kialakítású", r"vasbútor", r"sisaktartó", r"bárpult", r"bar counters", r"iron furniture", r"helmet holder"]
BOILER_RE = re.compile("|".join(BOILER), re.I)

KV = re.compile(r"^([A-ZÁÉÍÓÖŐÚÜŰa-záéíóöőúüű'’ /().-]{2,45}?)\s*:\s+(.{1,200})$")
SKIP_KEYS = {"márka", "brand", "pezsgőház", "champagne house", "house"}
YEAR_KEYS = {"készítés ideje", "gyártás ideje", "gyártási év", "évjárat", "kor", "korszak", "időszak", "datálás", "kiadás éve",
             "year", "period", "date", "era", "age", "circa", "production year", "year of production", "dating", "release year", "edition"}
MAT_KEYS = {"anyag", "anyaga", "material", "materials", "anyagok"}
COND_KEYS = {"állapot", "condition"}


def blocks_of(html):
    out = []
    for m in BLOCK.finditer(html):
        tag, inner = m.group(1).lower(), m.group(2)
        if tag in ("ul", "ol"):
            for li in re.findall(r"<li\b[^>]*>(.*?)</li>", inner, re.S | re.I):
                t = text_of(li)
                if t:
                    out.append({"tag": "li", "list": tag, "html": tidy_inline(li), "text": t})
            continue
        pieces = re.split(r"<br\s*/?>", inner, flags=re.I) if tag in ("p", "pre") else [inner]
        for piece in pieces:
            t = text_of(piece)
            if t:
                out.append({"tag": "p" if tag == "pre" else tag, "html": tidy_inline(piece), "text": t})
    return out


EN_KEYS = set("""brand collection manufacturer maker producer material materials origin country of origin made in
production production method year period date era age circa height width length depth diameter rim diameter
base diameter maximum bowl diameter capacity volume weight dimensions size condition colour color quantity
number of pieces pieces packaging design designer markings marking maker's mark edition limited edition style
shape finish type item suitable for bottle capacity handles lid insert""".replace("\n", " ").split(" "))
HU_KEYS_HINT = re.compile(r"[őűáéíóöüú]", re.I)


def kv_lang(text):
    m = KV.match(text)
    if not m:
        return None
    key = m.group(1).strip().lower()
    if HU_KEYS_HINT.search(key):
        return "hu"
    words = key.replace("'", " ").split()
    if words and all(w in EN_KEYS or w in ("of", "and", "the", "in") for w in words):
        return "en"
    return None


def split_languages(blocks):
    cur = "hu"
    for b in blocks:
        t = b["text"]
        lg = kv_lang(t)
        if lg is None and (len(t.split()) >= 6 or b["tag"].startswith("h")):
            lg = lang_of(t)
        if lg:
            cur = lg
        b["lang"] = lg or cur
    # a short block right before a switch belongs to the following language (titles, headings)
    for i in range(len(blocks) - 1):
        b, n = blocks[i], blocks[i + 1]
        if b["lang"] != n["lang"] and len(b["text"]) < 140 and lang_of(b["text"]) is None and kv_lang(b["text"]) is None:
            b["lang"] = n["lang"]
    return blocks


def split_at_english(blocks):
    """Articles: Hungarian first, then the English version starting at a heading."""
    langs = [lang_of(b["text"]) if len(b["text"].split()) >= 6 else None for b in blocks]
    cut = len(blocks)
    for i, b in enumerate(blocks):
        if not b["tag"].startswith("h"):
            continue
        after = [lg for lg in langs[i + 1:i + 12] if lg][:6]
        before = [lg for lg in langs[:i] if lg]
        if len(after) >= 4 and after.count("en") >= len(after) - 1 and before and before.count("hu") > len(before) / 2:
            cut = i
            break
    for i, b in enumerate(blocks):
        b["lang"] = "hu" if i < cut else "en"
    return blocks


def assemble(blocks, item=True):
    """Blocks of one language -> (intro, body html, details, title guess)."""
    details, body, intro, title_guess = [], [], None, None
    for b in blocks:
        t = b["text"]
        if BOILER_RE.search(t):
            continue
        kv = KV.match(t) if (item and len(t) < 220) else None
        if kv and b["tag"] in ("li", "p") and not t.endswith("?"):
            k, v = kv.group(1).strip(), kv.group(2).strip().rstrip(".")
            if k.lower() not in SKIP_KEYS and len(k.split()) <= 5:
                details.append([k[0].upper() + k[1:], v])
            continue
        if item and title_guess is None and b["tag"].startswith("h") and not body and intro is None:
            title_guess = t
            continue
        if item and len(t) < 60 and re.search(r"^(méret|műszaki adat|jellemző|dimensions|specification|details|features|technical)", t, re.I):
            continue
        if b["tag"].startswith("h"):
            # headings that only announce the details list are dropped
            if re.search(r"méret|műszaki adat|jellemző|dimensions|specification|details|features", t, re.I) and len(t) < 60:
                continue
            body.append(f"<h3>{b['html']}</h3>")
        elif b["tag"] == "li":
            body.append(f"<li>{b['html']}</li>")
        elif b["tag"] == "blockquote":
            body.append(f"<blockquote>{b['html']}</blockquote>")
        else:
            if intro is None and len(t) > 80 and t.rstrip().endswith((".", "!", "”", '"')) \
                    and not re.search(r"\d+([.,]\d+)?\s?(cm|mm)\b.*\d+([.,]\d+)?\s?(cm|mm)\b", t):
                intro = t.lstrip("—–- ").strip()
                if item:
                    continue
            body.append(f"<p>{b['html']}</p>")
    if intro is None and item:
        for i, part in enumerate(body):
            txt = text_of(part)
            if part.startswith("<p>") and len(txt) > 30 and not re.search(r"\d+([.,]\d+)?\s?(cm|mm)\b", txt):
                intro = txt.lstrip("—–- ").strip()
                body.pop(i)
                break
    # wrap loose <li> runs in <ul>
    html, inlist = [], False
    for part in body:
        if part.startswith("<li>") and not inlist:
            html.append("<ul>")
            inlist = True
        if not part.startswith("<li>") and inlist:
            html.append("</ul>")
            inlist = False
        html.append(part)
    if inlist:
        html.append("</ul>")
    return intro, "\n".join(html), details, title_guess


# ---------------------------------------------------------------- facts
TYPE_BY_WP = {t["wp"]: t["key"] for t in SITE["types"] if t["wp"]}
TYPE_PRIORITY = ["display-stands", "champagne-sabres", "cigar-accessories", "dummy-bottles", "illuminated-bar-accessories",
                 "vintage-antique-coolers", "multi-bottle-coolers", "single-bottle-coolers", "champagne-glasses",
                 "special-items", "gift-items"]


def guess_type(title, cats):
    found = [TYPE_BY_WP[c] for c in cats if c in TYPE_BY_WP]
    if found:
        return sorted(found, key=TYPE_PRIORITY.index)[0]
    t = title.lower()
    if re.search(r"szablya|sabre|sabrage|kard", t):
        return "champagne-sabres"
    if re.search(r"hamutartó|szivar|cigar|humidor", t):
        return "cigar-accessories"
    if re.search(r"dummy|demo|díszpalack|kirakati", t):
        return "dummy-bottles"
    if re.search(r"világító|\bled\b|illuminated", t):
        return "illuminated-bar-accessories"
    is_cooler = re.search(r"hűtő|huto|veder|vödör|vodor|jégtál|medence|kád|cooler|bucket", t)
    if is_cooler and re.search(r"antik|antique|19[0-4]\d|18\d\d|art deco", t):
        return "vintage-antique-coolers"
    if is_cooler and (re.search(r"([2-9]|1\d)\s*palackos|több palack|jégmedence|kád|xl|magnum", t)):
        return "multi-bottle-coolers"
    if re.search(r"pohár|pohar|poharak|kehely|glass|flute|coupe", t) and not is_cooler:
        return "champagne-glasses"
    if is_cooler:
        return "single-bottle-coolers"
    return "gift-items"


HOUSE_BY_WP = {}
for h in SITE["houses"]:
    for w in h["wp"]:
        HOUSE_BY_WP[w] = h["key"]


def guess_house(title, tags):
    t = title.lower()
    for h in SITE["houses"]:
        if any(m in t for m in h["match"]):
            return h["key"]
    for tg in tags:
        k = HOUSE_BY_WP.get(tg)
        if k and k != "other":
            return k
    return "other" if 65 in tags else None


YEAR_RE = re.compile(r"(?<!\d)(1[89]\d\d|20[0-2]\d)(?!\d)")
DECADE_HU = re.compile(r"(1[89]\d0|20[0-2]0)\s*[-–]?\s*(?:as|es|ás|és)\b")
DECADE_EN = re.compile(r"(1[89]\d0|20[0-2]0)['’]?s\b")
HU_SUFFIX = {"00": "es", "10": "es", "20": "as", "30": "as", "40": "es", "50": "es", "60": "as", "70": "es", "80": "as", "90": "es"}


def era_from(texts):
    for t in texts:
        if not t:
            continue
        m = DECADE_EN.search(t) or DECADE_HU.search(t)
        if m:
            y = int(m.group(1))
            return y, {"en": f"{y}s", "hu": f"{y}-{HU_SUFFIX[str(y)[2:]]} évek"}
        m = YEAR_RE.search(t)
        if m:
            y = int(m.group(1))
            return y, {"en": str(y), "hu": str(y)}
    return None, {}


def period_of(y):
    if not y:
        return None
    for p in SITE["periods"]:
        if y <= p["to"]:
            return p["key"]
    return None


def materials_of(texts):
    blob = " " + " ".join(t.lower() for t in texts if t) + " "
    blob = re.sub(r"ezüst\s?színű|ezüstös|silver[- ]colou?red|silver[- ]tone|silver colou?r|arany\s?színű|gold[- ]colou?red", " ", blob)
    found = []
    for m in SITE["materials"]:
        if any(k in blob for k in m["match"]):
            found.append(m["key"])
    if "steel" in found and "metal" in found and not re.search(r"brass|réz|alumin|bronz|zinc|cink", blob):
        found.remove("metal")
    if "silver" in found and "metal" in found and not re.search(r"brass|réz|alumin|bronz|zinc|cink", blob):
        found.remove("metal")
    return found


def clean_title(t):
    t = htmllib.unescape(t)
    t = re.sub(r"^\s*SOLD\s*/\s*ELADVA\s*[–\-—]\s*", "", t, flags=re.I)
    t = re.sub(r"\s*[–\-—]\s*(ELADÓ|FOGLALT|MEGRENDELHETŐ|SOLD|ELADVA)\s*$", "", t, flags=re.I)
    t = re.sub(r"\s*[–\-—]\s*(ELADÓ|FOGLALT|MEGRENDELHETŐ)\s*$", "", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip(" –-")


def slugify(s, n=80):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > n:
        s = s[:n].rsplit("-", 1)[0]
    while True:
        cut = re.sub(r"-(in|of|the|and|with|for|a|an|to)$", "", s)
        if cut == s:
            return s
        s = cut


# ---------------------------------------------------------------- main
PARTNER_PHOTO = re.compile(r"sursumvivere|fembutor|vasbutor|femszerkezet|lakasbutor|lakberendez", re.I)


def keep_photos(raw):
    """Drop the partner workshop's advert photos, except on display stands it makes."""
    if raw["id"] in CUR.get("display_stands", []) or raw["role"] == "article":
        photos = raw["photos"]
    else:
        photos = [p for p in raw["photos"] if not PARTNER_PHOTO.search(p.get("source", ""))]
    return photos

def deep_merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            deep_merge(a[k], v)
        else:
            a[k] = v
    return a


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    report, used_slugs = [], set()
    for p in sorted(RAW.glob("[0-9]*.json"), key=lambda x: int(x.stem)):
        raw = json.loads(p.read_text())
        role = raw["role"]
        title_hu = clean_title(raw["title"])
        status = "available"
        if re.search(r"SOLD|ELADVA", raw["title"], re.I):
            status = "sold"
        elif re.search(r"FOGLALT", raw["title"], re.I):
            status = "reserved"
        if raw["id"] in CUR.get("made_to_order", []) or re.search(r"MEGRENDELHETŐ", raw["title"], re.I):
            status = "made_to_order"

        is_item = role == "item"
        if is_item:
            blocks = split_languages(blocks_of(raw["html"]))
        else:
            blocks = split_at_english(blocks_of(raw["html"]))
        parts = {}
        for lg in ("hu", "en"):
            parts[lg] = assemble([b for b in blocks if b["lang"] == lg], item=is_item)
        intro_hu, body_hu, det_hu, _ = parts["hu"]
        intro_en, body_en, det_en, title_en = parts["en"]
        if title_en and (len(title_en) > 160 or lang_of(title_en) == "hu"):
            title_en = None

        e = {
            "id": raw["id"], "kind": {"item": "item", "article": "article", "page": "page"}[role],
            "ref": f"CC-{raw['id']}", "date": raw["date"][:10], "modified": raw["modified"][:10],
            "slug_hu": raw["slug"], "slug_en": None,
            "title": {"hu": title_hu, "en": title_en},
            "intro": {"hu": intro_hu, "en": intro_en},
            "body": {"hu": body_hu, "en": body_en},
            "details": {"hu": det_hu, "en": det_en},
            "photos": keep_photos(raw),
            "highlight": raw["id"] in CUR.get("highlights", []),
        }
        if role != "item":
            for lg in ("hu", "en"):
                b = e["body"][lg] or ""
                m = re.match(r"\s*<h3>(.*?)</h3>\s*", b, re.S)
                if m:  # the article's own title repeated at the top
                    e["body"][lg] = b[m.end():]
        if role == "page":
            e["page"] = CUR.get("pages", {}).get(str(raw["id"]), "about")
        if role == "item":
            e["status"] = status
            e["type"] = "display-stands" if raw["id"] in CUR.get("display_stands", []) else guess_type(title_hu, raw["categories"])
            e["house"] = guess_house(title_hu + " " + (title_en or ""), raw["tags"])
            year_texts = [v for k, v in det_hu + det_en if k.lower() in YEAR_KEYS] + [title_hu, title_en or ""]
            y, era = era_from(year_texts)
            e["year"], e["era"], e["period"] = y, era, period_of(y)
            mat_texts = [v for k, v in det_hu + det_en if k.lower() in MAT_KEYS]
            e["materials"] = materials_of(mat_texts)
        if role != "item" and (body_en or intro_en) and not title_en:
            title_en = None

        f = OVR / f"{raw['id']}.json"
        if f.exists():
            deep_merge(e, json.loads(f.read_text()))
        if str(raw["id"]) in OVERRIDES:
            deep_merge(e, json.loads(json.dumps(OVERRIDES[str(raw["id"])])))
        # photos that show other items (listed by number in the overrides as "drop_photos")
        drop = set(e.pop("drop_photos", []))
        if drop:
            e["photos"] = [ph for ph in e["photos"] if ph["n"] not in drop]
        # rebuild slug and keywords after overrides
        if e["title"].get("en"):
            base = e.get("slug_en") or slugify(e["title"]["en"])
            slug, i = base, 2
            while slug in used_slugs:
                slug, i = f"{base}-{i}", i + 1
            e["slug_en"] = slug
            used_slugs.add(slug)
        # old addresses that contain a price get a clean address; the old one redirects to it
        priced = re.sub(r"-\d{1,3}(?:-\d{3})+-?ft(?=-|$)|-\d+-?ft(?=-|$)|-\d{1,3}(?:-\d{3})+-?huf(?=-|$)", "", e["slug_hu"])
        if priced != e["slug_hu"]:
            e["old_slugs"] = [e["slug_hu"]]
            e["slug_hu"] = priced.strip("-")
        e["keywords"] = {"en": e["title"].get("hu") or "", "hu": e["title"].get("en") or ""}
        if e["kind"] == "item" and e["intro"].get("en") is None and e["body"].get("en"):
            pass
        (OUT / f"{raw['id']}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1))
        missing = [k for k in ("title", "intro") if not e[k].get("en")]
        has_ovr = f.exists() or str(raw["id"]) in OVERRIDES
        report.append({
            "id": raw["id"], "kind": e["kind"], "status": e.get("status"), "type": e.get("type"), "house": e.get("house"),
            "era": e.get("era", {}).get("en"), "mat": e.get("materials"), "photos": len(e["photos"]),
            "hu": title_hu[:70], "en": (e["title"].get("en") or "")[:70],
            "det": f"{len(e['details']['hu'])}/{len(e['details']['en'] or [])}",
            "missing_en": missing, "has_ovr": has_ovr,
        })
    (ROOT / "data" / "normalize-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"{len(report)} entries written to data/items")


if __name__ == "__main__":
    main()
