---
title: Mazak VTC 300
theme: dashboard
toc: false
---

# MTConnect Dashboard for Mazak VTC 300

This dashboard provides real-time monitoring of the Mazak VTC 300 machine using processed MTConnect data streams with enhanced analytics and error handling.

<!-- Load and process the combined MTConnect data -->

```js
// Load processed data from CSV files
const samplesData = FileAttachment("data/processed/samples.csv").csv({typed: true});
const eventsData = FileAttachment("data/processed/events.csv").csv({typed: true});
const conditionsData = FileAttachment("data/processed/conditions.csv").csv({typed: true});
const metadataData = FileAttachment("data/processed/metadata.csv").csv({typed: true});
```

```js
// Filter data for VTC 300 machine
const machineName = "mazak_2_vtc_300";

// Filter and process samples data with enhanced validation
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
  .filter(d => !isNaN(d.value) && isFinite(d.value))
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
// Calculate KPI values with proper error handling
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

// Enhanced efficiency metrics with validation
const totalTime = Math.max(latestSamples.total_time || 0, 1); // Avoid division by zero
const cutTime = latestSamples.cut_time || 0;
const autoTime = latestSamples.auto_time || 0;

// Cap efficiency at 100% to avoid calculation errors
const efficiency = Math.min(totalTime > 0 ? (cutTime / totalTime * 100) : 0, 100);
const utilization = Math.min(totalTime > 0 ? (autoTime / totalTime * 100) : 0, 100);

// Enhanced power calculations with validation
const powerData = samples.filter(d => d.item === "power" && isFinite(d.value));
const latestPower = powerData.slice(-1)[0]?.value || 0;
const avgPower = powerData.length > 0 ? 
  powerData.reduce((sum, d) => sum + d.value, 0) / powerData.length : 0;
const maxPower = powerData.length > 0 ? Math.max(...powerData.map(d => d.value)) : 0;
```

<!-- Machine Status Header with Enhanced Styling -->

```js
// Machine Status Header
display(html`<div class="hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 1rem; text-align: center; margin: 2rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
  <h2 style="margin: 0; font-size: 2rem;">Mazak VTC 300 - Live Status</h2>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
    Data Sources: ${machineInfo.length} files | 
    Last Updated: ${new Date(Math.max(...samples.map(d => d.ts), ...events.map(d => d.ts))).toLocaleString()}
  </p>
  <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
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
</div>`)
```

<!-- Enhanced KPI Cards -->

```js
// Enhanced KPI Cards
display(html`<div class="grid grid-cols-4">
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
</div>`)
```

```js
display(html`<div class="grid grid-cols-3">
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
</div>`)
```

<!-- Enhanced Chart functions with better error handling -->

```js
function axisPositionsChart(data, {width} = {}) {
  const positionData = data.filter(d => 
    /[XYZ]abs/.test(d.item) && 
    d.ts && 
    d.ts instanceof Date && 
    isFinite(d.value)
  );
  
  if (positionData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Axis Positions Over Time</h4>
      <p>No position data available</p>
    </div>`;
  }
  
  try {
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
  } catch (error) {
    console.error("Error creating axis positions chart:", error);
    return html`<div style="text-align: center; padding: 2rem; color: #ef4444;">
      <h4>Axis Positions Over Time</h4>
      <p>Error rendering chart: ${error.message}</p>
    </div>`;
  }
}
```

```js
function axisLoadsChart(data, {width} = {}) {
  const axisLoads = data.filter(d => 
    /(X|Y|Z)load/.test(d.item) && 
    d.ts && 
    d.ts instanceof Date && 
    isFinite(d.value)
  );
  const spindleLoad = data.filter(d => 
    d.item === "Sload" && 
    d.ts && 
    d.ts instanceof Date && 
    isFinite(d.value)
  );
  
  if (axisLoads.length === 0 && spindleLoad.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Axis & Spindle Loads</h4>
      <p>No load data available</p>
    </div>`;
  }
  
  try {
    return Plot.plot({
      title: "Axis & Spindle Loads",
      width,
      height: 300,
      x: {type: "time", nice: true},
      y: {label: "Load (%)", domain: [-100, 100]},
      color: {legend: true},
      marks: [
        ...(axisLoads.length > 0 ? [Plot.line(axisLoads, {
          x: "ts", 
          y: "value", 
          stroke: "item"
        })] : []),
        ...(spindleLoad.length > 0 ? [Plot.line(spindleLoad, {
          x: "ts", 
          y: "value", 
          stroke: "red",
          strokeWidth: 2
        })] : []),
        Plot.ruleY([0], {stroke: "gray", strokeDasharray: "2,2"})
      ]
    });
  } catch (error) {
    console.error("Error creating axis loads chart:", error);
    return html`<div style="text-align: center; padding: 2rem; color: #ef4444;">
      <h4>Axis & Spindle Loads</h4>
      <p>Error rendering chart: ${error.message}</p>
    </div>`;
  }
}
```

```js
function spindleChart(data, {width} = {}) {
  // More robust data filtering and validation
  const spindleData = data.filter(d => 
    d.item === "Srpm" && 
    d.ts && 
    d.ts instanceof Date && 
    isFinite(d.value) && 
    d.value !== null && 
    d.value !== undefined &&
    !isNaN(d.value)
  );
  
  console.log("Spindle data:", spindleData.length, spindleData.slice(0, 3));
  
  if (spindleData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Spindle RPM</h4>
      <p>No spindle data available</p>
    </div>`;
  }
  
  try {
    // Ensure data is properly formatted for Plot.js
    const plotData = spindleData.map(d => ({
      ts: d.ts,
      value: Number(d.value)
    }));
    
    return Plot.plot({
      title: "Spindle RPM",
      width,
      height: 300,
      x: {type: "time", nice: true, label: null},
      y: {label: "RPM"},
      marks: [
        Plot.line(plotData, {
          x: "ts", 
          y: "value", 
          stroke: "red",
          strokeWidth: 2
        }),
        Plot.dot(plotData.filter((d, i) => i % Math.max(1, Math.floor(plotData.length / 20)) === 0), {
          x: "ts", 
          y: "value", 
          fill: "red",
          r: 3
        })
      ]
    });
  } catch (error) {
    console.error("Error creating spindle chart:", error);
    return html`<div style="text-align: center; padding: 2rem; color: #ef4444;">
      <h4>Spindle RPM</h4>
      <p>Error rendering chart: ${error.message}</p>
      <p>Data points: ${spindleData.length}</p>
    </div>`;
  }
}
```

```js
function powerChart(data, {width} = {}) {
  const powerData = data.filter(d => 
    d.item === "power" && 
    d.ts && 
    d.ts instanceof Date && 
    isFinite(d.value)
  );
  
  if (powerData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Machine Power Consumption</h4>
      <p>No power data available</p>
    </div>`;
  }
  
  try {
    const avgPowerValue = powerData.reduce((sum, d) => sum + d.value, 0) / powerData.length;
    
    return Plot.plot({
      title: "Machine Power Consumption",
      width,
      height: 300,
      x: {type: "time", nice: true, label: null},
      y: {label: "Power (kW)"},
      marks: [
        Plot.line(powerData, {
          x: "ts", 
          y: "value", 
          stroke: "steelblue"
        }),
        Plot.area(powerData, {
          x: "ts", 
          y: "value", 
          fill: "steelblue",
          fillOpacity: 0.2
        }),
        Plot.ruleY([avgPowerValue], {stroke: "red", strokeDasharray: "3,3"})
      ]
    });
  } catch (error) {
    console.error("Error creating power chart:", error);
    return html`<div style="text-align: center; padding: 2rem; color: #ef4444;">
      <h4>Machine Power Consumption</h4>
      <p>Error rendering chart: ${error.message}</p>
    </div>`;
  }
}
```

```js
function dataTypeComparisonChart(samplesData, eventsData, {width} = {}) {
  const currentSamples = samplesData.filter(d => d.dataType === "current");
  const sampleSamples = samplesData.filter(d => d.dataType === "sample");
  
  const comparisonData = [
    {source: "Current Data", count: currentSamples.length, color: "#ef4444"},
    {source: "Sample Data", count: sampleSamples.length, color: "#10b981"}
  ];
  
  if (comparisonData.every(d => d.count === 0)) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Data Type Comparison</h4>
      <p>No data available for comparison</p>
    </div>`;
  }
  
  return Plot.plot({
    title: "Data Source Distribution",
    width,
    height: 300,
    x: {label: "Data Source"},
    y: {label: "Record Count"},
    marks: [
      Plot.barY(comparisonData, {
        x: "source",
        y: "count",
        fill: "color",
        title: d => `${d.source}: ${d.count} records`
      }),
      Plot.text(comparisonData, {
        x: "source",
        y: d => d.count + 5,
        text: d => d.count.toString(),
        fontSize: 14,
        fontWeight: "bold"
      })
    ]
  });
}
```

```js
function overrideChart(data, {width} = {}) {
  const overrideData = data.filter(d => ["Fovr", "Frapidovr"].includes(d.item) && d.ts && isFinite(d.value));
  
  if (overrideData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Feed & Rapid Override</h4>
      <p>No override data available</p>
    </div>`;
  }
  
  return Plot.plot({
    title: "Feed & Rapid Override",
    width,
    height: 300,
    x: {type: "time", nice: true, label: null},
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
    ["estop", "execution", "mode", "avail"].includes(d.item) && d.ts
  );
  
  if (stateData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">
      <h4>Machine State Timeline</h4>
      <p>No state timeline data available</p>
    </div>`;
  }
  
  // Add next timestamp for rectangle width
  const stateTimelineData = stateData.map((d, i) => ({
    ...d,
    next: i < stateData.length - 1 ? stateData[i + 1].ts : new Date(d.ts.getTime() + 60000)
  }));
  
  return Plot.plot({
    title: "Machine State Timeline",
    width,
    height: 200,
    x: {type: "time", label: null},
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

<!-- Enhanced Charts Layout -->

```js
display(html`<div class="grid grid-cols-2">
  <div class="card">${resize((width) => axisPositionsChart(samples, {width}))}</div>
  <div class="card">${resize((width) => axisLoadsChart(samples, {width}))}</div>
</div>`)
```

```js
display(html`<div class="grid grid-cols-2">
  <div class="card">${resize((width) => spindleChart(samples, {width}))}</div>
  <div class="card">${resize((width) => powerChart(samples, {width}))}</div>
</div>`)
```

```js
display(html`<div class="grid grid-cols-2">
  <div class="card">${resize((width) => dataTypeComparisonChart(samples, events, {width}))}</div>
  <div class="card">${resize((width) => overrideChart(events, {width}))}</div>
</div>`)
```

```js
display(html`<div class="grid grid-cols-1">
  <div class="card">${resize((width) => stateTimelineChart(events, {width}))}</div>
</div>`)
```

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

// Enhanced spindle RPM calculation
const latestSpindleRPM = samples.filter(d => d.item === "Srpm").slice(-1)[0]?.value || 0;

display(html`<div class="grid grid-cols-2">
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
      <li>Spindle RPM: ${latestSpindleRPM.toFixed(0)}</li>
      <li>Power: ${latestPower.toFixed(1)} kW</li>
    </ul>
  </div>
</div>`)
```

<!-- Enhanced Performance Metrics with Better Organization -->

```js
display(html`<div class="grid grid-cols-2">
  <div class="card">
    <h3>System Loads</h3>
    <ul>
      <li>X Load: <span style="color: ${Math.abs(latestLoads.Xload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Xload?.toFixed(1) || 'N/A'}%</span></li>
      <li>Y Load: <span style="color: ${Math.abs(latestLoads.Yload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Yload?.toFixed(1) || 'N/A'}%</span></li>
      <li>Z Load: <span style="color: ${Math.abs(latestLoads.Zload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Zload?.toFixed(1) || 'N/A'}%</span></li>
      <li>Spindle Load: <span style="color: ${Math.abs(latestLoads.Sload || 0) > 80 ? 'red' : 'green'}">${latestLoads.Sload?.toFixed(1) || 'N/A'}%</span></li>
    </ul>
  </div>
  <div class="card">
    <h3>Performance Metrics</h3>
    <ul>
      <li>Cutting Efficiency: <span style="color: ${efficiency > 70 ? 'green' : efficiency > 50 ? 'orange' : 'red'}">${efficiency.toFixed(1)}%</span></li>
      <li>Machine Utilization: <span style="color: ${utilization > 80 ? 'green' : utilization > 60 ? 'orange' : 'red'}">${utilization.toFixed(1)}%</span></li>
      <li>Average Power: <span style="color: ${avgPower > 0 ? 'green' : 'orange'}">${avgPower.toFixed(1)} kW</span></li>
      <li>Data Coverage: ${((samples.length + events.length) / 1000).toFixed(1)}K data points</li>
    </ul>
  </div>
</div>`)
```

<!-- Enhanced Power Analysis with Error Handling -->

```js
display(html`<div class="card">
  <h3>Power Analysis</h3>
  <div class="grid grid-cols-4">
    <div style="text-align: center;">
      <strong style="font-size: 1.2em; color: steelblue;">${latestPower.toFixed(1)} kW</strong>
      <div style="font-size: 0.8em; color: gray;">Current</div>
    </div>
    <div style="text-align: center;">
      <strong style="font-size: 1.2em; color: green;">${avgPower.toFixed(1)} kW</strong>
      <div style="font-size: 0.8em; color: gray;">Average</div>
    </div>
    <div style="text-align: center;">
      <strong style="font-size: 1.2em; color: red;">${maxPower.toFixed(1)} kW</strong>
      <div style="font-size: 0.8em; color: gray;">Peak</div>
    </div>
    <div style="text-align: center;">
      <strong style="font-size: 1.2em; color: orange;">${(efficiency * avgPower / 100).toFixed(1)} kW</strong>
      <div style="font-size: 0.8em; color: gray;">Efficiency</div>
    </div>
  </div>
</div>`)
```

<!-- Conditions Table -->

```js
const abnormalConditions = conditions.filter(d => d.state !== "Normal" && d.state !== "#text");

display(html`<div class="card">
  <h3>System Conditions</h3>
  ${abnormalConditions.length === 0 ? 
    html`<p>All systems showing Normal status ✅</p>` : 
    Inputs.table(abnormalConditions.map(d => ({
      Timestamp: d.ts.toLocaleString(),
      Component: d.component,
      Category: d.category,
      State: d.state,
      "Data Type": d.dataType
    })))
  }
</div>`)
```

---

```js
display(html`<div>
<p><em>Dashboard updated: ${new Date().toLocaleString()}</em></p>

<p><strong>Data Sources:</strong> Combined processed MTConnect data from ${machineInfo.length} files<br/>
<strong>Machine:</strong> Mazak VTC 300 CNC<br/>
<strong>Total Data Points:</strong> ${(samples.length + events.length + conditions.length).toLocaleString()}<br/>
<strong>Power Monitoring:</strong> ${powerData.length} power readings</p>
</div>`)
```
