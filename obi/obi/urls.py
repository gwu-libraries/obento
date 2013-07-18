from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'ui.views.home', name='home'),

    url(r'^aquabrowser_html', 'ui.views.aquabrowser_html',
        name='aquabrowser_html'),
    url(r'^aquabrowser_json', 'ui.views.aquabrowser_json',
        name='aquabrowser_json'),

    url(r'^databases_html', 'ui.views.databases_html', name='databases_html'),
    url(r'^databases_json', 'ui.views.databases_json', name='databases_json'),

    url(r'^summon_html', 'ui.views.summon_html', name='summon_html'),
    url(r'^summon_json', 'ui.views.summon_json', name='summon_json'),

    url(r'^admin/', include(admin.site.urls)),

)
