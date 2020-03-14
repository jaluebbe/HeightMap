#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import json
from height_map.terr50 import Terrain50
from height_map.srtm1 import Srtm1
from height_map.dgm200 import Dgm200
from height_map.gebco_2019 import Gebco2019
from height_map.height_info import HeightInfo

dgm200 = Dgm200()
terr50 = Terrain50()
srtm1 = Srtm1()
gebco_2019 = Gebco2019()
height_info = HeightInfo()


def get_height(lat, lon):

    srtm1_result = srtm1.get_height(lat, lon)
    terr50_result = terr50.get_height(lat, lon)
    dgm200_result = dgm200.get_height(lat, lon)
    gebco_2019_result = gebco_2019.get_height(lat, lon)

    results = {'request': {'lat': lat, 'lon': lon}}
    if srtm1_result['altitude_m'] != srtm1.NODATA:
        results['SRTM1'] = srtm1_result
    if terr50_result['altitude_m'] != terr50.NODATA:
        results['TERR50'] = terr50_result
    if dgm200_result['altitude_m'] != dgm200.NODATA:
        results['DGM200'] = dgm200_result
    if gebco_2019_result['altitude_m'] != gebco_2019.NODATA:
        results['GEBCO_2019'] = gebco_2019_result
    results['height_info'] = height_info.get_height(lat, lon)
    return results


def test_height(lat, lon, sources, name=''):

    print('##### height at {} ({}, {}) #####'.format(name, lat, lon))
    for source in sources:
        t = time.time()
        try:
            result = source.get_height(lat, lon)
        except ValueError as e:
            print(source, e)
            continue
        duration = time.time() - t
        if result['altitude_m'] != source.NODATA:
            print('{1} in {0:.3f}s'.format(duration, str(result)))
    try:
        results = height_info.get_height(lat, lon)
        print(results)
    except ValueError as e:
        print('height_info:', e)


def test_max(area, sources, name=''):

    print('max_height in {} {}'.format(name, area))
    for source in sources:
        t = time.time()
        results = source.get_max_height(*area)
        duration = time.time() - t
        if results['h_max'] != source.NODATA:
            locations = []
            for location in results['location_max']:
                (lat, lon) = location
                locations += [(round(lat, 5), round(lon, 5))]
            elevation = results['h_max']
            counter = results['counter_max']
            print('    {0!r}: {4}x {3:.2f}m at ({2}) in {1:.3f}s'
                  ''.format(source.attribution_name, duration, locations[:3],
                  elevation, counter))


def test_min(area, sources, name=''):

    print('min_height in {} {}'.format(name, area))
    for source in sources:
        t = time.time()
        results = source.get_min_height(*area)
        duration = time.time() - t
        if results['h_min'] != source.NODATA:
            locations = []
            for location in results['location_min']:
                (lat, lon) = location
                locations += [(round(lat, 5), round(lon, 5))]
            elevation = results['h_min']
            counter = results['counter_min']
            print('    {0!r}: {4}x {3:.2f}m at ({2}) in {1:.3f}s'
                  ''.format(source.attribution_name, duration, locations[:3],
                  elevation, counter))


if __name__ == "__main__":

    sources = [dgm200, srtm1, terr50, gebco_2019]
    with open('test_locations.json', 'r') as f:
        locations = json.loads(f.read())
    for location in locations['points']:
        label = location['label']
        lat = location['lat']
        lon = location['lon']
        results = test_height(lat, lon, sources, name=label)
    sources = [dgm200, terr50, gebco_2019, height_info]
    for location in locations['areas']:
        label = location['label']
        area = location['area']
        test_max(area, sources, label)
        test_min(area, sources, label)
