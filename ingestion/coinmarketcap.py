import datetime
import re
from bs4 import BeautifulSoup
from ingestion import util
import datetime


# Provides access to coinmarketcap.com data, using the API when available,
# or web scraping when there is no public API


def get_coin_list():
    all_coins = util.geturl_json("https://api.coinmarketcap.com/v1/ticker/")

    # Note that cryptocurrency symbols are not guaranteed to be unique so, we
    # use the unique id as the index, rather than the symbol

    ret = []
    for coin in all_coins:
        ret.append({
            "cmc_id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"]
        })

    return ret


def get_ticker():
    all_coins = util.geturl_json("https://api.coinmarketcap.com/v1/ticker/")

    ret = []
    for coin in all_coins:
        # This might not be the exact time cmc updated the ticker, but it's close enough
        # and prevents any potential issues with time zone issues screwing up our dates in the db
        now = datetime.datetime.today()

        ret.append({
            "symbol": coin["symbol"],
            "date": now,
            "price": __text_to_float(coin["price_usd"]),
            "price_btc": __text_to_float(coin["price_btc"]),
            "volume": __text_to_float(coin["24h_volume_usd"]),
            "market_cap": __text_to_float(coin["market_cap_usd"]),
            "supply_avail": __text_to_float(coin["available_supply"]),
            "supply_total": __text_to_float(coin["total_supply"]),
            "supply_max": __text_to_float(coin["max_supply"]),
        })

    return ret


def get_subreddit(id):
    # We have to scrape for the reddit url, because there is no api to get it
    # a simple regex does the trick

    html = util.geturl_text("https://coinmarketcap.com/currencies/" + id)
    pattern = "reddit\\.com\\/r\\/([^/.]*)\\."
    match = re.search(pattern, html)

    if match is not None:
        return match.group(1)
    else:
        return None


def __text_to_float(text):
    if text is None:
        return None

    text = text.strip()
    text = text.replace(",", "")

    if text == "-":
        # Some of the old volume data is missing on coin market cap
        return None

    return float(text)


# TODO: there may be an API on cryptocompare.com to get this data
def get_historical_prices(coin, start=datetime.datetime(2011, 1, 1), end=datetime.date.today()):
    # There's no API to get historic price data, but we can scrape it from a table
    # on the /historical-data page

    date_format = "%Y%m%d"
    s = start.strftime(date_format)
    e = end.strftime(date_format)

    url = "https://coinmarketcap.com/currencies/" + coin["cmc_id"] + "/historical-data/?start=" + s + "&end=" + e

    html = util.geturl_text(url)
    soup = BeautifulSoup(html, "lxml")

    div = soup.find("div", attrs={"class": "table-responsive"})
    table = div.find('table', attrs={'class': 'table'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    historic_data = []

    for row in rows:
        cols = row.find_all('td')

        if len(cols) < 7:
            return None

        date = cols[0].text.strip()
        date = datetime.datetime.strptime(date, "%b %d, %Y")
        open = __text_to_float(cols[1].text)
        high = __text_to_float(cols[2].text)
        low = __text_to_float(cols[3].text)
        close = __text_to_float(cols[4].text)
        volume = __text_to_float(cols[5].text)
        market_cap = __text_to_float(cols[6].text)

        daily_ticker = {
            "date": date,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "marketCap": market_cap
        }

        historic_data.append(daily_ticker)

    return historic_data
