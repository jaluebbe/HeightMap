import os
import json
import numpy as np
from height_map.gebco import Gebco

gebco = Gebco()

z_max = np.zeros([180, 360])
z_min = np.zeros([180, 360])

data = np.array(gebco.h5_file['elevation'])

for _x in range(180):
    for _y in range(360):
        z_max[_x, _y] = data[_x*240:(_x+1)*240, _y*240:(_y+1)*240].max()
        z_min[_x, _y] = data[_x*240:(_x+1)*240, _y*240:(_y+1)*240].min()

min_max_cache = {'minimum': np.around(z_min, 1).tolist(),
    'maximum': np.around(z_max, 1).tolist()}
with open(os.path.join(gebco.cache_path, gebco.cache_file_name), 'w') as f:
    json.dump(min_max_cache, f)
