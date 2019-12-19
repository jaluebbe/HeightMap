FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8
RUN apk --no-cache add hdf5 hdf5-dev libffi-dev --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
    && apk --update --no-cache --virtual .build-dep add \
    build-base \
    && pip install --upgrade pip \
    && pip install cython \
    && pip install pytest \
    && pip install h5py \
    && pip install pygeodesy \
    && pip install geojson \
    && pip install aiofiles \
    && apk del --purge hdf5-dev zlib-dev \
    && rm -rf ~/.cache/pip/*
COPY height_map /app/height_map
COPY static /app/static
COPY backend_fastapi.py /app/main.py
COPY src /app/src
RUN cd src && sh compile.sh && cd ..
