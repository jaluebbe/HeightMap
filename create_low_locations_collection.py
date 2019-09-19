import geojson
from geojson import Feature, Point, FeatureCollection

rms_titanic_wreck = Feature(
    geometry=Point((41.7325, -49.946944)[::-1]), properties={
    "name": "Wreck of the RMS Titanic", "elevation_m": -3784,
    "url": "https://en.wikipedia.org/wiki/RMS_Titanic", "type": "shipwreck"})

challenger_deep = Feature(
    geometry=Point((11.373333, 142.591667)[::-1]), properties={
    "name": "Challenger Deep", "elevation_m": -10920,
    "url": "https://en.wikipedia.org/wiki/Challenger_Deep",
    "type": "subsea_depression"})

badwater_basin = Feature(
    geometry=Point((36.250278, -116.825833)[::-1]), properties={
    "name": "Badwater Basin", "elevation_m": -85,
    "url": "https://en.wikipedia.org/wiki/Badwater_Basin",
    "type": "depression"})

laguna_del_carbon = Feature(
    geometry=Point((-49.5762, -68.3514)[::-1]), properties={
    "name": "Laguna del Carbón", "elevation_m": -105,
    "url": "https://en.wikipedia.org/wiki/Laguna_del_Carb%C3%B3n",
    "type": "depression"})

hambach_surface_mine = Feature(
    geometry=Point((50.910833, 6.502778)[::-1]), properties={
    "name": "Hambach surface mine", "elevation_m": -299,
    "url": "https://en.wikipedia.org/wiki/Hambach_surface_mine",
    "type": "surface_mine"})

dead_sea = Feature(
    geometry=Point((31.5, 35.5)[::-1]), properties={
    "name": "Dead Sea", "elevation_m": -430.5,
    "url": "https://en.wikipedia.org/wiki/Dead_Sea", "type": "depression"})

qattara_depression = Feature(
    geometry=Point((30, 27.5)[::-1]), properties={
    "name": "Qattara Depression", "elevation_m": -147,
    "url": "https://en.wikipedia.org/wiki/Qattara_Depression",
    "type": "depression"})

karagiye = Feature(
    geometry=Point((43.4, 51.79)[::-1]), properties={
    "name": "Karagiye", "elevation_m": -132,
    "url": "https://en.wikipedia.org/wiki/Karagiye", "type": "depression"})

ayding_lake = Feature(
    geometry=Point((42.6575, 89.270556)[::-1]), properties={
    "name": "Ayding Lake", "elevation_m": -154,
    "url": "https://en.wikipedia.org/wiki/Ayding_Lake", "type": "depression"})

danakil_depression = Feature(
    geometry=Point((14.2417, 40.3)[::-1]), properties={
    "name": "Danakil Depression", "elevation_m": -125,
    "url": "https://en.wikipedia.org/wiki/Danakil_Depression",
    "type": "depression"})

lake_assal = Feature(
    geometry=Point((11.65, 42.416667)[::-1]), properties={
    "name": "Lake Assal", "elevation_m": -155,
    "url": "https://en.wikipedia.org/wiki/Lake_Assal_(Djibouti)",
    "type": "depression"})

sea_of_galilee = Feature(
    geometry=Point((32.833333, 35.583333)[::-1]), properties={
    "name": "Sea of Galilee", "elevation_m": -214.66,
    "url": "https://en.wikipedia.org/wiki/Sea_of_Galilee",
    "type": "depression"})

calypso_deep = Feature(
    geometry=Point((36.566667, 21.133333)[::-1]), properties={
    "name": "Calypso Deep", "elevation_m": -5267,
    "url": "https://en.wikipedia.org/wiki/Calypso_Deep",
    "type": "subsea_depression"})

manila_trench = Feature(
    geometry=Point((14.7, 119)[::-1]), properties={
    "name": "Manila Trench", "elevation_m": -5400,
    "url": "https://en.wikipedia.org/wiki/Manila_Trench",
    "type": "subsea_depression"})

litke_deep = Feature(
    geometry=Point((82.4, 19.516667)[::-1]), properties={
    "name": "Litke Deep", "elevation_m": -5449,
    "url": "https://en.wikipedia.org/wiki/Litke_Deep",
    "type": "subsea_depression"})

south_sandwich_trench = Feature(
    geometry=Point((-55.2245, -26.1705)[::-1]), properties={
    "name": "South Sandwich Trench", "elevation_m": -8266,
    "url": "https://en.wikipedia.org/wiki/South_Sandwich_Trench",
    "type": "subsea_depression"})

cayman_trough = Feature(
    geometry=Point((18.5, -83)[::-1]), properties={
    "name": "Cayman Trough", "elevation_m": -7686,
    "url": "https://en.wikipedia.org/wiki/Cayman_Trough",
    "type": "subsea_depression"})

diamantina_deep = Feature(
    geometry=Point((-35, 104)[::-1]), properties={
    "name": "Diamantina Deep", "elevation_m": -7079,
    "url": "https://en.wikipedia.org/wiki/Diamantina_Deep",
    "type": "subsea_depression"})

low_locations = FeatureCollection([
    rms_titanic_wreck, challenger_deep, badwater_basin, laguna_del_carbon,
    hambach_surface_mine, dead_sea, qattara_depression, karagiye, ayding_lake,
    danakil_depression, lake_assal, sea_of_galilee, calypso_deep, manila_trench,
    litke_deep, south_sandwich_trench, cayman_trough, diamantina_deep    
    ])

file_name = 'static/low_locations.json'
with open(file_name, 'w') as f:
    geojson.dump(low_locations, f)
