import struct
import os
import fnmatch
import json
from height_map.srtm1 import NCOLS, NROWS, Srtm1

srtm = Srtm1()

map_cache = {}
NODATA = srtm.NODATA


def create_cache_entry(file_name):
    full_path = os.path.join(srtm.path, file_name)
    j_ll = 0
    i_ll = NROWS - 1
    j_ur = NCOLS - 1
    i_ur = 0
    counter_max = 0
    counter_min = 0
    h_max = NODATA
    h_min = -NODATA
    # start in the upper left edge of the target area
    i_pos = i_ur
    j_pos = j_ll
    if os.path.isfile(full_path):
        with open(full_path, "rb") as f:
            while i_ur <= i_pos <= i_ll:
                f.seek((i_pos * NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1
                buf = f.read(num_values * 2)
                values = struct.unpack('>{:d}h'.format(num_values), buf)
                while j_ll <= j_pos <= j_ur:
                    if values[j_pos - j_ll] > h_max:
                        h_max = values[j_pos - j_ll]
                        counter_max = 1
                    elif values[j_pos - j_ll] == h_max:
                        counter_max += 1
                    if NODATA < values[j_pos - j_ll] < h_min:
                        h_min = values[j_pos - j_ll]
                        counter_min = 1
                    elif NODATA < values[j_pos - j_ll] == h_min:
                        counter_min += 1
                    j_pos += 1
                j_pos = j_ll
                i_pos += 1
        if h_min == -NODATA:
            h_min = NODATA
        return {
            'counter_max': counter_max, 'counter_min': counter_min,
            'h_max': h_max, 'h_min': h_min}


pattern = '*.hgt'
for root, dirs, files in os.walk(srtm.path):
    for file_name in fnmatch.filter(files, pattern):
        _entry = create_cache_entry(file_name)
        map_cache[file_name] = _entry
        print(f"{file_name}: min={_entry['h_min']}m, max={_entry['h_max']}m")

with open(os.path.join(srtm.cache_path, 'srtm1_map_cache.json'), 'w') as f:
    json.dump(map_cache, f)
