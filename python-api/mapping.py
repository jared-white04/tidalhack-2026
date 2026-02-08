import panda as pd
import numpy as np
import os
import glob





'''
Notes for the File
all imports above will be used and more may be added
the process_directory is the main channel by which the files are utilized in matching anomalies between years

Naming Convention
Year - Pipeline Name - 
''' 


'''
@param file directory of formatted csv files taken for a single pipeline 
@return new formatted data file with added values of j_len, log_dist, elevation, and rotation
'''
def process_directory(directory_path: str):
    # find all csv files relevant within the directory (all properly formatted paths)

    # sort the list of files in the directory by year

    # create a list of all anomalies found in the first year

    # iterate through the following years into the next year (works solely new file by new file)

        # match all current anomalies from the first year into the next year using DTW (this is it's joint length)
        # match all the rotation of each anomaly, should be approximated from using DTW
        # match all points the elevation of an anomaly is found
        # match it's log_dist as it's current_dist(?) from the starting position

    # create a master table of all current pipelines into a new file

    return





import pandas as pd
import numpy as np
import os
import glob

def compute_dtw_alignment(series_a, series_b):
    """
    Computes the DTW distance and path without external libraries.
    Uses Euclidean distance as the cost metric.
    """
    n, m = len(series_a), len(series_b)
    # Initialize cost matrix with infinity
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0

    # Fill the cost matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate Euclidean distance between points
            dist = np.linalg.norm(series_a[i-1] - series_b[j-1])
            # The cost is the current distance + the minimum of the 3 neighbor cells
            cost_matrix[i, j] = dist + min(cost_matrix[i-1, j],    # Insertion
                                          cost_matrix[i, j-1],    # Deletion
                                          cost_matrix[i-1, j-1])  # Match

    # Backtrack to find the optimal path
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        # Find the direction of the minimum cost
        option = np.argmin([cost_matrix[i-1, j-1], cost_matrix[i-1, j], cost_matrix[i, j-1]])
        if option == 0:
            i, j = i - 1, j - 1
        elif option == 1:
            i -= 1
        else:
            j -= 1
            
    return cost_matrix[n, m], path[::-1]

def process_directory(directory_path: str):
    # 1. Gather and sort files by Year
    all_files = glob.glob(os.path.join(directory_path, "*.csv"))
    # Sort assumes "YYYY - PipelineName" format
    all_files.sort(key=lambda x: os.path.basename(x).split(' - ')[0])
    
    if len(all_files) < 2:
        print("Need at least two files to perform matching.")
        return None

    # 2. Load baseline (First Year)
    master_df = pd.read_csv(all_files[0])
    
    # 3. Iterate and match
    for next_file in all_files[1:]:
        year_label = os.path.basename(next_file).split(' - ')[0]
        current_df = pd.read_csv(next_file)

        # Prepare signals (Elevation and Rotation are critical for alignment)
        # We normalize columns to ensure rotation doesn't outweigh elevation
        base_signal = master_df[['elevation', 'rotation']].values
        curr_signal = current_df[['elevation', 'rotation']].values

        # 4. Run Custom DTW
        _, path = compute_dtw_alignment(base_signal, curr_signal)
        
        # Create a mapping dictionary {baseline_idx: current_year_idx}
        mapping = dict(path)

        # 5. Populate new values
        # j_len: joint length (distance between records in current year)
        # log_dist: position in the current year
        master_df[f'{year_label}_log_dist'] = [current_df.iloc[mapping[i]]['log_dist'] if i in mapping else np.nan for i in range(len(master_df))]
        master_df[f'{year_label}_elevation'] = [current_df.iloc[mapping[i]]['elevation'] if i in mapping else np.nan for i in range(len(master_df))]
        master_df[f'{year_label}_rotation'] = [current_df.iloc[mapping[i]]['rotation'] if i in mapping else np.nan for i in range(len(master_df))]
        
        # Calculate joint length based on the log_dist diff in the current file
        master_df[f'{year_label}_j_len'] = master_df[f'{year_label}_log_dist'].diff().abs().fillna(0)

    # 6. Export Master Table
    master_df.to_csv("Master_Anomaly_Tracking.csv", index=False)
    return master_df