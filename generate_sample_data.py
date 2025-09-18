#!/usr/bin/env python3
"""
Generate sample data for Mazak VTC 200 dashboard
This creates the CSV files needed for the optimized dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_data():
    """Generate sample data that matches the dashboard expectations"""
    
    # Create timestamps for the last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # Generate time series data
    time_range = pd.date_range(start=start_time, end=end_time, freq='1min')
    
    # Generate samples data
    samples_data = []
    machine_name = "mazak_1_vtc_200"
    
    # Create different components and their samples
    components = {
        'linear_x': ['Xabs', 'Xpos', 'Xload', 'Xfrt'],
        'linear_y': ['Yabs', 'Ypos', 'Yload', 'Yfrt'],
        'linear_z': ['Zabs', 'Zpos', 'Zload', 'Zfrt'],
        'spindle': ['Srpm', 'Sload', 'Stemp'],
        'controller': ['auto_time', 'cut_time', 'total_time'],
        'feedrate': ['Fovr', 'Frapidovr']
    }
    
    for ts in time_range[::5]:  # Every 5 minutes for performance
        for component_id, sample_names in components.items():
            for sample_name in sample_names:
                if sample_name in ['Xabs', 'Yabs', 'Zabs']:
                    # Position data with some movement
                    value = 100 + np.random.normal(0, 50)
                elif 'load' in sample_name.lower():
                    # Load data (0-100%)
                    value = max(0, min(100, np.random.normal(45, 15)))
                elif sample_name == 'Srpm':
                    # Spindle RPM (0-8000)
                    value = max(0, np.random.normal(2500, 800))
                elif sample_name in ['auto_time', 'cut_time', 'total_time']:
                    # Time values in seconds
                    base_time = (ts - start_time).total_seconds()
                    if sample_name == 'total_time':
                        value = base_time
                    elif sample_name == 'auto_time':
                        value = base_time * 0.7  # 70% auto time
                    else:  # cut_time
                        value = base_time * 0.4  # 40% cut time
                elif 'ovr' in sample_name.lower():
                    # Override percentages
                    value = np.random.normal(100, 5)
                else:
                    # General numeric values
                    value = np.random.normal(50, 10)
                
                # Add both current and sample data types
                for data_type in ['current', 'sample']:
                    samples_data.append({
                        'timestamp': ts.isoformat(),
                        'machine_name': machine_name,
                        'component_id': component_id,
                        'sample_name': sample_name,
                        'value': value + (np.random.normal(0, 1) if data_type == 'sample' else 0),
                        'sub_type': 'ACTUAL',
                        'data_type': data_type
                    })
    
    # Generate events data
    events_data = []
    event_types = {
        'controller': ['avail', 'mode', 'estop', 'execution'],
        'program': ['program', 'Tool_number'],
        'axis_x': ['xaxisstate'],
        'axis_y': ['yaxisstate'],
        'axis_z': ['zaxisstate']
    }
    
    for ts in time_range[::10]:  # Every 10 minutes
        for component_id, event_names in event_types.items():
            for event_name in event_names:
                if event_name == 'avail':
                    value = np.random.choice(['AVAILABLE', 'UNAVAILABLE'], p=[0.9, 0.1])
                elif event_name == 'mode':
                    value = np.random.choice(['AUTOMATIC', 'MANUAL'], p=[0.8, 0.2])
                elif event_name == 'estop':
                    value = np.random.choice(['ARMED', 'TRIGGERED'], p=[0.95, 0.05])
                elif event_name == 'execution':
                    value = np.random.choice(['EXECUTING', 'READY', 'STOPPED'], p=[0.6, 0.3, 0.1])
                elif event_name == 'program':
                    value = f'PROGRAM_{np.random.randint(1, 100):03d}'
                elif event_name == 'Tool_number':
                    value = np.random.randint(1, 20)
                else:
                    value = np.random.choice(['ACTIVE', 'INACTIVE'], p=[0.7, 0.3])
                
                for data_type in ['current', 'sample']:
                    events_data.append({
                        'timestamp': ts.isoformat(),
                        'machine_name': machine_name,
                        'component_id': component_id,
                        'event_name': event_name,
                        'value': value,
                        'data_type': data_type
                    })
    
    # Generate conditions data
    conditions_data = []
    condition_types = {
        'controller': ['system_condition'],
        'axis_x': ['x_travel'],
        'axis_y': ['y_travel'],
        'axis_z': ['z_travel'],
        'spindle': ['spindle_condition']
    }
    
    for ts in time_range[::30]:  # Every 30 minutes
        for component_id, condition_names in condition_types.items():
            for condition_name in condition_names:
                state = np.random.choice(['Normal', '#text'], p=[0.95, 0.05])
                category = np.random.choice(['SYSTEM', 'ACTUATOR', 'ANGLE'], p=[0.5, 0.3, 0.2])
                
                for data_type in ['current', 'sample']:
                    conditions_data.append({
                        'timestamp': ts.isoformat(),
                        'machine_name': machine_name,
                        'component_id': component_id,
                        'condition_name': condition_name,
                        'state': state,
                        'category': category,
                        'data_type': data_type
                    })
    
    # Generate metadata
    metadata_data = []
    for i in range(5):  # 5 data sources
        metadata_data.append({
            'machine_name': machine_name,
            'source_file': f'mazak_1_vtc_200_merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            'data_type': 'current' if i % 2 == 0 else 'sample',
            'file_size_mb': np.random.uniform(80, 120),
            'record_count': len(samples_data) // 5
        })
    
    # Create DataFrames and save as CSV
    samples_df = pd.DataFrame(samples_data)
    events_df = pd.DataFrame(events_data)
    conditions_df = pd.DataFrame(conditions_data)
    metadata_df = pd.DataFrame(metadata_data)
    
    # Ensure directories exist
    os.makedirs('src/data/processed', exist_ok=True)
    
    # Save CSV files
    samples_df.to_csv('src/data/processed/samples.csv', index=False)
    events_df.to_csv('src/data/processed/events.csv', index=False)
    conditions_df.to_csv('src/data/processed/conditions.csv', index=False)
    metadata_df.to_csv('src/data/processed/metadata.csv', index=False)
    
    print(f"Generated sample data:")
    print(f"- Samples: {len(samples_data)} records")
    print(f"- Events: {len(events_data)} records") 
    print(f"- Conditions: {len(conditions_data)} records")
    print(f"- Metadata: {len(metadata_data)} records")
    print(f"CSV files saved to src/data/processed/")

if __name__ == "__main__":
    generate_sample_data()