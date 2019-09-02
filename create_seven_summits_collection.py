import geojson
from geojson import Feature, Point, FeatureCollection

mount_everest = Feature(
    geometry=Point((27.988056, 86.925278)[::-1]), properties={
    "name": "Mount Everest", "elevation_m": 8848,
    "url": "https://en.wikipedia.org/wiki/Mount_Everest", "type": "summit"})

aconcagua = Feature(
    geometry=Point((-32.653611, -70.011111)[::-1]), properties={
    "name": "Aconcagua", "elevation_m": 6960.8,
    "url": "https://en.wikipedia.org/wiki/Aconcagua", "type": "summit"})

denali = Feature(
    geometry=Point((63.0695, -151.0074)[::-1]), properties={"name": "Denali",
    "elevation_m": 6190, "url": "https://en.wikipedia.org/wiki/Denali",
    "type": "summit"})

mount_kilimanjaro = Feature(
    geometry=Point((-3.075833, 37.353333)[::-1]), properties={
    "name": "Mount Kilimanjaro", "elevation_m": 5895,
    "url": "https://en.wikipedia.org/wiki/Mount_Kilimanjaro", "type": "summit"})

mount_elbrus = Feature(
    geometry=Point((43.355, 42.439167)[::-1]), properties={
    "name": "Mount Elbrus", "elevation_m": 5642,
    "url": "https://en.wikipedia.org/wiki/Mount_Elbrus", "type": "summit"})

mount_vinson = Feature(
    geometry=Point((-78.525483, -85.617147)[::-1]), properties={
    "name": "Mount Vinson", "elevation_m": 4892,
    "url": "https://en.wikipedia.org/wiki/Vinson_Massif", "type": "summit"})

puncak_jaya = Feature(
    geometry=Point((-4.078889, 137.158333)[::-1]), properties={
    "name": "Puncak Jaya", "elevation_m": 4884,
    "url": "https://en.wikipedia.org/wiki/Puncak_Jaya", "type": "summit"})

mount_kosciuszko = Feature(
    geometry=Point((-36.4575, 148.262222)[::-1]), properties={
    "name": "Mount Kosciuszko", "elevation_m": 2228,
    "url": "https://en.wikipedia.org/wiki/Mount_Kosciuszko", "type": "summit"})

# https://en.wikipedia.org/wiki/Seven_Summits
# Due to different definitions of the seven continents, there are two different
# lists of the highest mountains of each continent. This list contains all 
# mountains of both definitions
seven_summits = FeatureCollection([
    mount_everest, aconcagua, denali, mount_kilimanjaro, mount_elbrus,
    mount_vinson, puncak_jaya, mount_kosciuszko])

file_name = 'static/seven_summits.json'
with open(file_name, 'w') as f:
    geojson.dump(seven_summits, f)
