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
        print 'Reading %d rows...' % sh.nrows
        loaded_count = 0
        for rx in range(1, sh.nrows):
            r = sh.row(rx)
            status = r[2].value
            resource_type = r[3].value
            if ((status == "Subscribed") or
                    (status == "Canceled--Perpetual Access")) \
                    and resource_type == "Journal":
                title = r[0].value.encode('utf-8')
                ssid = r[1].value.encode('utf-8')
                issn = r[4].value.encode('utf-8')
                eissn = r[5].value.encode('utf-8')
                journal = Journal(title=title, ssid=ssid, issn=issn,
                                  eissn=eissn)
                journal.save()
                loaded_count += 1
            if rx % 1000 == 0:
                print "Read %d of %d rows, loaded %d titles" % (rx, sh.nrows,
                                                                loaded_count)
        print "Completed loading of %d journals from %d rows." % (loaded_count,
                                                                  sh.nrows)
