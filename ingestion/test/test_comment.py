from unittest import TestCase

from ingestion.comment import Comment, CommentScanner


class TestComment(TestCase):
    def test_init(self):
        c = Comment("this is a comment", 150)
        self.assertEqual(c.text, "this is a comment")
        self.assertEqual(c.score, 150)

    def test_init_badinput(self):
        c1 = Comment(None, None)
        self.assertEqual(c1.text, "")
        self.assertEqual(c1.score, 0)

        c2 = Comment(1234, "a score")
        self.assertEqual(c2.text, "")
        self.assertEqual(c2.score, 0)

    def test_str(self):
        c = Comment("this is a comment", 100)
        self.assertEqual(str(c), "this is a comment")

    def test_count_refs(self):
        c = Comment("hodl bitcoin buy buy bitcoin", 1)
        self.assertEqual(c.count_refs("hodl"), 1)
        self.assertEqual(c.count_refs("bitcoin"), 2)
        self.assertEqual(c.count_refs("buy"), 2)

    def test_sentiment(self):
        texts = [
            """I almost spent 1 BTC on 2000 ETH in the crowd sale but they didn't even have a working product then so I said fuck that. I have NO regrets about that as I would still not invest in vapourware.
            I've stuck to this rule so resisted pretty much every single alt and ICO, even through the mad bull
            run last year I stuck to my rule.""",

            """Despite falling prices this year, clients @etoro are increasing not decreasing their $BTC holdings.""",

            """will be entering a $BTC long with $6626 break, SL placed below 6k support around $5800 
            (below low of the weekly candle). anticipating Higher Low reversal and rejection at EMA 100 in Weekly, 
            EMA 200 in 3D. if $6626 does not get triggered, no position will be entered. """,

            """Alright, time for a little gamble on my part:
            If $BTC goes over $35,000 by the end of the year, I will give everyone who retweets this AND FOLLOWS ME 0.1 Bitcoin ($3,500)
            You have to follow me in order to win, if we hit $35,000 on BTC I can rest easy for life, blessed 🙏❤️🚀""",

            """I love this project , thank you for sharing this information and spreading awareness on APEX :)""",

            """Been holding since the ICO and averaging cost since then
            Solid team and existing customer base. extremely cheap to pick up now""",

            """This is definitely a moonshot in my opinion. Its so cheap right now that it seems like a 
            steal! Count me in. For me the biggest draw is having the parent company with 350 odd enterpise customers. 
            Surely some will adopt this product of theirs! The price sucks but everything has dropped badly that had 
            their crowdsale this year. I dont understand why some ppl slate apex because while other utility tokens 
            scrap and beg for any type of partnerships or customers, Apex has a long list that they can speak to 
            because of the parent company. Anyways.. im going long with this one and loading up""",

            """Honestly, it doesn't matter what the product is. Utility tokens are a joke, IMHO, and their 
            "utility" has never so far provided them with any value. Prices go up from pure speculation, and 
            then - when there is a product or final form - they dump, usually forever.
            Don't worry about that, it will be months away. For now, accept that the crypto market is how it is, and roll 
            with it. Tiny cap and major exchange listings, and a team willing to pump the coin - that's what counts. Like 
            or not.""",

            """This is good, It is taking time but it will be worth the long wait. Over the years more and 
            more people, companies, websites etc.... are accepting bitcoin payments and other cryptocurrencies and 
            this is just proof that it is becoming bigger and bigger.""",

            """People don't realize how fast Lightning is growing. It's going to change our lives"""
        ]

        sentiments = [
            -0.08705357142857142,
            0,
            .05,
            0.34861111111111115,
            .5,
            -0.13333333333333333,
            -0.02059523809523809,
            0.12209821428571428,
            0.25277777777777777,
            .2
        ]

        for i in range(len(texts)):
            c = Comment(texts[i], 1)
            self.assertEqual(c.sentiment, sentiments[i])

    def test_clean_text(self):
        t = "this is a, very. dirty & comment/ \ @sfdo2234sfd&  it \ needs / to &  be, cleaned. up. "
        c = Comment(t, 1)
        self.assertEqual(c.clean_text, "this is a very dirty comment it needs to be cleaned up")


class TestCommentScanner(TestCase):
    def foo(self):
        self.fail()