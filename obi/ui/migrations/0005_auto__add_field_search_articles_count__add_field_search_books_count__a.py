# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Search.articles_count'
        db.add_column(u'ui_search', 'articles_count',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Search.books_count'
        db.add_column(u'ui_search', 'books_count',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Search.database_count'
        db.add_column(u'ui_search', 'database_count',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Search.journals_count'
        db.add_column(u'ui_search', 'journals_count',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)

        # Adding field 'Search.researchguides_count'
        db.add_column(u'ui_search', 'researchguides_count',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Search.articles_count'
        db.delete_column(u'ui_search', 'articles_count')

        # Deleting field 'Search.books_count'
        db.delete_column(u'ui_search', 'books_count')

        # Deleting field 'Search.database_count'
        db.delete_column(u'ui_search', 'database_count')

        # Deleting field 'Search.journals_count'
        db.delete_column(u'ui_search', 'journals_count')

        # Deleting field 'Search.researchguides_count'
        db.delete_column(u'ui_search', 'researchguides_count')


    models = {
        u'ui.database': {
            'Meta': {'object_name': 'Database'},
            'description': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'})
        },
        u'ui.journal': {
            'Meta': {'object_name': 'Journal'},
            'eissn': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'max_length': '9', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issn': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'max_length': '9', 'blank': 'True'}),
            'ssid': ('django.db.models.fields.TextField', [], {'max_length': '13', 'db_index': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        u'ui.search': {
            'Meta': {'object_name': 'Search'},
            'articles_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'blank': 'True'}),
            'books_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'blank': 'True'}),
            'database_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'blank': 'True'}),
            'date_searched': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'journals_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'blank': 'True'}),
            'q': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'blank': 'True'}),
            'researchguides_count': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'blank': 'True'})
        }
    }

    complete_apps = ['ui']