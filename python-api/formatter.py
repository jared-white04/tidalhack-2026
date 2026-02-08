# library imports
import pandas as pd   # pandas - used for data processing

# path to the ILI data
file_path = '../data/'

ILI_2007 = pd.read_csv(file_path + '/Cleaned_ILIDataV2-2007.csv')   # 2007 ILI data
ILI_2015 = pd.read_csv(file_path + '/Cleaned_ILIDataV2-2015.csv')   # 2015 ILI data
ILI_2022 = pd.read_csv(file_path + '/Cleaned_ILIDataV2-2022.csv')   # 2022 ILI data

# column names for new formatted table
column_names = [
    'feature_id',
    'distance',
    'odometer',
    'joint_number',
    'relative_position',
    'angle',
    'feature_type',
    'depth_percent',
    'length',
    'width',
    'wall_thickness',
    'weld_type',
    'elevation'
]

fields_2007 = [
    None,
    'log dist. [ft]',
    'log dist. [ft]',
    'J. no.',
    'to u/s w. [ft]',
    'o\'clock',
    'event',
    'depth [%]',
    'length [in]',
    'width [in]',
    't [in]',
    None,
    None
]

ILI_2007_formatted = pd.DataFrame(columns=column_names)
ILI_2015_formatted = pd.DataFrame(columns=column_names)
ILI_2022_formatted = pd.DataFrame(columns=column_names)

columns = len(column_names)

for index in range(columns):
  column_name = column_names[index]
  field_2007 = fields_2007[index]

  if field_2007 == None:
    ILI_2007_formatted[column_name] = None
  else:
    ILI_2007_formatted[column_name] = ILI_2007[field_2007]

ILI_2007_formatted['joint_number'] = ILI_2007_formatted['joint_number'].ffill()
ILI_2007_formatted['wall_thickness'] = ILI_2007_formatted['wall_thickness'].ffill()

anomaly_codes = {
    'Cluster': 'C',
    'metal loss': 'ML',
    'metal loss-manufacturing anomaly': 'ML'
}

anomaly = ILI_2007_formatted['feature_type'].astype(str)
code = anomaly.map(anomaly_codes)

ILI_2007_formatted['feature_id'] = code + '-' + ILI_2007_formatted['joint_number'].astype('Int64').astype(str)

anomalies_2007 = [
    'Cluster',
    'metal loss',
    'metal loss-manufacturing anomaly'
]

ILI_2007_formatted = ILI_2007_formatted[
    ILI_2007_formatted['feature_type'].isin(anomalies_2007)
]

ILI_2007_formatted['relative_position'] = ILI_2007_formatted['relative_position'].abs()

def time_to_degrees(time):
  separator = ':'
  index = time.find(separator)

  hours = int(time[:index])
  minutes = int(time[(index + 1):])

  angle = (hours * 30) + (minutes * 0.5)
  return angle

ILI_2007_formatted['angle'] = ILI_2007_formatted['angle'].apply(time_to_degrees)
ILI_2007_formatted['depth_percent'] = ILI_2007_formatted['depth_percent'].apply(lambda x: x / 100)

ILI_2007_formatted.to_csv(file_path + '/ILI_2007_formatted.csv')