const data = window.KOREA_CIVIL_INFRA_DATASET || {};
const layers = data.layers || {};
const buildingFootprints = window.KOREA_BUILDING_FOOTPRINTS || {features: []};

const state = {
  mode: "semantic_summary",
  selected: {
    type: "event",
    id: (data.semantic_events || [])[0]?.id || "",
  },
  visible: {
    medical: true,
    building: true,
    communications: true,
    aggregates: true,
    events: true,
  },
};

const mapState = {
  map: null,
  groups: {},
  legend: null,
};

const layerConfig = [
  {
    key: "medical",
    label: "Medical assets",
    copy: "Public hospitals as protected civilian support nodes",
    count: (layers.medical_facilities || []).length,
  },
  {
    key: "building",
    label: "Buildings / apartments",
    copy: "Actual public building footprints, fallback to aggregate cells",
    count: (buildingFootprints.features || []).length || (layers.building_exposure_cells || []).length,
  },
  {
    key: "communications",
    label: "Communications context",
    copy: "Coarse coverage stress without base-station or backbone detail",
    count: (layers.communications_context_cells || []).length,
  },
  {
    key: "aggregates",
    label: "Power / public IT",
    copy: "Regional continuity context and protected-facility safe mode",
    count: (layers.power_it_aggregates || []).length,
  },
  {
    key: "events",
    label: "Semantic events",
    copy: "Compressed COP updates ranked by staff priority",
    count: (data.semantic_events || []).length,
  },
];

const elementById = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function titleCase(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDate(value) {
  if (!value) return "unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getBounds() {
  return data.scenario?.aoi?.bounds || {
    lat_min: 37.43,
    lat_max: 37.69,
    lon_min: 126.78,
    lon_max: 127.16,
  };
}

function severityClass(severity) {
  if (severity === "high") return "severity-high";
  if (severity === "medium") return "severity-medium";
  return "severity-low";
}

function markerSeverityClass(severity) {
  if (severity === "medium") return "medium";
  if (severity === "low") return "low";
  return "high";
}

function selectItem(type, id) {
  state.selected = {type, id};
  renderMap();
  renderSelectedDetails();
  renderEventList();
}

function renderTopbar() {
  const counts = [
    ["medical", (layers.medical_facilities || []).length],
    ["buildings", (buildingFootprints.features || []).length || (layers.building_exposure_cells || []).length],
    ["events", (data.semantic_events || []).length],
  ];
  elementById("topbarStatus").innerHTML = `
    <span class="status-pill">${escapeHtml(data.schema || "demo schema")}</span>
    <span class="status-pill muted">${escapeHtml(formatDate(data.generated_at))}</span>
    ${counts
      .map(([label, count]) => `<span class="metric-pill">${count} ${escapeHtml(label)}</span>`)
      .join("")}
  `;
}

function renderLayerToggles() {
  elementById("layerToggles").innerHTML = layerConfig
    .map(
      (layer) => `
        <label class="layer-toggle">
          <input type="checkbox" data-layer="${escapeHtml(layer.key)}" ${
            state.visible[layer.key] ? "checked" : ""
          } />
          <span>
            <span class="layer-name">${escapeHtml(layer.label)}</span>
            <span class="layer-copy">${escapeHtml(layer.copy)}</span>
          </span>
          <span class="layer-count">${escapeHtml(layer.count)}</span>
        </label>
      `,
    )
    .join("");

  elementById("layerToggles").querySelectorAll("input[data-layer]").forEach((input) => {
    input.addEventListener("change", (event) => {
      state.visible[event.currentTarget.dataset.layer] = event.currentTarget.checked;
      renderMap();
    });
  });
}

function renderModeTabs() {
  const modes = data.network_modes || {};
  elementById("modeTabs").innerHTML = Object.entries(modes)
    .map(
      ([key, mode]) => `
        <button class="mode-button ${state.mode === key ? "is-active" : ""}" data-mode="${escapeHtml(key)}">
          ${escapeHtml(mode.label || titleCase(key))}
        </button>
      `,
    )
    .join("");

  elementById("modeTabs").querySelectorAll("button[data-mode]").forEach((button) => {
    button.addEventListener("click", (event) => {
      state.mode = event.currentTarget.dataset.mode;
      renderModeTabs();
      renderMapMeta();
      renderMap();
    });
  });
}

function renderMapMeta() {
  const mode = data.network_modes?.[state.mode] || {};
  const safety = data.scenario?.safety_boundary || "";
  elementById("mapMetaStrip").innerHTML = `
    <span class="status-pill">${escapeHtml(mode.bandwidth_kbps || "?")} kbps</span>
    <span class="status-pill muted">${escapeHtml(mode.description || "")}</span>
    <span class="status-pill warning">${escapeHtml(safety)}</span>
  `;
}

function renderSafeBoundary() {
  elementById("safeBoundary").innerHTML = `
    <p class="panel-kicker">Safety Rules</p>
    <ul>
      ${(data.safety_rules || [])
        .map((rule) => `<li><span class="safe-dot"></span><span>${escapeHtml(rule)}</span></li>`)
        .join("")}
    </ul>
  `;
}

function markerIcon(kind, options = {}) {
  const selected = options.selected ? "is-selected" : "";
  const severity = options.severity ? markerSeverityClass(options.severity) : "";
  return L.divIcon({
    className: "",
    html: `<span class="map-marker ${escapeHtml(kind)} ${escapeHtml(severity)} ${selected}"></span>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -14],
  });
}

function buildingStyle(feature) {
  const selected = state.selected.type === "building_footprint" && state.selected.id === feature.properties.id;
  const buildingClass = feature.properties.building_class;
  const palette = {
    residential: {color: "#a86711", fillColor: "#f0c96d"},
    commercial: {color: "#1d64a8", fillColor: "#9cc5ec"},
    industrial: {color: "#6f559d", fillColor: "#c5b3e3"},
    public_or_civic: {color: "#256f58", fillColor: "#91cbb8"},
    other_building: {color: "#6f766f", fillColor: "#cfd8d2"},
  };
  const colors = palette[buildingClass] || palette.other_building;
  return {
    color: selected ? "#111d18" : colors.color,
    weight: selected ? 3 : 1.2,
    opacity: selected ? 0.95 : 0.82,
    fillColor: colors.fillColor,
    fillOpacity: selected ? 0.55 : 0.38,
  };
}

function popupHtml(title, copy, mode) {
  return `
    <p class="map-popup-title">${escapeHtml(title)}</p>
    <p class="map-popup-copy">${escapeHtml(copy || mode || "")}</p>
  `;
}

function fitAoi() {
  if (!mapState.map) return;
  const footprints = buildingFootprints.features || [];
  if (footprints.length && window.L) {
    mapState.map.setView([37.565, 126.995], 14);
    return;
  }
  const bounds = getBounds();
  const leafletBounds = [
    [bounds.lat_min, bounds.lon_min],
    [bounds.lat_max, bounds.lon_max],
  ];
  mapState.map.fitBounds(leafletBounds, {padding: [18, 18]});
}

function initMap() {
  const mapElement = elementById("infraMap");
  if (!mapElement) return false;
  if (!window.L) {
    mapElement.innerHTML = `<div class="detail-block"><p class="detail-label">Map unavailable</p><p>Leaflet 지도 라이브러리를 불러오지 못했습니다. 네트워크 연결을 확인해주세요.</p></div>`;
    return false;
  }
  if (mapState.map) return true;

  mapState.map = L.map(mapElement, {
    zoomControl: true,
    scrollWheelZoom: true,
    preferCanvas: false,
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(mapState.map);

  mapState.legend = L.control({position: "bottomleft"});
  mapState.legend.onAdd = () => {
    const div = L.DomUtil.create("div", "map-legend");
    div.innerHTML = `
      <div class="map-legend-row"><span class="map-legend-dot"></span><span>hospital</span></div>
      <div class="map-legend-row"><span class="map-legend-dot event"></span><span>semantic event</span></div>
      <div class="map-legend-row"><span class="map-legend-dot exposure"></span><span>building footprint</span></div>
      <div class="map-legend-row"><span class="map-legend-dot aggregate"></span><span>aggregate only</span></div>
    `;
    return div;
  };
  mapState.legend.addTo(mapState.map);
  fitAoi();
  return true;
}

function clearMapLayers() {
  if (!mapState.map) return;
  Object.values(mapState.groups).forEach((group) => group.remove());
  mapState.groups = {};
}

function addGroup(key) {
  const group = L.layerGroup();
  mapState.groups[key] = group;
  group.addTo(mapState.map);
  return group;
}

function bindInteractive(layer, type, record, title, copy) {
  layer.on("click", () => selectItem(type, record.id));
  layer.bindPopup(popupHtml(title, copy, record.source_mode || record.transmit_tier));
  return layer;
}

function renderBuildingLayer() {
  const group = addGroup("building");
  const footprints = buildingFootprints.features || [];
  if (footprints.length) {
    const geoJsonLayer = L.geoJSON(footprints, {
      style: buildingStyle,
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const title = props.name || props.id || "Public building footprint";
        const copy = [
          `class: ${props.building_class || "unknown"}`,
          `building: ${props.building || "yes"}`,
          props.levels ? `levels: ${props.levels}` : null,
          props.area_m2_est ? `area: ${props.area_m2_est} m2` : null,
        ].filter(Boolean).join("; ");
        layer.on("click", () => selectItem("building_footprint", props.id));
        layer.bindPopup(popupHtml(title, copy, props.source_mode));
      },
    });
    geoJsonLayer.addTo(group);
    return;
  }

  (layers.building_exposure_cells || []).forEach((cell) => {
    const selected = state.selected.type === "building" && state.selected.id === cell.id;
    const circle = L.circle([cell.lat, cell.lon], {
      radius: Number(cell.radius_km || 2) * 1000,
      color: "#a86711",
      weight: selected ? 3 : 1.5,
      fillColor: "#e8b64d",
      fillOpacity: 0.16 + Number(cell.density || 0.5) * 0.16,
    });
    bindInteractive(
      circle,
      "building",
      cell,
      cell.label,
      `Civilian exposure: ${cell.civilian_exposure}; movement constraint: ${cell.mobility_constraint}`,
    ).addTo(group);
    if (selected || (state.mode === "full_context" && Number(cell.density || 0) >= 0.8)) {
      circle.bindTooltip(cell.label, {permanent: true, direction: "top", className: "map-tooltip"});
    }
  });
}

function renderCommunicationsLayer() {
  const group = addGroup("communications");
  (layers.communications_context_cells || []).forEach((cell) => {
    const selected = state.selected.type === "communications" && state.selected.id === cell.id;
    const circle = L.circle([cell.lat, cell.lon], {
      radius: Number(cell.radius_km || 4) * 1000,
      color: "#1d64a8",
      weight: selected ? 3 : 2,
      dashArray: "8 8",
      fillColor: "#1d64a8",
      fillOpacity: state.mode === "semantic_summary" ? 0.04 : 0.07,
    });
    bindInteractive(
      circle,
      "communications",
      cell,
      cell.label,
      `${cell.note || "Coarse communications context only."} Coverage score: ${cell.coverage_score}`,
    ).addTo(group);
    if (selected || state.mode === "full_context") {
      circle.bindTooltip("comms aggregate", {permanent: true, direction: "center", className: "map-tooltip"});
    }
  });
}

function renderAggregatesLayer() {
  const group = addGroup("aggregates");
  (layers.power_it_aggregates || []).forEach((item) => {
    const selected = state.selected.type === "aggregates" && state.selected.id === item.id;
    const marker = L.marker([item.lat, item.lon], {
      icon: markerIcon("aggregate", {selected}),
      keyboard: true,
      title: item.label,
    });
    bindInteractive(marker, "aggregates", item, item.label, item.safe_use).addTo(group);
  });
}

function renderMedicalLayer() {
  const group = addGroup("medical");
  (layers.medical_facilities || []).forEach((item) => {
    const selected = state.selected.type === "medical" && state.selected.id === item.id;
    const marker = L.marker([item.lat, item.lon], {
      icon: markerIcon("medical", {selected}),
      keyboard: true,
      title: item.name,
    });
    bindInteractive(marker, "medical", item, item.name, item.role).addTo(group);
    if (selected || state.mode === "full_context") {
      marker.bindTooltip(item.name, {permanent: true, direction: "top", className: "map-tooltip"});
    }
  });
}

function renderEventsLayer() {
  const group = addGroup("events");
  (data.semantic_events || []).forEach((event) => {
    const selected = state.selected.type === "event" && state.selected.id === event.id;
    const marker = L.marker([event.lat, event.lon], {
      icon: markerIcon("event", {selected, severity: event.severity}),
      keyboard: true,
      zIndexOffset: 1000,
      title: event.event_type,
    });
    bindInteractive(marker, "event", event, event.event_type, event.summary).addTo(group);
    if (selected) {
      marker.bindTooltip(event.event_type, {permanent: true, direction: "top", className: "map-tooltip"});
    }
  });
}

function renderMap() {
  if (!initMap()) return;
  clearMapLayers();
  if (state.visible.building) renderBuildingLayer();
  if (state.visible.communications) renderCommunicationsLayer();
  if (state.visible.aggregates) renderAggregatesLayer();
  if (state.visible.medical) renderMedicalLayer();
  if (state.visible.events) renderEventsLayer();
  setTimeout(() => mapState.map.invalidateSize(), 0);
}

function findRecord(type, id) {
  const collectionByType = {
    event: data.semantic_events || [],
    medical: layers.medical_facilities || [],
    building: layers.building_exposure_cells || [],
    building_footprint: (buildingFootprints.features || []).map((feature) => ({
      id: feature.properties.id,
      ...feature.properties,
    })),
    communications: layers.communications_context_cells || [],
    aggregates: layers.power_it_aggregates || [],
  };
  return (collectionByType[type] || []).find((item) => item.id === id) || null;
}

function findEvidence(ref) {
  const pools = [
    ["medical", layers.medical_facilities || []],
    ["building", layers.building_exposure_cells || []],
    ["communications", layers.communications_context_cells || []],
    ["aggregates", layers.power_it_aggregates || []],
    [
      "building_footprint",
      (buildingFootprints.features || []).map((feature) => ({
        id: feature.properties.id,
        ...feature.properties,
      })),
    ],
  ];
  for (const [type, items] of pools) {
    const match = items.find((item) => item.id === ref);
    if (match) return {type, item: match};
  }
  return null;
}

function chipClassForMode(mode) {
  if (mode === "public_exact") return "";
  if (mode === "aggregate_only" || mode === "district_aggregate" || mode === "regional_aggregate") return "warning";
  return "muted";
}

function renderEventDetails(record) {
  const evidence = (record.evidence_refs || [])
    .map((ref) => {
      const evidenceRecord = findEvidence(ref);
      if (!evidenceRecord) return "";
      const label = evidenceRecord.item.name || evidenceRecord.item.label || evidenceRecord.item.id;
      return `<li><button class="evidence-button" data-type="${escapeHtml(evidenceRecord.type)}" data-id="${escapeHtml(ref)}">${escapeHtml(label)}</button></li>`;
    })
    .join("");

  return `
    <div class="detail-card">
      <p class="detail-summary">${escapeHtml(record.summary)}</p>
      <div class="detail-grid">
        <div class="metric">
          <p class="meta-label">Priority</p>
          <div class="metric-value">${escapeHtml(Math.round(Number(record.priority || 0) * 100))}</div>
        </div>
        <div class="metric">
          <p class="meta-label">Semantic Size</p>
          <div class="metric-value">${escapeHtml(record.bytes_semantic)} B</div>
        </div>
      </div>
      <div class="detail-block">
        <p class="detail-label">Why It Matters</p>
        <p>${escapeHtml(record.why_it_matters)}</p>
      </div>
      <div class="detail-block">
        <p class="detail-label">Recommended Action</p>
        <p>${escapeHtml(record.recommended_action)}</p>
      </div>
      <div class="detail-block">
        <p class="detail-label">Evidence</p>
        <ul class="evidence-list">${evidence}</ul>
      </div>
    </div>
  `;
}

function renderGenericDetails(record, type) {
  const title = record.name || record.label || record.id;
  const rows = Object.entries(record)
    .filter(([key]) => !["id", "lat", "lon", "name", "label", "source_candidates"].includes(key))
    .map(([key, value]) => {
      const display = Array.isArray(value) ? value.join(", ") : String(value);
      return `<li><span class="safe-dot"></span><span><strong>${escapeHtml(titleCase(key))}:</strong> ${escapeHtml(display)}</span></li>`;
    })
    .join("");
  const candidates = (record.source_candidates || [record.public_source_candidate, record.source_candidate])
    .filter(Boolean)
    .map((source) => `<span class="chip muted">${escapeHtml(source)}</span>`)
    .join(" ");

  return `
    <div class="detail-card">
      <p class="detail-summary">${escapeHtml(title)}</p>
      <div class="detail-block">
        <p class="detail-label">Record Attributes</p>
        <ul class="detail-list">${rows}</ul>
      </div>
      <div class="detail-block">
        <p class="detail-label">Source Candidates</p>
        <p>${candidates || "No source candidate recorded"}</p>
      </div>
      <div class="detail-block">
        <p class="detail-label">Precision Rule</p>
        <p>${
          type === "medical"
            ? "Public exact location, treated as protected civilian asset."
            : type === "building_footprint"
              ? "Public exact building footprint. Use for civilian exposure only; no PII, resident, owner, or unit-level data."
              : "Aggregate or synthetic context. Exact sensitive facility coordinates are omitted."
        }</p>
      </div>
    </div>
  `;
}

function renderSelectedDetails() {
  const record = findRecord(state.selected.type, state.selected.id) || (data.semantic_events || [])[0];
  if (!record) return;
  const title = record.name || record.label || record.event_type || record.id;
  const mode = record.source_mode || record.transmit_tier || (record.district_level_only ? "aggregate_only" : "public_context");

  elementById("selectedTitle").textContent = title;
  elementById("selectedMode").textContent = mode;
  elementById("selectedMode").className = `status-pill ${chipClassForMode(mode)}`;
  elementById("selectedDetails").innerHTML =
    state.selected.type === "event" ? renderEventDetails(record) : renderGenericDetails(record, state.selected.type);

  elementById("selectedDetails").querySelectorAll(".evidence-button").forEach((button) => {
    button.addEventListener("click", (event) => {
      selectItem(event.currentTarget.dataset.type, event.currentTarget.dataset.id);
    });
  });
}

function renderEventList() {
  const events = [...(data.semantic_events || [])].sort((a, b) => Number(b.priority || 0) - Number(a.priority || 0));
  elementById("eventList").innerHTML = events
    .map(
      (event) => `
        <button class="event-card ${
          state.selected.type === "event" && state.selected.id === event.id ? "is-selected" : ""
        }" data-id="${escapeHtml(event.id)}">
          <span class="event-card-head">
            <h3>${escapeHtml(event.event_type)}</h3>
            <span class="chip ${severityClass(event.severity)}">${escapeHtml(event.severity)}</span>
          </span>
          <p class="event-summary">${escapeHtml(event.summary)}</p>
          <span class="event-footer">
            <span class="chip muted">${escapeHtml(event.transmit_tier)}</span>
            <span class="chip">${escapeHtml(Math.round(Number(event.priority || 0) * 100))} priority</span>
          </span>
        </button>
      `,
    )
    .join("");

  elementById("eventList").querySelectorAll("button[data-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      selectItem("event", event.currentTarget.dataset.id);
    });
  });
}

function renderSourceTable() {
  const footprintSource = buildingFootprints.source
    ? [{
        source: buildingFootprints.source.name,
        status: "collected_public_demo",
        public_url: buildingFootprints.source.url,
        layer: "building_footprints",
        precision_allowed: "public exact building footprint; no resident, owner, unit-level, or access-control data",
      }]
    : [];
  const rows = [...(data.source_catalog || []), ...footprintSource]
    .map(
      (source) => `
        <tr>
          <td>
            <strong>${escapeHtml(source.source)}</strong>
            ${escapeHtml(source.layer)}
          </td>
          <td><span class="chip ${source.status === "key_available" ? "" : "muted"}">${escapeHtml(source.status)}</span></td>
          <td>${escapeHtml(source.precision_allowed)}</td>
          <td><a class="source-link" href="${escapeHtml(source.public_url)}" target="_blank" rel="noreferrer">Open</a></td>
        </tr>
      `,
    )
    .join("");

  elementById("sourceTable").innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Source</th>
          <th>Status</th>
          <th>Precision Rule</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function bootstrap() {
  renderTopbar();
  renderLayerToggles();
  renderModeTabs();
  renderMapMeta();
  renderSafeBoundary();
  renderMap();
  renderSelectedDetails();
  renderEventList();
  renderSourceTable();
}

bootstrap();
