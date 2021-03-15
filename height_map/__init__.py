import pygeodesy.ellipsoidalVincenty as eV


def calculate_distance(lat1, lon1, lat2, lon2): 
    if lat1 == lat2 and lon1 == lon2:
        return 0
    location_1 = eV.LatLon(lat1, lon1)
    location_2 = eV.LatLon(lat2, lon2)
    return location_1.distanceTo(location_2)
