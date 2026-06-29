# LinkedIn post drafts - India Disaster Monitoring System

Pick one, tweak the bracketed parts, and post.

---

## Option 1 - Short and punchy

Built a disaster monitoring system for India - tracking rainfall,
floods, earthquakes, and cyclones in one place.

What it does:
- Live rainfall data across all states/UTs (OpenWeatherMap)
- Automatic flood alerts when river levels cross danger thresholds
- Real-time earthquake feed from USGS (M>=5.0)
- Cyclone advisory tracking

Stack: Python, Flask, Django REST Framework, MySQL, vanilla JS + Leaflet

3 connected pieces - a data-collection engine, a REST API, and a live
map dashboard - all reading from one MySQL database.

GitHub: [your repo link]

#Python #Django #Flask #MySQL #OpenSource #WebDevelopment #DisasterManagement

---

## Option 2 - Build story

Spent the last few days building something I wanted to try for a
while: a full disaster monitoring platform for India.

The idea: pull together the four hazards that actually affect most of
the country (rainfall, floods, earthquakes, cyclones) into one system,
instead of checking five different sites.

How it is built:
- A Python backend collects data on a schedule: live rainfall from
  OpenWeatherMap, real earthquake data from USGS, and flood-risk
  modeling against real river danger levels
- MySQL stores everything across 9 relational tables
- A Django REST API exposes it all as clean JSON
- A standalone JS dashboard (Leaflet + Chart.js) renders it on a live
  map with flood/earthquake/cyclone alerts

Biggest lesson: India's flood (CWC) and cyclone (IMD) data don't have
simple public APIs, so I built the flood/cyclone modules with a
drop-in hook for a real feed, and a realistic simulator in the
meantime, rather than fake a working endpoint that does not exist.

Code is on GitHub if you want to dig in: [your repo link]

#Python #Django #Flask #MySQL #SoftwareEngineering #SideProject #BuildInPublic

---

## Option 3 - Minimal, link-in-comments style

Built a 3-part disaster monitoring system for India: rainfall, flood,
earthquake, and cyclone tracking, all on one live map.

Python + Flask backend, MySQL, Django REST API, JS dashboard.

Link to the repo is in the comments.

#Python #Django #MySQL #WebDev

---

## Posting tips

1. Attach a screenshot or short screen recording of the dashboard.
2. Put the GitHub link in the first comment, not the post body, for max reach.
3. Tag technologies, not just hashtags.
4. Pin it to your profile if job hunting.
5. Reply to comments quickly in the first hour.