import logging
import os
import sys
import zipfile

import pandas as pd
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress urllib3 warnings
import warnings

warnings.filterwarnings("ignore", category=Warning)

# Load environment variables
load_dotenv()


def get_access_token(email: str, sentinel_password: str) -> str:
    """Get access token from Copernicus Data Space Ecosystem"""
    data = {
        "client_id": "cdse-public",
        "username": email,
        "password": sentinel_password,
        "grant_type": "password",
    }

    logging.info("Requesting access token...")
    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
        logging.info("Access token obtained successfully")
        return r.json()["access_token"]
    except Exception as e:
        logging.error(f"Access token creation failed: {e}")
        sys.exit(1)


# Get credentials from environment variables
username = os.getenv('COPERNICUS_EMAIL')
password = os.getenv('COPERNICUS_PASSWORD')

if not username or not password:
    logging.error("Missing Copernicus credentials in .env file")
    sys.exit(1)

logging.info(f"Using credentials for user: {username}")

# Get access token
access_token = get_access_token(username, password)

# Set up file handling parameters
dir_name = '../..'
extension = ".zip"

# Define search parameters
# aoi = 'POINT(54.98 1.62)'
aoi = 'POINT(-1.62 54.98)'

# Explicit set dates
start_date = "2023-12-01"
end_date = "2024-01-20"

logging.info(f"Searching for products between {start_date} and {end_date}")
logging.info(f"Area of interest: {aoi}")

# Construct the query with explicit dates
filter_query = (
    f"Collection/Name eq 'SENTINEL-2' and "
    f"OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and "
    f"ContentDate/Start gt {start_date}T00:00:00.000Z and "
    f"ContentDate/Start lt {end_date}T23:59:59.999Z and "
    f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' "
    f"and att/OData.CSC.DoubleAttribute/Value lt 80.00)"
    # f"and att/OData.CSC.DoubleAttribute/Value lt 20.00)"
)

# Query the API
try:
    logging.info("Sending API request...")

    url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    params = {
        "$filter": filter_query,
        "$top": "10"  # Limit results to 10 items
    }

    response = requests.get(
        url,
        params=params,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
    )

    # Log the actual URL being called (for debugging)
    logging.info(f"Request URL: {response.url}")

    if response.status_code != 200:
        logging.error(f"API Error: {response.status_code}")
        logging.error(f"Response: {response.text}")
        sys.exit(1)

    json_response = response.json()
    logging.info("API response received")

    if 'value' not in json_response:
        logging.error("Unexpected API response format")
        logging.debug(f"Response content: {json_response}")
        sys.exit(1)

    products_df = pd.DataFrame.from_dict(json_response['value'])

    if len(products_df) == 0:
        logging.info("No products found matching the criteria")
        logging.info("Try adjusting the search parameters (date range, cloud cover, or location)")
        sys.exit(0)

    logging.info(f"Found {len(products_df)} products")

    # Display available products
    for idx, product in products_df.iterrows():
        logging.info(
            f"Product {idx + 1}: {product.get('Name', 'Unknown')} - Date: {product.get('ContentDate', 'Unknown')}")

    # Sort by date and get the most recent
    # Convert the 'ContentDate' column to a new column 'AcquisitionStart',
    # extracting the 'Start' key from the dictionary
    products_df["AcquisitionStart"] = products_df["ContentDate"].apply(lambda d: d["Start"])

    # Now you can sort by 'AcquisitionStart', which is a string or can be parsed as a datetime
    products_df = products_df.sort_values("AcquisitionStart", ascending=False)
    # products_df = products_df.sort_values('ContentDate', ascending=False)
    product_id = products_df.iloc[0]['Id']
    logging.info(f"Selected most recent product: {product_id}")

    # Set up session for download
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {access_token}'})

    # Download the product
    url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
    logging.info(f"Starting download from: {url}")

    response = session.get(url, allow_redirects=False)
    redirect_count = 0

    while response.status_code in (301, 302, 303, 307) and redirect_count < 5:
        redirect_count += 1
        url = response.headers['Location']
        logging.info(f"Following redirect {redirect_count} to: {url}")
        response = session.get(url, allow_redirects=False)

    if response.status_code != 200:
        logging.error(f"Download failed with status code: {response.status_code}")
        logging.error(f"Response content: {response.text}")
        sys.exit(1)

    file = session.get(url, verify=False, allow_redirects=True)

    # Save the file
    logging.info("Saving downloaded file...")
    with open("sentinel.zip", 'wb') as f:
        f.write(file.content)

    logging.info("File saved successfully")

    # Extract the file
    logging.info("Starting file extraction...")
    for item in os.listdir(dir_name):
        if item.endswith(extension):
            file_name = os.path.abspath(item)
            with zipfile.ZipFile(file_name) as zip_ref:
                zip_ref.extractall(dir_name)
            logging.info(f"Extracted: {file_name}")

    logging.info("Process completed successfully")

except requests.exceptions.RequestException as e:
    logging.error(f"API request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        logging.error(f"Response content: {e.response.text}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    sys.exit(1)
