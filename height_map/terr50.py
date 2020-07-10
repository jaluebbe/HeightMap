import os
import struct
import json
from pygeodesy import ellipsoidalVincenty as eV
from pygeodesy import toOsgr, parseOSGR, Osgr
from height_map.dgm200 import calculate_distance
from height_map.timeit import timeit

CELLSIZE = 50
NCOLS = 200
NROWS = 200


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
    return latlon.lat, latlon.lon


def get_osgr_from_indices(x, y, filename):
    easting = (x + int(filename[-6])*NCOLS) * CELLSIZE
    northing = ((NROWS - 1 - y) + int(filename[-5])*NROWS) * CELLSIZE
    letters = filename[-8:-6]
    osgr = parseOSGR('{}{:05d}{:05d}'.format(letters, easting, northing))
    return osgr


class Terrain50:
    attribution_url = (
        'https://www.ordnancesurvey.co.uk/business-and-government/products/'
        'terrain-50.html')
    attribution_name = 'OS Terrain 50'
    attribution = ('<a href="{}">Contains OS data &copy; Crown copyright and '
                   'database right 2019</a>').format(attribution_url)
    NODATA = -32768
    precision = 4.0  # RMS error
    seabed_included = False

    def __init__(self, path=None, cache_path=None, cache_file_name=None):
        pwd = os.path.dirname(os.path.abspath(__file__))
        if path is None:
            self.path = os.path.join(pwd, 'maps/os_terr50_gb')
        if cache_path is None:
            self.cache_path = pwd
        if cache_file_name is None:
            cache_file_name = os.path.join(self.cache_path, 'terr50_map_cache.json')
        if os.path.isfile(cache_file_name):
            with open(cache_file_name) as json_cache_file:
                try:
                    self.map_cache = json.load(json_cache_file)
                except json.decoder.JSONDecodeError:
                    self.map_cache = {}
        else:
            self.map_cache = {}

    def get_height(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        result = {
            'altitude_m': self.NODATA, 'source': self.attribution_name, 'lat': lat,
            'lon': lon, 'distance_m': 0, 'attributions': [self.attribution]}
        if lat < 49.7 or lat > 62 or lon < -10 or lon > 4:
            return result
        try:
            osgr = toOsgr(eV.LatLon(lat, lon))
            if len(osgr.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        # fit request to the grid
        osgr = osgr_to_grid(osgr)
        latlon = osgr.toLatLon(eV.LatLon)
        lat_found = latlon.lat
        lon_found = latlon.lon
        filename = get_filename(osgr)
        full_path = os.path.join(self.path, filename[:2].lower(), filename)
        if not os.path.isfile(full_path):
            return result
        x = get_x(osgr)
        y = get_y(osgr)
        with open(full_path, "rb") as f:
            # go to the right spot,
            f.seek((y * NCOLS + x) * 4)
            # read four bytes and convert them:
            buf = f.read(4)
            # ">f" is a four byte float
            val = struct.unpack('>f', buf)[0]
            result.update({
                'lat_found': round(lat_found, 6),
                'lon_found': round(lon_found, 6), 'altitude_m': round(val, 2),
                'distance_m': round(calculate_distance(lat, lon, lat_found,
                lon_found), 3)})
            return result

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
        try:
            osgr_ll = toOsgr(eV.LatLon(lat_ll, lon_ll))
            if len(osgr_ll.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        try:
            osgr_ur = toOsgr(eV.LatLon(lat_ur, lon_ur))
            if len(osgr_ur.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        file_list = {}
        self.create_filelist(osgr_ll, osgr_ur, file_list)
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
        try:
            osgr_ll = toOsgr(eV.LatLon(lat_ll, lon_ll))
            if len(osgr_ll.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        try:
            osgr_ur = toOsgr(eV.LatLon(lat_ur, lon_ur))
            if len(osgr_ur.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        file_list = {}
        self.create_filelist(osgr_ll, osgr_ur, file_list)
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
        try:
            osgr_ll = toOsgr(eV.LatLon(lat_ll, lon_ll))
            if len(osgr_ll.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        try:
            osgr_ur = toOsgr(eV.LatLon(lat_ur, lon_ur))
            if len(osgr_ur.toStr()) == 0:
                raise ValueError('not a valid OSGR coordinate')
        except ValueError:
            return result
        file_list = {}
        self.create_filelist(osgr_ll, osgr_ur, file_list)
        result.update(self.check_min_max_files(self.filter_min_max_list(
            file_list)))
        return result

    @timeit
    def filter_max_list(self, file_list):
        h_max = self.NODATA
        filtered_files = {}
        for filename, list_item in file_list.items():
            if list_item['complete']:
                cache_data = self.map_cache.get(filename)
                h_max = max(h_max, cache_data['h_max'])
        for filename, list_item in file_list.items():
            cache_data = self.map_cache.get(filename)
            if cache_data['h_max'] < h_max:
                continue
            filtered_files[filename] = list_item
        return filtered_files

    @timeit
    def filter_min_list(self, file_list):
        h_min = -self.NODATA
        filtered_files = {}
        for filename, list_item in file_list.items():
            if list_item['complete']:
                cache_data = self.map_cache.get(filename)
                if self.NODATA < cache_data['h_min'] < h_min:
                    h_min = cache_data['h_min']
        for filename, list_item in file_list.items():
            cache_data = self.map_cache.get(filename)
            if cache_data['h_min'] > h_min > self.NODATA:
                continue
            filtered_files[filename] = list_item
        return filtered_files

    @timeit
    def filter_min_max_list(self, file_list):
        h_max = self.NODATA
        h_min = -self.NODATA
        filtered_files = {}
        for filename, list_item in file_list.items():
            if list_item['complete']:
                cache_data = self.map_cache.get(filename)
                h_max = max(h_max, cache_data['h_max'])
                if self.NODATA < cache_data['h_min'] < h_min:
                    h_min = cache_data['h_min']
        for filename, list_item in file_list.items():
            cache_data = self.map_cache.get(filename)
            if cache_data['h_max'] >= h_max:
                filtered_files[filename] = list_item
            elif self.NODATA < cache_data['h_min'] <= h_min:
                filtered_files[filename] = list_item
        return filtered_files

    @timeit
    def check_max_files(self, file_list):
        h_max = self.NODATA
        osgr_list = []
        counter_max = 0
        for filename, list_item in file_list.items():
            x_ll = list_item['x_ll']
            y_ll = list_item['y_ll']
            x_ur = list_item['x_ur']
            y_ur = list_item['y_ur']
            x_pos = x_ll
            y_pos = y_ur
            full_path = os.path.join(self.path, filename[:2].lower(), filename)
            with open(full_path, "rb") as f:
                while y_ur <= y_pos <= y_ll:
                    f.seek((y_pos * NCOLS + x_pos) * 4)
                    num_values = x_ur - x_ll + 1
                    buf = f.read(num_values * 4)
                    values = struct.unpack('>{:d}f'.format(num_values), buf)
                    while x_ll <= x_pos <= x_ur:
                        # if current height value larger than previous maximum
                        if values[x_pos - x_ll] > h_max:
                            # store current height
                            h_max = values[x_pos - x_ll]
                            osgr_list = [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_max = 1
                        elif values[x_pos - x_ll] == h_max:
                            osgr_list += [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_max += 1
                        x_pos += 1
                    x_pos = x_ll
                    y_pos += 1
        _latlons_max = [_osgr.toLatLon(eV.LatLon) for _osgr in osgr_list]
        location_max = [(latlon.lat, latlon.lon) for latlon in _latlons_max]
        return {'location_max': location_max, 'h_max': h_max,
            'counter_max': counter_max}

    @timeit
    def check_min_files(self, file_list):
        h_min = -self.NODATA
        osgr_list = []
        counter_min = 0
        for filename, list_item in file_list.items():
            x_ll = list_item['x_ll']
            y_ll = list_item['y_ll']
            x_ur = list_item['x_ur']
            y_ur = list_item['y_ur']
            x_pos = x_ll
            y_pos = y_ur
            full_path = os.path.join(self.path, filename[:2].lower(), filename)
            with open(full_path, "rb") as f:
                while y_ur <= y_pos <= y_ll:
                    f.seek((y_pos * NCOLS + x_pos) * 4)
                    num_values = x_ur - x_ll + 1
                    buf = f.read(num_values * 4)
                    values = struct.unpack('>{:d}f'.format(num_values), buf)
                    while x_ll <= x_pos <= x_ur:
                        if self.NODATA < values[x_pos - x_ll] < h_min:
                            h_min = values[x_pos - x_ll]
                            osgr_list = [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_min = 1
                        elif self.NODATA < values[x_pos - x_ll] == h_min:
                            osgr_list += [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_min += 1
                        x_pos += 1
                    x_pos = x_ll
                    y_pos += 1
        if h_min == -self.NODATA:
            h_min = self.NODATA
        _latlons_min = [_osgr.toLatLon(eV.LatLon) for _osgr in osgr_list]
        location_min = [(latlon.lat, latlon.lon) for latlon in _latlons_min]
        return {'location_min': location_min, 'h_min': h_min,
            'counter_min': counter_min}

    @timeit
    def check_min_max_files(self, file_list):
        h_max = self.NODATA
        osgr_list_max = []
        counter_max = 0
        h_min = -self.NODATA
        osgr_list_min = []
        counter_min = 0
        for filename, list_item in file_list.items():
            x_ll = list_item['x_ll']
            y_ll = list_item['y_ll']
            x_ur = list_item['x_ur']
            y_ur = list_item['y_ur']
            x_pos = x_ll
            y_pos = y_ur
            full_path = os.path.join(self.path, filename[:2].lower(), filename)
            with open(full_path, "rb") as f:
                while y_ur <= y_pos <= y_ll:
                    f.seek((y_pos * NCOLS + x_pos) * 4)
                    num_values = x_ur - x_ll + 1
                    buf = f.read(num_values * 4)
                    values = struct.unpack('>{:d}f'.format(num_values), buf)
                    while x_ll <= x_pos <= x_ur:
                        if values[x_pos - x_ll] > h_max:
                            # store current height
                            h_max = values[x_pos - x_ll]
                            osgr_list_max = [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_max = 1
                        elif values[x_pos - x_ll] == h_max:
                            osgr_list_max += [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_max += 1
                        if self.NODATA < values[x_pos - x_ll] < h_min:
                            h_min = values[x_pos - x_ll]
                            osgr_list_min = [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_min = 1
                        elif self.NODATA < values[x_pos - x_ll] == h_min:
                            osgr_list_min += [get_osgr_from_indices(x_pos, y_pos,
                                filename)]
                            counter_min += 1
                        x_pos += 1
                    x_pos = x_ll
                    y_pos += 1
        if h_min == -self.NODATA:
            h_min = self.NODATA
        _latlons_max = [_osgr.toLatLon(eV.LatLon) for _osgr in osgr_list_max]
        location_max = [(latlon.lat, latlon.lon) for latlon in _latlons_max]
        _latlons_min = [_osgr.toLatLon(eV.LatLon) for _osgr in osgr_list_min]
        location_min = [(latlon.lat, latlon.lon) for latlon in _latlons_min]
        return {
            'location_min': location_min, 'h_min': h_min,
            'counter_min': counter_min, 'location_max': location_max,
            'h_max': h_max, 'counter_max': counter_max}

    def create_filelist(self, osgr_ll, osgr_ur, file_list):
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
            self.create_filelist(
                Osgr(osgr_ll.easting, northing_ll_tile + NROWS*CELLSIZE),
                Osgr(min(osgr_ur.easting, easting_ll_tile + (NCOLS - 1)*CELLSIZE),
                osgr_ur.northing), file_list)
            y_ur = 0
        if osgr_ur.easting - easting_ll_tile < NCOLS * CELLSIZE:
            x_ur = get_x(osgr_ur)
        else:
            # right neighbour
            self.create_filelist(Osgr(easting_ll_tile + NCOLS*CELLSIZE,
                                 osgr_ll.northing), osgr_ur, file_list)
            x_ur = NCOLS - 1
        filename = get_filename(osgr_ll)
        full_path = os.path.join(self.path, filename[:2].lower(), filename)
        if os.path.isfile(full_path):
            complete = (y_ur == 0 and x_ll == 0 and x_ur == NCOLS - 1
                        and y_ll == NROWS - 1)
            file_list[filename] = {'x_ll': x_ll, 'y_ll': y_ll, 'x_ur': x_ur,
                'y_ur': y_ur, 'complete': complete}
