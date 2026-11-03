import * as C from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";

interface Aircraft { hex: string; call: string; lat: number; lon: number; alt: number; vel: number; hdg: number; vr: number;
  kind?: string; reg?: string; squawk?: string; mach?: number; }
interface Feed { aircraft: Aircraft[]; source: string; age_s: number; stale: boolean; }
interface Plane extends Aircraft { bb: C.Billboard; trail: number[][]; nearAt: number; }
interface Airport { iata: string; location: string; name: string; lat: number; lon: number; countryiso2: string; }

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const AC = new Map<string, Plane>();
let selected: string | null = null;
let userBusy = false;
let counterShown = 0;

/* ---------------- globe ---------------- */
C.Ion.defaultAccessToken = "";
const viewer = new C.Viewer("globe", {
  baseLayer: false, baseLayerPicker: false, geocoder: false, homeButton: false, sceneModePicker: false, navigationHelpButton: false,
  animation: false, timeline: false, fullscreenButton: false, infoBox: false, selectionIndicator: false, skyBox: false as unknown as undefined,
});
(window as unknown as { __jeb: unknown }).__jeb = { viewer };
const scene = viewer.scene, globe = scene.globe, camera = scene.camera;
const esri = (svc: string, max: number, credit: string) => new C.UrlTemplateImageryProvider({
  url: `https://services.arcgisonline.com/ArcGIS/rest/services/${svc}/MapServer/tile/{z}/{y}/{x}`, maximumLevel: max, credit });
const day = new Date(Date.now() - 36e5 * 30).toISOString().slice(0, 10);   // NASA GIBS publishes yesterday's pass
const clouds = new C.UrlTemplateImageryProvider({
  url: `https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_SNPP_CorrectedReflectance_TrueColor/default/${day}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg`,
  maximumLevel: 8, credit: "NASA GIBS / VIIRS" });
const L = {
  sat: viewer.imageryLayers.addImageryProvider(esri("World_Imagery", 18, "Imagery © Esri, Maxar")),
  roads: viewer.imageryLayers.addImageryProvider(esri("Reference/World_Transportation", 15, "Roads © Esri")),
  labels: viewer.imageryLayers.addImageryProvider(esri("Reference/World_Boundaries_and_Places", 13, "Labels © Esri")),
  relief: viewer.imageryLayers.addImageryProvider(esri("NatGeo_World_Map", 12, "Map © Esri, National Geographic")),
  night: viewer.imageryLayers.addImageryProvider(new C.UrlTemplateImageryProvider({
    url: "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
    maximumLevel: 8, credit: "NASA Black Marble" })),
  live: viewer.imageryLayers.addImageryProvider(clouds),
};
L.sat.nightAlpha = 0.12; L.night.dayAlpha = 0; L.night.nightAlpha = 1;   // real city lights on the night side
function setTheme(t: "dark" | "light") {
  document.documentElement.dataset.theme = t;
  try { localStorage.setItem("theme", t); } catch { /* storage may be blocked */ }
  const dark = t === "dark";
  L.sat.show = dark; L.labels.show = dark; L.roads.show = dark; L.night.show = dark; L.relief.show = !dark;
  globe.enableLighting = dark; globe.showGroundAtmosphere = true;
  globe.baseColor = C.Color.fromCssColorString(dark ? "#0a1a2c" : "#bcd6e6");
  scene.backgroundColor = C.Color.fromCssColorString(dark ? "#05080d" : "#dfe8ef");
  scene.skyAtmosphere!.brightnessShift = dark ? 0.1 : 0.25;
  scene.fog.enabled = true;
  L.live.alpha = dark ? 0.5 : 0.4;
}
L.live.brightness = 1.05;
scene.skyAtmosphere!.hueShift = -0.02; globe.atmosphereLightIntensity = 14; globe.maximumScreenSpaceError = 1.4;
scene.screenSpaceCameraController.minimumZoomDistance = 60;
viewer.clock.shouldAnimate = true; viewer.clock.currentTime = C.JulianDate.now();
camera.setView({ destination: C.Cartesian3.fromDegrees(20, 25, 2.6e7) });
let saved: string | null = null;
try { saved = localStorage.getItem("theme"); } catch { /* default dark */ }
setTheme(saved === "light" ? "light" : "dark");
$("theme").onclick = () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");

/* ---------------- aircraft ---------------- */
const bills = scene.primitives.add(new C.BillboardCollection({ scene })) as C.BillboardCollection;
const labels = scene.primitives.add(new C.LabelCollection({ scene })) as C.LabelCollection;
function icon(): HTMLCanvasElement {
  const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d")!;
  g.translate(32, 32); g.beginPath();
  g.moveTo(0, -28); g.lineTo(4, -12); g.lineTo(27, 4); g.lineTo(27, 9); g.lineTo(4, 3); g.lineTo(3, 18); g.lineTo(11, 25); g.lineTo(11, 29);
  g.lineTo(0, 26); g.lineTo(-11, 29); g.lineTo(-11, 25); g.lineTo(-3, 18); g.lineTo(-4, 3); g.lineTo(-27, 9); g.lineTo(-27, 4); g.lineTo(-4, -12); g.closePath();
  g.fillStyle = "#fff"; g.fill(); g.lineWidth = 3; g.strokeStyle = "rgba(0,0,0,.55)"; g.stroke(); return c;
}
const ICON = icon();
const SEL = C.Color.fromCssColorString("#ff8a1f");
const altColor = (m: number) => m < 3000 ? C.Color.fromCssColorString("#ffb454") : m < 8000 ? C.Color.fromCssColorString("#c8f26b") : C.Color.fromCssColorString("#cdeeff");
const pos = (a: Aircraft) => C.Cartesian3.fromDegrees(a.lon, a.lat, Math.max(a.alt, 0));

function upsert(a: Aircraft, near = false): Plane {
  let p = AC.get(a.hex);
  if (!p) {
    const bb = bills.add({ image: ICON, scale: 0.34, alignedAxis: C.Cartesian3.UNIT_Z, id: a.hex,
      scaleByDistance: new C.NearFarScalar(2e5, 1.15, 2.4e7, 0.26), position: C.Cartesian3.ZERO });
    p = { ...a, bb, trail: [], nearAt: 0 }; AC.set(a.hex, p);
  } else {
    const keep = { kind: p.kind, reg: p.reg, squawk: p.squawk, mach: p.mach };
    Object.assign(p, a, { kind: a.kind ?? keep.kind, reg: a.reg ?? keep.reg, squawk: a.squawk ?? keep.squawk, mach: a.mach ?? keep.mach });
  }
  if (near) p.nearAt = performance.now();
  p.bb.rotation = -C.Math.toRadians(p.hdg);
  p.bb.color = a.hex === selected ? SEL : altColor(p.alt);
  p.bb.position = pos(p);
  return p;
}

async function pullGlobal() {
  try {
    const f = await invoke<Feed>("global_flights");
    const seen = new Set<string>();
    for (const a of f.aircraft) {
      seen.add(a.hex); const cur = AC.get(a.hex);
      if (cur && performance.now() - cur.nearAt < 40000) continue;    // fresher detailed data wins
      upsert(a);
    }
    for (const [hex, p] of AC) if (!seen.has(hex) && performance.now() - p.nearAt > 90000 && hex !== selected) { bills.remove(p.bb); AC.delete(hex); }
    $("feed").textContent = `${f.source.toUpperCase()} · ${f.stale ? "STALE " : "LIVE "}${f.age_s}s`;
    renderList();
  } catch { /* keep flying on the last real data */ }
}
function center(): { lat: number; lon: number } | null {
  const r = scene.canvas.getBoundingClientRect();
  const p = camera.pickEllipsoid(new C.Cartesian2(r.width / 2, r.height / 2), globe.ellipsoid);
  if (!p) return null; const g = C.Cartographic.fromCartesian(p);
  return { lat: C.Math.toDegrees(g.latitude), lon: C.Math.toDegrees(g.longitude) };
}
async function pullNearAt(lat: number, lon: number) {
  try {
    const f = await invoke<Feed>("near_flights", { lat, lon });
    for (const a of f.aircraft) upsert(a, true);
    const s = selected && AC.get(selected); if (s) { fillDetail(s); loadPhoto(s); }
    renderList();
  } catch { /* offline: positions keep dead-reckoning */ }
}
async function pullNear() {
  if (camera.positionCartographic.height > 3.5e6) return;
  const c = center(); if (c) pullNearAt(c.lat, c.lon);
}

/* dead reckoning between pulls: every aircraft keeps moving along its real heading and speed */
let lastAll = performance.now(), lastFrame = performance.now();
function advance(p: Plane, dt: number) {
  if (!p.vel) return;
  const h = C.Math.toRadians(p.hdg);
  p.lat += (p.vel * Math.cos(h) * dt) / 111320;
  p.lon += (p.vel * Math.sin(h) * dt) / (111320 * Math.max(Math.cos(C.Math.toRadians(p.lat)), 0.05));
  p.alt += p.vr * dt; p.bb.position = pos(p);
}
scene.preRender.addEventListener(() => {
  const now = performance.now(), dt = (now - lastFrame) / 1000; lastFrame = now;
  const h = camera.positionCartographic.height, c = h < 4e6 ? center() : null;
  if (now - lastAll > 250) { for (const p of AC.values()) advance(p, (now - lastAll) / 1000); lastAll = now; }
  else if (c) for (const p of AC.values()) if (Math.abs(p.lat - c.lat) < 6 && Math.abs(p.lon - c.lon) < 9) advance(p, dt);
  const s = selected ? AC.get(selected) : undefined; if (s) trackSelected(s);
  if (!userBusy && !selected && h > 8e6) camera.rotate(C.Cartesian3.UNIT_Z, -0.0009);
  L.live.show = h > 1.2e6;      // daily satellite cloud layer only where its resolution holds up
  counterShown += (AC.size - counterShown) * 0.08; $("count").textContent = Math.round(counterShown).toLocaleString("en-US");
});
scene.canvas.addEventListener("pointerdown", () => { userBusy = true; });
scene.canvas.addEventListener("pointerup", () => { setTimeout(() => (userBusy = false), 6000); });

/* callsign labels on the planes nearest the view centre */
setInterval(() => {
  labels.removeAll();
  const c = camera.positionCartographic.height < 1.6e6 ? center() : null; if (!c) return;
  const d = (a: Aircraft) => (a.lat - c.lat) ** 2 + (a.lon - c.lon) ** 2;
  const near = [...AC.values()].filter((a) => a.call && Math.abs(a.lat - c.lat) < 6 && Math.abs(a.lon - c.lon) < 9).sort((x, y) => d(x) - d(y)).slice(0, 90);
  const dark = document.documentElement.dataset.theme === "dark";
  for (const a of near) labels.add({ position: pos(a), text: a.call, font: "600 12px ui-monospace, Menlo, monospace",
    fillColor: dark ? C.Color.WHITE : C.Color.fromCssColorString("#10202e"), outlineColor: (dark ? C.Color.BLACK : C.Color.WHITE).withAlpha(0.85), outlineWidth: 3,
    style: C.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new C.Cartesian2(14, -10), horizontalOrigin: C.HorizontalOrigin.LEFT,
    distanceDisplayCondition: new C.DistanceDisplayCondition(0, 1.6e6) });
}, 700);

/* ---------------- selection ---------------- */
const lines = scene.primitives.add(new C.PolylineCollection()) as C.PolylineCollection;
const trail = lines.add({ width: 2.2, material: C.Material.fromType("Color", { color: SEL }), positions: [] });
const ahead = lines.add({ width: 2, material: C.Material.fromType("PolylineDash", { color: C.Color.WHITE.withAlpha(0.85), dashLength: 14 }), positions: [] });
let lastTrail = 0;
function trackSelected(p: Plane) {
  const now = performance.now(); if (now - lastTrail < 1000) return; lastTrail = now;
  p.trail.push([p.lon, p.lat, p.alt]); if (p.trail.length > 600) p.trail.shift();
  if (p.trail.length > 1) trail.positions = C.Cartesian3.fromDegreesArrayHeights(p.trail.flat());
  const h = C.Math.toRadians(p.hdg), pts: number[] = [];
  for (let i = 0; i <= 12; i++) { const s = p.vel * 120 * i;
    pts.push(p.lon + (s * Math.sin(h)) / (111320 * Math.cos(C.Math.toRadians(p.lat))), p.lat + (s * Math.cos(h)) / 111320, p.alt); }
  ahead.positions = C.Cartesian3.fromDegreesArrayHeights(pts); fillDetail(p);
}
function select(hex: string, fly = true) {
  const prev = selected ? AC.get(selected) : undefined; if (prev) prev.bb.color = altColor(prev.alt);
  selected = hex; const p = AC.get(hex); if (!p) return;
  p.bb.color = SEL; p.trail = []; trail.positions = []; ahead.positions = [];
  $("detail").classList.add("open"); fillDetail(p); loadPhoto(p); loadRoute(p); renderList();
  if (fly) camera.flyTo({ destination: C.Cartesian3.fromDegrees(p.lon, p.lat - 1.9, 300000),
    orientation: { heading: 0, pitch: C.Math.toRadians(-55), roll: 0 }, duration: 3.2 });
  pullNearAt(p.lat, p.lon);
}
function fillDetail(p: Plane) {
  $("did").textContent = p.call || p.hex.toUpperCase();
  $("dsub").textContent = [p.kind, p.reg].filter(Boolean).join(" · ") || "Aircraft";
  $("dpos").textContent = `${p.lat.toFixed(3)}° · ${p.lon.toFixed(3)}°`;
  $("dalt").textContent = Math.round(p.alt * 3.28084).toLocaleString("en-US"); $("dspd").textContent = String(Math.round(p.vel * 3.6));
  $("dhdg").textContent = String(Math.round(p.hdg)); $("dvr").textContent = p.vr.toFixed(1); $("dsq").textContent = p.squawk ?? "—";
  $("dmach").textContent = p.mach ? p.mach.toFixed(3) : "—"; $("dhex").textContent = p.hex.toUpperCase(); $("dreg").textContent = p.reg ?? "—";
  $("dbar").style.width = Math.min(100, (p.alt / 13000) * 100) + "%";
  updateProgress(p);
}
let photoFor = "", routeFor = "", route: { from: Airport; to: Airport } | null = null;
async function loadPhoto(p: Plane) {
  if (!p.reg || photoFor === p.reg) return; photoFor = p.reg; const box = $("dphoto"); box.innerHTML = "";
  try {
    const r = await invoke<{ src?: string; by?: string } | null>("photo", { reg: p.reg });
    if (!r?.src || photoFor !== p.reg) return;
    const im = new Image(); im.src = r.src; im.alt = p.reg; const by = document.createElement("span"); by.textContent = "© " + (r.by ?? ""); box.append(im, by);
  } catch { /* no photo is fine */ }
}
async function loadRoute(p: Plane) {
  if (!p.call || routeFor === p.call) return; routeFor = p.call; route = null; $("droute").innerHTML = "";
  try {
    const r = await invoke<{ from: Airport; to: Airport } | null>("route", { call: p.call });
    if (!r || routeFor !== p.call) return; route = r;
    $("droute").innerHTML = `<div class="route"><div class="cell"><label>From</label><b>${r.from.iata}</b><small>${r.from.location}</small></div>
      <div class="cell"><label>To</label><b>${r.to.iata}</b><small>${r.to.location}</small></div></div>
      <div class="prog"><i id="rprog" style="width:0"></i></div><div class="prog-l"><span>scheduled route</span><span id="rleft"></span></div>`;
    updateProgress(p);
  } catch { /* route unknown */ }
}
const km = (a: number, b: number, c: number, d: number) => { const r = Math.PI / 180, x = Math.sin(((c - a) * r) / 2) ** 2 + Math.cos(a * r) * Math.cos(c * r) * Math.sin(((d - b) * r) / 2) ** 2; return 12742 * Math.asin(Math.sqrt(x)); };
function updateProgress(p: Plane) {
  if (!route || !document.getElementById("rprog")) return;
  const total = km(route.from.lat, route.from.lon, route.to.lat, route.to.lon), left = km(p.lat, p.lon, route.to.lat, route.to.lon);
  $("rprog").style.width = Math.max(0, Math.min(100, (1 - left / Math.max(total, 1)) * 100)) + "%";
  $("rleft").textContent = `${Math.round(left).toLocaleString("en-US")} km to go` + (p.vel > 50 ? ` · ${(left / (p.vel * 3.6)).toFixed(1)} h` : "");
}
$("dclose").onclick = () => {
  $("detail").classList.remove("open"); const p = selected ? AC.get(selected) : undefined; if (p) p.bb.color = altColor(p.alt);
  selected = null; photoFor = routeFor = ""; route = null; trail.positions = []; ahead.positions = []; renderList();
};
new C.ScreenSpaceEventHandler(scene.canvas).setInputAction((m: { position: C.Cartesian2 }) => {
  const p = scene.pick(m.position); if (p && typeof p.id === "string" && AC.has(p.id)) select(p.id);
}, C.ScreenSpaceEventType.LEFT_CLICK);
$("zin").onclick = () => camera.zoomIn(camera.positionCartographic.height * 0.4);
$("zout").onclick = () => camera.zoomOut(camera.positionCartographic.height * 0.6);

/* ---------------- list + search ---------------- */
const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);
const row = (a: Plane) => `<div class="it${a.hex === selected ? " sel" : ""}" data-h="${a.hex}"><div class="t"><span>${esc(a.call || a.hex.toUpperCase())}</span><em>LIVE</em></div>
  <div class="s"><span>${esc([a.kind, a.reg].filter(Boolean).join(" · ") || "—")}</span><span>${Math.round((a.alt * 3.28084) / 100) * 100} ft · ${Math.round(a.vel * 3.6)} km/h</span></div></div>`;
let listT: number | undefined;
function renderList() {
  clearTimeout(listT);
  listT = window.setTimeout(() => {
    const q = ($("q") as HTMLInputElement).value.trim().toLowerCase(); let html: string;
    if (q) {
      const m = [...AC.values()].filter((a) => a.call.toLowerCase().includes(q) || (a.reg ?? "").toLowerCase().includes(q) || a.hex.includes(q)).slice(0, 14);
      html = m.length ? m.map(row).join("") : `<div class="empty">No match in live traffic.</div>`;
    } else {
      const c = center(), pool = [...AC.values()].filter((a) => a.call);
      const pick = c ? pool.sort((x, y) => (x.lat - c.lat) ** 2 + (x.lon - c.lon) ** 2 - ((y.lat - c.lat) ** 2 + (y.lon - c.lon) ** 2)).slice(0, 14) : pool.slice(0, 14);
      html = `<h4>${c ? "Near view centre" : "Tracking list"}</h4>` + pick.map(row).join("");
    }
    $("list").innerHTML = html;
  }, 120);
}
$("q").addEventListener("input", renderList);
$("q").addEventListener("keydown", (e) => { if ((e as KeyboardEvent).key === "Enter") focusQuery(($("q") as HTMLInputElement).value); });
$("list").addEventListener("click", (e) => { const it = (e.target as HTMLElement).closest<HTMLElement>(".it"); if (it?.dataset.h) select(it.dataset.h); });
setInterval(() => { if (!($("q") as HTMLInputElement).value) renderList(); }, 4000);
function focusQuery(q: string) {
  q = q.trim().toLowerCase(); if (!q) return;
  const all = [...AC.values()];
  const a = all.find((x) => x.call.toLowerCase() === q || (x.reg ?? "").toLowerCase() === q) ?? all.find((x) => x.call.toLowerCase().startsWith(q));
  if (a) select(a.hex);
}

/* ---------------- voice-driven map control ---------------- */
listen<{ kind: string; action?: string; query?: string }>("jeb-event", async ({ payload: e }) => {
  if (e.kind !== "map" || e.action === "hide" || !e.query) return;
  const g = await invoke<{ lat: number; lon: number } | null>("geocode", { q: e.query });
  if (g) camera.flyTo({ destination: C.Cartesian3.fromDegrees(g.lon, g.lat, 1500), orientation: { heading: 0, pitch: C.Math.toRadians(-45), roll: 0 }, duration: 5 });
});

/* ---------------- boot ---------------- */
(async () => {
  await pullGlobal(); $("boot").classList.add("gone"); $("globe").classList.add("ready");
  camera.flyTo({ destination: C.Cartesian3.fromDegrees(25, 30, 1.6e7), duration: 4 });
  setInterval(pullGlobal, 10000);     // core serves from cache; real refresh is 15 min anonymous, 10 s with OpenSky credentials
  setInterval(pullNear, 5000);
})();
