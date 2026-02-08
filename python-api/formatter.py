import pandas as pd
import numpy as np
import json

FILE = 'format.json'
PATH = '../data/' 

class ILI:
    def __init__(self, file_name, format_mapping):
        self.file_path = file_name # Assuming files are in current dir or handled by PATH
        # Note: If running locally where files are in the same folder, you might want:
        # self.file_path = file_name 
        # But keeping your original PATH structure:
        self.file_path = PATH + file_name
        self.format = format_mapping
        
        self.raw_data = pd.read_csv(self.file_path)
        # Normalize column names to handle extra spaces
        self.raw_data.columns = self.raw_data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        self.processed_data = pd.DataFrame(columns=self.format.keys())
        
        for target_col, source_col in self.format.items():
            if source_col is None:
                self.processed_data[target_col] = None
            else:
                # We use .get to avoid KeyError if a column is missing, though we expect them to be there.
                # Direct access [] is fine if we are sure keys exist.
                self.processed_data[target_col] = self.raw_data[source_col]

    def process(self):
        # FIX: Added 'j_len' to ffill list so it propagates from Girth Welds to anomalies
        cols_to_ffill = ['joint_number', 'wall_thickness', 'j_len']
        
        for col in cols_to_ffill:
            if col in self.processed_data.columns:
                self.processed_data[col] = self.processed_data[col].ffill()

    def filter_anomalies(self):
        anomalies_to_keep = [
            'Cluster',
            'metal loss',
            'metal loss-manufacturing anomaly'
        ]
        
        if 'feature_type' in self.processed_data.columns:
            self.processed_data = self.processed_data[
                self.processed_data['feature_type'].isin(anomalies_to_keep)
            ]

    def generate_ids(self):
        anomaly_codes = {
            'Cluster': 'C',
            'metal loss': 'ML',
            'metal loss-manufacturing anomaly': 'ML'
        }
        
        anomaly_col = self.processed_data['feature_type'].astype(str)
        codes = anomaly_col.map(anomaly_codes)
        
        # Handle NaN joint numbers gracefully if any remain
        joint_series = self.processed_data['joint_number'].fillna(0)
        joint_str = joint_series.astype(float).round().astype('Int64').astype(str)
        
        self.processed_data['feature_id'] = codes + '-' + joint_str

    def clock_to_degrees(self):
        def _convert(time_str):
            if not isinstance(time_str, str): return None
            try:
                hours, minutes = map(int, time_str.split(':'))
                return (hours * 30) + (minutes * 0.5)
            except:
                return None
                
        if 'angle' in self.processed_data.columns:
            self.processed_data['angle'] = self.processed_data['angle'].apply(_convert)

    def normalize_depth(self):
        if 'depth_percent' in self.processed_data.columns:
            self.processed_data['depth_percent'] = self.processed_data['depth_percent'] / 100

    def clean_relative_position(self):
        if 'relative_position' in self.processed_data.columns:
            self.processed_data['relative_position'] = self.processed_data['relative_position'].abs()

    def save_csv(self, output_name):
        self.processed_data.to_csv(PATH + output_name, index=False)

    def datasort2022(sheet4_df: pd.DataFrame) -> pd.DataFrame:
        anomoly_count = 0
        output_columns = [
            "feature_id", "distance", "odometer", "joint_number", "relative_position",
            "clock_position", "feature_type", "depth_percent", "length", "width",
            "wall_thickness", "weld_type", "B31G Pburst [PSI]/Pdesign [PSI]"
        ]
        output_data = []

        # Use .shape[0] for the loop range
        total_rows = sheet4_df.shape[0]
        num_anomolies = 0

        for i in range(total_rows - 1): # -1 to prevent index out of bounds on i+1
            if num_anomolies == 0:
                # Check current row column 20 and next row column 21
                # pd.isna() handles both None and NaN from CSV reads
                val_curr_20 = pd.to_numeric(sheet4_df.iat[i, 20], errors='coerce')
                val_next_21 = sheet4_df.iat[i + 1, 21]

                if (val_curr_20 > 0 and 
                    (pd.isna(sheet4_df.iat[i, 21]) or sheet4_df.iat[i, 21] == "") and 
                    pd.to_numeric(sheet4_df.iat[i + 1, 20], errors='coerce') > 0 and 
                    pd.notna(val_next_21) and val_next_21 != ""):
                    
                    num_anomolies = int(val_curr_20)
                    # weld_type = sheet4_df.iat[i, 6] # Extracted but not currently used in the logic
            else:
                feature_type_val = str(sheet4_df.iat[i, 6]).lower()

                if "metal loss" in feature_type_val:
                    anomoly_count += 1
                    feature_id = f"ML-{anomoly_count:05d}"
                elif "dent" in feature_type_val:
                    anomoly_count += 1
                    feature_id = f"D-{anomoly_count:05d}"
                elif "cluster" in feature_type_val:
                    anomoly_count += 1
                    feature_id = f"C-{anomoly_count:05d}"
                else:
                    # If it's not a target anomaly, skip this row but keep the anomaly count pending
                    continue

                # Data Extraction
                distance = sheet4_df.iat[i, 5]
                odometer = sheet4_df.iat[i, 5]
                joint_number = sheet4_df.iat[i, 0]
                relative_position = sheet4_df.iat[i, 3]

                # --- Fixed Clock position calculation ---
                clock_val = sheet4_df.iat[i, 18]
                clock_degree = 0.0

                try:
                    if isinstance(clock_val, str) and ':' in clock_val:
                        # Handles "HH:MM" format
                        hours, minutes = map(int, clock_val.split(':'))
                        # 30 degrees per hour, 0.5 degrees per minute
                        clock_degree = (hours % 12 * 30) + (minutes * 0.5)
                    else:
                        # Handles decimal format (e.g., 3.5 for 3:30)
                        decimal_time = float(clock_val)
                        clock_degree = (decimal_time % 12) * 30
                except (ValueError, TypeError):
                    clock_degree = 0.0

                clock_position = clock_degree

                # Depth calculation
                if "dent" in feature_type_val:
                    depth_raw = sheet4_df.iat[i, 13]
                else:
                    depth_raw = sheet4_df.iat[i, 8]
                
                depth_percent = depth_raw / 100 if pd.notnull(depth_raw) else np.nan

                # Pressure Ratio Calculation
                try:
                    val_32 = float(sheet4_df.iat[i, 32])
                    val_34 = float(sheet4_df.iat[i, 34])
                    b31g_ratio = val_34 / val_32 if val_32 > 0 else np.nan
                except (ValueError, TypeError):
                    b31g_ratio = np.nan

                output_data.append([
                    feature_id, distance, odometer, joint_number, relative_position,
                    clock_position, feature_type_val, depth_percent, 
                    sheet4_df.iat[i, 16], sheet4_df.iat[i, 17],
                    sheet4_df.iat[i, 2], "girthweld", b31g_ratio
                ])

                num_anomolies -= 1

        return pd.DataFrame(output_data, columns=output_columns)
    def datasort2015(df: pd.DataFrame) -> pd.DataFrame:
        output_columns = [
            "feature_id", "distance", "odometer", "joint_number", "relative_position",
            "clock_position", "feature_type", "depth_percent", "length", "width",
            "wall_thickness", "weld_type", "B31G Pburst [PSI]/Pdesign [PSI]"
            ]
        
        output_data = []
        anomaly_count = 0
        num_anomalies_pending = 0
        
        # Iterate through the DataFrame rows
        for i in range(len(df)):
            # Extract row as a series for easier indexing
            row = df.iloc[i]
            
            if num_anomalies_pending == 0:
                # Trigger: Check column 16 (index 16) for a count of upcoming anomalies
                val_16 = pd.to_numeric(row.iloc[16], errors='coerce')
                if pd.notna(val_16) and val_16 > 0:
                    num_anomalies_pending = int(val_16)
            else:
                feature_type_raw = str(row.iloc[6]).lower() if pd.notna(row.iloc[6]) else ""
                
                # Map feature types and increment IDs
                if "metal loss" in feature_type_raw:
                    anomaly_count += 1
                    f_id = f"ML-{anomaly_count:05d}"
                elif "dent" in feature_type_raw:
                    anomaly_count += 1
                    f_id = f"D-{anomaly_count:05d}"
                elif "cluster" in feature_type_raw:
                    anomaly_count += 1
                    f_id = f"C-{anomaly_count:05d}"
                else:
                    # If row doesn't match anomaly types, skip but keep pending count
                    continue

                # Clock position calculation (Time fraction * 720)
                clock_val = row.iloc[14]
                clock_pos = 0.0
                try:
                    if isinstance(clock_val, (int, float)):
                        time_frac = float(clock_val)
                    else:
                        # Try parsing common time formats
                        t_obj = pd.to_datetime(clock_val)
                        time_frac = (t_obj.hour * 3600 + t_obj.minute * 60 + t_obj.second) / 86400
                    
                    clock_pos = time_frac * 720
                    if clock_pos > 360: clock_pos -= 360
                except:
                    clock_pos = np.nan

                # Relative position (-1 * column 3)
                rel_pos = -1 * row.iloc[3] if pd.notna(row.iloc[3]) else np.nan

                # Depth percentage (column 10 for dents, column 8 for others)
                depth_raw = row.iloc[10] if "dent" in feature_type_raw else row.iloc[8]
                depth_pct = (depth_raw / 100) if pd.notna(depth_raw) else np.nan

                # Ratio calculation (Pburst [27] / Pdesign [25])
                try:
                    pdesign = float(row.iloc[25])
                    pburst = float(row.iloc[27])
                    ratio = pburst / pdesign if pdesign > 0 else np.nan
                except:
                    ratio = np.nan

                output_data.append([
                    f_id, row.iloc[5], row.iloc[5], row.iloc[0], rel_pos,
                    clock_pos, feature_type_raw, depth_pct, row.iloc[12], row.iloc[13],
                    row.iloc[2], "girthweld", ratio
                ])
                
                num_anomalies_pending -= 1
                
        return pd.DataFrame(output_data, columns=output_columns)

# --- Execution ---
file_path = '../data' # Change to your actual path

# 1. Load
ILI_2015 = pd.read_csv(file_path + '/Cleaned_ILIDataV2-2015.csv')

# 2. Process
ILI_2015_formatted = ILI.datasort2015(ILI_2015)

# 3. Save
ILI_2015_formatted.to_csv(file_path + '/ILI_2015_formatted.csv', index=False)

# --- Main Execution Block ---
file_path = '../data' # Update this to your actual directory path

# 1. Load the data
ILI_2022 = pd.read_csv(file_path + '/Cleaned_ILIDataV2-2022.csv')

# 2. Process the data
ILI_2022_formatted = ILI.datasort2022(ILI_2022)

# 3. Save the data
ILI_2022_formatted.to_csv(file_path + '/ILI_2022_formatted.csv', index=False)
# ... (2 lines left)


with open(FILE, 'r') as file:
    data = json.load(file)

ili_objects = {
    '2007': ILI('Cleaned_ILIDataV2-2007.csv', data['ILI_2007'])
}

for year, ili_obj in ili_objects.items():
    print(f"Processing {year}...")
    
    ili_obj.process()
    
    ili_obj.filter_anomalies()
    ili_obj.generate_ids()
    ili_obj.clock_to_degrees()
    ili_obj.normalize_depth()
    ili_obj.clean_relative_position()
    
    ili_obj.save_csv(f'ILI_{year}_formatted.csv')
    print(f"Finished {year}.")