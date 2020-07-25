import os
from height_map.geotiff_handler import GeoTiffHandler


class WaterBodies:

    attribution_url = 'https://www.mdpi.com/2072-4292/9/1/36'
    attribution_name = 'CCI Water Bodies v4.0'
    attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
        attribution_name)

    def __init__(self, path=None, file_name=None):
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'maps/cci_wb4')
        if file_name is None:
            file_name = 'ESACCI-LC-L4-WB-Ocean-Land-Map-150m-P13Y-2000-v4.0.tif'
        self.gth = GeoTiffHandler(os.path.join(path, file_name))
        self.legend = {'0': 'Ocean', '1': 'Land', '2': 'Water'}

    def get_value_at_position(self, lat, lon):
        return self.gth.get_value_at_position(lat, lon)

    def get_data_at_position(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        value = self.get_value_at_position(lat, lon)
        return {
            'value': value, 'label': self.legend.get(str(value)),
            'source': self.attribution_name, 'attributions': [self.attribution]}
