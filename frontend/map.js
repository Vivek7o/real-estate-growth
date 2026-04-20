// ── Config ───────────────────────────────────────────────────────────
const API = "http://localhost:5000/api";

let map, heatLayer, markersLayer;

// ── Initialize Map ───────────────────────────────────────────────────
function initMap() {
  // Center on Delhi NCR
  map = L.map("map").setView([28.6139, 77.2090], 10);

  // OpenStreetMap tiles (free, no API key needed)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "Map data: OpenStreetMap contributors",
    maxZoom: 18,
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

// ── Load Data and Render Everything ─────────────────────────────────
async function loadAll() {
  try {
    const [scoresRes, summaryRes] = await Promise.all([
      fetch(`${API}/growth-scores`),
      fetch(`${API}/summary`),
    ]);

    const scores  = await scoresRes.json();
    const summary = await summaryRes.json();

    renderSummaryBar(summary);
    renderHeatMap(scores);
    renderMarkers(scores);
    renderSidebar(scores);

  } catch (err) {
    console.error("Failed to load data:", err);
    document.getElementById("zone-list").innerHTML =
      '<div class="loading">Could not connect to server.<br>Make sure Flask is running on port 5000.</div>';
  }
}

// ── Summary Bar ──────────────────────────────────────────────────────
function renderSummaryBar(summary) {
  document.getElementById("stat-zones").textContent =
    `${summary.total_zones} Zones`;
  document.getElementById("stat-avg").textContent =
    `Avg Score: ${summary.average_score}`;
  document.getElementById("stat-top").textContent =
    `Top: ${summary.top_zone?.zone || "—"}`;
}

// ── Heat Map Layer ───────────────────────────────────────────────────
function renderHeatMap(scores) {
  if (heatLayer) map.removeLayer(heatLayer);

  const heatData = scores
    .filter(s => s.latitude && s.longitude)
    .map(s => [
      s.latitude,
      s.longitude,
      s.final_growth_score / 100   // normalize to 0-1 for heatmap intensity
    ]);

  heatLayer = L.heatLayer(heatData, {
    radius:  40,
    blur:    25,
    maxZoom: 17,
    gradient: {
      0.0: "#0000ff",   // blue   = very low
      0.3: "#00ffff",   // cyan   = low
      0.5: "#ffff00",   // yellow = medium
      0.7: "#ff8800",   // orange = high
      1.0: "#ff0000",   // red    = very high
    }
  }).addTo(map);
}

// ── Interactive Markers ──────────────────────────────────────────────
function renderMarkers(scores) {
  markersLayer.clearLayers();

  scores.forEach(zone => {
    if (!zone.latitude || !zone.longitude) return;

    const color = getScoreColor(zone.final_growth_score);

    const marker = L.circleMarker([zone.latitude, zone.longitude], {
      radius:      12,
      fillColor:   color,
      color:       "#ffffff",
      weight:      2,
      opacity:     1,
      fillOpacity: 0.85,
    });

    // Click popup with full breakdown
    marker.bindPopup(buildPopup(zone), { maxWidth: 240 });

    // Hover tooltip
    marker.bindTooltip(
      `<b>${zone.zone}</b><br>Score: ${zone.final_growth_score}`,
      { direction: "top", offset: [0, -10] }
    );

    markersLayer.addLayer(marker);
  });
}

function buildPopup(zone) {
  const scoreClass = getScoreClass(zone.final_growth_score);
  return `
    <div style="min-width:210px">
      <div class="popup-title">${zone.zone}</div>
      <div class="popup-city">${zone.city}</div>
      <div class="popup-score ${scoreClass}">${zone.final_growth_score}</div>
      <hr class="popup-divider">
      <div class="popup-row">
        <span>Municipal Score</span>
        <span>${zone.municipal_score}</span>
      </div>
      <div class="popup-row">
        <span>Market Score</span>
        <span>${zone.market_score}</span>
      </div>
      <div class="popup-row">
        <span>Trend Score</span>
        <span>${zone.trend_score}</span>
      </div>
    </div>
  `;
}

// ── Sidebar Zone List ────────────────────────────────────────────────
function renderSidebar(scores) {
  const list = document.getElementById("zone-list");
  list.innerHTML = "";

  if (!scores.length) {
    list.innerHTML = '<div class="loading">No zones found.</div>';
    return;
  }

  scores.slice(0, 8).forEach(zone => {
    const div = document.createElement("div");
    div.className = "zone-card";
    div.onclick = () => flyToZone(zone.latitude, zone.longitude, zone);

    div.innerHTML = `
      <div class="zone-name">${zone.zone}</div>
      <div class="zone-city">${zone.city}</div>
      <div class="zone-score ${getScoreClass(zone.final_growth_score)}">
        ${zone.final_growth_score}
      </div>
      <div class="score-bar-group">
        ${buildBar("Municipal", zone.municipal_score, "#58a6ff")}
        ${buildBar("Market",    zone.market_score,    "#3fb950")}
        ${buildBar("Trend",     zone.trend_score,     "#d29922")}
      </div>
    `;

    list.appendChild(div);
  });
}

function buildBar(label, value, color) {
  return `
    <div class="score-bar-wrap">
      <div class="score-bar-label">
        <span>${label}</span>
        <span>${value}</span>
      </div>
      <div class="score-bar-bg">
        <div class="score-bar-fill"
             style="width:${value}%; background:${color}">
        </div>
      </div>
    </div>
  `;
}

// ── Fly to Zone on Sidebar Click ─────────────────────────────────────
function flyToZone(lat, lon, zone) {
  map.flyTo([lat, lon], 13, { duration: 1.5 });
}

// ── Refresh Button ───────────────────────────────────────────────────
async function refreshData() {
  const btn = document.querySelector(".refresh-btn");
  btn.textContent = "Refreshing...";
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/refresh`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ city: "Delhi" }),
    });
    const data = await res.json();
    alert(data.message);
    await loadAll();
  } catch (e) {
    alert("Refresh failed. Make sure the Flask server is running.");
  }

  btn.textContent = "Refresh Data";
  btn.disabled = false;
}

// ── Helpers ──────────────────────────────────────────────────────────
function getScoreColor(score) {
  if (score >= 70) return "#3fb950";
  if (score >= 40) return "#d29922";
  return "#f85149";
}

function getScoreClass(score) {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
}

// ── Start ────────────────────────────────────────────────────────────
initMap();
loadAll();
