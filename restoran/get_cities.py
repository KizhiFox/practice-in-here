import json
import requests
from bs4 import BeautifulSoup


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


if __name__ == '__main__':
    cities = get_cities('kz')
    cities += get_cities('kg')
    with open('cities.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(cities, ensure_ascii=False, indent=4))
