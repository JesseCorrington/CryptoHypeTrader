import urllib.parse
import urllib.request
import json


CONFIG = json.loads(open("config.json").read())


def geturl_json(url):
    ret = urllib.request.urlopen(url)
    return json.loads(ret.read())


def geturl_text(url):
    ret = urllib.request.urlopen(url)
    return ret.read().decode()




def get_etherdelta_json(url):
    hdrs = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    req = urllib.request.Request(url, headers=hdrs)
    res = urllib.request.urlopen(req)
    return json.loads(res.read())


def etherdelta_test():
    ticker = get_etherdelta_json("https://api.etherdelta.com/returnTicker")

    for marketId in ticker:
        coin = ticker[marketId]

        bid = coin["bid"]
        ask = coin["ask"]
        if ask == 0 or bid == 0:
            continue

        spread = ask - bid

        if spread < 0:
            percentGain = (bid - ask) / ask

            if percentGain >= .025:
                print("---- Candidate Arbitrage ----")
                print(marketId)
                print("token address: ", coin["tokenAddr"])
                print("base volume: ", coin["baseVolume"])
                print("gain percent: ", percentGain * 100)
                print("ask: ", ask)
                print("bid: ", bid)

                print()

                print("getting open orders...")
                ordersUrl = "https://api.etherdelta.com/orders/" + coin["tokenAddr"] + "/0"
                print(ordersUrl)

                orders = get_etherdelta_json(ordersUrl)
                buys = orders["buys"]
                sells = orders["sells"]

                # we want sells to go low to high and bid high to low
                # just need to flip sells
                #sells = list(reversed(sells))

                #sells.sort(key=lambda x: x["price"], reverse=True)
                buys.sort(key=lambda x: x["price"], reverse=True)

                # TODO: there is an issue because sometimes we only have the most expensive
                # sells, since there is pagination
                # not an issue for buys, maybe just skip these markets?
                # we can get more pages if we have yet to find the cheapest sells, but is it worth it?


                print("** sells[0] = ", sells[0]["price"])

                # TODO: we're outputting volumes in the quote currency

                print("sells -----")
                for i in range(5):
                    sell = sells[4 - i]
                    print(sell["price"], "    ", sell["ethAvailableVolume"], "(ETH)")

                print("buys -----")
                for i in range(5):
                    buy = buys[i]
                    print(buy["price"], "    ", buy["ethAvailableVolume"], "(ETH)")


                print("-----------------------------")
                print()
                print()
