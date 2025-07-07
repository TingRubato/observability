import os
import csv
import glob
import psycopg2
import xml.etree.ElementTree as ET
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv
import argparse

# Load environment variables from .env file
load_dotenv()

# Ensure required environment variables are set
required_env_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
for var in required_env_vars:
    if var not in os.environ:
        raise EnvironmentError(f"Environment variable '{var}' is not set.")

# --- CONFIGURATION (via env vars) ---
DB_PARAMS = {
    'host':     os.environ['PGHOST'],
    'port':     os.environ.get('PGPORT', 5432),
    'dbname':   os.environ['PGDATABASE'],
    'user':     os.environ['PGUSER'],
    'password': os.environ['PGPASSWORD'],
}

XML_DIR = 'src/data/'   # or wherever your .xml files live

# --- HELPERS ---
def strip_ns(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag

def parse_iso(ts):
    # handle trailing Z
    ts = ts.replace('Z', '+00:00')
    if '.' in ts:
        date_part, rest = ts.split('.', 1)
        # rest may contain microseconds and timezone
        micro, *tz = rest.split('+')
        if len(micro) < 6:
            micro = micro.ljust(6, '0')
        tz_str = '+' + tz[0] if tz else ''
        ts = f"{date_part}.{micro}{tz_str}"
    return datetime.fromisoformat(ts)

def print_xml_preview(xml_file, namespaces):
    """Print a preview of the XML file content (similar to reference script)"""
    print(f"\n--- Preview of {os.path.basename(xml_file)} ---")
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Extract header information
        header = root.find('.//mt:Header', namespaces)
        if header is not None:
            print("  Header Information:")
            print(f"    Sender: {header.get('sender')}")
            print(f"    Creation Time: {header.get('creationTime')}")
            print(f"    Instance ID: {header.get('instanceId')}")
        
        # Find all DeviceStream elements
        device_streams = root.findall('.//mt:DeviceStream', namespaces)
        print(f"  Device Streams: {len(device_streams)} found")
        
        for device in device_streams:
            device_name = device.get('name')
            print(f"    Device: {device_name}")
            
            # Count events and samples
            events = device.findall('.//mt:Events/*', namespaces)
            samples = device.findall('.//mt:Samples/*', namespaces)
            conditions = device.findall('.//mt:Condition/*', namespaces)
            
            print(f"      Events: {len(events)}")
            print(f"      Samples: {len(samples)}")
            print(f"      Conditions: {len(conditions)}")
            
            # Show first few events/samples as examples
            if events:
                print("      Sample Events:")
                for event in events[:3]:  # Show first 3
                    tag_name = strip_ns(event.tag)
                    data_item_id = event.get('dataItemId', 'N/A')
                    timestamp = event.get('timestamp', 'N/A')
                    value = event.text or 'N/A'
                    print(f"        - {tag_name} ({data_item_id}): {value} at {timestamp}")
                if len(events) > 3:
                    print(f"        ... and {len(events) - 3} more events")
            
            if samples:
                print("      Sample Data:")
                for sample in samples[:3]:  # Show first 3
                    tag_name = strip_ns(sample.tag)
                    data_item_id = sample.get('dataItemId', 'N/A')
                    timestamp = sample.get('timestamp', 'N/A')
                    value = sample.text or 'N/A'
                    print(f"        - {tag_name} ({data_item_id}): {value} at {timestamp}")
                if len(samples) > 3:
                    print(f"        ... and {len(samples) - 3} more samples")
        
        print("-" * 50)
        
    except ET.ParseError as e:
        print(f"  Error parsing XML file: {e}")
    except Exception as e:
        print(f"  Error previewing file: {e}")

def setup_constraints(cur):
    """Setup database constraints with proper error handling"""
    print("Setting up database constraints...")
    
    constraints = [
        ("device_stream", "device_stream_unique", 
         "ALTER TABLE device_stream ADD CONSTRAINT device_stream_unique UNIQUE (device_name, instance_id, creation_time)"),
        ("component_stream", "component_stream_unique",
         "ALTER TABLE component_stream ADD CONSTRAINT component_stream_unique UNIQUE (device_stream_id, component_id)"),
        ("sample", "sample_unique",
         "ALTER TABLE sample ADD CONSTRAINT sample_unique UNIQUE (component_stream_id, tag, timestamp, sequence)"),
        ("event", "event_unique",
         "ALTER TABLE event ADD CONSTRAINT event_unique UNIQUE (component_stream_id, tag, timestamp, sequence)"),
        ("condition", "condition_unique",
         "ALTER TABLE condition ADD CONSTRAINT condition_unique UNIQUE (component_stream_id, tag, timestamp, sequence)")
    ]
    
    for table, constraint_name, sql in constraints:
        try:
            cur.execute(sql)
            print(f"Added {constraint_name} constraint")
        except psycopg2.errors.DuplicateTable:
            print(f"{constraint_name} constraint already exists")
        except Exception as e:
            print(f"Error setting up {constraint_name}: {e}")
            # Rollback the transaction on error
            cur.connection.rollback()
            raise

def process_xml_file(cur, xml_file, preview_mode=False):
    """Process a single XML file and insert data into database"""
    print(f"Processing {xml_file}...")
    
    try:
        # Robust XML parsing with error handling
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Error parsing XML file {xml_file}: {e}")
            return None
        except FileNotFoundError:
            print(f"Error: The file '{xml_file}' was not found.")
            return None
        
        # Detect namespace from root element
        root_ns = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
        if '1.5' in root_ns:
            namespace_uri = 'urn:mtconnect.org:MTConnectStreams:1.5'
        elif '2.0' in root_ns:
            namespace_uri = 'urn:mtconnect.org:MTConnectStreams:2.0'
        else:
            print(f"Warning: Unknown namespace in {xml_file}: {root_ns}")
            return None
            
        # Define namespace mapping
        namespaces = {'mt': namespace_uri}

        # Print preview if requested
        if preview_mode:
            print_xml_preview(xml_file, namespaces)
            return None

        # 1) Insert device_stream (header)
        hdr = root.find('.//mt:Header', namespaces)
        device_stream = root.find('.//mt:DeviceStream', namespaces)
        
        if hdr is None:
            print(f"Warning: Header not found in {xml_file}")
            return None
            
        if device_stream is None:
            print(f"Warning: DeviceStream not found in {xml_file}")
            return None

        ds_vals = (
            device_stream.attrib['name'],
            hdr.attrib['sender'],
            hdr.attrib.get('instanceId',''),
            parse_iso(hdr.attrib['creationTime']),
            int(hdr.attrib.get('nextSequence','0')),
            int(hdr.attrib.get('firstSequence','0')),
            int(hdr.attrib.get('lastSequence','0')),
        )
        
        cur.execute("""
            INSERT INTO device_stream
              (device_name, uuid, instance_id, creation_time,
               next_sequence, first_sequence, last_sequence)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (device_name, instance_id, creation_time) 
            DO UPDATE SET
              uuid = EXCLUDED.uuid,
              next_sequence = EXCLUDED.next_sequence,
              first_sequence = EXCLUDED.first_sequence,
              last_sequence = EXCLUDED.last_sequence
            RETURNING id
        """, ds_vals)
        device_stream_id, = cur.fetchone()

        # Prepare in-memory CSVs
        samples_buf = StringIO()
        events_buf  = StringIO()
        cond_buf    = StringIO()
        samples_writer = csv.writer(samples_buf)
        events_writer  = csv.writer(events_buf)
        cond_writer    = csv.writer(cond_buf)

        # Write headers for COPY
        samples_writer.writerow(
            ['component_stream_id','data_item_id','tag','timestamp','sequence','sub_type','composition_id','value']
        )
        events_writer.writerow(['component_stream_id','data_item_id','tag','timestamp','sequence','value'])
        cond_writer.writerow(['component_stream_id','data_item_id','tag','timestamp','sequence','type','value'])

        # Counters for logging
        total_components = 0
        total_samples = 0
        total_events = 0
        total_conditions = 0

        # 2) Iterate ComponentStream
        for comp in root.findall('.//mt:ComponentStream', namespaces):
            total_components += 1
            cs_vals = (
                device_stream_id,
                comp.attrib['component'],
                comp.attrib['name'],
                comp.attrib['componentId']
            )
            cur.execute("""
                INSERT INTO component_stream
                  (device_stream_id, component_type, component_name, component_id)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (device_stream_id, component_id)
                DO UPDATE SET
                  component_type = EXCLUDED.component_type,
                  component_name = EXCLUDED.component_name
                RETURNING id
            """, cs_vals)
            comp_stream_id, = cur.fetchone()

            # 3) Samples
            samp_parent = comp.find('mt:Samples', namespaces)
            if samp_parent is not None:
                for elem in samp_parent:
                    tag  = strip_ns(elem.tag)
                    attrib = elem.attrib
                    samples_writer.writerow([
                        comp_stream_id,
                        attrib.get('dataItemId',''),
                        tag,
                        parse_iso(attrib['timestamp']),
                        int(attrib['sequence']),
                        attrib.get('subType',''),
                        attrib.get('compositionId',''),
                        (elem.text or '').strip()
                    ])
                    total_samples += 1

            # 4) Events
            ev_parent = comp.find('mt:Events', namespaces)
            if ev_parent is not None:
                for elem in ev_parent:
                    tag  = strip_ns(elem.tag)
                    attrib = elem.attrib
                    events_writer.writerow([
                        comp_stream_id,
                        attrib.get('dataItemId',''),
                        tag,
                        parse_iso(attrib.get('timestamp')) if 'timestamp' in attrib else None,
                        int(attrib.get('sequence',0)),
                        (elem.text or '').strip()
                    ])
                    total_events += 1

            # 5) Condition
            cond_parent = comp.find('mt:Condition', namespaces)
            if cond_parent is not None:
                for elem in cond_parent:
                    tag    = strip_ns(elem.tag)
                    attrib = elem.attrib
                    cond_writer.writerow([
                        comp_stream_id,
                        attrib.get('dataItemId',''),
                        tag,
                        parse_iso(attrib['timestamp']),
                        int(attrib['sequence']),
                        attrib.get('type',''),
                        (elem.text or '').strip()
                    ])
                    total_conditions += 1

        # COPY into Postgres
        samples_buf.seek(0)
        cur.copy_expert(
            "COPY sample (component_stream_id,data_item_id,tag,timestamp,sequence,sub_type,composition_id,value) FROM STDIN CSV HEADER",
            samples_buf
        )
        events_buf.seek(0)
        cur.copy_expert(
            "COPY event (component_stream_id,data_item_id,tag,timestamp,sequence,value) FROM STDIN CSV HEADER",
            events_buf
        )
        cond_buf.seek(0)
        cur.copy_expert(
            "COPY condition (component_stream_id,data_item_id,tag,timestamp,sequence,type,value) FROM STDIN CSV HEADER",
            cond_buf
        )

        print(f"Loaded '{os.path.basename(xml_file)}' into device_stream id={device_stream_id}")
        print(f"  Components: {total_components}, Samples: {total_samples}, Events: {total_events}, Conditions: {total_conditions}")
        return device_stream_id
        
    except psycopg2.errors.UniqueViolation as e:
        print(f"Duplicate entry error in {xml_file}: {e}\nSkipping this file.")
        cur.connection.rollback()
        return None
    except Exception as e:
        print(f"Error processing {xml_file}: {e}")
        cur.connection.rollback()
        raise

def create_tables(cur):
    """Create the database tables if they don't exist"""
    print("Creating database tables...")
    
    # Create device_stream table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_stream (
            id SERIAL PRIMARY KEY,
            device_name VARCHAR(255) NOT NULL,
            uuid VARCHAR(255) NOT NULL,
            instance_id VARCHAR(255),
            creation_time TIMESTAMP NOT NULL,
            next_sequence INTEGER DEFAULT 0,
            first_sequence INTEGER DEFAULT 0,
            last_sequence INTEGER DEFAULT 0
        )
    """)
    
    # Create component_stream table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS component_stream (
            id SERIAL PRIMARY KEY,
            device_stream_id INTEGER REFERENCES device_stream(id) ON DELETE CASCADE,
            component_type VARCHAR(255) NOT NULL,
            component_name VARCHAR(255) NOT NULL,
            component_id VARCHAR(255) NOT NULL
        )
    """)
    
    # Create sample table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sample (
            id SERIAL PRIMARY KEY,
            component_stream_id INTEGER REFERENCES component_stream(id) ON DELETE CASCADE,
            data_item_id VARCHAR(255),
            tag VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            sequence INTEGER NOT NULL,
            sub_type VARCHAR(255),
            composition_id VARCHAR(255),
            value TEXT
        )
    """)
    
    # Create event table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS event (
            id SERIAL PRIMARY KEY,
            component_stream_id INTEGER REFERENCES component_stream(id) ON DELETE CASCADE,
            data_item_id VARCHAR(255),
            tag VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP,
            sequence INTEGER DEFAULT 0,
            value TEXT
        )
    """)
    
    # Create condition table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS condition (
            id SERIAL PRIMARY KEY,
            component_stream_id INTEGER REFERENCES component_stream(id) ON DELETE CASCADE,
            data_item_id VARCHAR(255),
            tag VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            sequence INTEGER NOT NULL,
            type VARCHAR(255),
            value TEXT
        )
    """)
    
    print("Database tables created successfully")

# --- MAIN ---
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Load MTConnect XML files into PostgreSQL database')
    parser.add_argument('--preview', action='store_true', 
                       help='Preview XML files without loading into database')
    parser.add_argument('--file', type=str, 
                       help='Process a single XML file instead of all files in the data directory')
    args = parser.parse_args()

    if args.preview:
        print("=== PREVIEW MODE ===")
        print("This will show XML file contents without loading into database")
        
        # Preview files
        if args.file:
            # Preview single file
            if not os.path.exists(args.file):
                print(f"Error: File '{args.file}' not found.")
                return
            
            # Detect namespace for preview
            try:
                tree = ET.parse(args.file)
                root = tree.getroot()
                root_ns = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
                if '1.5' in root_ns:
                    namespace_uri = 'urn:mtconnect.org:MTConnectStreams:1.5'
                elif '2.0' in root_ns:
                    namespace_uri = 'urn:mtconnect.org:MTConnectStreams:2.0'
                else:
                    namespace_uri = 'urn:mtconnect.org:MTConnectStreams:1.5'  # Default
                
                namespaces = {'mt': namespace_uri}
                print_xml_preview(args.file, namespaces)
            except Exception as e:
                print(f"Error previewing file: {e}")
        else:
            # Preview all files
            xml_files = glob.glob(os.path.join(XML_DIR, '*.xml'))
            # Exclude vtc300c.xml as it has different format and should be loaded separately
            xml_files = [f for f in xml_files if 'vtc300c' not in f]
            for xml_file in xml_files:
                try:
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    root_ns = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
                    if '1.5' in root_ns:
                        namespace_uri = 'urn:mtconnect.org:MTConnectStreams:1.5'
                    elif '2.0' in root_ns:
                        namespace_uri = 'urn:mtconnect.org:MTConnectStreams:2.0'
                    else:
                        namespace_uri = 'urn:mtconnect.org:MTConnectStreams:1.5'  # Default
                    
                    namespaces = {'mt': namespace_uri}
                    print_xml_preview(xml_file, namespaces)
                except Exception as e:
                    print(f"Error previewing {xml_file}: {e}")
        return

    # Database loading mode
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Create tables
        create_tables(cur)

        # Process XML files
        if args.file:
            # Process single file
            if not os.path.exists(args.file):
                print(f"Error: File '{args.file}' not found.")
                return
            process_xml_file(cur, args.file)
        else:
            # Process all files
            xml_files = glob.glob(os.path.join(XML_DIR, '*.xml'))
            # Exclude vtc300c.xml as it has different format and should be loaded separately
            xml_files = [f for f in xml_files if 'vtc300c' not in f]
            if not xml_files:
                print(f"No XML files found in {XML_DIR} (excluding vtc300c.xml)")
                return
            
            print(f"Found {len(xml_files)} XML files to process (excluding vtc300c.xml)")
            for xml_file in xml_files:
                process_xml_file(cur, xml_file)

        # Commit and close
        conn.commit()
        cur.close()
        conn.close()
        print("\nDatabase loading completed successfully!")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
    except Exception as e:
        print(f"Unexpected error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    main()