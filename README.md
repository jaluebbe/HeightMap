# HeightMap

## Software requirements

### Using conda 

conda env create -f environment.yml

### conda/apt

gunicorn numpy h5py gdal shapely requests pytest

### pip

pygeodesy geojson fastapi uvicorn aiofiles simplification

## Data Sources

### DGM200 (Germany, 200m grid):

https://www.bkg.bund.de/EN/Home/home.html

Put https://daten.gdz.bkg.bund.de/produkte/dgm/dgm200/aktuell/dgm200.utm32s.gridascii.zip to downloads/ and call dgm200_grid_conversion.py .

### OS Terrain 50 (UK, 50m grid, registration required):

Download ASCII Grid version of OS Terrain 50 from 
https://www.ordnancesurvey.co.uk/business-and-government/products/terrain-50.html to downloads/ and call terr50_data_conversion.py .
Finally, call create_terr50_min_max_cache.py to generate a cache of min/max values.

### SRTM (tiles of each 1 arc minute coverage with 30m resolution, registration required):

https://lpdaac.usgs.gov/products/srtmgl1v003/

Download required tiles from https://dwtkns.com/srtm30m/ , unpack and put them to height_map/maps/srtm1/ .

#### Replacement of SRTM .hgt files with improved data for many European countries:

The SRTM tiles could be replaced by .hgt files available from https://sonny.4lima.de where SRTM data is replaced by LiDAR where open data sources are available.

### World wide coverage of ocean and terrain

#### GEBCO_2023

15 arc-second resolution. Values are 16bit integer. File size approximately 7.5 GB.

https://www.gebco.net/data_and_products/gridded_bathymetry_data/

Download the global GEBCO_2023 Grid in netCDF format, unpack it and put GEBCO_2023.nc to height_map/maps/gebco/ .

#### ESA CCI Water Bodies v4.0

World wide map of ocean, water and land bodies in 150m resolution.

https://www.mdpi.com/2072-4292/9/1/36

http://maps.elie.ucl.ac.be/CCI/viewer/download.php

Download ftp://geo10.elie.ucl.ac.be/CCI/WaterBodies/ESACCI-LC-L4-WB-Ocean-Land-Map-150m-P13Y-2000-v4.0.tif and put it to height_map/maps/cci_wb4 .

#### ESA CCI Land Cover Maps v2.1.1

http://maps.elie.ucl.ac.be/CCI/viewer/download.php

Download C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc from http://maps.elie.ucl.ac.be/CCI/viewer/download.php and convert it to GeoTIFF:
```
gdalwarp -of Gtiff -co COMPRESS=LZW -co TILED=YES -ot Byte -te -180.0000000 -90.0000000 180.0000000 90.0000000 -tr 0.002777777777778 0.002777777777778 -t_srs EPSG:4326 NETCDF:C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc:lccs_class C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.tif
```

The corresponding legend is available at http://maps.elie.ucl.ac.be/CCI/viewer/download/ESACCI-LC-Legend.csv .

Put the GeoTIFF file and the legend to height_map/maps/cci_land_cover/ .

### NZ Railway Network

GeoJSON shapefiles published by KiwiRail describing the New Zealand railway network including tracks, bridges, tunnels and level crossings.

https://catalogue.data.govt.nz/organization/kiwirail-holdings-limited

The datasets being used are *kiwirail-tunnels1*, *kiwirail-bridges1*, *nz-railway-network* and *level-crossings-railway*.


## Startup of the web interface

The web interface and API is hosted using FastAPI. It could also be run as a Docker container.

### FastAPI
```
python backend_fastapi.py
```
You should take care if you would like to host on all interfaces (0.0.0.0) or on localhost (127.0.0.1) only.
Just modify the host parameter in the __main__ method according to your needs.

### Build and run as a Docker container
```
docker build -t heightmap ./
docker run -d -p 8000:80 --mount src=`pwd`/height_map/maps,target=/app/height_map/maps,type=bind,consistency=cached heightmap
```

### Additional mounting options
You may add you own imprint and/or privacy statement by adding
```
--mount src=`pwd`/imprint_privacy_statement.html,target=/app/static/datenschutz.html,type=bind,readonly
```
to your docker run command.

If you would like to use your own mapbox access token to display additional map layers, use 
```
--mount src=`pwd`/mapboxAccessToken.js,target=/app/static/mapboxAccessToken.js,type=bind,readonly
```
where mapboxAccessToken.js contains a line like
```
var mapboxAccessToken = '<your_mapbox_token>'
```

## Testing

Run ```py.test tests``` from the main directory to perform some tests.

## Accessing the API and web interface

You'll find an interative map at http://127.0.0.1:8000. Click anywhere on the map to obtain the local elevation from the most precise data source. 
You may drag the marker on the map. 
If you hold down shift and drag a rectangle on the map, A search for minimum and maximum elevation will be perfomed within the selected area. 
The map at http://127.0.0.1:8000/gps is using the position data of your mobile device. 
An example for surface elevation along tracks if provided at http://127.0.0.1:8000/railway where the tracks can be clicked. 
Documentation of the API is available at http://127.0.0.1:8000/docs (you can try out the API) and http://127.0.0.1:8000/redoc (more information but less interactive).

## Acknowledgements

Thanks to Andrea Y. Niemeyer for providing the marker icons.
