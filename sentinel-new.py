import logging
import os
import sys
import zipfile
import pandas as pd
import requests
from dotenv import load_dotenv
import datetime as dt

# Load environment variables
load_dotenv()


def get_access_token(username: str, password: str) -> str:
    """Get access token from Copernicus Data Space Ecosystem"""
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    try:
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
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

# Get access token
access_token = get_access_token(username, password)

# Set up file handling parameters
dir_name = '.'
extension = ".zip"

# Define search parameters
aoi = 'POINT (54.98 1.62)'  # Your area of interest
start_date = (dt.datetime.now() - dt.timedelta(hours=100)).strftime("%Y-%m-%d")
end_date = dt.datetime.now().strftime("%Y-%m-%d")

# Query the new API
print("Searching for products to download...")
try:
    json_response = requests.get(
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
        params={
            "$filter": f"""
                platformname eq 'Sentinel-2' and 
                processinglevel eq 'Level-2A' and 
                OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and 
                ContentDate/Start gt {start_date}T00:00:00.000Z and 
                ContentDate/Start lt {end_date}T00:00:00.000Z and 
                Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCoverPercentage' 
                and att/OData.CSC.DoubleAttribute/Value lt 20.00)
            """
        }
    ).json()

    # Convert to DataFrame
    if 'value' in json_response:
        products_df = pd.DataFrame.from_dict(json_response['value'])

        if len(products_df) == 0:
            print("No products found")
            sys.exit(0)

        # Sort by date and get most recent
        products_df = products_df.sort_values('ContentDate', ascending=False)
        product_id = products_df.iloc[0]['Id']

        # Set up session for download
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {access_token}'})

        # Download the product
        url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
        response = session.get(url, allow_redirects=False)

        while response.status_code in (301, 302, 303, 307):
            print("Following redirect...")
            url = response.headers['Location']
            response = session.get(url, allow_redirects=False)

        file = session.get(url, verify=False, allow_redirects=True)

        # Save the file
        with open("sentinel.zip", 'wb') as f:
            f.write(file.content)

        # Extract the file
        print("\nUnzipping downloaded files...")
        for item in os.listdir(dir_name):
            if item.endswith(extension):
                file_name = os.path.abspath(item)
                with zipfile.ZipFile(file_name) as zip_ref:
                    zip_ref.extractall(dir_name)
                # Uncomment to remove zip after extraction
                # os.remove(file_name)

        print("All files unzipped!")

except Exception as e:
    logging.error(f"Error occurred: {e}")
    sys.exit(1)