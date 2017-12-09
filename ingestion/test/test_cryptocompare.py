from unittest import TestCase

from ingestion.datasources import cryptocompare as cc


class TestCryptoCompare(TestCase):
    def test_get_list(self):
        data = cc.CoinList().get()
        self.assertTrue(len(data) > 1000)

    def test_get_links(self):
        coins = cc.CoinList().get()

        btc = next(coin for coin in coins if coin["symbol"] == "BTC")
        links = cc.CoinLinks(btc["cc_id"]).get()
        self.assertTrue(links["subreddit"] == "bitcoin")
        self.assertTrue(links["twitter"] == "bitcoin")

        eth = next(coin for coin in coins if coin["symbol"] == "ETH")
        links = cc.CoinLinks(eth["cc_id"]).get()
        self.assertTrue(links["subreddit"] == "ethereum")
        self.assertTrue(links["twitter"] == "ethereumproject")

    def test_get_social_stats(self):
        coins = cc.CoinList().get()

        btc = next(coin for coin in coins if coin["symbol"] == "BTC")
        stats = cc.SocialStats(btc["cc_id"]).get()
        self.assertTrue(stats["total_points"] > 0)
        self.assertTrue(stats["crypto_compare"]["points"] > 0)
        self.assertTrue(stats["twitter"]["points"] > 0)
        self.assertTrue(stats["reddit"]["points"] > 0)
        self.assertTrue(stats["facebook"]["points"] > 0)
