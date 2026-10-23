#!/usr/bin/env python3
"""Generate One Dundas static HTML pages."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BOOK = "https://book-directonline.com/properties/OneDundasDirect/"

def t(en, zh):
    """Bilingual inline span pair."""
    return f'<span class="i18n-en" data-i18n-en>{en}</span><span class="i18n-zh" data-i18n-zh>{zh}</span>'

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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Open+Sans:wght@400;600;700&family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/styles.css">
  <link rel="icon" href="assets/images/logo.png">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="index.html" aria-label="One Dundas">
        <img src="assets/images/logo.png" width="78" height="78" alt="One Dundas">
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
        <strong>One Dundas 壹登</strong>
        <p>1 Dundas Street, Mongkok, Kowloon, Hong Kong<br>九龍旺角登打士街1號</p>
        <p>
          <a href="tel:+85227001122">+852 2700 1122</a><br>
          <a href="mailto:leasing@onedundashk.com">leasing@onedundashk.com</a>
        </p>
      </div>
      <div class="footer-col">
        <h3>{explore}</h3>
        <ul>
          <li><a href="about.html">{about}</a></li>
          <li><a href="accommodation.html">{accom}</a></li>
          <li><a href="location.html">{location}</a></li>
          <li><a href="promotion.html">{promo}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3>{stay}</h3>
        <ul>
          <li><a href="gallery.html">{gallery}</a></li>
          <li><a href="virtual-tour.html">{vtour}</a></li>
          <li><a href="contact.html">{contact}</a></li>
          <li><a href="{book}" target="_blank" rel="noopener noreferrer">{book_label}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h3>{legal}</h3>
        <ul>
          <li><a href="privacy.html">{privacy}</a></li>
          <li><a href="disclaimer.html">{disclaimer}</a></li>
        </ul>
      </div>
    </div>
    <div class="container footer-bottom">
      <span>© 2026 One Dundas. All rights reserved.</span>
      <span>{footer_note}</span>
    </div>
  </footer>
  <script src="assets/js/main.js" defer></script>
</body>
</html>
'''

NAV = {
    "home": t("Home", "首頁"),
    "about": t("About", "關於我們"),
    "accom": t("Accommodation", "住宿"),
    "location": t("Location", "位置"),
    "promo": t("Promotion", "推廣"),
    "gallery": t("Gallery", "相片集"),
    "vtour": t("Virtual Tour", "虛擬導覽"),
    "contact": t("Enquiry", "查詢"),
    "book_label": t("Book Now", "立即預訂"),
    "explore": t("Explore", "探索"),
    "stay": t("Stay", "住宿相關"),
    "legal": t("Legal", "法律資訊"),
    "privacy": t("Privacy", "私隱政策"),
    "disclaimer": t("Disclaimer", "免責聲明"),
    "footer_note": t("Serviced apartments in Mongkok", "旺角服務式公寓"),
    "book": BOOK,
}

def page(title_en, title_zh, desc, body):
    head = HEADER.format(title_en=title_en, title_zh=title_zh, desc=desc, **NAV)
    foot = FOOTER.format(**NAV)
    return head + body + foot

def write(name, html):
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
index_body = f'''
<section class="hero">
  <div class="hero__media" style="background-image:url('assets/images/hero-lobby.jpg')" role="img" aria-label="One Dundas lobby"></div>
  <div class="container hero__content">
    <p class="eyebrow">{t("Serviced Apartments · Mongkok", "服務式公寓 · 旺角")}</p>
    <h1>{t("Your home in the heart of Kowloon", "九龍核心的都市居所")}</h1>
    <p class="lead">{t("109 stylish Studio, One-Bedroom and Two-Bedroom apartments at 1 Dundas Street — steps from Mongkok’s markets, MTR and city life.", "壹登提供109間時尚開放式、單卧室及雙卧室公寓，位於登打士街1號，步行即達旺角市集、港鐵與繁華街景。")}</p>
    <div class="btn-row">
      <a class="btn btn--accent" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
      <a class="btn btn--light" href="contact.html">{t("Enquire", "立即查詢")}</a>
    </div>
    {AVAIL}
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="promo-banner">
      <div>
        <p class="eyebrow" style="color:#f5d9ff">{t("Limited offer", "限時優惠")}</p>
        <h2>{t("Early Bird: up to 8% off monthly packages", "早鳥優惠：月租計劃高達 8% 折扣")}</h2>
        <p>{t("Book by 30 November 2026 and quote", "於 2026年11月30日前預訂，並提供折扣碼")} <span class="promo-code">BOOKEARLY</span> {t("for up to 8% off. Call leasing for details.", "即可享高達 8% 折扣。詳情請聯絡租務部。")}</p>
        <div class="btn-row">
          <a class="btn btn--light" href="promotion.html">{t("View promotion", "查看推廣")}</a>
          <a class="btn btn--ghost" style="border-color:#fff;color:#fff" href="tel:+85227001122">+852 2700 1122</a>
        </div>
      </div>
      <div>
        <img src="assets/images/promo.jpg" alt="One Dundas promotion" style="border-radius:12px;width:100%;object-fit:cover;max-height:220px">
      </div>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    <p class="eyebrow">{t("Apartments", "公寓")}</p>
    <h2>{t("Find your space", "選擇合適房型")}</h2>
    <p class="lead">{t("Floor-to-ceiling windows, kitchenettes and thoughtful amenities — designed for singles, students and small families.", "大片落地玻璃窗、設備齊全的廚房與貼心設施，適合單身、海外學生與小家庭。")}</p>
    <div class="grid-3" style="margin-top:2rem">
      <article class="card">
        <img src="assets/images/studio-a.jpg" alt="Studio apartment living area">
        <div class="card__body">
          <h3>{t("Studio", "開放式公寓")}</h3>
          <p class="card__meta">249–280 sq ft · 19–29/F</p>
          <p>{t("Compact and cosy with city views, queen bed and well-equipped kitchenette.", "舒適精巧，飽覽城市景觀，配備加大雙人床與設備齊全的廚房。")}</p>
          <a class="btn btn--ghost" href="accommodation.html#studio">{t("Details", "了解詳情")}</a>
        </div>
      </article>
      <article class="card">
        <img src="assets/images/1br-living.jpg" alt="One-bedroom apartment living area">
        <div class="card__body">
          <h3>{t("One-Bedroom", "單卧室公寓")}</h3>
          <p class="card__meta">437–479 sq ft · 19–35/F</p>
          <p>{t("Separate bedroom and living area with work space and harbour or city views.", "獨立睡房與客廳，設工作區，可賞海景或城市景觀。")}</p>
          <a class="btn btn--ghost" href="accommodation.html#one-bedroom">{t("Details", "了解詳情")}</a>
        </div>
      </article>
      <article class="card">
        <img src="assets/images/twobed-living.jpg" alt="Two-bedroom apartment living area">
        <div class="card__body">
          <h3>{t("Two-Bedroom", "雙卧室公寓")}</h3>
          <p class="card__meta">544 sq ft · 19–35/F</p>
          <p>{t("Master suite plus guest room, in-room washer & dryer — ideal for families.", "主人房連套房浴室與客房，房內洗衣乾衣機，適合家庭。")}</p>
          <a class="btn btn--ghost" href="accommodation.html#two-bedroom">{t("Details", "了解詳情")}</a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container grid-2">
    <div>
      <p class="eyebrow">{t("Why One Dundas", "為何選擇壹登")}</p>
      <h2>{t("Urban calm, steps from Mongkok energy", "繁華旺角旁的寧靜居所")}</h2>
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
      <img src="assets/images/hero-eco.jpg" alt="One Dundas apartment interior" style="border-radius:16px;box-shadow:var(--shadow-lg)">
    </div>
  </div>
</section>

<section class="section section--tint">
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
    <p class="eyebrow">{t("About", "關於")}</p>
    <h1>{t("About One Dundas", "關於壹登")}</h1>
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
      <div class="card"><img src="assets/images/gym.jpg" alt="Gymnasium"><div class="card__body"><h3>{t("Outdoor gym", "戶外健身")}</h3><p>{t("Stay active at the outdoor gym facilities.", "使用戶外健身設施保持活力。")}</p></div></div>
      <div class="card"><img src="assets/images/leisure.jpg" alt="Leisure area"><div class="card__body"><h3>{t("Leisure area", "休憩空間")}</h3><p>{t("Outdoor leisure spaces for unwinding after a busy day.", "戶外休憩區，讓你在忙碌一天後放鬆。")}</p></div></div>
      <div class="card"><img src="assets/images/hero-lobby.jpg" alt="Lobby"><div class="card__body"><h3>{t("Concierge", "禮賓服務")}</h3><p>{t("Concierge and security for peace of mind.", "禮賓與保安服務，安心無憂。")}</p></div></div>
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
      <img src="{img}" alt="{title_en}" style="border-radius:16px;box-shadow:var(--shadow)">
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
    <p class="eyebrow">{t("Accommodation", "住宿")}</p>
    <h1>{t("Apartments", "房間")}</h1>
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
    <p class="eyebrow">{t("Location", "位置")}</p>
    <h1>{t("Map & neighbourhood", "地圖與周邊")}</h1>
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
      <img src="assets/images/neighbourhood.jpg" alt="Mongkok neighbourhood" style="border-radius:16px;margin-bottom:1rem">
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
promo_body = f'''
<section class="page-hero">
  <div class="container">
    <p class="eyebrow">{t("Promotion", "推廣活動")}</p>
    <h1>{t("Current offers", "最新優惠")}</h1>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="promo-banner">
      <div>
        <h2>{t("Early Bird Special: up to 8% off monthly packages", "限時早鳥優惠：月租計劃專享高達 8% 折扣")}</h2>
        <p>{t("Enjoy exclusive savings with our early bird offer! Book any designated monthly stay plan on or before 30 November 2026 and quote the promo code", "把握限時禮遇！由即日起至2026年11月30日前預訂指定月租計劃，並於預訂時提供折扣碼")} <span class="promo-code">BOOKEARLY</span> {t("to receive up to 8% discount. Limited availability!", "即可尊享高達 8% 租金折扣。名額有限！")}</p>
        <div class="btn-row">
          <a class="btn btn--light" href="{BOOK}" data-book-now target="_blank" rel="noopener noreferrer">{t("Book Now", "立即預訂")}</a>
          <a class="btn btn--ghost" style="border-color:#fff;color:#fff" href="tel:+85227001122">{t("Call leasing", "致電租務部")}</a>
        </div>
      </div>
      <div>
        <img src="assets/images/promo.jpg" alt="" style="border-radius:12px;width:100%">
      </div>
    </div>
    <div style="margin-top:2.5rem;max-width:48rem">
      <h2>{t("Terms & conditions", "條款與細則")}</h2>
      <ul class="feature-list">
        <li>{t("Discount applies to leases commencing between 1 January 2027 and 30 June 2027.", "此優惠適用於租期由2027年1月1日至2027年6月30日期間起租的合約。")}</li>
        <li>{t("Cannot be used in conjunction with any other promotions.", "此優惠不能與其他推廣優惠同時使用。")}</li>
        <li>{t("For enquiries, contact Leasing at +852 2700 1122 or leasing@onedundashk.com.", "如欲查詢，請致電 +852 2700 1122 或電郵 leasing@onedundashk.com 與租務部聯絡。")}</li>
      </ul>
    </div>
  </div>
</section>
'''

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
    f'<a href="assets/images/{fn}" data-lightbox><img src="assets/images/{fn}" alt="{alt}" loading="lazy"></a>'
    for fn, alt in GALLERY_IMGS
)
gallery_body = f'''
<section class="page-hero">
  <div class="container">
    <p class="eyebrow">{t("Media", "媒體")}</p>
    <h1>{t("Gallery", "相片集")}</h1>
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
    <p class="eyebrow">{t("Virtual Tour", "虛擬導覽")}</p>
    <h1>{t("Explore our apartments", "探索公寓")}</h1>
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
<script src="assets/vt/pannellum/pannellum.js"></script>
'''

# ===================== CONTACT / ENQUIRY =====================
contact_body = f'''
<section class="page-hero">
  <div class="container">
    <p class="eyebrow">{t("Contact", "聯絡")}</p>
    <h1>{t("Enquiry", "查詢")}</h1>
    <p class="lead">{t("Tell us about your stay. Our leasing team will follow up.", "告訴我們您的入住需要，租務團隊會與您跟進。")}</p>
  </div>
</section>
<section class="section">
  <div class="container grid-2" style="align-items:start">
    <div class="form-card">
      <div class="form-success" data-enquiry-success tabindex="-1" role="status">
        {t("Thanks — your mail client should open with the enquiry. If it does not, please email leasing@onedundashk.com directly.", "謝謝 — 系統將開啟電郵程式載入查詢內容。如未成功，請直接電郵 leasing@onedundashk.com。")}
      </div>
      <form data-enquiry-form novalidate
            action="mailto:leasing@onedundashk.com" method="post" enctype="text/plain"
            data-formspree-endpoint="">
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
        <button class="btn btn--primary btn--block" type="submit">{t("Send enquiry", "送出查詢")}</button>
        <!-- Enquiry uses mailto to leasing@onedundashk.com (see README).
             To wire Formspree later: set data-formspree-endpoint="https://formspree.io/f/xxxx" on this form. -->
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

# ===================== PRIVACY =====================
privacy_body = f'''
<section class="page-hero"><div class="container">
  <h1>{t("Privacy Statement", "私隱政策")}</h1>
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
  <h1>{t("Disclaimer", "免責聲明")}</h1>
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
    ("index.html", "One Dundas | Serviced Apartments in Mongkok", "壹登 | 旺角服務式公寓",
     "One Dundas serviced apartments at 1 Dundas Street, Mongkok — Studio, 1BR and 2BR.", index_body),
    ("about.html", "About | One Dundas", "關於我們 | 壹登",
     "About One Dundas serviced apartments in Mongkok, Hong Kong.", about_body),
    ("accommodation.html", "Accommodation | One Dundas", "住宿 | 壹登",
     "Studio, One-Bedroom and Two-Bedroom serviced apartments at One Dundas.", accom_body),
    ("location.html", "Location | One Dundas", "位置 | 壹登",
     "Map, transport and neighbourhood guide for One Dundas, Mongkok.", location_body),
    ("promotion.html", "Promotion | One Dundas", "推廣 | 壹登",
     "Early bird BOOKEARLY promotion — up to 8% off monthly packages.", promo_body),
    ("gallery.html", "Gallery | One Dundas", "相片集 | 壹登",
     "Photo gallery of One Dundas apartments and facilities.", gallery_body),
    ("virtual-tour.html", "Virtual Tour | One Dundas", "虛擬導覽 | 壹登",
     "Explore One Dundas apartment types and request a viewing.", vtour_body),
    ("contact.html", "Enquiry | One Dundas", "查詢 | 壹登",
     "Enquire about One Dundas serviced apartments — leasing team contact and form.", contact_body),
    ("privacy.html", "Privacy Statement | One Dundas", "私隱政策 | 壹登",
     "Privacy statement for One Dundas website.", privacy_body),
    ("disclaimer.html", "Disclaimer | One Dundas", "免責聲明 | 壹登",
     "Website disclaimer for One Dundas.", disclaimer_body),
]

for name, te, tz, desc, body in PAGES:
    write(name, page(te, tz, desc, body))

print("DONE", len(PAGES), "pages")
