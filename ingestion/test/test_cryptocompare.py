from unittest import TestCase
from ingestion import cryptocompare as cc



class TestCryptoCompare(TestCase):
    def test_get_list(self):
        data = cc.CoinList().get()
        self.assertTrue(len(data) > 1000)

    def test_get_stats(self):
        coins = cc.CoinList().get()
        test_id = coins[0]["cc_id"]
        data = cc.SocialStats(test_id).get()

        for expected in ["General", "Twitter", "Reddit", "Facebook", "CodeRepository"]:
            assert(expected in data)
