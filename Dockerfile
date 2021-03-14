FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim AS build_image

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3 install aiofiles geojson numpy \
    pygeodesy h5py simplification

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim AS final_image
RUN apt-get -y update &&  \
    apt-get -y install --no-install-recommends python3-gdal && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build_image /opt/venv /opt/venv

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV KEEP_ALIVE=120
ENV TIMEOUT=60

COPY height_map /app/height_map
COPY static /app/static
COPY backend_fastapi.py /app/main.py
