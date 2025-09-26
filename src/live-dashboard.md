# Live Manufacturing Dashboard

```js
// Load data from our PostgreSQL database
const machines = FileAttachment("data/loaders/machines.json").json();
const machineSummary = FileAttachment("data/loaders/machine-summary.json").json();
const recentConditions = FileAttachment("data/loaders/recent-conditions.json").json();
const recentEvents = FileAttachment("data/loaders/recent-events.json").json();
```

```js
// Auto-refresh the page every 30 seconds for live updates
const refreshInterval = 30000; // 30 seconds
setInterval(() => {
  if (document.visibilityState === 'visible') {
    window.location.reload();
  }
}, refreshInterval);
```

<div class="hero">
  <h1>🏭 Mazak Manufacturing Live Dashboard</h1>
  <h2>Real-time monitoring of manufacturing equipment</h2>
</div>

## Machine Status Overview

```js
// Create status cards for each machine
const statusCards = machineSummary.map(machine => {
  const statusColor = machine.status === 'online' ? '#22c55e' : 
                     machine.status === 'idle' ? '#f59e0b' : '#ef4444';
  const statusIcon = machine.status === 'online' ? '🟢' : 
                    machine.status === 'idle' ? '🟡' : '🔴';
  
  return html`
    <div class="status-card" style="border-left: 4px solid ${statusColor}">
      <div class="status-header">
        <h3>${statusIcon} ${machine.name}</h3>
        <span class="status-badge" style="background-color: ${statusColor}20; color: ${statusColor}">
          ${machine.status.toUpperCase()}
        </span>
      </div>
      <div class="status-details">
        <p><strong>Model:</strong> ${machine.model}</p>
        <p><strong>Components:</strong> ${machine.totalComponents}</p>
        <p><strong>Samples (1h):</strong> ${machine.samplesLastHour}</p>
        <p><strong>Events (1h):</strong> ${machine.eventsLastHour}</p>
        <p><strong>Last Sample:</strong> ${machine.lastSampleTime ? new Date(machine.lastSampleTime).toLocaleString() : 'Never'}</p>
      </div>
    </div>
  `;
});

html`<div class="status-grid">${statusCards}</div>`
```

## Recent Activity Timeline

```js
// Combine and sort recent events and conditions
const recentActivity = [
  ...recentEvents.map(e => ({...e, type: 'event', icon: '⚡'})),
  ...recentConditions.map(c => ({...c, type: 'condition', icon: '📊'}))
].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
 .slice(0, 20);

// Create timeline
const timeline = recentActivity.map(item => {
  const timeAgo = Math.round((Date.now() - new Date(item.timestamp)) / 1000 / 60); // minutes ago
  const typeColor = item.type === 'event' ? '#3b82f6' : '#10b981';
  
  return html`
    <div class="timeline-item">
      <div class="timeline-icon" style="background-color: ${typeColor}">
        ${item.icon}
      </div>
      <div class="timeline-content">
        <div class="timeline-header">
          <strong>${item.machine}</strong>
          <span class="timeline-time">${timeAgo}m ago</span>
        </div>
        <div class="timeline-details">
          <span class="component-tag">${item.component}</span>
          ${item.type === 'event' ? 
            html`<span class="event-name">${item.event}: ${item.value}</span>` :
            html`<span class="condition-name">${item.condition}: ${item.state}</span>`
          }
        </div>
      </div>
    </div>
  `;
});

html`
  <div class="timeline-container">
    <h3>📈 Recent Activity (Last 24 Hours)</h3>
    <div class="timeline">
      ${timeline}
    </div>
  </div>
`
```

## Machine Performance Charts

```js
import {Plot} from "@observablehq/plot";

// Activity by machine (last hour)
const activityData = machineSummary.map(m => [
  {machine: m.name, type: 'Samples', count: m.samplesLastHour},
  {machine: m.name, type: 'Events', count: m.eventsLastHour}
]).flat();

Plot.plot({
  title: "Activity in Last Hour",
  width: 800,
  height: 400,
  marginLeft: 120,
  x: {label: "Count"},
  y: {label: "Machine"},
  color: {legend: true},
  marks: [
    Plot.barX(activityData, {
      x: "count",
      y: "machine",
      fill: "type",
      tip: true
    })
  ]
})
```

```js
// Status distribution pie chart
const statusCounts = machineSummary.reduce((acc, machine) => {
  acc[machine.status] = (acc[machine.status] || 0) + 1;
  return acc;
}, {});

const statusData = Object.entries(statusCounts).map(([status, count]) => ({
  status: status.charAt(0).toUpperCase() + status.slice(1),
  count
}));

Plot.plot({
  title: "Machine Status Distribution",
  width: 400,
  height: 400,
  marks: [
    Plot.arc(statusData, {
      innerRadius: 50,
      outerRadius: 150,
      startAngle: 0,
      endAngle: (d) => (d.count / machineSummary.length) * 2 * Math.PI,
      fill: "status",
      tip: true
    }),
    Plot.text(statusData, {
      text: (d) => `${d.status}\n${d.count}`,
      fontSize: 12,
      fontWeight: "bold"
    })
  ]
})
```

## Live Data Feed

```js
// Real-time data table
const liveDataTable = Inputs.table(recentActivity.slice(0, 10), {
  columns: [
    "machine",
    "type", 
    "component",
    "timestamp"
  ],
  header: {
    machine: "Machine",
    type: "Type",
    component: "Component",
    timestamp: "Time"
  },
  format: {
    timestamp: d => new Date(d).toLocaleString(),
    type: d => d.charAt(0).toUpperCase() + d.slice(1)
  },
  width: {
    machine: 150,
    type: 80,
    component: 120,
    timestamp: 180
  }
});

html`
  <div class="live-feed">
    <h3>🔴 Live Data Feed</h3>
    <div class="refresh-indicator">
      <span>🔄 Auto-refresh every 30 seconds</span>
      <span style="color: #22c55e; font-weight: bold;">● LIVE</span>
    </div>
    ${liveDataTable}
  </div>
`
```

<style>
.hero {
  text-align: center;
  padding: 2rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.hero h1 {
  margin: 0;
  font-size: 2.5rem;
}

.hero h2 {
  margin: 0.5rem 0 0 0;
  font-weight: 300;
  opacity: 0.9;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-left: 4px solid #3b82f6;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.status-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-details p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.timeline-container {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.timeline {
  max-height: 400px;
  overflow-y: auto;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.2rem;
  color: white;
}

.timeline-content {
  flex: 1;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.timeline-time {
  color: #6b7280;
  font-size: 0.8rem;
}

.component-tag {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-right: 0.5rem;
}

.event-name, .condition-name {
  font-size: 0.9rem;
  color: #374151;
}

.live-feed {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.refresh-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #f9fafb;
  border-radius: 4px;
  font-size: 0.9rem;
}
</style>
