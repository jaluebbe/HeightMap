import os
import height_map.maps.srtm1 as srtm1
import height_map.maps.dgm200 as dgm200
import height_map.maps.terr50 as terr50
import height_map.maps.earth2014 as earth2014
import height_map.maps.gebco_2019 as gebco_2019

NODATA = float('nan')

def get_height(lat, lon, ice=True, water=True):
    h_gebco_2019, lat_gebco_2019, lon_gebco_2019 = gebco_2019.get_height(lat,
        lon)
    dist_dgm200 = dgm200.get_closest_distance(lat, lon)[0]
    h_dgm200, lat_dgm200, lon_dgm200 = dgm200.get_height(lat, lon)
    if (dist_dgm200 < 25) and (h_dgm200 != dgm200.NODATA) and (
            h_gebco_2019 == gebco_2019.NODATA or h_gebco_2019 >= 0):
        # prefer sea floor bathymetry if possible
        return (
            h_dgm200, 'DGM200', lat_dgm200, lon_dgm200,
            dgm200.calculate_distance(lat, lon, lat_dgm200, lon_dgm200),
            dgm200.attribution)
    h_terr50, lat_terr50, lon_terr50 = terr50.get_height(lat, lon)
    if h_terr50 != terr50.NODATA and (h_gebco_2019 == gebco_2019.NODATA or
            h_gebco_2019 >= 0 or h_terr50 > 0 or h_gebco_2019 > h_terr50):
        # prefer sea floor bathymetry if possible
        return (h_terr50, 'TERR50', lat_terr50, lon_terr50,
            dgm200.calculate_distance(lat, lon, lat_terr50, lon_terr50),
            terr50.attribution)
    h_srtm1, lat_srtm1, lon_srtm1 = srtm1.get_height(lat, lon)
    if h_srtm1 != srtm1.NODATA and h_srtm1 != 0:
        # avoid sea surface at 0m being returned instead of sea floor bathymetry
        return (h_srtm1, 'SRTM1', lat_srtm1, lon_srtm1,
            dgm200.calculate_distance(lat, lon, lat_srtm1, lon_srtm1),
            srtm1.attribution)
    if h_dgm200 != dgm200.NODATA and (h_gebco_2019 == gebco_2019.NODATA or
            h_gebco_2019 >= 0):
        # prefer sea floor bathymetry if possible
        return (h_dgm200, 'DGM200', lat_dgm200, lon_dgm200,
            dgm200.calculate_distance(lat, lon, lat_dgm200, lon_dgm200),
            dgm200.attribution)
    if h_gebco_2019 != gebco_2019.NODATA:
        return (h_gebco_2019, 'GEBCO_2019', lat_gebco_2019, lon_gebco_2019,
            dgm200.calculate_distance(lat, lon, lat_gebco_2019, lon_gebco_2019),
            gebco_2019.attribution)
    h_earth2014, lat_earth2014, lon_earth2014 = earth2014.get_height(lat, lon,
        ice=ice, water=water)
    if h_earth2014 != earth2014.NODATA:
        return (h_earth2014, 'Earth2014', lat_earth2014, lon_earth2014,
            dgm200.calculate_distance(lat, lon, lat_earth2014, lon_earth2014),
            earth2014.attribution)
    else:
        return (NODATA, 'NODATA', lat, lon, 0)
