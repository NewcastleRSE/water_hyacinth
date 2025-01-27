# Import required libraries
# datetime for handling dates and time operations
import datetime as dt
# zipfile for handling compressed data downloads
import zipfile
# os for file and directory operations
import os
# pandas for data manipulation and analysis
import pandas as pd
# requests for making HTTP requests to the Copernicus API
import requests
# dotenv for loading environment variables from a .env file
from dotenv import load_dotenv

# Get current date in YYYY-MM-DD format
now = dt.datetime.today().strftime("%Y-%m-%d")
print(now)


# Function to authenticate with the Copernicus Data Space Ecosystem (CDSE)
def get_access_token(username: str, password: str) -> str:
    """
    Authenticates with CDSE and returns an access token.
    Uses OAuth2 password grant flow.

    Args:
        username: CDSE account email
        password: CDSE account password

    Returns:
        str: Access token for API requests

    Raises:
        Exception: If authentication fails
    """
    data = {
        "client_id": "cdse-public",  # Public client ID for CDSE
        "username": username,
        "password": password,
        "grant_type": "password",  # OAuth2 grant type
    }
    try:
        # Request token from CDSE authentication endpoint
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Access token creation failed. Response from the server was: {r.json()}"
        )
    return r.json()["access_token"]


# Load environment variables from .env file
# Expects COPERNICUS_EMAIL and COPERNICUS_PASSWORD to be defined
load_dotenv()

# Get access token using credentials from environment variables
access_token = get_access_token(
    os.getenv('COPERNICUS_EMAIL'),
    os.getenv('COPERNICUS_PASSWORD')
)

# Search parameters for Sentinel-2 data
print("Searching for products to download...")

# Define temporal and spatial search parameters
start_date = "2023-08-15"  # Start of search period
end_date = "2023-10-30"  # End of search period
data_collection = "SENTINEL-2"

# Area of Interest (AOI) defined as a WKT polygon
# Coordinates are in format: POLYGON ((longitude latitude, ...))
aoi = 'POLYGON ((77.497559 16.746688, 78.865356 16.799282, 79.656372 16.562493, \
        79.82666 15.850389, 79.491577 15.337167, 78.651123 15.130462, \
        77.711792 15.252389, 77.167969 15.850389, 77.102051 16.372851, \
        77.497559 16.746688))'

# Query CDSE catalogue using OData filter
# Filters:
# - Contains 'S2A' in name (Sentinel-2A satellite)
# - Cloud cover less than 20%
# - Intersects with defined AOI
# - Within specified date range
json = requests.get(
    f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=contains(Name,'S2A') "
    f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' "
    f"and att/OData.CSC.DoubleAttribute/Value lt 20.00) "
    f"and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') "
    f"and ContentDate/Start gt {start_date}T00:00:00.000Z "
    f"and ContentDate/Start lt {end_date}T00:00:00.000Z"
).json()

# Convert JSON response to pandas DataFrame and sort by name (descending)
df = pd.DataFrame.from_dict(json['value'])
df = df.sort_values(by=['Name'], ascending=False)

# Display search results
print(df)

# Get ID of most recent image (first row after sorting)
ID = df.iloc[0, 1]
print(ID)

# Download data using access token
session = requests.Session()
session.headers.update({'Authorization': f'Bearer {access_token}'})

# Construct download URL using product ID
url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({ID})/$value"
print(url)

# Handle redirects manually due to authentication requirements
response = session.get(url, allow_redirects=False)
while response.status_code in (301, 302, 303, 307):
    print("Downloading file")
    url = response.headers['Location']
    response = session.get(url, allow_redirects=False)

# Download the actual file
file = session.get(url, verify=False, allow_redirects=True)

# Save downloaded data as zip file
with open(f"sentinel.zip", 'wb') as p:
    p.write(file.content)

print("Done")

# Extract downloaded data
dir_name = '.'  # Current directory
extension = ".zip"

print("\nUnzipping downloaded files into folders...")

# Process all zip files in directory
for item in os.listdir(dir_name):
    if item.endswith(extension):
        file_name = os.path.abspath(item)
        zip_ref = zipfile.ZipFile(file_name)
        zip_ref.extractall(dir_name)
        zip_ref.close()
        # Uncomment to delete zip file after extraction:
        # os.remove(file_name)

print("All files unzipped!")