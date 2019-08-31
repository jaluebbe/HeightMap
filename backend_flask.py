#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from flask import Response
from flask import request
from flask import abort
from flask import jsonify
import logging

import height_map.height_info as hi

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def root():
    return app.send_static_file('heightmap.html')

@app.route('/api/get_height')
def api_get_height():
    latitude = request.args.get('lat', None)
    longitude = request.args.get('lon', None)
    if None in (latitude, longitude):
        abort(404)
    (altitude, source, source_lat, source_lon, distance, attribution
        ) = hi.get_height(float(latitude), float(longitude), water=False)
    return jsonify(altitude_m=altitude, source=source, latitude=source_lat,
        longitude=source_lon, distance_m=distance, attribution=attribution)

if __name__ == '__main__':

    app.run("0.0.0.0", 5000)
