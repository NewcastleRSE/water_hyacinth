# Import required libraries
import logging  # For creating log messages during script execution
import os       # For file and directory operations
import sys      # For system-specific functions like exiting the script
import zipfile  # For handling compressed files
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt  # Sentinel satellite data access utilities

# Sentinel Hub authentication credentials

# Implement something similar
# access_token = get_access_token(
#     os.getenv('COPERNICUS_EMAIL'),
#     os.getenv('COPERNICUS_PASSWORD')
# )

user = os.getenv('COPERNICUS_EMAIL')
password = os.getenv('COPERNICUS_PASSWORD')

# Initialize API connection to Copernicus Open Access Hub
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')

# Set up file handling parameters
dir_name = '.'      # Current directory
extension = ".zip"  # File extension to process

# Define search area and load geographical data
polygon = r'park.json'  # Path to GeoJSON file containing area of interest
aoi = 'POINT (54.98 1.62)'  # Alternative point-based search location
# Convert GeoJSON to Well-Known Text format that Sentinel API understands
footprint = geojson_to_wkt(read_geojson(polygon))

# Query Sentinel data with specific parameters
products = api.query(aoi,
                    date=('NOW-100HOURS', 'NOW'),  # Last 100 hours
                    platformname='Sentinel-2',      # Specify satellite
                    processinglevel='Level-2A',     # Processing level of data
                    cloudcoverpercentage=(0, 20))   # Max 20% cloud cover

# Alternative query parameters (commented out but kept for reference)
#products = api.query(aoi,
#                    date=('NOW-200HOURS', 'NOW'),
#                    producttype = 'GRD',           # Ground Range Detected
#                    orbitdirection='DESCENDING')

# Check if any products were found
print("There are", len(products), "data files found")
if not products:
    print("No data found, exiting script, goodbye!")
    sys.exit()

# Set up logging configuration
logger = logging.getLogger('sentinelsat')
logger.setLevel('INFO')  # Set logging level
h = logging.StreamHandler()  # Handler to output log to console
h.setLevel('INFO')
fmt = logging.Formatter('%(message)s')  # Simple message format
h.setFormatter(fmt)
logger.addHandler(h)

# Convert query results to pandas DataFrame for easier handling
products_df = api.to_dataframe(products)

# Sort products by cloud cover and ingestion date, keep only the newest
products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], 
                                           ascending=[True, True])
products_df_sorted = products_df_sorted.head(1)  # Keep only the best match

# Download the selected products
api.download_all(products_df_sorted.index)

# Extract downloaded files
print("\nUnzipping downloaded files into folders...")
for item in os.listdir(dir_name):
    if item.endswith(extension):
        file_name = os.path.abspath(item)  # Get full path
        zip_ref = zipfile.ZipFile(file_name)  # Create zipfile object
        zip_ref.extractall(dir_name)  # Extract all contents
        zip_ref.close()
        # Optionally delete zip file after extraction:
        #os.remove(file_name)

print("All files unzipped!")
print()
sys.exit()

# Additional functionality examples (commented out):
# Convert results to different formats
#products_df = api.to_dataframe(products)
#products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'],
#                                           ascending=[True, True])
#products_df_sorted = products_df_sorted.head(5)
#api.download_all(products_df_sorted.index)

# Get detailed metadata
#api.to_geodataframe(products)
#api.get_product_odata(<product_id>)
#api.get_product_odata(<product_id>, full=True)

#==============================================

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