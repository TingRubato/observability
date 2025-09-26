---
title: Component Usage Example
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-styles.css">
<link rel="stylesheet" href="./dashboard-components.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

```js
import {
  HeroSection,
  QuickStatsGrid,
  ModernCard,
  MetricCard,
  TimelineItem,
  StatusIndicator,
  DataTable,
  ChartContainer,
  ProgressBar,
  MachineStatusPanel,
  generateTimeSeriesData,
  responsivePlot
} from "./dashboard-components.js";
```

<!-- Hero Section Example -->
${HeroSection({
  title: "Production Overview",
  subtitle: "Real-time manufacturing dashboard",
  stats: [
    { value: "24", label: "Machines", icon: "fas fa-cogs" },
    { value: "18", label: "Active", icon: "fas fa-play-circle" },
    { value: "98.5%", label: "Uptime", icon: "fas fa-chart-line" },
    { value: "12.4m", label: "Avg Cycle", icon: "fas fa-clock" }
  ]
})}

<!-- Quick Stats Grid -->
${QuickStatsGrid({
  stats: [
    {
      icon: "fas fa-check-circle",
      iconType: "success",
      title: "Production Status",
      value: "Running",
      subtitle: "All systems operational"
    },
    {
      icon: "fas fa-thermometer-half",
      iconType: "primary",
      title: "Temperature",
      value: "68.2°C",
      subtitle: "Within normal range"
    },
    {
      icon: "fas fa-exclamation-triangle",
      iconType: "warning",
      title: "Alerts",
      value: "3",
      subtitle: "Requires attention"
    },
    {
      icon: "fas fa-clock",
      iconType: "info",
      title: "Cycle Time",
      value: "12.4m",
      subtitle: "Average cycle time"
    }
  ]
})}

<!-- Chart Example -->
<div class="grid grid-cols-2">
  ${ModernCard({
    title: "Performance Metrics",
    actions: [
      { icon: "fas fa-download", title: "Export" },
      { icon: "fas fa-cog", title: "Settings" }
    ],
    children: ChartContainer({
      title: "Real-time Data",
      chart: responsivePlot({
        height: 300,
        marginLeft: 60,
        y: { grid: true, label: "Value" },
        x: { label: "Time" },
        marks: [
          Plot.ruleY([0]),
          Plot.lineY(generateTimeSeriesData(20, 100, 20), {
            x: "time", 
            y: "value", 
            stroke: "#1BBAE1", 
            strokeWidth: 2, 
            tip: true
          })
        ]
      })
    })
  })}

  ${ModernCard({
    title: "Recent Events",
    actions: [{ icon: "fas fa-external-link-alt", title: "View All" }],
    children: html`
      <div class="timeline">
        ${TimelineItem({
          time: "14:32",
          title: "Production Started",
          description: "New batch initiated successfully",
          meta: "Operator: J. Smith"
        })}
        ${TimelineItem({
          time: "13:45",
          title: "Temperature Alert",
          description: "Coolant temperature exceeded threshold",
          meta: "Auto-resolved in 2 minutes"
        })}
        ${TimelineItem({
          time: "12:20",
          title: "Maintenance Complete",
          description: "Scheduled maintenance finished",
          meta: "Duration: 45 minutes"
        })}
      </div>
    `
  })}
</div>

<!-- Metrics Grid -->
<div class="metrics-grid">
  ${MetricCard({
    label: "Efficiency",
    value: "87.3%",
    change: "+2.1% from yesterday",
    changeType: "positive"
  })}
  
  ${MetricCard({
    label: "Quality Rate",
    value: "99.2%",
    change: "+0.5% from yesterday",
    changeType: "positive",
    cardType: "success"
  })}
  
  ${MetricCard({
    label: "Downtime",
    value: "1.2hrs",
    change: "+0.3hrs from yesterday",
    changeType: "negative",
    cardType: "warning"
  })}
  
  ${MetricCard({
    label: "Energy Usage",
    value: "247kWh",
    change: "-15kWh from yesterday",
    changeType: "positive"
  })}
</div>

<!-- Progress Bars Example -->
${ModernCard({
  title: "Production Progress",
  children: html`
    ${ProgressBar({
      label: "Daily Target",
      value: 247,
      max: 300,
      type: "primary"
    })}
    ${ProgressBar({
      label: "Quality Check",
      value: 98,
      max: 100,
      type: "success"
    })}
    ${ProgressBar({
      label: "Tool Life Remaining",
      value: 25,
      max: 100,
      type: "warning"
    })}
  `
})}

<!-- Machine Status Panel -->
${MachineStatusPanel({
  machines: [
    {
      name: "Mazak 350MSY",
      status: "Running",
      statusType: "success",
      details: "Cycle 247/300"
    },
    {
      name: "Mazak VTC200",
      status: "Idle",
      statusType: "warning",
      details: "Awaiting setup"
    },
    {
      name: "Mazak VTC300",
      status: "Maintenance",
      statusType: "danger",
      details: "Scheduled PM"
    }
  ]
})}

<!-- Data Table Example -->
${ModernCard({
  title: "Machine Parameters",
  children: DataTable({
    title: "Current Settings",
    columns: [
      { key: "parameter", header: "Parameter" },
      { key: "value", header: "Value" },
      { 
        key: "status", 
        header: "Status",
        render: (value) => StatusIndicator(value.type, value.label)
      }
    ],
    data: [
      {
        parameter: "Spindle Speed",
        value: "2,450 RPM",
        status: { type: "success", label: "Normal" }
      },
      {
        parameter: "Feed Rate",
        value: "850 mm/min",
        status: { type: "success", label: "Normal" }
      },
      {
        parameter: "Coolant Level",
        value: "15%",
        status: { type: "warning", label: "Low" }
      }
    ]
  })
})}

<style>
/* Page-specific styles can go here */
.demo-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border-left: 4px solid var(--accent-color);
  background: rgba(27, 186, 225, 0.05);
}

.demo-section h3 {
  margin-top: 0;
  color: var(--accent-color);
}
</style>
