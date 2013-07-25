import time

import xlrd

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from ui.models import Journal


class Command(BaseCommand):
    help = 'ingest an .xlsx (Excel) file of journal titles where each line \
            contains:  journal title, SSID, ISSN, eISSN'

    def handle(self, *args, **options):
        try:
            filename = args[0]
        except:
            print 'load_journals <inputfile>'

        cursor = connection.cursor()
        print 'emptying DB'
        cursor.execute('DELETE FROM ui_journal')
        cursor.execute('ALTER SEQUENCE ui_journal_id_seq RESTART WITH 1')
        transaction.commit_unless_managed()
        time.sleep(1)

        book = xlrd.open_workbook(filename, encoding_override='utf-8')
        sh = book.sheet_by_index(0)

        # row 0 contains column headers so skip it
        for rx in range(1, sh.nrows):
            r = sh.row(rx)
            title = r[0].value.encode('utf-8')
            ssid = r[1].value.encode('utf-8')
            issn = r[2].value.encode('utf-8')
            eissn = r[3].value.encode('utf-8')
            journal = Journal(title=title, ssid=ssid, issn=issn, eissn=eissn)
            journal.save()
