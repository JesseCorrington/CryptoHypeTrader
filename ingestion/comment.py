from textblob import TextBlob


class Comment:
    def __init__(self, text, score):
        self.text = text
        self.score = score
        self.sentiment = TextBlob(self.text).polarity

        # TODO: consider cleaning the text here

    def __str__(self):
        return self.text

    def count_refs(self, token):
        return self.text.count(token)


class CommentScanner:
    def __init__(self):
        self.__comments = []

    def _add_comment(self, text, score):
        self.__comments.append(Comment(text, score))

    def find_comments(self):
        raise NotImplementedError("CommentDataSource subclass must implement get_comments")

    def count(self):
        return len(self.__comments)

    def sum_score(self):
        return sum(c.score for c in self.__comments)

    def avg_score(self):
        return self.sum_score() / len(self.__comments)

    def avg_sentiment(self):
        return sum(c.sentiment for c in self.__comments) / len(self.__comments)


    # TODO: implement
    def count_strong_pos(self):
        return 0

    def count_strong_neg(self):
        return 0
