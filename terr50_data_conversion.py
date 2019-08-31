import struct
import os
import zipfile
import fnmatch
import shutil
import re

source_file = 'downloads/terr50_gagg_gb.zip'
build_directory = 'build/terr50'
destination_directory = 'height_map/maps/os_terr50_gb'
NODATA = -32768

with zipfile.ZipFile(source_file, 'r') as zip_ref:
    zip_ref.extractall(build_directory)

def convert_to_binary(in_file):
    if not os.path.isfile(in_file):
        return
    result = re.search('.*/([a-z]{2}).*/(.*)\.asc', in_file)
    subfolder = result.group(1)
    file_name = result.group(2)
    destination_folder = os.path.join(destination_directory, subfolder)
    if not os.path.isdir(destination_folder):
        os.makedirs(destination_folder)
    out_file = os.path.join(destination_folder, file_name + '.bin')
    head_file = os.path.join(destination_folder, file_name + '.head')
    other_nodata = None
    with open(in_file) as f:
        with open(head_file, "w") as hf:
            for _ in range(5):
                hf.write(next(f))
        with open(out_file, "wb") as of:
            for line in f:
                if line.startswith('nodata_value'):
                    other_nodata = line.split('nodata_value ')[1]
                    continue
                values = line.strip().split(' ')
                for value in values:
                    if other_nodata is not None and value == other_nodata:
                        of.write(struct.pack('>f', float(NODATA)))
                    else:
                        of.write(struct.pack('>f', float(value)))

pattern = '*.zip'
for root, dirs, files in os.walk(os.path.join(build_directory, 'data')):
    for file_name in fnmatch.filter(files, pattern):
            zipfile.ZipFile(os.path.join(root, file_name)).extractall(
                os.path.join(root, os.path.splitext(file_name)[0]))
            os.remove(os.path.join(root, file_name))

if os.path.isdir(destination_directory):
    shutil.rmtree(destination_directory)

pattern = '*.asc'
for root, dirs, files in os.walk(os.path.join(build_directory, 'data')):
    for file_name in fnmatch.filter(files, pattern):
            convert_to_binary(os.path.join(root, file_name))
#            os.remove(os.path.join(root, file_name))
