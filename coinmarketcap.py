import re
from bs4 import BeautifulSoup
import datetime
from util import *

def get_coin_list():
    all_coins = geturl_json("https://api.coinmarketcap.com/v1/ticker/")

    symbolMapped = {}
    for coin in all_coins:
        symbolMapped[coin["symbol"].lower()] = coin

    return symbolMapped


def get_subreddit(id):
    html = geturl_text("https://coinmarketcap.com/currencies/" + id)

    pattern = "reddit\\.com\\/r\\/([^/.]*)\\."
    match = re.search(pattern, html)

    subreddit = ""
    if match is not None:
        subreddit = match.group(1)
    else:
        print("ERROR: Failed to parse reddit url for ", id)

    return subreddit


def get_historical_prices(id):
    # TODO: dynamic url
    url = "https://coinmarketcap.com/currencies/chainlink/historical-data/?start=20130428&end=20171009"

    html = geturl_text(url)
    soup = BeautifulSoup(html)

    div = soup.find("div", attrs={"class": "table-responsive"})
    table = div.find('table', attrs={'class': 'table'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    historicData = []

    for row in rows:
        cols = row.find_all('td')

        date = cols[0].text.strip()
        open = cols[1].text.strip()
        high = cols[2].text.strip()
        low = cols[3].text.strip()
        close = cols[4].text.strip()
        volume = cols[5].text.strip()
        marketCap = cols[6].text.strip()

        date = datetime.datetime.strptime(date, "%b %d, %Y")

        dailyTicker = {
            "date": date,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "marketCap": marketCap
        }

        historicData.append(dailyTicker)

    return historicData