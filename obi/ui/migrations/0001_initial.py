# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(db_index=True)),
                ('description', models.TextField(db_index=True, blank=True)),
                ('url', models.URLField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(db_index=True)),
                ('ssid', models.TextField(max_length=13, db_index=True)),
                ('issn', models.TextField(db_index=True, max_length=9, blank=True)),
                ('eissn', models.TextField(db_index=True, max_length=9, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('q', models.TextField(db_index=True, blank=True)),
                ('date_searched', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('articles_count', models.BigIntegerField(default=0, blank=True)),
                ('books_count', models.BigIntegerField(default=0, blank=True)),
                ('database_count', models.BigIntegerField(default=0, blank=True)),
                ('journals_count', models.BigIntegerField(default=0, blank=True)),
                ('researchguides_count', models.BigIntegerField(default=0, blank=True)),
            ],
            options={
                'verbose_name_plural': 'searches',
            },
        ),
    ]
