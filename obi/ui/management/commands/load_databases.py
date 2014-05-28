import time

from bs4 import BeautifulSoup
import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from ui.models import Database


SLEEP_SECONDS = 2


class Command(BaseCommand):
    help = 'parse the a-z list of GW Libraries databases in libguides'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        print 'emptying DB'
        cursor.execute('DELETE FROM ui_database')
        cursor.execute('ALTER SEQUENCE ui_database_id_seq RESTART WITH 1')
        transaction.commit_unless_managed()
        time.sleep(1)

        for page_sid in settings.LIBGUIDES_DB_PAGE_SIDS:
            params = {'pid': settings.LIBGUIDES_DB_PID, 'sid': page_sid}
            print 'SID:', page_sid
            try:
                r = requests.get(settings.LIBGUIDES_DB_BASE_URL,
                                 params=params)
                print r.encoding, r.status_code, r.url
                soup = BeautifulSoup(r.text)
                itemlists = soup.find_all('div', class_='itemlist')
                for itemlist in itemlists:
                    items = itemlist.find_all('li')
                    for item in items:
                        # skip if there's no <a> tag
                        # this is the case for discontinued databases
                        if item.a is None:
                            continue
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
