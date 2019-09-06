# HeightMap

## Data Sources

DGM200 (Germany, 200m grid):

Put http://sg.geodatenzentrum.de/web_download/dgm/dgm200/utm32s/gridascii/dgm200.utm32s.gridascii.zip to downloads/ and call dgm200_grid_conversion.py .

OS Terrain 50 (UK, 50m grid, registration required):

Download ASCII Grid version of OS Terrain 50 from
https://www.ordnancesurvey.co.uk/business-and-government/products/terrain-50.html , put the content to downloads/ and call terr50_data_conversion.py .
SRTM (tiles of each 1 arc minute coverage with 30m resolution, registration required):

Download required tiles from https://dwtkns.com/srtm30m/ , unpack and put them to height_map/maps/srtm1/
EARTH2014

world wide coverage of ocean and terrain with 1 arc minute resolution, could be replaced by GEBCO_2019:

Put http://ddfe.curtin.edu.au/models/Earth2014/data_1min/topo_grids/Earth2014.BED2014.1min.geod.bin to height_map/maps/earth2014/ .
GEBCO_2019

world wide coverage of ocean and terrain with 15 arc-second resolution:
https://www.gebco.net/data_and_products/gridded_bathymetry_data/

Download the global GEBCO_2019_Grid in netCDF format (12GB), unpack it and put GEBCO_2019.nc to height_map/maps/gebco_2019/ .
