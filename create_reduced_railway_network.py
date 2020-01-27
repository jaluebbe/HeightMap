import geojson
from shapely.geometry import shape
import remove_third_dimension
import clip_geojson_precision


in_file = 'static/NZ_Railway_Network.geojson'
out_file = 'static/NZ_railway_network_reduced.geojson'
with open(in_file) as f:
    data = geojson.load(f)

for feature in data['features']:
    feature['geometry'] = remove_third_dimension.remove_third_dimension(
        shape(feature['geometry']))

with open(out_file, 'w') as f:
    geojson.dump(data, f)

clip_geojson_precision.clip(out_file)
