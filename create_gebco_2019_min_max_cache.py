import h5py
import os
import json
import numpy as np
import height_map.maps.gebco_2019 as gebco_2019

cache_filename = 'gebco_2019_cache.json'

z_max = np.zeros([180, 360])
z_min = np.zeros([180, 360])

with h5py.File(os.path.join(gebco_2019.path, gebco_2019.filename), 'r') as f:
    data = np.array(f['elevation'])

for _x in range(180):
    for _y in range(360):
        z_max[_x, _y] = data[_x*240:(_x+1)*240, _y*240:(_y+1)*240].max()
        z_min[_x, _y] = data[_x*240:(_x+1)*240, _y*240:(_y+1)*240].min()

min_max_cache = {'minimum': np.around(z_min, 1).tolist(),
    'maximum': np.around(z_max, 1).tolist()}
with open(os.path.join(gebco_2019.path, cache_filename), 'w') as f:
    json.dump(cache, f)
