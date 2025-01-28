import os
import shapefile

# Getting the current work directory (cwd)
path = '/home/ubuntu/json/IND'
os.chdir(path)


# r=root, d=directories, f = files
for root, directory, files in os.walk(path):
    for f in files:
        if f.endswith('.shp'):
            name = f[:-4]
            print(name)
            file = os.path.join(root,f)
            print(file)
           # read the shapefile
            reader = shapefile.Reader(file)
            fields = reader.fields[1:]
            field_names = [field[0] for field in fields]
            buffer = []
            for sr in reader.shapeRecords():
                atr = dict(zip(field_names, sr.record))
                geom = sr.shape.__geo_interface__
                buffer.append(dict(type="Feature", geometry=geom, properties=atr)) 

           # write the GeoJSON file
            from json import dumps
            json_file = ("%s.json")%name
            geojson = open(json_file,"w")
            geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
            print(geojson)
            geojson.close()

