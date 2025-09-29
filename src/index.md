---
title: Manufacturing Observability Dashboard
theme: dashboard
toc: false
---

<link rel="stylesheet" href="./dashboard-styles.css">

# Manufacturing Observability Dashboard

<div class="hero-modern">
  <div class="hero-modern__content">
    <h1 class="hero-modern__title">BHS Manufacturing</h1>
    <p class="hero-modern__subtitle">Real-time Machine Monitoring & Analytics</p>
    <div class="hero-modern__stats">
      <div class="hero-stat">
        <div class="hero-stat__value">4</div>
        <div class="hero-stat__label">
          <i class="fas fa-industry"></i>
          Machines
        </div>
      </div>
      <div class="hero-stat">
        <div class="hero-stat__value">3</div>
        <div class="hero-stat__label">
          <i class="fas fa-play-circle"></i>
          Active
        </div>
      </div>
      <div class="hero-stat">
        <div class="hero-stat__value">98.5%</div>
        <div class="hero-stat__label">
          <i class="fas fa-chart-line"></i>
          Uptime
        </div>
      </div>
      <div class="hero-stat">
        <div class="hero-stat__value">12.4m</div>
        <div class="hero-stat__label">
          <i class="fas fa-clock"></i>
          Avg Cycle
        </div>
      </div>
    </div>
  </div>
</div>

## Machine Overview

<div class="grid grid-cols-2">
  <div class="card-modern">
    <div class="card-modern__header">
      <h3 class="card-modern__title">Mazak VTC 200</h3>
      <div class="card-modern__actions">
        <a href="./mazak-vtc200" class="card-modern__action" title="View Dashboard">
          <i class="fas fa-external-link-alt"></i>
        </a>
      </div>
    </div>
    <div class="card-modern__content">
      <div class="machine-status">
        <div class="status-indicator status-indicator--success">
          <div class="status-indicator__dot"></div>
          Running
        </div>
        <div style="margin-left: auto;">
          <span style="font-weight: bold;">247</span> parts completed
        </div>
      </div>
      <div style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span>Efficiency</span>
          <span style="font-weight: bold;">87.3%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar__fill" style="width: 87.3%; background: #10b981;"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="card-modern">
    <div class="card-modern__header">
      <h3 class="card-modern__title">Mazak VTC 300</h3>
      <div class="card-modern__actions">
        <a href="./mazak-vtc300-final" class="card-modern__action" title="View Dashboard">
          <i class="fas fa-external-link-alt"></i>
        </a>
      </div>
    </div>
    <div class="card-modern__content">
      <div class="machine-status">
        <div class="status-indicator status-indicator--success">
          <div class="status-indicator__dot"></div>
          Running
        </div>
        <div style="margin-left: auto;">
          <span style="font-weight: bold;">189</span> parts completed
        </div>
      </div>
      <div style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span>Efficiency</span>
          <span style="font-weight: bold;">92.1%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar__fill" style="width: 92.1%; background: #10b981;"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="card-modern">
    <div class="card-modern__header">
      <h3 class="card-modern__title">Mazak 350MSY</h3>
      <div class="card-modern__actions">
        <a href="./mazak-350msy" class="card-modern__action" title="View Dashboard">
          <i class="fas fa-external-link-alt"></i>
        </a>
      </div>
    </div>
    <div class="card-modern__content">
      <div class="machine-status">
        <div class="status-indicator status-indicator--warning">
          <div class="status-indicator__dot"></div>
          Idle
        </div>
        <div style="margin-left: auto;">
          <span style="font-weight: bold;">156</span> parts completed
        </div>
      </div>
      <div style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span>Efficiency</span>
          <span style="font-weight: bold;">78.4%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar__fill" style="width: 78.4%; background: #f59e0b;"></div>
        </div>
      </div>
    </div>
  </div>

  <div class="card-modern">
    <div class="card-modern__header">
      <h3 class="card-modern__title">Mazak VTC 300C</h3>
      <div class="card-modern__actions">
        <span class="card-modern__action" title="Dashboard Coming Soon" style="opacity: 0.5;">
          <i class="fas fa-clock"></i>
        </span>
      </div>
    </div>
    <div class="card-modern__content">
      <div class="machine-status">
        <div class="status-indicator status-indicator--danger">
          <div class="status-indicator__dot"></div>
          Maintenance
        </div>
        <div style="margin-left: auto;">
          <span style="font-weight: bold;">0</span> parts completed
        </div>
      </div>
      <div style="margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span>Efficiency</span>
          <span style="font-weight: bold;">0%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar__fill" style="width: 0%; background: #ef4444;"></div>
        </div>
      </div>
    </div>
  </div>
</div>

## Quick Links

<div class="grid grid-cols-3">
  <div class="card">
    <h3><i class="fas fa-tachometer-alt"></i> Machine Dashboards</h3>
    <ul style="list-style: none; padding: 0;">
      <li><a href="./mazak-vtc200">Mazak VTC 200</a></li>
      <li><a href="./mazak-vtc300-final">Mazak VTC 300</a></li>
      <li><a href="./mazak-350msy">Mazak 350MSY (5-Axis)</a></li>
    </ul>
  </div>
  
  <div class="card">
    <h3><i class="fas fa-chart-bar"></i> Analytics</h3>
    <ul style="list-style: none; padding: 0;">
      <li><a href="./example-dashboard">Production Overview</a></li>
      <li><a href="./example-report">Historical Report</a></li>
    </ul>
  </div>
  
  <div class="card">
    <h3><i class="fas fa-cogs"></i> System</h3>
    <ul style="list-style: none; padding: 0;">
      <li><a href="./component-examples">Component Library</a></li>
      <li><span style="opacity: 0.6;">Data Processing</span></li>
      <li><span style="opacity: 0.6;">Configuration</span></li>
    </ul>
  </div>
</div>

---

*Dashboard updated: ${new Date().toLocaleString()}*

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">