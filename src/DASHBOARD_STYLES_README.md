# Modern Dashboard Styles for Observable Framework

This style system provides a modern, responsive dashboard design inspired by contemporary CSS Grid layouts, specifically designed for Observable Framework projects.

## Files Overview

- `dashboard-styles.css` - Main stylesheet with comprehensive dashboard styling
- `dashboard-components.css` - Additional styles for reusable components  
- `dashboard-components.js` - JavaScript components for common dashboard elements
- `component-examples.md` - Individual component usage examples

## Quick Start

### 1. Include Stylesheets

Add these lines to your Observable Framework markdown files:

```html
<link rel="stylesheet" href="./dashboard-styles.css">
<link rel="stylesheet" href="./dashboard-components.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
```

### 2. Import Components (Optional)

```js
import {
  HeroSection,
  OverviewCard,
  MetricCard,
  ModernCard,
  StatusIndicator,
  // ... other components
} from "./dashboard-components.js";
```

### 3. Use CSS Classes Directly

For simple layouts, you can use CSS classes directly in your HTML:

```html
<div class="hero-modern">
  <div class="hero-modern__content">
    <h1 class="hero-modern__title">Your Dashboard</h1>
    <p class="hero-modern__subtitle">Real-time monitoring</p>
  </div>
</div>
```

## Style System

### Color Palette

The system uses CSS custom properties for consistent theming:

```css
--primary-bg: #394263      /* Dark blue-gray for headers */
--secondary-bg: #EAEDF1    /* Light gray for backgrounds */
--accent-color: #1BBAE1    /* Bright blue for accents */
--success-color: #27ae60   /* Green for success states */
--warning-color: #f39c12   /* Orange for warnings */
--danger-color: #e74c3c    /* Red for errors/alerts */
--info-color: #3498db      /* Blue for information */
```

### Typography

- **Font Family**: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif
- **Font Weights**: 300 (light), 400 (normal), 700 (bold)
- **Responsive sizing** with clamp() functions

### Spacing System

Consistent spacing using CSS custom properties:

```css
--spacing-xs: 0.25rem   /* 4px */
--spacing-sm: 0.5rem    /* 8px */
--spacing-md: 1rem      /* 16px */
--spacing-lg: 1.5rem    /* 24px */
--spacing-xl: 2rem      /* 32px */
--spacing-xxl: 3rem     /* 48px */
```

## Component Library

### HeroSection

Creates an attractive header with stats:

```js
${HeroSection({
  title: "Machine Observatory",
  subtitle: "Real-time monitoring dashboard",
  stats: [
    { value: "24", label: "Machines", icon: "fas fa-cogs" },
    { value: "98.5%", label: "Uptime", icon: "fas fa-chart-line" }
  ]
})}
```

### OverviewCard

Perfect for key metrics display:

```js
${OverviewCard({
  icon: "fas fa-check-circle",
  iconType: "success",
  title: "Production Status", 
  value: "Running",
  subtitle: "All systems operational"
})}
```

### MetricCard

For displaying numerical metrics with trends:

```js
${MetricCard({
  label: "Efficiency",
  value: "87.3%",
  change: "+2.1% from yesterday",
  changeType: "positive",
  cardType: "success"
})}
```

### ModernCard

Container for charts, tables, and content:

```js
${ModernCard({
  title: "Performance Metrics",
  actions: [
    { icon: "fas fa-download", title: "Export" },
    { icon: "fas fa-cog", title: "Settings" }
  ],
  children: html`<div>Your content here</div>`
})}
```

### StatusIndicator

For showing operational states:

```js
${StatusIndicator("success", "Running")}
${StatusIndicator("warning", "Idle")}
${StatusIndicator("danger", "Alarm")}
```

### TimelineItem

For event lists and activity feeds:

```js
${TimelineItem({
  time: "14:32",
  title: "Production Started",
  description: "New batch initiated",
  meta: "Operator: J. Smith"
})}
```

## Layout Classes

### Grid Layouts

Use Observable Framework's built-in grid classes with enhanced styling:

```html
<div class="grid grid-cols-2">
  <!-- Two column layout -->
</div>

<div class="grid grid-cols-3">
  <!-- Three column layout -->
</div>
```

### Specialized Grids

```html
<!-- Overview cards -->
<div class="overview-grid">
  <!-- Auto-fit cards with minimum 280px width -->
</div>

<!-- Metrics grid -->
<div class="metrics-grid">
  <!-- Auto-fit metric cards with minimum 200px width -->
</div>
```

## CSS-Only Approach

You can build dashboards using only CSS classes without JavaScript components:

```html
<div class="card-modern">
  <div class="card-modern__header">
    <h3 class="card-modern__title">Your Title</h3>
    <div class="card-modern__actions">
      <button class="card-modern__action">
        <i class="fas fa-cog"></i>
      </button>
    </div>
  </div>
  <div class="card-modern__content">
    <p>Your content here...</p>
  </div>
</div>
```

## Responsive Design

The system is fully responsive with breakpoints:

- **Mobile**: < 768px - Single column layouts, adjusted spacing
- **Tablet**: 768px - 1024px - Two column layouts
- **Desktop**: > 1024px - Full multi-column layouts

## Accessibility Features

- **High contrast mode** support
- **Reduced motion** preferences respected
- **Keyboard navigation** support for interactive elements
- **Screen reader** friendly markup
- **Focus indicators** for all interactive elements

## Dark Mode Support

Automatic dark mode detection:

```css
@media (prefers-color-scheme: dark) {
  /* Dark mode styles applied automatically */
}
```

## Integration with Observable Plot

The styles work seamlessly with Observable Plot:

```js
// Use the responsivePlot utility for consistent styling
${responsivePlot({
  height: 300,
  y: { grid: true, label: "Value" },
  marks: [
    Plot.lineY(data, { x: "time", y: "value", stroke: "#1BBAE1" })
  ]
})}
```

## Browser Support

- **Modern browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **CSS Grid** and **CSS Custom Properties** required
- **Graceful degradation** for older browsers

## Performance Considerations

- **Optimized CSS**: Minimal unused styles
- **Hardware acceleration**: Smooth animations using transform and opacity
- **Efficient layouts**: CSS Grid and Flexbox for optimal rendering
- **Minimal JavaScript**: Components are lightweight

## Customization

### Custom Colors

Override CSS custom properties:

```css
:root {
  --accent-color: #your-brand-color;
  --primary-bg: #your-header-color;
}
```

### Custom Spacing

Adjust the spacing scale:

```css
:root {
  --spacing-md: 1.2rem; /* Increase base spacing */
}
```

### Custom Fonts

```css
:root {
  --font-family: "Your Font", sans-serif;
}
```

## Examples

See the example files for complete implementations:

1. `component-examples.md` - Individual component demonstrations
2. Machine dashboards: `mazak-vtc200.md`, `mazak-vtc300.md`, `mazak-350msy.md`

## Tips for Best Results

1. **Consistent icon usage**: Stick to FontAwesome for icons
2. **Semantic HTML**: Use proper heading hierarchy 
3. **Progressive enhancement**: Build with HTML/CSS first, enhance with JS
4. **Mobile-first**: Design for mobile, enhance for desktop
5. **Performance**: Use CSS transforms for animations
6. **Accessibility**: Always include alt text, proper focus states

## Troubleshooting

### Common Issues

1. **Icons not showing**: Ensure FontAwesome is loaded
2. **Responsive issues**: Check CSS Grid browser support
3. **Color inconsistencies**: Verify CSS custom property support
4. **Animation performance**: Use `transform` and `opacity` only

### Browser DevTools

Use these selectors to debug:

```css
.card-modern { /* All modern cards */ }
.overview-card { /* Overview metric cards */ }
.hero-modern { /* Hero sections */ }
.timeline { /* Event timelines */ }
```

This style system provides a solid foundation for building modern, professional dashboards in Observable Framework while maintaining flexibility for customization and excellent performance across devices.
