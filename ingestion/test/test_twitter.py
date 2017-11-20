from unittest import TestCase
from ingestion .datasources import twitter


class TestTwitter(TestCase):
    def test_counts(self):
        hours = 1
        self.assertTrue(twitter.count_tweets("btc", hours) > 100)
        self.assertTrue(twitter.count_tweets("eth", hours) > 100)
