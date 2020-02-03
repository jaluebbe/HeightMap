import os
import sys
import pytest
import math
sys.path.append(os.getcwd())
from height_map.dgm200 import Dgm200
from height_map.dgm200 import calculate_distance


def test_calculate_distance():
    assert math.isclose(calculate_distance(50.925084, 6.529813, 47.422239,
        10.986123), 506340.755, abs_tol=0.001)


def test_missing_file_operation():
    with pytest.raises(FileNotFoundError):
        Dgm200(file_name='missing_file.tif')
    with pytest.raises(FileNotFoundError):
        Dgm200(path='non_existent_path')


def test_check_for_metadata_get_height():
    dgm = Dgm200()
    for _location in [[53.57, 9.98], [52.51, 13.42], [47.94, 8.3]]:
        data = dgm.get_height(*_location)
        assert data['altitude_m'] != dgm.NODATA
        assert isinstance(data['source'], str)
        assert isinstance(data['attribution'], str)
        assert data['distance_m'] >= 0
        assert data['distance_m'] < 282.9
        assert isinstance(data['lat_found'], float)
        assert isinstance(data['lon_found'], float)


def test_map_bounds_get_height():
    dgm = Dgm200()
    # North Pole
    assert dgm.get_height(90, -180)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(90, 0)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(90, 180)['altitude_m'] == dgm.NODATA
    # Equator
    assert dgm.get_height(0, -180)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(0, 0)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(0, 180)['altitude_m'] == dgm.NODATA
    # South Pole
    assert dgm.get_height(-90, -180)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(-90, 0)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(-90, 180)['altitude_m'] == dgm.NODATA
    # invalid coordinates
    assert dgm.get_height(0, -181)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(0, 181)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(-91, 0)['altitude_m'] == dgm.NODATA
    assert dgm.get_height(91, 0)['altitude_m'] == dgm.NODATA
    # out of bounds
    # lower left limit
    assert dgm.get_height(47.239659, 6.091796)['altitude_m'] == dgm.NODATA
    # lower right limit
    assert dgm.get_height(47.141612, 14.556905)['altitude_m'] == dgm.NODATA
    # upper right limit
    assert dgm.get_height(54.887716, 15.572619)['altitude_m'] == dgm.NODATA
    # upper left limit
    assert dgm.get_height(55.016964, 5.557084)['altitude_m'] == dgm.NODATA
    # lower left
    assert dgm.get_height(47.240591, 6.093066)['altitude_m'] == dgm.NODATA
    # upper right
    assert dgm.get_height(54.886907, 15.570925)['altitude_m'] == dgm.NODATA
    # min height
    assert dgm.get_height(50.925084, 6.529813)['altitude_m'] != dgm.NODATA
    # max height
    assert dgm.get_height(47.422239, 10.986123)['altitude_m'] != dgm.NODATA
    # locations in Germany
    for _location in [[53.57, 9.98], [52.51, 13.42], [47.94, 8.3]]:
        assert dgm.get_height(*_location)['altitude_m'] != dgm.NODATA


def test_content_get_height():
    dgm = Dgm200()
    # Hambach open pit
    assert math.isclose(dgm.get_height(50.91, 6.51)['altitude_m'], -94.83,
        abs_tol=10)
    # storage pool in Geeste
    assert math.isclose(dgm.get_height(52.588, 7.294)['altitude_m'], 34,
        abs_tol=2)
    # Black Forest
    assert math.isclose(dgm.get_height(47.94, 8.3)['altitude_m'], 927.52,
        abs_tol=10)
    # farmland in the Emsland region
    assert math.isclose(dgm.get_height(52.78, 7.4)['altitude_m'], 32.61,
        abs_tol=10)
    # high moor in the Emsland region
    assert math.isclose(dgm.get_height(52.8, 7.4)['altitude_m'], 24.64,
        abs_tol=10)
    # lowest location
    assert math.isclose(dgm.get_height(50.925084, 6.529813)['altitude_m'],
        -265.5, abs_tol=10)
    # highest location
    assert math.isclose(dgm.get_height(47.422239, 10.986123)['altitude_m'],
        2920.32, abs_tol=10)


def test_check_for_metadata_get_max_height():
    dgm = Dgm200()
    data = dgm.get_max_height(51, 7, 52, 8)
    assert data['h_max'] != dgm.NODATA
    assert isinstance(data['h_max'], float)
    assert isinstance(data['location_max'], list)
    assert data['counter_max'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attribution'], str)


def test_check_for_metadata_get_min_height():
    dgm = Dgm200()
    data = dgm.get_min_height(51, 7, 52, 8)
    assert data['h_min'] != dgm.NODATA
    assert isinstance(data['h_min'], float)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attribution'], str)


def test_check_bounds_get_max_height():
    dgm = Dgm200()
    # out of bounds
    assert dgm.get_max_height(52.5, 5, 53, 5.5)['h_max'] == dgm.NODATA
    # invalid coordinates
    assert dgm.get_max_height(52.5, 5, 91, 5.5)['h_max'] == dgm.NODATA
    assert dgm.get_max_height(-91, 5, 53, 5.5)['h_max'] == dgm.NODATA
    assert dgm.get_max_height(52.5, -181, 53, 5.5)['h_max'] == dgm.NODATA
    assert dgm.get_max_height(52.5, 5, 53, 181)['h_max'] == dgm.NODATA
    # highest location
    assert math.isclose(dgm.get_max_height(47.240591, 6.093066, 54.886907,
        15.570925)['h_max'], 2920.32, abs_tol=10)


def test_check_bounds_get_min_height():
    dgm = Dgm200()
    # out of bounds
    assert dgm.get_min_height(52.5, 5, 53, 5.5)['h_min'] == dgm.NODATA
    # invalid coordinates
    assert dgm.get_min_height(52.5, 5, 91, 5.5)['h_min'] == dgm.NODATA
    assert dgm.get_min_height(-91, 5, 53, 5.5)['h_min'] == dgm.NODATA
    assert dgm.get_min_height(52.5, -181, 53, 5.5)['h_min'] == dgm.NODATA
    assert dgm.get_min_height(52.5, 5, 53, 181)['h_min'] == dgm.NODATA
    # lowest location
    assert math.isclose(dgm.get_min_height(47.240591, 6.093066, 54.886907,
        15.570925)['h_min'], -265.5, abs_tol=10)
