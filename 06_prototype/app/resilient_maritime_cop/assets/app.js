const state = {
  dataset: null,
  mode: "semantic_summary",
  selectedEventId: null,
  glossaryTerm: "S-DOT",
};

const buildingFootprints = window.KOREA_BUILDING_FOOTPRINTS || { features: [] };
const mapState = {
  map: null,
  groups: {},
  legend: null,
};

const $ = (id) => document.getElementById(id);
const glossary = window.D4D_GLOSSARY || {};
const PINNED_TERMS = ["S-DOT", "Mission Intent", "PACE", "Bearer", "Predicted COP", "Support Option", "Civil Comms Asset", "COP", "C2", "DDIL", "Semantic Event", "Priority Routing", "Evidence Bundle"];
const EVENT_TERM_MAP = {
  NETWORK_DEGRADED: ["Network", "Battle Network", "DDIL", "Store Forward"],
  WEATHER_HAZARD: ["Weather", "KMA", "Confidence"],
  URBAN_MOBILITY_CONSTRAINT: ["COP", "Priority Routing", "Evidence Bundle"],
  CIVILIAN_EXPOSURE_DENSITY: ["COP", "Evidence Bundle", "Confidence"],
  MEDICAL_SUPPORT_CAPACITY: ["Support Option", "COP", "Evidence Bundle"],
  PUBLIC_IT_POWER_CONTEXT: ["Civil Comms Asset", "COP", "Evidence Bundle"],
  LOW_TRUST_REPORT: ["Human Report", "Trust", "Evidence Bundle"],
  OSINT_INCIDENT: ["OSINT", "GDELT", "Evidence Bundle"],
  PRIORITY_BRIEF: ["Priority Brief", "Alert Card", "COP"],
  UNIT_ISOLATED: ["DDIL", "C2", "COP", "Store Forward"],
  SUPPORT_REQUEST: ["Support Option", "C2", "Priority Routing", "Evidence Bundle"],
  CIVIL_BEARER_CANDIDATE: ["Civil Comms Asset", "Network", "DDIL", "Priority Routing"],
  REJOIN_WINDOW: ["Predicted COP", "Store Forward", "DDIL", "Priority Routing"],
  OPPOSING_AXIS_WATCH: ["Predicted COP", "Priority Routing", "Evidence Bundle", "COP"],
};
const SENSOR_TERM_MAP = {
  WEATHER: "Weather",
  OSINT: "OSINT",
  NETWORK: "Network",
  HUMAN_REPORT: "Human Report",
  UNIT_STATUS: "COP",
  MISSION_INTENT: "C2",
  INFRASTRUCTURE: "Network",
  SUPPORT_RESOURCE: "Priority Routing",
  URBAN_CONTEXT: "COP",
  MEDICAL: "Support Option",
  PUBLIC_INFRA: "Civil Comms Asset",
  THREAT_ASSESSMENT: "COP",
};
const DATA_API_READINESS = [
  {
    label: "즉시 연결 가능한 공개 컨텍스트",
    status: "ready",
    sources: "OpenStreetMap, VWorld, 기상청, data.go.kr, HIRA/NMC, Open-Meteo",
    note: "COP 스키마를 바꾸지 않고 서울 지도·건물·의료·기상 맥락을 보강할 수 있는 소스입니다.",
  },
  {
    label: "합성 데모 백본",
    status: "synthetic",
    sources: "부대 상태, 지원자원, DDIL 상태, 현장 보고, 재연결 감사",
    note: "실제 부대·자원 배치가 아니라 안전하고 반복 가능한 해커톤 시나리오용 합성 데이터입니다.",
  },
  {
    label: "승인/거버넌스 필요",
    status: "pending",
    sources: "SafetyData, 통신사·공공안전 인프라 인벤토리, 승인형 PS-LTE/LTE-M/LTE-R 연계",
    note: "승인, 마스킹, 법적 근거, 보안 어댑터가 확인된 뒤에만 연결해야 합니다.",
  },
];

const MODE_LABEL_KO = {
  full_sync: "전체 동기화",
  delta_sync: "변경분 동기화",
  semantic_summary: "시맨틱 요약",
  store_forward: "저장 후 전달",
  local_only: "로컬 단독",
};

const MODE_DESC_KO = {
  full_sync: "세부 이벤트와 일부 원본 근거까지 이동할 수 있는 정상 연결 상태입니다.",
  delta_sync: "변경된 필드, 압축 이벤트, 근거 ID 중심으로 동기화합니다.",
  semantic_summary: "고우선순위 경보 카드와 핵심 객체 목록만 전송합니다.",
  store_forward: "대부분의 메시지는 현장에 저장하고, 매우 중요한 요약만 보냅니다.",
  local_only: "원격 전송이 불가능합니다. 로컬 COP와 재연결 후 감사가 핵심입니다.",
};

const EVENT_TYPE_KO = {
  NETWORK_DEGRADED: "통신 저하",
  WEATHER_HAZARD: "기상 위험",
  URBAN_MOBILITY_CONSTRAINT: "도심 이동 제약",
  CIVILIAN_EXPOSURE_DENSITY: "민간 노출 밀도",
  MEDICAL_SUPPORT_CAPACITY: "의료 지원 여력",
  PUBLIC_IT_POWER_CONTEXT: "공공 IT/전력 맥락",
  LOW_TRUST_REPORT: "저신뢰 보고",
  OSINT_INCIDENT: "OSINT 맥락",
  PRIORITY_BRIEF: "우선 브리핑",
  UNIT_ISOLATED: "부대 고립/간헐 접속",
  SUPPORT_REQUEST: "지원 요청",
  CIVIL_BEARER_CANDIDATE: "민간 bearer 후보",
  REJOIN_WINDOW: "재연결 창 예측",
  OPPOSING_AXIS_WATCH: "후보 기동축 감시",
};

const EVENT_COPY_KO = {
  evt_network_degraded_001: {
    summary: "서울 도심 링크 품질이 변경분 동기화에서 시맨틱 요약 단계로 저하되었습니다.",
    why: "원본 지도/건물/근거를 안정적으로 이동시키기 어려우므로 지휘 의도, readiness, 지원, 불확실성 패킷을 우선해야 합니다.",
    action: "시맨틱 요약 모드로 전환하고 원본 맥락 데이터는 저장 후 전달 큐에 넣습니다.",
  },
  evt_weather_hazard_001: {
    summary: "강우와 시정 저하가 도심 이동과 확인 신뢰도에 영향을 줍니다.",
    why: "기상 악화는 의료·전력·통신 지원 경로의 위험과 지연을 키웁니다.",
    action: "경로 불확실성을 높이고 readiness/support 패킷을 우선합니다.",
  },
  evt_urban_mobility_constraint: {
    summary: "한강 도하/도심 이동 제약이 지원과 재연결 창을 지연시킬 수 있습니다.",
    why: "지도상 가까운 지원 옵션도 교량·기상·혼잡 조건에 따라 실제 가치는 달라집니다.",
    action: "자동 배치가 아니라 지원 옵션 순위로 표시하고 사람 승인을 유지합니다.",
  },
  evt_opposing_axis_watch: {
    summary: "상대 후보축 A가 현재 감시 우선순위입니다. 단, 확인된 이동이 아니라 합성 확률 분기입니다.",
    why: "참모는 위협 가설을 보되, 이를 실시간 추적이나 확정 정보로 오인하면 안 됩니다.",
    action: "12-2는 CBD 감시를 유지하고, 12-3은 재연결/중계 옵션을 보존하며, 축 정보는 요약 카드로만 전송합니다.",
  },
  evt_civilian_exposure_cbd: {
    summary: "종로/중구 CBD 주변의 건물 밀도와 민간 노출도가 높습니다.",
    why: "도심 지상 지원은 긴급 접근로와 민간 보호를 보존해야 하며, 공공 맥락을 표적 레이어처럼 쓰면 안 됩니다.",
    action: "민간 노출도는 보호·우회·deconfliction 맥락으로만 사용합니다.",
  },
  evt_medical_capacity_north: {
    summary: "중앙/북동권 공공 의료 거점이 AOI 주변 지원 맥락을 제공합니다.",
    why: "의료 여력은 중요한 보호/지원 맥락이지만 지휘 가능한 군 자산은 아닙니다.",
    action: "보호 대상 지원 맥락으로 표시하고 Medic-2 staging은 사람 승인으로 처리합니다.",
  },
  evt_power_it_context: {
    summary: "공공 IT와 전력 의존성은 continuity 맥락이며, 정확한 보호시설 좌표는 지도에 두지 않습니다.",
    why: "지휘참모는 서비스 연속성 의존성을 이해해야 하지만 민감 노드를 노출하면 안 됩니다.",
    action: "구/권역 aggregate만 표시하고 민감 시설 좌표는 제외합니다.",
  },
  evt_low_trust_report_001: {
    summary: "미확인 현장 보고가 12-1 예측 분기 시간과 충돌합니다.",
    why: "사람 보고는 중요하지만 센서 근거와 가능성 제약을 함께 봐야 합니다.",
    action: "반박 가능 근거로 보존하되 confirmed/predicted 상태를 덮어쓰지 않습니다.",
  },
  evt_osint_context_001: {
    summary: "공개 출처 advisory가 해당 회랑의 감시 우선순위를 높입니다.",
    why: "OSINT는 증거가 아니라 맥락입니다. 센서 근거와 결합될 때 가치가 커집니다.",
    action: "맥락 근거로만 붙이고, 센서 corroboration 없이는 격상하지 않습니다.",
  },
  evt_composite_dark_vessel_review_001: {
    summary: "부대 간헐 접속, 기상 악화, 통신 저하, 지원 경로 불확실성이 동시에 수렴합니다.",
    why: "저대역 상황에서 하나만 보낼 수 있다면 가장 보존 가치가 큰 지휘연속성 카드입니다.",
    action: "복합 S-DOT 카드를 먼저 보내고 원본 지도/건물/맥락 데이터는 큐에 보관합니다.",
  },
  evt_unit_isolated_river1: {
    summary: "12-1이 간헐 접속 상태로 전환되어 지휘부에는 로컬 COP 일부만 보입니다.",
    why: "지휘부는 마지막 확인 위치를 실시간 사실처럼 다루면 안 되며, 불확실성 있는 예측 COP로 전환해야 합니다.",
    action: "지휘 의도와 핵심 지원 패킷만 우선 전송하고 로컬 이벤트 로그는 재연결 큐에 둡니다.",
  },
  evt_unit_isolated_alpha1: {
    summary: "12-1이 간헐 접속 상태로 전환되어 지휘부에는 로컬 COP 일부만 보입니다.",
    why: "마지막 확인 위치를 실시간 사실처럼 다루면 안 되며, 불확실성 있는 branch scenario로 전환해야 합니다.",
    action: "지휘 의도와 핵심 지원 패킷만 우선 전송하고 로컬 이벤트 로그는 재연결 큐에 둡니다.",
  },
  evt_support_request_medical_power: {
    summary: "12-1은 다음 접속창 전까지 의료 standby와 전력 연장이 필요합니다.",
    why: "전력 고갈은 이동보다 먼저 로컬 COP와 S-DOT outbox를 끊을 수 있습니다.",
    action: "Medic-2와 Comms Relay-3를 우선 지원 옵션으로 정렬하고 접속창은 readiness/route 패킷에 배정합니다.",
  },
  evt_civil_bearer_candidate_bridge7: {
    summary: "서울 민간/공공 통신 aggregate는 emergency bearer 후보이지만 자동으로 사용할 수 있는 자산은 아닙니다.",
    why: "한국의 촘촘한 인프라도 법적 권한, 인증, 전력, 백홀, 보안 조건이 맞아야만 후보 bearer가 됩니다.",
    action: "승인 필요 후보로 표시하고 접근 가능하다고 가정하지 않습니다.",
  },
  evt_civil_bearer_candidate_han: {
    summary: "한강 통신 aggregate는 emergency bearer 후보이지만 자동으로 사용할 수 있는 자산은 아닙니다.",
    why: "한국의 촘촘한 인프라도 법적 권한, 인증, 전력, 백홀, 보안, 혼잡 조건이 맞아야만 후보 bearer가 됩니다.",
    action: "승인형 opportunistic bearer 후보로 표시하고 접근 가능하다고 가정하지 않습니다.",
  },
  evt_rejoin_window_predicted: {
    summary: "12-1 예측 분기 회랑 근처에서 다음 90초 접속창이 예상됩니다.",
    why: "짧은 접속창에서는 어떤 S-DOT 큐를 먼저 보낼지 미리 결정해야 합니다.",
    action: "지휘 의도 수신확인, readiness snapshot, 지원요청을 낮은 우선순위 근거보다 먼저 보냅니다.",
  },
  evt_priority_brief_urban_continuity: {
    summary: "12-1 간헐 접속, 경로 불확실성, 공공 의료 맥락, 후보 bearer 상태가 동시에 수렴합니다.",
    why: "저대역 상황에서 하나만 보낼 수 있다면 가장 보존 가치가 큰 지휘연속성 카드입니다.",
    action: "복합 S-DOT 카드를 먼저 보내고 원본 지도/건물/맥락 데이터는 큐에 보관합니다.",
  },
};

const OBS_CLAIM_KO = {
  obs_weather_001: "강우와 시정 저하가 Mapo/Yeouido 도하 경로의 이동 위험을 높입니다.",
  obs_osint_001: "공개 advisory가 CBD 주변 혼잡과 응급 접근 압박을 언급합니다.",
  obs_network_001: "서울 도심 링크 품질이 시맨틱 요약 기준 아래로 떨어졌습니다.",
  obs_operator_lowtrust_001: "미확인 현장 보고가 12-1 예측 분기 시간과 충돌해 contested 상태로 유지됩니다.",
  obs_unit_alpha1_readiness: "12-1이 간헐 접속 상태로 전환되었습니다. 전력 42%, 로컬 COP 캐시 유지, 의료지원 우선순위 상승.",
  obs_intent_packet_001: "지휘 의도 패킷은 민간 보호, 로컬 상황 인식, 의료 readiness, 핵심 통신 복구를 우선합니다.",
  obs_civil_bearer_han: "한강 통신 aggregate는 후보 bearer지만 법적 권한, 인증, 전력, 백홀, 보안 조건이 미해결입니다.",
  obs_support_route_medic: "Medic-2는 북중앙 의료 회랑 근처로 28분 내 staging 가능합니다.",
  obs_civilian_exposure_cbd: "CBD 건물 밀도와 민간 노출도가 높아 deconfliction과 응급 접근 보존이 필요합니다.",
  obs_medical_capacity_north: "중앙/북동권 병원들이 AOI 근처 공공 의료 지원 맥락을 제공합니다.",
  obs_public_it_power: "공공 IT/전력 의존성은 aggregate continuity 맥락이며 정확한 보호시설 좌표는 제외됩니다.",
  obs_opposing_axis_a: "합성 평가상 후보축 A가 가장 높은 감시 우선순위이며, B/C는 낮은 신뢰도 분기로 유지됩니다.",
};

const PRIORITY_LABEL_KO = {
  medical: "의료",
  civilian_protection: "민간 보호",
  communications: "통신",
  power: "전력",
  local_awareness: "로컬 상황도",
  urban_context: "도심 맥락",
};

const TOKEN_KO = {
  connected: "연결",
  degraded: "저하",
  intermittent: "간헐",
  isolated: "고립",
  delegated: "위임형",
  collaborative: "협업형",
  medical_standby: "의료 대기",
  mobile_relay: "이동 중계",
  power_extension: "전력 연장",
  Route_Blue: "Blue 경로",
  Route_Green: "Green 경로",
  Route_Amber: "Amber 경로",
  pending_contact_window: "접속창 대기",
  active: "활성",
  standby: "대기",
  candidate: "후보",
  degraded_status: "저하",
  down: "단절",
  local_only_status: "로컬",
  unavailable_without_authority: "승인 전 사용불가",
};

const S_DOT_FAMILY_KO = {
  IntentUpdate: "지휘 의도 업데이트",
  ReadinessSnapshot: "전투준비 스냅샷",
  SupportRequest: "지원 요청",
  NetworkStateUpdate: "네트워크 상태 업데이트",
  RejoinWindow: "재연결 창",
};

const S_DOT_VALUE_KO = {
  sdot_001: "통신이 끊겨도 12-1의 현장 판단이 지휘 의도와 어긋나지 않게 합니다.",
  sdot_002: "전력과 의료 상태 악화가 지원 우선순위를 바꾸는지 알려줍니다.",
  sdot_003: "Medic-2, Comms Relay-3, Power Pack A의 지원 순위화를 트리거합니다.",
  sdot_004: "한강 통신 aggregate를 승인 필요 후보 bearer로 식별합니다.",
  sdot_005: "90초 접속창 동안 어떤 큐를 먼저 보낼지 결정합니다.",
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
    send: "전송",
    defer: "보류",
    drop: "폐기",
    hold_local: "로컬",
  }[decision] || decision.toUpperCase();
}

function modeLabel(key) {
  return MODE_LABEL_KO[key] || state.dataset.network_modes[key]?.label || key;
}

function modeDescription(key) {
  return MODE_DESC_KO[key] || state.dataset.network_modes[key]?.description || "";
}

function eventLabel(eventOrType) {
  const type = typeof eventOrType === "string" ? eventOrType : eventOrType.event_type;
  return EVENT_TYPE_KO[type] || type;
}

function eventSummary(event) {
  return EVENT_COPY_KO[event.event_id]?.summary || event.summary;
}

function eventWhy(event) {
  return EVENT_COPY_KO[event.event_id]?.why || event.why_it_matters;
}

function eventAction(event) {
  return EVENT_COPY_KO[event.event_id]?.action || event.recommended_action;
}

function observationClaim(obs) {
  return OBS_CLAIM_KO[obs.observation_id] || obs.claim;
}

function tokenKo(value) {
  if (value == null) return "확인 필요";
  const key = String(value).replaceAll(" ", "_");
  return TOKEN_KO[key] || TOKEN_KO[`${key}_status`] || String(value).replaceAll("_", " ");
}

function severityKo(value) {
  return {
    critical: "긴급",
    high: "높음",
    medium: "중간",
    low: "낮음",
  }[value] || value;
}

function reviewStatusKo(value) {
  return {
    needs_analyst_review: "분석관 검토",
    context_only: "맥락 참고",
  }[value] || tokenKo(value);
}

function priorityKeyKo(key) {
  return PRIORITY_LABEL_KO[key] || key.replaceAll("_", " ");
}

function routeNameKo(routeName) {
  return TOKEN_KO[String(routeName || "").replaceAll(" ", "_")] || routeName;
}

function supportReasonKo(option) {
  return {
    support_medic_2: "의료 대응력이 가장 높고 경로 위험이 허용 범위이며 추가 통신 승인 의존도가 낮습니다.",
    support_comms_relay_3: "통신 복구가 가장 빠르지만 기상과 백홀 불확실성이 신뢰도를 낮춥니다.",
    support_power_pack_a: "지속시간 확보에는 유용하지만 의료·통신 복구보다 긴급도는 낮습니다.",
  }[option.support_id] || option.why_ranked;
}

function severityColor(event) {
  if (event.severity === "critical") return "#bd2d2a";
  if (event.severity === "high") return "#b86b00";
  if (event.severity === "medium") return "#2f67b1";
  return "#277846";
}

function topAdversaryRoute() {
  const routes = state.dataset.adversary_assessment?.routes || [];
  return [...routes].sort((a, b) => Number(b.likelihood || 0) - Number(a.likelihood || 0))[0];
}

function unitStateClass(unit) {
  return String(unit.comm_state || "unknown").replaceAll("_", "-");
}

function unitColor(unit) {
  return {
    connected: "#2f9d62",
    degraded: "#2f67b1",
    intermittent: "#f1c84b",
    isolated: "#bd2d2a",
  }[unit.comm_state] || "#6c7a76";
}

function supportMarkerCode(option) {
  return {
    support_medic_2: "M2",
    support_comms_relay_3: "R3",
    support_power_pack_a: "P",
  }[option.support_id] || "S";
}

function routeColor(route) {
  if (route.route_id?.includes("blue")) return "#2f67b1";
  if (route.route_id?.includes("green")) return "#087f7a";
  if (route.route_id?.includes("amber")) return "#b86b00";
  return "#6c7a76";
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
  if (!terms.includes(state.glossaryTerm)) state.glossaryTerm = terms[0] || "S-DOT";
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

function renderTopbar() {
  const routing = getRouting();
  const metrics = routing.metrics;
  $("topbarMetrics").innerHTML = `
    <div class="metric-tile"><span class="metric-label">전송 이벤트</span><span class="metric-value">${metrics.events_sent}/${metrics.events_total}</span></div>
    <div class="metric-tile"><span class="metric-label">절감률</span><span class="metric-value">${metrics.bytes_saved_pct_vs_full_feed}%</span></div>
    <div class="metric-tile"><span class="metric-label">시맨틱 용량</span><span class="metric-value">${fmtBytes(metrics.semantic_bytes_sent)}</span></div>
  `;
}

function renderObjectiveBanner() {
  const objective = state.dataset.operation_objective;
  const topRoute = topAdversaryRoute();
  const element = $("objectiveBanner");
  if (!objective || !element) return;
  const focus = (objective.decision_focus || [])
    .slice(0, 4)
    .map((item) => `<span class="objective-chip">${item}</span>`)
    .join("");
  const routeCopy = topRoute
    ? `<span>최우선 감시축</span><strong>${topRoute.axis_code} · ${pct(topRoute.likelihood)}</strong><small>신뢰도 ${pct(topRoute.confidence)}</small>`
    : `<span>최우선 감시축</span><strong>확인 필요</strong><small>합성 분기 없음</small>`;
  element.innerHTML = `
    <div class="objective-main">
      <p class="panel-kicker">현 작전 목표</p>
      <h2>${objective.display_name}</h2>
      <p>${objective.primary_objective}</p>
    </div>
    <div class="objective-focus" aria-label="판단 초점">${focus}</div>
    <div class="objective-axis">${routeCopy}</div>
  `;
}

function renderSystemClock() {
  const now = new Date();
  $("systemClock").innerHTML = `
    <span>OPERATION TIME</span>
    <strong>${now.toLocaleString("ko-KR", {
      timeZone: "Asia/Seoul",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
  })} KST</strong>
  `;
}

function renderModes() {
  const modes = Object.entries(state.dataset.network_modes);
  $("modeButtons").innerHTML = modes.map(([key, mode]) => `
    <button class="mode-button ${state.mode === key ? "active" : ""}" data-mode="${key}" type="button">
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
  const mode = state.dataset.network_modes[state.mode];
  const latency = mode.latency_ms == null ? "링크 단절" : `${mode.latency_ms} ms`;
  $("modeSummary").innerHTML = `<strong>${modeLabel(state.mode)}</strong><br>${modeDescription(state.mode)}<br>${mode.bandwidth_kbps} kbps · ${latency} · 패킷 손실 ${mode.packet_loss_pct}%`;
}

function renderDataReadiness() {
  const mockSources = state.dataset.source_catalog.length;
  const eventCount = state.dataset.semantic_events.length;
  const modeCount = Object.keys(state.dataset.network_modes).length;
  const unitCount = state.dataset.unit_nodes?.length || 0;
  const supportCount = state.dataset.support_options?.length || 0;
  const cards = DATA_API_READINESS.map((item) => `
    <article class="readiness-card ${item.status}">
      <span class="readiness-status">${item.status}</span>
      <strong>${item.label}</strong>
      <p>${item.sources}</p>
      <span>${item.note}</span>
    </article>
  `).join("");
  $("dataReadiness").innerHTML = `
    <article class="readiness-card summary">
      <span class="readiness-status">데모</span>
      <strong>${eventCount}개 이벤트 · ${unitCount}개 합성 부대 · ${supportCount}개 지원 옵션</strong>
      <p>${mockSources}개 소스군 · ${modeCount}개 DDIL 모드.</p>
      <span>현재 빌드는 합성 부대/자원 데이터와 공개 컨텍스트 API 슬롯을 함께 제공합니다.</span>
    </article>
    ${cards}
  `;
}

function renderMapCommandStrip() {
  const event = getEvent();
  const packet = getPacket();
  const mode = state.dataset.network_modes[state.mode];
  const bundle = getBundle();
  const objective = state.dataset.operation_objective;
  const topRoute = topAdversaryRoute();
  const latency = mode.latency_ms == null ? "링크 단절" : `${mode.latency_ms} ms`;
  $("mapCommandStrip").innerHTML = `
    <div class="map-stat"><span>작전 단계</span><strong>${objective?.current_phase || "확인 필요"}</strong></div>
    <div class="map-stat"><span>감시축</span><strong>${topRoute ? `${topRoute.axis_code} · ${pct(topRoute.likelihood)}` : "확인 필요"}</strong></div>
    <div class="map-stat"><span>선택 이벤트</span><strong>${eventLabel(event)}</strong></div>
    <div class="map-stat"><span>링크</span><strong>${mode.bandwidth_kbps} kbps · ${latency}</strong></div>
    <div class="map-stat"><span>전송 판단</span><strong>${decisionLabel(packet.decision)}</strong></div>
  `;
  $("mapHud").innerHTML = `
    <div><strong>목표</strong><span>${objective?.display_name || state.dataset.scenario.aoi.name}</span></div>
    <div><strong>모드</strong><span>${modeLabel(state.mode)}</span></div>
    <div><strong>신뢰도</strong><span>${pct(bundle.confidence)} · refs ${bundle.evidence_refs.length}</span></div>
    <div><strong>화면</strong><span>훈련/합성 뷰</span></div>
  `;
  $("selectedDecision").className = `status-pill ${packet.decision}`;
  $("selectedDecision").textContent = decisionLabel(packet.decision);
}

function getMapBounds() {
  return state.dataset.scenario?.aoi?.bounds || {
    lat_min: 37.43,
    lat_max: 37.69,
    lon_min: 126.78,
    lon_max: 127.16,
  };
}

function leafletBounds() {
  const bounds = getMapBounds();
  return [
    [bounds.lat_min, bounds.lon_min],
    [bounds.lat_max, bounds.lon_max],
  ];
}

function fitAoi() {
  if (!mapState.map) return;
  mapState.map.fitBounds(leafletBounds(), { padding: [18, 18] });
}

function markerIcon(kind, options = {}) {
  const selected = options.selected ? "is-selected" : "";
  const severity = options.severity || "";
  const stateClass = options.state ? String(options.state).replaceAll("_", "-") : "";
  const label = options.label ? `<b>${options.label}</b>` : "";
  return L.divIcon({
    className: "",
    html: `<span class="leaflet-map-marker ${kind} ${severity} ${stateClass} ${selected}">${label}</span>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -14],
  });
}

function initMap() {
  const mapElement = $("copMap");
  if (!mapElement) return false;
  if (!window.L) {
    mapElement.innerHTML = `<div class="map-unavailable">Leaflet 지도 라이브러리를 불러오지 못했습니다. 네트워크 연결을 확인해주세요.</div>`;
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

  mapState.legend = L.control({ position: "bottomleft" });
  mapState.legend.onAdd = () => {
    const div = L.DomUtil.create("div", "leaflet-map-legend");
    div.innerHTML = `
      <div><span class="legend-dot event"></span>시맨틱 이벤트</div>
      <div><span class="legend-dot axis"></span>상대 후보축(합성)</div>
      <div><span class="legend-dot unit"></span>합성 부대 코드</div>
      <div><span class="legend-dot isolated"></span>고립/간헐 펄스</div>
      <div><span class="legend-dot support"></span>지원 옵션</div>
      <div><span class="legend-dot comms"></span>후보 bearer</div>
      <div><span class="legend-dot medical"></span>공공 의료</div>
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

function bindPopupAndSelect(layer, title, copy, eventId = null) {
  layer.bindPopup(`
    <p class="map-popup-title">${title}</p>
    <p class="map-popup-copy">${copy || ""}</p>
  `);
  if (eventId) {
    layer.on("click", () => {
      state.selectedEventId = eventId;
      renderAll();
    });
  }
  return layer;
}

function buildingStyle(feature) {
  const buildingClass = feature.properties?.building_class;
  const palette = {
    residential: { color: "#a86711", fillColor: "#f0c96d" },
    commercial: { color: "#1d64a8", fillColor: "#9cc5ec" },
    industrial: { color: "#6f559d", fillColor: "#c5b3e3" },
    public_or_civic: { color: "#256f58", fillColor: "#91cbb8" },
    other_building: { color: "#6f766f", fillColor: "#cfd8d2" },
  };
  const colors = palette[buildingClass] || palette.other_building;
  return {
    color: colors.color,
    weight: 1,
    opacity: 0.58,
    fillColor: colors.fillColor,
    fillOpacity: state.mode === "full_sync" ? 0.22 : 0.12,
  };
}

function renderSeoulContextLayers() {
  const ctx = state.dataset.korea_civil_infra_context || {};
  const layers = ctx.layers || {};

  const buildingGroup = addGroup("buildings");
  const footprints = buildingFootprints.features || [];
  if (footprints.length) {
    L.geoJSON(footprints, {
      style: buildingStyle,
      onEachFeature: (feature, layer) => {
        const props = feature.properties || {};
        const label = props.name || props.aoi_label || props.id || "공개 건물 footprint";
        layer.bindPopup(`
          <p class="map-popup-title">${label}</p>
          <p class="map-popup-copy">공개 건물 footprint · 민간 노출/이동 제약 맥락으로만 사용</p>
        `);
      },
    }).addTo(buildingGroup);
  }

  const exposureGroup = addGroup("exposure");
  (layers.building_exposure_cells || []).forEach((cell) => {
    L.circle([cell.lat, cell.lon], {
      radius: Number(cell.radius_km || 2) * 1000,
      color: "#a86711",
      weight: 1.5,
      fillColor: "#e8b64d",
      fillOpacity: 0.12 + Number(cell.density || 0.5) * 0.12,
    })
      .bindPopup(`<p class="map-popup-title">${cell.label}</p><p class="map-popup-copy">민간 노출: ${cell.civilian_exposure} · 이동 제약: ${cell.mobility_constraint}</p>`)
      .addTo(exposureGroup);
  });

  const commsGroup = addGroup("civilCommsContext");
  (layers.communications_context_cells || []).forEach((cell) => {
    L.circle([cell.lat, cell.lon], {
      radius: Number(cell.radius_km || 4) * 1000,
      color: "#1d64a8",
      weight: 2,
      dashArray: "8 8",
      fillColor: "#1d64a8",
      fillOpacity: 0.05,
    })
      .bindPopup(`<p class="map-popup-title">${cell.label}</p><p class="map-popup-copy">${cell.note || "coarse communications context only"}</p>`)
      .addTo(commsGroup);
  });

  const medicalGroup = addGroup("medical");
  (layers.medical_facilities || []).forEach((item) => {
    L.marker([item.lat, item.lon], {
      icon: markerIcon("medical"),
      keyboard: true,
      title: item.name,
    })
      .bindPopup(`<p class="map-popup-title">${item.name}</p><p class="map-popup-copy">${item.role}</p>`)
      .addTo(medicalGroup);
  });

  const aggregateGroup = addGroup("aggregates");
  (layers.power_it_aggregates || []).forEach((item) => {
    L.marker([item.lat, item.lon], {
      icon: markerIcon("aggregate"),
      keyboard: true,
      title: item.label,
    })
      .bindPopup(`<p class="map-popup-title">${item.label}</p><p class="map-popup-copy">${item.safe_use}</p>`)
      .addTo(aggregateGroup);
  });
}

function renderAdversaryRoutes(group) {
  const assessment = state.dataset.adversary_assessment;
  if (!assessment?.routes?.length) return;
  assessment.routes.forEach((route) => {
    const isPrimary = route.status === "watch";
    const routeClass = `opp-axis ${route.status || "branch"}`;
    const line = L.polyline(route.points, {
      color: isPrimary ? "#bd2d2a" : "#b86b00",
      weight: isPrimary ? 6 : 4,
      opacity: isPrimary ? 0.82 : 0.56,
      dashArray: isPrimary ? "14 10" : "8 12",
      className: routeClass,
    });
    line
      .bindPopup(`
        <p class="map-popup-title">${route.display_name}</p>
        <p class="map-popup-copy">합성 후보축 · 가능성 ${pct(route.likelihood)} · 신뢰도 ${pct(route.confidence)}<br>${route.why}</p>
      `)
      .addTo(group);
    const labelPoint = route.points[Math.min(1, route.points.length - 1)];
    L.marker(labelPoint, {
      icon: markerIcon("axis-label", { label: `${route.axis_code} ${Math.round(route.likelihood * 100)}` }),
      title: route.display_name,
      zIndexOffset: 850,
    })
      .bindPopup(`<p class="map-popup-title">${route.display_name}</p><p class="map-popup-copy">${assessment.safety_note}</p>`)
      .addTo(group);
  });
}

function renderOperationalLayers() {
  const adversaryGroup = addGroup("adversary");
  renderAdversaryRoutes(adversaryGroup);

  const unitsGroup = addGroup("units");
  (state.dataset.unit_nodes || []).forEach((unit) => {
    const confirmed = [unit.last_confirmed.lat, unit.last_confirmed.lon];
    const predicted = [unit.predicted_state.lat, unit.predicted_state.lon];
    L.polyline([confirmed, predicted], {
      color: unitColor(unit),
      weight: 3,
      dashArray: "8 8",
      opacity: 0.9,
      className: `unit-branch-line ${unitStateClass(unit)}`,
    }).addTo(unitsGroup);
    L.circle(predicted, {
      radius: Number(unit.predicted_state.uncertainty_km || 1) * 1000,
      color: unitColor(unit),
      fillColor: unitColor(unit),
      fillOpacity: 0.12,
      weight: 2,
      dashArray: "10 8",
    }).addTo(unitsGroup);
    L.marker(confirmed, {
      icon: markerIcon("unit-confirmed", { label: unit.unit_code, state: unit.comm_state }),
      title: `${unit.display_name} 최종확인`,
    })
      .bindPopup(`<p class="map-popup-title">${unit.display_name} 최종확인</p><p class="map-popup-copy">${unit.last_confirmed.time} · ${tokenKo(unit.comm_state)} · 합성 부대 상태</p>`)
      .addTo(unitsGroup);
    L.marker(predicted, {
      icon: markerIcon("unit-predicted", { label: unit.unit_code, state: unit.comm_state }),
      title: `${unit.display_name} 예측`,
      zIndexOffset: 900,
    })
      .bindPopup(`<p class="map-popup-title">${unit.display_name} 예측 분기</p><p class="map-popup-copy">상태 ${tokenKo(unit.comm_state)} · 신뢰도 ${pct(unit.predicted_state.confidence)} · 불확실성 ${unit.predicted_state.uncertainty_km} km</p>`)
      .addTo(unitsGroup);
  });

  const supportGroup = addGroup("support");
  (state.dataset.support_options || []).forEach((support) => {
    L.marker([support.lat, support.lon], {
      icon: markerIcon("support", { label: supportMarkerCode(support) }),
      title: support.display_name,
    })
      .bindPopup(`<p class="map-popup-title">${support.display_name}</p><p class="map-popup-copy">${tokenKo(support.support_type)} · ${routeNameKo(support.route_name)} · 예상 ${support.eta_minutes}분<br>${support.supports_objective || ""}</p>`)
      .addTo(supportGroup);
  });

  const commsGroup = addGroup("bearers");
  (state.dataset.civil_comms_assets || []).forEach((asset) => {
    L.marker([asset.lat, asset.lon], {
      icon: markerIcon("comms"),
      title: asset.display_name,
    })
      .bindPopup(`<p class="map-popup-title">${asset.display_name}</p><p class="map-popup-copy">${asset.bearer_type} · ${tokenKo(asset.legal_status)}</p>`)
      .addTo(commsGroup);
  });

  const routeGroup = addGroup("routes");
  (state.dataset.urban_routes || []).forEach((route) => {
    L.polyline(route.points, {
      color: routeColor(route),
      weight: 4,
      opacity: 0.64,
      className: "support-route-line",
    })
      .bindPopup(`<p class="map-popup-title">${route.label}</p><p class="map-popup-copy">합성 지원 경로 · risk ${Math.round(route.risk * 100)}</p>`)
      .addTo(routeGroup);
  });

  const eventGroup = addGroup("events");
  (state.dataset.semantic_events || []).forEach((event) => {
    const selected = event.event_id === state.selectedEventId;
    const severityClass = event.severity === "critical" ? "critical" : event.severity === "high" ? "high" : "medium";
    const marker = L.marker([event.location.lat, event.location.lon], {
      icon: markerIcon("event", { selected, severity: severityClass }),
      keyboard: true,
      zIndexOffset: selected ? 1200 : 1000,
      title: eventLabel(event),
    });
    bindPopupAndSelect(marker, eventLabel(event), eventSummary(event), event.event_id).addTo(eventGroup);
    if (selected) {
      marker.bindTooltip(eventLabel(event), { permanent: true, direction: "top", className: "map-tooltip" });
    }
  });
}

function renderMap() {
  if (!initMap()) return;
  clearMapLayers();
  renderSeoulContextLayers();
  renderOperationalLayers();
  setTimeout(() => {
    if (mapState.map) {
      mapState.map.invalidateSize();
      fitAoi();
    }
  }, 0);
}

function renderEventList() {
  const sorted = [...state.dataset.semantic_events].sort((a, b) => b.priority - a.priority);
  $("eventList").innerHTML = sorted.map((event) => {
    const packet = getPacket(event.event_id);
    const terms = eventTerms(event).slice(0, 3).map((term) => `<span class="event-term">${term}</span>`).join("");
    return `
      <button class="event-button ${event.event_id === state.selectedEventId ? "active" : ""}" data-event-id="${event.event_id}" type="button">
        <span class="event-button-top">
          <span class="event-type">${eventLabel(event)} · ${(event.priority * 100).toFixed(0)}</span>
          <span class="status-pill ${packet.decision}">${decisionLabel(packet.decision)}</span>
        </span>
        <span class="event-summary">${eventSummary(event)}</span>
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
  $("evidenceTitle").textContent = eventLabel(event);
  $("reviewStatus").textContent = reviewStatusKo(bundle.review_status);
  const obsItems = bundle.evidence_refs.map((ref) => {
    const obs = getObservation(ref);
    const term = SENSOR_TERM_MAP[obs.sensor_type];
    const sensor = term ? renderTermButton(term) : `<strong>${obs.sensor_type}</strong>`;
    return `
      <div class="evidence-item">
        <code>${obs.observation_id}</code><br>
        <strong>${obs.source_id}</strong> · ${sensor}<br>
        ${observationClaim(obs)}<br>
        <span class="muted-text">raw ref: ${obs.raw_ref}</span>
      </div>
    `;
  }).join("");
  $("evidenceBody").innerHTML = `
    <div class="fact-grid">
      <div class="fact"><b>우선순위</b><span>${(event.priority * 100).toFixed(0)}</span></div>
      <div class="fact"><b>심각도</b><span>${severityKo(event.severity)}</span></div>
      <div class="fact"><b>분석 신뢰도</b><span>${pct(bundle.confidence)}</span></div>
      <div class="fact"><b>출처 신뢰도</b><span>${pct(bundle.trust_score)}</span></div>
    </div>
    <h3>${eventSummary(event)}</h3>
    <p>${eventWhy(event)}</p>
    <p><strong>권고:</strong> ${eventAction(event)}</p>
    <div class="bar-row">
      <div class="bar-label"><span>분석 신뢰도</span><span>${pct(bundle.confidence)}</span></div>
      <div class="bar"><span style="width:${bundle.confidence * 100}%"></span></div>
    </div>
    <div class="bar-row">
      <div class="bar-label"><span>출처 신뢰도</span><span>${pct(bundle.trust_score)}</span></div>
      <div class="bar"><span style="width:${bundle.trust_score * 100}%"></span></div>
    </div>
    <h3>근거 refs</h3>
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
      <div class="fact"><b>원본 feed 크기</b><span>${fmtBytes(raw)}</span></div>
      <div class="fact"><b>전송된 시맨틱</b><span>${fmtBytes(sem)}</span></div>
      <div class="fact"><b>절감률</b><span>${metrics.bytes_saved_pct_vs_full_feed}%</span></div>
      <div class="fact"><b>생존율</b><span>${pct(metrics.message_survival_rate)}</span></div>
    </div>
    <div class="bar-row">
      <div class="bar-label"><span>시맨틱 payload vs 원본 feed</span><span>${fmtBytes(sem)} / ${fmtBytes(raw)}</span></div>
      <div class="bar"><span style="width:${semWidth}%"></span></div>
    </div>
  `;
  const eventById = Object.fromEntries(state.dataset.semantic_events.map((event) => [event.event_id, event]));
  $("packetTable").innerHTML = routing.packets.map((packet) => {
    const event = eventById[packet.event_id];
    return `
      <div class="packet-row">
        <span>${eventLabel(event)}</span>
        <span class="status-pill ${packet.decision}">${decisionLabel(packet.decision)}</span>
      </div>
    `;
  }).join("");
}

function renderBriefing() {
  const briefing = state.dataset.briefing;
  const claimKo = [
    "12-1은 간헐 접속 상태이므로 실시간 추적이 아니라 예측 분기 시나리오로 표시해야 합니다.",
    "지휘 의도는 민간 보호, 의료 readiness, 로컬 상황 인식, 통신 복구를 우선합니다.",
    "상대 움직임은 실제 추적이 아니라 합성 확률 분기이며, 현재 후보축 A가 감시 우선순위입니다.",
    "민간/공공 통신 aggregate는 법적 승인, 인증, 전력, 백홀, 혼잡, 보안 조건이 맞을 때만 후보 bearer입니다.",
    "합성 서울 시나리오에서 Medic-2가 가장 높은 지원 옵션입니다.",
    "CBD 고밀도 건물/민간 노출 정보는 보호·우회·deconfliction 맥락으로만 사용합니다.",
    "공공 IT/전력 의존성은 aggregate continuity 맥락이며 정확한 보호시설 좌표는 제외합니다.",
    "기상과 통신 저하는 원본 지도/건물/context feed 기반 확인을 어렵게 합니다.",
  ];
  const claims = briefing.grounded_claims.map((item, index) => `
    <div class="claim-item">
      ${claimKo[index] || item.claim}<br>
      ${item.evidence_refs.map((ref) => `<code>${ref}</code>`).join(" ")}
    </div>
  `).join("");
  $("briefingBody").innerHTML = `
    <div class="briefing-body-grid">
      <div class="briefing-summary">
        <h3>통신이 끊겨도 지휘 의도, 최소 상황도, 자원 상태, 예측 불확실성, 재연결 감사는 유지되어야 합니다.</h3>
        <p>지휘 의도 수신확인, readiness snapshot, 지원 요청을 낮은 우선순위 근거보다 먼저 보냅니다. 원본 지도·건물·공공 인프라 맥락 데이터는 재연결 후 동기화하고, 모든 부대·자원 데이터는 공개 데모에서 합성으로 유지합니다.</p>
        <p class="muted-text">S-DOT은 Semantic Data On Tactical-network라는 해커톤 개념명이며, 기존 SDoT 제품/표준과 구분됩니다.</p>
      </div>
      <div class="claims-list">${claims}</div>
    </div>
  `;
}

function renderMissionContinuity() {
  const intent = state.dataset.mission_intent;
  const units = state.dataset.unit_nodes || [];
  const supportOptions = [...(state.dataset.support_options || [])].sort((a, b) => b.support_score - a.support_score);
  const messages = [...(state.dataset.sdot_messages || [])].sort((a, b) => b.priority - a.priority);
  const pace = state.dataset.pace_bearer_ladder || [];
  const audit = state.dataset.rejoin_audit;
  if (!intent || !$("intentBody")) return;

  const weightRows = Object.entries(intent.priority_weights).map(([key, value]) => `
    <div class="mini-bar-row">
      <span>${priorityKeyKo(key)}</span>
      <b>${Math.round(value * 100)}</b>
      <i><em style="width:${value * 100}%"></em></i>
    </div>
  `).join("");
  $("intentBody").innerHTML = `
    <p class="mission-copy">통신이 끊겨도 로컬 상황 인식, 부대 지속성, 의료 readiness, 핵심 통신 복구 우선순위를 유지합니다.</p>
    <div class="mini-bar-list">${weightRows}</div>
    <div class="compact-tags">
      <span>실제 부대 데이터 미사용</span>
      <span>공개 데이터는 맥락으로만 사용</span>
      <span>민간 인프라는 후보 bearer</span>
      <span>지원 결정은 사람 승인 필요</span>
    </div>
  `;

  $("unitBody").innerHTML = units.map((unit) => `
    <article class="unit-card">
      <div class="unit-card-head">
        <strong>${unit.display_name}</strong>
        <span class="status-pill muted">${tokenKo(unit.comm_state)}</span>
      </div>
      <div class="unit-grid">
        <span>C2 모드</span><b>${tokenKo(unit.c2_mode)}</b>
        <span>전력</span><b>${unit.readiness.power_pct}%</b>
        <span>예측 신뢰도</span><b>${pct(unit.predicted_state.confidence)}</b>
        <span>불확실성</span><b>${unit.predicted_state.uncertainty_km} km</b>
      </div>
      <p>${unit.display_name}은 실시간 추적 대상이 아니라 마지막 확인 상태 기반의 branch scenario로 표시됩니다.</p>
      <div class="branch-list">
        ${(unit.branch_scenarios || []).map((branch) => `
          <div class="branch-row">
            <span>${branch.label}</span>
            <b>${Math.round(branch.probability * 100)}%</b>
          </div>
        `).join("")}
      </div>
    </article>
  `).join("");

  $("supportBody").innerHTML = supportOptions.map((option, index) => `
    <article class="support-option ${index === 0 ? "top" : ""}">
      <div class="support-rank">${index + 1}</div>
      <div>
        <strong>${option.display_name}</strong>
        <span>${tokenKo(option.support_type)} · ${routeNameKo(option.route_name)} · 예상 ${option.eta_minutes}분</span>
        <p>${supportReasonKo(option)}</p>
      </div>
      <b>${Math.round(option.support_score * 100)}</b>
    </article>
  `).join("");

  if ($("paceBody")) {
    $("paceBody").innerHTML = `
      <div class="pace-list">
        ${pace.map((item) => {
          const status = item.availability_by_mode?.[state.mode] || "unknown";
          return `
            <article class="pace-item">
              <div class="pace-letter">${item.pace}</div>
              <div>
                <strong>${item.label}</strong>
                <span>${item.role}</span>
                <small>${item.risk_note}</small>
              </div>
              <b class="pace-state">${tokenKo(status)}</b>
            </article>
          `;
        }).join("")}
      </div>
    `;
  }

  $("sdotBody").innerHTML = `
    <div class="sdot-list">
      ${messages.map((message) => {
        const packet = getPacket(message.event_id);
        const compression = message.raw_bytes ? Math.round(100 * (1 - message.semantic_bytes / message.raw_bytes)) : 0;
        return `
          <article class="sdot-message">
            <div>
              <strong>${S_DOT_FAMILY_KO[message.family] || message.family}</strong>
              <span>${message.from} -> ${message.to} · ${message.payload_tier}</span>
            </div>
            <span class="status-pill ${packet?.decision || "muted"}">${packet ? decisionLabel(packet.decision) : "QUEUE"}</span>
            <p>${S_DOT_VALUE_KO[message.message_id] || message.decision_value}</p>
            <small>${fmtBytes(message.semantic_bytes)} 시맨틱 · 원본 대비 ${compression}% 축소</small>
          </article>
        `;
      }).join("")}
    </div>
    <div class="rejoin-audit">
      <strong>재연결 감사</strong>
      <span>${tokenKo(audit.status)} · 우선 동기화: ${audit.expected_sync_order.slice(0, 3).join(", ")}</span>
    </div>
  `;
}

function renderAll() {
  renderSystemClock();
  renderTopbar();
  renderObjectiveBanner();
  renderModes();
  renderDataReadiness();
  renderMapCommandStrip();
  renderMap();
  renderEventList();
  renderEvidence();
  renderRouting();
  renderBriefing();
  renderMissionContinuity();
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
  setInterval(renderSystemClock, 1000);
}

boot().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><section class="panel"><div class="panel-heading"><h2>Dataset load failed</h2></div><pre>${String(error)}</pre></section></main>`;
});
