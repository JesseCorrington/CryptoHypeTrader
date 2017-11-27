from unittest import TestCase
from ingestion .datasources import twitter
from ingestion import tasks


class TestTwitter(TestCase):
    def test_import_twitter_comments(self):
        twitter.init_api()

        tasks.ImportCommentStats("twitter_comments", twitter.CommentScanner).run()
