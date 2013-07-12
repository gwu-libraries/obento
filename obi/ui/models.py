from django.db import models


class Database(models.Model):
    name = models.TextField(blank=False, db_index=True)
    description = models.TextField(blank=True, db_index=True)
    url = models.URLField(max_length=300)

    def __unicode__(self):
        return '<Database %s "%s">' % (self.id, self.name)
