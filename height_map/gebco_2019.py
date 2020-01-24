import h5py
import os
import json
import numpy as np
from height_map.dgm200 import calculate_distance

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


class Gebco2019:

    attribution_url = ('https://www.gebco.net/data_and_products/'
        'gridded_bathymetry_data/gebco_2019/gebco_2019_info.html')
    attribution_name = 'The GEBCO Grid'
    attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
        attribution_name)
    pwd = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(pwd, 'maps/gebco_2019')
    filename = 'GEBCO_2019.nc'
    file = os.path.join(path, filename)
    cache_path = pwd
    cache_filename = 'gebco_2019_cache.json'
    old_data = {}

    def get_height(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= 90 <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        file = os.path.join(self.path, self.filename)
        val = NODATA
        i = get_index_from_latitude(lat)
        j = get_index_from_longitude(lon)
        lat_found = get_lat_from_index(i)
        lon_found = get_lon_from_index(j)
        if self.old_data.get('i') == i and self.old_data.get('j') == j:
            # same grid position, file access not necessary
            val = self.old_data['val']
        elif os.path.isfile(file):
            with h5py.File(file, 'r') as f:
                val = round(float(f['elevation'][i][j]), 2)
            self.old_data.update({'i': i, 'j': j, 'val': val})
        return {
            'lat': lat, 'lon': lon, 'lat_found': round(lat_found, 6),
            'lon_found': round(lon_found, 6), 'altitude_m': val,
            'source': self.attribution_name, 'distance_m': round(
            calculate_distance(lat, lon, lat_found, lon_found), 3),
            'attribution': self.attribution}

    def get_max_height_from_indices(self, i_ll, j_ll, i_ur, j_ur):
        i_ur = i_ur + 1
        j_ur = j_ur + 1
        h_max = NODATA
        location_max = []
        counter = 0
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
            h5_results.append(self.get_max_height_from_h5file(i_ur_cache, j_ll,
                i_ur, j_ur))
            h5_results.append(self.get_max_height_from_h5file(i_ll_cache, j_ll,
                i_ur_cache, j_ll_cache))
            h5_results.append(self.get_max_height_from_h5file(i_ll_cache,
                j_ur_cache, i_ur_cache, j_ur))
            cache_result = self.get_max_height_from_cache(i_ll_cache//240,
                j_ll_cache//240, i_ur_cache//240, j_ur_cache//240)
            cache_location_max, cache_h_max, cache_counter = cache_result
            for _cache_location in cache_location_max:
                _i_ll = _cache_location[0] * 240
                _j_ll = _cache_location[1] * 240
                h5_results.append(self.get_max_height_from_h5file(_i_ll, _j_ll,
                    _i_ll+240, _j_ll+240))
            for _result in h5_results:
                _location_max, _h_max, _counter = _result
                if not _location_max:
                    continue
                if _h_max > h_max:
                    location_max = _location_max
                    h_max = _h_max
                    counter = _counter
                elif _h_max == h_max:
                    location_max += _location_max
                    counter += _counter
        return location_max, round(float(h_max), 1), counter

    def get_max_height_from_cache(self, i_ll, j_ll, i_ur, j_ur):
        h_max = NODATA
        location_max = []
        counter = 0
        cache_file = os.path.join(self.cache_path, self.cache_filename)
        if os.path.isfile(cache_file) and i_ll < i_ur and j_ll < j_ur:
            with open(cache_file, 'r') as f:
                max_cache = np.array(json.load(f)['maximum'])
                selection = max_cache[i_ll:i_ur, j_ll:j_ur]
                h_max = selection.max()
                x, y = np.where(selection == h_max)
                counter = len(x)
                for _index in range(counter):
                    location_max += [(i_ll+x[_index], j_ll+y[_index])]
        elif not os.path.isfile(cache_file):
            print('GEBCO_2019 min/max cache file is missing.')
        return location_max, round(float(h_max), 1), counter

    def get_max_height_from_h5file(self, i_ll, j_ll, i_ur, j_ur):
        h_max = NODATA
        location_max = []
        counter = 0
        file = os.path.join(self.path, self.filename)
        if os.path.isfile(file) and i_ll < i_ur and j_ll < j_ur:
            with h5py.File(file, 'r') as f:
                selection = f['elevation'][i_ll:i_ur, j_ll:j_ur]
                h_max = selection.max()
                x, y = np.where(selection == h_max)
                counter = len(x)
                for _index in range(counter):
                    location_max += [(i_ll+x[_index], j_ll+y[_index])]
        return location_max, round(float(h_max), 1), counter

    def get_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if lon_ur >= 180 - CELLSIZE/2:
            lon_ur -= CELLSIZE
        # consider only correctly defined rectangle:
        if (lat_ll > lat_ur) or (lon_ll > lon_ur):
            return [], NODATA, 0
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll)
        j_ll = get_index_from_longitude(lon_ll)
        i_ur = get_index_from_latitude(lat_ur)
        j_ur = get_index_from_longitude(lon_ur)
        location_max, h_max, counter = self.get_max_height_from_indices(
            i_ll, j_ll, i_ur, j_ur)
        location_max = [[get_lat_from_index(_x), get_lon_from_index(_y)]
            for (_x, _y) in location_max]
        return location_max, round(float(h_max), 1), counter

    def get_min_height_from_indices(self, i_ll, j_ll, i_ur, j_ur):
        i_ur = i_ur + 1
        j_ur = j_ur + 1
        h_min = -NODATA
        location_min = []
        counter = 0
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
            cache_result = self.get_min_height_from_cache(i_ll_cache//240,
                j_ll_cache//240, i_ur_cache//240, j_ur_cache//240)
            cache_location_min, cache_h_min, cache_counter = cache_result
            for _cache_location in cache_location_min:
                _i_ll = _cache_location[0] * 240
                _j_ll = _cache_location[1] * 240
                h5_results.append(self.get_min_height_from_h5file(_i_ll, _j_ll,
                    _i_ll+240, _j_ll+240))
            for _result in h5_results:
                _location_min, _h_min, _counter = _result
                if not _location_min:
                    continue
                if _h_min < h_min:
                    location_min = _location_min
                    h_min = _h_min
                    counter = _counter
                elif _h_min == h_min:
                    location_min += _location_min
                    counter += _counter
        return location_min, round(float(h_min), 1), counter

    def get_min_height_from_cache(self, i_ll, j_ll, i_ur, j_ur):
        h_min = -NODATA
        location_min = []
        counter = 0
        cache_file = os.path.join(self.cache_path, self.cache_filename)
        if os.path.isfile(cache_file) and i_ll < i_ur and j_ll < j_ur:
            with open(cache_file, 'r') as f:
                min_cache = np.array(json.load(f)['minimum'])
                selection = min_cache[i_ll:i_ur, j_ll:j_ur]
                h_min = selection.min()
                x, y = np.where(selection == h_min)
                counter = len(x)
                for _index in range(counter):
                    location_min += [(i_ll+x[_index], j_ll+y[_index])]
        elif not os.path.isfile(cache_file):
            print('GEBCO_2019 min/max cache file is missing.')
        return location_min, round(float(h_min), 1), counter

    def get_min_height_from_h5file(self, i_ll, j_ll, i_ur, j_ur):
        h_min = -NODATA
        location_min = []
        counter = 0
        file = os.path.join(self.path, self.filename)
        if os.path.isfile(file) and i_ll < i_ur and j_ll < j_ur:
            with h5py.File(file, 'r') as f:
                selection = f['elevation'][i_ll:i_ur, j_ll:j_ur]
                h_min = selection.min()
                x, y = np.where(selection == h_min)
                counter = len(x)
                for _index in range(counter):
                    location_min += [(i_ll+x[_index], j_ll+y[_index])]
        return location_min, round(float(h_min), 1), counter

    def get_min_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if lon_ur >= 180 - CELLSIZE/2:
            lon_ur -= CELLSIZE
        # consider only correctly defined rectangle:
        if (lat_ll > lat_ur) or (lon_ll > lon_ur):
            return [], NODATA, 0
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll)
        j_ll = get_index_from_longitude(lon_ll)
        i_ur = get_index_from_latitude(lat_ur)
        j_ur = get_index_from_longitude(lon_ur)
        location_min, h_min, counter = self.get_min_height_from_indices(
            i_ll, j_ll, i_ur, j_ur)
        location_min = [[get_lat_from_index(_x),
                         get_lon_from_index(_y)] for (_x, _y) in location_min]
        if h_min == -NODATA:
            h_min = NODATA
        return location_min, round(float(h_min), 1), counter


gebco = Gebco2019()


def get_height(lat, lon):
    return gebco.get_height(lat, lon)


def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    return gebco.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)


def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    return gebco.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)
