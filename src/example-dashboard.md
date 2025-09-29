---
theme: dashboard
title: Production Overview
toc: false
---

# Machine Status Dashboard 🏭

<!-- Custom styling for improved layout -->

```html
<style>
.machine-overview {
  margin: 2rem 0;
}

.overview-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.overview-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.overview-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.machine-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.machine-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.machine-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--status-color, #e5e7eb);
}

.machine-card.running::before { background: #22c55e; }
.machine-card.idle::before { background: #f59e0b; }
.machine-card.maintenance::before { background: #ef4444; }
.machine-card.setup::before { background: #3b82f6; }
.machine-card.error::before { background: #dc2626; }

.machine-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.machine-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.machine-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
}

.machine-status {
  text-align: center;
  margin-bottom: 1.5rem;
}

.status-text {
  font-size: 1.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.machine-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 0.9rem;
  color: #1f2937;
  font-weight: 600;
}

.chart-section {
  margin: 3rem 0;
}

.chart-section h3 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  color: #1f2937;
  font-weight: 600;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.individual-chart {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .machine-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-grid {
    grid-template-columns: 1fr;
  }
  
  .machine-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
```

<!-- Load and transform the data -->

```js
// Import required libraries
import * as Plot from "@observablehq/plot";

// Generate sample machine data for demonstration
const machines = [
  {id: "MAZAK-350MSY", name: "MAZAK 350MSY", type: "CNC Mill", location: "Shop Floor A"},
  {id: "MAZAK-VTC200", name: "MAZAK VTC200", type: "Vertical Center", location: "Shop Floor B"},
  {id: "MAZAK-VTC300", name: "MAZAK VTC300", type: "Vertical Center", location: "Shop Floor C"},
  {id: "HAAS-VF2", name: "HAAS VF2", type: "CNC Mill", location: "Shop Floor A"},
  {id: "FANUC-Robot", name: "FANUC Robot", type: "Industrial Robot", location: "Assembly Line"}
];

// Generate machine status data over time
const machineData = machines.flatMap(machine =>
  Array.from({length: 30}, (_, i) => ({
    machineId: machine.id,
    machineName: machine.name,
    machineType: machine.type,
    location: machine.location,
    date: new Date(2024, 0, i + 1),
    state: ["Running", "Idle", "Maintenance", "Setup", "Error"][Math.floor(Math.random() * 5)],
    temperature: Math.round(20 + Math.random() * 15), // 20-35°C
    vibration: Math.round(Math.random() * 10), // 0-10 scale
    efficiency: Math.round(60 + Math.random() * 40) // 60-100%
  }))
);

// Define chart functions
function machineStatusTimeline(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 300,
    color: {
      type: "categorical",
      domain: ["Running", "Idle", "Maintenance", "Setup", "Error"],
      range: ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#dc2626"]
    },
    marks: [
      Plot.line(data, {
        x: "date",
        y: "machineName",
        stroke: "state",
        strokeWidth: 2
      }),
      Plot.dot(data, {
        x: "date",
        y: "machineName",
        fill: "state",
        r: 4
      })
    ],
    x: {label: "Date"},
    y: {label: "Machine"}
  });
}

function machineStatusChart(data, {width} = {}) {
  return Plot.plot({
    width,
    height: 300,
    color: {
      type: "categorical",
      domain: ["Running", "Idle", "Maintenance", "Setup", "Error"],
      range: ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#dc2626"]
    },
    marks: [
      Plot.bar(data, Plot.groupX({y: "count"}, {
        x: "machineName",
        fill: "state"
      }))
    ],
    x: {label: "Machine"},
    y: {label: "Count"}
  });
}

function individualMachineChart(machineId, data, {width} = {}) {
  const machineData = data.filter(d => d.machineId === machineId);
  return Plot.plot({
    width,
    height: 200,
    color: {
      type: "categorical",
      domain: ["Running", "Idle", "Maintenance", "Setup", "Error"],
      range: ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#dc2626"]
    },
    marks: [
      Plot.line(machineData, {
        x: "date",
        y: "efficiency",
        stroke: "state",
        strokeWidth: 2
      }),
      Plot.dot(machineData, {
        x: "date",
        y: "efficiency",
        fill: "state",
        r: 3
      })
    ],
    x: {label: "Date"},
    y: {label: "Efficiency %"}
  });
}
```


<!-- Machine status summary cards -->

```js
// Get latest status for each machine
const latestMachineStatus = machines.map(machine => {
  const latestData = machineData.filter(d => d.machineId === machine.id).slice(-1)[0];
  const statusColors = {
    "Running": "#22c55e",
    "Idle": "#f59e0b",
    "Maintenance": "#ef4444",
    "Setup": "#3b82f6",
    "Error": "#dc2626"
  };
  return {
    ...machine,
    currentState: latestData ? latestData.state : 'Unknown',
    currentTemp: latestData ? latestData.temperature : null,
    stateColor: latestData ? statusColors[latestData.state] : '#666',
    efficiency: latestData ? latestData.efficiency : null,
    vibration: latestData ? latestData.vibration : null
  };
});

// Create machine cards HTML using a function that returns HTML string
function createMachineCards() {
  let cardsHTML = `
  <div class="machine-overview">
    <div class="overview-header">
      <h2>🏭 Machine Status Overview</h2>
      <p>Real-time status of all production machines</p>
    </div>

    <div class="machine-grid">
  `;

  latestMachineStatus.forEach(machine => {
    cardsHTML += `
        <div class="machine-card ${machine.currentState.toLowerCase()}">
          <div class="machine-header">
            <h3>${machine.name}</h3>
            <div class="status-indicator" style="background-color: ${machine.stateColor}"></div>
          </div>
          <div class="machine-status">
            <span class="status-text" style="color: ${machine.stateColor}">${machine.currentState}</span>
          </div>
          <div class="machine-metrics">
            <div class="metric">
              <span class="metric-label">Type</span>
              <span class="metric-value">${machine.type}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Location</span>
              <span class="metric-value">${machine.location}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Temperature</span>
              <span class="metric-value">${machine.currentTemp ? machine.currentTemp + '°C' : 'N/A'}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value">${machine.efficiency ? machine.efficiency + '%' : 'N/A'}</span>
            </div>
          </div>
        </div>
    `;
  });

  cardsHTML += `
    </div>
  </div>
  `;

  return cardsHTML;
}

const machineCardsHTML = createMachineCards();

// Output the machine cards HTML
machineCardsHTML
```

<!-- Analytics Section -->

<div class="chart-section">
  <h3>📊 Machine Analytics</h3>
  
  <div class="card">
    <h4>Machine Status Over Time</h4>
    ${resize((width) => machineStatusTimeline(machineData, {width}))}
  </div>
</div>

<div class="card">
  <h4>Status Distribution by Machine</h4>
  ${resize((width) => machineStatusChart(machineData, {width}))}
</div>

<!-- Individual Machine Analysis -->

<div class="chart-section">
  <h3>🔍 Individual Machine Analysis</h3>
  <p>Detailed status history for each machine</p>
  
  <div class="chart-grid">
    <div class="individual-chart">
      <h4>MAZAK 350MSY</h4>
      ${resize((width) => individualMachineChart("MAZAK-350MSY", machineData, {width}))}
    </div>
    <div class="individual-chart">
      <h4>MAZAK VTC200</h4>
      ${resize((width) => individualMachineChart("MAZAK-VTC200", machineData, {width}))}
    </div>
    <div class="individual-chart">
      <h4>MAZAK VTC300</h4>
      ${resize((width) => individualMachineChart("MAZAK-VTC300", machineData, {width}))}
    </div>
    <div class="individual-chart">
      <h4>HAAS VF2</h4>
      ${resize((width) => individualMachineChart("HAAS-VF2", machineData, {width}))}
    </div>
    <div class="individual-chart">
      <h4>FANUC Robot</h4>
      ${resize((width) => individualMachineChart("FANUC-Robot", machineData, {width}))}
    </div>
  </div>
</div>

Data: Sample machine status data for demonstration purposes
