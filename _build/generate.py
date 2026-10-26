#!/usr/bin/env python3
"""Generate One Dundas static HTML pages."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BOOK = "https://book-directonline.com/properties/OneDundasDirect/"
# Canonical production base (single source of truth). GitHub Pages preview canonicalises here.
SITE_URL = "https://onedundashk.com/"
OG_IMAGE = "assets/images/exterior-day.jpg"
# Web3Forms enquiry form (public access key, safe client-side).
WEB3FORMS_ACCESS_KEY = "0ca60608-4cab-4d0d-91c8-55cbe55573c1"
WEB3FORMS_ENDPOINT = "https://api.web3forms.com/submit"
# No-JS fallback redirect after POST. Update to SITE_URL + "contact.html#thank-you" at DNS cutover.
ENQUIRY_REDIRECT = "https://thf-it-hk.github.io/onedundas-revamp/contact.html#thank-you"
import re
try:
    from PIL import Image
except ImportError:
    Image = None

def t(en, zh):
    """Bilingual inline span pair."""
    return f'<span class="i18n-en" data-i18n-en>{en}</span><span class="i18n-zh" data-i18n-zh lang="zh-Hant">{zh}</span>'

def opt(value, en, zh, selected=False):
    """Select option with data-label-* for JS language switching (spans inside <option> are ignored by browsers)."""
    sel = " selected" if selected else ""
    return f'<option value="{value}" data-label-en="{en}" data-label-zh="{zh}"{sel}>{en}</option>'

HEADER = '''<!DOCTYPE html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title data-title-en="{title_en}" data-title-zh="{title_zh}">{title_en}</title>
  <meta name="description" content="{desc}">
{seo}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Open+Sans:wght@400;600;700&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/styles.css">
  <link rel="icon" href="assets/images/logo-sm.png">
{preload}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="index.html" aria-label="One Dundas home">
        <img src="assets/images/logo-sm.png" width="78" height="73" alt="One Dundas logo">
        <span class="visually-hidden">One Dundas</span>
      </a>
      <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
      <nav class="site-nav" id="site-nav" data-site-nav aria-label="Primary">
        <a href="index.html">{home}</a>
        <a href="about.html">{about}</a>
        <a href="accommodation.html">{accom}</a>
        <a href="location.html">{location}</a>
        <a href="promotion.html">{promo}</a>
        <a href="gallery.html">{gallery}</a>
        <a href="virtual-tour.html">{vtour}</a>
        <a href="contact.html">{contact}</a>
        <div class="nav-actions">
          <div class="lang-switch" role="group" aria-label="Language">
            <button type="button" data-lang-btn="en" aria-pressed="true">EN</button>
            <button type="button" data-lang-btn="zh" aria-pressed="false">繁</button>
          </div>
          <a class="btn btn--primary" href="{book}" data-book-now target="_blank" rel="noopener noreferrer">{book_label}</a>
        </div>
      </nav>
    </div>
  </header>
  <main id="main">
'''

FOOTER = '''
  </main>
  <footer class="site-footer">
    <div class="container footer-grid">
      <div class="footer-brand">
        <img class="footer-logo" src="assets/images/logo-sm.png" width="40" height="40" alt="One Dundas logo">
        <strong>One Dundas 壹登</strong>
        <p class="footer-meta">{footer_meta}</p>
        <p>1 Dundas Street, Mongkok, Kowloon, Hong Kong<br>九龍旺角登打士街1號</p>
        <p>
          <a href="tel:+85227001122">+852 2700 1122</a><br>
          <a href="mailto:leasing@onedundashk.com">leasing@onedundashk.com</a>
        </p>
      </div>
      <nav class="footer-col" aria-label="Footer explore">
        <h2 class="footer-h">{explore}</h2>
        <ul>
          <li><a href="about.html">{about}</a></li>
          <li><a href="accommodation.html">{accom}</a></li>
          <li><a href="location.html">{location}</a></li>
          <li><a href="promotion.html">{promo}</a></li>
        </ul>
      </nav>
      <nav class="footer-col" aria-label="Footer stay">
        <h2 class="footer-h">{stay}</h2>
        <ul>
          <li><a href="gallery.html">{gallery}</a></li>
          <li><a href="virtual-tour.html">{vtour}</a></li>
          <li><a href="contact.html">{contact}</a></li>
          <li><a href="{book}" target="_blank" rel="noopener noreferrer">{book_label}</a></li>
        </ul>
      </nav>
      <nav class="footer-col" aria-label="Footer legal">
        <h2 class="footer-h">{legal}</h2>
        <ul>
          <li><a href="privacy.html">{privacy}</a></li>
          <li><a href="disclaimer.html">{disclaimer}</a></li>
        </ul>
      </nav>
    </div>
    <div class="container footer-bottom">
      <span>© 2026 One Dundas. All rights reserved.</span>
    </div>
  </footer>
  <script src="assets/js/main.js" defer></script>
</body>
</html>
'''

NAV = {
    # EN main-nav labels stored uppercase (stylish hotel nav); CSS also applies text-transform.
    # Footer reuses these keys — uppercase EN is fine for footer links too.
    "home": t("HOME", "首頁"),
    "about": t("ABOUT", "關於我們"),
    "accom": t("ACCOMMODATION", "住宿"),
    "location": t("LOCATION", "位置"),
    "promo": t("PROMOTION", "推廣"),
    "gallery": t("GALLERY", "相片集"),
    "vtour": t("VIRTUAL TOUR", "虛擬導覽"),
    "contact": t("ENQUIRY", "查詢"),
    "book_label": t("Book Now", "立即預訂"),  # CTA stays title case
    "explore": t("EXPLORE", "探索"),
    "stay": t("STAY", "住宿相關"),
    "legal": t("LEGAL", "法律資訊"),
    "privacy": t("PRIVACY", "私隱政策"),
    "disclaimer": t("DISCLAIMER", "免責聲明"),
    # Short location meta only — do NOT restore removed「旺角服務式公寓」/「Serviced apartments in Mongkok」tagline
    "footer_meta": t("Mongkok · Dundas Street", "旺角 · 登打士街"),
    "book": BOOK,
}

def page(title_en, title_zh, desc, body, name="index.html", crumb="Home", noindex=False):
    url = SITE_URL if name == "index.html" else SITE_URL + name
    img = SITE_URL + OG_IMAGE
    seo = [f'  <link rel="canonical" href="{url}">']
    if noindex:
        seo.append('  <meta name="robots" content="noindex, follow">')
    seo += [
        '  <meta property="og:type" content="website">',
        '  <meta property="og:site_name" content="One Dundas">',
        f'  <meta property="og:title" content="{title_en}">',
        f'  <meta property="og:description" content="{desc}">',
        f'  <meta property="og:url" content="{url}">',
        f'  <meta property="og:image" content="{img}">',
        '  <meta property="og:image:alt" content="One Dundas building exterior, 1 Dundas Street, Mongkok">',
        '  <meta property="og:locale" content="en_HK">',
        '  <meta property="og:locale:alternate" content="zh_HK">',
        '  <meta name="twitter:card" content="summary_large_image">',
        f'  <meta name="twitter:title" content="{title_en}">',
        f'  <meta name="twitter:description" content="{desc}">',
        f'  <meta name="twitter:image" content="{img}">',
    ]
    graph = [ORG, WEBSITE, HOTEL]
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL}]
    if name != "index.html":
        items.append({"@type": "ListItem", "position": 2, "name": crumb, "item": url})
    graph.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": items})
    graph.append({"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title_en,
                  "description": desc, "inLanguage": ["en", "zh-Hant"], "isPartOf": {"@id": SITE_URL + "#website"},
                  "breadcrumb": {"@id": url + "#breadcrumb"}})
    if name == "contact.html":
        graph.append(FAQ_LD)
    if name == "promotion.html" and promo_offers_ld():
        graph.append({"@type": "OfferCatalog", "@id": url + "#offers", "name": "One Dundas promotions",
                      "itemListElement": promo_offers_ld()})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1).replace("</", "<\\/")
    seo.append(f'  <script type="application/ld+json">\n{ld}\n  </script>')
    preload = ''
    if name == "index.html":
        preload = '  <link rel="preload" as="image" href="assets/images/hero-lobby.jpg" fetchpriority="high">'
    head = HEADER.format(title_en=title_en, title_zh=title_zh, desc=desc, seo="\n".join(seo), preload=preload, **NAV)
    foot = FOOTER.format(**NAV)
    return head + body + foot

_SIZES = {}
def _size(src):
    if Image is None or src.startswith("http"):
        return None
    if src not in _SIZES:
        try:
            with Image.open(ROOT / src) as im:
                _SIZES[src] = im.size
        except Exception:
            _SIZES[src] = None
    return _SIZES[src]

def optimize_imgs(html):
    """Add width/height to every <img>; lazy-load all content images except header logo."""
    def fix(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        if "width=" not in tag:
            sz = _size(src)
            if sz:
                tag = tag.replace("<img ", f'<img width="{sz[0]}" height="{sz[1]}" ', 1)
        if "loading=" not in tag and "logo" not in src:
            tag = tag.replace("<img ", '<img loading="lazy" decoding="async" ', 1)
        return tag
    return re.sub(r"<img [^>]+>", fix, html)

def write(name, html):
    html = optimize_imgs(html)
    path = ROOT / name
    path.write_text(html, encoding="utf-8")
    print("wrote", path, len(html))

# ---------- Shared availability widget ----------
AVAIL = f'''
<div class="avail-bar" aria-label="Check availability">
  <form data-avail-form action="{BOOK}" method="get" target="_blank">
    <div class="field">
      <label for="avail-checkin">{t("Check-in", "入住日期")}</label>
      <input id="avail-checkin" type="date" name="checkIn" required>
    </div>
    <div class="field">
      <label for="avail-checkout">{t("Check-out", "退房日期")}</label>
      <input id="avail-checkout" type="date" name="checkOut" required>
    </div>
    <div class="field">
      <label for="avail-adults">{t("Adults", "成人")}</label>
      <select id="avail-adults" name="adults">
        <option value="1">1</option>
        <option value="2" selected>2</option>
        <option value="3">3</option>
      </select>
    </div>
    <button class="btn btn--accent" type="submit">{t("Check Availability", "查詢空房")}</button>
  </form>
</div>
'''

# ===================== INDEX =====================

# ===================== PROMOTIONS (data: content/promotions.json, edited via Pages CMS) =====================
import html as _html
import os as _os
from datetime import date as _date

BUILD_DATE = _date.fromisoformat(_os.environ["BUILD_DATE"]) if _os.environ.get("BUILD_DATE") else _date.today()

def _d(v):
    try:
        return _date.fromisoformat(str(v)[:10]) if v else None
    except ValueError:
        return None

def _load_promos():
    f = ROOT / "content" / "promotions.json"
    data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    out = []
    for p in data or []:
        if not p.get("active"):
            continue
        vf, vu = _d(p.get("valid_from")), _d(p.get("valid_until"))
        if vf and vf > BUILD_DATE: continue
        if vu and vu < BUILD_DATE: continue
        out.append(p)
    return out

PROMOS = _load_promos()
E = lambda v: _html.escape(str(v or ""))

def _img(p):
    im = (p.get("image") or "").lstrip("/")
    return im

def _tx(p, k):
    return t(E(p.get(k + "_en")), E(p.get(k + "_zh") or p.get(k + "_en")))

def _code(p):
    return f'<p>{t("Promo code:", "折扣碼：")} <span class="promo-code">{E(p["code"])}</span></p>' if p.get("code") else ""

def _date_line(p):
    vu = _d(p.get("valid_until"))
    if not vu: return ""
    return f'<p><small>{t("Valid until " + vu.strftime("%-d %B %Y"), "優惠期至 " + f"{vu.year}年{vu.month}月{vu.day}日")}</small></p>'

def _home_promo():
    if not PROMOS:
        return ""
    p = PROMOS[0]
    im = _img(p)
    img = f'<div><img src="{E(im)}" alt="{E(p.get("image_alt") or p.get("title_en"))}" style="border-radius:12px;width:100%;object-fit:cover;max-height:220px"></div>' if im else ""
    summ = _tx(p, "summary") if p.get("summary_en") else _tx(p, "description")
    return f"""<section class="section">
  <div class="container">
    <div class="promo-banner">
      <div>
        <p class="eyebrow" style="color:#f5d9ff">{_tx(p, "discount_label") if p.get("discount_label_en") else t("Limited offer", "限時優惠")}</p>
        <h2>{_tx(p, "title")}</h2>
        <p>{summ}</p>
        {_code(p)}
        <div class="btn-row">
          <a class="btn btn--accent" href="promotion.html">{t("View promotion", "查看推廣")}</a>
          <a class="btn btn--ghost" style="border-color:#fff;color:#fff" href="tel:+85227001122">+852 2700 1122</a>
        </div>
      </div>
      {img}
    </div>
  </div>
</section>"""

def _promo_card(p):
    im = _img(p)
    img = f'<div><img src="{E(im)}" alt="{E(p.get("image_alt") or p.get("title_en"))}" style="border-radius:12px;width:100%"></div>' if im else ""
    link = E(p.get("book_link") or BOOK)
    terms = ""
    if p.get("terms_en") or p.get("terms_zh"):
        terms = f"""<div style="margin-top:2.5rem;max-width:48rem" class="feature-list">
      <h2>{t("Terms & conditions", "條款與細則")}</h2>
      {t(p.get("terms_en") or "", p.get("terms_zh") or p.get("terms_en") or "")}
    </div>"""
    return f"""<div class="promo-banner" style="margin-bottom:2rem">
      <div>
        {('<p class="eyebrow" style="color:#f5d9ff">' + _tx(p, "discount_label") + '</p>') if p.get("discount_label_en") else ""}
        <h2>{_tx(p, "title")}</h2>
        <p>{_tx(p, "description")}</p>
        {_code(p)}
        {_date_line(p)}
        <div class="btn-row">
          <a class="btn btn--accent" href="{link}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
          <a class="btn btn--ghost" style="border-color:#fff;color:#fff" href="tel:+85227001122">{t("Call leasing", "致電租務部")}</a>
        </div>
      </div>
      {img}
    </div>
    {terms}"""

if PROMOS:
    _cards = "\n    ".join(_promo_card(p) for p in PROMOS)
else:
    _cards = f"""<div style="max-width:48rem">
      <h2>{t("No current promotions", "暫時未有推廣優惠")}</h2>
      <p>{t("There are no promotions running at the moment. Please check back soon, or contact Leasing at +852 2700 1122 or leasing@onedundashk.com for our latest rates.", "目前未有推廣優惠，敬請留意。如欲查詢最新租金，請致電 +852 2700 1122 或電郵 leasing@onedundashk.com 與租務部聯絡。")}</p>
      <div class="btn-row"><a class="btn btn--accent" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a></div>
    </div>"""

PROMO_PAGE = f"""
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("Promotion", "推廣活動")}</h1>
  </div>
</section>
<section class="section">
  <div class="container">
    {_cards}
  </div>
</section>
"""
HOME_PROMO = _home_promo()

def _strip(h):
    return re.sub(r"<[^>]+>", " ", h or "").split()

def promo_offers_ld():
    out = []
    for p in PROMOS:
        o = {"@type": "Offer", "name": p.get("title_en"), "description": p.get("description_en"),
             "url": SITE_URL + "promotion.html", "seller": {"@id": SITE_URL + "#organization"}}
        if p.get("valid_from"): o["validFrom"] = str(p["valid_from"])[:10]
        if p.get("valid_until"): o["validThrough"] = str(p["valid_until"])[:10]
        out.append(o)
    return out

def promo_llms():
    if not PROMOS:
        return "- Current offer: none at the moment (contact leasing for latest rates)"
    lines = []
    for p in PROMOS:
        bits = [p.get("title_en", "")]
        if p.get("code"): bits.append(f"code {p['code']}")
        if p.get("valid_until"): bits.append(f"valid until {str(p['valid_until'])[:10]}")
        terms = " ".join(_strip(p.get("terms_en")))
        lines.append("- Current offer: " + "; ".join(bits) + (f". {terms}" if terms else ""))
    return "\n".join(lines)

if PROMOS:
    _p0 = PROMOS[0]
    PROMO_TITLE = f"{_p0.get('title_en')} | One Dundas"
    PROMO_DESC = " ".join((_p0.get("description_en") or "").split())[:155] + (f" Code {_p0['code']}." if _p0.get("code") else "")
else:
    PROMO_TITLE = "Promotions | One Dundas Serviced Apartments"
    PROMO_DESC = "Current promotions and offers at One Dundas serviced apartments, Mongkok. Contact leasing for the latest rates."

index_body = f'''
<section class="hero">
  <div class="hero__media" style="background-image:url('assets/images/hero-lobby.jpg')" role="img" aria-label="One Dundas lobby"></div>
  <div class="container hero__content">
    <p class="eyebrow">{t("Serviced Apartments · Mongkok", "服務式公寓 · 旺角")}</p>
    <h1>{t("Your home in the heart of Kowloon", "九龍核心的​都市居所")}</h1>
    <p class="lead">{t("109 stylish Studio, One-Bedroom and Two-Bedroom apartments at 1 Dundas Street — steps from Mongkok’s markets, MTR and city life.", "壹登提供109間時尚開放式、單卧室及雙卧室公寓，位於登打士街1號，步行即達旺角市集、港鐵與繁華街景。")}</p>
    <div class="btn-row">
      <a class="btn btn--accent" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
      <a class="btn btn--light" href="contact.html">{t("Enquire", "立即查詢")}</a>
    </div>
    {AVAIL}
  </div>
</section>

{HOME_PROMO}

<section class="section section--tint">
  <div class="container">
    <p class="eyebrow">{t("Apartments", "公寓")}</p>
    <h2>{t("Find your space", "選擇合適房型")}</h2>
    <p class="lead">{t("Floor-to-ceiling windows, kitchenettes and thoughtful amenities — designed for singles, students and small families.", "大片落地玻璃窗、設備齊全的廚房與貼心設施，適合單身、海外學生與小家庭。")}</p>
    <div class="grid-3" style="margin-top:2rem">
      <article class="card">
        <img src="assets/images/studio-a.jpg" alt="Studio apartment at One Dundas with queen bed and city view">
        <div class="card__body">
          <h3>{t("Studio", "開放式公寓")}</h3>
          <p class="card__meta">249–280 sq ft · 19–29/F</p>
          <p>{t("Compact and cosy with city views, queen bed and well-equipped kitchenette.", "舒適精巧，飽覽城市景觀，配備加大雙人床與設備齊全的廚房。")}</p>
          <a class="btn btn--ghost" href="accommodation.html#studio">{t("Studio details", "開放式詳情")}</a>
        </div>
      </article>
      <article class="card">
        <img src="assets/images/1br-living.jpg" alt="One-bedroom apartment living area at One Dundas">
        <div class="card__body">
          <h3>{t("One-Bedroom", "單卧室公寓")}</h3>
          <p class="card__meta">437–479 sq ft · 19–35/F</p>
          <p>{t("Separate bedroom and living area with work space and harbour or city views.", "獨立睡房與客廳，設工作區，可賞海景或城市景觀。")}</p>
          <a class="btn btn--ghost" href="accommodation.html#one-bedroom">{t("One-Bedroom details", "單卧室詳情")}</a>
        </div>
      </article>
      <article class="card">
        <img src="assets/images/twobed-living.jpg" alt="Two-bedroom apartment living room at One Dundas">
        <div class="card__body">
          <h3>{t("Two-Bedroom", "雙卧室公寓")}</h3>
          <p class="card__meta">544 sq ft · 19–35/F</p>
          <p>{t("Master suite plus guest room, in-room washer & dryer — ideal for families.", "主人房連套房浴室與客房，房內洗衣乾衣機，適合家庭。")}</p>
          <a class="btn btn--ghost" href="accommodation.html#two-bedroom">{t("Two-Bedroom details", "雙卧室詳情")}</a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container grid-2">
    <div>
      <p class="eyebrow">{t("Why One Dundas", "為何選擇壹登")}</p>
      <h2>{t("Urban calm, steps from Mongkok energy", "繁華旺角旁的​寧靜居所")}</h2>
      <p class="lead">{t("Set on the residential side of Mongkok yet moments from Langham Place, Ladies’ Market and Mongkok MTR.", "座落旺角住宅區一側，步行即達朗豪坊、女人街與旺角港鐵站。")}</p>
      <ul class="feature-list">
        <li>{t("109 apartments across Studio / 1BR / 2BR", "109間開放式／單卧／雙卧公寓")}</li>
        <li>{t("Housekeeping twice weekly · linen weekly", "每週兩次清潔 · 每週更換床單")}</li>
        <li>{t("Outdoor leisure area & gym · BBQ rental", "戶外休憩與健身設施 · 燒烤爐租用")}</li>
        <li>{t("Rates inclusive of management, rates & utilities", "租金已包括管理費、差餉及水電空調")}</li>
        <li>{t("Non-smoking green living", "全幢禁煙綠色生活")}</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn--primary" href="about.html">{t("About One Dundas", "關於壹登")}</a>
        <a class="btn btn--ghost" href="location.html">{t("Location", "位置交通")}</a>
      </div>
    </div>
    <div>
      <img src="assets/images/hero-eco.jpg" alt="Eco-friendly apartment interior at One Dundas, Mongkok" style="border-radius:16px;box-shadow:var(--shadow-lg)">
    </div>
  </div>
</section>

<section class="section section--charcoal">
  <div class="container">
    <div class="stat-row">
      <div class="stat"><strong>109</strong><span>{t("Apartments", "公寓單位")}</span></div>
      <div class="stat"><strong>3</strong><span>{t("Apartment types", "房型選擇")}</span></div>
      <div class="stat"><strong>~2 min</strong><span>{t("to Mongkok MTR*", "至旺角站*")}</span></div>
      <div class="stat"><strong>24/7</strong><span>{t("Concierge & security", "禮賓與保安")}</span></div>
    </div>
    <p class="muted" style="margin-top:1rem;font-size:.85rem">* {t("Walking time estimates vary by exit and traffic.", "步行時間因出口與路況而異。")}</p>
  </div>
</section>

<section class="section section--purple">
  <div class="container" style="text-align:center">
    <h2>{t("Ready to stay?", "準備入住？")}</h2>
    <p class="lead" style="margin-inline:auto;color:rgba(255,255,255,.9)">{t("Book direct online or speak with our leasing team.", "網上直接預訂，或聯絡租務團隊。")}</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn btn--accent" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
      <a class="btn btn--light" href="contact.html">{t("Send an enquiry", "提交查詢")}</a>
    </div>
  </div>
</section>
'''

# ===================== ABOUT =====================
about_body = f'''
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("About", "關於")}</h1>
    <p class="lead">{t("Serviced apartments in the heart of Kowloon.", "座落九龍核心的服務式公寓。")}</p>
  </div>
</section>
<section class="section">
  <div class="container grid-2">
    <div>
      <h2>{t("Nestled in Mongkok", "佇立旺角")}</h2>
      <p>{t("Located at the heart of Kowloon, One Dundas Serviced Apartment is set on the residential side of bustling Mongkok and yet just a step away from a colourful, lively neighbourhood surrounded by traditional shops, local businesses and conveniently connected by public transportation.", "壹登座落於九龍的核心地帶，佇立在繁華旺角的寧靜住宅區中；然而，只要輕輕跨出一步，就能立刻擁抱那座色彩繽紛、充滿煙火氣的熱鬧街區。傳統老舖與在地小店錯落其間，隨時準備好讓你探索最道地的香港風情，加上四通八達的便捷交通，讓你輕鬆穿梭城市每個角落。")}</p>
      <p>{t("With 109 well-appointed Studio, One-Bedroom and Two-Bedroom apartments, One Dundas suits singles, overseas students and small families alike. Expansive windows capture city or Victoria Harbour views, while kitchenettes come equipped with cookware and utensils.", "壹登精心打造了109間設施齊全的開放式、單卧室及雙卧室公寓，無論單身、海外留學生還是小家庭都非常合適。大片落地玻璃窗盡覽城市或維港景色，廚房備齊烹調器具與餐具。")}</p>
    </div>
    <div>
      <img src="assets/images/entrance.jpg" alt="One Dundas main entrance" style="border-radius:16px">
    </div>
  </div>
</section>
<section class="section section--tint">
  <div class="container">
    <h2>{t("Facilities & services", "設施與服務")}</h2>
    <div class="grid-3" style="margin-top:1.5rem">
      <div class="card"><img src="assets/images/gym.jpg" alt="Outdoor gym at One Dundas"><div class="card__body"><h3>{t("Outdoor gym", "戶外健身")}</h3><p>{t("Stay active at the outdoor gym facilities.", "使用戶外健身設施保持活力。")}</p></div></div>
      <div class="card"><img src="assets/images/leisure.jpg" alt="Outdoor leisure area at One Dundas"><div class="card__body"><h3>{t("Leisure area", "休憩空間")}</h3><p>{t("Outdoor leisure spaces for unwinding after a busy day.", "戶外休憩區，讓你在忙碌一天後放鬆。")}</p></div></div>
      <div class="card"><img src="assets/images/hero-lobby.jpg" alt="One Dundas lobby and concierge"><div class="card__body"><h3>{t("Concierge", "禮賓服務")}</h3><p>{t("Concierge and security for peace of mind.", "禮賓與保安服務，安心無憂。")}</p></div></div>
    </div>
    <ul class="feature-list" style="margin-top:2rem;max-width:40rem">
      <li>{t("Self-service laundry (washer & dryer)", "自助洗衣設施（洗衣機及乾衣機）")}</li>
      <li>{t("BBQ facilities rental · car parking rental", "燒烤爐租用 · 泊車位租用")}</li>
      <li>{t("Housekeeping twice a week (except Sundays); linen weekly", "每週兩次清潔（星期日除外）；每週更換床單")}</li>
      <li>{t("Complimentary Wi-Fi and in-room internet", "免費 Wi-Fi 及室內上網")}</li>
      <li>{t("Non-smoking property", "全幢禁煙")}</li>
    </ul>
  </div>
</section>
<section class="section">
  <div class="container">
    <h2>{t("Contact leasing", "聯絡租務")}</h2>
    <p>{t("For business and leasing enquiries, please use:", "商務及租務查詢請聯絡：")}</p>
    <div class="contact-stack" style="max-width:28rem;margin-top:1rem">
      <div class="contact-item"><strong>{t("Phone", "電話")}</strong><a href="tel:+85227001122">+852 2700 1122</a></div>
      <div class="contact-item"><strong>{t("Email", "電郵")}</strong><a href="mailto:leasing@onedundashk.com">leasing@onedundashk.com</a></div>
      <div class="contact-item"><strong>{t("Address", "地址")}</strong>1 Dundas Street, Mongkok, Kowloon, Hong Kong<br>香港九龍旺角登打士街1號</div>
    </div>
  </div>
</section>
'''

# ===================== ACCOMMODATION =====================
def room_block(anchor, title_en, title_zh, img, size, bed, occ, storey, desc_en, desc_zh, extras_en, extras_zh):
    return f'''
<section class="section" id="{anchor}">
  <div class="container grid-2">
    <div>
      <img src="{img}" alt="{title_en} at One Dundas, Mongkok" style="border-radius:16px;box-shadow:var(--shadow)">
    </div>
    <div>
      <p class="eyebrow">{t("Apartment", "公寓")}</p>
      <h2>{t(title_en, title_zh)}</h2>
      <p>{t(desc_en, desc_zh)}</p>
      <div class="table-wrap" style="margin:1.25rem 0">
        <table class="spec">
          <thead><tr>
            <th>{t("Size", "面積")}</th>
            <th>{t("Bedding", "床具")}</th>
            <th>{t("Occupancy", "入住人數")}</th>
            <th>{t("Storey", "樓層")}</th>
          </tr></thead>
          <tbody><tr>
            <td>{size}</td><td>{bed}</td><td>{occ}</td><td>{storey}</td>
          </tr></tbody>
        </table>
      </div>
      <h3>{t("In-room provisions", "房內設備")}</h3>
      <ul class="feature-list">
        <li>{t("Well-equipped kitchenette with utensils & tableware", "設備齊全廚房，備烹調器具與餐具")}</li>
        <li>{t("4K smart TV with international channels", "4K 智能電視及國際頻道")}</li>
        <li>{extras_en and t(extras_en, extras_zh)}</li>
        <li>{t("Electric kettle · electronic safe · welcome kit (first check-in)", "電熱水壺 · 電子保險箱 · 迎賓套裝（首次入住）")}</li>
        <li>{t("Complimentary Wi-Fi · local calls with direct line", "免費 Wi-Fi · 直撥本地電話")}</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn--primary" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
        <a class="btn btn--ghost" href="contact.html">{t("Enquire", "查詢")}</a>
      </div>
    </div>
  </div>
</section>
'''

accom_body = f'''
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("Accommodation", "住宿")}</h1>
    <p class="lead">{t("One Dundas consists of 109 well-appointed Studio, One-Bedroom and Two-Bedroom apartments.", "壹登精心打造了109間設施齊全的開放式、單卧室及雙卧室公寓。")}</p>
    <ul class="pill-list">
      <li><a href="#studio" style="text-decoration:none;color:inherit">{t("Studio", "開放式")}</a></li>
      <li><a href="#one-bedroom" style="text-decoration:none;color:inherit">{t("One-Bedroom", "單卧室")}</a></li>
      <li><a href="#two-bedroom" style="text-decoration:none;color:inherit">{t("Two-Bedroom", "雙卧室")}</a></li>
    </ul>
  </div>
</section>
{room_block("studio", "Studio Apartment", "開放式公寓", "assets/images/studio-a.jpg",
  "249–280 sq ft (23–26 m²)", t("1 queen bed","加大雙人床 x1"), "2", "19–29/F",
  "Enjoying views of the city, the tastefully decorated, compact yet cosy Studio offers tranquillity from the bustling neighbourhood — with an efficient layout, kitchenette and large windows.",
  "飽覽城市景觀的開放式公寓裝潢雅致、精巧舒適，讓你在繁華街區中找到寧靜。佈局高效，配備廚房與大窗。",
  "1-door refrigerator", "單門雪櫃")}
{room_block("one-bedroom", "One-Bedroom Apartment", "單卧室公寓", "assets/images/1br-closed-living.jpg",
  "437–479 sq ft (41–45 m²)", t("1 queen bed","加大雙人床 x1"), "2", "19–35/F",
  "A practical, comfortable layout with contemporary décor, kitchenette, living area, spacious bedroom with work space and floor-to-ceiling city views. Open- and closed-kitchen variants available.",
  "實用舒適的佈局與現代裝潢，配備廚房、客廳、寬敞睡房連工作區及落地玻璃窗城市景觀。設開放式或封閉式廚房款式。",
  "2-door refrigerator · iron & ironing board", "雙門雪櫃 · 熨斗及熨板")}
{room_block("two-bedroom", "Two-Bedroom Apartment", "雙卧室公寓", "assets/images/twobed-living.jpg",
  "544 sq ft (51 m²)", t("1 queen + 1 single","加大雙人床 + 單人床"), "3", "19–35/F",
  "A sanctuary from busy city life: expansive views, in-room washer & dryer, kitchenette, inviting living area, master bedroom with en suite and work area, plus a cosy guest room.",
  "繁忙都市中的避世之所：開闊景觀、房內洗衣乾衣機、廚房、舒適客廳、主人房連套房浴室與工作區，另設客房。",
  "2-door refrigerator · in-room washer & dryer · iron & board", "雙門雪櫃 · 房內洗衣乾衣機 · 熨斗及熨板")}
<section class="section section--tint">
  <div class="container">
    <h2>{t("Included in rates", "租金已包括")}</h2>
    <ul class="feature-list">
      <li>{t("Property management fee & service charges", "物業管理費及服務費")}</li>
      <li>{t("Government rates & taxes", "差餉及稅項")}</li>
      <li>{t("Utilities (water, electricity and air-conditioning)", "水、電及空調費用")}</li>
    </ul>
    <p class="muted" style="margin-top:1rem">{t("Baby cot and rollaway bed available subject to availability with extra charges.", "嬰兒床及加床視供應情況另收費。")}</p>
  </div>
</section>
'''

# ===================== LOCATION =====================
location_body = f'''
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("Location", "位置")}</h1>
    <p class="lead">{t("1 Dundas Street, Mongkok, Kowloon, Hong Kong", "香港九龍旺角登打士街1號")}</p>
  </div>
</section>
<section class="section" id="map">
  <div class="container">
    <h2>{t("Getting here", "如何前往")}</h2>
    <p>{t("One Dundas is moments from Mongkok MTR and surrounded by shopping, dining and street life.", "壹登毗鄰旺角港鐵站，四周盡是購物、餐飲與街頭生活。")}</p>
    <iframe class="map-embed" title="One Dundas on Google Maps" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      src="https://www.google.com/maps?q=1+Dundas+Street,+Mongkok,+Kowloon,+Hong+Kong&output=embed"></iframe>
    <div class="table-wrap" style="margin-top:1.5rem">
      <table class="spec">
        <thead><tr><th>{t("Destination", "目的地")}</th><th>{t("Approx. time", "約需時間")}</th></tr></thead>
        <tbody>
          <tr><td>{t("Mongkok MTR Exit E1 / Langham Place", "旺角站 E1 出口／朗豪坊")}</td><td>~8 min walk</td></tr>
          <tr><td>{t("Yau Ma Tei MTR Exit A1", "油麻地站 A1 出口")}</td><td>~6 min walk</td></tr>
          <tr><td>{t("Olympic MTR / Olympian City", "奧運站／奧海城")}</td><td>~10 min</td></tr>
          <tr><td>{t("Kowloon MTR / ICC / Elements", "九龍站／環球貿易廣場／圓方")}</td><td>~10 min</td></tr>
          <tr><td>{t("Harbour City / Canton Road", "海港城／廣東道")}</td><td>~10 min</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>
<section class="section section--tint" id="neighbourhood">
  <div class="container grid-2">
    <div>
      <h2>{t("Neighbourhood", "探索周邊")}</h2>
      <p>{t("One Dundas is located in the heart of the city with an abundance of shopping, dining, entertainment and lifestyle options.", "壹登位於城市核心，購物、餐飲、娛樂與生活選擇豐富。")}</p>
      <h3>{t("Shopping & lifestyle", "購物與生活")}</h3>
      <ul class="feature-list">
        <li>Langham Place 朗豪坊</li>
        <li>{t("Ladies’ Market", "女人街")}</li>
        <li>{t("Sneakers Street", "波鞋街")}</li>
        <li>Harbour City 海港城 · Elements 圓方 · Olympian City 奧海城</li>
      </ul>
      <h3>{t("Banks nearby", "附近銀行")}</h3>
      <ul class="feature-list">
        <li>HSBC 匯豐銀行</li>
        <li>Bank of China 中國銀行</li>
        <li>Hang Seng Bank 恆生銀行</li>
        <li>Standard Chartered Bank 渣打銀行</li>
        <li>Bank of Communications 交通銀行</li>
      </ul>
    </div>
    <div>
      <img src="assets/images/neighbourhood.jpg" alt="Mongkok street scene near One Dundas" style="border-radius:16px;margin-bottom:1rem">
      <h3>{t("Universities", "大專院校")}</h3>
      <p>{t("Seamless connectivity to prestigious universities:", "交通便捷，輕鬆連接多所知名院校：")}</p>
      <ul class="feature-list">
        <li>The Hong Kong Polytechnic University 香港理工大學</li>
        <li>City University of Hong Kong 香港城市大學</li>
        <li>Hong Kong Baptist University 香港浸會大學</li>
        <li>Hong Kong Metropolitan University 香港都會大學</li>
      </ul>
    </div>
  </div>
</section>
'''

# ===================== PROMOTION =====================
promo_body = PROMO_PAGE

# ===================== GALLERY =====================
GALLERY_IMGS = [
    ("studio-a.jpg", "Studio Type A"),
    ("studio-b.jpg", "Studio Type B"),
    ("1br-living.jpg", "One-bedroom living area"),
    ("1br-closed-living.jpg", "One-bedroom closed kitchen living"),
    ("1br-kitchen.jpg", "Kitchenette"),
    ("1br-bedroom.jpg", "One-bedroom bedroom"),
    ("1br-bath.jpg", "Bathroom"),
    ("twobed-living.jpg", "Two-bedroom living"),
    ("2br-master.jpg", "Two-bedroom master"),
    ("2br-bath.jpg", "Two-bedroom bathroom"),
    ("hero-lobby.jpg", "Lobby"),
    ("entrance.jpg", "Main entrance"),
    ("exterior-day.jpg", "Exterior day"),
    ("exterior-night.jpg", "Exterior night"),
    ("gym.jpg", "Gymnasium"),
    ("leisure.jpg", "Leisure area"),
]
gallery_items = "\n".join(
    f'<a href="assets/images/{fn}" data-lightbox><img src="assets/images/{fn}" alt="{alt} – One Dundas" loading="lazy"></a>'
    for fn, alt in GALLERY_IMGS
)
gallery_body = f'''
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("Media", "媒體")}</h1>
    <p class="lead">{t("A selection of interiors, facilities and exteriors. Click any image to open full size.", "精選室內、設施與外觀相片。點擊可開啟原圖。")}</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="gallery-grid">
      {gallery_items}
    </div>
  </div>
</section>
'''

# ===================== VIRTUAL TOUR =====================
TOURS = json.loads((ROOT / "assets/vt/tours.json").read_text(encoding="utf-8"))
tour_tabs = "\n".join(
    f'<button type="button" class="tour-tab" role="tab" data-tour="{k}" aria-selected="{"true" if i == 0 else "false"}">{t(v["en"], v["zh"])}</button>'
    for i, (k, v) in enumerate(TOURS.items())
)
tour_json = json.dumps(TOURS, ensure_ascii=False).replace("</", "<\\/")
vtour_body = f'''
<link rel="stylesheet" href="assets/vt/pannellum/pannellum.css">
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("Virtual Tour", "虛擬導覽")}</h1>
    <p class="lead">{t("Choose an apartment type, then drag to look around 360°. Click the arrows to move between rooms.", "選擇房型，拖曳畫面即可 360° 環視；點擊箭咀可前往其他房間。")}</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="tour-tabs" role="tablist" aria-label="Apartment type">
      {tour_tabs}
    </div>
    <div class="tour-viewer" id="tour-viewer" role="region" aria-label="360° virtual tour"></div>
    <div class="tour-rooms" data-tour-rooms aria-label="Rooms"></div>
    <noscript><p>{t("Please enable JavaScript to view the virtual tour.", "請啟用 JavaScript 以瀏覽虛擬導覽。")}</p></noscript>
  </div>
  <div class="container" style="margin-top:2.5rem;text-align:center">
    <div class="btn-row" style="justify-content:center">
      <a class="btn btn--ghost" href="gallery.html">{t("View photos", "查看相片")}</a>
      <a class="btn btn--primary" href="contact.html">{t("Request a viewing", "預約參觀")}</a>
      <a class="btn btn--accent" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
    </div>
  </div>
</section>
<script type="application/json" id="tour-data">{tour_json}</script>
<script src="assets/vt/pannellum/pannellum.js" defer></script>
'''

# ===================== CONTACT / ENQUIRY =====================
contact_body = f'''
<section class="page-hero">
  <div class="container">
    <h1 class="eyebrow">{t("Contact", "聯絡")}</h1>
    <p class="lead">{t("Tell us about your stay. Our leasing team will follow up.", "告訴我們您的入住需要，租務團隊會與您跟進。")}</p>
  </div>
</section>
<section class="section">
  <div class="container grid-2" style="align-items:start">
    <div class="form-card">
      <div class="form-success" id="thank-you" data-enquiry-success tabindex="-1" role="status" aria-live="polite">
        {t("Thank you — your enquiry has been sent. Our leasing team will be in touch shortly.", "謝謝 — 您的查詢已送出，租務團隊會盡快與您聯絡。")}
      </div>
      <div class="form-error" data-enquiry-error tabindex="-1" role="alert">
        {t('Sorry, your enquiry could not be sent. Please email <a href="mailto:leasing@onedundashk.com">leasing@onedundashk.com</a> or call <a href="tel:+85227001122">+852 2700 1122</a>.', '抱歉，查詢未能送出。請電郵 <a href="mailto:leasing@onedundashk.com">leasing@onedundashk.com</a> 或致電 <a href="tel:+85227001122">+852 2700 1122</a>。')}
      </div>
      <form data-enquiry-form novalidate action="{WEB3FORMS_ENDPOINT}" method="post">
        <input type="hidden" name="access_key" value="{WEB3FORMS_ACCESS_KEY}">
        <input type="hidden" name="subject" value="New enquiry from onedundashk.com website">
        <input type="hidden" name="from_name" value="One Dundas Website">
        <input type="hidden" name="redirect" value="{ENQUIRY_REDIRECT}">
        <input type="checkbox" name="botcheck" class="visually-hidden-bot" style="display:none" tabindex="-1" autocomplete="off">
        <div class="form-grid form-grid--2">
          <div class="field">
            <label for="firstname">{t("First name *", "名字 *")}</label>
            <input id="firstname" name="firstname" autocomplete="given-name" required>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="lastname">{t("Last name *", "姓氏 *")}</label>
            <input id="lastname" name="lastname" autocomplete="family-name" required>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="company">{t("Company", "公司")}</label>
            <input id="company" name="company" autocomplete="organization">
            <div class="field-error"></div>
          </div>
          <div class="field">
            <label for="phone">{t("Phone *", "電話 *")}</label>
            <input id="phone" name="phone" type="tel" autocomplete="tel" required>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="email">{t("Email *", "電郵 *")}</label>
            <input id="email" name="email" type="email" autocomplete="email" required>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="apartmenttype">{t("Apartment type *", "公寓類型 *")}</label>
            <select id="apartmenttype" name="apartmenttype" required>
              {opt("", "Please select", "請選擇")}
              {opt("Studio", "Studio", "開放式")}
              {opt("One-Bedroom", "One-Bedroom", "單卧室")}
              {opt("Two-Bedroom", "Two-Bedroom", "雙卧室")}
              {opt("Flexible", "Flexible / not sure", "彈性／未定")}
            </select>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="adult">{t("Adults", "成人人數")}</label>
            <input id="adult" name="adult" type="number" min="1" max="6" value="1">
            <div class="field-error"></div>
          </div>
          <div class="field">
            <label for="child">{t("Children", "小童人數")}</label>
            <input id="child" name="child" type="number" min="0" max="4" value="0">
            <div class="field-error"></div>
          </div>
          <div class="field">
            <label for="adate">{t("Expected arrival *", "預計入住日期 *")}</label>
            <input id="adate" name="adate" type="date" required>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="ddate">{t("Expected departure *", "預計退房日期 *")}</label>
            <input id="ddate" name="ddate" type="date" required>
            <div class="field-error" aria-live="polite"></div>
          </div>
          <div class="field">
            <label for="budget">{t("Budget", "預算")}</label>
            <select id="budget" name="budget">
              {opt("", "Prefer not to say", "不便透露")}
              {opt("Under HKD 25,000", "Under HKD 25,000", "低於 HKD 25,000")}
              {opt("HKD 25,000–35,000", "HKD 25,000–35,000", "HKD 25,000–35,000")}
              {opt("HKD 35,000–45,000", "HKD 35,000–45,000", "HKD 35,000–45,000")}
              {opt("HKD 45,000+", "HKD 45,000+", "HKD 45,000+")}
            </select>
            <div class="field-error"></div>
          </div>
          <div class="field">
            <label for="hear">{t("How did you hear about us?", "如何得知壹登？")}</label>
            <select id="hear" name="hear">
              {opt("", "Please select", "請選擇")}
              {opt("Search", "Search", "搜尋")}
              {opt("Referral", "Referral", "介紹")}
              {opt("Social", "Social media", "社交媒體")}
              {opt("Agent", "Agent", "代理")}
              {opt("Other", "Other", "其他")}
            </select>
            <div class="field-error"></div>
          </div>
        </div>
        <div class="field" style="margin-top:1rem">
          <label for="remark">{t("Message / remarks", "留言／備註")}</label>
          <textarea id="remark" name="remark" rows="5"></textarea>
          <div class="field-error"></div>
        </div>
        <label class="checkbox" style="margin:1rem 0">
          <input type="checkbox" name="marketing" value="yes">
          <span>{t("I would like to receive news and offers from One Dundas (optional, not pre-checked).", "我願意接收壹登的最新消息與優惠（選填，預設不勾選）。")}</span>
        </label>
        <button class="btn btn--primary btn--block" type="submit" data-enquiry-submit><span data-label-idle>{t("Send enquiry", "送出查詢")}</span><span data-label-sending hidden>{t("Sending…", "傳送中…")}</span></button>
      </form>
    </div>
    <div class="contact-stack">
      <div class="contact-item">
        <strong>{t("Leasing (primary)", "租務（主要）")}</strong>
        <a href="tel:+85227001122">+852 2700 1122</a><br>
        <a href="mailto:leasing@onedundashk.com">leasing@onedundashk.com</a>
      </div>
      <div class="contact-item">
        <strong>{t("Address", "地址")}</strong>
        1 Dundas Street, Mongkok, Kowloon, Hong Kong<br>
        香港九龍旺角登打士街1號
      </div>
      <div class="contact-item">
        <strong>{t("Book direct", "網上直訂")}</strong>
        <p class="muted">{t("Check live availability on SiteMinder Direct.", "於 SiteMinder Direct 查詢即時空房。")}</p>
        <a class="btn btn--accent" style="margin-top:.75rem" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
      </div>
      <div class="avail-bar avail-bar--stacked" style="box-shadow:none;border:1px solid var(--line);padding:1rem">
        <p style="margin:0 0 .75rem;font-weight:700">{t("Quick availability", "快速查房")}</p>
        <form data-avail-form>
          <div class="field">
            <label for="c-checkin">{t("Check-in", "入住")}</label>
            <input id="c-checkin" type="date" name="checkIn" required>
          </div>
          <div class="field">
            <label for="c-checkout">{t("Check-out", "退房")}</label>
            <input id="c-checkout" type="date" name="checkOut" required>
          </div>
          <button class="btn btn--primary btn--block" type="submit">{t("Book now", "立即預訂")}</button>
        </form>
      </div>
    </div>
  </div>
</section>
'''

FAQS = [
    ("Where is One Dundas located?", "One Dundas is at 1 Dundas Street, Mongkok, Kowloon, Hong Kong — about an 8-minute walk to Mongkok MTR Exit E1 / Langham Place and about 6 minutes to Yau Ma Tei MTR Exit A1.",
     "壹登位於哪裏？", "壹登位於香港九龍旺角登打士街1號，步行約8分鐘至旺角站 E1 出口／朗豪坊，約6分鐘至油麻地站 A1 出口。"),
    ("What apartment types are available?", "109 serviced apartments: Studio (249–280 sq ft, up to 2 guests), One-Bedroom (437–479 sq ft, up to 2 guests) and Two-Bedroom (544 sq ft, up to 3 guests).",
     "有哪些房型？", "共109間服務式公寓：開放式（249–280平方呎，最多2人）、單卧室（437–479平方呎，最多2人）及雙卧室（544平方呎，最多3人）。"),
    ("What is included in the rent?", "Rates include property management fee and service charges, government rates and taxes, and utilities (water, electricity and air-conditioning).",
     "租金包括甚麼？", "租金已包括物業管理費及服務費、差餉及稅項，以及水、電及空調費用。"),
    ("Is housekeeping provided?", "Yes. Housekeeping is provided twice a week (except Sundays) and linen is changed weekly.",
     "有沒有清潔服務？", "有。每週兩次清潔（星期日除外），每週更換床單。"),
    ("What facilities does One Dundas have?", "Outdoor gym and leisure area, self-service laundry, BBQ facilities rental, car parking rental, 24/7 concierge and security, and complimentary Wi-Fi. The building is non-smoking.",
     "有甚麼設施？", "戶外健身及休憩區、自助洗衣、燒烤爐租用、泊車位租用、24小時禮賓及保安，以及免費 Wi-Fi。全幢禁煙。"),
    ("Which universities are nearby?", "One Dundas offers convenient transport to The Hong Kong Polytechnic University, City University of Hong Kong, Hong Kong Baptist University and Hong Kong Metropolitan University.",
     "附近有哪些大學？", "交通便捷連接香港理工大學、香港城市大學、香港浸會大學及香港都會大學。"),
    ("How do I book or enquire?", "Book online via the direct booking engine, call leasing on +852 2700 1122, or email leasing@onedundashk.com.",
     "如何預訂或查詢？", "可透過網上直接預訂，或致電租務部 +852 2700 1122，或電郵 leasing@onedundashk.com。"),
]
faq_html = "\n".join(
    f'<details class="faq-item"><summary><h3 style="display:inline;font-size:1rem">{t(qe, qz)}</h3></summary><p>{t(ae, az)}</p></details>'
    for qe, ae, qz, az in FAQS)
contact_body += f'''
<section class="section section--tint" id="faq">
  <div class="container" style="max-width:48rem">
    <h2>{t("Frequently asked questions", "常見問題")}</h2>
    {faq_html}
  </div>
</section>
'''
FAQ_LD = {"@type": "FAQPage", "@id": SITE_URL + "contact.html#faq", "mainEntity": [
    {"@type": "Question", "name": qe, "acceptedAnswer": {"@type": "Answer", "text": ae}} for qe, ae, _, _ in FAQS]}

ADDRESS = {"@type": "PostalAddress", "streetAddress": "1 Dundas Street, Mongkok", "addressLocality": "Kowloon",
           "addressRegion": "Hong Kong", "addressCountry": "HK"}
ORG = {"@type": "Organization", "@id": SITE_URL + "#organization", "name": "One Dundas", "alternateName": "壹登",
       "url": SITE_URL, "logo": SITE_URL + "assets/images/logo.png", "email": "leasing@onedundashk.com",
       "telephone": "+852 2700 1122", "address": ADDRESS}
WEBSITE = {"@type": "WebSite", "@id": SITE_URL + "#website", "url": SITE_URL, "name": "One Dundas",
           "inLanguage": ["en", "zh-Hant"], "publisher": {"@id": SITE_URL + "#organization"}}
_AMEN = ["Outdoor gym", "Outdoor leisure area", "Self-service laundry", "BBQ facilities rental", "Car parking rental",
         "Housekeeping twice weekly", "Weekly linen change", "Complimentary Wi-Fi", "24/7 concierge and security",
         "Kitchenette", "4K smart TV", "Electronic safe", "Non-smoking property"]
HOTEL = {"@type": ["Hotel", "LodgingBusiness"], "@id": SITE_URL + "#hotel", "name": "One Dundas Serviced Apartments",
         "alternateName": "壹登服務式公寓", "url": SITE_URL, "telephone": "+852 2700 1122", "email": "leasing@onedundashk.com",
         "address": ADDRESS, "image": [SITE_URL + OG_IMAGE, SITE_URL + "assets/images/hero-lobby.jpg"],
         "description": "109 serviced Studio, One-Bedroom and Two-Bedroom apartments at 1 Dundas Street, Mongkok, Kowloon.",
         "numberOfRooms": 109, "smokingAllowed": False, "hasMap": "https://www.google.com/maps?q=1+Dundas+Street,+Mongkok,+Kowloon,+Hong+Kong",
         "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": a, "value": True} for a in _AMEN],
         "parentOrganization": {"@id": SITE_URL + "#organization"}}

# ===================== PRIVACY =====================
privacy_body = f'''
<section class="page-hero"><div class="container">
  <h1 class="eyebrow">{t("Privacy", "私隱政策")}</h1>
</div></section>
<section class="section"><div class="container legal">
  <p>{t("We, One Dundas, respect your privacy and have formulated this statement outlining practices in relation to collection, use, retention, disclosure, transfer, security and accessibility of your personal information.", "壹登尊重您的私隱，並制訂本聲明說明有關收集、使用、保留、披露、轉移、保安及查閱個人資料的做法。")}</p>
  <h2>{t("Purpose of collection", "收集目的")}</h2>
  <p>{t("Information collected via this website (including enquiry forms) is used to respond to your requests, process bookings and improve our services. We do not sell your personal data.", "經本網站（包括查詢表格）收集的資料，用於回覆您的要求、處理預訂及改善服務。我們不會出售您的個人資料。")}</p>
  <h2>{t("Contact", "聯絡")}</h2>
  <p>One Dundas<br>1 Dundas Street, Mongkok, Kowloon, Hong Kong<br>Tel: +852 2700 1122<br>Email: leasing@onedundashk.com</p>
  <p class="muted">{t("This is a simplified stub for the static revamp. Replace with counsel-approved full text before production launch.", "此為靜態重建版之簡化摘要。正式上線前請以法律顧問審定全文取代。")}</p>
</div></section>
'''

# ===================== DISCLAIMER =====================
disclaimer_body = f'''
<section class="page-hero"><div class="container">
  <h1 class="eyebrow">{t("Disclaimer", "免責聲明")}</h1>
</div></section>
<section class="section"><div class="container legal">
  <p>{t("Before using this website, please read these terms carefully. By using this website you signify that you have read and accept the terms below.", "使用本網站前請細閱下列條款。使用本網站即表示您已閱讀並接受以下條款。")}</p>
  <p>{t("One Dundas reserves the right to change these terms at any time. Information on this site is provided for general reference; apartment availability, rates and promotions are subject to confirmation by leasing.", "壹登保留隨時修改條款的權利。本站資料僅供一般參考；公寓供應、租金及推廣優惠以租務確認為準。")}</p>
  <p>{t("External links (including the SiteMinder booking engine) are provided for convenience; One Dundas is not responsible for third-party sites.", "外部連結（包括 SiteMinder 預訂系統）僅為方便而提供；壹登對第三方網站概不負責。")}</p>
  <p>{t("Whenever there is a discrepancy between the English and Chinese versions of these terms, the English version shall prevail.", "中英文版本如有歧異，概以英文版本為準。")}</p>
  <p class="muted">{t("This is a simplified stub for the static revamp. Replace with counsel-approved full text before production launch.", "此為靜態重建版之簡化摘要。正式上線前請以法律顧問審定全文取代。")}</p>
</div></section>
'''

PAGES = [
    ("index.html", "Home", "One Dundas | Serviced Apartments in Mongkok, Hong Kong", "壹登 | 旺角服務式公寓",
     "109 serviced Studio, One-Bedroom and Two-Bedroom apartments at 1 Dundas Street, Mongkok, Kowloon. Rates include utilities; book direct.", index_body),
    ("about.html", "About", "About One Dundas | Mongkok Serviced Apartments", "關於我們 | 壹登",
     "About One Dundas: 109 serviced apartments on the residential side of Mongkok with outdoor gym, leisure area, laundry and twice-weekly housekeeping.", about_body),
    ("accommodation.html", "Accommodation", "Studio, 1-Bedroom & 2-Bedroom Apartments | One Dundas", "住宿 | 壹登",
     "Compare One Dundas apartments: Studio 249–280 sq ft, One-Bedroom 437–479 sq ft, Two-Bedroom 544 sq ft, with kitchenette and 4K smart TV.", accom_body),
    ("location.html", "Location", "Location & Transport near Mongkok MTR | One Dundas", "位置 | 壹登",
     "Map and directions to One Dundas, 1 Dundas Street, Mongkok — walking times to Mongkok and Yau Ma Tei MTR, shopping, banks and universities.", location_body),
    ("promotion.html", "Promotion", PROMO_TITLE, "推廣 | 壹登", PROMO_DESC, promo_body),
    ("gallery.html", "Gallery", "Photo Gallery | One Dundas Serviced Apartments", "相片集 | 壹登",
     "Photos of One Dundas Studio, One-Bedroom and Two-Bedroom interiors, lobby, building exterior, gym and leisure area.", gallery_body),
    ("virtual-tour.html", "Virtual Tour", "360° Virtual Tour of Apartments | One Dundas", "虛擬導覽 | 壹登",
     "Take a 360° virtual tour of One Dundas Studio, One-Bedroom and Two-Bedroom apartments, then request a viewing.", vtour_body),
    ("contact.html", "Enquiry", "Enquiry & FAQ | Contact One Dundas Leasing", "查詢 | 壹登",
     "Contact One Dundas leasing on +852 2700 1122 or leasing@onedundashk.com. Enquiry form and FAQ on location, rates, housekeeping and facilities.", contact_body),
    ("privacy.html", "Privacy", "Privacy Statement | One Dundas", "私隱政策 | 壹登",
     "Privacy statement for the One Dundas website.", privacy_body),
    ("disclaimer.html", "Disclaimer", "Disclaimer | One Dundas", "免責聲明 | 壹登",
     "Website disclaimer for One Dundas.", disclaimer_body),
]
NOINDEX = {"privacy.html", "disclaimer.html"}

for name, crumb, te, tz, desc, body in PAGES:
    write(name, page(te, tz, desc, body, name=name, crumb=crumb, noindex=name in NOINDEX))

# sitemap / robots / llms.txt
from datetime import date
urls = "".join(f"  <url><loc>{SITE_URL if n == 'index.html' else SITE_URL + n}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n"
               for n, *_ in PAGES if n not in NOINDEX)
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
        "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "CCBot", "Bingbot", "Googlebot"]
robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
(ROOT / "robots.txt").write_text(f"{robots}User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
links = "\n".join(f"- [{te}]({SITE_URL if n == 'index.html' else SITE_URL + n}): {d}" for n, _, te, _, d, _ in PAGES if n not in NOINDEX)
faq_md = "\n".join(f"- **{q}** {a}" for q, a, _, _ in FAQS)
(ROOT / "llms.txt").write_text(f"""# One Dundas Serviced Apartments (壹登)

> 109 serviced Studio, One-Bedroom and Two-Bedroom apartments at 1 Dundas Street, Mongkok, Kowloon, Hong Kong (香港九龍旺角登打士街1號). Bilingual site (English / 繁體中文).

## Key facts
- Address: 1 Dundas Street, Mongkok, Kowloon, Hong Kong
- Phone: +852 2700 1122 · Email: leasing@onedundashk.com
- Apartments: Studio 249–280 sq ft (19–29/F, 2 guests); One-Bedroom 437–479 sq ft (19–35/F, 2 guests); Two-Bedroom 544 sq ft (19–35/F, 3 guests)
- Rates include management fee, government rates and utilities (water, electricity, air-conditioning)
- Housekeeping twice weekly (except Sundays), linen weekly; outdoor gym & leisure area; self-service laundry; BBQ and car park rental; 24/7 concierge & security; non-smoking
- Transport: ~8 min walk to Mongkok MTR Exit E1 / Langham Place; ~6 min to Yau Ma Tei MTR Exit A1
- Direct booking: {BOOK}
{promo_llms()}

## Pages
{links}

## FAQ
{faq_md}
""", encoding="utf-8")

print("DONE", len(PAGES), "pages")
