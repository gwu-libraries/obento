import base64
from datetime import datetime
import hashlib
import hmac
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
RFC2616_DATEFORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def home(request):
    q = request.GET.get('q', '')
    if q:
        aquabrowser_response = _aquabrowser_query(request)
        databases_response = _databases_query(request)
        summon_response = _summon_query(request)
    params = {'title': 'home', 'q': q}
    if q:
        params['aquabrowser_response'] = aquabrowser_response
        params['databases_response'] = databases_response
        params['summon_response'] = summon_response
    return render(request, 'home.html', params)


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


def _summon_id_string(headers, params):
    params_sorted = '&'.join(['%s=%s' % (k, unicode(v).encode('utf-8'))
                              for k, v in sorted(params.items())])
    s = '\n'.join([headers['Accept'], headers['x-summon-date'],
                   settings.SUMMON_HOST, settings.SUMMON_PATH, params_sorted])
    # Don't forget the trailing '\n'!
    return s + '\n'


def _summon_query(request):
    headers = {'Accept': 'application/json'}
    headers['Host'] = settings.SUMMON_HOST
    headers['x-summon-date'] = datetime.utcnow().strftime(RFC2616_DATEFORMAT)
    # TODO: API docs say to reuse this once it's set for a user, punt for now
    headers['x-summon-session-id'] = ''
    params = settings.SUMMON_SCOPES['all']['params']
    q = request.GET.get('q', '')
    params['s.q'] = q
    # disable highlighting tags
    params['s.hl'] = 'false'
    id_str = _summon_id_string(headers, params)
    hash_code = hmac.new(settings.SUMMON_API_KEY, id_str, hashlib.sha1)
    digest = base64.encodestring(hash_code.digest())
    auth_str = "Summon %s;%s" % (settings.SUMMON_API_ID, digest)
    headers['Authorization'] = auth_str
    url = 'http://%s%s' % (settings.SUMMON_HOST, settings.SUMMON_PATH)
    r = requests.get(url, params=params, headers=headers)
    d = r.json()
    response = {'count_total': d['recordCount']}
    matches = []
    for document in d['documents'][:DEFAULT_HIT_COUNT]:
        match = {'url': document['link']}
        if document.get('Author', []):
            match['description'] = document['Author'][0]
        if document.get('DocumentTitleAlternate', []):
            match['name'] = document['DocumentTitleAlternate'][0]
        else:
            if document.get('Title', []):
                match['name'] = document['Title'][0]
            else:
                match['name'] = 'NO TITLE FOUND - SHOW A NICER MESSAGE PLEASE'
        matches.append(match)
    if settings.DEBUG:
        response['source'] = d
    response['matches'] = matches
    response['q'] = q
    response['more_url'] = '%s%s' %  \
        (settings.SUMMON_SCOPES['all']['more_url'], q)
    return response


def summon_html(request):
    response = _summon_query(request)
    return render(request, 'summon.html', {'response': response})


def summon_json(request):
    response = _summon_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')
