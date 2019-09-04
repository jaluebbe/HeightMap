import h5py
import os

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
