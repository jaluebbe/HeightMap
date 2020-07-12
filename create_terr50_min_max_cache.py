import struct
import os
import fnmatch
import json
from height_map.terr50 import NCOLS, NROWS, Terrain50

terr50 = Terrain50()

map_cache = {}
NODATA = terr50.NODATA


def create_cache_entry(filename):
    full_path = os.path.join(terr50.path, filename[:2].lower(), filename)
    x_ll = 0
    y_ll = NROWS - 1
    x_ur = NCOLS - 1
    y_ur = 0
    counter_max = 0
    counter_min = 0
    h_max = NODATA
    h_min = -NODATA
    # start in the upper left edge of the target area
    y_pos = y_ur
    x_pos = x_ll
    if os.path.isfile(full_path):
        with open(full_path, "rb") as f:
            while y_ur <= y_pos <= y_ll:
                f.seek((y_pos * NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while x_ll <= x_pos <= x_ur:
                    if values[x_pos - x_ll] > h_max:
                        h_max = values[x_pos - x_ll]
                        counter_max = 1
                    elif values[x_pos - x_ll] == h_max:
                        counter_max += 1
                    if NODATA < values[x_pos - x_ll] < h_min:
                        h_min = values[x_pos - x_ll]
                        counter_min = 1
                    elif NODATA < values[x_pos - x_ll] == h_min:
                        counter_min += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
        if h_min == -NODATA:
            h_min = NODATA
        return {
            'counter_max': counter_max, 'counter_min': counter_min,
            'h_max': h_max, 'h_min': h_min}


pattern = '*.bin'
for root, dirs, files in os.walk(terr50.path):
    for file_name in fnmatch.filter(files, pattern):
        map_cache[file_name] = create_cache_entry(file_name)

with open(os.path.join(terr50.cache_path, 'terr50_map_cache.json'), 'w') as f:
    json.dump(map_cache, f)
