import datetime
import re
import praw
import prawcore
from ingestion import config
from ingestion import datasource as ds
from ingestion import comment


# Provides access to reddit subscriber count numbers and average sentiment

api = None


def init_api():
    global api

    if api is not None:
        return

    # Use a single praw instance, so we get correct throttling per reddit's limits
    api = praw.Reddit(client_id=config.reddit["client_id"],
                      client_secret=config.reddit["client_secret"],
                      user_agent=config.reddit["user_agent"])


class CommentScanner(comment.CommentScanner):
    def __init__(self, coin, hours):
        super().__init__()
        self.subreddit_name = coin["subreddit"]
        self.hours = hours
        # TODO: do we want to use hours to filter out old data?

    def find_comments(self):
        global api

        submission_limit = 20
        subreddit = api.subreddit(self.subreddit_name)

        # Need to a bit to the submission limit here, because we'll likely get back some
        # stickied submissions that we ignore below
        limit = submission_limit + 5
        submission_set = {
            "hot": subreddit.hot(limit=limit),
            "new": subreddit.new(limit=limit),
            "rising": subreddit.rising(limit=limit)
        }

        for name, submissions in submission_set.items():
            # Ignore stickied posts and limit submissions
            submissions = [x for x in submissions if not x.stickied and x.score > 0]
            submissions = submissions[:submission_limit]

            for submission in submissions:
                self.scan_submission(submission)

    def scan_submission(self, submission):
        if submission.selftext:
            # give 80 percent of the score to the body, and 20 percent to the title
            self._add_comment(submission.title, submission.score * 0.2)
            self._add_comment(submission.selftext, submission.score * 0.8)
        else:
            self._add_comment(submission.title, submission.score)

        self.scan_comments(submission.comments)

    def scan_comments(self, comments):
        # exclude comments with negative scores
        comments = [x for x in comments if hasattr(x, "score") and x.score > 0]
        for c in comments:
            self._add_comment(c.body, c.score)

            if len(c.replies) > 0:
                self.scan_comments(c.replies)


def get_current_stats(subreddit_name):
    subreddit = api.subreddit(subreddit_name)
    stats = {
        "subscribers": subreddit.subscribers,
        "active": subreddit.accounts_active
    }

    return stats


def is_valid(subreddit_name):
    try:
        get_current_stats(subreddit_name)
    except (prawcore.exceptions.NotFound, prawcore.exceptions.Forbidden, prawcore.exceptions.Redirect):
        return False

    return True


class HistoricalStats(ds.DataSource):
    def __init__(self, coin, start=datetime.datetime(2011, 1, 1)):
        url = "http://redditmetrics.com/r/" + coin["subreddit"]
        super().__init__(url, response_format="text")
        self._start = start

    def parse(self, html):
        # There is no API to get historical subscriber counts, so scrape the data from redditmetrics.com
        # Once we're collecting data daily, we can just get the live stats from reddit and not use this
        dataStart = html.find("element: 'total-subscribers',")
        html = html[dataStart:]
        dataEnd = html.find("]")
        html = html[:dataEnd]

        pattern = "{y: '(\\d\\d\\d\\d-\\d\\d-\\d\\d)', a: (\d*)}"
        matches = re.findall(pattern, html)

        stats = []
        for date, total_subs in matches:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
            if date >= self._start:
                stats.append({
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
