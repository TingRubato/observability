# Real-Time Manufacturing Dashboard

```js
// Import our live data polling component
import {createLiveData} from "./components/live-data-poller.js";

// Set up live data streams (polls every 15 seconds)
const liveMachines = createLiveData("/data/loaders/machines.json", 15000);
const liveSummary = createLiveData("/data/loaders/machine-summary.json", 15000);
const liveConditions = createLiveData("/data/loaders/recent-conditions.json", 10000);
const liveEvents = createLiveData("/data/loaders/recent-events.json", 10000);
```

```js
// Current timestamp for "live" indicator
const now = new Date();
const liveIndicator = html`
  <div class="live-status">
    <span class="live-dot"></span>
    <span>LIVE</span>
    <span class="last-update">Last update: ${now.toLocaleTimeString()}</span>
  </div>
`;
```

<div class="dashboard-header">
  <h1>🚀 Real-Time Mazak Manufacturing Dashboard</h1>
  <div class="live-controls">
    ${liveIndicator}
  </div>
</div>

## 📊 Live Machine Status

```js
// Real-time machine status cards
function createStatusCard(machine) {
  const statusColors = {
    online: '#22c55e',
    idle: '#f59e0b', 
    offline: '#ef4444'
  };
  
  const statusIcons = {
    online: '🟢',
    idle: '🟡',
    offline: '🔴'
  };
  
  const color = statusColors[machine.status] || '#6b7280';
  const icon = statusIcons[machine.status] || '⚫';
  
  return html`
    <div class="machine-card ${machine.status}" style="border-color: ${color}">
      <div class="machine-header">
        <h3>${icon} ${machine.name}</h3>
        <div class="status-pill" style="background: ${color}">
          ${machine.status.toUpperCase()}
        </div>
      </div>
      
      <div class="machine-metrics">
        <div class="metric">
          <span class="metric-value">${machine.totalComponents}</span>
          <span class="metric-label">Components</span>
        </div>
        <div class="metric">
          <span class="metric-value">${machine.samplesLastHour}</span>
          <span class="metric-label">Samples/hr</span>
        </div>
        <div class="metric">
          <span class="metric-value">${machine.eventsLastHour}</span>
          <span class="metric-label">Events/hr</span>
        </div>
      </div>
      
      <div class="machine-details">
        <div class="detail-row">
          <span class="detail-label">Model:</span>
          <span class="detail-value">${machine.model}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Last Active:</span>
          <span class="detail-value">
            ${machine.lastSampleTime ? 
              formatTimeAgo(new Date(machine.lastSampleTime)) : 
              'Never'
            }
          </span>
        </div>
      </div>
      
      <div class="activity-indicator">
        <div class="activity-bar" style="width: ${Math.min(machine.samplesLastHour / 10, 100)}%"></div>
      </div>
    </div>
  `;
}

// Helper function to format time ago
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

// Render machine status cards
const machineCards = (liveSummary.value || []).map(createStatusCard);
html`<div class="machines-grid">${machineCards}</div>`
```

## 📈 Live Activity Stream

```js
// Combine and display recent activity
const recentActivity = [
  ...(liveEvents.value || []).slice(0, 10).map(e => ({...e, type: 'event', icon: '⚡', color: '#3b82f6'})),
  ...(liveConditions.value || []).slice(0, 10).map(c => ({...c, type: 'condition', icon: '📊', color: '#10b981'}))
].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
 .slice(0, 15);

// Activity stream component
function createActivityItem(item) {
  const timeAgo = formatTimeAgo(new Date(item.timestamp));
  
  return html`
    <div class="activity-item" style="border-left-color: ${item.color}">
      <div class="activity-icon" style="background: ${item.color}">
        ${item.icon}
      </div>
      <div class="activity-content">
        <div class="activity-header">
          <strong class="machine-name">${item.machine}</strong>
          <span class="activity-time">${timeAgo}</span>
        </div>
        <div class="activity-body">
          <span class="component-badge">${item.component}</span>
          <span class="activity-description">
            ${item.type === 'event' ? 
              `${item.event}: ${item.value || 'N/A'}` :
              `${item.condition}: ${item.state || 'N/A'}`
            }
          </span>
        </div>
      </div>
    </div>
  `;
}

html`
  <div class="activity-stream">
    <div class="stream-header">
      <h3>🔴 Live Activity Feed</h3>
      <span class="activity-count">${recentActivity.length} recent items</span>
    </div>
    <div class="stream-content">
      ${recentActivity.map(createActivityItem)}
    </div>
  </div>
`
```

## 📊 Real-Time Charts

```js
import {Plot} from "@observablehq/plot";

// Machine activity chart
const activityData = (liveSummary.value || []).flatMap(m => [
  {machine: m.name, type: 'Samples', count: m.samplesLastHour, status: m.status},
  {machine: m.name, type: 'Events', count: m.eventsLastHour, status: m.status}
]);

const activityChart = Plot.plot({
  title: "Machine Activity (Last Hour)",
  width: 800,
  height: 300,
  marginLeft: 100,
  x: {label: "Activity Count", grid: true},
  y: {label: "Machine", domain: (liveSummary.value || []).map(m => m.name)},
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
// Status distribution donut chart
const statusCounts = (liveSummary.value || []).reduce((acc, machine) => {
  acc[machine.status] = (acc[machine.status] || 0) + 1;
  return acc;
}, {});

const statusData = Object.entries(statusCounts).map(([status, count]) => ({
  status: status.charAt(0).toUpperCase() + status.slice(1),
  count,
  percentage: Math.round((count / (liveSummary.value || []).length) * 100)
}));

const statusChart = Plot.plot({
  title: "Machine Status Distribution",
  width: 400,
  height: 400,
  color: {
    domain: ["Online", "Idle", "Offline"],
    range: ["#22c55e", "#f59e0b", "#ef4444"]
  },
  marks: [
    Plot.arc(statusData, {
      innerRadius: 60,
      outerRadius: 140,
      startAngle: 0,
      endAngle: (d) => (d.count / (liveSummary.value || []).length) * 2 * Math.PI,
      fill: "status",
      tip: true
    }),
    Plot.text(statusData, {
      text: (d) => `${d.status}\n${d.count} (${d.percentage}%)`,
      fontSize: 12,
      fontWeight: "bold",
      fill: "white"
    })
  ]
});

statusChart
```

## 🔍 Live Data Table

```js
// Interactive data table with live updates
const tableData = recentActivity.slice(0, 20).map(item => ({
  time: new Date(item.timestamp).toLocaleString(),
  machine: item.machine,
  type: item.type.charAt(0).toUpperCase() + item.type.slice(1),
  component: item.component,
  description: item.type === 'event' ? 
    `${item.event}: ${item.value || 'N/A'}` :
    `${item.condition}: ${item.state || 'N/A'}`,
  status: item.type === 'event' ? '⚡' : '📊'
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
  <div class="data-table-container">
    <h3>📋 Live Data Table</h3>
    ${dataTable}
  </div>
`
```

<style>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 0;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.live-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f0fdf4;
  border: 1px solid #22c55e;
  border-radius: 8px;
  font-weight: 500;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.last-update {
  font-size: 0.8rem;
  color: #6b7280;
}

.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.machine-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.machine-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}

.machine-card.online {
  border-color: #22c55e;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, white 100%);
}

.machine-card.idle {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, white 100%);
}

.machine-card.offline {
  border-color: #ef4444;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, white 100%);
}

.machine-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.machine-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.status-pill {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  color: white;
  font-size: 0.8rem;
  font-weight: bold;
}

.machine-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric {
  text-align: center;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
}

.metric-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.metric-label {
  display: block;
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.machine-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.detail-label {
  color: #6b7280;
}

.detail-value {
  font-weight: 500;
}

.activity-indicator {
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.activity-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.activity-stream {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.stream-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.stream-header h3 {
  margin: 0;
}

.activity-count {
  color: #6b7280;
  font-size: 0.9rem;
}

.stream-content {
  max-height: 500px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem 0;
  border-left: 3px solid #e5e7eb;
  border-bottom: 1px solid #f3f4f6;
  padding-left: 1rem;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
  margin-right: 1rem;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.machine-name {
  color: #1f2937;
}

.activity-time {
  color: #6b7280;
  font-size: 0.8rem;
}

.activity-body {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.component-badge {
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #374151;
}

.activity-description {
  font-size: 0.9rem;
  color: #4b5563;
}

.data-table-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.data-table-container h3 {
  margin-top: 0;
  margin-bottom: 1rem;
}
</style>
