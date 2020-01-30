import os
import sys
sys.path.append(os.getcwd())
import pytest
from height_map.cci_water_bodies_v4 import WaterBodies


def test_missing_file_operation():
    with pytest.raises(FileNotFoundError):
        wb = WaterBodies(file_name='missing_file.tif')
    with pytest.raises(FileNotFoundError):
        wb = WaterBodies(path='non_existent_path')

def test_map_bounds():
    wb = WaterBodies()
    # North Pole
    assert wb.get_data_at_position(90, -180)['label'] is not None
    assert wb.get_data_at_position(90, 0)['label'] is not None
    assert wb.get_data_at_position(90, 180)['label'] is not None
    assert wb.get_data_at_position(90, 179)['label'] is not None
    # Equator
    assert wb.get_data_at_position(0, -180)['label'] is not None
    assert wb.get_data_at_position(0, 0)['label'] is not None
    assert wb.get_data_at_position(0, 180)['label'] is not None
    # South Pole
    assert wb.get_data_at_position(-90, -180)['label'] is not None
    assert wb.get_data_at_position(-89.9999, 0)['label'] is not None
    assert wb.get_data_at_position(-90, 0)['label'] is not None
    assert wb.get_data_at_position(-90, 180)['label'] is not None
    # out of bounds
    assert wb.get_data_at_position(-90.1, 0)['label'] is None
    assert wb.get_data_at_position(90.1, 0)['label'] is None
    assert wb.get_data_at_position(0, -180.1)['label'] is None
    assert wb.get_data_at_position(0, 180.1)['label'] is None
    assert wb.get_data_at_position(0, 360)['label'] is None


def test_content():
    wb = WaterBodies()
    # Hambach open pit
    assert wb.get_data_at_position(50.91, 6.51)['label'] == 'Land'
    # storage poll in Geeste
    assert wb.get_data_at_position(52.588, 7.294)['label'] == 'Water'
    # London, River Thames
    assert wb.get_data_at_position(51.499, -0.122)['label'] == 'Water'
    # London, The Serpentine
    assert wb.get_data_at_position(51.5052, -0.1666)['label'] == 'Water'
    # London, Round Pond
    assert wb.get_data_at_position(51.5058, -0.1834)['label'] == 'Water'
    # London, Hyde Park
    assert wb.get_data_at_position(51.509, -0.163)['label'] == 'Land'
    # London, Kensington Gardens
    assert wb.get_data_at_position(51.507, -0.179)['label'] == 'Land'
    # North Sea
    assert wb.get_data_at_position(53.8, 6.9)['label'] == 'Ocean'
    # Dead Sea
    assert wb.get_data_at_position(31.52, 35.48)['label'] == 'Water'
    # IJsselmeer
    assert wb.get_data_at_position(52.74, 5.42)['label'] in ['Water', 'Ocean']
    # Markermeer
    assert wb.get_data_at_position(52.54, 5.22)['label'] in ['Water', 'Ocean']
    # Naples harbour
    assert wb.get_data_at_position(40.836, 14.262)['label'] == 'Ocean'
    # Lake Constance
    assert wb.get_data_at_position(47.56, 9.5)['label'] == 'Water'
    # Black Forest
    assert wb.get_data_at_position(47.94, 8.3)['label'] == 'Land'
    # farmland in the Emsland region
    assert wb.get_data_at_position(52.78, 7.4)['label'] == 'Land'
    # high moor in the Emsland region
    assert wb.get_data_at_position(52.8, 7.4)['label'] == 'Land'
    # Salt Lake City
    assert wb.get_data_at_position(40.8, -112)['label'] == 'Land'
    # Tokyo
    assert wb.get_data_at_position(35.68, 139.77)['label'] == 'Land'
