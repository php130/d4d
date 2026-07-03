const state = {
  dataset: null,
  mode: "semantic_summary",
  selectedEventId: null,
  glossaryTerm: "AIS",
};

const $ = (id) => document.getElementById(id);
const glossary = window.D4D_GLOSSARY || {};
const PINNED_TERMS = ["AIS", "SAR", "COP", "C2", "MDA", "OSINT", "DDIL", "Semantic Event", "Priority Routing", "Evidence Bundle"];
const EVENT_TERM_MAP = {
  NETWORK_DEGRADED: ["Network", "Battle Network", "DDIL", "Store Forward"],
  WEATHER_HAZARD: ["Weather", "KMA", "Confidence"],
  AIS_GAP: ["AIS", "AIS Gap", "Freshness"],
  SAR_WITHOUT_AIS: ["SAR", "SAR without AIS", "Sensor Fusion"],
  LOW_TRUST_REPORT: ["Human Report", "Trust", "Evidence Bundle"],
  OSINT_INCIDENT: ["OSINT", "GDELT", "Evidence Bundle"],
  PRIORITY_BRIEF: ["Priority Brief", "Alert Card", "COP"],
};
const SENSOR_TERM_MAP = {
  AIS: "AIS",
  SAR: "SAR",
  WEATHER: "Weather",
  OSINT: "OSINT",
  NETWORK: "Network",
  HUMAN_REPORT: "Human Report",
};

function fmtBytes(bytes) {
  if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(2)} MB`;
  if (bytes >= 1_000) return `${(bytes / 1_000).toFixed(1)} KB`;
  return `${bytes} B`;
}

function pct(value) {
  return `${Math.round(value * 100)}%`;
}

function decisionLabel(decision) {
  return {
    send: "SEND",
    defer: "DEFER",
    drop: "DROP",
    hold_local: "LOCAL",
  }[decision] || decision.toUpperCase();
}

function severityColor(event) {
  if (event.severity === "critical") return "#bd2d2a";
  if (event.severity === "high") return "#b86b00";
  if (event.severity === "medium") return "#2f67b1";
  return "#277846";
}

function getRouting() {
  return state.dataset.routing_results[state.mode];
}

function getPacket(eventId = state.selectedEventId) {
  return getRouting().packets.find((packet) => packet.event_id === eventId);
}

function getEvent(eventId = state.selectedEventId) {
  return state.dataset.semantic_events.find((event) => event.event_id === eventId);
}

function getBundle(eventId = state.selectedEventId) {
  return state.dataset.evidence_bundles.find((bundle) => bundle.event_id === eventId);
}

function getObservation(id) {
  return state.dataset.observations.find((obs) => obs.observation_id === id);
}

function uniqueTerms(terms) {
  return [...new Set(terms)].filter((term) => glossary[term]);
}

function eventTerms(event) {
  const bundle = state.dataset ? getBundle(event.event_id) : null;
  const sensorTerms = bundle
    ? bundle.evidence_refs
        .map((ref) => getObservation(ref))
        .filter(Boolean)
        .map((obs) => SENSOR_TERM_MAP[obs.sensor_type])
    : [];
  return uniqueTerms([...(EVENT_TERM_MAP[event.event_type] || []), ...sensorTerms]);
}

function renderTermButton(term) {
  const item = glossary[term];
  const title = item ? `${item.full}: ${item.plain}` : term;
  return `<button class="term-chip" type="button" data-term="${term}" title="${title}">${term}</button>`;
}

function selectGlossaryTerm(term) {
  if (!glossary[term]) return;
  state.glossaryTerm = term;
  renderGlossary();
  wireTermButtons();
}

function renderGlossary() {
  const selected = getEvent();
  const terms = uniqueTerms([...PINNED_TERMS, ...eventTerms(selected)]);
  if (!terms.includes(state.glossaryTerm)) state.glossaryTerm = terms[0] || "AIS";
  const item = glossary[state.glossaryTerm];
  $("glossaryChips").innerHTML = terms.map(renderTermButton).join("");
  $("glossaryDefinition").innerHTML = item ? `
    <strong>${item.label}</strong>
    <span>${item.full}</span>
    <p>${item.plain}</p>
    <p class="muted-text">${item.example}</p>
  ` : "";
  document.querySelectorAll("[data-term]").forEach((button) => {
    button.classList.toggle("active", button.dataset.term === state.glossaryTerm);
  });
}

function wireTermButtons() {
  document.querySelectorAll(".term-chip[data-term]").forEach((button) => {
    if (button.dataset.bound === "true") return;
    button.dataset.bound = "true";
    button.addEventListener("click", () => selectGlossaryTerm(button.dataset.term));
  });
}

function projection() {
  const bounds = state.dataset.scenario.aoi.bounds;
  const pad = { x: 70, y: 62 };
  const width = 1000 - pad.x * 2;
  const height = 640 - pad.y * 2;
  return ({ lat, lon }) => {
    const x = pad.x + ((lon - bounds.lon_min) / (bounds.lon_max - bounds.lon_min)) * width;
    const y = pad.y + (1 - (lat - bounds.lat_min) / (bounds.lat_max - bounds.lat_min)) * height;
    return { x, y };
  };
}

function renderTopbar() {
  const routing = getRouting();
  const metrics = routing.metrics;
  $("topbarMetrics").innerHTML = `
    <div class="metric-tile"><span class="metric-label">Messages Sent</span><span class="metric-value">${metrics.events_sent}/${metrics.events_total}</span></div>
    <div class="metric-tile"><span class="metric-label">Bytes Saved</span><span class="metric-value">${metrics.bytes_saved_pct_vs_full_feed}%</span></div>
    <div class="metric-tile"><span class="metric-label">Semantic Bytes</span><span class="metric-value">${fmtBytes(metrics.semantic_bytes_sent)}</span></div>
  `;
}

function renderModes() {
  const modes = Object.entries(state.dataset.network_modes);
  $("modeButtons").innerHTML = modes.map(([key, mode]) => `
    <button class="mode-button ${state.mode === key ? "active" : ""}" data-mode="${key}" type="button">
      <strong>${mode.label}</strong>
      <span>${mode.bandwidth_kbps} kbps · loss ${mode.packet_loss_pct}%</span>
    </button>
  `).join("");
  document.querySelectorAll(".mode-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      renderAll();
    });
  });
  const mode = state.dataset.network_modes[state.mode];
  const latency = mode.latency_ms == null ? "n/a" : `${mode.latency_ms} ms`;
  $("modeSummary").innerHTML = `<strong>${mode.label}</strong><br>${mode.description}<br>${mode.bandwidth_kbps} kbps · ${latency} · packet loss ${mode.packet_loss_pct}%`;
}

function renderMap() {
  const project = projection();
  const events = state.dataset.semantic_events;
  const tracksByVessel = state.dataset.tracks.reduce((acc, point) => {
    acc[point.vessel_id] ||= [];
    acc[point.vessel_id].push(point);
    return acc;
  }, {});
  const grid = [];
  for (let i = 0; i <= 10; i += 1) {
    const x = 70 + i * 86;
    const y = 62 + i * 51.6;
    grid.push(`<line class="water-grid" x1="${x}" y1="62" x2="${x}" y2="578"></line>`);
    grid.push(`<line class="water-grid" x1="70" y1="${y}" x2="930" y2="${y}"></line>`);
  }
  const trackLines = Object.entries(tracksByVessel).map(([vesselId, points]) => {
    const path = points.map((point, idx) => {
      const p = project(point);
      return `${idx === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`;
    }).join(" ");
    const klass = vesselId === "vessel_haneul_77" ? "track-line" : "track-muted";
    return `<path class="${klass}" d="${path}"></path>`;
  }).join("");
  const trackPoints = state.dataset.tracks.map((point) => {
    const p = project(point);
    const vessel = state.dataset.vessels.find((v) => v.vessel_id === point.vessel_id);
    return `<g><circle class="map-node" cx="${p.x}" cy="${p.y}" r="9"></circle><text class="map-small" x="${p.x + 12}" y="${p.y - 9}">${vessel.display_name}</text></g>`;
  }).join("");
  const markers = events.map((event) => {
    const p = project(event.location);
    const selected = event.event_id === state.selectedEventId ? "selected" : "";
    const r = event.severity === "critical" ? 16 : event.severity === "high" ? 13 : 10;
    return `
      <g class="event-map-hit" data-event-id="${event.event_id}">
        <circle class="event-marker ${selected}" cx="${p.x}" cy="${p.y}" r="${r}" fill="${severityColor(event)}"></circle>
        <text class="map-small" x="${p.x + 18}" y="${p.y + 5}">${event.event_type}</text>
      </g>
    `;
  }).join("");
  const selected = getEvent();
  $("copMap").innerHTML = `
    <rect x="0" y="0" width="1000" height="640" fill="#d9e7e4"></rect>
    ${grid.join("")}
    <path d="M84 510 C180 472 230 390 286 360 C365 318 410 250 490 220 C605 176 705 118 910 96 L940 602 L84 602 Z" fill="#edf5f2" stroke="#a3b4b0" stroke-width="3"></path>
    <text class="map-label" x="86" y="44">Yellow Sea Training AOI</text>
    <text class="map-small" x="86" y="612">Synthetic COP view · selected: ${selected.event_type}</text>
    ${trackLines}
    ${trackPoints}
    ${markers}
  `;
  document.querySelectorAll(".event-map-hit").forEach((node) => {
    node.addEventListener("click", () => {
      state.selectedEventId = node.dataset.eventId;
      renderAll();
    });
  });
  const packet = getPacket();
  $("selectedDecision").className = `status-pill ${packet.decision}`;
  $("selectedDecision").textContent = decisionLabel(packet.decision);
}

function renderEventList() {
  const sorted = [...state.dataset.semantic_events].sort((a, b) => b.priority - a.priority);
  $("eventList").innerHTML = sorted.map((event) => {
    const packet = getPacket(event.event_id);
    const terms = eventTerms(event).slice(0, 3).map((term) => `<span class="event-term">${term}</span>`).join("");
    return `
      <button class="event-button ${event.event_id === state.selectedEventId ? "active" : ""}" data-event-id="${event.event_id}" type="button">
        <span class="event-button-top">
          <span class="event-type">${event.event_type} · ${(event.priority * 100).toFixed(0)}</span>
          <span class="status-pill ${packet.decision}">${decisionLabel(packet.decision)}</span>
        </span>
        <span class="event-summary">${event.summary}</span>
        <span class="event-terms">${terms}</span>
      </button>
    `;
  }).join("");
  document.querySelectorAll(".event-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedEventId = button.dataset.eventId;
      renderAll();
    });
  });
}

function renderEvidence() {
  const event = getEvent();
  const bundle = getBundle();
  $("evidenceTitle").textContent = event.event_type;
  $("reviewStatus").textContent = bundle.review_status.replaceAll("_", " ");
  const obsItems = bundle.evidence_refs.map((ref) => {
    const obs = getObservation(ref);
    const term = SENSOR_TERM_MAP[obs.sensor_type];
    const sensor = term ? renderTermButton(term) : `<strong>${obs.sensor_type}</strong>`;
    return `
      <div class="evidence-item">
        <code>${obs.observation_id}</code><br>
        <strong>${obs.source_id}</strong> · ${sensor}<br>
        ${obs.claim}<br>
        <span class="muted-text">raw ref: ${obs.raw_ref}</span>
      </div>
    `;
  }).join("");
  $("evidenceBody").innerHTML = `
    <div class="fact-grid">
      <div class="fact"><b>Priority</b><span>${(event.priority * 100).toFixed(0)}</span></div>
      <div class="fact"><b>Severity</b><span>${event.severity}</span></div>
      <div class="fact"><b>Confidence</b><span>${pct(bundle.confidence)}</span></div>
      <div class="fact"><b>Trust</b><span>${pct(bundle.trust_score)}</span></div>
    </div>
    <h3>${event.summary}</h3>
    <p>${event.why_it_matters}</p>
    <p><strong>Action:</strong> ${event.recommended_action}</p>
    <div class="bar-row">
      <div class="bar-label"><span>Confidence</span><span>${pct(bundle.confidence)}</span></div>
      <div class="bar"><span style="width:${bundle.confidence * 100}%"></span></div>
    </div>
    <div class="bar-row">
      <div class="bar-label"><span>Trust</span><span>${pct(bundle.trust_score)}</span></div>
      <div class="bar"><span style="width:${bundle.trust_score * 100}%"></span></div>
    </div>
    <h3>Evidence refs</h3>
    <div class="evidence-list">${obsItems}</div>
  `;
}

function renderRouting() {
  const routing = getRouting();
  const metrics = routing.metrics;
  const raw = metrics.raw_bytes_total_if_full_feed;
  const sem = metrics.semantic_bytes_sent;
  const semWidth = raw ? Math.max(1, Math.min(100, (sem / raw) * 100)) : 0;
  $("routingMetrics").innerHTML = `
    <div class="fact-grid">
      <div class="fact"><b>Full-feed size</b><span>${fmtBytes(raw)}</span></div>
      <div class="fact"><b>Semantic sent</b><span>${fmtBytes(sem)}</span></div>
      <div class="fact"><b>Saved</b><span>${metrics.bytes_saved_pct_vs_full_feed}%</span></div>
      <div class="fact"><b>Survival</b><span>${pct(metrics.message_survival_rate)}</span></div>
    </div>
    <div class="bar-row">
      <div class="bar-label"><span>Semantic payload vs raw feed</span><span>${fmtBytes(sem)} / ${fmtBytes(raw)}</span></div>
      <div class="bar"><span style="width:${semWidth}%"></span></div>
    </div>
  `;
  const eventById = Object.fromEntries(state.dataset.semantic_events.map((event) => [event.event_id, event]));
  $("packetTable").innerHTML = routing.packets.map((packet) => {
    const event = eventById[packet.event_id];
    return `
      <div class="packet-row">
        <span>${event.event_type}</span>
        <span class="status-pill ${packet.decision}">${decisionLabel(packet.decision)}</span>
      </div>
    `;
  }).join("");
}

function renderBriefing() {
  const briefing = state.dataset.briefing;
  const claims = briefing.grounded_claims.map((item) => `
    <div class="claim-item">
      ${item.claim}<br>
      ${item.evidence_refs.map((ref) => `<code>${ref}</code>`).join(" ")}
    </div>
  `).join("");
  $("briefingBody").innerHTML = `
    <div class="briefing-body-grid">
      <div class="briefing-summary">
        <h3>${briefing.headline}</h3>
        <p>${briefing.operator_summary}</p>
      </div>
      <div class="claims-list">${claims}</div>
    </div>
  `;
}

function renderAll() {
  renderTopbar();
  renderModes();
  renderMap();
  renderEventList();
  renderEvidence();
  renderRouting();
  renderBriefing();
  renderGlossary();
  wireTermButtons();
}

async function boot() {
  if (window.__D4D_MOCK_DATASET) {
    state.dataset = window.__D4D_MOCK_DATASET;
  } else {
    const response = await fetch("./data/mock_dataset.json");
    state.dataset = await response.json();
  }
  const topEvent = [...state.dataset.semantic_events].sort((a, b) => b.priority - a.priority)[0];
  state.selectedEventId = topEvent.event_id;
  renderAll();
}

boot().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><section class="panel"><div class="panel-heading"><h2>Dataset load failed</h2></div><pre>${String(error)}</pre></section></main>`;
});
