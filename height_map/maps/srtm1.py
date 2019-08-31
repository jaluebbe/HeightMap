import struct
from math import floor, ceil
import json
import os

NCOLS = 3601
NROWS = 3601
CELLSIZE = 1./3600
NODATA = -32768
path = 'height_map/maps/srtm1'
attribution_url = 'https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003'
attribution_name = 'SRTMGL1'
attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
    attribution_name)

precision = 16.0  # 16m SRTM vertical error

if os.path.isfile(os.path.join(path, 'srtm1_files.json')):
    with open(os.path.join(path, 'srtm1_files.json')) as srtm1_list_file:
        srtm1_file_list = json.load(srtm1_list_file)
else:
    srtm1_file_list = []

def get_index_from_latitude(lat, yllcenter):
    return NROWS - int(round((lat - yllcenter) / CELLSIZE)) - 1

def get_index_from_longitude(lon, xllcenter):
    return int(round((lon - xllcenter) / CELLSIZE)) 

def get_lat_from_index(i, yllcenter):
    return (NROWS - i - 1)*CELLSIZE + yllcenter

def get_lon_from_index(j, xllcenter):
    return j*CELLSIZE + xllcenter

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    xllcenter = floor(lon_ll)
    yllcenter = floor(lat_ll)
    total_location = []
    total_h_max = NODATA
    total_counter = 0
    # consider only correctly defined rectangle within SRTM coverage:
    if ((lat_ll > lat_ur) or (lon_ll > lon_ur) or lat_ur > 60 or lat_ll < -56):
        return ([], NODATA, 0)
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll, yllcenter)
    j_ll = get_index_from_longitude(lon_ll, xllcenter)
    if lat_ur < yllcenter + 1 + CELLSIZE/2:
        i_ur = get_index_from_latitude(lat_ur, yllcenter)
    else:
        # upper_neighbour
        (location, h_max, counter) = get_max_height(
            yllcenter + 1 + CELLSIZE/2, lon_ll, lat_ur, min(lon_ur, xllcenter + 1))
        if h_max > total_h_max:
            total_h_max = h_max
            total_counter = counter
            total_location = location
        elif h_max == total_h_max:
            total_counter += counter
            total_location += location
        i_ur = 0
    if lon_ur < xllcenter + 1 + CELLSIZE/2:
        j_ur = get_index_from_longitude(lon_ur, xllcenter)
    else:
        # right_neighbour
        (location, h_max, counter) = get_max_height(
            lat_ll, xllcenter + 1 + CELLSIZE/2, lat_ur, lon_ur)
        if h_max > total_h_max:
            total_h_max = h_max
            total_counter = counter
            total_location = location
        elif h_max == total_h_max:
            total_counter += counter
            total_location += location
        j_ur = NCOLS - 1
    h_max = NODATA
    counter = 0
    location = []
    # start in the upper left edge of the target area
    i_pos = i_ur
    j_pos = j_ll
    #
    file_name = get_filename(yllcenter, xllcenter)
    fullpath = os.path.join(path, file_name)
    if os.path.isfile(fullpath):
        with open(fullpath, "rb") as f:
            while(i_ur <= i_pos <= i_ll):
                f.seek((i_pos * NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1
                buf = f.read(num_values * 2)
                values = struct.unpack('>{:d}h'.format(num_values), buf)
                while(j_ll <= j_pos <= j_ur):
                    # if current height value larger than previous maximum
                    if values[j_pos - j_ll] > h_max:
                        # store current height and position
                        h_max = values[j_pos - j_ll]
                        lat = get_lat_from_index(i_pos, yllcenter)
                        lon = get_lon_from_index(j_pos, xllcenter)
                        location = [(lat, lon)]
                        counter = 1
                    elif values[j_pos - j_ll] == h_max:
                        lat = get_lat_from_index(i_pos, yllcenter)
                        lon = get_lon_from_index(j_pos, xllcenter)
                        location += [(lat, lon)]
                        counter += 1
                    j_pos += 1
                j_pos = j_ll
                i_pos += 1
        if h_max > total_h_max:
            total_h_max = h_max
            total_counter = counter
            total_location = location
        elif h_max == total_h_max:
            total_counter += counter
            total_location += location
    elif file_name in srtm1_file_list:
        print('SRTM1: missing file', file_name)
    return (total_location, total_h_max, total_counter)

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    xllcenter = floor(lon_ll)
    yllcenter = floor(lat_ll)
    total_location = []
    total_h_min = -NODATA
    total_counter = 0
    # consider only correctly defined rectangle:
    if ((lat_ll > lat_ur) or (lon_ll > lon_ur) or lat_ur > 60 or lat_ll < -56):
        return ([], NODATA, 0)
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll, yllcenter)
    j_ll = get_index_from_longitude(lon_ll, xllcenter)
    if lat_ur < yllcenter + 1 + CELLSIZE/2:
        i_ur = get_index_from_latitude(lat_ur, yllcenter)
    else:
        # upper_neighbour
        (location, h_min, counter) = get_min_height(
            yllcenter + 1 + CELLSIZE/2, lon_ll, lat_ur, min(lon_ur, xllcenter + 1))
        if (NODATA < h_min < total_h_min):
            total_h_min = h_min
            total_counter = counter
            total_location = location
        elif h_min == total_h_min:
            total_counter += counter
            total_location += location
        i_ur = 0
    if lon_ur < xllcenter + 1 + CELLSIZE/2:
        j_ur = get_index_from_longitude(lon_ur, xllcenter)
    else:
        # right_neighbour
        (location, h_min, counter) = get_min_height(
            lat_ll, xllcenter + 1 + CELLSIZE/2, lat_ur, lon_ur)
        if (NODATA < h_min < total_h_min):
            total_h_min = h_min
            total_counter = counter
            total_location = location
        elif h_min == total_h_min:
            total_counter += counter
            total_location += location
        j_ur = NCOLS - 1
    h_min = -NODATA
    counter = 0
    location = []
    # start in the upper left edge of the target area
    i_pos = i_ur
    j_pos = j_ll
    #
    file_name = get_filename(yllcenter, xllcenter)
    fullpath = os.path.join(path, file_name)
    if os.path.isfile(fullpath):
        with open(fullpath, "rb") as f:
            while(i_ur <= i_pos <= i_ll):
                f.seek((i_pos * NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1 
                buf = f.read(num_values * 2) 
                values = struct.unpack('>{:d}h'.format(num_values), buf) 
                while(j_ll <= j_pos <= j_ur):
                    # if current height value larger than previous maximum
                    if (NODATA < values[j_pos - j_ll] < h_min):
                        # store current height and position
                        h_min = values[j_pos - j_ll]
                        lat = get_lat_from_index(i_pos, yllcenter)
                        lon = get_lon_from_index(j_pos, xllcenter)
                        location = [(lat, lon)]
                        counter = 1
                    elif (NODATA < values[j_pos - j_ll] == h_min):
                        lat = get_lat_from_index(i_pos, yllcenter)
                        lon = get_lon_from_index(j_pos, xllcenter)
                        location += [(lat, lon)]
                        counter += 1
                    j_pos += 1
                j_pos = j_ll
                i_pos += 1
        if h_min == -NODATA:
            h_min = NODATA
        if (NODATA < h_min < total_h_min):
            total_h_min = h_min
            total_counter = counter
            total_location = location
        elif h_min == total_h_min:
            total_counter += counter
            total_location += location
    elif file_name in srtm1_file_list:
        print('SRTM1: missing file', file_name)
    return (total_location, total_h_min, total_counter)

def get_height(lat, lon):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
    xllcenter = floor(lon)
    yllcenter = floor(lat)
    file_name = get_filename(yllcenter, xllcenter)
    fullpath = os.path.join(path, file_name)
    val = NODATA
    if os.path.isfile(fullpath):
        # verified with 
        # gdallocationinfo N52W002.hgt -wgs84 -1.215090 52.925315
        i = get_index_from_latitude(lat, yllcenter)
        j = get_index_from_longitude(lon, xllcenter)
        with open(fullpath, "rb") as f:
            # go to the right spot,
            f.seek((i*NCOLS + j) * 2)
            # read two bytes and convert them:
            buf = f.read(2)
            # ">h" is a signed two byte integer
            val = struct.unpack('>h', buf)[0]
            # turn indices back to coordinates
            lat = get_lat_from_index(i, yllcenter)
            lon = get_lon_from_index(j, xllcenter)
    elif not (lat > 60 or lat < -56) and file_name in srtm1_file_list:
        print('SRTM1: missing file', file_name)
    return (val, lat, lon)

def get_filename(yllcenter, xllcenter):
    if (xllcenter >= 0):
        filename = "N{:02.0f}E{:03.0f}.hgt".format(yllcenter, xllcenter)
    else:
        filename = "N{:02.0f}W{:03.0f}.hgt".format(yllcenter, -xllcenter)
    return filename    
