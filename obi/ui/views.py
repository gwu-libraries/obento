import json

from lxml import etree
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


def _aquabrowser_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', DEFAULT_HIT_COUNT))
    except:
        count = DEFAULT_HIT_COUNT
    params = {'output': 'xml', 'q': q}
    # FIXME: move url to settings
    r = requests.get('http://surveyor.gelman.gwu.edu/result.ashx',
                     params=params)
    root = etree.fromstring(r.text)
    matches = []
    for record in root.findall('./results/record')[:count]:
        match = {}
        d = record.find('d')
        df245 = d.find('df245')
        title = ''
        for df245row in df245.findall("df245"):
            if df245row.attrib['key'] != "i1" \
                    and df245row.attrib['key'] != "i2":
                exact = df245row.find("exact")
                if exact:
                    df245rowtext = exact.text
                else:
                    df245rowtext = df245row.text
                title += df245rowtext + '\n'
        match['name'] = title.strip()
        match['url'] = 'http://surveyor.gelman.gwu.edu/?hreciid=%s' % \
                       record.attrib['extID']
        # TODO: what should go here?
        match['description'] = ''
        matches.append(match)
    more_url = 'http://surveyor.gelman.gwu.edu/?q=%s' % q
    response = {'matches': matches, 'q': q, 'count_total': len(matches),
                'more_url': more_url}
    return response


def aquabrowser_json(request):
    response = _aquabrowser_query(request)
    return HttpResponse(json.dumps(response, encoding='utf-8'),
                        content_type='application/json')


def aquabrowser_html(request):
    response = _aquabrowser_query(request)
    return render(request, 'aquabrowser.html', {'response': response})


def _databases_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', DEFAULT_HIT_COUNT))
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
    return render(request, 'databases.html', {'response': response})


def databases_json(request):
    response = _databases_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')
