#!/bin/sh
python3 setup.py build_ext --inplace
cp *.so ../height_map/
