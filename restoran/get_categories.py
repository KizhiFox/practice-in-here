import json
import requests
from bs4 import BeautifulSoup


def get_categories():
    """
    Типы заведений
    :return list: Типы заведений
    """
    page = requests.get('https://restoran.kz/')
    soup = BeautifulSoup(page.text, features='html.parser')
    selector = soup.find('div', {'class': 'sausage-nav sausage-nav_buttons_raised header-nav__sausage-nav'})
    links = selector.find_all('a')
    types = [{'name': x.find('span').text, 'link': x['href']} for x in links]
    return types


if __name__ == '__main__':
    types = get_categories()
    with open('categories.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(types, ensure_ascii=False, indent=4))
