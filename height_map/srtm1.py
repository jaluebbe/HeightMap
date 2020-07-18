import struct
from math import floor
import json
import os
from height_map.dgm200 import calculate_distance
from height_map.timeit import timeit

NCOLS = 3601
NROWS = 3601
CELLSIZE = 1./3600


def get_index_from_latitude(lat, yllcenter):
    return NROWS - int(round((lat - yllcenter) / CELLSIZE)) - 1


def get_index_from_longitude(lon, xllcenter):
    return int(round((lon - xllcenter) / CELLSIZE)) 


def get_lat_from_index(i, yllcenter):
    return (NROWS - i - 1)*CELLSIZE + yllcenter


def get_lon_from_index(j, xllcenter):
    return j*CELLSIZE + xllcenter


def get_filename(yllcenter, xllcenter):
    if yllcenter >= 0:
        if xllcenter >= 0:
            return "N{:02.0f}E{:03.0f}.hgt".format(yllcenter, xllcenter)
        elif xllcenter < 0:
            return "N{:02.0f}W{:03.0f}.hgt".format(yllcenter, -xllcenter)
    elif yllcenter < 0:
        if xllcenter >= 0:
            return "S{:02.0f}E{:03.0f}.hgt".format(-yllcenter, xllcenter)
        elif xllcenter < 0:
            return "S{:02.0f}W{:03.0f}.hgt".format(-yllcenter, -xllcenter)


class Srtm1:
    attribution_url = 'https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003'
    attribution_name = 'SRTMGL1'
    attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
        attribution_name)

    precision = 16.0  # 16m SRTM vertical error
    seabed_included = False
    NODATA = -32768
    old_file = None
    old_file_name = None

    def __init__(self, path=None, cache_path=None, cache_file_name=None):
        pwd = os.path.dirname(os.path.abspath(__file__))
        if path is None:
            self.path = os.path.join(pwd, 'maps/srtm1')
        if cache_path is None:
            self.cache_path = pwd
        if cache_file_name is None:
            cache_file_name = os.path.join(self.cache_path, 'srtm1_map_cache.json')
        if os.path.isfile(cache_file_name):
            with open(cache_file_name) as json_cache_file:
                try:
                    self.map_cache = json.load(json_cache_file)
                except json.decoder.JSONDecodeError:
                    self.map_cache = {}
        else:
            self.map_cache = {}

    def create_filelist(self, lat_ll, lon_ll, lat_ur, lon_ur, file_list):
        # obtain the coordinates of the tile containing the lower left
        x_ll_tile = floor(lon_ll)
        y_ll_tile = floor(lat_ll)
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll, y_ll_tile)
        j_ll = get_index_from_longitude(lon_ll, x_ll_tile)
        if lat_ur < y_ll_tile + 1 + CELLSIZE / 2:
            i_ur = get_index_from_latitude(lat_ur, y_ll_tile)
        else:
            # upper neighbour
            self.create_filelist(
                y_ll_tile + 1 + CELLSIZE / 2, lon_ll, lat_ur,
                min(lon_ur, x_ll_tile + 1), file_list)
            i_ur = 0
        if lon_ur < x_ll_tile + 1 + CELLSIZE / 2:
            j_ur = get_index_from_longitude(lon_ur, x_ll_tile)
        else:
            # right neighbour
            self.create_filelist(
                lat_ll, x_ll_tile + 1 + CELLSIZE / 2, lat_ur, lon_ur, file_list)
            j_ur = NCOLS - 1
        file_name = get_filename(y_ll_tile, x_ll_tile)
        full_path = os.path.join(self.path, file_name)
        if os.path.isfile(full_path):
            complete = (i_ur == 0 and j_ll == 0 and j_ur == NCOLS - 1
                        and i_ll == NROWS - 1)
            file_list[file_name] = {
                'j_ll': j_ll, 'i_ll': i_ll, 'j_ur': j_ur, 'i_ur': i_ur,
                'x_ll_tile': x_ll_tile, 'y_ll_tile': y_ll_tile,
                'complete': complete}
        else:
            raise IOError(f'requested {file_name} is out of SRTM1 coverage or '
                          'file is missing.')

    @timeit
    def filter_max_list(self, file_list):
        h_max = self.NODATA
        filtered_files = {}
        for file_name, list_item in file_list.items():
            if list_item['complete']:
                cache_data = self.map_cache.get(file_name)
                h_max = max(h_max, cache_data['h_max'])
        for file_name, list_item in file_list.items():
            cache_data = self.map_cache.get(file_name)
            if cache_data['h_max'] < h_max:
                continue
            filtered_files[file_name] = list_item
        return filtered_files

    @timeit
    def filter_min_list(self, file_list):
        h_min = -self.NODATA
        filtered_files = {}
        for file_name, list_item in file_list.items():
            if list_item['complete']:
                cache_data = self.map_cache.get(file_name)
                if self.NODATA < cache_data['h_min'] < h_min:
                    h_min = cache_data['h_min']
        for file_name, list_item in file_list.items():
            cache_data = self.map_cache.get(file_name)
            if cache_data['h_min'] > h_min > self.NODATA:
                continue
            filtered_files[file_name] = list_item
        return filtered_files

    @timeit
    def filter_min_max_list(self, file_list):
        h_max = self.NODATA
        h_min = -self.NODATA
        filtered_files = {}
        for file_name, list_item in file_list.items():
            if list_item['complete']:
                cache_data = self.map_cache.get(file_name)
                h_max = max(h_max, cache_data['h_max'])
                if self.NODATA < cache_data['h_min'] < h_min:
                    h_min = cache_data['h_min']
        for file_name, list_item in file_list.items():
            cache_data = self.map_cache.get(file_name)
            if cache_data['h_max'] >= h_max:
                filtered_files[file_name] = list_item
            elif self.NODATA < cache_data['h_min'] <= h_min:
                filtered_files[file_name] = list_item
        return filtered_files

    @timeit
    def check_max_files(self, file_list):
        h_max = self.NODATA
        location_max = []
        counter_max = 0
        for file_name, list_item in file_list.items():
            j_ll = list_item['j_ll']
            i_ll = list_item['i_ll']
            j_ur = list_item['j_ur']
            i_ur = list_item['i_ur']
            x_ll_tile = list_item['x_ll_tile']
            y_ll_tile = list_item['y_ll_tile']
            # start in the upper left edge of the target area
            i_pos = i_ur
            j_pos = j_ll
            full_path = os.path.join(self.path, file_name)
            with open(full_path, "rb") as f:
                while i_ur <= i_pos <= i_ll:
                    f.seek((i_pos * NCOLS + j_pos) * 2)
                    num_values = j_ur - j_ll + 1
                    buf = f.read(num_values * 2)
                    values = struct.unpack('>{:d}h'.format(num_values), buf)
                    while j_ll <= j_pos <= j_ur:
                        # if current height value larger than previous maximum
                        if values[j_pos - j_ll] > h_max:
                            # store current height
                            h_max = values[j_pos - j_ll]
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_max = [(lat, lon)]
                            counter_max = 1
                        elif values[j_pos - j_ll] == h_max:
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_max += [(lat, lon)]
                            counter_max += 1
                        j_pos += 1
                    j_pos = j_ll
                    i_pos += 1
        return {'location_max': location_max, 'h_max': h_max,
            'counter_max': counter_max}

    @timeit
    def check_min_files(self, file_list):
        h_min = -self.NODATA
        location_min = []
        counter_min = 0
        for file_name, list_item in file_list.items():
            j_ll = list_item['j_ll']
            i_ll = list_item['i_ll']
            j_ur = list_item['j_ur']
            i_ur = list_item['i_ur']
            x_ll_tile = list_item['x_ll_tile']
            y_ll_tile = list_item['y_ll_tile']
            # start in the upper left edge of the target area
            i_pos = i_ur
            j_pos = j_ll
            full_path = os.path.join(self.path, file_name)
            with open(full_path, "rb") as f:
                while i_ur <= i_pos <= i_ll:
                    f.seek((i_pos * NCOLS + j_pos) * 2)
                    num_values = j_ur - j_ll + 1
                    buf = f.read(num_values * 2)
                    values = struct.unpack('>{:d}h'.format(num_values), buf)
                    while j_ll <= j_pos <= j_ur:
                        if self.NODATA < values[j_pos - j_ll] < h_min:
                            h_min = values[j_pos - j_ll]
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_min = [(lat, lon)]
                            counter_min = 1
                        elif self.NODATA < values[j_pos - j_ll] == h_min:
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_min += [(lat, lon)]
                            counter_min += 1
                        j_pos += 1
                    j_pos = j_ll
                    i_pos += 1
        if h_min == -self.NODATA:
            h_min = self.NODATA
        return {'location_min': location_min, 'h_min': h_min,
            'counter_min': counter_min}

    @timeit
    def check_min_max_files(self, file_list):
        h_max = self.NODATA
        location_max = []
        counter_max = 0
        h_min = -self.NODATA
        location_min = []
        counter_min = 0
        for file_name, list_item in file_list.items():
            j_ll = list_item['j_ll']
            i_ll = list_item['i_ll']
            j_ur = list_item['j_ur']
            i_ur = list_item['i_ur']
            x_ll_tile = list_item['x_ll_tile']
            y_ll_tile = list_item['y_ll_tile']
            # start in the upper left edge of the target area
            i_pos = i_ur
            j_pos = j_ll
            full_path = os.path.join(self.path, file_name)
            with open(full_path, "rb") as f:
                while i_ur <= i_pos <= i_ll:
                    f.seek((i_pos * NCOLS + j_pos) * 2)
                    num_values = j_ur - j_ll + 1
                    buf = f.read(num_values * 2)
                    values = struct.unpack('>{:d}h'.format(num_values), buf)
                    while j_ll <= j_pos <= j_ur:
                        if values[j_pos - j_ll] > h_max:
                            # store current height
                            h_max = values[j_pos - j_ll]
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_max = [(lat, lon)]
                            counter_max = 1
                        elif values[j_pos - j_ll] == h_max:
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_max += [(lat, lon)]
                            counter_max += 1
                        if self.NODATA < values[j_pos - j_ll] < h_min:
                            h_min = values[j_pos - j_ll]
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_min = [(lat, lon)]
                            counter_min = 1
                        elif self.NODATA < values[j_pos - j_ll] == h_min:
                            lat = get_lat_from_index(i_pos, y_ll_tile)
                            lon = get_lon_from_index(j_pos, x_ll_tile)
                            location_min += [(lat, lon)]
                            counter_min += 1
                        j_pos += 1
                    j_pos = j_ll
                    i_pos += 1
        if h_min == -self.NODATA:
            h_min = self.NODATA
        return {
            'location_min': location_min, 'h_min': h_min,
            'counter_min': counter_min, 'location_max': location_max,
            'h_max': h_max, 'counter_max': counter_max}

    @timeit
    def get_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        result = {'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        file_list = {}
        try:
            self.create_filelist(lat_ll, lon_ll, lat_ur, lon_ur, file_list)
        except IOError:
            return result
        result.update(self.check_max_files(self.filter_max_list(file_list)))
        return result

    @timeit
    def get_min_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        result = {'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        file_list = {}
        try:
            self.create_filelist(lat_ll, lon_ll, lat_ur, lon_ur, file_list)
        except IOError:
            return result
        result.update(self.check_min_files(self.filter_min_list(file_list)))
        return result

    @timeit
    def get_min_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        result = {
            'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        file_list = {}
        try:
            self.create_filelist(lat_ll, lon_ll, lat_ur, lon_ur, file_list)
        except IOError:
            return result
        result.update(self.check_min_max_files(self.filter_min_max_list(
            file_list)))
        return result

    def get_height(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        x_ll_tile = floor(lon)
        y_ll_tile = floor(lat)
        file_name = get_filename(y_ll_tile, x_ll_tile)
        fullpath = os.path.join(self.path, file_name)
        val = self.NODATA
        lat_found = lat
        lon_found = lon
        if os.path.isfile(fullpath):
            # verified with
            # gdallocationinfo N52W002.hgt -wgs84 -1.215090 52.925315
            i = get_index_from_latitude(lat, y_ll_tile)
            j = get_index_from_longitude(lon, x_ll_tile)
            if self.old_file_name == file_name:
                f = self.old_file
            else:
                f = open(fullpath, "rb")
                self.old_file_name = file_name
                self.old_file = f
            # go to the right spot,
            f.seek((i*NCOLS + j) * 2)
            # read two bytes and convert them:
            buf = f.read(2)
            # ">h" is a signed two byte integer
            val = struct.unpack('>h', buf)[0]
            # turn indices back to coordinates
            lat_found = get_lat_from_index(i, y_ll_tile)
            lon_found = get_lon_from_index(j, x_ll_tile)
        return {
            'lat': lat, 'lon': lon, 'lat_found': round(lat_found, 6),
            'lon_found': round(lon_found, 6), 'altitude_m': val,
            'source': self.attribution_name, 'distance_m': round(
            calculate_distance(lat, lon, lat_found, lon_found), 3),
            'attributions': [self.attribution]}
