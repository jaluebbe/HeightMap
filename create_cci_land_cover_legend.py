import os
import csv
import json

path = 'height_map/maps/cci_land_cover'
legend = {}
color_mappings = {}

with open(os.path.join(path, 'ESACCI-LC-Legend.csv')) as csv_file:
    reader = csv.DictReader(csv_file, delimiter=';')
    for row in reader:
        legend[row['NB_LAB']] = {
            'value': int(row['NB_LAB']), 'label': row['LCCOwnLabel'].strip(),
            'color': (int(row['R']), int(row['G']), int(row['B']))}
        color_mappings[row['NB_LAB']] = {
            'color': '#{:02x}{:02x}{:02x}'.format(int(row['R']), int(row['G']),
            int(row['B'])), 'text': row['LCCOwnLabel'].strip()}

with open(os.path.join(path, 'cci_land_cover_legend.json'), 'w') as f:
    json.dump(legend, f)

print(json.dumps(color_mappings, indent=4).replace("\"", "'"))
