FROM debian:bullseye-slim

RUN apt-get -y update &&  \
    apt-get -y install python3-pip python3-gdal python3-numpy && \
    pip3 install --no-cache-dir uvicorn gunicorn fastapi aiofiles geojson \
    pygeodesy h5py simplification uvloop websockets httptools && \
    apt-get -y remove build-essential python3-setuptools python3-pip && \
    apt -y autoremove

COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY docker/gunicorn_conf.py /gunicorn_conf.py

COPY docker/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY height_map /app/height_map
COPY static /app/static
COPY backend_fastapi.py /app/main.py

ENV KEEP_ALIVE=120
ENV TIMEOUT=60

WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g.
# for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]
