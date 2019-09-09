#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import json
import height_map.maps.etopo1 as etopo1
import height_map.maps.srtm1 as srtm1
import height_map.maps.dgm200 as dgm200
import height_map.maps.terr50 as terr50
import height_map.maps.gebco_2019 as gebco_2019
import height_map.maps.earth2014 as earth2014
import height_map.height_info as heightInfo

def get_height(lat,lon):

    h_srtm1 = srtm1.get_height(lat,lon)
    h_terr50 = terr50.get_height(lat, lon)[0]
    h_dgm200, lat_dgm200, lon_dgm200 = dgm200.get_height(lat, lon)
    h_etopo1 = etopo1.get_height(lat,lon)[0]
    h_etopo1bed = etopo1.get_height(lat,lon,ice=False)[0]
    h_earth2014 = earth2014.get_height(lat,lon)[0]
    h_gebco_2019 = gebco_2019.get_height(lat,lon)[0]

    return_string='-> '
    if h_srtm1!=srtm1.NODATA:
        return_string+='SRTM1: '+str(h_srtm1)+'m, '
    if h_terr50 != terr50.NODATA:
        return_string+='TERR50: '+str(h_terr50)+'m, '
    if h_dgm200!=dgm200.NODATA:
        return_string+='DGM200: '+str(round(h_dgm200,2))+'m (dist: '+str(
            dgm200.get_closest_distance(lat, lon)[0])+'m), '
    if h_etopo1!=etopo1.NODATA:
        return_string+='ETOPO1: '+str(h_etopo1)+'m, '
    if h_etopo1!=h_etopo1bed:
        return_string+='ETOPO1_bed: '+str(h_etopo1bed)+'m, '
    if h_earth2014 != earth2014.NODATA:
        return_string += 'Earth2014: '+str(h_earth2014)+'m, '
    if h_gebco_2019 != gebco_2019.NODATA:
        return_string += 'GEBCO_2019: '+str(h_gebco_2019)+'m, '
    return_string += str(heightInfo.get_height(lat,lon))
    return return_string  

def test_height(lat, lon, sources, name=''):

    print('height at {} ({}, {})'.format(name, lat, lon))
    for source in sources:
        t = time.time()
        try:
            results = source.get_height(lat, lon)
        except ValueError as e:
            print (source, e)
            continue
        duration = time.time() - t
        if results[0] != source.NODATA:
            print('    {0!r}: {2:.2f}m at ({3:.5f}, {4:.5f}) in {1:.3f}s'
                  ''.format(source.attribution_name, duration, *results))
    try:
        water_results = heightInfo.get_height(lat, lon, water=True)
        seafloor_results = heightInfo.get_height(lat, lon, water=False)
        print('    {0!r}: {1:.2f}m ({2})'.format(heightInfo.__name__,
                                                 *water_results))
        if water_results[0] != seafloor_results[0]:
            print('    {0!r}, seafloor: {1:.2f}m ({2})'.format(
                  heightInfo.__name__, *seafloor_results))
    except ValueError as e:
        print ('heightInfo:', e)

def test_max(area, sources, name=''):

    print('max_height in {} {}'.format(name, area))
    for source in sources:
        t = time.time()
        results = source.get_max_height(*area)
        duration = time.time() - t
        if results[1] != source.NODATA:
            locations = []
            for location in results[0]:
                (lat, lon) = location
                locations += [(round(lat, 5), round(lon, 5))]
            elevation = results[1]
            counter = results[2]
            print('    {0!r}: {4}x {3:.2f}m at ({2}) in {1:.3f}s'
                  ''.format(source.attribution_name, duration, locations[:3],
                  elevation, counter))

def test_min(area, sources, name=''):

    print('min_height in {} {}'.format(name, area))
    for source in sources:
        t = time.time()
        results = source.get_min_height(*area)
        duration = time.time() - t
        if results[1] != source.NODATA:
            locations = []
            for location in results[0]:
                (lat, lon) = location
                locations += [(round(lat, 5), round(lon, 5))]
            elevation = results[1]
            counter = results[2]
            print('    {0!r}: {4}x {3:.2f}m at ({2}) in {1:.3f}s'
                  ''.format(source.attribution_name, duration, locations[:3],
                  elevation, counter))


if __name__ == "__main__":

    sources = [etopo1, earth2014, dgm200, srtm1, terr50, gebco_2019]
    with open('test_locations.json', 'r') as f:
        locations = json.loads(f.read())
    for location in locations['points']:
        label = location['label']
        lat = location['lat']
        lon = location['lon']
        results = test_height(lat, lon, sources, name=label)
    sources = [etopo1, earth2014, dgm200, terr50, gebco_2019]
    for location in locations['areas']:
        label = location['label']
        area = location['area']
        test_max(area, sources, label)
        test_min(area, sources, label)
