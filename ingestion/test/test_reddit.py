from unittest import TestCase
from ingestion import reddit
from datetime import datetime, timedelta

class TestReddit(TestCase):
    def test_get_historical_stats(self):
        stats = reddit.HistoricalStats("bitcoin").get()

        stats.sort(key=lambda x: x["date"], reverse=True)

        newest = stats[0]["date"]
        oldest = stats[-1]["date"]

        today = datetime.today()

        self.assertTrue(newest > oldest)
        self.assertTrue(today - newest < timedelta(days=3))

        # test using a date range
        start = datetime(2017, 1, 1)
        prices = reddit.HistoricalStats("bitcoin", start).get()
        prices.sort(key=lambda x: x["date"], reverse=True)

        self.assertTrue(start == prices[-1]["date"])

    def test_get_current_stats(self):
        stats = reddit.get_current_stats("bitcoin")
        print(stats)
        self.assertTrue(stats["reddit_subscribers"] > 1)
        self.assertTrue(stats["reddit_active"] > 1)
