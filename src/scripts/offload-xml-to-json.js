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

// Transform component data items (samples, events, conditions)
function transformDataItems(items, itemType) {
  const result = {};
  
  if (!items || !Array.isArray(items)) return result;
  
  items.forEach(itemGroup => {
    Object.keys(itemGroup).forEach(itemName => {
      if (itemName === '$') return;
      
      const itemArray = Array.isArray(itemGroup[itemName]) ? itemGroup[itemName] : [itemGroup[itemName]];
      
      itemArray.forEach(item => {
        const attrs = extractAttributes(item);
        const dataItemId = attrs.dataItemId;
        
        if (!dataItemId) return;
        
        const transformedItem = {
          timestamp: attrs.timestamp,
          sequence: attrs.sequence
        };
        
        // Add type-specific fields
        if (itemType === 'conditions') {
          transformedItem.state = itemName;
          transformedItem.category = attrs.type;
        } else {
          transformedItem.value = convertValue(item._ || item);
          if (attrs.subType) transformedItem.subType = attrs.subType;
          if (attrs.compositionId) transformedItem.compositionId = attrs.compositionId;
          if (attrs.assetType !== undefined) transformedItem.assetType = attrs.assetType;
          if (attrs.count !== undefined) transformedItem.count = convertValue(attrs.count);
        }
        
        result[dataItemId] = transformedItem;
      });
    });
  });
  
  return result;
}

// Transform component streams
function transformComponents(componentStreams) {
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
    
    // Transform samples
    if (component.Samples) {
      transformedComponent.samples = transformDataItems(component.Samples, 'samples');
    }
    
    // Transform events
    if (component.Events) {
      transformedComponent.events = transformDataItems(component.Events, 'events');
    }
    
    // Transform conditions
    if (component.Condition) {
      transformedComponent.conditions = transformDataItems(component.Condition, 'conditions');
    }
    
    components[componentId] = transformedComponent;
  });
  
  return components;
}

// Main conversion function that can be called from other modules
export async function convertXmlToJson(xmlFile, jsonFile) {
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
          
          // Transform device
          const deviceAttrs = extractAttributes(deviceStream);
          const transformedDevice = {
            name: deviceAttrs.name,
            uuid: deviceAttrs.uuid,
            components: transformComponents(deviceStream.ComponentStream)
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
    console.log('Usage: node offload-xml-to-json.js [input.xml] [output.json]');
    console.log('Defaults: input = ../data/vtc300c.xml, output = ../data/vtc300c.json');
    process.exit(0);
  }

  xmlFile = args[0] ? path.resolve(__dirname, args[0]) : path.join(__dirname, '../data/vtc300c.xml');
  jsonFile = args[1] ? path.resolve(__dirname, args[1]) : path.join(__dirname, '../data/vtc300c.json');

  // Execute conversion
  convertXmlToJson(xmlFile, jsonFile)
    .then(stats => {
      console.log('Successfully converted XML to normalized JSON:', stats.file);
      console.log(`- Components: ${stats.components}`);
      console.log(`- Total data items: ${stats.totalDataItems}`);
    })
    .catch(error => {
      console.error('Error:', error.message);
      process.exit(1);
    });
}