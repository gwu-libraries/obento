# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client


class UnicodeHMACTest(TestCase):
    QUERY_PAIRS = [
        ('prisoner of azkaban', 'Rowling'),
        ('the bluest eye', 'Morrison'),
        (u'piÃ±ata', 'Christopher'),
    ]

    def test_unicode_hmac(self):
        """Ensure HMAC signing properly handles unicode."""
        c = Client()
        for query, match_str in self.QUERY_PAIRS:
            response = c.get('/', {'q': query})
            self.assertTrue(match_str in response.content)
