/* Clinic demo sites — behaviour. No dependencies. */
(function () {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ---------- Mobile navigation ---------- */
  function initNav() {
    const toggle = $(".nav-toggle");
    const nav = $("#site-nav");
    if (!toggle || !nav) return;
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    nav.addEventListener("click", (e) => { if (e.target.closest("a, button")) setOpen(false); });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 1001px)").addEventListener("change", (mq) => { if (mq.matches) setOpen(false); });
  }

  /* ---------- Booking dialog ---------- */
  function initBooking() {
    const dialog = $("#booking");
    if (!dialog) return;
    const form = $(".booking__form", dialog);
    const done = $(".booking__done", dialog);
    const title = $("#booking-title", dialog);
    const dateInput = $(".date-input", dialog);
    const waLink = $("[data-wa-link]", done);
    const whatsapp = document.body.dataset.whatsapp || "";
    const clinic = document.body.dataset.clinic || "the clinic";
    let opener = null;

    const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    const today = new Date();
    const max = new Date(today); max.setDate(max.getDate() + 60);
    dateInput.min = iso(today);
    dateInput.max = iso(max);

    function open(trigger) {
      opener = trigger;
      form.reset();
      title.textContent = "Book an appointment";
      form.hidden = false;
      done.hidden = true;
      dateInput.hidden = true;
      $$("[aria-invalid]", form).forEach((el) => el.removeAttribute("aria-invalid"));
      $$(".field__error", form).forEach((el) => (el.hidden = true));
      const doctor = trigger && trigger.dataset.doctor;
      if (doctor) form.doctor.value = doctor;

      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
      setTimeout(() => form.name.focus(), 50);
    }

    function close() {
      if (typeof dialog.close === "function") dialog.close();
      else dialog.removeAttribute("open");
    }

    dialog.addEventListener("close", () => { if (opener) opener.focus(); });

    const quick = $("[data-quick]");
    if (quick) {
      quick.addEventListener("submit", (e) => {
        e.preventDefault();
        open(quick.querySelector("button[type=submit]"));
        form.name.value = quick.name.value;
        form.phone.value = quick.phone.value;
        const day = quick.day.value;
        const radio = form.querySelector(`input[name="day"][value="${day}"]`);
        if (radio) { radio.checked = true; dateInput.hidden = day !== "date"; }
        setTimeout(() => {
          const next = !form.name.value.trim() ? form.name : !form.phone.value.trim() ? form.phone : (day === "date" ? dateInput : form.doctor);
          next.focus();
        }, 60);
      });
    }
    document.addEventListener("click", (e) => {
      const trigger = e.target.closest("[data-book]");
      if (trigger) { e.preventDefault(); open(trigger); return; }
      if (e.target.closest("[data-close]")) close();
    });
    dialog.addEventListener("click", (e) => { if (e.target === dialog) close(); });

    function setError(field, show) {
      const err = $("#" + field.getAttribute("aria-describedby"));
      if (show) field.setAttribute("aria-invalid", "true"); else field.removeAttribute("aria-invalid");
      if (err) err.hidden = !show;
      return show;
    }
    const phoneOk = (v) => /^(\+92|0092|0)?3\d{2}-?\d{7}$/.test(v.replace(/\s+/g, ""));
    function validate(field) {
      if (field.name === "name") return !setError(field, field.value.trim().length < 2);
      if (field.name === "phone") return !setError(field, !phoneOk(field.value));
      if (field.name === "date") return !setError(field, !field.hidden && !field.value);
      return true;
    }

    form.addEventListener("change", (e) => {
      if (e.target.name === "day") {
        dateInput.hidden = e.target.value !== "date";
        if (dateInput.hidden) setError(dateInput, false); else dateInput.focus();
      }
    });
    form.addEventListener("input", (e) => {
      if (e.target.getAttribute("aria-invalid") === "true") validate(e.target);
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const bad = [form.name, form.phone, dateInput].filter((f) => !validate(f));
      if (bad.length) { bad[0].focus(); return; }

      const data = new FormData(form);
      let day = data.get("day");
      if (day === "date") {
        day = new Date(data.get("date") + "T00:00").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
      }
      const rows = [
        ["Patient", data.get("name").trim()],
        ["Mobile", data.get("phone").trim()],
        ["Doctor", data.get("doctor") || "Any available doctor"],
        ["When", `${day}, ${data.get("time").toLowerCase()}`],
      ];
      $("[data-summary]", done).innerHTML = rows
        .map(([k, v]) => `<div><dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v)}</dd></div>`).join("");
      const message = `Assalam o Alaikum, I'd like to book an appointment at ${clinic}.\n` + rows.map(([k, v]) => `${k}: ${v}`).join("\n");
      waLink.href = `https://wa.me/${whatsapp}?text=${encodeURIComponent(message)}`;

      form.hidden = true;
      done.hidden = false;
      title.textContent = "Your request is ready";
      waLink.focus();
    });
  }

  /* ---------- Demo list: copy links ---------- */
  function initCopy() {
    const toast = $(".toast");
    let timer;
    $$("[data-url]").forEach((el) => { el.textContent = new URL(el.dataset.url, window.location.href).href; });
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest("[data-copy]");
      if (!btn) return;
      const url = new URL(btn.dataset.copy, window.location.href).href;
      let ok = false;
      try { await navigator.clipboard.writeText(url); ok = true; } catch (err) { ok = false; }
      if (toast) {
        toast.textContent = ok ? "Link copied" : "Copy didn't work. Select the link and copy it.";
        toast.hidden = false;
        clearTimeout(timer);
        timer = setTimeout(() => (toast.hidden = true), 2200);
      }
      const label = $("span", btn);
      if (ok && label) {
        label.textContent = "Copied";
        setTimeout(() => (label.textContent = "Copy link"), 2200);
      }
    });
  }

  /* ---------- Header shadow on scroll ---------- */
  function initHeader() {
    const header = $(".site-header");
    if (!header) return;
    const update = () => header.classList.toggle("is-scrolled", window.scrollY > 40);
    update();
    window.addEventListener("scroll", update, { passive: true });
  }

  /* ---------- Reveal sections as they scroll into view ---------- */
  function initReveal() {
    const items = $$("[data-reveal]");
    if (!items.length) return;
    if (!("IntersectionObserver" in window)) { items.forEach((el) => el.classList.add("is-visible")); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    items.forEach((el) => io.observe(el));
  }

  /* ---------- Count-up numbers ---------- */
  function initCounters() {
    const nums = $$("[data-count]");
    if (!nums.length) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const render = (el, value) => {
      const decimals = Number(el.dataset.decimals || 0);
      el.textContent = value.toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + (el.dataset.suffix || "");
    };
    const run = (el) => {
      const target = Number(el.dataset.count);
      if (reduce) { render(el, target); return; }
      const start = performance.now();
      const dur = 1600;
      const tick = (now) => {
        const t = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - t, 3);
        render(el, target * eased);
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if (!("IntersectionObserver" in window)) { nums.forEach((el) => render(el, Number(el.dataset.count))); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => { if (entry.isIntersecting) { run(entry.target); io.unobserve(entry.target); } });
    }, { threshold: 0.6 });
    nums.forEach((el) => { render(el, 0); io.observe(el); });
  }

  initNav();
  initHeader();
  initReveal();
  initCounters();
  initBooking();
  initCopy();
})();
