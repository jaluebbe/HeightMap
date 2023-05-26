import os
import pygeodesy
import struct
import logging
from height_map import calculate_distance

XLLCENTER = 280000
YLLCENTER = 5236000
CELLSIZE = 200
NCOLS = 3207
NROWS = 4331
LAT_MIN = 47.141612
LAT_MAX = 55.016964
LON_MIN = 5.557084
LON_MAX = 15.572619


def utm_to_ll(easting, northing):
    _utm = pygeodesy.Utm(32, 'N', easting, northing)
    _latlon = _utm.toLatLon()
    return _latlon.lat, _latlon.lon


def ll_to_utm(latitude, longitude):
    _utm = pygeodesy.toUtm(latitude, longitude)
    _utm_32 = _utm.toUtm(32)
    return _utm_32.easting, _utm_32.northing


# calculate the distance to the closest DGM200 reference point
def get_closest_distance(latitude, longitude):
    # obtain UTM32 coordinates for given latitude, longitude
    easting, northing = ll_to_utm(latitude, longitude)
    # clip UTM32 coordinates to range of DGM200 data
    easting = max(XLLCENTER, min(easting, XLLCENTER + CELLSIZE*NCOLS - 1))
    northing = max(YLLCENTER, min(northing, YLLCENTER + CELLSIZE*NROWS - 1))
    # determine indices of DGM200 grid for given location
    x = int(round(((easting - XLLCENTER) / CELLSIZE)))
    y = int(round(NROWS - 1 - ((northing - YLLCENTER) / CELLSIZE)))
    # get UTM32 coordinates for grid point location
    ref_east = x*CELLSIZE + XLLCENTER
    ref_north = (NROWS - 1 - y)*CELLSIZE + YLLCENTER
    # convert UTM32 reference position back to latitude, logitude
    ref_lat, ref_lon = utm_to_ll(ref_east, ref_north)
    # calculate distance between position and reference
    distance = calculate_distance(latitude, longitude, ref_lat, ref_lon)
    return {'distance': round(distance * 100) / 100, 'ref_lat': ref_lat,
        'ref_lon': ref_lon}


def get_indices_from_latlon(latitude, longitude):
    easting, northing = ll_to_utm(latitude, longitude)
    x = int(round(((easting - XLLCENTER) / CELLSIZE)))
    y = int(round(NROWS - 1 - ((northing - YLLCENTER) / CELLSIZE)))
    if x < 0 or x >= NCOLS or y < 0 or y >= NROWS:
        x = -1
        y = -1
    return x, y


def get_latlon_from_indices(x, y):
    easting = x*CELLSIZE + XLLCENTER
    northing = (NROWS - 1 - y)*CELLSIZE + YLLCENTER
    lat, lon = utm_to_ll(easting, northing)
    return lat, lon


class Dgm200:
    logger = logging.getLogger(__name__)
    attribution_url = 'http://www.bkg.bund.de'
    attribution_name = 'DGM200'
    attribution = '&copy GeoBasis-DE / <a href="{}">BKG</a> 2023'.format(
        attribution_url)
    precision = 10.0  # max height error of dgm200 dataset
    file = None
    seabed_included = False
    NODATA = -9999

    def __init__(self, path=None, file_name=None):
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'maps/dgm200')
        if file_name is None:
            file_name = 'dgm200_utm32s_f4.bin'
        file = os.path.join(path, file_name)
        if os.path.isfile(file):
            self.file = file
        else:
            raise FileNotFoundError(file)

    def get_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        # ensure requested rectangle is not out of bounds:
        if (lat_ll < LAT_MIN or lat_ll > LAT_MAX or lon_ll < LON_MIN or
                lon_ll > LON_MAX or lat_ur < LAT_MIN or lat_ur > LAT_MAX or
                lon_ur < LON_MIN or lon_ur > LON_MAX):
            return result
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        (x_ll, y_ll) = get_indices_from_latlon(lat_ll, lon_ll)
        if x_ll == -1 or y_ll == -1:
            return result
        (x_ur, y_ur) = get_indices_from_latlon(lat_ur, lon_ur)
        if x_ur == -1 or y_ur == -1:
            return result
        #
        h_max = self.NODATA
        counter = 0
        # start in the upper left edge of the target area
        x_pos = x_ll
        y_pos = y_ur
        locations = []
        with open(self.file, "rb") as f:
            while y_ur <= y_pos <= y_ll:
                #
                f.seek((y_pos*NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while x_ll <= x_pos <= x_ur:
                    val = values[x_pos - x_ll]
                    if val > h_max:
                        h_max = val
                        locations.clear()
                        locations.append(get_latlon_from_indices(x_pos, y_pos))
                        counter = 1
                    elif val == h_max:
                        locations.append(get_latlon_from_indices(x_pos, y_pos))
                        counter += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
        result.update({'location_max': locations, 'h_max': h_max,
            'counter_max': counter})
        return result

    def get_min_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        # ensure requested rectangle is not out of bounds:
        if (lat_ll < LAT_MIN or lat_ll > LAT_MAX or lon_ll < LON_MIN or
                lon_ll > LON_MAX or lat_ur < LAT_MIN or lat_ur > LAT_MAX or
                lon_ur < LON_MIN or lon_ur > LON_MAX):
            return result
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        x_ll, y_ll = get_indices_from_latlon(lat_ll, lon_ll)
        if x_ll == -1 or y_ll == -1:
            return result
        x_ur, y_ur = get_indices_from_latlon(lat_ur, lon_ur)
        if x_ur == -1 or y_ur == -1:
            return result
        #
        h_min = -self.NODATA
        counter = 0
        # start in the upper left edge of the target area
        x_pos = x_ll
        y_pos = y_ur
        locations = []
        with open(self.file, "rb") as f:
            while y_ur <= y_pos <= y_ll:
                #
                f.seek((y_pos*NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while x_ll <= x_pos <= x_ur:
                    val = values[x_pos - x_ll]
                    if val == self.NODATA:
                        pass
                    elif val < h_min:
                        h_min = val
                        locations.clear()
                        locations.append(get_latlon_from_indices(x_pos, y_pos))
                        counter = 1
                    elif val == h_min:
                        locations.append(get_latlon_from_indices(x_pos, y_pos))
                        counter += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
        if h_min == -self.NODATA:
            h_min = self.NODATA
        result.update({'location_min': locations, 'h_min': h_min,
            'counter_min': counter})
        return result

    def get_min_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {
            'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attributions': [self.attribution]}
        # ensure requested rectangle is not out of bounds:
        if (lat_ll < LAT_MIN or lat_ll > LAT_MAX or lon_ll < LON_MIN or
                lon_ll > LON_MAX or lat_ur < LAT_MIN or lat_ur > LAT_MAX or
                lon_ur < LON_MIN or lon_ur > LON_MAX):
            return result
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        x_ll, y_ll = get_indices_from_latlon(lat_ll, lon_ll)
        if x_ll == -1 or y_ll == -1:
            return result
        x_ur, y_ur = get_indices_from_latlon(lat_ur, lon_ur)
        if x_ur == -1 or y_ur == -1:
            return result
        #
        h_max = self.NODATA
        h_min = -self.NODATA
        counter_max = 0
        counter_min = 0
        # start in the upper left edge of the target area
        x_pos = x_ll
        y_pos = y_ur
        locations_max = []
        locations_min = []
        with open(self.file, "rb") as f:
            while y_ur <= y_pos <= y_ll:
                #
                f.seek((y_pos*NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while x_ll <= x_pos <= x_ur:
                    val = values[x_pos - x_ll]
                    if val == self.NODATA:
                        pass
                    elif val < h_min:
                        h_min = val
                        locations_min.clear()
                        locations_min.append(get_latlon_from_indices(x_pos,
                            y_pos))
                        counter_min = 1
                    elif val == h_min:
                        locations_min.append(get_latlon_from_indices(x_pos,
                            y_pos))
                        counter_min += 1
                    if val > h_max:
                        h_max = val
                        locations_max.clear()
                        locations_max.append(get_latlon_from_indices(x_pos,
                            y_pos))
                        counter_max = 1
                    elif val == h_max:
                        locations_max.append(get_latlon_from_indices(x_pos,
                            y_pos))
                        counter_max += 1
                    x_pos += 1
                x_pos = x_ll
                y_pos += 1
        if h_min == -self.NODATA:
            h_min = self.NODATA
        result.update({
            'location_max': locations_max, 'h_max': h_max,
            'counter_max': counter_max, 'location_min': locations_min,
            'h_min': h_min, 'counter_min': counter_min})
        return result

    def get_height(self, latitude, longitude):
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(latitude,
                longitude))
        result = {
            'altitude_m': self.NODATA, 'source': self.attribution_name,
            'lat': latitude, 'lon': longitude, 'distance_m': 0,
            'attributions': [self.attribution]}
        if (latitude < LAT_MIN or latitude > LAT_MAX or longitude < LON_MIN or
                longitude > LON_MAX):
            return result
        x, y = get_indices_from_latlon(latitude, longitude)
        if x == -1 or y == -1:
            return result
        with open(self.file, "rb") as f:
            f.seek((y*NCOLS + x) * 4)  # go to the right spot,
            buf = f.read(4)  # read four bytes and convert them:
            val = struct.unpack('>f', buf)[0]  # ">f" is a four byte float
        lat_found, lon_found = get_latlon_from_indices(x, y)
        result.update({
            'lat_found': lat_found, 'lon_found': lon_found,
            'altitude_m': round(val * 100) / 100,
            'distance_m': calculate_distance(latitude, longitude, lat_found,
            lon_found)})
        return result
