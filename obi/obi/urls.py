from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'ui.views.home', name='home'),

    url(r'^aquabrowser', 'ui.views.aquabrowser', name='aquabrowser'),
    url(r'^databases', 'ui.views.databases', name='databases'),

    url(r'^admin/', include(admin.site.urls)),

)
