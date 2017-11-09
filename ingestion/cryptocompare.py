from ingestion import datasource as ds


class CryptoCompareDataSource(ds.DataSource):
    def validate(self, data):
        if "Response" not in data:
            raise Exception("ERROR: invalid response format")

        if "Data" not in data:
            raise Exception("ERROR: no response data")

        if data["Response"] != "Success":
            raise Exception("ERROR: response not success {0}".format(data["Response"]))

    def pre_parse(self, data):
        return data["Data"]


# TODO: there should be some slick way to make this a backup source for cmc.CoinList
class CoinList(CryptoCompareDataSource):
    def __init__(self):
        super().__init__("https://min-api.cryptocompare.com/data/all/coinlist")

    def parse(self, all_coins):
        ret = []
        for symbol, coin in all_coins.items():
            ret.append({
                "cc_id": coin["Id"],
                "symbol": coin["Symbol"],
                "name": coin["Name"]
            })

        return ret


class SocialStats(CryptoCompareDataSource):
    def __init__(self, cc_id):
        super().__init__("https://www.cryptocompare.com/api/data/socialstats/", {"id": cc_id})

    def parse(self, social_stats):
        return social_stats