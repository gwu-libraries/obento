from django.conf import settings
from django.core.management.base import BaseCommand

import solr

from ui.models import Database


COMMIT_BLOCK_SIZE = 100


class Command(BaseCommand):
    help = 'index the database list'

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
                print 'indexed:', total_indexed
                block = []
        if block:
            s.add_many(block, _commit=True)
            total_indexed += len(block)
            print 'indexed:', total_indexed, '. done.'
