import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

from bs4 import BeautifulSoup
import requests
import traceback

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from ui.models import Database

SLEEP_SECONDS = 2


class Command(BaseCommand):
    help = 'parse the a-z list of GW Libraries databases in libguides'

    def retrieve_html(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_driver_path = os.path.abspath(settings.CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(chrome_options=chrome_options,
                                  executable_path=chrome_driver_path)
        driver.get(settings.DATABASES_URL)
        time.sleep(5)
        html = driver.execute_script("return document.documentElement.innerHTML")
        return(html.encode('utf-8'))

    def handle(self, *args, **options):
        cursor = connection.cursor()
        print 'emptying DB'
        cursor.execute('DELETE FROM ui_database')
        cursor.execute('ALTER SEQUENCE ui_database_id_seq RESTART WITH 1')
        cursor.close()
        time.sleep(1)

        loaded_count = 0

        try:
            page_html = self.retrieve_html()
            soup = BeautifulSoup(page_html, "lxml")

            itemlists = soup.find_all('div', class_='s-lg-az-result')
            for itemlist in itemlists:
                name_div = itemlist.find('div', class_='s-lg-az-result-title')
                if name_div is None:
                    continue
                if name_div.a is None:
                    continue
                url = name_div.a.get('href')
                name = name_div.a.contents[0]
                description = ''
                if itemlist.find('div', class_='s-lg-az-result-description'):
                    description = itemlist.find('div', class_=
                                                's-lg-az-result-description'
                                                ).get_text()
                database = Database(name=name, url=url,
                                    description=description)
                database.save()
                loaded_count += 1
        except:
            print traceback.print_exc()
        print("Completed loading of %d database titles and descriptions" %
              loaded_count)
