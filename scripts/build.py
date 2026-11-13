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
    "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 13.2 17 22l-5-3-5 3 1.5-8.8"/>',
    "sparkle": '<path d="M12 3l1.9 5.6L19.5 10l-5.6 1.9L12 17.5l-1.9-5.6L4.5 10l5.6-1.4Z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8Z"/>',
    "clipboard": '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "receipt": '<path d="M4 2v20l3-2 3 2 3-2 3 2 3-2 2 2V2l-2 2-3-2-3 2-3-2-3 2Z"/><path d="M8 8h8M8 12h8M8 16h5"/>',
    "calendar-check": '<rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/><path d="m9 15 2 2 4-4"/>',
}


def icon(name: str, cls: str = "icon", filled: bool = False) -> str:
    paint = 'fill="currentColor" stroke="none"' if filled else 'fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg class="{cls}" viewBox="0 0 24 24" {paint} aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


# ---------------------------------------------------------------------------
# Images: "photo-..." = Unsplash id, anything else = a file inside the site folder
# (for example "assets/img/doctor.jpg"). A failed image shows a designed fallback.
# ---------------------------------------------------------------------------
FALLBACK_JS = "this.parentNode.classList.add('is-fallback');this.remove()"


def img_url(ref: str, width: int, height: int | None = None, faces: bool = False) -> str:
    if ref.startswith("photo-"):
        crop = f"&h={height}" if height else ""
        focus = "&crop=faces" if faces else ""
        return f"https://images.unsplash.com/{ref}?auto=format&fit=crop{focus}&w={width}{crop}&q=75"
    return ref


def picture(ref: str | None, alt: str, widths: tuple[int, ...], sizes: str, ratio: tuple[float, float],
            eager: bool = False, faces: bool = False) -> str:
    if not ref:
        return ""
    w0 = widths[-1]
    h0 = round(w0 * ratio[1] / ratio[0])
    srcset = ""
    if ref.startswith("photo-"):
        srcset = ", ".join(f"{img_url(ref, w, round(w * ratio[1] / ratio[0]), faces)} {w}w" for w in widths)
        srcset = f' srcset="{e(srcset)}" sizes="{e(sizes)}"'
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{e(img_url(ref, w0, h0, faces))}"{srcset} alt="{e(alt)}" width="{w0}" height="{h0}" '
            f'{loading} decoding="async" onerror="{FALLBACK_JS}">')


def media(ref: str | None, alt: str, cls: str, widths: tuple[int, ...], sizes: str, ratio: tuple[float, float],
          fallback_icon: str, eager: bool = False, faces: bool = False, extra: str = "", attrs: str = "") -> str:
    """A photo in a frame, with a designed fallback in the specialty colour."""
    img = picture(ref, alt, widths, sizes, ratio, eager, faces)
    fb = "" if ref else " is-fallback"
    return (f'<div class="media {cls}{fb}"{attrs}>{img}'
            f'<div class="media__fallback" aria-hidden="true">{icon(fallback_icon)}</div>{extra}</div>')


# ---------------------------------------------------------------------------
# Placeholder doctors (deterministic). Replace with the real doctor's details
# when you customise a demo for a client. Photo ids are checked Unsplash photos.
# ---------------------------------------------------------------------------
DOCTOR_PHOTOS = {
    "f": ["photo-1638202993928-7267aad84c31", "photo-1594824476967-48c8b964273f", "photo-1559839734-2b71ea197ec2",
          "photo-1659353888906-adb3e0041693", "photo-1584432810601-6c7f27d2362b", "photo-1758691462651-611d730c5272",
          "photo-1770134223774-13b735e29201", "photo-1736289173074-df6009da27c9"],
    "m": ["photo-1612349317150-e413f6a5b16d", "photo-1758691463582-11aea602cd4a", "photo-1622253692010-333f2da6031d",
          "photo-1637059824899-a441006a6875", "photo-1645066928295-2506defde470", "photo-1758691463393-a2aa9900af8a",
          "photo-1758691461513-88a0aef72160", "photo-1712215544003-af10130f8eb3"],
}
GALLERY = [("photo-1764727291644-5dcb0b1a0375", "Reception"), ("photo-1762625570087-6d98fca29531", "Waiting area"),
           ("photo-1704455306925-1401c3012117", "Treatment room")]
SIGN_PHOTOS = ["photo-1758691461990-03b49d969495", "photo-1758691462430-81160850496c", "photo-1758691462071-757bca955439"]
WHY_PHOTOS = ["photo-1758691462071-757bca955439", "photo-1758691463198-dc663b8a64e4", "photo-1666886573531-48d2e3c2b684"]
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


def make_clinic(spec: dict, index: int) -> None:
    rng = random.Random(spec["slug"])
    genders = ["f", "f", "f"] if spec.get("femaleOnly") else rng.choice(GENDER_PATTERNS)
    used = {"f": 0, "m": 0}
    doctors = []
    for g in genders:
        while True:
            name = f"{rng.choice(FIRST[g])} {rng.choice(LAST)}"
            if name not in _used_names:
                _used_names.add(name)
                break
        full = name if spec.get("noTitle") else f"Dr. {name}"
        pool = DOCTOR_PHOTOS[g]
        photo = pool[(index * 3 + used[g]) % len(pool)]  # different faces on different demos, never repeated on one
        used[g] += 1
        doctors.append({
            "name": full, "initials": initials(full), "gender": g, "photo": photo,
            "quals": rng.choice(QUALS[spec["slug"]]), "years": rng.randint(6, 24),
            "rating": round(rng.uniform(4.6, 4.95), 1), "reviews": rng.randint(38, 640),
            "fee": rng.randrange(spec["feeMin"], spec["feeMax"] + 1, 500),
            "slot": rng.choice(SLOTS), "days": rng.choice(DAYS),
        })
    doctors.sort(key=lambda d: -d["years"])  # the most experienced doctor leads the clinic
    area, city = rng.choice(AREAS)
    spec["doctors"] = doctors
    spec["lead"] = doctors[0]
    spec["area"], spec["city"] = area, city
    spec["address"] = f"{SITE['street']}, {area}, {city}"
    spec["hours"] = rng.choice(HOURS)
    spec["why_photo"] = WHY_PHOTOS[index % len(WHY_PHOTOS)]
    spec["sign_photo"] = SIGN_PHOTOS[(index + 1) % len(SIGN_PHOTOS)]
    total_reviews = sum(d["reviews"] for d in doctors)
    spec["review_count"] = total_reviews
    spec["avg_rating"] = round(sum(d["rating"] for d in doctors) / len(doctors), 1)
    spec["patients"] = round(total_reviews * 18 / 500) * 500
    sunday = spec["hours"][-1][1]
    spec["open_days"] = 6 if sunday in ("Closed", "By appointment") else 7


for _i, _s in enumerate(SPECS):
    make_clinic(_s, _i)


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
<script>document.documentElement.classList.add('js')</script>
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
    return f"""<a class="brand" href="#top" aria-label="{e(d['clinic'])} home">
      <span class="brand__mark">{icon(spec['icon'])}</span>
      <span class="brand__text"><span class="brand__name">{e(d['short'])}</span><span class="brand__tag">{e(d['tag'])}</span></span>
    </a>"""


def topbar(spec: dict) -> str:
    day, time = spec["hours"][0]
    return f"""<div class="topbar">
  <div class="container topbar__inner">
    <span class="topbar__item">{icon('clock')}{e(day)}: {e(time)}</span>
    <span class="topbar__item">{icon('pin')}{e(spec['address'])}</span>
    <a class="topbar__item topbar__item--end" href="{tel(SITE['phone'])}">{icon('phone')}Appointments: {e(SITE['phone'])}</a>
  </div>
</div>"""


def header(spec: dict) -> str:
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<span id="top"></span>
{topbar(spec)}
<header class="site-header">
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
        <li><a href="#visit">Contact</a></li>
      </ul>
      <a class="site-nav__phone" href="{tel(SITE['phone'])}">{icon('phone')}{e(SITE['phone'])}</a>
      <button class="btn btn-accent site-nav__cta" type="button" data-book>Book appointment</button>
    </nav>
  </div>
</header>"""


def pulse_line() -> str:
    return """
<div class="pulse" aria-hidden="true">
  <svg viewBox="0 0 1200 100" preserveAspectRatio="none" focusable="false">
    <path class="pulse__base" vector-effect="non-scaling-stroke" d="M0 62H470l14-9 14 9h36"/>
    <path class="pulse__beat" vector-effect="non-scaling-stroke" d="M534 62l10 12 16-64 17 76 12-24"/>
    <path class="pulse__base" vector-effect="non-scaling-stroke" d="M589 62h47l18-13 18 13H1200"/>
  </svg>
</div>"""


def avatar(doc: dict, cls: str, widths=(120, 240), sizes="60px", ratio=(1, 1)) -> str:
    img = picture(doc["photo"], f"Portrait of {doc['name']}", widths, sizes, ratio, faces=True)
    fallback = "" if doc["photo"] else " is-fallback"
    return (f'<div class="avatar media {cls}{fallback}">{img}'
            f'<span class="media__fallback avatar__initials" aria-hidden="true">{e(doc["initials"])}</span></div>')


def book_attrs(doc: dict | None = None) -> str:
    return f' data-doctor="{e(doc["name"])}"' if doc else ""


def stars(n: int = 5) -> str:
    return f'<span class="stars" aria-hidden="true">{icon("star", filled=True) * n}</span>'


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
      <button class="btn btn-accent btn-block btn-lg" type="submit">Request appointment</button>
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
# Hero variants
# ---------------------------------------------------------------------------
def hero_copy(spec: dict, light: bool = False) -> str:
    d, lead = spec["demo"], spec["lead"]
    call_cls = "btn-outline-light" if light else "btn-ghost"
    faces = "".join(avatar(doc, "", (96, 160), "46px") for doc in spec["doctors"])
    return f"""<div class="hero__copy">
        <p class="hero__place" data-reveal><span class="hero__place-dot" aria-hidden="true"></span><span>{e(d['clinic'])}<span class="hero__place-area">, {e(spec['area'])}</span>, {e(spec['city'])}</span></p>
        <h1 class="display hero__title" data-reveal style="--d:80ms">{e(d['headline'])}</h1>
        <p class="hero__lede" data-reveal style="--d:160ms">{e(spec['intro'])}</p>
        <div class="hero__actions" data-reveal style="--d:240ms">
          <button class="btn btn-accent btn-lg" type="button" data-book>{icon('calendar-check')}Book appointment</button>
          <a class="btn {call_cls} btn-lg" href="{tel(SITE['phone'])}">{icon('phone')}Call {e(SITE['phone'])}</a>
        </div>
        <div class="hero__trust" data-reveal style="--d:320ms">
          <div class="avatars">{faces}</div>
          <p class="hero__trust-text">{stars()} <strong>{spec['avg_rating']}</strong> average rating<br>from {spec['review_count']:,} patient reviews</p>
        </div>
      </div>"""


def token_slip(spec: dict) -> str:
    lead = spec["lead"]
    return f"""<div class="slip" aria-hidden="true">
          <div class="slip__top">
            <div><span class="slip__label">Your token</span><span class="slip__num">14</span></div>
            <p class="slip__now"><span class="slip__dot"></span>Now seeing <strong>11</strong></p>
          </div>
          <div class="slip__perf"></div>
          <div class="slip__body">
            <p class="slip__doctor">{e(lead['name'])}</p>
            <p class="slip__spec">{e(cap(spec['specialist']))}</p>
            <p class="slip__line">{icon('clock')}{e(lead['slot'])}</p>
          </div>
        </div>"""


def hero_a(spec: dict) -> str:
    alt = f"{spec['name']} care at {spec['demo']['clinic']}"
    main_img = media(spec["image"], alt, "collage__main", (560, 820, 1100), "(min-width: 900px) 46vw, 92vw", (4, 4.6), spec["icon"], eager=True)
    second = media(spec["image2"], f"Inside {spec['demo']['clinic']}", "collage__second", (320, 480), "220px", (1, 1), spec["icon"])
    return f"""<section class="hero hero--a">
    <span class="hero__glow hero__glow--1" aria-hidden="true"></span>
    <span class="hero__glow hero__glow--2" aria-hidden="true"></span>
    <span class="hero__dots" aria-hidden="true"></span>
    <div class="container hero__grid">
      {hero_copy(spec)}
      <div class="hero__visual" data-reveal="zoom" style="--d:200ms">
        <div class="collage">
          <span class="collage__ring" aria-hidden="true"></span>
          {main_img}
          {second}
          <div class="float-card float-card--rating float-card--bob">
            <span class="float-card__icon">{icon('award')}</span>
            <div><strong>{spec['lead']['years']}+ years</strong><span>of specialist experience</span></div>
          </div>
          {token_slip(spec)}
        </div>
      </div>
    </div>
    {pulse_line()}
  </section>"""


def hero_b(spec: dict) -> str:
    alt = f"{spec['name']} care at {spec['demo']['clinic']}"
    photo = media(spec["image"], alt, "hero__photo", (900, 1400, 2000), "100vw", (16, 9), spec["icon"], eager=True)
    next_slot = min((doc["slot"] for doc in spec["doctors"]), key=SLOTS.index)
    return f"""<section class="hero hero--b">
    {photo}
    <div class="hero__shade" aria-hidden="true"></div>
    <div class="container hero__grid">
      {hero_copy(spec, light=True)}
      <form class="quick-book" data-quick data-reveal="right" style="--d:250ms" novalidate>
        <h2 class="quick-book__title">Book a visit</h2>
        <p class="quick-book__sub">Takes less than a minute. We confirm on WhatsApp.</p>
        <div class="field">
          <label for="q-name">Patient's name</label>
          <input id="q-name" name="name" autocomplete="name" placeholder="Full name">
        </div>
        <div class="field">
          <label for="q-phone">Mobile number</label>
          <input id="q-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="0300 1234567">
        </div>
        <div class="field">
          <label for="q-day">Day</label>
          <select id="q-day" name="day"><option>Today</option><option>Tomorrow</option><option value="date">Pick a date</option></select>
        </div>
        <p class="quick-book__slot">{icon('clock')}<span>Next free slot: <strong>{e(next_slot)}</strong></span></p>
        <button class="btn btn-accent btn-block btn-lg" type="submit">Continue booking{icon('arrow', 'icon icon--arrow')}</button>
      </form>
    </div>
  </section>"""


def hero_c(spec: dict) -> str:
    alt = f"{spec['name']} care at {spec['demo']['clinic']}"
    banner = media(spec["image"], alt, "banner__media", (700, 1100, 1600), "(min-width: 1220px) 1180px, 94vw", (21, 9), spec["icon"], eager=True)
    return f"""<section class="hero hero--c">
    <div class="container">
      {hero_copy(spec)}
      <div class="banner" data-reveal="zoom" style="--d:280ms">
        {banner}
        <div class="banner__cards">
          <div class="float-card float-card--bob"><span class="float-card__icon">{icon('shield')}</span><div><strong>PMDC registered</strong><span>Qualified, verified doctors</span></div></div>
          <div class="float-card float-card--bob-alt"><span class="float-card__icon">{icon('message')}</span><div><strong>WhatsApp booking</strong><span>Confirmed within the hour</span></div></div>
          <div class="float-card float-card--bob"><span class="float-card__icon">{icon('receipt')}</span><div><strong>Clear fees</strong><span>Shared before treatment</span></div></div>
        </div>
      </div>
    </div>
  </section>"""


# ---------------------------------------------------------------------------
# A clinic site
# ---------------------------------------------------------------------------
SERVICE_ICONS = [None, "clipboard", "sparkle", "shield", "calendar-check", "award"]
# Where each card animates in from, by its position in a grid, so rows sweep in from the corners.
GRID3 = ["top-left", "down", "top-right", "bottom-left", "up", "bottom-right"]
GRID2 = ["top-left", "top-right", "bottom-left", "bottom-right"]


def reveal(kind: str, delay: int = 0) -> str:
    return f' data-reveal="{kind}" style="--d:{delay}ms"'


def build_clinic(spec: dict) -> str:
    d = spec["demo"]
    lead = spec["lead"]
    docs = spec["doctors"]
    who, who_pl = spec["specialist"], spec["specialists"]
    clinic = d["clinic"]
    layout = d["layout"]
    url = f"{SITE['baseUrl'].rstrip('/')}/{d['path']}/"
    hero = {"a": hero_a, "b": hero_b, "c": hero_c}[layout](spec)
    wa_question = wa(f"Assalam o Alaikum, I have a question for {clinic}.")

    stats = f"""<section class="stats-band" aria-label="Clinic at a glance">
    <div class="container">
      <div class="stats" data-reveal="zoom">
        <div class="stat"><span class="stat__num" data-count="{lead['years']}" data-suffix="+">{lead['years']}+</span><span class="stat__label">Years of experience</span></div>
        <div class="stat"><span class="stat__num" data-count="{spec['patients']}" data-suffix="+">{spec['patients']:,}+</span><span class="stat__label">Patients treated</span></div>
        <div class="stat"><span class="stat__num" data-count="{spec['avg_rating']}" data-decimals="1">{spec['avg_rating']}</span><span class="stat__label">Average patient rating</span></div>
        <div class="stat"><span class="stat__num" data-count="{spec['open_days']}" data-suffix=" days">{spec['open_days']} days</span><span class="stat__label">Open every week</span></div>
      </div>
    </div>
  </section>"""

    about_main = media(lead["photo"], f"Portrait of {lead['name']}", "about__main", (480, 760), "(min-width: 900px) 40vw, 90vw", (4, 5), spec["icon"], faces=True)
    about_second = media(GALLERY[0][0], f"Reception at {clinic}", "about__second", (360, 540), "260px", (4, 3.4), spec["icon"])
    ticks = "".join(f"<li>{icon('check')}<span>{e(t)}</span></li>" for t in
                    ["PMDC-registered doctors", "Fees shared before treatment", "Sterilised, modern equipment", "WhatsApp booking and reminders"])
    about = f"""<section class="section" id="about" aria-labelledby="about-title">
    <div class="container about">
      <div class="about__media" data-reveal="left">
        {about_main}
        {about_second}
        <div class="about__badge"><div><strong>{lead['years']}+</strong><span>years of experience</span></div></div>
      </div>
      <div class="about__copy" data-reveal="right">
        <p class="kicker">About the clinic</p>
        <h2 class="display h2" id="about-title">Trusted {e(lower_name(spec['name']))} care in {e(spec['city'])}</h2>
        <p class="about__lede">{e(clinic)} is {article(spec['name'])} {e(lower_name(spec['name']))} clinic in {e(spec['area'])}, {e(spec['city'])}, led by {e(lead['name'])}.</p>
        <p>{e(lead['name'])} has {lead['years']} years of experience and holds {e(lead['quals'])}. The clinic team sees {e(AUDIENCE.get(spec['slug'], 'adults and children'))}, explains every diagnosis in plain language, and shares fees before any treatment starts.</p>
        <ul class="ticks">{ticks}</ul>
        <div class="signature">
          {avatar(lead, '')}
          <div>
            <p class="signature__name">{e(lead['name'])}</p>
            <p class="signature__meta">{e(lead['quals'])}</p>
            <p class="signature__reg">{icon('shield')}PMDC registration no. 00000-P</p>
          </div>
        </div>
        <div class="about__actions">
          <button class="btn btn-accent" type="button" data-book{book_attrs(lead)}>Book with {e(lead['name'])}</button>
          <a class="btn btn-ghost" href="#doctors">Meet our doctors{icon('arrow', 'icon icon--arrow')}</a>
        </div>
      </div>
    </div>
  </section>"""

    service_cards = "".join(
        f"""<li class="service-card"{reveal(GRID3[i % 6], (i % 3) * 90)}>
          <span class="service-card__icon">{icon(SERVICE_ICONS[i % 6] or spec['icon'])}</span>
          <h3>{e(s['name'])}</h3>
          <p>{e(s['desc'])}</p>
          <button class="service-card__link" type="button" data-book>Book this{icon('arrow')}</button>
        </li>""" for i, s in enumerate(spec["services"]))
    conditions = "".join(
        f'<li{reveal("left" if i % 2 == 0 else "right", (i // 2) * 70)}>{icon("check")}<span>{e(c)}</span></li>'
        for i, c in enumerate(spec["conditions"]))
    services = f"""<section class="section section--tint" id="treatments" aria-labelledby="treatments-title">
    <div class="container">
      <div class="section-head section-head--center" data-reveal>
        <p class="kicker">Treatments</p>
        <h2 class="display h2" id="treatments-title">Treatments and services</h2>
        <p>Ask when you book if you need a specific procedure. Fees are shared before treatment starts.</p>
      </div>
      <ul class="services">{service_cards}</ul>
      <div class="conditions" data-reveal="up">
        <div class="conditions__intro">
          <span class="conditions__icon">{icon(spec['icon'])}</span>
          <h3 class="conditions__title">Conditions we treat</h3>
          <p>Don't see your problem here? Send us a message and the clinic team will tell you if we can help.</p>
          <a class="btn btn-accent btn-sm" href="{e(wa_question)}" target="_blank" rel="noopener">{icon('message')}Ask on WhatsApp</a>
        </div>
        <ul class="conditions__grid">{conditions}</ul>
      </div>
    </div>
  </section>"""

    why_items = [
        ("award", "Qualified specialists", f"Experienced {who_pl} with recognised qualifications."),
        ("receipt", "Fees shared upfront", "You'll know the cost before any test or treatment starts."),
        ("clock", "Short waiting times", "Book on WhatsApp and arrive close to your token time."),
        ("sparkle", "Clean, modern clinic", "Sterilised equipment and a comfortable, private waiting area."),
    ]
    why_list = "".join(
        f'<li class="why__item"{reveal(GRID2[i], i * 90)}>{icon(ic)}<h3>{e(t)}</h3><p>{e(dsc)}</p></li>'
        for i, (ic, t, dsc) in enumerate(why_items))
    why_img = media(spec["why_photo"], f"A doctor with a patient at {clinic}", "why__media", (560, 900), "(min-width: 900px) 44vw, 92vw", (4, 4.4), spec["icon"])
    why = f"""<section class="why" aria-labelledby="why-title">
    <div class="container why__grid">
      <div class="why__media-wrap" data-reveal="left">
        {why_img}
        <div class="float-card float-card--bob"><span class="float-card__icon">{icon('users')}</span><div><strong>{spec['patients']:,}+ patients</strong><span>have trusted {e(d['short'])}</span></div></div>
      </div>
      <div class="why__copy">
        <p class="kicker" data-reveal>Why choose us</p>
        <h2 class="display h2" id="why-title" data-reveal>Why patients choose {e(d['short'])}</h2>
        <p data-reveal>Good care starts with being listened to. Here's what you can expect from every visit.</p>
        <ul class="why__list">{why_list}</ul>
      </div>
    </div>
  </section>"""

    doc_cards = "".join(
        f"""<li class="doc-card"{reveal(["left", "up", "right"][i % 3], i * 100)}>
          {media(doc['photo'], f"Portrait of {doc['name']}", 'doc-card__photo', (420, 640), '(min-width: 1080px) 380px, (min-width: 640px) 46vw, 92vw', (4, 4.3), spec['icon'], faces=True,
                 extra=f'<span class="doc-card__exp">{doc["years"]} years experience</span><div class="doc-card__hover"><button class="btn btn-light btn-block" type="button" data-book{book_attrs(doc)}>{icon("calendar-check")}Book appointment</button></div>')}
          <div class="doc-card__body">
            <h3 class="doc-card__name">{e(doc['name'])}</h3>
            <p class="doc-card__quals">{e(doc['quals'])}</p>
            <ul class="meta">
              <li>{icon('star', 'icon icon--star', filled=True)}<span><strong>{doc['rating']}</strong> ({doc['reviews']} reviews)</span></li>
              <li>{icon('calendar')}Sees patients {e(doc['days'])}</li>
            </ul>
            <div class="doc-card__foot">
              <div><p class="doc-card__fee"><span>Consultation fee</span>{rs(doc['fee'])}</p><p class="doc-card__slot">{icon('clock')}Next: {e(doc['slot'])}</p></div>
              <button class="btn btn-accent btn-sm" type="button" data-book{book_attrs(doc)}>Book</button>
            </div>
          </div>
        </li>""" for i, doc in enumerate(docs))
    doctors = f"""<section class="section" id="doctors" aria-labelledby="doctors-title">
    <div class="container">
      <div class="section-head section-head--center" data-reveal>
        <p class="kicker">Our team</p>
        <h2 class="display h2" id="doctors-title">Meet our doctors</h2>
        <p>Fees are per consultation. The time shown is each doctor's next free slot.</p>
      </div>
      <ul class="doc-grid">{doc_cards}</ul>
    </div>
  </section>"""

    gallery_items = [(spec["image2"], "Consultation room")] + GALLERY
    gallery_html = "".join(
        f"""<figure class="gallery__item media{'' if ref else ' is-fallback'}"{reveal(["left", "top-right", "right", "bottom-right"][i], i * 90)}>
          {picture(ref, f'{cap_} at {clinic}', (480, 800), '(min-width: 900px) 40vw, 92vw', (4, 3))}
          <div class="media__fallback" aria-hidden="true">{icon(spec['icon'])}</div>
          <figcaption>{e(cap_)}</figcaption>
        </figure>""" for i, (ref, cap_) in enumerate(gallery_items))
    gallery = f"""<section class="section section--tint" aria-labelledby="gallery-title">
    <div class="container">
      <div class="section-head" data-reveal>
        <p class="kicker">Inside the clinic</p>
        <h2 class="display h2" id="gallery-title">A calm, clean place to get better</h2>
      </div>
      <div class="gallery">{gallery_html}</div>
    </div>
  </section>"""

    signs = "".join(f'<li{reveal("left", i * 70)}>{icon("check")}<span>{e(s)}</span></li>' for i, s in enumerate(spec["signs"]))
    if spec.get("alert"):
        side = f"""<aside class="callout callout--alert" role="note" data-reveal="top-right">
          {icon('alert', 'icon callout__icon')}
          <div><h3>When it can't wait</h3><p>{e(spec['alert'])}</p>
          <a class="btn btn-ghost btn-sm" href="tel:1122">{icon('phone')}Call 1122</a></div>
        </aside>"""
    else:
        side = f"""<aside class="callout" data-reveal="top-right">
          {icon('message', 'icon callout__icon')}
          <div><h3>Not sure if you need to come in?</h3>
          <p>Send us a message on WhatsApp. Our team will tell you whether you need a visit and which doctor to see.</p>
          <a class="btn btn-accent btn-sm" href="{e(wa_question)}" target="_blank" rel="noopener">{icon('message')}Message us on WhatsApp</a></div>
        </aside>"""
    when = f"""<section class="section" aria-labelledby="signs-title">
    <div class="container split">
      <div>
        <p class="kicker" data-reveal>Know the signs</p>
        <h2 class="display h2" id="signs-title" data-reveal>When to see {article(who)} {e(who)}</h2>
        <ul class="checks">{signs}</ul>
      </div>
      <div class="callout-stack">
        {side}
        <div class="sign-photo" data-reveal="bottom-right">
          {media(spec["sign_photo"], f"A doctor with a patient at {clinic}", "sign-photo__media", (560, 900), "(min-width: 900px) 44vw, 92vw", (16, 11), spec["icon"])}
          <p class="sign-photo__chip">{icon('calendar-check')}Same-day appointments available</p>
        </div>
      </div>
    </div>
  </section>"""

    review_cards = "".join(
        f"""<li class="review"{reveal(["right", "up", "left"][i % 3], i * 100)}>
          <span class="review__mark" aria-hidden="true">&ldquo;</span>
          {stars()}
          <blockquote><p>{e(r['q'])}</p></blockquote>
          <p class="review__by"><span class="review__avatar" aria-hidden="true">{e(''.join(w[0] for w in r['n'].replace('.', '').split()[:2]).upper())}</span>
          <span><strong>{e(r['n'])}</strong><span>{e(r['c'])}</span></span></p>
        </li>""" for i, r in enumerate(d["reviews"]))
    reviews = f"""<section class="section section--tint" id="reviews" aria-labelledby="reviews-title">
    <div class="container">
      <div class="reviews-head">
        <div class="section-head" data-reveal>
          <p class="kicker">Patient reviews</p>
          <h2 class="display h2" id="reviews-title">What our patients say</h2>
        </div>
        <div class="rating-box" data-reveal="right">
          <span class="rating-box__num">{spec['avg_rating']}</span>
          <div>{stars()}<p>Based on {spec['review_count']:,} reviews</p></div>
        </div>
      </div>
      <ul class="reviews">{review_cards}</ul>
    </div>
  </section>"""

    faq_items = "".join(
        f'<details class="faq"{reveal("right", i * 70)}><summary><span>{e(f["q"])}</span>{icon("plus", "icon faq__icon")}</summary>'
        f'<div class="faq__answer"><p>{e(f["a"])}</p></div></details>' for i, f in enumerate(spec["faqs"]))
    faq = f"""<section class="section" aria-labelledby="faq-title">
    <div class="container split">
      <div class="split__head" data-reveal="left">
        <p class="kicker">FAQs</p>
        <h2 class="display h2" id="faq-title">Common questions</h2>
        <p>Answers to what patients ask us most often.</p>
        <div class="faq-card">
          <strong>Still have a question?</strong>
          <p>Our team replies on WhatsApp during clinic hours.</p>
          <a class="btn btn-accent btn-sm" href="{e(wa_question)}" target="_blank" rel="noopener">{icon('message')}Ask on WhatsApp</a>
        </div>
      </div>
      <div class="faqs">{faq_items}</div>
    </div>
  </section>"""

    hours_rows = "".join(f"<div><dt>{e(day)}</dt><dd>{e(time)}</dd></div>" for day, time in spec["hours"])
    visit = f"""<section class="section section--line" id="visit" aria-labelledby="visit-title">
    <div class="container visit">
      <div class="visit__info" data-reveal="left">
        <p class="kicker">Visit us</p>
        <h2 class="display h2" id="visit-title">Find the clinic</h2>
        <p class="visit__address">{icon('pin')}<span>{e(spec['address'])}</span></p>
        <dl class="hours">{hours_rows}</dl>
        <ul class="contact-list contact-list--visit">
          <li>{icon('phone')}<a href="{tel(SITE['phone'])}">{e(SITE['phone'])}</a></li>
          <li>{icon('message')}<a href="{e(wa())}" target="_blank" rel="noopener">WhatsApp {e(SITE['phone'])}</a></li>
          <li>{icon('mail')}<a href="mailto:{e(SITE['email'])}">{e(SITE['email'])}</a></li>
        </ul>
      </div>
      <div class="map-card" data-reveal="right">
        <div class="map-card__map" aria-hidden="true">
          <span class="map-card__block" style="left:8%;top:10%;width:22%;height:30%"></span>
          <span class="map-card__block" style="left:44%;top:6%;width:30%;height:22%"></span>
          <span class="map-card__block" style="left:62%;top:66%;width:28%;height:26%"></span>
          <span class="map-card__block" style="left:6%;top:70%;width:24%;height:22%"></span>
          <span class="map-card__road map-card__road--h"></span>
          <span class="map-card__road map-card__road--v"></span>
          <span class="map-card__road map-card__road--d"></span>
          <span class="map-card__pin"><span class="map-card__pin-head">{icon(spec['icon'])}</span></span>
        </div>
        <div class="map-card__foot">
          <div><p class="map-card__name">{e(clinic)}</p><p>{e(spec['area'])}, {e(spec['city'])}</p></div>
          <a class="btn btn-ghost btn-sm" href="https://www.google.com/maps/search/?api=1&amp;query={e(quote(spec['address']))}" target="_blank" rel="noopener">{icon('directions')}Get directions</a>
        </div>
      </div>
    </div>
  </section>"""

    cta_photo = media(spec["image"], "", "cta-band__photo", (900, 1600), "100vw", (16, 7), spec["icon"])
    cta = f"""<section class="cta-band">
    {cta_photo}
    <div class="container cta-band__inner" data-reveal>
      <div>
        <h2 class="display h2">Ready to see {article(who)} {e(who)}?</h2>
        <p>Pick a day and time that suits you. The clinic confirms your appointment on WhatsApp.</p>
      </div>
      <div class="cta-band__actions">
        <button class="btn btn-light btn-lg" type="button" data-book>{icon('calendar-check')}Book appointment</button>
        <a class="btn btn-outline-light btn-lg" href="{tel(SITE['phone'])}">{icon('phone')}Call now</a>
      </div>
    </div>
  </section>"""

    footer = f"""<footer class="site-footer">
  <div class="container site-footer__grid">
    <div class="site-footer__brand">
      {brand(spec)}
      <p>{e(clinic)} in {e(spec['area'])}, {e(spec['city'])}. {e(spec['alias'])}.</p>
    </div>
    <div>
      <h2 class="site-footer__title">Quick links</h2>
      <ul class="site-footer__links">
        <li><a href="#about">About the clinic</a></li>
        <li><a href="#treatments">Treatments</a></li>
        <li><a href="#doctors">Our doctors</a></li>
        <li><a href="#reviews">Patient reviews</a></li>
        <li><a href="#visit">Contact</a></li>
      </ul>
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
</footer>"""

    body = f"""{header(spec)}
<main id="main">
  {hero}
  {stats}
  {about}
  {services}
  {why}
  {doctors}
  {gallery}
  {when}
  {reviews}
  {faq}
  {visit}
  {cta}
</main>
{footer}
<a class="wa-float" href="{e(wa(f'Assalam o Alaikum, I would like to book an appointment at {clinic}.'))}" target="_blank" rel="noopener">{icon('message')}<span class="wa-float__label">Chat on WhatsApp</span><span class="visually-hidden">Chat with the clinic on WhatsApp</span></a>
<div class="action-bar">
  <a class="btn btn-ghost" href="{tel(SITE['phone'])}">{icon('phone')}Call</a>
  <button class="btn btn-accent" type="button" data-book>Book appointment</button>
</div>
{booking_dialog(spec)}"""

    title = f"{clinic}: {who_pl} in {spec['city']}"
    desc = f"{clinic} in {spec['area']}, {spec['city']}. Book {article(who)} {who} for {spec['for'].lower()} and more."
    return (f"{head(title, desc, url, spec['accent'])}\n"
            f'<body class="clinic-site" data-whatsapp="{e(SITE["whatsapp"])}" data-clinic="{e(clinic)}" style="{theme(spec)}">\n'
            f"{body}\n</body>\n</html>\n")


# ---------------------------------------------------------------------------
# Your private list of demo links (sites/index.html)
# ---------------------------------------------------------------------------
def build_catalog() -> str:
    base = SITE["baseUrl"].rstrip("/")
    items = "".join(f"""<li class="demo-item" style="{theme(s)}">
  {media(s['image'], '', 'demo-item__thumb', (200,), '96px', (1, 1), s['icon'])}
  <div class="demo-item__body">
    <p class="demo-item__name">{e(s['plate'])}</p>
    <p class="demo-item__clinic">{e(s['demo']['clinic'])}</p>
    <p class="demo-item__url"><span data-url="{e(s['demo']['path'])}/">{e(base)}/{e(s['demo']['path'])}/</span></p>
    <div class="demo-item__actions">
      <a class="btn btn-ghost btn-sm" href="{e(s['demo']['path'])}/" target="_blank" rel="noopener">{icon('external')}Open</a>
      <button class="btn btn-accent btn-sm" type="button" data-copy="{e(s['demo']['path'])}/">{icon('copy')}<span>Copy link</span></button>
    </div>
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
<main id="main" class="notfound">
  <div class="container notfound__inner">
    <div class="pulse pulse--flat" aria-hidden="true">
      <svg viewBox="0 0 1200 100" preserveAspectRatio="none" focusable="false"><path vector-effect="non-scaling-stroke" d="M0 62H1200"/></svg>
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
