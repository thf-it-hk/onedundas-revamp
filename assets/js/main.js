(function () {
  "use strict";

  var BOOK_BASE = "https://book-directonline.com/properties/OneDundasDirect/";
  var STORAGE_LANG = "onedundas-lang";

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  /* ---------- Language (en / zh-Hant / zh-Hans) ---------- */
  function normalizeLang(lang) {
    if (!lang) return "en";
    var raw = String(lang).toLowerCase().replace(/_/g, "-");
    if (raw === "zh-hans" || raw === "zh-cn" || raw === "zh-sg" || raw === "zh-my") return "zh-Hans";
    if (raw === "zh" || raw === "zh-hant" || raw === "zh-hk" || raw === "zh-tw" || raw === "zh-mo") return "zh-Hant";
    if (raw === "en" || raw.indexOf("en-") === 0) return "en";
    return "en";
  }

  function langKeyFromNormalized(normalized) {
    if (normalized === "zh-Hans") return "zh-Hans";
    if (normalized === "zh-Hant") return "zh";
    return "en";
  }

  function applySelectOptions(normalized) {
    $all("select option[data-label-en]").forEach(function (opt) {
      var en = opt.getAttribute("data-label-en") || "";
      var zh = opt.getAttribute("data-label-zh") || en;
      var hans = opt.getAttribute("data-label-zh-hans") || zh;
      if (normalized === "zh-Hans") opt.textContent = hans;
      else if (normalized === "zh-Hant") opt.textContent = zh;
      else opt.textContent = en;
    });
  }

  function applyLang(lang) {
    var normalized = normalizeLang(lang);
    var langKey = langKeyFromNormalized(normalized);
    document.documentElement.lang = normalized;
    document.documentElement.setAttribute("data-lang", langKey);
    try { localStorage.setItem(STORAGE_LANG, normalized); } catch (e) {}
    // Keep URL shareable without breaking existing bookmarks
    try {
      var url = new URL(location.href);
      if (url.searchParams.get("lang") !== normalized) {
        url.searchParams.set("lang", normalized);
        history.replaceState(null, "", url.pathname + url.search + url.hash);
      }
    } catch (e) {}
    $all("[data-lang-btn]").forEach(function (btn) {
      var btnLang = normalizeLang(btn.getAttribute("data-lang-btn"));
      var isActive = btnLang === normalized;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
    var titleEl = document.querySelector("title");
    if (titleEl) {
      var en = titleEl.getAttribute("data-title-en");
      var zh = titleEl.getAttribute("data-title-zh");
      var hans = titleEl.getAttribute("data-title-zh-hans") || zh;
      if (en && zh) {
        if (normalized === "zh-Hans") titleEl.textContent = hans || zh;
        else if (normalized === "zh-Hant") titleEl.textContent = zh;
        else titleEl.textContent = en;
      }
    }
    applySelectOptions(normalized);
    refreshFlatpickrLocales();
  }

  function prefersLangFromSystem() {
    var list = [];
    try {
      if (navigator.languages && navigator.languages.length) {
        list = Array.prototype.slice.call(navigator.languages);
      } else if (navigator.language) {
        list = [navigator.language];
      }
    } catch (e) {}
    for (var i = 0; i < list.length; i++) {
      var raw = String(list[i] || "").toLowerCase().replace(/_/g, "-");
      if (!raw) continue;
      if (raw.indexOf("zh-cn") === 0 || raw.indexOf("zh-hans") === 0 || raw.indexOf("zh-sg") === 0) {
        return "zh-Hans";
      }
      if (
        raw === "zh" ||
        raw.indexOf("zh-hk") === 0 ||
        raw.indexOf("zh-tw") === 0 ||
        raw.indexOf("zh-hant") === 0 ||
        raw.indexOf("zh-mo") === 0
      ) {
        return "zh-Hant";
      }
    }
    return "en";
  }

  function initLang() {
    var saved = null;
    var fromQuery = null;
    try {
      var q = new URL(location.href).searchParams.get("lang");
      if (q) fromQuery = normalizeLang(q);
    } catch (e) {}
    try { saved = localStorage.getItem(STORAGE_LANG); } catch (e) {}
    var initial;
    if (fromQuery) {
      initial = fromQuery;
    } else if (saved === "en" || saved === "zh-Hant" || saved === "zh-Hans" || saved === "zh") {
      initial = normalizeLang(saved);
    } else {
      initial = prefersLangFromSystem();
    }
    applyLang(initial);
    $all("[data-lang-btn]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyLang(btn.getAttribute("data-lang-btn"));
      });
    });
  }

  /* ---------- Mobile nav ---------- */
  function initNav() {
    var toggle = $("[data-nav-toggle]");
    var nav = $("[data-site-nav]");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    $all("a", nav).forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Date helpers + Flatpickr ---------- */
  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function toISODate(d) {
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }

  function parseISODate(s) {
    if (!s) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
    if (!m) return null;
    var d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
    return isNaN(d.getTime()) ? null : d;
  }

  function addDays(d, n) {
    var x = new Date(d.getTime());
    x.setDate(x.getDate() + n);
    return x;
  }

  function currentLang() {
    return normalizeLang(document.documentElement.lang || "en");
  }

  function isZhLang() {
    var l = currentLang();
    return l === "zh-Hant" || l === "zh-Hans";
  }

  function fpLocale() {
    if (!window.flatpickr || !flatpickr.l10ns) return "default";
    var l = currentLang();
    if (l === "zh-Hans" && flatpickr.l10ns.zh) return flatpickr.l10ns.zh;
    if (l === "zh-Hant" && flatpickr.l10ns.zh_tw) return flatpickr.l10ns.zh_tw;
    return "default";
  }

  function fpAltFormat() {
    return isZhLang() ? "Y年m月d日" : "d/m/Y";
  }

  function setInputDate(el, d) {
    var fp = el && el._flatpickr;
    if (fp) {
      fp.setDate(d, false);
    } else if (el) {
      el.value = toISODate(d);
    }
  }

  function setInputMin(el, d) {
    var fp = el && el._flatpickr;
    if (fp) {
      fp.set("minDate", d);
    } else if (el) {
      el.min = toISODate(d);
    }
  }

  function setMinDates(checkInEl, checkOutEl) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    setInputMin(checkInEl, today);
    if (!checkInEl.value) {
      setInputDate(checkInEl, today);
    }
    var cin = parseISODate(checkInEl.value) || today;
    var minOut = addDays(cin, 1);
    setInputMin(checkOutEl, minOut);
    var cout = parseISODate(checkOutEl.value);
    if (!cout || cout <= cin) {
      // Default short stay (daily / SiteMinder path); monthly stays pick longer dates
      setInputDate(checkOutEl, addDays(cin, 3));
    }
  }

  function attachFlatpickr(el, onChange) {
    if (!el || !window.flatpickr) return null;
    if (el._flatpickr) return el._flatpickr;
    return flatpickr(el, {
      dateFormat: "Y-m-d",
      altInput: true,
      altFormat: fpAltFormat(),
      altInputClass: "flatpickr-alt",
      locale: fpLocale(),
      disableMobile: true,
      allowInput: false,
      monthSelectorType: "static",
      animate: true,
      onChange: function () {
        if (typeof onChange === "function") onChange();
      }
    });
  }

  function refreshFlatpickrLocales() {
    $all("input.js-date").forEach(function (el) {
      var fp = el._flatpickr;
      if (!fp) return;
      fp.set("locale", fpLocale());
      fp.set("altFormat", fpAltFormat());
    });
  }

  /* ---------- SiteMinder deep link ----------
     Confirmed pattern for book-directonline.com (SiteMinder Direct):
     checkInDate, checkOutDate as YYYY-MM-DD
     items[0][adults], items[0][children], items[0][infants]
     optional: promocode, locale, currency
  */
  function buildSiteMinderUrl(opts) {
    var params = new URLSearchParams();
    if (opts.checkIn) params.set("checkInDate", opts.checkIn);
    if (opts.checkOut) params.set("checkOutDate", opts.checkOut);
    params.set("items[0][adults]", String(opts.adults || 2));
    params.set("items[0][children]", String(opts.children || 0));
    params.set("items[0][infants]", "0");
    if (opts.promo) params.set("promocode", opts.promo);
    var loc = currentLang();
    var locale = loc === "zh-Hans" ? "zh_CN" : (loc === "zh-Hant" ? "zh_TW" : "en");
    params.set("locale", locale);
    params.set("currency", "HKD");
    return BOOK_BASE + "?" + params.toString();
  }

  function openBooking(opts) {
    var url = buildSiteMinderUrl(opts);
    window.open(url, "_blank", "noopener,noreferrer");
  }

  var MONTHLY_NIGHTS = 28;

  function nightsBetween(dIn, dOut) {
    return Math.round((dOut.getTime() - dIn.getTime()) / 86400000);
  }

  function buildEnquiryUrl(opts) {
    var params = new URLSearchParams();
    if (opts.checkIn) params.set("adate", opts.checkIn);
    if (opts.checkOut) params.set("ddate", opts.checkOut);
    if (opts.adults) params.set("adult", String(opts.adults));
    if (opts.children != null && opts.children !== "") params.set("child", String(opts.children));
    var q = params.toString();
    return "contact.html" + (q ? "?" + q : "") + "#enquiry-form";
  }

  function goEnquiry(opts) {
    window.location.href = buildEnquiryUrl(opts || {});
  }

  function readAvailDates(form) {
    form = form || $("[data-avail-form]");
    if (!form) return null;
    var checkIn = form.querySelector('[name="checkIn"], [name="checkin"]');
    var checkOut = form.querySelector('[name="checkOut"], [name="checkout"]');
    var adultsEl = form.querySelector('[name="adults"]');
    var childrenEl = form.querySelector('[name="children"]');
    if (!checkIn || !checkOut || !checkIn.value || !checkOut.value) return null;
    var dIn = parseISODate(checkIn.value);
    var dOut = parseISODate(checkOut.value);
    if (!dIn || !dOut || dOut <= dIn) return null;
    return {
      checkIn: checkIn.value,
      checkOut: checkOut.value,
      adults: adultsEl ? adultsEl.value : 2,
      children: childrenEl ? childrenEl.value : 0,
      nights: nightsBetween(dIn, dOut),
      form: form
    };
  }

  function alertInvalidDates() {
    var l = currentLang();
    var msg =
      l === "zh-Hans"
        ? "请选择有效的入住与退房日期（退房须晚于入住）。"
        : l === "zh-Hant"
          ? "請選擇有效的入住與退房日期（退房須晚於入住）。"
          : "Please choose valid check-in and check-out dates (check-out must be after check-in).";
    alert(msg);
  }

  function routeByNights(opts) {
    if (!opts || opts.nights == null) return;
    if (opts.nights >= MONTHLY_NIGHTS) {
      goEnquiry(opts);
    } else {
      openBooking(opts);
    }
  }

  /* ---------- Book now: daily vs monthly choice (Little Tai Hang pattern) ---------- */
  var bookChoiceLastFocus = null;
  var bookChoiceContext = null;

  function closeBookChoice() {
    var box = $("[data-book-choice]");
    if (!box) return;
    box.hidden = true;
    document.body.classList.remove("book-choice-open");
    bookChoiceContext = null;
    if (bookChoiceLastFocus && bookChoiceLastFocus.focus) bookChoiceLastFocus.focus();
  }

  function openBookChoice(trigger, presetDates) {
    var box = $("[data-book-choice]");
    if (!box) {
      // Fallback if modal missing: daily path
      if (presetDates && presetDates.nights >= MONTHLY_NIGHTS) goEnquiry(presetDates);
      else if (presetDates) openBooking(presetDates);
      else window.open(BOOK_BASE, "_blank", "noopener,noreferrer");
      return;
    }
    bookChoiceLastFocus = trigger || document.activeElement;
    bookChoiceContext = presetDates || readAvailDates() || null;
    box.hidden = false;
    document.body.classList.add("book-choice-open");
    var closeBtn = $("[data-book-choice-close]", box);
    if (closeBtn) closeBtn.focus();
  }

  function initBookChoice() {
    var box = $("[data-book-choice]");
    if (!box) return;
    $all("[data-book-choice-close]", box).forEach(function (el) {
      el.addEventListener("click", function () { closeBookChoice(); });
    });
    var daily = $("[data-book-choice-daily]", box);
    var monthly = $("[data-book-choice-monthly]", box);
    if (daily) {
      daily.addEventListener("click", function () {
        var opts = bookChoiceContext || readAvailDates() || {};
        closeBookChoice();
        openBooking({
          checkIn: opts.checkIn,
          checkOut: opts.checkOut,
          adults: opts.adults || 2,
          children: opts.children || 0
        });
      });
    }
    if (monthly) {
      monthly.addEventListener("click", function () {
        var opts = bookChoiceContext || readAvailDates() || {};
        closeBookChoice();
        goEnquiry(opts);
      });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && box && !box.hidden) {
        e.preventDefault();
        closeBookChoice();
      }
    });
  }

  function initAvailabilityWidgets() {
    $all("[data-avail-form]").forEach(function (form) {
      var checkIn = form.querySelector('[name="checkIn"], [name="checkin"]');
      var checkOut = form.querySelector('[name="checkOut"], [name="checkout"]');
      if (!checkIn || !checkOut) return;
      attachFlatpickr(checkIn, function () { setMinDates(checkIn, checkOut); });
      attachFlatpickr(checkOut);
      setMinDates(checkIn, checkOut);
      checkIn.addEventListener("change", function () { setMinDates(checkIn, checkOut); });

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var cin = checkIn.value;
        var cout = checkOut.value;
        var dIn = parseISODate(cin);
        var dOut = parseISODate(cout);
        if (!dIn || !dOut || dOut <= dIn) {
          alertInvalidDates();
          return;
        }
        var adultsEl = form.querySelector('[name="adults"]');
        var childrenEl = form.querySelector('[name="children"]');
        var promoEl = form.querySelector('[name="promocode"]');
        var opts = {
          checkIn: cin,
          checkOut: cout,
          adults: adultsEl ? adultsEl.value : 2,
          children: childrenEl ? childrenEl.value : 0,
          promo: promoEl && promoEl.value ? promoEl.value.trim() : "",
          nights: nightsBetween(dIn, dOut)
        };
        // Booking bar: nights decide destination (no modal)
        routeByNights(opts);
      });
    });

    // Header / CTA Book now → daily vs monthly choice panel
    $all("[data-book-now]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        var href = el.getAttribute("href") || "";
        if (href.indexOf("checkInDate=") !== -1) {
          window.open(href, "_blank", "noopener,noreferrer");
          return;
        }
        openBookChoice(el, readAvailDates());
      });
    });
  }

  /* ---------- Enquiry form ---------- */
  function setFieldError(fieldWrap, msg) {
    fieldWrap.classList.toggle("field--invalid", !!msg);
    var err = fieldWrap.querySelector(".field-error");
    if (err) err.textContent = msg || "";
  }

  function validateEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  }

  function initEnquiryForm() {
    var form = $("[data-enquiry-form]");
    if (!form) return;

    var checkIn = form.querySelector('[name="adate"]');
    var checkOut = form.querySelector('[name="ddate"]');
    if (checkIn && checkOut) {
      attachFlatpickr(checkIn, function () { setMinDates(checkIn, checkOut); });
      attachFlatpickr(checkOut);
      setMinDates(checkIn, checkOut);
    }
    if (checkIn) checkIn.addEventListener("change", function () { setMinDates(checkIn, checkOut); });

    // Prefill from ?adate=&ddate=&adult=&child= (monthly / booking-bar redirect)
    try {
      var qp = new URL(location.href).searchParams;
      function fillDate(el, key) {
        if (!el) return;
        var v = qp.get(key);
        if (v && parseISODate(v)) setInputDate(el, parseISODate(v));
      }
      fillDate(checkIn, "adate");
      fillDate(checkOut, "ddate");
      if (checkIn && checkOut) setMinDates(checkIn, checkOut);
      var adultEl = form.querySelector('[name="adult"]');
      var childEl = form.querySelector('[name="child"]');
      if (adultEl && qp.get("adult")) adultEl.value = qp.get("adult");
      if (childEl && qp.get("child")) childEl.value = qp.get("child");
    } catch (err) {}

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var lang = currentLang();
      var langZh = lang === "zh-Hant" || lang === "zh-Hans";
      var useHans = lang === "zh-Hans";
      var ok = true;

      function req(name, label) {
        var input = form.querySelector('[name="' + name + '"]');
        var wrap = input && input.closest(".field");
        if (!input || !wrap) return "";
        var val = (input.value || "").trim();
        if (!val || (input.classList.contains("js-date") && !parseISODate(val))) {
          setFieldError(wrap, langZh ? "請填寫" + label : label + " is required");
          ok = false;
          return "";
        }
        setFieldError(wrap, "");
        return val;
      }

      var firstname = req("firstname", useHans ? "名字" : (langZh ? "名字" : "First name"));
      var lastname = req("lastname", useHans ? "姓氏" : (langZh ? "姓氏" : "Last name"));
      var phone = req("phone", useHans ? "电话" : (langZh ? "電話" : "Phone"));
      var emailWrap = form.querySelector('[name="email"]').closest(".field");
      var email = (form.querySelector('[name="email"]').value || "").trim();
      if (!email || !validateEmail(email)) {
        setFieldError(emailWrap, useHans ? "请输入有效电邮" : (langZh ? "請輸入有效電郵" : "Please enter a valid email"));
        ok = false;
      } else setFieldError(emailWrap, "");

      var apartment = req("apartmenttype", useHans ? "公寓类型" : (langZh ? "公寓類型" : "Apartment type"));
      var adate = req("adate", useHans ? "预计入住日期" : (langZh ? "預計入住日期" : "Expected arrival"));
      var ddate = req("ddate", useHans ? "预计退房日期" : (langZh ? "預計退房日期" : "Expected departure"));

      if (adate && ddate) {
        var dIn = parseISODate(adate);
        var dOut = parseISODate(ddate);
        if (dIn && dOut && dOut <= dIn) {
          setFieldError(form.querySelector('[name="ddate"]').closest(".field"),
            useHans ? "退房日期须晚于入住日期" : (langZh ? "退房日期須晚於入住日期" : "Departure must be after arrival"));
          ok = false;
        }
      }

      if (!ok) {
        var firstInvalid = form.querySelector(".field--invalid input, .field--invalid select, .field--invalid textarea");
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      var company = (form.querySelector('[name="company"]').value || "").trim();
      var adult = (form.querySelector('[name="adult"]').value || "").trim();
      var child = (form.querySelector('[name="child"]').value || "").trim();
      var budget = (form.querySelector('[name="budget"]').value || "").trim();
      var remark = (form.querySelector('[name="remark"]').value || "").trim();
      var hear = (form.querySelector('[name="hear"]').value || "").trim();
      var marketing = form.querySelector('[name="marketing"]');
      var marketingYes = marketing && marketing.checked;

      var success = $("[data-enquiry-success]");
      var errorBox = $("[data-enquiry-error]");
      var btn = form.querySelector("[data-enquiry-submit]");
      if (success) success.classList.remove("is-visible");
      if (errorBox) errorBox.classList.remove("is-visible");

      var payload = {};
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.name === "redirect") return;
        if (el.type === "checkbox") {
          if (el.name === "botcheck") { if (el.checked) payload.botcheck = true; return; }
          payload[el.name] = el.checked ? "yes" : "no";
          return;
        }
        payload[el.name] = (el.value || "").trim();
      });
      payload.name = firstname + " " + lastname;
      payload.replyto = email;

      function setSending(on) {
        if (!btn) return;
        btn.disabled = on;
        btn.setAttribute("aria-busy", on ? "true" : "false");
        var idle = btn.querySelector("[data-label-idle]");
        var sending = btn.querySelector("[data-label-sending]");
        if (idle) idle.hidden = on;
        if (sending) sending.hidden = !on;
      }
      function show(box) {
        if (!box) return;
        box.classList.add("is-visible");
        if (box.focus) box.focus();
      }

      setSending(true);
      fetch(form.getAttribute("action"), {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload)
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (data) {
          if (!res.ok || !data || data.success !== true) throw new Error((data && data.message) || "Submit failed");
        });
      }).then(function () {
        form.reset();
        if (checkIn && checkOut) setMinDates(checkIn, checkOut);
        show(success);
      }).catch(function () {
        show(errorBox);
      }).then(function () {
        setSending(false);
      });
    });

    // No-JS POST redirects back to contact.html#thank-you
    if (location.hash === "#thank-you") {
      var s = $("[data-enquiry-success]");
      if (s) s.classList.add("is-visible");
    }
  }

  /* ---------- Current nav highlight ---------- */
  function initCurrentNav() {
    var path = location.pathname.split("/").pop() || "index.html";
    $all(".site-nav a[href]").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href || href.indexOf("http") === 0 || href.indexOf("mailto:") === 0) return;
      var file = href.split("/").pop().split("#")[0];
      if (file === path || (path === "" && file === "index.html")) {
        a.setAttribute("aria-current", "page");
      }
    });
  }


  /* ---------- Gallery lightbox ---------- */
  function initLightbox() {
    var links = $all("a[data-lightbox]");
    if (!links.length) return;
    var box = document.createElement("div");
    box.className = "lightbox"; box.hidden = true;
    box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true"); box.setAttribute("aria-label", "Image viewer");
    box.innerHTML = '<button type="button" class="lightbox__close" aria-label="Close">&times;</button>' +
      '<button type="button" class="lightbox__prev" aria-label="Previous image">&#8249;</button>' +
      '<figure><img alt=""><figcaption></figcaption></figure>' +
      '<button type="button" class="lightbox__next" aria-label="Next image">&#8250;</button>';
    document.body.appendChild(box);
    var img = $("img", box), cap = $("figcaption", box), idx = 0, lastFocus = null;
    var btns = $all("button", box);
    function show(i) {
      idx = (i + links.length) % links.length;
      var a = links[idx], alt = ($("img", a) || {}).alt || "";
      img.src = a.getAttribute("href"); img.alt = alt;
      cap.textContent = alt + " (" + (idx + 1) + " / " + links.length + ")";
    }
    function open(i) {
      lastFocus = document.activeElement; show(i); box.hidden = false;
      document.body.classList.add("lightbox-open"); btns[0].focus();
    }
    function close() {
      box.hidden = true; document.body.classList.remove("lightbox-open"); img.removeAttribute("src");
      if (lastFocus) lastFocus.focus();
    }
    links.forEach(function (a, i) {
      a.addEventListener("click", function (e) { e.preventDefault(); open(i); });
    });
    btns[0].addEventListener("click", close);
    btns[1].addEventListener("click", function () { show(idx - 1); });
    btns[2].addEventListener("click", function () { show(idx + 1); });
    box.addEventListener("click", function (e) { if (e.target === box || e.target.tagName === "FIGURE") close(); });
    document.addEventListener("keydown", function (e) {
      if (box.hidden) return;
      if (e.key === "Escape") { e.preventDefault(); close(); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); show(idx - 1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); show(idx + 1); }
      else if (e.key === "Tab") {
        var first = btns[0], last = btns[btns.length - 1], cur = btns.indexOf(document.activeElement);
        if (cur === -1) { e.preventDefault(); first.focus(); }
        else if (e.shiftKey && document.activeElement === btns[0]) { e.preventDefault(); btns[2].focus(); }
        else if (!e.shiftKey && document.activeElement === btns[2]) { e.preventDefault(); btns[0].focus(); }
      }
    });
  }

  /* ---------- Virtual tour (Pannellum cubemaps) ---------- */
  var ROOM_ZH = { "Bedroom": "睡房", "Bathroom": "浴室", "Living Room": "客廳", "Kitchen": "廚房", "Master Bedroom": "主人房", "2nd Bedroom": "第二睡房" };
  function initTour() {
    var el = document.getElementById("tour-viewer"), dataEl = document.getElementById("tour-data");
    if (!el || !dataEl || !window.pannellum) return;
    var tours = JSON.parse(dataEl.textContent), viewer = null, current = null, retried = {};
    var roomsEl = $("[data-tour-rooms]");
    function zh() { var k = document.documentElement.getAttribute("data-lang"); return k === "zh" || k === "zh-Hans"; }
    function label(title) { return zh() && ROOM_ZH[title] ? ROOM_ZH[title] : title; }
    function hsTooltip(div, args) {
      div.classList.add("tour-hs"); div.tabIndex = 0; div.setAttribute("role", "button");
      div.setAttribute("aria-label", args);
      var s = document.createElement("span"); s.textContent = args; div.appendChild(s);
    }
    function renderRooms(key) {
      if (!roomsEl || !viewer) return;
      var t = tours[key], sceneId = viewer.getScene();
      roomsEl.innerHTML = "";
      Object.keys(t.scenes).forEach(function (id) {
        var b = document.createElement("button"); b.type = "button";
        b.textContent = label(t.scenes[id].title);
        if (id === sceneId) b.setAttribute("aria-current", "true");
        b.addEventListener("click", function () { if (viewer && viewer.getScene() !== key + "-" + id) viewer.loadScene(key + "-" + id); });
        b.dataset.scene = key + "-" + id;
        roomsEl.appendChild(b);
      });
    }
    function load(key) {
      current = key;
      var t = tours[key], scenes = {};
      Object.keys(t.scenes).forEach(function (id) {
        var sc = t.scenes[id];
        scenes[key + "-" + id] = {
          title: label(sc.title), type: "cubemap", cubeMap: sc.faces,
          yaw: -sc.pan, pitch: sc.tilt, hfov: 100,
          hotSpots: sc.hotspots.map(function (h) {
            return { pitch: h.pitch != null ? h.pitch : h.tilt, yaw: h.yaw != null ? h.yaw : -h.pan, type: "scene", sceneId: key + "-" + h.target,
              cssClass: "tour-hs", createTooltipFunc: function (div) { hsTooltip(div, label(t.scenes[h.target] ? t.scenes[h.target].title : h.title)); },
              clickHandlerFunc: function () { viewer.loadScene(key + "-" + h.target); } };
          })
        };
      });
      if (viewer) { try { viewer.destroy(); } catch (e) {} viewer = null; }
      // fresh container per viewer so a destroyed instance can't touch the new one
      el.innerHTML = "";
      var host = document.createElement("div"); host.style.width = "100%"; host.style.height = "100%";
      el.appendChild(host);
      viewer = pannellum.viewer(host, {
        "default": { firstScene: key + "-" + t.start, sceneFadeDuration: 250, autoLoad: true, showControls: true,
          compass: false, mouseZoom: true, keyboardZoom: true },
        scenes: scenes
      });
      var v = viewer;
      viewer.on("error", function () {
        // retry once on transient load errors (e.g. after rapid switching)
        if (v === viewer && !retried[key]) { retried[key] = true; setTimeout(function () { if (v === viewer) load(key); }, 200); }
      });
      viewer.on("scenechange", function () { setTimeout(function () { if (v === viewer) renderRooms(key); }, 0); });
      viewer.on("load", function () { if (v === viewer) renderRooms(key); });
      renderRooms(key);
      $all(".tour-tab").forEach(function (b) { b.setAttribute("aria-selected", b.dataset.tour === key ? "true" : "false"); });
    }
    var pending = null;
    $all(".tour-tab").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.dataset.tour;
        $all(".tour-tab").forEach(function (x) { x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        clearTimeout(pending);
        pending = setTimeout(function () { if (k !== current) load(k); }, 180);
      });
    });
    $all("[data-lang-btn]").forEach(function (b) { b.addEventListener("click", function () { renderRooms(current); }); });
    var first = Object.keys(tours)[0], hash = location.hash.replace("#", "");
    load(tours[hash] ? hash : first);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initLightbox();
    initTour();
    initLang();
    initNav();
    initCurrentNav();
    initBookChoice();
    initAvailabilityWidgets();
    initEnquiryForm();
  });

  // Expose for debugging / README verification
  window.OneDundas = {
    buildSiteMinderUrl: buildSiteMinderUrl,
    buildEnquiryUrl: buildEnquiryUrl,
    BOOK_BASE: BOOK_BASE,
    MONTHLY_NIGHTS: MONTHLY_NIGHTS
  };
})();
