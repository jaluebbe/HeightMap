import os
import sys
import pytest
import math
sys.path.append(os.getcwd())
from height_map.srtm1 import Srtm1


def test_check_for_metadata_get_height():
    srtm = Srtm1()
    for location in [[51.499, -0.122], [51.5052, -0.1666], [51.5058, -0.1834],
                     [51.509, -0.163], [51.507, -0.179], [49.9262, -6.2979]]:
        data = srtm.get_height(*location)
        assert data['altitude_m'] != srtm.NODATA
        assert isinstance(data['source'], str)
        assert isinstance(data['attributions'], list)
        assert data['distance_m'] >= 0
        assert data['distance_m'] < 21.22
        assert isinstance(data['lat_found'], float)
        assert isinstance(data['lon_found'], float)


def test_map_bounds():
    invalid_locations = [
        [-90.1, 0], [90.1, 0], [0, -180.1], [0, 180.1], [0, 360],
    ]
    srtm = Srtm1()
    # out of bounds
    for location in invalid_locations:
        with pytest.raises(ValueError):
            srtm.get_height(*location)


def test_content_get_height():
    srtm = Srtm1()
    # London, River Thames
    assert math.isclose(srtm.get_height(51.499, -0.122)['altitude_m'],
        -2.3, abs_tol=16)
    # London, The Serpentine
    assert math.isclose(srtm.get_height(51.5052, -0.1666)['altitude_m'],
        14.5, abs_tol=16)
    # London, Round Pond
    assert math.isclose(srtm.get_height(51.5058, -0.1834)['altitude_m'],
        24, abs_tol=16)
    # London, Hyde Park
    assert math.isclose(srtm.get_height(51.509, -0.163)['altitude_m'],
        28.96, abs_tol=16)
    # London, Kensington Gardens
    assert math.isclose(srtm.get_height(51.507, -0.179)['altitude_m'],
        25.95, abs_tol=16)
    # Greenwich Observatory
    assert math.isclose(srtm.get_height(51.477963, -0.001647)['altitude_m'],
        38, abs_tol=16)
    # Ben Macdhui (1309m)
    assert math.isclose(srtm.get_height(57.069982, -3.670007)['altitude_m'],
        1304.6, abs_tol=16)
    # Ben Nevis (1345m)
    assert math.isclose(srtm.get_height(56.796556, -5.004599)['altitude_m'],
        1311, abs_tol=16)
    # Leinster Gardens
    assert math.isclose(srtm.get_height(51.512638, -0.183821)['altitude_m'],
        25, abs_tol=16)
    # Lochnagar (1155m)
    assert math.isclose(srtm.get_height(56.955906, -3.243050)['altitude_m'],
        1147.9, abs_tol=16)
    # Hambach open pit
    assert math.isclose(srtm.get_height(50.91, 6.51)['altitude_m'], -43,
        abs_tol=16)
    # storage pool in Geeste
    assert math.isclose(srtm.get_height(52.588, 7.294)['altitude_m'], 34,
        abs_tol=16)
    # Black Forest
    assert math.isclose(srtm.get_height(47.94, 8.3)['altitude_m'], 927.52,
        abs_tol=16)
    # farmland in the Emsland region
    assert math.isclose(srtm.get_height(52.78, 7.4)['altitude_m'], 32.61,
        abs_tol=16)
    # high moor in the Emsland region
    assert math.isclose(srtm.get_height(52.8, 7.4)['altitude_m'], 24.64,
        abs_tol=16)
    # lowest location in Germany
    assert math.isclose(srtm.get_height(50.918611, 6.551388)['altitude_m'],
        -299, abs_tol=16)
    # highest location in Germany
    assert math.isclose(srtm.get_height(47.422239, 10.986123)['altitude_m'],
        2770, abs_tol=16)


def test_check_for_metadata_get_max_height():
    srtm = Srtm1()
    data = srtm.get_max_height(51.9, -0.1, 52.1, 0)
    assert data['h_max'] != srtm.NODATA
    assert isinstance(data['h_max'], int)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_height():
    srtm = Srtm1()
    data = srtm.get_min_height(51.9, -0.1, 52.1, 0)
    assert data['h_min'] != srtm.NODATA
    assert isinstance(data['h_min'], int)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_max_height():
    srtm = Srtm1()
    data = srtm.get_min_max_height(51.9, -0.1, 52.1, 0)
    assert data['h_min'] != srtm.NODATA
    assert isinstance(data['h_min'], int)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert data['h_max'] != srtm.NODATA
    assert isinstance(data['h_max'], int)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_bounds_get_max_height():
    srtm = Srtm1()
    # in bounds
    assert srtm.get_max_height(50.8, -3.1, 53, -3)['h_max'] != srtm.NODATA
    assert srtm.get_max_height(50.8, 0.7, 53, 0.8)['h_max'] != srtm.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        srtm.get_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        srtm.get_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        srtm.get_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        srtm.get_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert srtm.get_max_height(54.886907, 15.570925, 47.240591, 6.093066
                               )['h_max'] == srtm.NODATA
    # highest location within the bounding box of the UK:
    # this is not fully covered by SRTM1
    assert srtm.get_max_height(49.96, -7.572168, 58.635, 1.681531
                               )['h_max'] == srtm.NODATA
    # these search areas should work without problems
    assert math.isclose(srtm.get_max_height(55.7, -5.05, 57.9,
        -4.95)['h_max'], 1345.4, abs_tol=16)
    assert math.isclose(srtm.get_max_height(56.65, -5.6, 56.85,
        -3.9)['h_max'], 1345.4, abs_tol=16)


def test_check_bounds_get_min_height():
    srtm = Srtm1()
    # in bounds
    assert srtm.get_min_height(50.8, -3.1, 53, -3)['h_min'] != srtm.NODATA
    assert srtm.get_min_height(50.8, 0.7, 53, 0.8)['h_min'] != srtm.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        srtm.get_min_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        srtm.get_min_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        srtm.get_min_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        srtm.get_min_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert srtm.get_min_height(54.886907, 15.570925, 47.240591, 6.093066)[
               'h_min'] == srtm.NODATA
    # search for the lowest locations in the bounding box of the UK:
    # this is not fully covered by SRTM1
    assert srtm.get_min_height(49.96, -7.572168, 58.635, 1.681531)[
               'h_min'] == srtm.NODATA


def test_check_bounds_get_min_max_height():
    srtm = Srtm1()
    # in bounds
    _result = srtm.get_min_max_height(50.8, -3.1, 53, -3)
    assert _result['h_max'] != srtm.NODATA
    assert _result['h_min'] != srtm.NODATA
    _result = srtm.get_min_max_height(50.8, 0.7, 53, 0.8)
    assert _result['h_max'] != srtm.NODATA
    assert _result['h_min'] != srtm.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        srtm.get_min_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        srtm.get_min_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        srtm.get_min_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        srtm.get_min_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    _result = srtm.get_min_max_height(54.8869, 15.5709, 47.2405, 6.0930)
    assert _result['h_max'] == srtm.NODATA
    assert _result['h_min'] == srtm.NODATA
    # highest and lowest locations in the bounding box of the UK:
    # this is not fully covered by SRTM1
    _result = srtm.get_min_max_height(49.96, -7.572168, 58.635, 1.681531)
    assert _result['h_max'] == srtm.NODATA
    assert _result['h_min'] == srtm.NODATA
    # these search areas should work without problems
    _result = srtm.get_min_max_height(55.7, -5.05, 57.9, -4.95)
    assert math.isclose(_result['h_max'], 1345.4, abs_tol=16)
    assert math.isclose(_result['h_min'], -12, abs_tol=16)
    _result = srtm.get_min_max_height(56.65, -5.6, 56.85, -3.9)
    assert math.isclose(_result['h_max'], 1345.4, abs_tol=16)
    assert math.isclose(_result['h_min'], -12, abs_tol=16)
