#!/usr/bin/env python3
"""Build the Champagne Club website.

Reads   data/site.json        (types, houses, labels)
        data/items/*.json     (one file per item, article or page)
        templates/base.html   (the page frame: header, footer)
Writes  the finished HTML pages, the collection search data, sitemap.xml,
        robots.txt, llms.txt and .htaccess.

Usage:
    python3 tools/build.py            # test build for GitHub Pages (not indexed by Google)
    python3 tools/build.py --live     # real build for champagneclub.hu
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LIVE = "--live" in sys.argv
SITE = json.loads((DATA / "site.json").read_text())
BASE_URL = SITE["site_url"]
TEMPLATE = (ROOT / "templates" / "base.html").read_text()
TODAY = date.today().isoformat()

# Folders and files this script creates (removed and rebuilt each time).
GENERATED_DIRS = ["en", "hu", "category", "tag"]
MANIFEST = DATA / ".generated.json"

esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)  # noqa: E731

# ---------------------------------------------------------------------------
# Words used on the pages
# ---------------------------------------------------------------------------
S = {
    "en": {
        "tagline": "A private collection of champagne accessories",
        "sub": "The Collection",
        "nav": {"collection": "Collection", "houses": "Champagne Houses", "new": "New Arrivals",
                "sold": "Sold Archive", "guide": "Collectors' Guide", "about": "About", "contact": "Contact"},
        "search": "Search", "menu": "Menu", "home": "Home", "skip": "Skip to content",
        "hero_eyebrow": "A private collection",
        "hero_title": "The art of serving champagne",
        "hero_lead": "Ice buckets, glasses and accessories from the great champagne houses – each piece photographed, described and catalogued.",
        "explore": "Explore the collection", "buy_sell": "Buy or sell",
        "browse_type": "Browse by type", "view_all": "View the whole collection",
        "highlights_eyebrow": "From the collection", "highlights": "Highlights", "view_item": "View item",
        "prev": "Previous", "next": "Next", "pause": "Pause", "play": "Play", "slide": "Item",
        "recent": "Recently added", "see_new": "See all new arrivals",
        "houses_eyebrow": "Explore by maker", "all_houses": "All houses A–Z",
        "guide_all": "All articles", "article": "Article",
        "callout_title": "Looking for a piece, or have one to offer?",
        "callout_text": "Whether you are searching for something specific or would like to sell an item from your own collection, send a message and you will receive a personal reply.",
        "get_in_touch": "Get in touch",
        "footer_text": "A private collection of champagne accessories, presented in English and Hungarian.",
        "explore_h": "Explore", "about_h": "About", "legal_h": "Legal",
        "imprint": "Imprint", "privacy": "Privacy policy",
        "collection_intro": "Every piece in the collection, past and present. Search by name, champagne house or reference number, or narrow the list with the filters.",
        "search_label": "Search the collection", "search_ph": "Search by name, house or reference number",
        "sort_by": "Sort by", "sort_new": "Newest first", "sort_old": "Oldest piece first", "sort_house": "Champagne house A–Z", "sort_title": "Name A–Z",
        "filters": "Filters", "f_type": "Type", "f_house": "Champagne house", "f_period": "Period", "f_material": "Material", "f_status": "Status",
        "showing": "Showing", "item": "item", "items": "items", "clear_all": "Clear all", "remove": "remove",
        "no_results": "No items match your search. Try removing a filter.",
        "pieces": "pieces", "piece": "piece",
        "ref": "Ref.", "enquire": "Enquire about this item", "share": "Share",
        "other_lang": "Ezt az oldalt magyarul is elolvashatja:", "other_lang_link": "Magyar változat",
        "about_piece": "About this piece", "more_from": "More from", "similar": "Similar pieces", "view_house": "View the house",
        "enlarge": "Enlarge photo", "close": "Close", "photo": "Photo", "show_photo": "Show photo",
        "d_house": "Champagne house", "d_type": "Type", "d_status": "Availability",
        "houses_title": "Champagne Houses", "houses_intro": "The collection by maker. Each house page shows every piece made for that house.",
        "house_intro": "Pieces in the collection made for {name}.",
        "new_title": "New Arrivals", "new_intro": "The most recently added pieces.",
        "sold_title": "Sold Archive", "sold_intro": "Pieces that have found a new home. They stay here as a record of the collection.",
        "type_intro": "{n} {pieces} in the collection.",
        "guide_title": "Collectors' Guide", "guide_intro": "Stories, history and practical advice for collectors of champagne accessories.",
        "contact_title": "Contact", "contact_intro": "Questions about a piece, an offer to sell, or anything else – write to us and we will reply personally.",
        "f_name": "Your name", "f_email": "Email address", "f_topic": "Subject", "f_item": "Item (optional)", "f_message": "Message",
        "t_general": "General question", "t_buy": "I would like to buy", "t_sell": "I would like to sell",
        "send": "Send message",
        "form_test": "This is the test version of the website, so the form does not send messages yet. Please write to {email}.",
        "contact_aside_h": "Write directly", "contact_aside": "You can also email us at",
        "notfound_title": "Page not found", "notfound_text": "The page you were looking for has moved or no longer exists.",
        "in_hu_only": "This article is currently available in Hungarian only.",
        "read_hu": "Read it in Hungarian",
        "imprint_title": "Imprint", "privacy_title": "Privacy policy",
        "legal_todo": "This page will be completed with the operator's details before the site goes live.",
        "new_badge": "New",
    },
    "hu": {
        "tagline": "Pezsgős kiegészítők magángyűjteménye",
        "sub": "A gyűjtemény",
        "nav": {"collection": "Gyűjtemény", "houses": "Pezsgőházak", "new": "Új darabok",
                "sold": "Eladott darabok", "guide": "Gyűjtői kalauz", "about": "Rólunk", "contact": "Kapcsolat"},
        "search": "Keresés", "menu": "Menü", "home": "Főoldal", "skip": "Ugrás a tartalomra",
        "hero_eyebrow": "Magángyűjtemény",
        "hero_title": "A pezsgő felszolgálásának művészete",
        "hero_lead": "Pezsgőhűtők, poharak és kiegészítők a nagy pezsgőházaktól – minden darab lefényképezve, leírva és katalogizálva.",
        "explore": "A gyűjtemény megtekintése", "buy_sell": "Vétel vagy eladás",
        "browse_type": "Böngészés típus szerint", "view_all": "A teljes gyűjtemény",
        "highlights_eyebrow": "A gyűjteményből", "highlights": "Kiemelt darabok", "view_item": "Megnézem",
        "prev": "Előző", "next": "Következő", "pause": "Szünet", "play": "Lejátszás", "slide": "Darab",
        "recent": "Nemrég érkezett", "see_new": "Az összes új darab",
        "houses_eyebrow": "Böngészés pezsgőház szerint", "all_houses": "Az összes pezsgőház",
        "guide_all": "Az összes cikk", "article": "Cikk",
        "callout_title": "Keres valamit, vagy eladná egy darabját?",
        "callout_text": "Ha egy konkrét darabot keres, vagy saját gyűjteményéből szeretne eladni, írjon nekünk – személyesen válaszolunk.",
        "get_in_touch": "Kapcsolatfelvétel",
        "footer_text": "Pezsgős kiegészítők magángyűjteménye, magyar és angol nyelven.",
        "explore_h": "Böngészés", "about_h": "Rólunk", "legal_h": "Jogi információk",
        "imprint": "Impresszum", "privacy": "Adatvédelmi tájékoztató",
        "collection_intro": "A gyűjtemény minden darabja, a jelenlegiek és a korábbiak. Keressen név, pezsgőház vagy azonosító szerint, vagy szűkítse a listát a szűrőkkel.",
        "search_label": "Keresés a gyűjteményben", "search_ph": "Név, pezsgőház vagy azonosító",
        "sort_by": "Rendezés", "sort_new": "Legújabb elöl", "sort_old": "Legrégebbi darab elöl", "sort_house": "Pezsgőház A–Z", "sort_title": "Név A–Z",
        "filters": "Szűrők", "f_type": "Típus", "f_house": "Pezsgőház", "f_period": "Korszak", "f_material": "Anyag", "f_status": "Állapot",
        "showing": "Találatok:", "item": "darab", "items": "darab", "clear_all": "Szűrők törlése", "remove": "eltávolítás",
        "no_results": "Nincs a keresésnek megfelelő darab. Próbáljon meg egy szűrőt kikapcsolni.",
        "pieces": "darab", "piece": "darab",
        "ref": "Azonosító:", "enquire": "Érdeklődöm a darab iránt", "share": "Megosztás",
        "other_lang": "Read this page in English:", "other_lang_link": "English version",
        "about_piece": "A darabról", "more_from": "További darabok:", "similar": "Hasonló darabok", "view_house": "A pezsgőház oldala",
        "enlarge": "Kép nagyítása", "close": "Bezárás", "photo": "Kép", "show_photo": "Kép mutatása",
        "d_house": "Pezsgőház", "d_type": "Típus", "d_status": "Elérhetőség",
        "houses_title": "Pezsgőházak", "houses_intro": "A gyűjtemény pezsgőházak szerint. Minden pezsgőház oldalán az adott házhoz készült darabok láthatók.",
        "house_intro": "A gyűjtemény {name} pezsgőházhoz készült darabjai.",
        "new_title": "Új darabok", "new_intro": "A legutóbb érkezett darabok.",
        "sold_title": "Eladott darabok", "sold_intro": "Darabok, amelyek új otthonra találtak. A gyűjtemény részeként itt maradnak.",
        "type_intro": "{n} {pieces} a gyűjteményben.",
        "guide_title": "Gyűjtői kalauz", "guide_intro": "Történetek, pezsgőháztörténet és gyakorlati tanácsok pezsgős kiegészítők gyűjtőinek.",
        "contact_title": "Kapcsolat", "contact_intro": "Kérdése van egy darabról, eladná egy darabját, vagy bármi másról írna? Személyesen válaszolunk.",
        "f_name": "Név", "f_email": "E-mail-cím", "f_topic": "Tárgy", "f_item": "Darab (nem kötelező)", "f_message": "Üzenet",
        "t_general": "Általános kérdés", "t_buy": "Vásárolni szeretnék", "t_sell": "Eladni szeretnék",
        "send": "Üzenet küldése",
        "form_test": "Ez a weboldal tesztváltozata, ezért az űrlap még nem küld üzenetet. Kérjük, írjon a(z) {email} címre.",
        "contact_aside_h": "Írjon közvetlenül", "contact_aside": "E-mailben is elérhet minket:",
        "notfound_title": "Az oldal nem található", "notfound_text": "A keresett oldal elköltözött vagy már nem létezik.",
        "in_hu_only": "", "read_hu": "",
        "imprint_title": "Impresszum", "privacy_title": "Adatvédelmi tájékoztató",
        "legal_todo": "Ezt az oldalt az üzemeltető adataival egészítjük ki az élesítés előtt.",
        "new_badge": "Új",
    },
}

ICON = {
    "search": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
    "menu": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    "prev": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
    "next": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>',
    "pause": '<svg class="icon-pause" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/></svg>',
    "play": '<svg class="icon-play" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 5v14l12-7z"/></svg>',
    "zoom": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 9V4h5"/><path d="M20 15v5h-5"/><path d="M4 4l6 6"/><path d="M20 20l-6-6"/></svg>',
    "close": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg>',
}

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
TYPES = {t["key"]: t for t in SITE["types"]}
HOUSES = {h["key"]: h for h in SITE["houses"]}
PERIODS = {p["key"]: p for p in SITE["periods"]}
MATERIALS = {m["key"]: m for m in SITE["materials"]}
STATUSES = {s["key"]: s for s in SITE["statuses"]}

ENTRIES = [json.loads(p.read_text()) for p in sorted((DATA / "items").glob("*.json"))]
ITEMS = [e for e in ENTRIES if e["kind"] == "item"]
ARTICLES = sorted([e for e in ENTRIES if e["kind"] == "article"], key=lambda e: e["date"], reverse=True)
PAGES = {e["page"]: e for e in ENTRIES if e["kind"] == "page"}
ITEMS.sort(key=lambda e: e["date"], reverse=True)
for _e in ITEMS + list(PAGES.values()):
    # safety net: an item without an English title still gets an English page
    if not _e["title"].get("en"):
        print(f"  ! {_e['id']}: no English title yet – using the Hungarian one")
        _e["title"]["en"] = _e["title"]["hu"]
    if not _e.get("slug_en"):
        _e["slug_en"] = f"item-{_e['id']}"
    for _k in ("intro", "body", "details"):
        _e.setdefault(_k, {}).setdefault("en", None)


def house_name(key, lang):
    h = HOUSES.get(key)
    if not h:
        return ""
    return h.get("name_" + lang, h["name"])


def type_name(key, lang):
    return TYPES[key][lang] if key in TYPES else ""


def status_label(key, lang):
    return STATUSES[key][lang]


# ---------------------------------------------------------------------------
# Addresses
# ---------------------------------------------------------------------------
PATHS = {
    "home": {"en": "/", "hu": "/hu/"},
    "collection": {"en": "/en/collection/", "hu": "/hu/gyujtemeny/"},
    "houses": {"en": "/en/champagne-houses/", "hu": "/hu/pezsgohazak/"},
    "new": {"en": "/en/new-arrivals/", "hu": "/hu/uj-darabok/"},
    "sold": {"en": "/en/sold-archive/", "hu": "/hu/eladott-darabok/"},
    "guide": {"en": "/en/collectors-guide/", "hu": "/hu/gyujtoi-kalauz/"},
    "about": {"en": "/en/about/", "hu": "/hu/rolunk/"},
    "contact": {"en": "/en/contact/", "hu": "/hu/kapcsolat/"},
    "imprint": {"en": "/en/imprint/", "hu": "/hu/impresszum/"},
    "privacy": {"en": "/en/privacy/", "hu": "/hu/adatvedelem/"},
}
if "about" in PAGES:
    PATHS["about"]["hu"] = "/" + PAGES["about"]["slug_hu"] + "/"


def entry_path(e, lang):
    if lang == "hu":
        return "/" + e["slug_hu"] + "/"
    if e["kind"] == "article":
        return "/en/collectors-guide/" + e["slug_en"] + "/"
    return "/en/" + e["slug_en"] + "/"


def type_path(key, lang):
    return PATHS["collection"][lang] + (key if lang == "en" else TYPES[key]["slug_hu"]) + "/"


def house_path(key, lang):
    return PATHS["houses"][lang] + key + "/"


def has_lang(e, lang):
    return bool(e["title"].get(lang)) and bool(e["body"].get(lang) or e.get("kind") == "item")


# ---------------------------------------------------------------------------
# Photos
# ---------------------------------------------------------------------------
def photo_src(e, p, w=None):
    sizes = p["sizes"]
    if w is None:
        w = sizes[-1]
    pick = min((s for s in sizes if s >= w), default=sizes[-1])
    return f"/img/items/{e['id']}/{p['n']:02d}-{pick}.webp"


def srcset(e, p):
    return ", ".join(f"/img/items/{e['id']}/{p['n']:02d}-{s}.webp {s}w" for s in p["sizes"])


def photo_alt(e, lang, i=0):
    t = e["title"].get(lang) or e["title"].get("en") or e["title"].get("hu")
    return t if i == 0 else f"{t} – {S[lang]['photo'].lower()} {i + 1}"


def img_tag(e, lang, sizes_attr, eager=False, ratio_w=480):
    if not e.get("photos"):
        return ""
    p = e["photos"][0]
    h = round(ratio_w * p["h"] / p["w"])
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{photo_src(e, p, 480)}" srcset="{srcset(e, p)}" sizes="{sizes_attr}" '
            f'alt="{esc(photo_alt(e, lang))}" width="{ratio_w}" height="{h}" {load} decoding="async">')


# ---------------------------------------------------------------------------
# Small building blocks
# ---------------------------------------------------------------------------
def card_meta(e, lang):
    bits = [type_name(e["type"], lang)]
    if e.get("era", {}).get(lang):
        bits.append(e["era"][lang])
    return " · ".join(b for b in bits if b)


def badge(e, lang, new_ids=()):
    st = e["status"]
    if st in ("sold", "reserved", "made_to_order"):
        return f'<span class="badge badge-{st}">{esc(status_label(st, lang))}</span>'
    if e["id"] in new_ids:
        return f'<span class="badge badge-new">{esc(S[lang]["new_badge"])}</span>'
    return ""


def card(e, lang, new_ids=()):
    return (f'<a class="card" href="{entry_path(e, lang)}">'
            f'<div class="frame ratio-45">{badge(e, lang, new_ids)}{img_tag(e, lang, "(max-width: 600px) 90vw, 300px")}</div>'
            f'<span class="small-caps card-house">{esc(house_name(e.get("house"), lang))}</span>'
            f'<span class="card-title">{esc(e["title"][lang])}</span>'
            f'<span class="card-meta">{esc(card_meta(e, lang))}</span></a>')


def grid(entries, lang, new_ids=()):
    return '<div class="grid">' + "".join(card(e, lang, new_ids) for e in entries) + "</div>"


def crumbs(lang, trail):
    """trail: list of (label, path or None)."""
    items = [(S[lang]["home"], PATHS["home"][lang])] + trail
    li = []
    for label, path in items:
        li.append(f'<li><a href="{path}">{esc(label)}</a></li>' if path else
                  f'<li aria-current="page">{esc(label)}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(li)}</ol></nav>'


def crumbs_ld(lang, trail):
    items = [(S[lang]["home"], PATHS["home"][lang])] + trail
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label,
             **({"item": BASE_URL + path} if path else {})}
            for i, (label, path) in enumerate(items)
        ],
    }


def page_head(lang, title, intro=None, trail=None):
    out = '<section class="page-head wrap">'
    if trail is not None:
        out += crumbs(lang, trail)
    out += f"<h1>{esc(title)}</h1>"
    if intro:
        out += f'<p class="intro">{esc(intro)}</p>'
    return out + "</section>"


def clip(text, n=158):
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rsplit(" ", 1)[0].rstrip(",.;:–-") + "…"


# ---------------------------------------------------------------------------
# Page frame
# ---------------------------------------------------------------------------
OUT_FILES = []


def render(lang, *, path, title, description, body, alternates, active=None, og_image=None,
           ld=None, og_type="website"):
    s = S[lang]
    full_title = title if title.startswith(SITE["name"]) else f"{title} | {SITE['name']}"
    nav = "".join(
        f'<li><a href="{PATHS[k][lang]}"{" aria-current=\"page\"" if k == active else ""}>{esc(s["nav"][k])}</a></li>'
        for k in ("collection", "houses", "new", "sold", "guide", "about", "contact"))
    other = "hu" if lang == "en" else "en"
    alt_other = alternates.get(other)
    lang_links = []
    for code in ("en", "hu"):
        href = alternates.get(code)
        cur = ' aria-current="true"' if code == lang else ""
        label = code.upper()
        hl = "en" if code == "en" else "hu"
        if href:
            lang_links.append(f'<a href="{href}" hreflang="{hl}" lang="{hl}"{cur}>{label}</a>')
        else:
            lang_links.append(f'<span aria-disabled="true">{label}</span>')
    head = []
    head.append(f'<link rel="canonical" href="{BASE_URL}{path}">')
    for code, href in alternates.items():
        if href:
            head.append(f'<link rel="alternate" hreflang="{code}" href="{BASE_URL}{href}">')
    if alternates.get("en"):
        head.append(f'<link rel="alternate" hreflang="x-default" href="{BASE_URL}{alternates["en"]}">')
    if not LIVE:
        head.append('<meta name="robots" content="noindex, nofollow">')
    img = og_image or "/img/og-default.jpg"
    head += [
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{SITE["name"]}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:url" content="{BASE_URL}{path}">',
        f'<meta property="og:locale" content="{"en_GB" if lang == "en" else "hu_HU"}">',
        f'<meta property="og:image" content="{BASE_URL}{img}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    for block in (ld or []):
        head.append('<script type="application/ld+json">' +
                    json.dumps(block, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    js_text = {k: s[k] for k in ("slide", "play", "pause", "showing", "item", "items", "clear_all", "remove")}
    js_text["clearAll"] = s["clear_all"]
    page = TEMPLATE
    repl = {
        "{{lang}}": lang,
        "{{title}}": esc(full_title),
        "{{description}}": esc(description),
        "{{head}}": "\n".join(head),
        "{{skip}}": esc(s["skip"]),
        "{{tagline}}": esc(s["tagline"]),
        "{{lang_links}}": '<span aria-hidden="true">|</span>'.join(lang_links),
        "{{home}}": PATHS["home"][lang],
        "{{logo_sub}}": esc(s["sub"]),
        "{{menu}}": esc(s["menu"]),
        "{{nav}}": nav,
        "{{search_href}}": PATHS["collection"][lang] + "#q",
        "{{search}}": esc(s["search"]),
        "{{body}}": body,
        "{{footer}}": footer(lang, alt_other),
        "{{js_text}}": json.dumps(js_text, ensure_ascii=False),
        "{{icon_search}}": ICON["search"], "{{icon_menu}}": ICON["menu"],
    }
    for k, v in repl.items():
        page = page.replace(k, v)
    write(path, page)


def footer(lang, other_href):
    s = S[lang]
    P = lambda k: PATHS[k][lang]  # noqa: E731
    other = "hu" if lang == "en" else "en"
    other_label = "Magyar" if other == "hu" else "English"
    return f"""<div class="wrap footer-cols">
<div class="footer-brand"><span class="logo-name">{SITE['name']}</span><p>{esc(s['footer_text'])}</p></div>
<div class="footer-col"><span class="small-caps">{esc(s['explore_h'])}</span>
<a href="{P('collection')}">{esc(s['nav']['collection'])}</a><a href="{P('houses')}">{esc(s['nav']['houses'])}</a>
<a href="{P('new')}">{esc(s['nav']['new'])}</a><a href="{P('sold')}">{esc(s['nav']['sold'])}</a></div>
<div class="footer-col"><span class="small-caps">{esc(s['about_h'])}</span>
<a href="{P('guide')}">{esc(s['nav']['guide'])}</a><a href="{P('about')}">{esc(s['nav']['about'])}</a>
<a href="{P('contact')}">{esc(s['nav']['contact'])}</a></div>
<div class="footer-col"><span class="small-caps">{esc(s['legal_h'])}</span>
<a href="{P('imprint')}">{esc(s['imprint'])}</a><a href="{P('privacy')}">{esc(s['privacy'])}</a></div>
</div>
<div class="wrap footer-bottom"><span>© {date.today().year} {SITE['name']}</span>
<span><a href="{other_href or PATHS['home'][other]}" lang="{other}" hreflang="{other}">{other_label}</a></span></div>"""


def write(path, content):
    rel = path.lstrip("/")
    target = ROOT / rel / "index.html" if (rel == "" or rel.endswith("/")) else ROOT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    OUT_FILES.append(str(target.relative_to(ROOT)))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def new_arrivals(n=8):
    return [e for e in ITEMS if e["status"] != "sold"][:n]


def build_home(lang):
    s = S[lang]
    new_ids = {e["id"] for e in new_arrivals(8)}
    hl = [e for e in ITEMS if e.get("highlight") and e.get("photos")]
    hero = hl[0] if hl else (ITEMS[0] if ITEMS else None)

    hero_html = ""
    if hero:
        hero_html = (f'<div class="hero-photo"><a href="{entry_path(hero, lang)}">{img_tag(hero, lang, "(max-width: 900px) 90vw, 560px", eager=True)}</a>'
                     f'<p class="hero-caption">{esc(house_name(hero.get("house"), lang))} – {esc(hero["title"][lang])}</p></div>')

    # browse by type
    type_cards = []
    for t in SITE["types"]:
        members = [e for e in ITEMS if e["type"] == t["key"]]
        if not members:
            continue
        rep = next((e for e in members if e.get("photos")), members[0])
        n = len(members)
        type_cards.append(
            f'<a class="card type-card" href="{type_path(t["key"], lang)}"><div class="frame ratio-11">'
            f'{img_tag(rep, lang, "(max-width: 600px) 45vw, 200px")}</div>'
            f'<span class="card-title">{esc(t[lang])}</span><span class="count">{n} {s["piece"] if n == 1 else s["pieces"]}</span></a>')

    # highlights
    slides = []
    for i, e in enumerate(hl):
        p = e["photos"][0]
        if i == 0:
            im = f'<img src="{photo_src(e, p, 960)}" srcset="{srcset(e, p)}" sizes="(max-width: 900px) 90vw, 600px" alt="{esc(photo_alt(e, lang))}" width="{p["w"]}" height="{p["h"]}" loading="lazy">'
        else:
            im = f'<img data-src="{photo_src(e, p, 960)}" data-srcset="{srcset(e, p)}" sizes="(max-width: 900px) 90vw, 600px" alt="{esc(photo_alt(e, lang))}" width="{p["w"]}" height="{p["h"]}">'
            im += f'<noscript><img src="{photo_src(e, p, 960)}" alt="{esc(photo_alt(e, lang))}"></noscript>'
        slides.append(
            f'<article class="hl-slide{" is-active" if i == 0 else ""}" aria-roledescription="slide" aria-label="{i + 1} / {len(hl)}">'
            f'<a class="hl-photo" href="{entry_path(e, lang)}" tabindex="-1" aria-hidden="true">{im}</a>'
            f'<div class="hl-text"><span class="small-caps">{esc(house_name(e.get("house"), lang))}</span>'
            f'<h3>{esc(e["title"][lang])}</h3><p>{esc(clip(e["intro"].get(lang), 220))}</p>'
            f'<a class="btn" href="{entry_path(e, lang)}">{esc(s["view_item"])}</a></div></article>')
    hl_html = ""
    if slides:
        hl_html = f"""<section class="section highlights" aria-roledescription="carousel" aria-label="{esc(s['highlights'])}">
<div class="wrap"><div class="section-head"><div><p class="eyebrow">{esc(s['highlights_eyebrow'])}</p><h2>{esc(s['highlights'])}</h2></div></div>
<div class="hl-viewport" aria-live="polite">{''.join(slides)}</div>
<div class="hl-controls">
<button type="button" class="hl-prev" aria-label="{esc(s['prev'])}">{ICON['prev']}</button>
<div class="hl-dots"></div>
<button type="button" class="hl-next" aria-label="{esc(s['next'])}">{ICON['next']}</button>
<button type="button" class="hl-play" aria-pressed="false" aria-label="{esc(s['pause'])}">{ICON['pause']}{ICON['play']}</button>
</div></div></section>"""

    # houses
    counts = {}
    for e in ITEMS:
        if e.get("house") and e["house"] != "other":
            counts[e["house"]] = counts.get(e["house"], 0) + 1
    top = sorted(counts, key=lambda k: (-counts[k], house_name(k, lang)))[:12]
    houses_html = "".join(f'<li><a href="{house_path(k, lang)}">{esc(house_name(k, lang))}</a></li>' for k in top)

    # guide
    arts = [a for a in ARTICLES if has_lang(a, lang)][:3]
    art_cards = "".join(
        f'<a class="card" href="{entry_path(a, lang)}"><div class="frame ratio-32">{img_tag(a, lang, "(max-width: 600px) 90vw, 400px")}</div>'
        f'<span class="small-caps card-house">{esc(s["article"])}</span><span class="card-title">{esc(a["title"][lang])}</span></a>'
        for a in arts)

    body = f"""
<section class="hero"><div class="wrap">
<div class="hero-text"><p class="eyebrow">{esc(s['hero_eyebrow'])}</p><h1>{esc(s['hero_title'])}</h1>
<p class="lead">{esc(s['hero_lead'])}</p>
<div class="hero-actions"><a class="btn btn-dark" href="{PATHS['collection'][lang]}">{esc(s['explore'])}</a>
<a class="btn" href="{PATHS['contact'][lang]}">{esc(s['buy_sell'])}</a></div></div>
{hero_html}</div></section>

<section class="section section-line"><div class="wrap">
<div class="section-head"><h2>{esc(s['browse_type'])}</h2><a class="link-line" href="{PATHS['collection'][lang]}">{esc(s['view_all'])}</a></div>
<div class="grid-types">{''.join(type_cards)}</div></div></section>

{hl_html}

<section class="section section-alt"><div class="wrap">
<div class="section-head"><div><p class="eyebrow">{esc(s['recent'])}</p><h2>{esc(s['nav']['new'])}</h2></div>
<a class="link-line" href="{PATHS['new'][lang]}">{esc(s['see_new'])}</a></div>
{grid(new_arrivals(8), lang)}</div></section>

<section class="section" style="text-align:center"><div class="wrap">
<p class="eyebrow">{esc(s['houses_eyebrow'])}</p><h2 style="font-size:clamp(34px,4vw,44px);margin-bottom:40px">{esc(s['nav']['houses'])}</h2>
<ul class="houses-list">{houses_html}</ul>
<p style="margin-top:40px"><a class="link-line" href="{PATHS['houses'][lang]}">{esc(s['all_houses'])}</a></p></div></section>

{f'''<section class="section section-line"><div class="wrap">
<div class="section-head"><h2>{esc(s['nav']['guide'])}</h2><a class="link-line" href="{PATHS['guide'][lang]}">{esc(s['guide_all'])}</a></div>
<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">{art_cards}</div></div></section>''' if art_cards else ''}

<section class="section" style="padding-top:0"><div class="wrap"><div class="callout">
<h2>{esc(s['callout_title'])}</h2><p>{esc(s['callout_text'])}</p>
<a class="btn btn-dark" href="{PATHS['contact'][lang]}">{esc(s['get_in_touch'])}</a></div></div></section>
"""
    ld = [{
        "@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": BASE_URL + "/",
        "inLanguage": ["en", "hu"],
        "potentialAction": {"@type": "SearchAction", "target": BASE_URL + PATHS["collection"]["en"] + "?q={search_term_string}",
                            "query-input": "required name=search_term_string"},
    }, {
        "@context": "https://schema.org", "@type": "Organization", "name": SITE["name"], "url": BASE_URL + "/",
        "email": SITE["email"], "description": S["en"]["tagline"],
    }]
    og = photo_src(hero, hero["photos"][0], 960) if hero and hero.get("photos") else None
    render(lang, path=PATHS["home"][lang], title=f"{SITE['name']} – {s['tagline']}",
           description=s["hero_lead"], body=body, alternates=PATHS["home"], og_image=og, ld=ld)


def build_collection(lang):
    s = S[lang]
    body = f"""{page_head(lang, s['nav']['collection'], s['collection_intro'], [(s['nav']['collection'], None)])}
<div class="wrap" id="collection-app" data-src="/assets/data/collection-{lang}.json">
<form class="toolbar" id="search-form" role="search">
<label for="q" class="visually-hidden">{esc(s['search_label'])}</label>
<div class="search-box">{ICON['search']}<input id="q" type="search" placeholder="{esc(s['search_ph'])}" autocomplete="off"></div>
<label for="sort" style="font-size:14px;color:var(--muted)">{esc(s['sort_by'])}</label>
<select id="sort" class="select"><option value="new">{esc(s['sort_new'])}</option><option value="old">{esc(s['sort_old'])}</option>
<option value="house">{esc(s['sort_house'])}</option><option value="title">{esc(s['sort_title'])}</option></select>
<button type="button" class="btn filters-toggle" aria-expanded="false" aria-controls="filters">{esc(s['filters'])}</button>
</form>
<div class="collection-layout" style="margin-top:36px">
<aside class="filters" id="filters" aria-label="{esc(s['filters'])}"></aside>
<div class="results">
<div class="results-bar"><span class="results-count" id="results-count" aria-live="polite"></span><div class="chips" id="chips"></div></div>
<div class="grid" id="results-grid"></div>
<p class="empty" id="empty" hidden>{esc(s['no_results'])}</p>
<nav class="pager" id="pager" aria-label="Pages"></nav>
<noscript><ul>{''.join(f'<li><a href="{type_path(t["key"], lang)}">{esc(t[lang])}</a></li>' for t in SITE["types"])}</ul></noscript>
</div></div></div>"""
    render(lang, path=PATHS["collection"][lang], title=s["nav"]["collection"], description=s["collection_intro"],
           body=body, alternates=PATHS["collection"], active="collection",
           ld=[crumbs_ld(lang, [(s["nav"]["collection"], PATHS["collection"][lang])])])

    # search data for the collection page
    used = lambda field: {v for e in ITEMS for v in (e.get(field) if isinstance(e.get(field), list) else [e.get(field)]) if v}  # noqa: E731
    facets = {
        "type": {"label": s["f_type"], "options": [{"key": t["key"], "label": t[lang]} for t in SITE["types"] if t["key"] in used("type")]},
        "house": {"label": s["f_house"], "options": sorted(
            [{"key": k, "label": house_name(k, lang)} for k in used("house")],
            key=lambda o: (o["key"] == "other", o["label"]))},
        "period": {"label": s["f_period"], "options": [{"key": p["key"], "label": p[lang]} for p in SITE["periods"] if p["key"] in used("period")]},
        "material": {"label": s["f_material"], "options": [{"key": m["key"], "label": m[lang]} for m in SITE["materials"] if m["key"] in used("materials")]},
        "status": {"label": s["f_status"], "options": [{"key": x["key"], "label": x[lang]} for x in SITE["statuses"] if x["key"] in used("status")]},
    }
    rows = []
    for e in ITEMS:
        p = e["photos"][0] if e.get("photos") else None
        rows.append({
            "id": e["id"], "ref": e["ref"], "url": entry_path(e, lang), "title": e["title"][lang],
            "house": e.get("house") or "", "houseName": house_name(e.get("house"), lang),
            "type": e["type"], "typeName": type_name(e["type"], lang),
            "period": e.get("period") or "", "material": e.get("materials", []), "status": e["status"],
            "badge": status_label(e["status"], lang) if e["status"] != "available" else "",
            "year": e.get("year"), "date": e["date"], "meta": card_meta(e, lang),
            "img": photo_src(e, p, 480) if p else "", "srcset": srcset(e, p) if p else "", "alt": photo_alt(e, lang),
            "keywords": e.get("keywords", {}).get(lang, ""),
        })
    out = {"facetOrder": ["type", "house", "period", "material", "status"], "facets": facets, "items": rows}
    target = ROOT / "assets" / "data" / f"collection-{lang}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))


def build_listing(lang, key, path_map, title, intro, entries, trail_parent=None, new_ids=()):
    s = S[lang]
    trail = ([trail_parent] if trail_parent else []) + [(title, None)]
    body = page_head(lang, title, intro, trail) + f'<section class="wrap" style="padding-bottom:96px">{grid(entries, lang, new_ids)}</section>'
    ld = [crumbs_ld(lang, [(t, p) for t, p in trail[:-1]] + [(title, path_map[lang])]),
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": BASE_URL + path_map[lang],
           "inLanguage": lang, "hasPart": [{"@type": "Product", "name": e["title"][lang], "url": BASE_URL + entry_path(e, lang)} for e in entries[:50]]}]
    og = photo_src(entries[0], entries[0]["photos"][0], 960) if entries and entries[0].get("photos") else None
    render(lang, path=path_map[lang], title=title, description=clip(intro), body=body,
           alternates=path_map, active=key, ld=ld, og_image=og)


def build_types(lang):
    s = S[lang]
    for t in SITE["types"]:
        members = [e for e in ITEMS if e["type"] == t["key"]]
        if not members:
            continue
        n = len(members)
        intro = s["type_intro"].format(n=n, pieces=s["piece"] if n == 1 else s["pieces"])
        build_listing(lang, "collection", {"en": type_path(t["key"], "en"), "hu": type_path(t["key"], "hu")},
                      t[lang], intro, members, (s["nav"]["collection"], PATHS["collection"][lang]))


def build_houses(lang):
    s = S[lang]
    counts = {}
    for e in ITEMS:
        if e.get("house"):
            counts[e["house"]] = counts.get(e["house"], 0) + 1
    keys = sorted(counts, key=lambda k: (k == "other", house_name(k, lang)))
    lis = "".join(
        f'<li><a href="{house_path(k, lang)}"><span>{esc(house_name(k, lang))}</span><span class="count">{counts[k]} {s["piece"] if counts[k] == 1 else s["pieces"]}</span></a></li>'
        for k in keys)
    body = page_head(lang, s["houses_title"], s["houses_intro"], [(s["nav"]["houses"], None)]) + \
        f'<section class="wrap" style="padding-bottom:96px"><ul class="houses-index">{lis}</ul></section>'
    render(lang, path=PATHS["houses"][lang], title=s["houses_title"], description=s["houses_intro"], body=body,
           alternates=PATHS["houses"], active="houses",
           ld=[crumbs_ld(lang, [(s["nav"]["houses"], PATHS["houses"][lang])])])
    for k in keys:
        members = [e for e in ITEMS if e.get("house") == k]
        name = house_name(k, lang)
        build_listing(lang, "houses", {"en": house_path(k, "en"), "hu": house_path(k, "hu")}, name,
                      s["house_intro"].format(name=name), members, (s["nav"]["houses"], PATHS["houses"][lang]))


def related_for(e):
    same_house = [x for x in ITEMS if x is not e and x.get("house") == e.get("house") and e.get("house") not in (None, "other")]
    same_type = [x for x in ITEMS if x is not e and x["type"] == e["type"] and x not in same_house]
    if len(same_house) >= 2:
        return "house", (same_house + same_type)[:4]
    return "type", (same_type + same_house)[:4]


def build_item(e, lang):
    s = S[lang]
    other = "hu" if lang == "en" else "en"
    alts = {"en": entry_path(e, "en"), "hu": entry_path(e, "hu")}
    title = e["title"][lang]
    photos = e.get("photos", [])
    tlabel = type_name(e["type"], lang)
    trail = [(s["nav"]["collection"], PATHS["collection"][lang]), (tlabel, type_path(e["type"], lang)), (title, None)]

    js_photos = [{"m": photo_src(e, p, 960), "l": photo_src(e, p), "srcset": srcset(e, p), "alt": photo_alt(e, lang, i)}
                 for i, p in enumerate(photos)]
    if photos:
        p0 = photos[0]
        main = (f'<img src="{photo_src(e, p0, 960)}" srcset="{srcset(e, p0)}" sizes="(max-width: 900px) 92vw, 620px" '
                f'alt="{esc(photo_alt(e, lang))}" width="{p0["w"]}" height="{p0["h"]}" fetchpriority="high">')
        thumbs = "".join(
            f'<button type="button" aria-label="{esc(s["show_photo"])} {i + 1}" aria-current="{"true" if i == 0 else "false"}">'
            f'<img src="{photo_src(e, p, 480)}" alt="" width="120" height="{round(120 * p["h"] / p["w"])}" loading="lazy"></button>'
            for i, p in enumerate(photos)) if len(photos) > 1 else ""
        gallery = (f'<div class="gallery" data-photos="{esc(json.dumps(js_photos, ensure_ascii=False))}">'
                   f'<div class="gallery-main">{main}<button type="button" class="zoom-btn" aria-label="{esc(s["enlarge"])}">{ICON["zoom"]}</button></div>'
                   f'<div class="thumbs">{thumbs}</div></div>')
    else:
        gallery = '<div class="gallery"><div class="gallery-main"></div></div>'

    details = [(s["d_house"], f'<a href="{house_path(e["house"], lang)}">{esc(house_name(e["house"], lang))}</a>')] if e.get("house") and e["house"] != "other" else []
    details.append((s["d_type"], f'<a href="{type_path(e["type"], lang)}">{esc(tlabel)}</a>'))
    details += [(esc(k), esc(v)) for k, v in e["details"].get(lang, [])]
    details.append((s["d_status"], esc(status_label(e["status"], lang))))
    dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in details)

    enquire = PATHS["contact"][lang] + "?item=" + esc(f'{e["ref"]} – {title}').replace(" ", "+")
    rel_kind, rel = related_for(e)
    rel_title = f'{s["more_from"]} {house_name(e["house"], lang)}' if rel_kind == "house" else s["similar"]
    rel_link = (f'<a class="link-line" href="{house_path(e["house"], lang)}">{esc(s["view_house"])}</a>' if rel_kind == "house" else
                f'<a class="link-line" href="{type_path(e["type"], lang)}">{esc(tlabel)}</a>')

    body_html = e["body"].get(lang) or ""
    body = f"""<div class="wrap" style="padding-top:36px">{crumbs(lang, trail[:-1] + [(title, None)])}</div>
<section class="wrap item-top" style="padding-top:24px">
{gallery}
<div class="item-info">
{f'<a class="small-caps" href="{house_path(e["house"], lang)}">{esc(house_name(e["house"], lang))}</a>' if e.get("house") and e["house"] != "other" else ''}
<h1>{esc(title)}</h1>
<div class="status-row"><span class="status status-{e['status']}">{esc(status_label(e['status'], lang))}</span><span>{s['ref']} {esc(e['ref'])}</span></div>
{f'<p class="item-intro">{esc(e["intro"][lang])}</p>' if e["intro"].get(lang) else ''}
<dl class="details">{dl}</dl>
<div class="item-actions"><a class="btn btn-dark" href="{enquire}">{esc(s['enquire'])}</a></div>
<p class="other-lang">{esc(s['other_lang'])} <a href="{alts[other]}" lang="{other}" hreflang="{other}">{esc(s['other_lang_link'])}</a></p>
</div></section>
{f'''<section class="section-line"><div class="wrap section split"><h2>{esc(s['about_piece'])}</h2><div class="prose">{body_html}</div></div></section>''' if body_html.strip() else ''}
{f'''<section class="section section-alt"><div class="wrap"><div class="section-head"><h2 style="font-size:36px">{esc(rel_title)}</h2>{rel_link}</div>{grid(rel, lang)}</div></section>''' if rel else ''}
<dialog class="lightbox" aria-label="{esc(title)}"><div class="lightbox-inner"><img src="" alt="">
<button type="button" class="lb-close" aria-label="{esc(s['close'])}">{ICON['close']}</button>
<button type="button" class="lb-prev" aria-label="{esc(s['prev'])}">{ICON['prev']}</button>
<button type="button" class="lb-next" aria-label="{esc(s['next'])}">{ICON['next']}</button>
<span class="lb-count"></span></div></dialog>"""

    product = {
        "@context": "https://schema.org", "@type": "Product", "name": title, "sku": e["ref"],
        "url": BASE_URL + entry_path(e, lang), "description": clip(e["intro"].get(lang) or body_html, 300),
        "image": [BASE_URL + photo_src(e, p) for p in photos[:6]],
        "category": tlabel, "inLanguage": lang,
    }
    if e.get("house") and e["house"] != "other":
        product["brand"] = {"@type": "Brand", "name": house_name(e["house"], lang)}
    for k, v in e.get("schema", {}).items():
        product[k] = v
    ld = [product, crumbs_ld(lang, trail[:-1] + [(title, entry_path(e, lang))])]
    desc = clip(e["intro"].get(lang) or body_html)
    render(lang, path=entry_path(e, lang), title=title, description=desc, body=body, alternates=alts,
           active="collection", og_image=photo_src(e, photos[0], 960) if photos else None, ld=ld, og_type="product")


def build_article(a, lang):
    s = S[lang]
    alts = {"en": entry_path(a, "en") if has_lang(a, "en") else None, "hu": entry_path(a, "hu")}
    title = a["title"][lang]
    trail = [(s["nav"]["guide"], PATHS["guide"][lang]), (title, None)]
    p = a["photos"][0] if a.get("photos") else None
    cover = (f'<div class="wrap" style="max-width:980px;margin-bottom:40px"><img src="{photo_src(a, p, 960)}" srcset="{srcset(a, p)}" '
             f'sizes="(max-width: 1000px) 92vw, 940px" alt="{esc(photo_alt(a, lang))}" width="{p["w"]}" height="{p["h"]}" fetchpriority="high"></div>') if p else ""
    gallery = ""
    if a.get("photos") and len(a["photos"]) > 1:
        gallery = '<div class="wrap" style="max-width:980px;padding-bottom:72px"><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px">' + "".join(
            f'<div class="frame ratio-11"><img src="{photo_src(a, ph, 480)}" srcset="{srcset(a, ph)}" sizes="240px" alt="{esc(photo_alt(a, lang, i + 1))}" loading="lazy" width="480" height="480"></div>'
            for i, ph in enumerate(a["photos"][1:13])) + "</div></div>"
    other = "hu" if lang == "en" else "en"
    other_link = f'<p class="other-lang" style="margin-top:32px">{esc(s["other_lang"])} <a href="{alts[other]}" lang="{other}">{esc(s["other_lang_link"])}</a></p>' if alts.get(other) else ""
    body = f"""<div class="wrap" style="max-width:980px;padding-top:36px">{crumbs(lang, trail)}
<p class="eyebrow" style="margin-top:24px">{esc(s['nav']['guide'])}</p><h1 style="font-size:clamp(38px,4.6vw,58px)">{esc(title)}</h1></div>
<div style="height:36px"></div>{cover}
<div class="wrap" style="max-width:980px;padding-bottom:56px"><div class="prose" style="margin:0 auto">{a['body'][lang]}{other_link}</div></div>
{gallery}"""
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": title, "inLanguage": lang,
           "datePublished": a["date"], "dateModified": a.get("modified", a["date"]),
           "image": [BASE_URL + photo_src(a, ph) for ph in a.get("photos", [])[:3]],
           "author": {"@type": "Organization", "name": SITE["name"]},
           "publisher": {"@type": "Organization", "name": SITE["name"]},
           "mainEntityOfPage": BASE_URL + entry_path(a, lang)},
          crumbs_ld(lang, [(s["nav"]["guide"], PATHS["guide"][lang]), (title, entry_path(a, lang))])]
    render(lang, path=entry_path(a, lang), title=title, description=clip(a["intro"].get(lang) or a["body"][lang]),
           body=body, alternates=alts, active="guide", ld=ld, og_type="article",
           og_image=photo_src(a, p, 960) if p else None)


def build_guide(lang):
    s = S[lang]
    cards = []
    for a in ARTICLES:
        if has_lang(a, lang):
            href, t = entry_path(a, lang), a["title"][lang]
        else:
            href, t = entry_path(a, "hu"), a["title"].get("en") or a["title"]["hu"]
        note = "" if has_lang(a, lang) else f'<span class="card-meta">{esc(s["in_hu_only"])}</span>'
        cards.append(f'<a class="card" href="{href}"><div class="frame ratio-32">{img_tag(a, lang, "(max-width: 600px) 90vw, 400px")}</div>'
                     f'<span class="small-caps card-house">{esc(s["article"])}</span><span class="card-title">{esc(t)}</span>{note}</a>')
    body = page_head(lang, s["guide_title"], s["guide_intro"], [(s["nav"]["guide"], None)]) + \
        f'<section class="wrap" style="padding-bottom:96px"><div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">{"".join(cards)}</div></section>'
    render(lang, path=PATHS["guide"][lang], title=s["guide_title"], description=s["guide_intro"], body=body,
           alternates=PATHS["guide"], active="guide", ld=[crumbs_ld(lang, [(s["nav"]["guide"], PATHS["guide"][lang])])])


def build_about(lang):
    s = S[lang]
    pg = PAGES.get("about")
    if not pg:
        return
    title = pg["title"][lang]
    p = pg["photos"][0] if pg.get("photos") else None
    cover = (f'<div class="wrap" style="max-width:980px;margin-bottom:40px"><img src="{photo_src(pg, p, 960)}" srcset="{srcset(pg, p)}" '
             f'sizes="(max-width: 1000px) 92vw, 940px" alt="{esc(title)}" width="{p["w"]}" height="{p["h"]}"></div>') if p else ""
    body = page_head(lang, title, None, [(s["nav"]["about"], None)]) + cover + \
        f'<div class="wrap" style="max-width:980px;padding-bottom:96px"><div class="prose">{pg["body"][lang]}</div></div>'
    render(lang, path=PATHS["about"][lang], title=title, description=clip(pg["intro"].get(lang) or pg["body"][lang]),
           body=body, alternates=PATHS["about"], active="about")


def build_contact(lang):
    s = S[lang]
    live = "true" if LIVE else "false"
    action = "/contact.php"
    body = page_head(lang, s["contact_title"], s["contact_intro"], [(s["nav"]["contact"], None)]) + f"""
<section class="wrap contact-layout">
<form class="form" id="contact-form" method="post" action="{action}" data-live="{live}">
<p class="notice" id="form-notice" tabindex="-1" {'hidden' if LIVE else ''}>{esc(s['form_test'].format(email=SITE['email']))}</p>
<div class="row"><div><label for="cf-name">{esc(s['f_name'])}</label><input id="cf-name" name="name" autocomplete="name" required></div>
<div><label for="cf-email">{esc(s['f_email'])}</label><input id="cf-email" name="email" type="email" autocomplete="email" required></div></div>
<div class="row"><div><label for="cf-topic">{esc(s['f_topic'])}</label><select id="cf-topic" name="topic">
<option value="general">{esc(s['t_general'])}</option><option value="buy">{esc(s['t_buy'])}</option><option value="sell">{esc(s['t_sell'])}</option></select></div>
<div><label for="cf-item">{esc(s['f_item'])}</label><input id="cf-item" name="item"></div></div>
<div><label for="cf-message">{esc(s['f_message'])}</label><textarea id="cf-message" name="message" required></textarea></div>
<div class="hp" aria-hidden="true"><label for="cf-website">Website</label><input id="cf-website" name="website" tabindex="-1" autocomplete="off"></div>
<input type="hidden" name="lang" value="{lang}">
<div><button class="btn btn-dark" type="submit">{esc(s['send'])}</button></div>
</form>
<aside class="contact-aside"><h2>{esc(s['contact_aside_h'])}</h2><p>{esc(s['contact_aside'])}<br><a class="link-line" style="text-transform:none;letter-spacing:0;font-size:16px" href="mailto:{SITE['email']}">{SITE['email']}</a></p></aside>
</section>"""
    render(lang, path=PATHS["contact"][lang], title=s["contact_title"], description=s["contact_intro"], body=body,
           alternates=PATHS["contact"], active="contact")


def build_legal(lang):
    s = S[lang]
    for key, tkey in (("imprint", "imprint_title"), ("privacy", "privacy_title")):
        body = page_head(lang, s[tkey], None, [(s[tkey], None)]) + \
            f'<div class="wrap" style="padding-bottom:96px"><p class="notice">{esc(s["legal_todo"])}</p></div>'
        render(lang, path=PATHS[key][lang], title=s[tkey], description=s[tkey], body=body, alternates=PATHS[key])


def build_404():
    s = S["en"]
    body = f"""<section class="page-head wrap" style="padding-bottom:96px"><h1>{esc(s['notfound_title'])}</h1>
<p class="intro">{esc(s['notfound_text'])}</p><p class="intro" lang="hu">{esc(S['hu']['notfound_text'])}</p>
<div class="hero-actions"><a class="btn btn-dark" href="/en/collection/">{esc(s['nav']['collection'])}</a><a class="btn" href="/hu/">Magyar főoldal</a></div></section>"""
    render("en", path="/404.html", title=s["notfound_title"], description=s["notfound_text"], body=body,
           alternates={"en": "/", "hu": "/hu/"})


# ---------------------------------------------------------------------------
# Old WordPress addresses → new pages
# ---------------------------------------------------------------------------
def redirects():
    rules = []  # (old path, new path)
    for t in SITE["types"]:
        if t["wp"]:
            rules.append((f"/category/{wp_cat_slug(t['wp'])}/", type_path(t["key"], "hu")))
    for h in SITE["houses"]:
        for tid in h["wp"]:
            slug = wp_tag_slug(tid)
            if slug:
                rules.append((f"/tag/{slug}/", house_path(h["key"], "hu") if h["key"] != "other" else PATHS["houses"]["hu"]))
    sold_cat = wp_cat_slug(24)
    if sold_cat:
        rules.append((f"/category/{sold_cat}/", PATHS["sold"]["hu"]))
    rules = [(o, n) for o, n in rules if o and "None" not in o]
    # GitHub Pages cannot send real redirects, so small forwarding pages are written there.
    for old, new in rules:
        write(old, f'<!doctype html><html lang="hu"><head><meta charset="utf-8"><title>Átirányítás</title>'
                   f'<meta name="robots" content="noindex"><link rel="canonical" href="{BASE_URL}{new}">'
                   f'<meta http-equiv="refresh" content="0; url={new}"></head><body><a href="{new}">{new}</a></body></html>')
    # Apache: real permanent redirects
    lines = ["# Generated by tools/build.py", "Options -Indexes", "ErrorDocument 404 /404.html", "",
             "<IfModule mod_rewrite.c>", "RewriteEngine On",
             "# Always use https and the main domain",
             "RewriteCond %{HTTPS} off [OR]", "RewriteCond %{HTTP_HOST} ^www\\. [NC]",
             "RewriteRule ^(.*)$ https://champagneclub.hu/$1 [R=301,L]",
             "# Old WordPress addresses",
             "RewriteRule ^page/[0-9]+/?$ / [R=301,L]",
             "RewriteRule ^author/ / [R=301,L]",
             "RewriteRule ^feed/?$ / [R=301,L]",
             "RewriteRule ^(.+)/feed/?$ /$1/ [R=301,L]",
             "RewriteRule ^wp-sitemap.*\\.xml$ /sitemap.xml [R=301,L]",
             "RewriteCond %{QUERY_STRING} ^p=([0-9]+)$", "RewriteRule ^$ / [R=301,L,QSD]",
             "</IfModule>", ""]
    for old, new in rules:
        lines.append(f"Redirect 301 {old} {new}")
    lines += ["", "<IfModule mod_expires.c>", "ExpiresActive On",
              'ExpiresByType image/webp "access plus 1 year"', 'ExpiresByType font/woff2 "access plus 1 year"',
              'ExpiresByType text/css "access plus 1 week"', 'ExpiresByType application/javascript "access plus 1 week"',
              'ExpiresByType text/html "access plus 0 seconds"', "</IfModule>",
              "<IfModule mod_deflate.c>", "AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml text/xml", "</IfModule>",
              "AddType font/woff2 .woff2", "AddType image/webp .webp", ""]
    write("/.htaccess", "\n".join(lines))
    return rules


_META = json.loads((DATA / "raw" / "_meta.json").read_text()) if (DATA / "raw" / "_meta.json").exists() else {"categories": [], "tags": []}


def wp_cat_slug(cid):
    return next((c["slug"] for c in _META.get("categories") or [] if c["id"] == cid), None)


def wp_tag_slug(tid):
    return next((t["slug"] for t in _META.get("tags") or [] if t["id"] == tid), None)


# ---------------------------------------------------------------------------
# Sitemap, robots.txt, llms.txt
# ---------------------------------------------------------------------------
def build_sitemap(alt_pairs):
    urls = []
    for en, hu in alt_pairs:
        for loc in (en, hu):
            if not loc:
                continue
            links = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{BASE_URL}{u}"/>'
                            for c, u in (("en", en), ("hu", hu)) if u)
            urls.append(f"<url><loc>{BASE_URL}{loc}</loc>{links}</url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")
    write("/sitemap.xml", xml)
    if LIVE:
        robots = ("User-agent: *\nAllow: /\n\n"
                  "# AI search and assistants are welcome\n"
                  "User-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\n"
                  "User-agent: ClaudeBot\nAllow: /\nUser-agent: Claude-SearchBot\nAllow: /\n"
                  "User-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\n"
                  f"Sitemap: {BASE_URL}/sitemap.xml\n")
    else:
        robots = "# Test version – not for search engines. The real site is https://champagneclub.hu\nUser-agent: *\nDisallow: /\n"
    write("/robots.txt", robots)
    llms = [f"# {SITE['name']}", "",
            "> A private collection of champagne accessories – ice buckets, coolers, glasses, bar accessories and "
            "promotional pieces from the great champagne houses. Each piece has its own page in English and Hungarian. "
            "Prices are not published; enquiries about buying or selling go through the contact page.", "",
            "## Main pages",
            f"- [Collection]({BASE_URL}{PATHS['collection']['en']}): every piece, searchable by type, house, period, material and status",
            f"- [Champagne houses]({BASE_URL}{PATHS['houses']['en']}): the collection by maker",
            f"- [New arrivals]({BASE_URL}{PATHS['new']['en']})",
            f"- [Sold archive]({BASE_URL}{PATHS['sold']['en']})",
            f"- [Collectors' guide]({BASE_URL}{PATHS['guide']['en']}): history and advice",
            f"- [Contact]({BASE_URL}{PATHS['contact']['en']})", "",
            "## Types"]
    for t in SITE["types"]:
        if any(e["type"] == t["key"] for e in ITEMS):
            llms.append(f"- [{t['en']}]({BASE_URL}{type_path(t['key'], 'en')})")
    llms += ["", "## Hungarian version", f"- [Magyar főoldal]({BASE_URL}/hu/)", ""]
    write("/llms.txt", "\n".join(llms))


# ---------------------------------------------------------------------------
def clean_previous():
    if MANIFEST.exists():
        for rel in json.loads(MANIFEST.read_text()):
            p = ROOT / rel
            if p.is_file():
                p.unlink()
        # remove now-empty folders
        for rel in sorted({str(Path(r).parent) for r in json.loads(MANIFEST.read_text())}, key=len, reverse=True):
            d = ROOT / rel
            if d != ROOT and d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    for d in GENERATED_DIRS:
        shutil.rmtree(ROOT / d, ignore_errors=True)


def main():
    clean_previous()
    alt_pairs = []
    for lang in ("en", "hu"):
        build_home(lang)
        build_collection(lang)
        build_types(lang)
        build_houses(lang)
        new = new_arrivals(24)
        build_listing(lang, "new", PATHS["new"], S[lang]["new_title"], S[lang]["new_intro"], new)
        sold = [e for e in ITEMS if e["status"] == "sold"]
        build_listing(lang, "sold", PATHS["sold"], S[lang]["sold_title"], S[lang]["sold_intro"], sold)
        build_guide(lang)
        build_about(lang)
        build_contact(lang)
        build_legal(lang)
        for e in ITEMS:
            build_item(e, lang)
        for a in ARTICLES:
            if has_lang(a, lang):
                build_article(a, lang)
    build_404()
    redirects()
    for k in ("home", "collection", "houses", "new", "sold", "guide", "about", "contact"):
        alt_pairs.append((PATHS[k]["en"], PATHS[k]["hu"]))
    for t in SITE["types"]:
        if any(e["type"] == t["key"] for e in ITEMS):
            alt_pairs.append((type_path(t["key"], "en"), type_path(t["key"], "hu")))
    for k in {e["house"] for e in ITEMS if e.get("house")}:
        alt_pairs.append((house_path(k, "en"), house_path(k, "hu")))
    for e in ITEMS:
        alt_pairs.append((entry_path(e, "en"), entry_path(e, "hu")))
    for a in ARTICLES:
        alt_pairs.append((entry_path(a, "en") if has_lang(a, "en") else None, entry_path(a, "hu")))
    build_sitemap(alt_pairs)
    MANIFEST.write_text(json.dumps(sorted(set(OUT_FILES)), indent=0))
    print(f"Built {len(OUT_FILES)} files: {len(ITEMS)} items, {len(ARTICLES)} articles ({'LIVE' if LIVE else 'test'} build)")


if __name__ == "__main__":
    main()
