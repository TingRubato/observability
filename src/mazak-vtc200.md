---
title: Mazak VTC 200
theme: dashboard
toc: false
---

# MTConnect Dashboard for Mazak VTC 200

This dashboard provides real-time monitoring of the Mazak VTC 200 machine using MTConnect data streams.

<!-- Load and normalize the MTConnect data -->

```js
const rawData = FileAttachment("data/vtc200.json").json();
```

```js
// Normalize nested stream structure into flat typed arrays
const samples = [];
const events = [];
const conditions = [];

// Extract samples, events, and conditions from all components
Object.entries(rawData.device.components).forEach(([componentId, component]) => {
  // Process samples
  if (component.samples) {
    Object.entries(component.samples).forEach(([itemId, sample]) => {
      if (sample.value !== null && sample.value !== undefined) {
        samples.push({
          component: componentId,
          item: itemId,
          subtype: sample.subType || null,
          ts: new Date(sample.timestamp),
          value: Number(sample.value)
        });
      }
    });
  }
  
  // Process events
  if (component.events) {
    Object.entries(component.events).forEach(([itemId, event]) => {
      if (event.value !== null && event.value !== undefined) {
        events.push({
          component: componentId,
          item: itemId,
          ts: new Date(event.timestamp),
          value: String(event.value)
        });
      }
    });
  }
  
  // Process conditions
  if (component.conditions) {
    Object.entries(component.conditions).forEach(([itemId, condition]) => {
      conditions.push({
        component: componentId,
        item: itemId,
        ts: new Date(condition.timestamp),
        state: condition.state,
        category: condition.category
      });
    });
  }
});

// Sort by timestamp
samples.sort((a, b) => a.ts - b.ts);
events.sort((a, b) => a.ts - b.ts);
conditions.sort((a, b) => a.ts - b.ts);
```

```js
// Calculate KPI values from the latest data
const latestSamples = samples.filter(d => 
  ['auto_time', 'cut_time', 'total_time'].includes(d.item)
).reduce((acc, d) => {
  acc[d.item] = d.value;
  return acc;
}, {});

const latestEvents = events.filter(d => 
  ['avail', 'mode', 'estop'].includes(d.item)
).reduce((acc, d) => {
  acc[d.item] = d.value;
  return acc;
}, {});
```

<!-- KPI Cards -->

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Auto Time</h2>
    <span class="big">${(latestSamples.auto_time / 3600).toFixed(1)} hrs</span>
  </div>
  <div class="card">
    <h2>Cut Time</h2>
    <span class="big">${(latestSamples.cut_time / 3600).toFixed(1)} hrs</span>
  </div>
  <div class="card">
    <h2>Total Time</h2>
    <span class="big">${(latestSamples.total_time / 3600).toFixed(1)} hrs</span>
  </div>
</div>

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Availability</h2>
    <span class="big" style="color: ${latestEvents.avail === 'AVAILABLE' ? 'green' : 'orange'}">${latestEvents.avail || 'Unknown'}</span>
  </div>
  <div class="card">
    <h2>Mode</h2>
    <span class="big">${latestEvents.mode || 'Unknown'}</span>
  </div>
  <div class="card">
    <h2>E-Stop</h2>
    <span class="big" style="color: ${latestEvents.estop === 'ARMED' ? 'green' : 'red'}">${latestEvents.estop || 'Unknown'}</span>
  </div>
</div>

<!-- Chart functions -->

```js
function axisPositionsChart(data, {width} = {}) {
  const positionData = data.filter(d => /[XYZ]abs/.test(d.item));
  
  return Plot.plot({
    title: "Axis Positions",
    width,
    height: 300,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    color: {legend: true},
    marks: [
      Plot.line(positionData, {
        x: "ts", 
        y: "value", 
        stroke: "item", 
        curve: "step"
      })
    ]
  });
}
```

```js
function axisLoadsChart(data, {width} = {}) {
  const axisLoads = data.filter(d => /(X|Y|Z)load/.test(d.item));
  const spindleLoad = data.filter(d => d.item === "Sload");
  
  return Plot.plot({
    title: "Axis & Spindle Loads",
    width,
    height: 300,
    x: {type: "time", nice: true},
    y: {label: "Load (%)", domain: [-100, 100]},
    color: {legend: true},
    marks: [
      Plot.line(axisLoads, {
        x: "ts", 
        y: "value", 
        stroke: "item"
      }),
      Plot.line(spindleLoad, {
        x: "ts", 
        y: "value", 
        stroke: "red",
        strokeWidth: 2
      })
    ]
  });
}
```

```js
function spindleChart(data, {width} = {}) {
  const spindleData = data.filter(d => d.item === "Srpm");
  
  return Plot.plot({
    title: "Spindle RPM",
    width,
    height: 300,
    x: {type: "time", nice: true},
    y: {label: "RPM"},
    marks: [
      Plot.line(spindleData, {
        x: "ts", 
        y: "value", 
        stroke: "red"
      })
    ]
  });
}
```

```js
function overrideChart(data, {width} = {}) {
  const overrideData = data.filter(d => ["Fovr", "Frapidovr"].includes(d.item));
  
  return Plot.plot({
    title: "Feed & Rapid Override",
    width,
    height: 300,
    x: {type: "time", nice: true},
    y: {label: "Override (%)"},
    color: {legend: true},
    marks: [
      Plot.line(overrideData, {
        x: "ts", 
        y: "value", 
        stroke: "item"
      })
    ]
  });
}
```

```js
function stateTimelineChart(data, {width} = {}) {
  const stateData = data.filter(d => 
    ["estop", "execution", "mode", "avail"].includes(d.item)
  );
  
  // Add next timestamp for rectangle width
  const stateTimelineData = stateData.map((d, i) => ({
    ...d,
    next: i < stateData.length - 1 ? stateData[i + 1].ts : new Date(d.ts.getTime() + 60000)
  }));
  
  return Plot.plot({
    title: "Machine State Timeline",
    width,
    height: 150,
    x: {type: "time"},
    y: {type: "band", domain: ["estop", "execution", "mode", "avail"]},
    color: {legend: true},
    marks: [
      Plot.rect(stateTimelineData, {
        x1: "ts", 
        x2: "next", 
        y: "item", 
        fill: "value", 
        inset: 0.5
      })
    ]
  });
}
```

<!-- Charts Layout -->

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => axisPositionsChart(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => axisLoadsChart(samples, {width}))}
  </div>
</div>

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => spindleChart(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => overrideChart(events, {width}))}
  </div>
</div>

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => stateTimelineChart(events, {width}))}
  </div>
</div>

<!-- Current Status Summary -->

## Current Status Summary

```js
// Get latest position data
const latestPositions = samples.filter(d => /[XYZ]abs/.test(d.item))
  .reduce((acc, d) => {
    acc[d.item] = d.value;
    return acc;
  }, {});

// Get latest tool and program info
const latestProgram = events.filter(d => ["program", "Tool_number"].includes(d.item))
  .reduce((acc, d) => {
    acc[d.item] = d.value;
    return acc;
  }, {});
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Current Position</h3>
    <ul>
      <li>X: ${latestPositions.Xabs?.toFixed(2) || 'N/A'} mm</li>
      <li>Y: ${latestPositions.Yabs?.toFixed(2) || 'N/A'} mm</li>
      <li>Z: ${latestPositions.Zabs?.toFixed(2) || 'N/A'} mm</li>
    </ul>
  </div>
  <div class="card">
    <h3>Current Operation</h3>
    <ul>
      <li>Program: ${latestProgram.program || 'N/A'}</li>
      <li>Tool: ${latestProgram.Tool_number || 'N/A'}</li>
      <li>Spindle RPM: ${samples.filter(d => d.item === "Srpm").slice(-1)[0]?.value || 0}</li>
    </ul>
  </div>
</div>

<!-- Conditions Table -->

```js
const abnormalConditions = conditions.filter(d => d.state !== "Normal");
```

<div class="card">
  <h3>System Conditions</h3>
  ${abnormalConditions.length === 0 ? 
    "All systems showing Normal status ✅" : 
    Inputs.table(abnormalConditions.map(d => ({
      Timestamp: d.ts.toLocaleString(),
      Component: d.component,
      Category: d.category,
      State: d.state
    })))
  }
</div>

---

*Dashboard updated: ${new Date().toLocaleString()}*

Data: MTConnect stream from Mazak VTC 200 CNC machine
