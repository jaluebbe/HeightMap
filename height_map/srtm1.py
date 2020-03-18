import struct
from math import floor
import json
import os
import logging
from height_map.dgm200 import calculate_distance

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
    pwd = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(pwd, 'maps/srtm1')
    attribution_url = 'https://doi.org/10.5067/MEaSUREs/SRTM/SRTMGL1.003'
    attribution_name = 'SRTMGL1'
    attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
        attribution_name)

    precision = 16.0  # 16m SRTM vertical error
    seabed_included = False
    NODATA = -32768
    old_file = None
    old_file_name = None

    def __init__(self):
        if os.path.isfile(os.path.join(self.path, 'srtm1_files.json')):
            with open(os.path.join(self.path, 'srtm1_files.json')
                    ) as srtm1_list_file:
                self.srtm1_file_list = json.load(srtm1_list_file)
        else:
            self.srtm1_file_list = []

    def get_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        self.old_file_name = None
        self.old_file = None
        xllcenter = floor(lon_ll)
        yllcenter = floor(lat_ll)
        total_location = []
        total_h_max = self.NODATA
        total_counter = 0
        # consider only correctly defined rectangle within SRTM coverage:
        if (lat_ll > lat_ur) or (lon_ll > lon_ur) or lat_ur > 60 or lat_ll < -56:
            return [], self.NODATA, 0
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll, yllcenter)
        j_ll = get_index_from_longitude(lon_ll, xllcenter)
        if lat_ur < yllcenter + 1 + CELLSIZE/2:
            i_ur = get_index_from_latitude(lat_ur, yllcenter)
        else:
            # upper_neighbour
            (location, h_max, counter) = self.get_max_height(
                yllcenter + 1 + CELLSIZE/2, lon_ll, lat_ur, min(lon_ur, xllcenter + 1))
            if h_max > total_h_max:
                total_h_max = h_max
                total_counter = counter
                total_location = location
            elif h_max == total_h_max:
                total_counter += counter
                total_location += location
            i_ur = 0
        if lon_ur < xllcenter + 1 + CELLSIZE/2:
            j_ur = get_index_from_longitude(lon_ur, xllcenter)
        else:
            # right_neighbour
            (location, h_max, counter) = self.get_max_height(
                lat_ll, xllcenter + 1 + CELLSIZE/2, lat_ur, lon_ur)
            if h_max > total_h_max:
                total_h_max = h_max
                total_counter = counter
                total_location = location
            elif h_max == total_h_max:
                total_counter += counter
                total_location += location
            j_ur = NCOLS - 1
        h_max = self.NODATA
        counter = 0
        location = []
        # start in the upper left edge of the target area
        i_pos = i_ur
        j_pos = j_ll
        #
        file_name = get_filename(yllcenter, xllcenter)
        fullpath = os.path.join(self.path, file_name)
        if os.path.isfile(fullpath):
            with open(fullpath, "rb") as f:
                while i_ur <= i_pos <= i_ll:
                    f.seek((i_pos * NCOLS + j_pos) * 2)
                    num_values = j_ur - j_ll + 1
                    buf = f.read(num_values * 2)
                    values = struct.unpack('>{:d}h'.format(num_values), buf)
                    while j_ll <= j_pos <= j_ur:
                        # if current height value larger than previous maximum
                        if values[j_pos - j_ll] > h_max:
                            # store current height and position
                            h_max = values[j_pos - j_ll]
                            lat = get_lat_from_index(i_pos, yllcenter)
                            lon = get_lon_from_index(j_pos, xllcenter)
                            location = [(lat, lon)]
                            counter = 1
                        elif values[j_pos - j_ll] == h_max:
                            lat = get_lat_from_index(i_pos, yllcenter)
                            lon = get_lon_from_index(j_pos, xllcenter)
                            location += [(lat, lon)]
                            counter += 1
                        j_pos += 1
                    j_pos = j_ll
                    i_pos += 1
            if h_max > total_h_max:
                total_h_max = h_max
                total_counter = counter
                total_location = location
            elif h_max == total_h_max:
                total_counter += counter
                total_location += location
    #    elif file_name in srtm1_file_list:
    #        print('SRTM1: missing file', file_name)
        return total_location, total_h_max, total_counter

    def get_min_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        self.old_file_name = None
        self.old_file = None
        xllcenter = floor(lon_ll)
        yllcenter = floor(lat_ll)
        total_location = []
        total_h_min = -self.NODATA
        total_counter = 0
        # consider only correctly defined rectangle:
        if (lat_ll > lat_ur) or (lon_ll > lon_ur) or lat_ur > 60 or lat_ll < -56:
            return [], self.NODATA, 0
        # convert coordinates to data indices:
        i_ll = get_index_from_latitude(lat_ll, yllcenter)
        j_ll = get_index_from_longitude(lon_ll, xllcenter)
        if lat_ur < yllcenter + 1 + CELLSIZE/2:
            i_ur = get_index_from_latitude(lat_ur, yllcenter)
        else:
            # upper_neighbour
            (location, h_min, counter) = self.get_min_height(
                yllcenter + 1 + CELLSIZE/2, lon_ll, lat_ur, min(lon_ur, xllcenter + 1))
            if self.NODATA < h_min < total_h_min:
                total_h_min = h_min
                total_counter = counter
                total_location = location
            elif h_min == total_h_min:
                total_counter += counter
                total_location += location
            i_ur = 0
        if lon_ur < xllcenter + 1 + CELLSIZE/2:
            j_ur = get_index_from_longitude(lon_ur, xllcenter)
        else:
            # right_neighbour
            (location, h_min, counter) = self.get_min_height(
                lat_ll, xllcenter + 1 + CELLSIZE/2, lat_ur, lon_ur)
            if self.NODATA < h_min < total_h_min:
                total_h_min = h_min
                total_counter = counter
                total_location = location
            elif h_min == total_h_min:
                total_counter += counter
                total_location += location
            j_ur = NCOLS - 1
        h_min = -self.NODATA
        counter = 0
        location = []
        # start in the upper left edge of the target area
        i_pos = i_ur
        j_pos = j_ll
        #
        file_name = get_filename(yllcenter, xllcenter)
        fullpath = os.path.join(self.path, file_name)
        if os.path.isfile(fullpath):
            with open(fullpath, "rb") as f:
                while i_ur <= i_pos <= i_ll:
                    f.seek((i_pos * NCOLS + j_pos) * 2)
                    num_values = j_ur - j_ll + 1
                    buf = f.read(num_values * 2)
                    values = struct.unpack('>{:d}h'.format(num_values), buf)
                    while j_ll <= j_pos <= j_ur:
                        # if current height value larger than previous maximum
                        if self.NODATA < values[j_pos - j_ll] < h_min:
                            # store current height and position
                            h_min = values[j_pos - j_ll]
                            lat = get_lat_from_index(i_pos, yllcenter)
                            lon = get_lon_from_index(j_pos, xllcenter)
                            location = [(lat, lon)]
                            counter = 1
                        elif self.NODATA < values[j_pos - j_ll] == h_min:
                            lat = get_lat_from_index(i_pos, yllcenter)
                            lon = get_lon_from_index(j_pos, xllcenter)
                            location += [(lat, lon)]
                            counter += 1
                        j_pos += 1
                    j_pos = j_ll
                    i_pos += 1
            if h_min == -self.NODATA:
                h_min = self.NODATA
            if self.NODATA < h_min < total_h_min:
                total_h_min = h_min
                total_counter = counter
                total_location = location
            elif h_min == total_h_min:
                total_counter += counter
                total_location += location
    #    elif file_name in srtm1_file_list:
    #        print('SRTM1: missing file', file_name)
        if total_h_min == -self.NODATA:
            total_h_min = self.NODATA
        return total_location, total_h_min, total_counter

    def get_height(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        xllcenter = floor(lon)
        yllcenter = floor(lat)
        file_name = get_filename(yllcenter, xllcenter)
        fullpath = os.path.join(self.path, file_name)
        val = self.NODATA
        lat_found = lat
        lon_found = lon
        if os.path.isfile(fullpath):
            # verified with
            # gdallocationinfo N52W002.hgt -wgs84 -1.215090 52.925315
            i = get_index_from_latitude(lat, yllcenter)
            j = get_index_from_longitude(lon, xllcenter)
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
            lat_found = get_lat_from_index(i, yllcenter)
            lon_found = get_lon_from_index(j, xllcenter)
        elif not (lat > 60 or lat < -56) and file_name in self.srtm1_file_list:
            logging.debug(f'SRTM1: missing file {file_name} for ({lat}, {lon})')
        return {
            'lat': lat, 'lon': lon, 'lat_found': round(lat_found, 6),
            'lon_found': round(lon_found, 6), 'altitude_m': val,
            'source': self.attribution_name, 'distance_m': round(
            calculate_distance(lat, lon, lat_found, lon_found), 3),
            'attribution': self.attribution}
