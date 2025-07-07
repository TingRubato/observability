import requests
import xml.etree.ElementTree as ET
import json
import sys
import os
from datetime import datetime
from collections import defaultdict

def load_endpoints_config():
    """Load endpoints configuration from endpoints.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'endpoints.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: endpoints.json not found at {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in endpoints.json: {e}")
        return None

def ensure_data_json_directory():
    """Ensure the data/json directory exists"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_json_dir = os.path.join(project_root, 'src','data', 'json')
    os.makedirs(data_json_dir, exist_ok=True)
    return data_json_dir

def ensure_data_xml_directory():
    """Ensure the data/xml directory exists"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_xml_dir = os.path.join(project_root, 'src','data', 'xml')
    os.makedirs(data_xml_dir, exist_ok=True)
    return data_xml_dir

def get_available_machines_and_endpoints():
    """Get list of available machines and endpoints for help text"""
    config = load_endpoints_config()
    if not config:
        return [], []
    
    machines = list(config['mazak_machines'].keys())
    endpoint_types = list(config['endpoint_types'].keys())
    return machines, endpoint_types

def build_url(machine_key, endpoint_type):
    """Build URL from machine key and endpoint type"""
    config = load_endpoints_config()
    if not config:
        return None
    
    if machine_key not in config['mazak_machines']:
        print(f"Error: Machine '{machine_key}' not found in configuration")
        return None
    
    if endpoint_type not in config['endpoint_types']:
        print(f"Error: Endpoint type '{endpoint_type}' not found in configuration")
        return None
    
    machine = config['mazak_machines'][machine_key]
    base_url = machine['base_url']
    endpoint_path = machine['endpoints'][endpoint_type]
    
    return f"{base_url}{endpoint_path}"

def display_menu():
    """Display interactive menu and get user selection"""
    config = load_endpoints_config()
    if not config:
        print("Error: Could not load endpoints configuration")
        return None, None, None
    
    machines = list(config['mazak_machines'].keys())
    endpoint_types = list(config['endpoint_types'].keys())
    
    print("\n" + "="*60)
    print("           MAZAK MACHINE DATA COLLECTOR")
    print("="*60)
    
    # Display available machines
    print("\nAvailable Machines:")
    print("-" * 30)
    for i, machine_key in enumerate(machines, 1):
        machine_info = config['mazak_machines'][machine_key]
        print(f"{i:2d}. {machine_info['name']} ({machine_key})")
    
    # Display available endpoints
    print("\nAvailable Endpoint Types:")
    print("-" * 30)
    for i, endpoint_key in enumerate(endpoint_types, 1):
        endpoint_desc = config['endpoint_types'][endpoint_key]
        print(f"{i:2d}. {endpoint_desc} ({endpoint_key})")
    
    print("\nOptions:")
    print("-" * 30)
    print(f"{len(machines) + len(endpoint_types) + 1:2d}. Use direct URL")
    print(f"{len(machines) + len(endpoint_types) + 2:2d}. Exit")
    
    # Get user selection
    while True:
        try:
            choice = input(f"\nSelect an option (1-{len(machines) + len(endpoint_types) + 2}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(machines):
                # Machine selected
                selected_machine = machines[choice_num - 1]
                print(f"\nSelected machine: {config['mazak_machines'][selected_machine]['name']}")
                
                # Get endpoint selection
                print("\nSelect endpoint type:")
                for i, endpoint_key in enumerate(endpoint_types, 1):
                    endpoint_desc = config['endpoint_types'][endpoint_key]
                    print(f"{i:2d}. {endpoint_desc} ({endpoint_key})")
                
                while True:
                    endpoint_choice = input(f"Select endpoint (1-{len(endpoint_types)}): ").strip()
                    endpoint_num = int(endpoint_choice)
                    
                    if 1 <= endpoint_num <= len(endpoint_types):
                        selected_endpoint = endpoint_types[endpoint_num - 1]
                        return selected_machine, selected_endpoint, None
                    else:
                        print(f"Please enter a number between 1 and {len(endpoint_types)}")
            
            elif len(machines) + 1 <= choice_num <= len(machines) + len(endpoint_types):
                # Endpoint selected (for direct URL option)
                selected_endpoint = endpoint_types[choice_num - len(machines) - 1]
                print(f"\nSelected endpoint: {config['endpoint_types'][selected_endpoint]}")
                
                # Get machine selection
                print("\nSelect machine:")
                for i, machine_key in enumerate(machines, 1):
                    machine_info = config['mazak_machines'][machine_key]
                    print(f"{i:2d}. {machine_info['name']} ({machine_key})")
                
                while True:
                    machine_choice = input(f"Select machine (1-{len(machines)}): ").strip()
                    machine_num = int(machine_choice)
                    
                    if 1 <= machine_num <= len(machines):
                        selected_machine = machines[machine_num - 1]
                        return selected_machine, selected_endpoint, None
                    else:
                        print(f"Please enter a number between 1 and {len(machines)}")
            
            elif choice_num == len(machines) + len(endpoint_types) + 1:
                # Direct URL option
                url = input("Enter the direct URL: ").strip()
                if url:
                    return None, None, url
                else:
                    print("Please enter a valid URL")
            
            elif choice_num == len(machines) + len(endpoint_types) + 2:
                # Exit option
                print("Goodbye!")
                return None, None, None
            
            else:
                print(f"Please enter a number between 1 and {len(machines) + len(endpoint_types) + 2}")
        
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            return None, None, None

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
        print(f"DEBUG: Starting XML to JSON conversion. XML string length: {len(xml_string)}")
        print(f"DEBUG: First 200 characters of XML: {xml_string[:200]}")
        
        root = ET.fromstring(xml_string)
        print(f"DEBUG: Successfully parsed XML root. Root tag: {root.tag}")
        
        # Extract header
        header_elem = root.find('.//Header')
        print(f"DEBUG: Header element found: {header_elem is not None}")
        header = extract_attributes(header_elem) if header_elem is not None else {}
        
        # Extract device stream - try different namespace patterns
        device_stream_elem = None
        namespace_patterns = [
            './/DeviceStream',
            './/{*}DeviceStream',
            './/{urn:mtconnect.org:MTConnectStreams:1.5}DeviceStream'
        ]
        
        for pattern in namespace_patterns:
            device_stream_elem = root.find(pattern)
            if device_stream_elem is not None:
                print(f"DEBUG: DeviceStream found using pattern: {pattern}")
                break
        
        print(f"DEBUG: DeviceStream element found: {device_stream_elem is not None}")
        if device_stream_elem is None:
            # Try to find any element that might be a device stream
            all_elements = root.findall('.//*')
            device_candidates = [elem for elem in all_elements if 'Device' in elem.tag or 'device' in elem.tag.lower()]
            print(f"DEBUG: Found {len(device_candidates)} potential device elements")
            for i, candidate in enumerate(device_candidates):
                print(f"DEBUG: Device candidate {i+1}: {candidate.tag}")
            
            # If still no device stream, try to process the root as if it contains the data
            print("DEBUG: No DeviceStream found, attempting to process root element")
            device_stream_elem = root
        
        device_attrs = extract_attributes(device_stream_elem)
        print(f"DEBUG: Device attributes: {device_attrs}")
        device = {
            'name': device_attrs.get('name', 'Unknown'),
            'uuid': device_attrs.get('uuid', 'Unknown'),
            'components': {}
        }
        
        # Process component streams with deduplication - try different patterns
        component_streams = []
        component_patterns = [
            './/ComponentStream',
            './/{*}ComponentStream',
            './/{urn:mtconnect.org:MTConnectStreams:1.5}ComponentStream'
        ]
        
        for pattern in component_patterns:
            component_streams = device_stream_elem.findall(pattern)
            if component_streams:
                print(f"DEBUG: ComponentStreams found using pattern: {pattern}")
                break
        
        # If no component streams found, try to find any elements that might be components
        if not component_streams:
            all_elements = device_stream_elem.findall('.//*')
            component_candidates = [elem for elem in all_elements if 'Component' in elem.tag or 'component' in elem.tag.lower()]
            print(f"DEBUG: Found {len(component_candidates)} potential component elements")
            if component_candidates:
                component_streams = component_candidates
        
        print(f"DEBUG: Found {len(component_streams)} component streams")
        if component_streams:
            # Convert to list of dictionaries for processing
            components_list = []
            for i, comp in enumerate(component_streams):
                print(f"DEBUG: Processing component {i+1}/{len(component_streams)}")
                comp_dict = {'@attributes': extract_attributes(comp)}
                
                # Process samples - try different patterns
                samples_elem = None
                sample_patterns = ['Samples', '{*}Samples', '{urn:mtconnect.org:MTConnectStreams:1.5}Samples']
                for pattern in sample_patterns:
                    samples_elem = comp.find(pattern)
                    if samples_elem is not None:
                        break
                
                print(f"DEBUG: Component {i+1} - Samples element found: {samples_elem is not None}")
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
                
                # Process events - try different patterns
                events_elem = None
                event_patterns = ['Events', '{*}Events', '{urn:mtconnect.org:MTConnectStreams:1.5}Events']
                for pattern in event_patterns:
                    events_elem = comp.find(pattern)
                    if events_elem is not None:
                        break
                
                print(f"DEBUG: Component {i+1} - Events element found: {events_elem is not None}")
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
                
                # Process conditions - try different patterns
                condition_elem = None
                condition_patterns = ['Condition', '{*}Condition', '{urn:mtconnect.org:MTConnectStreams:1.5}Condition']
                for pattern in condition_patterns:
                    condition_elem = comp.find(pattern)
                    if condition_elem is not None:
                        break
                
                print(f"DEBUG: Component {i+1} - Condition element found: {condition_elem is not None}")
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
            
            print(f"DEBUG: About to call transform_components_deduplicated with {len(components_list)} components")
            device['components'] = transform_components_deduplicated(components_list)
            print(f"DEBUG: Successfully transformed components")
        
        # Build final structure
        result = {
            'header': header,
            'device': device
        }
        
        print(f"DEBUG: About to convert result to JSON")
        json_result = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        print(f"DEBUG: Successfully converted to JSON. Result length: {len(json_result)}")
        return json_result
        
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None
    except Exception as e:
        print(f"Error converting XML to JSON: {e}")
        print(f"DEBUG: Exception type: {type(e).__name__}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return None
        
def main():
    # Display interactive menu and get user selection
    machine, endpoint, direct_url = display_menu()
    
    # If user chose to exit
    if machine is None and endpoint is None and direct_url is None:
        return
    
    # Ensure data directories exist
    data_json_dir = ensure_data_json_directory()
    data_xml_dir = ensure_data_xml_directory()
    
    # Determine URL and output filename
    if direct_url:
        url = direct_url
        print(f"Using direct URL: {url}")
        # For direct URLs, use timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"direct_url_{timestamp}.json"
        output_json_file = os.path.join(data_json_dir, filename)
    elif machine and endpoint:
        url = build_url(machine, endpoint)
        if not url:
            sys.exit(1)
        
        config = load_endpoints_config()
        if config:
            machine_name = config['mazak_machines'][machine]['name']
            endpoint_desc = config['endpoint_types'][endpoint]
            print(f"Fetching {endpoint_desc} from {machine_name}...")
            
            # Generate unique filename based on machine and endpoint
            machine_safe = machine.replace('_', '-')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{machine_safe}_{endpoint}_{timestamp}.json"
            output_json_file = os.path.join(data_json_dir, filename)
        else:
            print(f"Fetching data from {url}...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unknown_machine_{timestamp}.json"
            output_json_file = os.path.join(data_json_dir, filename)
    else:
        print("Error: Invalid selection")
        sys.exit(1)
    
    print(f"Fetching XML data from {url}...")
    xml_data = fetch_xml_from_url(url)

    if xml_data is None:
        print("Failed to fetch XML data")
        sys.exit(1)
    
    # Save XML data to file
    try:
        # Change .json extension to .xml for XML files
        xml_filename = filename.replace('.json', '.xml')
        output_xml_file = os.path.join(data_xml_dir, xml_filename)
        
        with open(output_xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_data)
        print(f"XML data saved to {output_xml_file}")
    except IOError as e:
        print(f"Warning: Could not save XML to file: {e}")

    print("Converting XML to JSON with deduplication...")
    json_data = convert_xml_to_json_deduplicated(xml_data)
    
    if json_data is None:
        print("Failed to convert XML to JSON")
        sys.exit(1)
    
    # Output to stdout
    # print(json_data)

    # Save JSON data to file
    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
        print(f"JSON data saved to {output_json_file}")
    except IOError as e:
        print(f"Warning: Could not save JSON to file: {e}")

if __name__ == "__main__":
    main() 