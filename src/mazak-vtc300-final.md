---
title: Mazak VTC 300
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-components.css">

# Mazak VTC 300 - MTConnect Dashboard

This dashboard provides analysis of the Mazak VTC 300 machine with interactive time range filtering. Data includes July 2025 with comprehensive machine monitoring.

```js
// Load data from database using data loaders
const samplesData = FileAttachment("data/loaders/vtc300-samples.json").json();
const eventsData = FileAttachment("data/loaders/vtc300-events.json").json();
```

```js
// Process and sample the data for performance
const allSamples = samplesData
  .map(d => ({
    item: d.data_item_id,
    ts: new Date(d.timestamp),
    value: +d.value,
    component: d.component_id
  }))
  .filter(d => !isNaN(d.value) && isFinite(d.value))
  .sort((a, b) => a.ts - b.ts);

const allEvents = eventsData
  .map(d => ({
    item: d.data_item_id,
    ts: new Date(d.timestamp),
    value: d.value,
    component: d.component_id
  }))
  .filter(d => d.value && String(d.value).trim() !== '')
  .sort((a, b) => a.ts - b.ts);

// Debug: Show available data items
const availableSampleItems = [...new Set(allSamples.map(d => d.item))];
const availableEventItems = [...new Set(allEvents.map(d => d.item))];
console.log('Available sample items:', availableSampleItems);
console.log('Available event items:', availableEventItems);
```

```js
// Optimized sampling strategy
const performanceCutoff = 10000; // Maximum points for performance
const sampleRate = Math.max(1, Math.floor(allSamples.length / performanceCutoff));
const eventRate = Math.max(1, Math.floor(allEvents.length / (performanceCutoff / 2)));

const samples = allSamples.filter((d, i) => i % sampleRate === 0);
const events = allEvents.filter((d, i) => i % eventRate === 0);

// Get date range
const dateRange = {
  start: samples[0]?.ts || new Date(),
  end: samples[samples.length-1]?.ts || new Date()
};
```js
display(html`<div class="hero">
  <h2>Mazak VTC 300 - Complete Dataset (Including July 2025)</h2>
  <p>Data Coverage: ${dateRange.start.toLocaleDateString()} to ${dateRange.end.toLocaleDateString()}</p>
  <div style="margin-top: 1rem;">
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem; margin-right: 1rem;">
      📊 ${samples.length.toLocaleString()} Samples (${allSamples.length.toLocaleString()} total)
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      📋 ${events.length.toLocaleString()} Events (${allEvents.length.toLocaleString()} total)
    </span>
  </div>
  <div style="margin-top: 0.5rem; font-size: 0.9em; opacity: 0.8;">
    <span style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.15); border-radius: 0.25rem; margin-right: 0.5rem;">
      📊 Sample Rate: 1 in ${sampleRate}
    </span>
    <span style="padding: 0.25rem 0.5rem; background: rgba(255,255,255,0.15); border-radius: 0.25rem;">
      📋 Event Rate: 1 in ${eventRate}
    </span>
  </div>
</div>`)
```

## Time Range Filter

```js
// Time range filter controls with July-specific options
const quickFilter = Inputs.radio([
  "July 10-12, 2025",
  "July 13-15, 2025", 
  "July 16-18, 2025",
  "Mid July (10-20)",
  "All July 2025",
  "All Available Data",
  "Custom Range"
], {
  label: "Quick Time Filters",
  value: "All Available Data"
});

const startDate = Inputs.date({
  label: "Custom Start Date",
  value: dateRange.start,
  min: dateRange.start,
  max: dateRange.end
});

const endDate = Inputs.date({
  label: "Custom End Date", 
  value: dateRange.end,
  min: dateRange.start,
  max: dateRange.end
});
```

<div class="card">
  <h3>📅 Time Range Selection</h3>
  <div class="grid grid-cols-3" style="gap: 1rem; align-items: end;">
    <div>${quickFilter}</div>
    <div>${startDate}</div>
    <div>${endDate}</div>
  </div>
  <div style="margin-top: 1rem; padding: 0.75rem; background: #f8fafc; border-radius: 0.5rem;">
    <strong>Available Data Period:</strong> ${dateRange.start.toLocaleDateString()} to ${dateRange.end.toLocaleDateString()}
    <br/>
    <strong>Coverage:</strong> Complete dataset including July 2025 data (${allSamples.length.toLocaleString()} total samples)
    <br/>
    <strong>Performance:</strong> Smart sampling applied for browser performance (${samples.length.toLocaleString()} displayed)
  </div>
</div>

```js
// REACTIVE: Calculate filter range with better structure
const selectedFilter = Generators.input(quickFilter);
const selectedStart = Generators.input(startDate);
const selectedEnd = Generators.input(endDate);

const dateFilters = {
  "July 10-12, 2025": { start: new Date('2025-07-10'), end: new Date('2025-07-12T23:59:59') },
  "July 13-15, 2025": { start: new Date('2025-07-13'), end: new Date('2025-07-15T23:59:59') },
  "July 16-18, 2025": { start: new Date('2025-07-16'), end: new Date('2025-07-18T23:59:59') },
  "Mid July (10-20)": { start: new Date('2025-07-10'), end: new Date('2025-07-20T23:59:59') },
  "All July 2025": { start: new Date('2025-07-01'), end: new Date('2025-07-31T23:59:59') },
  "Custom Range": { start: selectedStart, end: selectedEnd },
  "All Available Data": { start: dateRange.start, end: dateRange.end }
};

const filterRange = dateFilters[selectedFilter] || dateFilters["All Available Data"];

// REACTIVE: Filter data based on calculated range
const filteredSamples = samples.filter(d => d.ts >= filterRange.start && d.ts <= filterRange.end);
const filteredEvents = events.filter(d => d.ts >= filterRange.start && d.ts <= filterRange.end);
```

<div class="card" style="background: #e8f5e8; border-left: 4px solid #10b981;">
  <h4 style="color: #059669; margin-top: 0;">📊 Active Filter: ${selectedFilter}</h4>
  <div class="grid grid-cols-4" style="gap: 1rem; font-family: monospace;">
    <div><strong>Period:</strong><br/>${filterRange.start.toLocaleDateString()} to ${filterRange.end.toLocaleDateString()}</div>
    <div><strong>Samples:</strong><br/>${filteredSamples.length.toLocaleString()} points</div>
    <div><strong>Events:</strong><br/>${filteredEvents.length.toLocaleString()} events</div>
    <div><strong>Duration:</strong><br/>${((filterRange.end - filterRange.start) / (1000 * 60 * 60 * 24)).toFixed(1)} days</div>
  </div>
</div>

## Current Status

```js
// Calculate latest values from filtered data (reactive)
const latestSamples = filteredSamples.reduce((acc, d) => {
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

const latestEvents = filteredEvents.reduce((acc, d) => {
  if (!acc[d.item] || d.ts > acc[d.item].ts) {
    acc[d.item] = d;
  }
  return acc;
}, {});

const autoTime = latestSamples.auto_time?.value || 0;
const cutTime = latestSamples.cut_time?.value || 0;
const efficiency = autoTime > 0 ? Math.min((cutTime / autoTime * 100), 100) : 0;

const machineStatus = {
  availability: latestEvents.avail?.value || 'Unknown',
  mode: latestEvents.mode?.value || 'Unknown',
  estop: latestEvents.estop?.value || 'Unknown'
};
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Machine Status</h2>
    <span class="big" style="color: ${machineStatus.availability === 'AVAILABLE' ? 'green' : 'orange'}">${machineStatus.availability}</span>
    <small>Latest in filtered range</small>
  </div>
  <div class="card">
    <h2>Efficiency</h2>
    <span class="big" style="color: ${efficiency > 70 ? 'green' : efficiency > 50 ? 'orange' : 'red'}">${efficiency.toFixed(1)}%</span>
    <small>Cut time efficiency</small>
  </div>
  <div class="card">
    <h2>Auto Time</h2>
    <span class="big">${(autoTime / 3600).toFixed(1)} hrs</span>
    <small>Automatic operation</small>
  </div>
  <div class="card">
    <h2>Cut Time</h2>
    <span class="big">${(cutTime / 3600).toFixed(1)} hrs</span>
    <small>Active cutting</small>
  </div>
</div>

<div class="grid grid-cols-4">
  <div class="card">
    <h2>X Position</h2>
    <span class="big">${(latestSamples.Xabs?.value || 0).toFixed(2)} mm</span>
    <small>Latest in range</small>
  </div>
  <div class="card">
    <h2>Y Position</h2>
    <span class="big">${(latestSamples.Yabs?.value || 0).toFixed(2)} mm</span>
    <small>Latest in range</small>
  </div>
  <div class="card">
    <h2>Z Position</h2>
    <span class="big">${(latestSamples.Zabs?.value || 0).toFixed(2)} mm</span>
    <small>Latest in range</small>
  </div>
  <div class="card">
    <h2>Spindle RPM</h2>
    <span class="big">${(latestSamples.Srpm?.value || 0).toFixed(0)}</span>
    <small>Latest in range</small>
  </div>
</div>

## Charts

```js
function positionChart(data, {width} = {}) {
  // Look for position data with flexible matching
  const posData = data.filter(d => {
    const item = d.item ? d.item.toLowerCase() : '';
    return item.includes('x') || item.includes('y') || item.includes('z') || 
           item.includes('position') || item.includes('abs');
  });
  if (posData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No position data in selected time range</div>`;
  }
  
  // Limit points for performance
  const maxPoints = 200;
  const step = Math.max(1, Math.floor(posData.length / maxPoints));
  const sampledData = posData.filter((d, i) => i % step === 0);
  
  return Plot.plot({
    title: `Axis Positions (${sampledData.length} of ${posData.length} points)`,
    width,
    height: 300,
    x: {type: "time", label: "Time"},
    y: {label: "Position (mm)"},
    color: {legend: true},
    marks: [
      Plot.line(sampledData, {x: "ts", y: "value", stroke: "item", tip: true}),
      Plot.dot(sampledData.filter((d, i) => i % Math.max(1, Math.floor(sampledData.length / 20)) === 0), 
               {x: "ts", y: "value", fill: "item", r: 2})
    ]
  });
}

function loadChart(data, {width} = {}) {
  // Look for load data with flexible matching
  const loadData = data.filter(d => {
    const item = d.item ? d.item.toLowerCase() : '';
    return item.includes('load') || item.includes('torque') || item.includes('force');
  });
  if (loadData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No load data in selected time range</div>`;
  }
  
  // Performance optimization
  const maxPoints = 200;
  const step = Math.max(1, Math.floor(loadData.length / maxPoints));
  const sampledData = loadData.filter((d, i) => i % step === 0);
  
  return Plot.plot({
    title: `Axis & Spindle Loads (${sampledData.length} of ${loadData.length} points)`,
    width,
    height: 300,
    x: {type: "time", label: "Time"},
    y: {label: "Load (%)", domain: [-100, 100]},
    color: {legend: true},
    marks: [
      Plot.line(sampledData, {x: "ts", y: "value", stroke: "item", tip: true}),
      Plot.ruleY([0], {stroke: "gray", strokeDasharray: "2,2"})
    ]
  });
}

function spindleChart(data, {width} = {}) {
  // Look for spindle data with flexible matching
  const spindleData = data.filter(d => {
    const item = d.item ? d.item.toLowerCase() : '';
    return item.includes('spindle') || item.includes('rpm') || item.includes('s') ||
           item.includes('speed') || item.includes('rotation');
  });
  if (spindleData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No spindle data in selected time range</div>`;
  }
  
  // Performance optimization
  const maxPoints = 200;
  const step = Math.max(1, Math.floor(spindleData.length / maxPoints));
  const sampledData = spindleData.filter((d, i) => i % step === 0);
  
  return Plot.plot({
    title: `Spindle RPM (${sampledData.length} of ${spindleData.length} points)`,
    width,
    height: 300,
    x: {type: "time", label: "Time"},
    y: {label: "RPM"},
    marks: [
      Plot.line(sampledData, {x: "ts", y: "value", stroke: "red", strokeWidth: 2, tip: true}),
      Plot.area(sampledData, {x: "ts", y: "value", fill: "red", fillOpacity: 0.1})
    ]
  });
}

function timelineChart(data, {width} = {}) {
  // Look for time-related data with flexible matching
  const timeData = data.filter(d => {
    const item = d.item ? d.item.toLowerCase() : '';
    return item.includes('time') || item.includes('cycle') || item.includes('duration') ||
           item.includes('auto') || item.includes('cut') || item.includes('runtime');
  });
  if (timeData.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No time data in selected time range</div>`;
  }
  
  // Performance optimization
  const maxPoints = 200;
  const step = Math.max(1, Math.floor(timeData.length / maxPoints));
  const sampledData = timeData.filter((d, i) => i % step === 0);
  
  return Plot.plot({
    title: `Machine Time Metrics (${sampledData.length} of ${timeData.length} points)`,
    width,
    height: 300,
    x: {type: "time", label: "Time"},
    y: {label: "Time (seconds)"},
    color: {legend: true},
    marks: [
      Plot.line(sampledData, {x: "ts", y: "value", stroke: "item", tip: true})
    ]
  });
}

// Fallback chart for any available data
function fallbackChart(data, {width} = {}) {
  if (data.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No data available</div>`;
  }
  
  // Performance optimization
  const maxPoints = 200;
  const step = Math.max(1, Math.floor(data.length / maxPoints));
  const sampledData = data.filter((d, i) => i % step === 0);
  
  return Plot.plot({
    title: `Available Data (${sampledData.length} of ${data.length} points)`,
    width,
    height: 300,
    x: {type: "time", label: "Time"},
    y: {label: "Value"},
    color: {legend: true},
    marks: [
      Plot.line(sampledData, {x: "ts", y: "value", stroke: "item", tip: true})
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => {
      const posData = filteredSamples.filter(d => {
        const item = d.item ? d.item.toLowerCase() : '';
        return item.includes('x') || item.includes('y') || item.includes('z') || 
               item.includes('position') || item.includes('abs');
      });
      return posData.length > 0 ? positionChart(filteredSamples, {width}) : fallbackChart(filteredSamples, {width});
    })}
  </div>
  <div class="card">
    ${resize((width) => {
      const loadData = filteredSamples.filter(d => {
        const item = d.item ? d.item.toLowerCase() : '';
        return item.includes('load') || item.includes('torque') || item.includes('force');
      });
      return loadData.length > 0 ? loadChart(filteredSamples, {width}) : fallbackChart(filteredSamples, {width});
    })}
  </div>
</div>

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => {
      const spindleData = filteredSamples.filter(d => {
        const item = d.item ? d.item.toLowerCase() : '';
        return item.includes('spindle') || item.includes('rpm') || item.includes('s') ||
               item.includes('speed') || item.includes('rotation');
      });
      return spindleData.length > 0 ? spindleChart(filteredSamples, {width}) : fallbackChart(filteredSamples, {width});
    })}
  </div>
  <div class="card">
    ${resize((width) => {
      const timeData = filteredSamples.filter(d => {
        const item = d.item ? d.item.toLowerCase() : '';
        return item.includes('time') || item.includes('cycle') || item.includes('duration') ||
               item.includes('auto') || item.includes('cut') || item.includes('runtime');
      });
      return timeData.length > 0 ? timelineChart(filteredSamples, {width}) : fallbackChart(filteredSamples, {width});
    })}
  </div>
</div>

---

*Dashboard updated: ${new Date().toLocaleString()}*

**Data Source:** Complete July 2025 dataset for Mazak VTC 300  
**Performance:** Smart sampling for optimal browser performance  
**Time Range:** Interactive filtering with July-specific options
