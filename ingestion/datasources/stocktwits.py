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
from common import database as db


class CoinList(ds.DataSource):

    def __init__(self):
        self.stocktwits_coin_meta = []
        self.initial_failed_matches = []
        self.final_failed_matches = []
        super().__init__(
            "https://stocktwits.com/cryptocurrency_token_directory",
            params = {},
            response_format = 'soup'
            )

    def parse(self, data):
    # Scrape the stocktwits cryptocurrency directory for a current list of supported currencies


        def scrapeStockTwits(data):
        # Scrape stocktwits for a list of cryptocurrency names, symbols, and stocktwits ids
            data = data.find_all('li', class_ = 'clearfix')

            coin_meta = []
            for item in range(len(data)):
                ind = data[item].a.contents[0].rfind('(')
                contents = data[item].a.contents[0]
                coin_meta.append({
                'coin_id': data[item].get('id'),
                'name': contents[1:ind],
                'symbol': contents[ind+1:len(contents)-4]
                })

            # Save the coin list, with stocktwits-specific coin ids
            self.stocktwits_coin_meta = coin_meta



        def swap_ids():
        # Swap out the stocktwits coin ids for our own internal id system


            def full_id(coins):
            # Create new field in dataframes: 'full_id'
                for i in range(len(coins)):
                    add = ('{}_{}'.format(coins[i]['symbol'], coins[i]['name']))
                    coins[i]['full_id'] = add.strip()
                return coins


            def duplicate_symbols(coins):
            # Find duplicate symbols in coin list

                symbols = set()
                duplicate_symbols = set()
                for coin in coins.symbol:
                    sym = coin
                    if sym in symbols:
                        duplicate_symbols.add(sym)
                    else:
                        symbols.add(sym)

                return duplicate_symbols


            # Grab list of coins from db
            hype_coins = db.get_coins()

            # Make columns for the temporary dataframes
            stocktwits_columns = ['coin_id', 'name', 'symbol', 'full_id']
            hype_columns = list(hype_coins[0].keys())
            hype_columns.append('full_id')

            # Populate dataframes
            stocktwits_coins = pd.DataFrame(full_id(self.stocktwits_coin_meta), columns = stocktwits_columns)
            hype_coins = pd.DataFrame(full_id(hype_coins), columns = hype_columns)

            # Make mask with matching full_ids between stocktwit metadata and internal metadata
            mask = np.isin(stocktwits_coins.full_id, hype_coins.full_id)

            # Save items that didn't match with the 'full_id' scheme
            self.initial_failed_matches = stocktwits_coins[[not i for i in mask]]
            stocktwits_coins = stocktwits_coins.drop('full_id', axis = 1)

            # Find duplicates in hype_coin symbols
            hype_coin_duplicates = duplicate_symbols(hype_coins)

            # If there are no duplicates of a given symbol in hype_coins, base id match on symbol only
            for i in range(len(self.initial_failed_matches.symbol)):
                symbol = self.initial_failed_matches.iloc[i, 2]
                if (symbol not in hype_coin_duplicates) and (np.isin(symbol.strip(), hype_coins.symbol).any()):
                    mask[self.initial_failed_matches.index[i]] = True

            # Apply mask to stocktwits_coins and add swap the stocktwits-specific ids out for our internal id system
            self.final_failed_matches = stocktwits_coins[[not i for i in mask]]
            stocktwits_coins = stocktwits_coins[mask]
            for i in stocktwits_coins.index:
                stocktwits_coins.loc[i, 'coin_id'] = hype_coins[hype_coins.symbol == stocktwits_coins.loc[i, 'symbol']]._id.base[0][0]

            return stocktwits_coins


        # Finally, run the helper functions
        scrapeStockTwits(data)
        return swap_ids()



class recentPosts(ds.DataSource):

    def __init__(self, coin_symbol, coin_id, coin_name):
        token = config.stocktwits['token']
        self.coin_id = coin_id
        self.coin_name = coin_name
        self.coin_symbol = coin_symbol
        self.lim = 30

        super().__init__(
            "https://api.stocktwits.com/api/2/streams/symbols.json",
            {"access_token":token,
             "symbols":self.coin_symbol
            }
        )


    def parse(self, api_response):
    # query server for JSON data for the most recent 30 posts for up to 10 currencies

        #TODO The API limits calls to 400 per hour, which means that we can almost get data for every currency twice and hour, but not quite.
        #     Some currencies get tagged way less than 30 times per hour, so we need to come up with a smart way of using those 400 calls.

        contents = api_response
        posts = []
        for post in range(self.lim):
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
