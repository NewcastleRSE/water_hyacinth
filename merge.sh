#!/bin/sh

rm -rf /home/ubuntu/py/json/*.json
python3 shptojson.py
geojson-merge json/*.json > json/mergebig0.json
mapshaper json/mergebig0.json -simplify dp 10% keep-shapes -o format=geojson json/mergebig.json
cp json/mergebig.json /var/www/html/poly/json

