import logging
import numpy as np
from pydantic import BaseModel, confloat, constr, conlist
from typing import List
from geojson import FeatureCollection, Feature, LineString
import pygeodesy.ellipsoidalVincenty as eV
from simplification.cutil import simplify_coords
from height_map.height_info import HeightInfo
from height_map.cci_land_cover import LandCover
from fastapi import APIRouter

router = APIRouter()

logger = logging.getLogger(__name__)
hi = HeightInfo()
lc = LandCover()


class Location(BaseModel):
    lat: confloat(ge=-90, le=90)
    lon: confloat(ge=-180, le=180)


class PositionRequest(BaseModel):
    track: List[Location]
    distance: confloat(ge=0)


@router.post("/api/get_track_length")
def get_track_length(track: List[Location]):
    distance = 0
    old_location = None
    for _location in track:
        current_location = eV.LatLon(_location.lat, _location.lon)
        if old_location:
            distance += old_location.distanceTo(current_location)
        old_location = current_location
    return round(distance, 3)


@router.post("/api/get_track_position")
def get_track_position(data: PositionRequest):
    distance = 0
    old_location = None
    for _location in data.track:
        current_location = eV.LatLon(_location.lat, _location.lon)
        if old_location:
            segment_length, bearing = old_location.distanceTo3(
                current_location
            )[:2]
            if distance + segment_length >= data.distance:
                position = old_location.destination(
                    data.distance - distance, bearing
                ).latlon2(ndigits=6)
                return {"lat": position.lat, "lon": position.lon}
            distance += segment_length
        old_location = current_location
    return {}


class ElevationRequest(BaseModel):
    track: List[Location]


@router.post("/api/get_track_elevation")
def get_track_elevation(data: ElevationRequest):
    new_track = []
    for _location in data.track:
        response = hi.get_height(_location.lat, _location.lon)
        for key in [
            "attribution",
        ]:
            response.pop(key, None)
        new_track.append(response)
    return new_track


class SimplifyRequest(BaseModel):
    track: List[Location]
    epsilon: confloat(ge=0) = 0


@router.post("/api/get_simplified_track")
def get_simplified_track(data: SimplifyRequest):
    input_track = [[_t.lon, _t.lat] for _t in data.track]
    simplified_track = simplify_coords(input_track, epsilon=data.epsilon)
    output_track = [{"lat": y, "lon": x} for x, y in simplified_track]
    return output_track


class ResamplingRequest(BaseModel):
    track: List[Location]
    step: confloat(gt=0)
    include_existing_points: bool = True


def _get_lonlat(latlon, digits=6):
    _position = latlon.latlon2(ndigits=digits)
    return [_position.lon, _position.lat]


def resample_track_list(track, step, include_existing_points=True):
    if len(track) == 0:
        return []
    distance = 0
    target_distance = step
    old_location = eV.LatLon(track[0][1], track[0][0])
    new_track = [_get_lonlat(old_location)]
    for _location in track[1:]:
        current_location = eV.LatLon(_location[1], _location[0])
        segment_length, bearing = old_location.distanceTo3(current_location)[:2]
        segment_end = distance + segment_length
        for target_distance in np.arange(target_distance, segment_end, step):
            old_location = old_location.destination(
                target_distance - distance, bearing
            )
            new_track.append(_get_lonlat(old_location))
            distance = target_distance
        existing_point = _get_lonlat(current_location)
        distance = segment_end
        if include_existing_points and existing_point != new_track[-1]:
            new_track.append(existing_point)
            target_distance = segment_end + step
        elif not include_existing_points:
            target_distance += step
        old_location = current_location
    last_item = _get_lonlat(old_location)
    if not include_existing_points and new_track[-1] != last_item:
        new_track.append(last_item)
    return new_track


@router.post("/api/get_resampled_track")
def get_resampled_track(data: ResamplingRequest):
    track = [[_location.lon, _location.lat] for _location in data.track]
    resampled_track = resample_track_list(
        track, data.step, data.include_existing_points
    )
    return [{"lat": _item[1], "lon": _item[0]} for _item in resampled_track]


class GeoJSONLineString(BaseModel):
    type: constr(regex="LineString")
    coordinates: List[conlist(float, min_items=2, max_items=3)]


class GeoJSONRequest(BaseModel):
    type: constr(regex="Feature")
    properties: dict
    geometry: GeoJSONLineString


@router.post("/api/geojson/get_height_graph_data")
def geojson_get_height_graph_data(data: GeoJSONRequest):
    _coords = [xy[0:2] for xy in data.dict()["geometry"]["coordinates"]]
    simplified_track = simplify_coords(_coords, epsilon=0.00003)
    simplified_track = resample_track_list(simplified_track, 300)
    track_elevation = [hi.get_height(y, x) for x, y in simplified_track]
    _coordinates = [
        (round(pt["lon"], 6), round(pt["lat"], 6), pt["altitude_m"])
        for pt in track_elevation
    ]
    _lc_values = [
        lc.get_value_at_position(_lat, _lon)
        for _lon, _lat, _altitude_m in _coordinates
    ]
    _features = []
    _track = [_coordinates[0]]
    _current_value = _lc_values[0]
    _number_coords = len(_lc_values)
    for _i in range(1, _number_coords):
        _track.append(_coordinates[_i])
        if _current_value != _lc_values[_i] or _i == _number_coords - 1:
            _feature = Feature(
                geometry=LineString(_track),
                properties={"attributeType": str(_current_value)},
            )
            _features.append(_feature)
            _track = [_coordinates[_i]]
            _current_value = _lc_values[_i]
    _land_cover_feature_collection = FeatureCollection(
        _features, properties={"summary": "land cover"}
    )
    return [_land_cover_feature_collection]
