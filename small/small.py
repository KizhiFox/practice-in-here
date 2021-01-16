import codecs
import json
import re
from selenium import webdriver


def get_data(cities, driver_patch):
    """
    Возвращает список магазинов по заданным параметрам
    :param list cities: названия городов
    :param str driver_patch: путь к движку Gecko
    :return list: список магазинов
    """
    print('Запуск движка...')
    # Отключение загрузки изображений
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    driver = webdriver.Firefox(executable_path=driver_patch,
                               firefox_profile=firefox_profile)
    driver.get('https://small.kz/')
    points = []
    for city in cities:
        print(city)
        # Нажатие на кнопки в меню выбора города
        elem = driver.find_element_by_xpath('//a[@href="#city-modal"]')
        elem.click()
        elem = driver.find_element_by_class_name('d-flex-center-between-wrap')
        elem = elem.find_element_by_link_text(city)
        elem.click()
        # Поиск строки JS с объявлением списка
        script = driver.find_element_by_xpath("//script[contains(text(), 'let point_list')]").get_attribute('innerHTML')
        js_list = next(x for x in script.split('\n') if 'let point_list' in x)
        # Экспорт в список Python через JSON
        json_list = json.loads(re.sub(r';$', '}', re.sub(r'^\s*let point_list\s*=\s*', '{"points":', js_list)))
        points += json_list['points']
    driver.close()
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
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(json.dumps(output, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    data = get_data(['Алматы', 'Нур-Султан', 'Аксу', 'Талдыкорган', 'Алмалыбак', 'Капчагай', 'Караганда',
                     'Кокшетау', 'Костанай', 'Кызылорда', 'Павлодар', 'Семей', 'Степногорск', 'Талгар',
                     'Тараз', 'Ашибулак', 'Экибастуз'],
                    r'C:\Users\atrem\Documents\coding\heretech\scraping\geckodriver.exe')
    to_geojson(data, 'points.geojson')
