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
        assert isinstance(data['attributions'], list)
        assert data['distance_m'] >= 0
        assert data['distance_m'] < 282.9
        assert isinstance(data['lat_found'], float)
        assert isinstance(data['lon_found'], float)


def test_map_bounds_get_height():
    locations_off_coverage = [
        # North Pole
        [90, -180], [90, 0], [90, 180], [90, 179],
        # Equator
        [0, -180], [0, 0], [0, 180],
        # South Pole
        [-90, -180], [-90, 0], [-90, 180],
        # lower left limit
        [47.239659, 6.091796],
        # lower right limit
        [47.141612, 14.556905],
        # upper right limit
        [54.887716, 15.572619],
        # upper left limit
        [55.016964, 5.557084],
        # lower left
        [47.240591, 6.093066],
        # upper right
        [54.886907, 15.570925],
    ]
    invalid_locations = [
        [-90.1, 0], [90.1, 0], [0, -180.1], [0, 180.1], [0, 360],
    ]
    locations_in_coverage = [
        # min height
        [50.925084, 6.529813],
        # max height
        [47.422239, 10.986123],
        # locations in Germany
        [53.57, 9.98], [52.51, 13.42], [47.94, 8.3],
    ]
    dgm = Dgm200()
    # locations off dgm200 coverage
    for location in locations_off_coverage:
        assert dgm.get_height(*location)['altitude_m'] == dgm.NODATA
    # invalid coordinates
    for location in invalid_locations:
        with pytest.raises(ValueError):
            dgm.get_height(*location)
    # locations in dgm200 coverage
    for location in locations_in_coverage:
        assert dgm.get_height(*location)['altitude_m'] != dgm.NODATA


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
    assert isinstance(data['attributions'], list)


def test_check_for_metadata_get_min_height():
    dgm = Dgm200()
    data = dgm.get_min_height(51, 7, 52, 8)
    assert data['h_min'] != dgm.NODATA
    assert isinstance(data['h_min'], float)
    assert isinstance(data['location_min'], list)
    assert data['counter_min'] >= 0
    assert isinstance(data['source'], str)
    assert isinstance(data['attributions'], list)


def test_check_bounds_get_max_height():
    dgm = Dgm200()
    # out of bounds
    assert dgm.get_max_height(52.5, 5, 53, 5.5)['h_max'] == dgm.NODATA
    # invalid coordinates
    with pytest.raises(ValueError):
        dgm.get_max_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        dgm.get_max_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        dgm.get_max_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        dgm.get_max_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert dgm.get_max_height(54.886907, 15.570925, 47.240591, 6.093066
                              )['h_max'] == dgm.NODATA
    # highest location
    assert math.isclose(dgm.get_max_height(47.240591, 6.093066, 54.886907,
        15.570925)['h_max'], 2920.32, abs_tol=10)


def test_check_bounds_get_min_height():
    dgm = Dgm200()
    # out of bounds
    assert dgm.get_min_height(52.5, 5, 53, 5.5)['h_min'] == dgm.NODATA
    # invalid coordinates, expect ValueError
    with pytest.raises(ValueError):
        dgm.get_min_height(52.5, 5, 91, 5.5)
    with pytest.raises(ValueError):
        dgm.get_min_height(-91, 5, 53, 5.5)
    with pytest.raises(ValueError):
        dgm.get_min_height(52.5, -181, 53, 5.5)
    with pytest.raises(ValueError):
        dgm.get_min_height(52.5, 5, 53, 181)
    # incorrect rectangle
    assert dgm.get_min_height(54.886907, 15.570925, 47.240591, 6.093066
                              )['h_min'] == dgm.NODATA
    # lowest location
    assert math.isclose(dgm.get_min_height(47.240591, 6.093066, 54.886907,
        15.570925)['h_min'], -265.5, abs_tol=10)
