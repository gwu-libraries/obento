import time
import codecs

import requests

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from ui.models import Journal


class Command(BaseCommand):
    help = 'ingest a comma-delimited table of journal titles where each line \
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

        journalfp = codecs.open(filename, 'rb', encoding='utf-16')

        titleline = journalfp.readline()
        print(titleline)
        
        for line in iter(journalfp):
            print(line)
            if line[0] == "\"":
                lineaux = line.split("\"")
                print("lineaux = ")
                print(lineaux)
                title = lineaux[1]
                valuesaux = lineaux[2].split('\t')
                ssid = valuesaux[1]
                issn = valuesaux[2]
                eissn = valuesaux[3]
            else:
                values = line.split('\t')
                title = values[0]
                ssid = values[1]
                issn = values[2]
                eissn = values[3]

            print(values)

            journal = Journal(title=title, ssid=ssid, issn=issn, eissn=eissn)
            journal.save()
