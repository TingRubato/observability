# Test Dashboard

```js
// Load test data
const testData = FileAttachment("data/loaders/test-simple.json").json();
```

## Test Data

```js
// Display the test data
testData
```

```js
// Show test data in a table
Inputs.table(testData)
```

## Simple Chart

```js
// Simple Chart - using HTML visualization
const simpleChart = html`
<div style="background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
  <h4>Simple Chart</h4>
  <p>Data visualization for ${testData.length} items</p>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem; margin-top: 1rem;">
    ${testData.map(d => html`
      <div style="text-align: center; padding: 0.5rem; background: ${d.status === 'active' ? '#dcfce7' : d.status === 'idle' ? '#fef3c7' : '#fee2e2'}; border-radius: 4px; border: 1px solid #e5e7eb;">
        <div style="font-weight: bold; color: #374151;">${d.name}</div>
        <div style="font-size: 0.8rem; color: #6b7280;">ID: ${d.id}</div>
        <div style="font-size: 0.7rem; color: ${d.status === 'active' ? '#166534' : d.status === 'idle' ? '#92400e' : '#dc2626'}; font-weight: bold;">${d.status}</div>
      </div>
    `)}
  </div>
</div>
`;

simpleChart
```
