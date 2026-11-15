/* Champagne Club – site behaviour (plain JavaScript, no libraries) */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  doc.classList.add("js");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var T = window.CC_TEXT || {};

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  /* ---------- mobile menu ---------- */
  var navBtn = $(".nav-toggle"), nav = $(".main-nav");
  if (navBtn && nav) {
    navBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      navBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- highlights band ---------- */
  var hl = $(".hl-viewport");
  if (hl) {
    var slides = $all(".hl-slide", hl);
    var dotsBox = $(".hl-dots");
    var playBtn = $(".hl-play");
    var idx = Math.floor(Math.random() * slides.length);
    var timer = null, paused = reduceMotion, hover = false;
    var dots = slides.map(function (s, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", (T.slide || "Slide") + " " + (i + 1));
      b.addEventListener("click", function () { show(i); restart(); });
      dotsBox.appendChild(b);
      return b;
    });
    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, j) {
        var on = j === idx;
        s.classList.toggle("is-active", on);
        s.setAttribute("aria-hidden", on ? "false" : "true");
        $all("a, button", s).forEach(function (el) { el.tabIndex = on ? 0 : -1; });
        var img = $("img[data-src]", s);
        if (on && img) { img.src = img.getAttribute("data-src"); img.srcset = img.getAttribute("data-srcset") || ""; img.removeAttribute("data-src"); }
      });
      dots.forEach(function (d, j) { d.setAttribute("aria-current", j === idx ? "true" : "false"); });
    }
    function tick() { if (!paused && !hover) show(idx + 1); }
    function restart() { clearInterval(timer); timer = setInterval(tick, 6500); }
    function setPaused(p) {
      paused = p;
      playBtn.setAttribute("aria-pressed", p ? "true" : "false");
      playBtn.setAttribute("aria-label", p ? (T.play || "Play") : (T.pause || "Pause"));
      $(".icon-pause", playBtn).style.display = p ? "none" : "";
      $(".icon-play", playBtn).style.display = p ? "" : "none";
    }
    $(".hl-prev").addEventListener("click", function () { show(idx - 1); restart(); });
    $(".hl-next").addEventListener("click", function () { show(idx + 1); restart(); });
    playBtn.addEventListener("click", function () { setPaused(!paused); });
    hl.addEventListener("mouseenter", function () { hover = true; });
    hl.addEventListener("mouseleave", function () { hover = false; });
    hl.addEventListener("focusin", function () { hover = true; });
    hl.addEventListener("focusout", function () { hover = false; });
    var x0 = null;
    hl.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hl.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) { show(idx + (dx < 0 ? 1 : -1)); restart(); }
      x0 = null;
    });
    setPaused(paused);
    show(idx);
    restart();
  }

  /* ---------- item gallery + lightbox ---------- */
  var gallery = $(".gallery");
  if (gallery) {
    var photos = JSON.parse(gallery.getAttribute("data-photos") || "[]");
    var mainImg = $(".gallery-main img", gallery);
    var thumbs = $all(".thumbs button", gallery);
    var cur = 0;
    function select(i) {
      cur = (i + photos.length) % photos.length;
      var p = photos[cur];
      mainImg.src = p.m; mainImg.srcset = p.srcset; mainImg.alt = p.alt;
      thumbs.forEach(function (t, j) { t.setAttribute("aria-current", j === cur ? "true" : "false"); });
    }
    thumbs.forEach(function (t, i) { t.addEventListener("click", function () { select(i); }); });

    var lb = $(".lightbox");
    var lbImg = lb && $("img", lb);
    var lbCount = lb && $(".lb-count", lb);
    function lbShow(i) {
      cur = (i + photos.length) % photos.length;
      lbImg.src = photos[cur].l; lbImg.alt = photos[cur].alt;
      lbCount.textContent = (cur + 1) + " / " + photos.length;
    }
    function lbOpen() {
      if (!lb || typeof lb.showModal !== "function") { window.open(photos[cur].l, "_blank"); return; }
      lbShow(cur); lb.showModal();
    }
    $(".zoom-btn", gallery).addEventListener("click", lbOpen);
    mainImg.addEventListener("click", lbOpen);
    if (lb) {
      $(".lb-close", lb).addEventListener("click", function () { lb.close(); select(cur); });
      $(".lb-prev", lb).addEventListener("click", function () { lbShow(cur - 1); });
      $(".lb-next", lb).addEventListener("click", function () { lbShow(cur + 1); });
      lb.addEventListener("close", function () { select(cur); });
      lb.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") lbShow(cur - 1);
        if (e.key === "ArrowRight") lbShow(cur + 1);
      });
      lb.addEventListener("click", function (e) { if (e.target === lb || e.target.classList.contains("lightbox-inner")) lb.close(); });
    }
  }

  /* ---------- collection: search, filters, sorting, pages ---------- */
  var coll = $("#collection-app");
  if (coll) {
    var PER = 24;
    var state = { q: "", sort: "new", page: 1, f: { type: [], house: [], period: [], material: [], status: [] } };
    var data = null;
    var grid = $("#results-grid"), countEl = $("#results-count"), chipsEl = $("#chips"), pager = $("#pager");
    var filtersBox = $("#filters");

    function readUrl() {
      var p = new URLSearchParams(location.search);
      state.q = p.get("q") || "";
      state.sort = p.get("sort") || "new";
      state.page = parseInt(p.get("page") || "1", 10) || 1;
      Object.keys(state.f).forEach(function (k) { state.f[k] = p.get(k) ? p.get(k).split(",") : []; });
    }
    function writeUrl() {
      var p = new URLSearchParams();
      if (state.q) p.set("q", state.q);
      if (state.sort !== "new") p.set("sort", state.sort);
      Object.keys(state.f).forEach(function (k) { if (state.f[k].length) p.set(k, state.f[k].join(",")); });
      if (state.page > 1) p.set("page", state.page);
      var s = p.toString();
      history.replaceState(null, "", location.pathname + (s ? "?" + s : ""));
    }
    function norm(s) { return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
    function matches(it, skip) {
      for (var k in state.f) {
        if (k === skip || !state.f[k].length) continue;
        var v = it[k];
        var vals = Array.isArray(v) ? v : [v];
        if (!state.f[k].some(function (x) { return vals.indexOf(x) !== -1; })) return false;
      }
      if (state.q) {
        var words = norm(state.q).split(/\s+/).filter(Boolean);
        for (var i = 0; i < words.length; i++) if (it._s.indexOf(words[i]) === -1) return false;
      }
      return true;
    }
    function buildFilters() {
      var html = "";
      data.facetOrder.forEach(function (k) {
        var facet = data.facets[k];
        html += '<fieldset><legend>' + esc(facet.label) + '</legend><div class="opts">';
        facet.options.forEach(function (o) {
          var id = "f-" + k + "-" + o.key;
          html += '<label for="' + id + '"><input type="checkbox" id="' + id + '" data-facet="' + k + '" value="' + esc(o.key) + '"><span>' +
            esc(o.label) + '</span><span class="count" data-count="' + k + ':' + esc(o.key) + '"></span></label>';
        });
        html += "</div></fieldset>";
      });
      filtersBox.innerHTML = html;
      $all("input[data-facet]", filtersBox).forEach(function (inp) {
        inp.addEventListener("change", function () {
          var k = inp.getAttribute("data-facet"), arr = state.f[k];
          if (inp.checked) { if (arr.indexOf(inp.value) === -1) arr.push(inp.value); }
          else state.f[k] = arr.filter(function (x) { return x !== inp.value; });
          state.page = 1; render();
        });
      });
    }
    function card(it) {
      var badge = it.badge ? '<span class="badge badge-' + esc(it.badgeClass || it.status) + '">' + esc(it.badge) + "</span>" : "";
      return '<a class="card" href="' + esc(it.url) + '"><div class="frame ratio-45">' + badge +
        (it.img ? '<img src="' + esc(it.img) + '" srcset="' + esc(it.srcset) + '" sizes="(max-width: 600px) 90vw, 300px" alt="' + esc(it.alt) + '" loading="lazy" width="480" height="600">' : "") +
        '</div><span class="small-caps card-house">' + esc(it.houseName) + '</span><span class="card-title">' + esc(it.title) +
        '</span><span class="card-meta">' + esc(it.meta) + "</span></a>";
    }
    function render() {
      $("#q").value = state.q;
      $("#sort").value = state.sort;
      $all("input[data-facet]", filtersBox).forEach(function (inp) {
        inp.checked = state.f[inp.getAttribute("data-facet")].indexOf(inp.value) !== -1;
      });
      // counts per option (respecting the other filters)
      data.facetOrder.forEach(function (k) {
        var counts = {};
        data.items.forEach(function (it) {
          if (!matches(it, k)) return;
          (Array.isArray(it[k]) ? it[k] : [it[k]]).forEach(function (v) { counts[v] = (counts[v] || 0) + 1; });
        });
        $all('[data-count^="' + k + ':"]', filtersBox).forEach(function (el) {
          el.textContent = counts[el.getAttribute("data-count").slice(k.length + 1)] || 0;
        });
      });
      var list = data.items.filter(function (it) { return matches(it); });
      list.sort(function (a, b) {
        if (state.sort === "old") return (a.year || 9999) - (b.year || 9999) || a.title.localeCompare(b.title);
        if (state.sort === "house") return a.houseName.localeCompare(b.houseName) || a.title.localeCompare(b.title);
        if (state.sort === "title") return a.title.localeCompare(b.title);
        return b.date.localeCompare(a.date);
      });
      var pages = Math.max(1, Math.ceil(list.length / PER));
      if (state.page > pages) state.page = pages;
      var slice = list.slice((state.page - 1) * PER, state.page * PER);
      grid.innerHTML = slice.map(card).join("");
      countEl.textContent = (T.showing || "Showing") + " " + list.length + " " + (list.length === 1 ? (T.item || "item") : (T.items || "items"));
      $("#empty").hidden = list.length > 0;
      // chips
      var chips = "";
      Object.keys(state.f).forEach(function (k) {
        state.f[k].forEach(function (v) {
          var o = data.facets[k].options.filter(function (x) { return x.key === v; })[0];
          if (o) chips += '<button type="button" class="chip" data-k="' + k + '" data-v="' + esc(v) + '">' + esc(o.label) + ' <span aria-hidden="true">×</span><span class="visually-hidden"> – ' + esc(T.remove || "remove") + "</span></button>";
        });
      });
      if (chips || state.q) chips += '<button type="button" class="chip chip-clear" data-clear="1">' + esc(T.clearAll || "Clear all") + "</button>";
      chipsEl.innerHTML = chips;
      $all("button", chipsEl).forEach(function (b) {
        b.addEventListener("click", function () {
          if (b.getAttribute("data-clear")) { Object.keys(state.f).forEach(function (k) { state.f[k] = []; }); state.q = ""; }
          else { var k = b.getAttribute("data-k"); state.f[k] = state.f[k].filter(function (x) { return x !== b.getAttribute("data-v"); }); }
          state.page = 1; render();
        });
      });
      // pager
      var ph = "";
      if (pages > 1) {
        for (var p = 1; p <= pages; p++) ph += '<button type="button" data-p="' + p + '"' + (p === state.page ? ' aria-current="page"' : "") + ">" + p + "</button>";
      }
      pager.innerHTML = ph;
      $all("button", pager).forEach(function (b) {
        b.addEventListener("click", function () { state.page = +b.getAttribute("data-p"); render(); coll.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" }); });
      });
      writeUrl();
    }
    var qTimer;
    $("#q").addEventListener("input", function (e) { clearTimeout(qTimer); qTimer = setTimeout(function () { state.q = e.target.value.trim(); state.page = 1; render(); }, 200); });
    $("#search-form").addEventListener("submit", function (e) { e.preventDefault(); state.q = $("#q").value.trim(); state.page = 1; render(); });
    $("#sort").addEventListener("change", function (e) { state.sort = e.target.value; render(); });
    var ft = $(".filters-toggle");
    if (ft) ft.addEventListener("click", function () { var o = filtersBox.classList.toggle("open"); ft.setAttribute("aria-expanded", o ? "true" : "false"); });

    fetch(coll.getAttribute("data-src"))
      .then(function (r) { return r.json(); })
      .then(function (j) {
        data = j;
        data.items.forEach(function (it) { it._s = norm([it.title, it.houseName, it.typeName, it.ref, it.meta, it.keywords].join(" ")); });
        buildFilters(); readUrl(); render();
      })
      .catch(function () { $("#empty").hidden = false; });
  }

  /* ---------- contact form ---------- */
  var form = $("#contact-form");
  if (form) {
    var params = new URLSearchParams(location.search);
    var item = params.get("item");
    if (item) {
      var sel = $("#cf-topic"); if (sel) sel.value = "buy";
      var subj = $("#cf-item"); if (subj) subj.value = item;
    }
    if (form.getAttribute("data-live") !== "true") {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var n = $("#form-notice"); n.hidden = false; n.focus();
      });
    }
  }
})();
