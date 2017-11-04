import praw
import re
import datetime
import database as db
import util

def get_current_stats(subreddit):
    reddit = praw.Reddit(client_id=CONFIG["reddit_client_id"],
                         client_secret=CONFIG["reddit_client_secret"],
                         user_agent=CONFIG["reddit_user_agent"])

    try:
        subreddit = reddit.subreddit(subreddit)

        stats = {
            "reddit_subscribers": subreddit.subscribers,
            "active:": subreddit.accounts_active
        }

        return stats
    except Exception as err:
        return None


def get_historical_stats(coin, start=datetime.date(2011, 1, 1)):
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

