#!/bin/sh

## BASH SCRIPT TO DOWNLOAD SENTINEL2 IMAGERY AND PROCESS
## RGB SPECTRAL BANDS INTO GEOTIFF OUTPUT

echo "Starting automated download of Sentimel2 imagery and processing RGB bands to Geotiff Output"
sleep 3

#1. Download Sentinel2 Image File

echo ""
echo "Downloading Sentinel2 data..."
python3 sentinel.py
echo "Done!"
echo ""

#2. Extract RGB Files from Sentinel 2 Folder

echo "Extracting RGB Files from Sentinel 2 Folder"
python3 file.py
echo "Done!"
sleep 3
echo ""

#3. Merge bands
echo "Merging bands"
sleep 3
gdalbuildvrt -separate TCI.vrt B04.jp2 B03.jp2 B02.jp2
echo "Done!"
echo ""

#4. Convert to uncompressed GeoTiff

#echo "Converting to uncompressed GeoTiff"
#sleep 3
#gdal_translate -ot Byte -co TILED=YES -scale 0 4096 0 255 TCI.vrt TCI.tif
#echo "Done!"                                                                                                                      
#echo ""

#4. Convert to JPEG - compressed GeoTiff
echo "Converting to compressed GeoTiff"
sleep 3
gdal_translate -ot Byte -co TILED=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -scale 0 4096 0 255 TCI.vrt TCI.tif
echo "Done!"
echo ""

#5. Move tif file to web directory
sleep 3
echo "copy tif to web directory"
cp TCI.tif /var/www/html/temp
echo "done!"
echo ""

#6. Clean up jp2, zip & SAFE files
rm -rf *.jp2
rm -rf *.SAFE
rm -rf *.zip
