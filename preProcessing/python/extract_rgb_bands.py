import glob, os, shutil

# Python script to extract RGB image bands from Sentinel 2 Satellite download folder and copy
# to local folder for processing into Geotiff via GDAL

for file in glob.glob('/mnt/temp/zip/**/*B04_10m.jp2', recursive=True):
    shutil.copy(file,'/mnt/temp/zip')
    os.rename(file, 'B04.jp2')

for file in glob.glob('/mnt/temp/zip/**/*B03_10m.jp2', recursive=True):
    shutil.copy(file,'/mnt/temp/zip')
    os.rename(file, 'B03.jp2')

for file in glob.glob('/mnt/temp/zip/**/*B02_10m.jp2', recursive=True):
    shutil.copy(file,'/mnt/temp/zip')
    os.rename(file, 'B02.jp2')

