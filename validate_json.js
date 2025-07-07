const fs = require('fs');
const path = require('path');

// Function to validate JSON structure
function validateJsonFile(jsonPath) {
    try {
        console.log(`\n=== Validating ${path.basename(jsonPath)} ===`);
        
        // Read and parse JSON
        const jsonData = fs.readFileSync(jsonPath, 'utf8');
        const data = JSON.parse(jsonData);
        
        console.log('✅ JSON is valid and parseable');
        
        // Check structure
        if (!data.header) {
            console.log('❌ Missing header section');
            return false;
        }
        
        if (!data.device) {
            console.log('❌ Missing device section');
            return false;
        }
        
        if (!data.device.components) {
            console.log('❌ Missing components section');
            return false;
        }
        
        console.log('✅ Basic structure is correct');
        
        // Check header fields
        const requiredHeaderFields = ['creationTime', 'sender', 'instanceId'];
        const missingHeaderFields = requiredHeaderFields.filter(field => !data.header[field]);
        if (missingHeaderFields.length > 0) {
            console.log(`❌ Missing header fields: ${missingHeaderFields.join(', ')}`);
            return false;
        }
        
        console.log('✅ Header fields are complete');
        
        // Check device fields
        if (!data.device.name || !data.device.uuid) {
            console.log('❌ Missing device name or uuid');
            return false;
        }
        
        console.log('✅ Device fields are complete');
        
        // Count components and data items
        const componentCount = Object.keys(data.device.components).length;
        let totalDataItems = 0;
        let sampleCount = 0;
        let eventCount = 0;
        let conditionCount = 0;
        
        Object.values(data.device.components).forEach(component => {
            if (component.samples) {
                sampleCount += Object.keys(component.samples).length;
                totalDataItems += Object.keys(component.samples).length;
            }
            if (component.events) {
                eventCount += Object.keys(component.events).length;
                totalDataItems += Object.keys(component.events).length;
            }
            if (component.conditions) {
                conditionCount += Object.keys(component.conditions).length;
                totalDataItems += Object.keys(component.conditions).length;
            }
        });
        
        console.log(`📊 Statistics:`);
        console.log(`   Components: ${componentCount}`);
        console.log(`   Samples: ${sampleCount}`);
        console.log(`   Events: ${eventCount}`);
        console.log(`   Conditions: ${conditionCount}`);
        console.log(`   Total data items: ${totalDataItems}`);
        
        // Check for null values (UNAVAILABLE data)
        let nullCount = 0;
        let totalValues = 0;
        
        Object.values(data.device.components).forEach(component => {
            ['samples', 'events'].forEach(dataType => {
                if (component[dataType]) {
                    Object.values(component[dataType]).forEach(item => {
                        totalValues++;
                        if (item.value === null) nullCount++;
                    });
                }
            });
        });
        
        if (totalValues > 0) {
            const nullPercentage = ((nullCount / totalValues) * 100).toFixed(1);
            console.log(`📈 Data quality: ${nullCount}/${totalValues} null values (${nullPercentage}%)`);
        }
        
        // Check for specific data types
        const hasValidData = Object.values(data.device.components).some(component => {
            return (component.samples && Object.values(component.samples).some(s => s.value !== null)) ||
                   (component.events && Object.values(component.events).some(e => e.value !== null));
        });
        
        if (hasValidData) {
            console.log('✅ Contains valid (non-null) data values');
        } else {
            console.log('⚠️  Warning: All data values are null (UNAVAILABLE)');
        }
        
        return true;
        
    } catch (error) {
        console.log(`❌ Error validating ${path.basename(jsonPath)}: ${error.message}`);
        return false;
    }
}

// Validate all JSON files in the data directory
const dataDir = path.join(__dirname, 'src', 'data');
const jsonFiles = fs.readdirSync(dataDir).filter(file => file.endsWith('.json'));

console.log('🔍 JSON Data Validation Report');
console.log('==============================');

let allValid = true;
jsonFiles.forEach(jsonFile => {
    const jsonPath = path.join(dataDir, jsonFile);
    const isValid = validateJsonFile(jsonPath);
    if (!isValid) allValid = false;
});

console.log('\n📋 Summary');
console.log('==========');
if (allValid) {
    console.log('✅ All JSON files are properly parsed and valid');
} else {
    console.log('❌ Some JSON files have issues');
}

console.log('\n💡 Notes:');
console.log('- "UNAVAILABLE" values in XML are converted to null in JSON (this is correct)');
console.log('- The parsing script uses xml2js library with explicitArray: true');
console.log('- Data structure follows MTConnect standard with header, device, and components'); 