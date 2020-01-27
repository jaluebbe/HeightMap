import os
import geojson
from shapely.geometry import shape
import remove_third_dimension
import clip_geojson_precision

path = 'static'

for in_file, out_file in [
        ('NZ_Railway_Network.geojson', 'NZ_railway_network_reduced.geojson'),
        ('Level_Crossings_Railway.geojson',
        'level_crossings_railway_reduced.geojson'),
        ('KiwiRail_Bridges.geojson', 'KiwiRail_bridges_reduced.geojson'),
        ('KiwiRail_Tunnels.geojson', 'KiwiRail_tunnels_reduced.geojson')
        ]:
    with open(os.path.join(path, in_file)) as f:
        data = geojson.load(f)

    for feature in data['features']:
        feature['geometry'] = remove_third_dimension.remove_third_dimension(
            shape(feature['geometry']))

    with open(os.path.join(path, out_file), 'w') as f:
        geojson.dump(data, f)

    clip_geojson_precision.clip(os.path.join(path, out_file))
