import pandas as pd
import json

FILE = 'format.json'
PATH = '../data/'

class ILI:
    def __init__(self, file_name, format_mapping):
        self.file_path = PATH + file_name
        self.format = format_mapping
        self.raw_data = pd.read_csv(self.file_path)
        
        # FIX: Normalize column names by replacing multiple spaces with single space
        # and stripping leading/trailing whitespace
        self.raw_data.columns = self.raw_data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        # Create empty dataframe with the target keys
        self.processed_data = pd.DataFrame(columns=self.format.keys())

    def process(self):
        # 1. Map columns based on JSON format
        for target_col, source_col in self.format.items():
            if source_col is None:
                self.processed_data[target_col] = None
            else:
                self.processed_data[target_col] = self.raw_data[source_col]

        # 2. Forward Fill specific columns
        # Note: You might want to make the list of ffill columns a parameter or constant
        cols_to_ffill = ['joint_number', 'wall_thickness']
        for col in cols_to_ffill:
            if col in self.processed_data.columns:
                self.processed_data[col] = self.processed_data[col].ffill()

        # 3. Execute all transformation steps
        self.filter_anomalies()
        self.generate_ids()
        self.clock_to_degrees()
        self.normalize_depth()
        self.clean_relative_position()
        
        return self.processed_data

    def filter_anomalies(self):
        # Define anomaly types to keep
        anomalies_to_keep = [
            'Cluster',
            'metal loss',
            'metal loss-manufacturing anomaly'
        ]
        
        # Ensure we are checking a string column to avoid errors
        if 'feature_type' in self.processed_data.columns:
             # Standardize check (optional based on your previous issues)
             # self.processed_data['feature_type'] = self.processed_data['feature_type'].astype(str).str.strip()
             
             self.processed_data = self.processed_data[
                self.processed_data['feature_type'].isin(anomalies_to_keep)
             ]

    def generate_ids(self):
        anomaly_codes = {
            'Cluster': 'C',
            'metal loss': 'ML',
            'metal loss-manufacturing anomaly': 'ML'
        }
        
        # Ensure strictly string for mapping
        anomaly_col = self.processed_data['feature_type'].astype(str)
        # Map codes
        codes = anomaly_col.map(anomaly_codes)
        
        # Create ID: Code - JointNumber
        # Using Int64 to handle potential NaNs safely, though ffill should have handled it
        # joint_str = self.processed_data['joint_number'].astype('Int64').astype(str)
        # Round to nearest whole number first to handle 70.01, then convert
        joint_str = self.processed_data['joint_number'].round().astype('Int64').astype(str)

        
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


# --- Execution ---

with open(FILE, 'r') as file:
    data = json.load(file)

# Dictionary of ILI objects
ili_objects = {
    '2007': ILI('Cleaned_ILIDataV2-2007.csv', data['ILI_2007']),
    '2015': ILI('Cleaned_ILIDataV2-2015.csv', data['ILI_2015']),
    '2022': ILI('Cleaned_ILIDataV2-2022.csv', data['ILI_2022'])
}

# Process and Save
for year, ili_obj in ili_objects.items():
    print(f"Processing {year}...")
    ili_obj.process()
    ili_obj.save_csv(f'ILI_{year}_formatted.csv')
    print(f"Finished {year}.")