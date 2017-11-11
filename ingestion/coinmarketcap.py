import re
import datetime
from ingestion import datasource as ds


# Provides access to coinmarketcap.com data, using the API when available,
# or web scraping when there is no public API


class CoinList(ds.DataSource):
    def __init__(self):
        # limit defaults to 100, but coinmarketcap doesn't have a max for the limit,
        # so just set it super high to make sure we get all the coins
        # this may eventually fail if they put a max for limit, so we'll check for that
        # error after the request
        super().__init__(
            "https://api.coinmarketcap.com/v1/ticker",
            {"limit": 10000}
        )

    def parse(self, all_coins):
        # Note that cryptocurrency symbols are not guaranteed to be unique so, we
        # use the unique id as the index, rather than the symbol

        ret = []
        for coin in all_coins:
            ret.append({
                "cmc_id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"]
            })

        # make sure limit is working as expected
        # 1200 is a sanity check, roughly the number of coins as of 10/2017
        if len(ret) < 1200 or len(ret) == self.params["limit"]:
            raise Exception("cmc limit not working as expected, this likely means they changed the API to have a limit max")

        return ret


class Ticker(CoinList):
    def parse(self, all_coins):
        ret = []
        for coin in all_coins:
            # This might not be the exact time cmc updated the ticker, but it's close enough
            # and prevents any potential issues with time zone issues screwing up our dates in the db
            today = datetime.datetime.today()

            def to_float(s):
                return float(s) if s else None

            ret.append({
                "cmc_id": coin["id"],
                "date": today,
                "price": to_float(coin["price_usd"]),
                "price_btc": to_float(coin["price_btc"]),
                "volume": to_float(coin["24h_volume_usd"]),
                "market_cap": to_float(coin["market_cap_usd"]),
                "supply_avail": to_float(coin["available_supply"]),
                "supply_total": to_float(coin["total_supply"]),
                "supply_max": to_float(coin["max_supply"])
            })

        return ret


class SubredditName(ds.DataSource):
    def __init__(self, cmc_id):
        super().__init__("https://coinmarketcap.com/currencies/{0}".format(cmc_id), format="text")

    def parse(self, html):
        # We have to scrape for the reddit url, because there is no api to get it
        # a simple regex does the trick

        pattern = "reddit\\.com\\/r\\/([^/.]*)\\."
        match = re.search(pattern, html)

        if match is not None:
            return match.group(1)
        else:
            return None


class HistoricalPrices(ds.DataSource):
    def __init__(self, coin, start=datetime.datetime(2011, 1, 1), end=datetime.datetime.today()):
        date_format = "%Y%m%d"
        params = {
            "start": start.strftime(date_format),
            "end": end.strftime(date_format)
        }
        url = "https://coinmarketcap.com/currencies/" + coin["cmc_id"] + "/historical-data"

        super().__init__(url, params, "soup")

    def parse(self, soup):
        # TODO: there may be an API on cryptocompare.com to get this data

        # There's no API to get historic price data, but we can scrape it from a table
        # on the /historical-data page

        div = soup.find("div", attrs={"class": "table-responsive"})
        table = div.find('table', attrs={'class': 'table'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        historic_data = []

        def to_float(text):
            if text is None:
                return None

            text = text.strip()
            text = text.replace(",", "")

            if text == "-":
                # Some of the old volume data is missing on coin market cap
                return None

            return float(text)

        for row in rows:
            cols = row.find_all('td')

            if len(cols) < 7:
                return None

            date = cols[0].text.strip()
            date = datetime.datetime.strptime(date, "%b %d, %Y")
            open = to_float(cols[1].text)
            high = to_float(cols[2].text)
            low = to_float(cols[3].text)
            close = to_float(cols[4].text)
            volume = to_float(cols[5].text)
            market_cap = to_float(cols[6].text)

            daily_ticker = {
                "date": date,
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "market_cap": market_cap
            }

            historic_data.append(daily_ticker)

        return historic_data
