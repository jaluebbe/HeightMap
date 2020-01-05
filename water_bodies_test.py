from height_map.cci_water_bodies_v4 import WaterBodies

if __name__ == "__main__":

    wb = WaterBodies()
    print('London, riverside:', wb.get_data_at_position(51.5, -0.12)['label'])
    print('Black Forest:', wb.get_data_at_position(47.94, 8.3)['label'])
    print('high moor in Emsland region:', wb.get_data_at_position(52.8, 7.4)['label'])
    print('Naples harbour:', wb.get_data_at_position(40.836346,14.261627)['label'])
    print('precision test:', wb.get_data_at_position(52.123456, 8.123456)['label'])
    print('Salt Lake City:', wb.get_data_at_position(40.8, -112)['label'])
    print('Tokyo:', wb.get_data_at_position(35.68, 139.77)['label'])
    print('North Sea:', wb.get_data_at_position(53.8, 6.9)['label'])
    print('storage pool in Geeste:', wb.get_data_at_position(52.588, 7.294)['label'])
    print('Dead Sea:', wb.get_data_at_position(31.516917, 35.469527)['label'])
    print('IJsselmeer:', wb.get_data_at_position(52.740013, 5.420472)['label'])
    print('Lake Constance:', wb.get_data_at_position(47.56, 9.5)['label'])
    print('Hambach open pit:', wb.get_data_at_position(50.91, 6.51)['label'])
    print('farmland in Emsland region:', wb.get_data_at_position(52.78, 7.4)['label'])
