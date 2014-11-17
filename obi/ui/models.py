from django.db import connection
from django.db import models


class Database(models.Model):
    name = models.TextField(blank=False, db_index=True)
    description = models.TextField(blank=True, db_index=True)
    url = models.URLField(max_length=300)

    def __unicode__(self):
        return '<Database %s "%s">' % (self.id, self.name)


class Journal(models.Model):
    title = models.TextField(blank=False, db_index=True)
    ssid = models.TextField(blank=False, db_index=True, max_length=13)
    issn = models.TextField(blank=True, db_index=True, max_length=9)
    eissn = models.TextField(blank=True, db_index=True, max_length=9)

    def __unicode__(self):
        return '<Journal %s "%s">' % (self.id, self.title)


class SearchTermManager(models.Manager):
    def searched_terms(self, ndays, topn):
        cursor = connection.cursor()
        cursor.execute('''SELECT LOWER(q) q,COUNT(LOWER(q)) count
                       FROM ui_search WHERE
                         date_searched > current_date - interval ' %s days '
                       GROUP BY LOWER(q)
                       ORDER BY count DESC
                       LIMIT %s''' % (ndays, topn))
        return cursor.fetchall()


class Search(models.Model):
    q = models.TextField(blank=True, db_index=True)
    date_searched = models.DateTimeField(auto_now_add=True, db_index=True)
    objects = models.Manager()
    searchTermManager = SearchTermManager()

    class Meta:
        verbose_name_plural = 'searches'

    def __unicode__(self):
        return '<Search %s "%s">' % (self.id, self.q)
