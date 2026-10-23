(function () {
  "use strict";

  var BOOK_BASE = "https://book-directonline.com/properties/OneDundasDirect/";
  var ENQUIRY_EMAIL = "leasing@onedundashk.com";
  var STORAGE_LANG = "onedundas-lang";

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  /* ---------- Language ---------- */
  function applySelectOptions(langKey) {
    // <option> cannot host spans; labels live in data-label-en / data-label-zh
    $all("select option[data-label-en]").forEach(function (opt) {
      var en = opt.getAttribute("data-label-en") || "";
      var zh = opt.getAttribute("data-label-zh") || en;
      opt.textContent = langKey === "zh" ? zh : en;
    });
  }

  function applyLang(lang) {
    var normalized = lang === "zh" || lang === "zh-Hant" ? "zh-Hant" : "en";
    var langKey = normalized === "zh-Hant" ? "zh" : "en";
    document.documentElement.lang = normalized;
    document.documentElement.setAttribute("data-lang", langKey);
    try { localStorage.setItem(STORAGE_LANG, normalized); } catch (e) {}
    $all("[data-lang-btn]").forEach(function (btn) {
      var isActive = btn.getAttribute("data-lang-btn") === langKey;
      btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
    // Update document title if bilingual titles provided
    var titleEl = document.querySelector("title");
    if (titleEl) {
      var en = titleEl.getAttribute("data-title-en");
      var zh = titleEl.getAttribute("data-title-zh");
      if (en && zh) titleEl.textContent = normalized === "zh-Hant" ? zh : en;
    }
    applySelectOptions(langKey);
  }

  function prefersChineseFromSystem() {
    // First visit only: EN by default; switch to 繁 when browser locale is Chinese.
    // Matches zh-HK / zh-TW / zh-Hant, and optionally zh-CN / zh / zh-Hans.
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
      if (
        raw === "zh" ||
        raw.indexOf("zh-hk") === 0 ||
        raw.indexOf("zh-tw") === 0 ||
        raw.indexOf("zh-hant") === 0 ||
        raw.indexOf("zh-cn") === 0 ||
        raw.indexOf("zh-hans") === 0 ||
        raw.indexOf("zh-mo") === 0 ||
        raw.indexOf("zh-sg") === 0
      ) {
        return true;
      }
    }
    return false;
  }

  function initLang() {
    var saved = null;
    try { saved = localStorage.getItem(STORAGE_LANG); } catch (e) {}
    var initial;
    if (saved === "en" || saved === "zh-Hant" || saved === "zh") {
      initial = saved;
    } else {
      // No stored preference: English default, or 繁 if system language is Chinese
      initial = prefersChineseFromSystem() ? "zh-Hant" : "en";
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

  /* ---------- Date helpers ---------- */
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

  function setMinDates(checkInEl, checkOutEl) {
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    checkInEl.min = toISODate(today);
    if (!checkInEl.value) {
      checkInEl.value = toISODate(today);
    }
    var cin = parseISODate(checkInEl.value) || today;
    var minOut = addDays(cin, 1);
    checkOutEl.min = toISODate(minOut);
    var cout = parseISODate(checkOutEl.value);
    if (!cout || cout <= cin) {
      // Default to ~30 nights for serviced apartments / monthly stays
      checkOutEl.value = toISODate(addDays(cin, 30));
    }
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
    var locale = document.documentElement.lang === "zh-Hant" ? "zh_TW" : "en";
    params.set("locale", locale);
    params.set("currency", "HKD");
    return BOOK_BASE + "?" + params.toString();
  }

  function openBooking(opts) {
    var url = buildSiteMinderUrl(opts);
    window.open(url, "_blank", "noopener,noreferrer");
  }

  function initAvailabilityWidgets() {
    $all("[data-avail-form]").forEach(function (form) {
      var checkIn = form.querySelector('[name="checkIn"], [name="checkin"]');
      var checkOut = form.querySelector('[name="checkOut"], [name="checkout"]');
      if (!checkIn || !checkOut) return;
      setMinDates(checkIn, checkOut);
      checkIn.addEventListener("change", function () { setMinDates(checkIn, checkOut); });

      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var cin = checkIn.value;
        var cout = checkOut.value;
        var dIn = parseISODate(cin);
        var dOut = parseISODate(cout);
        if (!dIn || !dOut || dOut <= dIn) {
          alert(document.documentElement.lang === "zh-Hant"
            ? "請選擇有效的入住與退房日期（退房須晚於入住）。"
            : "Please choose valid check-in and check-out dates (check-out must be after check-in).");
          return;
        }
        var adultsEl = form.querySelector('[name="adults"]');
        var childrenEl = form.querySelector('[name="children"]');
        var promoEl = form.querySelector('[name="promocode"]');
        openBooking({
          checkIn: cin,
          checkOut: cout,
          adults: adultsEl ? adultsEl.value : 2,
          children: childrenEl ? childrenEl.value : 0,
          promo: promoEl && promoEl.value ? promoEl.value.trim() : ""
        });
      });
    });

    // Plain Book Now links without dates still go to base URL;
    // links with data-book-now get today's defaults if desired
    $all("[data-book-now]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        // If the link already has query params, leave it;
        // otherwise optionally inject default month stay
        var href = el.getAttribute("href") || "";
        if (href.indexOf("checkInDate=") !== -1) return;
        // Prefer nearest availability form dates + guests if present
        var form = el.closest("form[data-avail-form]") || $("[data-avail-form]");
        if (form) {
          e.preventDefault();
          var checkIn = form.querySelector('[name="checkIn"], [name="checkin"]');
          var checkOut = form.querySelector('[name="checkOut"], [name="checkout"]');
          var adultsEl = form.querySelector('[name="adults"]');
          var childrenEl = form.querySelector('[name="children"]');
          if (checkIn && checkOut && checkIn.value && checkOut.value) {
            openBooking({
              checkIn: checkIn.value,
              checkOut: checkOut.value,
              adults: adultsEl ? adultsEl.value : 2,
              children: childrenEl ? childrenEl.value : 0
            });
            return;
          }
        }
        // Fall through to base BOOK_BASE href
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
    if (checkIn && checkOut) setMinDates(checkIn, checkOut);
    if (checkIn) checkIn.addEventListener("change", function () { setMinDates(checkIn, checkOut); });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var langZh = document.documentElement.lang === "zh-Hant";
      var ok = true;

      function req(name, label) {
        var input = form.querySelector('[name="' + name + '"]');
        var wrap = input && input.closest(".field");
        if (!input || !wrap) return "";
        var val = (input.value || "").trim();
        if (!val || (input.type === "date" && !parseISODate(val))) {
          setFieldError(wrap, langZh ? "請填寫" + label : label + " is required");
          ok = false;
          return "";
        }
        setFieldError(wrap, "");
        return val;
      }

      var firstname = req("firstname", langZh ? "名字" : "First name");
      var lastname = req("lastname", langZh ? "姓氏" : "Last name");
      var phone = req("phone", langZh ? "電話" : "Phone");
      var emailWrap = form.querySelector('[name="email"]').closest(".field");
      var email = (form.querySelector('[name="email"]').value || "").trim();
      if (!email || !validateEmail(email)) {
        setFieldError(emailWrap, langZh ? "請輸入有效電郵" : "Please enter a valid email");
        ok = false;
      } else setFieldError(emailWrap, "");

      var apartment = req("apartmenttype", langZh ? "公寓類型" : "Apartment type");
      var adate = req("adate", langZh ? "預計入住日期" : "Expected arrival");
      var ddate = req("ddate", langZh ? "預計退房日期" : "Expected departure");

      if (adate && ddate) {
        var dIn = parseISODate(adate);
        var dOut = parseISODate(ddate);
        if (dIn && dOut && dOut <= dIn) {
          setFieldError(form.querySelector('[name="ddate"]').closest(".field"),
            langZh ? "退房日期須晚於入住日期" : "Departure must be after arrival");
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

      var subject = "One Dundas Enquiry — " + firstname + " " + lastname + " (" + apartment + ")";
      var body = [
        "One Dundas Enquiry / 壹登查詢",
        "----------------------------",
        "Name / 姓名: " + firstname + " " + lastname,
        "Company / 公司: " + (company || "—"),
        "Phone / 電話: " + phone,
        "Email / 電郵: " + email,
        "Adults / 成人: " + (adult || "—"),
        "Children / 小童: " + (child || "—"),
        "Budget / 預算: " + (budget || "—"),
        "Apartment type / 公寓類型: " + apartment,
        "Arrival / 入住: " + adate,
        "Departure / 退房: " + ddate,
        "How heard / 得知途徑: " + (hear || "—"),
        "Marketing opt-in / 接收推廣: " + (marketingYes ? "Yes" : "No"),
        "",
        "Message / 留言:",
        remark || "—"
      ].join("\r\n");

      // Progressive enhancement: mailto (no backend). Formspree can replace later.
      var mailto = "mailto:" + ENQUIRY_EMAIL +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);

      var success = $("[data-enquiry-success]");
      if (success) {
        success.classList.add("is-visible");
        success.focus && success.focus();
      }

      // Open mail client; also keep a Formspree-ready data attribute for future wiring
      window.location.href = mailto;

      // Optional: if data-formspree-endpoint is set later, POST JSON instead
      var endpoint = form.getAttribute("data-formspree-endpoint");
      if (endpoint) {
        var payload = {
          firstname: firstname, lastname: lastname, company: company,
          phone: phone, email: email, adult: adult, child: child,
          budget: budget, apartmenttype: apartment, adate: adate, ddate: ddate,
          remark: remark, hear: hear, marketing: marketingYes
        };
        fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload)
        }).catch(function () { /* mailto already fired */ });
      }
    });
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
    function zh() { return document.documentElement.getAttribute("data-lang") === "zh"; }
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
    initAvailabilityWidgets();
    initEnquiryForm();
  });

  // Expose for debugging / README verification
  window.OneDundas = {
    buildSiteMinderUrl: buildSiteMinderUrl,
    BOOK_BASE: BOOK_BASE
  };
})();
