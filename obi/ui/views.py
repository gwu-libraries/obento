import base64
from datetime import datetime
import hashlib
import hmac
import json
import urllib

from lxml import etree
import requests

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from ui.models import Database, Journal


# FIXME: make a local_setting
DEFAULT_HIT_COUNT = 3
RFC2616_DATEFORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def home(request):
    q = request.GET.get('q', '')
    if q:
        articles_response = _summon_query(request, scope='articles')
        books_media_response = _summon_query(request, scope='books_media')
        research_guides_response = _summon_query(request,
                                                 scope='research_guides')
        databases_response = _databases_query(request)
        journals_response = _journals_query(request)
        aquabrowser_response = _aquabrowser_query(request)
    params = {'title': 'home', 'q': q}
    if q:
        params['articles_response'] = articles_response
        params['books_media_response'] = books_media_response
        params['research_guides_response'] = research_guides_response
        params['databases_response'] = databases_response
        params['journals_response'] = journals_response
        params['aquabrowser_response'] = aquabrowser_response
    params['context'] = default_context_params()
    return render(request, 'home.html', params)


def ajax(request):
    q = request.GET.get('q', '')
    params = {'title': 'home', 'q': q}
    params['context'] = default_context_params()
    return render(request, 'ajax.html', params)


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
        if d is None:
            break
        match['name'] = _ab_marc_field_str(d, 'df245', ['a', 'h', 'b', 'c'])
        match['description'] = _ab_marc_field_str(d, 'df100', ['a'])
        match['publisher'] = _ab_marc_field_str(d, 'df260', ['a', 'b', 'c'])
        match['edition'] = _ab_marc_field_str(d, 'df250', ['a'])
        match['url'] = 'http://surveyor.gelman.gwu.edu/?hreciid=%s' % \
                       record.attrib['extID']
        matches.append(match)
    count_total_nodes = root.xpath('/root/feedbacks/standard/resultcount')
    if count_total_nodes:
        # there should be exactly one
        count_total = count_total_nodes[0].text
    else:
        count_total = len(records)
    response = {}
    response['more_url'] = '%s%s' % (settings.AQUABROWSER_MORE_URL, q)
    response['more_url_plain'] = settings.AQUABROWSER_URL
    response['matches'] = matches
    response['q'] = q
    response['count_total'] = count_total
    if settings.DEBUG:
        # TODO: NOT WORKING YET:
        #response['source'] = records.json()
        response['query_url'] = r.url
    return response


# Returns a concatenation of the values of the specified subfield codes
# Warning: this is specific to Aquabrowser result formatting
def _ab_marc_field_str(marcdict, fieldname, codes):
    fields = marcdict.find(fieldname)
    if fields is None:
        return ''
    result = ''
    for fieldrow in fields.findall(fieldname):
        key = fieldrow.attrib['key']
        if key in codes:
            result = result + ' ' + ''.join(fieldrow.xpath('.//text()'))
    return result


def aquabrowser_json(request):
    response = _aquabrowser_query(request)
    return HttpResponse(json.dumps(response, encoding='utf-8'),
                        content_type='application/json')


def aquabrowser_html(request):
    response = _aquabrowser_query(request)
    default_context_params()
    return render(request, 'aquabrowser.html',
                  {'response': response, 'context': default_context_params()})


def _databases_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', None))
    except:
        count = DEFAULT_HIT_COUNT
    response = {'q': q}
    if q:
        matches = []
        qs_databases = Database.objects.filter(Q(name__icontains=q) |
                                               Q(url__icontains=q) |
                                               Q(description__icontains=q))
        # for some reason, this is always returning 10 - TODO: need to research
        #        response['count_total'] = qs_databases.count()
        # temporarily using len() to work around this
        response['count_total'] = len(qs_databases)
        response['more_url'] = '%s%s' % (settings.DATABASES_MORE_URL, q)
        response['more_url_plain'] = settings.DATABASES_URL
        # count=0 is passed to request all records
        if count == 0:
            count = len(qs_databases)
        for db in qs_databases[:count]:
            match = {'name': db.name, 'url': db.url,
                     'description': db.description}
            matches.append(match)
        response['matches'] = matches
    return response


def databases_html(request):
    response = _databases_query(request)
    return render(request, 'databases.html',
                  {'response': response, 'context': default_context_params()})


def databases_json(request):
    response = _databases_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def _journals_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', DEFAULT_HIT_COUNT))
    except:
        count = DEFAULT_HIT_COUNT
    response = {'q': q}
    if q:
        matches = []
        qs_journals = Journal.objects.filter(Q(title__icontains=q))
        qs_journals = qs_journals.distinct('ssid')
        response['count_total'] = qs_journals.count()
        response['more_url_plain'] = settings.JOURNALS_URL
        response['more_url'] = '%s%s' % (settings.JOURNALS_MORE_URL, q)
        for journal in qs_journals[:count]:
            url = settings.JOURNALS_TITLE_EXACT_URL + \
                urllib.quote_plus(unicode(journal.title).encode('utf-8'))
            match = {'title': journal.title, 'ssid': journal.ssid,
                     'issn': journal.issn, 'eissn': journal.eissn,
                     'url': url}
            matches.append(match)
        response['matches'] = matches
    return response


def journals_html(request):
    response = _journals_query(request)
    response['context'] = default_context_params()
    return render(request, 'journals.html',
                  {'response': response, 'context': default_context_params()})


def journals_json(request):
    response = _journals_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def _summon_id_string(headers, params):
    params_sorted = '&'.join(['%s=%s' % (k, unicode(v).encode('utf-8'))
                             for k, v in sorted(params.items())])
    s = '\n'.join([headers['Accept'], headers['x-summon-date'],
                   settings.SUMMON_HOST, settings.SUMMON_PATH, params_sorted])
    # Don't forget the trailing '\n'!
    return s + '\n'


def _summon_query(request, scope='all'):
    headers = {'Accept': 'application/json'}
    headers['Host'] = settings.SUMMON_HOST
    headers['x-summon-date'] = datetime.utcnow().strftime(RFC2616_DATEFORMAT)
    # TODO: API docs say to reuse this once it's set for a user, punt for now
    headers['x-summon-session-id'] = ''
    params = settings.SUMMON_SCOPES[scope]['params']
    q = request.GET.get('q', '')
    if scope == 'research_guides':
        q = q + " NOT \"Research Guides. Databases\""
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
            match['author'] = document['Author'][0]
        #  else:
        #      if document.get('CorporateAuthor', []):
        #          match['author'] = document['CorporateAuthor'][0]
        if document.get('DocumentTitleAlternate', []):
            match['name'] = document['DocumentTitleAlternate'][0]
        else:
            if document.get('Title', []):
                title_str = document['Title'][0]
                # Remove "Research Guides. " from start of string
                MATCH_TO_REMOVE = 'Research Guides. '
                if scope == 'research_guides' \
                        and title_str.startswith(MATCH_TO_REMOVE):
                            title_str = title_str[len(MATCH_TO_REMOVE):]
                match['name'] = title_str
            else:
                match['name'] = 'NO TITLE FOUND - SHOW A NICER MESSAGE PLEASE'
        if document.get('Publisher', []):
            match['publisher'] = document['Publisher'][0]
        if document.get('PublicationTitle', []):
            match['publicationtitle'] = document['PublicationTitle'][0]
        if document.get('PublicationYear', []):
            match['publicationyear'] = document['PublicationYear'][0]
        if document.get('PublicationPlace', []):
            match['publicationplace'] = document['PublicationPlace'][0]
        matches.append(match)
    if settings.DEBUG:
        response['source'] = d
        response['query_url'] = r.url
    response['matches'] = matches
    response['q'] = q
    response['scope'] = scope
    response['more_url_plain'] = settings.SUMMON_URL
    response['more_url'] = '%s%s' %  \
        (settings.SUMMON_SCOPES[scope]['more_url'], q)
    return response


def summon_html(request, scope='all'):
    response = _summon_query(request, scope)
    return render(request, 'summon.html',
                  {'response': response, 'context': default_context_params()})


def summon_json(request, scope='all'):
    response = _summon_query(request, scope)
    return HttpResponse(json.dumps(response), content_type='application/json')


def default_context_params():
    return {'TITLE_DISPLAY_LENGTH': settings.TITLE_DISPLAY_LENGTH,
            'DESCRIPTION_DISPLAY_LENGTH':
            settings.DESCRIPTION_DISPLAY_LENGTH}
