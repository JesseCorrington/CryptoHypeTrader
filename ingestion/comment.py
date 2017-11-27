from textblob import TextBlob


class Comment:
    def __init__(self, text, score):
        self.text = text
        self.score = score
        self.sentiment = TextBlob(self.text).polarity

    def __str__(self):
        return self.text

    def count_refs(self, token):
        return self.text.count(token)


class CommentScanner:
    def __init__(self):
        self.comments = []

    def find_comments(self):
        raise NotImplementedError("CommentDataSource subclass must implement get_comments")

    def count(self):
        return len(self.comments)

    def sum_score(self):
        return sum(c.score for c in self.comments)

    def avg_score(self):
        return self.sum_score() / len(self.comments)

    def avg_sentiment(self):
        return sum(c.sentiment for c in self.comments) / len(self.comments)
