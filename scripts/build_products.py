#!/usr/bin/env python3
"""Generate static product pages (products/<sku>.html) from data/products.json.

Run from the repo root:  python3 scripts/build_products.py
Shared styles are taken from index.html so the pages always match the homepage.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://sophia-zhang101.github.io"
PHONE = "+86 135 8738 8738"

products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
index = (ROOT / "index.html").read_text(encoding="utf-8")
base_css = re.search(r"<style>(.*?)</style>", index, re.S).group(1)

PRODUCT_CSS = """
.crumbs{font-size:13px;letter-spacing:.1em;color:var(--mute);padding-top:28px}
.crumbs a{text-decoration:none;color:var(--mute)}.crumbs a:hover{color:var(--brand)}
.pd{display:grid;grid-template-columns:1.1fr 1fr;gap:64px;align-items:start;padding-top:28px;padding-bottom:104px}
.gal{display:flex;flex-direction:column;gap:14px;position:sticky;top:24px}
.gal-main{width:100%;aspect-ratio:1/1;object-fit:cover;background:#EEEDEB}
.thumbs{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}
.thumbs button{padding:0;border:1px solid transparent;background:#EEEDEB;cursor:pointer;line-height:0}
.thumbs button[aria-current="true"]{border-color:var(--ink)}
.thumbs button:focus-visible{outline:2px solid var(--brand);outline-offset:2px}
.thumbs img{aspect-ratio:1/1;object-fit:cover;width:100%}
.info{display:flex;flex-direction:column;gap:22px}
.info h1{font-size:clamp(38px,4.4vw,56px);line-height:1.08}
.info .zh{font-family:var(--serif);font-size:19px;color:var(--mute);letter-spacing:.16em;margin-top:-10px}
.tagline{font-family:var(--serif);font-style:italic;font-size:24px;line-height:1.4;color:var(--brand)}
.specs{margin:6px 0 0;display:grid;grid-template-columns:10em 1fr;border-top:1px solid var(--line)}
.specs dt,.specs dd{margin:0;padding:13px 0;border-bottom:1px solid var(--line);font-size:15px}
.specs dt{color:var(--mute);font-size:13px;letter-spacing:.1em;text-transform:uppercase;padding-top:15px}
.note{font-size:14px;color:var(--mute)}
.who{font-family:var(--serif);font-size:24px;line-height:1.45;max-width:34em}
.pd-values{grid-template-columns:repeat(3,minmax(0,1fr))}
.more{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:24px}
.more a{display:flex;flex-direction:column;gap:12px;text-decoration:none}
.more img{aspect-ratio:1/1;object-fit:cover;width:100%;background:#EEEDEB}
.more b{font-family:var(--serif);font-weight:500;font-size:21px;line-height:1.3}
.more span{font-size:13px;letter-spacing:.08em;color:var(--mute)}
.more span+span{margin-top:-10px}
.more a:hover b{color:var(--brand)}
@media (max-width:960px){.pd-values{grid-template-columns:1fr}.pd{grid-template-columns:1fr;gap:36px}.gal{position:static}.more{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:600px){.specs{grid-template-columns:1fr}.specs dt{border-bottom:0;padding-bottom:0}.thumbs{grid-template-columns:repeat(5,minmax(0,1fr))}}
"""

e = html.escape


def header():
    return """<div class="strip">A pearl family since 1976 · Shanxiahu, Zhuji — China&#39;s pearl heartland</div>
<header class="top">
  <div class="wrap">
    <a href="/" aria-label="XIAI JEWELRY home"><img src="/images/logo-horizontal.png" alt="XIAI JEWELRY 玺爱珠宝" width="238" height="46"></a>
    <nav aria-label="Main">
      <a href="/products">Jewelry</a>
      <a href="/#pearls">Pearls</a>
      <a href="/#story">Our Story</a>
      <a href="/#craft">Craft</a>
      <a href="/#partner">Partner</a>
      <a href="/#faq">FAQ</a>
      <a href="/#contact">Contact</a>
    </nav>
  </div>
</header>"""


def footer():
    return """<footer>
  <div class="wrap">
    <img src="/images/logo-horizontal.png" alt="XIAI JEWELRY 玺爱珠宝" width="198" height="38">
    <span>XIAI JEWELRY® is a brand of 诸暨市易承珍珠养殖有限公司 (Zhuji Yicheng Pearl Farming Co., Ltd.)</span>
    <span>© 2026 XIAI Jewelry</span>
  </div>
</footer>"""


def page(p):
    sku, name = p["sku"], p["name"]
    url = f"{SITE}/products/{sku}"
    photos = p["photos"]
    alt = lambda i: f"{name} (XIAI {sku}), view {i + 1} of {len(photos)}"

    thumbs = "\n".join(
        f'<button type="button" data-src="{src}" data-alt="{e(alt(i))}" aria-label="Show view {i + 1}"'
        f'{" aria-current=\"true\"" if i == 0 else ""}><img src="{src}" alt="" width="1400" height="1400" loading="lazy"></button>'
        for i, src in enumerate(photos)
    )
    specs = "\n".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in p["specs"])
    points = "\n".join(
        f'<div><span class="num">0{i + 1}</span><p>{e(t)}</p></div>' for i, t in enumerate(p["points"])
    )
    faq = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    same = [o for o in products if o["sku"] != sku and o["category"] == p["category"]]
    rest = [o for o in products if o["sku"] != sku and o["category"] != p["category"]]
    others = (same + rest)[:4]
    more = "\n".join(
        f'<a href="/products/{o["sku"]}"><img src="{o["photos"][0]}" alt="{e(o["name"])}" width="1400" height="1400" loading="lazy">'
        f'<b>{e(o["name"])}</b><span>{e(o["category"])} · No. {o["sku"]}</span></a>'
        for o in others
    )

    product_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "alternateName": p["name_zh"],
        "sku": sku,
        "category": p["category"],
        "description": p["description"],
        "image": [SITE + s for s in photos],
        "brand": {"@type": "Brand", "name": "XIAI JEWELRY"},
        "manufacturer": {"@type": "Organization", "name": "诸暨市易承珍珠养殖有限公司"},
        "url": url,
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]
        ],
    }
    crumbs_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "All jewelry", "item": SITE + "/products"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url},
        ],
    }
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
        for x in (product_ld, faq_ld, crumbs_ld)
    )
    title = f"{name} · No. {sku} · XIAI JEWELRY"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(p['description'])}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" href="/images/favicon.png">
<meta property="og:type" content="product">
<meta property="og:site_name" content="XIAI JEWELRY">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(p['tagline'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{photos[0]}">
<link rel="preload" href="/fonts/cormorant-garamond-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/jost-latin-300-normal.woff2" as="font" type="font/woff2" crossorigin>
{ld}
<style>{base_css}{PRODUCT_CSS}</style>
</head>
<body>
{header()}
<main>
<div class="wrap">
  <p class="crumbs"><a href="/">Home</a> / <a href="/products">All jewelry</a> / <a href="/products#{p['category'].lower()}">{e(p['category'])}</a> / {e(name)}</p>
  <div class="pd">
    <div class="gal">
      <img class="gal-main" id="gal-main" src="{photos[0]}" alt="{e(alt(0))}" width="1400" height="1400" fetchpriority="high">
      <div class="thumbs">
{thumbs}
      </div>
    </div>
    <div class="info">
      <p class="eyebrow">{e(p['category'])} · No. {sku}</p>
      <h1>{e(name)}</h1>
      <p class="zh">{e(p['name_zh'])}</p>
      <p class="tagline">{e(p['tagline'])}</p>
      <p class="lead">{e(p['description'])}</p>
      <dl class="specs">
{specs}
      </dl>
      <div class="hero-ctas">
        <a class="btn solid" href="/#contact">Enquire about No. {sku}</a>
        <a class="btn line" href="tel:{PHONE.replace(' ', '')}">Call {PHONE}</a>
      </div>
      <p class="note">Please quote item no. {sku} when you get in touch. Sizes, availability and prices are confirmed for each enquiry — retail, wholesale and custom orders welcome.</p>
    </div>
  </div>
</div>

<section class="sec panel">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Why this piece</p><h2 class="h2">The details</h2></div></div>
    <div class="values pd-values">
{points}
    </div>
    <p class="who" style="margin-top:56px">{e(p['for'])}</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Questions</p><h2 class="h2">About No. {sku}</h2></div></div>
    <div class="faq">
{faq}
    </div>
  </div>
</section>

<section class="sec panel">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">Keep exploring</p><h2 class="h2">More from the collection</h2></div><a class="textlink" href="/products">All jewelry</a></div>
    <div class="more">
{more}
    </div>
  </div>
</section>
</main>
{footer()}
<script>
(function(){{
  var main=document.getElementById('gal-main');
  document.querySelectorAll('.thumbs button').forEach(function(b){{
    b.addEventListener('click',function(){{
      main.src=b.dataset.src;main.alt=b.dataset.alt;
      document.querySelectorAll('.thumbs button').forEach(function(x){{x.removeAttribute('aria-current')}});
      b.setAttribute('aria-current','true');
    }});
  }});
}})();
</script>
</body>
</html>
"""


CATS = [
    ("Necklaces", "Strands, single pearls, long lines and layered pieces — saltwater and freshwater."),
    ("Pendants", "A single pearl, ready for a chain you choose."),
    ("Earrings", "Studs, drops and hoops — from fine freshwater pearls to large South Sea and Tahitian pearls."),
    ("Rings", "Single, double and three-pearl designs in gold and sterling silver."),
    ("Bracelets", "Pearls spaced along gold links, for the wrist."),
    ("Brooches", "Sculptural pieces for a lapel, a shawl or a coat."),
]


def short(p):
    d = dict(p["specs"])
    size = d.get("Pearl size") or ""
    metal = (d.get("Metal") or "").split(",")[0].replace(" fittings", "")
    return " · ".join(x for x in (size, metal) if x)


def overview():
    sections, items, n = [], [], 0
    for cat, blurb in CATS:
        ps = [p for p in products if p["category"] == cat]
        if not ps:
            continue
        cards = []
        for p in ps:
            n += 1
            items.append({"@type": "ListItem", "position": n, "url": f"{SITE}/products/{p['sku']}", "name": p["name"]})
            cards.append(
                f'<a href="/products/{p["sku"]}"><img src="{p["photos"][0]}" alt="{e(p["name"])} (XIAI {p["sku"]})" width="1400" height="1400" loading="lazy">'
                f'<b>{e(p["name"])}</b><span>{e(short(p))}</span><span>No. {p["sku"]}</span></a>'
            )
        sections.append(f"""<section class="sec cat-sec" id="{cat.lower()}">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow">{len(ps)} piece{'s' if len(ps) > 1 else ''}</p><h2 class="h2">{cat}</h2></div><p class="lead" style="max-width:26em">{e(blurb)}</p></div>
    <div class="more">
{chr(10).join(cards)}
    </div>
  </div>
</section>""")
    jump = " ".join(f'<a href="#{c.lower()}">{c}</a>' for c, _ in CATS if any(p["category"] == c for p in products))
    ld = json.dumps({"@context": "https://schema.org", "@type": "ItemList", "name": "XIAI JEWELRY pearl jewelry", "itemListElement": items}, ensure_ascii=False)
    desc = "All XIAI pearl jewelry: necklaces, pendants, earrings, rings, bracelets and brooches with South Sea, Tahitian, Akoya and freshwater pearls, from Shanxiahu, Zhuji."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Pearl Jewelry · XIAI JEWELRY</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/products">
<link rel="icon" type="image/png" href="/images/favicon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="XIAI JEWELRY">
<meta property="og:title" content="All Pearl Jewelry · XIAI JEWELRY">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}/products">
<meta property="og:image" content="{SITE}{products[0]['photos'][0]}">
<link rel="preload" href="/fonts/cormorant-garamond-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/jost-latin-300-normal.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">{ld}</script>
<style>{base_css}{PRODUCT_CSS}
.jump{{display:flex;gap:10px 28px;flex-wrap:wrap;font-size:14px;letter-spacing:.12em;text-transform:uppercase;padding:22px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:36px}}
.jump a{{text-decoration:none}}
.cat-sec{{padding:72px 0}}.cat-sec+.cat-sec{{border-top:1px solid var(--line)}}
</style>
</head>
<body>
{header()}
<main>
<div class="wrap" style="padding-top:28px">
  <p class="crumbs" style="padding-top:0"><a href="/">Home</a> / All jewelry</p>
  <p class="eyebrow" style="margin-top:40px">The collection · {len(products)} pieces</p>
  <h1 style="font-size:clamp(40px,5vw,68px);line-height:1.08;margin-top:14px">All pearl jewelry</h1>
  <p class="lead" style="margin-top:20px">Every piece below has its own page with more photos, the pearl and metal details, and answers to common questions. Sizes, availability and prices are confirmed for each enquiry.</p>
  <nav class="jump" aria-label="Categories">{jump}</nav>
</div>
{chr(10).join(sections)}
</main>
{footer()}
</body>
</html>
"""


out = ROOT / "products"
out.mkdir(exist_ok=True)
for p in products:
    (out / f"{p['sku']}.html").write_text(page(p), encoding="utf-8")
    print("built", f"products/{p['sku']}.html")
(out / "index.html").write_text(overview(), encoding="utf-8")
print("built products/index.html")

# keep sitemap in step with the pages
urls = [f"{SITE}/", f"{SITE}/products"] + [f"{SITE}/products/{p['sku']}" for p in products]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
print("updated sitemap.xml with", len(urls), "urls")
