import h5py
import os
import json
import numpy as np
from height_map import calculate_distance
from height_map.timeit import timeit

NCOLS = 86400
NROWS = 43200
CELLSIZE = 1./240
XLLCENTER = -180.
YLLCENTER = -90.


def get_index_from_latitude(lat):
    return max(min(int(round((lat - YLLCENTER) / CELLSIZE)), (NROWS - 1)), 0)


def get_index_from_longitude(lon):
    return int(round((lon - XLLCENTER) / CELLSIZE)) % NCOLS


def get_lat_from_index(i):
    return round(i*CELLSIZE + YLLCENTER, 6)


def get_lon_from_index(j):
    return round(j*CELLSIZE + XLLCENTER, 6)


class Gebco:
    attribution_url = ('https://www.gebco.net/data_and_products/'
        'gridded_bathymetry_data/gebco_2020/')
    attribution_name = 'GEBCO_2020 Grid'
    attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
        attribution_name)
    seabed_included = True
    NODATA = -32768
    old_i = None
    old_j = None
    old_val = None
    h5_file = None

    def __init__(self, path=None, file_name=None, cache_path=None,
            cache_file_name=None):
        pwd = os.path.dirname(os.path.abspath(__file__))
        if path is None:
            path = os.path.join(pwd, 'maps/gebco')
        if file_name is None:
            file_name = 'GEBCO_2020.nc'
        if cache_path is None:
            self.cache_path = pwd
        if cache_file_name is None:
            self.cache_file_name = 'gebco_2020_cache.json'
        file = os.path.join(path, file_name)
        if os.path.isfile(file):
            self.h5_file = h5py.File(file, 'r')
        else:
            raise FileNotFoundError(file)

    def get_height(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        val = self.NODATA
        i = get_index_from_latitude(lat)
        j = get_index_from_longitude(lon)
        lat_found = get_lat_from_index(i)
        lon_found = get_lon_from_index(j)
        if self.h5_file is None:
            pass
        elif self.old_i == i and self.old_j == j:
            # same grid position, file access not necessary
            val = self.old_val
        else:
            val = round(float(self.h5_file['elevation'][i][j]), 2)
            self.old_i = i
            self.old_j = j
            self.old_val = val
        distance = calculate_distance(lat, lon, lat_found, lon_found)
        return {
            'lat': lat, 'lon': lon, 'lat_found': round(lat_found, 6),
            'lon_found': round(lon_found, 6), 'altitude_m': val,
            'source': self.attribution_name,
            'distance_m': round(distance, 3), 'attributions': [self.attribution]}

    @timeit
    def get_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        result = {'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        if lon_ur >= 180 - CELLSIZE/2:
            lon_ur -= CELLSIZE
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll)
        j_ll = get_index_from_longitude(lon_ll)
        i_ur = get_index_from_latitude(lat_ur)
        j_ur = get_index_from_longitude(lon_ur)
        result.update(self.get_max_height_from_indices(i_ll, j_ll, i_ur, j_ur))
        result['location_max'] = [[get_lat_from_index(_x),
            get_lon_from_index(_y)] for (_x, _y) in result['location_max']]
        return result

    @timeit
    def get_min_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        result = {'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        if lon_ur >= 180 - CELLSIZE/2:
            lon_ur -= CELLSIZE
        # consider only correctly defined rectangle:
        if (lat_ll > lat_ur) or (lon_ll > lon_ur):
            return result
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll)
        j_ll = get_index_from_longitude(lon_ll)
        i_ur = get_index_from_latitude(lat_ur)
        j_ur = get_index_from_longitude(lon_ur)
        result.update(self.get_min_height_from_indices(i_ll, j_ll, i_ur, j_ur))
        result['location_min'] = [[get_lat_from_index(_x),
            get_lon_from_index(_y)] for (_x, _y) in result['location_min']]
        if result['h_min'] == -self.NODATA:
            result['h_min'] = self.NODATA
        return result

    @timeit
    def get_min_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        result = {
            'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        if lon_ur >= 180 - CELLSIZE/2:
            lon_ur -= CELLSIZE
        # consider only correctly defined rectangle:
        if (lat_ll > lat_ur) or (lon_ll > lon_ur):
            return result
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll)
        j_ll = get_index_from_longitude(lon_ll)
        i_ur = get_index_from_latitude(lat_ur)
        j_ur = get_index_from_longitude(lon_ur)
        result.update(self.get_min_max_height_from_indices(i_ll, j_ll, i_ur,
            j_ur))
        result['location_max'] = [[get_lat_from_index(_x),
            get_lon_from_index(_y)] for (_x, _y) in result['location_max']]
        result['location_min'] = [[get_lat_from_index(_x),
            get_lon_from_index(_y)] for (_x, _y) in result['location_min']]
        if result['h_min'] == -self.NODATA:
            result['h_min'] = self.NODATA
        return result

    @timeit
    def get_max_height_from_h5file(self, i_ll, j_ll, i_ur, j_ur):
        h_max = self.NODATA
        locations_max = []
        counter_max = 0
        if self.h5_file is not None and i_ll < i_ur and j_ll < j_ur:
            selection = self.h5_file['elevation'][i_ll:i_ur, j_ll:j_ur]
            h_max = selection.max()
            x_max, y_max = np.where(selection == h_max)
            counter_max = len(x_max)
            locations_max = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_max, y_max)]
        return {'location_max': locations_max, 'h_max': round(float(h_max), 1),
            'counter_max': counter_max}

    @timeit
    def get_min_height_from_h5file(self, i_ll, j_ll, i_ur, j_ur):
        h_min = -self.NODATA
        locations_min = []
        counter_min = 0
        if self.h5_file is not None and i_ll < i_ur and j_ll < j_ur:
            selection = self.h5_file['elevation'][i_ll:i_ur, j_ll:j_ur]
            h_min = selection.min()
            x_min, y_min = np.where(selection == h_min)
            counter_min = len(x_min)
            locations_min = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_min, y_min)]
        return {'location_min': locations_min, 'h_min': round(float(h_min), 1),
            'counter_min': counter_min}

    @timeit
    def get_min_max_height_from_h5file(self, i_ll, j_ll, i_ur, j_ur):
        h_max = self.NODATA
        locations_max = []
        counter_max = 0
        h_min = -self.NODATA
        locations_min = []
        counter_min = 0
        if self.h5_file is not None and i_ll < i_ur and j_ll < j_ur:
            selection = self.h5_file['elevation'][i_ll:i_ur, j_ll:j_ur]
            h_max = selection.max()
            x_max, y_max = np.where(selection == h_max)
            counter_max = len(x_max)
            locations_max = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_max, y_max)]
            h_min = selection.min()
            x_min, y_min = np.where(selection == h_min)
            counter_min = len(x_min)
            locations_min = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_min, y_min)]
        return {
            'location_max': locations_max, 'h_max': round(float(h_max), 1),
            'counter_max': counter_max, 'location_min': locations_min,
            'h_min': round(float(h_min), 1), 'counter_min': counter_min}

    @timeit
    def get_max_locations_from_cache(self, i_ll, j_ll, i_ur, j_ur):
        locations_max = []
        cache_file = os.path.join(self.cache_path, self.cache_file_name)
        if os.path.isfile(cache_file) and i_ll < i_ur and j_ll < j_ur:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            max_cache = np.array(cache_data['maximum'])
            selection = max_cache[i_ll:i_ur, j_ll:j_ur]
            h_max = selection.max()
            x_max, y_max = np.where(selection == h_max)
            locations_max = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_max, y_max)]
        elif not os.path.isfile(cache_file):
            raise FileNotFoundError('GEBCO min/max cache file is missing.')
        return locations_max

    @timeit
    def get_min_locations_from_cache(self, i_ll, j_ll, i_ur, j_ur):
        locations_min = []
        cache_file = os.path.join(self.cache_path, self.cache_file_name)
        if os.path.isfile(cache_file) and i_ll < i_ur and j_ll < j_ur:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            min_cache = np.array(cache_data['minimum'])
            selection = min_cache[i_ll:i_ur, j_ll:j_ur]
            h_min = selection.min()
            x_min, y_min = np.where(selection == h_min)
            locations_min = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_min, y_min)]
        elif not os.path.isfile(cache_file):
            raise FileNotFoundError('GEBCO min/max cache file is missing.')
        return locations_min

    @timeit
    def get_min_max_locations_from_cache(self, i_ll, j_ll, i_ur, j_ur):
        locations = []
        cache_file = os.path.join(self.cache_path, self.cache_file_name)
        if os.path.isfile(cache_file) and i_ll < i_ur and j_ll < j_ur:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            max_cache = np.array(cache_data['maximum'])
            selection = max_cache[i_ll:i_ur, j_ll:j_ur]
            h_max = selection.max()
            x_max, y_max = np.where(selection == h_max)
            locations_max = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_max, y_max)]
            min_cache = np.array(cache_data['minimum'])
            selection = min_cache[i_ll:i_ur, j_ll:j_ur]
            h_min = selection.min()
            x_min, y_min = np.where(selection == h_min)
            locations_min = [(i_ll+_x, j_ll+_y) for _x, _y in zip(x_min, y_min)]
            locations = set(locations_max + locations_min)
        elif not os.path.isfile(cache_file):
            raise FileNotFoundError('GEBCO min/max cache file is missing.')
        return locations

    @timeit
    def get_max_height_from_indices(self, i_ll, j_ll, i_ur, j_ur):
        i_ur = i_ur + 1
        j_ur = j_ur + 1
        h_max = self.NODATA
        location_max = []
        counter_max = 0
        h5_results = []
        if i_ll % 240 != 0:
            i_ll_cache = i_ll + 240 - i_ll%240
        else:
            i_ll_cache = i_ll
        if j_ll % 240 != 0:
            j_ll_cache = j_ll + 240 - j_ll%240
        else:
            j_ll_cache = j_ll
        i_ur_cache = i_ur - i_ur%240
        j_ur_cache = j_ur - j_ur%240
        if i_ll_cache >= i_ur_cache or j_ll_cache >= j_ur_cache:
            return self.get_max_height_from_h5file(i_ll, j_ll, i_ur, j_ur)
        else:
            h5_results.append(self.get_max_height_from_h5file(i_ll, j_ll,
                i_ll_cache, j_ur))
            h5_results.append(self.get_max_height_from_h5file(i_ur_cache,
                j_ll, i_ur, j_ur))
            h5_results.append(self.get_max_height_from_h5file(i_ll_cache,
                j_ll, i_ur_cache, j_ll_cache))
            h5_results.append(self.get_max_height_from_h5file(i_ll_cache,
                j_ur_cache, i_ur_cache, j_ur))
            cache_locations = self.get_max_locations_from_cache(
                i_ll_cache//240, j_ll_cache//240, i_ur_cache//240,
                j_ur_cache//240)
            for _cache_location in cache_locations:
                _i_ll = _cache_location[0] * 240
                _j_ll = _cache_location[1] * 240
                h5_results.append(self.get_max_height_from_h5file(_i_ll,
                    _j_ll, _i_ll+240, _j_ll+240))
            for _result in h5_results:
                if not _result['location_max']:
                    pass
                elif _result['h_max'] > h_max:
                    location_max = _result['location_max']
                    h_max = _result['h_max']
                    counter_max = _result['counter_max']
                elif _result['h_max'] == h_max:
                    location_max += _result['location_max']
                    counter_max += _result['counter_max']
        return {'location_max': location_max, 'h_max': h_max,
            'counter_max': counter_max}

    @timeit
    def get_min_height_from_indices(self, i_ll, j_ll, i_ur, j_ur):
        i_ur = i_ur + 1
        j_ur = j_ur + 1
        h_min = -self.NODATA
        location_min = []
        counter_min = 0
        h5_results = []
        if i_ll % 240 != 0:
            i_ll_cache = i_ll + 240 - i_ll%240
        else:
            i_ll_cache = i_ll
        if j_ll % 240 != 0:
            j_ll_cache = j_ll + 240 - j_ll%240
        else:
            j_ll_cache = j_ll
        i_ur_cache = i_ur - i_ur%240
        j_ur_cache = j_ur - j_ur%240
        if i_ll_cache >= i_ur_cache or j_ll_cache >= j_ur_cache:
            return self.get_min_height_from_h5file(i_ll, j_ll, i_ur, j_ur)
        else:
            h5_results.append(self.get_min_height_from_h5file(i_ll, j_ll,
                i_ll_cache, j_ur))
            h5_results.append(self.get_min_height_from_h5file(i_ur_cache,
                j_ll, i_ur, j_ur))
            h5_results.append(self.get_min_height_from_h5file(i_ll_cache,
                j_ll, i_ur_cache, j_ll_cache))
            h5_results.append(self.get_min_height_from_h5file(i_ll_cache,
                j_ur_cache, i_ur_cache, j_ur))
            cache_locations = self.get_min_locations_from_cache(
                i_ll_cache//240, j_ll_cache//240, i_ur_cache//240,
                j_ur_cache//240)
            for _cache_location in cache_locations:
                _i_ll = _cache_location[0] * 240
                _j_ll = _cache_location[1] * 240
                h5_results.append(self.get_min_height_from_h5file(_i_ll, _j_ll,
                    _i_ll+240, _j_ll+240))
            for _result in h5_results:
                if not _result['location_min']:
                    pass
                elif _result['h_min'] < h_min:
                    location_min = _result['location_min']
                    h_min = _result['h_min']
                    counter_min = _result['counter_min']
                elif _result['h_min'] == h_min:
                    location_min += _result['location_min']
                    counter_min += _result['counter_min']
        return {'location_min': location_min, 'h_min': h_min,
            'counter_min': counter_min}

    @timeit
    def get_min_max_height_from_indices(self, i_ll, j_ll, i_ur, j_ur):
        i_ur = i_ur + 1
        j_ur = j_ur + 1
        h_max = self.NODATA
        location_max = []
        counter_max = 0
        h_min = -self.NODATA
        location_min = []
        counter_min = 0
        h5_results = []
        if i_ll % 240 != 0:
            i_ll_cache = i_ll + 240 - i_ll%240
        else:
            i_ll_cache = i_ll
        if j_ll % 240 != 0:
            j_ll_cache = j_ll + 240 - j_ll%240
        else:
            j_ll_cache = j_ll
        i_ur_cache = i_ur - i_ur%240
        j_ur_cache = j_ur - j_ur%240
        if i_ll_cache >= i_ur_cache or j_ll_cache >= j_ur_cache:
            return self.get_min_max_height_from_h5file(i_ll, j_ll, i_ur, j_ur)
        else:
            h5_results.append(self.get_min_max_height_from_h5file(i_ll, j_ll,
                i_ll_cache, j_ur))
            h5_results.append(self.get_min_max_height_from_h5file(i_ur_cache,
                j_ll, i_ur, j_ur))
            h5_results.append(self.get_min_max_height_from_h5file(i_ll_cache,
                j_ll, i_ur_cache, j_ll_cache))
            h5_results.append(self.get_min_max_height_from_h5file(i_ll_cache,
                j_ur_cache, i_ur_cache, j_ur))
            cache_locations = self.get_min_max_locations_from_cache(
                i_ll_cache//240, j_ll_cache//240, i_ur_cache//240,
                j_ur_cache//240)
            for _cache_location in cache_locations:
                _i_ll = _cache_location[0] * 240
                _j_ll = _cache_location[1] * 240
                h5_results.append(self.get_min_max_height_from_h5file(_i_ll,
                    _j_ll, _i_ll+240, _j_ll+240))
            for _result in h5_results:
                if not _result['location_max']:
                    pass
                elif _result['h_max'] > h_max:
                    location_max = _result['location_max']
                    h_max = _result['h_max']
                    counter_max = _result['counter_max']
                elif _result['h_max'] == h_max:
                    location_max += _result['location_max']
                    counter_max += _result['counter_max']
                if not _result['location_min']:
                    pass
                elif _result['h_min'] < h_min:
                    location_min = _result['location_min']
                    h_min = _result['h_min']
                    counter_min = _result['counter_min']
                elif _result['h_min'] == h_min:
                    location_min += _result['location_min']
                    counter_min += _result['counter_min']
        return {
            'location_max': location_max, 'h_max': h_max,
            'counter_max': counter_max, 'location_min': location_min,
            'h_min': h_min, 'counter_min': counter_min}
