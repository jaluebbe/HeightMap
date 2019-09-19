from fastapi import FastAPI, Query
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse
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
    return hi.get_height(lat, lon, water=False)

@app.get("/api/get_max_height")
def get_max_height(
    lat_ll: float = Query(..., ge=-90, le=90),
    lon_ll: float = Query(..., ge=-180, le=180),
    lat_ur: float = Query(..., ge=-90, le=90),
    lon_ur: float = Query(..., ge=-180, le=180)
    ):
    return hi.get_max_height(lat_ll, lon_ll, lat_ur, lon_ur)

@app.get("/api/get_min_height")
def get_min_height(
    lat_ll: float = Query(..., ge=-90, le=90),
    lon_ll: float = Query(..., ge=-180, le=180),
    lat_ur: float = Query(..., ge=-90, le=90),
    lon_ur: float = Query(..., ge=-180, le=180)
    ):
    return hi.get_min_height(lat_ll, lon_ll, lat_ur, lon_ur)
