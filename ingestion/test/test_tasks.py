from unittest import TestCase
from ingestion .datasources import twitter, reddit
from ingestion import tasks


class TestTwitter(TestCase):
    def test_import_twitter_comments(self):
        twitter.init_api()
        tasks.ImportCommentStats("twitter_comments", twitter.CommentScanner, {"twitter": {"$exists": True}}, 1).run()

    def test_import_reddit_comments(self):
        reddit.init_api()
        tasks.ImportCommentStats("reddit_comments", reddit.CommentScanner, {"subreddit": {"$exists": True}}).run()

    def test_import_cc_stats(self):
        tasks.init()
        tasks.ImportCryptoCompareStats().run()
