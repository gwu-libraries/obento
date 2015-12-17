import requests
import solr

from django.conf import settings

from ui.models import Database, Journal


COMMIT_BLOCK_SIZE = 100


def index_databases(clearindex=True):
    s = solr.SolrConnection(settings.SOLR_URL)
    # unless the user gives a --no-clear option, clear the solr index.
    if clearindex:
        requests.get(settings.SOLR_URL + '/update' +
                     '?stream.body=<delete><query>id:db-*</query></delete>')
        requests.get(settings.SOLR_URL + '/update' +
                     '?stream.body=<commit/>')
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
        print 'indexed:', total_indexed, 'databases -- done.'


def index_journals(clearindex=True):
    s = solr.SolrConnection(settings.SOLR_URL)
    # unless the user gives a --no-clear option, clear the solr index.
    if clearindex:
        requests.get(settings.SOLR_URL + '/update' +
                     '?stream.body=<delete><query>id:j-*</query></delete>')
        requests.get(settings.SOLR_URL + '/update' +
                     '?stream.body=<commit/>')
    total_indexed = 0
    block = []
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
        print 'indexed:', total_indexed, 'journals -- done.'
