import time

from bs4 import BeautifulSoup
import requests

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from ui.models import Database


SLEEP_SECONDS = 2

# e.g.: http://libguides.gwu.edu/content.php?pid=98717&sid=1719900
BASE_URL = 'http://libguides.gwu.edu/content.php'
PID = 98717

PAGE_SIDS = [
    '1943946',
    '1719891',
    '1719892',
    '1719893',
    '1719894',
    '1719895',
    '1719896',
    '1719897',
    '1719898',
    '1719899',
    '1719900',
    '1719901',
    '1719902',
    '1719903',
    '1719904',
    '1719905',
    '1719906',
    '1719908',
    '1719909',
    '1719910',
    '1719911',
    '1719913',
    '1719914',
    '1719916',
    '1719917',
]


class Command(BaseCommand):
    help = 'parse the a-z list of GW Libraries databases in libguides'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        print 'emptying DB'
        cursor.execute('DELETE FROM ui_database')
        cursor.execute('ALTER SEQUENCE ui_database_id_seq RESTART WITH 1')
        transaction.commit_unless_managed()
        time.sleep(1)

        for page_sid in PAGE_SIDS:
            params = {'pid': PID, 'sid': page_sid}
            print 'SID:', page_sid
            try:
                r = requests.get(BASE_URL, params=params)
                print r.encoding, r.status_code, r.url
                soup = BeautifulSoup(r.text)
                itemlists = soup.find_all('div', class_='itemlist')
                for itemlist in itemlists:
                    items = itemlist.find_all('li')
                    for item in items:
                        name = item.a.string
                        url = item.a.get('href')
                        description = item.div.get_text()
                        database = Database(name=name, url=url,
                                            description=description)
                        database.save()
            except:
                import traceback
                print traceback.print_exc()
                print 'ERROR'
            time.sleep(SLEEP_SECONDS)
