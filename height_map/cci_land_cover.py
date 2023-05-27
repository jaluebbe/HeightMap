import os
import json
from height_map.geotiff_handler import GeoTiffHandler


class LandCover:

    attribution_url = (
        'https://cds.climate.copernicus.eu/cdsapp#!/dataset/'
        'satellite-land-cover?tab=overview')
    attribution_name = 'CCI Land Cover v2.1.1'
    attribution = '&copy <a href="{}">{}</a>'.format(attribution_url,
        attribution_name)

    def __init__(self, path=None, file_name=None):
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                'maps/cci_land_cover')
        if file_name is None:
            file_name = 'C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.tif'
        legend_file = os.path.join(path, 'cci_land_cover_legend.json')
        with open(legend_file, 'r') as f:
            self.legend = json.load(f)
        self.gth = GeoTiffHandler(os.path.join(path, file_name))

    def get_value_at_position(self, lat, lon):
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError('invalid coordinates ({}, {})'.format(lat, lon))
        return self.gth.get_value_at_position(lat, lon)

    def get_data_at_position(self, lat, lon):
        value = self.get_value_at_position(lat, lon)
        _legend = self.legend.get(str(value))
        return {
            'value': value, 'label': _legend['label'],
            'color': _legend['color'], 'source': self.attribution_name,
            'attributions': [self.attribution]}
