# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class UnicodeHMACTest(TestCase):
    QUERY_PAIRS = [
        ('prisoner of azkaban', 'Rowling'),
        ('the bluest eye', 'Morrison'),
        (u'夏目漱石', 'Natsume'),  # Kanji: Natsume Soseki
    ]

    def test_unicode_hmac(self):
        """Ensure HMAC signing properly handles unicode."""
        c = Client()
        for query, match_str in self.QUERY_PAIRS:
            response = c.get('/books_media_html', {'q': query})
            self.assertTrue(match_str in response.content)


class RemoteIPTest(TestCase):
    # https://github.com/gwu-libraries/obento/issues/2
    ON_CAMPUS_IP = '128.164.215.206'
    OFF_CAMPUS_IP = '254.254.254.254'
    QUERY = '/articles_html?q=organic+photovoltaics+su'
    MATCH_STR = 'Lan, SC, Wei, KH, Su, YW'

    def test_is_request_local_on_campus(self):
        c = Client()
        query_on_campus = '%s&remote_addr=%s' % (self.QUERY, self.ON_CAMPUS_IP)
        response_on_campus = c.get(query_on_campus)
        self.assertTrue(self.MATCH_STR in response_on_campus.content)

    def test_is_request_local_off_campus(self):
        c = Client()
        query_off_campus = '%s&remote_addr=%s' % (self.QUERY,
                                                  self.OFF_CAMPUS_IP)
        response_off_campus = c.get(query_off_campus)
        self.assertFalse(self.MATCH_STR in response_off_campus.content)
