from osgeo import gdal, gdalconst
import struct


class GeoTiffHandler:

    def __init__(self, file_name):
        self._fmttypes = {
            gdalconst.GDT_Byte: 'B',
            gdalconst.GDT_Int16: 'h',
            gdalconst.GDT_UInt16: 'H',
            gdalconst.GDT_Int32: 'i',
            gdalconst.GDT_UInt32: 'I',
            gdalconst.GDT_Float32: 'f',
            gdalconst.GDT_Float64: 'f'
        }
        self.ds = gdal.Open(file_name, gdalconst.GA_ReadOnly)
        if self.ds is None:
            raise FileNotFoundError(file_name)
        self.geo_transform = self.ds.GetGeoTransform()
        self.cols = self.ds.RasterXSize
        self.rows = self.ds.RasterYSize
        self.bands = self.ds.RasterCount
        self.inv_geo_transform = gdal.InvGeoTransform(self.geo_transform)

    def _pt2fmt(self, pt):
        return self._fmttypes.get(pt, 'x')

    def get_value_at_position(self, lat, lon, raster_band=1):
        band = self.ds.GetRasterBand(raster_band)
        nodata_value = band.GetNoDataValue()
        fmt = self._pt2fmt(band.DataType)
        px, py = gdal.ApplyGeoTransform(self.inv_geo_transform, lon, lat)
        px = int(px)
        py = int(py)
        if px == self.cols:
            px -= 1
        if py == self.rows:
            py -= 1
        if px > self.cols or py > self.rows or px < 0 or py < 0:
            if fmt == 'f':
                return float('nan')
            else:
                return None
        structval = band.ReadRaster(px, py, 1, 1,
            buf_type=band.DataType)
        value = struct.unpack(fmt, structval)
        if value[0] == nodata_value:
            if fmt == 'f':
                return float('nan')
            else:
                return None
        else:
            return value[0]

    def get_values_at_position(self, lat, lon):
        results = []
        for raster_band in range(1, self.bands+1):
            results.append(self.get_value_at_position(lat, lon, raster_band))
        return results
