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

    url(r'^journals_html', 'ui.views.journals_html', name='journals_html'),
    url(r'^journals_json', 'ui.views.journals_json', name='journals_json'),

    url(r'^summon_html', 'ui.views.summon_html', name='summon_html',
        kwargs={'scope': 'all'}),
    url(r'^summon_json', 'ui.views.summon_json', name='summon_json',
        kwargs={'scope': 'all'}),

    url(r'^articles_html', 'ui.views.summon_html', name='articles_html',
        kwargs={'scope': 'articles'}),
    url(r'^articles_json', 'ui.views.summon_json', name='articles_json',
        kwargs={'scope': 'articles'}),

    url(r'^books_media_html', 'ui.views.summon_html',
        name='books_media_html', kwargs={'scope': 'books_media'}),
    url(r'^books_media_json', 'ui.views.summon_json', 
        name='books_media_json', kwargs={'scope': 'books_media'}),

    url(r'^research_guides_html', 'ui.views.summon_html',
        name='research_guides_html', kwargs={'scope': 'research_guides'}),
    url(r'^research_guides_json', 'ui.views.summon_json', 
        name='research_guides_json', kwargs={'scope': 'research_guides'}),

    url(r'^best_bets_html', 'ui.views.summon_html',
        name='best_bets_html', kwargs={'scope': 'best_bets'}),
    url(r'^best_bets_json', 'ui.views.summon_json', 
        name='best_bets_json', kwargs={'scope': 'best_bets'}),

    url(r'^admin/', include(admin.site.urls)),

)
