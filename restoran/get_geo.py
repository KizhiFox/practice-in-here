import asyncio
import json
import timeit
from bs4 import BeautifulSoup
from aiohttp import ClientSession



async def fetch_geo(rest, session):
    """
    Получение геоданных со страницы заведений
    :param dict rest: заведение
    :param ClientSession session: сессия
    :return dict: заведение с геоданными
    """
    async with session.get(rest['url']) as response:
        soup = BeautifulSoup(await response.read(), features='html.parser')
    try:
        rest['address'] = f'{rest["city"]}, {soup.find("div", {"class": "text-overflow mt-2"}).getText()}'
    except AttributeError:
        rest['address'] = None
    try:
        road_button = soup.find('button', {'class': 'btn btn-classic take-route-btn'})
        button_data = json.loads(road_button['data-coordinates'])
        rest['longitude'] = float(button_data['longitude'])
        rest['latitude'] = float(button_data['latitude'])
    except TypeError:
        rest['longitude'] = None
        rest['latitude'] = None
    return rest


async def fetch_all_geo(restaurants):
    """
    Получение геоданных по заданным ссылкам
    :param list restaurants: список заведений без геоданных
    :return list: список заведений с геоданными
    """
    tasks = []
    async with ClientSession() as session:
        for rest in restaurants:
            task = asyncio.ensure_future(fetch_geo(rest, session))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return results


def add_geo(restaurants):
    """
    Добавляет адреса и координаты к списку заведений
    :param list restaurants: список заведений без геоданных
    :return (list, list): валидные и не валидные записи
    """
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all_geo(restaurants))
    restaurants = loop.run_until_complete(future)
    valid = []
    not_valid = []
    for rest in restaurants:
        if rest['address'] is None or rest['longitude'] is None:
            not_valid.append(f'{rest["url"]}|{rest["address"]}|{rest["longitude"]},{rest["latitude"]}')
        else:
            valid.append(rest)
    return valid, not_valid


def to_geojson(points, filename):
    """
    Сохраняет список заведений в формате GeoJSON
    :param list points: список заведений
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
                'coordinates': [point['longitude'], point['latitude']]
            },
            'properties': {
                'name': point['name'],
                'category': point['category'],
                'city': point['city'],
                'address': point['address'],
                'url': point['url']
            }
        })
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    with open('restaurants.json', 'r', encoding='utf-8') as f:
        restaurants = json.loads(f.read())
    start = timeit.default_timer()
    valid, not_valid = add_geo(restaurants)
    stop = timeit.default_timer()
    print(f'Получено {len(restaurants)} заведений за {stop - start} сек. Валидные / не валидные: {len(valid)}/{len(not_valid)}')
    to_geojson(valid, 'points.geojson')
    with open('not_valid.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(not_valid))
