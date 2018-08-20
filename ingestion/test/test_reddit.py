from datetime import datetime, timedelta
from unittest import TestCase

from ingestion.datasources import reddit


class TestReddit(TestCase):
    def test_get_historical_stats(self):
        coin = {"subreddit": "bitcoin"}

        stats = reddit.HistoricalStats(coin).get()

        stats.sort(key=lambda x: x["date"], reverse=True)

        newest = stats[0]["date"]
        oldest = stats[-1]["date"]

        self.assertGreater(newest, oldest)

        # test using a date range
        start = datetime(2017, 1, 1)
        prices = reddit.HistoricalStats(coin, start).get()
        prices.sort(key=lambda x: x["date"], reverse=True)

        self.assertEqual(start, prices[-1]["date"])

    def test_get_current_stats(self):
        stats = reddit.get_current_stats("bitcoin")
        self.assertGreater(stats["subscribers"], 1)
        self.assertGreater(stats["active"], 1)

    def test_is_valid(self):
        self.assertEqual(reddit.is_valid("bitcoin"), True)
        self.assertEqual(reddit.is_valid("doesnotexistdoesnotexistdoesnotexist"), False)

    def test_comment_scanner(self):
        reddit.init_api()

        coin = {
            "subreddit": "bitcoin"
        }

        btc_scanner = reddit.CommentScanner(coin, 1)
        btc_scanner.find_comments()
        self.assertGreater(btc_scanner.count(), 100)
        self.assertGreater(btc_scanner.sum_score(), 1000)
        self.assertGreater(btc_scanner.avg_score(), 10)
        self.assertGreater(btc_scanner.avg_sentiment(), -1)
        self.assertLess(btc_scanner.avg_sentiment(), 1)

        self.assertGreater(btc_scanner.count_strong_pos(), 0)
        self.assertGreater(btc_scanner.count_strong_neg(), 0)
