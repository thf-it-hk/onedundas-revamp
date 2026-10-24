# One Dundas — Static Site Revamp

Modern bilingual (Traditional Chinese + English) static rebuild of [onedundashk.com](https://onedundashk.com/) for Sunny Leung.

**Does not touch production.** This folder is a standalone static site.

## Stack

- Plain HTML / CSS / JS (no build step required)
- Shared design system: purple brand (`#87768b` / `#6b2d7b`), **Open Sans** + **Source Sans Pro** (matching original site) + Noto Sans TC for 繁
- Header brand shows **logo image only** (transparent `assets/images/logo.png`); accessible name via `alt` + `.visually-hidden`
- Top nav labels use CSS `text-transform: uppercase` (EN); Chinese unaffected
- Language switch via `localStorage` + `html[lang]` (EN / 繁) — separate strings, not mid-sentence WPML stacking
- Images downloaded under `assets/images/` for offline preview


## Language default

- **First visit** (no `localStorage` key `onedundas-lang`): default **English**.
- If `navigator.language` / `navigator.languages` indicates Chinese (`zh-HK`, `zh-TW`, `zh-Hant`, and optionally `zh-CN` / `zh` / `zh-Hans`), start in **繁**.
- After the user toggles EN / 繁, the choice is stored in `localStorage` (`onedundas-lang` = `en` or `zh-Hant`) and reused on later visits.
- Implementation: `assets/js/main.js` → `prefersChineseFromSystem()` + `initLang()`.

## Pages

| File | Purpose |
|------|---------|
| `index.html` | Home + availability bar → SiteMinder |
| `about.html` | About / facilities |
| `accommodation.html` | Studio / 1BR / 2BR |
| `location.html` | Map (Google embed) + neighbourhood (Bank of China 中國銀行 corrected) |
| `promotion.html` | BOOKEARLY early bird (until 2026-11-30, up to 8%) |
| `gallery.html` | Photo gallery |
| `virtual-tour.html` | Placeholder (old embeds unavailable) + CTAs |
| `contact.html` | Full enquiry form + quick availability |
| `privacy.html` | Privacy stub |
| `disclaimer.html` | Disclaimer stub |

## Preview locally

From this directory:

```bash
cd /workspace/onedundas-revamp
npx --yes serve -p 4173
# or:
python3 -m http.server 4173
```

Open http://localhost:4173/

## Book Now → SiteMinder deep links

Booking engine:

`https://book-directonline.com/properties/OneDundasDirect/`

Homepage / contact **Check Availability** widgets build:

```
?checkInDate=YYYY-MM-DD
&checkOutDate=YYYY-MM-DD
&items[0][adults]=2
&items[0][children]=0
&items[0][infants]=0
&locale=en|zh_TW
&currency=HKD
&promocode=...   (optional)
```

These parameter names match the common **SiteMinder Direct / book-directonline.com** pattern (`checkInDate` / `checkOutDate`). **Please verify once** on the live engine that pre-filled dates appear correctly; if SiteMinder ever changes the contract, update `assets/js/main.js` → `buildSiteMinderUrl()`.

Plain “Book Now” buttons open the same base URL; if an availability form is present on the page, they reuse those dates.

## Enquiry form

`contact.html` includes a real form (not mailto-only UI):

- Fields aligned with the old site: first/last name, company, phone, email, adults/children, budget, apartment type, arrival/departure, remarks, how-heard
- Marketing opt-in checkbox **not** pre-checked
- Client-side validation
- Submit: [Web3Forms](https://web3forms.com) — `POST https://api.web3forms.com/submit`
  - Access key (public, client-safe) is the single constant `WEB3FORMS_ACCESS_KEY` in `_build/generate.py`
  - Hidden fields: `access_key`, `subject` ("New enquiry from onedundashk.com website"), `from_name` ("One Dundas Website"), `redirect`, plus honeypot `botcheck` (hidden checkbox)
  - With JS: `assets/js/main.js` validates, then sends all fields as JSON via `fetch` (adds `name` and `replyto` = visitor email), disables the button while sending, and shows inline EN/繁中 success or error (error falls back to leasing@onedundashk.com / +852 2700 1122)
  - Without JS: normal form POST; Web3Forms redirects to `ENQUIRY_REDIRECT` (`contact.html#thank-you`). Update that constant to the production URL at DNS cutover

Primary leasing contact used throughout: **+852 2700 1122** / **leasing@onedundashk.com**

## Deploy (static host)

Any static host works. Examples:

### Cloudflare Pages

```bash
# Dashboard: Create project → Upload assets, or connect git
# Build command: (none)
# Output directory: .   (this folder)
```

### Netlify

```bash
npx netlify deploy --dir=/workspace/onedundas-revamp --prod
# Or drag-and-drop the folder in Netlify UI
```

### nginx / Apache / S3 / GitHub Pages

Serve the folder as document root. No PHP/Node required at runtime.

Optional: add `_redirects` (Netlify) or `public/_routes.json` only if you later introduce pretty URLs.

## Regenerating HTML

Shared header/footer live in `_build/generate.py`. After editing copy there:

```bash
python3 _build/generate.py
```

## Intentional omissions / next steps for Sunny

1. **Virtual tour embeds** — old WP page had no working Matterport/iframe URLs; page links to gallery + enquiry. Drop in embed URLs when available.
2. **Privacy / Disclaimer** — simplified stubs; replace with counsel-approved full text before production cutover.
3. **Enquiry backend** — Web3Forms (see Enquiry form). Update `ENQUIRY_REDIRECT` at cutover.
4. **News / Media Room CMS** — gallery only; no news posts (would need a static content folder or headless CMS).
5. **Do not point DNS** at this build until content sign-off; production `onedundashk.com` is untouched.
6. **Verify SiteMinder date params** on a test booking with real check-in/out dates.
7. Optional: add Open Graph images, favicon set, and compress hero images further with `sharp`/`imagemin` if needed.

## Brand notes

- Purple primary from legacy theme: `#87768b`, deep CTA `#6b2d7b`, accent orange `#fb8e03`
- Fonts: Open Sans + Source Sans Pro (Google Fonts HTTPS), Noto Sans TC for CJK; button text uses dark on light/orange/white and light only on deep purple
- Address: 1 Dundas Street, Mongkok, Kowloon, Hong Kong
- ~109 units: Studio / 1BR / 2BR
