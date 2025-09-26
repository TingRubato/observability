---
theme: dashboard
title: Production Overview
toc: false
---

# Production Overview Dashboard 📊

<!-- Load and transform the data -->

```js
// Generate sample production data for demonstration
const launches = [
  {date: new Date("2024-01-01"), state: "Running", stateId: "US", family: "Production Line A"},
  {date: new Date("2024-01-02"), state: "Running", stateId: "US", family: "Production Line A"},
  {date: new Date("2024-01-03"), state: "Maintenance", stateId: "RU", family: "Production Line B"},
  {date: new Date("2024-01-04"), state: "Running", stateId: "CN", family: "Production Line C"},
  {date: new Date("2024-01-05"), state: "Running", stateId: "US", family: "Production Line A"},
  // Add more sample data...
].concat(Array.from({length: 50}, (_, i) => ({
  date: new Date(2024, 0, i + 6),
  state: ["Running", "Idle", "Maintenance"][Math.floor(Math.random() * 3)],
  stateId: ["US", "RU", "CN"][Math.floor(Math.random() * 3)],
  family: ["Production Line A", "Production Line B", "Production Line C"][Math.floor(Math.random() * 3)]
})));
```

<!-- A shared color scale for consistency, sorted by the number of launches -->

```js
const color = Plot.scale({
  color: {
    type: "categorical",
    domain: d3.groupSort(launches, (D) => -D.length, (d) => d.state).filter((d) => d !== "Other"),
    unknown: "var(--theme-foreground-muted)"
  }
});
```

<!-- Cards with big numbers -->

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Production Line A 🏭</h2>
    <span class="big">${launches.filter((d) => d.family === "Production Line A").length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Production Line B ⚙️</h2>
    <span class="big">${launches.filter((d) => d.family === "Production Line B").length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Production Line C 🔧</h2>
    <span class="big">${launches.filter((d) => d.family === "Production Line C").length.toLocaleString("en-US")}</span>
  </div>
  <div class="card">
    <h2>Total Output</h2>
    <span class="big">${launches.length.toLocaleString("en-US")}</span>
  </div>
</div>

<!-- Plot of launch history -->

```js
function launchTimeline(data, {width} = {}) {
  return Plot.plot({
    title: "Production activity over time",
    width,
    height: 300,
    y: {grid: true, label: "Production Events"},
    color: {...color, legend: true},
    marks: [
      Plot.rectY(data, Plot.binX({y: "count"}, {x: "date", fill: "state", interval: "day", tip: true})),
      Plot.ruleY([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => launchTimeline(launches, {width}))}
  </div>
</div>

<!-- Plot of launch vehicles -->

```js
function vehicleChart(data, {width}) {
  return Plot.plot({
    title: "Production by line",
    width,
    height: 300,
    marginTop: 0,
    marginLeft: 50,
    x: {grid: true, label: "Production Events"},
    y: {label: null},
    color: {...color, legend: true},
    marks: [
      Plot.rectX(data, Plot.groupY({x: "count"}, {y: "family", fill: "state", tip: true, sort: {y: "-x"}})),
      Plot.ruleX([0])
    ]
  });
}
```

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => vehicleChart(launches, {width}))}
  </div>
</div>

Data: Sample manufacturing production data for demonstration purposes
