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
    """
    Standard DTW implementation to find the optimal alignment path.
    """
    n, m = len(series_a), len(series_b)
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Distance calculation between features
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

def process_directory(directory_path: str):
    # 1. Setup Output Directory
    output_folder = os.path.join(directory_path, "Aligned_Results")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. Find and sort files based on "ILI_year_formatted.csv" pattern
    # Regex extracts the digits between 'ILI_' and '_formatted' 
    file_paths = glob.glob(os.path.join(directory_path, "ILI_*_formatted.csv"))
    if not file_paths:
        return "Error: No files matching 'ILI_year_formatted.csv' found."

    file_metadata = []
    for fp in file_paths:
        match = re.search(r'ILI_(\d+)_formatted\.csv', os.path.basename(fp))
        if match:
            year = int(match.group(1))
            file_metadata.append({'path': fp, 'year': year})
    
    # Sort files chronologically by the extracted year
    sorted_files = sorted(file_metadata, key=lambda x: x['year'])
    
    # 3. Establish Baseline (First Chronological Year)
    baseline_info = sorted_files[0]
    baseline_df = pd.read_csv(baseline_info['path'])
    
    # Track anomalies identified by feature_id
    master_df = baseline_df[baseline_df['feature_id'].notnull()].copy()
    
    # Starting 'real_log_dist' is the cumulative distance in the first run
    master_df['real_log_dist'] = master_df['log_dist'].cumsum()

    # 4. Iterate and Align via DTW
    for file_info in sorted_files[1:]:
        current_year = file_info['year']
        current_df = pd.read_csv(file_info['path'])
        
        # Prepare signals for physical matching (elevation and rotation)
        base_signal = baseline_df[['elevation', 'rotation']].values
        curr_signal = current_df[['elevation', 'rotation']].values
        
        # Run DTW to align the whole pipeline run
        path = compute_custom_dtw(base_signal, curr_signal)
        mapping = dict(path) 

        year_suffix = f"_{current_year}"
        
        def get_curr_val(base_idx, col):
            curr_idx = mapping.get(base_idx)
            if curr_idx is not None and curr_idx < len(current_df):
                return current_df.iloc[curr_idx][col]
            return np.nan

        # Map current year data back to the original anomaly list
        master_df[f'rotation{year_suffix}'] = [get_curr_val(i, 'rotation') for i in master_df.index]
        master_df[f'elevation{year_suffix}'] = [get_curr_val(i, 'elevation') for i in master_df.index]
        master_df[f'j_len{year_suffix}'] = [get_curr_val(i, 'j_len') for i in master_df.index]
        
        # Update Real-position: Accumulated log_dist from the matched positions
        current_log_distances = [get_curr_val(i, 'log_dist') for i in master_df.index]
        master_df[f'log_dist{year_suffix}'] = np.cumsum(np.nan_to_num(current_log_distances))

    # 5. Save to the organized folder
    pipeline_id = os.path.basename(directory_path.rstrip(os.sep))
    final_filename = f"Master_Alignment_{pipeline_id}.csv"
    final_output_path = os.path.join(output_folder, final_filename)
    
    master_df.to_csv(final_output_path, index=False)

    return f"Success! Master file created: {final_output_path}"


#C:/Users/marcj/Documents (Computer)/TAMU/Hackathon/tidalhack-2026/
file_dir = "data/"

print(process_directory(file_dir))