import re
import datetime
from ingestion import datasource as ds


# Provides access to coinmarketcap.com data, using the API when available,
# or web scraping when there is no public API


class CoinList(ds.DataSource):
    """Used to get a list of all the coins on coinmarketcap"""

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
    """Used to get current price/marketcap/volume data for all coins"""

    def parse(self, all_coins):
        ret = []
        for coin in all_coins:
            # This might not be the exact time cmc updated the ticker, but it's close enough
            # and prevents any potential issues with time zone issues screwing up our dates in the db
            today = datetime.datetime.utcnow()

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


class CoinLinks(ds.DataSource):
    """Used to get social media links for a coin (subreddit, twitter, btctalk)"""

    def __init__(self, coin):
        url = "https://coinmarketcap.com/currencies/{}".format(coin["cmc_id"])
        super().__init__(url, response_format="text")

    def parse(self, html):
        # We have to scrape for the reddit url, because there is no api to get it
        # a simple regex does the trick

        links = {}

        def find_link(pattern):
            match = re.search(pattern, html)
            if match is not None:
                return match.group(1)
            return None

        # Find and save all the links we're looking for
        subreddit = find_link("reddit\\.com\\/r\\/([^/.]*)\\.")
        if subreddit:
            links["subreddit"] = subreddit

        twitter = find_link('class="twitter-timeline" href="https://twitter.com/([^"]*)')
        if twitter:
            links["twitter"] = twitter

        ann = find_link('href="https:\\/\\/bitcointalk\\.org\\/index\\.php\\?topic=([^"]*)')
        if ann:
            links["btctalk_ann"] = ann

        icon = find_link('src="(https:\\/\\/s2.coinmarketcap.com\\/static\\/img\\/coins\\/[0-9]*x[0-9]*\\/[0-9]*.png)"')
        if icon:
            links["icon"] = icon

        return links


class HistoricalPrices(ds.DataSource):
    """Used to get historical price data for a coin
    This requires scraping the site, because there is no API for this data
    This is only used for the initial data import, and after that we can just periodically get the ticker
    """

    def __init__(self, coin, start=datetime.datetime(2011, 1, 1), end=datetime.datetime.utcnow()):
        date_format = "%Y%m%d"
        params = {
            "start": start.strftime(date_format),
            "end": end.strftime(date_format)
        }
        url = "https://coinmarketcap.com/currencies/{}/historical-data".format(coin["cmc_id"])

        super().__init__(url, params, "soup")

    def parse(self, soup):
        # There's no API to get historical price data, but we can scrape it from a table
        # on the /historical-data page

        div = soup.find("div", attrs={"class": "table-responsive"})
        table = div.find('table', attrs={'class': 'table'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        historical_data = []

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

            historical_data.append(daily_ticker)

        return historical_data
