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
            "subscribers": subreddit.subscribers,
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
            "subscribers": int(total_subs)
        })

    stats.sort(key=lambda x: x["date"])
    return stats
