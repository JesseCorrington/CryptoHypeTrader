# Basics
import pandas as pd
import numpy as np
import urllib.request as request
import requests as req
import json
from bs4 import BeautifulSoup as bs

# Custom
from ingestion import datasource as ds
from ingestion import config
from ingestion import database as db


''' Because I'm just scraping a coin list from a web page, I
 Don't see an obvious way to impliment coinlist as a DataSource.
 Going with a hacky method for now '''

class CoinList:

    def __init__(self):
        self.stocktwits_coin_meta = []


    def ScrapeCoins(self):
    # Scrape the stocktwits cryptocurrency directory for a current list of supported currencies

        url = config.stocktwits["coinlist_url"]
        page = req.get(url)
        soup = bs(page.content, 'html.parser')
        data = soup.find_all('li', class_ = 'clearfix')

        coin_meta = []
        for item in range(len(data)):
            ind = data[item].a.contents[0].rfind('(')
            contents = data[item].a.contents[0]
            coin_meta.append({
            'coin_id': data[item].get('id'),
            'name': contents[1:ind],
            'symbol': contents[ind+1:len(contents)-4]
            })

        self.stocktwits_coin_meta = coin_meta
        return coin_meta



    def find_ids(self):
    # Find the correct ids for each scraped currency from our existing collection, based on coin symbols.
    # If there are no matching symbols, discard the data for now

        hype_coins = db.get_coins()

        stocktwits_columns = ['coin_id', 'name', 'symbol']
        hype_columns = list(hype_coins[0].keys())

        stocktwits_coins = pd.DataFrame(self.stocktwits_coin_meta, columns = stocktwits_columns)
        hype_coins = pd.DataFrame(hype_coins, columns = hype_columns)

        mask = np.isin(stocktwits_coins.symbol, hype_coins.symbol)
        stocktwits_coins = stocktwits_coins[mask]

        for i in stocktwits_coins.index:
            stocktwits_coins.loc[i, 'coin_id'] = hype_coins[hype_coins.symbol == stocktwits_coins.loc[i, 'symbol']]._id.base[0][0]

        return stocktwits_coins


def get_coins():
# Helper function to return list of coins for the stocktwits task

    coinlist = CoinList()
    stocktwits_coins = coinlist.ScrapeCoins()
    stocktwits_coins = coinlist.find_ids()
    return stocktwits_coins



class Ticker(ds.DataSource):

    def __init__(self, coin_symbol, coin_id, coin_name):
        token = config.stocktwits['token']
        self.coin_id = coin_id
        self.coin_name = coin_name
        self.coin_symbol = coin_symbol

        super().__init__(
            "https://api.stocktwits.com/api/2/streams/symbols.json",
            {"access_token":token,
             "symbols":self.coin_symbol
            }
        )

    def parse(self, api_response, lim = 30):
    # query server for JSON data for the most recent 30 posts for up to 10 currencies

        #TODO The API limits calls to 400 per hour, which means that we can almost get data for every currency twice and hour, but not quite.
        #     Some currencies get tagged way less than 30 times per hour, so we need to come up with a smart way of using those 400 calls.

        contents = api_response
        posts = []
        for post in range(lim):
            if contents['messages'][post]['entities']['sentiment']:
                sentiment = contents['messages'][post]['entities']['sentiment']['basic']
            else:
                sentiment = None
            posts.append({
                          'post':contents["messages"][post]["body"],
                          'sentiment': sentiment,
                          'date': contents['messages'][post]['created_at'],
                          'symbol': str(self.coin_symbol[:len(self.coin_symbol)-2]),
                          'name': str(self.coin_name),
                          'coin_id': int(self.coin_id)
                          })

        return posts
