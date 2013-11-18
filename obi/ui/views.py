import base64
from datetime import datetime
import hashlib
import hmac
import json
import urllib

from lxml import etree
import requests
import solr

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from ui.models import Database, Journal, Search

from netaddr import IPAddress, IPGlob


# FIXME: make a local_setting
DEFAULT_HIT_COUNT = 3
RFC2616_DATEFORMAT = "%a, %d %b %Y %H:%M:%S GMT"


def home(request):
    q = request.GET.get('q', '')
    if q:
        articles_response = _summon_query(request, scope='articles')
        books_media_response = _aquabrowser_query(request)
        libsite_response = _libsite_query(request)
        databases_solr_response = _databases_solr_query(request)
        journals_solr_response = _journals_solr_query(request)
        research_guides_response = _summon_query(request,
                                                 scope='research_guides')
        best_bets_response = _summon_query(request, scope='best_bets')

    params = {'title': 'home', 'q': q}
    params['context'] = default_context_params()
    if q:
        params['articles_response'] = articles_response
        params['books_media_response'] = books_media_response
        params['research_guides_response'] = research_guides_response
        params['best_bets_response'] = best_bets_response
        params['databases_solr_response'] = databases_solr_response
        params['journals_solr_response'] = journals_solr_response
        params['libsite_response'] = libsite_response
    return render(request, 'home.html', params)


def everything(request):
    q = request.GET.get('q', '')
    params = {'title': 'home', 'q': q}
    params['context'] = default_context_params()
    return render(request, 'everything.html', params)


def _aquabrowser_query(request):
    q = request.GET.get('q', '')
    # if the query is not already quoted, enclose in quotes
    if not(q.startswith('\"') and q.endswith('\"')):
        q = '\"'+q+'\"'

    try:
        count = int(request.GET.get('count', DEFAULT_HIT_COUNT))
    except:
        count = DEFAULT_HIT_COUNT
    params = {'output': 'xml', 'q': q}
    # TODO: move url to settings
    url = settings.AQUABROWSER_URL + settings.AQUABROWSER_API_PATH
    r = requests.get(url, params=params)
    root = etree.fromstring(r.text)
    matches = []
    records = root.findall('./results/record')
    for record in records[:count]:
        match = {}
        d = record.find('d')
        if d is None:
            break
        fields = record.find('fields')
        if fields is None:
            break
        match['name'] = _ab_marc_field_str(d, 'df245', ['a', 'h', 'b', 'c'])
        match['description'] = _ab_marc_field_str(d, 'df100', ['a'])
        match['publisher'] = _ab_marc_field_str(d, 'df260', ['a', 'b', 'c'])
        match['edition'] = _ab_marc_field_str(d, 'df250', ['a'])
        match['url'] = 'http://surveyor.gelman.gwu.edu/?hreciid=%s' % \
                       record.attrib['extID']
        holding_institutions = _ab_field_list(fields, 'bsall')
        if len(holding_institutions) > 0:
            if 'library\m\gw' in holding_institutions:
                holding_institutions_display = 'GW'
                if len(holding_institutions) > 1:
                    holding_institutions_display += ' and other WRLC Libraries'
            else:
                holding_institutions_display = 'Other WRLC Libraries'
        match['institutions'] = holding_institutions_display
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


# Returns a list of the values of the specified field
# Warning: this is specific to Aquabrowser result formatting
def _ab_field_list(abfields, fieldname):
    fields = abfields.findall(fieldname)
    if fields is None:
        return []
    result = []
    for fieldrow in fields:
        result.append(fieldrow.text)
    return result


def aquabrowser_json(request):
    response = _aquabrowser_query(request)
    return HttpResponse(json.dumps(response, encoding='utf-8'),
                        content_type='application/json')


def aquabrowser_html(request):
    response = _aquabrowser_query(request)
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


def _databases_solr_query(request):
    q = request.GET.get('q', '')
    # Don't use DEFAULT_HIT_COUNT, instead grab 25 so we can expand
    DATABASE_HIT_COUNT = 25
    try:
        count = int(request.GET.get('count', DATABASE_HIT_COUNT))
    except:
        count = DATABASE_HIT_COUNT
    response = {'q': q}
    if q:
        matches = []
        s = solr.SolrConnection(settings.SOLR_URL)
        query = u'+text:%s +id:db-* (name:%s OR description:%s)' % (q, q, q)
        solr_response = s.query(query, rows=DATABASE_HIT_COUNT)
        response['count_total'] = solr_response.numFound
        response['more_url'] = '%s%s' % (settings.DATABASES_MORE_URL, q)
        response['more_url_plain'] = settings.DATABASES_URL
        if count == 0:
            count = len(solr_response.results)
        for db in solr_response.results[:count]:
            match = {'name': db['name'], 'url': db.get('url', ''),
                     'description': db.get('description', '')}
            matches.append(match)
        response['matches'] = matches
        if settings.DEBUG:
            source = {'header': solr_response.header,
                      'results': solr_response.results}
            response['source'] = source
    return response


def databases_html(request):
    response = _databases_query(request)
    return render(request, 'databases.html',
                  {'response': response, 'context': default_context_params()})


def databases_solr_html(request):
    response = _databases_solr_query(request)
    return render(request, 'databases.html',
                  {'response': response, 'context': default_context_params()})


def databases_json(request):
    response = _databases_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def databases_solr_json(request):
    response = _databases_solr_query(request)
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
        if count == 0:
            count = len(qs_journals)
        for journal in qs_journals[:count]:
            url = settings.JOURNALS_TITLE_EXACT_URL + \
                urllib.quote_plus(unicode(journal.title).encode('utf-8'))
            match = {'title': journal.title, 'ssid': journal.ssid,
                     'issn': journal.issn, 'eissn': journal.eissn,
                     'url': url}
            matches.append(match)
        response['matches'] = matches
    return response


def _journals_solr_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', None))
    except:
        count = DEFAULT_HIT_COUNT
    response = {'q': q}
    if q:
        matches = []
        s = solr.SolrConnection(settings.SOLR_URL)
        solr_response = s.query('+text:%s +name:%s +id:j-*' % (q, q))
        response['count_total'] = solr_response.numFound
        response['more_url'] = '%s%s' % (settings.JOURNALS_MORE_URL, q)
        response['more_url_plain'] = settings.JOURNALS_URL
        if count == 0:
            count = len(solr_response.results)
        for j in solr_response.results[:count]:
            url = settings.JOURNALS_TITLE_EXACT_URL + \
                urllib.quote_plus(unicode(j['name']).encode('utf-8'))
            match = {'title': j['name'], 'url': url}
            if j.get('issn', ''):
                match['issn'] = j['issn']
            elif j.get('eissn', ''):
                match['issn'] = j['eissn']
            matches.append(match)
        response['matches'] = matches
        if settings.DEBUG:
            source = {'header': solr_response.header,
                      'results': solr_response.results}
            response['source'] = source
    return response


def journals_html(request):
    response = _journals_query(request)
    return render(request, 'journals.html',
                  {'response': response, 'context': default_context_params()})


def journals_solr_html(request):
    response = _journals_solr_query(request)
    # Save search terms only here, and in journals_json, to limit copies
    # of search terms from proliferating
    querystring = request.GET.get('q', '')
    if querystring:
        s = Search(q=querystring)
        s.save()
    return render(request, 'journals.html',
                  {'response': response, 'context': default_context_params()})


def journals_json(request):
    response = _journals_query(request)
    # Save search terms only here, and in journals_json, to limit copies
    # of search terms from proliferating
    s = Search(q=request.GET.get('q', ''))
    s.save()
    return HttpResponse(json.dumps(response), content_type='application/json')


def journals_solr_json(request):
    response = _journals_solr_query(request)
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
    if _is_request_local(request):
        params['s.role'] = 'authenticated'
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
            match['author'] = ", ".join(document['Author'])
        #  else:
        #      if document.get('CorporateAuthor', []):
        #          match['author'] = document['CorporateAuthor'][0]
        if document.get('Title', []):
            title_str = document['Title'][0]
        elif document.get('DocumentTitleAlternate', []):
            title_str = document['DocumentTitleAlternate'][0]
        else:
            title_str = 'NO TITLE FOUND - SHOW A NICER MESSAGE PLEASE'

        # Remove "Research Guides. " from start of string
        MATCH_TO_REMOVE = 'Research Guides. '
        if scope == 'research_guides' \
                and title_str.startswith(MATCH_TO_REMOVE):
            title_str = title_str[len(MATCH_TO_REMOVE):]
        match['name'] = title_str

        if document.get('Publisher', []):
            match['publisher'] = document['Publisher'][0]
        if document.get('PublicationTitle', []):
            match['publicationtitle'] = document['PublicationTitle'][0]
        if document.get('PublicationYear', []):
            match['publicationyear'] = document['PublicationYear'][0]
        if document.get('PublicationPlace', []):
            match['publicationplace'] = document['PublicationPlace'][0]
        if document.get('hasFullText', []):
            match['hasFullText'] = document['hasFullText']
        if document.get('Institution', []):
            match['institution'] = document['Institution'][0]
        matches.append(match)

    bbmatches = []
    if d.get('recommendationLists', []):
        rl = d['recommendationLists']
        if rl.get('bestBet', []):
            bblist = rl['bestBet']
            for bestbet in bblist[:DEFAULT_HIT_COUNT]:
                match = {'url': bestbet['link']}
                if bestbet.get('title', []):
                    match['title'] = bestbet['title']
                if bestbet.get('description', []):
                    match['description'] = bestbet['description']
                bbmatches.append(match)

    if settings.DEBUG:
        response['source'] = d
        response['query_url'] = r.url
    response['matches'] = matches
    response['bbmatches'] = bbmatches
    response['q'] = q
    response['scope'] = scope
    if scope == 'research_guides':
        response['more_url_plain'] = settings.LIBGUIDES_URL
    else:
        response['more_url_plain'] = settings.SUMMON_URL
    response['more_url'] = '%s%s' %  \
        (settings.SUMMON_SCOPES[scope]['more_url'], q)
    if _is_request_local(request):
        response['more_url'] += '&s.role=authenticated'
    else:
        response['more_url'] += '&s.role=none'
    return response


def summon_html(request, scope='all'):
    response = _summon_query(request, scope)
    if scope == 'best_bets':
        responsepage = 'bestbets.html'
    else:
        responsepage = 'summon.html'
    return render(request, responsepage,
                  {'response': response, 'context': default_context_params()})


def summon_json(request, scope='all'):
    response = _summon_query(request, scope)
    return HttpResponse(json.dumps(response), content_type='application/json')


def books_media_html(request, scope='all'):
    if _is_non_roman(request):
        return summon_html(request, scope)
    else:
        return aquabrowser_html(request)


def books_media_json(request, scope='all'):
    if _is_non_roman(request):
        return summon_json(request, scope)
    else:
        return aquabrowser_json(request)


def _is_non_roman(request):
    q = request.GET.get('q', '')
    #TODO: Maybe there's a better way to do this. For now, it seems to work.
    try:
        q.encode("iso-8859-1")
        return False
    except:
        return True


def best_bets_html(request):
    response = _summon_query(request, scope='best_bets')
    return render(request, 'best_bets.html',
                  {'response': response, 'context': default_context_params()})


def best_bets_json(request, scope='all'):
    response = _summon_query(request, scope='best_bets')
    return HttpResponse(json.dumps(response), content_type='application/json')


def _libsite_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', DEFAULT_HIT_COUNT))
    except:
        count = DEFAULT_HIT_COUNT
    params = {'keys': q}
    r = requests.get(settings.LIBSITE_SEARCH_URL, params=params)

    # FIXME: VERY FRAGILE!!!!  Breaks when results contain \'ed characters
    # Should be:
    # j = json.loads(jstr)
    j = json.loads(r.text[1:])  # FIXME: remove leading \ufeff at source
    response = {}
    matches = []
    nodesarray = j['nodes']
    for node in nodesarray[:count]:
        nodeinfo = node['node']
        match = {}
        match['view_node'] = nodeinfo['view_node']
        match['title'] = nodeinfo['title']
        matches.append(match)
    response['count_total'] = len(nodesarray)
    response['more_url'] = '%s%s' % (settings.LIBSITE_MORE_URL, q)
    response['more_url_plain'] = settings.LIBSITE_URL
    response['matches'] = matches
    response['q'] = q
    #response['count_total'] = count_total
    if settings.DEBUG:
        # TODO: NOT WORKING YET:
        #response['source'] = records.json()
        response['query_url'] = r.url
    return response


def libsite_html(request):
    response = _libsite_query(request)
    return render(request, 'libsite.html',
                  {'response': response, 'context': default_context_params()})


def libsite_json(request):
    response = _libsite_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def default_context_params():
    return {'TITLE_DISPLAY_LENGTH': settings.TITLE_DISPLAY_LENGTH,
            'DESCRIPTION_DISPLAY_LENGTH':
            settings.DESCRIPTION_DISPLAY_LENGTH,
            'AUTHOR_DISPLAY_LENGTH': settings.AUTHOR_DISPLAY_LENGTH}


def _is_request_local(request):
    remote_addr = request.GET.get('remote_addr', '')
    if remote_addr == '':
        remote_addr = request.META['REMOTE_ADDR']
    found_ip = False
    for ipg in settings.LOCAL_IPS:
        if IPAddress(remote_addr) in IPGlob(ipg):
            found_ip = True
    return found_ip
