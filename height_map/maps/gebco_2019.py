import h5py
import os
import numpy as np

attribution_url = ('https://www.gebco.net/data_and_products/'
    'gridded_bathymetry_data/gebco_2019/gebco_2019_info.html')
attribution_name = 'The GEBCO Grid'
attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
    attribution_name)        
path = 'height_map/maps/gebco_2019'
filename = 'GEBCO_2019.nc'
NCOLS = 86400
NROWS = 43200
CELLSIZE = 1./240
XLLCENTER = -180.
YLLCENTER = -90.
NODATA = -32768

def get_index_from_latitude(lat):
    return max(min(int(round((lat - YLLCENTER) / CELLSIZE)), (NROWS - 1)), 0)

def get_index_from_longitude(lon):
    return int(round((lon - XLLCENTER) / CELLSIZE)) % NCOLS

def get_lat_from_index(i):
    return i*CELLSIZE + YLLCENTER

def get_lon_from_index(j):
    return j*CELLSIZE + XLLCENTER

def get_height(lat, lon):
    if not (-90 <= lat <= 90 and -180 <= 90 <= 180):
        raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
    file = os.path.join(path, filename)
    val = NODATA
    if os.path.isfile(file):
        i = get_index_from_latitude(lat)
        j = get_index_from_longitude(lon)
        lat = get_lat_from_index(i)
        lon = get_lon_from_index(j)
        with h5py.File(file, 'r') as f:
            val = round(float(f['elevation'][i][j]), 1)
    return (val, lat, lon)

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    h_max = NODATA
    location_max = []
    counter = 0
    if lon_ur >= 180 - CELLSIZE/2:
        lon_ur -= CELLSIZE
    # consider only correctly defined rectangle:
    if ((lat_ll > lat_ur) or (lon_ll > lon_ur)):
        return (location_max, NODATA, counter)
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll)
    j_ll = get_index_from_longitude(lon_ll)
    i_ur = get_index_from_latitude(lat_ur)
    j_ur = get_index_from_longitude(lon_ur)
    file = os.path.join(path, filename)
    if os.path.isfile(file):
        with h5py.File(file, 'r') as f:
            selection = f['elevation'][i_ll:i_ur+1, j_ll:j_ur+1]
            h_max = selection.max()
            x, y = np.where(selection==h_max)
            counter = len(x)
            for _index in range(counter):
                location_max += [(get_lat_from_index(i_ll+x[_index]),
                    get_lon_from_index(j_ll+y[_index]))]
    return (location_max, round(float(h_max), 1), counter)

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    location_min = []
    counter = 0
    if lon_ur >= 180 - CELLSIZE/2:
        lon_ur -= CELLSIZE
    # consider only correctly defined rectangle:
    if ((lat_ll > lat_ur) or (lon_ll > lon_ur)):
        return (location_min, NODATA, counter)
    # convert coordinates to data indices:
    i_ll = get_index_from_latitude(lat_ll)
    j_ll = get_index_from_longitude(lon_ll)
    i_ur = get_index_from_latitude(lat_ur)
    j_ur = get_index_from_longitude(lon_ur)
    h_min = -NODATA
    file = os.path.join(path, filename)
    if os.path.isfile(file):
        with h5py.File(file, 'r') as f:
            selection = f['elevation'][i_ll:i_ur+1, j_ll:j_ur+1]
            h_min = selection.min()
            x, y = np.where(selection==h_min)
            counter = len(x)
            for _index in range(counter):
                location_min += [(get_lat_from_index(i_ll+x[_index]),
                    get_lon_from_index(j_ll+y[_index]))]
    if h_min == -NODATA:
        h_min = NODATA
    return (location_min, round(float(h_min), 1), counter)
