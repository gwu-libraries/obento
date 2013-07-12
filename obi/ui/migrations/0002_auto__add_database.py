# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Database'
        db.create_table(u'ui_database', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(db_index=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=300)),
        ))
        db.send_create_signal(u'ui', ['Database'])


    def backwards(self, orm):
        # Deleting model 'Database'
        db.delete_table(u'ui_database')


    models = {
        u'ui.database': {
            'Meta': {'object_name': 'Database'},
            'description': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['ui']