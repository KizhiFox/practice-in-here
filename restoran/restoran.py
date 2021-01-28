import asyncio
import json
import requests
import timeit
from bs4 import BeautifulSoup
from aiohttp import ClientSession
#import random


def get_cities(code):
    """
    Список городов в стране
    :param str code: Код страны
    :return list: Список городов
    """
    page = requests.get(f'https://restoran.{code}/')
    soup = BeautifulSoup(page.text, features='html.parser')
    dropdown = soup.find('div', {'class': 'header-base__city-select-wrap'})
    all_links = dropdown.find_all('a', {'class': 'dropdown-item'})
    cities_links = list(filter(lambda x: not x.has_attr('rel'), all_links))
    cities = [{'city': x.find('span').text, 'url': x['href']} for x in cities_links]
    return cities


def get_categories():
    """
    Типы заведений
    :return list: Типы заведений
    """
    page = requests.get('https://restoran.kz/')
    soup = BeautifulSoup(page.text, features='html.parser')
    selector = soup.find('div', {'class': 'sausage-nav sausage-nav_buttons_raised header-nav__sausage-nav'})
    links = selector.find_all('a')
    types = [{'name': x.find('span').text, 'url': x['href']} for x in links]
    return types


async def fetch_by_page(url, session):
    """
    Постраничный просмотр выбранного списка
    :param dict url: словарь с параметрами: url, city, category
    :param ClientSession session: сессия
    :return list: список заведений
    """
    try:
        async with session.get(url['url']) as response:
            soup = BeautifulSoup(await response.read(), features='html.parser')
            #if random.randint(1, 50) == 1:
            #    raise Exception
    except:
        return [{'TimeoutError': True, 'city': url['city'], 'category': url['category']}]
    restaurants = []
    while True:
        cards = soup.find_all('div', {'class': 'place-list-card'})
        for card in cards:
            restaurants.append({
                'city': url['city']['city'],
                'name': card.find('a', {'class': 'link-inherit-color'}).text.strip(),
                'category': url['category']['name'],
                'url': f'{url["city"]["url"][:-1]}{card.find("a", {"class": "link-inherit-color"})["href"]}'
            })
        pagination = soup.find('ul', {'class': 'pagination'})
        if pagination is None:
            break
        links_rel = pagination.find_all('a', {'rel': True})
        links_next = list(filter(lambda x: x.get('rel')[0] == 'next', links_rel))
        if len(links_next) == 0:
            break
        try:
            async with session.get(f'{url["city"]["url"][:-1]}{links_next[0]["href"]}') as response:
                soup = BeautifulSoup(await response.read(), features='html.parser')
        except:
            return [{'TimeoutError': True, 'city': url['city'], 'category': url['category']}]
    return restaurants


async def fetch_geo(rest, session):
    """
    Получение геоданных со страницы заведений
    :param dict rest: заведение
    :param ClientSession session: сессия
    :return dict: заведение с геоданными
    """
    try:
        async with session.get(rest['url']) as response:
            soup = BeautifulSoup(await response.read(), features='html.parser')
        #if random.randint(1, 100) == 1:
        #    raise Exception
    except:
        rest['TimeoutError'] = True
        return rest
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


async def fetch_all(items, fetch_function):
    """
    Получение заведений по заданным ссылкам
    :param list items: список заведений
    :param Coroutine fetch_function: функция для запросов
    :return list: список заведений
    """
    tasks = []
    async with ClientSession() as session:
        for item in items:
            task = asyncio.ensure_future(fetch_function(item, session))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return results


def get_restaurants(cities, categories):
    """
    Получение списка заведений по заданным городам и категориям
    :param list cities: города, список словарей с параметрами: city, url
    :param list categories: категории, список словарей с параметрами: city, url
    :return list: список заведений без геоданных
    """
    url_list = []
    for city in cities:
        for category in categories:
            url_list.append({'url': f'{city["url"]}{category["url"][1:]}',
                             'city': city,
                             'category': category})
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all(url_list, fetch_by_page))
    results = loop.run_until_complete(future)
    results = [item for sublist in results for item in sublist]
    correct = []
    timed_out = []
    for res in results:
        if 'TimeoutError' in res.keys():
            if {'city': res['city'], 'category': res['category']} not in timed_out:
                timed_out.append({'city': res['city'], 'category': res['category']})
        else:
            correct.append(res)
    return correct, timed_out


def add_geo(restaurants):
    """
    Добавляет адреса и координаты к списку заведений
    :param list restaurants: список заведений без геоданных
    :return (list, list): валидные и не валидные записи
    """
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all(restaurants, fetch_geo))
    restaurants = loop.run_until_complete(future)
    valid = []
    not_valid = []
    timed_out = []
    for rest in restaurants:
        if 'TimeoutError' in rest.keys():
            timed_out.append({'city': rest['city'], 'name': rest['name'], 'category': rest['category'], 'url': rest['url']})
        else:
            if rest['address'] is None or rest['longitude'] is None:
                not_valid.append(f'{rest["url"]}|{rest["address"]}|{rest["longitude"]},{rest["latitude"]}')
            else:
                valid.append(rest)
    return valid, not_valid, timed_out


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
    print('Получение городов...')
    cities = get_cities('kz')
    cities += get_cities('kg')
    print('Получение типов заведений...')
    categories = get_categories()

    print('Получение списка заведений...')
    start = timeit.default_timer()
    restaurants, timed_out = get_restaurants(cities, categories)
    while len(timed_out) != 0:
        print(f'TimeoutError для {len(timed_out)} запросов, повтор...')
        correct, timed_out = get_restaurants([x['city'] for x in timed_out], [x['category'] for x in timed_out])
        restaurants += correct
    stop = timeit.default_timer()
    print(f'Получено {len(restaurants)} заведений за {stop - start} сек.')

    print('Получение геоданных...')
    start = timeit.default_timer()
    valid, not_valid, timed_out = add_geo(restaurants)
    while len(timed_out) != 0:
        print(f'TimeoutError для {len(timed_out)} запросов, повтор...')
        correct, not_correct, timed_out = add_geo(timed_out)
        valid += correct
        not_valid += f'\n{not_correct}'
    stop = timeit.default_timer()
    print(f'Валидные / не валидные записи: {len(valid)} / {len(not_valid)}')

    print(f'Сохранение результатов...')
    to_geojson(valid, 'points.geojson')
    with open('not_valid.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(not_valid))