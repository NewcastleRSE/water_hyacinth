import logging
import os
import zipfile
import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_from_directory

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

def create_log():
    return {
        "messages": []
    }

def log_message(log_store, msg):
    logging.info(msg)
    log_store["messages"].append(msg)

@app.route('/search', methods=['POST'])
def search():
    log_store = create_log()

    # Parse input JSON
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    coordinates = data.get('coordinates')  # e.g. "POINT(-1.62 54.98)"

    if not start_date or not end_date or not coordinates:
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameters: start_date, end_date, or coordinates.'
        }), 400

    username = os.getenv('COPERNICUS_EMAIL')
    password = os.getenv('COPERNICUS_PASSWORD')

    if not username or not password:
        return jsonify({
            'status': 'error',
            'message': 'Missing Copernicus credentials in environment variables.'
        }), 500

    # A helper function that logs while we do the steps
    def get_access_token(email: str, sentinel_password: str, logs):
        log_message(logs, "Requesting access token...")
        data = {
            "client_id": "cdse-public",
            "username": email,
            "password": sentinel_password,
            "grant_type": "password",
        }
        r = requests.post(
            "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            data=data,
        )
        r.raise_for_status()
        log_message(logs, "Access token obtained successfully.")
        return r.json()["access_token"]

    try:
        # 1. Get token
        access_token = get_access_token(username, password, log_store)

        # 2. Construct query
        filter_query = (
            f"Collection/Name eq 'SENTINEL-2' and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{coordinates}') and "
            f"ContentDate/Start gt {start_date}T00:00:00.000Z and "
            f"ContentDate/Start lt {end_date}T23:59:59.999Z and "
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' "
            f"and att/OData.CSC.DoubleAttribute/Value lt 80.00)"
        )

        print("Constructed query:", filter_query)

        # 3. Make request
        log_message(log_store, "Sending query to Copernicus...")
        url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
        params = {
            "$filter": filter_query,
            "$top": "10"
        }

        response = requests.get(
            url,
            params=params,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
        )
        if response.status_code != 200:
            log_message(log_store, f"API Error: {response.status_code}")
            return jsonify({
                'status': 'error',
                'message': f'Copernicus API error: {response.text}',
                'logs': log_store["messages"]
            }), 500

        json_response = response.json()
        if 'value' not in json_response:
            log_message(log_store, "Unexpected API response format")
            return jsonify({
                'status': 'error',
                'message': f"Unexpected API response: {json_response}",
                'logs': log_store["messages"]
            }), 500

        products_df = pd.DataFrame.from_dict(json_response['value'])
        if len(products_df) == 0:
            log_message(log_store, "No products found.")
            return jsonify({
                'status': 'error',
                'message': "No products found. Try adjusting your search parameters.",
                'logs': log_store["messages"]
            }), 200

        log_message(log_store, f"Found {len(products_df)} products")

        # Sort + pick most recent
        products_df["AcquisitionStart"] = products_df["ContentDate"].apply(lambda d: d["Start"])
        products_df = products_df.sort_values("AcquisitionStart", ascending=False)
        product_id = products_df.iloc[0]['Id']
        log_message(log_store, f"Selected most recent product: {product_id}")

        # 4. Download the product
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {access_token}'})
        download_url = (f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value")
        download_response = session.get(download_url, allow_redirects=False)

        redirect_count = 0
        while download_response.status_code in (301, 302, 303, 307) and redirect_count < 5:
            redirect_count += 1
            redirect_url = download_response.headers['Location']
            download_response = session.get(redirect_url, allow_redirects=False)

        if download_response.status_code != 200:
            log_message(log_store, f"Download failed with status code: {download_response.status_code}")
            return jsonify({
                'status': 'error',
                'message': f"Download failed with status code: {download_response.status_code}",
                'logs': log_store["messages"]
            }), 500

        log_message(log_store, "Downloading product zip...")
        file_response = session.get(download_response.url, verify=False, allow_redirects=True)
        with open("sentinel.zip", 'wb') as f:
            f.write(file_response.content)

        # 5. Extract
        dir_name = '../..'
        zip_filename = os.path.join(dir_name, "sentinel.zip")

        # Just check if the file is actually there
        if not os.path.exists(zip_filename):
            log_message(log_store, "Zip file not found after download.")
            return jsonify({
                'status': 'error',
                'message': 'Zip file not found after download.',
                'logs': log_store["messages"]
            }), 500

        log_message(log_store, f"Extracting sentinel.zip in {dir_name}...")
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(dir_name)
        log_message(log_store, f"Extraction complete.")

        return jsonify({
            'status': 'success',
            'message': 'File downloaded and extracted successfully.',
            'logs': log_store["messages"]
        }), 200

    except Exception as e:
        log_message(log_store, f"Unexpected error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'logs': log_store["messages"]
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
