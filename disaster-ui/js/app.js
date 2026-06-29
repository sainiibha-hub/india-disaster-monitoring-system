/* ==========================================================================
   India Disaster Monitor -- standalone frontend
   Calls the Django REST API (disaster-api-django) directly from the
   browser. No backend rendering here -- this is plain HTML/CSS/JS, served
   from a different origin/port than the API itself (see README.md for why
   that's fine, and how CORS is handled on the Django side).
   ========================================================================== */

const STORAGE_KEY = "disaster_ui_api_base";
const DEFAULT_API_BASE = "http://127.0.0.1:8000/api";

function getApiBase() {
  return localStorage.getItem(STORAGE_KEY) || DEFAULT_API_BASE;
}

function setApiBase(url) {
  localStorage.setItem(STORAGE_KEY, url.replace(/\/+$/, ""));
}

const SIGNAL = {
  rain: "#2FD8E0",
  flood: "#FF5470",
  quake: "#9D7BFF",
  cyclone: "#FF9457",
};

const INDIA_CENTER = [22.9734, 78.6569];

// ---------------------------------------------------------------- helpers
async function getJSON(path) {
  const url = `${getApiBase()}${path}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Fetch failed:", url, err);
    return null; // null = "this call failed"; [] would look like "no data"
  }
}

function fmt(value, decimals = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "&ndash;";
  return Number(value).toFixed(decimals);
}

function timeAgo(rawDate) {
  if (!rawDate) return "";
  let s = String(rawDate);
  if (!s.includes("T")) s = s.replace(" ", "T"); // MySQL-raw "YYYY-MM-DD HH:MM:SS"
  if (!/[zZ]|[+-]\d{2}:\d{2}$/.test(s)) s += "Z"; // assume UTC if no offset given
  const diffMs = Date.now() - new Date(s).getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
}

// ---------------------------------------------------------------- API bar
function initApiBar() {
  document.getElementById("apiBaseLabel").textContent = getApiBase();
  document.getElementById("apiEditBtn").addEventListener("click", () => {
    const next = prompt("Django API base URL:", getApiBase());
    if (next && next.trim()) {
      setApiBase(next.trim());
      document.getElementById("apiBaseLabel").textContent = getApiBase();
      loadAll();
    }
  });
}

function setApiHealth(ok) {
  const el = document.getElementById("apiHealth");
  el.textContent = ok ? "● connected" : "● cannot reach API -- check it's running & CORS is allowed";
  el.className = ok ? "ok" : "err";
}

// ---------------------------------------------------------------- clock
function startClock() {
  const el = document.getElementById("clock");
  const tick = () => {
    el.textContent = new Date().toLocaleString("en-IN", {
      hour12: false, dateStyle: "medium", timeStyle: "medium",
    });
  };
  tick();
  setInterval(tick, 1000);
}

// ---------------------------------------------------------------- map
let map, rainLayer, floodLayer, quakeLayer, cycloneLayer;

function initMap() {
  map = L.map("map", { scrollWheelZoom: false }).setView(INDIA_CENTER, 5);

  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: 18,
    }
  ).addTo(map);

  rainLayer = L.layerGroup().addTo(map);
  floodLayer = L.layerGroup().addTo(map);
  quakeLayer = L.layerGroup().addTo(map);
  cycloneLayer = L.layerGroup().addTo(map);
}

function pulseIcon(color) {
  return L.divIcon({
    className: "",
    html: `<div class="pulse-marker" style="background:${color}; color:${color};"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
}

function renderRainfallMarkers(rows) {
  rainLayer.clearLayers();
  rows.forEach((r) => {
    if (!r.rainfall_mm || r.rainfall_mm <= 0) return;
    const radius = 4 + Math.min(r.rainfall_mm, 100) / 6;
    L.circleMarker([r.latitude, r.longitude], {
      radius,
      color: SIGNAL.rain,
      weight: 1,
      fillColor: SIGNAL.rain,
      fillOpacity: 0.45,
    })
      .bindPopup(
        `<strong>${r.district_name}, ${r.state_name}</strong><br>` +
          `Rainfall: ${fmt(r.rainfall_mm)} mm<br>` +
          `Temp: ${fmt(r.temperature_c)}&deg;C &middot; Humidity: ${fmt(r.humidity_percent, 0)}%`
      )
      .addTo(rainLayer);
  });
}

function renderFloodMarkers(rows) {
  floodLayer.clearLayers();
  rows.forEach((r) => {
    if (r.latitude == null || r.longitude == null) return;
    L.marker([r.latitude, r.longitude], { icon: pulseIcon(SIGNAL.flood) })
      .bindPopup(
        `<strong>${r.river_name} at ${r.station_name}</strong> (${r.state_name})<br>` +
          `Severity: <b>${r.severity}</b><br>` +
          `Level: ${fmt(r.water_level, 2)} m (danger ${fmt(r.danger_level, 2)} m)<br>` +
          `${r.alert_message}`
      )
      .addTo(floodLayer);
  });
}

function renderQuakeMarkers(rows) {
  quakeLayer.clearLayers();
  rows.forEach((r) => {
    const radius = 4 + (r.magnitude - 5) * 3;
    L.circleMarker([r.latitude, r.longitude], {
      radius: Math.max(radius, 4),
      color: SIGNAL.quake,
      weight: 1,
      fillColor: SIGNAL.quake,
      fillOpacity: 0.55,
    })
      .bindPopup(
        `<strong>M${fmt(r.magnitude)}</strong> &mdash; ${r.place}<br>` +
          `Depth: ${fmt(r.depth_km)} km<br>${timeAgo(r.event_time)}`
      )
      .addTo(quakeLayer);
  });
}

function renderCycloneMarkers(rows) {
  cycloneLayer.clearLayers();
  rows.forEach((r) => {
    if (r.latitude == null || r.longitude == null) return;
    L.marker([r.latitude, r.longitude], { icon: pulseIcon(SIGNAL.cyclone) })
      .bindPopup(
        `<strong>${r.cyclone_name}</strong> (${r.category})<br>` +
          `Basin: ${r.basin}<br>Wind: ${fmt(r.wind_speed_kmph)} km/h &middot; ` +
          `Alert: <b>${r.alert_level}</b><br>${r.advisory || ""}`
      )
      .addTo(cycloneLayer);
  });
}

// ---------------------------------------------------------------- tickers
function renderTickerList(containerId, rows, renderItem) {
  const el = document.getElementById(containerId);
  if (!rows || rows.length === 0) {
    el.innerHTML = '<p class="empty">No current activity.</p>';
    return;
  }
  el.innerHTML = rows.map(renderItem).join("");
}

function renderFloodTicker(rows) {
  renderTickerList("floodList", rows.slice(0, 10), (r) => `
    <div class="ticker__item">
      <div><strong>${r.river_name}</strong> at ${r.station_name} &mdash; ${r.state_name}</div>
      <div class="meta">
        <span class="value">${fmt(r.water_level, 2)} m</span> /
        danger ${fmt(r.danger_level, 2)} m &middot; ${r.severity} &middot; ${timeAgo(r.created_at)}
      </div>
    </div>
  `);
}

function renderQuakeTicker(rows) {
  renderTickerList("quakeList", rows.slice(0, 10), (r) => `
    <div class="ticker__item">
      <div><span class="value">M${fmt(r.magnitude)}</span> &mdash; ${r.place}</div>
      <div class="meta">Depth ${fmt(r.depth_km)} km &middot; ${timeAgo(r.event_time)}</div>
    </div>
  `);
}

function renderCycloneTicker(rows) {
  renderTickerList("cycloneList", rows.slice(0, 10), (r) => `
    <div class="ticker__item">
      <div><strong>${r.cyclone_name}</strong> &mdash; ${r.category}</div>
      <div class="meta">
        ${r.basin} &middot; <span class="value">${fmt(r.wind_speed_kmph)} km/h</span> &middot;
        ${r.alert_level} &middot; ${timeAgo(r.issued_at)}
      </div>
    </div>
  `);
}

// ---------------------------------------------------------------- chart
let rainfallChart;

function renderChart(rows) {
  const ctx = document.getElementById("rainfallChart");
  const labels = rows.map((r) => r.day);
  const avg = rows.map((r) => r.avg_mm);
  const max = rows.map((r) => r.max_mm);

  if (rainfallChart) rainfallChart.destroy();

  rainfallChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Avg rainfall (mm)",
          data: avg,
          borderColor: SIGNAL.rain,
          backgroundColor: "rgba(47,216,224,0.12)",
          fill: true,
          tension: 0.3,
          pointRadius: 2,
        },
        {
          label: "Peak rainfall (mm)",
          data: max,
          borderColor: SIGNAL.cyclone,
          borderDash: [4, 3],
          fill: false,
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: { ticks: { color: "#8C9BB8", maxTicksLimit: 8 }, grid: { color: "#223150" } },
        y: { ticks: { color: "#8C9BB8" }, grid: { color: "#223150" } },
      },
      plugins: { legend: { labels: { color: "#ECF1F9", font: { size: 11 } } } },
    },
  });
}

// ---------------------------------------------------------------- table
function renderTopStatesTable(rows) {
  const tbody = document.querySelector("#topStatesTable tbody");
  if (!rows || rows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" class="empty">No data for today yet.</td></tr>';
    return;
  }
  tbody.innerHTML = rows
    .map(
      (r) => `<tr><td>${r.state_name}</td><td>${fmt(r.avg_mm)}</td><td>${fmt(r.max_mm)}</td></tr>`
    )
    .join("");
}

// ---------------------------------------------------------------- summary
function renderSummary(s) {
  document.getElementById("statRainfall").textContent = fmt(s.avg_rainfall_today_mm);
  document.getElementById("statFloods").textContent = s.flood_alerts_today ?? 0;
  document.getElementById("statQuakes").textContent = s.earthquakes_last_30_days ?? 0;
  document.getElementById("statCyclones").textContent = s.cyclone_advisories_today ?? 0;
}

// ---------------------------------------------------------------- main load
async function loadAll() {
  const [summary, rainfall, floods, quakes, cyclones, trend, topStates] = await Promise.all([
    getJSON("/summary/"),
    getJSON("/rainfall/latest/"),
    getJSON("/floods/"),
    getJSON("/earthquakes/"),
    getJSON("/cyclones/"),
    getJSON("/rainfall/trend/"),
    getJSON("/rainfall/top-states/"),
  ]);

  setApiHealth(summary !== null);

  if (summary) renderSummary(summary);

  renderRainfallMarkers(Array.isArray(rainfall) ? rainfall : []);
  renderFloodMarkers(Array.isArray(floods) ? floods : []);
  renderQuakeMarkers(Array.isArray(quakes) ? quakes : []);
  renderCycloneMarkers(Array.isArray(cyclones) ? cyclones : []);

  renderFloodTicker(Array.isArray(floods) ? floods : []);
  renderQuakeTicker(Array.isArray(quakes) ? quakes : []);
  renderCycloneTicker(Array.isArray(cyclones) ? cyclones : []);

  renderChart(Array.isArray(trend) ? trend : []);
  renderTopStatesTable(Array.isArray(topStates) ? topStates : []);
}

document.addEventListener("DOMContentLoaded", () => {
  initApiBar();
  startClock();
  initMap();
  loadAll();
  setInterval(loadAll, 60000); // refresh every 60s
});
