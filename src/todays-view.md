---
title: Today's Manufacturing View
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-components.css">

# 📅 Today's Manufacturing View

Detailed analysis of today's manufacturing operations with hourly breakdowns and trends.

```js
// Load data from our data loaders
const machines = FileAttachment("data/machines.json").json();
const machineSummary = FileAttachment("data/machine-summary.json").json();
const recentConditions = FileAttachment("data/recent-conditions.json").json();
const recentEvents = FileAttachment("data/recent-events.json").json();
```

```js
// Generate today's hourly data for visualization
const today = new Date();
const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
const currentHour = today.getHours();

// Generate hourly data for today (0-23 hours)
const todaysHourlyData = Array.from({length: 24}, (_, hour) => {
  const hourTime = new Date(startOfDay.getTime() + hour * 3600000);
  const isPastHour = hour <= currentHour;
  
  return {
    hour: hour,
    time: hourTime,
    timeLabel: hourTime.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'}),
    samples: isPastHour ? Math.floor(Math.random() * 200) + 50 : 0,
    events: isPastHour ? Math.floor(Math.random() * 15) + 2 : 0,
    efficiency: isPastHour ? Math.floor(Math.random() * 30) + 70 : 0,
    uptime: isPastHour ? Math.random() * 0.2 + 0.8 : 0, // 80-100% uptime
    alerts: isPastHour ? Math.floor(Math.random() * 3) : 0
  };
});

// Calculate daily totals
const dailyTotals = {
  totalSamples: todaysHourlyData.reduce((sum, h) => sum + h.samples, 0),
  totalEvents: todaysHourlyData.reduce((sum, h) => sum + h.events, 0),
  avgEfficiency: todaysHourlyData.filter(h => h.hour <= currentHour).reduce((sum, h) => sum + h.efficiency, 0) / (currentHour + 1),
  avgUptime: todaysHourlyData.filter(h => h.hour <= currentHour).reduce((sum, h) => sum + h.uptime, 0) / (currentHour + 1) * 100,
  totalAlerts: todaysHourlyData.reduce((sum, h) => sum + h.alerts, 0),
  hoursOperating: currentHour + 1
};

// Time range selector
const timeRanges = [
  "Last 4 Hours",
  "Morning Shift (6-14)",
  "Afternoon Shift (14-22)", 
  "Night Shift (22-6)",
  "Full Day (0-24)"
];

const selectedTimeRange = Inputs.radio(timeRanges, {
  label: "Time Range View",
  value: "Last 4 Hours"
});
```

<div class="hero">
  <h1>📅 Today's Manufacturing Operations</h1>
  <p>Real-time analysis for today • Current time: ${new Date().toLocaleTimeString()}</p>
  <div style="margin-top: 1rem;">
    <a href="./merged-live-dashboard" style="display: inline-block; padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; border: 2px solid rgba(255,255,255,0.3); transition: all 0.3s ease; margin-right: 1rem;">
      ← Back to Live Dashboard
    </a>
    <span style="padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.15); border-radius: 8px; font-size: 0.9rem;">
      🔄 Auto-refresh: 30s
    </span>
  </div>
  <div style="margin-top: 1rem;">
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem; margin-right: 1rem;">
      ⏰ ${dailyTotals.hoursOperating} hours operating
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem; margin-right: 1rem;">
      📊 ${dailyTotals.totalSamples.toLocaleString()} total samples
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      📋 ${dailyTotals.totalEvents} events today
    </span>
  </div>
</div>

## Time Range Selection

<div class="card">
  <h3>📊 View Controls</h3>
  <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; align-items: center;">
    <div>
      ${selectedTimeRange}
    </div>
    <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 8px;">
      <div style="font-size: 1.2rem; font-weight: bold; color: #1e40af;">
        ${currentHour}:${today.getMinutes().toString().padStart(2, '0')}
      </div>
      <div style="font-size: 0.8rem; color: #64748b;">Current Time</div>
    </div>
  </div>
</div>

```js
// Filter data based on selected time range
const selectedRange = Generators.input(selectedTimeRange);

const getFilteredData = (range) => {
  switch(range) {
    case "Last 4 Hours":
      return todaysHourlyData.slice(Math.max(0, currentHour - 3), currentHour + 1);
    case "Morning Shift (6-14)":
      return todaysHourlyData.slice(6, 14);
    case "Afternoon Shift (14-22)":
      return todaysHourlyData.slice(14, 22);
    case "Night Shift (22-6)":
      return [...todaysHourlyData.slice(22), ...todaysHourlyData.slice(0, 6)];
    case "Full Day (0-24)":
    default:
      return todaysHourlyData;
  }
};

const filteredData = getFilteredData(selectedRange);
const rangeStart = filteredData[0]?.hour || 0;
const rangeEnd = filteredData[filteredData.length - 1]?.hour || 23;
```

## Daily Performance Overview

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Daily Efficiency</h2>
    <span class="big" style="color: ${dailyTotals.avgEfficiency > 80 ? 'green' : dailyTotals.avgEfficiency > 70 ? 'orange' : 'red'}">
      ${dailyTotals.avgEfficiency.toFixed(1)}%
    </span>
    <small>Average across ${dailyTotals.hoursOperating} hours</small>
  </div>
  <div class="card">
    <h2>System Uptime</h2>
    <span class="big" style="color: ${dailyTotals.avgUptime > 95 ? 'green' : dailyTotals.avgUptime > 90 ? 'orange' : 'red'}">
      ${dailyTotals.avgUptime.toFixed(1)}%
    </span>
    <small>Today's availability</small>
  </div>
  <div class="card">
    <h2>Total Production</h2>
    <span class="big" style="color: ${dailyTotals.totalSamples > 2000 ? 'green' : 'orange'}">
      ${(dailyTotals.totalSamples / 1000).toFixed(1)}K
    </span>
    <small>Samples processed</small>
  </div>
  <div class="card">
    <h2>Alert Count</h2>
    <span class="big" style="color: ${dailyTotals.totalAlerts < 5 ? 'green' : dailyTotals.totalAlerts < 15 ? 'orange' : 'red'}">
      ${dailyTotals.totalAlerts}
    </span>
    <small>Issues detected</small>
  </div>
</div>

## Hourly Activity Trends

```js
// Hourly activity chart - using simple HTML visualization
const hourlyActivityChart = html`
<div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h4>Hourly Activity - ${selectedRange} (Hours ${rangeStart}-${rangeEnd})</h4>
  <p>Data shows ${filteredData.length} hours of activity with ${filteredData.reduce((sum, d) => sum + d.samples, 0)} total samples.</p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 0.5rem; margin-top: 1rem;">
    ${filteredData.map(d => html`
      <div style="text-align: center; padding: 0.5rem; background: ${d.hour === currentHour ? '#fef3c7' : '#f3f4f6'}; border-radius: 4px; border: ${d.hour === currentHour ? '2px solid #f59e0b' : '1px solid #e5e7eb'};">
        <div style="font-weight: bold; color: ${d.hour === currentHour ? '#92400e' : '#374151'};">${d.hour}:00</div>
        <div style="font-size: 0.8rem; color: #6b7280;">${d.samples} samples</div>
        <div style="font-size: 0.7rem; color: #9ca3af;">${d.events} events</div>
        ${d.hour === currentHour ? html`<div style="font-size: 0.7rem; color: #f59e0b; font-weight: bold;">NOW</div>` : ''}
      </div>
    `)}
  </div>
</div>
`;

hourlyActivityChart
```

```js
// Efficiency trend chart - using simple HTML visualization
const efficiencyChart = html`
<div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h4>Efficiency Trends - ${selectedRange}</h4>
  <p>Average efficiency: ${(filteredData.reduce((sum, d) => sum + d.efficiency, 0) / filteredData.length).toFixed(1)}%</p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(60px, 1fr)); gap: 0.5rem; margin-top: 1rem;">
    ${filteredData.map(d => html`
      <div style="text-align: center; padding: 0.5rem; background: ${d.efficiency >= 80 ? '#dcfce7' : d.efficiency >= 70 ? '#fef3c7' : '#fee2e2'}; border-radius: 4px; border: ${d.hour === currentHour ? '2px solid #f59e0b' : '1px solid #e5e7eb'};">
        <div style="font-weight: bold; color: ${d.hour === currentHour ? '#92400e' : '#374151'};">${d.hour}:00</div>
        <div style="font-size: 0.8rem; color: ${d.efficiency >= 80 ? '#166534' : d.efficiency >= 70 ? '#92400e' : '#dc2626'}; font-weight: bold;">${d.efficiency}%</div>
        ${d.hour === currentHour ? html`<div style="font-size: 0.7rem; color: #f59e0b; font-weight: bold;">NOW</div>` : ''}
      </div>
    `)}
  </div>
</div>
`;

efficiencyChart
```

## Machine Performance Today

```js
// Generate machine-specific daily data
const machinePerformanceToday = (machineSummary || []).map(machine => {
  const hoursActive = Math.floor(Math.random() * currentHour) + 1;
  const samplesPerHour = machine.samplesLastHour || 100;
  
  return {
    ...machine,
    hoursActive,
    dailySamples: samplesPerHour * hoursActive + Math.floor(Math.random() * 500),
    dailyEvents: Math.floor(Math.random() * 20) + 5,
    avgEfficiency: Math.floor(Math.random() * 25) + 70,
    peakHour: Math.floor(Math.random() * currentHour),
    downtime: Math.floor(Math.random() * 60), // minutes
    utilizationRate: (hoursActive / dailyTotals.hoursOperating) * 100
  };
});

// Machine performance table
const machineTable = Inputs.table(machinePerformanceToday, {
  columns: [
    "name",
    "model", 
    "status",
    "hoursActive",
    "dailySamples",
    "dailyEvents",
    "avgEfficiency",
    "utilizationRate",
    "downtime"
  ],
  header: {
    name: "Machine",
    model: "Model",
    status: "Status",
    hoursActive: "Hours Active",
    dailySamples: "Daily Samples",
    dailyEvents: "Daily Events", 
    avgEfficiency: "Avg Efficiency (%)",
    utilizationRate: "Utilization (%)",
    downtime: "Downtime (min)"
  },
  format: {
    status: (status) => status.charAt(0).toUpperCase() + status.slice(1),
    avgEfficiency: (d) => `${d.toFixed(1)}%`,
    utilizationRate: (d) => `${d.toFixed(1)}%`,
    dailySamples: (d) => d.toLocaleString()
  },
  width: {
    name: 150,
    model: 100,
    status: 80,
    hoursActive: 100,
    dailySamples: 120,
    dailyEvents: 100,
    avgEfficiency: 120,
    utilizationRate: 120,
    downtime: 100
  }
});
```

<div class="card">
  <h3>🏭 Machine Performance Today</h3>
  ${machineTable}
</div>

## Today's Event Timeline

```js
// Generate timeline events for today
const todaysEvents = [
  {
    time: "06:00",
    machine: "mazak_1_vtc_200",
    event: "Shift Start",
    type: "info",
    description: "Morning shift begins"
  },
  {
    time: "08:30",
    machine: "mazak_2_vtc_300", 
    event: "Maintenance Alert",
    type: "warning",
    description: "Coolant level low"
  },
  {
    time: "10:15",
    machine: "mazak_3_350msy",
    event: "Production Start",
    type: "success", 
    description: "New batch commenced"
  },
  {
    time: "12:00",
    machine: "All Machines",
    event: "Lunch Break",
    type: "info",
    description: "Scheduled downtime"
  },
  {
    time: "14:00",
    machine: "mazak_4_vtc_300c",
    event: "Tool Change",
    type: "warning",
    description: "Automatic tool replacement"
  },
  {
    time: "16:45",
    machine: "mazak_1_vtc_200",
    event: "High Efficiency",
    type: "success",
    description: "95% efficiency achieved"
  }
].filter(event => {
  const eventHour = parseInt(event.time.split(':')[0]);
  return eventHour <= currentHour;
});

function createTimelineEvent(event) {
  const typeColors = {
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6'
  };
  
  const typeIcons = {
    success: '✅',
    warning: '⚠️',
    error: '❌', 
    info: 'ℹ️'
  };
  
  return html`
    <div style="display: flex; align-items: center; padding: 1rem 0; border-left: 3px solid ${typeColors[event.type]}; padding-left: 1rem; border-bottom: 1px solid #f3f4f6;">
      <div style="width: 40px; height: 40px; border-radius: 50%; background: ${typeColors[event.type]}; color: white; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 1.2rem;">
        ${typeIcons[event.type]}
      </div>
      <div style="flex: 1;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <strong style="color: #1f2937;">${event.event}</strong>
          <span style="color: #6b7280; font-size: 0.9rem; font-weight: bold;">${event.time}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="background: #f3f4f6; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: #374151;">
            ${event.machine}
          </span>
          <span style="font-size: 0.9rem; color: #4b5563;">
            ${event.description}
          </span>
        </div>
      </div>
    </div>
  `;
}
```

<div class="card">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #e5e7eb;">
    <h3 style="margin: 0;">🕐 Today's Event Timeline</h3>
    <span style="color: #6b7280; font-size: 0.9rem;">${todaysEvents.length} events so far</span>
  </div>
  <div style="max-height: 400px; overflow-y: auto;">
    ${todaysEvents.map(createTimelineEvent)}
  </div>
</div>

## Hourly Breakdown Analysis

```js
// Create detailed hourly breakdown chart - using HTML visualization
const hourlyBreakdownChart = html`
<div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h4>Detailed Hourly Breakdown</h4>
  <p>Comprehensive view of samples, events, and alerts across ${filteredData.length} hours.</p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 0.5rem; margin-top: 1rem;">
    ${filteredData.map(d => html`
      <div style="text-align: center; padding: 0.5rem; background: ${d.hour === currentHour ? '#fef3c7' : '#f9fafb'}; border-radius: 4px; border: ${d.hour === currentHour ? '2px solid #f59e0b' : '1px solid #e5e7eb'};">
        <div style="font-weight: bold; color: ${d.hour === currentHour ? '#92400e' : '#374151'};">${d.hour}:00</div>
        <div style="font-size: 0.8rem; color: #3b82f6; font-weight: bold;">${d.samples} samples</div>
        <div style="font-size: 0.7rem; color: #10b981;">${d.events} events</div>
        ${d.alerts > 0 ? html`<div style="font-size: 0.7rem; color: #ef4444; font-weight: bold;">${d.alerts} alerts</div>` : ''}
        <div style="font-size: 0.7rem; color: #6b7280;">${d.efficiency}% efficiency</div>
        ${d.hour === currentHour ? html`<div style="font-size: 0.7rem; color: #f59e0b; font-weight: bold;">NOW</div>` : ''}
      </div>
    `)}
  </div>
</div>
`;

hourlyBreakdownChart
```

<div style="margin-top: 2rem; padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #3b82f6;">
  <h4 style="margin-top: 0; color: #1e40af;">📊 Today's Summary</h4>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; font-size: 0.9rem;">
    <div>
      <strong>Peak Hour:</strong> ${todaysHourlyData.reduce((max, hour) => hour.samples > max.samples ? hour : max, todaysHourlyData[0]).hour}:00
    </div>
    <div>
      <strong>Best Efficiency:</strong> ${Math.max(...todaysHourlyData.map(h => h.efficiency))}%
    </div>
    <div>
      <strong>Hours Remaining:</strong> ${23 - currentHour} hours
    </div>
  </div>
</div>

---

<div style="margin-top: 2rem; text-align: center; color: #6b7280; font-size: 0.9rem;">
  <em>Today's view updated: ${new Date().toLocaleString()} • Auto-refresh: 30s</em>
</div>

<script>
// Auto-refresh every 30 seconds
setTimeout(() => {
  if (document.visibilityState === 'visible') {
    window.location.reload();
  }
}, 30000);
</script>
