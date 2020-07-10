import os
import sys
sys.path.append(os.getcwd())
import pytest
from height_map.cci_land_cover import LandCover


def test_missing_file_operation():
    with pytest.raises(FileNotFoundError):
        lc = LandCover(file_name='missing_file.tif')
    with pytest.raises(FileNotFoundError):
        lc = LandCover(path='non_existent_path')

def test_check_for_metadata():
    lc = LandCover()
    for _location in [[53.8, 6.9], [47.56, 9.5], [47.94, 8.3]]:
        data = lc.get_data_at_position(*_location)
        assert data['value'] in [210, 70, 2]
        assert data['label'] in [
            'Water bodies',
            'Tree cover, needleleaved, evergreen, closed to open (>15%)',
            'Water']
        assert isinstance(data['color'], list)
        assert len(data['color']) == 3
        assert isinstance(data['source'], str)
        assert isinstance(data['attributions'], list)

def test_map_bounds():
    lc = LandCover()
    # North Pole
    assert lc.get_data_at_position(90, -180)['label'] is not None
    assert lc.get_data_at_position(90, 0)['label'] is not None
    assert lc.get_data_at_position(90, 180)['label'] is not None
    assert lc.get_data_at_position(90, 179)['label'] is not None
    # Equator
    assert lc.get_data_at_position(0, -180)['label'] is not None
    assert lc.get_data_at_position(0, 0)['label'] is not None
    assert lc.get_data_at_position(0, 180)['label'] is not None
    # South Pole
    assert lc.get_data_at_position(-90, -180)['label'] is not None
    assert lc.get_data_at_position(-89.9999, 0)['label'] is not None
    assert lc.get_data_at_position(-90, 0)['label'] is not None
    assert lc.get_data_at_position(-90, 180)['label'] is not None
    # out of bounds
    with pytest.raises(ValueError):
        lc.get_data_at_position(-90.1, 0)
    with pytest.raises(ValueError):
        lc.get_data_at_position(0, -180.1)
    with pytest.raises(ValueError):
        lc.get_data_at_position(0, 180.1)
    with pytest.raises(ValueError):
        lc.get_data_at_position(0, 360)

def test_content():
    lc = LandCover()
    # Hambach open pit
    assert lc.get_data_at_position(50.91, 6.51)['value'] == 150
    # storage pool in Geeste
    assert lc.get_data_at_position(52.588, 7.294)['value'] == 210
    # London, River Thames
    assert lc.get_data_at_position(51.499, -0.1225)['value'] == 210
    # London, The Serpentine
    assert lc.get_data_at_position(51.5052, -0.1666)['value'] == 210
    # London, Hyde Park
    assert lc.get_data_at_position(51.509, -0.163)['value'] == 11
    # London, Kensington Gardens
    assert lc.get_data_at_position(51.507, -0.179)['value'] == 70
    # North Sea
    assert lc.get_data_at_position(53.8, 6.9)['value'] == 210
    # Dead Sea
    assert lc.get_data_at_position(31.52, 35.48)['value'] == 210
    # IJsselmeer
    assert lc.get_data_at_position(52.74, 5.42)['value'] == 210
    # Markermeer
    assert lc.get_data_at_position(52.54, 5.22)['value'] == 210
    # Naples harbour
    assert lc.get_data_at_position(40.836, 14.262)['value'] == 210
    # Lake Constance
    assert lc.get_data_at_position(47.56, 9.5)['value'] == 210
    # Black Forest
    assert lc.get_data_at_position(47.94, 8.3)['value'] == 70
    # farmland in the Emsland region
    assert lc.get_data_at_position(52.78, 7.4)['value'] == 11
    # high moor in the Emsland region
    assert lc.get_data_at_position(52.8, 7.4)['value'] == 180
    # Salt Lake City
    assert lc.get_data_at_position(40.8, -112)['value'] == 100
    # Tokyo
    assert lc.get_data_at_position(35.68, 139.77)['value'] == 190
