# India Disaster Monitor -- Standalone Frontend

Plain HTML/CSS/JS dashboard. No build step, no framework, no backend
rendering -- it just calls the **Django REST API** (`disaster-api-django/`)
directly from the browser with `fetch()` and draws the map/charts/panels
with Leaflet + Chart.js (both loaded from a CDN).

## Why you can't just double-click `index.html`

Opening the file directly (`file://...`) works for the page itself, but
some browsers restrict `fetch()` calls made from a `file://` page, and the
Django side's CORS allow-list (see below) is configured for an `http://`
origin, not `file://`. So: serve this folder with a tiny local web server
instead -- it takes one command.

## 1. Start the Django API first

In the `disaster-api-django` project (separate folder, can be anywhere):
```bash
python manage.py runserver
```
Leave that running. It serves on `http://127.0.0.1:8000` by default.

## 2. Serve this frontend folder

Python already has everything you need for this -- no install required:
```bash
cd disaster-ui
python -m http.server 8080
```
Open **http://localhost:8080** in your browser.

(Any static server works -- VS Code's "Live Server" extension, `npx serve`,
etc. Just note what port it uses, see step 3.)

## 3. Make sure Django allows this origin (CORS)

The Django project's `.env.example` already whitelists the common local
dev ports, including `http://localhost:8080` (what `python -m http.server
8080` uses). If you serve this frontend on a **different** port, add it to
`CORS_ALLOWED_ORIGINS` in the Django project's `.env`, comma-separated,
then restart `python manage.py runserver`:
```
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080,http://localhost:5500
```

If `disaster-api-django` doesn't have `django-cors-headers` installed yet
(it was added after the initial setup), run inside that project:
```bash
pip install django-cors-headers
```

## 4. Point the frontend at your API (if it's not on localhost:8000)

The header has a small **API bar** showing the current API base URL with a
"change" button -- click it to type in a different URL (e.g. if your Django
server is on another machine/port). It's saved in the browser's
`localStorage`, so it sticks across reloads. Default is
`http://127.0.0.1:8000/api`.

## What you should see

- Top stat cards: today's avg rainfall, flood alerts, earthquakes (30d),
  cyclone advisories
- A dark India map with rainfall circle markers, pulsing flood-alert and
  earthquake/cyclone markers
- Live ticker panels for floods / earthquakes / cyclones
- A 30-day rainfall trend chart and a top-rainfall-states table

If the "API:" bar at the top shows a red **"cannot reach API"** message:
1. Confirm `python manage.py runserver` is actually running
2. Open `http://127.0.0.1:8000/api/summary/` directly in a browser tab --
   if that 404s/errors, the problem is on the Django side, not here
3. Check the browser console (F12) for a CORS error specifically -- if you
   see one, revisit step 3 above

## Project structure

```
disaster-ui/
├── index.html
├── css/style.css
├── js/app.js       # all fetch calls + map/chart/ticker rendering
└── README.md
```
