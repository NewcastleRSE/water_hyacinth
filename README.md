# Invasive Water Hyacinth Project

A project to identify invasive water hyacinth through satellite imagery layered onto a mapping interface

## About

This project will take satellite imagery (sentinel) from the satellite host and then pre-process it using an API before
being fed into an algorithm for post-processing
and outputting to a shape file. This shapefile would then be uploaded to a webmap for visual overlay display. This
process would consist of converting the shapefile to a GeoJSON and then combining
with existing GeoJSON files to create an overlay which can be switched on or off on the webmap.

### Deliverable To

Deepayan Bhowmik   
Senior lecturer in Data Science   
Newcastle University   
[deepayan.bhowmik@newcastle.ac.uk](mailto:deepayan.bhowmik@newcastle.ac.uk)   

### Development Team

**Imre Draskovits**     
Research Software Engineer    
Newcastle University   
[imre.draskovits@newcastle.ac.uk](mailto:imre.draskovits@newcastle.ac.uk)   

**Ben Daly**  
Research Software Engineer   
Newcastle University    
[ben.daly@newcastle.ac.uk](mailto:ben.daly@newcastle.ac.uk)   

## Built With

Leaflet Mapping   
Python    
JavaScript    

## Getting Started

### Prerequisites

This app runs on a Ubuntu instance of AWS and can be accessed via SSH into the AWS box as follows:
It requires download of the key UBUNTU.pem (download above)
Once downloaded, run the following command from the same directory:

> ssh -i "ubuntu.pem" ubuntu@ec2-16-16-213-96.eu-north-1.compute.amazonaws.com

### URL

http://ec2-51-20-68-120.eu-north-1.compute.amazonaws.com/poly/

### Folders

Once logged into the AWS box, you will be in the home directory (/home/ubuntu)
To access the app install folders navigate to the following directory:

> cd /var/www/html/poly

This contains the following 3 files:

* index.html (index page)
* style.css (css)
* script.js (Leaflet JS)

### Git Working Directory

> /home/ubuntu/py/water_hyacinth

## Coverting Shapefile to GeoJSON Pipeline...

There is a staging process for converting shapefiles to a combined GeoJSON file for display on the Leaflet map. This is
done within a bash script called merge.sh
Firstly the shapefiles should be downloaded into the directory /home/ubuntu/py/shp

```bash
#!/bin/sh

rm -rf /home/ubuntu/py/json/*.json
python3 shptojson.py
geojson-merge json/*.json > json/mergebig.json
mapshaper json/mergebig0.json -simplify dp 10% keep-shapes -o format=geojson json/mergebig.json
cp json/mergebig.json /var/www/html/poly/json

# This is as follows:

#  (this removes the existing json files previously converted from the folder)
rm -rf /home/ubuntu/py/json/*.json

#  (this is script that converts the shapefiles to json files and saves them in /home/ubuntu/py/json
python3 shptojson.py

#  (this merges the created converted json files into 1 geojson file for overlay on leaflet map)
geojson-merge json/*.json > json/mergebig0.json

#  (this refactors the geojson to a much smaller (and more responsive) size)
mapshaper json/mergebig0.json -simplify dp 10% keep-shapes -o format=geojson json/mergebig.json

#  (this copies the combined geojson file into the web folder ready for access via the web server)
cp json/mergebig.json /var/www/html/poly/json
```

### SENTINEL2 IMAGE DATA --> OLD METHOD (sentinel.py)

Sentinel 2 data can be downloaded using a API Script such as the following (NOTE THIS IS NO LONGER VALID AS THE OPEN
ACCESS HUB CLOSED DOWN, THUS API IS INVALID)

```python
# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

api = SentinelAPI('user', 'password', 'https://apihub.copernicus.eu/apihub')

# download single scene by known product id
api.download(<product_id>)

# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('/path/to/map.geojson'))
products = api.query(footprint,
                     date=('20151219', date(2015, 12, 29)),
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 30))

# download all results from the search
api.download_all(products)

# convert to Pandas DataFrame
products_df = api.to_dataframe(products)

# GeoJSON FeatureCollection containing footprints and metadata of the scenes
api.to_geojson(products)

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
api.to_geodataframe(products)

# Get basic information about the product: its title, file size, MD5 sum, date, footprint and
# its download url
api.get_product_odata(<product_id>)

# Get the product's full metadata available on the server
api.get_product_odata(<product_id>, full=True)

```

### SENTINEL2 IMAGE DATA --> NEW METHOD (corp.py)

```python
import datetime as dt
import zipfile

import os
import pandas as pd
import requests

now = dt.datetime.today().strftime("%Y-%m-%d")
print(now)


# Setup access token/entry to dataspace access hub...

def get_access_token(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
                          data=data,
                          )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Access token creation failed. Reponse from the server was: {r.json()}"
        )
    return r.json()["access_token"]


access_token = get_access_token("ben.daly@ncl.ac.uk", "########")

# =====================================#

# Set parameters for data download...

print("Searching for products to download...")

start_date = "2023-08-15"
end_date = "2023-10-30"
data_collection = "SENTINEL-2"
# aoi = 'POLYGON((73.76637462028609 18.60744222377967,73.76637462028609 18.454997850822508, 73.94931027079727 18.454997850822508,73.94931027079727 18.60744222377967,73.76637462028609 18.60744222377967))'
aoi = 'POLYGON ((77.497559 16.746688, 78.865356 16.799282, 79.656372 16.562493, 79.82666 15.850389, 79.491577 15.337167, 78.651123 15.130462, 77.711792 15.252389, 77.167969 15.850389, 77.102051 16.372851, 77.497559 16.746688))'
# aoi = 'POINT (18.6 73.9)' 

json = requests.get(
    f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=contains(Name,'S2A') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 20.00) and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {start_date}T00:00:00.000Z and ContentDate/Start lt {end_date}T00:00:00.000Z").json()

# json = requests.get(f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq {data_collection} and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {start_date}T00:00:00.000Z and ContentDate/Start lt {end_date}T00:00:00.000Z").json()
# json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=contains(Name,'S2A') and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt 2022-05-03T00:00:00.000Z and ContentDate/Start lt 2022-05-30T00:11:00.000Z").json()
# json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.00) and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection' and att/OData.CSC.StringAttribute/Value eq 'ASCENDING') and ContentDate/Start gt 2022-05-03T00:00:00.000Z and ContentDate/Start lt 2022-05-03T04:00:00.000Z&$top=10").json()

# Add Json output to dataframe
df = pd.DataFrame.from_dict(json['value'])
df = df.sort_values(by=['Name'], ascending=False)

# Print out DF 
print(df)

# Take first result (most recent data file) ID from dataframe 
ID = df.iloc[0, 1]
print(ID)

# sys.exit()

# =====================================#

# Download data...

session = requests.Session()

session.headers.update({'Authorization': f'Bearer {access_token}'})

url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products(" + ID + ")/$value"
print(url)

response = session.get(url, allow_redirects=False)

while response.status_code in (301, 302, 303, 307):
    print("Downloading file")
    url = response.headers['Location']
    response = session.get(url, allow_redirects=False)
file = session.get(url, verify=False, allow_redirects=True)

with open(f"sentinel.zip", 'wb') as p:
    p.write(file.content)

print("Done")

# =====================================#

# Unzip file...

dir_name = '.'
extension = ".zip"

print()
print("Unzipping downloaded files into folders...")

for item in os.listdir(dir_name):  # loop through items in dir
    if item.endswith(extension):  # check for zip" extension
        file_name = os.path.abspath(item)  # get full path of files
        zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
        zip_ref.extractall(dir_name)  # extract file to dir
        zip_ref.close()  # close file
#        os.remove(file_name) # delete zipped file

print("All files unzipped!")
```

## SENTINEL2 BANDS

```bash
Band   Category	  Spatial Resolution	Revisit
Visible (4)	      10 m	              5 days
Near-Infrared (6)	20 m	              5 days
Short-wave IR (3)	60 m	              5 days

Name	Resolution	Description
B01	60 m	Coastal aerosol, 442.7 nm (S2A), 442.2 nm (S2B)
B02	10 m	Blue, 492.4 nm (S2A), 492.1 nm (S2B)
B03	10 m	Green, 559.8 nm (S2A), 559.0 nm (S2B)
B04	10 m	Red, 664.6 nm (S2A), 664.9 nm (S2B)
B05	20 m	Vegetation red edge, 704.1 nm (S2A), 703.8 nm (S2B)
B06	20 m	Vegetation red edge, 740.5 nm (S2A), 739.1 nm (S2B)
B07	10 m	Vegetation red edge, 782.8 nm (S2A), 779.7 nm (S2B)
B08	10 m	NIR, 832.8 nm (S2A), 832.9 nm (S2B)
B8A	20 m	Narrow NIR, 864.7 nm (S2A), 864.0 nm (S2B)
B09	60 m	Water vapour, 945.1 nm (S2A), 943.2 nm (S2B)
B10	60 m	SWIR – Cirrus, 1373.5 nm (S2A), 1376.9 nm (S2B)
B11	20 m	SWIR, 1613.7 nm (S2A), 442.2 nm (S2B)
B12	20 m	SWIR, 2202.4 nm (S2A), 442.2 nm (S2B)
```

## SENTINEL DOWNLOAD/CONVERSION BASH SCRIPT - UPDATED FOR NEW PYTHON SCRIPT (SentinelTiff.sh)

```bash
#!/bin/sh
set -e

## BASH SCRIPT TO DOWNLOAD SENTINEL2 IMAGERY AND PROCESS
## RGB SPECTRAL BANDS INTO GEOTIFF OUTPUT

echo "Starting automated download of Sentinel2 imagery and processing RGB bands to Geotiff Output"
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
```

## DIRECTORY LOCATIONS (Sentinel data download files)

On the Ubuntu box, navigate to the following directory to find the bash script above and relevant files contained within

```bash
cd /mnt/GetData

ls
SentinelTiff.sh  corbettNP.json  file.py  park.json  sentinel.py
```

## Mount drive on reboot

Enter the following command when rebooting drive to mount /mnt:

```
>sudo mount -t xfs -o nouuid /dev/nvme1n1 /mnt
```

I will try to set this up in fstab so that it mounts on reboot.

### Production

TODO

## Usage

TODO

## Roadmap

- [x] Initial Research
- [x] Minimum viable product
- [x] Alpha Release
- [x] Imre took over
- [ ] Feature-Complete Release


## License

TODO
