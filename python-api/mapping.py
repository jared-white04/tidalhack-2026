import pandas as pd
import numpy as np
import os
import glob
import re

'''
Notes for the File:
This script aligns pipeline inspection data across multiple years (2007, 2015, 2022).
It aligns features to a 2007 baseline using Dynamic Time Warping (DTW).

ALIGNMENT STRATEGY:
1. Joint Length (j_len): The primary "fingerprint" of the pipe. Matches joints with similar physical lengths.
2. Relative Position: Matches defects based on where they fall within a joint (0-40ft).
3. Angle: Differentiates multiple defects at the same longitudinal position.
'''

def get_alignment_signal(df):
    """
    Extracts and normalizes features for DTW alignment.
    Prioritizes Joint Length (j_len) and Relative Position.
    """
    # 1. Joint Length (Primary Anchor)
    # Normalized by standard pipe length (approx 40ft)
    if 'j_len' in df.columns:
        j_len = df['j_len'].fillna(40.0).values / 40.0
    else:
        # Fallback if missing (should not happen with new files)
        j_len = np.ones(len(df))

    # 2. Relative Position (Secondary Anchor)
    # Position within the joint (0-1.0 scale)
    if 'relative_position' in df.columns:
        # Cap at 40 to prevent outliers from skewing
        rel_pos = np.clip(df['relative_position'].fillna(0).values, 0, 45) / 40.0
    else:
        rel_pos = np.zeros(len(df))

    # 3. Angle (Rotation) - Cyclic Normalization
    if 'angle' in df.columns:
        angle_rad = np.deg2rad(df['angle'].fillna(0).values)
        angle_sin = np.sin(angle_rad)
        angle_cos = np.cos(angle_rad)
    else:
        angle_sin = np.zeros(len(df))
        angle_cos = np.zeros(len(df))

    # Stack into a feature matrix (N x 4)
    # Weights: j_len (high), rel_pos (medium), angle (low)
    # We multiply columns to apply weights implicitly in Euclidean distance
    return np.column_stack([
        j_len * 2.0,      # High weight: Lengths must match
        rel_pos * 1.0,    # Medium weight: Position in joint must match
        angle_sin * 0.5,  # Low weight: Orientation helps disambiguate
        angle_cos * 0.5
    ])

def compute_custom_dtw(series_a, series_b):
    """
    Computes the optimal path between the baseline (A) and current run (B).
    Optimized with a window constraint to prevent impossible matches 
    (e.g. matching mile 1 to mile 50).
    """
    n, m = len(series_a), len(series_b)
    
    # Window size: Constraints matching to within ~500 features
    # This assumes defects don't shift position by more than 500 spots index-wise.
    window = 500
    
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0
    
    for i in range(1, n + 1):
        # Constrain j loop to valid window around i
        j_start = max(1, i - window)
        j_end = min(m + 1, i + window)
        
        for j in range(j_start, j_end):
            dist = np.linalg.norm(series_a[i-1] - series_b[j-1])
            cost_matrix[i, j] = dist + min(cost_matrix[i-1, j],    # Insertion
                                           cost_matrix[i, j-1],    # Deletion
                                           cost_matrix[i-1, j-1])  # Match

    # Backtracking
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        
        # Determine valid moves based on window
        candidates = []
        if i > 0 and j > 0: candidates.append((cost_matrix[i-1, j-1], 0)) # Match
        if i > 1:           candidates.append((cost_matrix[i-1, j], 1))   # Deletion (limit to prevent drift)
        if j > 1:           candidates.append((cost_matrix[i, j-1], 2))   # Insertion
        
        # Simple greedy choice
        best_move = min(candidates, key=lambda x: x[0])[1]
        
        if best_move == 0: i, j = i - 1, j - 1
        elif best_move == 1: i -= 1
        else: j -= 1
            
    return path[::-1]

def process_directory(script_path: str):
    # 1. Resolve Paths
    # Script is in .../python-api/
    # Data is in   .../data/
    
    current_dir = os.path.dirname(os.path.abspath(script_path))
    
    # Move up one level from 'python-api' to root, then down to 'data'
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    
    output_folder = os.path.join(data_dir, "Aligned_Results")
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    print(f"Reading data from: {data_dir}")
    print(f"Writing results to: {output_folder}")

    # 2. Collect Files
    file_paths = glob.glob(os.path.join(data_dir, "*.csv"))
    file_metadata = []

    for fp in file_paths:
        fname = os.path.basename(fp)
        m1 = re.search(r'ILI_(\d+)_formatted\.csv', fname)
        m2 = re.search(r'Cleaned_ILIDataV2-(\d+)\.csv', fname)
        
        if m1:
            file_metadata.append({'path': fp, 'year': int(m1.group(1)), 'type': 'formatted'})
        elif m2:
            file_metadata.append({'path': fp, 'year': int(m2.group(1)), 'type': 'cleaned'})

    # 3. Establish Anchor (2007 Formatted File)
    formatted_files = sorted([f for f in file_metadata if f['type'] == 'formatted'], key=lambda x: x['year'])
    if not formatted_files:
        return f"Error: No 'ILI_year_formatted.csv' files found in {data_dir}."

    baseline_info = formatted_files[0]
    print(f"Baseline established: {baseline_info['year']}")
    
    baseline_df = pd.read_csv(baseline_info['path'])
    baseline_signal = get_alignment_signal(baseline_df)

    # Initialize Master Table (Yellow Columns)
    master_df = baseline_df.copy()
    rename_map = {
        'feature_id': 'anomaly_no',
        'joint_number': 'joint_no',
        'distance': 'start_distance',
        'feature_type': 'anomaly_type'
    }
    master_df.rename(columns=rename_map, inplace=True)
    
    # Initialize Target Columns (Blue)
    for col in ['j_len', 'rotation', 'log_dist', 'elevation']:
        if col not in master_df.columns:
            master_df[col] = np.nan

    # 4. Schema Mapping (Target <- Source)
    schema_map = {
        'j_len': ('J. len [ft]', 'j_len'),
        'rotation': (None, 'angle'),
        'log_dist': ('log dist. [ft]', 'distance'),
        'elevation': ('Height [ft]', 'elevation')
    }

    # 5. Process Files
    sorted_all_files = sorted(file_metadata, key=lambda x: x['year'])

    for file_info in sorted_all_files:
        current_type = file_info['type']
        current_year = file_info['year']
        
        if current_year < baseline_info['year']:
            continue
            
        print(f"Aligning {current_year} ({current_type})...")
        current_df = pd.read_csv(file_info['path'])

        # Align signals
        curr_signal = get_alignment_signal(current_df)
        path_indices = compute_custom_dtw(baseline_signal, curr_signal)
        mapping = dict(path_indices)

        # Update Master Data
        for target_col, (clean_col, format_col) in schema_map.items():
            source_col = clean_col if current_type == 'cleaned' else format_col
            
            # Skip invalid columns or rotation for cleaned files
            if not source_col or source_col not in current_df.columns:
                continue
            if target_col == 'rotation' and current_type == 'cleaned':
                continue

            # Vectorized Update
            aligned_values = []
            for i in range(len(master_df)):
                match_idx = mapping.get(i)
                if match_idx is not None and match_idx < len(current_df):
                    aligned_values.append(current_df.iloc[match_idx][source_col])
                else:
                    aligned_values.append(master_df.iloc[i][target_col])
            
            master_df[target_col] = aligned_values

    # 6. Output
    final_path = os.path.join(output_folder, "Master_Alignment_Final.csv")
    final_cols = ['anomaly_no', 'joint_no', 'start_distance', 'anomaly_type', 
                  'j_len', 'log_dist', 'elevation', 'rotation']
    
    master_df = master_df[final_cols] if set(final_cols).issubset(master_df.columns) else master_df
    
    master_df.to_csv(final_path, index=False)
    return f"Success! Aligned data saved to: {final_path}"

# --- Execution ---
if __name__ == "__main__":
    # Pass the current file's path to resolve sibling directories correctly
    print(process_directory(__file__))
