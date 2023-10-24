#  Invasive Water Hyacinth Project
A project to identify invasive water hyacinth through satellite imagery layered onto a mapping interface

## About
This project will take satellite imagery (sentinel) from the satellite host and then pre-process it using an API before being fed into an algorithm for post-processing
and outputting to a shape file. This shapefile would then be uploaded to a webmap for visual overlay display. This process would consist of converting the shapefile to a GeoJSON and then combining
with exisiting GeoJSON files to create an overlay which can be switched on or off on the webmap. 

### Project Team
Deepayan Bhowmik <Deepayan.Bhowmik@newcastle.ac.uk>  

### RSE Contact
Ben Daly  
RSE Team  
Newcastle University  


## Built With
Leaflet Mapping
Python
JavaScript

## Getting Started

### Prerequisites
This app runs on a Ubuntu instance of AWS and can be accessed via SSH into the AWS box as follows:
It requires download of the key UBUNTU.pem which can be found in the AWS console
Once downloaded, run the following command from the same directory:

>  ssh -i "ubuntu.pem" ubuntu@ec2-16-16-213-96.eu-north-1.compute.amazonaws.com

### Folders
Once logged into the AWS box, you will be in the home directory (/home/ubuntu)
To access the app install folders navigate to the following directory:

> cd /var/www/html/poly

This contains the following 3 files:
* index.html (index page)
* style.css (css)
* script.js (Leaflet JS)

## Coverting Shapefile to GeoJSON Pipeline...

There is a staging process for converting shapefiles to a combined GeoJSON file for display on the Leaflet map. This is done within a bash script called merge.sh
Firstly the shapefiles should be downloaded into the directory /home/ubuntu/py/shp

```
===================================================
#!/bin/sh

rm -rf /home/ubuntu/py/json/*.json
python3 shptojson.py
geojson-merge json/*.json > json/mergebig.json
mapshaper json/mergebig0.json -simplify dp 10% keep-shapes -o format=geojson json/mergebig.json
cp json/mergebig.json /var/www/html/poly/json

This is as follows:

* rm -rf /home/ubuntu/py/json/*.json
  (this removes the exisiting json files previosly converted from the folder)

* python3 shptojson.py
  (this is script that converts the shapefiles to json files and saves them in /home/ubuntu/py/json

* geojson-merge json/*.json > json/mergebig0.json
  (this merges the created converted json files into 1 geojson file for overlay on leaflet map)

* mapshaper json/mergebig0.json -simplify dp 10% keep-shapes -o format=geojson json/mergebig.json
  (this refactors the geojson to a much smaller (and more responsive) size)

* cp json/mergebig.json /var/www/html/poly/json
  (this copies the combined geojson file into the web folder ready for access via the web server)
```


### SENTINEL2 IMAGE DATA

Sentinel 2 data can be downloaded using a API Script such as the following 
```
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
## SENTINEL2 BANDS
```
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

### Production

Deploying to the production system. Examples of this would include cloud, HPC or virtual machine. 

## Usage

Any links to production environment, video demos and screenshots.

## Roadmap

- [x] Initial Research  
- [ ] Minimum viable product <-- You are Here  
- [ ] Alpha Release  
- [ ] Feature-Complete Release  

## Contributing

### Main Branch
Protected and can only be pushed to via pull requests. Should be considered stable and a representation of production code.

### Dev Branch
Should be considered fragile, code should compile and run but features may be prone to errors.

### Feature Branches
A branch per feature being worked on.

https://nvie.com/posts/a-successful-git-branching-model/

## License

## Citation

Please cite the associated papers for this work if you use this code:

```
@article{xxx2023paper,
  title={Title},
  author={Author},
  journal={arXiv},
  year={2023}
}
```


## Acknowledgements
This work was funded by a grant from the UK Research Councils, EPSRC grant ref. EP/L012345/1, “Example project title, please update”.
