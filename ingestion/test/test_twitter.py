from unittest import TestCase
from ingestion .datasources import twitter


class TestTwitter(TestCase):
    def test_comment_scanner(self):
        twitter.init_api()

        hours = 1
        btc_scanner = twitter.CommentScanner("btc", hours)
        btc_scanner.find_comments()
        self.assertTrue(btc_scanner.count() > 100)
        self.assertTrue(btc_scanner.sum_score() > 10000)
        self.assertTrue(btc_scanner.avg_score() > 10)
        self.assertTrue(-1 < btc_scanner.avg_sentiment() < 1)

        eth_scanner = twitter.CommentScanner("eth", hours)
        eth_scanner.find_comments()
        self.assertTrue(eth_scanner.count() > 100)
        self.assertTrue(eth_scanner.sum_score() > 10000)
        self.assertTrue(eth_scanner.avg_score() > 10)
        self.assertTrue(-1 < eth_scanner.avg_sentiment() < 1)
