from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import os, zipfile, shutil, sys
import logging


user = 'brd102' 
password = '*******' 

api = SentinelAPI(user,password,'https://apihub.copernicus.eu/apihub')
dir_name = '/home/ubuntu/py/sentinel/temp/zip'
ZIP_NAME = '/home/ubuntu/py/sentinel/temp/zip'
jp2_directory = '/home/ubuntu/py/sentinel/r10'
extension = ".zip"

# search by polygon, time, and SciHub query keywords
polygon = r'/home/ubuntu/py/json/park.json'
aoi = 'POINT (41.9 12.5)'
footprint = geojson_to_wkt(read_geojson(polygon))

products = api.query(footprint,
                     date=('NOW-110HOURS', 'NOW'),                     
                     platformname='Sentinel-2',
                     processinglevel = 'Level-2A',
                     cloudcoverpercentage=(0, 30))

#Define the path to your AOI - Must be a Geojson shapefile
#Define the products you need - Here you will be looking for Ground Range detected products, with a Descending orbit direction from 01/05/2019 to 01/06/2019 


#products = api.query(aoi,
#                    # date = ('20180401','20180410'),
#                     date=('NOW-200HOURS', 'NOW'),
#                     producttype = 'GRD',
#                     orbitdirection='DESCENDING')

print("There are", len(products),"data files found")

if not products:
    print("No data found, exiting script, goodbye!")
    sys.exit()

#Loggging Follows...

logger = logging.getLogger('sentinelsat')
logger.setLevel('INFO')

h = logging.StreamHandler()
h.setLevel('INFO')
fmt = logging.Formatter('%(message)s')
h.setFormatter(fmt)
logger.addHandler(h)


# download all results from the search
#api.download_all(products)

# convert to Pandas DataFrame
products_df = api.to_dataframe(products)

# sort and limit to first 5 sorted products
products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
products_df_sorted = products_df_sorted.head(5)

# download sorted and reduced products
api.download_all(products_df_sorted.index)

#sys.exit()

#os.chdir(dir_name) # change directory from working dir to dir with files
exclude_directories = set({'r10','R60m','R20m','QI_DATA','AUX_DATA'})    #directory (only names) want to exclude
extensions = ('.jp2')
print ("Unzipping downloaded files into folder and deleting zip files afterwards...")

for item in os.listdir(dir_name): # loop through items in dir
    if item.endswith(extension): # check for zip" extension
        file_name = os.path.abspath(item) # get full path of files
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        zip_ref.extractall(dir_name) # extract file to dir
        zip_ref.close() # close file
#        os.remove(file_name) # delete zipped file

print ("All files unzipped and zip files removed!")
print ()
sys.exit()
print ("Copying jp2 files to r10 folder...")

for root, dirs, files in os.walk(dir_name):
    dirs[:] = [d for d in dirs if d not in exclude_directories] # exclude directory if in exclude list 

    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        if ext in extensions:
            path_file = os.path.join(root,file)
            print (path_file)
            shutil.copy2(path_file,jp2_directory)

print ("All jp2 files copied!")


# convert to Pandas DataFrame
#products_df = api.to_dataframe(products)



# sort and limit to first 5 sorted products
#products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
#products_df_sorted = products_df_sorted.head(5)

# download sorted and reduced products
#api.download_all(products_df_sorted.index)

# GeoJSON FeatureCollection containing footprints and metadata of the scenes

# GeoPandas GeoDataFrame with the metadata of the scenes and the footprints as geometries
#api.to_geodataframe(products)

# Get basic information about the product: its title, file size, MD5 sum, date, footprint and
# its download url
#api.get_product_odata(<product_id>)

# Get the product's full metadata available on the server
#api.get_product_odata(<product_id>, full=True)
