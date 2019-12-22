import os
import height_map.srtm1 as srtm1
import height_map.dgm200 as dgm200
import height_map.terr50 as terr50
import height_map.bd_alti75 as bd_alti75
import height_map.earth2014 as earth2014
import height_map.gebco_2019 as gebco_2019
attribution_name = 'height_info'
NODATA = -32768

def get_height(lat, lon, ice=True, water=True):
    gebco_2019_result = gebco_2019.get_height(lat, lon)
    h_gebco_2019 = gebco_2019_result['altitude_m']
    dist_dgm200 = dgm200.get_closest_distance(lat, lon)[0]
    dgm200_result = dgm200.get_height(lat, lon)
    if (dgm200_result['distance_m'] < 25) and (
        dgm200_result['altitude_m'] != dgm200.NODATA) and (
        h_gebco_2019 == gebco_2019.NODATA or h_gebco_2019 >= 0):
        # prefer sea floor bathymetry if possible
        return dgm200_result
    terr50_result = terr50.get_height(lat, lon)
    h_terr50 = terr50_result['altitude_m']
    if h_terr50 != terr50.NODATA and (h_gebco_2019 == gebco_2019.NODATA or
        h_gebco_2019 >= 0 or h_terr50 > 0 or h_gebco_2019 > h_terr50):
        # prefer sea floor bathymetry if possible
        return terr50_result
    bd_alti75_result = bd_alti75.get_height(lat, lon)
    h_bd_alti75 = bd_alti75_result['altitude_m']
    if h_bd_alti75 != bd_alti75.NODATA and (h_gebco_2019 == gebco_2019.NODATA or
        h_gebco_2019 >= 0 or h_bd_alti75 > 0 or h_gebco_2019 > h_bd_alti75):
        # prefer sea floor bathymetry if possible
        return bd_alti75_result
    srtm1_result = srtm1.get_height(lat, lon)
    if srtm1_result['altitude_m'] not in (srtm1.NODATA, 0):
        # avoid sea surface at 0m being returned instead of sea floor bathymetry
        return srtm1_result
    if dgm200_result['altitude_m'] != dgm200.NODATA and (
        h_gebco_2019 == gebco_2019.NODATA or h_gebco_2019 >= 0):
        # prefer sea floor bathymetry if possible
        return dgm200_result
    if gebco_2019_result['altitude_m'] != gebco_2019.NODATA:
        return gebco_2019_result
    earth2014_result = earth2014.get_height(lat, lon, ice=ice, water=water)
    if earth2014_result['altitude_m'] != earth2014.NODATA:
        return earth2014_result
    else:
        return {'altitude_m': NODATA, 'latitude': lat, 'longitude': lon,
            'distance_m': 0, 'source': 'NODATA'}

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    for source in [terr50, bd_alti75, srtm1, dgm200, gebco_2019, earth2014]:
        result = source.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)
        (location_max, h_max, counter) = result
        if h_max != source.NODATA:
            return result

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    for source in [terr50, bd_alti75, srtm1, dgm200, gebco_2019, earth2014]:
        result = source.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)
        (location_min, h_min, counter) = result
        if h_min != source.NODATA:
            return result
