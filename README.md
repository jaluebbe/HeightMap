# HeightMap

## Data Sources

### DGM200 (Germany, 200m grid):

https://www.bkg.bund.de/EN/Home/home.html

Put http://sg.geodatenzentrum.de/web_download/dgm/dgm200/utm32s/gridascii/dgm200.utm32s.gridascii.zip to downloads/ and call dgm200_grid_conversion.py .

### OS Terrain 50 (UK, 50m grid, registration required):

Download ASCII Grid version of OS Terrain 50 from
https://www.ordnancesurvey.co.uk/business-and-government/products/terrain-50.html to downloads/ and call terr50_data_conversion.py .

### SRTM (tiles of each 1 arc minute coverage with 30m resolution, registration required):

https://lpdaac.usgs.gov/products/srtmgl1v003/

Download required tiles from https://dwtkns.com/srtm30m/ , unpack and put them to height_map/maps/srtm1/

### World wide coverage of ocean and terrain

Select one of the following data sources for world wide coverage of ocean and terrain. GEBCO_2019 is the more recent dataset with higher resolution than Earth 2014 but consumes a lot of memory on disk.

#### Earth 2014 

1 arc-minute resolution. Values are 16bit integer. File size approximately 467 MB.

http://ddfe.curtin.edu.au/models/Earth2014/

Put http://ddfe.curtin.edu.au/models/Earth2014/data_1min/topo_grids/Earth2014.TBI2014.1min.geod.bin to height_map/maps/earth2014/ .

#### GEBCO_2019

15 arc-second resolution. Values are 32bit float. File size approximately 12 GB.

https://www.gebco.net/data_and_products/gridded_bathymetry_data/

Download the global GEBCO_2019_Grid in netCDF format, unpack it and put GEBCO_2019.nc to height_map/maps/gebco_2019/ .
