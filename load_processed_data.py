#!/usr/bin/env python3
"""
Load processed CSV data into the Mazak observability database.
This script loads data from the processed CSV files into the new database schema.
"""

import os
import csv
import psycopg2
from io import StringIO
from datetime import datetime
import argparse
import sys

# Database connection parameters
DB_PARAMS = {
    'host': '100.83.52.87',
    'port': 5432,
    'dbname': 'mazak',
    'user': 'tableplus',
    'password': 'tableplus',
}

def get_machine_id_by_name(cur, machine_name):
    """Get machine ID by name, create if doesn't exist"""
    # Map CSV machine names to our database machine names
    machine_mapping = {
        'mazak_1_vtc_200': 'VTC-200-001',
        'mazak_2_vtc_300': 'VTC-300-001', 
        'mazak_3_350msy': '350MSY-001',
        'mazak_4_vtc_300c': 'VTC-300C-001'
    }
    
    db_machine_name = machine_mapping.get(machine_name, machine_name)
    
    cur.execute("SELECT id FROM machines WHERE name = %s", (db_machine_name,))
    result = cur.fetchone()
    
    if result:
        return result[0]
    else:
        # Create new machine if it doesn't exist
        print(f"Creating new machine: {db_machine_name}")
        cur.execute("""
            INSERT INTO machines (name, model, series, status) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (db_machine_name, db_machine_name.split('-')[0], 'VTC', 'ACTIVE'))
        return cur.fetchone()[0]

def get_or_create_component(cur, machine_id, component_id, component_type, component_name):
    """Get component ID, create if doesn't exist"""
    # Map component types to our enum values
    type_mapping = {
        'Linear': 'LINEAR',
        'Rotary': 'ROTARY', 
        'Controller': 'CONTROLLER',
        'Adapter': 'CONTROLLER',
        'Agent': 'CONTROLLER',
        'Path': 'CONTROLLER',
        'Axes': 'LINEAR'
    }
    
    db_component_type = type_mapping.get(component_type, 'CONTROLLER')
    
    cur.execute("""
        SELECT id FROM components 
        WHERE machine_id = %s AND component_id = %s
    """, (machine_id, component_id))
    result = cur.fetchone()
    
    if result:
        return result[0]
    else:
        # Create new component
        cur.execute("""
            INSERT INTO components (machine_id, component_id, component_type, component_name) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (machine_id, component_id, db_component_type, component_name))
        return cur.fetchone()[0]

def get_or_create_data_stream(cur, machine_id, data_type):
    """Get or create data stream for machine and type"""
    stream_type = 'SAMPLE' if data_type == 'sample' else 'CURRENT'
    
    cur.execute("""
        SELECT id FROM data_streams 
        WHERE machine_id = %s AND stream_type = %s
    """, (machine_id, stream_type))
    result = cur.fetchone()
    
    if result:
        return result[0]
    else:
        # Create new data stream
        cur.execute("""
            INSERT INTO data_streams (machine_id, stream_type, instance_id, creation_time) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (machine_id, stream_type, f"{stream_type.lower()}_stream_{machine_id}", datetime.now()))
        return cur.fetchone()[0]

def load_samples(cur, csv_file_path):
    """Load samples data from CSV"""
    print(f"Loading samples from {csv_file_path}...")
    
    # Prepare in-memory CSV for COPY
    samples_buf = StringIO()
    samples_writer = csv.writer(samples_buf)
    
    # Write header
    samples_writer.writerow([
        'data_stream_id', 'component_id', 'data_item_id', 'sample_name', 
        'timestamp', 'sequence', 'value', 'sub_type', 'composition_id'
    ])
    
    total_rows = 0
    batch_size = 10000
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Get machine and component IDs
                machine_id = get_machine_id_by_name(cur, row['machine_name'])
                component_id = get_or_create_component(
                    cur, machine_id, row['component_id'], 
                    row['component_type'], row['component_name']
                )
                data_stream_id = get_or_create_data_stream(cur, machine_id, row['data_type'])
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                
                # Parse sequence
                sequence = int(row.get('sequence', 0))
                
                # Parse value (handle empty strings)
                value = row.get('value', '').strip()
                if value == '':
                    value = None
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        value = value  # Keep as string if not numeric
                
                samples_writer.writerow([
                    data_stream_id, component_id, row['sample_name'], row['sample_name'],
                    timestamp, sequence, value, row.get('sub_type', ''), ''
                ])
                
                total_rows += 1
                
                # Commit in batches
                if total_rows % batch_size == 0:
                    print(f"Processed {total_rows} samples...")
                    cur.connection.commit()
                    
            except Exception as e:
                print(f"Error processing sample row: {e}")
                continue
    
    # Load remaining data
    if total_rows % batch_size != 0:
        print(f"Processed {total_rows} samples...")
        cur.connection.commit()
    
    # Copy to database
    samples_buf.seek(0)
    cur.copy_expert("""
        COPY samples (data_stream_id, component_id, data_item_id, sample_name, 
                     timestamp, sequence, value, sub_type, composition_id) 
        FROM STDIN CSV HEADER
    """, samples_buf)
    
    print(f"Loaded {total_rows} samples into database")

def load_events(cur, csv_file_path):
    """Load events data from CSV"""
    print(f"Loading events from {csv_file_path}...")
    
    events_buf = StringIO()
    events_writer = csv.writer(events_buf)
    
    # Write header
    events_writer.writerow([
        'data_stream_id', 'component_id', 'data_item_id', 'event_name',
        'timestamp', 'sequence', 'value', 'event_type'
    ])
    
    total_rows = 0
    batch_size = 10000
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Get machine and component IDs
                machine_id = get_machine_id_by_name(cur, row['machine_name'])
                component_id = get_or_create_component(
                    cur, machine_id, row['component_id'],
                    row['component_type'], row['component_name']
                )
                data_stream_id = get_or_create_data_stream(cur, machine_id, row['data_type'])
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                
                # Parse sequence
                sequence = int(row.get('sequence', 0))
                
                # Determine event type based on event name
                event_name = row['event_name']
                if 'program' in event_name.lower():
                    event_type = 'PROGRAM'
                elif 'door' in event_name.lower() or 'safety' in event_name.lower():
                    event_type = 'SAFETY'
                elif 'control' in event_name.lower():
                    event_type = 'CONTROL'
                else:
                    event_type = 'EXECUTION'
                
                events_writer.writerow([
                    data_stream_id, component_id, event_name, event_name,
                    timestamp, sequence, row.get('value', ''), event_type
                ])
                
                total_rows += 1
                
                # Commit in batches
                if total_rows % batch_size == 0:
                    print(f"Processed {total_rows} events...")
                    cur.connection.commit()
                    
            except Exception as e:
                print(f"Error processing event row: {e}")
                continue
    
    # Load remaining data
    if total_rows % batch_size != 0:
        print(f"Processed {total_rows} events...")
        cur.connection.commit()
    
    # Copy to database
    events_buf.seek(0)
    cur.copy_expert("""
        COPY events (data_stream_id, component_id, data_item_id, event_name,
                    timestamp, sequence, value, event_type)
        FROM STDIN CSV HEADER
    """, events_buf)
    
    print(f"Loaded {total_rows} events into database")

def load_conditions(cur, csv_file_path):
    """Load conditions data from CSV"""
    print(f"Loading conditions from {csv_file_path}...")
    
    conditions_buf = StringIO()
    conditions_writer = csv.writer(conditions_buf)
    
    # Write header
    conditions_writer.writerow([
        'data_stream_id', 'component_id', 'data_item_id', 'condition_name',
        'timestamp', 'sequence', 'state', 'category', 'message'
    ])
    
    total_rows = 0
    batch_size = 10000
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Get machine and component IDs
                machine_id = get_machine_id_by_name(cur, row['machine_name'])
                component_id = get_or_create_component(
                    cur, machine_id, row['component_id'],
                    row['component_type'], row['component_name']
                )
                data_stream_id = get_or_create_data_stream(cur, machine_id, row['data_type'])
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                
                # Parse sequence
                sequence = int(row.get('sequence', 0))
                
                # Map state
                state = 'NORMAL'
                if row.get('state') == '#text':
                    state = 'NORMAL'
                elif 'warning' in row.get('state', '').lower():
                    state = 'WARNING'
                elif 'fault' in row.get('state', '').lower():
                    state = 'FAULT'
                
                # Map category
                category_mapping = {
                    'TEMPERATURE': 'TEMPERATURE',
                    'LOAD': 'LOAD',
                    'LOGIC_PROGRAM': 'LOGIC_PROGRAM',
                    'COMMUNICATIONS': 'COMMUNICATIONS'
                }
                category = category_mapping.get(row.get('category', ''), 'TEMPERATURE')
                
                conditions_writer.writerow([
                    data_stream_id, component_id, row['condition_name'], row['condition_name'],
                    timestamp, sequence, state, category, row.get('state', '')
                ])
                
                total_rows += 1
                
                # Commit in batches
                if total_rows % batch_size == 0:
                    print(f"Processed {total_rows} conditions...")
                    cur.connection.commit()
                    
            except Exception as e:
                print(f"Error processing condition row: {e}")
                continue
    
    # Load remaining data
    if total_rows % batch_size != 0:
        print(f"Processed {total_rows} conditions...")
        cur.connection.commit()
    
    # Copy to database
    conditions_buf.seek(0)
    cur.copy_expert("""
        COPY conditions (data_stream_id, component_id, data_item_id, condition_name,
                        timestamp, sequence, state, category, message)
        FROM STDIN CSV HEADER
    """, conditions_buf)
    
    print(f"Loaded {total_rows} conditions into database")

def main():
    parser = argparse.ArgumentParser(description='Load processed CSV data into Mazak database')
    parser.add_argument('--samples', action='store_true', help='Load samples data')
    parser.add_argument('--events', action='store_true', help='Load events data')
    parser.add_argument('--conditions', action='store_true', help='Load conditions data')
    parser.add_argument('--all', action='store_true', help='Load all data types')
    parser.add_argument('--data-dir', default='src/data/processed', help='Directory containing CSV files')
    
    args = parser.parse_args()
    
    if not any([args.samples, args.events, args.conditions, args.all]):
        print("Please specify which data to load: --samples, --events, --conditions, or --all")
        return
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Set up for bulk loading
        cur.execute("SET session_replication_role = replica;")  # Disable triggers temporarily
        
        if args.all or args.samples:
            samples_file = os.path.join(args.data_dir, 'samples.csv')
            if os.path.exists(samples_file):
                load_samples(cur, samples_file)
            else:
                print(f"Samples file not found: {samples_file}")
        
        if args.all or args.events:
            events_file = os.path.join(args.data_dir, 'events.csv')
            if os.path.exists(events_file):
                load_events(cur, events_file)
            else:
                print(f"Events file not found: {events_file}")
        
        if args.all or args.conditions:
            conditions_file = os.path.join(args.data_dir, 'conditions.csv')
            if os.path.exists(conditions_file):
                load_conditions(cur, conditions_file)
            else:
                print(f"Conditions file not found: {conditions_file}")
        
        # Re-enable triggers
        cur.execute("SET session_replication_role = DEFAULT;")
        
        # Commit all changes
        conn.commit()
        print("\nData loading completed successfully!")
        
        # Show summary
        cur.execute("SELECT COUNT(*) FROM samples")
        sample_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM events")
        event_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM conditions")
        condition_count = cur.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"  Samples: {sample_count:,}")
        print(f"  Events: {event_count:,}")
        print(f"  Conditions: {condition_count:,}")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()


