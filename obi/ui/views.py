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
    q = request.GET.get('q', '')
    aquabrowser_response = _aquabrowser_query(request)
    databases_response = _databases_query(request)
    return render(request, 'home.html', {
        'title': 'home',
        'q': q,
        'aquabrowser_response': aquabrowser_response,
        'databases_response': databases_response,
    })


def _aquabrowser_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', DEFAULT_HIT_COUNT))
    except:
        count = DEFAULT_HIT_COUNT
    params = {'output': 'xml', 'q': q}
    # TODO: move url to settings
    r = requests.get('http://surveyor.gelman.gwu.edu/result.ashx',
                     params=params)
    root = etree.fromstring(r.text)
    matches = []
    records = root.findall('./results/record')
    for record in records[:count]:
        match = {}
        d = record.find('d')
        df245 = d.find('df245')
        title_subs = {'a': '', 'b': '', 'c': ''}
        for df245row in df245.findall("df245"):
            key = df245row.attrib['key']
            if key in ['a', 'b', 'c']:
                title_subs[key] = ' '.join(df245row.xpath('.//text()'))
        match['name'] = ' '.join([title_subs['a'], title_subs['b'],
                                  title_subs['c']])
        match['url'] = 'http://surveyor.gelman.gwu.edu/?hreciid=%s' % \
                       record.attrib['extID']
        # TODO: what should go here, if anything?
        match['description'] = ''
        matches.append(match)
    more_url = 'http://surveyor.gelman.gwu.edu/?q=%s' % q
    response = {'matches': matches, 'q': q, 'count_total': len(records),
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
