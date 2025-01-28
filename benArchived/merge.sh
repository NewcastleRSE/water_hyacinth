#!/bin/sh

####
# Ben's old `merge.sh` file created around November 2023.
# This file is for reference.
####

rm -rf /home/ubuntu/py/json/*.json

echo "Converting shapefiles to geojson..."
sleep 2
python3 shptojson.py
echo "Done!"

echo "Merging json files to master json..."
sleep 2
geojson-merge json/*.json > json/mergebig0.json
echo "Done!"

echo "Compressing json file to smaller size..."
sleep 2
mapshaper json/mergebig0.json -simplify dp 10% keep-shapes -o format=geojson json/mergebig.json
echo "Done!"

echo "Copy to web directory..."
sleep 2
cp json/mergebig.json /var/www/html/poly/json
echo "Done!"