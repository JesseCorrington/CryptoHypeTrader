from unittest import TestCase
from ingestion import reddit
from datetime import datetime, timedelta


class TestReddit(TestCase):
    def test_get_historical_stats(self):
        coin = {"subreddit": "bitcoin"}

        stats = reddit.HistoricalStats(coin).get()

        stats.sort(key=lambda x: x["date"], reverse=True)

        newest = stats[0]["date"]
        oldest = stats[-1]["date"]

        today = datetime.today()

        self.assertTrue(newest > oldest)
        self.assertTrue(today - newest < timedelta(days=3))

        # test using a date range
        start = datetime(2017, 1, 1)
        prices = reddit.HistoricalStats(coin, start).get()
        prices.sort(key=lambda x: x["date"], reverse=True)

        self.assertTrue(start == prices[-1]["date"])

    def test_get_current_stats(self):
        stats = reddit.get_current_stats("bitcoin")
        self.assertTrue(stats["subscribers"] > 1)
        self.assertTrue(stats["active"] > 1)

    def test_get_sentiment(self):
        polarities = reddit.get_avg_sentiment("bitcoin")
        print(polarities)

        self.assertTrue(-1.0 <= polarities["hot"] <= 1.0)
        self.assertTrue(-1.0 <= polarities["new"] <= 1.0)
        self.assertTrue(-1.0 <= polarities["rising"] <= 1.0)

    def test_is_valid(self):
        self.assertEqual(reddit.is_valid("bitcoin"), True)
        self.assertEqual(reddit.is_valid("doesnotexistdoesnotexistdoesnotexist"), False)
