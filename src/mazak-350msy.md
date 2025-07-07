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

<div class="hero">
  <h2 style="margin: 0; font-size: 2rem;">MTConnect Real-Time Monitoring</h2>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Advanced 5-axis CNC machining center with rotary table capabilities</p>
  <div class="machine-status">
    <div class="status-indicator status-running"></div>
    <span>System Online</span>
  </div>
</div>

<!-- Load and normalize the MTConnect data -->

```js
const rawData = FileAttachment("data/350msy.json").json();
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
        // Use number if possible, otherwise string
        const num = Number(event.value);
        events.push({
          component: componentId,
          item: itemId,
          ts: new Date(event.timestamp),
          value: (!isNaN(num) && isFinite(num)) ? num : String(event.value)
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

## Key Performance Indicators

<div class="grid grid-cols-4">
  <div class="metric-card">
    <div class="metric-value">${(latestSamples.auto_time / 3600).toFixed(1)}</div>
    <div class="metric-label">Auto Time (hrs)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">${(latestSamples.cut_time / 3600).toFixed(1)}</div>
    <div class="metric-label">Cut Time (hrs)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">${(latestSamples.total_time / 3600).toFixed(1)}</div>
    <div class="metric-label">Total Time (hrs)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value" style="color: ${latestEvents.avail === 'AVAILABLE' ? '#10b981' : '#f59e0b'}">${latestEvents.avail || 'Unknown'}</div>
    <div class="metric-label">Machine Status</div>
  </div>
</div>

```js
// Calculate efficiency metrics
const efficiency = latestSamples.total_time > 0 ? (latestSamples.cut_time / latestSamples.total_time * 100) : 0;
const utilization = latestSamples.total_time > 0 ? (latestSamples.auto_time / latestSamples.total_time * 100) : 0;
```

<div class="performance-section">
  <h3 style="margin-top: 0;">Performance Metrics</h3>
  <div class="grid grid-cols-3">
    <div class="metric-card">
      <div class="metric-value" style="color: ${efficiency > 70 ? '#10b981' : efficiency > 50 ? '#f59e0b' : '#ef4444'}">${efficiency.toFixed(1)}%</div>
      <div class="metric-label">Cutting Efficiency</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color: ${utilization > 80 ? '#10b981' : utilization > 60 ? '#f59e0b' : '#ef4444'}">${utilization.toFixed(1)}%</div>
      <div class="metric-label">Machine Utilization</div>
    </div>
    <div class="metric-card">
      <div class="metric-value" style="color: ${latestEvents.estop === 'ARMED' ? '#10b981' : '#ef4444'}">${latestEvents.estop || 'Unknown'}</div>
      <div class="metric-label">Emergency Stop</div>
    </div>
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
function xAxisPositionWidget(data, {width} = {}) {
  const xData = data.filter(d => d.item === "Xabs");
  const latestX = xData.length > 0 ? xData[xData.length - 1].value : 0;
  
  return Plot.plot({
    title: "X Axis Position",
    width,
    height: 200,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    marks: [
      Plot.line(xData, {
        x: "ts", 
        y: "value", 
        stroke: "#1f77b4",
        strokeWidth: 2
      }),
      Plot.ruleY([latestX], {stroke: "red", strokeDasharray: "3,3"}),
      Plot.text([xData[xData.length - 1]?.ts || new Date()], {
        x: [xData[xData.length - 1]?.ts || new Date()],
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
  const latestY = yData.length > 0 ? yData[yData.length - 1].value : 0;
  
  return Plot.plot({
    title: "Y Axis Position",
    width,
    height: 200,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    marks: [
      Plot.line(yData, {
        x: "ts", 
        y: "value", 
        stroke: "#ff7f0e",
        strokeWidth: 2
      }),
      Plot.ruleY([latestY], {stroke: "red", strokeDasharray: "3,3"}),
      Plot.text([yData[yData.length - 1]?.ts || new Date()], {
        x: [yData[yData.length - 1]?.ts || new Date()],
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
  const latestZ = zData.length > 0 ? zData[zData.length - 1].value : 0;
  
  return Plot.plot({
    title: "Z Axis Position",
    width,
    height: 200,
    x: {type: "time", nice: true, label: null},
    y: {label: "Position (mm)"},
    marks: [
      Plot.line(zData, {
        x: "ts", 
        y: "value", 
        stroke: "#2ca02c",
        strokeWidth: 2
      }),
      Plot.ruleY([latestZ], {stroke: "red", strokeDasharray: "3,3"}),
      Plot.text([zData[zData.length - 1]?.ts || new Date()], {
        x: [zData[zData.length - 1]?.ts || new Date()],
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
  // Get latest load values
  const latestLoads = data.filter(d => /(X|Y|Z)load|Sload/.test(d.item))
    .reduce((acc, d) => {
      acc[d.item] = d.value;
      return acc;
    }, {});
  
  const gaugeData = [
    {name: "X Load", value: latestLoads.Xload || 0, color: "#1f77b4"},
    {name: "Y Load", value: latestLoads.Yload || 0, color: "#ff7f0e"},
    {name: "Z Load", value: latestLoads.Zload || 0, color: "#2ca02c"},
    {name: "Spindle Load", value: latestLoads.Sload || 0, color: "#d62728"}
  ];
  
  return Plot.plot({
    title: "Axis & Spindle Loads",
    width,
    height: 300,
    y: {label: "Load (%)", domain: [0, 100]},
    color: {legend: true},
    marks: [
      Plot.barX(gaugeData, {
        x: "value",
        y: "name",
        fill: "color",
        title: d => `${d.name}: ${d.value.toFixed(1)}%`
      }),
      Plot.ruleX([0, 25, 50, 75, 100], {stroke: "gray", strokeDasharray: "2,2"}),
      Plot.text([25, 50, 75, 100], {
        x: [25, 50, 75, 100],
        y: "Spindle Load",
        text: ["25%", "50%", "75%", "100%"],
        fontSize: 10,
        fill: "gray"
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
function rotaryAxisChart(data, {width} = {}) {
  const rotaryData = data.filter(d => /[BC]abs/.test(d.item));
  
  return Plot.plot({
    title: "Rotary Axis Positions (B & C)",
    width,
    height: 300,
    x: {type: "time", nice: true},
    y: {label: "Angle (degrees)"},
    color: {legend: true},
    marks: [
      Plot.line(rotaryData, {
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

## Linear Axis Monitoring

<div class="axis-grid">
  <div class="card">
    ${resize((width) => xAxisPositionWidget(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => yAxisPositionWidget(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => zAxisPositionWidget(samples, {width}))}
  </div>
</div>

## Machine Performance & Status

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => axisLoadsGauge(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => spindleChart(samples, {width}))}
  </div>
</div>

## 5-Axis Capabilities

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => rotaryAxisChart(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => overrideChart(events, {width}))}
  </div>
</div>

## Machine State & Timeline

<div class="card">
  ${resize((width) => stateTimelineChart(events, {width}))}
</div>

## Detailed Status Information

```js
// Get latest position data
const latestPositions = samples.filter(d => /[XYZBC]abs/.test(d.item))
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

// Get current spindle data
const currentSpindle = samples.filter(d => d.item === "Srpm").slice(-1)[0]?.value || 0;
```

<div class="performance-section">
  <div class="grid grid-cols-3">
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Linear Axes Position</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>X: <strong>${latestPositions.Xabs?.toFixed(2) || 'N/A'} mm</strong></div>
        <div>Y: <strong>${latestPositions.Yabs?.toFixed(2) || 'N/A'} mm</strong></div>
        <div>Z: <strong>${latestPositions.Zabs?.toFixed(2) || 'N/A'} mm</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Rotary Axes Position</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>B-Axis: <strong>${latestPositions.Babs?.toFixed(2) || 'N/A'}°</strong></div>
        <div>C-Axis: <strong>${latestPositions.Cabs?.toFixed(2) || 'N/A'}°</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Current Operation</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>Program: <strong>${latestProgram.program || 'N/A'}</strong></div>
        <div>Tool: <strong>#${latestProgram.Tool_number || 'N/A'}</strong></div>
        <div>Spindle: <strong>${currentSpindle.toLocaleString()} RPM</strong></div>
      </div>
    </div>
  </div>
  
  <div class="grid grid-cols-2" style="margin-top: 1.5rem;">
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Axis Loads</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>X Load: <strong style="color: ${(latestLoads.Xload || 0) > 80 ? '#ef4444' : '#10b981'}">${latestLoads.Xload?.toFixed(1) || 'N/A'}%</strong></div>
        <div>Y Load: <strong style="color: ${(latestLoads.Yload || 0) > 80 ? '#ef4444' : '#10b981'}">${latestLoads.Yload?.toFixed(1) || 'N/A'}%</strong></div>
        <div>Z Load: <strong style="color: ${(latestLoads.Zload || 0) > 80 ? '#ef4444' : '#10b981'}">${latestLoads.Zload?.toFixed(1) || 'N/A'}%</strong></div>
        <div>Spindle Load: <strong style="color: ${(latestLoads.Sload || 0) > 80 ? '#ef4444' : '#10b981'}">${latestLoads.Sload?.toFixed(1) || 'N/A'}%</strong></div>
      </div>
    </div>
    <div class="metric-card">
      <h4 style="margin-top: 0; color: #4b5563;">Machine Mode</h4>
      <div style="display: grid; gap: 0.5rem; font-family: monospace;">
        <div>Mode: <strong>${latestEvents.mode || 'Unknown'}</strong></div>
        <div>Availability: <strong style="color: ${latestEvents.avail === 'AVAILABLE' ? '#10b981' : '#f59e0b'}">${latestEvents.avail || 'Unknown'}</strong></div>
        <div>E-Stop: <strong style="color: ${latestEvents.estop === 'ARMED' ? '#10b981' : '#ef4444'}">${latestEvents.estop || 'Unknown'}</strong></div>
      </div>
    </div>
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

Data: MTConnect stream from Mazak 350MSY 5-axis CNC machine