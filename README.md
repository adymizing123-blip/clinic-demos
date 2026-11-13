# Clinic website demos

16 separate demo websites for doctors and clinics, one per specialty. When a doctor asks for a demo, send them the link for their own specialty only. No demo links to the others.

| Link | Specialty | Demo clinic |
|---|---|---|
| `/family-doctor/` | General physician | Family Health Clinic |
| `/skin/` | Dermatology | Derma Care Skin Clinic |
| `/dental/` | Dental | Pearl Dental Studio |
| `/gynae/` | Gynecology | Noor Women's Health Clinic |
| `/child/` | Pediatrics | Little Steps Children's Clinic |
| `/bones/` | Orthopedics | Motion Bone and Joint Centre |
| `/ent/` | ENT | ClearSound ENT Clinic |
| `/eye/` | Eye care | Clear View Eye Clinic |
| `/heart/` | Cardiology | Heartline Cardiac Clinic |
| `/physio/` | Physiotherapy | Active Life Physiotherapy |
| `/diet/` | Nutrition | Balanced Plate Nutrition Clinic |
| `/mind/` | Psychiatry | Calm Mind Clinic |
| `/diabetes/` | Diabetes and thyroid | Sugar Care Diabetes and Thyroid Centre |
| `/gastro/` | Gastroenterology | Gut Health Gastro and Liver Clinic |
| `/urology/` | Urology | Renal Care Urology Clinic |
| `/neuro/` | Neurology | NeuroCare Brain and Nerve Clinic |

Each site has its own colour theme and one of three hero layouts, plus: about the lead doctor, treatments, conditions, doctors with fees and timings, when to see a specialist, patient reviews, FAQs, clinic hours and location, a WhatsApp booking form, and a Call / Book bar on mobile.

Plain HTML, CSS and JavaScript. No framework and no `npm install`.

## Project structure

```
clinic-demos/
├── data/
│   ├── site.json          # phone, WhatsApp, email, street address, agency name
│   ├── specialties.json   # specialty text: services, conditions, FAQs, colours, images
│   └── demos.json         # per demo: link, clinic name, headline, reviews, layout (a, b or c)
├── src/assets/            # CSS, JavaScript and icon (copied into every site)
├── scripts/build.py       # generates all 16 sites into sites/
├── sites/                 # the generated websites (this is what Vercel serves)
│   ├── index.html         # your private list of all 16 links, with Copy link buttons
│   ├── skin/index.html    # one folder per demo, each fully self-contained
│   └── ...
└── vercel.json
```

## Deploy: one GitHub repo, one Vercel project, 16 links

1. Push this folder to a GitHub repository, for example `clinic-demos`.
2. On vercel.com click **Create New → Project**, then **Import** the repository.
3. Leave Framework Preset as **Other** and the build command empty. `vercel.json` already serves the `sites` folder.
4. Click **Deploy**.

Your links will look like this:

```
https://clinic-demos.vercel.app/skin/
https://clinic-demos.vercel.app/dental/
https://clinic-demos.vercel.app/heart/
```

Open `https://clinic-demos.vercel.app/` to see all 16 links with **Copy link** buttons. That page is only for you; delete `sites/index.html` if you don't want it reachable.

### Optional: a separate address for one demo

If you want a demo on its own address (for example `derma-care-demo.vercel.app`), import the same repository again in Vercel as a new project, and set **Root Directory** to that demo's folder, for example `sites/skin`. Each demo folder works on its own.

## Customise a demo for a client

1. In `data/demos.json`, change that specialty's clinic name, short name, headline or reviews.
2. In `data/site.json`, set the phone, WhatsApp number (format `923001234567`, no `+` or spaces) and email.
3. Doctors (names, qualifications, fees) are generated in `scripts/build.py`. Replace them with the real doctor's details.
4. Rebuild and push:

```bash
python3 scripts/build.py
git add .
git commit -m "Update demo"
git push
```

Vercel redeploys automatically after every push.

## Images

Photos are placeholders from Unsplash. If one fails to load, the site shows a designed placeholder in that specialty's colour. To use your own photos, put them in `src/assets/img/`, set `"image": "assets/img/your-photo.jpg"` for that specialty in `data/specialties.json`, and rebuild.

## Good to know

- All demo pages tell search engines not to index them, because the doctors, fees and reviews are placeholders. When a demo becomes a real clinic's website, remove the `robots` meta line in `scripts/build.py`, the `X-Robots-Tag` header in `vercel.json` and the `robots.txt` files.
- The footer says "Demo website by Adymizing". Change the agency name in `data/site.json`.
- The booking form sends the request to the clinic on WhatsApp. To save bookings in a database instead, connect the form to a service such as Formspree, Google Sheets or Supabase.
