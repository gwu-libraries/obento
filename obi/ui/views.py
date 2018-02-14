import base64
import datetime
import hashlib
import hmac
import json
import logging
import time
import urllib
import urllib2
import xmltodict

from netaddr import IPAddress, IPGlob
import requests
import solr

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template import RequestContext

from ui.models import Database, Journal, Search


RFC2616_DATEFORMAT = "%a, %d %b %Y %H:%M:%S GMT"

logger = logging.getLogger('django.request')


def home(request):
    q = request.GET.get('q', '').strip()
    return render(request, 'home.html', {'title': 'home', 'q': q})


def everything(request):
    q = request.GET.get('q', '')
    params = {'title': 'home', 'q': q}
    params['context'] = default_context_params()
    return render(request, 'everything.html', params)


def _launchpad_query(request):
    q = request.GET.get('q', '')
    page_no = 1
    count = int(float(request.GET.get('count', settings.DEFAULT_HIT_COUNT)))
    # Getting three times the required results by multiplying page_size by 3
    # This is needed since launchpad merges some of the results returned by
    # summon into 1 before passing it to obento. The multiplier ensures that
    # we will get atleast the expected number of results in 90% of the cases.
    page_size = count*3
    params = {'q': q, 'format': 'json', 'page': page_no,
              'page_size': page_size}

    r = requests.get(settings.LAUNCHPAD_API_URL, params=params,
                     timeout=settings.LAUNCHPAD_TIMEOUT_SECONDS)
    retries_left = settings.LAUNCHPAD_RETRIES
    while r.status_code != requests.codes.ok and retries_left > 0:
        logger.error('Retrying due to Launchpad  error: %s', r.text)
        r = requests.get(settings.LAUNCHPAD_API_URL, params=params,
                         timeout=settings.LAUNCHPAD_TIMEOUT_SECONDS)
        retries_left -= 1
        time.sleep(settings.LAUNCHPAD_RETRY_SLEEP)
    r.raise_for_status()
    d = r.json()
    matches = []
    response = {'q': q}

    for result in d['results'][:count]:
        match = {'name': result['name']}
        match['url'] = settings.LAUNCHPAD_URL + result['@id']
        if 'author' in result:
            match['author'] = '; '.join(a['name'] for a in result['author'])
        if 'publisher' in result:
            match['publisher'] = result['publisher']['name']
        if 'datePublished' in result:
            if 'publisher' in match:
                match['publisher'] += ' ' + result['datePublished'] + '.'
            else:
                match['publisher'] = result['datePublished'] + '.'
        if result['offers']:
            holders = [offer['seller'] for offer in result['offers']]
            if len(holders) == 1:
                match['institutions'] = holders[0]
            elif len(holders) > 1:
                if 'George Washington University' in holders:
                    match['institutions'] = 'GW and other WRLC Libraries'
                else:
                    match['institutions'] = 'Other WRLC Libraries'
        matches.append(match)

    if settings.DEBUG:
        response['source'] = d
        response['query_url'] = r.url

    q = q.replace("%20", "%2b")
    q = q.replace("+", "%2b")
    q = q.replace("#", "%23")

    response['matches'] = matches
    response['more_url'] = '%s?q=%s' % (settings.LAUNCHPAD_API_URL, q)
    response['more_url_plain'] = settings.LAUNCHPAD_MORE_URL_PLAIN
    response['count_total'] = d['totalResults']
    searchid = request.GET.get('searchid', 0)
    save_result_count(searchid, "books", response['count_total'])
    return response


def launchpad_json(request):
    response = _launchpad_query(request)
    return HttpResponse(json.dumps(response, encoding='utf-8'),
                        content_type='application/json')


def launchpad_html(request):
    try:
        response = _launchpad_query(request)
    except Exception as e:
        wrlc_url = settings.WRLC_CATALOG_URL % request.GET.get('q')
        return _render_cleanerror(request, 'books and media', e,
                                  settings.WRLC_CATALOG_LABEL,
                                  wrlc_url)

    return render(request, 'launchpad.html',
                  {'response': response, 'context': default_context_params()})


def _databases_query(request):
    q = request.GET.get('q', '')
    try:
        count = int(request.GET.get('count', None))
    except:
        count = settings.DEFAULT_HIT_COUNT
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
    q = request.GET.get('q', '').strip()
    display_count = int(request.GET.get('count', settings.DEFAULT_HIT_COUNT))
    response = {'q': q, 'display_count': display_count}
    if q:
        matches = []
        s = solr.SolrConnection(settings.SOLR_URL)
        if not q[0] == '\"':
            q = " AND ".join(q.split())
            q = q.replace("\"", " ")
        query = u'+id:db-* +(name:(%s) OR description:(%s))' % (q, q)
        solr_response = s.query(query)
        response['count_total'] = solr_response.numFound
        response['more_url'] = '%s%s' % (settings.DATABASES_MORE_URL, q)
        response['more_url_plain'] = settings.DATABASES_URL
        for db in solr_response.results:
            match = {'name': db['name'], 'url': db.get('url', ''),
                     'description': db.get('description', '')}
            matches.append(match)
        response['matches'] = matches
        if settings.DEBUG:
            source = {'header': solr_response.header,
                      'results': solr_response.results}
            response['source'] = source
        searchid = request.GET.get('searchid', 0)
        save_result_count(searchid, "database", solr_response.numFound)
    return response


def databases_html(request):
    response = _databases_query(request)
    return render(request, 'databases.html',
                  {'response': response, 'context': default_context_params()})


def databases_solr_html(request):
    try:
        response = _databases_solr_query(request)
    except Exception as e:
        db_url = settings.DATABASES_MORE_URL + request.GET.get('q')
        # db_url = "%s%s" % (settings.DATABASES_MORE_URL,request.GET.get('q', ''))
        return _render_cleanerror(request, 'databases', e,
                                  'databases list', db_url)
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
        count = int(request.GET.get('count', settings.DEFAULT_HIT_COUNT))
    except:
        count = settings.DEFAULT_HIT_COUNT
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
    q = request.GET.get('q', '').strip()
    display_count = int(request.GET.get('count', settings.DEFAULT_HIT_COUNT))
    response = {'q': q, 'display_count': display_count}
    if q:
        matches = []
        s = solr.SolrConnection(settings.SOLR_URL)
        if not q[0] == '\"':
            q = " AND ".join(q.split())
            q = q.replace("\"", " ")
        query = u'+id:j-* +(name:(%s) OR text:(%s))' % (q, q)
        solr_response = s.query(query)
        response['count_total'] = solr_response.numFound
        response['more_url'] = '%s%s' % (settings.JOURNALS_MORE_URL, q)
        response['more_url_plain'] = settings.JOURNALS_URL
        for j in solr_response.results:
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
        searchid = request.GET.get('searchid', 0)
        save_result_count(searchid, "journals", solr_response.numFound)
    return response


def journals_html(request):
    response = _journals_query(request)
    return render(request, 'journals.html',
                  {'response': response, 'context': default_context_params()})


def journals_solr_html(request):
    try:
        response = _journals_solr_query(request)
    except Exception as e:
        j_url = settings.JOURNALS_MORE_URL + request.GET.get('q')
        return _render_cleanerror(request, 'journals', e,
                                  'journals list', j_url)
    return render(request, 'journals.html',
                  {'response': response, 'context': default_context_params()})


def journals_json(request):
    response = _journals_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def journals_solr_json(request):
    response = _journals_solr_query(request)
    return HttpResponse(json.dumps(response), content_type='application/json')


def _summon_id_string(accept, xsummondate, host, path, params):
    if len(params) > 0:
        params_sorted = '&'.join(['%s=%s' % (k, unicode(v).encode('utf-8'))
                                 for k, v in sorted(params)])
    else:
        params_sorted = ''
    s = '\n'.join([accept, xsummondate, host, path, params_sorted])
    # Don't forget the trailing '\n'!
    return s + '\n'


def _summon_query(request, scope='all'):
    headers = {'Accept': 'application/json'}
    headers['Host'] = settings.SUMMON_HOST
    headers['User-Agent'] = settings.SUMMON_USER_AGENT
    headers['x-summon-date'] = datetime.datetime.utcnow().strftime(
        RFC2616_DATEFORMAT)
    # TODO: API docs say to reuse this once it's set for a user, punt for now
    headers['x-summon-session-id'] = ''
    params = list(settings.SUMMON_SCOPES[scope]['params'])
    q = request.GET.get('q', '')
    if scope == 'research_guides':
        q = q + " NOT \"Research Guides. Databases\""
    params.append(('s.q', q))
    # always disable highlighting tags
    params.append(('s.hl', 'false'))
    if _is_request_local(request):
        params.append(('s.role', 'authenticated'))
    else:
        params.append(('s.role', 'none'))
    id_str = _summon_id_string(headers['Accept'], headers['x-summon-date'],
                               settings.SUMMON_HOST, settings.SUMMON_PATH,
                               params)
    hash_code = hmac.new(settings.SUMMON_API_KEY, id_str, hashlib.sha1)
    digest = base64.encodestring(hash_code.digest())
    auth_str = "Summon %s;%s" % (settings.SUMMON_API_ID, digest)
    auth_str = auth_str.replace('\n', '')
    headers['Authorization'] = auth_str
    url = 'http://%s%s' % (settings.SUMMON_HOST, settings.SUMMON_PATH)
    r = requests.get(url, params=params, headers=headers,
                     timeout=settings.SUMMON_TIMEOUT_SECONDS)
    # if the request returns a bad status code,
    # try again (a few times).  If it's still bad,
    # don't ignore it; raise it as the appropriate exception
    retries_left = settings.SUMMON_RETRIES
    while r.status_code != requests.codes.ok and retries_left > 0:
        logger.error('Retrying due to Summon error: %s', r.text)
        r = requests.get(url, params=params, headers=headers,
                         timeout=settings.SUMMON_TIMEOUT_SECONDS)
        retries_left -= 1
        time.sleep(settings.SUMMON_RETRY_SLEEP)
    r.raise_for_status()
    d = r.json()
    matches = []
    response = {}

    if d.get('recordCount'):
        response['count_total'] = d.get('recordCount')
    else:
        response['count_total'] = 0

    try:
        count = int(request.GET.get('count', settings.DEFAULT_HIT_COUNT))
    except:
        count = settings.DEFAULT_HIT_COUNT
    for document in d['documents'][:count]:
        match = {}
        if document.get('Author', []):
            match['author'] = ", ".join(document['Author'])
        #  else:
        #      if document.get('CorporateAuthor', []):
        #          match['author'] = document['CorporateAuthor'][0]
        if _is_non_roman(request):
            if document.get('DocumentTitle_FL', []):
                title_str = document['DocumentTitle_FL'][0]
            elif document.get('Title', []):
                title_str = document['Title'][0]
            elif document.get('DocumentTitleAlternate', []):
                title_str = document['DocumentTitleAlternate'][0]
            else:
                title_str = 'NO TITLE FOUND - SHOW A NICER MESSAGE PLEASE'
        else:
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
        else:
            match['hasFullText'] = False
        if document.get('Institution', []):
            match['institution'] = document['Institution'][0]

        # Start with the result provided by Summon,
        # but overwrite if we can do better
        match['url'] = document['link']
        if scope == 'articles' and match['hasFullText'] is True:
            # Check whether Summon-provided link resolves to
            # findit.library.gwu.edu.
            # If it takes us elsewhere (to the resource), use that.
            # But if it takes us to findit, attempt to resolve w/openURL.

            # Send a HEAD request, not a GET request, to avoid the
            # added time involved to provide the message body (which
            # in this case could be an entire scholarly article)
            r = requests.head(document['link'],
                              timeout=settings.SUMMON_TIMEOUT_SECONDS)
            if 200 <= r.status_code < 400:
                resolved_url = r.headers['Location']
                match['url'] = resolved_url
                # If summon isn't already resolving to the resource
                # (in which case, great, use resolved_url!),
                # then see if we can do better
                if resolved_url.startswith('http://findit.library.gwu') or \
                   resolved_url.startswith('https://findit.library.gwu'):
                    # Construct the OpenURL request
                    # and get the OpenURL XML document
                    xmlurl = 'http://uz4ug4lz9g.openurl.xml.serialssolutions.com/openurlxml?version=1.0&' + document['openUrl']
                    f = urllib2.urlopen(xmlurl)
                    tree = f.read()
                    f.close()
                    # When there is a single child node of a given type,
                    # xmltodict.parse generates {child-node-type: child-node}
                    # but when there are mutiples it generates a list:
                    # {child-node-type: [child-node, child-node, ...]}
                    # We wish to force it to always create a list
                    data = xmltodict.parse(tree,
                                           force_list=('ssopenurl:result',
                                                       'ssopenurl:linkGroup',
                                                       'ssopenurl:url',))
                    match['OpenUrl'] = xmlurl

                    # Traverse the tree and look for the node(s) containing
                    # article link, if present
                    results = data['ssopenurl:openURLResponse']['ssopenurl:results']['ssopenurl:result']
                    try:
                        for result in results:
                            if not 'ssopenurl:linkGroups' in result:
                                break
                            linkgroups = result['ssopenurl:linkGroups']['ssopenurl:linkGroup']
                            found_article_url = False
                            for lg in linkgroups:
                                urlnodes = lg['ssopenurl:url']
                                articleurls = [node['#text'] for node in urlnodes if '@type' in node and node['@type'] == 'article']
                                if articleurls:
                                    # If there is one, replace with
                                    # the [first] OpenURL result.
                                    match['url'] = articleurls[0]
                                    # Done, stop here
                                    found_article_url = True
                                    break
                            if found_article_url:
                                # stop looping through results
                                break
                    except (TypeError, IndexError, KeyError):
                        # If there's an error, just stick with the resolved url
                        pass

        matches.append(match)

    bbmatches = []
    if d.get('recommendationLists', []):
        rl = d['recommendationLists']
        if rl.get('bestBet', []):
            bblist = rl['bestBet']
            for bestbet in bblist[:settings.DEFAULT_HIT_COUNT]:
                match = {'url': bestbet['link']}
                if bestbet.get('title', []):
                    match['title'] = bestbet['title']
                if bestbet.get('description', []):
                    match['description'] = bestbet['description']
                bbmatches.append(match)

    if d.get('didYouMeanSuggestions', {}):
        dym = d['didYouMeanSuggestions'][0]['suggestedQuery']
        response['dym'] = dym

    q = q.replace("%20", "%2b")
    q = q.replace("+", "%2b")
    q = q.replace("#", "%23")

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
    searchid = request.GET.get('searchid', 0)
    if scope == 'research_guides':
        save_result_count(searchid, "researchguides", response['count_total'])
    elif scope == 'articles':
        save_result_count(searchid, "articles", response['count_total'])
    return response


def summon_html(request, scope='all'):
    try:
        response = _summon_query(request, scope)
    except Exception as e:
        if scope == 'best_bets':
            # if summon isn't working, don't even bother showing best bets
            return render(request, 'emptypage.html')
        else:
            if scope == 'articles':
                scopeterm = 'article'
            if scope == 'books_media':
                scopeterm = 'books and media'
            if scope == 'research_guides':
                scopeterm = 'research guides'
            return _render_cleanerror(request, scopeterm, e)

    if scope == 'best_bets':
        responsepage = 'bestbets.html'
    else:
        responsepage = 'summon.html'
    return render(request, responsepage,
                  {'response': response, 'context': default_context_params()},
                  context_instance=RequestContext(request))


def summon_json(request, scope='all'):
    response = _summon_query(request, scope)
    return HttpResponse(json.dumps(response), content_type='application/json')


def books_media_html(request):
    return launchpad_html(request)


def books_media_json(request):
    return launchpad_json(request)


def _is_non_roman(request):
    q = request.GET.get('q', '')
    # TODO: Maybe there's a better way to do this. For now, it seems to work.
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
        count = int(request.GET.get('count', settings.DEFAULT_HIT_COUNT))
    except:
        count = settings.DEFAULT_HIT_COUNT
    # ----
    # TODO: Remove this once the Drupal search json packaging stops
    # choking on single quotes.  This wraps each word containing a '
    # in double quotes.  Not a perfect solution but it'll handle "most"
    # real-world queries
    qlist = q.split(' ')
    for i in range(len(qlist)):
        if qlist[i].find("\'") > -1:
            qlist[i] = '\"' + qlist[i] + '\"'
    q = ' '.join(qlist)
    # ----
    params = {'keys': q, 'fields': 'nid'}
    try:
        r = requests.get(settings.LIBSITE_SEARCH_URL, params=params,
                         timeout=settings.LIBSITE_TIMEOUT_SECONDS)
        more_url = settings.LIBSITE_MORE_URL
        site_url = settings.LIBSITE_URL
    except requests.exceptions.ConnectionError:
        r = requests.get(settings.LIBSITE_BACKUP_SEARCH_URL, params=params,
                         timeout=settings.LIBSITE_TIMEOUT_SECONDS)
        more_url = settings.LIBSITE_BACKUP_MORE_URL
        site_url = settings.LIBSITE_BACKUP_URL
    if r.status_code != 404:
        r.raise_for_status()

    response = {'more_url': '%s%s' % (more_url, q),
                'more_url_plain': site_url,
                'q': q}

    rtext = r.text
    # Strip off BOM if present (presence depends on Drupal site configuration)
    response_prefix = settings.LIBSITE_RESPONSE_BOM_PREFIX
    if r.text.startswith(response_prefix):
        rtext = r.text[len(response_prefix):]

    # Check for no-results case
    if rtext == "[\"Search returned no results.\"]":
        return response

    j = json.loads(rtext)
    matches = []
    for result in j[:count]:
        match = {}
        match['title'] = result['title']
        match['link'] = result['link']
        match['snippet'] = result['snippet']
        matches.append(match)
    response['count_total'] = len(j)
    response['matches'] = matches
    if settings.DEBUG:
        response['query_url'] = r.url
    return response


def libsite_html(request):
    try:
        response = _libsite_query(request)
    except Exception as e:
        libsearch_url = settings.LIBSITE_MORE_URL + request.GET.get('q')
        return _render_cleanerror(request, 'library website', e,
                                  settings.LIBSITE_SEARCH_LABEL,
                                  libsearch_url)

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
   

def _summon_healthcheck():
    headers = {}
    headers['Accept'] = 'application/json'
    headers['Host'] = settings.SUMMON_HOST
    headers['x-summon-date'] = datetime.datetime.utcnow().strftime(
        RFC2616_DATEFORMAT)
    headers['x-summon-session-id'] = ''
    id_str = _summon_id_string(headers['Accept'], headers['x-summon-date'],
                               settings.SUMMON_HOST,
                               settings.SUMMON_HEALTHCHECK_PATH,
                               '')
    hash_code = hmac.new(settings.SUMMON_API_KEY, id_str, hashlib.sha1)
    digest = base64.encodestring(hash_code.digest())
    auth_str = "Summon %s;%s" % (settings.SUMMON_API_ID, digest)
    auth_str = auth_str.replace('\n', '')
    headers['Authorization'] = auth_str
    url = 'http://%s%s' % (settings.SUMMON_HOST,
                           settings.SUMMON_HEALTHCHECK_PATH)
    try:
        r = requests.get(url, headers=headers,
                         timeout=settings.SUMMON_HEALTHCHECK_TIMEOUT_SECONDS)
    except:
        return False
    if r.status_code == 200:
        response = r.json()
        if response['status'] == 'available':
            return True
    return False


def summon_healthcheck_json(request):
    summon_status = _summon_healthcheck()
    if summon_status is True:
        response = {'status': 'available'}
    else:
        response = {'status': 'unavailable'}
    return HttpResponse(json.dumps(response), content_type='application/json')


def _render_cleanerror(request, scope, exception, altsite_label='',
                       altsite_url=''):
    # logger = logging.getLogger('django.request')
    logger.error("%s -- %s" % (request.get_full_path(), exception))
    # TODO: Log here
    return render(request, 'service_unavailable.html',
                  {'scope': scope, 'altsite_label': altsite_label,
                   'altsite_url': altsite_url})


def searches(request):
    tk = request.GET.get('token')
    if tk != settings.STAFF_TOKEN:
        return HttpResponseForbidden('Access Denied')

    sortby = request.GET.get("sort")
    if sortby not in ['id', '-id',
                      'q', '-q',
                      'date_searched', '-date_searched',
                      'articles_count', '-articles_count',
                      'books_count', '-books_count',
                      'database_count', '-database_count',
                      'journals_count', '-journals_count',
                      'researchguides_count', '-researchguides_count',
                      'islocal', '-islocal']:
        sortby = '-id'
    searches = Search.objects.order_by(sortby)

    page = request.GET.get("page")
    if page is None:
        page = 1
    elif not page.isdigit():
        page = 1
    elif int(page) == 0:
        page = 1

    per_page = request.GET.get("per_page")
    if per_page is None:
        per_page = 25
    elif not per_page.isdigit():
        per_page = 25
    elif int(per_page) == 0:
        per_page = 25

    p = Paginator(searches, per_page)
    try:
        searches = p.page(page)
    except EmptyPage:
        # get the last page
        searches = p.page(p.num_pages)

    # Top queries within the last n days
    last_n_days = request.GET.get("last_n_days")
    if last_n_days is None:
        last_n_days = settings.DEFAULT_LAST_N_DAYS
    elif not last_n_days.isdigit():
        last_n_days = settings.DEFAULT_LAST_N_DAYS
    elif int(last_n_days) == 0:
        last_n_days = settings.DEFAULT_LAST_N_DAYS

    top_n_searches = request.GET.get("top_n_searches")
    if top_n_searches is None:
        top_n_searches = settings.DEFAULT_TOP_N_SEARCHES
    elif not top_n_searches.isdigit():
        top_n_searches = settings.DEFAULT_TOP_N_SEARCHES
    elif int(top_n_searches) == 0:
        top_n_searches = settings.DEFAULT_TOP_N_SEARCHES

    qdata = Search.searchTermManager.searched_terms(last_n_days,
                                                    top_n_searches)
    headersort = {'id': '-', 'q': '', 'date_searched': '-'}
    # flip the bit for whichever column we're currently sorting on.
    # set the other columns to default.
    if sortby[0] == '-':
        headersort[sortby[1:]] = ''
    else:
        headersort[sortby] = '-'

    search_all_url = 'http://library.gwu.edu/search-all?query='
    if settings.LIBSITE_SEARCH_ALL_URL:
        search_all_url = settings.LIBSITE_SEARCH_ALL_URL

    return render(request, 'searches.html',
                  {'searches': searches,
                   'this_week_qdata': qdata,
                   'headersort': headersort,
                   'last_n_days': last_n_days,
                   'top_n_searches': top_n_searches,
                   'search_all_url': search_all_url})


def save_data(request):
    querystring = request.GET.get('q', '')
    response = {}
    if querystring and not (request.GET.get('ignoresearch') == 'true'):
        s = Search(q=querystring)
        s.islocal = _is_request_local(request)
        s.save()
        response['searchid'] = s.id
    return HttpResponse(json.dumps(response))


def save_result_count(searchid, section_name, count):
    if searchid == 0:
        return
    if(section_name == "articles"):
        Search.objects.filter(id=searchid).update(
            articles_count=count)
    elif(section_name == "books"):
        Search.objects.filter(id=searchid).update(
            books_count=count)
    elif(section_name == "database"):
        Search.objects.filter(id=searchid).update(
            database_count=count)
    elif(section_name == "journals"):
        Search.objects.filter(id=searchid).update(
            journals_count=count)
    elif(section_name == "researchguides"):
        Search.objects.filter(id=searchid).update(
            researchguides_count=count)
