import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseString } from 'xml2js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper function to convert string values to appropriate types
function convertValue(value) {
  if (value === 'UNAVAILABLE') return null;
  if (value === undefined || value === '') return null;
  
  // Try to convert to number
  const num = Number(value);
  if (!isNaN(num) && isFinite(num)) return num;
  
  return value;
}

// Helper function to extract attributes and convert them
function extractAttributes(xmlNode) {
  const attrs = xmlNode.$ || {};
  const result = {};
  
  for (const [key, value] of Object.entries(attrs)) {
    if (key.startsWith('xmlns') || key === 'xsi:schemaLocation') continue;
    result[key] = convertValue(value);
  }
  
  return result;
}

// Helper function to parse ISO timestamp
function parseTimestamp(timestampStr) {
  if (!timestampStr) return null;
  try {
    return new Date(timestampStr);
  } catch (e) {
    return null;
  }
}

// Transform component data items with deduplication (keep only latest)
function transformDataItemsDeduplicated(items, itemType) {
  const result = {};
  const groupedItems = new Map(); // dataItemId -> array of items
  
  if (!items || !Array.isArray(items)) return result;
  
  // First pass: group items by dataItemId
  items.forEach(itemGroup => {
    Object.keys(itemGroup).forEach(itemName => {
      if (itemName === '$') return;
      
      const itemArray = Array.isArray(itemGroup[itemName]) ? itemGroup[itemName] : [itemGroup[itemName]];
      
      itemArray.forEach(item => {
        const attrs = extractAttributes(item);
        const dataItemId = attrs.dataItemId;
        
        if (!dataItemId) return;
        
        // Parse timestamp for comparison
        const timestamp = parseTimestamp(attrs.timestamp);
        if (!timestamp) return; // Skip items without valid timestamp
        
        if (!groupedItems.has(dataItemId)) {
          groupedItems.set(dataItemId, []);
        }
        
        groupedItems.get(dataItemId).push({
          item,
          attrs,
          timestamp,
          itemName
        });
      });
    });
  });
  
  // Second pass: for each dataItemId, keep only the item with the latest timestamp
  for (const [dataItemId, itemList] of groupedItems) {
    if (itemList.length === 0) continue;
    
    // Sort by timestamp (most recent first) and take the first one
    itemList.sort((a, b) => b.timestamp - a.timestamp);
    const latest = itemList[0];
    
    const transformedItem = {
      timestamp: latest.attrs.timestamp,
      sequence: latest.attrs.sequence
    };
    
    // Add type-specific fields
    if (itemType === 'conditions') {
      transformedItem.state = latest.itemName;
      transformedItem.category = latest.attrs.type;
    } else {
      transformedItem.value = convertValue(latest.item._ || latest.item);
      if (latest.attrs.subType) transformedItem.subType = latest.attrs.subType;
      if (latest.attrs.compositionId) transformedItem.compositionId = latest.attrs.compositionId;
      if (latest.attrs.assetType !== undefined) transformedItem.assetType = latest.attrs.assetType;
      if (latest.attrs.count !== undefined) transformedItem.count = convertValue(latest.attrs.count);
    }
    
    result[dataItemId] = transformedItem;
  }
  
  return result;
}

// Transform component streams with deduplication
function transformComponentsDeduplicated(componentStreams) {
  const components = {};
  
  if (!Array.isArray(componentStreams)) return components;
  
  componentStreams.forEach(component => {
    const attrs = extractAttributes(component);
    const componentId = attrs.componentId;
    
    if (!componentId) return;
    
    const transformedComponent = {
      type: attrs.component,
      name: attrs.name
    };
    
    // Transform samples with deduplication
    if (component.Samples) {
      transformedComponent.samples = transformDataItemsDeduplicated(component.Samples, 'samples');
    }
    
    // Transform events with deduplication
    if (component.Events) {
      transformedComponent.events = transformDataItemsDeduplicated(component.Events, 'events');
    }
    
    // Transform conditions with deduplication
    if (component.Condition) {
      transformedComponent.conditions = transformDataItemsDeduplicated(component.Condition, 'conditions');
    }
    
    components[componentId] = transformedComponent;
  });
  
  return components;
}

// Main conversion function with deduplication
export async function convertXmlToJsonDeduplicated(xmlFile, jsonFile) {
  return new Promise((resolve, reject) => {
    fs.readFile(xmlFile, 'utf8', (err, xmlData) => {
      if (err) {
        reject(new Error(`Error reading XML file: ${err.message}`));
        return;
      }
      
      parseString(xmlData, { explicitArray: true }, (err, result) => {
        if (err) {
          reject(new Error(`Error parsing XML: ${err.message}`));
          return;
        }
        
        try {
          const mtconnectStreams = result.MTConnectStreams;
          const header = mtconnectStreams.Header[0];
          const deviceStream = mtconnectStreams.Streams[0].DeviceStream[0];
          
          // Transform header
          const transformedHeader = extractAttributes(header);
          
          // Transform device with deduplication
          const deviceAttrs = extractAttributes(deviceStream);
          const transformedDevice = {
            name: deviceAttrs.name,
            uuid: deviceAttrs.uuid,
            components: transformComponentsDeduplicated(deviceStream.ComponentStream)
          };
          
          // Extract metadata
          const rootAttrs = extractAttributes(mtconnectStreams);
          const metadata = {
            schema: rootAttrs.xmlns || 'urn:mtconnect.org:MTConnectStreams:1.5',
            schemaLocation: mtconnectStreams.$['xsi:schemaLocation'] || 'http://schemas.mtconnect.org/schemas/MTConnectStreams_1.5.xsd'
          };
          
          // Build final structure
          const transformedData = {
            header: transformedHeader,
            device: transformedDevice,
            metadata: metadata
          };
          
          fs.writeFile(jsonFile, JSON.stringify(transformedData, null, 2), (err) => {
            if (err) {
              reject(new Error(`Error writing JSON file: ${err.message}`));
              return;
            }
            
            // Calculate statistics
            const stats = {
              file: jsonFile,
              components: Object.keys(transformedDevice.components).length,
              totalDataItems: Object.values(transformedDevice.components).reduce((sum, comp) => {
                return sum + 
                  (comp.samples ? Object.keys(comp.samples).length : 0) +
                  (comp.events ? Object.keys(comp.events).length : 0) +
                  (comp.conditions ? Object.keys(comp.conditions).length : 0);
              }, 0)
            };
            
            resolve(stats);
          });
          
        } catch (transformError) {
          reject(new Error(`Error transforming XML data: ${transformError.message}`));
        }
      });
    });
  });
}

// CLI execution - only run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  // --- Argument parsing ---
  const args = process.argv.slice(2);
  let xmlFile, jsonFile;

  if (args.includes('--help') || args.includes('-h')) {
    console.log('Usage: node offload-xml-to-json-deduplicated.js [input.xml] [output.json]');
    console.log('Defaults: input = ../data/vtc300c.xml, output = ../data/vtc300c_deduplicated.json');
    console.log('This version deduplicates data items and keeps only the most recent value for each dataItemId.');
    process.exit(0);
  }

  xmlFile = args[0] ? path.resolve(__dirname, args[0]) : path.join(__dirname, '../data/vtc300c.xml');
  jsonFile = args[1] ? path.resolve(__dirname, args[1]) : path.join(__dirname, '../data/vtc300c_deduplicated.json');

  // Execute conversion
  convertXmlToJsonDeduplicated(xmlFile, jsonFile)
    .then(stats => {
      console.log('Successfully converted XML to deduplicated JSON:', stats.file);
      console.log(`- Components: ${stats.components}`);
      console.log(`- Total unique data items: ${stats.totalDataItems}`);
      console.log('Note: Only the most recent value for each dataItemId is included.');
    })
    .catch(error => {
      console.error('Error:', error.message);
      process.exit(1);
    });
} 