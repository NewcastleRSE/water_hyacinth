#!/bin/sh

rm -rf /home/ubuntu/py/json/*.json
python3 shptojson.py
geojson-merge json/*.json > json/mergebig.json
cp json/mergebig.json /var/www/html/poly/json

