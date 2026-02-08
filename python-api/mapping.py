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
''' 


'''
@param file directory of formatted csv files taken for a single pipeline 
@return new formatted data file with added values of j_len, log_dist, elevation, and rotation
'''
# def process_directory(directory_path: str):
#     # find all csv files relevant within the directory (all properly formatted paths)

#     # sort the list of files in the directory by year (not sorted in the file name and must be found)

#     # create a list of all anomalies found in the first year (determined by the "feature_id")

#     # iterate through the following years into the next year (works solely new file by new file)

#         # match all current anomalies from the first year into the next year using DTW (this is it's joint length)
#         # match all the rotation of each anomaly, should be approximated from using DTW
#         # match all points the elevation of an anomaly is found
#         # match it's log_dist as it's current_dist(?) from the starting position by adding up all new positions to current

#     # create a master table of all current pipelines into a new file

#     return

def compute_custom_dtw(series_a, series_b):
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
    # 1. Identify the Directory
    # If user passed a file, get the directory containing that file
    if os.path.isfile(input_path):
        target_dir = os.path.dirname(input_path)
    else:
        target_dir = input_path

    # Use absolute path to avoid confusion
    target_dir = os.path.abspath(target_dir)
    output_folder = os.path.join(target_dir, "Aligned_Results")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Find and sort files
    file_pattern = os.path.join(target_dir, "ILI_*_formatted.csv")
    file_paths = glob.glob(file_pattern)
    
    if not file_paths:
        return f"Error: No files matching 'ILI_year_formatted.csv' found in {target_dir}"

    file_metadata = []
    for fp in file_paths:
        match = re.search(r'ILI_(\d+)_formatted\.csv', os.path.basename(fp))
        if match:
            file_metadata.append({'path': fp, 'year': int(match.group(1))})
    
    sorted_files = sorted(file_metadata, key=lambda x: x['year'])
    
    # 3. Establish Baseline
    try:
        baseline_df = pd.read_csv(sorted_files[0]['path'])
    except PermissionError:
        return f"Permission Denied: Close {sorted_files[0]['path']} in Excel and try again."
    
    master_df = baseline_df[baseline_df['feature_id'].notnull()].copy()
    # Use 'distance' as the primary log position
    master_df['real_log_dist'] = master_df['distance']

    # 4. Iterate and Align
    for file_info in sorted_files[1:]:
        current_year = file_info['year']
        try:
            current_df = pd.read_csv(file_info['path'])
        except PermissionError:
            return f"Permission Denied: Close {file_info['path']} in Excel."
        
        # signal alignment using angle and elevation
        base_signal = baseline_df[['elevation', 'angle']].fillna(0).values
        curr_signal = current_df[['elevation', 'angle']].fillna(0).values
        
        path_indices = compute_custom_dtw(base_signal, curr_signal)
        mapping = dict(path_indices)
        year_suffix = f"_{current_year}"
        
        def get_curr_val(base_idx, col_name_in_csv):
            curr_idx = mapping.get(base_idx)
            if curr_idx is not None and curr_idx < len(current_df):
                return current_df.iloc[curr_idx][col_name_in_csv]
            return np.nan

        # Mapping the specific CSV columns to your desired Master Table headers
        # CSV 'angle' -> Master 'rotation'
        master_df[f'rotation{year_suffix}'] = [get_curr_val(i, 'angle') for i in master_df.index]
        
        # CSV 'elevation' -> Master 'elevation'
        master_df[f'elevation{year_suffix}'] = [get_curr_val(i, 'elevation') for i in master_df.index]
        
        # CSV 'length' -> Master 'j_len' (Joint Length)
        master_df[f'j_len{year_suffix}'] = [get_curr_val(i, 'length') for i in master_df.index]
        
        # CSV 'distance' -> Master 'log_dist'
        master_df[f'log_dist{year_suffix}'] = [get_curr_val(i, 'distance') for i in master_df.index]

        
    # 5. Save Results
    pipeline_id = os.path.basename(target_dir)
    final_path = os.path.join(output_folder, f"Master_Alignment_{pipeline_id}.csv")
    
    master_df.to_csv(final_path, index=False)
    return f"Success! Master file created at: {final_path}"

# --- Set your path here ---
# It's safer to point to the data directory itself
file_dir = "../data/" 

print(process_directory(file_dir))


#C:/Users/marcj/Documents (Computer)/TAMU/Hackathon/tidalhack-2026/
