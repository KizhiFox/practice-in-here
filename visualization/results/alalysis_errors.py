import json
# 'ADDRESS', 'ORIGINAL_LAT', 'ORIGINAL_LNG', 'LABEL', 'COUNTRY', 'ADMIN3', 'CITY', 'POSTALCODE', 'LAT', 'LNG',
# 'ACCESS_LAT', 'ACCESS_LNG', 'RESULT_TYPE', 'HOUSE_NUMBER_TYPE', 'QUERY_SCORE', 'CITY_SCORE', 'STREET_SCORE',
# 'HOUSE_NUMBER_SCORE', 'distances'
with open('cmd_geocoded_points.geojson', 'r', encoding='utf-8') as f:
    features = json.loads(f.read())['features']
    geocoded = [x['properties'] for x in features]
with open('cmd_none_points.geojson', 'r', encoding='utf-8') as f:
    none = len(json.loads(f.read())['features'])
print(geocoded[0].keys())
small = 0
medium = 0
large = 0
huge = 0
error = 0
geocoded_error = 0
for point in geocoded:
    if point['distances'] > 1000 and point['QUERY_SCORE'] < 0.9:
        geocoded_error += 1
    elif point['distances'] > 1000:
        error += 1
    elif point['distances'] > 100:
        huge += 1
    elif point['distances'] > 30:
        large += 1
    elif point['distances'] > 10:
        medium += 1
    else:
        small += 1
summ = none + small + medium + large + huge + error + geocoded_error
print('Небольшая:', small, small / summ)
print('Средняя:', medium, medium / summ)
print('Большая:', large, large / summ)
print('Огромная:', huge, huge / summ)
print('Определённо ошибка:', error, error / summ)
print('Ошибка геокодера:', geocoded_error, geocoded_error / summ)
print('Адрес не распознан:', none, none / summ)
