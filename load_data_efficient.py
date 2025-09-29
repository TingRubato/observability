#!/usr/bin/env python3
"""
Efficient data loading script for large CSV files.
Uses COPY FROM STDIN for maximum performance and proper connection management.
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
        print(f"Creating new machine: {db_machine_name}")
        cur.execute("""
            INSERT INTO machines (name, model, series, status) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (db_machine_name, db_machine_name.split('-')[0], 'VTC', 'ACTIVE'))
        return cur.fetchone()[0]

def get_or_create_component(cur, machine_id, component_id, component_type, component_name):
    """Get component ID, create if doesn't exist"""
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
        cur.execute("""
            INSERT INTO data_streams (machine_id, stream_type, instance_id, creation_time) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (machine_id, stream_type, f"{stream_type.lower()}_stream_{machine_id}", datetime.now()))
        return cur.fetchone()[0]

def load_samples_efficient(cur, csv_file_path):
    """Load samples data efficiently using COPY FROM STDIN"""
    print(f"Loading samples from {csv_file_path}...")
    
    # First, build lookup tables to avoid repeated queries
    machine_lookup = {}
    component_lookup = {}
    stream_lookup = {}
    
    # Process file in chunks to build lookup tables
    chunk_size = 50000
    total_processed = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Build lookup tables first
        print("Building lookup tables...")
        for row in reader:
            machine_name = row['machine_name']
            component_id = row['component_id']
            data_type = row['data_type']
            
            if machine_name not in machine_lookup:
                machine_lookup[machine_name] = get_machine_id_by_name(cur, machine_name)
            
            machine_id = machine_lookup[machine_name]
            lookup_key = (machine_id, component_id)
            
            if lookup_key not in component_lookup:
                component_lookup[lookup_key] = get_or_create_component(
                    cur, machine_id, component_id, 
                    row['component_type'], row['component_name']
                )
            
            stream_key = (machine_id, data_type)
            if stream_key not in stream_lookup:
                stream_lookup[stream_key] = get_or_create_data_stream(cur, machine_id, data_type)
            
            total_processed += 1
            if total_processed % chunk_size == 0:
                print(f"Built lookups for {total_processed:,} records...")
                cur.connection.commit()
    
    print(f"Lookup tables built for {total_processed:,} records")
    
    # Now load data efficiently
    print("Loading data into database...")
    
    # Reset file pointer
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Use COPY FROM STDIN for maximum efficiency
        samples_buf = StringIO()
        samples_writer = csv.writer(samples_buf)
        
        # Write header for COPY
        samples_writer.writerow([
            'data_stream_id', 'component_id', 'data_item_id', 'sample_name', 
            'timestamp', 'sequence', 'value', 'sub_type', 'composition_id'
        ])
        
        batch_count = 0
        batch_size = 100000
        
        for row in reader:
            try:
                machine_name = row['machine_name']
                component_id = row['component_id']
                data_type = row['data_type']
                
                machine_id = machine_lookup[machine_name]
                component_db_id = component_lookup[(machine_id, component_id)]
                data_stream_id = stream_lookup[(machine_id, data_type)]
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                
                # Parse sequence
                sequence = int(row.get('sequence', 0))
                
                # Parse value
                value = row.get('value', '').strip()
                if value == '':
                    value = None
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        value = value
                
                samples_writer.writerow([
                    data_stream_id, component_db_id, row['sample_name'], row['sample_name'],
                    timestamp, sequence, value, row.get('sub_type', ''), ''
                ])
                
                batch_count += 1
                
                # Write in batches
                if batch_count % batch_size == 0:
                    samples_buf.seek(0)
                    cur.copy_expert("""
                        COPY samples (data_stream_id, component_id, data_item_id, sample_name, 
                                     timestamp, sequence, value, sub_type, composition_id) 
                        FROM STDIN CSV HEADER
                    """, samples_buf)
                    print(f"Loaded batch of {batch_count:,} samples...")
                    
                    # Clear buffer for next batch
                    samples_buf = StringIO()
                    samples_writer = csv.writer(samples_buf)
                    samples_writer.writerow([
                        'data_stream_id', 'component_id', 'data_item_id', 'sample_name', 
                        'timestamp', 'sequence', 'value', 'sub_type', 'composition_id'
                    ])
                    
                    cur.connection.commit()
                    
            except Exception as e:
                print(f"Error processing sample row: {e}")
                continue
        
        # Load remaining data
        if batch_count % batch_size != 0:
            samples_buf.seek(0)
            cur.copy_expert("""
                COPY samples (data_stream_id, component_id, data_item_id, sample_name, 
                             timestamp, sequence, value, sub_type, composition_id) 
                FROM STDIN CSV HEADER
            """, samples_buf)
            print(f"Loaded final batch of {batch_count % batch_size:,} samples...")
        
        cur.connection.commit()
        print(f"Successfully loaded samples data")

def load_events_efficient(cur, csv_file_path):
    """Load events data efficiently"""
    print(f"Loading events from {csv_file_path}...")
    
    # Build lookup tables
    machine_lookup = {}
    component_lookup = {}
    stream_lookup = {}
    
    # First pass: build lookups
    print("Building lookup tables...")
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            machine_name = row['machine_name']
            component_id = row['component_id']
            data_type = row['data_type']
            
            if machine_name not in machine_lookup:
                machine_lookup[machine_name] = get_machine_id_by_name(cur, machine_name)
            
            machine_id = machine_lookup[machine_name]
            lookup_key = (machine_id, component_id)
            
            if lookup_key not in component_lookup:
                component_lookup[lookup_key] = get_or_create_component(
                    cur, machine_id, component_id, 
                    row['component_type'], row['component_name']
                )
            
            stream_key = (machine_id, data_type)
            if stream_key not in stream_lookup:
                stream_lookup[stream_key] = get_or_create_data_stream(cur, machine_id, data_type)
    
    cur.connection.commit()
    print("Lookup tables built")
    
    # Second pass: load data
    print("Loading events data...")
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        events_buf = StringIO()
        events_writer = csv.writer(events_buf)
        
        # Write header
        events_writer.writerow([
            'data_stream_id', 'component_id', 'data_item_id', 'event_name',
            'timestamp', 'sequence', 'value', 'event_type'
        ])
        
        batch_count = 0
        batch_size = 100000
        
        for row in reader:
            try:
                machine_name = row['machine_name']
                component_id = row['component_id']
                data_type = row['data_type']
                
                machine_id = machine_lookup[machine_name]
                component_db_id = component_lookup[(machine_id, component_id)]
                data_stream_id = stream_lookup[(machine_id, data_type)]
                
                # Parse timestamp
                timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                
                # Parse sequence
                sequence = int(row.get('sequence', 0))
                
                # Determine event type
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
                    data_stream_id, component_db_id, event_name, event_name,
                    timestamp, sequence, row.get('value', ''), event_type
                ])
                
                batch_count += 1
                
                # Write in batches
                if batch_count % batch_size == 0:
                    events_buf.seek(0)
                    cur.copy_expert("""
                        COPY events (data_stream_id, component_id, data_item_id, event_name,
                                    timestamp, sequence, value, event_type)
                        FROM STDIN CSV HEADER
                    """, events_buf)
                    print(f"Loaded batch of {batch_count:,} events...")
                    
                    # Clear buffer
                    events_buf = StringIO()
                    events_writer = csv.writer(events_buf)
                    events_writer.writerow([
                        'data_stream_id', 'component_id', 'data_item_id', 'event_name',
                        'timestamp', 'sequence', 'value', 'event_type'
                    ])
                    
                    cur.connection.commit()
                    
            except Exception as e:
                print(f"Error processing event row: {e}")
                continue
        
        # Load remaining data
        if batch_count % batch_size != 0:
            events_buf.seek(0)
            cur.copy_expert("""
                COPY events (data_stream_id, component_id, data_item_id, event_name,
                            timestamp, sequence, value, event_type)
                FROM STDIN CSV HEADER
            """, events_buf)
            print(f"Loaded final batch of {batch_count % batch_size:,} events...")
        
        cur.connection.commit()
        print(f"Successfully loaded events data")

def main():
    parser = argparse.ArgumentParser(description='Efficiently load processed CSV data into Mazak database')
    parser.add_argument('--samples', action='store_true', help='Load samples data')
    parser.add_argument('--events', action='store_true', help='Load events data')
    parser.add_argument('--all', action='store_true', help='Load all data types')
    parser.add_argument('--data-dir', default='src/data/processed', help='Directory containing CSV files')
    
    args = parser.parse_args()
    
    if not any([args.samples, args.events, args.all]):
        print("Please specify which data to load: --samples, --events, or --all")
        return
    
    conn = None
    cur = None
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Disable triggers for faster loading
        cur.execute("SET session_replication_role = replica;")
        
        if args.all or args.samples:
            samples_file = os.path.join(args.data_dir, 'samples.csv')
            if os.path.exists(samples_file):
                load_samples_efficient(cur, samples_file)
            else:
                print(f"Samples file not found: {samples_file}")
        
        if args.all or args.events:
            events_file = os.path.join(args.data_dir, 'events.csv')
            if os.path.exists(events_file):
                load_events_efficient(cur, events_file)
            else:
                print(f"Events file not found: {events_file}")
        
        # Re-enable triggers
        cur.execute("SET session_replication_role = DEFAULT;")
        
        # Final commit
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
        
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    main()


