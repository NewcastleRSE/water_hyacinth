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
This is as follows:

* Step 1 rm -rf /home/ubuntu/py/json/*.json (this removes the exisiting json files previosly converted from the folder)

* Step 2 python3 shptojson.py (this is script that converts the shapefiles to json files and saves them in /home/ubuntu/py/json

* Step 3 geojson-merge json/*.json > json/mergebig.json (this merges the created converted json files into 1 geojson file for overlay on leaflet map)

* Step 4 cp json/mergebig.json /var/www/html/poly/json (this copies the combined geojson file into the web folder ready for access via the web server)



### Local

Deploying to a production style setup but on the local system. Examples of this would include `venv`, `anaconda`, `Docker` or `minikube`. 

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
