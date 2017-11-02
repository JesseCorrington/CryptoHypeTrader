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


def get_historical_stats(subreddit, symbol):
    url = "http://redditmetrics.com/r/" + subreddit
    html = util.geturl_text(url)

    dataStart = html.find("element: 'total-subscribers',")
    html = html[dataStart:]
    dataEnd = html.find("]")
    html = html[:dataEnd]

    pattern = "{y: '(\\d\\d\\d\\d-\\d\\d-\\d\\d)', a: (\d*)}"
    matches = re.findall(pattern, html)

    stats = []
    for date, total_subs in matches:
        stats.append({
            "symbol": symbol,
            "date": datetime.datetime.strptime(date, "%Y-%m-%d"),
            "reddit_subscribers": int(total_subs)
        })

    prev = None
    for item in stats:
        if prev and prev["date"] == item["date"]:
            # TODO: it might be better to average these
            prev["reddit_subscribers"] = int((prev["reddit_subscribers"] + item["reddit_subscribers"]) / 2.0)
            stats.remove(item)
        else:
            prev = item

    return stats

