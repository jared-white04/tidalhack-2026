import pandas as pd
import json

FILE = 'format.json'
PATH = '../data/'

class ILI:
    def __init__(self, file_name, format_mapping):
        self.file_path = PATH + file_name
        self.format = format_mapping
        self.raw_data = pd.read_csv(self.file_path)
        
        self.raw_data.columns = self.raw_data.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
        self.processed_data = pd.DataFrame(columns=self.format.keys())

        for target_col, source_col in self.format.items():
            if source_col is None:
                self.processed_data[target_col] = None
            else:
                self.processed_data[target_col] = self.raw_data[source_col]

    def process(self):
        cols_to_ffill = ['joint_number', 'wall_thickness']
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
        
        joint_str = self.processed_data['joint_number'].astype(float).round().astype('Int64').astype(str)
        
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


with open(FILE, 'r') as file:
    data = json.load(file)

ili_objects = {
    '2007': ILI('Cleaned_ILIDataV2-2007.csv', data['ILI_2007']),
    '2015': ILI('Cleaned_ILIDataV2-2015.csv', data['ILI_2015']),
    '2022': ILI('Cleaned_ILIDataV2-2022.csv', data['ILI_2022'])
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