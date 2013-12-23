from django.conf import settings
from django.core.management.base import BaseCommand

import solr

from ui.models import Database, Journal


COMMIT_BLOCK_SIZE = 100


class Command(BaseCommand):
    help = 'index the database list and journal titles list'

    def handle(self, *args, **options):
        # TODO: add an option for zapping the index first
        s = solr.SolrConnection(settings.SOLR_URL)
        qs_databases = Database.objects.all()
        total_indexed = 0
        block = []
        for db in qs_databases:
            block.append({'id': 'db-%s' % db.id,
                          'name': db.name,
                          'url': db.url,
                          'description': db.description})
            if len(block) == COMMIT_BLOCK_SIZE:
                s.add_many(block, _commit=True)
                total_indexed += len(block)
                print 'indexed:', total_indexed, 'databases'
                block = []
        if block:
            s.add_many(block, _commit=True)
            total_indexed += len(block)
            print 'indexed:', total_indexed, '. done.'
            block = []
        total_indexed = 0
        qs_journals = Journal.objects.distinct('ssid')
        for journal in qs_journals:
            block.append({'id': 'j-%s' % journal.id,
                          'name': journal.title,
                          'issn': journal.issn,
                          'eissn': journal.eissn})
            if len(block) == COMMIT_BLOCK_SIZE:
                s.add_many(block, _commit=True)
                total_indexed += len(block)
                print 'indexed:', total_indexed, 'journals'
                block = []
        if block:
            s.add_many(block, _commit=True)
            total_indexed += len(block)
            print 'indexed:', total_indexed, 'journals'
