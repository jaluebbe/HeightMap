import struct
import os
import numpy as np
import zipfile

source_file = 'downloads/dgm200.utm32s.gridascii.zip'
build_directory = 'build/dgm200'
ascii_grid_file = os.path.join(build_directory,
    'dgm200.utm32s.gridascii/dgm200/dgm200_utm32s.asc')
destination_file = 'height_map/maps/dgm200/dgm200_utm32s_f4.bin'

with zipfile.ZipFile(source_file, 'r') as zip_ref:
    zip_ref.extractall(build_directory)

my_array = np.loadtxt(ascii_grid_file, skiprows=6)
with open(destination_file, 'wb') as f:
    for y in range(4331):
        for x in range(3207):
            f.write(struct.pack('>f', float(my_array[y][x])))
