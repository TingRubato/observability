// Reusable Dashboard Components for Observable Framework
// Import this file in your markdown pages with: ```js import {ComponentName} from "./dashboard-components.js"```

// Import required styles
import "./dashboard-styles.css";

// Import required libraries
import { Plot } from "@observablehq/plot";
import { html } from "@observablehq/stdlib";
import { resize } from "@observablehq/stdlib";

// Status Indicator Component
export function StatusIndicator(status, label) {
  const statusClasses = {
    success: 'status-indicator--success',
    warning: 'status-indicator--warning',
    danger: 'status-indicator--danger',
    info: 'status-indicator--info'
  };
  
  return html`
    <span class="status-indicator ${statusClasses[status] || statusClasses.info}">
      <div class="status-indicator__dot"></div>
      ${label}
    </span>
  `;
}

// Overview Card Component
export function OverviewCard({icon, iconType = 'primary', title, value, subtitle}) {
  return html`
    <div class="overview-card">
      <div class="overview-card__icon overview-card__icon--${iconType}">
        <i class="${icon}"></i>
      </div>
      <div class="overview-card__content">
        <h3 class="overview-card__title">${title}</h3>
        <div class="overview-card__value">${value}</div>
        <p class="overview-card__subtitle">${subtitle}</p>
      </div>
    </div>
  `;
}

// Metric Card Component
export function MetricCard({label, value, change, changeType, cardType = 'default'}) {
  const changeIcon = changeType === 'positive' ? 'fas fa-arrow-up' : 
                     changeType === 'negative' ? 'fas fa-arrow-down' : 'fas fa-equals';
  
  return html`
    <div class="metric-card ${cardType !== 'default' ? `metric-card--${cardType}` : ''}">
      <div class="metric-card__label">${label}</div>
      <div class="metric-card__value">${value}</div>
      <div class="metric-card__change metric-card__change--${changeType}">
        <i class="${changeIcon}"></i>
        ${change}
      </div>
    </div>
  `;
}

// Timeline Item Component
export function TimelineItem({time, title, description, meta}) {
  return html`
    <div class="timeline-item">
      <div class="timeline-item__time">${time}</div>
      <div class="timeline-item__title">${title}</div>
      <div class="timeline-item__description">${description}</div>
      <div class="timeline-item__meta">${meta}</div>
    </div>
  `;
}

// Modern Card Component
export function ModernCard({title, actions = [], children}) {
  return html`
    <div class="card-modern">
      <div class="card-modern__header">
        <h3 class="card-modern__title">${title}</h3>
        <div class="card-modern__actions">
          ${actions.map(action => html`
            <button class="card-modern__action" title="${action.title}">
              <i class="${action.icon}"></i>
            </button>
          `)}
        </div>
      </div>
      <div class="card-modern__content">
        ${children}
      </div>
    </div>
  `;
}

// Hero Section Component
export function HeroSection({title, subtitle, stats = []}) {
  return html`
    <div class="hero-modern">
      <div class="hero-modern__content">
        <h1 class="hero-modern__title">${title}</h1>
        <p class="hero-modern__subtitle">${subtitle}</p>
        <div class="hero-modern__stats">
          ${stats.map(stat => html`
            <div class="hero-stat">
              <div class="hero-stat__value">${stat.value}</div>
              <div class="hero-stat__label">
                <i class="${stat.icon}"></i>
                ${stat.label}
              </div>
            </div>
          `)}
        </div>
      </div>
    </div>
  `;
}

// Data Table Component
export function DataTable({title, data, columns}) {
  return html`
    <div class="data-table">
      <div class="data-table__header">
        <h3 class="data-table__title">${title}</h3>
      </div>
      <table>
        <thead>
          <tr>
            ${columns.map(col => html`<th>${col.header}</th>`)}
          </tr>
        </thead>
        <tbody>
          ${data.map(row => html`
            <tr>
              ${columns.map(col => html`<td>${col.render ? col.render(row[col.key]) : row[col.key]}</td>`)}
            </tr>
          `)}
        </tbody>
      </table>
    </div>
  `;
}

// Chart Container Component
export function ChartContainer({title, chart, actions = []}) {
  return html`
    <div class="chart-container">
      <div class="chart-container__header">
        <h3 class="chart-container__title">${title}</h3>
        <div class="card-modern__actions">
          ${actions.map(action => html`
            <button class="card-modern__action" title="${action.title}">
              <i class="${action.icon}"></i>
            </button>
          `)}
        </div>
      </div>
      ${chart}
    </div>
  `;
}

// Machine Parameter Row Component (for tables)
export function ParameterRow({label, value, status, statusType = 'success'}) {
  return html`
    <tr>
      <td><strong>${label}</strong></td>
      <td>${value}</td>
      <td>${StatusIndicator(statusType, status)}</td>
    </tr>
  `;
}

// Alert Badge Component
export function AlertBadge({type = 'info', message, icon}) {
  return html`
    <div class="alert-badge alert-badge--${type}">
      <i class="${icon}"></i>
      <span>${message}</span>
    </div>
  `;
}

// Progress Bar Component
export function ProgressBar({label, value, max = 100, type = 'primary'}) {
  const percentage = (value / max) * 100;
  return html`
    <div class="progress-container">
      <div class="progress-label">
        <span>${label}</span>
        <span>${value}/${max} (${percentage.toFixed(1)}%)</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill progress-fill--${type}" style="width: ${percentage}%"></div>
      </div>
    </div>
  `;
}

// Quick Stats Grid Component
export function QuickStatsGrid({stats}) {
  return html`
    <div class="overview-grid">
      ${stats.map(stat => OverviewCard(stat))}
    </div>
  `;
}

// Machine Status Panel Component
export function MachineStatusPanel({machines}) {
  return html`
    <div class="machine-status-panel">
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
        ${machines.map(machine => html`
          <div style="text-align: center; padding: 1rem; background: white; border-radius: 0.5rem; box-shadow: var(--shadow-light);">
            ${StatusIndicator(machine.statusType, machine.status)}
            <div style="margin-top: 0.5rem; font-weight: bold;">${machine.name}</div>
            <div style="margin-top: 0.25rem; font-size: 0.875rem; color: var(--medium-gray);">${machine.details}</div>
          </div>
        `)}
      </div>
    </div>
  `;
}

// Utility function to format timestamps
export function formatTime(date) {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
}

// Utility function to format numbers
export function formatNumber(num, decimals = 1) {
  return Number(num).toFixed(decimals);
}

// Utility function to generate random data (for demos)
export function generateTimeSeriesData(points = 20, baseValue = 100, variance = 20) {
  return Array.from({length: points}, (_, i) => ({
    time: new Date(Date.now() - (points - i) * 60000),
    value: baseValue + (Math.random() - 0.5) * variance + Math.sin(i / 3) * (variance / 4)
  }));
}

// Utility function to create responsive plot wrapper
export function responsivePlot(plotConfig) {
  return resize((width) => Plot.plot({
    ...plotConfig,
    width,
    style: {
      backgroundColor: 'transparent',
      fontSize: '12px'
    }
  }));
}
