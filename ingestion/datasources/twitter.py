import time
import datetime
import tweepy
from ingestion import config


def count_tweets(symbol, hours):
    auth = tweepy.OAuthHandler(config.twitter["api_key"], config.twitter["api_secret"])
    auth.set_access_token(config.twitter["access_token"], config.twitter["access_token_secret"])
    api = tweepy.API(auth)

    query = "$" + symbol.lower()
    now = datetime.datetime.utcnow()
    max_old = datetime.timedelta(hours=hours)

    # 450 requests in a 15 minute interval.
    api_wait = 60 * 15

    # This is the maximum number of tweets the api wil give us per page
    # this means we can get a maximum of 45,000 tweets every 15 minutes, assuming all full pages
    max_count = 100

    count = 0

    c = tweepy.Cursor(api.search, q=query, include_entities=False, result_type="recent", count=max_count).items()

    while True:
        try:
            tweet = c.next()

            old = now - tweet.created_at
            if old > max_old:
                break

            count += 1

        except tweepy.TweepError:
            print("Twitter Rate limit exceeded, waiting 15 minutes")
            time.sleep(api_wait)
            continue
        except StopIteration:
            break

    print(symbol, count)
    return count


