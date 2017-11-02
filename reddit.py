import praw
import re
import datetime
from database import *


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
    for date, total_subs in matches:
        stats.append({
            "date": datetime.datetime.strptime(date, "%Y-%m-%d"),
            "subscribers": int(total_subs)
        })

    return stats

def save_historic_stats(subreddit, symbol):
    daily_stats = get_historical_stats(subreddit)
    collection = MONGO_DB.social_stats

    # TODO: only insert if date is not there
    for day in daily_stats:
        day["symbol"] = symbol
        collection.insert_one(day)
