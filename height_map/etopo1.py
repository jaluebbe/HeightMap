import struct
import os
from height_map.dgm200 import calculate_distance

# original file header:
# header = {
#     'NCOLS': 21601, 'XLLCENTER': -180.000000, 'CELLSIZE': 0.01666666667,
#     'NROWS': 10801, 'YLLCENTER': -90.000000, 'NODATA_VALUE': -32768,
#     'ZUNITS':'METERS', 'MIN_VALUE':-10898, 'MAX_VALUE':8271,
#     'BYTEORDER':'LSBFIRST', 'NUMBERTYPE':'2_BYTE_INTEGER'}

filename_ice = 'etopo1_ice_g_i2.bin'
filename_bed = 'etopo1_bed_g_i2.bin'

NCOLS = 21601
NROWS = 10801
CELLSIZE = 1./60
XLLCENTER = -180.0
YLLCENTER = -90.0
NODATA = -32768
pwd = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(pwd, 'maps/etopo1')
attribution_url = 'https://dx.doi.org/10.7289/V5C8276M'
attribution_name = 'ETOPO1'
attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
    attribution_name)


def get_index_from_latitude(lat):
    return NROWS - int(round((lat - YLLCENTER) / CELLSIZE)) - 1


def get_index_from_longitude(lon):
    return int(round((lon - XLLCENTER) / CELLSIZE))


def get_lat_from_index(i):
    return (NROWS - i - 1)*CELLSIZE + YLLCENTER


def get_lon_from_index(j):
    return j*CELLSIZE + XLLCENTER


def get_height(lat, lon, ice=True):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
    if ice:
        filename = filename_ice
    else:
        filename = filename_bed
    file = os.path.join(path, filename)
    val = NODATA
    lat_found = lat
    lon_found = lon
    if os.path.isfile(file):
        i = get_index_from_latitude(lat)
        j = get_index_from_longitude(lon)
        lat_found = get_lat_from_index(i)
        lon_found = get_lon_from_index(j)
        with open(file, "rb") as f:
            # go to the right spot,
            f.seek((i*NCOLS + j) * 2)
            # read two bytes and convert them:
            buf = f.read(2)
            # "<h" is a signed two byte integer
            val = struct.unpack('<h', buf)[0]
    return {
        'lat': lat, 'long': lon, 'lat_found': round(lat_found, 6),
        'lon_found': round(lon_found, 6), 'altitude_m': val,
        'source': attribution_name, 'distance_m': round(calculate_distance(lat,
        lon, lat_found, lon_found), 3), 'attribution': attribution}


def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur, ice=True):
    h_max = NODATA
    location_max = []
    counter = 0
    # consider only correctly defined rectangle:
    if lat_ll > lat_ur or lon_ll > lon_ur:
        return location_max, h_max, counter
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll)
    j_ll = get_index_from_longitude(lon_ll)
    i_ur = get_index_from_latitude(lat_ur)
    j_ur = get_index_from_longitude(lon_ur)
    # start in the upper left edge of the target area
    i_pos = i_ur
    j_pos = j_ll
    #
    if ice:
        filename = filename_ice
    else:
        filename = filename_bed
    file = os.path.join(path, filename)
    if os.path.isfile(file):
        with open(file, "rb") as f:
            while i_ur <= i_pos <= i_ll:
                f.seek((i_pos*NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1
                buf = f.read(num_values * 2)
                values = struct.unpack('<{:d}h'.format(num_values), buf)
                while j_ll <= j_pos <= j_ur:
                    val = values[j_pos - j_ll]
                    # if current height value larger than previous maximum
                    if val > h_max:
                        # store current height and location
                        h_max = val
                        location_max = [(get_lat_from_index(i_pos),
                                         get_lon_from_index(j_pos))]
                        counter = 1
                    elif val == h_max:
                        location_max += [(get_lat_from_index(i_pos),
                                          get_lon_from_index(j_pos))]
                        counter += 1
                    j_pos += 1
                j_pos = j_ll
                i_pos += 1
    return location_max, h_max, counter


def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur, ice=True):
    location_min = []
    counter = 0
    # consider only correctly defined rectangle:
    if lat_ll > lat_ur or lon_ll > lon_ur:
        return location_min, NODATA, counter
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll)
    j_ll = get_index_from_longitude(lon_ll)
    i_ur = get_index_from_latitude(lat_ur)
    j_ur = get_index_from_longitude(lon_ur)
    #
    h_min = -NODATA
    i_pos = i_ur
    j_pos = j_ll
    #
    if ice:
        filename = filename_ice
    else:
        filename = filename_bed
    file = os.path.join(path, filename)
    if os.path.isfile(file):
        with open(file, "rb") as f:
            while i_ur <= i_pos <= i_ll:
                f.seek((i_pos*NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1
                buf = f.read(num_values * 2)
                values = struct.unpack('<{:d}h'.format(num_values), buf)
                while j_ll <= j_pos <= j_ur:
                    val = values[j_pos - j_ll]
                    if NODATA < val < h_min:
                        h_min = val
                        location_min = [(get_lat_from_index(i_pos),
                                         get_lon_from_index(j_pos))]
                        counter = 1
                    elif NODATA < val == h_min:
                        location_min += [(get_lat_from_index(i_pos),
                                         get_lon_from_index(j_pos))]
                        counter += 1
                    j_pos += 1
                j_pos = j_ll
                i_pos += 1
    if h_min == -NODATA:
        h_min = NODATA
    return location_min, h_min, counter
