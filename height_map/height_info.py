import os
import height_map.srtm1 as srtm1
import height_map.dgm200 as dgm200
import height_map.terr50 as terr50
import height_map.earth2014 as earth2014
import height_map.gebco_2019 as gebco_2019
from height_map.cci_water_bodies_v4 import WaterBodies

wb = WaterBodies()
attribution_name = 'height_info'
NODATA = -32768

def get_height(lat, lon, water=True):
    """
    Get the elevation of the given location from the best available data source.

    :param lat: float -- latitude.
    :param lon: float -- longitude.
    :param water: bool -- Should water surface be reported as 0m?
    :returns: dict
    """
    wb_label = wb.get_data_at_position(lat, lon)['label']
    is_ocean = wb_label == 'Ocean'
    dist_dgm200 = dgm200.get_closest_distance(lat, lon)[0]
    dgm200_result = dgm200.get_height(lat, lon)
    if (dgm200_result['distance_m'] < 25) and (
        dgm200_result['altitude_m'] != dgm200.NODATA) and not is_ocean:
        # prefer sea floor bathymetry if possible
        dgm200_result['wb_label'] = wb_label
        return dgm200_result
    terr50_result = terr50.get_height(lat, lon)
    h_terr50 = terr50_result['altitude_m']
    if h_terr50 != terr50.NODATA and not is_ocean or h_terr50 > 0:
        # prefer sea floor bathymetry if possible
        terr50_result['wb_label'] = wb_label
        return terr50_result
    srtm1_result = srtm1.get_height(lat, lon)
    h_srtm1 = srtm1_result['altitude_m']
    if h_srtm1 != srtm1.NODATA and not is_ocean or h_srtm1 > 0:
        # prefer sea floor bathymetry if possible
        srtm1_result['wb_label'] = wb_label
        return srtm1_result
    if dgm200_result['altitude_m'] != dgm200.NODATA and not is_ocean:
        # prefer sea floor bathymetry if possible
        dgm200_result['wb_label'] = wb_label
        return dgm200_result
    gebco_2019_result = gebco_2019.get_height(lat, lon)
    if gebco_2019_result['altitude_m'] != gebco_2019.NODATA:
        gebco_2019_result['wb_label'] = wb_label
        return gebco_2019_result
    earth2014_result = earth2014.get_height(lat, lon, water=water)
    if earth2014_result['altitude_m'] != earth2014.NODATA:
        earth2014_result['wb_label'] = wb_label
        return earth2014_result
    else:
        return {'altitude_m': NODATA, 'latitude': lat, 'longitude': lon,
            'distance_m': 0, 'source': 'NODATA', 'wb_label': wb_label}

def get_max_height(lat_ll, lon_ll, lat_ur, lon_ur):
    for source in [terr50, srtm1, dgm200, gebco_2019, earth2014]:
        result = source.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)
        (location_max, h_max, counter) = result
        if h_max != source.NODATA:
            return result

def get_min_height(lat_ll, lon_ll, lat_ur, lon_ur):
    for source in [terr50, srtm1, dgm200, gebco_2019, earth2014]:
        result = source.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)
        (location_min, h_min, counter) = result
        if h_min != source.NODATA:
            return result
