import datetime
import re
import praw
import textblob
import numpy as np

from ingestion import config
from ingestion import datasource as ds


# Provides access to reddit subscriber count numbers


def get_avg_sentiment(subreddit_name):
    # Calculate the current average sentiment of the top reddit posts, defined as follows
    # sentiment(subreddit) = avg(sentiment(s1), sentiment(s2), ... sentiment(sn), weights=submission_scores)
    # sentiment(reddit_submission) = avg(sentiment(title), sentiment(body), sentiment(comments)
    # sentiment(comments) = avg(sentiment(c1), sentiment(c2), ... sentiment(cn), weights=comment_scores)

    reddit = praw.Reddit(client_id=config.reddit["client_id"],
                         client_secret=config.reddit["client_secret"],
                         user_agent=config.reddit["user_agent"])

    subreddit = reddit.subreddit(subreddit_name)

    comment_limit = 20
    submission_limit = 20


    def comments_polarity(comments):
        polarities, scores = _comments_polarity(comments)
        if polarities == None or scores == None:
            return None

        return np.average(polarities, weights=scores)

    def _comments_polarity(comments, depth=0):
        depth_weights = [1, .7, .4]

        if depth >= len(depth_weights):
            return None, None

        comment_polarities = []
        comment_scores = []

        # exclude comments with negative score and limit
        comments = [x for x in comments if hasattr(x, "score") and x.score > 0]
        comments[:comment_limit]

        if len(comments) == 0:
            return None, None

        for comment in comments:
            comment_polarity = textblob.TextBlob(comment.body).polarity

            comment_polarities.append(comment_polarity)

            # Weight the comment by it's depth, so deeper ones count less
            weighted_score = comment.score * depth_weights[depth]
            comment_scores.append(weighted_score)

            # TODO: get comment replies too
            if len(comment.replies) > 0:
                polarities, scores = _comments_polarity(comment.replies, depth + 1)
                if polarities != None and scores != None:
                    comment_polarities + polarities
                    comment_scores + scores

        # Now calculate a weighted avg for all comment polarities, using score as weight factor
        return comment_polarities, comment_scores

    def submission_polarity(submission):
        polarities_to_avg = []
        polarities_to_avg.append(textblob.TextBlob(submission.title).polarity)

        if submission.selftext:
            # Average the polarity from title and body
            polarities_to_avg.append(textblob.TextBlob(submission.selftext).polarity)

        avg_comment_polarity = comments_polarity(submission.comments)
        if avg_comment_polarity:
            polarities_to_avg.append(avg_comment_polarity)

        return np.average(polarities_to_avg)

    # Need to a bit to the submission limit here, beceause we'll likely get back some
    # stickied submissions that we ignore below
    limit = submission_limit + 5
    submission_set = {
        "hot": subreddit.hot(limit=limit),
        "new": subreddit.new(limit=limit),
        "rising": subreddit.rising(limit=limit)
    }

    polarities = []
    scores = []
    avg_polarities = {}

    for name, submissions in submission_set.items():
        # Ignore stickied posts and limit submissions
        submissions = [x for x in submissions if not x.stickied and x.score > 0]
        submissions = submissions[:submission_limit]

        for submission in submissions:
            polarities.append(submission_polarity(submission))
            scores.append(submission.score)

        avg_polarities[name] = np.average(polarities, weights=scores)

    return avg_polarities


def get_current_stats(subreddit_name):
    reddit = praw.Reddit(client_id=config.reddit["client_id"],
                         client_secret=config.reddit["client_secret"],
                         user_agent=config.reddit["user_agent"])

    subreddit = reddit.subreddit(subreddit_name)
    stats = {
        "subscribers": subreddit.subscribers,
        "active": subreddit.accounts_active
    }

    return stats


class HistoricalStats(ds.DataSource):
    def __init__(self, coin, start=datetime.datetime(2011, 1, 1)):
        url = "http://redditmetrics.com/r/" + coin["subreddit"]
        super().__init__(url, format="text")
        self._start = start

    def parse(self, html):
        # There is no API to get historic subscriber counts, so scrape the data from redditmetrics.com
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
