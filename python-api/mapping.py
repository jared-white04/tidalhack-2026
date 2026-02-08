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

def compute_custom_dtw(series_a, series_b):
    """
    Standard Dynamic Time Warping with a window constraint.
    """
    n, m = len(series_a), len(series_b)
    window = 500 # constrain search window
    
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0
    
    for i in range(1, n + 1):
        j_start = max(1, i - window)
        j_end = min(m + 1, i + window)
        for j in range(j_start, j_end):
            dist = np.linalg.norm(series_a[i-1] - series_b[j-1])
            cost_matrix[i, j] = dist + min(cost_matrix[i-1, j], cost_matrix[i, j-1], cost_matrix[i-1, j-1])
            
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        candidates = []
        if i > 0 and j > 0: candidates.append((cost_matrix[i-1, j-1], 0)) 
        if i > 1:           candidates.append((cost_matrix[i-1, j], 1))   
        if j > 1:           candidates.append((cost_matrix[i, j-1], 2))   
        best_move = min(candidates, key=lambda x: x[0])[1]
        
        if best_move == 0: i, j = i - 1, j - 1
        elif best_move == 1: i -= 1
        else: j -= 1
            
    return path[::-1]

def process_directory(script_path: str):
    # 1. Setup Paths
    project_root = os.path.dirname(current_dir)
    data_dir = os.path.join(project_root, "data")
    output_folder = os.path.join(data_dir, "Aligned_Results")
    if not os.path.exists(output_folder): os.makedirs(output_folder)

    # 2. Collect Files
    file_paths = glob.glob(os.path.join(data_dir, "*.csv"))
    file_metadata = []
    for fp in file_paths:
        fname = os.path.basename(fp)
        m1 = re.search(r'ILI_(\d+)_formatted\.csv', fname)
        if m1:
            file_metadata.append({'path': fp, 'year': int(m1.group(1))})
            
    if not file_metadata: return "Error: No formatted ILI files found."
    
    sorted_files = sorted(file_metadata, key=lambda x: x['year'])
    
    # 3. Establish Baseline
    baseline_info = sorted_files[0]
    print(f"Baseline established: {baseline_info['year']}")
    baseline_df = pd.read_csv(baseline_info['path'])
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
    target_cols = ['confidence', 'severity', 'growth_rate', 'j_len', 'log_dist', 'elevation', 'rotation']
    for col in target_cols:
        if col not in master_df.columns: master_df[col] = np.nan

    # History dictionary to store multi-year data for scoring
    history = {i: {'j_len': [], 'log_dist': [], 'elevation': [], 'rotation': [], 
                   'depth': [], 'length': [], 'width': [], 'bool': [], 'year': [], 'rpr': []} 
               for i in range(len(master_df))}

    # 4. Process Every File
    for file_info in sorted_files:
        current_year = file_info['year']
        current_df = pd.read_csv(file_info['path'])
        print(f"Aligning {current_year}...")

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
        else:
            curr_signal = get_alignment_signal(current_df)
            path_indices = compute_custom_dtw(baseline_signal, curr_signal)
            mapping = dict(path_indices)
        
        # Update Master Data & History
        for i in range(len(master_df)):
            match_idx = mapping.get(i)
            
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
                history[i]['bool'].append(False)

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
    
    # Select columns (excluding persistence)
    final_cols = ['anomaly_no', 'joint_no', 'start_distance', 'anomaly_type', 
                  'confidence', 'severity', 'growth_rate', 'viewed',
                  'j_len', 'log_dist', 'elevation', 'rotation']
    
    # Append any extra green columns if they exist
    extra_cols = ['internal', 'ml_depth', 'ml_depth_lenth', 'width', 'mod_b31g']
    for c in extra_cols:
        if c in master_df.columns: final_cols.append(c)
        
    master_df = master_df[final_cols]
    master_df.to_csv(final_path, index=False)
    
    return f"Success! Results saved to: {final_path}"

if __name__ == "__main__":
    print(process_directory(__file__))