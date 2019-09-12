import os
import height_map.srtm1 as srtm1
import height_map.dgm200 as dgm200
import height_map.terr50 as terr50
import height_map.earth2014 as earth2014
import height_map.gebco_2019 as gebco_2019

NODATA = float('nan')

def get_height(lat, lon, ice=True, water=True):
    h_gebco_2019, lat_gebco_2019, lon_gebco_2019 = gebco_2019.get_height(lat,
        lon)
    dist_dgm200 = dgm200.get_closest_distance(lat, lon)[0]
    h_dgm200, lat_dgm200, lon_dgm200 = dgm200.get_height(lat, lon)
    if (dist_dgm200 < 25) and (h_dgm200 != dgm200.NODATA) and (
            h_gebco_2019 == gebco_2019.NODATA or h_gebco_2019 >= 0):
        # prefer sea floor bathymetry if possible
        return {
            'altitude_m': h_dgm200, 'source': 'DGM200', 'latitude': lat_dgm200,
            'longitude': lon_dgm200, 'distance_m': dgm200.calculate_distance(
            lat, lon, lat_dgm200, lon_dgm200),
            'attribution': dgm200.attribution}
    h_terr50, lat_terr50, lon_terr50 = terr50.get_height(lat, lon)
    if h_terr50 != terr50.NODATA and (h_gebco_2019 == gebco_2019.NODATA or
            h_gebco_2019 >= 0 or h_terr50 > 0 or h_gebco_2019 > h_terr50):
        # prefer sea floor bathymetry if possible
        return {
            'altitude_m': h_terr50, 'source': 'TERR50', 'latitude': lat_terr50,
            'longitude': lon_terr50, 'distance_m': dgm200.calculate_distance(
            lat, lon, lat_terr50, lon_terr50),
            'attribution': terr50.attribution}
    h_srtm1, lat_srtm1, lon_srtm1 = srtm1.get_height(lat, lon)
    if h_srtm1 != srtm1.NODATA and h_srtm1 != 0:
        # avoid sea surface at 0m being returned instead of sea floor bathymetry
        return {
            'altitude_m': h_srtm1, 'source': 'SRTM1', 'latitude': lat_srtm1,
            'longitude': lon_srtm1, 'distance_m': dgm200.calculate_distance(
            lat, lon, lat_srtm1, lon_srtm1),
            'attribution': srtm1.attribution}
    if h_dgm200 != dgm200.NODATA and (h_gebco_2019 == gebco_2019.NODATA or
            h_gebco_2019 >= 0):
        # prefer sea floor bathymetry if possible
        return {
            'altitude_m': h_dgm200, 'source': 'DGM200', 'latitude': lat_dgm200,
            'longitude': lon_dgm200, 'distance_m': dgm200.calculate_distance(
            lat, lon, lat_dgm200, lon_dgm200),
            'attribution': dgm200.attribution}
    if h_gebco_2019 != gebco_2019.NODATA:
        return {
            'altitude_m': h_gebco_2019, 'source': 'GEBCO_2019',
            'latitude': lat_gebco_2019, 'longitude': lon_gebco_2019,
            'distance_m': dgm200.calculate_distance(lat, lon, lat_gebco_2019,
            lon_gebco_2019), 'attribution': gebco_2019.attribution}
    h_earth2014, lat_earth2014, lon_earth2014 = earth2014.get_height(lat, lon,
        ice=ice, water=water)
    if h_earth2014 != earth2014.NODATA:
        return {
            'altitude_m': h_earth2014, 'source': 'EARTH2014',
            'latitude': lat_earth2014, 'longitude': lon_earth2014,
            'distance_m': dgm200.calculate_distance(lat, lon, lat_earth2014,
            lon_earth2014), 'attribution': earth2014.attribution}
    else:
        return {'altitude_m': NODATA, 'latitude': lat, 'longitude': lon,
            'distance_m': 0, 'source': 'NODATA'}
