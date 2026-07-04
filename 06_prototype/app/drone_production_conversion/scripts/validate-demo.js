const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const failures = [];

function fail(message) {
  failures.push(message);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function readWindowAssignment(relativePath, key) {
  const code = fs.readFileSync(path.join(root, relativePath), "utf8");
  const context = {window: {}};
  vm.runInNewContext(code, context, {filename: relativePath, timeout: 5000});
  return context.window[key];
}

function uniqueValues(values) {
  return [...new Set((values || []).filter(Boolean))];
}

function checkDuplicates(label, rows) {
  const seen = new Set();
  const duplicates = [];
  rows.forEach((row) => {
    if (!row.id) return;
    if (seen.has(row.id)) duplicates.push(row.id);
    seen.add(row.id);
  });
  assert(!duplicates.length, `${label} has duplicate ids: ${duplicates.slice(0, 8).join(", ")}`);
}

function assertFinitePoint(route, field, label) {
  const point = route[field];
  assert(point && Number.isFinite(Number(point.lat)) && Number.isFinite(Number(point.lon)), `${route.id} has invalid ${label} point`);
}

function haversineKm(a, b) {
  const toRad = (deg) => (Number(deg) * Math.PI) / 180;
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
  const meanLat = ((Number(point.lat) + Number(start.lat) + Number(end.lat)) / 3) * (Math.PI / 180);
  const px = Number(point.lon) * Math.cos(meanLat);
  const py = Number(point.lat);
  const ax = Number(start.lon) * Math.cos(meanLat);
  const ay = Number(start.lat);
  const bx = Number(end.lon) * Math.cos(meanLat);
  const by = Number(end.lat);
  const dx = bx - ax;
  const dy = by - ay;
  if (dx === 0 && dy === 0) return haversineKm(point, start);
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)));
  return haversineKm(point, {lat: ay + t * dy, lon: (ax + t * dx) / Math.cos(meanLat)});
}

function pointInsideImpact(point, pathPoints, corridorBufferKm = 0) {
  const insideCircle = pathPoints.some((impactPoint) => haversineKm(point, impactPoint) <= Number(impactPoint.radius_km || 0));
  const insideCorridor =
    Number(corridorBufferKm) > 0 &&
    pathPoints.some((impactPoint, index) => index > 0 && pointToSegmentKm(point, pathPoints[index - 1], impactPoint) <= Number(corridorBufferKm));
  return insideCircle || insideCorridor;
}

function routePoints(route) {
  const points = route.route_geometry && route.route_geometry.length ? route.route_geometry : [route.from, route.to];
  return points.filter(Boolean).map((point) => ({lat: Number(point.lat), lon: Number(point.lon)}));
}

function interpolatePoint(start, end, t) {
  return {
    lat: start.lat + (end.lat - start.lat) * t,
    lon: start.lon + (end.lon - start.lon) * t,
  };
}

function routeTouchesImpact(route, pathPoints, corridorBufferKm = 0) {
  const points = routePoints(route);
  if (points.length === 1) return pointInsideImpact(points[0], pathPoints, corridorBufferKm);
  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    const sampleCount = Math.max(1, Math.min(8, Math.ceil(haversineKm(start, end) / 18)));
    for (let sample = 0; sample <= sampleCount; sample += 1) {
      if (pointInsideImpact(interpolatePoint(start, end, sample / sampleCount), pathPoints, corridorBufferKm)) return true;
    }
  }
  return false;
}

function createMockElement(id = "") {
  return {
    id,
    hidden: false,
    value: "",
    textContent: "",
    innerHTML: "",
    dataset: {},
    style: {},
    classList: {
      add() {},
      remove() {},
      toggle() {},
      contains() {
        return false;
      },
    },
    setAttribute() {},
    removeAttribute() {},
    addEventListener() {},
    querySelectorAll() {
      return [];
    },
    closest() {
      return this;
    },
  };
}

function createMockLeaflet() {
  const chainable = {
    addTo() {
      return this;
    },
    bindPopup() {
      return this;
    },
    on() {
      return this;
    },
    remove() {
      return this;
    },
    setLatLng() {
      return this;
    },
  };
  return {
    map() {
      return {
        setView() {
          return this;
        },
        fitBounds() {
          return this;
        },
        invalidateSize() {
          return this;
        },
        on() {
          return this;
        },
      };
    },
    control: {
      zoom() {
        return chainable;
      },
    },
    tileLayer() {
      return chainable;
    },
    layerGroup() {
      return chainable;
    },
    divIcon(options) {
      return options;
    },
    marker() {
      return {...chainable};
    },
    polyline() {
      return {...chainable};
    },
    circle() {
      return {...chainable};
    },
  };
}

function smokeRenderApp() {
  const elements = new Map();
  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, createMockElement(id));
      return elements.get(id);
    },
    querySelector(selector) {
      if (selector === ".map-first-shell") return this.getElementById("appShell");
      return createMockElement(selector);
    },
    querySelectorAll() {
      return [];
    },
    addEventListener() {},
  };
  const context = {
    window: {
      DRONE_PRODUCTION_CONVERSION_DATASET: datasetJson,
      DRONE_OPTIMIZATION_RESULT_V0_9: optimizer,
      DRONE_RECONFIGURATION_RESULT_V1_0: reconfiguration,
    },
    document,
    L: createMockLeaflet(),
    console,
    performance: {now: () => 0},
    setTimeout() {
      return 0;
    },
    clearTimeout() {},
    setInterval() {
      return 0;
    },
    clearInterval() {},
    requestAnimationFrame() {
      return 1;
    },
    cancelAnimationFrame() {},
  };
  vm.runInNewContext(fs.readFileSync(path.join(root, "assets/app.js"), "utf8"), context, {
    filename: "assets/app.js",
    timeout: 10000,
  });
}

const datasetJson = readJson("data/drone_production_conversion_dataset.json");
const datasetJs = readWindowAssignment("data/drone_production_conversion_dataset.js", "DRONE_PRODUCTION_CONVERSION_DATASET");
const optimizer = readWindowAssignment("data/optimizer_result_v0_9.js", "DRONE_OPTIMIZATION_RESULT_V0_9");
const reconfiguration = readWindowAssignment("data/reconfiguration_result_v1_0.js", "DRONE_RECONFIGURATION_RESULT_V1_0");

assert(datasetJson.schema === datasetJs.schema, "dataset JSON and JS schema mismatch");
assert(datasetJson.generated_at === datasetJs.generated_at, "dataset JSON and JS generated_at mismatch");

const factories = datasetJson.factory_candidates || [];
const resources = datasetJson.resource_candidates || [];
const ports = datasetJson.import_ports || [];
const plans = datasetJson.plans || [];
const factoryIds = new Set(factories.map((factory) => factory.id));
const resourceIds = new Set(resources.map((resource) => resource.id));
const portIds = new Set(ports.map((port) => port.id));

checkDuplicates("factory_candidates", factories);
checkDuplicates("resource_candidates", resources);
checkDuplicates("import_ports", ports);
checkDuplicates("plans", plans);

["baseline", "western_axis_threat", "southern_port_disruption"].forEach((scenarioId) => {
  assert(plans.some((plan) => plan.id === scenarioId), `missing plan ${scenarioId}`);
  assert((optimizer.scenarios || []).some((scenario) => scenario.scenario_id === scenarioId), `missing optimizer scenario ${scenarioId}`);
  assert((reconfiguration.scenarios || []).some((scenario) => scenario.scenario_id === scenarioId), `missing reconfiguration scenario ${scenarioId}`);
});

plans.forEach((plan) => {
  (plan.route_segments || []).forEach((route) => {
    assert(factoryIds.has(route.factory_id), `${plan.id}:${route.id} missing factory_id ${route.factory_id}`);
    assert(factoryIds.has(route.destination_factory_id), `${plan.id}:${route.id} missing destination_factory_id ${route.destination_factory_id}`);
    assertFinitePoint(route, "from", "from");
    assertFinitePoint(route, "to", "to");
  });
  (plan.resource_route_segments || []).forEach((route) => {
    assert(resourceIds.has(route.resource_id), `${plan.id}:${route.id} missing resource_id ${route.resource_id}`);
    assert(factoryIds.has(route.target_factory_id), `${plan.id}:${route.id} missing target_factory_id ${route.target_factory_id}`);
    assertFinitePoint(route, "from", "from");
    assertFinitePoint(route, "to", "to");
  });
  (plan.port_to_factory_material_routes || []).forEach((route) => {
    assert(portIds.has(route.port_id), `${plan.id}:${route.id} missing port_id ${route.port_id}`);
    assert(factoryIds.has(route.target_factory_id), `${plan.id}:${route.id} missing target_factory_id ${route.target_factory_id}`);
    assertFinitePoint(route, "from", "from");
    assertFinitePoint(route, "to", "to");
  });
  (plan.maritime_import_route_segments || []).forEach((route) => {
    assert(portIds.has(route.destination_port_id), `${plan.id}:${route.id} missing destination_port_id ${route.destination_port_id}`);
    assertFinitePoint(route, "from", "from");
    assertFinitePoint(route, "to", "to");
  });
});

const impactEvents = datasetJson.scenario_impact_events || [];
const westernImpact = impactEvents.find((event) => event.scenario_id === "western_axis_threat");
const southernImpact = impactEvents.find((event) => event.scenario_id === "southern_port_disruption");
assert(westernImpact?.geometry?.path?.length >= 2, "western impact geometry missing path");
assert(southernImpact?.geometry?.path?.length >= 2, "southern impact geometry missing path");

if (southernImpact) {
  const southernPlan = plans.find((plan) => plan.id === "southern_port_disruption") || {};
  const pathPoints = southernImpact.geometry.path || [];
  const corridorBufferKm = Number(southernImpact.geometry.corridor_buffer_km || 0);
  const impactedPortIds = uniqueValues(ports.filter((port) => pointInsideImpact(port, pathPoints, corridorBufferKm)).map((port) => port.id));
  const impactedPortSet = new Set(impactedPortIds);
  const blockedSeaRoutes = (southernPlan.maritime_import_route_segments || []).filter(
    (route) => impactedPortSet.has(route.destination_port_id) || routeTouchesImpact(route, pathPoints, corridorBufferKm),
  );
  const hiddenMaterialRoutes = (southernPlan.port_to_factory_material_routes || []).filter(
    (route) => impactedPortSet.has(route.port_id) || routeTouchesImpact(route, pathPoints, corridorBufferKm),
  );
  assert(impactedPortIds.includes("port_busan"), "southern scenario should disable Busan port");
  assert(impactedPortIds.includes("port_ulsan"), "southern scenario should disable Ulsan port");
  assert(blockedSeaRoutes.length >= 3, "southern scenario should block Japan-to-port sea routes");
  assert(hiddenMaterialRoutes.length >= 1, "southern scenario should hide downstream material routes");
}

try {
  smokeRenderApp();
} catch (error) {
  fail(`app smoke render failed: ${error.stack || error.message}`);
}

if (failures.length) {
  console.error("Validation failed:");
  failures.slice(0, 50).forEach((message) => console.error(`- ${message}`));
  process.exit(1);
}

console.log(
  JSON.stringify(
    {
      status: "ok",
      factories: factories.length,
      resources: resources.length,
      ports: ports.length,
      plans: plans.length,
      impactEvents: impactEvents.length,
    },
    null,
    2,
  ),
);
