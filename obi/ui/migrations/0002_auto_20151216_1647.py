# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='search',
            name='articles_count',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='search',
            name='books_count',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='search',
            name='database_count',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='search',
            name='journals_count',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='search',
            name='researchguides_count',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
