#!/usr/bin/env python3
"""
Builds 16 standalone clinic demo websites, one per specialty.

  sites/<link>/index.html + sites/<link>/assets/   one self-contained site per specialty
  sites/index.html                                 your private list of all 16 demo links
  sites/404.html, sites/robots.txt

Each site folder works on its own: it has its own copy of the CSS, JS and icons, and
never links to the other specialties, so a doctor only ever sees their own demo.

Run from the project root:   python3 scripts/build.py
Only the Python standard library is used.
"""
from __future__ import annotations

import html
import json
import random
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SRC_ASSETS = ROOT / "src" / "assets"
OUT = ROOT / "sites"
YEAR = 2026

SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SPECS = json.loads((DATA / "specialties.json").read_text(encoding="utf-8"))
DEMOS = json.loads((DATA / "demos.json").read_text(encoding="utf-8"))
for s in SPECS:
    s["demo"] = DEMOS[s["slug"]]


def _clinic_wording(value):
    """The specialty texts were written for a directory; reword them for a single clinic."""
    if isinstance(value, str):
        return value.replace(" listed on this page", " at this clinic").replace(" listed here", " at this clinic")
    if isinstance(value, list):
        return [_clinic_wording(v) for v in value]
    if isinstance(value, dict):
        return {k: _clinic_wording(v) for k, v in value.items()}
    return value


SPECS = [_clinic_wording(s) for s in SPECS]


def e(value) -> str:
    return html.escape(str(value), quote=True)


# ---------------------------------------------------------------------------
# Icons (24px grid, 1.75 stroke)
# ---------------------------------------------------------------------------
ICONS = {
    "general-physician": '<path d="M11 2v2"/><path d="M5 2v2"/><path d="M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><circle cx="20" cy="10" r="2"/>',
    "dermatology": '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01"/><path d="M15 9h.01"/>',
    "dental": '<path d="M7 3c-2.2 0-4 1.8-4 4.2 0 2 .7 3.3 1.3 4.6.6 1.4.9 3 1.2 5.2.3 2.3.9 4 2.2 4 1.4 0 1.7-1.8 2-3.6.3-1.6.8-2.4 2.3-2.4s2 .8 2.3 2.4c.3 1.8.6 3.6 2 3.6 1.3 0 1.9-1.7 2.2-4 .3-2.2.6-3.8 1.2-5.2.6-1.3 1.3-2.6 1.3-4.6C21 4.8 19.2 3 17 3c-1.9 0-2.9 1-5 1S8.9 3 7 3Z"/>',
    "gynecology": '<circle cx="12" cy="9" r="6"/><path d="M12 15v7"/><path d="M9 19h6"/>',
    "pediatrics": '<path d="M9 12h.01"/><path d="M15 12h.01"/><path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M19 6.3a9 9 0 0 1 1.8 3.9 2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1"/>',
    "orthopedics": '<path d="M17 10c.7-.7 1.69 0 2.5 0a2.5 2.5 0 1 0 0-5 .5.5 0 0 1-.5-.5 2.5 2.5 0 1 0-5 0c0 .81.7 1.8 0 2.5l-7 7c-.7.7-1.69 0-2.5 0a2.5 2.5 0 0 0 0 5c.28 0 .5.22.5.5a2.5 2.5 0 1 0 5 0c0-.81-.7-1.8 0-2.5Z"/>',
    "ent": '<path d="M6 8.5a6.5 6.5 0 1 1 13 0c0 6-6 6-6 10a3.5 3.5 0 1 1-7 0"/><path d="M15 8.5a2.5 2.5 0 0 0-5 0v1a2 2 0 1 1 0 4"/>',
    "eye-care": '<path d="M2.06 12.35a1 1 0 0 1 0-.7 10.75 10.75 0 0 1 19.88 0 1 1 0 0 1 0 .7 10.75 10.75 0 0 1-19.88 0"/><circle cx="12" cy="12" r="3"/>',
    "cardiology": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
    "physiotherapy": '<circle cx="12" cy="4.5" r="1.6"/><path d="m9 21 3-6.5 3 6.5"/><path d="m5.5 8.5 6.5 2 6.5-2"/><path d="M12 10.5v4"/>',
    "nutrition": '<path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.9 4.9 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z"/><path d="M10 2c1 .5 2 2 2 5"/>',
    "psychiatry": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M15.8 9.2a2.5 2.5 0 0 0-3.5 0l-.3.4-.35-.3a2.42 2.42 0 1 0-3.2 3.6l3.55 3.5 3.6-3.5c1.2-1.2 1.1-2.7.2-3.7"/>',
    "diabetes-endocrinology": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7Z"/><path d="M9.5 15.5a2.5 2.5 0 0 0 2.5 2.5"/>',
    "gastroenterology": '<path d="M9 2.5V7c0 1.6-.9 2.6-2.4 3.3C4.4 11.3 3 13 3 15.5 3 18.5 5.5 21 8.5 21H11c4.4 0 8-3.6 8-8 0-2.6-1.6-4.5-3.8-4.5-2 0-3.2 1.3-3.2 3.2"/><path d="M12 2.5V6"/>',
    "urology": '<path d="M15.5 3C12 3 10 5.6 10 8c0 1.5.9 2.4.9 4s-.9 2.5-.9 4c0 2.4 2 5 5.5 5 3.6 0 5.5-4.2 5.5-9s-1.9-9-5.5-9Z"/><path d="M10.9 12H7a3 3 0 0 0-3 3v6"/>',
    "neurology": '<path d="M12 5a3 3 0 1 0-6 .13 4 4 0 0 0-2.52 5.77 4 4 0 0 0 .55 6.59A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 6 .13 4 4 0 0 1 2.52 5.77 4 4 0 0 1-.55 6.59A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>',
    "logo": '<path d="M2.5 12.5h4.2l2.3-6 4.2 12 2.6-6h5.7"/>',
    "pin": '<path d="M20 10c0 5-8 12-8 12s-8-7-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "alert": '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4M12 17h.01"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "message": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
    "copy": '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "directions": '<path d="M3 11 22 2l-9 19-2-8Z"/>',
}


def icon(name: str, cls: str = "icon", filled: bool = False) -> str:
    paint = 'fill="currentColor" stroke="none"' if filled else 'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg class="{cls}" viewBox="0 0 24 24" {paint} aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


# ---------------------------------------------------------------------------
# Images: "photo-..." = Unsplash id, anything else = a file inside the site folder
# (for example "assets/img/doctor.jpg"). A failed image shows a designed fallback.
# ---------------------------------------------------------------------------
FALLBACK_JS = "this.parentNode.classList.add('is-fallback');this.remove()"


def img_url(ref: str, width: int, height: int | None = None) -> str:
    if ref.startswith("photo-"):
        crop = f"&h={height}" if height else ""
        return f"https://images.unsplash.com/{ref}?auto=format&fit=crop&w={width}{crop}&q=75"
    return ref


def picture(ref: str | None, alt: str, widths: tuple[int, ...], sizes: str, ratio: tuple[int, int], eager: bool = False) -> str:
    if not ref:
        return ""
    w0 = widths[-1]
    h0 = round(w0 * ratio[1] / ratio[0])
    srcset = ""
    if ref.startswith("photo-"):
        srcset = ", ".join(f"{img_url(ref, w, round(w * ratio[1] / ratio[0]))} {w}w" for w in widths)
        srcset = f' srcset="{e(srcset)}" sizes="{e(sizes)}"'
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{e(img_url(ref, w0, h0))}"{srcset} alt="{e(alt)}" width="{w0}" height="{h0}" '
            f'{loading} decoding="async" onerror="{FALLBACK_JS}">')


# ---------------------------------------------------------------------------
# Placeholder doctors (deterministic). Replace with the real doctor's details
# when you customise a demo for a client.
# ---------------------------------------------------------------------------
DOCTOR_PHOTOS = {
    "f": ["photo-1559839734-2b71ea197ec2", "photo-1594824476967-48c8b964273f"],
    "m": ["photo-1612349317150-e413f6a5b16d", "photo-1622253692010-333f2da6031d", "photo-1537368910025-700350fe46c7"],
}
FIRST = {
    "f": ["Ayesha", "Hira", "Sana", "Mahnoor", "Fatima", "Zainab", "Amna", "Rabia", "Mehwish", "Saba", "Nida", "Iqra",
          "Maryam", "Sadia", "Kiran", "Anum", "Farah", "Bushra", "Asma", "Sidra", "Huma", "Rida", "Noor", "Aiman"],
    "m": ["Ahmed", "Usman", "Bilal", "Hamza", "Faisal", "Imran", "Kamran", "Salman", "Omar", "Adeel", "Junaid", "Tariq",
          "Waqas", "Zeeshan", "Asad", "Haris", "Shahid", "Fahad", "Saad", "Yasir", "Danish", "Talha", "Arslan", "Owais"],
}
LAST = ["Khan", "Malik", "Qureshi", "Siddiqui", "Sheikh", "Butt", "Chaudhry", "Mirza", "Hashmi", "Rizvi", "Javed",
        "Aslam", "Abbasi", "Baig", "Farooq", "Iqbal", "Anwar", "Nadeem", "Saleem", "Zafar", "Haider", "Akhtar", "Rana"]
QUALS = {
    "general-physician": ["MBBS, FCPS (Medicine)", "MBBS, MRCP (UK)", "MBBS, FCPS (Family Medicine)"],
    "dermatology": ["MBBS, FCPS (Dermatology)", "MBBS, MCPS (Dermatology)", "MBBS, Dip. Dermatology (UK)"],
    "dental": ["BDS, FCPS (Operative Dentistry)", "BDS, MDS (Orthodontics)", "BDS, MSc (Prosthodontics)"],
    "gynecology": ["MBBS, FCPS (Obs and Gynae)", "MBBS, MRCOG (UK)", "MBBS, MCPS (Obs and Gynae)"],
    "pediatrics": ["MBBS, FCPS (Paediatrics)", "MBBS, MRCPCH (UK)", "MBBS, DCH"],
    "orthopedics": ["MBBS, FCPS (Orthopaedics)", "MBBS, FRCS (Orth)", "MBBS, MS (Orthopaedics)"],
    "ent": ["MBBS, FCPS (ENT)", "MBBS, MS (ENT)", "MBBS, FRCS (ENT)"],
    "eye-care": ["MBBS, FCPS (Ophthalmology)", "MBBS, FRCS (Ophth)", "MBBS, MS (Ophthalmology)"],
    "cardiology": ["MBBS, FCPS (Cardiology)", "MBBS, MRCP, FCPS (Cardiology)", "MBBS, FCPS (Cardiology), FACC"],
    "physiotherapy": ["DPT, MS (Orthopedic Manual Therapy)", "DPT, MS (Sports Physical Therapy)", "DPT, MS (Neuromuscular PT)"],
    "nutrition": ["MSc Human Nutrition and Dietetics", "MPhil Clinical Nutrition", "BS Human Nutrition, RD"],
    "psychiatry": ["MBBS, FCPS (Psychiatry)", "MBBS, MRCPsych (UK)", "MBBS, MCPS (Psychiatry)"],
    "diabetes-endocrinology": ["MBBS, FCPS (Endocrinology)", "MBBS, MRCP, CCT (Endocrinology)", "MBBS, FCPS (Medicine), Diabetology"],
    "gastroenterology": ["MBBS, FCPS (Gastroenterology)", "MBBS, MRCP (Gastroenterology)", "MBBS, FCPS (Medicine), Hepatology"],
    "urology": ["MBBS, FCPS (Urology)", "MBBS, FRCS (Urol)", "MBBS, MS (Urology)"],
    "neurology": ["MBBS, FCPS (Neurology)", "MBBS, MRCP (Neurology)", "MBBS, FCPS (Medicine), Neurology"],
}
AREAS = [("Gulberg III", "Lahore"), ("DHA Phase 5", "Lahore"), ("Johar Town", "Lahore"), ("Model Town", "Lahore"),
         ("Clifton", "Karachi"), ("Gulshan-e-Iqbal", "Karachi"), ("North Nazimabad", "Karachi"), ("DHA Phase 6", "Karachi"),
         ("F-8 Markaz", "Islamabad"), ("Blue Area", "Islamabad"), ("G-9 Markaz", "Islamabad"), ("Saddar", "Rawalpindi")]
SLOTS = ["Today, 5:30 pm", "Today, 6:45 pm", "Today, 8:00 pm", "Tomorrow, 10:30 am", "Tomorrow, 12:15 pm", "Tomorrow, 4:00 pm"]
DAYS = ["Mon to Sat", "Mon to Fri", "Tue to Sun", "Mon, Wed and Fri"]
HOURS = [
    [("Monday to Saturday", "5:00 pm to 10:00 pm"), ("Sunday", "Closed")],
    [("Monday to Friday", "10:00 am to 2:00 pm, 5:00 pm to 9:00 pm"), ("Saturday", "10:00 am to 2:00 pm"), ("Sunday", "Closed")],
    [("Monday to Saturday", "9:00 am to 5:00 pm"), ("Sunday", "By appointment")],
    [("Monday to Saturday", "4:00 pm to 9:00 pm"), ("Sunday", "11:00 am to 2:00 pm")],
]
GENDER_PATTERNS = [["f", "m", "m"], ["m", "f", "m"], ["m", "m", "f"], ["f", "m", "f"], ["m", "f", "f"]]
_used_names: set[str] = set()


def initials(name: str) -> str:
    parts = [p for p in name.replace("Dr.", "").split() if p]
    return (parts[0][0] + parts[-1][0]).upper()


def make_clinic(spec: dict) -> None:
    rng = random.Random(spec["slug"])
    genders = ["f", "f", "f"] if spec.get("femaleOnly") else rng.choice(GENDER_PATTERNS)
    photo_i = {"f": 0, "m": 0}
    doctors = []
    for g in genders:
        while True:
            name = f"{rng.choice(FIRST[g])} {rng.choice(LAST)}"
            if name not in _used_names:
                _used_names.add(name)
                break
        full = name if spec.get("noTitle") else f"Dr. {name}"
        pool = DOCTOR_PHOTOS[g]
        photo = pool[photo_i[g]] if photo_i[g] < len(pool) else None
        photo_i[g] += 1
        doctors.append({
            "name": full, "initials": initials(full), "gender": g, "photo": photo,
            "quals": rng.choice(QUALS[spec["slug"]]), "years": rng.randint(6, 24),
            "rating": round(rng.uniform(4.6, 4.95), 1), "reviews": rng.randint(38, 640),
            "fee": rng.randrange(spec["feeMin"], spec["feeMax"] + 1, 500),
            "slot": rng.choice(SLOTS), "days": rng.choice(DAYS),
        })
    # the most experienced doctor with a photo leads the clinic
    doctors.sort(key=lambda d: (d["photo"] is None, -d["years"]))
    area, city = rng.choice(AREAS)
    spec["doctors"] = doctors
    spec["lead"] = doctors[0]
    spec["area"], spec["city"] = area, city
    spec["address"] = f"{SITE['street']}, {area}, {city}"
    spec["hours"] = rng.choice(HOURS)


for _s in SPECS:
    make_clinic(_s)


def rs(n: int) -> str:
    return f"Rs {n:,}"


def fee_range(spec: dict) -> str:
    text = f"{rs(spec['feeMin'])} to {spec['feeMax']:,}"
    return f"{text} {spec['feeNote']}" if spec.get("feeNote") else text


def theme(spec: dict) -> str:
    return f'--accent:{spec["accent"]};--tint:{spec["tint"]}'


def cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def article(word: str) -> str:
    return "an" if word[0].lower() in "aeiou" else "a"


AUDIENCE = {"pediatrics": "babies, children and teenagers", "gynecology": "women of all ages"}


def lower_name(name: str) -> str:
    return name if name.isupper() else name.lower()


def tel(phone: str) -> str:
    return "tel:" + phone.replace(" ", "")


def wa(text: str = "") -> str:
    return f"https://wa.me/{SITE['whatsapp']}" + (f"?text={quote(text)}" if text else "")


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------
FONT_URL = "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&display=swap"


def head(title: str, desc: str, url: str, theme_color: str, prefix: str = "") -> str:
    # Demo sites carry placeholder doctors and reviews, so they are kept out of search engines.
    # Remove the robots line once a site holds a real clinic's details.
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="{e(theme_color)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="{FONT_URL}">
<link rel="stylesheet" href="{prefix}assets/css/styles.css">
<script src="{prefix}assets/js/main.js" defer></script>
</head>"""


def brand(spec: dict) -> str:
    d = spec["demo"]
    return f"""<a class="brand brand--clinic" href="#top" aria-label="{e(d['clinic'])} home">
      <span class="brand__mark">{icon(spec['icon'])}</span>
      <span class="brand__text"><span class="brand__name">{e(d['short'])}</span><span class="brand__tag">{e(d['tag'])}</span></span>
    </a>"""


def header(spec: dict) -> str:
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" id="top">
  <div class="container site-header__inner">
    {brand(spec)}
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="nav-toggle__open">{icon('menu')}</span>
      <span class="nav-toggle__close">{icon('close')}</span>
      <span class="visually-hidden">Menu</span>
    </button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul class="site-nav__list">
        <li><a href="#about">About</a></li>
        <li><a href="#treatments">Treatments</a></li>
        <li><a href="#doctors">Doctors</a></li>
        <li><a href="#reviews">Reviews</a></li>
        <li><a href="#visit">Visit us</a></li>
      </ul>
      <a class="site-nav__phone" href="{tel(SITE['phone'])}">{icon('phone')}{e(SITE['phone'])}</a>
      <button class="btn btn-accent site-nav__cta" type="button" data-book>Book appointment</button>
    </nav>
  </div>
</header>"""


def pulse_line() -> str:
    return """
<div class="pulse pulse--accent" aria-hidden="true">
  <svg viewBox="0 0 1200 100" preserveAspectRatio="none" focusable="false">
    <path class="pulse__base" vector-effect="non-scaling-stroke" d="M0 62H470l14-9 14 9h36"/>
    <path class="pulse__beat" vector-effect="non-scaling-stroke" d="M534 62l10 12 16-64 17 76 12-24"/>
    <path class="pulse__base" vector-effect="non-scaling-stroke" d="M589 62h47l18-13 18 13H1200"/>
  </svg>
</div>"""


def avatar(doc: dict, cls: str, widths=(160, 320), sizes="96px", ratio=(1, 1)) -> str:
    img = picture(doc["photo"], f"Portrait of {doc['name']}", widths, sizes, ratio)
    fallback = "" if doc["photo"] else " is-fallback"
    return f'<div class="avatar {cls}{fallback}">{img}<span class="avatar__initials" aria-hidden="true">{e(doc["initials"])}</span></div>'


def book_attrs(doc: dict | None = None) -> str:
    return f' data-doctor="{e(doc["name"])}"' if doc else ""


def doctor_row(doc: dict) -> str:
    return f"""<li class="doc-row">
  {avatar(doc, 'avatar--row')}
  <div class="doc-row__main">
    <h3 class="doc-row__name">{e(doc['name'])}</h3>
    <p class="doc-row__quals">{e(doc['quals'])}</p>
    <ul class="meta">
      <li>{icon('briefcase')}{doc['years']} years experience</li>
      <li>{icon('star', filled=True)}<span><strong>{doc['rating']}</strong> ({doc['reviews']} reviews)</span></li>
      <li>{icon('calendar')}Sees patients {e(doc['days'])}</li>
    </ul>
  </div>
  <div class="doc-row__aside">
    <p class="doc-row__fee"><span>Fee</span>{rs(doc['fee'])}</p>
    <p class="doc-row__slot">{icon('clock')}Next: {e(doc['slot'])}</p>
    <button class="btn btn-accent" type="button" data-book{book_attrs(doc)}>Book</button>
  </div>
</li>"""


def booking_dialog(spec: dict) -> str:
    doc_opts = '<option value="">Any available doctor</option>' + "".join(
        f'<option>{e(d["name"])}</option>' for d in spec["doctors"])

    def chips(name: str, values: list[tuple[str, str]], checked: str) -> str:
        return "".join(
            f'<label class="chip"><input type="radio" name="{name}" value="{e(v)}"{" checked" if v == checked else ""}>'
            f'<span>{e(label)}</span></label>' for v, label in values)

    return f"""
<dialog class="booking" id="booking" aria-labelledby="booking-title">
  <div class="booking__panel">
    <div class="booking__head">
      <h2 class="booking__title" id="booking-title">Book an appointment</h2>
      <button class="icon-btn" type="button" data-close>{icon('close')}<span class="visually-hidden">Close</span></button>
    </div>
    <form class="booking__form" novalidate>
      <div class="field">
        <label for="b-name">Patient's full name</label>
        <input id="b-name" name="name" autocomplete="name" required aria-describedby="b-name-err">
        <p class="field__error" id="b-name-err" hidden>Enter the patient's name.</p>
      </div>
      <div class="field">
        <label for="b-phone">Mobile number</label>
        <input id="b-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="0300 1234567" required aria-describedby="b-phone-err">
        <p class="field__error" id="b-phone-err" hidden>Enter a Pakistani mobile number, like 0300 1234567.</p>
      </div>
      <div class="field">
        <label for="b-doctor">Doctor</label>
        <select id="b-doctor" name="doctor">{doc_opts}</select>
      </div>
      <fieldset class="field">
        <legend>Day</legend>
        <div class="chips">{chips('day', [('Today', 'Today'), ('Tomorrow', 'Tomorrow'), ('date', 'Pick a date')], 'Today')}</div>
        <input class="date-input" id="b-date" type="date" name="date" aria-label="Appointment date" aria-describedby="b-date-err" hidden>
        <p class="field__error" id="b-date-err" hidden>Choose a date for your visit.</p>
      </fieldset>
      <fieldset class="field">
        <legend>Time of day</legend>
        <div class="chips">{chips('time', [('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Evening')], 'Evening')}</div>
      </fieldset>
      <button class="btn btn-accent btn-block" type="submit">Request appointment</button>
      <p class="booking__fine">The clinic replies on WhatsApp to confirm your exact time and token number.</p>
    </form>
    <div class="booking__done" hidden>
      <div class="slip slip--flat">
        <p class="slip__label">Appointment request</p>
        <dl class="slip__rows" data-summary></dl>
      </div>
      <p class="booking__done-text">Send this request to the clinic on WhatsApp. They'll reply to confirm your time.</p>
      <div class="booking__done-actions">
        <a class="btn btn-accent" data-wa-link href="#" target="_blank" rel="noopener">{icon('message')}Send on WhatsApp</a>
        <button class="btn btn-ghost" type="button" data-close>Done</button>
      </div>
    </div>
  </div>
</dialog>"""


# ---------------------------------------------------------------------------
# A clinic site
# ---------------------------------------------------------------------------
def build_clinic(spec: dict) -> str:
    d = spec["demo"]
    lead = spec["lead"]
    docs = spec["doctors"]
    who, who_pl = spec["specialist"], spec["specialists"]
    clinic = d["clinic"]
    layout = d["layout"]
    next_slot = min((doc["slot"] for doc in docs), key=SLOTS.index)
    url = f"{SITE['baseUrl'].rstrip('/')}/{d['path']}/"

    ratio = (16, 9) if layout == "c" else (4, 5)
    hero_img = picture(spec["image"], f"{spec['name']} care at {clinic}", (560, 900, 1400) if layout == "c" else (480, 760, 1000),
                       "(min-width: 960px) 1100px, 94vw" if layout == "c" else "(min-width: 960px) 44vw, 92vw", ratio, eager=True)
    lead_img = avatar(lead, "avatar--portrait", (420, 720), "(min-width: 960px) 380px, 90vw", (4, 5))

    hours_rows = "".join(f"<div><dt>{e(day)}</dt><dd>{e(time)}</dd></div>" for day, time in spec["hours"])
    hours_short = spec["hours"][0][1]
    conditions = "".join(f"<li>{e(c)}</li>" for c in spec["conditions"])
    services = "".join(f'<li class="service"><h3 class="service__name">{e(s["name"])}</h3><p>{e(s["desc"])}</p></li>' for s in spec["services"])
    signs = "".join(f'<li>{icon("check")}<span>{e(s)}</span></li>' for s in spec["signs"])
    faqs = "".join(
        f'<details class="faq"><summary><span>{e(f["q"])}</span>{icon("plus", "icon faq__icon")}</summary>'
        f'<div class="faq__answer"><p>{e(f["a"])}</p></div></details>' for f in spec["faqs"])
    reviews = "".join(
        f'<li class="quote"><div class="quote__stars" aria-label="5 out of 5 stars">{icon("star", filled=True) * 5}</div>'
        f'<blockquote><p>{e(r["q"])}</p></blockquote>'
        f'<p class="quote__by"><strong>{e(r["n"])}</strong><span>{e(r["c"])}</span></p></li>' for r in d["reviews"])

    if spec.get("alert"):
        side = f"""<aside class="callout callout--alert" role="note">
          {icon('alert', 'icon callout__icon')}
          <div><h3>When it can't wait</h3><p>{e(spec['alert'])}</p></div>
        </aside>"""
    else:
        side = f"""<aside class="callout">
          {icon('message', 'icon callout__icon')}
          <div><h3>Not sure if you need to come in?</h3>
          <p>Send us a message on WhatsApp. Our team will tell you whether you need a visit and which doctor to see.</p>
          <a class="text-link" href="{e(wa(f'Assalam o Alaikum, I have a question for {clinic}.'))}" target="_blank" rel="noopener">Message us on WhatsApp</a></div>
        </aside>"""

    title = f"{clinic}: {who_pl} in {spec['city']}"
    desc = f"{clinic} in {spec['area']}, {spec['city']}. Book {article(who)} {who} for {spec['for'].lower()} and more."

    hero_slip = f"""<div class="slip slip--hero" aria-hidden="true">
          <div class="slip__top">
            <div class="slip__token"><span class="slip__label">Your token</span><span class="slip__num">14</span></div>
            <p class="slip__now"><span class="slip__dot"></span>Now seeing <strong>11</strong></p>
          </div>
          <div class="slip__perf"></div>
          <div class="slip__body">
            <p class="slip__doctor">{e(lead['name'])}</p>
            <p class="slip__spec">{e(cap(who))}</p>
            <p class="slip__line">{icon('clock')}{e(lead['slot'])}</p>
            <p class="slip__line">{icon('pin')}{e(spec['area'])}, {e(spec['city'])}</p>
          </div>
        </div>"""

    body = f"""{header(spec)}
<main id="main">
  <section class="hero hero--{layout} ecg ecg--accent">
    <div class="container hero__grid">
      <div class="hero__copy">
        <p class="hero__clinic">{icon('pin')}{e(clinic)}, {e(spec['area'])}, {e(spec['city'])}</p>
        <h1 class="display hero__title">{e(d['headline'])}</h1>
        <p class="hero__lede">{e(spec['intro'])}</p>
        <div class="hero__actions">
          <button class="btn btn-accent" type="button" data-book>Book appointment</button>
          <a class="btn btn-ghost" href="{tel(SITE['phone'])}">{icon('phone')}Call {e(SITE['phone'])}</a>
        </div>
        <ul class="hero__facts">
          <li>{icon('briefcase')}<span><strong>{lead['years']} years</strong> of experience</span></li>
          <li>{icon('star', filled=True)}<span><strong>{lead['rating']}</strong> from {lead['reviews']} patients</span></li>
          <li>{icon('clock')}<span>Next slot <strong>{e(next_slot)}</strong></span></li>
        </ul>
      </div>
      <div class="hero__visual">
        <div class="media media--hero">
          {hero_img}
          <div class="media__fallback" aria-hidden="true">{icon(spec['icon'], 'icon media__fallback-icon')}</div>
        </div>
        {hero_slip}
      </div>
    </div>
    {pulse_line()}
  </section>

  <section class="section" id="about" aria-labelledby="about-title">
    <div class="container about">
      <figure class="lead-card">
        {lead_img}
        <figcaption>
          <p class="lead-card__name">{e(lead['name'])}</p>
          <p class="lead-card__quals">{e(lead['quals'])}</p>
          <p class="lead-card__reg">{icon('shield')}PMDC registration no. 00000-P</p>
        </figcaption>
      </figure>
      <div class="about__copy">
        <h2 class="display h2" id="about-title">About {e(clinic)}</h2>
        <p class="about__lede">{e(clinic)} is {article(spec['name'])} {e(lower_name(spec['name']))} clinic in {e(spec['area'])}, {e(spec['city'])}, led by {e(lead['name'])}.</p>
        <p>{e(lead['name'])} has {lead['years']} years of experience and holds {e(lead['quals'])}. The clinic team sees {e(AUDIENCE.get(spec['slug'], 'adults and children'))}, explains every diagnosis in plain language, and shares fees before any treatment starts.</p>
        <dl class="facts facts--about">
          <div><dt>Consultation fee</dt><dd>{e(fee_range(spec))}</dd></div>
          <div><dt>Clinic hours</dt><dd>{e(hours_short)}</dd></div>
          <div><dt>Languages</dt><dd>Urdu and English</dd></div>
        </dl>
      </div>
    </div>
  </section>

  <section class="section section--tint" id="treatments" aria-labelledby="treatments-title">
    <div class="container">
      <div class="section-head">
        <h2 class="display h2" id="treatments-title">Treatments and services</h2>
        <p>Ask when you book if you need a specific procedure. Fees are shared before treatment starts.</p>
      </div>
      <ul class="services">{services}</ul>
      <div class="conditions">
        <h3 class="conditions__title">Conditions we treat</h3>
        <ul class="tags">{conditions}</ul>
      </div>
    </div>
  </section>

  <section class="section" id="doctors" aria-labelledby="doctors-title">
    <div class="container">
      <div class="section-head">
        <h2 class="display h2" id="doctors-title">Our doctors</h2>
        <p>Fees are per consultation. The time shown is each doctor's next free slot.</p>
      </div>
      <ul class="doc-rows">{''.join(doctor_row(doc) for doc in docs)}</ul>
    </div>
  </section>

  <section class="section section--line" aria-labelledby="signs-title">
    <div class="container split">
      <div>
        <h2 class="display h2" id="signs-title">When to see {article(who)} {e(who)}</h2>
        <ul class="checks">{signs}</ul>
      </div>
      {side}
    </div>
  </section>

  <section class="section section--scrub" id="reviews" aria-labelledby="reviews-title">
    <div class="container">
      <div class="section-head">
        <h2 class="display h2" id="reviews-title">What our patients say</h2>
      </div>
      <ul class="quotes">{reviews}</ul>
    </div>
  </section>

  <section class="section" aria-labelledby="faq-title">
    <div class="container split">
      <div class="split__head">
        <h2 class="display h2" id="faq-title">Common questions</h2>
        <p>Still have a question? <a class="text-link" href="{e(wa(f'Assalam o Alaikum, I have a question for {clinic}.'))}" target="_blank" rel="noopener">Ask us on WhatsApp</a>.</p>
      </div>
      <div class="faqs">{faqs}</div>
    </div>
  </section>

  <section class="section section--line" id="visit" aria-labelledby="visit-title">
    <div class="container visit">
      <div class="visit__info">
        <h2 class="display h2" id="visit-title">Visit the clinic</h2>
        <p class="visit__address">{icon('pin')}<span>{e(spec['address'])}</span></p>
        <dl class="hours">{hours_rows}</dl>
        <ul class="contact-list contact-list--visit">
          <li>{icon('phone')}<a href="{tel(SITE['phone'])}">{e(SITE['phone'])}</a></li>
          <li>{icon('message')}<a href="{e(wa())}" target="_blank" rel="noopener">WhatsApp {e(SITE['phone'])}</a></li>
          <li>{icon('mail')}<a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></li>
        </ul>
      </div>
      <div class="map-card">
        <div class="map-card__map" aria-hidden="true">
          <span class="map-card__road map-card__road--h"></span>
          <span class="map-card__road map-card__road--v"></span>
          <span class="map-card__road map-card__road--d"></span>
          <span class="map-card__pin">{icon(spec['icon'])}</span>
        </div>
        <div class="map-card__foot">
          <div><p class="map-card__name">{e(clinic)}</p><p>{e(spec['area'])}, {e(spec['city'])}</p></div>
          <a class="btn btn-ghost btn-sm" href="https://www.google.com/maps/search/?api=1&amp;query={e(quote(spec['address']))}" target="_blank" rel="noopener">{icon('directions')}Get directions</a>
        </div>
      </div>
    </div>
  </section>

  <section class="cta-band">
    <div class="container cta-band__inner">
      <div>
        <h2 class="display h2">Ready to see {article(who)} {e(who)}?</h2>
        <p>Pick a day and time. The clinic confirms on WhatsApp.</p>
      </div>
      <button class="btn btn-light" type="button" data-book>Book appointment</button>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container site-footer__grid site-footer__grid--clinic">
    <div class="site-footer__brand">
      {brand(spec)}
      <p>{e(clinic)}, {e(spec['area'])}, {e(spec['city'])}. {e(spec['alias'])}.</p>
    </div>
    <div>
      <h2 class="site-footer__title">Clinic hours</h2>
      <dl class="hours hours--footer">{hours_rows}</dl>
    </div>
    <div>
      <h2 class="site-footer__title">Contact</h2>
      <ul class="contact-list">
        <li>{icon('phone')}<a href="{tel(SITE['phone'])}">{e(SITE['phone'])}</a></li>
        <li>{icon('mail')}<a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></li>
        <li>{icon('pin')}<span>{e(spec['address'])}</span></li>
      </ul>
    </div>
  </div>
  <div class="container site-footer__bottom">
    <p>&copy; {YEAR} {e(clinic)}. Demo website by {e(SITE['agency'])}.</p>
    <p>Doctor names, fees, reviews and photos on this demo are placeholders.</p>
  </div>
</footer>

<div class="action-bar" aria-label="Quick actions">
  <a class="btn btn-ghost" href="{tel(SITE['phone'])}">{icon('phone')}Call</a>
  <button class="btn btn-accent" type="button" data-book>Book appointment</button>
</div>
{booking_dialog(spec)}"""

    return (f"{head(title, desc, url, spec['accent'])}\n"
            f'<body class="clinic-site" data-whatsapp="{e(SITE["whatsapp"])}" data-clinic="{e(clinic)}" style="{theme(spec)}">\n'
            f"{body}\n</body>\n</html>\n")


# ---------------------------------------------------------------------------
# Your private list of demo links (sites/index.html)
# ---------------------------------------------------------------------------
def build_catalog() -> str:
    base = SITE["baseUrl"].rstrip("/")
    items = "".join(f"""<li class="demo-item" style="{theme(s)}">
  <div class="plate plate--static">
    <span class="plate__icon">{icon(s['icon'])}</span>
    <span class="plate__text">
      <span class="plate__name">{e(s['plate'])}</span>
      <span class="plate__for">{e(s['demo']['clinic'])}</span>
    </span>
  </div>
  <p class="demo-item__url"><span data-url="{e(s['demo']['path'])}/">{e(base)}/{e(s['demo']['path'])}/</span></p>
  <div class="demo-item__actions">
    <a class="btn btn-ghost btn-sm" href="{e(s['demo']['path'])}/" target="_blank" rel="noopener">{icon('external')}Open</a>
    <button class="btn btn-accent btn-sm" type="button" data-copy="{e(s['demo']['path'])}/">{icon('copy')}<span>Copy link</span></button>
  </div>
</li>""" for s in SPECS)
    body = f"""
<main id="main" class="catalog">
  <div class="container">
    <div class="catalog__head">
      <span class="brand__mark">{icon('logo')}</span>
      <div>
        <h1 class="display h2">Clinic website demos</h1>
        <p>Send each doctor the link for their own specialty. Each demo is a separate website and doesn't link to the others.</p>
      </div>
    </div>
    <ul class="demo-list">{items}</ul>
    <p class="catalog__note">This list is for you. Delete <code>sites/index.html</code> if you don't want anyone to find it at the main address.</p>
  </div>
</main>
<p class="toast" role="status" aria-live="polite" hidden></p>"""
    page_title = f"Clinic website demos | {SITE['agency']}"
    return (f"{head(page_title, 'All 16 clinic demo links.', base + '/', '#14213D')}\n"
            f'<body class="catalog-page">\n{body}\n</body>\n</html>\n')


def build_404() -> str:
    body = """
<main id="main" class="notfound ecg">
  <div class="container notfound__inner">
    <div class="pulse pulse--flat" aria-hidden="true">
      <svg viewBox="0 0 1200 100" preserveAspectRatio="none" focusable="false"><path class="pulse__base" vector-effect="non-scaling-stroke" d="M0 62H1200"/></svg>
    </div>
    <h1 class="display notfound__title">This page has no pulse.</h1>
    <p>The link may be old or mistyped. Check the address and try again.</p>
  </div>
</main>"""
    return f"{head('Page not found', 'This page does not exist.', SITE['baseUrl'], '#14213D', '/')}\n<body>\n{body}\n</body>\n</html>\n"


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(SRC_ASSETS, OUT / "assets")
    (OUT / "index.html").write_text(build_catalog(), encoding="utf-8")
    (OUT / "404.html").write_text(build_404(), encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    for spec in SPECS:
        folder = OUT / spec["demo"]["path"]
        shutil.copytree(SRC_ASSETS, folder / "assets")
        (folder / "index.html").write_text(build_clinic(spec), encoding="utf-8")
        (folder / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    print(f"Built {len(SPECS)} clinic sites into {OUT.relative_to(ROOT)}/:")
    for spec in SPECS:
        print(f"  /{spec['demo']['path']}/  {spec['demo']['clinic']}")


if __name__ == "__main__":
    main()
