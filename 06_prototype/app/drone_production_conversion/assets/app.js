const data = window.DRONE_PRODUCTION_CONVERSION_DATASET || {};
const factories = data.factory_candidates || [];
const resources = data.resource_candidates || [];
const categories = data.part_categories || {};
const resourceCategories = data.resource_categories || {};
const plans = data.plans || [];
const gridRiskZones = data.grid_risk_zones || [];
const gridDisruptionScenarios = data.grid_disruption_scenarios || [];
const scenarioImpactEvents = data.scenario_impact_events || [];
const frozenOrders = data.frozen_orders || [];
const inTransitShipments = data.in_transit_shipments || [];
const inventoryWip = data.inventory_wip || [];
const rawMaterialCatalog = data.raw_material_catalog || {};
const importPorts = data.import_ports || [];
const foreignMaterialSources = data.foreign_material_sources || [];
const alliedSupplySources = data.allied_supply_sources || [];
const componentCatalog = data.component_catalog || {};
const subcomponentCatalog = data.subcomponent_catalog || {};
const blockadeDemandModel = data.blockade_demand_model || {};
const optimizationResult = window.DRONE_OPTIMIZATION_RESULT_V0_9 || {};
const reconfigurationResult = window.DRONE_RECONFIGURATION_RESULT_V1_0 || {};

const factoryById = Object.fromEntries(factories.map((factory) => [factory.id, factory]));
const resourceById = Object.fromEntries(resources.map((resource) => [resource.id, resource]));
const portById = Object.fromEntries(importPorts.map((port) => [port.id, port]));
const foreignSourceById = Object.fromEntries(foreignMaterialSources.map((source) => [source.id, source]));
const planById = Object.fromEntries(plans.map((plan) => [plan.id, plan]));
const optimizationByScenarioId = Object.fromEntries((optimizationResult.scenarios || []).map((scenario) => [scenario.scenario_id, scenario]));
const reconfigurationByScenarioId = Object.fromEntries((reconfigurationResult.scenarios || []).map((scenario) => [scenario.scenario_id, scenario]));
const inventoryByFactoryId = Object.fromEntries(inventoryWip.filter((row) => row.factory_id).map((row) => [row.factory_id, row]));
const frozenOrdersByFactoryId = frozenOrders.reduce((memo, order) => {
  if (!order.factory_id) return memo;
  if (!memo[order.factory_id]) memo[order.factory_id] = [];
  memo[order.factory_id].push(order);
  return memo;
}, {});
const shipmentsByFactoryId = inTransitShipments.reduce((memo, shipment) => {
  const factoryId = shipment.factory_id || shipment.target_factory_id;
  if (!factoryId) return memo;
  if (!memo[factoryId]) memo[factoryId] = [];
  memo[factoryId].push(shipment);
  return memo;
}, {});

const partCategoryKorean = {
  drone_assembly: {label: "드론 최종 조립", role: "기체 통합, 최종 조립, 비행 점검 후보"},
  flight_stack: {label: "비행제어/전자부품", role: "PCB, 제어기, 통신 전자부품 후보"},
  power: {label: "배터리/전원", role: "배터리팩, 충전기, 전원관리 부품 후보"},
  propulsion: {label: "모터/추진계", role: "모터, 로터, 구동장치 부품 후보"},
  sensor_payload: {label: "센서/카메라", role: "카메라, 광학, 감지 payload 후보"},
  airframe: {label: "기체 프레임/소재", role: "프레임, 사출, 복합재, 브라켓 후보"},
  harness: {label: "하네스/커넥터", role: "배선 하네스, 커넥터, 케이블 조립 후보"},
  qa_packaging: {label: "시험/포장", role: "검사, 계측, 운송 케이스, 포장 후보"},
};

const resourceCategoryKorean = {
  rare_earth_magnet_recovery: {label: "희토류/자석 원료", role: "NdFeB 자석, 자석 적용 장비, 회수 후보"},
  battery_material_recovery: {label: "배터리 소재/셀 회수", role: "폐배터리, 리튬, 전지 소재 수급 후보"},
  metal_electronics_recycling: {label: "도시광산/전자스크랩", role: "PCB, 커넥터, 구리, 비철금속 회수 후보"},
  carbon_composite_supply: {label: "복합재/경량금속 원료", role: "탄소섬유, 복합재, 알루미늄, 재생 플라스틱 후보"},
};

const rawMaterialKorean = {
  ndfeb_magnet_feedstock: {label: "희토류/자석 원료", short_label: "자석 원료"},
  lithium_battery_feedstock: {label: "배터리 소재 원료", short_label: "배터리 소재"},
  copper_electronics_feedstock: {label: "전자부품 금속/구리", short_label: "전자금속"},
  lightweight_airframe_feedstock: {label: "경량 기체 소재", short_label: "기체 소재"},
  optical_sensor_components: {label: "광학/센서 부품", short_label: "광학부품"},
  industrial_polymers_packaging: {label: "포장/폴리머 소재", short_label: "포장소재"},
};

const routeStatusKorean = {
  active: "활성",
  candidate: "후보",
  primary: "주 경로",
  rerouted: "대체 경로",
  fallback: "예비 경로",
  routed: "도로 경로",
  onsite: "현장 배정",
  "final-assembly": "최종조립",
  "import-to-factory": "항만-공장",
  east_sea_preferred: "동해 우선 경로",
  southern_port_link: "남부 항만 경로",
  maritime_corridor_estimate: "해상 경로 추정",
  "resource-reroute": "자원 대체 경로",
  "resource-primary": "자원 주 경로",
};

const mapPresets = {
  trade: {
    buttonId: "presetTrade",
    bounds: [
      [33.6, 124.9],
      [38.5, 137.4],
    ],
  },
  korea: {
    buttonId: "presetKorea",
    bounds: [
      [33.0, 124.5],
      [38.9, 131.2],
    ],
  },
  central: {
    buttonId: "presetCentral",
    bounds: [
      [35.75, 126.0],
      [38.15, 128.1],
    ],
  },
  gyeongsang: {
    buttonId: "presetGyeongsang",
    bounds: [
      [34.5, 127.7],
      [37.45, 130.3],
    ],
  },
};

const missionProfileKorean = {
  short_range_recon_quad: {label: "소모성 FPV", use: "전방 단기 소요"},
  comms_relay_quad: {label: "회수 멀티로터(중형)", use: "중형 회수 운용"},
  light_logistics_quad: {label: "소모성 고정익(대형)", use: "대형 고정익 소요"},
};

const syntheticUnitDemandProfiles = [
  {
    id: "unit_north_isr",
    name: "전방 감시 소요부대 A",
    area: "수도권 북부",
    profile_id: "short_range_recon_quad",
    deadline_day: 2,
    share: 0.34,
    urgency: 0.96,
  },
  {
    id: "unit_east_relay",
    name: "동해 통신중계 소요부대 B",
    area: "동해안 권역",
    profile_id: "comms_relay_quad",
    deadline_day: 3,
    share: 0.42,
    urgency: 0.88,
  },
  {
    id: "unit_central_logistics",
    name: "중부 보급지원 소요부대 C",
    area: "충청 내륙",
    profile_id: "light_logistics_quad",
    deadline_day: 4,
    share: 0.46,
    urgency: 0.82,
  },
  {
    id: "unit_west_isr",
    name: "서해 시설점검 소요부대 D",
    area: "서해안 권역",
    profile_id: "short_range_recon_quad",
    deadline_day: 5,
    share: 0.18,
    urgency: 0.71,
  },
];

const scenarioCaseNarratives = {
  baseline: {
    phase: "D+0 생산전환 발령",
    title: "수요 폭증 대응 기본안",
    operatorFocus: "후보 공장 검증, 모터/추진계 병목 확인, 기존 동결 주문 보호",
    caseSignal: "전시 수요 10,000대/30일이 접수되어 기존 후보망으로 먼저 공급 가능량을 산정",
    uiChange: "지도는 기본 공급망과 원료 유입 경로를 보여주고, 데이터셋 패널은 부족량과 1순위 병목을 표시",
    logicChange: "기존 공장/경로 후보를 유지하면서 부족량 최소화와 낮은 위험 경로를 우선 선택",
    steps: [
      {time: "T+00", label: "수요 접수", detail: "30일 목표 10,000대 기준 BOM/공장/원료 장부 갱신"},
      {time: "T+10", label: "기본 배정", detail: "기존 후보 경로에서 생산 가능량과 부족량 계산"},
      {time: "T+20", label: "병목 확인", detail: "모터/추진계 계열을 1순위 제약으로 표시"},
      {time: "T+30", label: "검증 명령", detail: "후보 공장 capa, QA, 생산 중 물량, 동결 주문 확인"},
    ],
  },
  western_axis_threat: {
    phase: "D+1 서부축 위협 상승",
    title: "서부축 공장/도로 위험 상승 케이스",
    operatorFocus: "위험 회랑 인근 공장 제외, 대체 공장 추가, 운송 중 물량 재검토",
    caseSignal: "서해/수도권 서부 방향의 예측 위험이 올라가 일부 공급 경로가 위험 패널티를 받음",
    uiChange: "지도에 적색 위험 회랑이 나타나고, 재배치 흐름과 추가/제외 공장 숫자가 증가",
    logicChange: "공장/도로 risk score를 올리고 route score를 재계산해 비용이 늘더라도 위험이 낮은 대체 경로를 선택",
    steps: [
      {time: "T+00", label: "위험 신호", detail: "서부축 합성 위협 회랑 활성화"},
      {time: "T+08", label: "노드 영향", detail: "회랑 인근 공장과 경로의 가용성/위험 재평가"},
      {time: "T+18", label: "긴급 재계획", detail: "대체 공장 34개 추가, 31개 제외, 31개 흐름 재배치"},
      {time: "T+30", label: "운영 검토", detail: "동결 주문 19건, 운송 중 물량 14건 사람 검토 카드 생성"},
    ],
  },
  southern_port_disruption: {
    phase: "D+2 남부 항만 차질",
    title: "원료 수입/항만 물류 차질 케이스",
    operatorFocus: "해상 수입 경로, 항만-공장 원료 이동, 최종조립 공장 우선순위 재검토",
    caseSignal: "남부 항만 처리 차질이 발생해 희토류/반도체/전자스크랩 원료 feeder route 위험이 상승",
    uiChange: "해상/항만-공장 경로와 내륙 예비 조립 흐름을 함께 보여주고, 위험 증분을 Plan Delta에 표시",
    logicChange: "항만 및 남부권 feeder route risk를 반영해 원료/부품 경로를 재배정하고 일부 flow만 대체",
    steps: [
      {time: "T+00", label: "항만 스트레스", detail: "southern logistics disruption 시나리오 활성화"},
      {time: "T+09", label: "원료 경로 점검", detail: "수입항-공장 경로와 국내 회수 후보를 함께 비교"},
      {time: "T+19", label: "부분 재배치", detail: "대체 공장 14개 추가, 14개 제외, 4개 flow 재배치"},
      {time: "T+28", label: "명령 검토", detail: "동결 주문 7건, 운송 중 물량 5건 재확인"},
    ],
  },
};

const state = {
  scenarioId: plans[0]?.id || "baseline",
  selectedKind: "",
  selectedFactoryId: "",
  selectedResourceId: "",
  targetDrones: plans[0]?.target_drones || 10000,
  visible: Object.fromEntries(Object.keys(categories).map((key) => [key, true])),
  resourceVisible: Object.fromEntries(Object.keys(resourceCategories).map((key) => [key, true])),
  materialRoutesVisible: true,
  mapPresetId: "korea",
  viewMode: "default",
  scenarioStageIndex: 0,
  factoryScope: "all",
  playbackActive: false,
  opsDetail: {
    open: false,
    kind: "",
    itemId: "",
    side: "left",
    hoverRouteId: "",
    hoverFactoryId: "",
    hoverMaterialId: "",
  },
};

const layerFilterPresets = {
  all: {
    factories: "all",
    resources: "all",
    materialRoutes: true,
  },
  finalAssemblyOnly: {
    factories: ["drone_assembly"],
    resources: [],
    materialRoutes: false,
  },
  portBlockadeIntro: {
    factories: ["drone_assembly"],
    resources: [],
    materialRoutes: true,
  },
  motorBottleneck: {
    factories: ["drone_assembly", "propulsion"],
    resources: ["rare_earth_magnet_recovery"],
    materialRoutes: true,
  },
  coreComponentSupply: {
    factories: ["drone_assembly", "flight_stack", "power", "propulsion"],
    resources: [],
    materialRoutes: false,
  },
  inlandReplacement: {
    factories: ["drone_assembly", "flight_stack", "power", "propulsion", "harness"],
    resources: [],
    materialRoutes: false,
  },
  allSupplyGraph: {
    factories: "all",
    resources: "all",
    materialRoutes: true,
  },
  rawMaterialFeeder: {
    factories: ["drone_assembly", "flight_stack", "propulsion", "power"],
    resources: ["rare_earth_magnet_recovery", "metal_electronics_recycling"],
    materialRoutes: true,
  },
};

const mapState = {
  map: null,
  layerGroup: null,
  flowMarkers: [],
  animationFrame: null,
};

const uiState = {
  controlsReady: false,
  playbackTimer: null,
};

const scenarioStageCache = new Map();
const scenarioFocusContextCache = new WeakMap();
const emptyScenarioSet = new Set();
const emptyScenarioFocusContext = {
  active: false,
  focus: {},
  routeIds: emptyScenarioSet,
  excludedFactoryIds: emptyScenarioSet,
  disabledPortIds: emptyScenarioSet,
  blockedRouteIds: emptyScenarioSet,
  hiddenRouteIds: emptyScenarioSet,
  threatRouteTouchCache: new Map(),
  forcedFactoryIds: emptyScenarioSet,
};

function elementById(id) {
  return document.getElementById(id);
}

function setDrawerOpen(id, open) {
  const drawer = elementById(id);
  if (!drawer) return;
  drawer.classList.toggle("is-open", open);
  drawer.setAttribute("aria-hidden", open ? "false" : "true");
  if (mapState.map) {
    setTimeout(() => mapState.map.invalidateSize(), 180);
  }
}

function closeDetailsDrawer({clearSelection = false} = {}) {
  setDrawerOpen("detailsDrawer", false);
  if (clearSelection) {
    state.selectedKind = "";
    state.selectedFactoryId = "";
    state.selectedResourceId = "";
    renderMap();
  }
}

function openDetailsDrawer() {
  setDrawerOpen("detailsDrawer", false);
}

function setSummaryOpen(open) {
  const panel = elementById("summaryPopover");
  const button = elementById("summaryToggle");
  if (!panel || !button) return;
  panel.hidden = true;
  button.setAttribute("aria-expanded", "false");
}

function setLegendOpen(open) {
  const panel = elementById("mapLegend");
  const button = elementById("mapLegendButton");
  if (!panel || !button) return;
  panel.hidden = !open;
  panel.classList.toggle("is-open", open);
  panel.setAttribute("aria-hidden", open ? "false" : "true");
  button.setAttribute("aria-expanded", open ? "true" : "false");
}

function setOpsModalOpen(open) {
  const modal = elementById("opsModal");
  if (!modal) return;
  modal.hidden = !open;
  modal.classList.toggle("is-open", open);
  modal.setAttribute("aria-hidden", open ? "false" : "true");
}

function openOpsModal(kicker, title, bodyHtml) {
  // Reserved for a future full-report action. The map-first flow uses openOpsSheet().
  elementById("opsModalKicker").textContent = kicker;
  elementById("opsModalTitle").textContent = title;
  elementById("opsModalBody").innerHTML = bodyHtml;
  setOpsModalOpen(true);
}

function closeOpsModal() {
  setOpsModalOpen(false);
}

function opsSideForKind(kind) {
  return kind === "unit" || kind === "procurement" ? "right" : "left";
}

function setOpsSheetOpen(open) {
  const sheet = elementById("opsDetailSheet");
  if (!sheet) return;
  sheet.hidden = !open;
  sheet.classList.toggle("is-open", open);
  sheet.setAttribute("aria-hidden", open ? "false" : "true");
}

function openOpsSheet(kicker, title, bodyHtml, {kind = "", itemId = "", side = opsSideForKind(kind), subtitle = ""} = {}) {
  state.opsDetail = {
    open: true,
    kind,
    itemId,
    side,
    hoverRouteId: "",
    hoverFactoryId: "",
    hoverMaterialId: "",
  };
  const sheet = elementById("opsDetailSheet");
  if (sheet) {
    sheet.dataset.side = side;
    sheet.dataset.kind = kind;
  }
  elementById("opsSheetKicker").textContent = kicker;
  elementById("opsSheetTitle").textContent = title;
  elementById("opsSheetSubtitle").textContent = subtitle || "지도 위 관련 노드와 경로를 함께 강조합니다.";
  elementById("opsSheetBack").hidden = !itemId;
  elementById("opsSheetBody").innerHTML = bodyHtml;
  setOpsSheetOpen(true);
  bindOpsSheetInteractions();
  renderMap();
}

function closeOpsSheet({rerender = true} = {}) {
  state.opsDetail.open = false;
  state.opsDetail.kind = "";
  state.opsDetail.itemId = "";
  state.opsDetail.hoverRouteId = "";
  state.opsDetail.hoverFactoryId = "";
  state.opsDetail.hoverMaterialId = "";
  setOpsSheetOpen(false);
  if (rerender) renderMap();
}

function bindOpsSheetInteractions() {
  elementById("opsSheetBody")?.querySelectorAll("[data-hover-route], [data-hover-factory], [data-hover-material]").forEach((card) => {
    const setHover = () => {
      state.opsDetail.hoverRouteId = card.dataset.hoverRoute || "";
      state.opsDetail.hoverFactoryId = card.dataset.hoverFactory || "";
      state.opsDetail.hoverMaterialId = card.dataset.hoverMaterial || "";
      renderMap();
    };
    const clearHover = () => {
      state.opsDetail.hoverRouteId = "";
      state.opsDetail.hoverFactoryId = "";
      state.opsDetail.hoverMaterialId = "";
      renderMap();
    };
    card.addEventListener("mouseenter", setHover);
    card.addEventListener("focus", setHover);
    card.addEventListener("mouseleave", clearHover);
    card.addEventListener("blur", clearHover);
  });
}

function setupChromeControls() {
  if (uiState.controlsReady) return;
  uiState.controlsReady = true;

  elementById("layerDrawerButton")?.addEventListener("click", () => setDrawerOpen("layerDrawer", true));
  elementById("layerDrawerClose")?.addEventListener("click", () => setDrawerOpen("layerDrawer", false));
  elementById("datasetInfoButton")?.addEventListener("click", () => setDrawerOpen("datasetInfoDrawer", true));
  elementById("datasetInfoClose")?.addEventListener("click", () => setDrawerOpen("datasetInfoDrawer", false));
  elementById("detailsDrawerClose")?.addEventListener("click", () => closeDetailsDrawer({clearSelection: true}));
  elementById("opsModalClose")?.addEventListener("click", closeOpsModal);
  elementById("opsModalBackdrop")?.addEventListener("click", closeOpsModal);
  elementById("opsSheetClose")?.addEventListener("click", () => closeOpsSheet());
  elementById("opsSheetBack")?.addEventListener("click", () => openDashboardModal(state.opsDetail.kind, ""));
  elementById("mapLegendButton")?.addEventListener("click", () => {
    const panel = elementById("mapLegend");
    setLegendOpen(panel?.hidden !== false);
  });
  elementById("mapLegendClose")?.addEventListener("click", () => setLegendOpen(false));
  document.querySelectorAll("[data-factory-scope]").forEach((button) => {
    button.addEventListener("click", () => {
      state.factoryScope = button.dataset.factoryScope || "all";
      renderFactoryScopeControls();
      renderLayerToggles();
      renderMap();
      renderFlowLedger();
    });
  });
  Object.entries(mapPresets).forEach(([presetId, preset]) => {
    elementById(preset.buttonId)?.addEventListener("click", () => applyMapPreset(presetId));
  });
  elementById("summaryToggle")?.addEventListener("click", () => setSummaryOpen(false));
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    setDrawerOpen("layerDrawer", false);
    setDrawerOpen("datasetInfoDrawer", false);
    closeDetailsDrawer({clearSelection: true});
    setSummaryOpen(false);
    setLegendOpen(false);
    closeOpsSheet();
    closeOpsModal();
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fmt(value) {
  return Number(value || 0).toLocaleString("ko-KR");
}

function pct(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function currentPlan() {
  return planById[state.scenarioId] || plans[0] || {};
}

function currentScenarioScale() {
  const plan = currentPlan();
  return Math.max(0.1, Number(state.targetDrones || plan.target_drones || 1) / Number(plan.target_drones || 1));
}

function categoryColor(category) {
  return categories[category]?.color || "#546061";
}

function resourceCategoryColor(category) {
  return resourceCategories[category]?.color || "#4e6b62";
}

function materialColor(materialId) {
  return rawMaterialCatalog[materialId]?.color || "#2f7c8c";
}

const routePalette = {
  part: "#7fb3ff",
  resource: "#2fd0a8",
  maritime: "#77dce8",
  material: "#f0bd5e",
  threat: "#ff5a4f",
  fallback: "#ffb14a",
  blockade: "#a936a8",
};

function routeTypeColor(type) {
  return routePalette[type] || routePalette.part;
}

const koreaStraitBlockade = {
  label: "중국 해상 민병대 대한해협 봉쇄선",
  line: [
    {lat: 33.98, lon: 128.42},
    {lat: 34.18, lon: 128.82},
    {lat: 34.47, lon: 129.05},
    {lat: 34.82, lon: 129.23},
    {lat: 35.18, lon: 129.37},
  ],
  ships: [
    {lat: 34.03, lon: 128.55, angle: 28},
    {lat: 34.18, lon: 128.82, angle: 32},
    {lat: 34.36, lon: 128.98, angle: 38},
    {lat: 34.58, lon: 129.09, angle: 52},
    {lat: 34.82, lon: 129.23, angle: 62},
    {lat: 35.02, lon: 129.31, angle: 70},
    {lat: 35.2, lon: 129.38, angle: 76},
  ],
};

function routeFlowColor(route = {}) {
  if (route.route_type === "maritime_import" || route.material_ids?.length) return routeTypeColor("maritime");
  if (route.route_type === "port_to_factory_material" || route.material_id) return routeTypeColor("material");
  if (route.resource_category) return routeTypeColor("resource");
  return routeTypeColor("part");
}

function materialLabel(materialId, {short = false} = {}) {
  const korean = rawMaterialKorean[materialId];
  if (korean) return korean[short ? "short_label" : "label"] || korean.label;
  const material = rawMaterialCatalog[materialId] || {};
  return material[short ? "short_label" : "label"] || materialId || "material";
}

function partCategoryText(key, category = categories[key] || {}) {
  return partCategoryKorean[key] || {label: category.label || key, role: category.role || "공장 후보"};
}

function resourceCategoryText(key, category = resourceCategories[key] || {}) {
  return resourceCategoryKorean[key] || {label: category.label || key, role: category.role || "원료/자원 후보"};
}

function statusText(value) {
  if (!value) return "검증 대기";
  return routeStatusKorean[value] || String(value).replace(/_/g, " ");
}

function setAllLayerVisibility(checked) {
  Object.keys(state.visible).forEach((key) => {
    state.visible[key] = checked;
  });
  Object.keys(state.resourceVisible).forEach((key) => {
    state.resourceVisible[key] = checked;
  });
  state.materialRoutesVisible = checked;
  renderLayerToggles();
  renderMap();
  renderFlowLedger();
  renderMaterialSupplySummary();
}

function applyKeyVisibility(target, keys) {
  const selected = keys === "all" ? new Set(Object.keys(target)) : new Set(keys || []);
  Object.keys(target).forEach((key) => {
    target[key] = selected.has(key);
  });
}

function applyLayerFilterPreset(presetId = "all", {rerender = false} = {}) {
  const preset = layerFilterPresets[presetId] || layerFilterPresets.finalAssemblyOnly;
  applyKeyVisibility(state.visible, preset.factories);
  applyKeyVisibility(state.resourceVisible, preset.resources);
  state.materialRoutesVisible = Boolean(preset.materialRoutes);
  if (!rerender) return;
  renderLayerToggles();
  renderMap();
  renderFlowLedger();
  renderMaterialSupplySummary();
}

function applyCurrentScenarioLayerPreset({rerender = false} = {}) {
  if (state.viewMode !== "scenario") return;
  const stage = currentScenarioStage();
  applyLayerFilterPreset(stage?.layerPreset || stage?.focus?.layerPreset || "finalAssemblyOnly", {rerender});
}

function updatePresetButtons() {
  Object.entries(mapPresets).forEach(([presetId, preset]) => {
    elementById(preset.buttonId)?.classList.toggle("is-active", state.mapPresetId === presetId);
  });
}

function renderFactoryScopeControls() {
  const counts = factoryScopeCounts();
  elementById("factoryScopeAllCount").textContent = fmt(counts.all);
  elementById("factoryScopeActiveCount").textContent = fmt(counts.active);
  document.querySelectorAll("[data-factory-scope]").forEach((button) => {
    const active = button.dataset.factoryScope === state.factoryScope;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function applyMapPreset(presetId) {
  const preset = mapPresets[presetId];
  if (!preset || !mapState.map) return;
  state.mapPresetId = presetId;
  updatePresetButtons();
  mapState.map.fitBounds(preset.bounds, mapFitOptions());
}

function updateViewModeClass() {
  const shell = document.querySelector(".map-first-shell");
  if (!shell) return;
  shell.classList.toggle("is-default-mode", state.viewMode === "default");
  shell.classList.toggle("is-scenario-mode", state.viewMode === "scenario");
}

function mapFitOptions(focus = {}) {
  const width = window.innerWidth || 1280;
  const height = window.innerHeight || 900;
  const scenarioBottomPadding = Math.min(390, Math.max(280, Math.round(height * 0.29)));
  const options =
    state.viewMode === "scenario" && focus.maxZoom
      ? {maxZoom: focus.maxZoom}
      : {};
  if (state.viewMode === "default") {
    if (width < 900) {
      return {
        ...options,
        paddingTopLeft: [24, 96],
        paddingBottomRight: [24, 220],
      };
    }
    if (width < 1280) {
      return {
        ...options,
        paddingTopLeft: [300, 80],
        paddingBottomRight: [300, 96],
      };
    }
    return {
      ...options,
      paddingTopLeft: [370, 80],
      paddingBottomRight: [370, 96],
    };
  }
  if (width < 900) {
    return {
      ...options,
      paddingTopLeft: [24, 72],
      paddingBottomRight: [24, 300],
    };
  }
  return {
    ...options,
    paddingTopLeft: [48, 72],
    paddingBottomRight: [48, scenarioBottomPadding],
  };
}

function setViewMode(mode, {fit = true} = {}) {
  state.viewMode = mode === "scenario" ? "scenario" : "default";
  if (state.viewMode === "default") {
    stopScenarioPlayback({rerender: false});
    state.scenarioId = plans[0]?.id || state.scenarioId;
    state.scenarioStageIndex = 0;
    state.targetDrones = currentPlan().target_drones || state.targetDrones;
    state.mapPresetId = "korea";
    applyLayerFilterPreset("all");
    closeDetailsDrawer({clearSelection: true});
  } else if (state.scenarioId === "southern_port_disruption") {
    state.mapPresetId = "trade";
    applyCurrentScenarioLayerPreset();
  } else {
    state.mapPresetId = "korea";
    applyCurrentScenarioLayerPreset();
  }
  const input = elementById("targetInput");
  if (input) input.value = state.targetDrones;
  updateViewModeClass();
  renderAll();
  if (!fit || !mapState.map) return;
  if (state.viewMode === "default") {
    applyMapPreset("korea");
  } else {
    fitMap();
  }
}

function currentScenarioNarrative() {
  return scenarioCaseNarratives[state.scenarioId] || {
    phase: "시나리오 검토",
    title: currentPlan().name || state.scenarioId,
    operatorFocus: "현재 계획의 생산, 물류, 위험 변화를 확인",
    caseSignal: currentPlan().description || "scenario data available",
    uiChange: "현재 데이터셋에 연결된 지도와 계획 카드가 갱신됩니다.",
    logicChange: "선택된 scenario_id 기준으로 공급망 후보와 재계획 결과를 다시 표시합니다.",
    steps: [],
  };
}

function scenarioPlan(scenarioId = state.scenarioId) {
  return planById[scenarioId] || plans[0] || {};
}

function optimizationForScenario(scenarioId = state.scenarioId) {
  return optimizationByScenarioId[scenarioId] || optimizationResult.scenarios?.[0] || {};
}

function reconfigurationForScenario(scenarioId = state.scenarioId) {
  return reconfigurationByScenarioId[scenarioId] || reconfigurationResult.scenarios?.[0] || {};
}

function impactEventsForScenario(scenarioId = state.scenarioId) {
  return scenarioImpactEvents.filter((event) => event.scenario_id === scenarioId);
}

function primaryImpactEventForScenario(scenarioId = state.scenarioId, eventType = "") {
  const events = impactEventsForScenario(scenarioId);
  if (eventType) return events.find((event) => event.event_type === eventType) || events[0] || null;
  return events[0] || null;
}

function impactPointToThreatPoint(point = {}, fallbackRadiusKm = 50) {
  const lat = Number(point.lat);
  const lon = Number(point.lon);
  const radiusKm = Number(point.radiusKm ?? point.radius_km ?? fallbackRadiusKm);
  return {
    lat,
    lon,
    radiusKm: Number.isFinite(radiusKm) ? radiusKm : fallbackRadiusKm,
    label: point.label || "",
  };
}

function impactEventPaths(event = {}) {
  const geometry = event?.geometry || {};
  const fallbackRadiusKm = Number(geometry.default_circle_radius_km || geometry.defaultCircleRadiusKm || 50);
  if (Array.isArray(geometry.paths) && geometry.paths.length) {
    return geometry.paths
      .map((path) => (path || []).map((point) => impactPointToThreatPoint(point, fallbackRadiusKm)))
      .filter((path) => path.length >= 2);
  }
  if (Array.isArray(geometry.path) && geometry.path.length >= 2) {
    return [geometry.path.map((point) => impactPointToThreatPoint(point, fallbackRadiusKm))];
  }
  return [];
}

function impactEventCircleRadiiKm(event = {}) {
  return impactEventPaths(event)[0]?.map((point) => point.radiusKm) || [];
}

function impactEventDefaultCircleRadiusKm(event = {}, fallbackRadiusKm = 50) {
  const geometry = event?.geometry || {};
  const radiusKm = Number(geometry.default_circle_radius_km || geometry.defaultCircleRadiusKm || fallbackRadiusKm);
  return Number.isFinite(radiusKm) ? radiusKm : fallbackRadiusKm;
}

function impactEventCorridorBufferKm(event = {}, fallbackBufferKm = 0) {
  const geometry = event?.geometry || {};
  const bufferKm = Number(geometry.corridor_buffer_km || geometry.corridorBufferKm || fallbackBufferKm);
  return Number.isFinite(bufferKm) ? bufferKm : fallbackBufferKm;
}

function threatPathsFromPlanThreat(plan = {}) {
  return Array.isArray(plan.threat?.path) && plan.threat.path.length >= 2
    ? [plan.threat.path.map((point) => impactPointToThreatPoint(point, Number(plan.threat.risk_radius_km || 50)))]
    : [];
}

function scenarioIds() {
  return plans.map((plan) => plan.id).filter(Boolean);
}

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))];
}

function routeIdsForFactories(plan, factoryIds, limit = 12) {
  const ids = new Set(factoryIds);
  return (plan.route_segments || [])
    .filter((route) => ids.has(route.factory_id) || ids.has(route.destination_factory_id))
    .slice(0, limit)
    .map((route) => route.id);
}

function materialRouteIdsForFactories(plan, factoryIds, limit = 10) {
  const ids = new Set(factoryIds);
  return (plan.port_to_factory_material_routes || [])
    .filter((route) => ids.has(route.target_factory_id))
    .slice(0, limit)
    .map((route) => route.id);
}

function routeIdsForPart(plan, partCategory, limit = 12) {
  return (plan.route_segments || [])
    .filter((route) => route.part_category === partCategory)
    .slice(0, limit)
    .map((route) => route.id);
}

function materialRouteIdsForMaterial(plan, materialId, limit = 10) {
  return (plan.port_to_factory_material_routes || [])
    .filter((route) => route.material_id === materialId)
    .slice(0, limit)
    .map((route) => route.id);
}

function factoryIdsForRouteIds(plan, routeIds, limit = 24) {
  const routeIdSet = new Set(routeIds || []);
  return uniqueValues(
    allPlanRoutes(plan)
      .filter((route) => route.id && routeIdSet.has(route.id))
      .flatMap((route) => routeFactoryIds(route)),
  ).slice(0, limit);
}

function factoriesInside(factoryIds, {minLat = -90, maxLat = 90, minLon = -180, maxLon = 180} = {}, limit = 18) {
  return uniqueValues(factoryIds || [])
    .filter((id) => {
      const factory = factoryById[id];
      if (!factory) return false;
      return factory.lat >= minLat && factory.lat <= maxLat && factory.lon >= minLon && factory.lon <= maxLon;
    })
    .slice(0, limit);
}

function factoryIdsByCategoryInside(category, bounds, limit = 24) {
  return factoriesInside(
    factories.filter((factory) => factory.category === category).map((factory) => factory.id),
    bounds,
    limit,
  );
}

function actionFactoryIds(reconfiguration, actionName, limit = 12) {
  return uniqueValues((reconfiguration[actionName] || []).map((item) => item.factory_id)).slice(0, limit);
}

function actionRouteIds(reconfiguration, actionName, limit = 12) {
  return uniqueValues((reconfiguration[actionName] || []).map((item) => item.route_id)).slice(0, limit);
}

function factoryNames(factoryIds, limit = 3) {
  return factoryIds
    .slice(0, limit)
    .map((id) => factoryById[id]?.company_name)
    .filter(Boolean)
    .join(" / ");
}

function countText(value, suffix = "") {
  return `${fmt(value)}${suffix}`;
}

function buildScenarioStages(scenarioId = state.scenarioId) {
  const plan = scenarioPlan(scenarioId);
  const optimization = optimizationForScenario(scenarioId);
  const reconfiguration = reconfigurationForScenario(scenarioId);
  const objective = optimization.objective_breakdown || {};
  const metrics = reconfiguration.delta_metrics || {};
  const addedFactoryIds = uniqueValues(reconfiguration.added_factory_ids || []);
  const removedFactoryIds = uniqueValues(reconfiguration.removed_factory_ids || []);
  const frozenFactoryIds = actionFactoryIds(reconfiguration, "frozen_order_actions", 12);
  const transitFactoryIds = actionFactoryIds(reconfiguration, "in_transit_actions", 12);
  const transitRouteIds = actionRouteIds(reconfiguration, "in_transit_actions", 12);
  const finalAssemblyFactoryIds = uniqueValues(factories.filter((factory) => factory.category === "drone_assembly").map((factory) => factory.id));
  const propulsionRouteIds = routeIdsForPart(plan, "propulsion", 10);
  const assemblyRouteIds = routeIdsForPart(plan, "drone_assembly", 8);
  const ndfebRouteIds = materialRouteIdsForMaterial(plan, "ndfeb_magnet_feedstock", 8);
  const batteryRouteIds = materialRouteIdsForMaterial(plan, "lithium_battery_feedstock", 8);
  const electronicsRouteIds = materialRouteIdsForMaterial(plan, "copper_electronics_feedstock", 8);
  const coreComponentRouteIds = uniqueValues([
    ...routeIdsForPart(plan, "flight_stack", 6),
    ...routeIdsForPart(plan, "power", 6),
    ...routeIdsForPart(plan, "propulsion", 6),
  ]);
  const baselineAllocationRouteIds = coreComponentRouteIds.slice(0, 18);
  const baselineAllocationFactoryIds = factoriesInside(factoryIdsForRouteIds(plan, baselineAllocationRouteIds, 30), {
    minLat: 36.1,
    maxLat: 38.25,
    minLon: 126.1,
    maxLon: 128.65,
  }, 18);
  const southernPlan = scenarioPlan("southern_port_disruption");
  const southernImpactEvent = primaryImpactEventForScenario("southern_port_disruption", "logistics_disruption");
  const southernImpactPaths = impactEventPaths(southernImpactEvent);
  const southernThreatPaths = southernImpactPaths.length ? southernImpactPaths : threatPathsFromPlanThreat(southernPlan);
  const southernImpactCircleRadiiKm = impactEventCircleRadiiKm(southernImpactEvent);
  const southernImpactDefaultCircleRadiusKm = impactEventDefaultCircleRadiusKm(
    southernImpactEvent,
    Number(southernPlan.threat?.risk_radius_km || 42),
  );
  const southernImpactCorridorBufferKm = impactEventCorridorBufferKm(southernImpactEvent, 14);
  const southernImpactOptions = {
    circleRadiiKm: southernImpactCircleRadiiKm,
    circleRadiusKm: southernImpactDefaultCircleRadiusKm,
    corridorBufferKm: southernImpactCorridorBufferKm,
  };
  const southernImpactedPortIds = uniqueValues(
    importPorts
      .filter((port) => threatImpactForFactory(port, southernThreatPaths, southernImpactOptions).insideImpact)
      .map((port) => port.id),
  );
  const southernBlockadedPortIds = uniqueValues([...southernImpactedPortIds, "port_pohang"]);
  const southernBlockadedPortIdSet = new Set(southernBlockadedPortIds);
  const southernImpactSeaRouteIds = (plan.maritime_import_route_segments || [])
    .filter(
      (route) =>
        southernBlockadedPortIdSet.has(route.destination_port_id) ||
        routeTouchesThreatImpact(route, southernThreatPaths, southernImpactOptions),
    )
    .map((route) => route.id);
  const southernBlockadeFocusPoints = uniqueValues([
    ...southernThreatPaths.flat(),
    ...koreaStraitBlockade.line,
    ...southernBlockadedPortIds.map((id) => portById[id]).filter(Boolean),
  ]);
  const southernImpactMaterialRouteIds = (plan.port_to_factory_material_routes || [])
    .filter(
      (route) =>
        southernBlockadedPortIdSet.has(route.port_id) ||
        routeTouchesThreatImpact(route, southernThreatPaths, southernImpactOptions),
    )
    .map((route) => route.id);
  const inlandAddedFactoryIds = factoriesInside(addedFactoryIds, {
    minLat: 36.0,
    maxLat: 38.2,
    minLon: 126.1,
    maxLon: 128.25,
  }, 12);
  const selectedAssemblyFactoryIds = uniqueValues(
    (plan.selected_suppliers || [])
      .filter((supplier) => supplier.part_category === "drone_assembly")
      .map((supplier) => supplier.factory_id),
  );
  const westernPlan = scenarioPlan("western_axis_threat");
  const westernImpactEvent = primaryImpactEventForScenario("western_axis_threat", "attack_corridor");
  const westernAttackPaths = impactEventPaths(westernImpactEvent);
  const westernThreatPaths = westernAttackPaths.length ? westernAttackPaths : threatPathsFromPlanThreat(westernPlan);
  const westernAttackPath = westernThreatPaths[0] || [];
  const westernAttackCircleRadiiKm = impactEventCircleRadiiKm(westernImpactEvent);
  const westernThreatCorridorBufferKm = impactEventCorridorBufferKm(westernImpactEvent, 18);
  const westernDefaultCircleRadiusKm = impactEventDefaultCircleRadiusKm(westernImpactEvent, Number(westernPlan.threat?.risk_radius_km || 58));
  const westernImpactLabel = westernImpactEvent?.label || westernPlan.threat?.label || "서해축 공장 공격 영향권";
  const westernAssemblyIds = selectedAssemblyFactoryIds.length
    ? selectedAssemblyFactoryIds
    : factoryIdsByCategoryInside("drone_assembly", {
      minLat: 36.15,
      maxLat: 37.9,
      minLon: 126.45,
      maxLon: 129.1,
    }, 24);
  const boneAssemblyId = westernAssemblyIds.find((id) => {
    const factory = factoryById[id] || {};
    const label = `${factory.company_name || ""} ${factory.display_name || ""} ${factory.city || ""}`;
    return /본AI|Bone|D-MAKERS/i.test(label);
  });
  const boneAssemblyFactory = factoryById[boneAssemblyId];
  const westernThreatImpactOptions = {
    circleRadiiKm: westernAttackCircleRadiiKm,
    circleRadiusKm: westernDefaultCircleRadiusKm,
    corridorBufferKm: westernThreatCorridorBufferKm,
  };
  const impactedFactoryIds = uniqueValues(
    factories
      .filter((factory) => threatImpactForFactory(factory, westernThreatPaths, westernThreatImpactOptions).insideImpact)
      .map((factory) => factory.id),
  );
  const impactedFactorySet = new Set(impactedFactoryIds);
  const disabledAssemblyIds = uniqueValues(westernAssemblyIds.filter((id) => impactedFactorySet.has(id)));
  const impactedFinalAssemblyIds = uniqueValues(finalAssemblyFactoryIds.filter((id) => impactedFactorySet.has(id)));
  const usableAssemblyIds = westernAssemblyIds.filter((id) => !disabledAssemblyIds.includes(id));
  const routeAvoidsThreatImpact = (route) =>
    !routeFactoryIds(route).some((id) => impactedFactorySet.has(id)) &&
    !routeTouchesThreatImpact(route, westernThreatPaths, westernThreatImpactOptions);
  const candidateReplacementRouteIds = allPlanRoutes(plan)
    .filter((route) => routeFactoryIds(route).some((id) => usableAssemblyIds.includes(id)))
    .filter(routeAvoidsThreatImpact)
    .map((route) => route.id)
    .filter(Boolean);
  const candidateReplacementRouteIdSet = new Set(candidateReplacementRouteIds);
  const inlandReplacementFactoryIds = factoriesInside(
    uniqueValues([
      ...usableAssemblyIds,
      ...addedFactoryIds,
      ...factoryIdsForRouteIds(plan, candidateReplacementRouteIds, 36),
    ]).filter((id) => !impactedFactorySet.has(id)),
    {
      minLat: 35.8,
      maxLat: 37.3,
      minLon: 126.8,
      maxLon: 129.25,
    },
    24,
  );
  const inlandReplacementFactoryIdSet = new Set(inlandReplacementFactoryIds);
  const inlandReplacementRouteIds = uniqueValues(
    allPlanRoutes(plan)
      .filter((route) => candidateReplacementRouteIdSet.has(route.id) || routeFactoryIds(route).some((id) => inlandReplacementFactoryIdSet.has(id)))
      .filter(routeAvoidsThreatImpact)
      .map((route) => route.id),
  ).slice(0, 24);
  const allFactoryIds = factories.map((factory) => factory.id);
  const westernThreatFitPoints = boneAssemblyFactory
    ? [...westernAttackPath, {lat: boneAssemblyFactory.lat, lon: boneAssemblyFactory.lon}]
    : westernAttackPath;

  if (scenarioId === "western_axis_threat") {
    return [
      {
        code: "2-1",
        title: "공격 방향 감지",
        phase: "D+1 / T+00",
        layerPreset: "finalAssemblyOnly",
        situation: "서해 북서 방향에서 인천·경기 서부를 지나 상주 서측 영향권까지 이어지는 단일 공격 회랑이 감지됩니다.",
        action: "드론 최종 조립 후보만 남겨 공격 회랑, 빨간 영향권, 본AI 인접 위험 범위를 먼저 확인합니다.",
        algorithm: `${westernImpactLabel} 이벤트의 geometry.path/radius_km 데이터를 읽어 최종 조립 후보와 겹쳐 봅니다.`,
        metric: {label: "조립 후보", value: countText(westernAssemblyIds.length)},
        alert: {label: "ALERT", title: "서해축 공격 회랑 감지", mission: "공격 회랑과 최종 조립 후보망을 먼저 분리해서 확인합니다."},
        focus: {
          includeThreat: true,
          threatPaths: westernThreatPaths,
          threatRadiusKm: 36,
          threatCircleRadiusKm: westernDefaultCircleRadiusKm,
          threatCircleRadiiKm: westernAttackCircleRadiiKm,
          threatCorridorBufferKm: westernThreatCorridorBufferKm,
          factoryIds: westernAssemblyIds,
          activeFactoryIds: westernAssemblyIds,
          fitPoints: westernThreatFitPoints,
          fitFactoryIds: [],
          fitThreatOnly: true,
          showFallbackRoutes: false,
          maxZoom: 8,
        },
      },
      {
        code: "2-2",
        title: "위험권 내 조립 거점 불능 표시",
        phase: "D+1 / T+08",
        layerPreset: "finalAssemblyOnly",
        situation: `드론 최종 조립 후보 중 빨간 영향권에 들어온 ${fmt(impactedFinalAssemblyIds.length)}개 조립 거점은 생산 후보에서 불능 처리됩니다.`,
        action: "드론 최종 조립 노드만 남긴 화면에서 영향권 내 조립 후보를 큰 빨간 X로 표시하고, 우회 경로는 아직 숨깁니다.",
        algorithm: `공장 좌표가 빨간 원 안에 있거나 단일 회랑 ${fmt(westernThreatCorridorBufferKm)}km 버퍼 안에 있으면 disabledFactoryIds로 전환합니다.`,
        metric: {label: "불능 조립", value: countText(impactedFinalAssemblyIds.length)},
        focus: {
          includeThreat: true,
          threatPaths: westernThreatPaths,
          threatRadiusKm: 36,
          threatCircleRadiusKm: westernDefaultCircleRadiusKm,
          threatCircleRadiiKm: westernAttackCircleRadiiKm,
          threatCorridorBufferKm: westernThreatCorridorBufferKm,
          factoryIds: uniqueValues([...westernAssemblyIds, ...impactedFinalAssemblyIds]),
          disabledFactoryIds: impactedFinalAssemblyIds,
          fitFactoryIds: uniqueValues([...westernAssemblyIds, ...impactedFinalAssemblyIds]),
          fitFactoriesOnly: true,
          showFallbackRoutes: false,
          maxZoom: 9,
        },
      },
      {
        code: "2-3",
        title: "내륙 대체 부품-제조 매핑",
        phase: "D+1 / T+18",
        layerPreset: "allSupplyGraph",
        situation: "빨간 영향권에 들어온 조립·부품 제조 노드와 해당 endpoint를 지나는 엣지를 제외하고, 남은 내륙·남부권 후보로 공급망을 다시 매핑합니다.",
        action: "공격 영향권 내부의 노드/엣지는 운영 그래프에서 제거하고, 남은 경로만 재계산 결과로 표시합니다.",
        algorithm: "행정구역 고정 제외가 아니라 attack impact geometry 안의 factory/route endpoint를 제거한 뒤 added factory, 부품 route, 조립 후보를 재매칭합니다.",
        metric: {label: "내륙 후보", value: countText(inlandReplacementFactoryIds.length)},
        focus: {
          includeThreat: true,
          threatPaths: westernThreatPaths,
          threatRadiusKm: 36,
          threatCircleRadiusKm: westernDefaultCircleRadiusKm,
          threatCircleRadiiKm: westernAttackCircleRadiiKm,
          threatCorridorBufferKm: westernThreatCorridorBufferKm,
          factoryIds: inlandReplacementFactoryIds,
          activeFactoryIds: inlandReplacementFactoryIds,
          excludedFactoryIds: impactedFactoryIds,
          routeIds: inlandReplacementRouteIds,
          fitFactoryIds: uniqueValues([...inlandReplacementFactoryIds, ...disabledAssemblyIds]),
          fitFactoriesOnly: true,
          hideExcludedFactories: true,
          hideRoutesThroughExcludedFactories: true,
          hideRoutesThroughThreatImpact: true,
          strictRouteIds: true,
          showFallbackRoutes: false,
          maxZoom: 9,
        },
      },
      {
        code: "2-4",
        title: "전체 공급망 현황 파악",
        phase: "D+1 / T+30",
        layerPreset: "allSupplyGraph",
        situation: "불능 조립 거점과 내륙 대체 후보를 포함한 전체 공급망 상태를 다시 펼쳐 최종 판단 화면으로 전환합니다.",
        action: "전체 후보 공장, 원료/자원, 운송 route를 함께 열고 사람 검토 대상만 분리합니다.",
        algorithm: "전체 candidate graph를 다시 표시하되 disabled node는 빨간 X로 유지합니다.",
        metric: {label: "검토 건", value: countText((metrics.frozen_order_conflict_count || 0) + (metrics.in_transit_review_count || 0))},
        focus: {
          includeThreat: true,
          threatPaths: westernThreatPaths,
          threatRadiusKm: 36,
          threatCircleRadiusKm: westernDefaultCircleRadiusKm,
          threatCircleRadiiKm: westernAttackCircleRadiiKm,
          threatCorridorBufferKm: westernThreatCorridorBufferKm,
          factoryIds: allFactoryIds,
          disabledFactoryIds: impactedFactoryIds,
          excludedFactoryIds: impactedFactoryIds,
          routeIds: uniqueValues([...inlandReplacementRouteIds, ...transitRouteIds]).slice(0, 28),
          hideRoutesThroughExcludedFactories: true,
          hideRoutesThroughThreatImpact: true,
          showFallbackRoutes: false,
          maxZoom: 7,
        },
      },
    ];
  }

  if (scenarioId === "southern_port_disruption") {
    return [
      {
        code: "3-1",
        title: "대한해협 봉쇄 감지",
        phase: "D+2 / T+00",
        layerPreset: "portBlockadeIntro",
        situation: "중국 해상 민병대성 선박이 대한해협 남동쪽을 둘러싸며 부산·울산·포항 항만 접근 위험이 동시에 상승합니다.",
        action: "대한해협 봉쇄선과 항만 주변을 zoom-in하고, 일본발 원료 feeder route를 차단/재계산 대상으로 전환합니다.",
        algorithm: "항만 좌표와 해상 route geometry가 blockade/impact corridor에 걸리면 port와 maritime edge를 disabled/blocked 상태로 전파합니다.",
        metric: {label: "route risk", value: pct(objective.weighted_route_risk || 0)},
        alert: {label: "ALERT", title: "대한해협 봉쇄 징후", mission: "봉쇄선, 항만 불능, 원료 feeder route 차단 여부를 먼저 확인합니다."},
        focus: {
          includeThreat: true,
          includeTrade: true,
          blockade: koreaStraitBlockade,
          threatPaths: southernThreatPaths,
          threatCircleRadiusKm: southernImpactDefaultCircleRadiusKm,
          threatCircleRadiiKm: southernImpactCircleRadiiKm,
          threatCorridorBufferKm: southernImpactCorridorBufferKm,
          disabledPortIds: southernBlockadedPortIds,
          blockedRouteIds: southernImpactSeaRouteIds,
          hiddenRouteIds: southernImpactMaterialRouteIds,
          hideRoutesThroughDisabledPorts: true,
          fitThreatOnly: true,
          routeIds: [...southernImpactSeaRouteIds, ...southernImpactMaterialRouteIds],
          fitPoints: southernBlockadeFocusPoints,
          maxZoom: 10,
        },
      },
      {
        code: "3-2",
        title: "희토류/반도체 feeder 점검",
        phase: "D+2 / T+09",
        layerPreset: "rawMaterialFeeder",
        situation: "부산·울산·포항 항만은 봉쇄 영향 항만으로 불능 처리되고, 해당 항만으로 들어오는 일본발 해상 원료 edge는 차단 상태가 됩니다.",
        action: "불능 항만은 빨간 X로 표시하고, 일본→항만 해상 route는 빨간 차단선으로 표시하며, 항만→공장 downstream 파이프라인은 끕니다.",
        algorithm: "port 좌표 또는 봉쇄 대상 항만 id가 disabledPortIds에 들어오면 destination_port_id/port_id가 연결된 route를 blocked/hidden 상태로 전파합니다.",
        metric: {label: "원료 route", value: countText(ndfebRouteIds.length + electronicsRouteIds.length)},
        focus: {
          includeThreat: true,
          includeTrade: true,
          blockade: koreaStraitBlockade,
          threatPaths: southernThreatPaths,
          threatCircleRadiusKm: southernImpactDefaultCircleRadiusKm,
          threatCircleRadiiKm: southernImpactCircleRadiiKm,
          threatCorridorBufferKm: southernImpactCorridorBufferKm,
          disabledPortIds: southernBlockadedPortIds,
          blockedRouteIds: southernImpactSeaRouteIds,
          hiddenRouteIds: southernImpactMaterialRouteIds,
          hideRoutesThroughDisabledPorts: true,
          hideRoutesThroughThreatImpact: true,
          materialIds: ["ndfeb_magnet_feedstock", "copper_electronics_feedstock"],
          routeIds: uniqueValues([...southernImpactSeaRouteIds, ...ndfebRouteIds, ...electronicsRouteIds]),
          fitPoints: southernBlockadeFocusPoints,
          maxZoom: 9,
        },
      },
      {
        code: "3-3",
        title: "내륙 대체 조립/공장 후보",
        phase: "D+2 / T+19",
        layerPreset: "inlandReplacement",
        situation: `${factoryNames(addedFactoryIds) || "대체 후보 공장"} 등 항만 스트레스와 무관한 내륙 후보를 보강합니다.`,
        action: `${fmt(metrics.added_factory_count || addedFactoryIds.length)}개 후보를 추가하고, ${fmt(metrics.removed_factory_count || removedFactoryIds.length)}개 후보는 우선순위에서 내립니다.`,
        algorithm: "baseline 대비 added/removed factory delta를 산출해 원료-부품-조립 흐름을 재구성합니다.",
        metric: {label: "대체 공장", value: countText(metrics.added_factory_count || addedFactoryIds.length)},
        focus: {
          blockade: koreaStraitBlockade,
          disabledPortIds: southernBlockadedPortIds,
          blockedRouteIds: southernImpactSeaRouteIds,
          hiddenRouteIds: southernImpactMaterialRouteIds,
          hideRoutesThroughDisabledPorts: true,
          hideRoutesThroughThreatImpact: true,
          factoryIds: addedFactoryIds.slice(0, 14),
          routeIds: routeIdsForFactories(plan, addedFactoryIds, 10),
          fitFactoryIds: inlandAddedFactoryIds,
          fitFactoriesOnly: true,
          maxZoom: 11,
        },
      },
      {
        code: "3-4",
        title: "공급 안정화 명령 검토",
        phase: "D+2 / T+28",
        layerPreset: "allSupplyGraph",
        situation: `생산량은 baseline 대비 ${fmt(metrics.feasible_output_delta_units_30d || 0)}대 수준으로 보존되지만, route risk가 ${pct(metrics.weighted_route_risk_delta || 0)} 상승합니다.`,
        action: "최종 조립과 운송 중 물량을 묶어 검토하고, 실제 명령 전 사람 승인 대상으로 올립니다.",
        algorithm: "v1.0 reconfiguration은 생산량/비용/위험 delta와 동결 주문 충돌을 Plan Delta로 표시합니다.",
        metric: {label: "운송 검토", value: countText(metrics.in_transit_review_count || 0)},
        focus: {
          blockade: koreaStraitBlockade,
          disabledPortIds: southernBlockadedPortIds,
          blockedRouteIds: southernImpactSeaRouteIds,
          hiddenRouteIds: southernImpactMaterialRouteIds,
          hideRoutesThroughDisabledPorts: true,
          hideRoutesThroughThreatImpact: true,
          factoryIds: uniqueValues([...frozenFactoryIds, ...transitFactoryIds]),
          routeIds: [...assemblyRouteIds, ...transitRouteIds].slice(0, 12),
          maxZoom: 10,
        },
      },
    ];
  }

  return [
    {
      code: "1-1",
      title: "전시 수요 접수",
      phase: "D+0 / T+00",
      layerPreset: "finalAssemblyOnly",
      situation: "30일 목표 10,000대 수요가 접수되고 BOM/공장/원료 장부를 계산 가능한 상태로 묶습니다.",
      action: "전국 후보 공장, 자원 회수 후보, 조립 route를 기본 운영 화면의 판단 대상으로 올립니다.",
      algorithm: "v0.8 optimizer input이 수요, 공장 capacity, route, 원료, 생산 중 장부를 생성합니다.",
      metric: {label: "목표", value: countText(objective.target_drones_30d || plan.target_drones || 0)},
      alert: {label: "ALERT", title: "전시 수요 발생", mission: "30일 목표 수량을 기준으로 공장·원료·생산 중 장부를 계산 가능한 상태로 묶습니다."},
      focus: {
        factoryIds: finalAssemblyFactoryIds,
        activeFactoryIds: finalAssemblyFactoryIds,
        fitFactoryIds: finalAssemblyFactoryIds,
        fitFactoriesOnly: true,
        maxZoom: 8,
      },
    },
    {
      code: "1-2",
      title: "모터/추진계 병목 확인",
      phase: "D+0 / T+10",
      layerPreset: "motorBottleneck",
      situation: `현재 후보망으로 ${fmt(objective.feasible_output_units_30d || 0)}대가 가능하고, 모터/추진계가 1순위 병목입니다.`,
      action: "추진계 route와 NdFeB 자석 feeder를 먼저 확인해 부족량을 줄일 후보를 찾습니다.",
      algorithm: "v0.9 allocation이 part coverage를 계산하고 limiting_part_family를 고릅니다.",
      metric: {label: "모터 coverage", value: pct(0.6428)},
      focus: {routeIds: [...propulsionRouteIds, ...ndfebRouteIds].slice(0, 14), materialIds: ["ndfeb_magnet_feedstock"], maxZoom: 10},
    },
    {
      code: "1-3",
      title: "핵심 부품 공급망 배정",
      phase: "D+0 / T+20",
      layerPreset: "coreComponentSupply",
      situation: "부족량을 먼저 줄이고, 이후 route risk와 비용 proxy가 낮은 공장-조립 경로를 선택합니다.",
      action: "최종 조립 route와 핵심 부품 route를 운영 후보로 확정하기 전에 검증 큐로 올립니다.",
      algorithm: "selected flows는 full MILP가 아니라 deterministic allocation prototype 결과입니다.",
      metric: {label: "부족", value: countText(objective.output_gap_units_30d || 0)},
      focus: {
        routeIds: baselineAllocationRouteIds,
        factoryIds: uniqueValues([...finalAssemblyFactoryIds, ...factoryIdsForRouteIds(plan, baselineAllocationRouteIds, 60)]),
        fitFactoryIds: baselineAllocationFactoryIds,
        fitFactoriesOnly: true,
        strictRouteIds: true,
        maxZoom: 11,
      },
    },
    {
      code: "1-4",
      title: "전체 공급망 현황 파악",
      phase: "D+0 / T+30",
      layerPreset: "allSupplyGraph",
      situation: "핵심 부품 공급망 배정 이후 전체 후보 공장, 자원, 원료 수급 경로를 한 화면에서 확인합니다.",
      action: "생산 중 물량, 동결 주문, 운송 중 물량을 전체 공급망 현황 위에 겹쳐 최종 검토합니다.",
      algorithm: "전체 candidate graph와 frozen/in-transit ledger를 함께 표시해 다음 위협 시나리오의 기준선을 만듭니다.",
      metric: {label: "운송 중", value: countText((reconfiguration.in_transit_actions || []).length)},
      focus: {factoryIds: allFactoryIds, routeIds: transitRouteIds, maxZoom: 7},
    },
  ];
}

function getScenarioStages(scenarioId = state.scenarioId) {
  const cacheKey = scenarioId || "baseline";
  if (!scenarioStageCache.has(cacheKey)) {
    scenarioStageCache.set(cacheKey, buildScenarioStages(cacheKey));
  }
  return scenarioStageCache.get(cacheKey) || [];
}

function currentScenarioStages() {
  return getScenarioStages(state.scenarioId);
}

function currentScenarioStage() {
  const stages = currentScenarioStages();
  const index = Math.max(0, Math.min(state.scenarioStageIndex || 0, stages.length - 1));
  return stages[index] || stages[0] || null;
}

function currentScenarioFocus() {
  return currentScenarioFocusContext().focus;
}

function scenarioFocusContext(focus = {}) {
  if (!focus || !Object.keys(focus).length) return emptyScenarioFocusContext;
  if (!scenarioFocusContextCache.has(focus)) {
    scenarioFocusContextCache.set(focus, {
      active: true,
      focus,
      routeIds: new Set(focus.routeIds || []),
      excludedFactoryIds: new Set(focus.excludedFactoryIds || []),
      disabledPortIds: new Set(focus.disabledPortIds || []),
      blockedRouteIds: new Set(focus.blockedRouteIds || []),
      hiddenRouteIds: new Set(focus.hiddenRouteIds || []),
      threatRouteTouchCache: new Map(),
      forcedFactoryIds: null,
    });
  }
  return scenarioFocusContextCache.get(focus);
}

function currentScenarioFocusContext() {
  if (state.viewMode !== "scenario") return emptyScenarioFocusContext;
  return scenarioFocusContext(currentScenarioStage()?.focus || {});
}

function currentThreatPaths(plan = currentPlan()) {
  const focus = currentScenarioFocus();
  if (state.viewMode === "scenario" && plan?.id === currentPlan()?.id) {
    if (Array.isArray(focus.threatPaths) && focus.threatPaths.length) {
      return focus.threatPaths.filter((path) => Array.isArray(path) && path.length >= 2);
    }
    if (Array.isArray(focus.threatPath) && focus.threatPath.length >= 2) return [focus.threatPath];
  }
  const impactPaths = impactEventPaths(primaryImpactEventForScenario(plan?.id));
  if (impactPaths.length) return impactPaths;
  return threatPathsFromPlanThreat(plan);
}

function currentThreatPath(plan = currentPlan()) {
  return currentThreatPaths(plan)[0] || [];
}

function currentThreatRadiusKm(plan = currentPlan()) {
  const focus = currentScenarioFocus();
  if (state.viewMode === "scenario" && plan?.id === currentPlan()?.id && Number.isFinite(Number(focus.threatRadiusKm))) {
    return Number(focus.threatRadiusKm);
  }
  const impactEvent = primaryImpactEventForScenario(plan?.id);
  if (impactEvent) return impactEventDefaultCircleRadiusKm(impactEvent, Number(plan?.threat?.risk_radius_km || 50));
  return Number(plan?.threat?.risk_radius_km || 50);
}

function allPlanRoutes(plan = currentPlan()) {
  return [
    ...(plan.route_segments || []),
    ...(plan.resource_route_segments || []),
    ...(plan.port_to_factory_material_routes || []),
    ...(plan.maritime_import_route_segments || []),
  ];
}

function routeFactoryIds(route = {}) {
  return uniqueValues([route.factory_id, route.target_factory_id, route.destination_factory_id]);
}

function routePortIds(route = {}) {
  return uniqueValues([route.port_id, route.origin_port_id, route.destination_port_id, route.preferred_port_id]);
}

function routeMaterialIds(route = {}) {
  return uniqueValues([route.material_id, ...(route.material_ids || [])]);
}

function routeHasMaterialFlow(route = {}) {
  return Boolean(
    route.material_id ||
      route.material_ids?.length ||
      route.port_id ||
      route.origin_port_name ||
      route.destination_port_name ||
      route.destination_port_id,
  );
}

function routeMatchesFocus(route = {}, focus = {}) {
  const routeIds = new Set(focus.routeIds || []);
  const factoryIds = new Set(focus.factoryIds || []);
  const materialIds = new Set(focus.materialIds || []);
  return (
    (route.id && routeIds.has(route.id)) ||
    routeFactoryIds(route).some((id) => factoryIds.has(id)) ||
    routeMaterialIds(route).some((id) => materialIds.has(id))
  );
}

function routeShouldExposeEndpointNodes(route = {}, focus = {}) {
  if (routeMatchesFocus(route, focus)) return true;
  return Boolean(focus.includeTrade && routeHasMaterialFlow(route) && !focusHasExplicitRoutes(focus));
}

function addRouteToFocusContext(context, route = {}) {
  if (route.id) context.routeIds.add(route.id);
  routeFactoryIds(route).forEach((id) => context.factoryIds.add(id));
  routeMaterialIds(route).forEach((id) => context.materialIds.add(id));
}

function focusHasExplicitRoutes(focus = {}) {
  return Boolean((focus.routeIds || []).length || (focus.materialIds || []).length || (focus.factoryIds || []).length);
}

function addScenarioFocusToContext(context, plan = currentPlan()) {
  const focus = currentScenarioFocus();
  if (!Object.keys(focus).length) return context;
  if (focus.revealAll && !focusHasExplicitRoutes(focus)) return context;
  context.active = true;
  (focus.factoryIds || []).forEach((id) => context.factoryIds.add(id));
  (focus.routeIds || []).forEach((id) => context.routeIds.add(id));
  (focus.blockedRouteIds || []).forEach((id) => context.routeIds.add(id));
  (focus.materialIds || []).forEach((id) => context.materialIds.add(id));
  (focus.disabledFactoryIds || []).forEach((id) => {
    context.factoryIds.add(id);
    context.disabledFactoryIds?.add(id);
  });
  (focus.activeFactoryIds || []).forEach((id) => {
    context.factoryIds.add(id);
    context.activeFactoryIds?.add(id);
  });

  const allowBroadTrade = focus.includeTrade && !focusHasExplicitRoutes(focus);
  allPlanRoutes(plan)
    .filter((route) => routeMatchesFocus(route, focus) || (allowBroadTrade && routeHasMaterialFlow(route)))
    .forEach((route) => addRouteToFocusContext(context, route));
  return context;
}

function addAssemblyReplacementFocusToContext(context, plan = currentPlan()) {
  const actions = assemblyReplacementActions(plan.id || state.scenarioId);
  if (!actions.length || state.viewMode !== "scenario") return context;
  context.active = true;
  actions.forEach((action) => {
    if (action.from_factory_id) {
      context.factoryIds.add(action.from_factory_id);
      context.disabledFactoryIds?.add(action.from_factory_id);
    }
    if (action.to_factory_id) {
      context.factoryIds.add(action.to_factory_id);
      context.activeFactoryIds?.add(action.to_factory_id);
    }
  });
  return context;
}

function pushLatLon(points, point = {}) {
  const lat = Number(point.lat);
  const lon = Number(point.lon);
  if (Number.isFinite(lat) && Number.isFinite(lon)) points.push([lat, lon]);
}

function safeRoutePoints(route = {}) {
  if (Array.isArray(route.route_geometry) && route.route_geometry.length >= 2) {
    return route.route_geometry.map((point) => ({lat: Number(point.lat), lon: Number(point.lon)}));
  }
  if (route.from && route.to) return [route.from, route.to];
  return [];
}

function uniqueLatLngs(points) {
  const seen = new Set();
  return points.filter((point) => {
    const key = `${Number(point[0]).toFixed(5)},${Number(point[1]).toFixed(5)}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function scenarioStageFocusPoints() {
  const plan = currentPlan();
  const focus = currentScenarioFocus();
  const points = [];
  if (state.viewMode !== "scenario" || !Object.keys(focus).length) return {points, focus};

  const hasFitFactoryIds = Object.prototype.hasOwnProperty.call(focus, "fitFactoryIds");
  const hasFitRouteIds = Object.prototype.hasOwnProperty.call(focus, "fitRouteIds");
  const hasFitMaterialIds = Object.prototype.hasOwnProperty.call(focus, "fitMaterialIds");
  const fitFocus = {
    ...focus,
    factoryIds: hasFitFactoryIds ? focus.fitFactoryIds || [] : focus.factoryIds || [],
    routeIds: hasFitRouteIds ? focus.fitRouteIds || [] : focus.routeIds || [],
    materialIds: hasFitMaterialIds ? focus.fitMaterialIds || [] : focus.materialIds || [],
  };

  (focus.fitPoints || []).forEach((point) => pushLatLon(points, point));
  (fitFocus.factoryIds || []).forEach((id) => {
    const factory = factoryById[id];
    if (factory) pushLatLon(points, factory);
  });

  if (!focus.fitThreatOnly && !focus.fitFactoriesOnly) {
    const allowBroadTrade = fitFocus.includeTrade && !focusHasExplicitRoutes(fitFocus);
    allPlanRoutes(plan).forEach((route) => {
      if (!routeAllowedByScenarioDisplay(route)) return;
      if (!routeMatchesFocus(route, fitFocus) && !(allowBroadTrade && routeHasMaterialFlow(route))) return;
      safeRoutePoints(route).forEach((point) => pushLatLon(points, point));
      routeFactoryIds(route).forEach((id) => {
        const factory = factoryById[id];
        if (factory) pushLatLon(points, factory);
      });
    });
  }

  if (focus.includeThreat) {
    currentThreatPaths(plan).forEach((path) => path.forEach((point) => pushLatLon(points, point)));
  }
  if (focus.includeTrade && points.length < 4) {
    importPorts.forEach((port) => pushLatLon(points, port));
    foreignMaterialSources.forEach((source) => pushLatLon(points, source));
  }
  if (!points.length) {
    visibleFactories()
      .slice(0, 12)
      .forEach((factory) => pushLatLon(points, factory));
  }
  return {points: uniqueLatLngs(points), focus};
}

function setScenario(scenarioId, {fromPlayback = false, stageIndex = 0} = {}) {
  if (!planById[scenarioId]) return;
  const scenarioChanged = state.scenarioId !== scenarioId;
  if (!fromPlayback && state.playbackActive) {
    stopScenarioPlayback({rerender: false});
  }
  state.viewMode = "scenario";
  state.scenarioId = scenarioId;
  state.scenarioStageIndex = Math.max(0, stageIndex);
  state.targetDrones = currentPlan().target_drones;
  state.mapPresetId = scenarioId === "southern_port_disruption" ? "trade" : "korea";
  applyCurrentScenarioLayerPreset();
  closeDetailsDrawer({clearSelection: true});
  const input = elementById("targetInput");
  if (input) input.value = state.targetDrones;
  renderAll();
  if (mapState.map) {
    if (scenarioChanged || state.viewMode === "scenario") fitMap();
  }
}

function shiftScenario(offset) {
  const ids = scenarioIds();
  if (!ids.length) return;
  const currentIndex = Math.max(0, ids.indexOf(state.scenarioId));
  const nextIndex = (currentIndex + offset + ids.length) % ids.length;
  setScenario(ids[nextIndex]);
}

function shiftScenarioStage(offset, {fromPlayback = false} = {}) {
  const ids = scenarioIds();
  if (!ids.length) return;
  const scenarioIndex = Math.max(0, ids.indexOf(state.scenarioId));
  const stages = currentScenarioStages();
  const nextStageIndex = Number(state.scenarioStageIndex || 0) + offset;
  if (nextStageIndex >= 0 && nextStageIndex < stages.length) {
    if (!fromPlayback && state.playbackActive) stopScenarioPlayback({rerender: false});
    state.viewMode = "scenario";
    state.scenarioStageIndex = nextStageIndex;
    applyCurrentScenarioLayerPreset();
    renderScenarioStep();
    if (mapState.map) fitMap();
    return;
  }
  const nextScenarioIndex = (scenarioIndex + (offset > 0 ? 1 : -1) + ids.length) % ids.length;
  const nextScenarioId = ids[nextScenarioIndex];
  const nextStages = getScenarioStages(nextScenarioId);
  const wrappedStageIndex = offset > 0 ? 0 : Math.max(0, nextStages.length - 1);
  setScenario(nextScenarioId, {fromPlayback, stageIndex: wrappedStageIndex});
}

function advanceScenarioPlayback() {
  shiftScenarioStage(1, {fromPlayback: true});
}

function stopScenarioPlayback({rerender = false} = {}) {
  state.playbackActive = false;
  if (uiState.playbackTimer) {
    clearInterval(uiState.playbackTimer);
    uiState.playbackTimer = null;
  }
  if (rerender) {
    renderScenarioLiveTabs();
    renderCaseTicker();
  }
}

function toggleScenarioPlayback() {
  if (state.playbackActive) {
    stopScenarioPlayback({rerender: true});
    return;
  }
  state.viewMode = "scenario";
  state.mapPresetId = state.scenarioId === "southern_port_disruption" ? "trade" : "korea";
  applyCurrentScenarioLayerPreset();
  state.playbackActive = true;
  renderAll();
  if (mapState.map) fitMap();
  uiState.playbackTimer = setInterval(advanceScenarioPlayback, 4200);
}

function haversineKm(a, b) {
  const toRad = (deg) => (deg * Math.PI) / 180;
  const lat1 = toRad(a.lat);
  const lon1 = toRad(a.lon);
  const lat2 = toRad(b.lat);
  const lon2 = toRad(b.lon);
  const dlat = lat2 - lat1;
  const dlon = lon2 - lon1;
  const h =
    Math.sin(dlat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(h));
}

function pointToSegmentKm(point, start, end) {
  const meanLat = ((point.lat + start.lat + end.lat) / 3) * (Math.PI / 180);
  const px = point.lon * Math.cos(meanLat);
  const py = point.lat;
  const ax = start.lon * Math.cos(meanLat);
  const ay = start.lat;
  const bx = end.lon * Math.cos(meanLat);
  const by = end.lat;
  const dx = bx - ax;
  const dy = by - ay;
  if (dx === 0 && dy === 0) return haversineKm(point, start);
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)));
  return haversineKm(point, {lat: ay + t * dy, lon: (ax + t * dx) / Math.cos(meanLat)});
}

function threatCircleRadiusForPoint(point = {}, circleRadiiKm = [], pathIndex = 0, pointIndex = 0, fallbackRadiusKm = 50) {
  const pointRadius = Number(point.radiusKm);
  if (Number.isFinite(pointRadius)) return pointRadius;
  const configuredRadius = Array.isArray(circleRadiiKm[pathIndex])
    ? Number(circleRadiiKm[pathIndex][pointIndex])
    : Number(circleRadiiKm[pointIndex]);
  return Number.isFinite(configuredRadius) ? configuredRadius : fallbackRadiusKm;
}

function threatImpactForFactory(factory = {}, paths = [], {
  circleRadiiKm = [],
  circleRadiusKm = 50,
  corridorBufferKm = 0,
} = {}) {
  const point = {lat: Number(factory.lat), lon: Number(factory.lon)};
  if (!Number.isFinite(point.lat) || !Number.isFinite(point.lon) || !paths.length) {
    return {insideImpact: false, reason: "factory coordinate or threat path unavailable"};
  }

  let nearestSegmentKm = Infinity;
  let nearestCircleKm = Infinity;
  let nearestCircleRadiusKm = Number(circleRadiusKm) || 50;
  let maxCircleMarginKm = -Infinity;
  paths.forEach((path, pathIndex) => {
    for (let index = 0; index < path.length - 1; index += 1) {
      nearestSegmentKm = Math.min(nearestSegmentKm, pointToSegmentKm(point, path[index], path[index + 1]));
    }
    path.forEach((threatPoint, pointIndex) => {
      const radiusKm = threatCircleRadiusForPoint(threatPoint, circleRadiiKm, pathIndex, pointIndex, circleRadiusKm);
      const distanceKm = haversineKm(point, threatPoint);
      const marginKm = radiusKm - distanceKm;
      if (distanceKm < nearestCircleKm) {
        nearestCircleKm = distanceKm;
        nearestCircleRadiusKm = radiusKm;
      }
      maxCircleMarginKm = Math.max(maxCircleMarginKm, marginKm);
    });
  });

  const insideCircle = maxCircleMarginKm >= 0;
  const insideCorridor = Number(corridorBufferKm) > 0 && nearestSegmentKm <= Number(corridorBufferKm);
  const nearestDistanceKm = Math.min(nearestCircleKm, nearestSegmentKm);
  const reason = insideCircle
    ? `영향권 원 안쪽 ${Math.round(maxCircleMarginKm)} km`
    : insideCorridor
      ? `회랑 중심선에서 ${Math.round(nearestSegmentKm)} km`
      : `최근접 영향권까지 ${Math.round(nearestDistanceKm)} km`;
  return {
    insideImpact: insideCircle || insideCorridor,
    insideCircle,
    insideCorridor,
    nearestSegmentKm,
    nearestCircleKm,
    nearestCircleRadiusKm,
    maxCircleMarginKm,
    reason,
  };
}

function interpolatePoint(start = {}, end = {}, t = 0) {
  return {
    lat: Number(start.lat) + (Number(end.lat) - Number(start.lat)) * t,
    lon: Number(start.lon) + (Number(end.lon) - Number(start.lon)) * t,
  };
}

function routeTouchesThreatImpact(route = {}, paths = [], options = {}) {
  const points = safeRoutePoints(route);
  if (!points.length || !paths.length) return false;
  if (points.length === 1) return threatImpactForFactory(points[0], paths, options).insideImpact;
  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    const segmentKm = haversineKm(start, end);
    const sampleCount = Math.max(1, Math.min(8, Math.ceil(segmentKm / 18)));
    for (let sample = 0; sample <= sampleCount; sample += 1) {
      const point = interpolatePoint(start, end, sample / sampleCount);
      if (threatImpactForFactory(point, paths, options).insideImpact) return true;
    }
  }
  return false;
}

function factoryRisk(factory, plan = currentPlan()) {
  const threat = plan.threat;
  if (!threat) return {risk: 0.12, reason: "baseline uncertainty"};
  const threatPaths = currentThreatPaths(plan);
  if (!threatPaths.length) return {risk: 0.16, reason: "threat model unavailable"};
  const scenarioFocus = currentScenarioFocus();
  if (state.viewMode === "scenario" && Object.keys(scenarioFocus).length) {
    const impact = threatImpactForFactory(factory, threatPaths, {
      circleRadiiKm: scenarioFocus.threatCircleRadiiKm || [],
      circleRadiusKm: Number(scenarioFocus.threatCircleRadiusKm || currentThreatRadiusKm(plan)),
      corridorBufferKm: Number(scenarioFocus.threatCorridorBufferKm || 0),
    });
    if (impact.insideImpact) return {risk: 0.94, reason: impact.reason};
  }
  const point = {lat: factory.lat, lon: factory.lon};
  const distances = [];
  threatPaths.forEach((path) => {
    for (let index = 0; index < path.length - 1; index += 1) {
      distances.push(pointToSegmentKm(point, path[index], path[index + 1]));
    }
  });
  const nearest = Math.min(...distances);
  const radius = currentThreatRadiusKm(plan);
  if (nearest >= radius * 2.1) return {risk: 0.16, reason: `예측 회랑에서 ${Math.round(nearest)} km 이격`};
  const corridorFactor = Math.max(0, 1 - nearest / (radius * 2.1));
  const risk = Math.min(0.94, 0.16 + Number(threat.probability || 0.5) * 0.72 * corridorFactor);
  return {risk, reason: `예측 회랑에서 ${Math.round(nearest)} km 이격`};
}

function routeMidpoint(route, t) {
  const points = routePoints(route);
  if (points.length <= 2) {
    return {
      lat: route.from.lat + (route.to.lat - route.from.lat) * t,
      lon: route.from.lon + (route.to.lon - route.from.lon) * t,
    };
  }
  const segments = [];
  let total = 0;
  for (let index = 0; index < points.length - 1; index += 1) {
    const distance = haversineKm(points[index], points[index + 1]);
    segments.push(distance);
    total += distance;
  }
  let target = total * Math.max(0, Math.min(1, t));
  for (let index = 0; index < segments.length; index += 1) {
    if (target <= segments[index] || index === segments.length - 1) {
      const ratio = segments[index] ? target / segments[index] : 0;
      return {
        lat: points[index].lat + (points[index + 1].lat - points[index].lat) * ratio,
        lon: points[index].lon + (points[index + 1].lon - points[index].lon) * ratio,
      };
    }
    target -= segments[index];
  }
  return points[points.length - 1];
}

function routePoints(route) {
  if (Array.isArray(route.route_geometry) && route.route_geometry.length >= 2) {
    return route.route_geometry.map((point) => ({lat: Number(point.lat), lon: Number(point.lon)}));
  }
  return [route.from, route.to];
}

function routeLatLngs(route) {
  return routePoints(route).map((point) => [point.lat, point.lon]);
}

function hasRoadGeometry(route) {
  return route.routing_status === "routed" && Array.isArray(route.route_geometry) && route.route_geometry.length > 2;
}

function routeDistanceText(route) {
  const km = route.road_distance_km || route.distance_km || route.route_distance_km || 0;
  if ((route.routing_status === "onsite" || route.routing_provider === "onsite_final_assembly_assignment") && !km) {
    return "현장 최종조립";
  }
  const basis = route.routing_status === "routed" ? "도로" : "도로 추정";
  return `${fmt(km)} km ${basis}`;
}

function routeCostText(route) {
  const minutes = Number(route.duration_min || 0);
  const fuel = Number(route.fuel_liters_per_trip || 0);
  const cost = Number(route.estimated_trip_cost_krw || 0);
  if ((route.routing_status === "onsite" || route.routing_provider === "onsite_final_assembly_assignment") && !minutes && !fuel && !cost) {
    return "현장 배정 · 운송비 0원/회";
  }
  return `${fmt(Math.round(minutes))}분 · ${fmt(fuel)}L · ${fmt(cost)}원/회`;
}

function routeDestinationName(route = {}) {
  return route.destination_name || route.destination_factory_name || route.hub_name || "최종조립 공장";
}

function supplierDestinationName(supplier = {}) {
  return supplier.destination_name || supplier.destination_factory_name || supplier.hub_name || "최종조립 공장";
}

function routeSourceName(route = {}) {
  return factoryById[route.factory_id]?.company_name || route.factory_name || "공장";
}

function routeQuantity(route = {}) {
  return Number(route.quantity || route.requested_quantity || 0);
}

function routeRoadSummary(route) {
  if (route.route_road_summary) return route.route_road_summary;
  if (route.routing_status === "routed") return "OSRM 도로 형상 있음, 도로 단계 요약 없음";
  return route.routing_note || "휴리스틱 경로 추정";
}

function routeEvidenceText(route) {
  if (route.routing_status === "onsite" || route.routing_provider === "onsite_final_assembly_assignment") {
    return "대표 최종조립 공장 현장 배정";
  }
  const status = route.routing_status === "routed" ? "OSRM 도로 경로" : "추정 경로";
  return `${status} · ${routeRoadSummary(route)}`;
}

function energyEvidenceText(profile = {}) {
  const direct = profile.match_type === "ngms_company_direct";
  const score = Math.round(Number(profile.capacity_evidence_score || 0) * 100);
  if (direct) {
    return `직접 보고값 · ${escapeHtml(profile.matched_company_name || "")} · ${fmt(profile.reported_energy_use_toe)} toe · ${fmt(
      profile.reported_ghg_emissions_tco2e,
    )} tCO2e · evidence ${score}%`;
  }
  return `지역/공정 프록시 · 산업전력 ${fmt(profile.regional_industrial_electricity_mwh)} MWh · evidence ${score}%`;
}

function scoreText(value) {
  return `${Math.round(Number(value || 0) * 100)}%`;
}

function capacityProfileSummary(factory = {}) {
  const profile = factory.factory_capacity_profile || {};
  if (!Object.keys(profile).length) {
    return {
      tier: "VERIFY",
      estimate: fmt(factory.capacity_units_30d || 0),
      index: "n/a",
      confidence: "n/a",
      role: "verification queue",
      evidence: "capacity profile not available",
      missing: "factory-scale backdata required",
    };
  }
  const evidence = profile.evidence || {};
  const productionFit = evidence.production_fit?.score;
  const physicalScale = evidence.physical_scale?.score;
  const workforceScale = evidence.workforce_scale?.score;
  const energyScale = evidence.energy_operating_scale?.score;
  const employeeCount = evidence.workforce_scale?.employee_total;
  const manufacturingArea = evidence.physical_scale?.manufacturing_area_m2;
  const buildingArea = evidence.physical_scale?.building_area_m2;
  return {
    tier: profile.capacity_tier || "VERIFY",
    estimate: fmt(profile.predicted_output_units_30d || factory.capacity_units_30d || 0),
    index: scoreText(profile.capacity_index),
    confidence: scoreText(profile.capacity_confidence),
    role: profile.recommended_role || "verification_queue",
    evidence: [
      `fit ${scoreText(productionFit)}`,
      `scale ${scoreText(physicalScale)}`,
      `workforce ${scoreText(workforceScale)}`,
      `energy ${scoreText(energyScale)}`,
    ].join(" · "),
    scale: `${employeeCount ? `${fmt(employeeCount)} workers` : "workforce n/a"} · ${
      manufacturingArea ? `${fmt(Math.round(manufacturingArea))} m2 mfg` : buildingArea ? `${fmt(Math.round(buildingArea))} m2 bldg` : "area n/a"
    }`,
    missing: (profile.missing_evidence || []).slice(0, 4).join(" / ") || "verification checklist not available",
  };
}

function manufacturingSummary(factory = {}) {
  const profile = factory.manufacturing_profile || {};
  if (!Object.keys(profile).length) return "manufacturing speed profile unavailable";
  return `${fmt(profile.nominal_daily_output_units)} / day nominal · ${fmt(profile.surge_daily_output_units)} / day surge · setup ${profile.setup_days_estimate ?? "n/a"}d · yield ${pct(profile.estimated_yield_rate)}`;
}

function gridRiskSummary(factory = {}) {
  const profile = factory.grid_risk_profile || {};
  if (!Object.keys(profile).length) return "grid risk profile unavailable";
  return `${escapeHtml(profile.primary_grid_zone_name || "load zone")} · dependency ${scoreText(profile.grid_dependency_score)} · outage output ${scoreText(
    profile.outage_output_multiplier,
  )} · backup ${profile.estimated_backup_hours ?? "n/a"}h`;
}

function operationalSummary(factory = {}) {
  const inventory = inventoryByFactoryId[factory.id] || {};
  const orders = frozenOrdersByFactoryId[factory.id] || [];
  const shipments = shipmentsByFactoryId[factory.id] || [];
  const inventoryText = Object.keys(inventory).length
    ? `완제품 ${fmt(inventory.finished_goods_units)} · 생산 중 ${fmt(inventory.wip_units)} · QA 보류 ${fmt(inventory.qa_hold_units)} · 출하 가능 ${fmt(
        inventory.available_to_ship_units,
      )} · 원자재 ${inventory.raw_material_days_on_hand ?? "미상"}일`
    : "재고/생산 중 장부 없음";
  const orderText = orders.length
    ? `${fmt(orders.reduce((sum, order) => sum + Number(order.frozen_quantity_units || 0), 0))}개 동결 물량 · ${fmt(orders.length)}건 잠금 주문`
    : "기본 장부에 동결 주문 없음";
  const shipmentText = shipments.length ? `${fmt(shipments.length)}건 운송 중` : "연결된 운송 중 물량 없음";
  return `${inventoryText}<br />${orderText} · ${shipmentText}`;
}

function selectedSupplierRows(factoryId = state.selectedFactoryId) {
  return (currentPlan().selected_suppliers || []).filter((supplier) => supplier.factory_id === factoryId);
}

function selectedResourceRoutes(resourceId = state.selectedResourceId) {
  return (currentPlan().resource_route_segments || []).filter((route) => route.resource_id === resourceId);
}

function selectedFactoryMaterialRoutes(factoryId = state.selectedFactoryId) {
  return (currentPlan().port_to_factory_material_routes || []).filter((route) => route.target_factory_id === factoryId);
}

function missionText(profileId) {
  return missionProfileKorean[profileId] || {label: profileId || "드론", use: "임무 프로파일"};
}

function factoryDailyOutput(factory = {}) {
  const inventory = inventoryByFactoryId[factory.id] || {};
  const manufacturing = factory.manufacturing_profile || {};
  const capacity = factory.factory_capacity_profile || {};
  return Math.round(
    Number(inventory.max_daily_output_units || manufacturing.nominal_daily_output_units || capacity.predicted_output_units_30d / 30 || 0),
  );
}

function selectedFactoryIds(plan = currentPlan()) {
  return new Set((plan.selected_suppliers || []).map((supplier) => supplier.factory_id));
}

function isCoreOperatingAssemblyFactory(factory = {}) {
  return factory.assembly_operating_status === "core_operating" || factory.is_core_operating_assembly === true;
}

function isReserveAssemblyFactory(factory = {}) {
  return factory.assembly_operating_status === "reserve_standby" || factory.is_reserve_assembly_seed === true;
}

function assemblyReplacementActions(scenarioId = state.scenarioId) {
  return reconfigurationForScenario(scenarioId).assembly_replacement_actions || [];
}

function activeFactoryIds(plan = currentPlan()) {
  const ids = selectedFactoryIds(plan);
  (plan.route_segments || []).forEach((route) => {
    if (route.factory_id) ids.add(route.factory_id);
    if (route.destination_factory_id) ids.add(route.destination_factory_id);
  });
  (plan.port_to_factory_material_routes || []).forEach((route) => {
    if (route.target_factory_id) ids.add(route.target_factory_id);
  });
  (plan.resource_route_segments || []).forEach((route) => {
    if (route.target_factory_id) ids.add(route.target_factory_id);
  });
  assemblyReplacementActions(plan.id || state.scenarioId).forEach((action) => {
    if (action.from_factory_id) ids.add(action.from_factory_id);
    if (action.to_factory_id) ids.add(action.to_factory_id);
  });
  return ids;
}

function convergenceFactoryIds(plan = currentPlan()) {
  const ids = new Set();
  (plan.selected_suppliers || []).forEach((supplier) => {
    if (supplier.part_category === "drone_assembly" && supplier.factory_id) ids.add(supplier.factory_id);
    if (supplier.destination_factory_id) ids.add(supplier.destination_factory_id);
  });
  (plan.port_to_factory_material_routes || []).forEach((route) => {
    if (route.target_factory_id) ids.add(route.target_factory_id);
  });
  (plan.resource_route_segments || []).forEach((route) => {
    if (route.target_factory_id) ids.add(route.target_factory_id);
  });
  return ids;
}

function isConvergenceFactory(factory, plan = currentPlan()) {
  return Boolean(
    (factory.category === "drone_assembly" && !isReserveAssemblyFactory(factory)) ||
      (factory.is_priority_assembly_seed && !isReserveAssemblyFactory(factory)) ||
      convergenceFactoryIds(plan).has(factory.id),
  );
}

function factoryInCurrentScope(factory, activeIds = activeFactoryIds()) {
  return state.factoryScope === "all" || activeIds.has(factory.id);
}

function currentScenarioExcludedFactoryIds() {
  return currentScenarioFocusContext().excludedFactoryIds;
}

function currentScenarioDisabledPortIds() {
  return currentScenarioFocusContext().disabledPortIds;
}

function currentScenarioBlockedRouteIds() {
  return currentScenarioFocusContext().blockedRouteIds;
}

function currentScenarioHiddenRouteIds() {
  return currentScenarioFocusContext().hiddenRouteIds;
}

function currentScenarioForcedFactoryIds() {
  const context = currentScenarioFocusContext();
  const focus = context.focus;
  if (!context.active) return emptyScenarioSet;
  if (context.forcedFactoryIds) return context.forcedFactoryIds;
  const ids = new Set([
    ...(focus.factoryIds || []),
    ...(focus.activeFactoryIds || []),
    ...(focus.disabledFactoryIds || []),
    ...(focus.fitFactoryIds || []),
  ]);
  allPlanRoutes(currentPlan()).forEach((route) => {
    if (!routeAllowedByScenarioDisplay(route)) return;
    if (!routeShouldExposeEndpointNodes(route, focus)) return;
    routeFactoryIds(route).forEach((id) => ids.add(id));
  });
  context.forcedFactoryIds = ids;
  return ids;
}

function factoryAllowedByScenarioDisplay(factory = {}) {
  const context = currentScenarioFocusContext();
  if (!context.focus.hideExcludedFactories) return true;
  return !context.excludedFactoryIds.has(factory.id);
}

function routeBlockedByScenarioDisplay(route = {}) {
  return currentScenarioFocusContext().blockedRouteIds.has(route.id);
}

function routeTouchesDisabledPort(route = {}) {
  const context = currentScenarioFocusContext();
  return routePortIds(route).some((id) => context.disabledPortIds.has(id));
}

function routeAllowedByScenarioDisplay(route = {}) {
  const context = currentScenarioFocusContext();
  const focus = context.focus;
  if (context.hiddenRouteIds.has(route.id)) return false;
  if (focus.strictRouteIds && context.routeIds.size && !context.routeIds.has(route.id)) return false;
  if (focus.hideRoutesThroughExcludedFactories) {
    if (routeFactoryIds(route).some((id) => context.excludedFactoryIds.has(id))) return false;
  }
  if (focus.hideRoutesThroughDisabledPorts && route.route_type !== "maritime_import" && routeTouchesDisabledPort(route)) return false;
  if (focus.hideRoutesThroughThreatImpact && !context.blockedRouteIds.has(route.id)) {
    const routeCacheKey = route.id || `${route.route_type || "route"}:${routeFactoryIds(route).join(">")}`;
    if (context.threatRouteTouchCache.has(routeCacheKey)) {
      return !context.threatRouteTouchCache.get(routeCacheKey);
    }
    const threatPaths = focus.threatPaths || currentThreatPaths(currentPlan());
    const touchesImpact = routeTouchesThreatImpact(route, threatPaths, {
      circleRadiiKm: focus.threatCircleRadiiKm || [],
      circleRadiusKm: Number(focus.threatCircleRadiusKm || currentThreatRadiusKm(currentPlan())),
      corridorBufferKm: Number(focus.threatCorridorBufferKm || 0),
    });
    context.threatRouteTouchCache.set(routeCacheKey, touchesImpact);
    if (touchesImpact) return false;
  }
  return true;
}

function visibleFactories() {
  const activeIds = activeFactoryIds();
  const forcedIds = currentScenarioForcedFactoryIds();
  return factories.filter(
    (factory) =>
      (forcedIds.has(factory.id) || (state.visible[factory.category] && factoryInCurrentScope(factory, activeIds))) &&
      factoryAllowedByScenarioDisplay(factory),
  );
}

function factoryScopeCounts() {
  return {
    all: factories.length,
    active: activeFactoryIds().size,
    visible: visibleFactories().length,
  };
}

function selectedFactoryOperations(plan = currentPlan()) {
  const byFactory = new Map();
  (plan.selected_suppliers || []).forEach((supplier) => {
    const factory = factoryById[supplier.factory_id];
    if (!factory) return;
    if (!byFactory.has(factory.id)) {
      const inventory = inventoryByFactoryId[factory.id] || {};
      byFactory.set(factory.id, {
        factory,
        assignments: [],
        routes: [],
        inventory,
        requested: 0,
        dailyOutput: factoryDailyOutput(factory),
        risk: factoryRisk(factory, plan).risk,
      });
    }
    const row = byFactory.get(factory.id);
    row.assignments.push(supplier);
    row.requested += Number(supplier.requested_quantity || supplier.adjusted_capacity_units_30d || 0);
    row.risk = Math.max(row.risk, Number(supplier.risk || 0));
  });
  (plan.route_segments || []).forEach((route) => {
    const row = byFactory.get(route.factory_id);
    if (row) row.routes.push(route);
  });
  return [...byFactory.values()].sort((a, b) => {
    const priorityDelta = Number(b.factory.priority_weight || 0) - Number(a.factory.priority_weight || 0);
    if (priorityDelta) return priorityDelta;
    if (b.risk !== a.risk) return b.risk - a.risk;
    return Number(a.inventory.raw_material_days_on_hand || 99) - Number(b.inventory.raw_material_days_on_hand || 99);
  });
}

function companyQueueKey(factory = {}) {
  return String(factory.company_name || factory.display_name || factory.id || "")
    .split("/")[0]
    .replace(/\(주\)|주식회사|[\s·.,()-]/g, "")
    .toLowerCase();
}

function finalAssemblySiteScore(factory = {}, supplier = {}) {
  const siteText = [
    factory.priority_site_label,
    factory.priority_site_type,
    supplier.destination_site_label,
    factory.product_text,
  ].join(" ");
  const isCoreOperatingFactory = supplier.selection_basis === "core_domestic_drone_manufacturer_operating_factory";
  const hasFactorySignal = /공장|제조센터|제조기반|Manufacturing|manufacturing|테크센터|항공우주 제조|생산공장|생산기지|제조 인프라|기술원|R&D·제조거점|연구소\/공장/.test(
    siteText,
  );
  const weakSiteSignal = /연구소|지사|본사|교육원|전환 후보|가정/.test(siteText);
  return (
    Number(factory.priority_weight || supplier.priority_weight || 0) * 100 +
    Number(supplier.requested_quantity || supplier.adjusted_capacity_units_30d || 0) / 50 +
    Number(factory.factory_capacity_profile?.capacity_confidence || supplier.capacity_confidence || 0) * 10 +
    (factory.factory_capacity_profile?.capacity_tier === "A" ? 8 : 0) +
    (isCoreOperatingFactory ? 32 : 0) +
    (hasFactorySignal ? 18 : 0) -
    (!hasFactorySignal && weakSiteSignal ? 18 : 0)
  );
}

function isFinalAssemblyFactorySite(factory = {}, supplier = {}) {
  if (supplier.selection_basis === "core_domestic_drone_manufacturer_operating_factory") return true;
  const siteText = [
    factory.priority_site_label,
    factory.priority_site_type,
    supplier.destination_site_label,
    factory.product_text,
  ].join(" ");
  return /공장|제조센터|제조기반|Manufacturing|manufacturing|테크센터|항공우주 제조|생산공장|생산기지|제조 인프라|기술원|R&D·제조거점|연구소\/공장/.test(
    siteText,
  );
}

function selectedFinalAssemblyOperations(plan = currentPlan()) {
  const byCompany = new Map();
  (plan.selected_suppliers || [])
    .filter((supplier) => supplier.part_category === "drone_assembly")
    .forEach((supplier) => {
      const factory = factoryById[supplier.factory_id];
      if (!factory) return;
      if (!isFinalAssemblyFactorySite(factory, supplier)) return;
      const inventory = inventoryByFactoryId[factory.id] || {};
      const requested = Number(supplier.requested_quantity || supplier.adjusted_capacity_units_30d || supplier.capacity_units_30d || 0);
      const row = {
        factory,
        assignments: [supplier],
        routes: [supplier],
        inventory,
        requested,
        dailyOutput: factoryDailyOutput(factory),
        risk: Math.max(factoryRisk(factory, plan).risk, Number(supplier.risk || 0)),
        finalAssemblyScore: finalAssemblySiteScore(factory, supplier),
      };
      const key = companyQueueKey(factory);
      const current = byCompany.get(key);
      if (
        !current ||
        row.finalAssemblyScore > current.finalAssemblyScore ||
        (row.finalAssemblyScore === current.finalAssemblyScore && row.requested > current.requested) ||
        (row.finalAssemblyScore === current.finalAssemblyScore && row.requested === current.requested && row.dailyOutput > current.dailyOutput)
      ) {
        byCompany.set(key, row);
      }
    });
  return [...byCompany.values()].sort((a, b) => {
    if (b.requested !== a.requested) return b.requested - a.requested;
    if (b.finalAssemblyScore !== a.finalAssemblyScore) return b.finalAssemblyScore - a.finalAssemblyScore;
    return b.dailyOutput - a.dailyOutput;
  });
}

function alternativeFactories(factory, plan = currentPlan(), limit = 2) {
  const selectedIds = selectedFactoryIds(plan);
  const sourceIsAssembly = factory.category === "drone_assembly";
  const sourceCompanyKey = companyQueueKey(factory);
  return factories
    .filter((candidate) => candidate.category === factory.category && candidate.id !== factory.id && !selectedIds.has(candidate.id))
    .map((candidate) => ({
      factory: candidate,
      risk: factoryRisk(candidate, plan).risk,
      capacityIndex: Number(candidate.factory_capacity_profile?.capacity_index || candidate.confidence || 0),
      dailyOutput: factoryDailyOutput(candidate),
      isReserve: isReserveAssemblyFactory(candidate),
      sameCompany: sourceCompanyKey && sourceCompanyKey === companyQueueKey(candidate),
    }))
    .sort((a, b) => {
      if (sourceIsAssembly && a.isReserve !== b.isReserve) return a.isReserve ? -1 : 1;
      if (sourceIsAssembly && a.sameCompany !== b.sameCompany) return a.sameCompany ? -1 : 1;
      return a.risk - b.risk || b.capacityIndex - a.capacityIndex || b.dailyOutput - a.dailyOutput;
    })
    .slice(0, limit);
}

function fallbackRerouteSuggestions(plan = currentPlan()) {
  const replacementRoutes = assemblyReplacementActions(plan.id || state.scenarioId)
    .map((action) => {
      const fromFactory = factoryById[action.from_factory_id];
      const toFactory = factoryById[action.to_factory_id];
      if (!fromFactory || !toFactory) return null;
      return {
        id: action.action_id || `reserve_${fromFactory.id}_${toFactory.id}`,
        fromFactory,
        toFactory,
        from: action.from || {lat: fromFactory.lat, lon: fromFactory.lon},
        to: action.to || {lat: toFactory.lat, lon: toFactory.lon},
        risk: Number(action.from_scenario_risk || factoryRisk(fromFactory, plan).risk || 0),
        action,
      };
    })
    .filter(Boolean);
  if (replacementRoutes.length) return replacementRoutes.slice(0, 10);
  if (!currentThreatPaths(plan).length) return [];
  return selectedFactoryOperations(plan)
    .filter((row) => row.risk >= 0.44)
    .map((row) => {
      const alternative = alternativeFactories(row.factory, plan, 1)[0]?.factory;
      if (!alternative) return null;
      return {
        id: `fallback_${row.factory.id}_${alternative.id}`,
        fromFactory: row.factory,
        toFactory: alternative,
        from: {lat: row.factory.lat, lon: row.factory.lon},
        to: {lat: alternative.lat, lon: alternative.lon},
        risk: row.risk,
      };
    })
    .filter(Boolean)
    .slice(0, 10);
}

function arrowAngleDeg(from, to) {
  const dx = to.lon - from.lon;
  const dy = to.lat - from.lat;
  return Math.atan2(dy, dx) * (180 / Math.PI);
}

function buildFactoryStatus() {
  const plan = currentPlan();
  const ops = selectedFinalAssemblyOperations(plan);
  const totalDaily = ops.reduce((sum, row) => sum + row.dailyOutput, 0);
  const totalWip = ops.reduce((sum, row) => sum + Number(row.inventory.wip_units || 0), 0);
  const totalAvailable = ops.reduce((sum, row) => sum + Number(row.inventory.available_to_ship_units || 0), 0);
  const highRisk = ops.filter((row) => row.risk >= 0.44 || Number(row.inventory.raw_material_days_on_hand || 99) <= 6).length;
  return {plan, ops, totalDaily, totalWip, totalAvailable, highRisk};
}

function droneProgressRows() {
  const plan = currentPlan();
  const scale = currentScenarioScale();
  const assemblyInventory = inventoryWip.filter((row) => row.part_category === "drone_assembly");
  const assemblyAvailable = assemblyInventory.reduce((sum, row) => sum + Number(row.available_to_ship_units || 0), 0);
  const assemblyWip = assemblyInventory.reduce((sum, row) => sum + Number(row.wip_units || 0), 0);
  return (data.drone_mission_profiles || []).map((profile) => {
    const text = missionText(profile.profile_id);
    const target = Math.round(Number(state.targetDrones || plan.target_drones || 0) * Number(profile.default_mix_share || 0));
    const feasible = Math.round(Number(plan.possible_drones_30d || 0) * Number(profile.default_mix_share || 0) * scale);
    const completed = Math.min(target, Math.round(assemblyAvailable * Number(profile.default_mix_share || 0)));
    const wip = Math.round(assemblyWip * Number(profile.default_mix_share || 0));
    const prepared = Math.min(target, completed + Math.round(wip * 0.62) + Math.round(feasible * 0.16));
    const progress = target ? Math.min(1, prepared / target) : 0;
    const assemblyRoutes = selectedFinalAssemblyOperations(plan).map((row) => row.assignments[0]).filter(Boolean);
    return {profile, text, target, feasible, completed, wip, prepared, progress, assemblyRoutes};
  });
}

function unitDemandRows() {
  const plan = currentPlan();
  const droneRows = Object.fromEntries(droneProgressRows().map((row) => [row.profile.profile_id, row]));
  return syntheticUnitDemandProfiles
    .map((unit) => {
      const drone = droneRows[unit.profile_id] || {};
      const requested = Math.max(1, Math.round(Number(drone.target || state.targetDrones || 0) * unit.share));
      const prepared = Math.min(requested, Math.round(Number(drone.prepared || 0) * unit.share));
      const shortage = Math.max(0, requested - prepared);
      const shortageRatio = requested ? shortage / requested : 0;
      const assemblyRoutes = selectedFinalAssemblyOperations(plan).map((row) => row.assignments[0]).filter(Boolean);
      const finalAssemblyFactory = factoryById[assemblyRoutes[0]?.factory_id] || {};
      const priority = Number(unit.urgency || 0) + shortageRatio + 1 / Math.max(1, Number(unit.deadline_day || 1));
      return {...unit, drone, requested, prepared, shortage, shortageRatio, priority, finalAssemblyFactory, assemblyRoutes};
    })
    .sort((a, b) => b.priority - a.priority);
}

function procurementRows() {
  const plan = currentPlan();
  return (plan.raw_material_supply_summary || [])
    .map((item) => {
      const required = Math.round(Number(item.required_kg_30d || 0) * currentScenarioScale());
      const available = Number(item.total_available_kg_30d || 0);
      const coverage = required ? Math.min(1, available / required) : 0;
      const shortage = Math.max(0, required - available);
      const maritimeRoutes = (plan.maritime_import_route_segments || []).filter((route) => (route.material_ids || []).includes(item.material_id));
      const roadRoutes = (plan.port_to_factory_material_routes || []).filter((route) => route.material_id === item.material_id);
      const topRisk = Math.max(0, ...maritimeRoutes.map((route) => Number(route.risk_score || 0)));
      return {...item, required, available, coverage, shortage, maritimeRoutes, roadRoutes, topRisk};
    })
    .sort((a, b) => b.shortage - a.shortage || a.coverage - b.coverage || b.topRisk - a.topRisk);
}

function sheetSection(title, subtitle, contentHtml) {
  return `
    <section class="ops-sheet-section">
      <div class="ops-sheet-section-head">
        <h3>${escapeHtml(title)}</h3>
        ${subtitle ? `<span>${escapeHtml(subtitle)}</span>` : ""}
      </div>
      ${contentHtml}
    </section>
  `;
}

function sheetMetrics(items) {
  return `
    <div class="ops-sheet-metrics">
      ${items
        .map(
          (item) => `
            <span class="${item.warn ? "is-warn" : ""}">
              <strong>${escapeHtml(item.value)}</strong>
              <small>${escapeHtml(item.label)}</small>
            </span>
          `,
        )
        .join("")}
    </div>
  `;
}

function compactNote(text) {
  if (!text) return "";
  return `
    <details class="ops-route-note">
      <summary>근거 보기</summary>
      <p>${escapeHtml(text)}</p>
    </details>
  `;
}

function routeCard({title, subtitle = "", stats = [], routeId = "", factoryId = "", materialId = "", status = "", warning = false, note = ""}) {
  return `
    <article class="ops-route-card ${warning ? "is-warn" : ""}" tabindex="0" data-hover-route="${escapeHtml(routeId)}" data-hover-factory="${escapeHtml(
      factoryId,
    )}" data-hover-material="${escapeHtml(materialId)}">
      <div class="ops-route-card-head">
        <div>
          <strong>${escapeHtml(title)}</strong>
          ${subtitle ? `<small>${escapeHtml(subtitle)}</small>` : ""}
        </div>
        ${status ? `<em>${escapeHtml(status)}</em>` : ""}
      </div>
      <div class="ops-route-card-metrics">
        ${stats
          .map(
            (item) => `
              <span class="${item.warn ? "is-warn" : ""}">
                <b>${escapeHtml(item.value)}</b>
                <small>${escapeHtml(item.label)}</small>
              </span>
            `,
          )
          .join("")}
      </div>
      ${compactNote(note)}
    </article>
  `;
}

function routeCardList(cardsHtml) {
  return `<div class="ops-route-card-list">${cardsHtml || `<p class="ops-sheet-empty">표시할 상세 후보가 없습니다.</p>`}</div>`;
}

function planRouteForSupplier(supplier = {}) {
  return (currentPlan().route_segments || []).find(
    (route) => route.factory_id === supplier.factory_id && route.part_category === supplier.part_category,
  );
}

function opsMapFocusContext() {
  const context = {
    active: Boolean(state.opsDetail.open),
    factoryIds: new Set(),
    routeIds: new Set(),
    materialIds: new Set(),
    disabledFactoryIds: new Set(),
    activeFactoryIds: new Set(),
  };
  addScenarioFocusToContext(context);
  addAssemblyReplacementFocusToContext(context);
  if (!context.active) return context;
  const addRoute = (route = {}) => addRouteToFocusContext(context, route);
  if (state.opsDetail.hoverRouteId) context.routeIds.add(state.opsDetail.hoverRouteId);
  if (state.opsDetail.hoverFactoryId) context.factoryIds.add(state.opsDetail.hoverFactoryId);
  if (state.opsDetail.hoverMaterialId) context.materialIds.add(state.opsDetail.hoverMaterialId);

  if (state.opsDetail.kind === "factory") {
    if (state.opsDetail.itemId) {
      context.factoryIds.add(state.opsDetail.itemId);
      (currentPlan().route_segments || [])
        .filter((route) => route.factory_id === state.opsDetail.itemId || route.destination_factory_id === state.opsDetail.itemId)
        .forEach(addRoute);
      (currentPlan().port_to_factory_material_routes || [])
        .filter((route) => route.target_factory_id === state.opsDetail.itemId)
        .forEach(addRoute);
      (currentPlan().resource_route_segments || [])
        .filter((route) => route.target_factory_id === state.opsDetail.itemId)
        .forEach(addRoute);
    }
    const rows = buildFactoryStatus().ops;
    const focused = state.opsDetail.itemId ? rows.filter((row) => row.factory.id === state.opsDetail.itemId) : rows.slice(0, 10);
    focused.forEach((row) => {
      context.factoryIds.add(row.factory.id);
      row.routes.forEach(addRoute);
    });
  }

  if (state.opsDetail.kind === "drone") {
    const rows = state.opsDetail.itemId
      ? droneProgressRows().filter((row) => row.profile.profile_id === state.opsDetail.itemId)
      : droneProgressRows();
    rows.forEach((row) => {
      row.assemblyRoutes.slice(0, 8).forEach((route) => {
        context.factoryIds.add(route.factory_id);
        addRoute(planRouteForSupplier(route));
      });
    });
  }

  if (state.opsDetail.kind === "unit") {
    const rows = state.opsDetail.itemId ? unitDemandRows().filter((unit) => unit.id === state.opsDetail.itemId) : unitDemandRows();
    rows.forEach((unit) => {
      unit.assemblyRoutes.slice(0, 8).forEach((route) => {
        context.factoryIds.add(route.factory_id);
        addRoute(planRouteForSupplier(route));
      });
    });
  }

  if (state.opsDetail.kind === "procurement") {
    const rows = state.opsDetail.itemId
      ? procurementRows().filter((row) => row.material_id === state.opsDetail.itemId)
      : procurementRows().slice(0, 4);
    rows.forEach((row) => {
      context.materialIds.add(row.material_id);
      row.maritimeRoutes.forEach(addRoute);
      row.roadRoutes.slice(0, 8).forEach(addRoute);
    });
  }
  return context;
}

function routeIsContextFocused(route, context) {
  if (!context.active) return false;
  return (
    (route.id && context.routeIds.has(route.id)) ||
    routeFactoryIds(route).some((id) => context.factoryIds.has(id)) ||
    routeMaterialIds(route).some((id) => context.materialIds.has(id))
  );
}

function renderTopbar() {
  const stats = data.stats || {};
  const rows = stats.raw_factory_rows || 0;
  elementById("topbarStatus").innerHTML = `
    <span class="status-pill">${escapeHtml(data.schema || "demo")}</span>
    <span class="metric-pill">${fmt(rows)} public rows</span>
    <span class="metric-pill">${fmt(stats.full_factory_candidate_pool_count || factories.length)} full candidates</span>
    <span class="metric-pill">${fmt(stats.pipeline_shortlist_candidate_count || 0)} shortlist candidates</span>
    <span class="metric-pill">${fmt(factories.length)} demo factories</span>
    <span class="metric-pill">${fmt(resources.length)} resource nodes</span>
    <span class="metric-pill">${fmt(stats.grid_risk_zone_count || gridRiskZones.length)} grid risk zones</span>
    <span class="metric-pill">${fmt((stats.frozen_order_count || frozenOrders.length) + (stats.in_transit_shipment_count || inTransitShipments.length))} ops records</span>
    <span class="metric-pill">${fmt((stats.direct_factory_energy_matches || 0) + (stats.direct_resource_energy_matches || 0))} direct energy matches</span>
    <span class="metric-pill">${fmt(stats.raw_material_count || Object.keys(rawMaterialCatalog).length)} raw materials</span>
    <span class="metric-pill">${fmt(stats.maritime_import_route_count || 0)} maritime routes</span>
    <span class="metric-pill">${fmt(stats.allied_supply_source_count || alliedSupplySources.length)} allied sources</span>
    <span class="metric-pill">${fmt(stats.component_count || Object.keys(componentCatalog).length)} components</span>
    <span class="metric-pill">${fmt(stats.subcomponent_count || Object.keys(subcomponentCatalog).length)} subcomponents</span>
    <span class="status-pill warning">verification required</span>
  `;
}

function renderScenarioTabs() {
  elementById("scenarioTabs").innerHTML = plans
    .map(
      (plan) => `
        <button class="scenario-button ${plan.id === state.scenarioId ? "is-active" : ""}" data-scenario="${escapeHtml(plan.id)}" type="button">
          <span>${escapeHtml(plan.short_name || plan.name)}</span>
          <small>${escapeHtml(plan.threat ? plan.threat.label : "예측 위협 회랑 없음")}</small>
        </button>
      `,
    )
    .join("");

  elementById("scenarioTabs").querySelectorAll("[data-scenario]").forEach((button) => {
    button.addEventListener("click", () => {
      setScenario(button.dataset.scenario);
    });
  });
}

function renderScenarioLiveTabs() {
  const element = elementById("scenarioLiveTabs");
  if (!element) return;
  const buttons = plans
    .map((plan) => {
      const narrative = scenarioCaseNarratives[plan.id] || {};
      return `
        <button class="header-scenario-button ${
          state.viewMode === "scenario" && plan.id === state.scenarioId ? "is-active" : ""
        }" data-scenario="${escapeHtml(plan.id)}" type="button">
          <strong>${escapeHtml(plan.short_name || plan.name || plan.id)}</strong>
          <span>${escapeHtml(narrative.phase || plan.threat?.label || "case")}</span>
        </button>
      `;
    })
    .join("");
  element.innerHTML = `
    <button class="header-scenario-button default-mode ${state.viewMode === "default" ? "is-active" : ""}" id="defaultModeButton" type="button">
      <strong>Default</strong>
      <span>운영 화면</span>
    </button>
    ${buttons}
    <button class="header-scenario-button playback ${state.playbackActive ? "is-active" : ""}" id="scenarioPlaybackButton" type="button">
      <strong>${state.playbackActive ? "정지" : "재생"}</strong>
      <span>case loop</span>
    </button>
  `;

  elementById("defaultModeButton")?.addEventListener("click", () => setViewMode("default"));
  element.querySelectorAll("[data-scenario]").forEach((button) => {
    button.addEventListener("click", () => setScenario(button.dataset.scenario));
  });
  elementById("scenarioPlaybackButton")?.addEventListener("click", toggleScenarioPlayback);
}

function renderCaseTicker() {
  const element = elementById("caseTicker");
  if (!element) return;
  const plan = currentPlan();
  const optimization = currentOptimizationResult();
  const reconfiguration = currentReconfigurationResult();
  const objective = optimization?.objective_breakdown || {};
  const metrics = reconfiguration?.delta_metrics || {};
  const levelLabel = {
    monitor: "모니터링",
    replan_review: "재계획 검토",
    emergency_replan: "긴급 재계획",
  }[reconfiguration?.reconfiguration_level] || reconfiguration?.reconfiguration_level || "검토";
  const ids = scenarioIds();
  const scenarioIndex = Math.max(0, ids.indexOf(state.scenarioId));
  const stages = currentScenarioStages();
  const stageIndex = Math.max(0, Math.min(Number(state.scenarioStageIndex || 0), stages.length - 1));
  const stage = stages[stageIndex] || currentScenarioNarrative();
  element.classList.toggle("is-alert-stage", Boolean(stage.alert));
  const stageMetric = stage.metric || {label: "재구성", value: metrics.added_factory_count || metrics.rerouted_flow_count || 0};
  const stageMetricValue = typeof stageMetric.value === "number" ? fmt(stageMetric.value) : escapeHtml(stageMetric.value ?? "0");
  const stageRows = stages
    .map(
      (step, index) => `
        <button class="case-step-dot ${index === stageIndex ? "is-active" : ""}" data-case-stage="${index}" type="button">
          <strong>${escapeHtml(step.code || `${scenarioIndex + 1}-${index + 1}`)}</strong>
          <span>${escapeHtml(step.title || "")}</span>
        </button>
      `,
    )
    .join("");

  element.innerHTML = `
    <button class="case-slide-button" data-case-shift="-1" type="button" aria-label="이전 시나리오">←</button>
    <div class="case-body">
      ${
        stage.alert
          ? `
            <div class="case-alert-strip">
              <b>${escapeHtml(stage.alert.label || "ALERT")}</b>
              <span>${escapeHtml(stage.alert.title || stage.title)}</span>
              <small>${escapeHtml(stage.alert.mission || stage.action || "")}</small>
            </div>
          `
          : ""
      }
      <div class="case-heading">
        <div>
          <p class="panel-kicker">Scenario Case ${escapeHtml(stage.code || `${scenarioIndex + 1}-${stageIndex + 1}`)} / ${fmt(stages.length || 1)}</p>
          <h2>${escapeHtml(stage.title)}</h2>
          <span>${escapeHtml(stage.phase)} · ${escapeHtml(levelLabel)}</span>
        </div>
      </div>
      <div class="case-metrics">
        <span><strong>${fmt(objective.feasible_output_units_30d || plan.possible_drones_30d || 0)}</strong><small>가능 수량</small></span>
        <span><strong>${fmt(objective.output_gap_units_30d || 0)}</strong><small>부족</small></span>
        <span><strong>${pct(objective.weighted_route_risk || 0)}</strong><small>경로 위험</small></span>
        <span><strong>${stageMetricValue}</strong><small>${escapeHtml(stageMetric.label || "단계 지표")}</small></span>
      </div>
      <div class="case-action-grid">
        <div><b>상황</b><span>${escapeHtml(stage.situation || stage.caseSignal || "")}</span></div>
        <div><b>조치사항</b><span>${escapeHtml(stage.action || stage.operatorFocus || "")}</span></div>
      </div>
      <div class="case-stage-track">${stageRows}</div>
      <div class="case-footer">
        <span>${escapeHtml(stage.algorithm || stage.logicChange || "")}</span>
        <button class="case-open-dataset" id="caseOpenDataset" type="button">근거</button>
      </div>
    </div>
    <button class="case-slide-button" data-case-shift="1" type="button" aria-label="다음 시나리오">→</button>
  `;

  element.querySelectorAll("[data-case-shift]").forEach((button) => {
    button.addEventListener("click", () => shiftScenarioStage(Number(button.dataset.caseShift || 0)));
  });
  element.querySelectorAll("[data-case-stage]").forEach((button) => {
    button.addEventListener("click", () => {
      if (state.playbackActive) stopScenarioPlayback({rerender: false});
      state.scenarioStageIndex = Number(button.dataset.caseStage || 0);
      applyCurrentScenarioLayerPreset();
      renderAll();
      if (mapState.map) fitMap();
    });
  });
  elementById("caseOpenDataset")?.addEventListener("click", () => setDrawerOpen("datasetInfoDrawer", true));
}

function renderDemandControl() {
  const input = elementById("targetInput");
  if (!input) return;
  input.value = state.targetDrones;
  input.addEventListener("input", () => {
    state.targetDrones = Number(input.value || currentPlan().target_drones || 10000);
    renderMapMeta();
    renderPlanSummary();
    renderOptimizationResultSummary();
    renderReconfigurationSummary();
    renderMaterialSupplySummary();
    renderDecisionCards();
    if (state.selectedKind) renderSelectedDetails();
    renderFlowLedger();
  });
}

function renderLayerToggles() {
  const activeIds = activeFactoryIds();
  const scopedFactories = factories.filter((factory) => factoryInCurrentScope(factory, activeIds));
  const counts = scopedFactories.reduce((memo, factory) => {
    memo[factory.category] = (memo[factory.category] || 0) + 1;
    return memo;
  }, {});
  const resourceCounts = resources.reduce((memo, resource) => {
    memo[resource.resource_category] = (memo[resource.resource_category] || 0) + 1;
    return memo;
  }, {});
  const partToggles = Object.entries(categories)
    .map(([key, category]) => {
      const korean = partCategoryText(key, category);
      return `
        <label class="layer-toggle">
          <input type="checkbox" data-layer="${escapeHtml(key)}" ${state.visible[key] ? "checked" : ""} />
          <span>
            <span class="layer-name">${escapeHtml(korean.label)}</span>
            <span class="layer-copy">${escapeHtml(korean.role)}</span>
          </span>
          <span class="layer-count">${fmt(counts[key] || 0)}</span>
        </label>
      `;
    })
    .join("");
  const resourceToggles = Object.entries(resourceCategories)
    .map(([key, category]) => {
      const korean = resourceCategoryText(key, category);
      return `
        <label class="layer-toggle resource-toggle">
          <input type="checkbox" data-resource-layer="${escapeHtml(key)}" ${state.resourceVisible[key] ? "checked" : ""} />
          <span>
            <span class="layer-name">${escapeHtml(korean.label)}</span>
            <span class="layer-copy">${escapeHtml(korean.role)}</span>
          </span>
          <span class="layer-count">${fmt(resourceCounts[key] || 0)}</span>
        </label>
      `;
    })
    .join("");
  const plan = currentPlan();
  const materialRouteCount =
    Number(plan.maritime_import_route_segments?.length || 0) + Number(plan.port_to_factory_material_routes?.length || 0);
  elementById("layerToggles").innerHTML = `
    <div class="toggle-section-heading">
      <p class="toggle-section-title">공장 구성</p>
      <div class="toggle-bulk-actions">
        <button class="mini-action-button" data-all-layers="on" type="button">전체 선택</button>
        <button class="mini-action-button" data-all-layers="off" type="button">전체 해제</button>
      </div>
    </div>
    ${partToggles}
    <p class="toggle-section-title">핵심 원료/자원</p>
    ${resourceToggles}
    <p class="toggle-section-title">원료 수급 경로</p>
    <label class="layer-toggle material-toggle">
      <input type="checkbox" data-material-routes ${state.materialRoutesVisible ? "checked" : ""} />
      <span>
        <span class="layer-name">수입항-공장 원료 경로</span>
        <span class="layer-copy">한-일 해상 수급로, 수입항, 공장 연결 경로</span>
      </span>
      <span class="layer-count">${fmt(materialRouteCount)}</span>
    </label>
  `;

  elementById("layerToggles").querySelectorAll("[data-all-layers]").forEach((button) => {
    button.addEventListener("click", () => {
      setAllLayerVisibility(button.dataset.allLayers === "on");
    });
  });
  elementById("layerToggles").querySelectorAll("[data-layer]").forEach((input) => {
    input.addEventListener("change", () => {
      state.visible[input.dataset.layer] = input.checked;
      renderMap();
      renderFlowLedger();
    });
  });
  elementById("layerToggles").querySelectorAll("[data-resource-layer]").forEach((input) => {
    input.addEventListener("change", () => {
      state.resourceVisible[input.dataset.resourceLayer] = input.checked;
      renderMap();
      renderFlowLedger();
    });
  });
  elementById("layerToggles").querySelectorAll("[data-material-routes]").forEach((input) => {
    input.addEventListener("change", () => {
      state.materialRoutesVisible = input.checked;
      renderMap();
      renderFlowLedger();
      renderMaterialSupplySummary();
    });
  });
}

function renderSafeBoundary() {
  elementById("safeBoundary").innerHTML = `
    <p class="panel-kicker">Safety Boundary</p>
    <ul>
      <li><span class="safe-dot"></span><span>무장·탄두·세부 제작 사양은 포함하지 않는 상위 부품군 데모입니다.</span></li>
      <li><span class="safe-dot"></span><span>공장 후보는 공개 데이터 기반 추정이며 실제 전환 가능성은 현장 검증이 필요합니다.</span></li>
      <li><span class="safe-dot"></span><span>희토류·폐배터리·전자스크랩 노드는 원재료 후보 큐이며 실제 회수 공정과 허가는 별도 확인 대상입니다.</span></li>
      <li><span class="safe-dot"></span><span>해상 수입로는 공개 시연용 물류 회랑이며 실제 선박 운용·호송·작전 경로가 아닙니다.</span></li>
      <li><span class="safe-dot"></span><span>위협 회랑은 시연용 합성 가정이며 실제 정보 판단이 아닙니다.</span></li>
    </ul>
  `;
}

function renderMapMeta() {
  const plan = currentPlan();
  const possible = plan.possible_drones_30d || 0;
  const shortfall = Math.max(0, Number(state.targetDrones || 0) - possible);
  const mapSummary = elementById("mapSummaryCompact");
  const mapSummaryShell = mapSummary?.closest(".map-summary");
  const showScenarioSummary = state.viewMode === "scenario";
  elementById("mapTitle").textContent = plan.name || "Production Plan";
  if (mapSummaryShell) mapSummaryShell.hidden = !showScenarioSummary;
  if (!showScenarioSummary) {
    if (mapSummary) mapSummary.innerHTML = "";
    elementById("mapMetaStrip").innerHTML = "";
    elementById("summaryPopover").hidden = true;
    return;
  }
  if (mapSummary) {
    mapSummary.innerHTML = `
      <strong>${fmt(state.targetDrones)}</strong> target
      <span>${fmt(possible)} feasible</span>
      <span class="${shortfall ? "summary-warn" : ""}">${fmt(shortfall)} gap</span>
    `;
  }
  elementById("mapMetaStrip").innerHTML = `
    <span class="status-pill">${fmt(state.targetDrones)} target drones</span>
    <span class="status-pill">${fmt(possible)} feasible by bottleneck</span>
    <span class="status-pill ${shortfall ? "warning" : ""}">${fmt(shortfall)} shortfall</span>
    <span class="status-pill muted">${escapeHtml(plan.recommendation || "")}</span>
  `;
}

function markerIcon(factory, opsFocus = opsMapFocusContext(), plan = currentPlan()) {
  const risk = factoryRisk(factory).risk;
  const selected = state.selectedKind === "factory" && factory.id === state.selectedFactoryId ? "is-selected" : "";
  const focused = opsFocus.active && opsFocus.factoryIds.has(factory.id) ? "is-context-highlight" : "";
  const disabled = opsFocus.active && opsFocus.disabledFactoryIds?.has(factory.id) ? "is-disabled-node" : "";
  const activeAlternate = opsFocus.active && opsFocus.activeFactoryIds?.has(factory.id) ? "is-alternate-node" : "";
  const faded = opsFocus.active && !opsFocus.factoryIds.has(factory.id) ? "is-context-faded" : "";
  const convergenceNode = isConvergenceFactory(factory, plan);
  const reserveNode = isReserveAssemblyFactory(factory);
  const convergence = convergenceNode ? "is-convergence" : "";
  const reserve = reserveNode ? "is-reserve-node" : "";
  const threatened = risk > 0.44 && currentThreatPaths(plan).length ? "is-threatened" : "";
  const riskClass = risk > 0.44 ? "is-risk" : "";
  const enlarged = selected || focused || disabled || activeAlternate;
  const size = disabled ? 38 : enlarged ? (convergenceNode || reserveNode ? 34 : 28) : convergenceNode ? 28 : reserveNode ? 22 : 18;
  const anchor = size / 2;
  return L.divIcon({
    className: "",
    html: `<span class="factory-marker cat-${escapeHtml(factory.category)} ${selected} ${focused} ${disabled} ${activeAlternate} ${faded} ${convergence} ${reserve} ${threatened} ${riskClass}"></span>`,
    iconSize: [size, size],
    iconAnchor: [anchor, anchor],
    popupAnchor: [0, -10],
  });
}

function resourceIcon(resource) {
  const selected = state.selectedKind === "resource" && resource.id === state.selectedResourceId ? "is-selected" : "";
  return L.divIcon({
    className: "",
    html: `<span class="resource-marker cat-${escapeHtml(resource.resource_category)} ${selected}"></span>`,
    iconSize: selected ? [28, 28] : [22, 22],
    iconAnchor: selected ? [14, 14] : [11, 11],
    popupAnchor: [0, -12],
  });
}

function importPortIcon(port = {}) {
  const disabled = currentScenarioDisabledPortIds().has(port.id);
  const className = disabled ? "is-disabled-port" : "";
  const size = disabled ? 34 : 26;
  const anchor = size / 2;
  return L.divIcon({
    className: "",
    html: `<span class="import-port-marker ${className}"></span>`,
    iconSize: [size, size],
    iconAnchor: [anchor, anchor],
    popupAnchor: [0, -12],
  });
}

function foreignMaterialIcon(source) {
  const materialId = source.material_ids?.[0];
  return L.divIcon({
    className: "",
    html: `<span class="foreign-material-marker" style="--marker-color:${escapeHtml(materialColor(materialId))}"></span>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -10],
  });
}

function flowDotIcon(category, status, color = "") {
  const style = color ? ` style="background:${escapeHtml(color)}"` : "";
  return L.divIcon({
    className: "",
    html: `<span class="flow-dot cat-${escapeHtml(category)} ${escapeHtml(status)}"${style}></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
}

function fallbackArrowIcon(angle) {
  return L.divIcon({
    className: "",
    html: `<span class="fallback-arrow-marker" style="transform: rotate(${Number(angle || 0)}deg)"></span>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
}

function blockadeShipIcon(angle = 0) {
  return L.divIcon({
    className: "",
    html: `<span class="blockade-ship-marker" style="transform: rotate(${Number(angle || 0)}deg)"></span>`,
    iconSize: [34, 22],
    iconAnchor: [17, 11],
    popupAnchor: [0, -12],
  });
}

function visibleRoutes() {
  return (currentPlan().route_segments || []).filter(
    (route) => state.visible[route.part_category] && hasRoadGeometry(route) && routeAllowedByScenarioDisplay(route),
  );
}

function visibleResourceRoutes() {
  return (currentPlan().resource_route_segments || []).filter(
    (route) => state.resourceVisible[route.resource_category] && hasRoadGeometry(route) && routeAllowedByScenarioDisplay(route),
  );
}

function materialNetworkForcedVisible() {
  const focus = currentScenarioFocus();
  return Boolean(
    focus.includeTrade ||
      focus.blockade ||
      (focus.disabledPortIds || []).length ||
      (focus.blockedRouteIds || []).length ||
      (focus.hiddenRouteIds || []).length,
  );
}

function visibleMaritimeRoutes() {
  return state.materialRoutesVisible || materialNetworkForcedVisible()
    ? (currentPlan().maritime_import_route_segments || []).filter(routeAllowedByScenarioDisplay)
    : [];
}

function visiblePortMaterialRoutes() {
  return state.materialRoutesVisible || materialNetworkForcedVisible()
    ? (currentPlan().port_to_factory_material_routes || []).filter((route) => hasRoadGeometry(route) && routeAllowedByScenarioDisplay(route))
    : [];
}

function topAnimatedRoutes(focusContext = opsMapFocusContext()) {
  const routes = [...visibleRoutes(), ...visibleResourceRoutes(), ...visiblePortMaterialRoutes(), ...visibleMaritimeRoutes()].filter(
    (route) => !routeBlockedByScenarioDisplay(route),
  );
  const scopedRoutes = focusContext.active ? routes.filter((route) => routeIsContextFocused(route, focusContext)) : routes;
  return (scopedRoutes.length ? scopedRoutes : routes)
    .sort(
      (a, b) =>
        (b.quantity || b.quantity_kg_30d || b.import_capacity_kg_30d || 0) -
        (a.quantity || a.quantity_kg_30d || a.import_capacity_kg_30d || 0),
    )
    .slice(0, 24);
}

function clearFlowAnimation() {
  if (mapState.animationFrame) {
    cancelAnimationFrame(mapState.animationFrame);
    mapState.animationFrame = null;
  }
  mapState.flowMarkers.forEach((marker) => marker.remove());
  mapState.flowMarkers = [];
}

function startFlowAnimation(routes) {
  clearFlowAnimation();
  if (!mapState.map || !routes.length) return;
  const animated = routes.map((route, index) => {
    const category = route.part_category || route.resource_category || route.material_id || route.material_ids?.[0] || "material";
    const color = routeFlowColor(route);
    const marker = L.marker([route.from.lat, route.from.lon], {
      icon: flowDotIcon(category, route.status, color),
      interactive: false,
      keyboard: false,
    }).addTo(mapState.map);
    return {
      marker,
      route,
      offset: (index * 0.137) % 1,
      speed: 0.000035 + (index % 5) * 0.000006,
    };
  });
  mapState.flowMarkers = animated.map((item) => item.marker);

  let lastTime = performance.now();
  function animate(now) {
    const delta = now - lastTime;
    lastTime = now;
    animated.forEach((item) => {
      item.offset = (item.offset + delta * item.speed) % 1;
      const point = routeMidpoint(item.route, item.offset);
      item.marker.setLatLng([point.lat, point.lon]);
    });
    mapState.animationFrame = requestAnimationFrame(animate);
  }
  mapState.animationFrame = requestAnimationFrame(animate);
}

function renderMap() {
  if (!mapState.map) {
    mapState.map = L.map("productionMap", {
      zoomControl: false,
      preferCanvas: true,
    }).setView([36.45, 127.95], 7);
    L.control.zoom({position: "bottomleft"}).addTo(mapState.map);
    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      attribution:
        "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
      maxZoom: 19,
    }).addTo(mapState.map);
    L.tileLayer(
      "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      {
        attribution: "Boundaries and places &copy; Esri",
        maxZoom: 19,
        pane: "tilePane",
        opacity: 0.78,
      },
    ).addTo(mapState.map);
    mapState.map.on("click", () => {
      if (state.opsDetail.open) closeOpsSheet();
    });
    updatePresetButtons();
  }
  if (mapState.layerGroup) mapState.layerGroup.remove();
  mapState.layerGroup = L.layerGroup().addTo(mapState.map);

  const plan = currentPlan();
  const opsFocus = opsMapFocusContext();
  const scenarioFocus = currentScenarioFocus();
  const threatPaths = currentThreatPaths(plan);

  if (threatPaths.length) {
    const threatCircleRadiusKm = Number.isFinite(Number(scenarioFocus.threatCircleRadiusKm))
      ? Number(scenarioFocus.threatCircleRadiusKm)
      : currentThreatRadiusKm(plan) * 0.28;
    const threatCircleRadiiKm = scenarioFocus.threatCircleRadiiKm || [];
    threatPaths.forEach((path, pathIndex) => {
      const points = path.map((point) => [point.lat, point.lon]);
      L.polyline(points, {
        color: routeTypeColor("threat"),
        weight: pathIndex === 0 ? 5 : 3.6,
        opacity: pathIndex === 0 ? 0.9 : 0.72,
        className: "threat-line",
      }).addTo(mapState.layerGroup);
      path.forEach((point, index) => {
        const radiusKm = threatCircleRadiusForPoint(point, threatCircleRadiiKm, pathIndex, index, threatCircleRadiusKm);
        L.circle([point.lat, point.lon], {
          radius: radiusKm * 1000,
          color: routeTypeColor("threat"),
          fillColor: routeTypeColor("threat"),
          fillOpacity: index % 2 ? 0.04 : 0.07,
          weight: 1,
        }).addTo(mapState.layerGroup);
      });
    });
  }

  (scenarioFocus.emphasisCircles || []).forEach((circle) => {
    L.circle([circle.lat, circle.lon], {
      radius: Number(circle.radiusKm || 80) * 1000,
      color: routeTypeColor("fallback"),
      fillColor: routeTypeColor("fallback"),
      fillOpacity: 0.05,
      opacity: 0.82,
      weight: 2.2,
      dashArray: "8 10",
    }).addTo(mapState.layerGroup);
  });

  if (scenarioFocus.blockade?.line?.length) {
    const blockade = scenarioFocus.blockade;
    L.polyline(blockade.line.map((point) => [point.lat, point.lon]), {
      color: routeTypeColor("blockade"),
      weight: 7,
      opacity: 0.9,
      dashArray: "18 12",
      className: "blockade-line",
    })
      .bindPopup(`<strong>${escapeHtml(blockade.label || "해상 봉쇄선")}</strong><br />부산항/대한해협 접근 제한`)
      .addTo(mapState.layerGroup);
    (blockade.ships || []).forEach((ship) => {
      L.marker([ship.lat, ship.lon], {
        icon: blockadeShipIcon(ship.angle),
        interactive: false,
        keyboard: false,
      }).addTo(mapState.layerGroup);
    });
  }

  visibleMaritimeRoutes().forEach((route) => {
    const materialId = route.material_ids?.[0];
    const materials = (route.material_ids || []).map((id) => materialLabel(id, {short: true})).join(" / ");
    const highlighted = routeIsContextFocused(route, opsFocus);
    const blocked = routeBlockedByScenarioDisplay(route);
    L.polyline(routeLatLngs(route), {
      color: blocked ? routeTypeColor("threat") : routeTypeColor("maritime"),
      weight: blocked ? 4.2 : highlighted ? 3.4 : 1.6,
      opacity: blocked ? 0.92 : highlighted ? 0.9 : opsFocus.active ? 0.18 : 0.58,
      className: `maritime-import-line ${route.status} ${blocked ? "is-blocked-route" : ""} ${
        highlighted ? "is-context-highlight" : ""
      }`,
    })
      .bindPopup(
        `<strong>${escapeHtml(route.origin_port_name)} → ${escapeHtml(route.destination_port_name)}</strong><br />${escapeHtml(
          blocked ? "차단된 항만 유입 route" : "해상 원료 route",
        )}<br />${escapeHtml(
          materials,
        )}<br />${fmt(route.import_capacity_kg_30d)} kg / 30d · ${fmt(route.distance_nm)} nm · ${fmt(
          Math.round(route.duration_hours_estimate || 0),
        )} h · risk ${pct(route.risk_score)}`,
      )
      .addTo(mapState.layerGroup);
  });

  visiblePortMaterialRoutes().forEach((route) => {
    const highlighted = routeIsContextFocused(route, opsFocus);
    L.polyline(routeLatLngs(route), {
      color: routeTypeColor("material"),
      weight: highlighted ? 3.2 : 1.6,
      opacity: highlighted ? 0.86 : opsFocus.active ? 0.16 : 0.42,
      className: `material-road-line ${route.status} ${highlighted ? "is-context-highlight" : ""}`,
    })
      .bindPopup(
        `<strong>${escapeHtml(route.port_name)} → ${escapeHtml(route.target_factory_name)}</strong><br />${escapeHtml(
          materialLabel(route.material_id, {short: true}),
        )}<br />${fmt(route.quantity_kg_30d)} kg / 30일 · ${escapeHtml(routeDistanceText(route))}<br />${escapeHtml(
          routeCostText(route),
        )}<br />${escapeHtml(routeEvidenceText(route))}`,
      )
      .addTo(mapState.layerGroup);
  });

  if (state.materialRoutesVisible || materialNetworkForcedVisible()) {
    foreignMaterialSources.forEach((source) => {
      const labels = (source.material_ids || []).map((id) => materialLabel(id, {short: true})).join(" / ");
      const preferredPort = portById[source.preferred_port_id] || {};
      L.marker([source.lat, source.lon], {icon: foreignMaterialIcon(source)})
        .bindPopup(
          `<strong>${escapeHtml(source.name)}</strong><br />${escapeHtml(source.port_name)}, ${escapeHtml(
            source.country,
          )}<br />${escapeHtml(labels)} · ${fmt(source.monthly_capacity_kg)} kg/month<br />preferred: ${escapeHtml(
            preferredPort.name || source.preferred_port_id,
          )}`,
        )
        .addTo(mapState.layerGroup);
    });
    importPorts.forEach((port) => {
      const disabled = currentScenarioDisabledPortIds().has(port.id);
      L.marker([port.lat, port.lon], {icon: importPortIcon(port)})
        .bindPopup(
          `<strong>${escapeHtml(port.name)}</strong><br />${
            disabled ? "scenario disabled import port" : "raw material import port"
          } · ${escapeHtml(port.coast || "coast")}`,
        )
        .addTo(mapState.layerGroup);
    });
  }

  visibleResourceRoutes().forEach((route) => {
    const highlighted = routeIsContextFocused(route, opsFocus);
    L.polyline(routeLatLngs(route), {
        color: routeTypeColor("resource"),
        weight: highlighted ? 3.2 : route.status === "resource-reroute" ? 2.4 : 1.6,
        opacity: highlighted ? 0.86 : opsFocus.active ? 0.16 : route.status === "resource-reroute" ? 0.58 : 0.34,
        className: `resource-flow-line ${route.status} ${highlighted ? "is-context-highlight" : ""}`,
      })
      .bindPopup(
        `<strong>${escapeHtml(route.resource_name)} → ${escapeHtml(route.target_factory_name)}</strong><br />${escapeHtml(
          route.resource_label,
        )}<br />${fmt(route.quantity_kg_30d)} kg / 30d · ${escapeHtml(routeDistanceText(route))}<br />${escapeHtml(
          routeCostText(route),
        )}<br />${escapeHtml(routeEvidenceText(route))}`,
      )
      .addTo(mapState.layerGroup);
  });

  visibleRoutes().forEach((route) => {
    const highlighted = routeIsContextFocused(route, opsFocus);
    L.polyline(routeLatLngs(route), {
        color: routeTypeColor("part"),
        weight: highlighted ? 4.2 : route.status === "rerouted" ? 2.8 : 2.1,
        opacity: highlighted ? 0.9 : opsFocus.active ? 0.16 : route.status === "rerouted" ? 0.62 : 0.38,
        className: `flow-line ${route.status} ${highlighted ? "is-context-highlight" : ""}`,
      })
      .bindPopup(
        `<strong>${escapeHtml(routeSourceName(route))} → ${escapeHtml(routeDestinationName(route))}</strong><br />${escapeHtml(
          route.part_label,
        )}<br />${fmt(route.quantity)} units / 30d · ${escapeHtml(routeDistanceText(route))}<br />${escapeHtml(
          routeCostText(route),
        )}<br />${escapeHtml(routeEvidenceText(route))}`,
      )
      .addTo(mapState.layerGroup);
  });

  const showFallbackRoutes = Boolean(scenarioFocus.showFallbackRoutes);
  if (showFallbackRoutes) fallbackRerouteSuggestions(plan).forEach((route) => {
    const points = routeLatLngs(route);
    const midpoint = routeMidpoint(route, 0.58);
    L.polyline(points, {
      color: routeTypeColor("fallback"),
      weight: 3,
      opacity: 0.86,
      className: "fallback-reroute-line",
    })
      .bindPopup(
        `<strong>${escapeHtml(route.fromFactory.company_name)} → ${escapeHtml(route.toFactory.company_name)}</strong><br />위험 노드 대체 후보 · risk ${pct(
          route.risk,
        )}`,
      )
      .addTo(mapState.layerGroup);
    L.marker([midpoint.lat, midpoint.lon], {
      icon: fallbackArrowIcon(arrowAngleDeg(route.from, route.to)),
      interactive: false,
      keyboard: false,
    }).addTo(mapState.layerGroup);
  });

  resources
    .filter((resource) => state.resourceVisible[resource.resource_category])
    .forEach((resource) => {
      L.marker([resource.lat, resource.lon], {icon: resourceIcon(resource)})
        .on("click", (event) => {
          if (event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent);
          state.selectedKind = "resource";
          state.selectedResourceId = resource.id;
          renderSelectedDetails();
          renderMap();
          renderFlowLedger();
        })
        .bindPopup(
          `<strong>${escapeHtml(resource.company_name)}</strong><br />${escapeHtml(resource.resource_label)}<br />Confidence ${Math.round(
            Number(resource.confidence || 0) * 100,
          )}%`,
        )
        .addTo(mapState.layerGroup);
    });

  visibleFactories()
    .forEach((factory) => {
      const risk = factoryRisk(factory);
      L.marker([factory.lat, factory.lon], {icon: markerIcon(factory, opsFocus, plan)})
        .on("click", (event) => {
          if (event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent);
          state.selectedKind = "factory";
          state.selectedFactoryId = factory.id;
          closeDetailsDrawer();
          openFactoryDashboardModal(factory.id, {origin: "node"});
          renderFlowLedger();
        })
        .bindPopup(
          `<strong>${escapeHtml(factory.company_name)}</strong><br />${escapeHtml(factory.category_label)}<br />Risk ${Math.round(
            risk.risk * 100,
          )}% · ${escapeHtml(risk.reason)}`,
        )
        .addTo(mapState.layerGroup);
    });

  startFlowAnimation(topAnimatedRoutes(opsFocus));
}

function fitMap() {
  if (!mapState.map) return;
  if (state.viewMode === "scenario") {
    const {points, focus} = scenarioStageFocusPoints();
    if (points.length === 1) {
      mapState.map.setView(points[0], focus.maxZoom || 10);
      return;
    }
    if (points.length > 1) {
      mapState.map.fitBounds(points, mapFitOptions(focus));
      return;
    }
  }
  const bounds = [];
  visibleFactories().forEach((factory) => bounds.push([factory.lat, factory.lon]));
  resources.forEach((resource) => {
    if (state.resourceVisible[resource.resource_category]) bounds.push([resource.lat, resource.lon]);
  });
  const includeTradeRoutesInFocus = state.mapPresetId === "trade" || state.scenarioId === "southern_port_disruption";
  if (state.materialRoutesVisible && includeTradeRoutesInFocus) {
    importPorts.forEach((port) => bounds.push([port.lat, port.lon]));
    foreignMaterialSources.forEach((source) => bounds.push([source.lat, source.lon]));
    [...visibleMaritimeRoutes(), ...visiblePortMaterialRoutes()].forEach((route) => {
      routePoints(route).forEach((point) => bounds.push([point.lat, point.lon]));
    });
  }
  currentPlan().threat?.path?.forEach((point) => bounds.push([point.lat, point.lon]));
  if (bounds.length) mapState.map.fitBounds(bounds, mapFitOptions());
}

function renderSelectedDetails() {
  if (!state.selectedKind) return;
  if (state.selectedKind === "resource") {
    const resource = resourceById[state.selectedResourceId] || resources[0];
    if (!resource) return;
    const routes = selectedResourceRoutes(resource.id);
    const confidenceWidth = Math.max(6, Math.round(Number(resource.confidence || 0) * 100));
    const targetLabels = (resource.target_part_categories || [])
      .map((category) => categories[category]?.short_label || categories[category]?.label || category)
      .join(" / ");
    elementById("selectedTitle").textContent = resource.company_name;
    elementById("selectedCategory").textContent = resource.resource_label;
    elementById("selectedDetails").innerHTML = `
      <div class="detail-section">
        <div class="detail-row">
          <span class="label">Public product text</span>
          <span class="value">${escapeHtml(resource.product_text)}</span>
        </div>
        <div class="detail-row">
          <span class="label">Location</span>
          <span class="value">${escapeHtml(resource.province)} ${escapeHtml(resource.city || "")}</span>
        </div>
        <div class="detail-row">
          <span class="label">Resource role</span>
          <span class="value">${escapeHtml(resourceCategories[resource.resource_category]?.role || resource.resource_label)}</span>
        </div>
        <div class="detail-row">
          <span class="label">Feeds part family</span>
          <span class="value">${escapeHtml(targetLabels || "verification queue")}</span>
        </div>
        <div class="detail-row">
          <span class="label">Confidence</span>
          <span class="value">${pct(resource.confidence)} · ${escapeHtml((resource.confidence_reasons || []).join(" / "))}</span>
          <div class="confidence-bar"><div class="confidence-fill" style="width:${confidenceWidth}%"></div></div>
        </div>
        <div class="detail-row">
          <span class="label">Energy / Capa evidence</span>
          <span class="value">${energyEvidenceText(resource.energy_profile || {})}</span>
        </div>
        <div class="detail-row">
          <span class="label">Plan assignment</span>
          <span class="value">${
            routes.length
              ? routes
                  .map(
                    (route) =>
                      `${fmt(route.quantity_kg_30d)} kg / 30d → ${escapeHtml(route.target_factory_name)} (${escapeHtml(
                        route.target_part_label,
                      )}) <span class="tag ${escapeHtml(route.status)}">${escapeHtml(route.status)}</span><br />${escapeHtml(
                        routeCostText(route),
                      )} · ${escapeHtml(routeEvidenceText(route))}`,
                  )
                  .join("<br />")
              : "현재 시나리오에서는 예비 자원 후보로만 표시"
          }</span>
        </div>
        <div class="detail-row">
          <span class="label">Verification checklist</span>
          <span class="value">폐자원 확보권, 재활용·처리 허가, 분리/정제 공정, 원소 분석, 품질 등급, 부품공장 재투입 가능성 확인 필요</span>
        </div>
      </div>
    `;
    openDetailsDrawer();
    return;
  }

  const factory = factoryById[state.selectedFactoryId] || factories[0];
  if (!factory) return;
  const assignments = selectedSupplierRows(factory.id);
  const materialInbound = selectedFactoryMaterialRoutes(factory.id);
  const risk = factoryRisk(factory);
  const confidenceWidth = Math.max(6, Math.round(factory.confidence * 100));
  const capacitySummary = capacityProfileSummary(factory);
  elementById("selectedTitle").textContent = factory.company_name;
  elementById("selectedCategory").textContent = factory.category_label;
  elementById("selectedDetails").innerHTML = `
    <div class="detail-section">
      <div class="detail-row">
        <span class="label">Public product text</span>
        <span class="value">${escapeHtml(factory.product_text)}</span>
      </div>
      <div class="detail-row">
        <span class="label">Location</span>
        <span class="value">${escapeHtml(factory.province)} ${escapeHtml(factory.city || "")}</span>
      </div>
      <div class="detail-row">
        <span class="label">Candidate capability</span>
        <span class="value">${escapeHtml(factory.category_label)}</span>
      </div>
      <div class="detail-row">
        <span class="label">Capacity tier</span>
        <span class="value">${escapeHtml(capacitySummary.tier)} · ${escapeHtml(capacitySummary.role)} · index ${escapeHtml(
          capacitySummary.index,
        )} · confidence ${escapeHtml(capacitySummary.confidence)}</span>
      </div>
      <div class="detail-row">
        <span class="label">30d production estimate</span>
        <span class="value">${escapeHtml(capacitySummary.estimate)} units · ${escapeHtml(capacitySummary.evidence)}</span>
      </div>
      <div class="detail-row">
        <span class="label">Manufacturing speed</span>
        <span class="value">${escapeHtml(manufacturingSummary(factory))}</span>
      </div>
      <div class="detail-row">
        <span class="label">Factory scale evidence</span>
        <span class="value">${escapeHtml(capacitySummary.scale || "scale evidence unavailable")}</span>
      </div>
      <div class="detail-row">
        <span class="label">Confidence</span>
        <span class="value">${pct(factory.confidence)} · ${escapeHtml((factory.confidence_reasons || []).join(" / "))}</span>
        <div class="confidence-bar"><div class="confidence-fill" style="width:${confidenceWidth}%"></div></div>
      </div>
      <div class="detail-row">
        <span class="label">Scenario risk</span>
        <span class="value">${pct(risk.risk)} · ${escapeHtml(risk.reason)}</span>
      </div>
      <div class="detail-row">
        <span class="label">Energy / Capa evidence</span>
        <span class="value">${energyEvidenceText(factory.energy_profile || {})}</span>
      </div>
      <div class="detail-row">
        <span class="label">Grid / power risk</span>
        <span class="value">${gridRiskSummary(factory)}</span>
      </div>
      <div class="detail-row">
        <span class="label">재고 / 생산 중 / 주문</span>
        <span class="value">${operationalSummary(factory)}</span>
      </div>
      <div class="detail-row">
        <span class="label">Plan assignment</span>
        <span class="value">${
          assignments.length
            ? assignments
                .map(
                  (assignment) =>
                    `${escapeHtml(assignment.part_label)} ${fmt(Math.round(assignment.requested_quantity * currentScenarioScale()))} units → ${escapeHtml(
                      supplierDestinationName(assignment),
                    )} <span class="tag ${escapeHtml(assignment.status)}">${escapeHtml(assignment.status)}</span><br />${escapeHtml(
                      routeCostText(assignment),
                    )} · ${escapeHtml(routeEvidenceText(assignment))}`,
                )
                .join("<br />")
            : "현재 시나리오에서는 예비 후보로만 표시"
        }</span>
      </div>
      <div class="detail-row">
        <span class="label">원료 반입 경로</span>
        <span class="value">${
          materialInbound.length
            ? materialInbound
                .slice(0, 6)
                .map(
                  (route) =>
                    `${escapeHtml(route.port_name)} → ${escapeHtml(materialLabel(route.material_id, {short: true}))} ${fmt(
                      route.quantity_kg_30d,
                    )} kg / 30일 · ${escapeHtml(routeDistanceText(route))} · ${escapeHtml(routeCostText(route))}<br />${escapeHtml(
                      routeEvidenceText(route),
                    )}`,
                )
                .join("<br />")
            : "현재 시나리오에서 연결된 원료 반입 경로 없음"
        }</span>
      </div>
      <div class="detail-row">
        <span class="label">Verification checklist</span>
        <span class="value">보유설비, 생산라인 여유, QA 인증, 원자재 재고, 보안요건, 전환 소요일 확인 필요 · missing: ${escapeHtml(
          capacitySummary.missing,
        )}</span>
      </div>
    </div>
  `;
  openDetailsDrawer();
}

function renderPlanSummary() {
  const plan = currentPlan();
  const scale = currentScenarioScale();
  const possible = plan.possible_drones_30d || 0;
  const shortfall = Math.max(0, Number(state.targetDrones || 0) - possible);
  const categoriesHtml = (plan.category_summary || [])
    .map((item) => {
      const required = Math.round(item.required_units * scale);
      const coverage = required ? Math.min(1, item.allocated_units / required) : 0;
      const isAssembly = item.part_category === "drone_assembly";
      const assemblyOps = isAssembly ? selectedFinalAssemblyOperations(plan) : [];
      const supplierNames = isAssembly
        ? assemblyOps.map((row) => `${row.factory.company_name} · ${row.factory.priority_site_label || row.factory.city || "대표 공장"}`)
        : item.top_supplier_names || [];
      const supplierCount = isAssembly ? assemblyOps.length : Number(item.supplier_count || 0);
      return `
        <div class="plan-row">
          <div>
            <div class="plan-title">
              <span>${escapeHtml(partCategoryText(item.part_category).label)}</span>
              <span>${pct(coverage)}</span>
            </div>
            <div class="coverage-bar"><div class="coverage-fill" style="width:${Math.max(4, Math.round(coverage * 100))}%"></div></div>
            <div class="plan-sub">${escapeHtml(supplierNames.join(" · ") || "검증 대기")}</div>
          </div>
          <div class="plan-qty">
            ${fmt(item.allocated_units)} / ${fmt(required)}
            <br />${fmt(supplierCount)}${isAssembly ? "개 가동" : "개 공급처"}
          </div>
        </div>
      `;
    })
    .join("");
  const resourceHtml = (plan.resource_supply_summary || [])
    .map(
      (item) => `
        <div class="resource-plan-row">
          <span class="route-color cat-${escapeHtml(item.resource_category)}"></span>
          <span>
            <strong>${escapeHtml(resourceCategoryText(item.resource_category).label)}</strong>
            <small>${fmt(item.allocated_kg_30d)} kg / 30일 · ${fmt(item.selected_route_count)}개 활성 경로 · ${escapeHtml(
              (item.top_resource_names || []).join(" · ") || "검증 대기",
            )}</small>
          </span>
        </div>
      `,
    )
    .join("");
  const rawMaterialHtml = (plan.raw_material_supply_summary || [])
    .map((item) => {
      const required = Math.round(Number(item.required_kg_30d || 0) * scale);
      const available = Number(item.total_available_kg_30d || 0);
      const coverage = required ? Math.min(1, available / required) : 0;
      return `
        <div class="resource-plan-row material-plan-row">
          <span class="route-color" style="background:${escapeHtml(materialColor(item.material_id))}"></span>
          <span>
            <strong>${escapeHtml(materialLabel(item.material_id))}</strong>
            <small>${fmt(available)} / ${fmt(required)} kg · 수입 ${fmt(
              item.import_supply_kg_30d,
            )} kg · 커버리지 ${pct(coverage)}</small>
          </span>
        </div>
      `;
    })
    .join("");

  elementById("planSummary").innerHTML = `
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(possible)}</strong><span>병목 기준 가능 수량</span></div>
      <div class="metric-box"><strong>${fmt(shortfall)}</strong><span>목표 대비 부족분</span></div>
      <div class="metric-box"><strong>${escapeHtml(partCategoryText(plan.bottleneck_part_category).label || "-")}</strong><span>현재 병목 부품군</span></div>
      <div class="metric-box"><strong>${fmt(plan.rerouted_supplier_count || 0)}</strong><span>재배치된 공급 경로</span></div>
    </div>
    <div class="plan-list">${categoriesHtml}</div>
    <div class="resource-plan">
      <p class="toggle-section-title">핵심 원료 공급 경로</p>
      ${resourceHtml}
    </div>
    <div class="resource-plan">
      <p class="toggle-section-title">원자재 커버리지</p>
      ${rawMaterialHtml}
    </div>
  `;
}

function currentOptimizationResult() {
  return optimizationByScenarioId[state.scenarioId] || optimizationResult.scenarios?.[0] || null;
}

function renderOptimizationResultSummary() {
  const element = elementById("optimizationResultSummary");
  if (!element) return;
  const result = currentOptimizationResult();
  if (!result) {
    element.innerHTML = `<p class="source-note">아직 v0.9 최적화 결과가 생성되지 않았습니다. optimizer input export 이후 allocation solver를 실행해야 합니다.</p>`;
    return;
  }

  const objective = result.objective_breakdown || {};
  const delta = result.plan_delta || {};
  const limiting = result.binding_constraints?.[0] || {};
  const shortageRows = (result.shortages || [])
    .filter((row) => String(row.commodity_id || "").startsWith("part:"))
    .slice()
    .sort((a, b) => Number(a.coverage_ratio || 0) - Number(b.coverage_ratio || 0))
    .slice(0, 5)
    .map(
      (row) => `
        <div class="plan-row">
          <div>
            <div class="plan-title">
              <span>${escapeHtml(row.commodity_label || row.commodity_id)}</span>
              <span>${pct(row.coverage_ratio || 0)}</span>
            </div>
            <div class="coverage-bar"><div class="coverage-fill" style="width:${Math.max(4, Math.round(Number(row.coverage_ratio || 0) * 100))}%"></div></div>
            <div class="plan-sub">${escapeHtml(row.driver || "candidate edge capacity")} · ${escapeHtml(row.severity || "watch")}</div>
          </div>
          <div class="plan-qty">
            ${fmt(row.allocated_quantity)} / ${fmt(row.required_quantity)}
            <br />부족 ${fmt(row.shortage_quantity)}
          </div>
        </div>
      `,
    )
    .join("");
  const bindingRows = (result.binding_constraints || [])
    .slice(0, 4)
    .map(
      (row) => `
        <div class="resource-plan-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(row.commodity_label || row.constraint_type)}</strong>
            <small>${escapeHtml(row.constraint_type || "constraint")} · ${
              row.survival_days_likely !== undefined ? `survival ${fmt(row.survival_days_likely)}d` : `coverage ${pct(row.coverage_ratio || 0)}`
            }</small>
          </span>
        </div>
      `,
    )
    .join("");

  element.innerHTML = `
    <p class="source-note">v0.9는 현재 후보 경로 안에서 부족량을 먼저 줄이고, 그 다음 비용/위험 점수가 낮은 경로를 고르는 allocation prototype입니다. 아직 full MILP는 아닙니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(objective.feasible_output_units_30d || 0)}</strong><span>최적화 가능 수량</span></div>
      <div class="metric-box"><strong>${fmt(objective.output_gap_units_30d || 0)}</strong><span>목표 대비 부족</span></div>
      <div class="metric-box"><strong>${fmt(objective.logistics_cost_krw_proxy || 0)}</strong><span>추정 물류비(원)</span></div>
      <div class="metric-box"><strong>${pct(objective.weighted_route_risk || 0)}</strong><span>가중 route risk</span></div>
    </div>
    <div class="metric-grid">
      <div class="metric-box"><strong>${escapeHtml(limiting.commodity_label || "-")}</strong><span>제약 1순위</span></div>
      <div class="metric-box"><strong>${fmt(delta.rerouted_flow_count || 0)}</strong><span>재배치 flow</span></div>
      <div class="metric-box"><strong>${fmt(delta.added_factory_count || 0)}</strong><span>추가 공장</span></div>
      <div class="metric-box"><strong>${fmt(delta.removed_factory_count || 0)}</strong><span>제외 공장</span></div>
    </div>
    <div class="plan-list">${shortageRows}</div>
    <div class="resource-plan">
      <p class="toggle-section-title">주요 제약 조건</p>
      ${bindingRows}
    </div>
  `;
}

function currentReconfigurationResult() {
  return reconfigurationByScenarioId[state.scenarioId] || reconfigurationResult.scenarios?.[0] || null;
}

function renderReconfigurationSummary() {
  const element = elementById("reconfigurationSummary");
  if (!element) return;
  const result = currentReconfigurationResult();
  if (!result) {
    element.innerHTML = `<p class="source-note">아직 v1.0 재구성 결과가 생성되지 않았습니다. v0.9 최적화 결과 이후 Plan Delta를 생성해야 합니다.</p>`;
    return;
  }

  const metrics = result.delta_metrics || {};
  const levelLabel = {
    monitor: "모니터링",
    replan_review: "재계획 검토",
    emergency_replan: "긴급 재계획",
  }[result.reconfiguration_level] || result.reconfiguration_level;
  const actionRows = [
    ...(result.assembly_replacement_actions || []).slice(0, 4).map((item) => ({
      title: `${item.from_factory_name} → ${item.to_factory_name}`,
      detail: `예비 조립 전환 · ${fmt(item.road_distance_km_estimate)} km 추정 · ${fmt(item.reserve_nominal_daily_output_units)} / day`,
      action: item.recommended_action,
    })),
    ...(result.frozen_order_actions || []).slice(0, 3).map((item) => ({
      title: `동결 주문 ${item.order_id}`,
      detail: `${item.part_category} · ${fmt(item.quantity_units)} units · D+${fmt(item.freeze_until_day)}까지 보호`,
      action: item.recommended_action,
    })),
    ...(result.in_transit_actions || [])
      .filter((item) => item.recommended_action !== "continue")
      .slice(0, 3)
      .map((item) => ({
        title: `운송 중 ${item.shipment_id}`,
        detail: `${item.part_category || item.shipment_kind} · ETA ${fmt(item.eta_hours)}h`,
        action: item.recommended_action,
      })),
  ]
    .map(
      (item) => `
        <div class="resource-plan-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(item.title)}</strong>
            <small>${escapeHtml(item.detail)} · ${escapeHtml(item.action)}</small>
          </span>
        </div>
      `,
    )
    .join("");

  element.innerHTML = `
    <p class="source-note">v1.0은 baseline 대비 현재 시나리오에서 바뀌는 공장, 비용, 위험, 동결 주문, 운송 중 물량을 설명하는 Plan Delta입니다. 아직 자동 명령이 아니라 사람 검토용 의사결정 카드입니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${escapeHtml(levelLabel)}</strong><span>재구성 수준</span></div>
      <div class="metric-box"><strong>${fmt(metrics.feasible_output_delta_units_30d || 0)}</strong><span>생산량 변화</span></div>
      <div class="metric-box"><strong>${fmt(metrics.logistics_cost_delta_krw_proxy || 0)}</strong><span>비용 변화 proxy</span></div>
      <div class="metric-box"><strong>${pct(metrics.weighted_route_risk_delta || 0)}</strong><span>위험 변화</span></div>
    </div>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(metrics.added_factory_count || 0)}</strong><span>추가 공장</span></div>
      <div class="metric-box"><strong>${fmt(metrics.removed_factory_count || 0)}</strong><span>제외 공장</span></div>
      <div class="metric-box"><strong>${fmt(metrics.reserve_replacement_action_count || 0)}</strong><span>예비 전환</span></div>
      <div class="metric-box"><strong>${fmt(metrics.in_transit_review_count || 0)}</strong><span>운송 검토</span></div>
    </div>
    <div class="resource-plan">
      <p class="toggle-section-title">권장 검토 작업</p>
      ${actionRows || `<p class="source-note">현재 시나리오에서는 즉시 검토할 동결 주문/운송 충돌이 없습니다.</p>`}
    </div>
  `;
}

function renderFlowLedger() {
  const scale = currentScenarioScale();
  const maritimeRoutes = visibleMaritimeRoutes()
    .slice()
    .sort((a, b) => Number(b.import_capacity_kg_30d || 0) - Number(a.import_capacity_kg_30d || 0));
  const materialRoadRoutes = visiblePortMaterialRoutes()
    .slice()
    .sort((a, b) => Number(b.quantity_kg_30d || 0) - Number(a.quantity_kg_30d || 0));
  const resourceRoutes = visibleResourceRoutes()
    .slice()
    .sort((a, b) => b.quantity_kg_30d - a.quantity_kg_30d);
  const routes = visibleRoutes()
    .slice()
    .sort((a, b) => {
      if (a.status !== b.status) return a.status === "rerouted" ? -1 : 1;
      return b.quantity - a.quantity;
    });
  elementById("flowLedger").innerHTML = `
    <p class="source-note">지도 위 점들은 선택된 공급 경로를 따라 움직입니다. 점선 해상로는 해외 원료→수입항, 얇은 선은 원료/자원→부품공장, 굵은 선은 부품공장→우선 최종조립 공장 흐름입니다.</p>
    <div class="route-list">
      ${maritimeRoutes
        .slice(0, 8)
        .map((route) => {
          const materialId = route.material_ids?.[0];
          const labels = (route.material_ids || []).map((id) => materialLabel(id, {short: true})).join(" / ");
          const blocked = routeBlockedByScenarioDisplay(route);
          return `
            <button class="route-row maritime-route route-static" type="button">
              <span class="route-color" style="background:${escapeHtml(blocked ? routeTypeColor("threat") : routeTypeColor("maritime"))}"></span>
              <span class="route-main">
                <strong>${escapeHtml(route.origin_port_name)} → ${escapeHtml(route.destination_port_name)}</strong>
                <span>${escapeHtml(labels)} · ${fmt(route.distance_nm)} nm maritime · <span class="tag maritime">${escapeHtml(
                  blocked ? "blocked" : route.status,
                )}</span></span>
                <span>${fmt(Math.round(route.duration_hours_estimate || 0))} h · risk ${pct(route.risk_score)}</span>
                <span>${escapeHtml(blocked ? "차단된 항만 유입 route" : statusText(route.routing_status || "maritime_corridor_estimate"))}</span>
              </span>
              <span class="route-qty"><strong>${fmt(route.import_capacity_kg_30d)}</strong><span>kg</span></span>
            </button>
          `;
        })
        .join("")}
      ${materialRoadRoutes
        .slice(0, 16)
        .map(
          (route) => `
            <button class="route-row material-road-route" data-factory="${escapeHtml(route.target_factory_id)}" type="button">
              <span class="route-color" style="background:${escapeHtml(routeTypeColor("material"))}"></span>
              <span class="route-main">
                <strong>${escapeHtml(route.port_name)} → ${escapeHtml(route.target_factory_name)}</strong>
                <span>${escapeHtml(materialLabel(route.material_id, {short: true}))} · ${escapeHtml(
                  routeDistanceText(route),
                )} · <span class="tag material">${escapeHtml(statusText(route.status))}</span></span>
                <span>${escapeHtml(routeCostText(route))}</span>
                <span>${escapeHtml(routeEvidenceText(route))}</span>
              </span>
              <span class="route-qty"><strong>${fmt(route.quantity_kg_30d)}</strong><span>kg</span></span>
            </button>
          `,
        )
        .join("")}
      ${resourceRoutes
        .slice(0, 18)
        .map(
          (route) => `
            <button class="route-row resource-route" data-resource="${escapeHtml(route.resource_id)}" type="button">
              <span class="route-color" style="background:${escapeHtml(routeTypeColor("resource"))}"></span>
              <span class="route-main">
                <strong>${escapeHtml(route.resource_name)} → ${escapeHtml(route.target_factory_name)}</strong>
                <span>${escapeHtml(route.resource_label)} · ${escapeHtml(routeDistanceText(route))} · <span class="tag ${escapeHtml(
                  route.status,
                )}">${escapeHtml(route.status)}</span></span>
                <span>${escapeHtml(routeCostText(route))}</span>
                <span>${escapeHtml(routeEvidenceText(route))}</span>
              </span>
              <span class="route-qty"><strong>${fmt(route.quantity_kg_30d)}</strong><span>kg</span></span>
            </button>
          `,
        )
        .join("")}
      ${routes
        .slice(0, 30)
        .map(
          (route) => `
            <button class="route-row" data-factory="${escapeHtml(route.factory_id)}" type="button">
              <span class="route-color" style="background:${escapeHtml(routeTypeColor("part"))}"></span>
              <span class="route-main">
                <strong>${escapeHtml(routeSourceName(route))} → ${escapeHtml(routeDestinationName(route))}</strong>
                <span>${escapeHtml(route.part_label)} · ${escapeHtml(routeDistanceText(route))} · <span class="tag ${escapeHtml(route.status)}">${escapeHtml(route.status)}</span></span>
                <span>${escapeHtml(routeCostText(route))}</span>
                <span>${escapeHtml(routeEvidenceText(route))}</span>
              </span>
              <span class="route-qty"><strong>${fmt(Math.round(route.quantity * scale))}</strong><span>units</span></span>
            </button>
          `,
        )
        .join("")}
    </div>
  `;

  elementById("flowLedger").querySelectorAll("[data-factory]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedKind = "factory";
      state.selectedFactoryId = button.dataset.factory;
      renderSelectedDetails();
      renderMap();
    });
  });
  elementById("flowLedger").querySelectorAll("[data-resource]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedKind = "resource";
      state.selectedResourceId = button.dataset.resource;
      renderSelectedDetails();
      renderMap();
    });
  });
}

function renderPowerRiskSummary() {
  const zoneRows = gridRiskZones
    .slice()
    .sort((a, b) => Number(b.grid_dependency_score || 0) - Number(a.grid_dependency_score || 0))
    .slice(0, 6)
    .map(
      (zone) => `
        <div class="resource-plan-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(zone.province)} · ${escapeHtml(zone.exposure_tier)}</strong>
            <small>${fmt(zone.factory_count)} factories · dependency ${scoreText(zone.grid_dependency_score)} · industrial power ${fmt(
              zone.industrial_electricity_mwh,
            )} MWh</small>
          </span>
        </div>
      `,
    )
    .join("");
  const scenarioRows = gridDisruptionScenarios
    .slice(0, 4)
    .map(
      (scenario) => `
        <div class="plan-row">
          <div>
            <div class="plan-title">
              <span>${escapeHtml(scenario.name)}</span>
              <span>${scoreText(scenario.assumed_availability_multiplier)}</span>
            </div>
            <div class="plan-sub">${fmt(scenario.affected_factory_count)} factories · ${fmt(
              scenario.capacity_units_30d_at_risk,
            )} units / 30d at risk</div>
          </div>
          <div class="plan-qty">${escapeHtml((scenario.part_family_exposure || []).slice(0, 2).map((item) => item.part_label).join(" / "))}</div>
        </div>
      `,
    )
    .join("");
  elementById("powerRiskSummary").innerHTML = `
    <p class="source-note">전력망 의존성은 공개 전력사용량과 공장 분포 기반 권역 프록시입니다. 특정 전력설비-공장 종속관계로 해석하지 않습니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(gridRiskZones.length)}</strong><span>전력 리스크 권역</span></div>
      <div class="metric-box"><strong>${fmt(gridDisruptionScenarios.length)}</strong><span>전력망 저하 시나리오</span></div>
      <div class="metric-box"><strong>${fmt(gridRiskZones.filter((zone) => zone.exposure_tier === "high").length)}</strong><span>high exposure 권역</span></div>
      <div class="metric-box"><strong>${fmt(factories.filter((factory) => factory.grid_risk_profile?.manual_override_required).length)}</strong><span>수동 검증 필요 공장</span></div>
    </div>
    <div class="resource-plan">${zoneRows}</div>
    <div class="plan-list">${scenarioRows}</div>
  `;
}

function renderOperationalState() {
  const totalAvailable = inventoryWip.reduce((sum, row) => sum + Number(row.available_to_ship_units || 0), 0);
  const totalWip = inventoryWip.reduce((sum, row) => sum + Number(row.wip_units || 0), 0);
  const totalFrozen = frozenOrders.reduce((sum, row) => sum + Number(row.frozen_quantity_units || 0), 0);
  const shipmentUnits = inTransitShipments.reduce(
    (sum, row) => sum + Number(row.quantity_units || 0) + Number(row.quantity_kg || 0),
    0,
  );
  const shipmentRows = inTransitShipments
    .slice(0, 8)
    .map((shipment) => {
      const factory = factoryById[shipment.factory_id || shipment.target_factory_id] || {};
      const label = shipment.part_label || shipment.resource_label || shipment.part_category || shipment.resource_category;
      const qty = shipment.quantity_units ? `${fmt(shipment.quantity_units)} units` : `${fmt(shipment.quantity_kg)} kg`;
      return `
        <div class="resource-plan-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(factory.company_name || shipment.shipment_kind)}</strong>
            <small>${escapeHtml(label)} · ${qty} · progress ${scoreText(shipment.progress_ratio)} · ETA ${shipment.eta_hours ?? "n/a"}h</small>
          </span>
        </div>
      `;
    })
    .join("");
  elementById("operationalState").innerHTML = `
    <p class="source-note">현재 값은 ERP/MES/TMS 연동 전 synthetic ledger입니다. 재계획 모델에서 동결 주문과 운송 중 물량을 고정 제약으로 쓰기 위한 스키마입니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(totalAvailable)}</strong><span>가용 재고 추정</span></div>
      <div class="metric-box"><strong>${fmt(totalWip)}</strong><span>생산 중 추정</span></div>
      <div class="metric-box"><strong>${fmt(totalFrozen)}</strong><span>동결 주문 수량</span></div>
      <div class="metric-box"><strong>${fmt(shipmentUnits)}</strong><span>운송 중 수량/kg</span></div>
    </div>
    <div class="resource-plan">${shipmentRows}</div>
  `;
}

function opsProgressBar(value) {
  return `<div class="ops-progress"><div style="width:${Math.max(4, Math.round(Number(value || 0) * 100))}%"></div></div>`;
}

function renderDecisionCards() {
  const factoryStatus = buildFactoryStatus();
  const droneRows = droneProgressRows();
  const units = unitDemandRows();
  const procurements = procurementRows();
  const materialCritical = procurements.filter((row) => row.coverage < 1 || row.topRisk >= 0.28).length;

  elementById("factoryStatusCard").innerHTML = `
    <div class="ops-card-header">
      <div>
        <p>최종 조립 공장 현황</p>
        <h3>${fmt(factoryStatus.ops.length)}개 가동 중</h3>
      </div>
      <button class="ops-card-action" data-ops-modal="factory" type="button">상세</button>
    </div>
    <div class="ops-metrics">
      <span><strong>${fmt(factoryStatus.ops.length)}</strong><small>가동</small></span>
      <span><strong>${fmt(factoryStatus.totalDaily)}</strong><small>일 생산량</small></span>
      <span><strong>${fmt(factoryStatus.totalWip)}</strong><small>생산 중</small></span>
      <span><strong>${fmt(factoryStatus.highRisk)}</strong><small>위험</small></span>
    </div>
    <div class="ops-list">
      ${factoryStatus.ops
        .map((row) => {
          const factory = row.factory;
          return `
            <button class="ops-list-row" data-ops-modal="factory" data-ops-item="${escapeHtml(factory.id)}" type="button">
              <span>
                <strong>${escapeHtml(factory.company_name)}${
                  factory.is_priority_assembly_seed ? ' <span class="ops-inline-badge">최종조립 우선</span>' : ""
                }</strong>
                <small>${escapeHtml(factory.priority_site_label || "최종 조립 공장")} · ${escapeHtml(factory.province)} ${escapeHtml(
                  factory.city || "",
                )} · ${fmt(row.dailyOutput)}/day · 생산 중 ${fmt(
                  row.inventory.wip_units || 0,
                )}</small>
              </span>
              <em class="${row.risk >= 0.44 ? "warn" : ""}">${pct(row.risk)}</em>
            </button>
          `;
        })
        .join("")}
    </div>
  `;

  elementById("droneProgressCard").innerHTML = `
    <div class="ops-card-header">
      <div>
        <p>드론 종류별 생산 진행현황</p>
        <h3>${fmt(droneRows.reduce((sum, row) => sum + row.prepared, 0))}대 준비 중</h3>
      </div>
      <button class="ops-card-action" data-ops-modal="drone" type="button">상세</button>
    </div>
    <div class="ops-list">
      ${droneRows
        .map(
          (row) => `
            <button class="ops-list-row progress-row" data-ops-modal="drone" data-ops-item="${escapeHtml(row.profile.profile_id)}" type="button">
              <span>
                <strong>${escapeHtml(row.text.label)}</strong>
                <small>${escapeHtml(row.text.use)} · ${fmt(row.prepared)} / ${fmt(row.target)}대 · 생산 중 ${fmt(row.wip)}</small>
                ${opsProgressBar(row.progress)}
              </span>
              <em>${pct(row.progress)}</em>
            </button>
          `,
        )
        .join("")}
    </div>
  `;

  elementById("unitStatusCard").innerHTML = `
    <div class="ops-card-header">
      <div>
        <p>부대 현황</p>
        <h3>보급 우선순위</h3>
      </div>
      <button class="ops-card-action" data-ops-modal="unit" type="button">상세</button>
    </div>
    <div class="ops-list">
      ${units
        .slice(0, 4)
        .map(
          (unit) => `
            <button class="ops-list-row" data-ops-modal="unit" data-ops-item="${escapeHtml(unit.id)}" type="button">
              <span>
                <strong>${escapeHtml(unit.name)}</strong>
                <small>${escapeHtml(missionText(unit.profile_id).label)} ${fmt(unit.requested)}대 · D+${fmt(unit.deadline_day)}까지 · 부족 ${fmt(unit.shortage)}</small>
                ${opsProgressBar(unit.requested ? unit.prepared / unit.requested : 0)}
              </span>
              <em class="${unit.shortageRatio > 0.35 ? "warn" : ""}">${pct(unit.urgency)}</em>
            </button>
          `,
        )
        .join("")}
    </div>
  `;

  elementById("procurementStatusCard").innerHTML = `
    <div class="ops-card-header">
      <div>
        <p>원료/부품 조달 현황</p>
        <h3>${fmt(materialCritical)}개 집중 모니터링</h3>
      </div>
      <button class="ops-card-action" data-ops-modal="procurement" type="button">상세</button>
    </div>
    <div class="ops-list">
      ${procurements
        .slice(0, 4)
        .map(
          (row) => `
            <button class="ops-list-row progress-row" data-ops-modal="procurement" data-ops-item="${escapeHtml(row.material_id)}" type="button">
              <span>
                <strong>${escapeHtml(materialLabel(row.material_id))}</strong>
                <small>${fmt(row.available)} / ${fmt(row.required)}kg · 수입 ${fmt(row.import_supply_kg_30d)}kg · 경로 ${fmt(
                  row.maritimeRoutes.length + row.roadRoutes.length,
                )}개</small>
                ${opsProgressBar(row.coverage)}
              </span>
              <em class="${row.coverage < 1 ? "warn" : ""}">${pct(row.coverage)}</em>
            </button>
          `,
        )
        .join("")}
    </div>
  `;

  document.querySelectorAll("[data-ops-modal]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      openDashboardModal(button.dataset.opsModal, button.dataset.opsItem || "");
    });
  });
}

function openDashboardModal(kind, itemId = "") {
  if (kind === "factory") return openFactoryDashboardModal(itemId);
  if (kind === "drone") return openDroneDashboardModal(itemId);
  if (kind === "unit") return openUnitDashboardModal(itemId);
  if (kind === "procurement") return openProcurementDashboardModal(itemId);
}

function openFactoryDashboardModal(factoryId = "", {origin = "card"} = {}) {
  const status = buildFactoryStatus();
  const rows = status.ops;
  let focused = factoryId ? rows.filter((row) => row.factory.id === factoryId) : rows.slice(0, 10);
  if (factoryId && !focused.length) {
    const factory = factoryById[factoryId];
    if (factory) {
      const inventory = inventoryByFactoryId[factory.id] || {};
      const routes = (currentPlan().route_segments || []).filter(
        (route) => route.factory_id === factory.id || route.destination_factory_id === factory.id,
      );
      focused = [
        {
          factory,
          assignments: selectedSupplierRows(factory.id),
          routes,
          inventory,
          requested: routes.reduce((sum, route) => sum + routeQuantity(route), 0),
          dailyOutput: factoryDailyOutput(factory),
          risk: factoryRisk(factory).risk,
        },
      ];
    }
  }
  const routeCards = focused
    .map((row) => {
      const factory = row.factory;
      const inventory = row.inventory || {};
      const alternatives = alternativeFactories(factory)
        .map((candidate) => `${candidate.factory.company_name} ${fmt(candidate.dailyOutput)}/day, risk ${pct(candidate.risk)}`)
        .join(" · ");
      const routeQty = row.routes.reduce((sum, route) => sum + routeQuantity(route), 0);
      const primaryRoute = row.routes[0] || {};
      return routeCard({
        title: factory.company_name,
        subtitle: `${factory.priority_site_label || "최종 조립 공장"} · ${factory.province} ${factory.city || ""}`,
        routeId: primaryRoute.id,
        factoryId: factory.id,
        status: row.risk >= 0.44 ? "위험" : "가동",
        warning: row.risk >= 0.44,
        stats: [
          {label: "생산 속도", value: `${fmt(row.dailyOutput)}/day`},
          {label: "총 가능/요청", value: `${fmt(routeQty || row.requested)}대`},
          {label: "예상 시간", value: primaryRoute.duration_min ? `${fmt(Math.round(primaryRoute.duration_min))}분` : "현장/미정"},
          {label: "예상 비용", value: primaryRoute.estimated_trip_cost_krw ? `${fmt(primaryRoute.estimated_trip_cost_krw)}원` : "0원/미정"},
          {label: "신뢰도", value: pct(factory.confidence || row.capacityIndex || 0)},
          {label: "위험", value: pct(row.risk), warn: row.risk >= 0.44},
        ],
        note: `${gridRiskSummary(factory)} · 재고 ${fmt(inventory.available_to_ship_units || 0)} · 생산 중 ${fmt(
          inventory.wip_units || 0,
        )} · QA hold ${fmt(inventory.qa_hold_units || 0)} · 대안 후보: ${alternatives || "검증 필요"}`,
      });
    })
    .join("");
  const selectedTitle = factoryId ? focused[0]?.factory.company_name || "선택 공장" : "가동 중 공장";
  openOpsSheet(
    "최종 조립 공장 현황",
    factoryId ? "선택 공장 운영 상세" : "최종 조립 공장 운영 상세",
    `
      ${sheetMetrics([
        {label: "표시 대상", value: `${fmt(focused.length)}개`},
        {label: "일 생산량", value: `${fmt(focused.reduce((sum, row) => sum + row.dailyOutput, 0))}/day`},
        {label: "생산 중", value: fmt(focused.reduce((sum, row) => sum + Number(row.inventory.wip_units || 0), 0))},
        {label: "위험", value: fmt(focused.filter((row) => row.risk >= 0.44).length), warn: true},
      ])}
      ${sheetSection("Summary", selectedTitle, `<p class="ops-sheet-note">좌측 공장 큐는 현재 시나리오에서 최종 드론 제조/조립으로 배정된 대표 공장만 표시합니다. 동일 기업의 복수 주소는 공장/제조 신호와 배정량 기준으로 1개 대표 사업장만 올립니다.</p>`)}
      ${sheetSection("Current readiness", "최종 조립 공장과 출하 가능성", routeCardList(routeCards))}
    `,
    {
      kind: "factory",
      itemId: factoryId,
      side: "left",
      subtitle: origin === "node" ? "지도 노드에서 선택된 공장의 생산/경로 상세입니다." : "좌측 공장 카드에서 이어지는 drill-down 상세입니다.",
    },
  );
}

function openDroneDashboardModal(profileId = "") {
  const rows = profileId ? droneProgressRows().filter((row) => row.profile.profile_id === profileId) : droneProgressRows();
  const unitRows = unitDemandRows();
  const body = rows
    .map((row) => {
      const units = unitRows.filter((unit) => unit.profile_id === row.profile.profile_id);
      const factoryCards = row.assemblyRoutes.slice(0, 6).map((route) => {
        const unit = units[0] || unitRows[0] || {};
        const factory = factoryById[route.factory_id] || {};
        const quantity = routeQuantity(route);
        const planRoute = planRouteForSupplier(route) || route;
        return routeCard({
          title: factory.company_name || routeSourceName(route),
          subtitle: `${supplierDestinationName(route)} 최종조립 · ${unit.name || "합성 수요부대"}`,
          routeId: planRoute.id,
          factoryId: route.factory_id,
          status: `D+${fmt(unit.deadline_day || 3)}`,
          stats: [
            {label: "생산 속도", value: `${fmt(Math.round(quantity / 30))}/day`},
            {label: "총 가능 수량", value: `${fmt(quantity)}대`},
            {label: "예상 시간", value: planRoute.duration_min ? `${fmt(Math.round(planRoute.duration_min))}분` : "현장/미정"},
            {label: "예상 비용", value: planRoute.estimated_trip_cost_krw ? `${fmt(planRoute.estimated_trip_cost_krw)}원` : "0원/미정"},
            {label: "신뢰도", value: pct(factory.confidence || route.capacity_confidence || 0)},
            {label: "검증", value: statusText(route.routing_status || "candidate")},
          ],
          note: routeEvidenceText(planRoute),
        });
      }).join("");
      return sheetSection(
        row.text.label,
        `${fmt(row.prepared)} / ${fmt(row.target)}대 · ${pct(row.progress)}`,
        `${opsProgressBar(row.progress)}${routeCardList(factoryCards)}`,
      );
    })
    .join("");
  const totalPrepared = rows.reduce((sum, row) => sum + row.prepared, 0);
  const totalTarget = rows.reduce((sum, row) => sum + row.target, 0);
  openOpsSheet(
    "드론 종류별 생산 진행현황",
    profileId ? "선택 드론 생산 상세" : "드론 종류별 생산 상세",
    `
      ${sheetMetrics([
        {label: "목표", value: `${fmt(totalTarget)}대`},
        {label: "준비 중", value: `${fmt(totalPrepared)}대`},
        {label: "진척률", value: pct(totalTarget ? totalPrepared / totalTarget : 0)},
        {label: "프로파일", value: `${fmt(rows.length)}종`},
      ])}
      ${body}
    `,
    {kind: "drone", itemId: profileId, side: "left", subtitle: "좌측 생산 진행 카드에서 이어지는 프로파일별 상세입니다."},
  );
}

function openUnitDashboardModal(unitId = "") {
  const rows = unitId ? unitDemandRows().filter((unit) => unit.id === unitId) : unitDemandRows();
  const content = rows
    .map((unit) => {
      const factories = unit.assemblyRoutes.slice(0, 5).map((route) => {
        const factory = factoryById[route.factory_id] || {};
        const quantity = routeQuantity(route);
        const daily = Math.round(quantity / 30);
        const planRoute = planRouteForSupplier(route) || route;
        return routeCard({
          title: factory.company_name || routeSourceName(route),
          subtitle: `${supplierDestinationName(route)} 최종조립 · ${missionText(unit.profile_id).label}`,
          routeId: planRoute.id,
          factoryId: route.factory_id,
          status: unit.shortageRatio > 0.35 ? "부족 우선" : "배정 후보",
          warning: unit.shortageRatio > 0.35,
          stats: [
            {label: "생산 속도", value: `${fmt(daily)}/day`},
            {label: "총 가능 수량", value: `${fmt(quantity)}대`},
            {label: "예상 시간", value: planRoute.duration_min ? `${fmt(Math.round(planRoute.duration_min))}분` : "현장/미정"},
            {label: "예상 비용", value: planRoute.estimated_trip_cost_krw ? `${fmt(planRoute.estimated_trip_cost_krw)}원` : "0원/미정"},
            {label: "신뢰도", value: pct(factory.confidence || route.capacity_confidence || 0)},
            {label: "검증", value: statusText(route.routing_status || "candidate")},
          ],
          note: `${routeCostText(planRoute)} · ${routeEvidenceText(planRoute)}`,
        });
      }).join("");
      return sheetSection(
        unit.name,
        `D+${fmt(unit.deadline_day)} · 부족 ${fmt(unit.shortage)}대`,
        `
          ${sheetMetrics([
            {label: "필요 드론", value: missionText(unit.profile_id).label},
            {label: "요청 수량", value: fmt(unit.requested)},
            {label: "현재 준비량", value: fmt(unit.prepared)},
            {label: "우선도", value: pct(unit.urgency), warn: unit.urgency >= 0.82},
          ])}
          ${routeCardList(factories)}
        `,
      );
    })
    .join("");
  openOpsSheet(
    "부대 현황",
    unitId ? "선택 부대 보급 상세" : "보급 우선순위 상세",
    content,
    {kind: "unit", itemId: unitId, side: "right", subtitle: "우측 수요 카드에서 이어지는 보급 우선순위 상세입니다."},
  );
}

function openProcurementDashboardModal(materialId = "") {
  const rows = materialId ? procurementRows().filter((row) => row.material_id === materialId) : procurementRows();
  const content = rows
    .map((row) => {
      const seaRows = row.maritimeRoutes
        .map(
          (route) =>
            routeCard({
              title: `${route.origin_port_name} → ${route.destination_port_name}`,
              subtitle: `${materialLabel(row.material_id, {short: true})} 해상 수입 경로`,
              routeId: route.id,
              materialId: row.material_id,
              status: statusText(route.status),
              warning: Number(route.risk_score || 0) >= 0.28,
              stats: [
                {label: "수입량", value: `${fmt(route.import_capacity_kg_30d)}kg`},
                {label: "거리", value: `${fmt(route.distance_nm)}해리`},
                {label: "예상 시간", value: `${fmt(Math.round(route.duration_hours_estimate || 0))}시간`},
                {label: "위험", value: pct(route.risk_score), warn: Number(route.risk_score || 0) >= 0.28},
              ],
              note: statusText(route.routing_status || "maritime_corridor_estimate"),
            }),
        )
        .join("");
      const roadRows = row.roadRoutes
        .slice(0, 6)
        .map(
          (route) =>
            routeCard({
              title: `${route.port_name} → ${route.target_factory_name}`,
              subtitle: partCategoryText(route.target_part_category).label,
              routeId: route.id,
              factoryId: route.target_factory_id,
              materialId: row.material_id,
              status: statusText(route.routing_status || route.status),
              stats: [
                {label: "물량", value: `${fmt(route.quantity_kg_30d)}kg`},
                {label: "거리", value: routeDistanceText(route)},
                {label: "예상 시간", value: route.duration_min ? `${fmt(Math.round(route.duration_min))}분` : "미정"},
                {label: "예상 비용", value: route.estimated_trip_cost_krw ? `${fmt(route.estimated_trip_cost_krw)}원` : "미정"},
              ],
              note: `${routeCostText(route)} · ${statusText(route.routing_status || route.status)}`,
            }),
        )
        .join("");
      return sheetSection(
        materialLabel(row.material_id),
        `${fmt(row.available)} / ${fmt(row.required)}kg · ${pct(row.coverage)}`,
        `
          ${opsProgressBar(row.coverage)}
          ${sheetMetrics([
            {label: "필요량", value: `${fmt(row.required)}kg`},
            {label: "가용량", value: `${fmt(row.available)}kg`},
            {label: "부족량", value: `${fmt(row.shortage)}kg`, warn: row.shortage > 0},
            {label: "연결 경로", value: `${fmt(row.maritimeRoutes.length + row.roadRoutes.length)}개`},
          ])}
          ${sheetSection("권장 해상 경로", "해외 공급원 → 한국 수입항", routeCardList(seaRows))}
          ${sheetSection("권장 공급 경로", "수입항 → 부품/조립 공장", routeCardList(roadRows))}
        `,
      );
    })
    .join("");
  openOpsSheet(
    "원료/부품 조달 현황",
    materialId ? "선택 원료 조달 상세" : "필수 원료/부품 조달 상세",
    content,
    {kind: "procurement", itemId: materialId, side: "right", subtitle: "우측 조달 카드에서 이어지는 경로 중심 상세입니다."},
  );
}

function renderMaterialSupplySummary() {
  const plan = currentPlan();
  const scale = currentScenarioScale();
  const materialRows = (plan.raw_material_supply_summary || [])
    .slice()
    .sort((a, b) => Number(a.coverage_ratio || 0) - Number(b.coverage_ratio || 0))
    .map((item) => {
      const required = Math.round(Number(item.required_kg_30d || 0) * scale);
      const available = Number(item.total_available_kg_30d || 0);
      const coverage = required ? Math.min(1, available / required) : 0;
      const shortfall = Math.max(0, required - available);
      return `
        <div class="plan-row material-summary-row">
          <div>
            <div class="plan-title">
              <span>${escapeHtml(materialLabel(item.material_id))}</span>
              <span>${pct(coverage)}</span>
            </div>
            <div class="coverage-bar"><div class="coverage-fill" style="width:${Math.max(4, Math.round(coverage * 100))}%; background:${escapeHtml(
              materialColor(item.material_id),
            )}"></div></div>
            <div class="plan-sub">
              ${escapeHtml((item.feeds_part_categories || []).map((category) => partCategoryText(category).label).join(" / "))} ·
              수입 ${fmt(item.import_supply_kg_30d)} kg · 국내 회수 ${fmt(item.domestic_resource_supply_kg)} kg · 보유재고 ${fmt(
                item.existing_factory_inventory_kg,
              )} kg
            </div>
          </div>
          <div class="plan-qty">
            ${fmt(available)} / ${fmt(required)}
            <br />${shortfall ? `${fmt(shortfall)} kg 부족` : "충족"}
          </div>
        </div>
      `;
    })
    .join("");
  const missionRows = (data.drone_mission_profiles || [])
    .map(
      (profile) => `
        <div class="resource-plan-row mission-profile-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(missionText(profile.profile_id).label)}</strong>
            <small>${pct(profile.default_mix_share)} 구성비 · ${escapeHtml(missionText(profile.profile_id).use || profile.safe_use || "운용 프로파일")} · ${
              Object.keys(profile.material_kg_per_drone || {}).length
            }개 원료 투입</small>
          </span>
        </div>
      `,
    )
    .join("");
  const weakestMaterial = (plan.raw_material_supply_summary || [])
    .slice()
    .sort((a, b) => Number(a.material_feasible_drones_30d || 0) - Number(b.material_feasible_drones_30d || 0))[0];
  elementById("materialSupplySummary").innerHTML = `
    <p class="source-note">원자재 수급은 공장 보유 재고, 국내 회수/재활용 후보, 해외 수입 경로를 합산한 demo backdata입니다. 실제 운용 전에는 공급계약, 통관, 항만 처리능력, 품질 등급 검증이 필요합니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(Object.keys(rawMaterialCatalog).length)}</strong><span>원자재 카탈로그</span></div>
      <div class="metric-box"><strong>${fmt((plan.maritime_import_route_segments || []).length)}</strong><span>해상 수입 경로</span></div>
      <div class="metric-box"><strong>${fmt((plan.port_to_factory_material_routes || []).length)}</strong><span>항만-공장 원료 경로</span></div>
      <div class="metric-box"><strong>${fmt(weakestMaterial?.material_feasible_drones_30d || 0)}</strong><span>원료 기준 최소 가능 수량</span></div>
    </div>
    <div class="plan-list">${materialRows}</div>
    <div class="resource-plan">
      <p class="toggle-section-title">드론 운용 구성 / BOM 기준</p>
      ${missionRows}
    </div>
  `;
}

function renderAlliedSupplySummary() {
  const countries = [...new Set(alliedSupplySources.map((source) => source.country).filter(Boolean))];
  const linkedStagingCount = new Set(alliedSupplySources.flatMap((source) => source.staging_source_ids || [])).size;
  const materialCount = new Set(alliedSupplySources.flatMap((source) => source.material_ids || [])).size;
  const rows = alliedSupplySources
    .map((source) => {
      const materials = (source.material_ids || []).map((id) => materialLabel(id, {short: true})).join(" / ");
      const components = (source.component_ids || []).map((id) => componentCatalog[id]?.short_label || componentCatalog[id]?.label || id).join(" / ");
      const staging = source.staging_port_name || (source.staging_source_ids || []).join(" / ") || "일본 경유지 미정";
      return `
        <div class="resource-plan-row allied-source-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(source.country)} · ${escapeHtml(source.source_port_name || "출발 항만 미정")}</strong>
            <small>${escapeHtml(source.supply_role || "공급 역할 미정")}</small>
            <small>경유 ${escapeHtml(staging)} · ${escapeHtml(materials || components || "연계 원료 미정")} · 신뢰도 ${escapeHtml(
              source.confidence || "미정",
            )}</small>
          </span>
        </div>
      `;
    })
    .join("");
  elementById("alliedSupplySummary").innerHTML = `
    <p class="source-note">우방국 원료/부품 후보는 공개 리서치 기반의 sourcing hypothesis입니다. 실제 조달 판단 전에는 공급계약, 수출통제, 항만 처리능력, 품질 등급, 일본 staging 가능성을 별도로 검증해야 합니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(alliedSupplySources.length)}</strong><span>우방국/협력 소스</span></div>
      <div class="metric-box"><strong>${fmt(countries.length)}</strong><span>연결 국가</span></div>
      <div class="metric-box"><strong>${fmt(materialCount)}</strong><span>연계 원료군</span></div>
      <div class="metric-box"><strong>${fmt(linkedStagingCount)}</strong><span>일본 staging nodes</span></div>
    </div>
    <div class="resource-plan">${rows}</div>
  `;
}

function renderBlockadeSurvivalSummary() {
  const plan = currentPlan();
  const headline = plan.blockade_survival_headline || {};
  const survival = headline.survival_days || {};
  const valley = headline.valley || {};
  const bottleneck = headline.bottleneck || {};
  const subBottleneck = headline.subcomponent_bottleneck || {};
  const componentRows = (plan.component_survival_summary || [])
    .slice()
    .sort((a, b) => Number(a.bottleneck_rank || 99) - Number(b.bottleneck_rank || 99))
    .slice(0, 8)
    .map((item) => {
      const days = item.survival_days || {};
      const gap = Number(item.ramp_gap_days || 0);
      return `
        <div class="plan-row blockade-row">
          <div>
            <div class="plan-title">
              <span>${escapeHtml(item.component_label)}</span>
              <span>${fmt(days.likely)}d</span>
            </div>
            <div class="plan-sub">
              ${escapeHtml(item.part_label)} · demand ${fmt(item.daily_demand_units)} ${escapeHtml(item.unit)}/day · burn ${fmt(
                item.net_burn_units_per_day,
              )}/day · ramp D+${fmt(item.ramp_ready_day)}
            </div>
          </div>
          <div class="plan-qty">
            P10 ${fmt(days.p10)}d
            <br />${gap ? `${fmt(gap)}d gap` : "no gap"}
          </div>
        </div>
      `;
    })
    .join("");
  const subRows = (plan.subcomponent_survival_summary || [])
    .slice(0, 5)
    .map((item) => {
      const days = item.survival_days || {};
      return `
        <div class="resource-plan-row">
          <span class="route-color"></span>
          <span>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${escapeHtml(item.type)} · ${fmt(item.daily_demand_units)} ${escapeHtml(item.unit)}/day · survival ${fmt(
              days.likely,
            )}d · ${escapeHtml(item.import_dependency)}</small>
          </span>
        </div>
      `;
    })
    .join("");
  elementById("blockadeSurvivalSummary").innerHTML = `
    <p class="source-note">완전봉쇄 시 완성부품 재고, 국내 라인 램프업, 칩/자석 등 서브부품 제약을 합산한 synthetic survival model입니다. 실제 의사결정 전에는 ERP/MES/조달/재고 피드로 교체해야 합니다.</p>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(survival.likely || 0)}d</strong><span>최약 부품 생존일수</span></div>
      <div class="metric-box"><strong>${escapeHtml(bottleneck.label || "-")}</strong><span>부품 병목</span></div>
      <div class="metric-box"><strong>${fmt(valley.start_day || 0)}-${fmt(valley.end_day || 0)}</strong><span>램프업 골짜기 D-day</span></div>
      <div class="metric-box"><strong>${escapeHtml(subBottleneck.label || "-")}</strong><span>서브부품 병목</span></div>
    </div>
    <div class="metric-grid">
      <div class="metric-box"><strong>${fmt(headline.blockade_total_producible?.likely || 0)}</strong><span>완전봉쇄 총 가능량</span></div>
      <div class="metric-box"><strong>${fmt(headline.required_units_per_day || blockadeDemandModel.required_fpv_class_units_per_day || 0)}</strong><span>소모 기반 일수요</span></div>
      <div class="metric-box"><strong>${pct(headline.fiber_variant_share || 0)}</strong><span>광섬유형 share</span></div>
      <div class="metric-box"><strong>${fmt(valley.depth_units_per_day || 0)}</strong><span>골짜기 일 부족량</span></div>
    </div>
    <div class="plan-list">${componentRows}</div>
    <div class="resource-plan">
      <p class="toggle-section-title">Deep subcomponent constraints</p>
      ${subRows}
    </div>
  `;
}

function renderApacExtension() {
  const extension = data.apac_extension || {};
  const materialRows = (data.material_requirements || [])
    .map(
      (item) => `
        <li>
          <span class="safe-dot"></span>
          <span><strong>${escapeHtml(item.label)}</strong><br />${escapeHtml(item.linked_bom_item)} · ${escapeHtml(item.verification_need)}</span>
        </li>
      `,
    )
    .join("");
  elementById("apacExtension").innerHTML = `
    <p class="apac-note">Critical materials · resource-aware production continuity</p>
    <ul class="apac-list material-list">${materialRows}</ul>
    <p class="apac-note">${escapeHtml(extension.title || "APAC allied sustainment C2")} · ${escapeHtml(extension.priority || "follow-on")}</p>
    <ul class="apac-list">
      ${(extension.design_direction || [])
        .map((item) => `<li><span class="safe-dot"></span><span>${escapeHtml(item)}</span></li>`)
        .join("")}
    </ul>
  `;
}

function renderScenarioStep() {
  updateViewModeClass();
  renderScenarioLiveTabs();
  renderCaseTicker();
  renderFactoryScopeControls();
  renderLayerToggles();
  renderMapMeta();
  renderMap();
  renderFlowLedger();
  renderDecisionCards();
}

function renderAll() {
  setupChromeControls();
  updateViewModeClass();
  renderTopbar();
  renderScenarioTabs();
  renderScenarioLiveTabs();
  renderCaseTicker();
  renderFactoryScopeControls();
  renderLayerToggles();
  renderSafeBoundary();
  renderMapMeta();
  renderMap();
  if (state.selectedKind) {
    renderSelectedDetails();
  } else {
    closeDetailsDrawer();
  }
  renderPlanSummary();
  renderFlowLedger();
  renderOptimizationResultSummary();
  renderReconfigurationSummary();
  renderPowerRiskSummary();
  renderOperationalState();
  renderMaterialSupplySummary();
  renderAlliedSupplySummary();
  renderBlockadeSurvivalSummary();
  renderApacExtension();
  renderDecisionCards();
}

renderDemandControl();
renderAll();
setTimeout(() => {
  if (mapState.map) mapState.map.invalidateSize();
  applyMapPreset(state.mapPresetId);
}, 250);
