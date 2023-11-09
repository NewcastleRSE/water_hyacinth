#!/bin/sh
set -e

## BASH SCRIPT TO DOWNLOAD SENTINEL2 IMAGERY AND PROCESS
## RGB SPECTRAL BANDS INTO GEOTIFF OUTPUT

echo "Starting automated download of Sentimel2 imagery and processing RGB bands to Geotiff Output"
sleep 3

#1. Download Sentinel2 Image File

python3 corp.py
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
#gdal_translate -ot Byte -co TILED=YES -co COMPRESS=JPEG -scale 0 4096 0 255 TCI.vrt TCI.tif

echo "Done!"
echo ""

#5. Move tif file to web directory
sleep 3
echo "timestamp tiff and copy to tiff folder" 
echo "copy tif to web folder"
cp TCI.tif /var/www/html/temp
echo "Done!"
echo "timestamp tif and archive to folder"
cp TCI.tif tiffs/$(date -d "today" +"%Y%m%d%H%M").tif
#echo "copy tif to web directory"
#cp tiffs/$(date -d "today" +"%Y%m%d%H%M").tif /var/www/html/temp
echo "done!"

#5. Move tif file to web directory
#sleep 3
#echo "copy tif to web directory"
#cp TCI.tif /var/www/html/temp
#echo "done!"
#echo "http://ec2-51-20-68-120.eu-north-1.compute.amazonaws.com/temp/TCI.tif"
#echo ""

#6. Clean up files
rm -rf *.jp2
rm -rf *.SAFE
rm -rf *.zip
rm -rf TCI.*
