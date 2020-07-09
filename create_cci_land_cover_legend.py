import os
import csv
import json

path = 'height_map/maps/cci_land_cover'
legend = {}

with open(os.path.join(path, 'ESACCI-LC-Legend.csv')) as csv_file:
    reader = csv.DictReader(csv_file, delimiter=';')
    for row in reader:
        legend[row['NB_LAB']] = {
            'value': int(row['NB_LAB']), 'label': row['LCCOwnLabel'],
            'color': (int(row['R']), int(row['G']), int(row['B']))}

with open(os.path.join(path, 'cci_land_cover_legend.json'), 'w') as f:
    json.dump(legend, f)
