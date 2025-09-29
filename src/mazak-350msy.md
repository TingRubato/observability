---
title: Mazak 350MSY
theme: dashboard
toc: false
---

<style>
  .hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 2rem 0;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 1rem;
    color: white;
    text-align: center;
  }
  
  .machine-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
  }
  
  .status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
  
  .status-running { background-color: #10b981; }
  .status-idle { background-color: #f59e0b; }
  .status-alarm { background-color: #ef4444; }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  
  .metric-card {
    background: white;
    border-radius: 0.75rem;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #3b82f6;
  }
  
  .metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f2937;
    line-height: 1;
  }
  
  .metric-label {
    color: #6b7280;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.5rem;
  }
  
  .axis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
  }
  
  .performance-section {
    background: #f8fafc;
    border-radius: 1rem;
    padding: 2rem;
    margin: 2rem 0;
  }
</style>

# Mazak 350MSY - 5-Axis Manufacturing Center

<!-- Load and process data from PostgreSQL database -->

```js
// Import database connection utilities
import { createDatabaseConnection, loadDataWithFallback } from "./database-connection.js";

// Load machine-specific data from database
const machineName = "mazak_3_350msy";

// Load data from PostgreSQL database with fallback to files
const timeSeriesData = await loadDataWithFallback('timeSeries', machineName, 24); // 24 hours
const recentEvents = await loadDataWithFallback('recentEvents', machineName, 24); // 24 hours
const recentConditions = await loadDataWithFallback('recentConditions', machineName, 24); // 24 hours

// Process samples data from database
const samples = timeSeriesData
  .filter(d => d.data_type === 'sample')
  .map(d => ({
    component: d.component_id,
    item: d.name,
    subtype: d.sub_type,
    ts: new Date(d.timestamp),
    value: +d.value,
    machine: machineName,
    dataType: 'sample'
  }))
  .filter(d => !isNaN(d.value) && isFinite(d.value) && d.value !== null)
  .sort((a, b) => a.ts - b.ts);

// Process events data from database
const events = recentEvents
  .map(d => ({
    component: d.component_id,
    item: d.event_name,
    ts: new Date(d.timestamp),
    value: d.event_value != null && String(d.event_value).trim() !== '' ? d.event_value : null,
    machine: machineName,
    dataType: 'event'
  }))
  .filter(d => d.value !== null && d.value !== undefined && d.value !== '')
  .sort((a, b) => a.ts - b.ts);

// Process conditions data from database
const conditions = recentConditions
  .map(d => ({
    component: d.component_id,
    item: d.condition_name,
    ts: new Date(d.timestamp),
    state: d.state_value,
    category: d.category,
    machine: machineName,
    dataType: 'condition'
  }))
  .sort((a, b) => a.ts - b.ts);

// Debug info
console.log("Debug: Loaded from database - Samples:", samples.length, "Events:", events.length, "Conditions:", conditions.length);
console.log("Debug: Available sample items:", [...new Set(samples.map(d => d.item))]);
console.log("Debug: Available event items:", [...new Set(events.map(d => d.item))]);
```

```js
// Calculate KPI values with proper error handling
const latestSamples = samples.reduce((acc, d) => {
  // Get the latest value for each item
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

const latestEvents = events.reduce((acc, d) => {
  // Get the latest value for each item
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

// Enhanced efficiency metrics with validation
const autoTime = latestSamples['auto_time']?.value || 0;
const cutTime = latestSamples['cut_time']?.value || 0;

// Calculate efficiency metrics
const efficiency = autoTime > 0 ? Math.min((cutTime / autoTime * 100), 100) : 0;
const utilization = autoTime > 0 ? Math.min((autoTime / (autoTime + 3600) * 100), 100) : 0;

// Get position data (5-axis positions)
const positions = {
  X: latestSamples['Xabs']?.value || 0,
  Y: latestSamples['Yabs']?.value || 0,
  Z: latestSamples['Zabs']?.value || 0,
  B: latestSamples['Babs']?.value || 0,
  C: latestSamples['Cabs']?.value || 0
};

// Get load data
const loads = {
  X: latestSamples['Xload']?.value || 0,
  Y: latestSamples['Yload']?.value || 0,
  Z: latestSamples['Zload']?.value || 0,
  Spindle: latestSamples['Sload']?.value || 0
};

// Get spindle data
const spindleRPM = latestSamples['Srpm']?.value || 0;

// Machine status
const machineStatus = {
  availability: latestEvents['avail']?.value || 'Unknown',
  mode: latestEvents['mode']?.value || 'Unknown',
  estop: latestEvents['estop']?.value || 'Unknown'
};

// Check data availability
const hasSampleData = samples.length > 0;
const hasEventData = events.length > 0;
const hasPositionData = positions.X !== 0 || positions.Y !== 0 || positions.Z !== 0;
const hasLoadData = loads.X !== 0 || loads.Y !== 0 || loads.Z !== 0 || loads.Spindle !== 0;
```

```js
display(html`<div class="hero">
  <h2 style="margin: 0; font-size: 2rem;">Mazak 350MSY - 5-Axis Manufacturing Center</h2>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Advanced 5-axis CNC machining center with rotary table capabilities</p>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.8;">
    Data Sources: Current & Sample JSON files | 
    Last Updated: ${samples.length > 0 || events.length > 0 ? new Date(Math.max(...[...samples, ...events].map(d => d.ts))).toLocaleString() : 'No data available'}
  </p>
    <div class="machine-status">
      <div class="status-indicator ${machineStatus.availability === 'AVAILABLE' ? 'status-running' : 'status-idle'}"></div>
      <span>System ${machineStatus.availability === 'AVAILABLE' ? 'Online' : machineStatus.availability}</span>
    </div>
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
  ${!hasSampleData || !hasEventData ? html`
    <div style="margin-top: 1rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 0.5rem;">
      ⚠️ Limited data available for this machine. This may be due to:
      <ul style="text-align: left; margin: 0.5rem 0; padding-left: 1.5rem;">
        <li>Machine not currently connected</li>
        <li>Different data structure than expected</li>
        <li>Data processing configuration needs adjustment</li>
      </ul>
    </div>
  ` : ''}
</div>`)
```

## Key Performance Indicators

```js
display(html`<div class="grid grid-cols-4">
  <div class="metric-card">
    <div class="metric-value">${positions.X.toFixed(2)}</div>
    <div class="metric-label">X Position (mm)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">${positions.Y.toFixed(2)}</div>
    <div class="metric-label">Y Position (mm)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">${positions.Z.toFixed(2)}</div>
    <div class="metric-label">Z Position (mm)</div>
  </div>
    <div class="metric-card">
      <div class="metric-value" style="color: ${machineStatus.availability === 'AVAILABLE' ? '#10b981' : '#f59e0b'}">${machineStatus.availability}</div>
      <div class="metric-label">Machine Status</div>
    </div>
</div>`)
```

```js
display(html`<div class="performance-section">
  <h3 style="margin-top: 0;">Performance Metrics</h3>
  <div class="grid grid-cols-4">
    <div class="metric-card">
      <div class="metric-value" style="color: ${loads.X > 80 ? '#ef4444' : loads.X > 50 ? '#f59e0b' : '#10b981'}">${loads.X.toFixed(1)}%</div>
      <div class="metric-label">X Axis Load</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color: ${loads.Y > 80 ? '#ef4444' : loads.Y > 50 ? '#f59e0b' : '#10b981'}">${loads.Y.toFixed(1)}%</div>
      <div class="metric-label">Y Axis Load</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color: ${loads.Z > 80 ? '#ef4444' : loads.Z > 50 ? '#f59e0b' : '#10b981'}">${loads.Z.toFixed(1)}%</div>
      <div class="metric-label">Z Axis Load</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${spindleRPM.toFixed(0)}</div>
      <div class="metric-label">Spindle RPM</div>
    </div>
  </div>
</div>`)
```

## Data Diagnostics

```js
display(html`<div class="card" style="background: #f0f9ff; border-left: 4px solid #3b82f6;">
  <h3 style="color: #1e40af;">Data Source Analysis</h3>
  <div style="font-family: monospace; font-size: 0.875rem;">
    <p><strong>Machine:</strong> Mazak 350MSY (${machineName})</p>
    <p><strong>Sample Data:</strong> ${samples.length} records</p>
    <p><strong>Event Data:</strong> ${events.length} records</p>
    <p><strong>Condition Data:</strong> ${conditions.length} records</p>
    <p><strong>Position Data Available:</strong> ${hasPositionData ? '✅ Yes' : '❌ No'}</p>
    <p><strong>Load Data Available:</strong> ${hasLoadData ? '✅ Yes' : '❌ No'}</p>
    ${samples.length > 0 ? html`
      <p><strong>Sample Items:</strong> ${[...new Set(samples.map(d => d.item))].join(', ')}</p>
    ` : ''}
    <p><strong>Data Quality:</strong> Using optimized CSV files for optimal performance</p>
  </div>
</div>`)
```

<!-- Chart functions -->

```js
function axisPositionsChart(data, {width} = {}) {
  const positionData = data.filter(d => /[XYZ]abs/.test(d.item));
  if (!positionData || positionData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No position data available</div>`;
  }
  return Plot.plot({
    title: "Linear Axis Positions",
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
      Plot.dot(positionData, {
        x: "ts", 
        y: "value", 
        fill: "item", 
        r: 3
      })
    ]
  });
}
```

```js
function xAxisPositionWidget(data, {width} = {}) {
  const xData = data.filter(d => d.item === "Xabs");
  const latestX = positions?.X ?? 0;
  if (!xData || xData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;"><h4>X Axis Position</h4><div style="font-size: 2rem; font-weight: bold; color: #1f77b4;">${latestX.toFixed(2)} mm</div><p>Current position from latest sample</p></div>`;
  }
  
  // Limit data points for performance
  const maxPoints = 100;
  const step = Math.max(1, Math.floor(xData.length / maxPoints));
  const sampledData = xData.filter((d, i) => i % step === 0);
  return Plot.plot({
    title: `X Axis Position (${sampledData.length} of ${xData.length} points)`,
    width,
    height: 200,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    marks: [
      Plot.line(sampledData, {
        x: "ts", 
        y: "value", 
        stroke: "#1f77b4",
        strokeWidth: 2
      }),
      Plot.ruleY([latestX], {stroke: "red", strokeDasharray: "3,3"}),
      Plot.text([sampledData[sampledData.length - 1]?.ts || new Date()], {
        x: [sampledData[sampledData.length - 1]?.ts || new Date()],
        y: [latestX],
        text: [`${latestX.toFixed(2)} mm`],
        fontSize: 12,
        fill: "red",
        dx: 10
      })
    ]
  });
}
```

```js
function yAxisPositionWidget(data, {width} = {}) {
  const yData = data.filter(d => d.item === "Yabs");
  const latestY = positions?.Y ?? 0;
  if (!yData || yData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;"><h4>Y Axis Position</h4><div style="font-size: 2rem; font-weight: bold; color: #ff7f0e;">${latestY.toFixed(2)} mm</div><p>Current position from latest sample</p></div>`;
  }
  
  // Limit data points for performance
  const maxPoints = 100;
  const step = Math.max(1, Math.floor(yData.length / maxPoints));
  const sampledData = yData.filter((d, i) => i % step === 0);
  return Plot.plot({
    title: `Y Axis Position (${sampledData.length} of ${yData.length} points)`,
    width,
    height: 200,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    marks: [
      Plot.line(sampledData, {
        x: "ts", 
        y: "value", 
        stroke: "#ff7f0e",
        strokeWidth: 2
      }),
      Plot.ruleY([latestY], {stroke: "red", strokeDasharray: "3,3"}),
      Plot.text([sampledData[sampledData.length - 1]?.ts || new Date()], {
        x: [sampledData[sampledData.length - 1]?.ts || new Date()],
        y: [latestY],
        text: [`${latestY.toFixed(2)} mm`],
        fontSize: 12,
        fill: "red",
        dx: 10
      })
    ]
  });
}
```

```js
function zAxisPositionWidget(data, {width} = {}) {
  const zData = data.filter(d => d.item === "Zabs");
  const latestZ = positions?.Z ?? 0;
  if (!zData || zData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;"><h4>Z Axis Position</h4><div style="font-size: 2rem; font-weight: bold; color: #2ca02c;">${latestZ.toFixed(2)} mm</div><p>Current position from latest sample</p></div>`;
  }
  
  // Limit data points for performance
  const maxPoints = 100;
  const step = Math.max(1, Math.floor(zData.length / maxPoints));
  const sampledData = zData.filter((d, i) => i % step === 0);
  return Plot.plot({
    title: `Z Axis Position (${sampledData.length} of ${zData.length} points)`,
    width,
    height: 200,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    marks: [
      Plot.line(sampledData, {
        x: "ts", 
        y: "value", 
        stroke: "#2ca02c",
        strokeWidth: 2
      }),
      Plot.ruleY([latestZ], {stroke: "red", strokeDasharray: "3,3"}),
      Plot.text([sampledData[sampledData.length - 1]?.ts || new Date()], {
        x: [sampledData[sampledData.length - 1]?.ts || new Date()],
        y: [latestZ],
        text: [`${latestZ.toFixed(2)} mm`],
        fontSize: 12,
        fill: "red",
        dx: 10
      })
    ]
  });
}
```

```js
function axisLoadsGauge(data, {width} = {}) {
  if (!loads) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No load data available</div>`;
  }
  const gaugeData = [
    {name: "X Load", value: loads.X, color: "#1f77b4"},
    {name: "Y Load", value: loads.Y, color: "#ff7f0e"},
    {name: "Z Load", value: loads.Z, color: "#2ca02c"},
    {name: "Spindle Load", value: loads.Spindle, color: "#d62728"}
  ];
  return Plot.plot({
    title: "Axis & Spindle Loads",
    width,
    height: 300,
    x: {label: "Load (%)", domain: [0, 100]},
    y: {label: null},
    marks: [
      Plot.barX(gaugeData, {
        x: "value",
        y: "name",
        fill: "color",
        title: d => `${d.name}: ${d.value.toFixed(1)}%`
      }),
      Plot.ruleX([25, 50, 75, 100], {stroke: "gray", strokeDasharray: "2,2"}),
      Plot.text(gaugeData, {
        x: d => d.value + 5,
        y: "name",
        text: d => `${d.value.toFixed(1)}%`,
        fontSize: 12,
        fill: "black"
      })
    ]
  });
}
```

```js
function spindleChart(data, {width} = {}) {
  const spindleData = data.filter(d => d.item === "Srpm");
  if (!spindleData || spindleData.length === 0) {
    return html`<div style="text-align:center; color:#888; padding:2rem;">No spindle data available</div>`;
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
      }),
      Plot.area(spindleData, {
        x: "ts", 
        y: "value", 
        fill: "red",
        fillOpacity: 0.1
      })
    ]
  });
}
```

```js
function overrideChart(data, {width} = {}) {
  const overrideData = data.filter(d => ["Fovr", "Frapidovr"].includes(d.item));
  if (!overrideData || overrideData.length === 0) {
    return html`<div style="text-align:center; color:#888; padding:2rem;">No override data available</div>`;
  }
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
function rotaryAxisChart(data, {width} = {}) {
  const rotaryData = data.filter(d => /[BC]abs/.test(d.item));
  if (!rotaryData || rotaryData.length === 0) {
    return html`<div style="text-align:center; color:#888; padding:2rem;">No rotary axis data</div>`;
  }
  return Plot.plot({
    title: "Rotary Axis Positions (B & C)",
    width,
    height: 300,
    x: {type: "time", nice: true},
    y: {label: "Angle (degrees)"},
    color: {legend: true},
    marks: [
      Plot.line(rotaryData, {x: "ts", y: "value", stroke: "item", curve: "step"}),
      Plot.dot(rotaryData, {x: "ts", y: "value", fill: "item", r: 3})
    ]
  });
}
```

```js
function dataTypeComparisonChart(samplesData, eventsData, {width} = {}) {
  const sampleSamples = samples.filter(d => d.dataType === "sample");
  const eventSamples = events.filter(d => d.dataType === "event");
  const conditionSamples = conditions.filter(d => d.dataType === "condition");

  const comparisonData = [
    {source: "Sample Data", count: sampleSamples.length, color: "#10b981"},
    {source: "Event Data", count: eventSamples.length, color: "#f59e0b"},
    {source: "Condition Data", count: conditionSamples.length, color: "#3b82f6"}
  ];

  if (comparisonData.every(d => d.count === 0)) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No data source information available</div>`;
  }

  return Plot.plot({
    title: "Database Data Distribution",
    width,
    height: 300,
    x: {label: "Data Type"},
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
function stateTimelineChart(data, {width} = {}) {
  const stateData = data.filter(d => ["estop", "execution", "mode", "avail"].includes(d.item));
  if (!stateData || stateData.length === 0) {
    return html`<div style="text-align:center; color:#888; padding:2rem;">No state timeline data available</div>`;
  }
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

## Linear Axis Monitoring

```js
display(hasSampleData
  ? html`<div class="axis-grid">
      <div class="card">${resize((width) => xAxisPositionWidget(samples, {width}))}</div>
      <div class="card">${resize((width) => yAxisPositionWidget(samples, {width}))}</div>
      <div class="card">${resize((width) => zAxisPositionWidget(samples, {width}))}</div>
    </div>`
  : html`<div class="card" style="background: #f3f4f6; text-align: center; padding: 3rem;">
      <h3 style="color: #6b7280;">No Linear Axis Data Available</h3>
      <p style="color: #9ca3af;">Axis position data is not currently available for this machine.</p>
    </div>`)
```

## Machine Performance & Status

```js
display(hasSampleData
  ? html`<div class="grid grid-cols-2">
      <div class="card">${resize((width) => axisLoadsGauge(samples, {width}))}</div>
      <div class="card">${resize((width) => spindleChart(samples, {width}))}</div>
    </div>`
  : html`<div class="card" style="background: #f3f4f6; text-align: center; padding: 3rem;">
      <h3 style="color: #6b7280;">No Performance Data Available</h3>
      <p style="color: #9ca3af;">Machine performance metrics are not currently available.</p>
    </div>`)
```

## 5-Axis Capabilities & Data Analysis

```js
display(html`<div class="grid grid-cols-2">
  ${hasSampleData 
    ? html`<div class="card">${resize((width) => rotaryAxisChart(samples, {width}))}</div>` 
    : html`<div class="card" style="background: #f3f4f6; text-align: center; padding: 2rem;">
        <h4 style="color: #6b7280;">No Rotary Axis Data</h4>
        <p style="color: #9ca3af;">B & C axis data not available</p>
      </div>`}
  <div class="card">${resize((width) => dataTypeComparisonChart(samplesData, eventsData, {width}))}</div>
</div>`)
```

```js
display(html`<div class="grid grid-cols-2">
  ${hasEventData 
    ? html`<div class="card">${resize((width) => overrideChart(events, {width}))}</div>` 
    : html`<div class="card" style="background: #f3f4f6; text-align: center; padding: 2rem;">
        <h4 style="color: #6b7280;">No Override Data</h4>
        <p style="color: #9ca3af;">Feed & rapid override data not available</p>
      </div>`}
  ${hasSampleData 
    ? html`<div class="card">${resize((width) => axisPositionsChart(samples, {width}))}</div>` 
    : html`<div class="card" style="background: #f3f4f6; text-align: center; padding: 2rem;">
        <h4 style="color: #6b7280;">No Position Data</h4>
        <p style="color: #9ca3af;">Axis position trends not available</p>
      </div>`}
</div>`)
```

## Machine State & Timeline

```js
display(hasEventData
  ? html`<div class="card">${resize((width) => stateTimelineChart(events, {width}))}</div>`
  : html`<div class="card" style="background: #f3f4f6; text-align: center; padding: 3rem;">
      <h3 style="color: #6b7280;">No State Timeline Data Available</h3>
      <p style="color: #9ca3af;">Machine state and timeline information is not currently available.</p>
    </div>`)
```

## Detailed Status Information

```js
// Get latest tool and program info from events
const latestProgram = {
  program: latestEvents['program']?.value || 'N/A',
  Tool_number: latestEvents['Tool_number']?.value || 'N/A'
};

// Get axis state information (if available)
const axisStates = {};

display(html`<div class="performance-section">
  <div class="grid grid-cols-3">
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Linear Axes Position</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>X: <strong>${positions.X.toFixed(2)} mm</strong></div>
        <div>Y: <strong>${positions.Y.toFixed(2)} mm</strong></div>
        <div>Z: <strong>${positions.Z.toFixed(2)} mm</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Rotary Axes Position</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>B-Axis: <strong>${positions.B.toFixed(2)}°</strong></div>
        <div>C-Axis: <strong>${positions.C.toFixed(2)}°</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Current Operation</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>Program: <strong>${latestProgram.program || 'N/A'}</strong></div>
        <div>Tool: <strong>#${latestProgram.Tool_number || 'N/A'}</strong></div>
        <div>Spindle: <strong>${spindleRPM.toLocaleString()} RPM</strong></div>
      </div>
    </div>
  </div>
  
  <div class="grid grid-cols-3" style="margin-top: 1.5rem;">
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Axis Loads</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>X Load: <strong style="color: ${loads.X > 80 ? '#ef4444' : '#10b981'}">${loads.X.toFixed(1)}%</strong></div>
        <div>Y Load: <strong style="color: ${loads.Y > 80 ? '#ef4444' : '#10b981'}">${loads.Y.toFixed(1)}%</strong></div>
        <div>Z Load: <strong style="color: ${loads.Z > 80 ? '#ef4444' : '#10b981'}">${loads.Z.toFixed(1)}%</strong></div>
        <div>Spindle Load: <strong style="color: ${loads.Spindle > 80 ? '#ef4444' : '#10b981'}">${loads.Spindle.toFixed(1)}%</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Machine Mode</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>Mode: <strong>${machineStatus.mode}</strong></div>
        <div>Availability: <strong style="color: ${machineStatus.availability === 'AVAILABLE' ? '#10b981' : '#f59e0b'}">${machineStatus.availability}</strong></div>
        <div>E-Stop: <strong style="color: ${machineStatus.estop === 'ARMED' ? '#10b981' : '#ef4444'}">${machineStatus.estop}</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Database Data Summary</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>Sample Data: <strong>${samples.filter(d => d.dataType === "sample").length.toLocaleString()}</strong></div>
        <div>Event Data: <strong>${events.filter(d => d.dataType === "event").length.toLocaleString()}</strong></div>
        <div>Condition Data: <strong>${conditions.filter(d => d.dataType === "condition").length.toLocaleString()}</strong></div>
        <div>Total Records: <strong>${(samples.length + events.length + conditions.length).toLocaleString()}</strong></div>
      </div>
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

<p><strong>Data Sources:</strong> Live PostgreSQL database<br/>
<strong>Machine:</strong> Mazak 350MSY 5-axis CNC (${machineName})<br/>
<strong>Total Data Points:</strong> ${(samples.length + events.length + conditions.length).toLocaleString()}<br/>
<strong>5-Axis Capability:</strong> Linear (X,Y,Z) + Rotary (B,C) axes monitoring<br/>
<strong>Database Integration:</strong> Real-time data via API server with fallback to files</p>
</div>`)