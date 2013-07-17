from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'ui.views.home', name='home'),

    url(r'^aquabrowser', 'ui.views.aquabrowser', name='aquabrowser'),

    url(r'^databases_html', 'ui.views.databases_html', name='databases_html'),
    url(r'^databases_json', 'ui.views.databases_json', name='databases_json'),

    url(r'^admin/', include(admin.site.urls)),

)
