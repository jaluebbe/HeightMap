import struct
import os
import zipfile
import libarchive.public
import fnmatch
import shutil
import re
from collections import Counter

source_file = 'downloads/BDALTIV2_2-0_75M_ASC_LAMB93-IGN69_FRANCE_2018-01-15.7z'
source_directory = 'downloads/BDALTIV2_2-0_75M_ASC_LAMB93-IGN69_FRANCE_2018-01-15/BDALTIV2/1_DONNEES_LIVRAISON_2018-01-00245/BDALTIV2_MNT_75M_ASC_LAMB93_IGN69_FRANCE/'
build_directory = 'build/bd_alti75'
destination_folder = 'height_map/maps/bd_alti75'
NODATA = -99999.00

#with libarchive.public.file_reader(source_file) as e:
#    for entry in e:
#        print(entry)
#        print(type(entry))
#        with open(os.path.join(build_directory, str(entry)), 'wb') as f:
#            for block in entry.get_blocks():
#                f.write(block)
#exit(0)

def convert_to_binary(in_file):
    if not os.path.isfile(in_file):
        return
    result = re.search('.*/(.*)\.asc', in_file)
    nodata_counter = Counter()
    file_name = result.group(1)
    if not os.path.isdir(destination_folder):
        os.makedirs(destination_folder)
    out_file = os.path.join(destination_folder, file_name + '.bin')
    head_file = os.path.join(destination_folder, file_name + '.head')
    other_nodata = None
    old_value = None
    with open(in_file) as f:
        with open(head_file, "w") as hf:
            for _ in range(6):
                hf.write(next(f))
        with open(out_file, "wb") as of:
            for line in f:
                if line.startswith('nodata_value'):
                    other_nodata = line.split('nodata_value ')[1]
                    print('has nodata entry:', in_file)
                    continue
                values = line.strip().split(' ')
                for value in values:
                    if float(value) == 0:
                        if old_value == value:
                            nodata_counter[value] += 1
                        elif old_value is not None and abs(float(old_value)) > 15:
                            nodata_counter[old_value] += 1
                        elif old_value is not None and float(old_value) == 0 and abs(float(value)) > 15:
                            nodata_counter[value] += 1
                    old_value = value
                    if value == '-1276.80':
                        value = NODATA
                    if other_nodata is not None and value == other_nodata:
                        of.write(struct.pack('>f', float(NODATA)))
                    else:
                        of.write(struct.pack('>f', float(value)))

    if len(nodata_counter) > 0:
        print(nodata_counter, os.path.basename(in_file))

pattern = '*.asc'
for root, dirs, files in os.walk(source_directory):
    for file_name in fnmatch.filter(files, pattern):
            convert_to_binary(os.path.join(root, file_name))
