# Сохраняет список ссылок на все города, доступные для выбора
from pathlib import Path
from selenium import webdriver

driver_path = Path.cwd().parent / 'geckodriver.exe'

firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
driver = webdriver.Firefox(executable_path=driver_path,
                           firefox_profile=firefox_profile)
driver.get('https://small.kz/')
driver.find_element_by_xpath('//a[@href="#city-modal"]').click()
elem = driver.find_element_by_id('city-modal')
buttons = elem.find_elements_by_xpath('/html/body/div[2]/div/div/div/div/form')
with open('cities.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(f'https://small.kz/ru/{x.get_attribute("id")}/shops' for x in buttons))
driver.close()
