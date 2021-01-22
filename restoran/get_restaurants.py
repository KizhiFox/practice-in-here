import json
import requests
from bs4 import BeautifulSoup


def get_restaurants(cities, categories):
    restaurants = []
    for city in cities:
        for category in categories:
            page = requests.get(f'{city["link"]}{category["link"][1:]}')
            soup = BeautifulSoup(page.text, features='html.parser')
            while True:
                print(page.url)
                cards = soup.find_all('div', {'class': 'place-list-card'})
                for card in cards:
                    restaurants.append({
                        'city': city['city'],
                        'name': card.find('a', {'class': 'link-inherit-color'}).text.strip(),
                        'category': category['name'],
                        'link': f'{city["link"][:-1]}{card.find("a", {"class": "link-inherit-color"})["href"]}'
                    })
                pagination = soup.find('ul', {'class': 'pagination'})
                links_rel = pagination.find_all('a', {'rel': True})
                links_next = list(filter(lambda x: x.get('rel')[0] == 'next', links_rel))
                if len(links_next) == 0:
                    break
                else:
                    page = requests.get(f'{city["link"][:-1]}{links_next[0]["href"]}')
                    soup = BeautifulSoup(page.text, features='html.parser')
    return restaurants


if __name__ == '__main__':
    with open('cities.json', 'r', encoding='utf-8') as f:
        cities = json.loads(f.read())
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.loads(f.read())
    restaurants = get_restaurants(cities, categories)
    with open('restaurants.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(restaurants, ensure_ascii=False, indent=4))
