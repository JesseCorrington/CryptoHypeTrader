import time
import datetime
import tweepy
from ingestion import config
from ingestion import comment


# Provides access to sentiment data for twitter comments via the twitter.com API


api = None


def init_api():
    global api

    if api is not None:
        return

    auth = tweepy.OAuthHandler(config.twitter["api_key"], config.twitter["api_secret"])
    auth.set_access_token(config.twitter["access_token"], config.twitter["access_token_secret"])
    api = tweepy.API(auth)


class CommentScanner(comment.CommentScanner):
    def __init__(self, coin, hours):
        super().__init__()

        self.query = "$" + coin["symbol"].lower()
        self.hours = hours

    def find_comments(self):
        global api

        now = datetime.datetime.utcnow()
        max_old = datetime.timedelta(hours=self.hours)

        # 450 requests in a 15 minute interval.
        api_wait = 60 * 15

        # This is the maximum number of tweets the api wil give us per page
        # this means we can get a maximum of 45,000 tweets every 15 minutes, assuming all full pages
        max_count = 100

        c = tweepy.Cursor(api.search, q=self.query, include_entities=False,
                          result_type="recent", count=max_count).items()

        while True:
            try:
                tweet = c.next()
                old = now - tweet.created_at
                if old > max_old:
                    break

                # TODO: we should also factor in how many users a follower has into scoring

                # The base score value is 1, so add it here
                score = tweet.retweet_count + 1
                self._add_comment(tweet.text, score)

            except tweepy.TweepError:
                print("Twitter Rate limit exceeded, waiting 15 minutes")
                time.sleep(api_wait)
                continue
            except StopIteration:
                break
