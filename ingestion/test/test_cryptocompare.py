from unittest import TestCase

from ingestion.datasources import cryptocompare as cc


class TestCryptoCompare(TestCase):
    def test_get_list(self):
        data = cc.CoinList().get()
        self.assertGreater(len(data), 1000)

    def test_get_links(self):
        coins = cc.CoinList().get()

        btc = next(coin for coin in coins if coin["symbol"] == "BTC")
        links = cc.CoinLinks(btc["cc_id"]).get()
        self.assertEqual(links["subreddit"], "bitcoin")
        self.assertEqual(links["twitter"], "bitcoin")

        eth = next(coin for coin in coins if coin["symbol"] == "ETH")
        links = cc.CoinLinks(eth["cc_id"]).get()
        self.assertEqual(links["subreddit"], "ethereum")
        self.assertEqual(links["twitter"], "ethereum")

    def test_get_social_stats(self):
        coins = cc.CoinList().get()

        btc = next(coin for coin in coins if coin["symbol"] == "BTC")
        stats = cc.SocialStats(btc["cc_id"]).get()
        self.assertGreater(stats["total_points"], 0)
        self.assertGreater(stats["crypto_compare"]["points"], 0)
        self.assertGreater(stats["twitter"]["points"], 0)
        self.assertGreater(stats["reddit"]["points"], 0)
        self.assertGreater(stats["facebook"]["points"], 0)
