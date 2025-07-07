const fs = require('fs');
const path = require('path');

// Function to analyze data structure and count duplicates
function analyzeDataStructure(jsonPath, label) {
    console.log(`\n=== ${label} ===`);
    
    try {
        const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
        
        let totalDataItems = 0;
        let uniqueDataItems = 0;
        let duplicateCounts = {};
        
        // Analyze components
        if (data.device && data.device.components) {
            Object.entries(data.device.components).forEach(([componentId, component]) => {
                console.log(`\nComponent: ${componentId} (${component.type})`);
                
                // Analyze samples
                if (component.samples) {
                    const sampleIds = Object.keys(component.samples);
                    console.log(`  Samples: ${sampleIds.length} unique data items`);
                    totalDataItems += sampleIds.length;
                    uniqueDataItems += sampleIds.length;
                    
                    // Check for duplicates in the data structure
                    sampleIds.forEach(id => {
                        if (!duplicateCounts[id]) {
                            duplicateCounts[id] = 0;
                        }
                        duplicateCounts[id]++;
                    });
                }
                
                // Analyze events
                if (component.events) {
                    const eventIds = Object.keys(component.events);
                    console.log(`  Events: ${eventIds.length} unique data items`);
                    totalDataItems += eventIds.length;
                    uniqueDataItems += eventIds.length;
                    
                    eventIds.forEach(id => {
                        if (!duplicateCounts[id]) {
                            duplicateCounts[id] = 0;
                        }
                        duplicateCounts[id]++;
                    });
                }
                
                // Analyze conditions
                if (component.conditions) {
                    const conditionIds = Object.keys(component.conditions);
                    console.log(`  Conditions: ${conditionIds.length} unique data items`);
                    totalDataItems += conditionIds.length;
                    uniqueDataItems += conditionIds.length;
                    
                    conditionIds.forEach(id => {
                        if (!duplicateCounts[id]) {
                            duplicateCounts[id] = 0;
                        }
                        duplicateCounts[id]++;
                    });
                }
            });
        }
        
        // Check for actual duplicates (same dataItemId across components)
        const duplicates = Object.entries(duplicateCounts).filter(([id, count]) => count > 1);
        
        console.log(`\nSummary:`);
        console.log(`  Total unique data items: ${uniqueDataItems}`);
        console.log(`  Duplicate dataItemIds across components: ${duplicates.length}`);
        
        if (duplicates.length > 0) {
            console.log(`  Duplicate IDs: ${duplicates.map(([id, count]) => `${id}(${count})`).join(', ')}`);
        }
        
        return {
            totalDataItems: uniqueDataItems,
            duplicates: duplicates.length,
            duplicateIds: duplicates.map(([id]) => id)
        };
        
    } catch (error) {
        console.log(`Error analyzing ${label}: ${error.message}`);
        return null;
    }
}

// Function to compare original vs deduplicated data
function compareDataProcessing() {
    console.log('🔍 Data Processing Comparison');
    console.log('============================');
    
    // Check if we have the original output.json from the notebook
    const originalFile = path.join(__dirname, 'output.json');
    const deduplicatedFile = path.join(__dirname, 'output_deduplicated.json');
    
    if (!fs.existsSync(originalFile)) {
        console.log('❌ Original output.json not found. Please run the notebook first.');
        return;
    }
    
    if (!fs.existsSync(deduplicatedFile)) {
        console.log('❌ Deduplicated output not found. Please run the Python deduplication script first.');
        return;
    }
    
    // Analyze original data
    const originalStats = analyzeDataStructure(originalFile, 'ORIGINAL DATA (with duplicates)');
    
    // Analyze deduplicated data
    const deduplicatedStats = analyzeDataStructure(deduplicatedFile, 'DEDUPLICATED DATA (latest values only)');
    
    // Show comparison
    console.log('\n📊 COMPARISON SUMMARY');
    console.log('=====================');
    
    if (originalStats && deduplicatedStats) {
        console.log(`Original data items: ${originalStats.totalDataItems}`);
        console.log(`Deduplicated data items: ${deduplicatedStats.totalDataItems}`);
        console.log(`Duplicates removed: ${originalStats.duplicates}`);
        
        if (originalStats.duplicates > 0) {
            console.log(`\n⚠️  Issues found in original data:`);
            console.log(`   - ${originalStats.duplicates} dataItemIds appear multiple times`);
            console.log(`   - This creates confusion for real-time dashboards`);
            console.log(`   - Each dataItemId should have only one current value`);
        }
        
        console.log(`\n✅ Benefits of deduplication:`);
        console.log(`   - Clean, single-value-per-metric structure`);
        console.log(`   - Ready for real-time dashboard consumption`);
        console.log(`   - No ambiguity about which value is current`);
        console.log(`   - Reduced data size and processing overhead`);
    }
    
    // Show example of the problem
    console.log('\n🔍 EXAMPLE OF THE PROBLEM');
    console.log('========================');
    console.log('In the original data, you might see:');
    console.log('  "auto_time": [');
    console.log('    { "timestamp": "2025-07-07T13:26:07Z", "value": "1013787" },');
    console.log('    { "timestamp": "2025-07-07T13:26:09Z", "value": "1013790" },');
    console.log('    { "timestamp": "2025-07-07T13:26:12Z", "value": "1013792" }');
    console.log('  ]');
    console.log('');
    console.log('After deduplication:');
    console.log('  "auto_time": {');
    console.log('    "timestamp": "2025-07-07T13:26:12Z", "value": "1013792"');
    console.log('  }');
    console.log('');
    console.log('This ensures only the most recent value is used for real-time monitoring.');
}

// Function to demonstrate the deduplication logic
function demonstrateDeduplicationLogic() {
    console.log('\n🧠 DEDUPLICATION LOGIC');
    console.log('======================');
    console.log('1. Group all data items by dataItemId');
    console.log('2. For each dataItemId, find all entries with different timestamps');
    console.log('3. Sort by timestamp (most recent first)');
    console.log('4. Keep only the item with the latest timestamp');
    console.log('5. Discard all older entries for that dataItemId');
    console.log('');
    console.log('This ensures:');
    console.log('  ✅ Only current values are available');
    console.log('  ✅ No confusion about which value is latest');
    console.log('  ✅ Clean data structure for dashboards');
    console.log('  ✅ Reduced data volume');
}

// Main execution
if (require.main === module) {
    compareDataProcessing();
    demonstrateDeduplicationLogic();
    
    console.log('\n💡 RECOMMENDATIONS');
    console.log('==================');
    console.log('1. Use the deduplicated version for real-time dashboards');
    console.log('2. Keep the original version for historical analysis');
    console.log('3. Implement deduplication in your data pipeline');
    console.log('4. Consider using sequence numbers as backup for timestamp comparison');
    console.log('5. Validate that deduplication preserves all unique dataItemIds');
} 