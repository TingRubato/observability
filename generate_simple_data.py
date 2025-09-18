#!/usr/bin/env python3
"""
Generate sample CSV data for Mazak VTC 200 dashboard without pandas
"""

import csv
import random
import os
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample data that matches the dashboard expectations"""
    
    # Create timestamps for the last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    # Create directories
    os.makedirs('src/data/processed', exist_ok=True)
    
    machine_name = "mazak_1_vtc_200"
    
    # Generate samples.csv
    with open('src/data/processed/samples.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'machine_name', 'component_id', 'sample_name', 'value', 'sub_type', 'data_type'])
        
        # Generate data every 10 minutes for 24 hours
        current_time = start_time
        total_samples = 0
        
        while current_time <= end_time:
            # Axis positions
            for axis in ['X', 'Y', 'Z']:
                for suffix, base_val in [('abs', 100), ('pos', 100), ('load', 45)]:
                    value = base_val + random.gauss(0, 10 if suffix == 'load' else 50)
                    if suffix == 'load':
                        value = max(0, min(100, value))
                    
                    for data_type in ['current', 'sample']:
                        writer.writerow([
                            current_time.isoformat(),
                            machine_name,
                            f'linear_{axis.lower()}',
                            f'{axis}{suffix}',
                            round(value, 2),
                            'ACTUAL',
                            data_type
                        ])
                        total_samples += 1
            
            # Spindle data
            for item, base_val in [('Srpm', 2500), ('Sload', 40)]:
                value = base_val + random.gauss(0, 200 if item == 'Srpm' else 15)
                if item == 'Sload':
                    value = max(0, min(100, value))
                
                for data_type in ['current', 'sample']:
                    writer.writerow([
                        current_time.isoformat(),
                        machine_name,
                        'spindle',
                        item,
                        round(value, 2),
                        'ACTUAL',
                        data_type
                    ])
                    total_samples += 1
            
            # Time data
            elapsed_seconds = (current_time - start_time).total_seconds()
            for time_type, multiplier in [('total_time', 1.0), ('auto_time', 0.7), ('cut_time', 0.4)]:
                value = elapsed_seconds * multiplier
                
                for data_type in ['current', 'sample']:
                    writer.writerow([
                        current_time.isoformat(),
                        machine_name,
                        'controller',
                        time_type,
                        round(value, 0),
                        'ACTUAL',
                        data_type
                    ])
                    total_samples += 1
            
            current_time += timedelta(minutes=10)
    
    # Generate events.csv
    with open('src/data/processed/events.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'machine_name', 'component_id', 'event_name', 'value', 'data_type'])
        
        current_time = start_time
        total_events = 0
        
        while current_time <= end_time:
            # Status events
            events_data = [
                ('controller', 'avail', random.choice(['AVAILABLE', 'UNAVAILABLE'])),
                ('controller', 'mode', random.choice(['AUTOMATIC', 'MANUAL'])),
                ('controller', 'estop', random.choice(['ARMED', 'TRIGGERED'])),
                ('controller', 'execution', random.choice(['EXECUTING', 'READY', 'STOPPED'])),
                ('program', 'program', f'PROGRAM_{random.randint(1, 100):03d}'),
                ('program', 'Tool_number', random.randint(1, 20))
            ]
            
            for component, event_name, value in events_data:
                for data_type in ['current', 'sample']:
                    writer.writerow([
                        current_time.isoformat(),
                        machine_name,
                        component,
                        event_name,
                        value,
                        data_type
                    ])
                    total_events += 1
            
            current_time += timedelta(minutes=20)
    
    # Generate conditions.csv
    with open('src/data/processed/conditions.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'machine_name', 'component_id', 'condition_name', 'state', 'category', 'data_type'])
        
        current_time = start_time
        total_conditions = 0
        
        while current_time <= end_time:
            conditions_data = [
                ('controller', 'system_condition', 'Normal', 'SYSTEM'),
                ('axis_x', 'x_travel', 'Normal', 'ACTUATOR'),
                ('axis_y', 'y_travel', 'Normal', 'ACTUATOR'),
                ('axis_z', 'z_travel', 'Normal', 'ACTUATOR'),
                ('spindle', 'spindle_condition', 'Normal', 'SYSTEM')
            ]
            
            for component, condition_name, state, category in conditions_data:
                for data_type in ['current', 'sample']:
                    writer.writerow([
                        current_time.isoformat(),
                        machine_name,
                        component,
                        condition_name,
                        state,
                        category,
                        data_type
                    ])
                    total_conditions += 1
            
            current_time += timedelta(hours=1)
    
    # Generate metadata.csv
    with open('src/data/processed/metadata.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['machine_name', 'source_file', 'data_type', 'file_size_mb', 'record_count'])
        
        for i in range(5):
            writer.writerow([
                machine_name,
                f'mazak_1_vtc_200_merged_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{i}.json',
                'current' if i % 2 == 0 else 'sample',
                round(random.uniform(80, 120), 2),
                total_samples // 5
            ])
    
    print(f"Generated sample data:")
    print(f"- Samples: {total_samples} records")
    print(f"- Events: {total_events} records")
    print(f"- Conditions: {total_conditions} records")
    print(f"CSV files saved to src/data/processed/")

if __name__ == "__main__":
    generate_sample_data()