from unittest import TestCase
from ingestion .datasources import twitter


class TestTwitter(TestCase):
    def test_comment_scanner(self):
        twitter.init_api()

        btc = {
            "symbol": "BTC"
        }
        eth = {
            "symbol": "ETH"
        }
        hours = 1

        btc_scanner = twitter.CommentScanner(btc, hours)
        btc_scanner.find_comments()
        self.assertGreater(btc_scanner.count(), 100)
        self.assertGreater(btc_scanner.sum_score(), 10000)
        self.assertGreater(btc_scanner.avg_score(), 10)
        self.assertGreater(btc_scanner.avg_sentiment(), -1)
        self.assertLess(btc_scanner.avg_sentiment(), 1)

        eth_scanner = twitter.CommentScanner(eth, hours)
        eth_scanner.find_comments()
        self.assertGreater(eth_scanner.count(), 100)
        self.assertGreater(eth_scanner.sum_score(), 10000)
        self.assertGreater(eth_scanner.avg_score(), 10)
        self.assertGreater(eth_scanner.avg_sentiment(), -1)
        self.assertLess(eth_scanner.avg_sentiment(), 1)
