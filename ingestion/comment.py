import re
from textblob import TextBlob


class Comment:
    """Represents a social media comment"""

    def __init__(self, text, score):
        self.text = text if isinstance(text, str) else ""
        self.score = score if isinstance(score, int) else 0
        self.clean_text = self.__clean_text(self.text)
        self.sentiment = TextBlob(self.clean_text).polarity

    def __str__(self):
        return self.text

    def count_refs(self, token):
        """Count the number of times a search string appears inside a comment"""
        return self.text.count(token)

    @staticmethod
    def __clean_text(text):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", text).split())


class CommentScanner:
    """Abstract base class for scanning comments on social media sites
    implement a concrete base class to scan comments on reddit, twitter, etc.
    """

    def __init__(self):
        self.__comments = []
        self.__strong_threshold = .5

    def _add_comment(self, text, score):
        """Derived classes should call this when they find a new comment to add"""

        self.__comments.append(Comment(text, score))

    def find_comments(self):
        raise NotImplementedError("CommentScanner subclass must implement get_comments")

    def count(self):
        """The number of comments scanned"""

        return len(self.__comments)

    def sum_score(self):
        """The sum of the scores of all the comments scanned"""

        return sum(c.score for c in self.__comments)

    def avg_score(self):
        """The average score of all the comments scanned"""

        if len(self.__comments) == 0:
            return 0

        return self.sum_score() / len(self.__comments)

    def avg_sentiment(self):
        """The average sentiment of all the comments scanned"""

        if len(self.__comments) == 0:
            return 0

        return sum(c.sentiment for c in self.__comments) / len(self.__comments)

    def count_strong_pos(self):
        """The count of comments with a strong positive sentiment"""

        return sum(1 if c.sentiment > self.__strong_threshold else 0 for c in self.__comments)

    def count_strong_neg(self):
        """The count of comments with a strong negative sentiment"""

        return sum(1 if c.sentiment < -self.__strong_threshold else 0 for c in self.__comments)

    def strong_pos(self):
        """The list of comments with a strong positive sentiment"""

        return [c for c in self.__comments if c.sentiment > self.__strong_threshold]

    def strong_neg(self):
        """The list of comments with a strong negative sentiment"""

        return [c for c in self.__comments if c.sentiment < -self.__strong_threshold]
