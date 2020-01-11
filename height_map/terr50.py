import os
import struct
import json
import time
from pygeodesy import ellipsoidalVincenty as eV
from pygeodesy import toOsgr, parseOSGR, Osgr
from height_map.dgm200 import calculate_distance
CELLSIZE = 50
NCOLS = 200
NROWS = 200
NODATA = -32768
pwd = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(pwd, 'maps/os_terr50_gb')
attribution_url = ('https://www.ordnancesurvey.co.uk/business-and-government/'
    'products/terrain-50.html')
attribution_name = 'OS Terrain 50'
attribution = ('<a href="{}">Contains OS data &copy; Crown copyright and '
    'database right 2019</a>').format(attribution_url)
cache_path = pwd
map_cache_filename = os.path.join(cache_path, 'terr50_map_cache.json')
if os.path.isfile(map_cache_filename):
    with open(map_cache_filename) as json_cache_file:
        try:
            map_cache = json.load(json_cache_file)
        except json.decoder.JSONDecodeError:
            map_cache = {}
else:
    map_cache = {}

precision = 4.0  # RMS error

def get_x(osgr):
    return int(osgr.easting % (NCOLS * CELLSIZE) // CELLSIZE)

def get_y(osgr):
    return int(NROWS - 1 - osgr.northing % (NROWS * CELLSIZE) // CELLSIZE)

def osgr_to_grid(osgr):
    return Osgr(osgr.easting - (osgr.easting % CELLSIZE),
        osgr.northing - (osgr.northing % CELLSIZE))

def get_filename(osgr):
    filename = osgr.toStr(prec=2, sep='') + '.bin'
    return filename

def get_lat_lon_from_indices(x, y, filename):
    osgr = get_osgr_from_indices(x+1, y, filename)
    latlon = osgr.toLatLon(eV.LatLon)
    return (latlon.lat, latlon.lon)

def get_osgr_from_indices(x, y, filename):
    easting = (x + int(filename[-6])*NCOLS) * CELLSIZE
    northing = ((NROWS - 1 - y) + int(filename[-5])*NROWS) * CELLSIZE
    letters = filename[-8:-6]
    osgr = parseOSGR('{}{:05d}{:05d}'.format(letters, easting, northing))
    return osgr

def get_height(lat, lon):
    try:
        osgr = toOsgr(eV.LatLon(lat, lon))
        if len(osgr.toStr()) == 0:
            raise ValueError('not a valid OSGR coordinate')
    except ValueError as e:
        return {
            'altitude_m': NODATA, 'source': attribution_name, 'latitude': lat,
            'lon': lon, 'distance_m': 0, 'attribution': attribution}
    # fit request to the grid
    osgr = osgr_to_grid(osgr)
    latlon = osgr.toLatLon(eV.LatLon)
    lat_found = latlon.lat
    lon_found = latlon.lon
    filename = get_filename(osgr)
    full_path = os.path.join(path, filename[:2].lower(), filename)
    if not os.path.isfile(full_path):
        return {
            'altitude_m': NODATA, 'source': attribution_name, 'latitude': lat,
            'longitude': lon, 'distance_m': 0, 'attribution': attribution}
    x = get_x(osgr)
    y = get_y(osgr)
    with open(full_path, "rb") as f:
        # go to the right spot,
        f.seek((y * NCOLS + x) * 4)
        # read four bytes and convert them:
        buf = f.read(4)
        # ">f" is a four byte float
        val = struct.unpack('>f', buf)[0]
        return {
            'latitude': lat, 'longitude': lon, 'latitude_found': round(
            lat_found, 6), 'longitude_found': round(lon_found, 6),
            'altitude_m': round(val, 2), 'source': attribution_name,
            'distance_m': round(calculate_distance(lat, lon, lat_found,
            lon_found), 3), 'attribution': attribution}

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    # consider only correctly defined rectangle:
    if (lat_ll > lat_ur or lon_ll > lon_ur):
        return ([], NODATA, 0)
    try:
        osgr_ll = toOsgr(eV.LatLon(lat_ll, lon_ll))
        if len(osgr_ll.toStr()) == 0:
            raise ValueError('not a valid OSGR coordinate')
    except ValueError as e:
        return ([], NODATA, 0)
    try:
        osgr_ur = toOsgr(eV.LatLon(lat_ur, lon_ur))
        if len(osgr_ur.toStr()) == 0:
            raise ValueError('not a valid OSGR coordinate')
    except ValueError as e:
        return ([], NODATA, 0)
    file_list = {}
    create_filelist(osgr_ll, osgr_ur, file_list)
    raw_length = len(file_list)
    lowest_max = check_max_list(file_list)
    new_length = len(file_list)
    (osgr_list, h_max, counter) = check_max_files(file_list)
    latlon_list = []
    for osgr in osgr_list:
        latlon = osgr.toLatLon(eV.LatLon)
        latlon_list += [(latlon.lat, latlon.lon)]
    return (latlon_list, h_max, counter)

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    # consider only correctly defined rectangle:
    if (lat_ll > lat_ur or lon_ll > lon_ur):
        return ([], NODATA, 0)
    try:
        osgr_ll = toOsgr(eV.LatLon(lat_ll, lon_ll))
        if len(osgr_ll.toStr()) == 0:
            raise ValueError('not a valid OSGR coordinate')
    except ValueError as e:
        return ([], NODATA, 0)
    try:
        osgr_ur = toOsgr(eV.LatLon(lat_ur, lon_ur))
        if len(osgr_ur.toStr()) == 0:
            raise ValueError('not a valid OSGR coordinate')
    except ValueError as e:
        return ([], NODATA, 0)
    file_list = {}
    create_filelist(osgr_ll, osgr_ur, file_list)
    raw_length = len(file_list)
    largest_min = check_min_list(file_list)
    new_length = len(file_list)
    (osgr_list, h_min, counter) = check_min_files(file_list)
    latlon_list = []
    for osgr in osgr_list:
        latlon = osgr.toLatLon(eV.LatLon)
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
    osgr_list = []
    counter = 0
    for filename, list_item in file_list.items():
        x_ll = list_item['x_ll']
        y_ll = list_item['y_ll']
        x_ur = list_item['x_ur']
        y_ur = list_item['y_ur']
        x_pos = x_ll
        y_pos = y_ur
        full_path = os.path.join(path, filename[:2].lower(), filename)
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
                        osgr_list = [get_osgr_from_indices(x_pos, y_pos,
                            filename)]
                        counter = 1
                    elif values[x_pos - x_ll] == h_max:
                        osgr_list += [get_osgr_from_indices(x_pos, y_pos,
                                                            filename)]
                        counter += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
    return (osgr_list, h_max, counter)

def check_min_files(file_list):
    h_min = -NODATA
    osgr_list = []
    counter = 0
    for filename, list_item in file_list.items():
        x_ll = list_item['x_ll']
        y_ll = list_item['y_ll']
        x_ur = list_item['x_ur']
        y_ur = list_item['y_ur']
        x_pos = x_ll
        y_pos = y_ur
        full_path = os.path.join(path, filename[:2].lower(), filename)
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
                        osgr_list = [get_osgr_from_indices(x_pos, y_pos,
                            filename)]
                        counter = 1
                    elif (NODATA < values[x_pos - x_ll] == h_min):
                        osgr_list += [get_osgr_from_indices(x_pos, y_pos,
                                                            filename)]
                        counter += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
    if h_min == -NODATA:
        h_min = NODATA
    return (osgr_list, h_min, counter)

def create_filelist(osgr_ll, osgr_ur, file_list):
    # obtain the coordinates of the tile containing the lower left
    easting_ll_tile = osgr_ll.easting - osgr_ll.easting % (NCOLS * CELLSIZE)
    northing_ll_tile = osgr_ll.northing - osgr_ll.northing % (NROWS * CELLSIZE)
    # convert coordinates to data indices:
    x_ll = get_x(osgr_ll)
    y_ll = get_y(osgr_ll)
    if osgr_ur.northing - northing_ll_tile < NROWS * CELLSIZE:
        y_ur = get_y(osgr_ur)
    else:
        # upper neighbour
        create_filelist(
            Osgr(osgr_ll.easting, northing_ll_tile + NROWS*CELLSIZE),
            Osgr(min(osgr_ur.easting, easting_ll_tile + (NCOLS - 1)*CELLSIZE),
            osgr_ur.northing), file_list)
        y_ur = 0
    if osgr_ur.easting - easting_ll_tile < NCOLS * CELLSIZE:
        x_ur = get_x(osgr_ur)
    else:
        # right neighbour
        create_filelist(Osgr(easting_ll_tile + NCOLS*CELLSIZE,
                             osgr_ll.northing), osgr_ur, file_list)
        x_ur = NCOLS - 1
    filename = get_filename(osgr_ll)
    full_path = os.path.join(path, filename[:2].lower(), filename)
    if os.path.isfile(full_path):
        complete = (y_ur == 0 and x_ll == 0 and x_ur == NCOLS - 1
                    and y_ll == NROWS - 1)
        file_list[filename] = {'x_ll': x_ll, 'y_ll': y_ll, 'x_ur': x_ur,
                               'y_ur': y_ur, 'complete': complete}

