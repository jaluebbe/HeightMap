import os
import sys
import pytest
import math
sys.path.append(os.getcwd())
from height_map.terr50 import Terrain50


def test_check_for_metadata_get_height():
    terr50 = Terrain50()
    for location in [[51.499, -0.122], [51.5052, -0.1666], [51.5058, -0.1834],
                     [51.509, -0.163], [51.507, -0.179], [49.9262, -6.2979]]:
        data = terr50.get_height(*location)
        assert data['altitude_m'] != terr50.NODATA
        assert isinstance(data['source'], str)
        assert isinstance(data['attributions'], list)
        assert data['distance_m'] >= 0
        assert data['distance_m'] < 35.36
        assert isinstance(data['lat_found'], float)
        assert isinstance(data['lon_found'], float)


def test_map_bounds():
    invalid_locations = [
        [-90.1, 0], [90.1, 0], [0, -180.1], [0, 180.1], [0, 360],
    ]
    terr50 = Terrain50()
    # out of bounds
    for location in invalid_locations:
        with pytest.raises(ValueError):
            terr50.get_height(*location)


def test_content_get_height():
    terr50 = Terrain50()
    # London, River Thames
    assert math.isclose(terr50.get_height(51.499, -0.122)['altitude_m'],
        -2.3, abs_tol=4)
    # London, The Serpentine
    assert math.isclose(terr50.get_height(51.5052, -0.1666)['altitude_m'],
        14.5, abs_tol=4)
    # London, Round Pond
    assert math.isclose(terr50.get_height(51.5058, -0.1834)['altitude_m'],
        24, abs_tol=4)
    # London, Hyde Park
    assert math.isclose(terr50.get_height(51.509, -0.163)['altitude_m'],
        28.96, abs_tol=4)
    # London, Kensington Gardens
    assert math.isclose(terr50.get_height(51.507, -0.179)['altitude_m'],
        25.95, abs_tol=4)
    # Greenwich Observatory
    assert math.isclose(terr50.get_height(51.477963, -0.001647)['altitude_m'],
        38, abs_tol=4)
    # Ben Macdhui (1309m)
    assert math.isclose(terr50.get_height(57.069982, -3.670007)['altitude_m'],
        1304.6, abs_tol=4)
    # Ben Nevis (1345m)
    assert math.isclose(terr50.get_height(56.796556, -5.004599)['altitude_m'],
        1345, abs_tol=4)
    # Leinster Gardens
    assert math.isclose(terr50.get_height(51.512638, -0.183821)['altitude_m'],
        25, abs_tol=4)
    # Lochnagar (1155m)
    assert math.isclose(terr50.get_height(56.955906, -3.243050)['altitude_m'],
        1147.9, abs_tol=4)


def test_check_for_metadata_get_max_height():
    terr50 = Terrain50()
    data = terr50.get_max_height(51.5, -1, 52.5, 0)
    assert data['h_max'] != terr50.NODATA
    assert isinstance(data['h_max'], float)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_height():
    terr50 = Terrain50()
    data = terr50.get_min_height(51.5, -1, 52.5, 0)
    assert data['h_min'] != terr50.NODATA
    assert isinstance(data['h_min'], float)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_max_height():
    terr50 = Terrain50()
    data = terr50.get_min_max_height(51.5, -1, 52.5, 0)
    assert data['h_min'] != terr50.NODATA
    assert isinstance(data['h_min'], float)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert data['h_max'] != terr50.NODATA
    assert isinstance(data['h_max'], float)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_bounds_get_max_height():
    terr50 = Terrain50()
    # in bounds
    assert terr50.get_max_height(50.8, -3.1, 53, 0.8)['h_max'] != terr50.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        terr50.get_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        terr50.get_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        terr50.get_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        terr50.get_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert terr50.get_max_height(54.886907, 15.570925, 47.240591, 6.093066
                                 )['h_max'] == terr50.NODATA
    # highest location within the bounding box of the UK:
    # this is not fully covered by Terrain50
    assert terr50.get_max_height(49.96, -7.572168, 58.635, 1.681531
                                 )['h_max'] == terr50.NODATA
    # this search area should work without problems
    assert math.isclose(terr50.get_max_height(55.7, -5.6, 57.9,
        -3.9)['h_max'], 1345.4, abs_tol=4)


def test_check_bounds_get_min_height():
    terr50 = Terrain50()
    # in bounds
    assert terr50.get_min_height(50.8, -3.1, 53, 0.8)['h_min'] != terr50.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        terr50.get_min_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        terr50.get_min_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        terr50.get_min_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        terr50.get_min_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert terr50.get_min_height(54.886907, 15.570925, 47.240591, 6.093066)[
               'h_min'] == terr50.NODATA
    # search for the lowest locations in the bounding box of the UK:
    # this is not fully covered by Terrain50
    assert terr50.get_min_height(49.96, -7.572168, 58.635, 1.681531)[
               'h_min'] == terr50.NODATA
    # these search areas should work without problems
    assert math.isclose(terr50.get_min_height(55.06, -1.7, 55.12,
        -1.6)['h_min'], -24, abs_tol=4)
    assert math.isclose(terr50.get_min_height(50.8, -3.1, 53.8,
        0.1)['h_min'], -27, abs_tol=4)


def test_check_bounds_get_min_max_height():
    terr50 = Terrain50()
    # in bounds
    _result = terr50.get_min_max_height(50.8, -3.1, 53, 0.8)
    assert _result['h_max'] != terr50.NODATA
    assert _result['h_min'] != terr50.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        terr50.get_min_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        terr50.get_min_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        terr50.get_min_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        terr50.get_min_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    _result = terr50.get_min_max_height(54.8869, 15.5709, 47.2405, 6.0930)
    assert _result['h_max'] == terr50.NODATA
    assert _result['h_min'] == terr50.NODATA
    # highest and lowest locations in the bounding box of the UK:
    # this is not fully covered by Terrain50
    _result = terr50.get_min_max_height(49.96, -7.572168, 58.635, 1.681531)
    assert _result['h_max'] == terr50.NODATA
    assert _result['h_min'] == terr50.NODATA
    # these search areas should work without problems
    _result = terr50.get_min_max_height(55.7, -5.6, 57.9, -3.9)
    assert math.isclose(_result['h_max'], 1345.4, abs_tol=4)
    assert math.isclose(_result['h_min'], -12, abs_tol=4)
    # these search areas should work without problems
    _result = terr50.get_min_max_height(55.06, -1.7, 55.12, -1.6)
    assert math.isclose(_result['h_max'], 114, abs_tol=4)
    assert math.isclose(_result['h_min'], -24, abs_tol=4)
    # these search areas should work without problems
    _result = terr50.get_min_max_height(50.8, -3.1, 53.8, 0.1)
    assert math.isclose(_result['h_max'], 797, abs_tol=4)
    assert math.isclose(_result['h_min'], -27, abs_tol=4)
