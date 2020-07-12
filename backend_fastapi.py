from fastapi import FastAPI, Query, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
import geojson
from height_map.height_info import HeightInfo
from height_map.cci_land_cover import LandCover
import height_map.track_methods as tm

hi = HeightInfo()
lc = LandCover()

app = FastAPI(
    openapi_prefix='',
    title='HeightMap',
    description='Combination of several elevation data sources.'
    )

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse('static/heightmap.html')


@app.get("/gps", include_in_schema=False)
async def gps():
    return FileResponse('static/heightmap_gps.html')


@app.get("/railway", include_in_schema=False)
async def railway():
    return FileResponse('static/railwaymap.html')


@app.get("/api/get_height")
def get_height(
        lat: float = Query(..., ge=-90, le=90),
        lon: float = Query(..., ge=-180, le=180)):
    response = hi.get_height(lat, lon)
    if response['source'] == 'NODATA':
        raise HTTPException(status_code=404, detail="no data available")
    return response


@app.get("/api/get_max_height")
def get_max_height(
        lat_ll: float = Query(..., ge=-90, le=90),
        lon_ll: float = Query(..., ge=-180, le=180),
        lat_ur: float = Query(..., ge=-90, le=90),
        lon_ur: float = Query(..., ge=-180, le=180)):
    return hi.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)


@app.get("/api/get_min_height")
def get_min_height(
        lat_ll: float = Query(..., ge=-90, le=90),
        lon_ll: float = Query(..., ge=-180, le=180),
        lat_ur: float = Query(..., ge=-90, le=90),
        lon_ur: float = Query(..., ge=-180, le=180)):
    return hi.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)


@app.get("/api/get_min_max_height")
def get_min_max_height(
        lat_ll: float = Query(..., ge=-90, le=90),
        lon_ll: float = Query(..., ge=-180, le=180),
        lat_ur: float = Query(..., ge=-90, le=90),
        lon_ur: float = Query(..., ge=-180, le=180)):
    extreme_locations = []
    result = hi.get_min_max_height(lat_ll, lon_ll, lat_ur, lon_ur)
    for _location in result['location_min']:
        extreme_locations.append(geojson.Feature(
            geometry=geojson.Point(_location[::-1]), properties={
                "type": "minimum", "elevation_m": round(result['h_min'], 1),
                "source": result['source_min']}))
    for _location in result['location_max']:
        extreme_locations.append(geojson.Feature(
            geometry=geojson.Point(_location[::-1]), properties={
                "type": "maximum", "elevation_m": round(result['h_max'], 1),
                "source": result['source_max']}))
    return geojson.FeatureCollection(extreme_locations, properties={
        'source': result['source']})


@app.post("/api/get_track_length")
def post_get_track_length(track: tm.List[tm.Location]):
    return tm.get_track_length(track)


@app.post("/api/get_track_position")
def post_get_track_position(data: tm.PositionRequest):
    return tm.get_track_position(data)


@app.post("/api/get_track_elevation")
def post_get_track_elevation(data: tm.ElevationRequest):
    return tm.get_track_elevation(data)


@app.post("/api/get_simplified_track")
def post_get_simplified_track(data: tm.SimplifyRequest):
    return tm.get_simplified_track(data)


@app.post("/api/get_resampled_track")
def post_get_resampled_track(data: tm.ResamplingRequest):
    return tm.get_resampled_track(data)


@app.post("/api/geojson/get_height_graph_data")
def post_geojson_get_height_graph_data(data: tm.GeoJSONRequest):
    return tm.geojson_get_height_graph_data(data)

@app.get("/api/get_land_cover")
def get_surface_cover(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
    ):
    return lc.get_data_at_position(lat, lon)
