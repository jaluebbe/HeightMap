import struct
import os
from height_map.dgm200 import calculate_distance

filename_ice = 'Earth2014.TBI2014.1min.geod.bin'
filename_bed = 'Earth2014.BED2014.1min.geod.bin'
filename_water = 'Earth2014.SUR2014.1min.geod.bin'

NCOLS = 21600
NROWS = 10800
CELLSIZE = 1./60
XLLCENTER = -180.0 + CELLSIZE / 2
YLLCENTER = -90.0 + CELLSIZE / 2
NODATA = -32768
path = 'height_map/maps/earth2014'
attribution_url = 'http://ddfe.curtin.edu.au/models/Earth2014/'
attribution_name = 'EARTH2014'
attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
    attribution_name)
ICE_DEFAULT = True
WATER_DEFAULT = False


def get_index_from_latitude(lat):
    return max(min(int(round((lat - YLLCENTER) / CELLSIZE)), (NROWS - 1)), 0)

def get_index_from_longitude(lon):
    return (int(round((lon - XLLCENTER) / CELLSIZE)) ) % NCOLS

def get_lat_from_index(i):
    return i*CELLSIZE + YLLCENTER

def get_lon_from_index(j):
    return j*CELLSIZE + XLLCENTER

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur, ice=None, water=None):
    if ice is None:
        ice = ICE_DEFAULT
    if water is None:
        water = WATER_DEFAULT
    h_max = NODATA
    location_max = []
    counter = 0
    if lon_ur == 180:
        lon_ur -= CELLSIZE / 2 
    # consider only correctly defined rectangle:
    if ((lat_ll > lat_ur) or (lon_ll > lon_ur)): 
        return (location_max, h_max, counter)
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll)
    j_ll = get_index_from_longitude(lon_ll)
    i_ur = get_index_from_latitude(lat_ur)
    j_ur = get_index_from_longitude(lon_ur)
    # start in the lower left edge of the target area
    i_pos = i_ll
    j_pos = j_ll
    #
    if water:
        filename = filename_water  # SUR  
    elif ice:      
        filename = filename_ice  # TBI        
    else:            
        filename = filename_bed  # BED   
    file = os.path.join(path, filename)
    if os.path.isfile(file): 
        with open(file, "rb") as f:
            while(i_ur >= i_pos >= i_ll):
                f.seek((i_pos*NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1
                buf = f.read(num_values * 2)
                values = struct.unpack('>{:d}h'.format(num_values), buf)
                while(j_ll <= j_pos <= j_ur):
                    val = values[j_pos - j_ll]
                    # if current height value larger than previous maximum
                    if val > h_max:
                        # store current height
                        h_max = val
                        # and position indices
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
    return (location_max, h_max, counter)

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur, ice=None, water=None):
    if ice is None:
        ice = ICE_DEFAULT
    if water is None:
        water = WATER_DEFAULT
    h_min = -NODATA
    location_min = []
    counter = 0
    if lon_ur == 180:
        lon_ur -= CELLSIZE / 2
    # consider only correctly defined rectangle:
    if ((lat_ll > lat_ur) or (lon_ll > lon_ur)):
        return (location_min, NODATA, counter)
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll)
    j_ll = get_index_from_longitude(lon_ll)
    i_ur = get_index_from_latitude(lat_ur)
    j_ur = get_index_from_longitude(lon_ur)
    #
    i_pos = i_ll
    j_pos = j_ll
    #
    if water:
        filename = filename_water  # SUR
    elif ice:
        filename = filename_ice  # TBI
    else:
        filename = filename_bed  # BED
    file = os.path.join(path, filename)
    if os.path.isfile(file):
        with open(file, "rb") as f:
            while(i_ur >= i_pos >= i_ll):
                f.seek((i_pos*NCOLS + j_pos) * 2)
                num_values = j_ur - j_ll + 1
                buf = f.read(num_values * 2)
                values = struct.unpack('>{:d}h'.format(num_values), buf)
                while(j_ll <= j_pos <= j_ur):
                    val = values[j_pos - j_ll]      
                    if (NODATA < val < h_min):
                        h_min = val
                        location_min = [(get_lat_from_index(i_pos),
                                         get_lon_from_index(j_pos))]
                        counter = 1
                    elif (NODATA < val == h_min):
                        location_min += [(get_lat_from_index(i_pos),
                                         get_lon_from_index(j_pos))]
                        counter += 1
                    j_pos += 1
                j_pos = j_ll
                i_pos += 1
    if h_min == -NODATA:
        h_min = NODATA
    return (location_min, h_min, counter)

def get_height(lat, lon, ice=None, water=None):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
    if ice is None:
        ice = ICE_DEFAULT
    if water is None:
        water = WATER_DEFAULT
    if water:
        filename = filename_water  # SUR
    elif ice:
        filename = filename_ice  # TBI
    else:
        filename = filename_bed  # BED
    file = os.path.join(path, filename)
    val = NODATA
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
            # ">h" is a signed two byte integer
            val = struct.unpack('>h', buf)[0]
    return {
        'altitude_m': val, 'source': attribution_name, 'latitude': lat_found,
        'longitude': lon_found, 'distance_m': calculate_distance(lat, lon,
        lat_found, lon_found), 'attribution': attribution}
