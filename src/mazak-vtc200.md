---
title: Mazak VTC 200
theme: dashboard
toc: false
---

# MTConnect Dashboard for Mazak VTC 200

This dashboard provides real-time monitoring of the Mazak VTC 200 machine using processed MTConnect data streams.

<!-- Load and process the combined MTConnect data -->

```js
// Load processed data from CSV files
const samplesData = FileAttachment("data/processed/samples.csv").csv({typed: true});
const eventsData = FileAttachment("data/processed/events.csv").csv({typed: true});
const conditionsData = FileAttachment("data/processed/conditions.csv").csv({typed: true});
const metadataData = FileAttachment("data/processed/metadata.csv").csv({typed: true});
```

```js
// Filter data for VTC 200 machine
const machineName = "mazak_1_vtc_200";

// Filter and process samples data
const samples = samplesData
  .filter(d => d.machine_name === machineName)
  .map(d => ({
    component: d.component_id,
    item: d.sample_name,
    subtype: d.sub_type,
    ts: new Date(d.timestamp),
    value: +d.value,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .filter(d => !isNaN(d.value))
  .sort((a, b) => a.ts - b.ts);

// Filter and process events data
const events = eventsData
  .filter(d => d.machine_name === machineName)
  .map(d => ({
    component: d.component_id,
    item: d.event_name,
    ts: new Date(d.timestamp),
    value: isNaN(+d.value) ? d.value : +d.value,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .sort((a, b) => a.ts - b.ts);

// Filter and process conditions data
const conditions = conditionsData
  .filter(d => d.machine_name === machineName)
  .map(d => ({
    component: d.component_id,
    item: d.condition_name,
    ts: new Date(d.timestamp),
    state: d.state,
    category: d.category,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .sort((a, b) => a.ts - b.ts);

// Get machine metadata
const machineInfo = metadataData.filter(d => d.machine_name === machineName);
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

// Calculate efficiency metrics
const totalTime = latestSamples.total_time || 0;
const cutTime = latestSamples.cut_time || 0;
const autoTime = latestSamples.auto_time || 0;

const efficiency = totalTime > 0 ? (cutTime / totalTime * 100) : 0;
const utilization = totalTime > 0 ? (autoTime / totalTime * 100) : 0;
```

<!-- Machine Status Header -->

<div class="hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 1rem; text-align: center; margin: 2rem 0;">
  <h2 style="margin: 0; font-size: 2rem;">Mazak VTC 200 - Live Status</h2>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
    Data Sources: ${machineInfo.length} files | 
    Last Updated: ${new Date(Math.max(...samples.map(d => d.ts), ...events.map(d => d.ts))).toLocaleString()}
  </p>
  <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem;">
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      Samples: ${samples.length.toLocaleString()}
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      Events: ${events.length.toLocaleString()}
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      Conditions: ${conditions.length.toLocaleString()}
    </span>
  </div>
</div>

<!-- KPI Cards -->

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Auto Time</h2>
    <span class="big">${(latestSamples.auto_time / 3600).toFixed(1)} hrs</span>
    <small>Automatic operation time</small>
  </div>
  <div class="card">
    <h2>Cut Time</h2>
    <span class="big">${(latestSamples.cut_time / 3600).toFixed(1)} hrs</span>
    <small>Active cutting time</small>
  </div>
  <div class="card">
    <h2>Total Time</h2>
    <span class="big">${(latestSamples.total_time / 3600).toFixed(1)} hrs</span>
    <small>Total operation time</small>
  </div>
  <div class="card">
    <h2>Efficiency</h2>
    <span class="big" style="color: ${efficiency > 70 ? 'green' : efficiency > 50 ? 'orange' : 'red'}">${efficiency.toFixed(1)}%</span>
    <small>Cut time / Total time</small>
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
    title: "Axis Positions Over Time",
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
      }),
      Plot.dot(positionData.filter((d, i) => i % 10 === 0), {
        x: "ts", 
        y: "value", 
        fill: "item", 
        r: 2
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
      }),
      Plot.ruleY([0], {stroke: "gray", strokeDasharray: "2,2"})
    ]
  });
}
```

```js
function spindleChart(data, {width} = {}) {
  const spindleData = data.filter(d => d.item === "Srpm" && !isNaN(d.value) && d.value !== null);
  
  // Handle case when no valid spindle data is available
  if (spindleData.length === 0) {
    return Plot.plot({
      title: "Spindle RPM",
      width,
      height: 300,
      x: {type: "time", nice: true},
      y: {label: "RPM", domain: [0, 1000]},
      marks: [
        Plot.text([{ts: new Date(), value: 500}], {
          x: "ts", 
          y: "value", 
          text: ["No spindle data available"],
          fontSize: 14,
          fill: "gray",
          textAnchor: "middle"
        })
      ]
    });
  }
  
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
function dataTypeComparisonChart(samplesData, eventsData, {width} = {}) {
  // Compare current vs sample data types
  const currentSamples = samplesData.filter(d => d.dataType === "current");
  const sampleSamples = samplesData.filter(d => d.dataType === "sample");
  
  return Plot.plot({
    title: "Data Type Comparison - Sample Count by Component",
    width,
    height: 300,
    x: {label: "Component"},
    y: {label: "Sample Count"},
    color: {legend: true},
    marks: [
      Plot.barY(currentSamples, Plot.groupX({y: "count"}, {x: "component", fill: "current"})),
      Plot.barY(sampleSamples, Plot.groupX({y: "count"}, {x: "component", fill: "sample", dx: 20}))
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
    height: 200,
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
    ${resize((width) => dataTypeComparisonChart(samples, events, {width}))}
  </div>
</div>

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => stateTimelineChart(events, {width}))}
  </div>
</div>

<div class="grid grid-cols-1">
  <div class="card">
    ${resize((width) => overrideChart(events, {width}))}
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

// Get latest load values
const latestLoads = samples.filter(d => /(X|Y|Z)load|Sload/.test(d.item))
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

<div class="grid grid-cols-2">
  <div class="card">
    <h3>System Loads</h3>
    <ul>
      <li>X Load: <span style="color: ${(latestLoads.Xload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Xload?.toFixed(1) || 'N/A'}%</span></li>
      <li>Y Load: <span style="color: ${(latestLoads.Yload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Yload?.toFixed(1) || 'N/A'}%</span></li>
      <li>Z Load: <span style="color: ${(latestLoads.Zload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Zload?.toFixed(1) || 'N/A'}%</span></li>
      <li>Spindle Load: <span style="color: ${(latestLoads.Sload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Sload?.toFixed(1) || 'N/A'}%</span></li>
    </ul>
  </div>
  <div class="card">
    <h3>Performance Metrics</h3>
    <ul>
      <li>Cutting Efficiency: <span style="color: ${efficiency > 70 ? 'green' : efficiency > 50 ? 'orange' : 'red'}">${efficiency.toFixed(1)}%</span></li>
      <li>Machine Utilization: <span style="color: ${utilization > 80 ? 'green' : utilization > 60 ? 'orange' : 'red'}">${utilization.toFixed(1)}%</span></li>
      <li>Data Coverage: ${((samples.length + events.length) / 1000).toFixed(1)}K data points</li>
    </ul>
  </div>
</div>

<!-- Conditions Table -->

```js
const abnormalConditions = conditions.filter(d => d.state !== "Normal" && d.state !== "#text");
```

<div class="card">
  <h3>System Conditions</h3>
  ${abnormalConditions.length === 0 ? 
    "All systems showing Normal status ✅" : 
    Inputs.table(abnormalConditions.map(d => ({
      Timestamp: d.ts.toLocaleString(),
      Component: d.component,
      Category: d.category,
      State: d.state,
      "Data Type": d.dataType
    })))
  }
</div>

---

*Dashboard updated: ${new Date().toLocaleString()}*

**Data Sources:** Combined processed MTConnect data from ${machineInfo.length} files  
**Machine:** Mazak VTC 200 CNC  
**Total Data Points:** ${(samples.length + events.length + conditions.length).toLocaleString()}
