from pygeodesy import ellipsoidalVincenty as eV
from pygeodesy import toOsgr, parseOSGR, Osgr


def test_ll_to_osgr_to_ll():
    # location on the Isles of Scilly
    lat = 49.926244
    lon = -6.297934
    ll_orig = eV.LatLon(lat, lon)
    osgr = toOsgr(ll_orig)
    ll_osgr = osgr.toLatLon(eV.LatLon)
    assert ll_orig.distanceTo(ll_osgr) < 1
    parsed_osgr = parseOSGR(str(osgr))
    ll_parsed_osgr = parsed_osgr.toLatLon(eV.LatLon)
    assert ll_orig.distanceTo(ll_parsed_osgr) < 1
    osgr_new = Osgr(osgr.easting, osgr.northing)
    ll_osgr_new = osgr_new.toLatLon(eV.LatLon)
    assert ll_orig.distanceTo(ll_osgr) < 1

    
