# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Search'
        db.create_table(u'ui_search', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('q', self.gf('django.db.models.fields.TextField')(db_index=True, blank=True)),
            ('date_searched', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'ui', ['Search'])


    def backwards(self, orm):
        # Deleting model 'Search'
        db.delete_table(u'ui_search')


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
            'date_searched': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ui']