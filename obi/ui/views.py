import json

import requests

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from ui.models import Database


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


def databases(request):
    q = request.GET.get('q', None)
    response = {'q': q}
    if q:
        matches = []
        qs_databases = Database.objects.filter(Q(name__icontains=q) |
                                               Q(url__icontains=q) |
                                               Q(description__icontains=q))
        response['count_total'] = qs_databases.count()
        response['more_url'] = '%s%s' % (settings.DATABASES_MORE_URL, q)
        for db in qs_databases[:10]:
            match = {'name': db.name, 'url': db.url,
                     'description': db.description}
            matches.append(match)
        response['matches'] = matches
    return HttpResponse(json.dumps(response), content_type='application/json')
