import os
from libc.math cimport M_PI, sqrt, sin, tan, cos, acos, pow, round, fmin, fmax
import struct
import logging

XLLCENTER = 280000
YLLCENTER = 5236000
CELLSIZE = 200
NCOLS = 3207
NROWS = 4331
LAT_MIN = 47.141612
LAT_MAX = 55.016964
LON_MIN = 5.557084
LON_MAX = 15.572619

cdef double _deg2rad = M_PI / 180.0
cdef double _rad2deg = 180.0 / M_PI


cdef (double, double) LLtoUTM(double Lat, double Long):
    cdef double a = 6378137
    cdef double eccSquared = 0.00669438
    cdef double k0 = 0.9996

    # Make sure the longitude is between -180.00 .. 179.9
    cdef double LongTemp = Long + 180 - int((Long + 180) / 360)*360 - 180
    cdef double LatRad = Lat * _deg2rad
    cdef double LongRad = LongTemp * _deg2rad
    cdef int ZoneNumber = 32
    # +3 puts origin in middle of zone
    cdef int LongOrigin = (ZoneNumber - 1)*6 - 180 + 3
    cdef double LongOriginRad = LongOrigin * _deg2rad
    cdef double eccPrimeSquared = (eccSquared) / (1 - eccSquared)
    cdef double N = a / sqrt(1 - eccSquared*sin(LatRad)*sin(LatRad))
    cdef double T = tan(LatRad) * tan(LatRad)
    cdef double C = eccPrimeSquared * cos(LatRad) * cos(LatRad)
    cdef double A = cos(LatRad) * (LongRad - LongOriginRad)
    cdef double M = (
        a * ((1 - eccSquared/4 - 3*pow(eccSquared, 2)/64
        - 5*pow(eccSquared, 3)/256)*LatRad
        - (3*eccSquared/8 + 3*pow(eccSquared, 2)/32
        + 45*pow(eccSquared, 3)/1024)*sin(2 * LatRad)
        + (15*pow(eccSquared, 2)/256 + 45*pow(eccSquared, 3)/1024)
        *sin(4 * LatRad)
        - (35*pow(eccSquared, 3)/3072)*sin(6 * LatRad)))
    cdef double UTMEasting = (
        k0 * N * (A + (1 - T + C) * A * A * A / 6
        + (5 - 18*T + T*T + 72*C - 58*eccPrimeSquared)*pow(A, 5)/120)
        + 500000.0)
    cdef double UTMNorthing = (
        k0 * (M + N*tan(LatRad)*(A*A/2 + (5 - T + 9*C + 4*C*C)*pow(A, 4)/24
        + (61 - 58*T + T*T + 600*C - 330*eccPrimeSquared)*pow(A, 6)/720)))
    return UTMEasting, UTMNorthing


cdef (double, double) UTMtoLL(double easting, double northing):
    cdef double k0 = 0.9996
    cdef double a = 6378137
    cdef double eccSquared = 0.00669438
    cdef double e1 = (1 - sqrt(1 - eccSquared)) / (1 + sqrt(1 - eccSquared))
    # remove 500,000 meter offset for longitude
    cdef double x = easting - 500000.0
    cdef int ZoneNumber = 32
    # +3 puts origin in middle of zone
    cdef int LongOrigin = (ZoneNumber - 1)*6 - 180 + 3
    cdef double eccPrimeSquared = (eccSquared) / (1 - eccSquared)
    cdef double M = northing / k0
    cdef double mu = M / (a * (1 - eccSquared/4 - 3*pow(eccSquared, 2)/64
        - 5*pow(eccSquared, 3)/256))
    cdef double phi1Rad = (mu + (3*e1/2 - 27*pow(e1, 3)/32)*sin(2*mu)
                           + (21*e1*e1/16 - 55*pow(e1, 4)/32)*sin(4 * mu)
                           + (151 * pow(e1, 3) / 96)*sin(6 * mu))
    cdef double phi1 = phi1Rad * _rad2deg;
    cdef double N1 = a / sqrt(1 - eccSquared*pow(sin(phi1Rad), 2))
    cdef double T1 = pow(tan(phi1Rad), 2)
    cdef double C1 = eccPrimeSquared * pow(cos(phi1Rad), 2)
    cdef double R1 = (
        a * (1 - eccSquared) / pow(1 - eccSquared*pow(sin(phi1Rad), 2), 1.5))
    cdef double D = x / (N1 * k0)
    cdef double Lat = (
        phi1Rad - (N1 * tan(phi1Rad) / R1)
        *(D*D/2 - (5 + 3*T1 + 10*C1 - 4*C1*C1 - 9*eccPrimeSquared)*pow(D, 4)/24
        + (61 + 90*T1 + 298*C1 + 45*T1*T1 - 252*eccPrimeSquared - 3*C1*C1)
        *pow(D, 6)/720))
    Lat = Lat * _rad2deg
    cdef double Long = (
        D - (1 + 2*T1 + C1)*pow(D, 3)/6
        + (5 - 2*C1 + 28*T1 - 3*C1*C1 + 8*eccPrimeSquared + 24*T1*T1)
        *pow(D, 5)/120) / cos(phi1Rad)
    Long = LongOrigin + Long * _rad2deg
    return round(Lat * 1e6) / 1e6, round(Long * 1e6) / 1e6


# calculate the distance between two gps coordinates:
cdef double get_distance(double lat1, double lon1, double lat2, double lon2):
    cdef double degRad = 2 * M_PI / 360
    cdef double distance = 6.370e6 * acos(sin(lat1 * degRad) * sin(lat2 * degRad)
        + cos(lat1 * degRad) * cos(lat2 * degRad) * cos((lon2 - lon1) * degRad))
    return distance


# expose get_distance
def calculate_distance(lat1, lon1, lat2, lon2):
    if lat1 == lat2 and lon1 == lon2:
        return 0
    return get_distance(lat1, lon1, lat2, lon2)


# calculate the distance to the closest DGM200 reference point
def get_closest_distance(double latitude, double longitude):
    cdef double easting, northing, distance
    cdef ref_east, ref_north, ref_lat, ref_lon
    # obtain UTM32 coordinates for given latitude, longitude
    easting, northing = LLtoUTM(latitude, longitude)
    # clip UTM32 coordinates to range of DGM200 data
    easting = fmax(XLLCENTER, fmin(easting, XLLCENTER + CELLSIZE*NCOLS - 1))
    northing = fmax(YLLCENTER, fmin(northing, YLLCENTER + CELLSIZE*NROWS - 1))
    # determine indices of DGM200 grid for given location
    x = int(round(((easting - XLLCENTER) / CELLSIZE)))
    y = int(round(NROWS - 1 - ((northing - YLLCENTER) / CELLSIZE)))
    # get UTM32 coordinates for grid point location
    ref_east = x*CELLSIZE + XLLCENTER
    ref_north = (NROWS - 1 - y)*CELLSIZE + YLLCENTER
    # convert UTM32 reference position back to latitude, logitude
    ref_lat, ref_lon = UTMtoLL(ref_east, ref_north)
    # calculate distance between position and reference
    distance = get_distance(latitude, longitude, ref_lat, ref_lon)
    return {'distance': round(distance * 100) / 100, 'ref_lat': ref_lat,
        'ref_lon': ref_lon}


cdef (int, int) get_indices_from_latlon(double latitude, double longitude):
    cdef double easting, northing
    easting, northing = LLtoUTM(latitude, longitude)
    cdef int x = int(round(((easting - XLLCENTER) / CELLSIZE)))
    cdef int y = int(round(NROWS - 1 - ((northing - YLLCENTER) / CELLSIZE)))
    if x < 0 or x >= NCOLS or y < 0 or y >= NROWS:
        x = -1
        y = -1
    return x, y


cdef (double, double) get_latlon_from_indices(unsigned int x, unsigned int y):
    cdef double easting = x*CELLSIZE + XLLCENTER
    cdef double northing = (NROWS - 1 - y)*CELLSIZE + YLLCENTER
    cdef double lat, lon
    lat, lon = UTMtoLL(easting, northing)
    return lat, lon


class Dgm200:
    logger = logging.getLogger(__name__)
    attribution_url = 'http://www.bkg.bund.de'
    attribution_name = 'DGM200'
    attribution = '&copy GeoBasis-DE / <a href="{}">BKG</a> 2019'.format(
        attribution_url)
    precision = 10.0  # max height error of dgm200 dataset
    file = None
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

    def get_max_height(self, double lat_ll, double lon_ll, double lat_ur,
            double lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'source': self.attribution_name, 'attribution': self.attribution}
        # ensure requested rectangle is not out of bounds:
        if (lat_ll < LAT_MIN or lat_ll > LAT_MAX or lon_ll < LON_MIN or
                lon_ll > LON_MAX or lat_ur < LAT_MIN or lat_ur > LAT_MAX or
                lon_ur < LON_MIN or lon_ur > LON_MAX):
            return result
        # consider only correctly defined rectangle:
        if (lat_ll > lat_ur or lon_ll > lon_ur):
            return result
        cdef int x_ll, y_ll, x_ur, y_ur
        cdef double val
        (x_ll, y_ll) = get_indices_from_latlon(lat_ll, lon_ll)
        if x_ll == -1 or y_ll == -1:
            return result
        (x_ur, y_ur) = get_indices_from_latlon(lat_ur, lon_ur)
        if x_ur == -1 or y_ur == -1:
            return result
        #
        cdef double h_max = self.NODATA
        cdef int counter = 0
        # start in the upper left edge of the target area
        cdef int x_pos = x_ll
        cdef int y_pos = y_ur
        locations = []
        with open(self.file, "rb") as f:
            while(y_ur <= y_pos <= y_ll):
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

    def get_min_height(self, double lat_ll, double lon_ll, double lat_ur,
            double lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attribution': self.attribution}
        # ensure requested rectangle is not out of bounds:
        if (lat_ll < LAT_MIN or lat_ll > LAT_MAX or lon_ll < LON_MIN or
                lon_ll > LON_MAX or lat_ur < LAT_MIN or lat_ur > LAT_MAX or
                lon_ur < LON_MIN or lon_ur > LON_MAX):
            return result
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        cdef int x_ll, y_ll, x_ur, y_ur
        cdef double val
        x_ll, y_ll = get_indices_from_latlon(lat_ll, lon_ll)
        if x_ll == -1 or y_ll == -1:
            return result
        x_ur, y_ur = get_indices_from_latlon(lat_ur, lon_ur)
        if x_ur == -1 or y_ur == -1:
            return result
        #
        cdef double h_min = -self.NODATA
        cdef int counter = 0
        # start in the upper left edge of the target area
        cdef int x_pos = x_ll
        cdef int y_pos = y_ur
        locations = []
        with open(self.file, "rb") as f:
            while y_ur <= y_pos <= y_ll:
                #
                f.seek((y_pos*NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while(x_ll <= x_pos <= x_ur):
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

    def get_min_max_height(self, double lat_ll, double lon_ll, double lat_ur,
            double lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {
            'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attribution': self.attribution}
        # ensure requested rectangle is not out of bounds:
        if (lat_ll < LAT_MIN or lat_ll > LAT_MAX or lon_ll < LON_MIN or
                lon_ll > LON_MAX or lat_ur < LAT_MIN or lat_ur > LAT_MAX or
                lon_ur < LON_MIN or lon_ur > LON_MAX):
            return result
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        cdef int x_ll, y_ll, x_ur, y_ur
        cdef double val
        x_ll, y_ll = get_indices_from_latlon(lat_ll, lon_ll)
        if x_ll == -1 or y_ll == -1:
            return result
        x_ur, y_ur = get_indices_from_latlon(lat_ur, lon_ur)
        if x_ur == -1 or y_ur == -1:
            return result
        #
        cdef double h_max = self.NODATA
        cdef double h_min = -self.NODATA
        cdef int counter_max = 0
        cdef int counter_min = 0
        # start in the upper left edge of the target area
        cdef int x_pos = x_ll
        cdef int y_pos = y_ur
        locations_max = []
        locations_min = []
        with open(self.file, "rb") as f:
            while y_ur <= y_pos <= y_ll:
                #
                f.seek((y_pos*NCOLS + x_pos) * 4)
                num_values = x_ur - x_ll + 1
                buf = f.read(num_values * 4)
                values = struct.unpack('>{:d}f'.format(num_values), buf)
                while(x_ll <= x_pos <= x_ur):
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

    def get_height(self, double latitude, double longitude):
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(latitude,
                longitude))
        result = {
            'altitude_m': self.NODATA, 'source': self.attribution_name,
            'lat': latitude, 'lon': longitude, 'distance_m': 0,
            'attribution': self.attribution}
        if (latitude < LAT_MIN or latitude > LAT_MAX or longitude < LON_MIN or
                longitude > LON_MAX):
            return result
        cdef int x, y
        x, y = get_indices_from_latlon(latitude, longitude)
        cdef double val
        val = self.NODATA
        if x == -1 or y == -1:
            return result
        with open(self.file, "rb") as f:
            f.seek((y*NCOLS + x) * 4)  # go to the right spot,
            buf = f.read(4)  # read four bytes and convert them:
            val = struct.unpack('>f', buf)[0]  # ">f" is a four byte float
        cdef double lat_found, lon_found
        lat_found, lon_found = get_latlon_from_indices(x, y)
        result.update({
            'lat_found': lat_found, 'lon_found': lon_found,
            'altitude_m': round(val * 100) / 100, 'distance_m': get_distance(
            latitude, longitude, lat_found, lon_found)})
        return result
