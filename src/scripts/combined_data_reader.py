"""
Combined Data Reader for Machine Observability
==============================================

This script reads the combined JSON data files and converts them into structured
DataFrames suitable for database operations. It handles the complex nested structure
of machine data including metadata, conditions, samples, and events.

Author: Generated for machine observability project
Date: 2025-07-07
"""

import json
import pandas as pd
import os
import glob
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CombinedDataReader:
    """
    A class to read and process combined machine data JSON files into structured DataFrames.
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize the data reader with the directory containing combined JSON files.
        
        Args:
            data_directory (str): Path to the directory containing combined JSON files
        """
        self.data_directory = data_directory
        self.metadata_df = None
        self.conditions_df = None
        self.samples_df = None
        self.events_df = None
        self.machines_df = None
        self.components_df = None
        
    def get_json_files(self) -> List[str]:
        """
        Get all JSON files from the combined data directory.
        
        Returns:
            List[str]: List of JSON file paths
        """
        pattern = os.path.join(self.data_directory, "*.json")
        json_files = glob.glob(pattern)
        logger.info(f"Found {len(json_files)} JSON files in {self.data_directory}")
        return json_files
    
    def parse_machine_info(self, filename: str) -> Tuple[str, str, str]:
        """
        Parse machine information from filename.
        
        Args:
            filename (str): The JSON filename
            
        Returns:
            Tuple[str, str, str]: machine_name, data_type, timestamp
        """
        basename = os.path.basename(filename)
        # Expected format: mazak_1_vtc_200_current_merged_20250707_152414.json
        parts = basename.replace('.json', '').split('_')
        
        if 'current' in basename:
            machine_name = '_'.join(parts[:-4])  # mazak_1_vtc_200
            data_type = 'current'
            timestamp_part = parts[-2] + '_' + parts[-1]  # 20250707_152414
        elif 'sample' in basename:
            machine_name = '_'.join(parts[:-4])  # mazak_1_vtc_200
            data_type = 'sample'
            timestamp_part = parts[-2] + '_' + parts[-1]  # 20250707_152414
        else:
            # Fallback parsing
            machine_name = '_'.join(parts[:-3])
            data_type = parts[-3]
            timestamp_part = parts[-2] + '_' + parts[-1]
            
        return machine_name, data_type, timestamp_part
    
    def read_single_file(self, filepath: str) -> Dict:
        """
        Read and parse a single JSON file.
        
        Args:
            filepath (str): Path to the JSON file
            
        Returns:
            Dict: Parsed JSON data
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded {os.path.basename(filepath)}")
            return data
        except Exception as e:
            logger.error(f"Error reading {filepath}: {str(e)}")
            return {}
    
    def process_metadata(self, json_data: Dict, machine_name: str, data_type: str, 
                        filename: str) -> Dict:
        """
        Process metadata section of the JSON file.
        
        Args:
            json_data (Dict): The parsed JSON data
            machine_name (str): Machine identifier
            data_type (str): Type of data (current/sample)
            filename (str): Original filename
            
        Returns:
            Dict: Processed metadata
        """
        metadata = json_data.get('metadata', {})
        
        processed_metadata = {
            'file_name': os.path.basename(filename),
            'machine_name': machine_name,
            'data_type': data_type,
            'created_at': metadata.get('created_at'),
            'machine_id': metadata.get('machine_id'),
            'total_json_files': metadata.get('total_json_files', 0),
            'total_xml_files': metadata.get('total_xml_files', 0),
            'total_data_sources': len(metadata.get('data_sources', [])),
        }
        
        return processed_metadata
    
    def process_conditions(self, json_data: Dict, machine_name: str, data_type: str) -> List[Dict]:
        """
        Process conditions data from components.
        
        Args:
            json_data (Dict): The parsed JSON data
            machine_name (str): Machine identifier
            data_type (str): Type of data (current/sample)
            
        Returns:
            List[Dict]: List of condition records
        """
        conditions = []
        device = json_data.get('data', {}).get('device', {})
        components = device.get('components', {})
        
        for component_id, component_data in components.items():
            component_type = component_data.get('type', '')
            component_name = component_data.get('name', '')
            component_conditions = component_data.get('conditions', {})
            
            for condition_name, condition_data in component_conditions.items():
                condition_record = {
                    'machine_name': machine_name,
                    'data_type': data_type,
                    'component_id': component_id,
                    'component_type': component_type,
                    'component_name': component_name,
                    'condition_name': condition_name,
                    'timestamp': condition_data.get('timestamp'),
                    'sequence': condition_data.get('sequence'),
                    'state': condition_data.get('state'),
                    'category': condition_data.get('category'),
                }
                conditions.append(condition_record)
        
        return conditions
    
    def process_samples(self, json_data: Dict, machine_name: str, data_type: str) -> List[Dict]:
        """
        Process samples data from components.
        
        Args:
            json_data (Dict): The parsed JSON data
            machine_name (str): Machine identifier
            data_type (str): Type of data (current/sample)
            
        Returns:
            List[Dict]: List of sample records
        """
        samples = []
        device = json_data.get('data', {}).get('device', {})
        components = device.get('components', {})
        
        for component_id, component_data in components.items():
            component_type = component_data.get('type', '')
            component_name = component_data.get('name', '')
            component_samples = component_data.get('samples', {})
            
            for sample_name, sample_list in component_samples.items():
                if isinstance(sample_list, list):
                    for sample_data in sample_list:
                        sample_record = {
                            'machine_name': machine_name,
                            'data_type': data_type,
                            'component_id': component_id,
                            'component_type': component_type,
                            'component_name': component_name,
                            'sample_name': sample_name,
                            'timestamp': sample_data.get('timestamp'),
                            'sequence': sample_data.get('sequence'),
                            'value': sample_data.get('value'),
                            'sub_type': sample_data.get('subType'),
                        }
                        samples.append(sample_record)
        
        return samples
    
    def process_events(self, json_data: Dict, machine_name: str, data_type: str) -> List[Dict]:
        """
        Process events data from components.
        
        Args:
            json_data (Dict): The parsed JSON data
            machine_name (str): Machine identifier
            data_type (str): Type of data (current/sample)
            
        Returns:
            List[Dict]: List of event records
        """
        events = []
        device = json_data.get('data', {}).get('device', {})
        components = device.get('components', {})
        
        for component_id, component_data in components.items():
            component_type = component_data.get('type', '')
            component_name = component_data.get('name', '')
            component_events = component_data.get('events', {})
            
            for event_name, event_list in component_events.items():
                if isinstance(event_list, list):
                    for event_data in event_list:
                        event_record = {
                            'machine_name': machine_name,
                            'data_type': data_type,
                            'component_id': component_id,
                            'component_type': component_type,
                            'component_name': component_name,
                            'event_name': event_name,
                            'timestamp': event_data.get('timestamp'),
                            'sequence': event_data.get('sequence'),
                            'value': event_data.get('value'),
                        }
                        events.append(event_record)
        
        return events
    
    def process_components(self, json_data: Dict, machine_name: str, data_type: str) -> List[Dict]:
        """
        Process component information.
        
        Args:
            json_data (Dict): The parsed JSON data
            machine_name (str): Machine identifier
            data_type (str): Type of data (current/sample)
            
        Returns:
            List[Dict]: List of component records
        """
        components = []
        device = json_data.get('data', {}).get('device', {})
        device_components = device.get('components', {})
        
        for component_id, component_data in device_components.items():
            component_record = {
                'machine_name': machine_name,
                'data_type': data_type,
                'component_id': component_id,
                'component_type': component_data.get('type', ''),
                'component_name': component_data.get('name', ''),
                'has_conditions': bool(component_data.get('conditions', {})),
                'has_samples': bool(component_data.get('samples', {})),
                'has_events': bool(component_data.get('events', {})),
                'conditions_count': len(component_data.get('conditions', {})),
                'samples_count': sum(len(v) if isinstance(v, list) else 0 
                                   for v in component_data.get('samples', {}).values()),
                'events_count': sum(len(v) if isinstance(v, list) else 0 
                                  for v in component_data.get('events', {}).values()),
            }
            components.append(component_record)
        
        return components
    
    def process_machines(self, json_data: Dict, machine_name: str, data_type: str) -> Dict:
        """
        Process machine-level information.
        
        Args:
            json_data (Dict): The parsed JSON data
            machine_name (str): Machine identifier
            data_type (str): Type of data (current/sample)
            
        Returns:
            Dict: Machine record
        """
        device = json_data.get('data', {}).get('device', {})
        
        machine_record = {
            'machine_name': machine_name,
            'data_type': data_type,
            'device_name': device.get('name', ''),
            'device_uuid': device.get('uuid', ''),
            'components_count': len(device.get('components', {})),
        }
        
        return machine_record
    
    def read_all_files(self) -> None:
        """
        Read all JSON files and process them into DataFrames.
        """
        json_files = self.get_json_files()
        
        all_metadata = []
        all_conditions = []
        all_samples = []
        all_events = []
        all_components = []
        all_machines = []
        
        for filepath in json_files:
            logger.info(f"Processing {os.path.basename(filepath)}")
            
            # Parse machine info from filename
            machine_name, data_type, timestamp = self.parse_machine_info(filepath)
            
            # Read JSON data
            json_data = self.read_single_file(filepath)
            if not json_data:
                continue
            
            # Process each data type
            metadata = self.process_metadata(json_data, machine_name, data_type, filepath)
            all_metadata.append(metadata)
            
            conditions = self.process_conditions(json_data, machine_name, data_type)
            all_conditions.extend(conditions)
            
            samples = self.process_samples(json_data, machine_name, data_type)
            all_samples.extend(samples)
            
            events = self.process_events(json_data, machine_name, data_type)
            all_events.extend(events)
            
            components = self.process_components(json_data, machine_name, data_type)
            all_components.extend(components)
            
            machine = self.process_machines(json_data, machine_name, data_type)
            all_machines.append(machine)
        
        # Create DataFrames
        logger.info("Creating DataFrames...")
        
        self.metadata_df = pd.DataFrame(all_metadata)
        self.conditions_df = pd.DataFrame(all_conditions)
        self.samples_df = pd.DataFrame(all_samples)
        self.events_df = pd.DataFrame(all_events)
        self.components_df = pd.DataFrame(all_components)
        self.machines_df = pd.DataFrame(all_machines)
        
        # Convert timestamp columns
        self._convert_timestamps()
        
        logger.info("DataFrames created successfully!")
        self._print_summary()
    
    def _convert_timestamps(self) -> None:
        """Convert timestamp columns to proper datetime format."""
        timestamp_columns = {
            'metadata_df': ['created_at'],
            'conditions_df': ['timestamp'],
            'samples_df': ['timestamp'],
            'events_df': ['timestamp'],
        }
        
        for df_name, columns in timestamp_columns.items():
            df = getattr(self, df_name)
            if df is not None:
                for col in columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    def _print_summary(self) -> None:
        """Print summary of loaded data."""
        print("\n" + "="*60)
        print("DATA LOADING SUMMARY")
        print("="*60)
        
        dataframes = {
            'Metadata': self.metadata_df,
            'Machines': self.machines_df,
            'Components': self.components_df,
            'Conditions': self.conditions_df,
            'Samples': self.samples_df,
            'Events': self.events_df,
        }
        
        for name, df in dataframes.items():
            if df is not None:
                print(f"{name:12}: {len(df):8,} records")
            else:
                print(f"{name:12}: No data")
        
        print("\nMachine Summary:")
        if self.machines_df is not None:
            machine_summary = self.machines_df.groupby('machine_name')['data_type'].apply(list).to_dict()
            for machine, types in machine_summary.items():
                print(f"  {machine}: {', '.join(types)}")
        
        print("="*60)
    
    def get_dataframes(self) -> Dict[str, pd.DataFrame]:
        """
        Get all processed DataFrames.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of DataFrames
        """
        return {
            'metadata': self.metadata_df,
            'machines': self.machines_df,
            'components': self.components_df,
            'conditions': self.conditions_df,
            'samples': self.samples_df,
            'events': self.events_df,
        }
    
    def save_to_csv(self, output_directory: str) -> None:
        """
        Save all DataFrames to CSV files.
        
        Args:
            output_directory (str): Directory to save CSV files
        """
        os.makedirs(output_directory, exist_ok=True)
        
        dataframes = self.get_dataframes()
        
        for name, df in dataframes.items():
            if df is not None and not df.empty:
                output_path = os.path.join(output_directory, f"{name}.csv")
                df.to_csv(output_path, index=False)
                logger.info(f"Saved {name} to {output_path}")
        
        logger.info(f"All DataFrames saved to {output_directory}")
    
    def _prepare_for_parquet(self) -> None:
        """Prepare DataFrames for Parquet format by ensuring consistent data types for 'value' columns."""
        value_columns = {
            'samples_df': ['value'],
            'events_df': ['value'],
            'conditions_df': ['value'],
        }
        for df_name, columns in value_columns.items():
            df = getattr(self, df_name)
            if df is not None:
                for col in columns:
                    if col in df.columns:
                        df[col] = df[col].astype(str)

    def save_to_parquet(self, output_directory: str) -> None:
        """
        Save all DataFrames to Parquet files for better performance.
        
        Args:
            output_directory (str): Directory to save Parquet files
        """
        os.makedirs(output_directory, exist_ok=True)
        self._prepare_for_parquet()
        dataframes = self.get_dataframes()
        for name, df in dataframes.items():
            if df is not None and not df.empty:
                output_path = os.path.join(output_directory, f"{name}.parquet")
                df.to_parquet(output_path, index=False)
                logger.info(f"Saved {name} to {output_path}")
        logger.info(f"All DataFrames saved to {output_directory}")


def main():
    """
    Main function to demonstrate usage of the CombinedDataReader.
    """
    # Configuration
    data_directory = "src/data/combined"
    output_directory = "src/data/processed"
    
    # Initialize reader
    reader = CombinedDataReader(data_directory)
    
    # Read all files
    reader.read_all_files()
    
    # Get DataFrames for further processing
    dataframes = reader.get_dataframes()
    
    # Save to CSV and Parquet
    reader.save_to_csv(output_directory)
    reader.save_to_parquet(output_directory)
    
    # Example: Display first few rows of each DataFrame
    print("\n" + "="*60)
    print("SAMPLE DATA PREVIEW")
    print("="*60)
    
    for name, df in dataframes.items():
        if df is not None and not df.empty:
            print(f"\n{name.upper()} (first 3 rows):")
            print(df.head(3).to_string())
    
    return dataframes


if __name__ == "__main__":
    dataframes = main()