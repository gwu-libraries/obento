from django.contrib import admin

from ui import models as m


class DatabaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'url']
    search_fields = ['name', 'description', 'url']
admin.site.register(m.Database, DatabaseAdmin)
