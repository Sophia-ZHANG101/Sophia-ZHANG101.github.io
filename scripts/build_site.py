#!/usr/bin/env python3
"""Build the whole XIAI JEWELRY site from data/products.json.

Run from the repo root:   python3 scripts/build_site.py

Writes: index.html, products/index.html, products/<category>.html,
products/<sku>.html, pearl-guide.html, our-story.html, wholesale.html,
contact.html, 404.html and sitemap.xml. Styles live in assets/site.css and
behaviour in assets/site.js; edit those files directly.

Every product shown anywhere comes from data/products.json (the client's SKU
sheet). AI campaign images are listed in CAMPAIGN below and are only used for
pieces that exist in that file.
"""
import hashlib
import html
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://sophia-zhang101.github.io"
PHONE = "+86 135 8738 8738"
TEL = "+8613587388738"
COMPANY = "诸暨市易承珍珠养殖有限公司 (Zhuji Yicheng Pearl Farming Co., Ltd.)"
ADDRESS = "XIAI Jewelry Creative Park, Building 2, Yunshan Jinfu, Shanxiahu Town, Zhuji, Zhejiang, China"
ADDRESS_ZH = "浙江省诸暨市山下湖镇云山金府2幢玺爱珠宝创意园"

e = html.escape
products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
BY_SKU = {p["sku"]: p for p in products}


def ver(path):
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]


CSS_V, JS_V = ver("assets/site.css"), ver("assets/site.js")


def size(src):
    """Width/height attributes for a site-relative image path."""
    with Image.open(ROOT / src.lstrip("/")) as im:
        return im.size


# ---------------------------------------------------------------- data -----
# Pearl types per item, from the pearl column of the SKU sheet.
PEARLS = {
    "golden": dict(name="Golden pearls", short="Golden", img="/images/products/33187/33187-01.jpg",
                   skus="13162 13165 13210 14121 23183 33168 33187 43018 52018 53070 62021 63034 63061 73069 73081"),
    "white": dict(name="White South Sea pearls", short="White South Sea", img="/images/products/62038/62038-01.jpg",
                  skus="14121 32089 44020 52018 62038"),
    "tahitian": dict(name="Tahitian pearls", short="Tahitian", img="/images/products/34115/34115-01.jpg",
                     skus="14103 14121 14157 14164 14174 34108 34115 44020 54057 64048 64053 74021"),
    "akoya": dict(name="Akoya pearls", short="Akoya", img="/images/products/66055/66055-01.jpg",
                  skus="14121 14164 14174 44020 66055"),
    "freshwater": dict(name="Freshwater pearls", short="Freshwater", img="/images/products/11508/11508-01.jpg",
                       skus="11508 31335 31349"),
}
for k in PEARLS:
    PEARLS[k]["skus"] = PEARLS[k]["skus"].split()
    n = PEARLS[k]["name"]
    PEARLS[k]["lower"] = n[0].lower() + n[1:] if k in ("golden", "white", "freshwater") else n
for p in products:
    p["pearls"] = [k for k, v in PEARLS.items() if p["sku"] in v["skus"]]
    assert p["pearls"], f"no pearl type for {p['sku']}"
for k, v in PEARLS.items():
    for s in v["skus"]:
        assert s in BY_SKU, f"pearl list names unknown item {s}"

CATEGORIES = [
    dict(slug="necklaces", name="Necklaces", tile="/images/products/14174/14174-01.jpg",
         blurb="Strands, single pearls, long lines and layered pieces, in saltwater and freshwater pearls."),
    dict(slug="earrings", name="Earrings", tile="/images/products/33187/33187-01.jpg", head="/images/products/34115/34115-02.jpg",
         blurb="Studs, drops and hoops that frame the face, from fine freshwater pearls to large golden and Tahitian pearls."),
    dict(slug="rings", name="Rings", tile="/images/products/64048/64048-01.jpg",
         blurb="Single, double and three-pearl rings. Ring sizes are confirmed for each piece before you order."),
    dict(slug="bracelets", name="Bracelets", tile="/images/products/52018/52018-01.jpg", head="/images/products/52018/52018-02.jpg",
         blurb="Multi-row bangles and a station bracelet, with golden, white and Tahitian pearls."),
    dict(slug="pendants", name="Pendants", tile="/images/products/23183/23183-01.jpg", head="/images/products/23183/23183-03.jpg",
         blurb="A single golden pearl, ready for a chain you already own."),
    dict(slug="brooches", name="Brooches", tile="/images/products/73081/73081-01.jpg", head="/images/products/73081/73081-02.jpg",
         blurb="Sculptural pieces that lift a jacket, a knit or a scarf."),
]
CAT_BY_NAME = {c["name"]: c for c in CATEGORIES}
SINGULAR = {"Necklaces": "Necklace", "Earrings": "Earrings", "Rings": "Ring", "Bracelets": "Bracelet",
            "Pendants": "Pendant", "Brooches": "Brooch"}
for c in CATEGORIES:
    c["items"] = [p for p in products if p["category"] == c["name"]]
    assert c["items"], c["name"]

# AI-generated campaign images (Canva, made with photos of the real piece as
# reference). Each must name a real item; delete an entry to drop the image.
CAMPAIGN = {
    "hero": dict(src="/images/campaign/hero-33168.jpg", sku="33168"),
    "mixed": dict(src="/images/campaign/mixed-14121.jpg", sku="14121"),
    "ring": dict(src="/images/campaign/ring-63034.jpg", sku="63034"),
}
CAMPAIGN = {k: v for k, v in CAMPAIGN.items() if (ROOT / v["src"].lstrip("/")).exists()}
for v in CAMPAIGN.values():
    assert v["sku"] in BY_SKU, v
WORN = {v["sku"]: v for v in CAMPAIGN.values()}
CAT_HEAD_CAMPAIGN = {"Necklaces": "mixed", "Rings": "ring"}
AI_NOTE = ("Model photographs on this site are AI-generated from photos of our real pieces. "
           "Product pages show the actual jewellery.")


def metal(p):
    m = dict(p["specs"]).get("Metal", "")
    for cut in (",", " (", " —"):
        m = m.split(cut)[0]
    return m.replace(" fittings", "")


def plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


# ------------------------------------------------------------ chrome ------
def head(title, desc, path, image, ld=()):
    url = SITE + path
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" href="/images/favicon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="XIAI JEWELRY">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/cormorant-garamond-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/jost-latin-300-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={CSS_V}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def header(current=""):
    def cur(key):
        return ' aria-current="page"' if current == key else ""

    cats = "\n".join(f'<li><a href="/products/{c["slug"]}">{c["name"]}</a></li>' for c in CATEGORIES)
    pearls = "\n".join(f'<li><a href="/pearl-guide#{k}">{v["name"]}</a></li>' for k, v in PEARLS.items())
    fig = ""
    if "mixed" in CAMPAIGN:
        fig = f"""<figure><img src="{CAMPAIGN['mixed']['src']}" alt="Model wearing the Mixed Saltwater Pearl Necklace" width="400" height="500" loading="lazy">
          <figcaption>Why choose one colour?<a class="ul" href="/products/14121">See the necklace</a></figcaption></figure>"""
    drawer_cats = "\n".join(f'<li><a href="/products/{c["slug"]}">{c["name"]}</a></li>' for c in CATEGORIES)
    return f"""
<div class="bar">From Shanxiahu, the heart of China&#39;s pearl industry. Enquiries welcome from anywhere.</div>
<header class="site-header">
  <div class="wrap mast">
    <div class="mast-side">
      <button class="menu-btn" type="button" aria-controls="drawer" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg>Menu</button>
    </div>
    <a class="logo" href="/" aria-label="XIAI JEWELRY home"><img src="/images/logo-horizontal.png" alt="XIAI JEWELRY 玺爱珠宝" width="238" height="46"></a>
    <div class="mast-side end">
      <a class="hide-sm" href="tel:{TEL}">{PHONE}</a>
      <a class="ul" href="/contact">Enquire</a>
    </div>
  </div>
  <nav class="mainnav" aria-label="Main">
    <ul>
      <li class="has-mega{' is-current' if current == 'jewellery' else ''}">
        <button type="button" aria-expanded="false" aria-controls="mega-jewellery">Jewellery</button>
        <div class="mega" id="mega-jewellery">
          <div class="wrap">
            <div><h2>Jewellery</h2><ul><li><a href="/products">All jewellery</a></li>
{cats}</ul></div>
            <div><h2>Shop by pearl</h2><ul>
{pearls}</ul></div>
            {fig}
          </div>
        </div>
      </li>
      <li><a href="/pearl-guide"{cur('guide')}>Pearl guide</a></li>
      <li><a href="/our-story"{cur('story')}>Our story</a></li>
      <li><a href="/wholesale"{cur('wholesale')}>Wholesale &amp; custom</a></li>
      <li><a href="/contact"{cur('contact')}>Contact</a></li>
    </ul>
  </nav>
</header>
<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer-top"><img src="/images/logo-horizontal.png" alt="XIAI JEWELRY" width="176" height="34"><button class="drawer-close" type="button">Close</button></div>
  <nav aria-label="Mobile">
    <h2>Jewellery</h2>
    <ul><li><a href="/products">All jewellery</a></li>
{drawer_cats}</ul>
    <h2>XIAI</h2>
    <ul><li><a href="/pearl-guide">Pearl guide</a></li><li><a href="/our-story">Our story</a></li><li><a href="/wholesale">Wholesale &amp; custom</a></li><li><a href="/contact">Contact</a></li></ul>
    <p class="contact-mini">Call or WeChat <a href="tel:{TEL}">{PHONE}</a></p>
  </nav>
</div>
<main id="main">"""


def footer():
    cats = "\n".join(f'<li><a href="/products/{c["slug"]}">{c["name"]}</a></li>' for c in CATEGORIES)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot">
      <div class="brand">
        <img src="/images/logo-horizontal.png" alt="XIAI JEWELRY 玺爱珠宝" width="218" height="42" loading="lazy">
        <p>Saltwater and freshwater pearl jewellery from Shanxiahu, Zhuji. A pearl family since 1976.</p>
      </div>
      <div><h2>Jewellery</h2><ul><li><a href="/products">All jewellery</a></li>
{cats}</ul></div>
      <div><h2>XIAI</h2><ul><li><a href="/pearl-guide">Pearl guide</a></li><li><a href="/our-story">Our story</a></li><li><a href="/wholesale">Wholesale &amp; custom</a></li><li><a href="/contact">Contact &amp; FAQ</a></li></ul></div>
      <div><h2>Get in touch</h2><ul><li>Mr. Chen (玺爱哥)</li><li><a href="tel:{TEL}">{PHONE}</a></li><li><a href="/contact#wechat">WeChat</a></li><li>Shanxiahu Town, Zhuji, China</li></ul></div>
    </div>
    <div class="legal">
      <p>XIAI JEWELRY® is a brand of {COMPANY}. {AI_NOTE}</p>
      <p>© 2026 XIAI Jewelry</p>
    </div>
  </div>
</footer>
<script src="/assets/site.js?v={JS_V}" defer></script>
</body>
</html>
"""


def card(p, lazy=True):
    a, b = p["photos"][0], p["photos"][1] if len(p["photos"]) > 1 else None
    w, h = size(a)
    alt_img = f'<img class="alt" src="{b}" alt="" width="{w}" height="{h}" loading="lazy">' if b else ""
    return (f'<a class="card" href="/products/{p["sku"]}" data-pearls="{" ".join(p["pearls"])}">'
            f'<div class="ph"><img src="{a}" alt="{e(p["name"])}, item {p["sku"]}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else ""}>{alt_img}</div>'
            f'<h3>{e(p["name"])}</h3><p class="meta">{e(metal(p))}&ensp;&ensp;No. {p["sku"]}</p></a>')


def grid(items, lazy=True):
    return '<div class="grid">\n' + "\n".join(card(p, lazy) for p in items) + "\n</div>"


def filters(items):
    present = [(k, v) for k, v in PEARLS.items() if any(k in p["pearls"] for p in items)]
    if len(present) < 2:
        return f'<div class="filters"><span class="note" id="shown">{plural(len(items), "piece")}</span></div>'
    chips = "".join(
        f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{v["short"]} <span class="n">{sum(k in p["pearls"] for p in items)}</span></button>'
        for k, v in present)
    return (f'<div class="filters" role="group" aria-label="Filter by pearl"><span class="label">Pearl</span>'
            f'<button class="chip" type="button" data-filter="all" aria-pressed="true">All <span class="n">{len(items)}</span></button>{chips}'
            f'<span class="note" id="shown" aria-live="polite" style="margin-left:auto">{plural(len(items), "piece")}</span></div>')


def wearing(key):
    c = CAMPAIGN[key]
    p = BY_SKU[c["sku"]]
    return f'<p class="wearing">Wearing <a href="/products/{p["sku"]}">{e(p["name"])}</a>, no. {p["sku"]}. AI-generated image.</p>'


def crumbs(*parts):
    out = ['<a href="/">Home</a>']
    for label, href in parts:
        out.append(f'<a href="{href}">{e(label)}</a>' if href else e(label))
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(out) + "</nav>"


def write(rel, text):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("built", rel)


# ------------------------------------------------------------- pages ------
def home():
    edit = [BY_SKU[s] for s in "33187 34115 14174 52018 64048 73081 32089 13210".split()]
    tiles = "\n".join(
        f'<a class="tile" href="/products/{c["slug"]}"><img src="{c["tile"]}" alt="" width="1400" height="1400" loading="lazy"><span>{c["name"]}<small>{plural(len(c["items"]), "piece")}</small></span></a>'
        for c in CATEGORIES)
    pearls = "\n".join(
        f'<a href="/pearl-guide#{k}"><img src="{v["img"]}" alt="" width="400" height="400" loading="lazy"><b>{v["name"]}</b><span>{plural(len(v["skus"]), "piece")}</span></a>'
        for k, v in PEARLS.items())

    hero = ""
    if "hero" in CAMPAIGN:
        w, h = size(CAMPAIGN["hero"]["src"])
        hero = f"""<section class="hero" aria-label="Introduction">
  <div class="wrap">
    <div class="hero-media"><img src="{CAMPAIGN['hero']['src']}" alt="Model wearing XIAI cream-gold pearl drop earrings" width="{w}" height="{h}" fetchpriority="high"></div>
    <div class="hero-copy">
      <h1>Because it&rsquo;s XiAi, it&rsquo;s love at first&nbsp;sight.</h1>
      <p class="sub">Golden, white and Tahitian pearls, chosen at the source in Shanxiahu and set in gold and silver.</p>
      <div class="btns"><a class="btn fill" href="/products">Discover the collection</a></div>
    </div>
    {wearing('hero')}
  </div>
</section>"""

    if not hero:  # no campaign image yet: text beside a real product photo
        hp = BY_SKU["33168"]
        w, h = size(hp["photos"][0])
        hero = f"""<section class="hero" aria-label="Introduction">
  <div class="wrap"><div class="hero-split">
    <div class="hero-copy-alt">
      <h1>Because it&rsquo;s XiAi, it&rsquo;s love at first&nbsp;sight.</h1>
      <p class="sub">Golden, white and Tahitian pearls, chosen at the source in Shanxiahu and set in gold and silver.</p>
      <div class="btns"><a class="btn fill" href="/products">Discover the collection</a></div>
    </div>
    <a class="hero-product" href="/products/{hp['sku']}"><img src="{hp['photos'][0]}" alt="{e(hp['name'])}, item {hp['sku']}" width="{w}" height="{h}" fetchpriority="high"><span>{e(hp['name'])}, no. {hp['sku']}</span></a>
  </div></div>
</section>"""

    duo = ""
    if "tahitian" in CAMPAIGN and "long" in CAMPAIGN:
        duo = f"""<section class="sec" aria-label="Campaign">
  <div class="wrap duo">
    <article class="story">
      <img src="{CAMPAIGN['tahitian']['src']}" alt="Model in a black turtleneck wearing grey Tahitian pearl drop earrings" width="1080" height="1350" loading="lazy">
      <h3>Tahitian, in soft grey</h3>
      <p>Platinum-grey Tahitian pearls under a small interlaced top. Quiet enough for every day, with a turtleneck or a white shirt.</p>
      <a class="ul" href="/pearl-guide#tahitian">Explore Tahitian pearls</a>
      {wearing('tahitian')}
    </article>
    <article class="story">
      <img src="{CAMPAIGN['long']['src']}" alt="Model in a cream knit wearing a long golden pearl necklace" width="1080" height="1350" loading="lazy">
      <h3>Worn long</h3>
      <p>An 85 cm line of golden pearls and small gold beads that falls over knitwear, tailoring and dresses.</p>
      <a class="ul" href="/products/43018">See the necklace</a>
      {wearing('long')}
    </article>
  </div>
</section>"""

    mixed = ""
    if "mixed" in CAMPAIGN:
        mixed = f"""<section class="split" aria-label="Mixed pearls">
  <div class="media"><img src="{CAMPAIGN['mixed']['src']}" alt="Model in a white shirt wearing a necklace of mixed saltwater pearls" width="1080" height="1350" loading="lazy"></div>
  <div class="copy">
    <h2>Why choose one colour?</h2>
    <p>Tahitian, golden, white South Sea and Akoya pearls in varied sizes on one fine 18K gold chain, in 43 cm or 46 cm.</p>
    <div class="btns"><a class="btn" href="/products/14121">See the necklace</a></div>
    {wearing('mixed')}
  </div>
</section>"""

    ring = ""
    if "ring" in CAMPAIGN:
        ring = f"""<section class="split rev lilac" aria-label="Rings">
  <div class="media"><img src="{CAMPAIGN['ring']['src']}" alt="Hand on a camel coat wearing a golden pearl ring" width="1080" height="1350" loading="lazy"></div>
  <div class="copy">
    <h2>A golden pearl, close up</h2>
    <p>A 12–13 mm golden pearl inside a swirl of small stones. See all seven rings, from a three-pearl Akoya band to Tahitian statement pieces.</p>
    <div class="btns"><a class="btn" href="/products/rings">Shop rings</a><a class="btn" href="/products/63034">See this ring</a></div>
    {wearing('ring')}
  </div>
</section>"""

    ld = [{
        "@context": "https://schema.org", "@type": "JewelryStore", "@id": SITE + "/#store",
        "name": "XIAI JEWELRY", "alternateName": ["玺爱珠宝", "Xiai Jewelry"],
        "slogan": "Because it’s XiAi, it’s love at first sight. 因为玺爱，所以喜爱",
        "url": SITE + "/", "logo": SITE + "/images/logo-vertical.png", "image": SITE + "/images/showroom.jpg",
        "description": "Pearl jewellery brand in Shanxiahu, Zhuji, offering golden, white South Sea, Tahitian, Akoya and freshwater pearl necklaces, earrings, rings, bracelets, pendants and brooches, plus wholesale and custom orders.",
        "telephone": PHONE,
        "address": {"@type": "PostalAddress", "streetAddress": "XIAI Jewelry Creative Park, Building 2, Yunshan Jinfu",
                    "addressLocality": "Shanxiahu Town, Zhuji", "addressRegion": "Zhejiang", "addressCountry": "CN"},
        "parentOrganization": {"@type": "Organization", "name": "诸暨市易承珍珠养殖有限公司", "alternateName": "Zhuji Yicheng Pearl Farming Co., Ltd."},
        "foundingDate": "2010",
        "memberOf": {"@type": "Organization", "name": "Zhejiang Pearl Industry Association"},
    }]
    og = CAMPAIGN["hero"]["src"] if "hero" in CAMPAIGN else edit[0]["photos"][0]
    body = f"""{hero}
<section class="sec" aria-labelledby="edit-h">
  <div class="wrap">
    <div class="head"><h2 id="edit-h">The edit</h2><p>A few pieces to start with. Every one has its own page with real photos and details.</p></div>
    {grid(edit)}
    <div class="after"><a class="btn" href="/products">View all {len(products)} pieces</a></div>
  </div>
</section>
<section class="band" aria-labelledby="find-h">
  <div class="wrap">
    <div class="head"><h2 id="find-h">Find your pearl</h2><p>From everyday studs to statement rings and brooches.</p></div>
    <div class="tiles">
{tiles}
    </div>
  </div>
</section>
{duo}
{mixed}
{ring}
<section class="sec" aria-labelledby="types-h">
  <div class="wrap">
    <div class="head"><h2 id="types-h">Know your pearls</h2><p>Saltwater first, freshwater too. Learn what makes each pearl different, then see the pieces made with it.</p></div>
    <div class="pearls">
{pearls}
    </div>
    <div class="after"><a class="btn" href="/pearl-guide">Read the pearl guide</a></div>
  </div>
</section>
<section class="split plain" aria-labelledby="roots-h">
  <div class="media"><img src="/images/farm-lake.jpg" alt="Pearl farm on a lake near Zhuji" width="1800" height="1200" loading="lazy"></div>
  <div class="copy">
    <h2 id="roots-h">Rooted in Shanxiahu since 1976</h2>
    <p>Our family began working with pearls in 1976. Today XIAI works within the Shanxiahu pearl belt, close to farming, harvesting, grading and raw pearl supply, with a showroom in Zhuji.</p>
    <div class="btns"><a class="btn" href="/our-story">Our story</a></div>
  </div>
</section>
<section class="sec dark" aria-labelledby="trade-h">
  <div class="wrap trade">
    <div>
      <h2 id="trade-h">For retailers, creators and custom projects</h2>
      <ul>
        <li><b>Wholesale &amp; channel supply</b><span>Steady stock, product selection support and reliable delivery.</span></li>
        <li><b>Livestream partnerships</b><span>Product selection for creators and on-site livestream support.</span></li>
        <li><b>Custom &amp; bespoke</b><span>Pearls selected for you and designs made to your brief.</span></li>
      </ul>
      <a class="btn on-dark" href="/wholesale">Work with us</a>
    </div>
    <img src="/images/display.jpg" alt="Trays of pearl jewellery in the XIAI showroom" width="1200" height="675" loading="lazy">
  </div>
</section>
<section class="sec" aria-label="Services">
  <div class="wrap services">
    <div><h3>Ask about any piece</h3><p>Send us the item number. We are happy to share extra photos or videos, sizes and the price.</p><a class="ul" href="/contact">Contact us</a></div>
    <div><h3>Made to order</h3><p>Pearls selected for you and designs made to your brief. Costs and delivery are confirmed order by order.</p><a class="ul" href="/wholesale#custom">Custom orders</a></div>
    <div><h3>Visit the showroom</h3><p>See and choose pieces in person at our creative park in Shanxiahu, Zhuji.</p><a class="ul" href="/our-story#showroom">The showroom</a></div>
    <div><h3>Certificates</h3><p>Before you buy, we confirm which certificate comes with the piece and which after-sales terms apply.</p><a class="ul" href="/contact#faq">Read the FAQ</a></div>
  </div>
</section>"""
    return (head("XIAI JEWELRY · Golden, Tahitian and South Sea Pearl Jewellery from Shanxiahu",
                 "Pearl jewellery from Shanxiahu, Zhuji: golden, white South Sea, Tahitian, Akoya and freshwater pearl necklaces, earrings, rings, bracelets and brooches. Enquiries welcome worldwide.",
                 "/", og, ld) + header("home") + body + footer())


def listing(cat=None):
    items = cat["items"] if cat else products
    chips = "".join(
        f'<a class="chip" href="/products/{c["slug"]}"{" aria-current=\"page\"" if cat and c is cat else ""}>{c["name"]} <span class="n">{len(c["items"])}</span></a>'
        for c in CATEGORIES)
    allchip = f'<a class="chip" href="/products"{"" if cat else " aria-current=\"page\""}>All <span class="n">{len(products)}</span></a>'
    if cat:
        key = CAT_HEAD_CAMPAIGN.get(cat["name"])
        if key in CAMPAIGN:
            img, alt, note = CAMPAIGN[key]["src"], f"{cat['name']} by XIAI, as worn", wearing(key)
        else:
            img, alt, note = cat.get("head", cat["tile"]), f"{cat['name']} by XIAI", ""
        w, h = size(img)
        top = f"""<div class="wrap">
  {crumbs(('Jewellery', '/products'), (cat['name'], None))}
  <div class="cat-head">
    <div><h1>{cat['name']}</h1><p class="sub">{e(cat['blurb'])}</p><p class="count">{plural(len(items), 'piece')}. Prices, sizes and availability are confirmed when you enquire.</p></div>
    <figure><img src="{img}" alt="{e(alt)}" width="{w}" height="{h}" fetchpriority="high">{note}</figure>
  </div>
</div>"""
        title = f"Pearl {cat['name']} · XIAI JEWELRY"
        desc = f"XIAI pearl {cat['name'].lower()}: {cat['blurb']}"
        path = f"/products/{cat['slug']}"
    else:
        top = f"""<div class="wrap">
  {crumbs(('Jewellery', None))}
  <div class="page-head"><h1>All jewellery</h1><p class="sub">{len(products)} pieces with golden, white South Sea, Tahitian, Akoya and freshwater pearls. Prices, sizes and availability are confirmed when you enquire.</p></div>
</div>"""
        title, path = "All Pearl Jewellery · XIAI JEWELRY", "/products"
        desc = f"All {len(products)} XIAI pieces: pearl necklaces, earrings, rings, bracelets, pendants and brooches from Shanxiahu, Zhuji."
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": title,
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/products/{p['sku']}", "name": p["name"]} for i, p in enumerate(items)]}]
    body = f"""{top}
<section class="wrap" style="padding-bottom:112px" aria-label="Pieces">
  <nav class="filters" aria-label="Categories" style="border-bottom:0;margin-bottom:0;padding-bottom:0">{allchip}{chips}</nav>
  {filters(items)}
  {grid(items, lazy=False)}
</section>"""
    return head(title, desc, path, items[0]["photos"][0], ld) + header("jewellery") + body + footer()


def product(p):
    sku, name, photos = p["sku"], p["name"], p["photos"]
    cat = CAT_BY_NAME[p["category"]]
    w, h = size(photos[0])
    alt = lambda i: f"{name} (XIAI {sku}), photo {i + 1} of {len(photos)}"
    thumbs = "\n".join(
        f'<button type="button" data-src="{src}" data-alt="{e(alt(i))}" aria-label="Show photo {i + 1}"'
        f'{" aria-current=\"true\"" if i == 0 else ""}><img src="{src}" alt="" width="{w}" height="{h}" loading="lazy"></button>'
        for i, src in enumerate(photos))
    specs = "\n".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in p["specs"])
    points = "\n".join(f"<li>{e(t)}</li>" for t in p["points"])
    faq = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    same = [o for o in products if o["sku"] != sku and o["category"] == p["category"]]
    rest = [o for o in products if o["sku"] != sku and o["category"] != p["category"] and set(o["pearls"]) & set(p["pearls"])]
    others = (same + rest)[:4]
    worn = ""
    if sku in WORN:
        worn = f"""<section class="sec tight" aria-labelledby="worn-h">
  <div class="wrap worn">
    <img src="{WORN[sku]['src']}" alt="Model wearing the {e(name)}" width="1080" height="1350" loading="lazy">
    <div><h2 id="worn-h">As worn</h2><p>{e(p['for'])}</p><p class="ai">AI-generated image, made with photos of this piece. The photos above show the actual jewellery.</p></div>
  </div>
</section>"""
    pearl_links = ", ".join(f'<a href="/pearl-guide#{k}">{PEARLS[k]["lower"]}</a>' for k in p["pearls"])
    ld = [
        {"@context": "https://schema.org", "@type": "Product", "name": name, "alternateName": p["name_zh"], "sku": sku,
         "category": p["category"], "description": p["description"], "image": [SITE + s for s in photos],
         "brand": {"@type": "Brand", "name": "XIAI JEWELRY"},
         "manufacturer": {"@type": "Organization", "name": "诸暨市易承珍珠养殖有限公司"}, "url": f"{SITE}/products/{sku}"},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": cat["name"], "item": f"{SITE}/products/{cat['slug']}"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE}/products/{sku}"}]},
    ]
    body = f"""<div class="wrap">
  {crumbs(('Jewellery', '/products'), (cat['name'], f"/products/{cat['slug']}"), (name, None))}
  <div class="pd">
    <div class="gal">
      <img class="gal-main" id="gal-main" src="{photos[0]}" alt="{e(alt(0))}" width="{w}" height="{h}" fetchpriority="high">
      <div class="thumbs">
{thumbs}
      </div>
    </div>
    <div class="info">
      <p class="kicker">{SINGULAR[cat['name']]}, item no. {sku}</p>
      <h1>{e(name)}</h1>
      <p class="zh" lang="zh">{e(p['name_zh'])}</p>
      <p class="tagline">{e(p['tagline'])}</p>
      <p class="desc">{e(p['description'])}</p>
      <dl class="specs">
{specs}
      </dl>
      <div class="btns"><a class="btn fill" href="/contact?item={sku}">Enquire about this piece</a><a class="btn" href="tel:{TEL}">Call {PHONE}</a></div>
      <p class="note">Quote item no. {sku} when you get in touch. Sizes, availability and the price are confirmed for each enquiry. Made with {pearl_links}.</p>
    </div>
  </div>
</div>
{worn}
<section class="sec tight" aria-labelledby="details-h" style="background:var(--rose)">
  <div class="wrap">
    <div class="head" style="margin-bottom:40px"><h2 id="details-h">The details</h2></div>
    <ul class="points">
{points}
    </ul>
    {'' if sku in WORN else f'<p class="for">{e(p["for"])}</p>'}
  </div>
</section>
<section class="sec tight" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="head" style="margin-bottom:36px"><h2 id="faq-h">About no. {sku}</h2></div>
    <div class="faq">
{faq}
    </div>
  </div>
</section>
<section class="sec tight" aria-labelledby="more-h" style="padding-top:0">
  <div class="wrap">
    <div class="head" style="margin-bottom:40px"><h2 id="more-h">You may also like</h2></div>
    {grid(others)}
    <div class="after"><a class="btn" href="/products/{cat['slug']}">All {cat['name'].lower()}</a></div>
  </div>
</section>"""
    title = f"{name} · No. {sku} · XIAI JEWELRY"
    return head(title, p["description"], f"/products/{sku}", photos[0], ld) + header("jewellery") + body + footer()


GUIDE = {
    "golden": ("Golden pearls are grown in the gold-lipped variety of the large Pinctada maxima oyster, the same oyster that gives white South Sea pearls. Their colour runs from pale champagne and cream to deep gold.",
               ["In our pieces: cream-gold to deep gold", "Sizes in our pieces: 8–15 mm", "Set in 18K gold, 14K gold, sterling silver or copper alloy, depending on the piece"]),
    "white": ("White South Sea pearls come from the silver-lipped Pinctada maxima oyster. They are among the largest cultured pearls, with a silvery-white colour and a soft, satin glow.",
              ["In our pieces: white, including drop-shaped pearls", "Sizes in our pieces: 8–13 mm", "Shown on their own, or mixed with golden and Tahitian pearls"]),
    "tahitian": ("Tahitian pearls grow in the black-lipped Pinctada margaritifera oyster. Their natural colours run from silvery and platinum grey to near-black, often with green, blue or rosé overtones.",
                 ["In our pieces: platinum grey and darker greys, including baroque shapes", "Sizes in our pieces: 8–14 mm", "Easy to wear with black, white, grey and denim"]),
    "akoya": ("Akoya pearls come from the small Pinctada fucata oyster. They are smaller than South Sea and Tahitian pearls, usually round, with a bright, mirror-like lustre.",
              ["In our pieces: white and grey-toned Akoya", "Sizes in our pieces: 3–8.5 mm", "Used as accents between larger pearls, or three in a row on a ring"]),
    "freshwater": ("Freshwater pearls grow in mussels in lakes and ponds, including those around Zhuji where XIAI is based. They come in the widest range of shapes, sizes and colours.",
                   ["In our pieces: white and purple", "Sizes in our pieces: 3–10 mm", "We also offer premium freshwater, Edison and freshwater baroque pearls. Ask us what is in stock"]),
}


def guide():
    nav = "".join(f'<a class="chip" href="#{k}">{v["short"]}</a>' for k, v in PEARLS.items()) + '<a class="chip" href="#mabe">Mabe &amp; baroque</a>'
    secs = []
    for k, v in PEARLS.items():
        text, facts = GUIDE[k]
        items = [BY_SKU[s] for s in v["skus"]]
        fl = "".join(f"<li>{e(f)}</li>" for f in facts)
        secs.append(f"""<section class="pearl-sec" id="{k}" aria-labelledby="{k}-h">
  <div class="wrap">
    <div class="cols"><div><h2 id="{k}-h">{v['name']}</h2><p class="body-text" style="margin-top:18px">{e(text)}</p></div><ul class="facts">{fl}</ul></div>
    {grid(items)}
  </div>
</section>""")
    mabe = f"""<section class="pearl-sec" id="mabe" aria-labelledby="mabe-h">
  <div class="wrap cols">
    <div><h2 id="mabe-h">Mabe &amp; baroque pearls</h2>
      <p class="body-text" style="margin-top:18px">Mabe pearls are cultured against the inside of the shell, which gives them a domed shape and a flat back. Baroque pearls grow in irregular shapes, so every one is different.</p>
      <p class="body-text" style="margin-top:16px">Our baroque piece is the <a href="/products/14103">Baroque Tahitian Pearl Necklace</a>. For Mabe pieces such as the cocktail ring shown here, ask us what is currently available.</p>
      <div class="btns" style="margin-top:28px"><a class="btn" href="/contact">Ask about Mabe pieces</a></div></div>
    <figure><img src="/images/sig-mabe-ring.jpg" alt="Mabe pearl cocktail ring with a pavé halo" width="1200" height="1200" loading="lazy"><figcaption class="note" style="margin-top:10px">Mabe pearl cocktail ring, from our showroom.</figcaption></figure>
  </div>
</section>"""
    body = f"""<div class="wrap">
  {crumbs(('Pearl guide', None))}
  <div class="cols" style="padding:40px 0 64px;align-items:center">
    <div class="page-head" style="padding:0"><h1>The pearl guide</h1><p class="sub">Golden, white South Sea, Tahitian, Akoya and freshwater pearls: where each comes from, how it looks, and the pieces we make with it.</p>
      <nav class="guide-nav" aria-label="Pearl types">{nav}</nav></div>
    <figure><img src="/images/pearl-types.jpg" alt="Sample box comparing Tahitian, Akoya, white South Sea and golden pearls" width="1200" height="1599" style="max-height:620px;width:auto;margin:0 auto" fetchpriority="high"><figcaption class="note center" style="margin-top:10px">Our pearl sample box in the showroom.</figcaption></figure>
  </div>
</div>
{''.join(secs)}
{mabe}"""
    return head("Pearl Guide: Golden, South Sea, Tahitian, Akoya and Freshwater Pearls · XIAI JEWELRY",
                "How golden, white South Sea, Tahitian, Akoya, freshwater, Mabe and baroque pearls differ, and the XIAI pieces made with each.",
                "/pearl-guide", "/images/pearl-types.jpg") + header("guide") + body + footer()


MILESTONES = [("1976", "The family begins working in the pearl industry."), ("1979", "First pearls brought to market."),
              ("1999", "The second generation takes over the business."), ("2008", "Moves into the East China International Jewelry City."),
              ("2010", "Registers the XIAI brand."), ("2012", "Starts selling through e-commerce."),
              ("2020", "Shifts toward livestream e-commerce."), ("2021–22", "Expands into creator partnerships, Douyin and WeChat Channels."),
              ("2023–now", "Builds out supply-chain and partnership services.")]


def story():
    tl = "".join(f"<li><b>{y}</b><span>{e(t)}</span></li>" for y, t in MILESTONES)
    body = f"""<div class="wrap">
  {crumbs(('Our story', None))}
  <div class="page-head"><h1>A pearl family since 1976</h1><p class="sub">XIAI is based in Shanxiahu Town, Zhuji, the heart of China&#39;s pearl industry.</p></div>
  <img class="wide-img" src="/images/farm-lake.jpg" alt="Pearl farm on a lake near Zhuji" width="1800" height="1200" fetchpriority="high">
</div>
<section class="sec" aria-labelledby="who-h">
  <div class="wrap cols">
    <h2 id="who-h" class="lede">Drawing on the region&#39;s pearl resources, we select pearls, develop and design products, craft them and sell them.</h2>
    <div class="body-text">
      <p>Our showroom, online store and personal advisory service connect with every kind of buyer, while dedicated teams for product selection, crafting, quality control, packing, shipping and after-sales work together behind each order.</p>
      <p>Beyond retail customers, we also supply sales channels and partner with livestream creators and on custom projects.</p>
    </div>
  </div>
</section>
<section class="sec" style="background:var(--rose)" aria-labelledby="ms-h">
  <div class="wrap cols">
    <div><h2 id="ms-h" style="font-size:clamp(38px,4vw,58px)">Milestones</h2><p class="body-text" style="margin-top:16px">Two generations, from the first pearls brought to market to today&#39;s showroom and partnerships.</p></div>
    <ol class="timeline">{tl}</ol>
  </div>
</section>
<section class="sec" aria-labelledby="src-h">
  <div class="wrap">
    <div class="head"><h2 id="src-h">Close to every step of a pearl&#39;s journey</h2><p>Working within the Shanxiahu pearl belt keeps us close to farming, harvesting, grading and raw pearl supply.</p></div>
    <ol class="steps">
      <li><img src="/images/farm-lake.jpg" alt="" width="1800" height="1200" loading="lazy"><h3>Farming</h3><p>Pearls grow in mussels on the lakes and ponds around Zhuji.</p></li>
      <li><img src="/images/opening-mussels.jpg" alt="" width="1200" height="800" loading="lazy"><h3>Harvesting</h3><p>Mussels are opened by hand and the pearls collected.</p></li>
      <li><img src="/images/measuring.jpg" alt="" width="1200" height="800" loading="lazy"><h3>Measuring</h3><p>Each pearl is sized so strands and pairs match.</p></li>
      <li><img src="/images/sorting.jpg" alt="" width="1200" height="800" loading="lazy"><h3>Grading</h3><p>Pearls are sorted by colour, shape and quality and kept in graded stock.</p></li>
    </ol>
  </div>
</section>
<section class="sec" style="background:var(--lilac)" aria-labelledby="make-h">
  <div class="wrap">
    <div class="head"><h2 id="make-h">From brief to finished jewellery</h2><p>Every new design follows the same five steps, so requirements are met and progress stays clear.</p></div>
    <ol class="steps five">
      <li><h3>Brief</h3><p>Agree the style, quantity and product requirements.</p></li>
      <li><h3>Design</h3><p>Shape a first concept around the character of the pearls.</p></li>
      <li><h3>Pearl matching</h3><p>Select pearls by size, colour and quality.</p></li>
      <li><h3>Sampling &amp; making</h3><p>Drilling, setting, assembly and the first sample.</p></li>
      <li><h3>Final check</h3><p>Inspect structure, how it wears and overall quality.</p></li>
    </ol>
  </div>
</section>
<section class="sec" id="showroom" aria-labelledby="room-h">
  <div class="wrap">
    <div class="head"><h2 id="room-h">A real showroom in Shanxiahu</h2><p>Where we welcome visitors, discuss projects, select pieces in person and shoot content.</p></div>
    <div class="gallery">
      <figure><img src="/images/showroom.jpg" alt="XIAI showroom with display counters" width="1800" height="1350" loading="lazy"><figcaption>The showroom</figcaption></figure>
      <figure><img src="/images/display.jpg" alt="Trays of pearl jewellery for in-person selection" width="1200" height="675" loading="lazy"><figcaption>In-person selection</figcaption></figure>
      <figure><img src="/images/studio.jpg" alt="Photo and livestream studio" width="1200" height="675" loading="lazy"><figcaption>Photo &amp; livestream studio</figcaption></figure>
    </div>
  </div>
</section>
<section class="sec" style="padding-top:0" aria-labelledby="val-h">
  <div class="wrap">
    <h2 id="val-h" class="vh">What we value</h2>
    <div class="values">
      <div><h3>Quality</h3><p>High standards in choosing pearls and making jewellery.</p></div>
      <div><h3>Taste</h3><p>Pearl culture meets modern design and how people dress today.</p></div>
      <div><h3>Service</h3><p>Clear advice before you buy, order follow-up and after-sales support.</p></div>
      <div><h3>Long-term partnership</h3><p>We value lasting relationships with customers and partners.</p></div>
    </div>
  </div>
</section>
<section class="sec" style="background:var(--rose)" aria-labelledby="cred-h">
  <div class="wrap">
    <div class="head"><h2 id="cred-h">Industry membership &amp; business credit</h2></div>
    <div class="certs">
      <figure><img src="/images/cert-association.jpg" alt="Plaque: Council member unit, Zhejiang Pearl Industry Association" loading="lazy"><figcaption>Council member, Zhejiang Pearl Industry Association</figcaption></figure>
      <figure><img src="/images/cert-aaa.jpg" alt="Certificate: AAA enterprise credit rating" loading="lazy"><figcaption>AAA enterprise credit rating</figcaption></figure>
      <figure><img src="/images/cert-contract.jpg" alt="Plaque: Zhejiang A-grade contract-abiding and trustworthy enterprise" loading="lazy"><figcaption>Zhejiang A-grade &ldquo;contract-abiding &amp; trustworthy&rdquo; enterprise</figcaption></figure>
    </div>
  </div>
</section>"""
    return head("Our Story · A Pearl Family in Shanxiahu since 1976 · XIAI JEWELRY",
                "XIAI is a pearl family business in Shanxiahu, Zhuji, since 1976: milestones, sourcing, how a new piece is made, the showroom and credentials.",
                "/our-story", "/images/farm-lake.jpg") + header("story") + body + footer()


def wholesale():
    body = f"""<div class="wrap">
  {crumbs(('Wholesale & custom', None))}
  <div class="cols" style="padding:40px 0 72px;align-items:center">
    <div class="page-head" style="padding:0"><h1>Wholesale, partnerships &amp; custom</h1><p class="sub">For retailers, brands, creators and anyone looking for something made to order.</p>
      <div class="btns" style="margin-top:30px"><a class="btn fill" href="/contact">Discuss a partnership</a><a class="btn" href="tel:{TEL}">Call {PHONE}</a></div></div>
    <img src="/images/studio.jpg" alt="XIAI photo and livestream studio" width="1200" height="675" fetchpriority="high">
  </div>
</div>
<section class="sec" style="background:var(--lilac)" aria-labelledby="ways-h">
  <div class="wrap">
    <div class="head"><h2 id="ways-h">Four ways to partner with XIAI</h2></div>
    <ul class="ways">
      <li><h3>Wholesale &amp; channel supply</h3><p>Steady stock, product selection support and reliable delivery for your channel.</p></li>
      <li><h3>Livestream partnerships</h3><p>Product selection for creators, on-site livestream support and after-sales handled for you.</p></li>
      <li><h3>Content e-commerce</h3><p>Support with content production, store operations and sales fulfilment.</p></li>
      <li id="custom"><h3>Custom &amp; bespoke</h3><p>Pearls selected for you and designs made to your brief.</p></li>
    </ul>
  </div>
</section>
<section class="sec" aria-labelledby="how-h">
  <div class="wrap">
    <div class="head"><h2 id="how-h">How it works</h2></div>
    <div class="paths">
      <div><h3>Buying for yourself</h3><ol><li>Browse our jewellery</li><li>Ask us about styles and specifications</li><li>Confirm the price and where to buy</li><li>Place your order and we ship it</li><li>Contact us any time for after-sales help</li></ol></div>
      <div><h3>Custom pieces &amp; partnerships</h3><ol><li>Tell us what you need</li><li>Agree the pearl selection and design</li><li>Approve the sample or product</li><li>Delivery</li></ol></div>
    </div>
  </div>
</section>
<section class="sec" style="background:var(--rose)" aria-labelledby="teams-h">
  <div class="wrap cols">
    <div><h2 id="teams-h" style="font-size:clamp(38px,4vw,58px)">Five teams, one order</h2><p class="body-text" style="margin-top:16px">From choosing a piece to delivery, every request has a team that follows it through.</p>
      <img src="/images/packing.jpg" alt="Checking and packing orders in the warehouse" width="900" height="1125" loading="lazy" style="margin-top:36px;max-width:420px;width:100%"></div>
    <ul class="teams">
      <li><b>Product &amp; selection</b><span>Styles, stock and product information</span></li>
      <li><b>Operations &amp; content</b><span>Channel operations, content planning and materials</span></li>
      <li><b>Photo &amp; livestream</b><span>Product photography, livestream sets and on-site support</span></li>
      <li><b>Customer service &amp; orders</b><span>Enquiries, order details and progress updates</span></li>
      <li><b>Warehouse &amp; shipping</b><span>Inventory, quality check, packing and logistics</span></li>
    </ul>
  </div>
</section>
<section class="sec" aria-labelledby="src2-h">
  <div class="wrap">
    <div class="head"><h2 id="src2-h">Close to the source</h2><p>Working within the Shanxiahu pearl belt keeps us close to farming, harvesting, grading and raw pearl supply.</p><div class="btns"><a class="btn" href="/our-story">Our story</a><a class="btn" href="/products">See the collection</a></div></div>
    <div class="gallery">
      <figure><img src="/images/sorting.jpg" alt="Team hand-sorting pearls" width="1200" height="800" loading="lazy"><figcaption>Grading and sorting</figcaption></figure>
      <figure><img src="/images/drilling.jpg" alt="Pearl being drilled on a precision machine" width="1200" height="800" loading="lazy"><figcaption>Drilling</figcaption></figure>
      <figure><img src="/images/quality-check.jpg" alt="Checking a finished pearl bracelet in hand" width="1200" height="1600" loading="lazy" style="object-position:50% 40%"><figcaption>Checking the finished piece</figcaption></figure>
    </div>
  </div>
</section>"""
    return head("Wholesale, Livestream Partnerships & Custom Pearl Jewellery · XIAI JEWELRY",
                "Work with XIAI: wholesale and channel supply, livestream partnerships, content e-commerce and custom pearl jewellery from Shanxiahu, Zhuji.",
                "/wholesale", "/images/studio.jpg") + header("wholesale") + body + footer()


FAQ = [("What does XIAI sell?", "Pearl necklaces, earrings, rings, bracelets, pendants and brooches."),
       ("Do you only sell freshwater pearls?", "No. Our focus is saltwater pearls — South Sea gold, Australian white, Tahitian, Akoya and Mabe — and we also offer premium freshwater, Edison and baroque pearls."),
       ("Are all settings 18K gold?", "It depends on the piece. The metal is stated in each product's description."),
       ("What should I look at when choosing pearl jewellery?", "The style, the pearl type, surface quality, size, the setting metal, real photos and the price. We are happy to send extra photos or videos of any piece."),
       ("Can you make custom pieces or supply wholesale?", "Yes. Tell us what you need; costs and delivery are confirmed order by order."),
       ("How do certificates and after-sales service work?", "Before you buy, we confirm which certificate comes with the specific piece and which after-sales terms apply."),
       ("Are the photos of models real?", "The model photographs are AI-generated from photos of our real pieces. Every product page shows actual photos of the jewellery."),
       ("How do I contact you?", f"Call or add Mr. Chen on WeChat at {PHONE}, or visit our showroom in Shanxiahu, Zhuji.")]


def contact():
    names = json.dumps({p["sku"]: p["name"] for p in products}, ensure_ascii=False)
    faq = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
    ld = [{"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    body = f"""<div class="wrap">
  {crumbs(('Contact', None))}
  <div class="page-head"><h1>Come to Shanxiahu, or simply get in touch</h1><p class="sub">Ask about a piece, arrange a showroom visit, or talk to us about wholesale, custom design and livestream partnerships.</p></div>
  <div class="contact-grid" style="padding-bottom:112px">
    <div>
      <p class="asking" id="asking" data-names="{e(names)}">You are asking about <b></b>. Please quote this item number when you call or message us.</p>
      <dl class="contact-list">
        <dt>Contact</dt><dd>Mr. Chen (&ldquo;XIAI Ge&rdquo; 玺爱哥)</dd>
        <dt>Phone</dt><dd><a href="tel:{TEL}">{PHONE}</a></dd>
        <dt>WeChat</dt><dd>Scan the QR code, or search {PHONE}</dd>
        <dt>Address</dt><dd>{ADDRESS}<br><span lang="zh">{ADDRESS_ZH}</span></dd>
      </dl>
      <img src="/images/building.jpg" alt="The XIAI Jewelry Creative Park building" width="1400" height="934" loading="lazy" style="margin-top:40px">
    </div>
    <div class="qr" id="wechat">
      <img src="/images/wechat-qr.jpg" alt="WeChat QR code for XIAI Jewelry" width="220" height="220" loading="lazy">
      <h2>Chat with us on WeChat</h2>
      <p>Scan with WeChat to send us a message, photos of what you are looking for, or your partnership idea.</p>
      <a class="btn fill" href="tel:{TEL}">Call {PHONE}</a>
    </div>
  </div>
</div>
<section class="sec" id="faq" style="background:var(--rose)" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="head" style="margin-bottom:40px"><h2 id="faq-h">Questions we are often asked</h2></div>
    <div class="faq">
{faq}
    </div>
  </div>
</section>"""
    return head("Contact & FAQ · XIAI JEWELRY, Shanxiahu, Zhuji",
                f"Contact XIAI JEWELRY: call or WeChat Mr. Chen on {PHONE}, or visit the showroom in Shanxiahu, Zhuji. Answers to common questions.",
                "/contact", "/images/showroom.jpg", ld) + header("contact") + body + footer()


def not_found():
    body = """<div class="wrap" style="padding:120px 16px 140px;text-align:center">
  <h1 style="font-size:clamp(44px,5vw,72px)">This page has moved</h1>
  <p class="sub" style="margin:16px auto 34px">Browse the collection, or ask us about a piece by its item number.</p>
  <div class="btns" style="justify-content:center"><a class="btn fill" href="/products">All jewellery</a><a class="btn" href="/contact">Contact us</a></div>
</div>"""
    return head("Page not found · XIAI JEWELRY", "This page could not be found.", "/404", "/images/showroom.jpg") + header() + body + footer()


# -------------------------------------------------------------- build -----
def main():
    missing = [k for k in ("hero", "mixed", "ring") if k not in CAMPAIGN]
    small = [k for k, v in CAMPAIGN.items() if size(v["src"])[0] < 1000]
    if missing:
        print("note: campaign images not found, sections skipped:", ", ".join(missing))
    if small:
        print("WARNING: campaign images below 1000px wide (placeholders?):", ", ".join(small))
        if "--allow-small" not in sys.argv:
            sys.exit("refusing to build with low-resolution campaign images; pass --allow-small for a local preview")
    write("index.html", home())
    write("products/index.html", listing())
    for c in CATEGORIES:
        write(f"products/{c['slug']}.html", listing(c))
    for p in products:
        write(f"products/{p['sku']}.html", product(p))
    write("pearl-guide.html", guide())
    write("our-story.html", story())
    write("wholesale.html", wholesale())
    write("contact.html", contact())
    write("404.html", not_found())
    urls = ["/", "/products"] + [f"/products/{c['slug']}" for c in CATEGORIES] + [f"/products/{p['sku']}" for p in products] + \
           ["/pearl-guide", "/our-story", "/wholesale", "/contact"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} urls; {len(products)} products")


if __name__ == "__main__":
    main()
