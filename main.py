import csv
import os
import ssl
import sys
from time import sleep

import wget
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException


def read_csv(filename):
    with open(filename, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        id, lat, lon = csv_reader.fieldnames
        for i in csv_reader:
            yield (i[id], i[lat], i[lon])


def click_as_load_by_xpath(xpath):
    while True:
        try:
            elem = driver.find_element_by_xpath(xpath)
            elem.click()
            print('element was clicked')
            break
        except (NoSuchElementException, ElementNotVisibleException):
            print('waiting untie the page will be fully loaded...')
            sleep(5)
    return elem


def start_scraping(filename, directory):
    driver.get(link)
    assert "ArcGIS Web Application" in driver.title
    click_as_load_by_xpath('//*[@id="jimu_dijit_CheckBox_0"]')  # tick off AmBev Base Consumo Energia checkbox
    click_as_load_by_xpath(
        '//*[@id="jimu_dijit_CheckBox_8"]')  # tick Riscos - Vulnerabilidade a Inundações do Brasil v1.3
    for map_title, lat, lon in read_csv(filename):

        coordinate_string = lat + ' ' + lon
        search_field = click_as_load_by_xpath('//*[@id="esri_dijit_Search_0_input"]')
        search_field.clear()
        search_field.send_keys(coordinate_string)
        click_as_load_by_xpath('//*[@id="esri_dijit_Search_0"]/div/div[2]')  # search buttin
        click_as_load_by_xpath('//*[@id="map_root"]/div[3]/div[1]/div[1]/div/div[6]')  # close pop-up window

        for _ in range(times_zoom_out):
            click_as_load_by_xpath('//*[@id="widgets_ZoomSlider_Widget_33"]/div[2]')  # click zoom out button

        sleep(2)

        click_as_load_by_xpath('//*[@id="dijit__WidgetBase_0"]')  # click printer button
        map_title_field = click_as_load_by_xpath(
            '//*[@id="dijit_form_ValidationTextBox_0"]')  # click the name of the map field
        map_title_field.clear()
        map_title_field.send_keys(map_title)
        click_as_load_by_xpath('//*[@id="dijit__WidgetsInTemplateMixin_0"]/div[2]/div[3]/div')  # click print button
        # click_as_load_by_class_name('printResultHover')
        click_as_load_by_xpath("//div[contains(concat(' ', @class, ' '), ' printResultHover ')]")  # click created PDF
        click_as_load_by_xpath('//*[@id="dijit__WidgetsInTemplateMixin_0"]/div[4]/div')  # clean list with PDFs to print
        elem = driver.find_element_by_tag_name('body')
        window_before = driver.window_handles[0]
        window_after = driver.window_handles[1]
        driver.switch_to.window(window_after)  # focus to just opened window
        pdf_url = driver.current_url
        print('Downloading PDF...')

        wget.download(pdf_url, os.path.join(directory, map_title + '.pdf'))

        print(pdf_url + '\n the above PDF was downloaded')
        driver.close()
        driver.switch_to.window(window_before)
        click_as_load_by_xpath('//*[@id="dijit__WidgetBase_0"]')  # close printer window

    sleep(5)
    driver.quit()


if __name__ == '__main__':

    if len(sys.argv) == 3:
        filename = sys.argv[1]
        directory = sys.argv[2]
    else:
        filename = sys.argv[1]
        directory = 'downloaded_files'

    if not os.path.exists(directory):
        os.makedirs(directory)

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    link = 'https://brasol.maps.arcgis.com/apps/webappviewer/index.html?id=ffcf65aebbc04f40a06da1e9e855b8af'
    times_zoom_out = 3

    driver = webdriver.Chrome(executable_path='chromedriver')

    start_scraping(filename, directory)
