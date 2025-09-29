---
title: Live Manufacturing Dashboard
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-components.css">

# 🏭 Live Mazak Manufacturing Dashboard

Real-time monitoring with PostgreSQL database integration and historical analysis capabilities.

```js
// Import database connection utilities
import { createDatabaseConnection, loadDataWithFallback, DatabaseLivePoller } from "./database-connection.js";

// Load data from PostgreSQL database with fallback to files
const machines = await loadDataWithFallback('machines');
const machineSummary = await loadDataWithFallback('machineSummary');
const recentConditions = await loadDataWithFallback('recentConditions');
const recentEvents = await loadDataWithFallback('recentEvents');
```

```js
// Live data polling with database integration
const livePoller = new DatabaseLivePoller({
  host: 'localhost',
  port: 3000,
  interval: 30000 // 30 seconds
});

// Start live polling
await livePoller.start();

// Get current timestamp
const currentTime = new Date().toLocaleString();
```

```js
// Process live data and calculate KPIs
const processedMachines = (machineSummary || []).map(machine => {
  const efficiency = machine.samplesLastHour > 0 ? 
    Math.min((machine.eventsLastHour / machine.samplesLastHour * 100), 100) : 0;
  
  return {
    ...machine,
    efficiency: efficiency,
    statusColor: machine.status === 'online' ? '#22c55e' : 
                machine.status === 'idle' ? '#f59e0b' : '#ef4444',
    statusIcon: machine.status === 'online' ? '🟢' : 
               machine.status === 'idle' ? '🟡' : '🔴'
  };
});

// Calculate overall system metrics
const totalMachines = processedMachines.length;
const onlineMachines = processedMachines.filter(m => m.status === 'online').length;
const totalSamplesLastHour = processedMachines.reduce((sum, m) => sum + (m.samplesLastHour || 0), 0);
const totalEventsLastHour = processedMachines.reduce((sum, m) => sum + (m.eventsLastHour || 0), 0);
const avgEfficiency = processedMachines.length > 0 ? 
  processedMachines.reduce((sum, m) => sum + m.efficiency, 0) / processedMachines.length : 0;
```

<div class="hero">
  <h1>🚀 Live Manufacturing Intelligence Center</h1>
  <p>Real-time monitoring • Last updated: ${currentTime}</p>
  <div style="margin-top: 1rem;">
    <a href="./todays-view" style="display: inline-block; padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.2); color: white; text-decoration: none; border-radius: 8px; font-weight: bold; border: 2px solid rgba(255,255,255,0.3); transition: all 0.3s ease;">
      📅 View Today's Analysis
    </a>
  </div>
  <div style="margin-top: 1rem;">
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem; margin-right: 1rem;">
      🏭 ${onlineMachines}/${totalMachines} Machines Online
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem; margin-right: 1rem;">
      📊 ${totalSamplesLastHour.toLocaleString()} Samples/hr
    </span>
    <span style="padding: 0.5rem 1rem; background: rgba(255,255,255,0.2); border-radius: 0.5rem;">
      📋 ${totalEventsLastHour.toLocaleString()} Events/hr
    </span>
  </div>
  <div style="margin-top: 1rem;">
    <div style="display: inline-block; padding: 0.5rem 1rem; background: rgba(255,255,255,0.15); border-radius: 0.5rem;">
      <span style="color: #10b981;">● LIVE</span> Auto-refresh every 30 seconds
    </div>
  </div>
</div>

## System Overview

<div class="grid grid-cols-4">
  <div class="card">
    <h2>System Status</h2>
    <span class="big" style="color: ${onlineMachines === totalMachines ? 'green' : onlineMachines > 0 ? 'orange' : 'red'}">
      ${Math.round((onlineMachines / totalMachines) * 100)}%
    </span>
    <small>${onlineMachines} of ${totalMachines} machines online</small>
  </div>
  <div class="card">
    <h2>Avg Efficiency</h2>
    <span class="big" style="color: ${avgEfficiency > 70 ? 'green' : avgEfficiency > 50 ? 'orange' : 'red'}">
      ${avgEfficiency.toFixed(1)}%
    </span>
    <small>Across all machines</small>
  </div>
  <div class="card">
    <h2>Activity Rate</h2>
    <span class="big" style="color: ${totalSamplesLastHour > 500 ? 'green' : 'orange'}">
      ${totalSamplesLastHour}
    </span>
    <small>Samples per hour</small>
  </div>
  <div class="card">
    <h2>Event Rate</h2>
    <span class="big" style="color: ${totalEventsLastHour < 50 ? 'green' : 'orange'}">
      ${totalEventsLastHour}
    </span>
    <small>Events per hour</small>
  </div>
</div>

## Machine Status Cards

```js
function createAdvancedStatusCard(machine) {
  return html`
    <div class="card" style="border-left: 4px solid ${machine.statusColor}; position: relative;">
      <div class="status-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
          ${machine.statusIcon} ${machine.name}
        </h3>
        <span style="padding: 0.25rem 0.75rem; background: ${machine.statusColor}; color: white; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">
          ${machine.status.toUpperCase()}
        </span>
      </div>
      
      <div style="margin-bottom: 1rem;">
        <p style="margin: 0.25rem 0;"><strong>Model:</strong> ${machine.model}</p>
        <p style="margin: 0.25rem 0;"><strong>Components:</strong> ${machine.totalComponents}</p>
        <p style="margin: 0.25rem 0;"><strong>Efficiency:</strong> 
          <span style="color: ${machine.efficiency > 70 ? 'green' : machine.efficiency > 50 ? 'orange' : 'red'}; font-weight: bold;">
            ${machine.efficiency.toFixed(1)}%
          </span>
        </p>
      </div>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
        <div style="text-align: center; padding: 0.75rem; background: #f8fafc; border-radius: 6px;">
          <div style="font-size: 1.4rem; font-weight: bold; color: #3b82f6;">${machine.samplesLastHour}</div>
          <div style="font-size: 0.8rem; color: #64748b;">Samples/hr</div>
        </div>
        <div style="text-align: center; padding: 0.75rem; background: #f8fafc; border-radius: 6px;">
          <div style="font-size: 1.4rem; font-weight: bold; color: #10b981;">${machine.eventsLastHour}</div>
          <div style="font-size: 0.8rem; color: #64748b;">Events/hr</div>
        </div>
      </div>
      
      <div style="font-size: 0.85rem; color: #64748b;">
        <strong>Last Active:</strong> ${machine.lastSampleTime ? 
          formatTimeAgo(new Date(machine.lastSampleTime)) : 
          'Never'
        }
      </div>
      
      <!-- Activity indicator bar -->
      <div style="margin-top: 1rem; height: 4px; background: #e5e7eb; border-radius: 2px; overflow: hidden;">
        <div style="height: 100%; background: linear-gradient(90deg, ${machine.statusColor}, #10b981); width: ${Math.min(machine.samplesLastHour / 10, 100)}%; transition: width 0.5s ease;"></div>
      </div>
    </div>
  `;
}

// Helper function for time formatting
function formatTimeAgo(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

const machineCards = processedMachines.map(createAdvancedStatusCard);
html`<div class="grid grid-cols-2">${machineCards}</div>`
```

## Live Activity Stream

```js
// Combine and process recent activity
const recentActivity = [
  ...(recentEvents || []).slice(0, 15).map(e => ({
    ...e, 
    type: 'event', 
    icon: '⚡', 
    color: '#3b82f6',
    description: `${e.event}: ${e.value || 'N/A'}`
  })),
  ...(recentConditions || []).slice(0, 15).map(c => ({
    ...c, 
    type: 'condition', 
    icon: '📊', 
    color: '#10b981',
    description: `${c.condition}: ${c.state || 'N/A'}`
  }))
].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
 .slice(0, 20);

function createActivityItem(item) {
  const timeAgo = formatTimeAgo(new Date(item.timestamp));
  
  return html`
    <div style="display: flex; align-items: flex-start; padding: 1rem 0; border-left: 3px solid ${item.color}; border-bottom: 1px solid #f3f4f6; padding-left: 1rem;">
      <div style="width: 32px; height: 32px; border-radius: 50%; background: ${item.color}; color: white; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; margin-right: 1rem; flex-shrink: 0;">
        ${item.icon}
      </div>
      <div style="flex: 1;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <strong style="color: #1f2937;">${item.machine}</strong>
          <span style="color: #6b7280; font-size: 0.8rem;">${timeAgo}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="background: #f3f4f6; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: #374151;">
            ${item.component}
          </span>
          <span style="font-size: 0.9rem; color: #4b5563;">
            ${item.description}
          </span>
        </div>
      </div>
    </div>
  `;
}

html`
  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #e5e7eb;">
      <h3 style="margin: 0;">🔴 Live Activity Feed</h3>
      <span style="color: #6b7280; font-size: 0.9rem;">${recentActivity.length} recent items</span>
    </div>
    <div style="max-height: 500px; overflow-y: auto;">
      ${recentActivity.map(createActivityItem)}
    </div>
  </div>
`
```

## Real-Time Charts

```js
// Machine activity comparison chart
const activityData = processedMachines.flatMap(m => [
  {machine: m.name, type: 'Samples', count: m.samplesLastHour, status: m.status},
  {machine: m.name, type: 'Events', count: m.eventsLastHour, status: m.status}
]);

const activityChart = Plot.plot({
  title: "Machine Activity (Last Hour)",
  width: 800,
  height: 300,
  marginLeft: 120,
  x: {label: "Activity Count", grid: true},
  y: {label: "Machine", domain: processedMachines.map(m => m.name)},
  color: {legend: true, range: ["#3b82f6", "#10b981"]},
  marks: [
    Plot.barX(activityData, {
      x: "count",
      y: "machine", 
      fill: "type",
      tip: true,
      opacity: 0.8
    }),
    Plot.ruleX([0])
  ]
});

activityChart
```

```js
// Status distribution and efficiency charts
const statusData = processedMachines.map(m => ({
  machine: m.name,
  status: m.status.charAt(0).toUpperCase() + m.status.slice(1),
  efficiency: m.efficiency,
  samples: m.samplesLastHour
}));

// Create status counts for bar chart
const statusCounts = statusData.reduce((acc, m) => {
  acc[m.status] = (acc[m.status] || 0) + 1;
  return acc;
}, {});

const statusChartData = Object.entries(statusCounts).map(([status, count]) => ({
  status,
  count
}));

const statusChart = Plot.plot({
  title: "Machine Status Distribution",
  width: 400,
  height: 300,
  marginLeft: 80,
  x: {label: "Count"},
  y: {label: "Status"},
  color: {
    domain: ["Online", "Idle", "Offline"],
    range: ["#22c55e", "#f59e0b", "#ef4444"]
  },
  marks: [
    Plot.barX(statusChartData, {
      x: "count",
      y: "status",
      fill: "status",
      tip: true
    })
  ]
});

const efficiencyChart = Plot.plot({
  title: "Machine Efficiency Levels",
  width: 400,
  height: 300,
  x: {label: "Machine"},
  y: {label: "Efficiency (%)", domain: [0, 100]},
  color: {
    type: "threshold",
    domain: [50, 70],
    range: ["#ef4444", "#f59e0b", "#22c55e"]
  },
  marks: [
    Plot.barY(statusData, {
      x: "machine",
      y: "efficiency",
      fill: "efficiency",
      tip: true
    }),
    Plot.ruleY([50, 70], {stroke: "gray", strokeDasharray: "2,2"})
  ]
});

html`
  <div class="grid grid-cols-2">
    <div class="card">${statusChart}</div>
    <div class="card">${efficiencyChart}</div>
  </div>
`
```

## Live Data Table

```js
const tableData = recentActivity.slice(0, 15).map(item => ({
  time: new Date(item.timestamp).toLocaleString(),
  machine: item.machine,
  type: item.type.charAt(0).toUpperCase() + item.type.slice(1),
  component: item.component,
  description: item.description,
  status: item.icon
}));

const dataTable = Inputs.table(tableData, {
  columns: ["status", "time", "machine", "type", "component", "description"],
  header: {
    status: "",
    time: "Time",
    machine: "Machine", 
    type: "Type",
    component: "Component",
    description: "Details"
  },
  width: {
    status: 30,
    time: 150,
    machine: 120,
    type: 80,
    component: 100,
    description: 300
  },
  sort: "time",
  reverse: true
});

html`
  <div class="card">
    <h3>📋 Live Data Table</h3>
    ${dataTable}
  </div>
`
```

## System Health Monitoring

```js
// Calculate system health metrics
const systemHealth = {
  uptime: Math.round((onlineMachines / totalMachines) * 100),
  throughput: totalSamplesLastHour,
  alertLevel: totalEventsLastHour > 100 ? 'high' : totalEventsLastHour > 50 ? 'medium' : 'low',
  dataFreshness: Math.min(...processedMachines.map(m => 
    m.lastSampleTime ? (Date.now() - new Date(m.lastSampleTime)) / 60000 : 999
  ))
};

const healthColor = systemHealth.uptime > 90 ? '#22c55e' : 
                   systemHealth.uptime > 70 ? '#f59e0b' : '#ef4444';
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>System Uptime</h2>
    <span class="big" style="color: ${healthColor}">${systemHealth.uptime}%</span>
    <small>Machines operational</small>
  </div>
  <div class="card">
    <h2>Throughput</h2>
    <span class="big" style="color: ${systemHealth.throughput > 1000 ? 'green' : 'orange'}">
      ${(systemHealth.throughput / 1000).toFixed(1)}K
    </span>
    <small>Samples per hour</small>
  </div>
  <div class="card">
    <h2>Alert Level</h2>
    <span class="big" style="color: ${systemHealth.alertLevel === 'low' ? 'green' : systemHealth.alertLevel === 'medium' ? 'orange' : 'red'}">
      ${systemHealth.alertLevel.toUpperCase()}
    </span>
    <small>Event frequency</small>
  </div>
  <div class="card">
    <h2>Data Freshness</h2>
    <span class="big" style="color: ${systemHealth.dataFreshness < 5 ? 'green' : systemHealth.dataFreshness < 30 ? 'orange' : 'red'}">
      ${systemHealth.dataFreshness.toFixed(0)}m
    </span>
    <small>Latest data age</small>
  </div>
</div>

---

*Live dashboard powered by PostgreSQL • Auto-refresh: 30s • Last update: ${currentTime}*
