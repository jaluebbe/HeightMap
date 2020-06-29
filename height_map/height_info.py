from height_map.terr50 import Terrain50
from height_map.srtm1 import Srtm1
from height_map.dgm200 import Dgm200
from height_map.gebco_2019 import Gebco2019
from height_map.cci_water_bodies_v4 import WaterBodies


class HeightInfo:
    attribution_name = 'height_info'
    NODATA = -32768

    def __init__(self):
        self.wb = WaterBodies()
        self.srtm = Srtm1()
        self.gebco = Gebco2019()
        self.dgm = Dgm200()
        self.terr50 = Terrain50()
        self.sources = [self.terr50, self.dgm, self.gebco]

    def get_height(self, lat, lon):
        """
        Get the elevation of the given location from the best available data source.

        :param lat: float -- latitude.
        :param lon: float -- longitude.
        :returns: dict
        """
        wb_label = self.wb.get_data_at_position(lat, lon)['label']
        is_ocean = wb_label == 'Ocean'
        dgm200_result = self.dgm.get_height(lat, lon)
        if dgm200_result['distance_m'] < 25 and (dgm200_result['altitude_m']
                != self.dgm.NODATA) and not is_ocean:
            # prefer sea floor bathymetry if possible
            dgm200_result['wb_label'] = wb_label
            return dgm200_result
        terr50_result = self.terr50.get_height(lat, lon)
        h_terr50 = terr50_result['altitude_m']
        if h_terr50 != self.terr50.NODATA and not is_ocean or h_terr50 > 0:
            # prefer sea floor bathymetry if possible
            terr50_result['wb_label'] = wb_label
            return terr50_result
        srtm1_result = self.srtm.get_height(lat, lon)
        h_srtm1 = srtm1_result['altitude_m']
        if h_srtm1 != self.srtm.NODATA and not is_ocean or h_srtm1 > 0:
            # prefer sea floor bathymetry if possible
            srtm1_result['wb_label'] = wb_label
            return srtm1_result
        if dgm200_result['altitude_m'] != self.dgm.NODATA and not is_ocean:
            # prefer sea floor bathymetry if possible
            dgm200_result['wb_label'] = wb_label
            return dgm200_result
        gebco_2019_result = self.gebco.get_height(lat, lon)
        if gebco_2019_result['altitude_m'] != self.gebco.NODATA:
            gebco_2019_result['wb_label'] = wb_label
            return gebco_2019_result
        else:
            return {'altitude_m': self.NODATA, 'lat': lat, 'lon': lon,
                'distance_m': 0, 'source': 'NODATA', 'wb_label': wb_label}

    def get_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {
            'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'source': self.attribution_name, 'attribution': ''}
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        for source in self.sources:
            result = source.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)
            if result['h_max'] != source.NODATA:
                return result

    def get_min_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {
            'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attribution': ''}
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        for source in self.sources:
            result = source.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)
            if result['h_min'] != source.NODATA:
                return result

    def get_min_max_height(self, lat_ll, lon_ll, lat_ur, lon_ur):
        if not (-90 <= lat_ll <= 90 and -180 <= lon_ll <= 180 and
                -90 <= lat_ur <= 90 and -180 <= lon_ur <= 180):
            raise ValueError('invalid coordinates ({}, {}), ({}, {})'.format(
                lat_ll, lon_ll, lat_ur, lon_ur))
        result = {
            'location_max': [], 'h_max': self.NODATA, 'counter_max': 0,
            'location_min': [], 'h_min': self.NODATA, 'counter_min': 0,
            'source': self.attribution_name, 'attribution': ''}
        # consider only correctly defined rectangle:
        if lat_ll > lat_ur or lon_ll > lon_ur:
            return result
        max_found = False
        min_found = False
        for source in self.sources:
            if not max_found and not min_found:
                _result = source.get_min_max_height(lat_ll, lon_ll, lat_ur,
                    lon_ur)
                min_locations = _result['location_min']
                max_locations = _result['location_max']
                min_is_ocean = [
                    self.wb.get_data_at_position(lat, lon)['label'] == 'Ocean'
                    for lat, lon in min_locations]
                max_is_ocean = [
                    self.wb.get_data_at_position(lat, lon)['label'] == 'Ocean'
                    for lat, lon in max_locations]
                if 0 < len(min_locations) < 50 and (not any(min_is_ocean) or
                        source.seabed_included):
                    min_found = True
                    _result['source_min'] = _result['source']
                if 0 < len(max_locations) < 50 and (not any(max_is_ocean) or
                        source.seabed_included):
                    max_found = True
                    _result['source_max'] = _result['source']
                if not min_found and not max_found:
                    continue
            elif not max_found:
                _result = source.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)
                max_locations = _result['location_max']
                max_is_ocean = [
                    self.wb.get_data_at_position(lat, lon)['label'] == 'Ocean'
                    for lat, lon in max_locations]
                if 0 < len(max_locations) < 50 and (not any(max_is_ocean) or
                        source.seabed_included):
                    max_found = True
                    _result['source_max'] = _result['source']
                else:
                    continue
            elif not min_found:
                _result = source.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)
                min_locations = _result['location_min']
                min_is_ocean = [
                    self.wb.get_data_at_position(lat, lon)['label'] == 'Ocean'
                    for lat, lon in min_locations]
                if 0 < len(min_locations) < 50 and (not any(min_is_ocean) or
                        source.seabed_included):
                    min_found = True
                    _result['source_min'] = _result['source']
                else:
                    continue
            else:
                break
            _result.pop('attribution')
            _result.pop('source')
            result.update(_result)
        return result
