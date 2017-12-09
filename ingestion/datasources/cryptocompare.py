from urllib.parse import urlparse
from ingestion import datasource as ds
from common.util import safe_assign


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


class SocialStats(CryptoCompareDataSource):
    def __init__(self, cc_id):
        super().__init__("https://www.cryptocompare.com/api/data/socialstats/", {"id": cc_id})

    def parse(self, data):
        stats = {
            "total_points": data["General"]["Points"],
        }

        if "CryptoCompare" in data:
            cc_stats = data["CryptoCompare"]
            stats["crypto_compare"] = {}
            safe_assign(stats["crypto_compare"], "comments", cc_stats, "Comments", int)
            safe_assign(stats["crypto_compare"], "followers", cc_stats, "Followers", int)
            safe_assign(stats["crypto_compare"], "posts", cc_stats, "Posts", int)
            safe_assign(stats["crypto_compare"], "points", cc_stats, "Points", int)
            safe_assign(stats["crypto_compare"], "page_views", cc_stats, "PageViews", int)

        if "Twitter" in data:
            twitter_stats = data["Twitter"]
            stats["twitter"] = {}
            safe_assign(stats["twitter"], "followers", twitter_stats, "followers", int)
            safe_assign(stats["twitter"], "points", twitter_stats, "Points", int)

        if "Reddit" in data:
            reddit_stats = data["Reddit"]
            stats["reddit"] = {}
            safe_assign(stats["reddit"], "comments_per_hour", reddit_stats, "comments_per_hour", float)
            safe_assign(stats["reddit"], "comments_per_day", reddit_stats, "comments_per_day", float)
            safe_assign(stats["reddit"], "posts_per_hour", reddit_stats, "posts_per_hour", float)
            safe_assign(stats["reddit"], "posts_per_day", reddit_stats, "posts_per_day", float)
            safe_assign(stats["reddit"], "points", reddit_stats, "Points", int)

        if "Facebook" in data:
            fb = data["Facebook"]
            stats["facebook"] = {}
            safe_assign(stats["facebook"], "likes", fb, "likes", int)
            safe_assign(stats["facebook"], "points", fb, "Points", int)

        if "CodeRepository" in data:
            stats["code_repo"] = {}
            safe_assign(stats["code_repo"], "points", data["CodeRepository"], "Points", int)

        return stats
