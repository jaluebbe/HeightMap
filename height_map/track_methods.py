import logging
from pydantic import BaseModel, confloat, constr, conlist
from typing import List
from geojson import FeatureCollection, Feature, LineString
import pygeodesy.ellipsoidalVincenty as eV
from simplification.cutil import simplify_coords
from height_map.height_info import HeightInfo
from height_map.timeit import timeit

logger = logging.getLogger(__name__)
hi = HeightInfo()


class Location(BaseModel):
    lat: confloat(ge=-90, le=90)
    lon: confloat(ge=-180, le=180)


class PositionRequest(BaseModel):
    track: List[Location]
    distance: confloat(ge=0)


@timeit
def get_track_length(track: List[Location]):
    distance = 0
    old_location = None
    for _location in track:
        current_location = eV.LatLon(_location.lat, _location.lon)
        if old_location:
            distance += old_location.distanceTo(current_location)
        old_location = current_location
    return round(distance, 3)


@timeit
def get_track_position(data: PositionRequest):
    distance = 0
    old_location = None
    for _location in data.track:
        current_location = eV.LatLon(_location.lat, _location.lon)
        if old_location:
            segment_length, bearing = old_location.distanceTo3(
                current_location)[:2]
            if distance + segment_length >= data.distance:
                position = old_location.destination(data.distance - distance,
                    bearing).latlon2(ndigits=6)
                return {'lat': position.lat, 'lon': position.lon}
            distance += segment_length
        old_location = current_location
    return {}


class ElevationRequest(BaseModel):
    track: List[Location]
    water: bool = False


@timeit
def get_track_elevation(data: ElevationRequest):
    new_track = []
    for _location in data.track:
        response = hi.get_height(_location.lat, _location.lon, water=data.water)
        for key in ['attribution', ]:
            response.pop(key, None)
        new_track.append(response)
    return new_track


class SimplifyRequest(BaseModel):
    track: List[Location]
    epsilon: confloat(ge=0) = 0


@timeit
def get_simplified_track(data: SimplifyRequest):
    input_track = [[_t.lon, _t.lat] for _t in data.track]
    simplified_track = simplify_coords(input_track, epsilon=data.epsilon)
    output_track = [{'lat': y, 'lon': x} for x, y in simplified_track]
    return output_track


class ResamplingRequest(BaseModel):
    track: List[Location]
    step: confloat(gt=0)
    include_existing_points: bool = True


@timeit
def resample_track_list(track, step, include_existing_points=True):
    new_track = []
    distance = 0
    target_distance = step
    old_location = None
    for _location in track:
        current_location = eV.LatLon(_location[1], _location[0])
        if old_location:
            segment_length, bearing = old_location.distanceTo3(
                current_location)[:2]
            segment_end = distance + segment_length
            while segment_end >= target_distance:
                old_location = old_location.destination(
                    target_distance - distance, bearing)
                track_item = old_location.latlon2(ndigits=6)
                new_track.append([track_item.lon, track_item.lat])
                distance = target_distance
                target_distance += step
            remaining_distance, bearing = old_location.distanceTo3(
                current_location)[:2]
            distance += remaining_distance
            existing_point = current_location.latlon2(ndigits=6)
            if include_existing_points and existing_point != track_item:
                target_distance = distance + step
                track_item = existing_point
                new_track.append([track_item.lon, track_item.lat])
        else:
            track_item = current_location.latlon2(ndigits=6)
            new_track.append([track_item.lon, track_item.lat])
        old_location = current_location
    last_item = old_location.latlon2(ndigits=6)
    if not include_existing_points and track_item != last_item:
        new_track.append([last_item.lon, last_item.lat])
    return new_track


@timeit
def get_resampled_track(data: ResamplingRequest):
    track = [[_location.lon, _location.lat] for _location in data.track]
    resampled_track = resample_track_list(track, data.step,
        data.include_existing_points)
    return [{'lat': _item[1], 'lon': _item[0]} for _item in resampled_track]


class GeoJSONLineString(BaseModel):
    type: constr(regex='LineString')
    coordinates: List[conlist(float, min_items=2, max_items=3)]


class GeoJSONRequest(BaseModel):
    type: constr(regex='Feature')
    properties: dict
    geometry: GeoJSONLineString


@timeit
def geojson_get_height_graph_data(data: GeoJSONRequest):
    _coords = [xy[0:2] for xy in data.dict()['geometry']['coordinates']]
    simplified_track = simplify_coords(_coords, epsilon=0.0001)
    simplified_track = resample_track_list(simplified_track, 300)
    track_elevation = [hi.get_height(y, x, water=False) for x, y in 
        simplified_track]
    _coordinates = [(round(pt['lon'], 6), round(pt['lat'], 6),
        pt['altitude_m']) for pt in track_elevation]
    _feature = Feature(geometry=LineString(_coordinates),
        properties={"attributeType": "surface elevation"})
    return [FeatureCollection([_feature], properties={"summary": "elevation"})]
