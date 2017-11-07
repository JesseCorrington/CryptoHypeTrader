from ingestion import util

COIN_LIST_URL = "https://min-api.cryptocompare.com/data/all/coinlist"
SOCIAL_STATS_URL = "https://www.cryptocompare.com/api/data/socialstats/"


def __api_request(url):
    data = util.geturl_json(url)
    if "Response" not in data:
        raise Exception("ERROR: invalid response format")

    if "Data"not in data:
        raise Exception("ERROR: no response data")

    if data["Response"] != "Success":
        raise Exception("ERROR: invalid response data", data["Response"])

    return data["Data"]


def get_coin_list():
    all_coins = __api_request(COIN_LIST_URL)

    ret = []
    for symbol, coin in all_coins.items():
        ret.append({
            "cc_id": coin["Id"],
            "symbol": coin["Symbol"],
            "name": coin["Name"]
        })

    return ret


def get_social_stats(cc_id):
    return __api_request(SOCIAL_STATS_URL + "?id=" + cc_id)
