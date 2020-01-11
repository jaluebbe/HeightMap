from fastapi import FastAPI, Query, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel, confloat
from typing import List
import geojson
import pygeodesy.ellipsoidalVincenty as eV
import height_map.height_info as hi

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
async def root():
    return FileResponse('static/heightmap_gps.html')

@app.get("/api/get_height")
def get_height(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
    ):
    response = hi.get_height(lat, lon, water=False)
    if response['source'] == 'NODATA':
        raise HTTPException(status_code=404, detail="no data available")
    return response

@app.get("/api/get_max_height")
def get_max_height(
    lat_ll: float = Query(..., ge=-90, le=90),
    lon_ll: float = Query(..., ge=-180, le=180),
    lat_ur: float = Query(..., ge=-90, le=90),
    lon_ur: float = Query(..., ge=-180, le=180)
    ):
    (location_max, h_max, counter) = hi.get_max_height(lat_ll, lon_ll, lat_ur,
        lon_ur)
    return {'location_max': location_max, 'altitude_m': h_max,
        'counter': counter}

@app.get("/api/get_min_height")
def get_min_height(
    lat_ll: float = Query(..., ge=-90, le=90),
    lon_ll: float = Query(..., ge=-180, le=180),
    lat_ur: float = Query(..., ge=-90, le=90),
    lon_ur: float = Query(..., ge=-180, le=180)
    ):
    (location_min, h_min, counter) = hi.get_min_height(lat_ll, lon_ll, lat_ur,
        lon_ur)
    return {'location_min': location_min, 'altitude_m': h_min,
        'counter': counter}

@app.get("/api/get_min_max_height")
def get_min_max_height(
    lat_ll: float = Query(..., ge=-90, le=90),
    lon_ll: float = Query(..., ge=-180, le=180),
    lat_ur: float = Query(..., ge=-90, le=90),
    lon_ur: float = Query(..., ge=-180, le=180)
    ):
    extreme_locations = []
    (location_min, h_min, counter_min) = hi.get_min_height(lat_ll, lon_ll,
        lat_ur, lon_ur)
    (location_max, h_max, counter_max) = hi.get_max_height(lat_ll, lon_ll,
        lat_ur, lon_ur)
    for _index in range(counter_min):
        extreme_locations.append(geojson.Feature(
            geometry=geojson.Point(location_min[_index][::-1]), properties={
                "type": "minimum", "elevation_m": round(h_min, 1)}))
    for _index in range(counter_max):
        extreme_locations.append(geojson.Feature(
            geometry=geojson.Point(location_max[_index][::-1]), properties={
                "type": "maximum", "elevation_m": round(h_max, 1)}))
    return geojson.FeatureCollection(extreme_locations)

class Location(BaseModel):
    lat: confloat(ge=-90, le=90)
    lon: confloat(ge=-180, le=180)

class PositionRequest(BaseModel):
    track: List[Location]
    distance: confloat(ge=0)

@app.post("/api/get_track_length")
def post_get_track_length(track: List[Location]):
    distance = 0
    old_location = None
    for _location in track:
        current_location = eV.LatLon(_location.lat, _location.lon)
        if old_location:
            distance += old_location.distanceTo(current_location)
        old_location = current_location
    return round(distance, 3)

@app.post("/api/get_track_position")
def post_get_track_position(data: PositionRequest):
    distance = 0
    old_location = None
    for _location in data.track:
        current_location = eV.LatLon(_location.lat, _location.lon)
        if old_location:
            segment_length, bearing = old_location.distanceTo3(current_location
                )[:2]
            if distance + segment_length >= data.distance:
                position = old_location.destination(data.distance - distance,
                    bearing).latlon2(ndigits=6)
                return {'lat': position.lat, 'lon': position.lon}
            distance += segment_length
        old_location = current_location
    return {}
