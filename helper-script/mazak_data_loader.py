#!/usr/bin/env python3
"""
Mazak Manufacturing Data Loader

This script loads processed Mazak machine data from CSV files into a PostgreSQL database.
It handles the complete data pipeline from CSV files to a fully populated database.

Requirements:
    pip install pandas psycopg2-binary python-dotenv tqdm

Usage:
    python mazak_data_loader.py --data-dir "/Users/timmy/Downloads/src 2/data/processed"
"""

import os
import sys
import argparse
import logging
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from tqdm import tqdm
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mazak_data_loader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    database: str = os.getenv('DB_NAME', 'mazak_manufacturing')
    username: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', 'password')
    
    def get_connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class MazakDataLoader:
    """Main class for loading Mazak manufacturing data into PostgreSQL"""
    
    def __init__(self, db_config: DatabaseConfig, data_directory: str):
        self.db_config = db_config
        self.data_directory = Path(data_directory)
        self.connection = None
        
        # Validate data directory
        if not self.data_directory.exists():
            raise ValueError(f"Data directory does not exist: {data_directory}")
        
        # Expected CSV files
        self.required_files = [
            'machines.csv',
            'components.csv', 
            'conditions.csv',
            'events.csv',
            'samples.csv',
            'metadata.csv'
        ]
        
        self._validate_files()
    
    def _validate_files(self):
        """Validate that all required CSV files exist"""
        missing_files = []
        for file in self.required_files:
            file_path = self.data_directory / file
            if not file_path.exists():
                missing_files.append(str(file_path))
        
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {missing_files}")
        
        logger.info(f"All required CSV files found in {self.data_directory}")
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                user=self.db_config.username,
                password=self.db_config.password
            )
            self.connection.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_schema(self):
        """Create the complete database schema"""
        schema_sql = """
        -- ============================================================
        -- MAZAK MANUFACTURING DATABASE SCHEMA
        -- ============================================================
        
        -- Master Data Tables
        CREATE TABLE IF NOT EXISTS machines (
            machine_id SERIAL PRIMARY KEY,
            machine_name VARCHAR(100) NOT NULL,
            machine_model VARCHAR(50) NOT NULL,
            machine_series VARCHAR(50),
            device_name VARCHAR(100) NOT NULL,
            device_uuid VARCHAR(255) NOT NULL,
            location VARCHAR(100),
            installation_date DATE,
            manufacturer VARCHAR(100) DEFAULT 'Mazak',
            asset_id VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(machine_name, device_uuid)
        );
        
        CREATE TABLE IF NOT EXISTS data_types (
            data_type_id SERIAL PRIMARY KEY,
            data_type_name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            is_realtime BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS component_types (
            component_type_id SERIAL PRIMARY KEY,
            type_name VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            category VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Configuration Tables
        CREATE TABLE IF NOT EXISTS machine_configurations (
            config_id SERIAL PRIMARY KEY,
            machine_id INTEGER NOT NULL REFERENCES machines(machine_id),
            data_type_id INTEGER NOT NULL REFERENCES data_types(data_type_id),
            components_count INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(machine_id, data_type_id)
        );
        
        CREATE TABLE IF NOT EXISTS machine_components (
            component_id SERIAL PRIMARY KEY,
            machine_id INTEGER NOT NULL REFERENCES machines(machine_id),
            data_type_id INTEGER NOT NULL REFERENCES data_types(data_type_id),
            component_identifier VARCHAR(100) NOT NULL,
            component_type_id INTEGER NOT NULL REFERENCES component_types(component_type_id),
            component_name VARCHAR(100) NOT NULL,
            has_conditions BOOLEAN DEFAULT FALSE,
            has_samples BOOLEAN DEFAULT FALSE,
            has_events BOOLEAN DEFAULT FALSE,
            conditions_count INTEGER DEFAULT 0,
            samples_count INTEGER DEFAULT 0,
            events_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(machine_id, data_type_id, component_identifier)
        );
        
        -- Time-series Data Tables
        CREATE TABLE IF NOT EXISTS machine_conditions (
            condition_id BIGSERIAL PRIMARY KEY,
            machine_id INTEGER NOT NULL REFERENCES machines(machine_id),
            data_type_id INTEGER NOT NULL REFERENCES data_types(data_type_id),
            component_id INTEGER NOT NULL REFERENCES machine_components(component_id),
            condition_name VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            sequence_number BIGINT,
            state_value TEXT,
            category VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS machine_samples (
            sample_id BIGSERIAL PRIMARY KEY,
            machine_id INTEGER NOT NULL REFERENCES machines(machine_id),
            data_type_id INTEGER NOT NULL REFERENCES data_types(data_type_id),
            component_id INTEGER NOT NULL REFERENCES machine_components(component_id),
            sample_name VARCHAR(150) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            sequence_number BIGINT,
            sample_value NUMERIC(20,6),
            sub_type VARCHAR(50),
            unit VARCHAR(20),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS machine_events (
            event_id BIGSERIAL PRIMARY KEY,
            machine_id INTEGER NOT NULL REFERENCES machines(machine_id),
            data_type_id INTEGER NOT NULL REFERENCES data_types(data_type_id),
            component_id INTEGER NOT NULL REFERENCES machine_components(component_id),
            event_name VARCHAR(150) NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            sequence_number BIGINT,
            event_value TEXT,
            event_type VARCHAR(50),
            severity INTEGER DEFAULT 1,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Metadata Tables
        CREATE TABLE IF NOT EXISTS data_processing_batches (
            batch_id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            machine_id INTEGER NOT NULL REFERENCES machines(machine_id),
            data_type_id INTEGER NOT NULL REFERENCES data_types(data_type_id),
            processing_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            machine_identifier VARCHAR(100) NOT NULL,
            total_json_files INTEGER NOT NULL DEFAULT 0,
            total_xml_files INTEGER NOT NULL DEFAULT 0,
            total_data_sources INTEGER NOT NULL DEFAULT 0,
            processing_version VARCHAR(20),
            data_source_range_start TIMESTAMP WITH TIME ZONE,
            data_source_range_end TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(file_name)
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_machine_conditions_timestamp ON machine_conditions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_machine_conditions_machine_time ON machine_conditions(machine_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_machine_samples_timestamp ON machine_samples(timestamp);
        CREATE INDEX IF NOT EXISTS idx_machine_samples_machine_time ON machine_samples(machine_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_machine_events_timestamp ON machine_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_machine_events_machine_time ON machine_events(machine_id, timestamp);
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(schema_sql)
            self.connection.commit()
            logger.info("Database schema created successfully")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to create schema: {e}")
            raise
        finally:
            cursor.close()
    
    def clear_all_data(self):
        """Clear all data in the correct order (respecting foreign key constraints)"""
        cursor = self.connection.cursor()
        
        try:
            # Delete in reverse dependency order
            tables_to_clear = [
                'machine_samples',
                'machine_conditions', 
                'machine_events',
                'machine_components',
                'machine_configurations',
                'machines',
                'component_types',
                'data_types'
            ]
            
            for table in tables_to_clear:
                cursor.execute(f"DELETE FROM {table}")
                logger.info(f"Cleared {table} table")
            
            self.connection.commit()
            logger.info("All data cleared successfully")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to clear data: {e}")
            raise
        finally:
            cursor.close()
    
    def load_reference_data(self):
        """Load reference data (data types and component types)"""
        try:
            cursor = self.connection.cursor()
            
            # Insert data types
            data_types = [
                ('current', 'Real-time operational data', True),
                ('sample', 'Measurement and sensor samples', False)
            ]
            
            for data_type in data_types:
                cursor.execute("""
                    INSERT INTO data_types (data_type_name, description, is_realtime) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (data_type_name) 
                    DO UPDATE SET description = EXCLUDED.description, is_realtime = EXCLUDED.is_realtime
                """, data_type)
            
            # Insert component types
            component_types = [
                ('Adapter', 'Data collection adapter', 'Control'),
                ('Linear', 'Linear axis component', 'Mechanical'),
                ('Rotary', 'Rotary axis component', 'Mechanical'),
                ('Controller', 'Machine controller', 'Control'),
                ('Path', 'Path/program control', 'Control'),
                ('Axes', 'Axis system', 'Mechanical'),
                ('Coolant', 'Coolant system', 'Fluid'),
                ('Device', 'Generic device', 'System'),
                ('Electric', 'Electrical system', 'Electrical'),
                ('Hydraulic', 'Hydraulic system', 'Fluid'),
                ('Lubrication', 'Lubrication system', 'Fluid'),
                ('Pneumatic', 'Pneumatic system', 'Fluid'),
                ('Door', 'Safety door system', 'Safety'),
                ('Personnel', 'Personnel detection', 'Safety'),
                ('Stock', 'Material stock handling', 'Material'),
                ('Agent', 'Software agent', 'Software')
            ]
            
            for comp_type in component_types:
                cursor.execute("""
                    INSERT INTO component_types (type_name, description, category) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (type_name) 
                    DO UPDATE SET description = EXCLUDED.description, category = EXCLUDED.category
                """, comp_type)
            
            self.connection.commit()
            logger.info("Reference data loaded successfully")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to load reference data: {e}")
            raise
        finally:
            cursor.close()
    
    def extract_machine_info(self, machine_name: str) -> Tuple[str, str]:
        """Extract machine model and series from machine name"""
        # Parse machine names like 'mazak_1_vtc_200', 'mazak_3_350msy'
        parts = machine_name.split('_')
        if len(parts) >= 3:
            if len(parts) == 4:  # mazak_1_vtc_200
                series = parts[2].upper()
                model = f"{series}-{parts[3]}"
            else:  # mazak_3_350msy
                model = parts[2].upper()
                series = model
        else:
            model = machine_name.upper()
            series = model
        
        return model, series
    
    def load_machines_data(self):
        """Load machines data from machines.csv"""
        file_path = self.data_directory / 'machines.csv'
        logger.info(f"Loading machines data from {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            cursor = self.connection.cursor()
            
            # Get unique machines (avoid duplicates)
            unique_machines = df.drop_duplicates(subset=['machine_name', 'device_uuid'])
            
            for _, row in tqdm(unique_machines.iterrows(), total=len(unique_machines), desc="Loading machines"):
                machine_model, machine_series = self.extract_machine_info(row['machine_name'])
                
                # Generate asset_id from machine name
                asset_id = f"MZ-{machine_model.replace('-', '')}-{row['machine_name'].split('_')[1].zfill(3)}"
                
                cursor.execute("""
                    INSERT INTO machines (machine_name, machine_model, machine_series, device_name, device_uuid, asset_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (machine_name, device_uuid) DO NOTHING
                """, (
                    row['machine_name'],
                    machine_model,
                    machine_series,
                    row['device_name'],
                    row['device_uuid'],
                    asset_id
                ))
            
            self.connection.commit()
            logger.info(f"Loaded {len(unique_machines)} unique machines")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to load machines data: {e}")
            raise
        finally:
            cursor.close()
    
    def load_machine_configurations(self):
        """Load machine configurations from machines.csv"""
        file_path = self.data_directory / 'machines.csv'
        logger.info(f"Loading machine configurations from {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            cursor = self.connection.cursor()
            
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Loading configurations"):
                cursor.execute("""
                    INSERT INTO machine_configurations (machine_id, data_type_id, components_count)
                    SELECT m.machine_id, dt.data_type_id, %s
                    FROM machines m, data_types dt
                    WHERE m.machine_name = %s AND m.device_uuid = %s AND dt.data_type_name = %s
                    ON CONFLICT (machine_id, data_type_id) 
                    DO UPDATE SET components_count = EXCLUDED.components_count
                """, (
                    row['components_count'],
                    row['machine_name'],
                    row['device_uuid'],
                    row['data_type']
                ))
            
            self.connection.commit()
            logger.info(f"Loaded {len(df)} machine configurations")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to load machine configurations: {e}")
            raise
        finally:
            cursor.close()
    
    def load_components_data(self):
        """Load components data from components.csv"""
        file_path = self.data_directory / 'components.csv'
        logger.info(f"Loading components data from {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            cursor = self.connection.cursor()
            
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Loading components"):
                cursor.execute("""
                    INSERT INTO machine_components (
                        machine_id, data_type_id, component_identifier, component_type_id,
                        component_name, has_conditions, has_samples, has_events,
                        conditions_count, samples_count, events_count
                    )
                    SELECT m.machine_id, dt.data_type_id, %s, ct.component_type_id, %s, %s, %s, %s, %s, %s, %s
                    FROM machines m, data_types dt, component_types ct
                    WHERE m.machine_name = %s AND dt.data_type_name = %s AND ct.type_name = %s
                    ON CONFLICT (machine_id, data_type_id, component_identifier) 
                    DO UPDATE SET
                        component_name = EXCLUDED.component_name,
                        has_conditions = EXCLUDED.has_conditions,
                        has_samples = EXCLUDED.has_samples,
                        has_events = EXCLUDED.has_events,
                        conditions_count = EXCLUDED.conditions_count,
                        samples_count = EXCLUDED.samples_count,
                        events_count = EXCLUDED.events_count,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    row['component_id'],
                    row['component_name'],
                    row['has_conditions'],
                    row['has_samples'],
                    row['has_events'],
                    row['conditions_count'],
                    row['samples_count'],
                    row['events_count'],
                    row['machine_name'],
                    row['data_type'],
                    row['component_type']
                ))
            
            self.connection.commit()
            logger.info(f"Loaded {len(df)} components")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to load components data: {e}")
            raise
        finally:
            cursor.close()
    
    def load_time_series_data(self, table_name: str, csv_file: str, columns_mapping: Dict[str, str]):
        """Generic method to load time-series data"""
        file_path = self.data_directory / csv_file
        logger.info(f"Loading {table_name} data from {file_path}")
        
        try:
            # First, get total line count for progress tracking
            total_lines = sum(1 for _ in open(file_path)) - 1  # Subtract header
            logger.info(f"Processing {total_lines} rows from {csv_file}")
            
            # Create lookup cache for performance
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT m.machine_name, dt.data_type_name, mc.component_identifier,
                       mc.component_id, m.machine_id, dt.data_type_id
                FROM machine_components mc
                JOIN machines m ON mc.machine_id = m.machine_id
                JOIN data_types dt ON mc.data_type_id = dt.data_type_id
            """)
            
            # Build lookup dictionary for fast access
            lookup_cache = {}
            for row in cursor.fetchall():
                machine_name, data_type_name, component_identifier, component_id, machine_id, data_type_id = row
                key = (machine_name, data_type_name, component_identifier)
                lookup_cache[key] = (component_id, machine_id, data_type_id)
            
            logger.info(f"Built lookup cache with {len(lookup_cache)} entries")
            
            # Read CSV in chunks to handle large files
            chunk_size = 5000  # Reduced chunk size for better memory management
            total_rows = 0
            processed_rows = 0
            
            # Use tqdm with total count for accurate progress
            with tqdm(total=total_lines, desc=f"Loading {table_name}") as pbar:
                for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                    # Prepare data for bulk insert
                    data_rows = []
                    
                    for _, row in chunk.iterrows():
                        processed_rows += 1
                        
                        # Fast lookup using cache
                        key = (row['machine_name'], row['data_type'], row['component_id'])
                        if key in lookup_cache:
                            component_id, machine_id, data_type_id = lookup_cache[key]
                            
                            # Build row data based on columns mapping
                            row_data = [component_id, machine_id, data_type_id]
                            for csv_col, db_col in columns_mapping.items():
                                value = row[csv_col]
                                # Handle NULL/empty values
                                if pd.isna(value) or value == '':
                                    value = None
                                row_data.append(value)
                            
                            data_rows.append(tuple(row_data))
                        else:
                            logger.warning(f"No matching component found for: {key}")
                    
                    # Bulk insert
                    if data_rows:
                        columns = ['component_id', 'machine_id', 'data_type_id'] + list(columns_mapping.values())
                        
                        insert_sql = f"""
                            INSERT INTO {table_name} ({', '.join(columns)})
                            VALUES %s
                        """
                        
                        execute_values(cursor, insert_sql, data_rows, page_size=1000)
                        total_rows += len(data_rows)
                    
                    # Update progress bar
                    pbar.update(len(chunk))
                    
                    # Commit every few chunks to avoid long transactions
                    if processed_rows % (chunk_size * 5) == 0:
                        self.connection.commit()
            
            self.connection.commit()
            logger.info(f"Loaded {total_rows} rows into {table_name}")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to load {table_name} data: {e}")
            raise
        finally:
            cursor.close()
    
    def load_conditions_data(self):
        """Load conditions data from conditions.csv"""
        columns_mapping = {
            'condition_name': 'condition_name',
            'timestamp': 'timestamp',
            'sequence': 'sequence_number',
            'state': 'state_value',
            'category': 'category'
        }
        self.load_time_series_data('machine_conditions', 'conditions.csv', columns_mapping)
    
    def load_samples_data(self):
        """Load samples data from samples.csv"""
        columns_mapping = {
            'sample_name': 'sample_name',
            'timestamp': 'timestamp',
            'sequence': 'sequence_number',
            'value': 'sample_value',
            'sub_type': 'sub_type'
        }
        self.load_time_series_data('machine_samples', 'samples.csv', columns_mapping)
    
    def load_events_data(self):
        """Load events data from events.csv"""
        columns_mapping = {
            'event_name': 'event_name',
            'timestamp': 'timestamp',
            'sequence': 'sequence_number',
            'value': 'event_value'
        }
        self.load_time_series_data('machine_events', 'events.csv', columns_mapping)
    
    def load_metadata(self):
        """Load processing metadata from metadata.csv"""
        file_path = self.data_directory / 'metadata.csv'
        logger.info(f"Loading metadata from {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            cursor = self.connection.cursor()
            
            for _, row in tqdm(df.iterrows(), total=len(df), desc="Loading metadata"):
                cursor.execute("""
                    INSERT INTO data_processing_batches (
                        file_name, machine_id, data_type_id, processing_timestamp,
                        machine_identifier, total_json_files, total_xml_files, total_data_sources
                    )
                    SELECT %s, m.machine_id, dt.data_type_id, %s, %s, %s, %s, %s
                    FROM machines m, data_types dt
                    WHERE m.machine_name = %s AND dt.data_type_name = %s
                    ON CONFLICT (file_name) DO NOTHING
                """, (
                    row['file_name'],
                    row['created_at'],
                    row['machine_id'],
                    row['total_json_files'],
                    row['total_xml_files'],
                    row['total_data_sources'],
                    row['machine_name'],
                    row['data_type']
                ))
            
            self.connection.commit()
            logger.info(f"Loaded {len(df)} metadata records")
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to load metadata: {e}")
            raise
        finally:
            cursor.close()
    
    def create_views(self):
        """Create analytical views for dashboard use"""
        views_sql = """
        -- Real-time Machine Status View
        CREATE OR REPLACE VIEW v_machine_status AS
        SELECT DISTINCT ON (m.machine_id, dt.data_type_name)
            m.machine_id,
            m.machine_name,
            m.machine_model,
            m.asset_id,
            dt.data_type_name,
            mc.components_count,
            (SELECT MAX(timestamp) FROM machine_samples ms WHERE ms.machine_id = m.machine_id) as last_sample_time,
            (SELECT MAX(timestamp) FROM machine_events me WHERE me.machine_id = m.machine_id) as last_event_time,
            CASE 
                WHEN (SELECT MAX(timestamp) FROM machine_samples ms WHERE ms.machine_id = m.machine_id) > CURRENT_TIMESTAMP - INTERVAL '5 minutes' 
                THEN 'ONLINE'
                WHEN (SELECT MAX(timestamp) FROM machine_samples ms WHERE ms.machine_id = m.machine_id) > CURRENT_TIMESTAMP - INTERVAL '1 hour'
                THEN 'IDLE'
                ELSE 'OFFLINE'
            END as connection_status
        FROM machines m
        LEFT JOIN machine_configurations mc ON m.machine_id = mc.machine_id
        LEFT JOIN data_types dt ON mc.data_type_id = dt.data_type_id
        WHERE m.is_active = TRUE AND mc.is_active = TRUE;
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(views_sql)
            self.connection.commit()
            logger.info("Analytical views created successfully")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to create views: {e}")
            raise
        finally:
            cursor.close()
    
    def run_full_load(self):
        """Execute the complete data loading process"""
        start_time = datetime.now()
        logger.info("Starting full data load process")
        
        try:
            self.connect()
            
            # Step 1: Create schema
            logger.info("Step 1: Creating database schema")
            self.create_schema()
            
            # Step 1.5: Clear all existing data
            logger.info("Step 1.5: Clearing existing data")
            self.clear_all_data()
            
            # Step 2: Load reference data
            logger.info("Step 2: Loading reference data")
            self.load_reference_data()
            
            # Step 3: Load machines
            logger.info("Step 3: Loading machines data")
            self.load_machines_data()
            
            # Step 4: Load machine configurations
            logger.info("Step 4: Loading machine configurations")
            self.load_machine_configurations()
            
            # Step 5: Load components
            logger.info("Step 5: Loading components data")
            self.load_components_data()
            
            # Step 6: Load time-series data
            logger.info("Step 6: Loading conditions data")
            self.load_conditions_data()
            
            logger.info("Step 7: Loading samples data")
            self.load_samples_data()
            
            logger.info("Step 8: Loading events data")
            self.load_events_data()
            
            # Step 7: Load metadata
            logger.info("Step 9: Loading metadata")
            self.load_metadata()
            
            # Step 8: Create views
            logger.info("Step 10: Creating analytical views")
            self.create_views()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"Data loading completed successfully in {duration}")
            logger.info("Database is ready for dashboard integration!")
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            raise
        finally:
            self.disconnect()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Load Mazak manufacturing data into PostgreSQL')
    parser.add_argument(
        '--data-dir',
        required=True,
        help='Path to the processed data directory containing CSV files'
    )
    parser.add_argument(
        '--db-host',
        default=os.getenv('PGHOST', 'localhost'),
        help='Database host (default: PGHOST env var or localhost)'
    )
    parser.add_argument(
        '--db-port',
        default=os.getenv('PGPORT', '5432'),
        help='Database port (default: PGPORT env var or 5432)'
    )
    parser.add_argument(
        '--db-name',
        default=os.getenv('PGDATABASE', 'mazak_manufacturing'),
        help='Database name (default: PGDATABASE env var or mazak_manufacturing)'
    )
    parser.add_argument(
        '--db-user',
        default=os.getenv('PGUSER', 'postgres'),
        help='Database user (default: PGUSER env var or postgres)'
    )
    parser.add_argument(
        '--db-password',
        default=os.getenv('PGPASSWORD'),
        help='Database password (default: PGPASSWORD env var)'
    )
    
    args = parser.parse_args()
    
    # Create database config
    db_config = DatabaseConfig(
        host=args.db_host,
        port=int(args.db_port),
        database=args.db_name,
        username=args.db_user,
        password=args.db_password or os.getenv('PGPASSWORD', 'password')
    )
    
    try:
        # Create and run data loader
        loader = MazakDataLoader(db_config, args.data_dir)
        loader.run_full_load()
        
        print("\n" + "="*60)
        print("🎉 DATA LOADING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Database: {db_config.database}")
        print(f"Host: {db_config.host}:{db_config.port}")
        print("\nYour Mazak manufacturing database is now ready!")
        print("You can now connect your dashboard to the database.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()