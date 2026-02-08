import pandas as pd
import numpy as np
import os
import glob
import re
import sys

# Add the current directory to sys.path to ensure we can import the sibling file
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import functions from your existing 'anomaly_score.py' file
try:
    from anomaly_score import calculate_confidence_score, calculate_severity_score, calculate_growth_rate
except ImportError:
    print("Error: Could not import 'anomaly_score.py'. Ensure it is in the same directory.")
    sys.exit(1)

# --- ALIGNMENT LOGIC ---

def get_alignment_signal(df):
    """
    Extracts and normalizes features for DTW alignment.
    """
    # 1. Joint Length (Primary Feature)
    if 'j_len' in df.columns:
        j_len = df['j_len'].fillna(40.0).values / 40.0
    else:
        j_len = np.ones(len(df))

    # 2. Relative Position (Secondary Feature)
    if 'relative_position' in df.columns:
        rel_pos = np.clip(df['relative_position'].fillna(0).values, 0, 45) / 40.0
    else:
        rel_pos = np.zeros(len(df))

    # 3. Angle (Tertiary Feature)
    if 'angle' in df.columns:
        angle_rad = np.deg2rad(df['angle'].fillna(0).values)
        angle_sin = np.sin(angle_rad)
        angle_cos = np.cos(angle_rad)
    else:
        angle_sin = np.zeros(len(df))
        angle_cos = np.zeros(len(df))

    return np.column_stack([
        j_len * 2.0,      # Weight 2.0
        rel_pos * 1.0,    # Weight 1.0
        angle_sin * 0.5,  # Weight 0.5
        angle_cos * 0.5
    ])

def compute_custom_dtw(series_a, series_b, max_distance_threshold=2.0):
    """
    Dynamic Time Warping with a window constraint and distance threshold.
    Returns a mapping dict where keys are baseline indices and values are matched indices.
    If no good match exists (distance > threshold), the key won't be in the dict.
    """
    n, m = len(series_a), len(series_b)
    window = 500  # constrain search window
    
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0
    
    for i in range(1, n + 1):
        j_start = max(1, i - window)
        j_end = min(m + 1, i + window)
        for j in range(j_start, j_end):
            dist = np.linalg.norm(series_a[i-1] - series_b[j-1])
            cost_matrix[i, j] = dist + min(cost_matrix[i-1, j], cost_matrix[i, j-1], cost_matrix[i-1, j-1])
    
    # Backtrack to find path
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        # path.append((i - 1, j - 1))
        candidates = []
        if i > 0 and j > 0: candidates.append((cost_matrix[i-1, j-1], 0)) 
        if i > 1:           candidates.append((cost_matrix[i-1, j], 1))   
        if j > 1:           candidates.append((cost_matrix[i, j-1], 2))   
        
        best_move = min(candidates, key=lambda x: x[0])[1]
        print("best_move: " + str(best_move))

        if best_move > 8:
            continue 
        
        path.append((i - 1, j - 1))

        if best_move == 0: i, j = i - 1, j - 1
        elif best_move == 1: i -= 1
        else: j -= 1
    
    path = path[::-1]
    
    # Filter path by distance threshold
    # Only keep mappings where the actual feature distance is below threshold
    filtered_mapping = {}
    for baseline_idx, current_idx in path:
        dist = np.linalg.norm(series_a[baseline_idx] - series_b[current_idx])
        if dist <= max_distance_threshold:
            # Only keep the mapping if it's the best match for this baseline index
            # (DTW can map multiple baseline points to same current point)
            if baseline_idx not in filtered_mapping:
                filtered_mapping[baseline_idx] = current_idx
    
    return filtered_mapping

def process_directory(script_path: str):
    # 1. Setup Paths
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data", "formatted_files")
    output_folder = os.path.join(project_root, "data", "Aligned_Results")
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    # 2. Collect Files
    file_paths = glob.glob(os.path.join(data_dir, "*.csv"))
    file_metadata = []
    for fp in file_paths:
        fname = os.path.basename(fp)
        # Match pattern: ILI_YYYY_formatted.csv
        m1 = re.search(r'ILI_(\d{4})_formatted\.csv', fname)
        if m1:
            file_metadata.append({'path': fp, 'year': int(m1.group(1))})
            print(f"Found file: {fname} (Year: {m1.group(1)})")
            
    if not file_metadata: 
        print(f"Error: No formatted ILI files found in {data_dir}")
        return "Error: No formatted ILI files found."
    
    sorted_files = sorted(file_metadata, key=lambda x: x['year'])
    print(f"\nProcessing {len(sorted_files)} files in chronological order:")
    for f in sorted_files:
        print(f"  - {os.path.basename(f['path'])} ({f['year']})")
    print()
    
    # 3. Establish Baseline
    baseline_info = sorted_files[0]
    print(f"=== Baseline established: {baseline_info['year']} ===")
    print(f"Loading baseline from: {os.path.basename(baseline_info['path'])}\n")
    baseline_df = pd.read_csv(baseline_info['path'])
    print(f"Baseline contains {len(baseline_df)} anomalies")
    baseline_signal = get_alignment_signal(baseline_df)
    
    master_df = baseline_df.copy()
    
    # Rename Baseline Columns for the Final Table
    rename_map = {
        'feature_id': 'anomaly_no', 
        'joint_number': 'joint_no',
        'distance': 'start_distance', # Baseline distance stays as 'start_distance'
        'feature_type': 'anomaly_type',
        'depth_percent': 'ml_depth', 
        'length': 'ml_depth_lenth'
    }
    master_df.rename(columns=rename_map, inplace=True)
    
    # Initialize Target Columns
    # log_dist and rotation are initialized as NaN, to be filled by the latest aligned data
    target_cols = ['confidence', 'severity', 'persistence', 'growth_rate', 'j_len', 'log_dist', 'elevation', 'rotation']
    target_cols = ['confidence', 'severity', 'persistence', 'growth_rate', 'j_len', 'log_dist', 'elevation', 'rotation']
    for col in target_cols:
        if col not in master_df.columns: master_df[col] = np.nan

    # History dictionary to store multi-year data for scoring
    history = {i: {'j_len': [], 'log_dist': [], 'elevation': [], 'rotation': [], 
                   'depth': [], 'length': [], 'width': [], 'bool': [], 'year': [], 'rpr': []} 
               for i in range(len(master_df))}

    # 4. Process Every File
    # Track which current-year indices have been mapped to avoid duplicates
    mapped_indices_per_year = {}
    
    for file_info in sorted_files:
        current_year = file_info['year']
        current_df = pd.read_csv(file_info['path'])
        print(f"\n=== Processing Year {current_year} ===")
        print(f"File: {os.path.basename(file_info['path'])}")
        print(f"Anomalies in this file: {len(current_df)}")

        # Determine RPR (Remaining Pipe Strength)
        # If mod_b31g exists, use it. Otherwise use (1 - depth) as a proxy.
        if 'mod_b31g' in current_df.columns:
            rpr_col = current_df['mod_b31g']
        else:
            depth_vals = current_df['depth_percent'].fillna(0) if 'depth_percent' in current_df.columns else np.zeros(len(current_df))
            rpr_col = 1.0 - depth_vals

        # Perform DTW Alignment
        if current_year == baseline_info['year']:
            mapping = {i: i for i in range(len(master_df))}
            print(f"Baseline year - direct 1:1 mapping ({len(mapping)} mappings)")
        else:
            curr_signal = get_alignment_signal(current_df)
            # Returns dict: baseline_idx -> current_idx (only for good matches)
            mapping = compute_custom_dtw(baseline_signal, curr_signal, max_distance_threshold=2.0)
            print(f"DTW alignment complete: {len(mapping)} matches found out of {len(master_df)} baseline anomalies")
        
        # Track which indices in current file have been mapped
        mapped_indices_per_year[current_year] = set(mapping.values())
        
        # Update Master Data & History
        for i in range(len(master_df)):
            match_idx = mapping.get(i)  # Will be None if no good match found
            
            if match_idx is not None and match_idx < len(current_df):
                row = current_df.iloc[match_idx]
                h = history[i]
                
                # Append to history for scoring
                h['year'].append(current_year)
                h['bool'].append(True)
                h['j_len'].append(row.get('j_len', row.get('length', 0))) # J_len
                h['log_dist'].append(row.get('distance', 0))              # Log_dist <- distance
                h['elevation'].append(row.get('elevation', 0))            # Elevation
                h['rotation'].append(row.get('angle', 0))                 # Rotation <- angle
                
                h['depth'].append(row.get('depth_percent', 0))
                h['length'].append(row.get('length', 0))
                h['width'].append(row.get('width', 0))
                h['rpr'].append(rpr_col[match_idx] if isinstance(rpr_col, (pd.Series, np.ndarray)) else 0)
                
                # Update Master Columns with the LATEST available data
                # We overwrite every time we find a match, so the final value is from the last seen year.
                master_df.at[i, 'j_len'] = row.get('j_len', np.nan)
                master_df.at[i, 'log_dist'] = row.get('distance', np.nan) # Ensure log_dist updates from distance
                master_df.at[i, 'elevation'] = row.get('elevation', np.nan)
                master_df.at[i, 'rotation'] = row.get('angle', np.nan)    # Ensure rotation updates from angle
                master_df.at[i, 'ml_depth'] = row.get('depth_percent', np.nan)
            else:
                # No match found for this baseline anomaly in current year
                h = history[i]
                h['year'].append(current_year)
                h['bool'].append(False)
                # Don't update any values - they remain as last known or NaN
    
    # 4b. Add new anomalies from the most recent file that weren't mapped
    most_recent_file = sorted_files[-1]
    most_recent_year = most_recent_file['year']
    most_recent_df = pd.read_csv(most_recent_file['path'])
    mapped_in_recent = mapped_indices_per_year[most_recent_year]
    
    print(f"\n=== Checking for new anomalies in {most_recent_year} ===")
    new_anomalies = []
    for idx in range(len(most_recent_df)):
        if idx not in mapped_in_recent:
            new_anomalies.append(idx)
    
    print(f"Found {len(new_anomalies)} new anomalies in {most_recent_year} that weren't in baseline")
    
    if new_anomalies:
        # Determine RPR for most recent file
        if 'mod_b31g' in most_recent_df.columns:
            rpr_col = most_recent_df['mod_b31g']
        else:
            depth_vals = most_recent_df['depth_percent'].fillna(0) if 'depth_percent' in most_recent_df.columns else np.zeros(len(most_recent_df))
            rpr_col = 1.0 - depth_vals
        
        for idx in new_anomalies:
            row = most_recent_df.iloc[idx]
            
            # Create new row for master_df
            new_row = {
                'anomaly_no': len(master_df) + 1,
                'joint_no': row.get('joint_number', np.nan),
                'start_distance': row.get('distance', np.nan),
                'anomaly_type': row.get('feature_type', 'Unknown'),
                'j_len': row.get('j_len', np.nan),
                'log_dist': row.get('distance', np.nan),
                'elevation': row.get('elevation', np.nan),
                'rotation': row.get('angle', np.nan),
                'ml_depth': row.get('depth_percent', np.nan),
                'ml_depth_lenth': row.get('length', np.nan),
                'width': row.get('width', np.nan),
                'internal': row.get('internal', np.nan),
                'mod_b31g': rpr_col[idx] if isinstance(rpr_col, (pd.Series, np.ndarray)) else np.nan,
            }
            
            # Add to master_df
            master_df = pd.concat([master_df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Create history entry for this new anomaly
            new_history_idx = len(history)
            history[new_history_idx] = {
                'year': [most_recent_year],
                'bool': [True],
                'j_len': [row.get('j_len', row.get('length', 0))],
                'log_dist': [row.get('distance', 0)],
                'elevation': [row.get('elevation', 0)],
                'rotation': [row.get('angle', 0)],
                'depth': [row.get('depth_percent', 0)],
                'length': [row.get('length', 0)],
                'width': [row.get('width', 0)],
                'rpr': [rpr_col[idx] if isinstance(rpr_col, (pd.Series, np.ndarray)) else 0]
            }

    # 5. Calculate Scores (Using imported functions)
    for i in range(len(master_df)):
        h = history[i]
        if not h['year']: continue
        
        # Confidence Score
        curr_depth = h['depth'][-1] if h['depth'] else 0
        conf = calculate_confidence_score(
            h['j_len'], h['log_dist'], h['elevation'], h['rotation'],
            curr_depth, h['bool']
        )
        master_df.at[i, 'confidence'] = round(conf, 4)
        
        # Severity Score
        sev = calculate_severity_score(h['rpr'], h['year'])
        master_df.at[i, 'severity'] = round(sev, 4)
        
        # Persistence (difference between first and last year anomaly appeared)
        years_with_anomaly = [h['year'][j] for j in range(len(h['year'])) if h['bool'][j]]
        if years_with_anomaly:
            persistence = years_with_anomaly[-1] - years_with_anomaly[0]
        else:
            persistence = 0
        master_df.at[i, 'persistence'] = persistence
        
        # Growth Rate
        if len(h['year']) >= 2:
            gr = calculate_growth_rate(
                h['depth'][0], h['depth'][-1],
                h['length'][0], h['length'][-1],
                h['width'][0], h['width'][-1],
                h['year'][-1] - h['year'][0]
            )
            # Clip negative growth to 0 (assuming defects don't heal)
            if gr < 0: gr = 0.0
            master_df.at[i, 'growth_rate'] = round(gr, 6)
        else:
            master_df.at[i, 'growth_rate'] = 0.0

        master_df.at[i, 'viewed'] = "Yes"

    # 6. Save Final Result
    final_path = os.path.join(output_folder, "Master_Alignment_Final.csv")
    
    # Close any open file handles and ensure we can write
    try:
        # Try to remove the file if it exists to avoid permission issues
        if os.path.exists(final_path):
            os.remove(final_path)
    except Exception as e:
        print(f"Warning: Could not remove existing file: {e}")
        # Try with a timestamped filename instead
        import time
        timestamp = int(time.time())
        final_path = os.path.join(output_folder, f"Master_Alignment_Final_{timestamp}.csv")
        print(f"Using alternate filename: {final_path}")
    
    # Select columns (including persistence)
    final_cols = ['anomaly_no', 'joint_no', 'start_distance', 'anomaly_type', 
                  'confidence', 'severity', 'persistence', 'growth_rate', 'viewed',
                  'confidence', 'severity', 'persistence', 'growth_rate', 'viewed',
                  'j_len', 'log_dist', 'elevation', 'rotation']
    
    # Append any extra green columns if they exist
    extra_cols = ['internal', 'ml_depth', 'ml_depth_lenth', 'width', 'mod_b31g']
    for c in extra_cols:
        if c in master_df.columns: final_cols.append(c)
    
    # Ensure anomaly_no is properly formatted (convert any strings to sequential numbers)
    master_df['anomaly_no'] = range(1, len(master_df) + 1)
    
    master_df = master_df[final_cols]
    master_df.to_csv(final_path, index=False)
    
    print(f"\n{'='*60}")
    print(f"SUCCESS! Alignment complete.")
    print(f"{'='*60}")
    print(f"Total anomalies tracked: {len(master_df)}")
    print(f"Output saved to: {final_path}")
    print(f"{'='*60}\n")
    
    return f"Success! Results saved to: {final_path}"


if __name__ == "__main__":
    print(process_directory(__file__))