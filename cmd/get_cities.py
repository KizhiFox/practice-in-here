# Сохраняет список всех городов, доступных для выбора
import codecs
from selenium import webdriver


firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
driver = webdriver.Firefox(executable_path=r'C:\Users\atrem\Documents\coding\heretech\scraping\geckodriver.exe',
                           firefox_profile=firefox_profile)
driver.get('https://www.cmd-online.ru/patsientam/gde-sdat-analizy/')
elem = driver.find_element_by_xpath('//button[text()="Выбрать другой"]')
elem.click()
cities = []
for e in driver.find_elements_by_class_name('city-picker__item-val'):
    cities.append(e.text)
with codecs.open('cities.txt', 'w', 'utf-8') as f:
    f.write('\n'.join(cities))
driver.close()
