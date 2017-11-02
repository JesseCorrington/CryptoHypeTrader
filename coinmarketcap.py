import re
from bs4 import BeautifulSoup
import datetime
from database import *

def get_coin_list():
    all_coins = geturl_json("https://api.coinmarketcap.com/v1/ticker/")

    symbolMapped = {}
    for coin in all_coins:
        symbolMapped[coin["symbol"]] = {
            "symbol": coin["symbol"],
            "cmc_id": coin["id"],
            "name": coin["name"]
        }

    return symbolMapped


def get_subreddit(id):
    html = geturl_text("https://coinmarketcap.com/currencies/" + id)

    pattern = "reddit\\.com\\/r\\/([^/.]*)\\."
    match = re.search(pattern, html)

    subreddit = ""
    if match is not None:
        subreddit = match.group(1)
    else:
        raise Exception("ERROR: Failed to parse reddit url for ", id)

    return subreddit

def text_to_float(text):
    text = text.strip()
    text = text.replace(",", "")

    if text == "-":

        # TODO:
        return None

    return float(text)

def get_historical_prices(id):
    # TODO: always want all data, just make it go current day + 1
    s = "20110101"
    e = "20180101"

    url = "https://coinmarketcap.com/currencies/" + id + "/historical-data/?start=" + s + "&end=" + e

    html = geturl_text(url)
    soup = BeautifulSoup(html, "lxml")

    div = soup.find("div", attrs={"class": "table-responsive"})
    table = div.find('table', attrs={'class': 'table'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    historicData = []

    for row in rows:
        cols = row.find_all('td')

        date = cols[0].text.strip()
        date = datetime.datetime.strptime(date, "%b %d, %Y")

        open = text_to_float(cols[1].text)
        high = text_to_float(cols[2].text)
        low = text_to_float(cols[3].text)
        close = text_to_float(cols[4].text)
        volume = text_to_float(cols[5].text)
        marketCap = text_to_float(cols[6].text)

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

    historicData.sort(key=lambda x: x["date"])
    return historicData


def save_historic_data(id, symbol):
    daily_ticker = get_historical_prices(id)

    collection = MONGO_DB.prices

    # TODO: only insert if date is not there
    for day in daily_ticker:
        day["symbol"] = symbol
        collection.insert_one(day)
