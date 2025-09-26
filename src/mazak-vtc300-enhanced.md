---
title: Mazak VTC 300 Enhanced
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-components.css">

# Mazak VTC 300 - Enhanced 5-Axis Dashboard

This dashboard provides comprehensive monitoring of the Mazak VTC 300 machine with advanced 5-axis capabilities, asset management, and real-time operational insights.

```js
// Load comprehensive VTC300 data
const samplesData = FileAttachment("data/optimized/mazak_2_vtc_300/samples.csv").csv({typed: true});
const eventsData = FileAttachment("data/optimized/mazak_2_vtc_300/events.csv").csv({typed: true});
const conditionsData = FileAttachment("data/optimized/mazak_2_vtc_300/conditions.csv").csv({typed: true});
const metadataData = FileAttachment("data/optimized/mazak_2_vtc_300/metadata.csv").csv({typed: true});
const recentSamples = FileAttachment("data/optimized/mazak_2_vtc_300/recent/samples_recent.csv").csv({typed: true});
const recentEvents = FileAttachment("data/optimized/mazak_2_vtc_300/recent/events_recent.csv").csv({typed: true});
```

```js
// Process comprehensive data with enhanced validation
const machineName = "mazak_2_vtc_300";

// Process all samples data
const allSamples = samplesData
  .map(d => ({
    component: d.component_id,
    item: d.sample_name,
    subtype: d.sub_type,
    ts: new Date(d.timestamp),
    value: d.value !== null && d.value !== undefined && !isNaN(d.value) ? +d.value : null,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .filter(d => d.value !== null && !isNaN(d.value) && isFinite(d.value))
  .sort((a, b) => a.ts - b.ts);

// Process all events data
const allEvents = eventsData
  .map(d => ({
    component: d.component_id,
    item: d.event_name,
    ts: new Date(d.timestamp),
    value: d.value != null && String(d.value).trim() !== '' ? (isNaN(+d.value) ? d.value : +d.value) : null,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .filter(d => d.value !== null && d.value !== undefined && d.value !== '')
  .sort((a, b) => a.ts - b.ts);

// Process recent data for real-time monitoring
const recentSamplesData = recentSamples
  .map(d => ({
    component: d.component_id,
    item: d.sample_name,
    subtype: d.sub_type,
    ts: new Date(d.timestamp),
    value: d.value !== null && d.value !== undefined && !isNaN(d.value) ? +d.value : null,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .filter(d => d.value !== null && !isNaN(d.value) && isFinite(d.value))
  .sort((a, b) => a.ts - b.ts);

const recentEventsData = recentEvents
  .map(d => ({
    component: d.component_id,
    item: d.event_name,
    ts: new Date(d.timestamp),
    value: d.value != null && String(d.value).trim() !== '' ? (isNaN(+d.value) ? d.value : +d.value) : null,
    machine: d.machine_name,
    dataType: d.data_type
  }))
  .filter(d => d.value !== null && d.value !== undefined && d.value !== '')
  .sort((a, b) => a.ts - b.ts);

// Process conditions data
const conditions = conditionsData
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

// Get data range information
const dateRange = {
  start: allSamples[0]?.ts || new Date(),
  end: allSamples[allSamples.length - 1]?.ts || new Date(),
  recentStart: recentSamplesData[0]?.ts || new Date(),
  recentEnd: recentSamplesData[recentSamplesData.length - 1]?.ts || new Date()
};

// Performance optimization - sample large datasets
const performanceCutoff = 15000;
const sampleRate = Math.max(1, Math.floor(allSamples.length / performanceCutoff));
const eventRate = Math.max(1, Math.floor(allEvents.length / performanceCutoff));

const samples = allSamples.filter((d, i) => i % sampleRate === 0);
const events = allEvents.filter((d, i) => i % eventRate === 0);

// Debug info
console.log("VTC300 Data Summary:");
console.log("All Samples:", allSamples.length.toLocaleString());
console.log("All Events:", allEvents.length.toLocaleString());
console.log("Recent Samples:", recentSamplesData.length.toLocaleString());
console.log("Recent Events:", recentEventsData.length.toLocaleString());
console.log("Sample Rate: 1 in", sampleRate);
console.log("Event Rate: 1 in", eventRate);
```

```js
// Calculate comprehensive KPIs
const latestSamples = samples.reduce((acc, d) => {
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

const latestEvents = events.reduce((acc, d) => {
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

// Get recent values for real-time status
const latestRecentSamples = recentSamplesData.reduce((acc, d) => {
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

const latestRecentEvents = recentEventsData.reduce((acc, d) => {
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

// Enhanced efficiency metrics
const autoTime = latestSamples.auto_time?.value || 0;
const cutTime = latestSamples.cut_time?.value || 0;
const totalAutoCutTime = latestSamples.total_auto_cut_time?.value || 0;
const totalTime = latestSamples.total_time?.value || 0;

const efficiency = autoTime > 0 ? Math.min((cutTime / autoTime * 100), 100) : 0;
const overallEfficiency = totalTime > 0 ? Math.min((totalAutoCutTime / totalTime * 100), 100) : 0;
const utilization = autoTime > 0 ? Math.min((autoTime / (autoTime + 3600) * 100), 100) : 0;

// Enhanced 5-axis position data
const positions = {
  X: latestSamples.Xabs?.value || 0,
  Y: latestSamples.Yabs?.value || 0,
  Z: latestSamples.Zabs?.value || 0,
  B: latestSamples.Babs?.value || 0,
  C: latestSamples.Cabs?.value || 0
};

// Enhanced axis loads and feeds
const axisData = {
  X: {
    position: positions.X,
    load: latestSamples.Xload?.value || 0,
    feedRate: latestSamples.Xfrt?.value || 0,
    pos: latestSamples.Xpos?.value || 0
  },
  Y: {
    position: positions.Y,
    load: latestSamples.Yload?.value || 0,
    feedRate: latestSamples.Yfrt?.value || 0,
    pos: latestSamples.Ypos?.value || 0
  },
  Z: {
    position: positions.Z,
    load: latestSamples.Zload?.value || 0,
    feedRate: latestSamples.Zfrt?.value || 0,
    pos: latestSamples.Zpos?.value || 0
  },
  B: {
    position: positions.B,
    load: latestSamples.Bload?.value || 0,
    feedRate: latestSamples.Bfrt?.value || 0,
    pos: latestSamples.Bpos?.value || 0,
    speed: latestSamples.Cspeed?.value || 0
  },
  C: {
    position: positions.C,
    load: latestSamples.Cload?.value || 0,
    feedRate: latestSamples.Cfrt?.value || 0,
    pos: latestSamples.Cpos?.value || 0
  }
};

// Spindle data
const spindleData = {
  rpm: latestSamples.Srpm?.value || 0,
  load: latestSamples.Sload?.value || 0,
  override: latestRecentEvents.Sovr?.value || 100,
  temperature: latestSamples.Stemp?.value || 0
};

// Enhanced machine status
const machineStatus = {
  availability: latestEvents.avail?.value || 'Unknown',
  mode: latestEvents.mode?.value || 'Unknown',
  estop: latestEvents.estop?.value || 'Unknown',
  execution: latestEvents.execution?.value || 'Unknown',
  program: latestEvents.program?.value || 'N/A',
  toolNumber: latestEvents.Tool_number?.value || 'N/A',
  toolGroup: latestEvents.Tool_group?.value || 'N/A',
  toolSuffix: latestEvents.Tool_suffix?.value || 'N/A',
  partCount: latestEvents.PartCountAct?.value || 0
};

// Enhanced overrides
const overrides = {
  feed: latestEvents.Fovr?.value || 100,
  rapid: latestEvents.Frapidovr?.value || 100,
  spindle: spindleData.override
};

// Asset management data
const assetManagement = {
  assetChanges: events.filter(d => d.item === 'd1_asset_chg').length,
  assetRemovals: events.filter(d => d.item === 'd1_asset_rem').length,
  palletNumber: latestEvents.pallet_num?.value || 'N/A',
  unitNumber: latestEvents.unitNum?.value || 'N/A'
};

// Enhanced axis states
const axisStates = {
  X: latestEvents.xaxisstate?.value || 'Unknown',
  Y: latestEvents.yaxisstate?.value || 'Unknown',
  Z: latestEvents.zaxisstate?.value || 'Unknown',
  B: latestEvents.baxisstate?.value || 'Unknown',
  C: latestEvents.caxisstate?.value || 'Unknown'
};

// Temperature monitoring
const temperatures = {
  servo1: latestSamples.servotemp1?.value || 0,
  servo2: latestSamples.servotemp2?.value || 0,
  servo3: latestSamples.servotemp3?.value || 0,
  coolant: latestSamples.cooltemp?.value || 0,
  spindle: spindleData.temperature
};

// Enhanced operational states
const operationalStates = {
  delay: latestEvents.emdelay?.value || 'Unknown',
  loaded: latestEvents.emloaded?.value || 'Unknown',
  operating: latestEvents.emoperating?.value || 'Unknown',
  powered: latestEvents.empowered?.value || 'Unknown',
  working: latestEvents.emworking?.value || 'Unknown'
};

// Data availability checks
const hasComprehensiveData = samples.length > 1000 && events.length > 1000;
const hasRecentData = recentSamplesData.length > 0 && recentEventsData.length > 0;
const has5AxisData = positions.B !== 0 || positions.C !== 0;
```

```js
display(html`<div class="hero">
  <h2 style="margin: 0; font-size: 2.5rem;">Mazak VTC 300 - Enhanced 5-Axis Control</h2>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Advanced 5-axis machining with comprehensive operational monitoring</p>
  <p style="margin: 0.5rem 0 0 0; opacity: 0.8; font-size: 0.9rem;">
    Comprehensive Dataset: ${dateRange.start.toLocaleDateString()} to ${dateRange.end.toLocaleDateString()}
    ${hasRecentData ? `| Recent Data: ${dateRange.recentStart.toLocaleDateString()} to ${dateRange.recentEnd.toLocaleDateString()}` : ''}
  </p>
  <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      📊 ${samples.length.toLocaleString()} Samples (${allSamples.length.toLocaleString()} total)
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      📋 ${events.length.toLocaleString()} Events (${allEvents.length.toLocaleString()} total)
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      ⚙️ ${conditions.length.toLocaleString()} Conditions
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      🕒 ${hasRecentData ? recentSamplesData.length.toLocaleString() + ' Recent' : 'No Recent'}
    </span>
  </div>
  <div style="margin-top: 0.5rem; font-size: 0.9em; opacity: 0.8;">
    <span style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.15); border-radius: 0.25rem; margin-right: 0.5rem;">
      📊 Sample Rate: 1 in ${sampleRate}
    </span>
    <span style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.15); border-radius: 0.25rem; margin-right: 0.5rem;">
      📋 Event Rate: 1 in ${eventRate}
    </span>
    <span style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.15); border-radius: 0.25rem;">
      🎯 5-Axis: ${has5AxisData ? 'Available' : 'Limited'}
    </span>
    <span style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.15); border-radius: 0.25rem;">
      🔄 Recent: ${hasRecentData ? 'Live' : 'Historical'}
    </span>
  </div>
</div>`)
```

## Machine Status Overview

```js
display(html`<div class="grid grid-cols-4">
  <div class="card">
    <h2>System Status</h2>
    <span class="big" style="color: ${machineStatus.availability === 'AVAILABLE' ? 'green' : 'orange'}">${machineStatus.availability}</span>
    <small>Availability | ${hasRecentData ? 'Live Data' : 'Historical'}</small>
  </div>
  <div class="card">
    <h2>Operational Mode</h2>
    <span class="big" style="color: ${machineStatus.mode === 'AUTOMATIC' ? 'green' : 'blue'}">${machineStatus.mode}</span>
    <small>Current Mode | ${machineStatus.execution}</small>
  </div>
  <div class="card">
    <h2>Overall Efficiency</h2>
    <span class="big" style="color: ${overallEfficiency > 70 ? 'green' : overallEfficiency > 50 ? 'orange' : 'red'}">${overallEfficiency.toFixed(1)}%</span>
    <small>Total vs Cut Time | Efficiency: ${efficiency.toFixed(1)}%</small>
  </div>
  <div class="card">
    <h2>Parts Produced</h2>
    <span class="big">${machineStatus.partCount.toLocaleString()}</span>
    <small>Active Program: ${machineStatus.program}</small>
  </div>
</div>`)
```

## Enhanced 5-Axis Position Monitoring

```js
display(html`<div class="grid grid-cols-5">
  <div class="card">
    <h2>X Position</h2>
    <span class="big">${positions.X.toFixed(3)} mm</span>
    <small>Load: ${axisData.X.load.toFixed(1)}% | Feed: ${axisData.X.feedRate.toFixed(0)}</small>
    <div style="margin-top: 0.5rem; padding: 0.25rem; background: ${axisStates.X === 'HOME' ? '#d1fae5' : '#fef3c7'}; border-radius: 0.25rem; font-size: 0.8rem;">
      State: ${axisStates.X}
    </div>
  </div>
  <div class="card">
    <h2>Y Position</h2>
    <span class="big">${positions.Y.toFixed(3)} mm</span>
    <small>Load: ${axisData.Y.load.toFixed(1)}% | Feed: ${axisData.Y.feedRate.toFixed(0)}</small>
    <div style="margin-top: 0.5rem; padding: 0.25rem; background: ${axisStates.Y === 'HOME' ? '#d1fae5' : '#fef3c7'}; border-radius: 0.25rem; font-size: 0.8rem;">
      State: ${axisStates.Y}
    </div>
  </div>
  <div class="card">
    <h2>Z Position</h2>
    <span class="big">${positions.Z.toFixed(3)} mm</span>
    <small>Load: ${axisData.Z.load.toFixed(1)}% | Feed: ${axisData.Z.feedRate.toFixed(0)}</small>
    <div style="margin-top: 0.5rem; padding: 0.25rem; background: ${axisStates.Z === 'HOME' ? '#d1fae5' : '#fef3c7'}; border-radius: 0.25rem; font-size: 0.8rem;">
      State: ${axisStates.Z}
    </div>
  </div>
  <div class="card">
    <h2>B-Axis</h2>
    <span class="big">${positions.B.toFixed(3)}°</span>
    <small>Load: ${axisData.B.load.toFixed(1)}% | Speed: ${axisData.B.speed.toFixed(0)}</small>
    <div style="margin-top: 0.5rem; padding: 0.25rem; background: ${axisStates.B === 'HOME' ? '#d1fae5' : '#fef3c7'}; border-radius: 0.25rem; font-size: 0.8rem;">
      State: ${axisStates.B}
    </div>
  </div>
  <div class="card">
    <h2>C-Axis</h2>
    <span class="big">${positions.C.toFixed(3)}°</span>
    <small>Load: ${axisData.C.load.toFixed(1)}% | Feed: ${axisData.C.feedRate.toFixed(0)}</small>
    <div style="margin-top: 0.5rem; padding: 0.25rem; background: ${axisStates.C === 'HOME' ? '#d1fae5' : '#fef3c7'}; border-radius: 0.25rem; font-size: 0.8rem;">
      State: ${axisStates.C}
    </div>
  </div>
</div>`)
```

## Enhanced Performance Metrics

```js
display(html`<div class="grid grid-cols-4">
  <div class="card">
    <h2>Spindle Performance</h2>
    <span class="big" style="color: ${spindleData.rpm > 0 ? 'green' : 'gray'}">${spindleData.rpm.toLocaleString()}</span>
    <small>RPM | Load: ${spindleData.load.toFixed(1)}% | Temp: ${spindleData.temperature.toFixed(1)}°C</small>
    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
      Override: ${spindleData.override}% | Efficiency: ${spindleData.rpm > 0 ? ((spindleData.load / 100) * 100).toFixed(1) : 0}%
    </div>
  </div>
  <div class="card">
    <h2>Feed Overrides</h2>
    <span class="big" style="color: ${overrides.feed > 100 ? 'orange' : 'green'}">${overrides.feed}%</span>
    <small>Feed | Rapid: ${overrides.rapid}% | Spindle: ${overrides.spindle}%</small>
    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
      Combined Efficiency: ${((overrides.feed / 100) * (overrides.spindle / 100) * 100).toFixed(1)}%
    </div>
  </div>
  <div class="card">
    <h2>Time Management</h2>
    <span class="big">${(autoTime / 3600).toFixed(1)}h</span>
    <small>Auto: ${(cutTime / 3600).toFixed(1)}h Cut | ${(totalTime / 3600).toFixed(1)}h Total</small>
    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
      Utilization: ${utilization.toFixed(1)}%
    </div>
  </div>
  <div class="card">
    <h2>Tool Management</h2>
    <span class="big">#${machineStatus.toolNumber}</span>
    <small>Group: ${machineStatus.toolGroup} | Suffix: ${machineStatus.toolSuffix}</small>
    <div style="margin-top: 0.5rem; font-size: 0.9rem;">
      Parts Completed: ${machineStatus.partCount}
    </div>
  </div>
</div>`)
```

## Temperature Monitoring

```js
display(html`<div class="grid grid-cols-5">
  <div class="card">
    <h2>Servo 1</h2>
    <span class="big" style="color: ${temperatures.servo1 > 60 ? 'red' : temperatures.servo1 > 50 ? 'orange' : 'green'}">${temperatures.servo1.toFixed(1)}°C</span>
    <small>X-Axis Drive Temperature</small>
  </div>
  <div class="card">
    <h2>Servo 2</h2>
    <span class="big" style="color: ${temperatures.servo2 > 60 ? 'red' : temperatures.servo2 > 50 ? 'orange' : 'green'}">${temperatures.servo2.toFixed(1)}°C</span>
    <small>Y-Axis Drive Temperature</small>
  </div>
  <div class="card">
    <h2>Servo 3</h2>
    <span class="big" style="color: ${temperatures.servo3 > 60 ? 'red' : temperatures.servo3 > 50 ? 'orange' : 'green'}">${temperatures.servo3.toFixed(1)}°C</span>
    <small>Z-Axis Drive Temperature</small>
  </div>
  <div class="card">
    <h2>Spindle</h2>
    <span class="big" style="color: ${temperatures.spindle > 60 ? 'red' : temperatures.spindle > 50 ? 'orange' : 'green'}">${temperatures.spindle.toFixed(1)}°C</span>
    <small>Spindle Temperature</small>
  </div>
  <div class="card">
    <h2>Coolant</h2>
    <span class="big" style="color: ${temperatures.coolant > 40 ? 'orange' : 'green'}">${temperatures.coolant.toFixed(1)}°C</span>
    <small>Coolant Temperature</small>
  </div>
</div>`)
```

## Advanced Chart Functions

```js
function enhanced5AxisChart(data, {width} = {}) {
  const axisData = data.filter(d => /[XYZBC]abs/.test(d.item));
  if (!axisData || axisData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No 5-axis position data available</div>`;
  }

  // Performance optimization
  const maxPoints = 300;
  const step = Math.max(1, Math.floor(axisData.length / maxPoints));
  const sampledData = axisData.filter((d, i) => i % step === 0);

  return Plot.plot({
    title: `5-Axis Position Monitoring (${sampledData.length} of ${axisData.length} points)`,
    width,
    height: 400,
    x: {type: "time", nice: true, label: "Time"},
    y: {label: "Position", domain: [-180, 180]},
    color: {legend: true},
    facet: {data: sampledData, x: "item"},
    marks: [
      Plot.line(sampledData, {
        x: "ts",
        y: "value",
        stroke: "item",
        strokeWidth: 2
      }),
      Plot.dot(sampledData.filter((d, i) => i % Math.max(1, Math.floor(sampledData.length / 50)) === 0), {
        x: "ts",
        y: "value",
        fill: "item",
        r: 3
      })
    ]
  });
}

function enhancedAxisLoadsChart(data, {width} = {}) {
  const loadData = data.filter(d => /[XYZBC]load/.test(d.item));
  if (!loadData || loadData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No axis load data available</div>`;
  }

  // Performance optimization
  const maxPoints = 300;
  const step = Math.max(1, Math.floor(loadData.length / maxPoints));
  const sampledData = loadData.filter((d, i) => i % step === 0);

  return Plot.plot({
    title: `Enhanced Axis Loads (${sampledData.length} of ${loadData.length} points)`,
    width,
    height: 350,
    x: {type: "time", nice: true, label: "Time"},
    y: {label: "Load (%)", domain: [-150, 150]},
    color: {legend: true},
    facet: {data: sampledData, x: "item"},
    marks: [
      Plot.line(sampledData, {
        x: "ts",
        y: "value",
        stroke: "item",
        strokeWidth: 2
      }),
      Plot.ruleY([0], {stroke: "gray", strokeDasharray: "3,3"}),
      Plot.ruleY([-100, 100], {stroke: "red", strokeDasharray: "1,1", strokeOpacity: 0.5})
    ]
  });
}

function enhancedFeedRatesChart(data, {width} = {}) {
  const feedData = data.filter(d => /[XYZBC]frt/.test(d.item));
  if (!feedData || feedData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No feed rate data available</div>`;
  }

  // Performance optimization
  const maxPoints = 300;
  const step = Math.max(1, Math.floor(feedData.length / maxPoints));
  const sampledData = feedData.filter((d, i) => i % step === 0);

  return Plot.plot({
    title: `Axis Feed Rates (${sampledData.length} of ${feedData.length} points)`,
    width,
    height: 300,
    x: {type: "time", nice: true, label: "Time"},
    y: {label: "Feed Rate (mm/min)"},
    color: {legend: true},
    marks: [
      Plot.line(sampledData, {
        x: "ts",
        y: "value",
        stroke: "item",
        strokeWidth: 2
      })
    ]
  });
}

function temperatureMonitoringChart(data, {width} = {}) {
  const tempData = data.filter(d => /temp/.test(d.item) || d.item === 'Stemp');
  if (!tempData || tempData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No temperature data available</div>`;
  }

  // Performance optimization
  const maxPoints = 200;
  const step = Math.max(1, Math.floor(tempData.length / maxPoints));
  const sampledData = tempData.filter((d, i) => i % step === 0);

  return Plot.plot({
    title: `Temperature Monitoring (${sampledData.length} of ${tempData.length} points)`,
    width,
    height: 300,
    x: {type: "time", nice: true, label: "Time"},
    y: {label: "Temperature (°C)"},
    color: {legend: true},
    marks: [
      Plot.line(sampledData, {
        x: "ts",
        y: "value",
        stroke: "item",
        strokeWidth: 2
      }),
      Plot.ruleY([50], {stroke: "orange", strokeDasharray: "2,2"}),
      Plot.ruleY([60], {stroke: "red", strokeDasharray: "2,2"})
    ]
  });
}

function assetManagementChart(events, {width} = {}) {
  const assetEvents = events.filter(d => ['d1_asset_chg', 'd1_asset_rem'].includes(d.item));
  if (!assetEvents || assetEvents.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No asset management data available</div>`;
  }

  return Plot.plot({
    title: "Asset Management Events",
    width,
    height: 250,
    x: {type: "time", nice: true, label: "Time"},
    y: {type: "band", domain: ["d1_asset_chg", "d1_asset_rem"]},
    color: {legend: true},
    marks: [
      Plot.dot(assetEvents, {
        x: "ts",
        y: "item",
        fill: "item",
        r: 4
      })
    ]
  });
}

function operationalStatesTimeline(events, {width} = {}) {
  const stateEvents = events.filter(d =>
    ['emdelay', 'emloaded', 'emoperating', 'empowered', 'emworking'].includes(d.item)
  );
  if (!stateEvents || stateEvents.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No operational state data available</div>`;
  }

  // Create timeline data
  const timelineData = stateEvents.map((d, i) => ({
    ...d,
    next: i < stateEvents.length - 1 ? stateEvents[i + 1].ts : new Date(d.ts.getTime() + 300000)
  }));

  return Plot.plot({
    title: "Operational States Timeline",
    width,
    height: 200,
    x: {type: "time"},
    y: {type: "band", domain: ["emdelay", "emloaded", "emoperating", "empowered", "emworking"]},
    color: {legend: true},
    marks: [
      Plot.rect(timelineData, {
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

## Enhanced 5-Axis Monitoring Charts

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => enhanced5AxisChart(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => enhancedAxisLoadsChart(samples, {width}))}
  </div>
</div>
```

## Performance Monitoring Charts

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => enhancedFeedRatesChart(samples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => temperatureMonitoringChart(samples, {width}))}
  </div>
</div>
```

## Asset & Operational Management

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => assetManagementChart(events, {width}))}
  </div>
  <div class="card">
    ${resize((width) => operationalStatesTimeline(events, {width}))}
  </div>
</div>
```

## Enhanced Data Summary

<div class="card" style="background: #f0f9ff; border-left: 4px solid #3b82f6;">
  <h3 style="color: #1e40af;">📊 Enhanced VTC300 Data Analysis</h3>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
    <div>
      <strong>🎯 5-Axis Capability:</strong><br/>
      Linear: X, Y, Z<br/>
      Rotary: B, C<br/>
      Status: ${has5AxisData ? '✅ Full' : '⚠️ Limited'}
    </div>
    <div>
      <strong>📈 Performance Metrics:</strong><br/>
      Efficiency: ${overallEfficiency.toFixed(1)}%<br/>
      Utilization: ${utilization.toFixed(1)}%<br/>
      Parts: ${machineStatus.partCount}
    </div>
    <div>
      <strong>🔧 Asset Management:</strong><br/>
      Changes: ${assetManagement.assetChanges}<br/>
      Removals: ${assetManagement.assetRemovals}<br/>
      Pallet: ${assetManagement.palletNumber}
    </div>
    <div>
      <strong>🌡️ Temperature Status:</strong><br/>
      Max Servo: ${Math.max(temperatures.servo1, temperatures.servo2, temperatures.servo3).toFixed(1)}°C<br/>
      Spindle: ${temperatures.spindle.toFixed(1)}°C<br/>
      Status: ${Math.max(...Object.values(temperatures)) > 50 ? '⚠️ Warm' : '✅ Normal'}
    </div>
  </div>
  <div style="margin-top: 1rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 0.5rem;">
    <strong>🚀 Enhanced Features:</strong> Advanced axis monitoring | Asset tracking | Temperature management | Operational states | 5-axis capabilities
  </div>
</div>
```

## Detailed Status Information

<div class="card">
  <h3>🔍 Detailed Machine Status</h3>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
    <div>
      <h4 style="color: #4b5563;">Axis States</h4>
      <div style="font-family: monospace; font-size: 0.9rem;">
        <div>X: <strong>${axisStates.X}</strong></div>
        <div>Y: <strong>${axisStates.Y}</strong></div>
        <div>Z: <strong>${axisStates.Z}</strong></div>
        <div>B: <strong>${axisStates.B}</strong></div>
        <div>C: <strong>${axisStates.C}</strong></div>
      </div>
    </div>
    <div>
      <h4 style="color: #4b5563;">Operational States</h4>
      <div style="font-family: monospace; font-size: 0.9rem;">
        <div>Delay: <strong>${operationalStates.delay}</strong></div>
        <div>Loaded: <strong>${operationalStates.loaded}</strong></div>
        <div>Operating: <strong>${operationalStates.operating}</strong></div>
        <div>Powered: <strong>${operationalStates.powered}</strong></div>
        <div>Working: <strong>${operationalStates.working}</strong></div>
      </div>
    </div>
    <div>
      <h4 style="color: #4b5563;">Control States</h4>
      <div style="font-family: monospace; font-size: 0.9rem;">
        <div>Single Block: <strong>${latestEvents.cmosingleblock?.value || 'Unknown'}</strong></div>
        <div>Dry Run: <strong>${latestEvents.cmodryrun?.value || 'Unknown'}</strong></div>
        <div>Edit Mode: <strong>${latestEvents.peditmode?.value || 'Unknown'}</strong></div>
        <div>Axis Lock: <strong>${latestEvents.cmomachineaxislock?.value || 'Unknown'}</strong></div>
        <div>Door State: <strong>${latestEvents.doorstate?.value || 'Unknown'}</strong></div>
      </div>
    </div>
    <div>
      <h4 style="color: #4b5563;">Program Information</h4>
      <div style="font-family: monospace; font-size: 0.9rem;">
        <div>Program: <strong>${machineStatus.program}</strong></div>
        <div>Line: <strong>${latestEvents.linenumber?.value || 'N/A'}</strong></div>
        <div>Sequence: <strong>${latestEvents.sequenceNum?.value || 'N/A'}</strong></div>
        <div>Subprogram: <strong>${latestEvents.subprogram?.value || 'N/A'}</strong></div>
        <div>Operator: <strong>${latestEvents.operator?.value || 'N/A'}</strong></div>
      </div>
    </div>
  </div>
</div>
```

---

<div style="margin-top: 2rem; text-align: center; color: #6b7280; font-size: 0.9rem;">
  <p><em>Enhanced VTC300 Dashboard updated: ${new Date().toLocaleString()}</em></p>
  <p><strong>Data Sources:</strong> Comprehensive VTC300 dataset (July-September 2025) | Recent data: ${hasRecentData ? 'Available' : 'Historical only'}<br/>
  <strong>Enhanced Features:</strong> 5-axis monitoring | Asset management | Temperature tracking | Operational states | Advanced metrics<br/>
  <strong>Total Data Points:</strong> ${(allSamples.length + allEvents.length + conditions.length).toLocaleString()} | Displayed: ${(samples.length + events.length).toLocaleString()}</p>
</div>