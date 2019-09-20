import os
from libc.math cimport M_PI, sqrt, sin, tan, cos, acos, pow, round, fmin, fmax
import struct

grid_file = 'dgm200_utm32s_f4.hgt'

XLLCENTER = 280000
YLLCENTER = 5236000
CELLSIZE = 200
NCOLS = 3207
NROWS = 4331
NODATA = -9999
path = 'height_map/maps/dgm200'
attribution_url = 'http://www.bkg.bund.de'
attribution_name = 'DGM200'
attribution = '&copy GeoBasis-DE / <a href="{}">BKG</a> 2019'.format(
    attribution_url)

precision = 10.0  # max height error of dgm200 dataset 

# calculate the distance between two gps coordinates:
cdef double get_distance(double lat1, double lon1, double lat2, double lon2):
    cdef double degRad = 2 * M_PI / 360
    cdef double distance = 6.370e6 * acos(sin(lat1 * degRad) * sin(lat2 * degRad)
        + cos(lat1 * degRad) * cos(lat2 * degRad) * cos((lon2 - lon1) * degRad))
    return distance

# expose get_distance
def calculate_distance(lat1, lon1, lat2, lon2):
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
    return (round(distance * 100) / 100, ref_lat, ref_lon)

def get_indices_from_latlon(double latitude, double longitude):
    cdef int x = -1
    cdef int y = -1
    cdef double easting, northing, val, ref_easting, ref_northing
    val = NODATA
    easting, northing = LLtoUTM(latitude, longitude)
    if (easting >= XLLCENTER and easting < XLLCENTER + CELLSIZE*NCOLS):
        x = int(round(((easting - XLLCENTER) / CELLSIZE)))
    if (northing >= YLLCENTER and northing < YLLCENTER + CELLSIZE*NROWS):
        y = int(round(NROWS - 1 - ((northing - YLLCENTER) / CELLSIZE)))
    return (x, y)

def get_latlon_from_indices(int x, int y):
    cdef double easting = x*CELLSIZE + XLLCENTER
    cdef double northing = (NROWS - 1 - y)*CELLSIZE + YLLCENTER
    cdef double lat, lon
    (lat, lon) = UTMtoLL(easting, northing)
    return (lat, lon)

def get_max_height(double lat_ll, double lon_ll, double lat_ur, double lon_ur):
    # consider only correctly defined rectangle:
    if (lat_ll > lat_ur or lon_ll > lon_ur):
        return ([], NODATA, 0)
    cdef int x_ll, y_ll, x_ur, y_ur
    cdef double val
    (x_ll, y_ll) = get_indices_from_latlon(lat_ll, lon_ll)
    if x_ll == -1 or y_ll == -1:
        return ([], NODATA, 0)
    (x_ur, y_ur) = get_indices_from_latlon(lat_ur, lon_ur)
    if x_ur == -1 or y_ur == -1:
        return ([], NODATA, 0)
    #
    cdef double h_max = NODATA
    cdef int counter = 0
    # start in the upper left edge of the target area
    cdef int x_pos = x_ll
    cdef int y_pos = y_ur
    file_name = os.path.join(path, grid_file)
    locations = []
    with open(file_name, "rb") as f:
        while(y_ur <= y_pos <= y_ll):
            #
            f.seek((y_pos*NCOLS + x_pos) * 4)
            num_values = x_ur - x_ll + 1
            buf = f.read(num_values * 4)
            values = struct.unpack('>{:d}f'.format(num_values), buf)
            while(x_ll <= x_pos <= x_ur):
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
    return (locations, h_max, counter)

def get_min_height(double lat_ll, double lon_ll, double lat_ur, double lon_ur):
    # consider only correctly defined rectangle:
    if (lat_ll > lat_ur or lon_ll > lon_ur):
        return ([], NODATA, 0)
    cdef int x_ll, y_ll, x_ur, y_ur
    cdef double val
    (x_ll, y_ll) = get_indices_from_latlon(lat_ll, lon_ll)
    if x_ll == -1 or y_ll == -1:
        return ([], NODATA, 0)
    (x_ur, y_ur) = get_indices_from_latlon(lat_ur, lon_ur)
    if x_ur == -1 or y_ur == -1:
        return ([], NODATA, 0)
    #
    cdef double h_min = -NODATA
    cdef int counter = 0
    # start in the upper left edge of the target area
    cdef int x_pos = x_ll
    cdef int y_pos = y_ur
    file_name = os.path.join(path, grid_file)
    locations = []
    with open(file_name, "rb") as f:
        while(y_ur <= y_pos <= y_ll):
            #
            f.seek((y_pos*NCOLS + x_pos) * 4)
            num_values = x_ur - x_ll + 1
            buf = f.read(num_values * 4)
            values = struct.unpack('>{:d}f'.format(num_values), buf)
            while(x_ll <= x_pos <= x_ur):
                val = values[x_pos - x_ll]
                if (NODATA < val < h_min):
                    h_min = val
                    locations.clear()
                    locations.append(get_latlon_from_indices(x_pos, y_pos))
                    counter = 1
                elif (NODATA < val == h_min):
                    locations.append(get_latlon_from_indices(x_pos, y_pos))
                    counter += 1
                x_pos += 1
            x_pos = x_ll
            y_pos += 1
    if h_min == -NODATA:
        h_min = NODATA
    return (locations, h_min, counter)

def get_height(double latitude, double longitude):
    cdef int x, y
    (x, y) = get_indices_from_latlon(latitude, longitude)
    cdef double val
    val = NODATA
    if x == -1 or y == -1:
        return {
            'altitude_m': NODATA, 'source': attribution_name,
            'latitude': latitude, 'lon': longitude, 'distance_m': 0,
            'attribution': attribution}
    file_name = os.path.join(path, grid_file)
    with open(file_name, "rb") as f:
        f.seek((y*NCOLS + x) * 4)  # go to the right spot,
        buf = f.read(4)  # read four bytes and convert them:
        val = struct.unpack('>f', buf)[0]  # ">f" is a four byte float
    cdef double lat, lon
    (lat, lon) = get_latlon_from_indices(x, y)
    return {
        'altitude_m': round(val * 100) / 100, 'source': attribution_name,
        'latitude': lat, 'longitude': lon, 'distance_m': get_distance(latitude,
        longitude, lat, lon), 'attribution': attribution}

cdef double _deg2rad = M_PI / 180.0
cdef double _rad2deg = 180.0 / M_PI

def LLtoUTM(double Lat, double Long):
    cdef double a = 6378137
    cdef double eccSquared = 0.00669438
    cdef double k0 = 0.9996

    #Make sure the longitude is between -180.00 .. 179.9
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
    return (UTMEasting, UTMNorthing)

def UTMtoLL(double easting, double northing):
    cdef double k0 = 0.9996
    cdef double a = 6378137
    cdef double eccSquared = 0.00669438
    cdef double e1 = (1 - sqrt(1 - eccSquared)) / (1 + sqrt(1 - eccSquared))
    #remove 500,000 meter offset for longitude
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
    return (round(Lat * 1e6) / 1e6, round(Long * 1e6) / 1e6)
