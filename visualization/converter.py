import json


with open('points.geojson', 'r', encoding='utf-8') as f:
    geojson = json.loads(f.read())
csv = ['ADDRESS;ORIGINAL_LAT;ORIGINAL_LNG']
for point in geojson['features']:
    if type(point['geometry']['coordinates'][1]) != float or type(point['geometry']['coordinates'][0]) != float:
        print(point['geometry']['coordinates'])
        print(point['properties']['address'])
    csv.append(f"{point['properties']['address']};{point['geometry']['coordinates'][1]};{point['geometry']['coordinates'][0]}")
with open('points.csv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(csv))
