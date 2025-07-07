#!/usr/bin/env python3
"""
Machine Data Merger Script

This script merges all available data for each machine from both JSON and XML sources,
organizing the data by machine ID and creating a comprehensive merged dataset.
"""

import json
import os
import glob
from datetime import datetime
from collections import defaultdict
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

def get_project_root():
    """Get the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def get_data_directories():
    """Get paths to data directories"""
    project_root = get_project_root()
    return {
        'json': os.path.join(project_root, 'src', 'data', 'json'),
        'xml': os.path.join(project_root, 'src', 'data', 'xml'),
        'combined': os.path.join(project_root, 'src', 'data', 'combined')
    }

def ensure_directory(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)

def parse_machine_id_from_filename(filename):
    """Extract machine ID from filename"""
    # Remove extension
    base_name = os.path.splitext(filename)[0]
    
    # Extract machine ID (e.g., mazak-1-vtc-200, mazak-2-vtc-300, etc.)
    parts = base_name.split('_')
    if len(parts) >= 3:
        # Combine first parts to get machine ID
        machine_id = '_'.join(parts[:-2])  # Remove timestamp and data type
        return machine_id
    return None

def get_data_type_from_filename(filename):
    """Extract data type (current/sample) from filename"""
    base_name = os.path.splitext(filename)[0]
    parts = base_name.split('_')
    if len(parts) >= 2:
        return parts[-2]  # Second to last part
    return None

def get_timestamp_from_filename(filename):
    """Extract timestamp from filename"""
    base_name = os.path.splitext(filename)[0]
    parts = base_name.split('_')
    if len(parts) >= 1:
        return parts[-1]  # Last part
    return None

def load_json_file(filepath):
    """Load and parse JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {e}")
        return None

def strip_ns(tag):
    """Remove namespace from XML tag"""
    return tag.split('}', 1)[-1] if '}' in tag else tag

def parse_xml_file(filepath):
    """Parse XML file and convert to JSON-like structure"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        def element_to_dict(element):
            """Convert XML element to dictionary"""
            result = {}
            
            # Handle attributes
            if element.attrib:
                result['attributes'] = element.attrib
            
            # Handle text content
            if element.text and element.text.strip():
                result['text'] = element.text.strip()
            
            # Handle child elements
            children = {}
            for child in element:
                tag = strip_ns(child.tag)
                child_data = element_to_dict(child)
                
                if tag in children:
                    if isinstance(children[tag], list):
                        children[tag].append(child_data)
                    else:
                        children[tag] = [children[tag], child_data]
                else:
                    children[tag] = child_data
            
            if children:
                result.update(children)
            
            return result
        
        return element_to_dict(root)
    
    except Exception as e:
        print(f"Error parsing XML file {filepath}: {e}")
        return None

def merge_samples(existing_samples, new_samples):
    """Merge sample data, handling duplicates by timestamp and sequence"""
    if not existing_samples:
        return new_samples
    
    merged = existing_samples.copy()
    
    for sample_name, sample_data in new_samples.items():
        if sample_name not in merged:
            # Ensure sample_data is always a list
            if isinstance(sample_data, list):
                merged[sample_name] = sample_data
            else:
                merged[sample_name] = [sample_data]
        else:
            # Handle existing sample - merge if it's a list or single item
            existing = merged[sample_name]
            
            # Ensure existing is a list
            if not isinstance(existing, list):
                existing = [existing]
                merged[sample_name] = existing
            
            # Ensure new sample_data is a list
            if isinstance(sample_data, list):
                merged[sample_name] = existing + sample_data
            else:
                merged[sample_name] = existing + [sample_data]
    
    return merged

def merge_events(existing_events, new_events):
    """Merge event data, handling duplicates by timestamp and sequence"""
    if not existing_events:
        return new_events
    
    merged = existing_events.copy()
    
    for event_name, event_data in new_events.items():
        if event_name not in merged:
            # Ensure event_data is always a list
            if isinstance(event_data, list):
                merged[event_name] = event_data
            else:
                merged[event_name] = [event_data]
        else:
            # Handle existing event - merge if it's a list or single item
            existing = merged[event_name]
            
            # Ensure existing is a list
            if not isinstance(existing, list):
                existing = [existing]
                merged[event_name] = existing
            
            # Ensure new event_data is a list
            if isinstance(event_data, list):
                merged[event_name] = existing + event_data
            else:
                merged[event_name] = existing + [event_data]
    
    return merged

def merge_conditions(existing_conditions, new_conditions):
    """Merge condition data"""
    if not existing_conditions:
        return new_conditions
    
    merged = existing_conditions.copy()
    
    for condition_name, condition_data in new_conditions.items():
        if condition_name not in merged:
            merged[condition_name] = condition_data
        else:
            # For conditions, we might want to keep the most recent one
            # This is a simplified approach - you might want more sophisticated logic
            merged[condition_name] = condition_data
    
    return merged

def merge_components(existing_components, new_components):
    """Merge component data"""
    if not existing_components:
        return new_components
    
    merged = existing_components.copy()
    
    for component_name, component_data in new_components.items():
        if component_name not in merged:
            merged[component_name] = component_data
        else:
            # Merge existing component
            existing = merged[component_name]
            
            # Merge samples
            if 'samples' in component_data and 'samples' in existing:
                existing['samples'] = merge_samples(existing['samples'], component_data['samples'])
            elif 'samples' in component_data:
                existing['samples'] = component_data['samples']
            
            # Merge events
            if 'events' in component_data and 'events' in existing:
                existing['events'] = merge_events(existing['events'], component_data['events'])
            elif 'events' in component_data:
                existing['events'] = component_data['events']
            
            # Merge conditions
            if 'conditions' in component_data and 'conditions' in existing:
                existing['conditions'] = merge_conditions(existing['conditions'], component_data['conditions'])
            elif 'conditions' in component_data:
                existing['conditions'] = component_data['conditions']
            
            # Update other fields if they exist
            for key in ['type', 'name']:
                if key in component_data:
                    existing[key] = component_data[key]
    
    return merged

def merge_machine_data(existing_data, new_data):
    """Merge data for a single machine"""
    if not existing_data:
        return new_data
    
    merged = existing_data.copy()
    
    # Merge device components
    if 'device' in new_data and 'device' in merged:
        if 'components' in new_data['device'] and 'components' in merged['device']:
            merged['device']['components'] = merge_components(merged['device']['components'], new_data['device']['components'])
        elif 'components' in new_data['device']:
            merged['device']['components'] = new_data['device']['components']
    elif 'device' in new_data:
        merged['device'] = new_data['device']
    
    # Handle direct components (if not nested in device)
    if 'components' in new_data and 'components' in merged:
        merged['components'] = merge_components(merged['components'], new_data['components'])
    elif 'components' in new_data:
        merged['components'] = new_data['components']
    
    # Update header if available
    if 'header' in new_data:
        merged['header'] = new_data['header']
    
    return merged

def collect_machine_files():
    """Collect all files organized by machine ID"""
    dirs = get_data_directories()
    machine_files = defaultdict(lambda: {'json': [], 'xml': []})
    
    # Collect JSON files
    json_pattern = os.path.join(dirs['json'], '*.json')
    for filepath in glob.glob(json_pattern):
        filename = os.path.basename(filepath)
        machine_id = parse_machine_id_from_filename(filename)
        if machine_id:
            machine_files[machine_id]['json'].append({
                'filepath': filepath,
                'filename': filename,
                'data_type': get_data_type_from_filename(filename),
                'timestamp': get_timestamp_from_filename(filename)
            })
    
    # Collect XML files
    xml_pattern = os.path.join(dirs['xml'], '*.xml')
    for filepath in glob.glob(xml_pattern):
        filename = os.path.basename(filepath)
        machine_id = parse_machine_id_from_filename(filename)
        if machine_id:
            machine_files[machine_id]['xml'].append({
                'filepath': filepath,
                'filename': filename,
                'data_type': get_data_type_from_filename(filename),
                'timestamp': get_timestamp_from_filename(filename)
            })
    
    return machine_files

def process_machine_data(machine_id, files_info):
    """Process and merge all data for a single machine"""
    merged_data = None
    data_sources = []
    
    # Process JSON files
    for file_info in files_info['json']:
        data = load_json_file(file_info['filepath'])
        if data:
            merged_data = merge_machine_data(merged_data, data)
            data_sources.append({
                'source_type': 'json',
                'source_file': file_info['filename'],
                'data_type': file_info['data_type'],
                'timestamp': file_info['timestamp']
            })
    
    # Process XML files
    for file_info in files_info['xml']:
        data = parse_xml_file(file_info['filepath'])
        if data:
            # Convert XML structure to match JSON structure
            converted_data = convert_xml_to_json_structure(data)
            merged_data = merge_machine_data(merged_data, converted_data)
            data_sources.append({
                'source_type': 'xml',
                'source_file': file_info['filename'],
                'data_type': file_info['data_type'],
                'timestamp': file_info['timestamp']
            })
    
    # If we have merged data, ensure it has the proper structure
    if merged_data:
        # Ensure we have the device structure
        if 'device' not in merged_data:
            merged_data['device'] = {
                'name': 'Mazak',
                'uuid': 'Mazak',
                'components': {}
            }
        
        # Ensure we have components
        if 'components' not in merged_data['device']:
            merged_data['device']['components'] = {}
    
    return merged_data, data_sources

def convert_xml_to_json_structure(xml_data):
    """Convert XML structure to match JSON structure"""
    result = {
        'header': {},
        'device': {
            'name': 'Mazak',
            'uuid': 'Mazak',
            'components': {}
        }
    }
    
    # Navigate through the XML structure to find components
    if 'MTConnectStreams' in xml_data:
        streams = xml_data['MTConnectStreams']
        if 'DeviceStream' in streams:
            device_stream = streams['DeviceStream']
            if 'Device' in device_stream:
                device = device_stream['Device']
                
                # Extract components
                if 'Components' in device:
                    components = device['Components']
                    for component_name, component_data in components.items():
                        # Convert component data to the expected format
                        converted_component = {
                            'type': component_data.get('type', 'Unknown'),
                            'name': component_data.get('name', component_name)
                        }
                        
                        # Handle samples
                        if 'Samples' in component_data:
                            converted_component['samples'] = {}
                            samples = component_data['Samples']
                            for sample_name, sample_data in samples.items():
                                if isinstance(sample_data, list):
                                    converted_component['samples'][sample_name] = sample_data
                                else:
                                    converted_component['samples'][sample_name] = [sample_data]
                        
                        # Handle events
                        if 'Events' in component_data:
                            converted_component['events'] = {}
                            events = component_data['Events']
                            for event_name, event_data in events.items():
                                if isinstance(event_data, list):
                                    converted_component['events'][event_name] = event_data
                                else:
                                    converted_component['events'][event_name] = [event_data]
                        
                        # Handle conditions
                        if 'Conditions' in component_data:
                            converted_component['conditions'] = {}
                            conditions = component_data['Conditions']
                            for condition_name, condition_data in conditions.items():
                                converted_component['conditions'][condition_name] = condition_data
                        
                        result['device']['components'][component_name] = converted_component
    
    return result

def count_data_items(data):
    """Count samples, events, and components in the data"""
    total_samples = 0
    total_events = 0
    total_components = 0
    
    # Check for components in the root level
    if 'components' in data:
        total_components = len(data['components'])
        for component in data['components'].values():
            if 'samples' in component:
                for sample_list in component['samples'].values():
                    if isinstance(sample_list, list):
                        total_samples += len(sample_list)
                    else:
                        total_samples += 1
            if 'events' in component:
                for event_list in component['events'].values():
                    if isinstance(event_list, list):
                        total_events += len(event_list)
                    else:
                        total_events += 1
    
    # Check for components nested under device
    if 'device' in data and 'components' in data['device']:
        total_components = len(data['device']['components'])
        for component in data['device']['components'].values():
            if 'samples' in component:
                for sample_list in component['samples'].values():
                    if isinstance(sample_list, list):
                        total_samples += len(sample_list)
                    else:
                        total_samples += 1
            if 'events' in component:
                for event_list in component['events'].values():
                    if isinstance(event_list, list):
                        total_events += len(event_list)
                    else:
                        total_events += 1
    
    return total_samples, total_events, total_components

def generate_summary_report(machines_data, output_file):
    """Generate a summary report"""
    timestamp = datetime.now().isoformat()
    
    report_lines = [
        "=" * 60,
        "INDIVIDUAL MACHINE DATA MERGE SUMMARY REPORT",
        "=" * 60,
        f"Generated at: {timestamp}",
        f"Total machines processed: {len(machines_data)}",
        "",
        "MACHINES:",
        "-" * 20
    ]
    
    total_json_files = 0
    total_xml_files = 0
    
    for machine_id, machine_info in machines_data.items():
        data_sources = machine_info['data_sources']
        json_count = len([ds for ds in data_sources if ds['source_type'] == 'json'])
        xml_count = len([ds for ds in data_sources if ds['source_type'] == 'xml'])
        total_json_files += json_count
        total_xml_files += xml_count
        
        samples, events, components = count_data_items(machine_info['data'])
        output_filename = os.path.basename(machine_info['output_file'])
        
        report_lines.extend([
            f"Machine: {machine_id}",
            f"  Output file: {output_filename}",
            f"  Data sources: {len(data_sources)} (JSON: {json_count}, XML: {xml_count})",
            f"  Components: {components}",
            f"  Total samples: {samples}",
            f"  Total events: {events}",
            ""
        ])
    
    report_lines.extend([
        f"TOTALS:",
        "-" * 20,
        f"Total JSON files processed: {total_json_files}",
        f"Total XML files processed: {total_xml_files}",
        f"Total individual machine files created: {len(machines_data)}",
        "",
        "SOURCE FILES:",
        "-" * 20
    ])
    
    all_files = []
    for machine_info in machines_data.values():
        for source in machine_info['data_sources']:
            all_files.append(source['source_file'])
    
    for filename in sorted(set(all_files)):  # Remove duplicates
        report_lines.append(f"  {filename}")
    
    report_content = "\n".join(report_lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_content

def main():
    """Main function to merge machine data"""
    print("Starting machine data merge process...")
    
    # Get data directories
    dirs = get_data_directories()
    ensure_directory(dirs['combined'])
    
    # Collect all machine files
    machine_files = collect_machine_files()
    
    if not machine_files:
        print("No machine files found!")
        return
    
    print(f"Found data for {len(machine_files)} machines:")
    for machine_id in machine_files.keys():
        print(f"  - {machine_id}")
    
    # Process each machine and save individually
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    machines_data = {}
    
    for machine_id, files_info in machine_files.items():
        print(f"\nProcessing machine: {machine_id}")
        print(f"  JSON files: {len(files_info['json'])}")
        print(f"  XML files: {len(files_info['xml'])}")
        
        merged_data, data_sources = process_machine_data(machine_id, files_info)
        
        if merged_data:
            # Create individual machine output structure
            machine_output = {
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'machine_id': machine_id,
                    'total_json_files': len([ds for ds in data_sources if ds['source_type'] == 'json']),
                    'total_xml_files': len([ds for ds in data_sources if ds['source_type'] == 'xml']),
                    'data_sources': data_sources
                },
                'data': merged_data
            }
            
            # Save individual machine file
            safe_machine_id = machine_id.replace('-', '_').replace(' ', '_')
            output_file = os.path.join(dirs['combined'], f'{safe_machine_id}_merged_{timestamp}.json')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(machine_output, f, indent=2, ensure_ascii=False)
            
            machines_data[machine_id] = {
                'machine_id': machine_id,
                'data_sources': data_sources,
                'data': merged_data,
                'output_file': output_file
            }
            
            print(f"  ✓ Successfully merged data")
            print(f"  ✓ Saved to: {output_file}")
        else:
            print(f"  ✗ Failed to merge data")
    
    if not machines_data:
        print("No data was successfully merged!")
        return
    
    # Generate summary report
    summary_file = os.path.join(dirs['combined'], f'machine_merge_summary_{timestamp}.txt')
    summary_content = generate_summary_report(machines_data, summary_file)
    
    print(f"\nSummary report saved to: {summary_file}")
    print(f"\nSuccessfully created {len(machines_data)} individual machine files:")
    for machine_id, machine_info in machines_data.items():
        print(f"  - {machine_id}: {os.path.basename(machine_info['output_file'])}")
    
    print("\n" + summary_content)

if __name__ == "__main__":
    main() 