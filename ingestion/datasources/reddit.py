import datetime
import re
import praw
import prawcore
import textblob
import numpy as np

from ingestion import config
from ingestion import datasource as ds


# Provides access to reddit subscriber count numbers and average sentiment

# TODO: seems that having this be global is causing thread shutdown issues

# Use a single praw instance, so we get correct throttling per reddit's limits
__reddit = praw.Reddit(client_id=config.reddit["client_id"],
                       client_secret=config.reddit["client_secret"],
                       user_agent=config.reddit["user_agent"])


def __comments_polarity(comments, comment_limit=20, depth=0):
    # don't need to be too aggressive when weighting down nested comments,
    # as they should already have a lower score
    depth_weights = [1, .9, .8, .7]

    if depth >= len(depth_weights):
        return [], []

    comment_polarities = []
    comment_scores = []

    # exclude comments with negative scores and limit
    comments = [x for x in comments if hasattr(x, "score") and x.score > 0]
    comments = comments[:comment_limit]

    if len(comments) == 0:
        return [], []

    for comment in comments:
        comment_polarity = textblob.TextBlob(comment.body).polarity
        comment_polarities.append(comment_polarity)

        # Weight the comment by it's score and depth, so deeper ones count less
        weighted_score = comment.score * depth_weights[depth]
        comment_scores.append(weighted_score)

        if len(comment.replies) > 0:
            polarities, scores = __comments_polarity(comment.replies, int(comment_limit / 2), depth + 1)
            if polarities is not None and scores is not None:
                comment_polarities += polarities
                comment_scores += scores

    return comment_polarities, comment_scores


def __submission_polarity(submission):
    title_weight = 1
    body_weight = 3
    comments_weight = 3

    title_polarity = textblob.TextBlob(submission.title).polarity
    polarities_to_avg = [title_polarity]
    weights = [title_weight]

    if submission.selftext:
        text_polarity = textblob.TextBlob(submission.selftext).polarity
        polarities_to_avg.append(text_polarity)
        weights.append(body_weight)

    comment_polarities, comment_scores = __comments_polarity(submission.comments)
    if len(comment_polarities) > 0 and len(comment_scores) > 0:
        avg_comments_polarity = np.average(comment_polarities, weights=comment_scores)
        polarities_to_avg.append(avg_comments_polarity)
        weights.append(comments_weight)

    # count strong negative and positives
    pos = 0
    neg = 0
    threshold = 0.3

    for p in polarities_to_avg:
        if p > threshold:
            pos += 1
        if p < -threshold:
            neg += 1

    return np.average(polarities_to_avg, weights=weights), pos, neg


# TODO: this should be moved to a sentiment model,
# data sources should just be generic ways to get the data

def get_avg_sentiment(subreddit_name):
    # Calculate the current average sentiment of the top reddit posts, defined as follows
    # sentiment(subreddit) = avg(sentiment(s1), sentiment(s2), ... sentiment(sn), weights=submission_scores)
    # sentiment(reddit_submission) = avg(sentiment(title), sentiment(body), sentiment(comments)
    # sentiment(comments) = avg(sentiment(c1), sentiment(c2), ... sentiment(cn), weights=comment_scores)

    submission_limit = 20
    subreddit = __reddit.subreddit(subreddit_name)

    # Need to a bit to the submission limit here, because we'll likely get back some
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
    counts = {name: {"pos": 0, "neg": 0} for name in submission_set}

    for name, submissions in submission_set.items():
        # Ignore stickied posts and limit submissions
        submissions = [x for x in submissions if not x.stickied and x.score > 0]
        submissions = submissions[:submission_limit]

        for submission in submissions:
            polarity, positive, negative = __submission_polarity(submission)
            polarities.append(polarity)
            scores.append(submission.score)
            counts[name]["pos"] += positive
            counts[name]["neg"] += negative

        avg_polarities[name] = np.average(polarities, weights=scores)

    avg_polarities["counts"] = counts

    return avg_polarities


def get_current_stats(subreddit_name):
    subreddit = __reddit.subreddit(subreddit_name)
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
