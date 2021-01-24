import asyncio
import json
import timeit
from bs4 import BeautifulSoup
from aiohttp import ClientSession


async def fetch_by_page(url, session):
    """
    Постраничный просмотр выбранного списка
    :param dict url: словарь с параметрами: url, city, category
    :param ClientSession session: сессия
    :return list: список заведений
    """
    async with session.get(url['url']) as response:
        soup = BeautifulSoup(await response.read(), features='html.parser')
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
        async with session.get(f'{url["city"]["url"][:-1]}{links_next[0]["href"]}') as response:
            soup = BeautifulSoup(await response.read(), features='html.parser')
    return restaurants


async def fetch_all(url_list):
    """
    Получение заведений по заданным ссылкам
    :param list url_list: список словарей с параметрами: url, city, category
    :return list: список заведений
    """
    tasks = []
    async with ClientSession() as session:
        for url in url_list:
            task = asyncio.ensure_future(fetch_by_page(url, session))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        flat_res = [item for sublist in results for item in sublist]
    return flat_res


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
    future = asyncio.ensure_future(fetch_all(url_list))
    results = loop.run_until_complete(future)
    return results


if __name__ == '__main__':
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities = json.loads(f.read())
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.loads(f.read())
    start = timeit.default_timer()
    restaurants = get_restaurants(cities, categories)
    stop = timeit.default_timer()
    print(f'Получено {len(restaurants)} заведений за {stop - start} сек.')
    with open('restaurants.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(restaurants, ensure_ascii=False, indent=4))
