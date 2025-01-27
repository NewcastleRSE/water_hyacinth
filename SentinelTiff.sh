#!/bin/sh
set -e  # Exit immediately if a command exits with non-zero status

## BASH SCRIPT TO DOWNLOAD SENTINEL2 IMAGERY AND PROCESS
## RGB SPECTRAL BANDS INTO GEOTIFF OUTPUT

echo "Starting automated download of Sentinel2 imagery and processing RGB bands to Geotiff Output"
sleep 3  # Pause to allow reading status message

#1. Download Sentinel2 Image File
python3 corp.py  # Uses Copernicus API to download satellite imagery
echo "Done!"
echo ""

#2. Extract RGB Files from Sentinel 2 Folder
echo "Extracting RGB Files from Sentinel 2 Folder"
python3 file.py  # Extracts specific band files (Red, Green, Blue) from downloaded data
echo "Done!"
sleep 3
echo ""

#3. Merge bands
echo "Merging bands"
sleep 3
# Combine RGB bands (B04=Red, B03=Green, B02=Blue) into single virtual raster
gdalbuildvrt -separate TCI.vrt B04.jp2 B03.jp2 B02.jp2
echo "Done!"
echo ""

#4. Convert to uncompressed GeoTiff (commented out alternative)
#echo "Converting to uncompressed GeoTiff"
#sleep 3
#gdal_translate -ot Byte -co TILED=YES -scale 0 4096 0 255 TCI.vrt TCI.tif
#echo "Done!"
#echo ""

#4. Convert to JPEG - compressed GeoTiff
echo "Converting to compressed GeoTiff"
sleep 3
# Convert virtual raster to compressed GeoTIFF with JPEG compression
# -ot Byte: Convert to 8-bit
# -co TILED=YES: Create tiled output
# -co COMPRESS=JPEG: Use JPEG compression
# -co PHOTOMETRIC=YCBCR: Use YCbCr color space for better JPEG compression
# -scale 0 4096 0 255: Scale values from 0-4096 to 0-255
gdal_translate -ot Byte -co TILED=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -scale 0 4096 0 255 TCI.vrt TCI.tif

#Alternative compression without YCbCr color space (commented out)
#gdal_translate -ot Byte -co TILED=YES -co COMPRESS=JPEG -scale 0 4096 0 255 TCI.vrt TCI.tif
echo "Done!"
echo ""

#5. Move tif file to web directory
sleep 3
echo "timestamp tiff and copy to tiff folder"
echo "copy tif to web folder"
cp TCI.tif /var/www/html/temp  # Copy to web-accessible directory
echo "Done!"
echo "timestamp tif and archive to folder"
# Create timestamped copy in archive folder using format YYYYMMDDHHMM
cp TCI.tif tiffs/$(date -d "today" +"%Y%m%d%H%M").tif
echo "done!"

#Alternative copy method (commented out)
#sleep 3
#echo "copy tif to web directory"
#cp TCI.tif /var/www/html/temp
#echo "done!"
#echo "http://ec2-51-20-68-120.eu-north-1.compute.amazonaws.com/temp/TCI.tif"
#echo ""

#6. Clean up files
# Remove all temporary and intermediate files
rm -rf *.jp2      # Remove JPEG2000 band files
rm -rf *.SAFE     # Remove SAFE format files
rm -rf *.zip      # Remove downloaded zip files
rm -rf TCI.*      # Remove temporary TCI files