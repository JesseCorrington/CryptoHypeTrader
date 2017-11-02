import re
from bs4 import BeautifulSoup
import util
import datetime


def get_coin_list():
    all_coins = util.geturl_json("https://api.coinmarketcap.com/v1/ticker/")

    symbolMapped = {}
    for coin in all_coins:
        symbolMapped[coin["symbol"]] = {
            "symbol": coin["symbol"],
            "cmc_id": coin["id"],
            "name": coin["name"]
        }

    return symbolMapped


def get_subreddit(id):
    html = util.geturl_text("https://coinmarketcap.com/currencies/" + id)

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
        # Some of the old volume data is missing on coin market cap
        return None

    return float(text)


def get_historical_prices(id, start=datetime.date(2011, 1, 1), end=datetime.date.today()):
    date_format = "%Y%m%d"
    s = start.strftime(date_format)
    e = end.strftime(date_format)

    url = "https://coinmarketcap.com/currencies/" + id + "/historical-data/?start=" + s + "&end=" + e

    html = util.geturl_text(url)
    soup = BeautifulSoup(html, "lxml")

    div = soup.find("div", attrs={"class": "table-responsive"})
    table = div.find('table', attrs={'class': 'table'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    historicData = []

    for row in rows:
        cols = row.find_all('td')

        if len(cols) < 7:
            return None

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
