import os
import sys
import pytest
import math
sys.path.append(os.getcwd())
from height_map.gebco import Gebco


def test_missing_file_operation():
    with pytest.raises(FileNotFoundError):
        Gebco(file_name='missing_file.tif')
    with pytest.raises(FileNotFoundError):
        Gebco(path='non_existent_path')


def test_check_for_metadata_get_height():
    gebco = Gebco()
    for location in [[53.57, 9.98], [52.51, 13.42], [47.94, 8.3], [-41, 172]]:
        data = gebco.get_height(*location)
        assert data['altitude_m'] != gebco.NODATA
        assert isinstance(data['source'], str)
        assert isinstance(data['attributions'], list)
        assert data['distance_m'] >= 0
        assert data['distance_m'] < 654.86
        assert isinstance(data['lat_found'], float)
        assert isinstance(data['lon_found'], float)


def test_map_bounds():
    locations = [
        # North Pole
        [90, -180], [90, 0], [90, 180], [90, 179],
        # Equator
        [0, -180], [0, 0], [0, 180],
        # South Pole
        [-90, -180], [-90, 0], [-90, 180]
    ]
    invalid_locations = [
        [-90.1, 0], [90.1, 0], [0, -180.1], [0, 180.1], [0, 360],
    ]
    gebco = Gebco()
    for location in locations:
        assert gebco.get_height(*location)['altitude_m'] != gebco.NODATA
    # out of bounds
    for location in invalid_locations:
        with pytest.raises(ValueError):
            gebco.get_height(*location)


def test_content_get_height():
    gebco = Gebco()
    # Hambach open pit
    assert math.isclose(gebco.get_height(50.91, 6.51)['altitude_m'], -94.83,
        abs_tol=16)
    # storage pool in Geeste
    assert math.isclose(gebco.get_height(52.588, 7.294)['altitude_m'], 34,
        abs_tol=16)
    # Black Forest
    assert math.isclose(gebco.get_height(47.94, 8.3)['altitude_m'], 927.52,
        abs_tol=16)
    # farmland in the Emsland region
    assert math.isclose(gebco.get_height(52.78, 7.4)['altitude_m'], 32.61,
        abs_tol=16)
    # high moor in the Emsland region
    assert math.isclose(gebco.get_height(52.8, 7.4)['altitude_m'], 24.64,
        abs_tol=16)
    # lowest location of this dataset in Germany
    assert math.isclose(gebco.get_height(50.92, 6.5)['altitude_m'],
        -192.2, abs_tol=16)
    # surface mine in Belgium
    assert math.isclose(gebco.get_height(50.604167, 3.479167)['altitude_m'],
        -87, abs_tol=16)
    # highest location of this dataset in the bounding box of Germany
    assert math.isclose(gebco.get_height(47.420833, 13.0625)['altitude_m'],
        2818.2, abs_tol=16)
    # lowest location
    assert math.isclose(gebco.get_height(11.366667, 142.5875)['altitude_m'],
        -10928, abs_tol=16)
    # highest location
    assert math.isclose(gebco.get_height(27.9875, 86.925)['altitude_m'],
        8613.2, abs_tol=16)
    # London, River Thames
    assert math.isclose(gebco.get_height(51.499, -0.122)['altitude_m'],
        6.98, abs_tol=16)
    # London, The Serpentine
    assert math.isclose(gebco.get_height(51.5052, -0.1666)['altitude_m'],
        20.96, abs_tol=16)
    # London, Round Pond
    assert math.isclose(gebco.get_height(51.5058, -0.1834)['altitude_m'],
        28.96, abs_tol=16)
    # London, Hyde Park
    assert math.isclose(gebco.get_height(51.509, -0.163)['altitude_m'],
        28.96, abs_tol=16)
    # London, Kensington Gardens
    assert math.isclose(gebco.get_height(51.507, -0.179)['altitude_m'],
        25.95, abs_tol=16)
    # North Sea
    assert math.isclose(gebco.get_height(53.8, 6.9)['altitude_m'],
        -22.04, abs_tol=16)
    # Dead Sea
    assert math.isclose(gebco.get_height(31.52, 35.48)['altitude_m'],
        -415, abs_tol=16)
    # IJsselmeer
    assert math.isclose(gebco.get_height(52.74, 5.42)['altitude_m'],
        -4.28, abs_tol=16)
    # Markermeer
    assert math.isclose(gebco.get_height(52.54, 5.22)['altitude_m'],
        -3.89, abs_tol=16)
    # Naples harbour
    assert math.isclose(gebco.get_height(40.836, 14.262)['altitude_m'],
        -14.21, abs_tol=16)
    # Lake Constance
    assert math.isclose(gebco.get_height(47.56, 9.5)['altitude_m'],
        392, abs_tol=16)
    # Salt Lake City
    assert math.isclose(gebco.get_height(40.8, -112)['altitude_m'],
        1289.59, abs_tol=16)
    # Tokyo
    assert math.isclose(gebco.get_height(35.68, 139.77)['altitude_m'],
        20.31, abs_tol=16)


def test_check_for_metadata_get_max_height():
    gebco = Gebco()
    data = gebco.get_max_height(51, 7, 52, 8)
    assert data['h_max'] != gebco.NODATA
    assert isinstance(data['h_max'], float)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_height():
    gebco = Gebco()
    data = gebco.get_min_height(51, 7, 52, 8)
    assert data['h_min'] != gebco.NODATA
    assert isinstance(data['h_min'], float)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_max_height():
    gebco = Gebco()
    data = gebco.get_min_max_height(51, 7, 52, 8)
    assert data['h_min'] != gebco.NODATA
    assert isinstance(data['h_min'], float)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert data['h_max'] != gebco.NODATA
    assert isinstance(data['h_max'], float)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_bounds_get_max_height():
    gebco = Gebco()
    # in bounds
    assert gebco.get_max_height(52.5, 5, 53, 5.5)['h_max'] != gebco.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        gebco.get_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        gebco.get_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        gebco.get_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        gebco.get_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert gebco.get_max_height(54.886907, 15.570925, 47.240591, 6.093066
                                )['h_max'] == gebco.NODATA
    # highest location in the bounding box of Germany
    assert math.isclose(gebco.get_max_height(47.240591, 6.093066, 54.886907,
        15.570925)['h_max'], 2818.2, abs_tol=16)
    # highest location of the world
    assert math.isclose(gebco.get_max_height(-90, -180, 90, 180)['h_max'],
        8613.2, abs_tol=16)


def test_check_bounds_get_min_height():
    gebco = Gebco()
    # in bounds
    assert gebco.get_min_height(52.5, 5, 53, 5.5)['h_min'] != gebco.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        gebco.get_min_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        gebco.get_min_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        gebco.get_min_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        gebco.get_min_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert gebco.get_min_height(54.886907, 15.570925, 47.240591, 6.093066
                                )['h_min'] == gebco.NODATA
    # lowest location in the bounding box of Germany
    assert math.isclose(gebco.get_min_height(47.240591, 6.093066, 54.886907,
        15.570925)['h_min'], -195.2, abs_tol=16)
    # lowest location of the world
    assert math.isclose(gebco.get_min_height(-90, -180, 90, 180)['h_min'],
        -10928, abs_tol=16)

def test_check_bounds_get_min_max_height():
    gebco = Gebco()
    # in bounds
    _result = gebco.get_min_max_height(52.5, 5, 53, 5.5)
    assert _result['h_max'] != gebco.NODATA
    assert _result['h_min'] != gebco.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        gebco.get_min_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        gebco.get_min_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        gebco.get_min_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        gebco.get_min_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    _result = gebco.get_min_max_height(54.886907, 15.570925, 47.240591,
        6.093066)
    assert _result['h_max'] == gebco.NODATA
    assert _result['h_min'] == gebco.NODATA
    # highest and lowest location in the bounding box of Germany
    _result = gebco.get_min_max_height(47.240591, 6.093066, 54.886907,
        15.570925)
    assert math.isclose(_result['h_max'], 2818.2, abs_tol=16)
    assert math.isclose(_result['h_min'], -195.2, abs_tol=16)
    # highest and lowest location of the world
    _result = gebco.get_min_max_height(-90, -180, 90, 180)
    assert math.isclose(_result['h_max'], 8613.2, abs_tol=16)
    assert math.isclose(_result['h_min'], -10928, abs_tol=16)
