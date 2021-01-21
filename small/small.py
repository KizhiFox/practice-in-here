import json
import re
import requests


def get_data(cities_path):
    """
    Возвращает список магазинов по заданным параметрам
    :param str cities_path: путь к файлу со ссылками на города
    :return list: список магазинов
    """
    with open(cities_path, 'r', encoding='utf-8') as f:
        cities = list(filter(lambda x: x != '', f.read().split('\n')))
    points = []
    for i, city in enumerate(cities, start=1):
        print(f'{i}/{len(cities)}: {city}')
        page = requests.get(city)
        # Поиск строки JS с объявлением списка
        script = list(filter(lambda x: 'let point_list' in x, page.text.split('\n')))[0]
        # Экспорт в список Python через JSON
        json_list = json.loads(re.sub(r';$', '}', re.sub(r'^\s*let point_list\s*=\s*', '{"points":', script)))
        points += json_list['points']
    return points


def to_geojson(points, filename):
    """
    Сохраняет список магазинов в формате GeoJSON
    :param list points: список магазинов
    :param str filename: имя файла
    """
    output = {
        'type': 'FeatureCollection',
        'features': []
    }
    for point in points:
        output['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(point['longitude']), float(point['latitude'])]
            },
            'properties': {
                'name': point['name'],
                'address': point['address'],
                'opening_hours': point['working_hours']
            }
        })
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    data = get_data('cities.txt')
    to_geojson(data, 'points.geojson')
