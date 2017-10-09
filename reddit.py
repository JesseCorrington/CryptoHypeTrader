import praw
from util import *
import re
import datetime


def get_current_stats(subreddit):
    reddit = praw.Reddit(client_id=CONFIG["reddit_client_id"],
                         client_secret=CONFIG["reddit_client_secret"],
                         user_agent=CONFIG["reddit_user_agent"])

    subreddit = reddit.subreddit(subreddit)

    stats = {
        "subscribers": subreddit.subscribers,
        "active:": subreddit.accounts_active
    }

    return stats


def get_historical_stats(subreddit):
    url = "http://redditmetrics.com/r/" + subreddit
    html = geturl_text(url)

    dataStart = html.find("element: 'total-subscribers',")
    html = html[dataStart:]
    dataEnd = html.find("]")
    html = html[:dataEnd]

    pattern = "{y: '(\\d\\d\\d\\d-\\d\\d-\\d\\d)', a: (\d*)}"
    matches = re.findall(pattern, html)

    stats = []
    for date, growth in matches:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")

        stats.append({
            "date": date,
            "subscribers": growth
        })

    return stats