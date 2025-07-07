import requests
import xml.etree.ElementTree as ET
import json
import sys
from datetime import datetime
from collections import defaultdict

def fetch_xml_from_url(url):
    """Fetch XML data from the specified URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching XML from {url}: {e}")
        return None

def strip_ns(tag):
    """Remove namespace from XML tag"""
    return tag.split('}', 1)[-1] if '}' in tag else tag

def parse_iso(ts):
    """Parse ISO timestamp with proper handling of microseconds and timezone"""
    ts = ts.replace('Z', '+00:00')
    if '.' in ts:
        date_part, rest = ts.split('.', 1)
        micro, *tz = rest.split('+')
        if len(micro) < 6:
            micro = micro.ljust(6, '0')
        tz_str = '+' + tz[0] if tz else ''
        ts = f"{date_part}.{micro}{tz_str}"
    return datetime.fromisoformat(ts)

def convert_value(value):
    """Convert string values to appropriate types"""
    if value == 'UNAVAILABLE':
        return None
    if value is None or value == '':
        return None
    
    # Try to convert to number
    try:
        num = float(value)
        if num.is_integer():
            return int(num)
        return num
    except (ValueError, TypeError):
        return value

def extract_attributes(xml_node):
    """Extract and convert attributes from XML node"""
    attrs = xml_node.attrib or {}
    result = {}
    
    for key, value in attrs.items():
        if key.startswith('xmlns') or key == 'xsi:schemaLocation':
            continue
        result[key] = convert_value(value)
    
    return result

def deduplicate_data_items(items, item_type):
    """
    Process data items and keep only the most recent value for each dataItemId.
    Returns a dictionary with dataItemId as key and the latest item as value.
    """
    # Group items by dataItemId
    grouped_items = defaultdict(list)
    
    if not items:
        return {}
    
    # Handle different item structures
    if isinstance(items, dict):
        # Single item
        items = [items]
    elif not isinstance(items, list):
        return {}
    
    for item in items:
        if isinstance(item, dict):
            attrs = item.get('@attributes', {})
            data_item_id = attrs.get('dataItemId')
            
            if not data_item_id:
                continue
            
            # Parse timestamp for comparison
            timestamp_str = attrs.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = parse_iso(timestamp_str)
                    item['_parsed_timestamp'] = timestamp
                    grouped_items[data_item_id].append(item)
                except ValueError:
                    # Skip items with invalid timestamps
                    continue
    
    # For each dataItemId, keep only the item with the latest timestamp
    result = {}
    for data_item_id, item_list in grouped_items.items():
        if item_list:
            # Sort by timestamp (most recent first)
            latest_item = max(item_list, key=lambda x: x.get('_parsed_timestamp', datetime.min))
            
            # Remove the temporary timestamp field
            if '_parsed_timestamp' in latest_item:
                del latest_item['_parsed_timestamp']
            
            # Transform to the expected format
            attrs = latest_item.get('@attributes', {})
            transformed_item = {
                'timestamp': attrs.get('timestamp'),
                'sequence': attrs.get('sequence')
            }
            
            # Add type-specific fields
            if item_type == 'conditions':
                # For conditions, the tag name is the state
                tag_name = None
                for key in latest_item.keys():
                    if key not in ['@attributes', '_parsed_timestamp']:
                        tag_name = key
                        break
                transformed_item['state'] = tag_name
                transformed_item['category'] = attrs.get('type')
            else:
                # For samples and events
                transformed_item['value'] = convert_value(latest_item.get('#text'))
                if attrs.get('subType'):
                    transformed_item['subType'] = attrs.get('subType')
                if attrs.get('compositionId'):
                    transformed_item['compositionId'] = attrs.get('compositionId')
                if attrs.get('assetType') is not None:
                    transformed_item['assetType'] = attrs.get('assetType')
                if attrs.get('count') is not None:
                    transformed_item['count'] = convert_value(attrs.get('count'))
            
            result[data_item_id] = transformed_item
    
    return result

def transform_components_deduplicated(component_streams):
    """Transform component streams with deduplication"""
    components = {}
    
    if not isinstance(component_streams, list):
        return components
    
    for component in component_streams:
        attrs = component.get('@attributes', {})
        component_id = attrs.get('componentId')
        
        if not component_id:
            continue
        
        transformed_component = {
            'type': attrs.get('component'),
            'name': attrs.get('name')
        }
        
        # Transform samples with deduplication
        if 'Samples' in component:
            samples = component['Samples']
            transformed_component['samples'] = {}
            
            for sample_type, sample_data in samples.items():
                if sample_type == '@attributes':
                    continue
                
                # Handle both single items and arrays
                if isinstance(sample_data, list):
                    deduplicated = deduplicate_data_items(sample_data, 'samples')
                else:
                    deduplicated = deduplicate_data_items([sample_data], 'samples')
                
                # Merge into samples
                transformed_component['samples'].update(deduplicated)
        
        # Transform events with deduplication
        if 'Events' in component:
            events = component['Events']
            transformed_component['events'] = {}
            
            for event_type, event_data in events.items():
                if event_type == '@attributes':
                    continue
                
                # Handle both single items and arrays
                if isinstance(event_data, list):
                    deduplicated = deduplicate_data_items(event_data, 'events')
                else:
                    deduplicated = deduplicate_data_items([event_data], 'events')
                
                # Merge into events
                transformed_component['events'].update(deduplicated)
        
        # Transform conditions with deduplication
        if 'Condition' in component:
            conditions = component['Condition']
            transformed_component['conditions'] = {}
            
            for condition_type, condition_data in conditions.items():
                if condition_type == '@attributes':
                    continue
                
                # Handle both single items and arrays
                if isinstance(condition_data, list):
                    deduplicated = deduplicate_data_items(condition_data, 'conditions')
                else:
                    deduplicated = deduplicate_data_items([condition_data], 'conditions')
                
                # Merge into conditions
                transformed_component['conditions'].update(deduplicated)
        
        components[component_id] = transformed_component
    
    return components

def convert_xml_to_json_deduplicated(xml_string):
    """Convert XML string to JSON with deduplication"""
    try:
        root = ET.fromstring(xml_string)
        
        # Extract header
        header_elem = root.find('.//Header')
        header = extract_attributes(header_elem) if header_elem is not None else {}
        
        # Extract device stream
        device_stream_elem = root.find('.//DeviceStream')
        if device_stream_elem is None:
            raise ValueError("No DeviceStream found in XML")
        
        device_attrs = extract_attributes(device_stream_elem)
        device = {
            'name': device_attrs.get('name'),
            'uuid': device_attrs.get('uuid'),
            'components': {}
        }
        
        # Process component streams with deduplication
        component_streams = device_stream_elem.findall('.//ComponentStream')
        if component_streams:
            # Convert to list of dictionaries for processing
            components_list = []
            for comp in component_streams:
                comp_dict = {'@attributes': extract_attributes(comp)}
                
                # Process samples
                samples_elem = comp.find('Samples')
                if samples_elem is not None:
                    comp_dict['Samples'] = {}
                    for sample in samples_elem:
                        tag = strip_ns(sample.tag)
                        if tag not in comp_dict['Samples']:
                            comp_dict['Samples'][tag] = []
                        comp_dict['Samples'][tag].append({
                            '@attributes': extract_attributes(sample),
                            '#text': sample.text.strip() if sample.text else None
                        })
                
                # Process events
                events_elem = comp.find('Events')
                if events_elem is not None:
                    comp_dict['Events'] = {}
                    for event in events_elem:
                        tag = strip_ns(event.tag)
                        if tag not in comp_dict['Events']:
                            comp_dict['Events'][tag] = []
                        comp_dict['Events'][tag].append({
                            '@attributes': extract_attributes(event),
                            '#text': event.text.strip() if event.text else None
                        })
                
                # Process conditions
                condition_elem = comp.find('Condition')
                if condition_elem is not None:
                    comp_dict['Condition'] = {}
                    for condition in condition_elem:
                        tag = strip_ns(condition.tag)
                        if tag not in comp_dict['Condition']:
                            comp_dict['Condition'][tag] = []
                        comp_dict['Condition'][tag].append({
                            '@attributes': extract_attributes(condition),
                            '#text': condition.text.strip() if condition.text else None
                        })
                
                components_list.append(comp_dict)
            
            device['components'] = transform_components_deduplicated(components_list)
        
        # Build final structure
        result = {
            'header': header,
            'device': device
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None
    except Exception as e:
        print(f"Error converting XML to JSON: {e}")
        return None

def main():
    url = "http://192.168.100.241:5000/sample"
    
    print(f"Fetching XML data from {url}...")
    xml_data = fetch_xml_from_url(url)
    
    if xml_data is None:
        print("Failed to fetch XML data")
        sys.exit(1)
    
    print("Converting XML to JSON with deduplication...")
    json_data = convert_xml_to_json_deduplicated(xml_data)
    
    if json_data is None:
        print("Failed to convert XML to JSON")
        sys.exit(1)
    
    # Output to stdout
    print(json_data)
    
    # Save to file
    try:
        with open('output_deduplicated.json', 'w', encoding='utf-8') as f:
            f.write(json_data)
        print("\nJSON data saved to output_deduplicated.json")
    except IOError as e:
        print(f"Warning: Could not save to file: {e}")

if __name__ == "__main__":
    main() 