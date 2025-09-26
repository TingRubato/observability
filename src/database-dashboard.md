# 🏭 Live Manufacturing Database Dashboard

Real-time dashboard connected to PostgreSQL database.

```js
// Simple test to show the dashboard is loading
const currentTime = new Date().toLocaleString();
```

<div class="hero">
  <h1>🚀 Manufacturing Dashboard</h1>
  <p>Last updated: ${currentTime}</p>
</div>

## Database Connection Test

```js
// Test if we can load static data first
const testMachines = [
  {
    id: 1,
    name: "mazak_1_vtc_200",
    model: "VTC-200",
    status: "online",
    components: 15,
    samplesLastHour: 245,
    eventsLastHour: 12,
    lastUpdate: "2025-07-15 14:30:00"
  },
  {
    id: 2, 
    name: "mazak_2_vtc_300",
    model: "VTC-300",
    status: "idle", 
    components: 18,
    samplesLastHour: 89,
    eventsLastHour: 3,
    lastUpdate: "2025-07-15 14:28:00"
  },
  {
    id: 3,
    name: "mazak_3_350msy",
    model: "350MSY",
    status: "offline",
    components: 12,
    samplesLastHour: 0,
    eventsLastHour: 1,
    lastUpdate: "2025-07-15 12:15:00"
  },
  {
    id: 4,
    name: "mazak_4_vtc_300c",
    model: "VTC-300C", 
    status: "online",
    components: 20,
    samplesLastHour: 312,
    eventsLastHour: 8,
    lastUpdate: "2025-07-15 14:29:00"
  }
];

testMachines
```

## Machine Status Cards

```js
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
    <div class="machine-card" style="border-left: 4px solid ${color}">
      <div class="card-header">
        <h3>${icon} ${machine.name}</h3>
        <span class="status-badge" style="background: ${color}; color: white;">
          ${machine.status.toUpperCase()}
        </span>
      </div>
      <div class="card-content">
        <p><strong>Model:</strong> ${machine.model}</p>
        <p><strong>Components:</strong> ${machine.components}</p>
        <div class="metrics">
          <div class="metric">
            <span class="metric-value">${machine.samplesLastHour}</span>
            <span class="metric-label">Samples/hr</span>
          </div>
          <div class="metric">
            <span class="metric-value">${machine.eventsLastHour}</span>
            <span class="metric-label">Events/hr</span>
          </div>
        </div>
        <p class="last-update"><strong>Last Update:</strong> ${machine.lastUpdate}</p>
      </div>
    </div>
  `;
}

const statusCards = testMachines.map(createStatusCard);
html`<div class="machines-grid">${statusCards}</div>`
```

## Activity Chart

```js
// Activity Chart - using HTML visualization
const activityData = testMachines.flatMap(m => [
  {machine: m.name, type: 'Samples', count: m.samplesLastHour},
  {machine: m.name, type: 'Events', count: m.eventsLastHour}
]);

const activityChart = html`
<div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h4>Machine Activity (Last Hour)</h4>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
    ${testMachines.map(machine => html`
      <div style="background: #f8fafc; padding: 1rem; border-radius: 6px; border: 1px solid #e5e7eb;">
        <h5 style="margin: 0 0 0.5rem 0; color: #374151;">${machine.name}</h5>
        <div style="display: flex; gap: 1rem;">
          <div style="flex: 1; text-align: center; padding: 0.5rem; background: #dbeafe; border-radius: 4px;">
            <div style="font-size: 1.2rem; font-weight: bold; color: #1e40af;">${machine.samplesLastHour}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Samples</div>
          </div>
          <div style="flex: 1; text-align: center; padding: 0.5rem; background: #dcfce7; border-radius: 4px;">
            <div style="font-size: 1.2rem; font-weight: bold; color: #166534;">${machine.eventsLastHour}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Events</div>
          </div>
        </div>
      </div>
    `)}
  </div>
</div>
`;

activityChart
```

## Status Distribution

```js
// Status Distribution - using HTML visualization
const statusCounts = testMachines.reduce((acc, machine) => {
  acc[machine.status] = (acc[machine.status] || 0) + 1;
  return acc;
}, {});

const statusData = Object.entries(statusCounts).map(([status, count]) => ({
  status: status.charAt(0).toUpperCase() + status.slice(1),
  count,
  percentage: Math.round((count / testMachines.length) * 100)
}));

const statusChart = html`
<div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h4>Machine Status Distribution</h4>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
    ${statusData.map(status => {
      const colors = {
        'Online': '#22c55e',
        'Idle': '#f59e0b', 
        'Offline': '#ef4444'
      };
      const icons = {
        'Online': '🟢',
        'Idle': '🟡',
        'Offline': '🔴'
      };
      return html`
        <div style="text-align: center; padding: 1rem; background: ${colors[status.status] || '#f3f4f6'}; border-radius: 8px; color: white;">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">${icons[status.status] || '⚫'}</div>
          <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.25rem;">${status.count}</div>
          <div style="font-size: 0.9rem; opacity: 0.9;">${status.status}</div>
          <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.25rem;">${status.percentage}%</div>
        </div>
      `;
    })}
  </div>
</div>
`;

statusChart
```

## Data Table

```js
Inputs.table(testMachines, {
  columns: ["name", "model", "status", "components", "samplesLastHour", "eventsLastHour", "lastUpdate"],
  header: {
    name: "Machine Name",
    model: "Model", 
    status: "Status",
    components: "Components",
    samplesLastHour: "Samples/hr",
    eventsLastHour: "Events/hr",
    lastUpdate: "Last Update"
  },
  format: {
    status: (status) => status.charAt(0).toUpperCase() + status.slice(1)
  }
})
```

<style>
.hero {
  text-align: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.hero h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.5rem;
}

.hero p {
  margin: 0;
  opacity: 0.9;
}

.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.machine-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-left: 4px solid #3b82f6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.card-content p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.metrics {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.metric {
  text-align: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
  flex: 1;
}

.metric-value {
  display: block;
  font-size: 1.4rem;
  font-weight: bold;
  color: #1e40af;
}

.metric-label {
  display: block;
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.last-update {
  color: #64748b;
  font-size: 0.85rem !important;
}
</style>
