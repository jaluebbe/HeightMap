FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN pip install aiofiles pygeodesy geojson h5py numpy cython
COPY height_map /app/height_map
COPY static /app/static
COPY backend_fastapi.py /app/main.py
COPY src /app/src
RUN cd src&&sh compile.sh&&cd ..
