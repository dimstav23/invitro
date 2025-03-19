import os
import json
import csv
import time
from datetime import datetime, timedelta

def process_iat_files(directory_path, output_csv_path):
    """
    Process all iat*.json files in the given directory and create a CSV file
    with the format: app,func,end_timestamp,duration,memory
    Units Conversion:
    - IAT values are in microseconds, converted to seconds
    - Runtime values are in milliseconds, converted to seconds
    - Memory values are in megabytes
    
    All time values are converted to floating-point seconds with high precision.
    """
    # Create a list to store all records
    all_records = []
    
    # Set a common app identifier
    app_identifier = "serverless-app"
    
    # Get all iat*.json files
    iat_files = [f for f in os.listdir(directory_path) if f.startswith("iat") and f.endswith(".json")]
    
    for file_name in iat_files:
        # Extract function ID from filename (e.g., "iat0.json" -> "0")
        func_id = file_name.replace("iat", "").replace(".json", "")
        
        # Read the JSON file
        with open(os.path.join(directory_path, file_name), 'r') as f:
            data = json.load(f)
        
        # Extract IATs and RuntimeSpecification
        iats = data["IAT"]
        runtime_specs = data["RuntimeSpecification"]
        
        if iats == [] or runtime_specs == []:
            continue
        
        # Ensure we have matching IATs and runtime specs
        if len(iats) != len(runtime_specs):
            print(f"Warning: Mismatch in IATs and RuntimeSpecification counts in {file_name}")
            continue
        
        # Use 0 as the base timestamp (in seconds)
        current_timestamp_sec = 0.0
        
        # Process each invocation
        timestamp_sec = current_timestamp_sec
        for i in range(len(iats)):
            # Get runtime and memory values
            runtime_ms = runtime_specs[i]["Runtime"]  # in milliseconds
            memory_mb = runtime_specs[i]["Memory"]    # in megabytes
            
            # Convert runtime from ms to seconds
            runtime_sec = runtime_ms / 1000.0
            
            # Calculate timestamp: add previous IAT (converted from ns to sec)
            if i > 0:
                timestamp_sec += iats[i-1] / 1_000_000.0  # Convert microseconds to seconds
            
            # Calculate end timestamp with runtime added
            end_timestamp_sec = timestamp_sec + runtime_sec
            
            # Create a record
            record = {
                "app": app_identifier,
                "func": func_id,
                "end_timestamp": format(end_timestamp_sec, '.9f'),  # 9 decimal places for nanosecond precision
                "duration": format(runtime_sec, '.9f'),
                "memory": memory_mb
            }
            
            all_records.append(record)
    
    # Sort records by end_timestamp
    all_records.sort(key=lambda x: float(x["end_timestamp"]))
    
    # Write to CSV
    with open(output_csv_path, 'w', newline='') as csvfile:
        fieldnames = ["app", "func", "end_timestamp", "duration", "memory"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in all_records:
            writer.writerow(record)
    
    print(f"CSV file created at: {output_csv_path}")
    print(f"Processed {len(all_records)} invocations across {len(iat_files)} functions")

if __name__ == "__main__":
    # Directory containing the iat*.json files
    directory_path = "."  # Current directory, modify as needed
    
    # Output CSV file path
    output_csv_path = "function_invocations.csv"
    
    process_iat_files(directory_path, output_csv_path)