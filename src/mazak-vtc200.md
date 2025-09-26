---
title: Mazak VTC 200
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-components.css">

# Mazak VTC 200 - MTConnect Dashboard

This dashboard provides analysis of the Mazak VTC 200 machine with interactive time range filtering. Data includes July 2025 with comprehensive machine monitoring.

```js
// Load FULL dataset to include July 2025 data
const samplesData = FileAttachment("data/optimized/mazak_1_vtc_200/samples.csv").csv({typed: true});
const eventsData = FileAttachment("data/optimized/mazak_1_vtc_200/events.csv").csv({typed: true});
```

```js
// Process and sample the data for performance
const allSamples = samplesData
  .map(d => ({
    item: d.sample_name,
    ts: new Date(d.timestamp),
    value: +d.value,
    component: d.component_id
  }))
  .filter(d => !isNaN(d.value) && isFinite(d.value))
  .sort((a, b) => a.ts - b.ts);

const allEvents = eventsData
  .map(d => ({
    item: d.event_name,
    ts: new Date(d.timestamp),
    value: d.value,
    component: d.component_id
  }))
  .filter(d => d.value && String(d.value).trim() !== '')
  .sort((a, b) => a.ts - b.ts);

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
```

```js
display(html`<div class="hero">
  <h2>Mazak VTC 200 - Complete Dataset (Including July 2025)</h2>
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
  const posData = data.filter(d => ['Xabs', 'Yabs', 'Zabs'].includes(d.item));
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
  const loadData = data.filter(d => ['Xload', 'Yload', 'Zload', 'Sload'].includes(d.item));
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
  const spindleData = data.filter(d => d.item === 'Srpm');
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
  const timeData = data.filter(d => ['auto_time', 'cut_time'].includes(d.item));
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

function machineWorkingStagesTimeline(eventsData, samplesData, {width} = {}) {
  // Get key operational states from events
  const operationalEvents = eventsData.filter(d =>
    ['avail', 'mode', 'execution', 'estop'].includes(d.item)
  );

  // Get spindle activity as an indicator of working stages
  const spindleData = samplesData.filter(d => d.item === 'Srpm');
  const positionData = samplesData.filter(d => ['Xabs', 'Yabs', 'Zabs'].includes(d.item));

  // Create working stage classifications based on spindle activity and machine state
  const workingStages = [];

  // Process spindle data to determine active periods
  if (spindleData.length > 0) {
    const spindleThreshold = 100; // RPM threshold for "active"

    spindleData.forEach((d, i) => {
      const nextSpindle = spindleData[i + 1];
      const endTime = nextSpindle ? nextSpindle.ts : new Date(d.ts.getTime() + 300000); // 5 min default

      let stage = 'IDLE';
      if (d.value > spindleThreshold) {
        stage = 'CUTTING';
      } else if (d.value > 0 && d.value <= spindleThreshold) {
        stage = 'POSITIONING';
      }

      workingStages.push({
        ts: d.ts,
        endTime: endTime,
        stage: stage,
        rpm: d.value,
        type: 'spindle'
      });
    });
  }

  // Add operational state changes from events
  operationalEvents.forEach(d => {
    const nextEvent = operationalEvents.find(e => e.ts > d.ts && e.item === d.item);
    const endTime = nextEvent ? nextEvent.ts : new Date(d.ts.getTime() + 600000); // 10 min default

    let stage = 'UNKNOWN';

    if (d.item === 'avail') {
      stage = d.value === 'AVAILABLE' ? 'AVAILABLE' : 'UNAVAILABLE';
    } else if (d.item === 'mode') {
      stage = d.value === 'AUTOMATIC' ? 'AUTOMATIC' : 'MANUAL';
    } else if (d.item === 'execution') {
      stage = d.value === 'ACTIVE' ? 'ACTIVE' : 'STOPPED';
    } else if (d.item === 'estop') {
      stage = d.value === 'ARMED' ? 'E_STOP_ARMED' : 'E_STOP_TRIGGERED';
    }

    workingStages.push({
      ts: d.ts,
      endTime: endTime,
      stage: stage,
      value: d.value,
      type: 'event',
      event: d.item
    });
  });

  // Add movement-based stages
  if (positionData.length > 0) {
    const movementThreshold = 0.1; // mm threshold for significant movement

    for (let i = 0; i < positionData.length - 1; i++) {
      const current = positionData[i];
      const next = positionData[i + 1];

      const movement = Math.abs(next.value - current.value);

      if (movement > movementThreshold) {
        workingStages.push({
          ts: current.ts,
          endTime: next.ts,
          stage: 'MOVING',
          axis: current.item,
          movement: movement,
          type: 'movement'
        });
      }
    }
  }

  // Sort all stages by timestamp
  workingStages.sort((a, b) => a.ts - b.ts);

  // Create a simplified timeline with overlapping stages resolved
  const timelineStages = [];
  const stageColors = {
    'CUTTING': '#ef4444',      // Red - active cutting
    'POSITIONING': '#f59e0b',  // Amber - positioning
    'MOVING': '#3b82f6',       // Blue - moving
    'AVAILABLE': '#10b981',     // Green - available
    'AUTOMATIC': '#8b5cf6',     // Purple - automatic mode
    'ACTIVE': '#06b6d4',       // Cyan - active execution
    'IDLE': '#6b7280',         // Gray - idle
    'UNAVAILABLE': '#ef4444',  // Red - unavailable
    'MANUAL': '#f97316',       // Orange - manual mode
    'STOPPED': '#dc2626',      // Dark red - stopped
    'E_STOP_ARMED': '#22c55e', // Green - e-stop armed
    'E_STOP_TRIGGERED': '#991b1b', // Dark red - e-stop triggered
    'UNKNOWN': '#9ca3af'       // Light gray - unknown
  };

  // Group stages by time periods (every 30 minutes for visualization)
  const timeInterval = 30 * 60 * 1000; // 30 minutes in milliseconds
  const currentTime = new Date(Math.min(...workingStages.map(s => s.ts.getTime())));
  const endTime = new Date(Math.max(...workingStages.map(s => s.endTime.getTime())));

  while (currentTime <= endTime) {
    const intervalStart = new Date(currentTime);
    const intervalEnd = new Date(currentTime.getTime() + timeInterval);

    // Find stages active during this interval
    const activeStages = workingStages.filter(s =>
      s.ts <= intervalEnd && s.endTime >= intervalStart
    );

    if (activeStages.length > 0) {
      // Determine dominant stage for this interval
      const priorityStages = ['CUTTING', 'MOVING', 'POSITIONING', 'ACTIVE', 'AUTOMATIC', 'AVAILABLE', 'IDLE'];
      let dominantStage = 'UNKNOWN';

      for (const priority of priorityStages) {
        if (activeStages.some(s => s.stage === priority)) {
          dominantStage = priority;
          break;
        }
      }

      timelineStages.push({
        start: intervalStart,
        end: intervalEnd,
        stage: dominantStage,
        stages: activeStages.map(s => s.stage),
        color: stageColors[dominantStage] || stageColors['UNKNOWN'],
        details: activeStages
      });
    }

    currentTime.setTime(currentTime.getTime() + timeInterval);
  }

  if (timelineStages.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No machine working stages data available in selected time range</div>`;
  }

  return Plot.plot({
    title: `Machine Working Stages Timeline (${timelineStages.length} intervals)`,
    width,
    height: 400,
    x: {type: "time", label: "Time", nice: true},
    y: {type: "band", domain: [...new Set(timelineStages.map(s => s.stage))].sort()},
    color: {legend: true},
    marks: [
      Plot.rect(timelineStages, {
        x1: "start",
        x2: "end",
        y: "stage",
        fill: "color",
        inset: 1,
        title: d => `${d.stage}\n${d.start.toLocaleDateString()} ${d.start.toLocaleTimeString()}\nActive stages: ${d.stages.join(', ')}`
      }),
      // Add stage transition markers
      Plot.dot(
        timelineStages.filter((d, i) => i === 0 || d.stage !== timelineStages[i - 1].stage),
        {
          x: "start",
          y: "stage",
          fill: "black",
          r: 3,
          stroke: "white",
          strokeWidth: 1
        }
      )
    ]
  });
}

function machineActivityGanttChart(eventsData, samplesData, {width} = {}) {
  // Create a comprehensive Gantt chart showing different machine activities
  const activities = [];

  // Spindle activity
  const spindleData = samplesData.filter(d => d.item === 'Srpm');
  const spindleActiveThreshold = 100;

  spindleData.forEach((d, i) => {
    const next = spindleData[i + 1];
    const endTime = next ? next.ts : new Date(d.ts.getTime() + 300000);

    if (d.value > spindleActiveThreshold) {
      activities.push({
        start: d.ts,
        end: endTime,
        activity: 'Spindle Active',
        category: 'Spindle',
        value: d.value,
        color: '#ef4444'
      });
    }
  });

  // Axis movement activity
  const axes = ['Xabs', 'Yabs', 'Zabs'];
  axes.forEach(axis => {
    const axisData = samplesData.filter(d => d.item === axis);

    for (let i = 0; i < axisData.length - 1; i++) {
      const current = axisData[i];
      const next = axisData[i + 1];
      const movement = Math.abs(next.value - current.value);

      if (movement > 0.1) { // Significant movement
        activities.push({
          start: current.ts,
          end: next.ts,
          activity: `${axis} Movement`,
          category: 'Axis Movement',
          value: movement.toFixed(2),
          color: axis === 'Xabs' ? '#3b82f6' : axis === 'Yabs' ? '#10b981' : '#f59e0b'
        });
      }
    }
  });

  // Machine state changes
  const stateEvents = eventsData.filter(d => ['avail', 'mode', 'execution'].includes(d.item));

  stateEvents.forEach((d, i) => {
    const next = stateEvents.find(e => e.ts > d.ts && e.item === d.item);
    const endTime = next ? next.ts : new Date(d.ts.getTime() + 600000);

    let activity = '';
    let color = '#6b7280';

    if (d.item === 'avail') {
      activity = `Availability: ${d.value}`;
      color = d.value === 'AVAILABLE' ? '#10b981' : '#ef4444';
    } else if (d.item === 'mode') {
      activity = `Mode: ${d.value}`;
      color = d.value === 'AUTOMATIC' ? '#8b5cf6' : '#f97316';
    } else if (d.item === 'execution') {
      activity = `Execution: ${d.value}`;
      color = d.value === 'ACTIVE' ? '#06b6d4' : '#dc2626';
    }

    activities.push({
      start: d.ts,
      end: endTime,
      activity: activity,
      category: 'Machine State',
      value: d.value,
      color: color
    });
  });

  // Sort activities by start time
  activities.sort((a, b) => a.start - b.start);

  if (activities.length === 0) {
    return html`<div style="text-align: center; padding: 2rem; color: #6b7280;">No machine activity data available in selected time range</div>`;
  }

  // Group by category for better visualization
  const categories = [...new Set(activities.map(a => a.category))];

  return Plot.plot({
    title: `Machine Activity Gantt Chart (${activities.length} activities)`,
    width,
    height: Math.max(300, categories.length * 40),
    x: {type: "time", label: "Time", nice: true},
    y: {type: "band", domain: categories},
    color: {legend: true},
    marks: [
      Plot.rect(activities, {
        x1: "start",
        x2: "end",
        y: "category",
        fill: "color",
        inset: 0.5,
        title: d => `${d.activity}\n${d.start.toLocaleDateString()} ${d.start.toLocaleTimeString()}\n${d.end.toLocaleDateString()} ${d.end.toLocaleTimeString()}${d.value !== undefined ? '\nValue: ' + d.value : ''}`
      })
    ]
  });
}
```

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => positionChart(filteredSamples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => loadChart(filteredSamples, {width}))}
  </div>
</div>

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => spindleChart(filteredSamples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => timelineChart(filteredSamples, {width}))}
  </div>
</div>

## Machine Working Stages Timeline

<div class="grid grid-cols-2">
  <div class="card">
    ${resize((width) => machineWorkingStagesTimeline(filteredEvents, filteredSamples, {width}))}
  </div>
  <div class="card">
    ${resize((width) => machineActivityGanttChart(filteredEvents, filteredSamples, {width}))}
  </div>
</div>

## Working Stages Analysis

<div class="card" style="background: #f0f9ff; border-left: 4px solid #3b82f6;">
  <h3 style="color: #1e40af;">🕐 Machine Working Stages Analysis</h3>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
    <div>
      <strong>🔴 Cutting:</strong><br/>
      Spindle RPM > 100<br/>
      Active material removal
    </div>
    <div>
      <strong>🟡 Positioning:</strong><br/>
      Spindle RPM ≤ 100<br/>
      Tool positioning
    </div>
    <div>
      <strong>🔵 Moving:</strong><br/>
      Axis movement > 0.1mm<br/>
      Rapid traverse
    </div>
    <div>
      <strong>⚪ Idle:</strong><br/>
      No significant activity<br/>
      Machine standby
    </div>
    <div>
      <strong>🟢 Available:</strong><br/>
      Machine ready<br/>
      Normal operation
    </div>
    <div>
      <strong>🟣 Automatic:</strong><br/>
      Auto mode active<br/>
      Program execution
    </div>
  </div>
  <div style="margin-top: 1rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 0.5rem;">
    <strong>📊 Timeline Features:</strong> Color-coded working stages | Real-time activity tracking | Gantt chart visualization | Machine state transitions
  </div>
</div>

---

*Dashboard updated: ${new Date().toLocaleString()}*

**Data Source:** Complete July 2025 dataset for Mazak VTC 200  
**Performance:** Smart sampling for optimal browser performance  
**Time Range:** Interactive filtering with July-specific options
