FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip install --upgrade pip \
    && pip install cython h5py pygeodesy geojson aiofiles numpy
COPY height_map /app/height_map
COPY static /app/static
COPY backend_fastapi.py /app/main.py
COPY src /app/src
RUN cd src && sh compile.sh && cd ..
