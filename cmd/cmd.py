import json
from bs4 import BeautifulSoup
from pathlib import Path
from time import sleep
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def get_data(cities_path, driver_path):
    """
    Возвращает список центров по заданным параметрам
    :param str cities_path: имя файла с городами
    :param str_or_Path driver_path: путь к движку Gecko
    :return list: список центров
    """
    with open(cities_path, 'r', encoding='utf-8') as f:
        cities = list(filter(lambda x: x != '', f.read().split('\n')))
    print('Запуск движка...')
    # Отключение загрузки изображений и CSS
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('permissions.default.stylesheet', 2)
    driver = webdriver.Firefox(executable_path=driver_path,
                               firefox_profile=firefox_profile)
    driver.get('https://www.cmd-online.ru/patsientam/gde-sdat-analizy/')
    # Принятие куки (надпись мешает кликать)
    driver.find_element_by_id('accept-cookies').click()
    points = []
    # Поиск по городам
    for i, city in enumerate(cities, start=1):
        print(f'{i}/{len(cities)}: {city}')
        while True:
            try:
                # Периодически не кликалось because another element <div class="loader is-active"> obscures it
                elem = WebDriverWait(driver, 20).until(
                    ec.visibility_of_element_located((By.CLASS_NAME, 'popup-modal-ajax')))
                # Без понятия, почему, но WebDriverWait until element_to_be_clickable срабатывает не всегда,
                # поэтому повторяем...
                # Меню выбора города
                elem.click()
            except exceptions.ElementClickInterceptedException as e:
                print(f'{str(e)}: повтор...')
                sleep(0.5)
                continue
            break
        # Иногда возникало Unable to locate element: .city-picker__list
        elem = WebDriverWait(driver, 20).until(ec.visibility_of_element_located((By.CLASS_NAME, 'city-picker__list')))
        elem.find_element_by_xpath(f'//*[self::span|self::b][contains(text(), "{city}")]').click()
        # Цикл по офисам
        for e in driver.find_elements_by_class_name('office-list__item'):
            data_json = e.find_element_by_class_name('office-item').get_attribute('data-office')
            data = json.loads(data_json)
            balloon_data = data['point']['balloonData']['balloonContent']
            soup = BeautifulSoup(balloon_data, features='html.parser')
            points.append({'longitude': data['point']['coords'][1],
                           'latitude': data['point']['coords'][0],
                           'address': f'{city}, {soup.find("div", {"class": "office-item__address"}).text}',
                           'working_hours': ', '.join(x.text for x in soup.find_all('li'))})
    driver.close()
    return points


def to_geojson(points, filename):
    """
    Сохраняет список центров в формате GeoJSON
    :param list points: список центров
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
                'address': point['address'],
                'opening_hours': point['working_hours']
            }
        })
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(output, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    data = get_data('cities.txt', Path.cwd().parent / 'geckodriver.exe')
    to_geojson(data, 'points.geojson')
