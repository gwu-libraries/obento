import json

import requests

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from ui.models import Database


# FIXME: make a local_setting
DEFAULT_HIT_COUNT = 3


def home(request):
    q = request.GET.get('q', None)
    return render(request, 'home.html', {
        'title': 'home',
        'q': q,
    })


def aquabrowser(request):
    q = request.GET.get('q', None)
    if q:
        payload = {'output': 'xml', 'q': q}
        r = requests.get('http://surveyor.gelman.gwu.edu/result.ashx',
                         params=payload)
    return HttpResponse(r.content, content_type='application/xml')


def _databases_query(request):
    q = request.GET.get('q', '')
    try:
        count = request.GET.get('count', DEFAULT_HIT_COUNT)
    except:
        count = DEFAULT_HIT_COUNT
    response = {'q': q}
    if q:
        matches = []
        qs_databases = Database.objects.filter(Q(name__icontains=q) |
                                               Q(url__icontains=q) |
                                               Q(description__icontains=q))
        response['count_total'] = qs_databases.count()
        response['more_url'] = '%s%s' % (settings.DATABASES_MORE_URL, q)
        for db in qs_databases[:count]:
            match = {'name': db.name, 'url': db.url,
                     'description': db.description}
            matches.append(match)
        response['matches'] = matches
    return response


def databases_html(request):
    response = _databases_query(request)
    return render(request, 'databases.html', {
        'response': response,
    })


def databases_json(request):
    response = _databases_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')
