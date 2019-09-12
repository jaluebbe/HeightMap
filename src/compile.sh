#!/bin/sh
python setup.py build_ext --inplace
cp *.so ../height_map/
