import datetime
import re
import praw
from ingestion import util, config


# Provides access to reddit subscriber count numbers

def get_current_stats(subreddit):
    reddit = praw.Reddit(client_id=config.reddit["client_id"],
                         client_secret=config.reddit["client_secret"],
                         user_agent=config.reddit["user_agent"])

    try:
        subreddit = reddit.subreddit(subreddit)

        stats = {
            "reddit_subscribers": subreddit.subscribers,
            "reddit_active:": subreddit.accounts_active
        }

        return stats
    except Exception as err:
        return None


def get_historical_stats(coin, start=datetime.date(2011, 1, 1)):
    # There is no API to get historic subscriber counts, so scrape the data from redditmetrics.com
    # Once we're collecting data daily, we can just get the live stats from reddit and not use this

    url = "http://redditmetrics.com/r/" + coin["subreddit"]
    html = util.geturl_text(url)

    dataStart = html.find("element: 'total-subscribers',")
    html = html[dataStart:]
    dataEnd = html.find("]")
    html = html[:dataEnd]

    pattern = "{y: '(\\d\\d\\d\\d-\\d\\d-\\d\\d)', a: (\d*)}"
    matches = re.findall(pattern, html)

    stats = []
    for date, total_subs in matches:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        if date >= start:
            stats.append({
                "symbol": coin["symbol"],
                "date": date,
                "reddit_subscribers": int(total_subs)
            })

    # There are a few duplicate days on reddit metrics, so just average them to fix our data
    # this only seems to have happened once a year, so no big deal
    prev = None
    for item in stats:
        if prev and prev["date"] == item["date"]:
            prev["reddit_subscribers"] = int((prev["reddit_subscribers"] + item["reddit_subscribers"]) / 2.0)
            stats.remove(item)
        else:
            prev = item

    return stats

