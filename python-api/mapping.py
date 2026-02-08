import pandas as pd
import numpy as np
import os
import glob
import re

'''
Notes for the File
all imports above will be used and more may be added
the process_directory is the main channel by which the files are utilized in matching anomalies between years

No Specified Naming Convention for name file 
Below is the columns and rows for each assigned file in the given file directory sent to this file
,feature_id,distance,odometer,joint_number,relative_position,angle,feature_type,depth_percent,length,width,wall_thickness,weld_type,elevation
24,C-70,125.12,125.12,70.0,21.69,272.0,Cluster,0.16,3.55,2.64,0.344,,

Also calls onto data type: "Cleaned_ILIDataV2-2022.csv for data like j_len, and log_dist. Elevation will come in dates later than 2007 (i.e. 2015 and 2022)
''' 


'''
Further Notes:
How it compares and aggregates across the directory:
File Gathering: glob.glob(os.path.join(target_dir, "*.csv")) finds every single CSV file in your folder.

Chronological Sort: The code uses Regex to extract the years and sorts the entire list of files (both Cleaned and Formatted) from oldest to newest.

The Anchor: It sets the oldest formatted file as the baseline_signal. This is the "map" that all other files must match.

The Comparative Loop: for file_info in sorted_all_files: iterates through every year. For each file:

It runs a new DTW calculation comparing that specific year's elevation profile to the baseline.

It identifies the exact row in the new file that corresponds to your baseline anomalies.

It updates the j_len, rotation, log_dist, and elevation columns with the data from that file.
'''

def compute_custom_dtw(series_a, series_b):
    """
    Computes the optimal path between the baseline (A) and current run (B).
    """
    n, m = len(series_a), len(series_b)
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist = np.linalg.norm(series_a[i-1] - series_b[j-1])
            cost_matrix[i, j] = dist + min(cost_matrix[i-1, j], 
                                           cost_matrix[i, j-1], 
                                           cost_matrix[i-1, j-1])
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        option = np.argmin([cost_matrix[i-1, j-1], cost_matrix[i-1, j], cost_matrix[i, j-1]])
        if option == 0: i, j = i - 1, j - 1
        elif option == 1: i -= 1
        else: j -= 1
    return path[::-1]

def process_directory(input_path: str):
    target_dir = os.path.abspath(os.path.dirname(input_path) if os.path.isfile(input_path) else input_path)
    output_folder = os.path.join(target_dir, "Aligned_Results")
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    # 1. Collect and Identify all files in the directory
    file_paths = glob.glob(os.path.join(target_dir, "*.csv"))
    file_metadata = []
    for fp in file_paths:
        fname = os.path.basename(fp)
        m1 = re.search(r'ILI_(\d+)_formatted\.csv', fname)
        m2 = re.search(r'Cleaned_ILIDataV2-(\d+)\.csv', fname)
        if m1:
            file_metadata.append({'path': fp, 'year': int(m1.group(1)), 'type': 'formatted'})
        elif m2:
            file_metadata.append({'path': fp, 'year': int(m2.group(1)), 'type': 'cleaned'})

    # 2. Establish Anchor (The chronologically first 'formatted' file)
    formatted_files = sorted([f for f in file_metadata if f['type'] == 'formatted'], key=lambda x: x['year'])
    if not formatted_files:
        return "Error: No 'ILI_year_formatted.csv' found to anchor features."
    
    baseline_info = formatted_files[0]
    baseline_df = pd.read_csv(baseline_info['path'])
    baseline_signal = baseline_df[['elevation']].fillna(0).values

    # Initialize Master Table with baseline features
    master_df = baseline_df[baseline_df['feature_id'].notnull()].copy()
    
    # Initialize generalized columns
    master_df['j_len'] = np.nan
    master_df['rotation'] = np.nan
    master_df['log_dist'] = np.nan
    master_df['elevation'] = np.nan

    # 3. Define Schema Mapping
    schema_map = {
        'j_len': ('J. len [ft]', 'length'),
        'rotation': (None, 'angle'), 
        'log_dist': ('log dist. [ft]', 'distance'),
        'elevation': ('Height [ft]', 'elevation')
    }

    # 4. Process Every File Chronologically (Matching each to Baseline)
    sorted_all_files = sorted(file_metadata, key=lambda x: x['year'])
    
    for file_info in sorted_all_files:
        current_type = file_info['type']
        current_year = file_info['year']
        current_df = pd.read_csv(file_info['path'])
        
        # Determine current signal column for DTW
        elev_col = 'Height [ft]' if current_type == 'cleaned' else 'elevation'
        if elev_col not in current_df.columns: 
            continue

        # PERFORM DTW: Align current file to the original Baseline signal
        curr_signal = current_df[[elev_col]].fillna(0).values
        path_indices = compute_custom_dtw(baseline_signal, curr_signal)
        mapping = dict(path_indices)

        # Update Generalized Columns based on matching results
        for target_col, (clean_col, format_col) in schema_map.items():
            # Source selection
            source_col = clean_col if current_type == 'cleaned' else format_col
            
            # Skip rotation if it's a cleaned file
            if target_col == 'rotation' and current_type == 'cleaned':
                continue
            
            if source_col and source_col in current_df.columns:
                def get_val(base_idx):
                    curr_idx = mapping.get(base_idx)
                    return current_df.iloc[curr_idx][source_col] if curr_idx is not None else np.nan

                # Overwrite master columns with latest matches from this specific year
                master_df[target_col] = [get_val(idx) for idx in master_df.index]

    # 5. Save Results
    final_path = os.path.join(output_folder, "Master_Alignment_Longitudinal.csv")
    master_df.to_csv(final_path, index=False)
    return f"Success! Longitudinal Generalized Master file created at: {final_path}"

# --- Set your path here ---
# It's safer to point to the data directory itself
file_dir = "../data/" 

print(process_directory(file_dir))
