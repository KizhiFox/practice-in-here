# Сохраняет список всех городов, доступных для выбора
from pathlib import Path
from selenium import webdriver

driver_patch = Path.cwd().parent / 'geckodriver.exe'

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
driver = webdriver.Firefox(executable_path=driver_patch,
                           firefox_profile=firefox_profile)
driver.get('https://www.cmd-online.ru/patsientam/gde-sdat-analizy/')
elem = driver.find_element_by_xpath('//button[text()="Выбрать другой"]')
elem.click()
cities = []
for e in driver.find_elements_by_class_name('city-picker__item-val'):
    cities.append(e.text)
with open('cities.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cities))
driver.close()
