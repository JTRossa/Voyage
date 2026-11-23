import fs from "fs";
import * as d3 from "d3-geo";
import * as topo from "topojson-client";

const W = 600, H = 400;
const land50 = topo.feature(JSON.parse(fs.readFileSync("node_modules/world-atlas/land-50m.json")), "land");
const land110 = topo.feature(JSON.parse(fs.readFileSync("node_modules/world-atlas/land-110m.json")), "land");

// Each route: stops (5 named landmarks) and legs (waypoints between consecutive stops, inclusive)
const routes = JSON.parse(fs.readFileSync("routes.json"));
const out = {};
for (const [id, r] of Object.entries(routes)) {
  const all = r.legs.flat();
  const proj = d3.geoNaturalEarth1().rotate([-r.center, 0]);
  proj.fitExtent([[60, 45], [W - 60, H - 45]], { type: "MultiPoint", coordinates: all });
  proj.clipExtent([[0, 0], [W, H]]);
  const path = d3.geoPath(proj).digits(1);
  const land = path(r.detail === "110" ? land110 : land50);
  const grat = path(d3.geoGraticule10()) || "M0,0";
  const legs = r.legs.map(l => path({ type: "LineString", coordinates: l }));
  const stops = r.stops.map(s => { const [x, y] = proj(s.at); return { name: s.name, x: +x.toFixed(1), y: +y.toFixed(1), dx: s.dx || 0, dy: s.dy || 0 }; });
  out[id] = { land, grat, legs, stops };
  console.log(id, "land bytes", land.length);
}
fs.writeFileSync("maps.json", JSON.stringify(out));
