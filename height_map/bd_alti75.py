import os
import re
import struct
import json
import time
from pygeodesy import ellipsoidalVincenty as eV
from pygeodesy import toLcc, Lcc
from pygeodesy import Conics
from height_map.dgm200 import calculate_distance

CELLSIZE = 75
NCOLS = 1000
NROWS = 1000
NODATA = -99999.00
pwd = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(pwd, 'maps/bd_alti75')
attribution_url = ('http://professionnels.ign.fr/bdalti')
attribution_name = 'BD ALTI 75m'
attribution = ('<a href="{}">BD ALTI&reg;</a>').format(attribution_url)
cache_path = 'height_map'
map_cache_filename = os.path.join(cache_path, 'bd_alti_75_map_cache.json')
if os.path.isfile(map_cache_filename):
    with open(map_cache_filename) as json_cache_file:
        try:
            map_cache = json.load(json_cache_file)
        except json.decoder.JSONDecodeError:
            map_cache = {}
else:
    map_cache = {}

def get_x(lcc):
    return round(round(lcc.easting + CELLSIZE/2, 1) % (NCOLS * CELLSIZE)
        ) // CELLSIZE

def get_y(lcc):
    return NROWS - 1 - round(round(lcc.northing - CELLSIZE/2, 1) % (
        NROWS * CELLSIZE)) // CELLSIZE

def get_filename(lcc):
    filename = (
        'BDALTIV2_75M_FXX_{:04d}_{:04d}_MNT_LAMB93_IGN69.bin'.format(
        int((lcc.easting + CELLSIZE/2) // (NCOLS * CELLSIZE) * CELLSIZE),
        int(((lcc.northing + CELLSIZE/2)//(NROWS * CELLSIZE) + 1) * CELLSIZE)))
    return filename

def get_lat_lon_from_indices(x, y, filename):
    latlon = get_lcc_from_indices(x, y, filename).toLatLon()
    return (latlon.lat, latlon.lon)

def get_lcc_from_indices(x, y, filename):
    result = re.search(
        '^BDALTIV2_75M_FXX_([0-9]{4})_([0-9]{4})_MNT_LAMB93_IGN69\.bin$',
        filename)
    xllcorner = int(result.group(1)) * NCOLS - CELLSIZE/2
    yllcorner = (int(result.group(2)) - CELLSIZE)*NROWS + CELLSIZE/2
    easting = x*CELLSIZE + xllcorner
    northing = (NROWS - 1 - y) * CELLSIZE + yllcorner
    lcc = Lcc(easting, northing, conic=Conics.Fr93Lb)
    return lcc

def get_height(lat, lon):
    try:
        lcc = toLcc(eV.LatLon(lat, lon), conic=Conics.Fr93Lb)
    except ValueError as e:
        return {
            'altitude_m': NODATA, 'source': attribution_name, 'latitude': lat,
            'lon': lon, 'distance_m': 0, 'attribution': attribution}
    filename = get_filename(lcc)
    full_path = os.path.join(path, filename)
    if os.path.isfile(full_path):
        x = get_x(lcc)
        y = get_y(lcc)
        with open(full_path, "rb") as f:
            # go to the right spot,
            f.seek((y * NCOLS + x) * 4)
            # read four bytes and convert them:
            buf = f.read(4)
            # ">f" is a four byte float
            val = struct.unpack('>f', buf)[0]
            (lat_found, lon_found) = get_lat_lon_from_indices(x, y, filename)
            return {
                'altitude_m': round(val, 1), 'source': attribution_name,
                'latitude': lat_found, 'longitude': lon_found,
                'distance_m': calculate_distance(lat, lon, lat_found,
                lon_found), 'attribution': attribution}
    else:
        return {
            'altitude_m': NODATA, 'source': attribution_name, 'latitude': lat,
            'longitude': lon, 'distance_m': 0, 'attribution': attribution}

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    # consider only correctly defined rectangle:
    if (lat_ll > lat_ur or lon_ll > lon_ur):
        return ([], NODATA, 0)
    try:
        lcc_ll = toLcc(eV.LatLon(lat_ll, lon_ll), conic=Conics.Fr93Lb)
    except ValueError as e:
        return ([], NODATA, 0)
    try:
        lcc_ur = toLcc(eV.LatLon(lat_ur, lon_ur), conic=Conics.Fr93Lb)
    except ValueError as e:
        return ([], NODATA, 0)
    file_list = {}
    create_filelist(lcc_ll, lcc_ur, file_list)
    raw_length = len(file_list)
    lowest_max = check_max_list(file_list)
    new_length = len(file_list)
    (lcc_list, h_max, counter) = check_max_files(file_list)
    latlon_list = []
    for lcc in lcc_list:
        latlon = lcc.toLatLon(eV.LatLon)
        latlon_list += [(latlon.lat, latlon.lon)]
    return (latlon_list, h_max, counter)

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    # consider only correctly defined rectangle:
    if (lat_ll > lat_ur or lon_ll > lon_ur):
        return ([], NODATA, 0)
    try:
        lcc_ll = toLcc(eV.LatLon(lat_ll, lon_ll), conic=Conics.Fr93Lb)
    except ValueError as e:
        return ([], NODATA, 0)
    try:
        lcc_ur = toLcc(eV.LatLon(lat_ur, lon_ur), conic=Conics.Fr93Lb)
    except ValueError as e:
        return ([], NODATA, 0)
    file_list = {}
    create_filelist(lcc_ll, lcc_ur, file_list)
    raw_length = len(file_list)
    largest_min = check_min_list(file_list)
    new_length = len(file_list)
    (lcc_list, h_min, counter) = check_min_files(file_list)
    latlon_list = []
    for lcc in lcc_list:
        latlon = lcc.toLatLon(eV.LatLon)
        latlon_list += [(latlon.lat, latlon.lon)]
    return (latlon_list, h_min, counter)

def check_max_list(file_list):
    h_max = NODATA
    for filename, list_item in file_list.items():
        cache_data = map_cache.get(filename)
        if list_item['complete']:
            h_max = max(h_max, cache_data['h_max'])
    for filename in list(file_list.keys()):
        cache_data = map_cache.get(filename)
        if cache_data['h_max'] < h_max:
            del file_list[filename]
    return h_max

def check_min_list(file_list):
    h_min = -NODATA
    for filename, list_item in file_list.items():
        cache_data = map_cache.get(filename)
        if list_item['complete']:
            if (NODATA < cache_data['h_min'] < h_min):
                h_min = cache_data['h_min']
    for filename in list(file_list.keys()):
        cache_data = map_cache.get(filename)
        if cache_data['h_min'] > h_min > NODATA:
            del file_list[filename]
    if h_min == -NODATA:
        h_min = NODATA
    return h_min

def check_max_files(file_list):
    h_max = NODATA
    lcc_list = []
    counter = 0
    for filename, list_item in file_list.items():
        x_ll = list_item['x_ll']
        y_ll = list_item['y_ll']
        x_ur = list_item['x_ur']
        y_ur = list_item['y_ur']
        x_pos = x_ll
        y_pos = y_ur
        full_path = os.path.join(path, filename)
        with open(full_path, "rb") as f:
            while(y_ur <= y_pos <= y_ll):
                f.seek((y_pos * NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while(x_ll <= x_pos <=x_ur):
                    # if current height value larger than previous maximum
                    if values[x_pos - x_ll] > h_max:
                        # store current height
                        h_max = values[x_pos - x_ll]
                        lcc_list = [get_lcc_from_indices(x_pos, y_pos,
                            filename)]
                        counter = 1
                    elif values[x_pos - x_ll] == h_max:
                        lcc_list += [get_lcc_from_indices(x_pos, y_pos,
                                                            filename)]
                        counter += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
    return (lcc_list, h_max, counter)

def check_min_files(file_list):
    h_min = -NODATA
    lcc_list = []
    counter = 0
    for filename, list_item in file_list.items():
        x_ll = list_item['x_ll']
        y_ll = list_item['y_ll']
        x_ur = list_item['x_ur']
        y_ur = list_item['y_ur']
        x_pos = x_ll
        y_pos = y_ur
        full_path = os.path.join(path, filename)
        with open(full_path, "rb") as f:
            while(y_ur <= y_pos <= y_ll):
                f.seek((y_pos * NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while(x_ll <= x_pos <=x_ur):
                    # if current height value larger than previous maximum
                    if (NODATA < values[x_pos - x_ll] < h_min):
                        # store current height
                        h_min = values[x_pos - x_ll]
                        lcc_list = [get_lcc_from_indices(x_pos, y_pos,
                            filename)]
                        counter = 1
                    elif (NODATA < values[x_pos - x_ll] == h_min):
                        lcc_list += [get_lcc_from_indices(x_pos, y_pos,
                                                            filename)]
                        counter += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
    if h_min == -NODATA:
        h_min = NODATA
    return (lcc_list, h_min, counter)

def create_filelist(lcc_ll, lcc_ur, file_list):
    # obtain the coordinates of the tile containing the lower left
    easting_ll_tile = round(lcc_ll.easting - round(lcc_ll.easting + CELLSIZE/2,
        1) % (NCOLS * CELLSIZE), 1)
    northing_ll_tile = round(lcc_ll.northing - round(
        lcc_ll.northing - CELLSIZE/2, 1) % (NCOLS * CELLSIZE), 1)
    # convert coordinates to data indices:
    x_ll = get_x(lcc_ll)
    y_ll = get_y(lcc_ll)
    if lcc_ur.northing - northing_ll_tile < NROWS * CELLSIZE:
        y_ur = get_y(lcc_ur)
    else:
        # upper neighbour
        create_filelist(
            Lcc(lcc_ll.easting, northing_ll_tile + NROWS*CELLSIZE,
            conic=Conics.Fr93Lb),
            Lcc(min(lcc_ur.easting, easting_ll_tile + (NCOLS - 1)*CELLSIZE),
            lcc_ur.northing, conic=Conics.Fr93Lb), file_list)
        y_ur = 0
    if lcc_ur.easting - easting_ll_tile < NCOLS * CELLSIZE:
        x_ur = get_x(lcc_ur)
    else:
        # right neighbour
        create_filelist(Lcc(easting_ll_tile + NCOLS*CELLSIZE,
            lcc_ll.northing, conic=Conics.Fr93Lb), lcc_ur, file_list)
        x_ur = NCOLS - 1
    filename = get_filename(lcc_ll)
    full_path = os.path.join(path, filename)
    if os.path.isfile(full_path):
        complete = (y_ur == 0 and x_ll == 0 and x_ur == NCOLS - 1
                    and y_ll == NROWS - 1)
        file_list[filename] = {'x_ll': x_ll, 'y_ll': y_ll, 'x_ur': x_ur,
                               'y_ur': y_ur, 'complete': complete}
