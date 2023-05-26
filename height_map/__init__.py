import pygeodesy.ellipsoidalVincenty as ev
import pygeodesy.ellipsoidalExact as ee


def calculate_distance(lat1, lon1, lat2, lon2):
    if lat1 == lat2 and lon1 == lon2:
        return 0
    try:
        location_1 = ev.LatLon(lat1, lon1)
        location_2 = ev.LatLon(lat2, lon2)
        distance = location_1.distanceTo(location_2)
    except ev.VincentyError:
        location_1 = ee.LatLon(lat1, lon1)
        location_2 = ee.LatLon(lat2, lon2)
        distance = location_1.distanceTo(location_2)
    return distance
