const state = {
  dataset: null,
  caseId: "case_c_gnss_jamming_suspected",
  mode: "semantic_summary",
  selectedEventId: null,
  timeIndex: 0,
  sceneReady: false,
};

const sceneState = {
  scene: null,
  camera: null,
  renderer: null,
  drone: null,
  uncertainty: null,
  reportedMarker: null,
  predictedMarker: null,
  fov: null,
  dynamicGroup: null,
  lastFrameTime: 0,
};

const $ = (id) => document.getElementById(id);

const EVENT_LABEL_KO = {
  LINK_DEGRADED: "통신 저하",
  GNSS_DEGRADED: "GNSS 저하",
  JAMMING_SUSPECTED: "교란 의심",
  SPOOFING_SUSPECTED: "위치 불일치",
  REJOIN_AUDIT_REQUIRED: "재연결 감사",
  STATUS_SUMMARY: "상태 요약",
};

const MODE_LABEL_KO = {
  full_sync: "전체 동기화",
  delta_sync: "변경분 동기화",
  semantic_summary: "시맨틱 요약",
  store_forward: "저장 후 전달",
  local_only: "로컬 단독",
};

const QUALITY_KO = {
  normal: "정상",
  degraded: "저하",
  intermittent: "간헐",
  rejoined: "재연결",
  inconsistent: "불일치",
  nominal_but_inconsistent: "표면상 정상/불일치",
};

const ASSET_TYPE_KO = {
  synthetic_quadcopter: "합성 정찰 드론",
  synthetic_ground_relay: "합성 지상 중계 노드",
  synthetic_rf_sensor: "합성 RF 센서",
};

const SENSOR_LABEL_KO = {
  EO_IR: "EO/IR",
  GNSS: "GNSS",
  IMU: "IMU",
  LINK_TELEMETRY: "링크 원격측정",
  LINK_RELAY: "링크 중계",
  RF_CONTEXT: "RF 맥락",
  STATUS_SUMMARY: "상태 요약",
  GNSS_HEALTH: "GNSS 상태",
  IMU_STATE: "IMU 상태",
  GNSS_INCONSISTENCY: "GNSS 불일치",
  WEATHER_CONTEXT: "기상/풍향 맥락",
  NAVIGATION_RESIDUAL_SPIKE: "항법 잔차 급증",
  POSITION_REPORT_INCONSISTENCY: "보고 위치 불일치",
  jamming_suspected: "교란 의심",
  navigation_degraded: "항법 저하",
  spoofing_like_inconsistency: "위치 무결성 불일치",
  case_evaluation_inputs: "케이스 평가 입력값",
  gnss_quality_drop: "GNSS 품질 저하",
  link_quality_drop: "링크 품질 저하",
  normalized_position_residual: "정규화 위치 잔차",
  heartbeat_gap_score: "Heartbeat 공백",
  imu_gnss_disagreement: "IMU-GNSS 불일치",
  context_risk: "환경 맥락 위험",
};

const PACKET_TIER_KO = {
  STATUS_CARD: "상태 카드",
  LINK_HEALTH_CARD: "링크 상태 카드",
  NAV_HEALTH_CARD: "항법 상태 카드",
  NAV_INTEGRITY_CARD: "항법 무결성 카드",
  REJOIN_AUDIT_CARD: "재연결 감사 카드",
};

const WEIGHT_LABEL_KO = {
  flight_safety: "비행 안전",
  navigation_integrity: "항법 무결성",
  mission_relevance: "임무 관련성",
  link_survivability: "링크 생존성",
  provenance_audit: "근거 감사",
};

const DIAGNOSTIC_LABEL_KO = {
  normal: "정상",
  link_degraded: "통신 저하",
  jamming_suspected: "교란 의심",
  spoofing_suspected: "위치 불일치",
  rejoin_audit: "재연결 감사",
};

const UPDATE_DECISION_KO = {
  accepted: "측정 반영",
  rejected_gate: "게이트 차단",
};

function fmtBytes(bytes) {
  if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(2)} MB`;
  if (bytes >= 1_000) return `${(bytes / 1_000).toFixed(1)} KB`;
  return `${bytes} B`;
}

function pct(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function modeLabel(mode) {
  return MODE_LABEL_KO[mode] || mode;
}

function eventLabel(event) {
  return EVENT_LABEL_KO[event.event_type] || event.event_type;
}

function qualityKo(value) {
  return QUALITY_KO[value] || String(value || "확인 필요");
}

function assetTypeKo(value) {
  return ASSET_TYPE_KO[value] || String(value || "자산");
}

function sensorLabelKo(value) {
  return SENSOR_LABEL_KO[value] || String(value || "").replaceAll("_", " ");
}

function packetTierKo(value) {
  return PACKET_TIER_KO[value] || String(value || "").replaceAll("_", " ");
}

function diagnosticLabelKo(value) {
  return DIAGNOSTIC_LABEL_KO[value] || String(value || "").replaceAll("_", " ");
}

function weightLabelKo(value) {
  return WEIGHT_LABEL_KO[value] || String(value || "").replaceAll("_", " ");
}

function currentCase() {
  return state.dataset.simulation_cases.find((item) => item.case_id === state.caseId);
}

function timeline(caseId = state.caseId) {
  return state.dataset.flight_timelines[caseId] || [];
}

function currentRow() {
  const rows = timeline();
  return rows[state.timeIndex % rows.length] || rows[0];
}

function caseEvents() {
  return state.dataset.semantic_events
    .filter((event) => (event.case_ids || []).includes(state.caseId))
    .sort((a, b) => b.priority - a.priority);
}

function casePackets() {
  const eventIds = new Set(caseEvents().map((event) => event.event_id));
  return state.dataset.routing_results[state.mode].packets.filter((packet) => eventIds.has(packet.event_id));
}

function caseRoutingMetrics() {
  const packets = casePackets();
  const sentPackets = packets.filter((packet) => packet.decision === "send");
  const rawTotal = packets.reduce((sum, packet) => sum + Number(packet.bytes_raw_represented || 0), 0);
  const semanticSent = sentPackets.reduce((sum, packet) => sum + Number(packet.bytes_semantic || 0), 0);
  return {
    events_sent: sentPackets.length,
    events_total: packets.length,
    raw_bytes_total_if_full_feed: rawTotal,
    semantic_bytes_sent: semanticSent,
    bytes_saved_pct_vs_full_feed: rawTotal ? Math.round((100 * (1 - semanticSent / rawTotal)) * 100) / 100 : 0,
    message_survival_rate: packets.length ? sentPackets.length / packets.length : 0,
  };
}

function caseDiagnostic() {
  return state.dataset.case_diagnostics?.[state.caseId] || {
    label: "unknown",
    score: 0,
    max_residual_m: 0,
    max_nis: 0,
    interpretation_ko: "케이스 진단값이 없습니다.",
  };
}

function caseEvaluation() {
  return state.dataset.case_evaluations?.[state.caseId] || {
    max_residual_m: 0,
    max_nis: 0,
    nis_threshold_watch: 9.21,
    detection_latency_sec: null,
    false_alarm_risk: 0,
    confidence: 0,
    operator_decision_ko: "평가값이 없습니다.",
    semantic_policy_ko: "패킷 정책을 확인해야 합니다.",
  };
}

function caseEvaluationSeries(caseId = state.caseId) {
  return state.dataset.case_evaluation_series?.[caseId]?.series || [];
}

function kalmanTrace(caseId = state.caseId) {
  return state.dataset.kalman_estimator_traces?.[caseId]?.trace || [];
}

function currentKalmanRow() {
  const trace = kalmanTrace();
  return trace[state.timeIndex % trace.length] || trace[0] || null;
}

function initialTimeIndexForCase(caseId) {
  const series = caseEvaluationSeries(caseId);
  const index = series.findIndex((item) => ["degraded", "watch", "critical"].includes(item.threshold_state));
  return index >= 0 ? index : 0;
}

function updateDecisionKo(value) {
  return UPDATE_DECISION_KO[value] || String(value || "확인 필요").replaceAll("_", " ");
}

function selectedEvent() {
  const events = caseEvents();
  return events.find((event) => event.event_id === state.selectedEventId) || events[0] || state.dataset.semantic_events[0];
}

function packetFor(eventId = state.selectedEventId) {
  return state.dataset.routing_results[state.mode].packets.find((packet) => packet.event_id === eventId);
}

function sourceByRef(ref) {
  return (
    state.dataset.raw_observations.find((item) => item.observation_id === ref) ||
    state.dataset.edge_detections.find((item) => item.detection_id === ref) ||
    state.dataset.jamming_hypotheses.find((item) => item.hypothesis_id === ref)
  );
}

function toScene(pos) {
  return new THREE.Vector3(
    Number(pos.east || 0) / 24,
    Math.max(1.5, -Number(pos.down || -120) / 18),
    -Number(pos.north || 0) / 24,
  );
}

function material(color, options = {}) {
  return new THREE.MeshStandardMaterial({
    color,
    metalness: 0.18,
    roughness: 0.58,
    transparent: Boolean(options.transparent),
    opacity: options.opacity ?? 1,
    side: options.side || THREE.FrontSide,
  });
}

function lineMaterial(color, options = {}) {
  return new THREE.LineBasicMaterial({
    color,
    transparent: Boolean(options.transparent),
    opacity: options.opacity ?? 1,
  });
}

function makeLine(points, color, options = {}) {
  const geometry = new THREE.BufferGeometry().setFromPoints(points.map(toScene));
  return new THREE.Line(geometry, lineMaterial(color, options));
}

function makeMarker(color, radius = 0.8) {
  return new THREE.Mesh(new THREE.SphereGeometry(radius, 20, 16), material(color));
}

function makeDrone() {
  const group = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.6, 1.6), material(0x2d66ad));
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.5, 1.1, 4), material(0xf1c84b));
  nose.rotation.z = -Math.PI / 2;
  nose.position.x = 1.75;
  group.add(body, nose);

  const armMaterial = material(0xdce9e6);
  const armA = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.12, 0.12), armMaterial);
  const armB = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 3.8), armMaterial);
  group.add(armA, armB);

  const rotorMaterial = material(0x111614);
  [
    [2.2, 0, 1.8],
    [2.2, 0, -1.8],
    [-2.2, 0, 1.8],
    [-2.2, 0, -1.8],
  ].forEach(([x, y, z]) => {
    const rotor = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.08, 24), rotorMaterial);
    rotor.position.set(x, y, z);
    rotor.userData.rotor = true;
    group.add(rotor);
  });

  const fov = new THREE.Mesh(
    new THREE.ConeGeometry(3.3, 9, 32, 1, true),
    material(0x5aa2ff, {transparent: true, opacity: 0.13, side: THREE.DoubleSide}),
  );
  fov.rotation.x = Math.PI;
  fov.position.y = -4.8;
  group.add(fov);
  sceneState.fov = fov;

  return group;
}

function makeUncertaintyEllipse() {
  const points = [];
  for (let i = 0; i <= 96; i += 1) {
    const theta = (i / 96) * Math.PI * 2;
    points.push(new THREE.Vector3(Math.cos(theta), 0, Math.sin(theta)));
  }
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  return new THREE.LineLoop(geometry, lineMaterial(0x5aa2ff, {transparent: true, opacity: 0.92}));
}

function setupScene() {
  const root = $("sceneRoot");
  if (!window.THREE || !root) return false;
  if (sceneState.scene) return true;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0d1412);
  scene.fog = new THREE.Fog(0x0d1412, 70, 210);

  const camera = new THREE.PerspectiveCamera(46, root.clientWidth / root.clientHeight, 0.1, 600);
  camera.position.set(38, 42, 54);
  camera.lookAt(10, 2, -24);

  const renderer = new THREE.WebGLRenderer({antialias: true, alpha: false, preserveDrawingBuffer: true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(root.clientWidth, root.clientHeight);
  root.appendChild(renderer.domElement);

  const ambient = new THREE.AmbientLight(0xffffff, 0.62);
  const directional = new THREE.DirectionalLight(0xffffff, 1.4);
  directional.position.set(24, 50, 18);
  scene.add(ambient, directional);

  const grid = new THREE.GridHelper(150, 30, 0x4f6964, 0x253732);
  scene.add(grid);

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(180, 180),
    material(0x14201d, {transparent: true, opacity: 0.56, side: THREE.DoubleSide}),
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.02;
  scene.add(ground);

  sceneState.dynamicGroup = new THREE.Group();
  scene.add(sceneState.dynamicGroup);

  sceneState.drone = makeDrone();
  scene.add(sceneState.drone);
  sceneState.predictedMarker = makeMarker(0xf1c84b, 0.65);
  sceneState.reportedMarker = makeMarker(0xe15a50, 0.65);
  scene.add(sceneState.predictedMarker, sceneState.reportedMarker);
  sceneState.uncertainty = makeUncertaintyEllipse();
  scene.add(sceneState.uncertainty);

  sceneState.scene = scene;
  sceneState.camera = camera;
  sceneState.renderer = renderer;
  state.sceneReady = true;

  window.addEventListener("resize", resizeScene);
  return true;
}

function resizeScene() {
  const root = $("sceneRoot");
  if (!root || !sceneState.renderer || !sceneState.camera) return;
  sceneState.camera.aspect = root.clientWidth / root.clientHeight;
  sceneState.camera.updateProjectionMatrix();
  sceneState.renderer.setSize(root.clientWidth, root.clientHeight);
}

function clearDynamicScene() {
  const group = sceneState.dynamicGroup;
  if (!group) return;
  while (group.children.length) {
    const child = group.children.pop();
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
  }
}

function rebuildSceneForCase() {
  if (!setupScene()) return;
  clearDynamicScene();
  const rows = timeline();
  const truth = rows.map((row) => row.truth_position_m);
  const predicted = rows.map((row) => row.predicted_position_m);
  const reported = rows.map((row) => row.reported_position_m);

  const plannedLine = makeLine(truth, 0x9fb2ad, {transparent: true, opacity: 0.7});
  const predictedLine = makeLine(predicted, 0xf1c84b, {transparent: true, opacity: 0.9});
  const reportedLine = makeLine(reported, 0xe15a50, {transparent: true, opacity: 0.74});
  sceneState.dynamicGroup.add(plannedLine, predictedLine, reportedLine);

  if (state.caseId.includes("jamming") || state.caseId.includes("spoofing") || state.caseId.includes("rejoin")) {
    const degradedRow = rows[Math.min(7, rows.length - 1)];
    const center = toScene(degradedRow.reported_position_m);
    const zone = new THREE.Mesh(
      new THREE.RingGeometry(5.5, 9.5, 64),
      new THREE.MeshBasicMaterial({color: 0xbd2f2a, transparent: true, opacity: 0.2, side: THREE.DoubleSide}),
    );
    zone.rotation.x = -Math.PI / 2;
    zone.position.set(center.x, 0.06, center.z);
    sceneState.dynamicGroup.add(zone);
  }
}

function updateSceneObjects() {
  if (!sceneState.drone) return;
  const row = currentRow();
  const truth = toScene(row.truth_position_m);
  const predicted = toScene(row.predicted_position_m);
  const reported = toScene(row.reported_position_m);
  sceneState.drone.position.copy(truth);
  sceneState.drone.rotation.y = -0.35;
  sceneState.predictedMarker.position.copy(predicted);
  sceneState.reportedMarker.position.copy(reported);

  const scaleX = Math.max(1, Number(row.uncertainty_ellipse_m.minor || 50) / 24);
  const scaleZ = Math.max(1, Number(row.uncertainty_ellipse_m.major || 100) / 24);
  sceneState.uncertainty.position.copy(predicted);
  sceneState.uncertainty.scale.set(scaleX, 1, scaleZ);

  sceneState.drone.children.forEach((child) => {
    if (child.userData.rotor) child.rotation.y += 0.55;
  });
}

function animateScene(now = 0) {
  if (!sceneState.renderer || !sceneState.scene || !sceneState.camera) return;
  if (now - sceneState.lastFrameTime > 900) {
    state.timeIndex = (state.timeIndex + 1) % timeline().length;
    sceneState.lastFrameTime = now;
    renderDynamicReadouts();
    renderEvaluation();
  }
  updateSceneObjects();
  sceneState.renderer.render(sceneState.scene, sceneState.camera);
  requestAnimationFrame(animateScene);
}

function renderTopMetrics() {
  const routing = caseRoutingMetrics();
  const diagnostic = caseDiagnostic();
  $("topMetrics").innerHTML = `
    <div class="metric"><span>케이스 진단 점수</span><strong>${pct(diagnostic.score)}</strong></div>
    <div class="metric"><span>시맨틱 전송</span><strong>${fmtBytes(routing.semantic_bytes_sent)}</strong></div>
    <div class="metric"><span>절감률</span><strong>${routing.bytes_saved_pct_vs_full_feed}%</strong></div>
  `;
}

function renderObjective() {
  const intent = state.dataset.control_intent;
  const weights = Object.entries(intent.priority_weights)
    .slice(0, 4)
    .map(([key, value]) => `<span class="chip">${weightLabelKo(key)} ${pct(value)}</span>`)
    .join("");
  const diagnostic = caseDiagnostic();
  $("objectiveStrip").innerHTML = `
    <div class="objective-card">
      <p class="panel-kicker">현 임무 목표</p>
      <h2>${intent.display_name_ko}</h2>
      <p>${intent.primary_objective}</p>
    </div>
    <div class="objective-focus">${weights}</div>
    <div class="objective-score">
      <span>케이스 점수</span>
      <strong>${pct(diagnostic.score)}</strong>
      <small>${diagnosticLabelKo(diagnostic.label)}</small>
    </div>
  `;
}

function renderCaseButtons() {
  $("caseButtons").innerHTML = state.dataset.simulation_cases.map((item) => `
    <button class="case-button ${item.case_id === state.caseId ? "active" : ""}" data-case="${item.case_id}" type="button">
      <strong>${item.label_ko}</strong>
      <span>${item.scenario_summary_ko || item.case_id.replaceAll("_", " ")}</span>
    </button>
  `).join("");
  document.querySelectorAll(".case-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.caseId = button.dataset.case;
      state.mode = currentCase()?.default_mode || state.mode;
      state.timeIndex = initialTimeIndexForCase(state.caseId);
      sceneState.lastFrameTime = performance.now();
      state.selectedEventId = caseEvents()[0]?.event_id || state.selectedEventId;
      rebuildSceneForCase();
      renderAll();
    });
  });
}

function renderModeButtons() {
  $("modeButtons").innerHTML = Object.entries(state.dataset.network_modes).map(([key, mode]) => `
    <button class="mode-button ${key === state.mode ? "active" : ""}" data-mode="${key}" type="button">
      <strong>${modeLabel(key)}</strong>
      <span>${mode.bandwidth_kbps} kbps · 손실 ${mode.packet_loss_pct}%</span>
    </button>
  `).join("");
  document.querySelectorAll(".mode-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      renderAll();
    });
  });
}

function renderAssets() {
  $("assetList").innerHTML = state.dataset.drone_assets.map((asset) => `
    <div class="asset-row">
      <div class="asset-code">${asset.asset_code}</div>
      <div>
        <strong>${assetTypeKo(asset.asset_type)}</strong>
        <span>${asset.sensor_modalities.map(sensorLabelKo).join(" · ")} · ${qualityKo(asset.comm_state)}</span>
      </div>
      <b class="battery">${asset.battery_pct}%</b>
    </div>
  `).join("");
}

function renderDynamicReadouts() {
  const row = currentRow();
  const event = selectedEvent();
  const packet = packetFor(event.event_id);
  const diagnostic = caseDiagnostic();
  $("simToolbar").innerHTML = `
    <div class="sim-stat"><span>시간</span><strong>T+${row.t_seconds}s</strong></div>
    <div class="sim-stat"><span>잔차</span><strong>${row.residual_m} m</strong></div>
    <div class="sim-stat"><span>NIS</span><strong>${row.nis}</strong></div>
    <div class="sim-stat"><span>GNSS / Link</span><strong>${qualityKo(row.gnss_quality)} · ${qualityKo(row.link_quality)}</strong></div>
  `;
  $("navIntegrity").innerHTML = `
    <div class="fact-grid">
      <div class="fact"><b>잔차</b><span>${row.residual_m} m</span></div>
      <div class="fact"><b>NIS</b><span>${row.nis}</span></div>
      <div class="fact"><b>불확실성 장축</b><span>${row.uncertainty_ellipse_m.major} m</span></div>
      <div class="fact"><b>패킷 판단</b><span>${decisionKo(packet.decision)}</span></div>
    </div>
    <div class="score-bar"><span style="width:${Math.min(100, row.nis * 4)}%"></span></div>
    <div class="evidence-item"><strong>${diagnosticLabelKo(diagnostic.label)}</strong><br>${diagnostic.interpretation_ko}</div>
  `;
  $("caseStatus").className = `status-pill ${event.severity}`;
  $("caseStatus").textContent = eventLabel(event);
}

function thresholdStateKo(value) {
  return {
    nominal: "정상",
    degraded: "저하",
    watch: "주의",
    critical: "위험",
  }[value] || value;
}

function metricPoints(series, key, width, height) {
  if (!series.length) return "";
  const maxIndex = Math.max(1, series.length - 1);
  return series.map((item, index) => {
    const x = Math.round((index / maxIndex) * width * 10) / 10;
    const y = Math.round((height - Math.max(0, Math.min(1, Number(item[key] || 0))) * height) * 10) / 10;
    return `${x},${y}`;
  }).join(" ");
}

function renderTrendChart() {
  const series = caseEvaluationSeries();
  if (!series.length) return `<div class="trend-card">평가 추세 데이터가 없습니다.</div>`;
  const width = 300;
  const height = 96;
  const currentIndex = state.timeIndex % series.length;
  const current = series[currentIndex];
  const currentX = Math.round((currentIndex / Math.max(1, series.length - 1)) * width * 10) / 10;
  const watchY = Math.round((height - (9.21 / 16) * height) * 10) / 10;
  return `
    <div class="trend-card">
      <div class="trend-heading">
        <strong>평가 추세</strong>
        <span>T+${current.t_seconds}s · ${thresholdStateKo(current.threshold_state)} · ${current.action_hint_ko}</span>
      </div>
      <svg class="trend-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="잔차 NIS 불확실성 추세">
        <line class="trend-threshold" x1="0" y1="${watchY}" x2="${width}" y2="${watchY}"></line>
        <polyline class="trend-line residual-line" points="${metricPoints(series, "residual_norm", width, height)}"></polyline>
        <polyline class="trend-line nis-line" points="${metricPoints(series, "nis_norm", width, height)}"></polyline>
        <polyline class="trend-line uncertainty-line" points="${metricPoints(series, "uncertainty_norm", width, height)}"></polyline>
        <polyline class="trend-line hypothesis-line" points="${metricPoints(series, "hypothesis_score", width, height)}"></polyline>
        <line class="trend-current" x1="${currentX}" y1="0" x2="${currentX}" y2="${height}"></line>
      </svg>
      <div class="trend-legend">
        <span><b class="residual-line"></b>잔차</span>
        <span><b class="nis-line"></b>NIS</span>
        <span><b class="uncertainty-line"></b>불확실성</span>
        <span><b class="hypothesis-line"></b>가설 점수</span>
      </div>
    </div>
  `;
}

function renderEstimatorComparison() {
  const estimate = currentKalmanRow();
  if (!estimate) return `<div class="estimator-card">추정기 trace 데이터가 없습니다.</div>`;
  const maxError = Math.max(1, Number(estimate.reported_error_m || 0), Number(estimate.estimate_error_m || 0));
  const reportedWidth = Math.min(100, (Number(estimate.reported_error_m || 0) / maxError) * 100);
  const estimateWidth = Math.min(100, (Number(estimate.estimate_error_m || 0) / maxError) * 100);
  return `
    <div class="estimator-card">
      <div class="estimator-heading">
        <strong>추정기 비교</strong>
        <span class="status-pill ${estimate.update_decision}">${updateDecisionKo(estimate.update_decision)}</span>
      </div>
      <div class="estimator-grid">
        <div class="fact"><b>Innovation NIS</b><span>${estimate.innovation_nis}</span></div>
        <div class="fact"><b>Gate 기준</b><span>${estimate.gate_threshold}</span></div>
        <div class="fact"><b>측정 sigma</b><span>${estimate.measurement_sigma_m} m</span></div>
        <div class="fact"><b>2σ 위치</b><span>${estimate.position_sigma_major_m} m</span></div>
      </div>
      <div class="compare-bars">
        <div class="byte-row">
          <div class="bar-label"><span>보고 위치 오차</span><strong>${estimate.reported_error_m} m</strong></div>
          <div class="bar"><span style="width:${reportedWidth}%; background:var(--red)"></span></div>
        </div>
        <div class="byte-row">
          <div class="bar-label"><span>Kalman 추정 오차</span><strong>${estimate.estimate_error_m} m</strong></div>
          <div class="bar"><span style="width:${estimateWidth}%; background:var(--blue)"></span></div>
        </div>
      </div>
      <p>${estimate.semantic_meaning_ko}</p>
    </div>
  `;
}

function renderEvaluation() {
  const row = currentRow();
  const evaluation = caseEvaluation();
  const basis = state.dataset.algorithm_basis || {};
  const event = selectedEvent();
  const refs = event.evidence_refs || [];
  const hypothesis = refs.map(sourceByRef).find((source) => source?.inputs);
  const latency = evaluation.detection_latency_sec === null || evaluation.detection_latency_sec === undefined
    ? "해당 없음"
    : `+${evaluation.detection_latency_sec}s`;
  const nisWidth = Math.min(100, (Number(row.nis || 0) / Number(evaluation.nis_threshold_critical || 16)) * 100);
  const inputBars = hypothesis?.inputs
    ? Object.entries(hypothesis.inputs).map(([key, value]) => `
      <div class="input-row">
        <span>${sensorLabelKo(key)}</span>
        <div class="mini-bar"><b style="width:${Math.min(100, Number(value) * 100)}%"></b></div>
        <strong>${pct(value)}</strong>
      </div>
    `).join("")
    : `<div class="evidence-item">현재 선택 이벤트에는 가설 점수 입력값이 없습니다. 정상/단순 링크 저하 케이스는 잔차와 전송정책 중심으로 평가합니다.</div>`;

  $("evaluationPanel").innerHTML = `
    <div class="eval-grid">
      <div class="fact"><b>최대 잔차</b><span>${evaluation.max_residual_m} m</span></div>
      <div class="fact"><b>최대 NIS</b><span>${evaluation.max_nis}</span></div>
      <div class="fact"><b>NIS 기준</b><span>${evaluation.nis_threshold_watch}</span></div>
      <div class="fact"><b>탐지 지연</b><span>${latency}</span></div>
      <div class="fact"><b>오탐 위험</b><span>${pct(evaluation.false_alarm_risk)}</span></div>
      <div class="fact"><b>신뢰도</b><span>${pct(evaluation.confidence)}</span></div>
    </div>
    <div class="score-caption">
      <span>현재 NIS / 위험 기준</span>
      <strong>${row.nis} / ${evaluation.nis_threshold_critical || 16}</strong>
    </div>
    <div class="score-bar"><span style="width:${nisWidth}%"></span></div>
    ${renderTrendChart()}
    ${renderEstimatorComparison()}
    <div class="logic-card">
      <strong>판정 로직</strong>
      <ol>
        <li>${basis.prediction_model?.explain_ko || "예측 위치를 계산합니다."}</li>
        <li>${basis.residual_model?.explain_ko || "보고 위치와 예측 위치의 차이를 계산합니다."}</li>
        <li>${basis.nis_model?.explain_ko || "잔차가 불확실성 대비 과도한지 봅니다."}</li>
      </ol>
    </div>
    <div class="policy-card">
      <strong>오퍼레이터 판단</strong>
      <p>${evaluation.operator_decision_ko}</p>
      <strong>전송 정책</strong>
      <p>${evaluation.semantic_policy_ko}</p>
    </div>
    <div class="hypothesis-box">
      <strong>${hypothesis?.label ? sensorLabelKo(hypothesis.label) : sensorLabelKo("case_evaluation_inputs")}</strong>
      ${inputBars}
      ${hypothesis?.caveat ? `<p>${hypothesis.caveat}</p>` : ""}
    </div>
  `;
}

function decisionKo(decision) {
  return {
    send: "전송",
    defer: "보류",
    drop: "폐기",
    hold_local: "로컬 보존",
  }[decision] || decision;
}

function renderEvents() {
  const events = caseEvents();
  $("eventList").innerHTML = events.map((event) => {
    const packet = packetFor(event.event_id);
    return `
      <button class="event-button ${event.event_id === state.selectedEventId ? "active" : ""}" data-event="${event.event_id}" type="button">
        <strong>${eventLabel(event)} · ${pct(event.priority)}</strong>
        <span>${event.summary}</span>
        <span>${decisionKo(packet.decision)} · ${fmtBytes(packet.bytes_semantic)}</span>
      </button>
    `;
  }).join("");
  document.querySelectorAll(".event-button").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedEventId = button.dataset.event;
      renderAll();
    });
  });
}

function renderEvidence() {
  const event = selectedEvent();
  const refs = event.evidence_refs || [];
  $("evidencePanel").innerHTML = refs.map((ref) => {
    const source = sourceByRef(ref);
    if (!source) return `<div class="evidence-item"><code>${ref}</code><br>근거 참조 확인 필요</div>`;
    const label = sensorLabelKo(source.sensor_type || source.candidate_type || source.label || source.hypothesis_id);
    const summary = source.summary || source.caveat || source.model_or_rule || "";
    return `<div class="evidence-item"><code>${ref}</code><br><strong>${label}</strong><br>${summary}</div>`;
  }).join("");
}

function renderPackets() {
  const metrics = caseRoutingMetrics();
  const selectedPacket = packetFor();
  const semanticWidth = metrics.raw_bytes_total_if_full_feed
    ? Math.max(1, Math.min(100, (metrics.semantic_bytes_sent / metrics.raw_bytes_total_if_full_feed) * 100))
    : 0;
  $("routingDecision").className = `status-pill ${selectedPacket.decision}`;
  $("routingDecision").textContent = decisionKo(selectedPacket.decision);
  $("packetInspector").innerHTML = `
    <div class="packet-summary">
      <div class="byte-row">
        <div class="bar-label"><span>원본 feed</span><strong>${fmtBytes(metrics.raw_bytes_total_if_full_feed)}</strong></div>
        <div class="bar"><span style="width:100%; background:var(--red)"></span></div>
      </div>
      <div class="byte-row">
        <div class="bar-label"><span>전송된 시맨틱</span><strong>${fmtBytes(metrics.semantic_bytes_sent)}</strong></div>
        <div class="bar"><span style="width:${semanticWidth}%"></span></div>
      </div>
      <div class="byte-row">
        <div class="bar-label"><span>생존 이벤트</span><strong>${metrics.events_sent}/${metrics.events_total}</strong></div>
        <div class="bar"><span style="width:${metrics.message_survival_rate * 100}%; background:var(--blue)"></span></div>
      </div>
    </div>
    <div class="packet-table">
      ${casePackets().map((packet) => {
        const event = state.dataset.semantic_events.find((item) => item.event_id === packet.event_id);
        return `
          <div class="packet-row">
            <strong>${eventLabel(event)}</strong>
            <span>${packetTierKo(packet.payload_tier)}</span>
            <span class="status-pill ${packet.decision}">${decisionKo(packet.decision)}</span>
          </div>
        `;
      }).join("")}
    </div>
  `;
}

function renderHandoff() {
  const handoff = state.dataset.platform_handoff || {};
  const objectTables = handoff.object_tables || [];
  const actions = handoff.action_definitions || [];
  const workflows = handoff.aip_workflow_cards || [];
  const guardrails = handoff.guardrails_ko || [];
  $("handoffPanel").innerHTML = `
    <div class="handoff-summary">
      <div class="handoff-card">
        <span>객체 테이블</span>
        <strong>${objectTables.length}</strong>
        <small>${handoff.bundle_id || "handoff bundle"}</small>
      </div>
      <div class="handoff-card">
        <span>관계 링크</span>
        <strong>${handoff.relationship_links || 0}</strong>
        <small>링크 참조 무결성 검증</small>
      </div>
      <div class="handoff-card">
        <span>액션</span>
        <strong>${actions.length}</strong>
        <small>승인 · contested 표시 · 감사 · DDIL</small>
      </div>
      <div class="handoff-card">
        <span>AIP 카드</span>
        <strong>${workflows.length}</strong>
        <small>요약 · 패킷 우선순위 · 재연결 감사</small>
      </div>
    </div>
    <div class="handoff-body">
      <div class="handoff-list">
        <strong>Ontology 후보 객체</strong>
        <div>${objectTables.map((item) => `<span>${item}</span>`).join("")}</div>
      </div>
      <div class="handoff-list">
        <strong>Action 후보</strong>
        <div>${actions.map((item) => `<span>${item.replaceAll("_", " ")}</span>`).join("")}</div>
      </div>
      <div class="handoff-guardrails">
        <strong>안전 경계</strong>
        ${guardrails.map((item) => `<p>${item}</p>`).join("")}
      </div>
    </div>
    <p class="handoff-note">경로: ${handoff.bundle_path || "07_deliverables/palantir/sdot_drone_semantic_ops"}</p>
  `;
}

function renderAll() {
  renderTopMetrics();
  renderObjective();
  renderCaseButtons();
  renderModeButtons();
  renderAssets();
  renderDynamicReadouts();
  renderEvaluation();
  renderEvents();
  renderEvidence();
  renderPackets();
  renderHandoff();
}

async function boot() {
  state.dataset = window.__D4D_DRONE_SDOT_DATASET || await (await fetch("./data/mock_dataset.json")).json();
  const primaryCase = state.dataset.simulation_cases.find((item) => item.primary);
  state.caseId = primaryCase?.case_id || state.dataset.simulation_cases[0].case_id;
  state.mode = currentCase()?.default_mode || state.mode;
  state.timeIndex = initialTimeIndexForCase(state.caseId);
  sceneState.lastFrameTime = performance.now();
  state.selectedEventId = caseEvents()[0]?.event_id || state.dataset.semantic_events[0].event_id;
  setupScene();
  rebuildSceneForCase();
  renderAll();
  requestAnimationFrame(animateScene);
}

boot().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><section class="panel"><div class="panel-heading"><h2>Demo load failed</h2></div><pre>${String(error)}</pre></section></main>`;
});
