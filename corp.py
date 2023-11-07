import json,zipfile
import requests,sys,os,datetime
import pandas as pd
import datetime as dt 
from datetime import timedelta

now = dt.datetime.today().strftime("%Y-%m-%d")
print(now)

#Setup access token/entry to dataspace access hub...

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

#=====================================#

#Set parameters for data download...

print ("Searching for products to download...")


start_date = "2023-08-15"
end_date = "2023-10-30"
data_collection = "SENTINEL-2"
#aoi = 'POLYGON((73.76637462028609 18.60744222377967,73.76637462028609 18.454997850822508, 73.94931027079727 18.454997850822508,73.94931027079727 18.60744222377967,73.76637462028609 18.60744222377967))'
aoi = 'POLYGON ((77.497559 16.746688, 78.865356 16.799282, 79.656372 16.562493, 79.82666 15.850389, 79.491577 15.337167, 78.651123 15.130462, 77.711792 15.252389, 77.167969 15.850389, 77.102051 16.372851, 77.497559 16.746688))'
#aoi = 'POINT (18.6 73.9)' 

json = requests.get(f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=contains(Name,'S2A') and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 20.00) and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {start_date}T00:00:00.000Z and ContentDate/Start lt {end_date}T00:00:00.000Z").json()

#json = requests.get(f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq {data_collection} and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt {start_date}T00:00:00.000Z and ContentDate/Start lt {end_date}T00:00:00.000Z").json()
#json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=contains(Name,'S2A') and OData.CSC.Intersects(area=geography'SRID=4326;{aoi}') and ContentDate/Start gt 2022-05-03T00:00:00.000Z and ContentDate/Start lt 2022-05-30T00:11:00.000Z").json()
#json = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt 10.00) and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A') and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'orbitDirection' and att/OData.CSC.StringAttribute/Value eq 'ASCENDING') and ContentDate/Start gt 2022-05-03T00:00:00.000Z and ContentDate/Start lt 2022-05-03T04:00:00.000Z&$top=10").json()

#Add Json output to dataframe
df = pd.DataFrame.from_dict(json['value'])
df = df.sort_values(by=['Name'],ascending=False)

#Print out DF 
print(df)

#Take first result (most recent data file) ID from dataframe 
ID = df.iloc[0,1]
print(ID)

#sys.exit()

#=====================================#

#Download data...

session = requests.Session()

session.headers.update({'Authorization': f'Bearer {access_token}'})

url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products("+ ID +")/$value"
print (url)

response = session.get(url, allow_redirects=False)

while response.status_code in (301, 302, 303, 307):
    print ("Downloading file")
    url = response.headers['Location']
    response = session.get(url, allow_redirects=False)
file = session.get(url, verify=False, allow_redirects=True)


with open(f"sentinel.zip", 'wb') as p:
    p.write(file.content)

print ("Done")

#=====================================#

#Unzip file...

dir_name = '.'
extension = ".zip"

print()
print ("Unzipping downloaded files into folders...")

for item in os.listdir(dir_name): # loop through items in dir
    if item.endswith(extension): # check for zip" extension
        file_name = os.path.abspath(item) # get full path of files
        zip_ref = zipfile.ZipFile(file_name) # create zipfile object
        zip_ref.extractall(dir_name) # extract file to dir
        zip_ref.close() # close file
#        os.remove(file_name) # delete zipped file

print ("All files unzipped!")
