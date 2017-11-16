from urllib.parse import urlparse
from ingestion import datasource as ds


class CryptoCompareDataSource(ds.DataSource):
    def validate(self, data):
        if "Response" not in data:
            return "invalid response format"

        if "Data" not in data:
            return "no response data"

        if data["Response"] != "Success":
            return "response not success {}".format(data["Response"])

    def pre_parse(self, data):
        return data["Data"]


class CoinList(CryptoCompareDataSource):
    def __init__(self):
        super().__init__("https://min-api.cryptocompare.com/data/all/coinlist")

    def parse(self, all_coins):
        ret = []
        for symbol, coin in all_coins.items():
            ret.append({
                "cc_id": coin["Id"],
                "symbol": coin["Symbol"],
                "name": coin["CoinName"]
            })

        return ret


class CoinLinks(CryptoCompareDataSource):
    def __init__(self, cc_id):
        super().__init__("https://www.cryptocompare.com/api/data/socialstats/", {"id": cc_id})

    def parse(self, stats):
        links = {}

        if "Reddit" in stats and "link" in stats["Reddit"] and stats["Reddit"]["link"]:
            subreddit_url = stats["Reddit"]["link"]
            links["subreddit"] = urlparse(subreddit_url).path.replace("/r/", "").replace("/", "")

        if "Twitter" in stats and "link" in stats["Twitter"] and stats["Twitter"]["link"]:
            twitter_url = stats["Twitter"]["link"]
            links["twitter"] = urlparse(twitter_url).path.replace("/", "")

        return links
